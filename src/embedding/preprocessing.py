from langchain_experimental.text_splitter import SemanticChunker
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document
from transformers import AutoTokenizer
from sqlalchemy import text
from crawl_and_insert_to_db.db import engine
from pyvi.ViTokenizer import tokenize
import csv
import os
import re
from dotenv import load_dotenv
from tqdm import tqdm

# Truy vấn dữ liệu
query = "select mapc, noidung, vbqppl, vbqppl_link" \
"        from pd_dieu join pd_chude on pd_dieu.chude_id = pd_chude.id" \
"        where pd_chude.stt = '39';"
with engine.connect() as connection:
    result = connection.execute(text(query))
    rows = result.fetchall()
    columns = result.keys()


# Tải model embedding và text splitter
embedding_model = HuggingFaceEmbeddings(model_name="dangvantuan/vietnamese-embedding")
tokenizer = AutoTokenizer.from_pretrained("dangvantuan/vietnamese-embedding")

# Hàm đếm token
def count_tokens(text):
    return len(tokenizer.encode(text))

semantic_text_splitter = SemanticChunker(embedding_model, breakpoint_threshold_type="percentile",breakpoint_threshold_amount=75)
recursive_text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50,
    length_function=count_tokens,
    is_separator_regex=True,
)

# Tách văn bản và lưu vào danh sách
def document_splitter(is_semantic_chunk):
    processed_data = []
    for row in tqdm(rows):
        row_dict = dict(zip(columns, row))
        raw_noidung = re.sub(r'[^\S ]+', ' ', row_dict['noidung'])

        vbqppl = row_dict.get('vbqppl', '')
        raw_content = f"{vbqppl} - {raw_noidung}"
        processed_content = re.sub(r'_+', '_', tokenize(raw_content))

        content = Document(page_content=processed_content)
        chunks = recursive_text_splitter.create_documents([content.page_content])

        if is_semantic_chunk:
            schunk_data = []
            for chunk in chunks:
                semantic_chunks = semantic_text_splitter.create_documents([chunk.page_content])
                schunk_data.extend(semantic_chunks)
            chunks = schunk_data
            
        for chunk in chunks:
            chunk_entry = {
                'noidung': chunk.page_content,
                'mapc': row_dict.get('mapc', None),
                'vbqppl': row_dict.get('vbqppl', None),
                'vbqppl_link': row_dict.get('vbqppl_link', None),
            }
            processed_data.append(chunk_entry)
    return processed_data

# Lưu vào file CSV
def save_to_csv(processed_data, csv_file):
    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['noidung', 'mapc', 'vbqppl', 'vbqppl_link']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(processed_data)


semantic_chunk_data = document_splitter(True)
semantic_csv_file = './src/embedding/semantic_chunks_output.csv'
save_to_csv(semantic_chunk_data, semantic_csv_file)
print(f"Đã lưu {len(semantic_chunk_data)} chunk bằng semantic chunker vào {semantic_csv_file}")

recursive_chunk_data = document_splitter(False)
recursive_csv_file = './src/embedding/recursive_chunks_output.csv'
save_to_csv(recursive_chunk_data, recursive_csv_file)
print(f"Đã lưu {len(recursive_chunk_data)} chunk bằng recursive chunker vào {recursive_csv_file}")