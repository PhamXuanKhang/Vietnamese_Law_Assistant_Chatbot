from pyvi.ViTokenizer import tokenize
import csv
import weaviate
from .load_embedding_model import model1, model2
from weaviate.util import generate_uuid5
from tqdm import tqdm
from dotenv import load_dotenv
import os

load_dotenv()
host = os.getenv("VECTOR_DB_HOST")
port = os.getenv("VECTOR_DB_PORT")

# Kết nối weaviate server
client = weaviate.connect_to_local(
    host=host,
    port=port
)

# Hàm embedding vào db
def import_to_vector_db(csv_file, model, collection_name, is_model1):
    data = []
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            row['mapc'] = row['mapc'] or ""
            row['vbqppl'] = row['vbqppl'] or ""
            row['noidung'] = row['noidung'] or ""
            row['vbqppl_link'] = row['vbqppl_link'] or ""
            row['ten_demuc'] = row['ten_demuc'] or ""
            row['ten_chude'] = row['ten_chude'] or ""
            row['ten_chuong'] = row['ten_chuong'] or ""
            data.append(row)

    collection = client.collections.get(collection_name)

    with collection.batch.dynamic() as batch:
        for i, entry in tqdm(enumerate(data)):
            if is_model1:
                tokenized_content = tokenize(entry['noidung'])
            else:
                tokenized_content = entry['noidung']
            embedding = model.encode(tokenized_content).tolist()
            
            chunk_obj = {
                "noidung": entry['noidung'],
                "mapc": entry['mapc'],
                "vbqppl": entry['vbqppl'],
                "vbqppl_link": entry['vbqppl_link'],
                "ten_demuc": entry['ten_demuc'],
                "ten_chude": entry['ten_chude'],
                "ten_chuong": entry['ten_chuong']
            }
            
            batch.add_object(
                properties=chunk_obj,
                vector=embedding,
                uuid=generate_uuid5(entry['mapc'] + str(i))
            )

    if len(collection.batch.failed_objects) > 0:
        print(f"Failed to import {len(collection.batch.failed_objects)} objects")
    else:
        print(f"Đã nhúng và lưu {len(data)} chunk vào Weaviate!")


csv_file = './chatbot_v1/data/chunking/non_chunk_output.csv'
import_to_vector_db(csv_file, model2, 'non_chunk_data2', False)
client.close()