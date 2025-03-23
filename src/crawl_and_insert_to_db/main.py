from db import get_db, create_tables, engine
from models import PDChuDe, PDDeMuc, PDChuong, PDDieu, PDTable, PDFile, PDMucLienQuan
from bs4 import BeautifulSoup
from utils import convert_roman_to_num, extract_input
import uuid
import json
import os
import re

# Tạo các bảng nếu chưa tồn tại trong database
create_tables(engine=engine)

# Load checkpoint và dữ liệu
def load_json_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except Exception as e:
        print(f"Không thể đọc file {file_path}: {e}")
        return {}

def load_checkpoint():
    if os.path.exists("checkpoint.txt"):
        with open("checkpoint.txt", "r") as f:
            return f.read().strip()
    return None

def save_checkpoint(file_name):
    with open("checkpoint.txt", "w") as f:
        f.write(file_name)

checkpoint = load_checkpoint()

# Insert thông tin vào database
print("Load Chủ Đề Từ File ...")
chudes = load_json_file("./BoPhapDienDienTu/ChuDe.json")
with next(get_db()) as db:
    try:
        chude_objects = [PDChuDe(ten=chude["Text"], stt=chude["STT"], id=chude["Value"]) for chude in chudes]
        db.add_all(chude_objects)
        db.commit()
        print("Inserted tất cả chủ đề pháp điển!")
    except Exception as e:
        db.rollback()

print("Load Đề Mục Từ File ...")
demucs = load_json_file("./BoPhapDienDienTu/DeMuc.json")
with next(get_db()) as db:
    try:
        demuc_objects = [PDDeMuc(ten=demuc["Text"], stt=demuc["STT"], id=demuc["Value"], chude_id=demuc["ChuDe"]) for demuc in demucs]
        db.add_all(demuc_objects)
        db.commit()
        print("Inserted tất cả đề mục pháp điển!")
    except Exception as e:
        db.rollback()

print("Load Tree Nodes Từ File ...")
tree_nodes = load_json_file("./BoPhapDienDienTu/TreeNode.json")

demuc_directory = os.fsencode("./BoPhapDienDienTu/demuc")
isSkipping = bool(checkpoint)

