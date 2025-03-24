from langchain_experimental.text_splitter import SemanticChunker
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document
from transformers import AutoTokenizer
from sqlalchemy import text
from src.crawl_and_insert_to_db.db import engine
from pyvi.ViTokenizer import tokenize
import csv
import os
import re
from dotenv import load_dotenv
from tqdm import tqdm

# Truy vấn dữ liệu từ MySQL để lấy thông tin trong chủ đề 39
query = "select pd_dieu.mapc, pd_dieu.noidung, pd_dieu.vbqppl, pd_dieu.vbqppl_link," \
"        pd_demuc.ten as ten_demuc, pd_chude.ten as ten_chude, pd_chuong.ten as ten_chuong" \
"        from pd_dieu join pd_chuong on pd_dieu.chuong_id = pd_chuong.mapc" \
"        join pd_demuc on pd_dieu.demuc_id = pd_demuc.id" \
"        join pd_chude on pd_dieu.chude_id = pd_chude.id" \
"        where pd_chude.stt = '39'"
with engine.connect() as connection:
    result = connection.execute(text(query))
    rows = result.fetchall()
    columns = result.keys()

# # Tải model embedding và text splitter
# embedding_model_1 = HuggingFaceEmbeddings(model_name="dangvantuan/vietnamese-embedding", cache_folder="./models")
# tokenizer_1 = AutoTokenizer.from_pretrained("dangvantuan/vietnamese-embedding", cache_dir="./models")

# embedding_model_2 = HuggingFaceEmbeddings(model_name="AITeamVN/Vietnamese_Embedding", cache_folder="./models")
# tokenizer_2 = AutoTokenizer.from_pretrained("AITeamVN/Vietnamese_Embedding", cache_dir="./models")

# # Hàm đếm token
# def count_token_1(text):
#     return len(tokenizer_1.encode(text))
# def count_token_2(text):
#     return len(tokenizer_2.encode(text))

# semantic_text_splitter_1 = SemanticChunker(embedding_model_1, breakpoint_threshold_type="percentile",breakpoint_threshold_amount=75)
# semantic_text_splitter_2 = SemanticChunker(embedding_model_2, breakpoint_threshold_type="percentile",breakpoint_threshold_amount=75)

# recursive_text_splitter_1 = RecursiveCharacterTextSplitter(
#     chunk_size=450,
#     chunk_overlap=50,
#     length_function=count_token_1,
#     is_separator_regex=True,
# )
# recursive_text_splitter_2 = RecursiveCharacterTextSplitter(
#     chunk_size=1950,
#     chunk_overlap=50,
#     length_function=count_token_1,
#     is_separator_regex=True,
# )

# # Tách văn bản và lưu vào danh sách
# def document_splitter(is_semantic_chunk, recursive_text_splitter, semantic_text_splitter, is_embedding_1):
#     processed_data = []
#     for row in tqdm(rows):
#         row_dict = dict(zip(columns, row))
#         raw_noidung = re.sub(r'[^\S ]+', ' ', row_dict['noidung'])

#         if is_embedding_1:
#             processed_content = re.sub(r'_+', '_', tokenize(raw_noidung))
#         else:
#             processed_content = raw_noidung

#         content = Document(page_content=processed_content)
#         chunks = recursive_text_splitter.create_documents([content.page_content])

#         if is_semantic_chunk:
#             schunk_data = []
#             for chunk in chunks:
#                 semantic_chunks = semantic_text_splitter.create_documents([chunk.page_content])
#                 schunk_data.extend(semantic_chunks)
#             chunks = schunk_data
            
#         for chunk in chunks:
#             chunk_entry = {
#                 'noidung': chunk.page_content,
#                 'mapc': row_dict.get('mapc', None),
#                 'vbqppl': row_dict.get('vbqppl', None),
#                 'vbqppl_link': row_dict.get('vbqppl_link', None),
#                 'ten_demuc': row_dict.get('ten_demuc', None),
#                 'ten_chude': row_dict.get('ten_chude', None),
#                 'ten_chuong': row_dict.get('ten_chuong', None)
#             }
#             processed_data.append(chunk_entry)
#     return processed_data

# Lưu vào file CSV
def save_to_csv(processed_data, csv_file):
    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['noidung', 'mapc', 'vbqppl', 'vbqppl_link', 'ten_demuc', 'ten_chude', 'ten_chuong']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(processed_data)


# semantic_chunk_data_1 = document_splitter(True, recursive_text_splitter_1, semantic_text_splitter_1,
#                                           is_embedding_1=True)
# semantic_csv_file_1 = './data/chunking/semantic_chunks_output_1.csv'
# save_to_csv(semantic_chunk_data_1, semantic_csv_file_1)
# print(f"Đã lưu {len(semantic_chunk_data_1)} chunk bằng semantic chunker vào {semantic_csv_file_1}")


# semantic_chunk_data_2 = document_splitter(True, recursive_text_splitter_2, semantic_text_splitter_2,
#                                        is_embedding_1=False)
# semantic_csv_file_2 = './data/chunking/semantic_chunks_output_2.csv'
# save_to_csv(semantic_chunk_data_2, semantic_csv_file_2)
# print(f"Đã lưu {len(semantic_chunk_data_2)} chunk bằng semantic chunker vào {semantic_csv_file_2}")


# recursive_chunk_data_1 = document_splitter(False, recursive_text_splitter_1, semantic_text_splitter_1,
#                                          is_embedding_1=True)
# recursive_csv_file_1 = './data/chunking/recursive_chunks_output.csv'
# save_to_csv(recursive_chunk_data_1, recursive_csv_file_1)
# print(f"Đã lưu {len(recursive_chunk_data_1)} chunk bằng recursive chunker vào {recursive_csv_file_1}")


# recursive_chunk_data_2 = document_splitter(False, recursive_text_splitter_2, semantic_text_splitter_2,
#                                          is_embedding_1=False)
# recursive_csv_file_2 = './data/chunking/recursive_chunks_output_2.csv'
# save_to_csv(recursive_chunk_data_2, recursive_csv_file_2)
# print(f"Đã lưu {len(recursive_chunk_data_2)} chunk bằng recursive chunker vào {recursive_csv_file_2}")


non_chunk_data = []
for row in tqdm(rows):
    row_dict = dict(zip(columns, row))
    raw_noidung = re.sub(r'[^\S ]+', ' ', row_dict['noidung'])
    chunk_entry = {
        'noidung': raw_noidung,
        'mapc': row_dict.get('mapc', None),
        'vbqppl': row_dict.get('vbqppl', None),
        'vbqppl_link': row_dict.get('vbqppl_link', None),
        'ten_demuc': row_dict.get('ten_demuc', None),
        'ten_chude': row_dict.get('ten_chude', None),
        'ten_chuong': row_dict.get('ten_chuong', None)
    }
    non_chunk_data.append(chunk_entry)

csv_file = './chatbot_v1/data/chunking/non_chunk_output.csv'
save_to_csv(non_chunk_data, csv_file)
print(f"Đã lưu {len(non_chunk_data)} chunk vào {csv_file}")