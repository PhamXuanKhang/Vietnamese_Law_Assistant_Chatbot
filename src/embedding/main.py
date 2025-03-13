from sentence_transformers import SentenceTransformer
from pyvi.ViTokenizer import tokenize
import csv
import weaviate
from weaviate.util import generate_uuid5
from tqdm import tqdm

client = weaviate.connect_to_local(
    host="localhost",
    port=8080
)

model = SentenceTransformer('dangvantuan/vietnamese-embedding')

csv_file = './src/embedding/chunks_output.csv'
chunked_data = []
with open(csv_file, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        row['mapc'] = row['mapc'] or ""
        row['chunk_index'] = int(row['chunk_index']) if row['chunk_index'] and row['chunk_index'] != '' else 0
        row['noidung'] = row['noidung'] or ""
        row['ten'] = row['ten'] or ""
        chunked_data.append(row)

collection = client.collections.get("Chunk")

with collection.batch.dynamic() as batch:
    for entry in tqdm(chunked_data):
        tokenized_content = tokenize(entry['noidung'])
        embedding = model.encode(tokenized_content).tolist()
        
        chunk_obj = {
            "noidung": entry['noidung'],
            "mapc": entry['mapc'],
            "chunk_index": entry['chunk_index'],
            "ten": entry['ten']
        }
        
        batch.add_object(
            properties=chunk_obj,
            vector=embedding,
            uuid=generate_uuid5(entry['mapc'] + str(entry['chunk_index']))
        )

if len(collection.batch.failed_objects) > 0:
    print(f"Failed to import {len(collection.batch.failed_objects)} objects")
else:
    print(f"Đã nhúng và lưu {len(chunked_data)} chunk vào Weaviate!")

client.close()