for file in os.listdir(demuc_directory):
    file_name = os.fsdecode(file)
    with open("./BoPhapDienDienTu/demuc/" + file_name, "r") as demuc_file:
        if file_name == checkpoint:
            isSkipping = False
        if isSkipping:
            continue
        
        demuc_html = BeautifulSoup(demuc_file.read(), "html.parser")
        demuc_nodes = [node for node in tree_nodes if node["DeMucID"] == file_name.split(".")[0]]
        
        if not demuc_nodes:
            print("Không tìm thấy node cho đề mục: " + file_name)
            continue

        with next(get_db()) as db:
            try:
                demuc_chuong = [node for node in demuc_nodes if node["TEN"].startswith("Chương ")]
                chuongs_data = []
                
                for chuong in demuc_chuong:
                    mapc = chuong["MAPC"]
                    stt = convert_roman_to_num(chuong["ChiMuc"])
                    chuong_data = PDChuong(ten=chuong["TEN"], mapc=mapc, chimuc=chuong["ChiMuc"], stt=stt, demuc_id=chuong["DeMucID"])
                    db.add(chuong_data)
                    chuongs_data.append(chuong_data)

                try:
                    db.commit()
                    print(f'Insert {len(demuc_chuong)} chương của đề mục {file_name}')
                except Exception as e:
                    db.rollback()
                
                if not chuongs_data:
                    chuong_data = PDChuong(ten="", mapc=uuid.uuid4(), chimuc="0", stt=0, demuc_id=file_name.split(".")[0])
                    db.add(chuong_data)
                    try:
                        db.commit()
                        chuongs_data.append(chuong_data)
                    except Exception as e:
                        db.rollback()

                demuc_dieus = [node for node in demuc_nodes if node["TEN"].startswith("Điều ")]
                print(f'Đề mục {file_name} có {len(demuc_chuong)} chương và {len(demuc_dieus)} điều')
                stt = 0
                all_dieus_lienquan = []
                
                for dieu in demuc_dieus:
                    if len(chuongs_data) == 1:
                        dieu["ChuongID"] = chuongs_data[0].mapc
                    else:
                        for chuong in chuongs_data:
                            if dieu["MAPC"].startswith(chuong.mapc):
                                dieu["ChuongID"] = chuong.mapc
                                break
                    
                    mapc = dieu["MAPC"]
                    dieu_html_list = demuc_html.select(f'a[name="{mapc}"]')
                    if not dieu_html_list:
                        print(f"Không tìm thấy thẻ a[name={mapc}] trong {file_name}, bỏ qua điều {mapc}")
                        continue
                    dieu_html = dieu_html_list[0]
                    ten = dieu_html.next_sibling
                    ghi_chu_html = dieu_html.parent.next_sibling
                    vbqppl = ghi_chu_html.text.strip("()") if ghi_chu_html else None
                    vbqppl_link = ghi_chu_html.select("a")[0]["href"] if ghi_chu_html.select("a") else None
                    chimuc = re.sub(r'[^0-9]', '', dieu["ChiMuc"]) if dieu["ChiMuc"] else None
                    
                    noidung_html = dieu_html.parent.find_next("p", {"class": "pNoiDung"})
                    noidung = ""
                    tables = []
                    files = []
                    dieus_lienquan = []

                    for content in noidung_html.contents:
                        if content.name == "table":
                            tables.append(str(content))
                            continue
                        noidung += str(content.text.strip()) + "\n"

                    element = noidung_html.next_sibling
                    while element and element.name == "a":
                        link = element["href"]
                        files.append(link)
                        element = element.next_sibling

                    if element and element.name == "p" and element.get("class", []) and element["class"][0] == "pChiDan":
                        lienquans_html = element.select("a")
                        for lienquan_html in lienquans_html:
                            if "onclick" not in lienquan_html.attrs or not lienquan_html["onclick"]:
                                continue
                            mapc_lienquan = extract_input(lienquan_html["onclick"]).replace("'", "")
                            dieus_lienquan.append({"dieu_id": mapc, "dieu_id_lienquan": mapc_lienquan})

                    dieu_obj = PDDieu(
                        ten=ten, mapc=mapc, chimuc=chimuc, stt=stt,
                        noidung=noidung, vbqppl=vbqppl, vbqppl_link=vbqppl_link,
                        demuc_id=dieu["DeMucID"], chude_id=dieu["ChuDeID"], chuong_id=dieu["ChuongID"]
                    )
                    db.add(dieu_obj)

                    table_objects = [PDTable(dieu_id=mapc, html=table) for table in tables]
                    db.add_all(table_objects)

                    file_objects = [PDFile(dieu_id=mapc, link=file, path="") for file in files]
                    db.add_all(file_objects)

                    all_dieus_lienquan.extend(dieus_lienquan)
                    stt += 1
                
                try:
                    db.commit()
                    print(f"Inserted PDDieu, PDTable, PDFile cho đề mục {file_name}")
                except Exception as e:
                    print(f"Error inserting PDDieu/PDTable/PDFile: {e}")
                    save_checkpoint(file_name)
                    db.rollback()
                    continue

                lienquan_objects = [
                    PDMucLienQuan(dieu_id=d["dieu_id"], dieu_id_lienquan=d["dieu_id_lienquan"])
                    for d in all_dieus_lienquan
                    if db.query(PDDieu).filter(PDDieu.mapc == d["dieu_id_lienquan"]).first()
                ]
                db.add_all(lienquan_objects)

                try:
                    db.commit()
                    print(f"Inserted PDMucLienQuan cho đề mục {file_name}")
                except Exception as e:
                    print(f"Error inserting PDMucLienQuan: {e}")
                    save_checkpoint(file_name)
                    db.rollback()

            except Exception as e:
                print(f"Error processing {file_name}: {e}")
                save_checkpoint(file_name)
                db.rollback()

print("Inserted tất cả nodes pháp điển!")