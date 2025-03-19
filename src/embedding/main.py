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

csv_file = './src/embedding/recursive_chunks_output.csv'
chunked_data = []
with open(csv_file, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        row['mapc'] = row['mapc'] or ""
        row['vbqppl'] = row['vbqppl'] or ""
        row['noidung'] = row['noidung'] or ""
        row['vbqppl_link'] = row['vbqppl_link'] or ""
        chunked_data.append(row)

collection = client.collections.get("Chunk")

with collection.batch.dynamic() as batch:
    for i, entry in tqdm(enumerate(chunked_data)):
        tokenized_content = tokenize(entry['noidung'])
        embedding = model.encode(tokenized_content).tolist()
        
        chunk_obj = {
            "noidung": entry['noidung'],
            "mapc": entry['mapc'],
            "vbqppl": entry['vbqppl'],
            "vbqppl_link": entry['vbqppl_link']
        }
        
        batch.add_object(
            properties=chunk_obj,
            vector=embedding,
            uuid=generate_uuid5(entry['mapc'] + str(i))
        )

if len(collection.batch.failed_objects) > 0:
    print(f"Failed to import {len(collection.batch.failed_objects)} objects")
else:
    print(f"Đã nhúng và lưu {len(chunked_data)} chunk vào Weaviate!")

client.close()