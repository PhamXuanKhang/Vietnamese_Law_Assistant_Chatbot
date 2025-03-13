from langchain.text_splitter import TokenTextSplitter
from sqlalchemy import create_engine, text
import csv
import os
from dotenv import load_dotenv

# Load biến môi trường từ file .env
load_dotenv(".env")
user = os.getenv('DB_USER')
password = os.getenv('DB_PASSWORD')
host = os.getenv('DB_HOST')
port = os.getenv('DB_PORT')
db_name = os.getenv('DB_NAME')

# Chuỗi kết nối SQL
connection_string = f"mysql+pymysql://{user}:{password}@{host}:{port}/{db_name}?charset=utf8mb4"
engine = create_engine(connection_string)

# Truy vấn dữ liệu
query = "select mapc, noidung, pd_dieu.ten" \
"        from pd_dieu join pd_chude on pd_dieu.chude_id = pd_chude.id" \
"        where pd_chude.stt = '39';"
with engine.connect() as connection:
    result = connection.execute(text(query))
    rows = result.fetchall()
    columns = result.keys()

# Khởi tạo splitter
splitter = TokenTextSplitter(
    chunk_size=500,
    chunk_overlap=50
)

# Tách văn bản và lưu vào danh sách
chunked_data = []
for row in rows:
    row_dict = dict(zip(columns, row))
    content = row_dict['noidung']
    chunks = splitter.split_text(content)
    
    for i, chunk in enumerate(chunks):
        chunk_entry = {
            'noidung': chunk,
            'mapc': row_dict.get('mapc', None),
            'chunk_index': i,
            'ten': row_dict.get('ten', None),
        }
        chunked_data.append(chunk_entry)

# Lưu vào file CSV
csv_file = './src/embedding/chunks_output.csv'
with open(csv_file, 'w', newline='', encoding='utf-8') as f:
    fieldnames = ['noidung', 'mapc', 'chunk_index', 'ten']
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(chunked_data)

print(f"Đã lưu {len(chunked_data)} chunk vào {csv_file}")