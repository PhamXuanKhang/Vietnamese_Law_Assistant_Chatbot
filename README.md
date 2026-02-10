# Vietnamese Law Assistant Chatbot

Hệ thống chatbot hỗ trợ tư vấn pháp luật Việt Nam sử dụng AI, tập trung vào chủ đề **Trật tự, An toàn xã hội** từ Bộ Pháp điển điện tử. Dự án cung cấp 2 phiên bản chatbot với các kỹ thuật AI khác nhau để tra cứu và giải đáp các câu hỏi về luật pháp một cách chính xác và nhanh chóng.

## 📋 Giới thiệu

**Vietnamese Law Assistant Chatbot** được phát triển bởi **Team CuliData**, nhằm:
- Cung cấp thông tin pháp lý chính xác dựa trên văn bản luật trong pháp điển
- Hỗ trợ người dùng tìm kiếm và hiểu các điều luật liên quan
- Tăng cường khả năng tiếp cận pháp luật thông qua công nghệ AI

## ✨ Tính năng chính

### Hệ thống Backend
- **Crawl dữ liệu tự động** từ Bộ Pháp điển điện tử
- **Lưu trữ có cấu trúc** trong MySQL với các bảng: Chủ đề, Đề mục, Chương, Điều luật, Bảng biểu, File đính kèm, Mục liên quan
- **Vector database** (Weaviate) để tìm kiếm ngữ nghĩa
- **FastAPI** với streaming response cho trải nghiệm real-time

### Chatbot Version 1.0 - RAG với Semantic Routing
- **Semantic Router**: Phân loại câu hỏi (luật pháp vs. câu hỏi chung)
- **Reflection**: Tinh chỉnh câu hỏi dựa trên ngữ cảnh hội thoại
- **RAG (Retrieval-Augmented Generation)**: Tìm kiếm vector similarity và sinh câu trả lời
- **Nguồn tham khảo**: Hiển thị link đến văn bản pháp luật gốc

### Chatbot Version 2.0 - NER-based Retrieval
- **Named Entity Recognition (NER)**: Trích xuất thực thể pháp lý từ câu hỏi bằng BiLSTM
- **Entity-based Retrieval**: Tìm kiếm dựa trên thực thể được nhận diện
- **Multi-retrieval**: Kết hợp nhiều nguồn thông tin
- **Gemini 2.0 Flash**: Sử dụng LLM mới nhất của Google

### Giao diện người dùng
- **Streamlit UI**: Giao diện web thân thiện, dễ sử dụng
- **Chat streaming**: Hiển thị câu trả lời theo thời gian thực
- **Multi-version support**: Chuyển đổi giữa 2 phiên bản chatbot
- **Session management**: Lưu lịch sử hội thoại

## 🏗️ Kiến trúc hệ thống

```
┌─────────────────┐
│  Streamlit UI   │
│  (user_interface)│
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   FastAPI       │
│  (fastAPI.py)   │
└────┬───────┬────┘
     │       │
     ▼       ▼
┌─────────┐ ┌─────────┐
│Chatbot  │ │Chatbot  │
│  V1     │ │  V2     │
└────┬────┘ └────┬────┘
     │           │
     ▼           ▼
┌─────────────────────┐
│  MySQL + Weaviate   │
│  (Database Layer)   │
└─────────────────────┘
```

## 📁 Cấu trúc dự án

```
Vietnamese_Law_Assistant_Chatbot/
│
├── chatbot_v1/                      # Chatbot Version 1.0 (RAG + Semantic Routing)
│   ├── src/
│   │   ├── crawl_and_insert_to_db/  # Module crawl và lưu dữ liệu
│   │   │   ├── main.py              # Logic crawl HTML từ pháp điển
│   │   │   ├── models.py            # SQLAlchemy models (PDChuDe, PDDeMuc, PDChuong, PDDieu...)
│   │   │   ├── db.py                # Database connection
│   │   │   └── utils.py             # Utilities (convert roman, extract...)
│   │   │
│   │   ├── embedding/               # Module xử lý embedding
│   │   │   ├── main.py              # Tạo embeddings cho dữ liệu
│   │   │   ├── preprocessing.py     # Tiền xử lý văn bản tiếng Việt
│   │   │   └── load_embedding_model.py
│   │   │
│   │   ├── LLM_response/            # Module xử lý phản hồi
│   │   │   ├── main.py              # Pipeline chính (routing → reflection → retrieval → generation)
│   │   │   ├── semantic_router.py   # Phân loại câu hỏi
│   │   │   ├── reflection.py        # Tinh chỉnh câu hỏi
│   │   │   ├── retriever.py         # Tìm kiếm vector similarity
│   │   │   ├── LLM_generator.py     # Sinh câu trả lời
│   │   │   └── route_sample.py      # Dữ liệu mẫu cho routing
│   │   │
│   │   └── evaluation/              # Module đánh giá
│   │
│   ├── BoPhapDienDienTu/            # Dữ liệu pháp điển gốc
│   │   ├── ChuDe.json               # Danh sách chủ đề
│   │   ├── DeMuc.json               # Danh sách đề mục
│   │   ├── TreeNode.json            # Cấu trúc cây
│   │   └── demuc/                   # 39 file HTML (1.html → 39.html)
│   │
│   ├── weaviate-docker/             # Cấu hình Weaviate
│   │   └── docker-compose.yml
│   │
│   └── requirements.txt
│
├── chatbot_v2/                      # Chatbot Version 2.0 (NER-based)
│   ├── Code/
│   │   ├── main.py                  # Pipeline chính (NER → retrieval → generation)
│   │   ├── NER/                     # Named Entity Recognition
│   │   │   ├── ner.py               # BiLSTM NER model
│   │   │   ├── bilstm_ner.pt        # Pretrained model (~2.6MB)
│   │   │   └── ner_data_8000.json   # Training data (~3.1MB)
│   │   │
│   │   ├── retrieve/                # Multi-retrieval system
│   │   ├── embedding/               # Embedding cho V2
│   │   ├── save_database/           # Database utilities
│   │   └── create_relation/         # Xử lý quan hệ giữa các điều luật
│   │
│   ├── database/                    # Database cho V2
│   └── requirements.txt
│
├── user_interface/                  # Giao diện Streamlit
│   ├── Home.py                      # Trang chủ
│   ├── pages/
│   │   ├── Vietnamese_Law_Assistant_Chatbot_v1.py
│   │   └── Vietnamese_Law_Assistant_Chatbot_v2.py
│   ├── logo.png
│   └── requirements.txt
│
├── fastAPI.py                       # FastAPI server (endpoints: /v1/chat, /v2/chat)
├── .env                             # Environment variables
└── README.md
```

## 🔧 Yêu cầu hệ thống

- **Python**: 3.8+
- **MySQL**: 8.0+
- **Docker & Docker Compose**: Để chạy Weaviate
- **Google API Key**: Cho Google Gemini LLM
- **RAM**: Tối thiểu 8GB
- **Ổ cứng**: Tối thiểu 10GB trống

## 🚀 Cài đặt

### 1. Clone repository
```bash
git clone https://github.com/PhamXuanKhang/Vietnamese_Law_Assistant_Chatbot.git
cd Vietnamese_Law_Assistant_Chatbot
```

### 2. Tạo môi trường ảo
```bash
python -m venv myenv
myenv\Scripts\activate     # Windows
source myenv/bin/activate  # Linux/Mac
```

### 3. Cài đặt dependencies
```bash
# Cài đặt cho chatbot_v1
pip install -r chatbot_v1/requirements.txt

# Cài đặt cho chatbot_v2
pip install -r chatbot_v2/requirements.txt

# Cài đặt cho user interface
pip install -r user_interface/requirements.txt

# Cài đặt FastAPI
pip install fastapi uvicorn
```

### 4. Cấu hình file .env
Tạo file `.env` trong thư mục gốc:
```env
# Database configuration
DB_USER=your_username
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=3306
DB_NAME=phap_dien_db

# Weaviate configuration
WEAVIATE_HOST=localhost
WEAVIATE_PORT=8080

# Google API Key
API_KEY=your_google_api_key

# Application configuration
APP_HOST=0.0.0.0
APP_PORT=8000
```

### 5. Khởi động Weaviate
```bash
cd chatbot_v1/weaviate-docker
docker-compose up -d
```

### 6. Tạo database MySQL
```sql
CREATE DATABASE phap_dien_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

## 📊 Database Schema

### pd_chude (Chủ đề)
```sql
CREATE TABLE pd_chude (
    id VARCHAR(128) PRIMARY KEY,
    ten TEXT,
    stt INT
);
```

### pd_demuc (Đề mục)
```sql
CREATE TABLE pd_demuc (
    id VARCHAR(128) PRIMARY KEY,
    ten TEXT,
    stt INT,
    chude_id VARCHAR(128),
    FOREIGN KEY (chude_id) REFERENCES pd_chude(id)
);
```

### pd_chuong (Chương)
```sql
CREATE TABLE pd_chuong (
    mapc VARCHAR(128) PRIMARY KEY,
    ten TEXT,
    demuc_id VARCHAR(128),
    chimuc TEXT,
    stt INT,
    FOREIGN KEY (demuc_id) REFERENCES pd_demuc(id)
);
```

### pd_dieu (Điều luật)
```sql
CREATE TABLE pd_dieu (
    mapc VARCHAR(128) PRIMARY KEY,
    ten TEXT,
    noidung TEXT,
    chimuc TEXT,
    vbqppl TEXT,
    vbqppl_link TEXT,
    stt INT,
    demuc_id VARCHAR(128),
    chuong_id VARCHAR(128),
    chude_id VARCHAR(128),
    FOREIGN KEY (demuc_id) REFERENCES pd_demuc(id),
    FOREIGN KEY (chuong_id) REFERENCES pd_chuong(mapc),
    FOREIGN KEY (chude_id) REFERENCES pd_chude(id)
);
```

### pd_table (Bảng biểu)
```sql
CREATE TABLE pd_table (
    id INT PRIMARY KEY AUTO_INCREMENT,
    dieu_id VARCHAR(128),
    html TEXT,
    FOREIGN KEY (dieu_id) REFERENCES pd_dieu(mapc)
);
```

### pd_file (File đính kèm)
```sql
CREATE TABLE pd_file (
    id INT PRIMARY KEY AUTO_INCREMENT,
    dieu_id VARCHAR(128),
    link TEXT,
    path TEXT,
    FOREIGN KEY (dieu_id) REFERENCES pd_dieu(mapc)
);
```

### pd_muclienquan (Mục liên quan)
```sql
CREATE TABLE pd_muclienquan (
    dieu_id VARCHAR(128),
    dieu_id_lienquan VARCHAR(128),
    PRIMARY KEY (dieu_id, dieu_id_lienquan),
    FOREIGN KEY (dieu_id) REFERENCES pd_dieu(mapc),
    FOREIGN KEY (dieu_id_lienquan) REFERENCES pd_dieu(mapc)
);
```

## 💻 Sử dụng

### Bước 1: Crawl dữ liệu (chỉ chạy lần đầu)
```bash
python -m chatbot_v1.src.crawl_and_insert_to_db.main
```
Script này sẽ:
- Đọc file JSON (ChuDe.json, DeMuc.json, TreeNode.json)
- Parse 39 file HTML từ thư mục `demuc/`
- Insert vào MySQL: Chủ đề → Đề mục → Chương → Điều luật → Bảng/File/Mục liên quan
- Lưu checkpoint để tiếp tục nếu bị gián đoạn

### Bước 2: Tạo embeddings (chỉ chạy lần đầu)
```bash
python -m chatbot_v1.src.embedding.main
```
Script này sẽ:
- Đọc dữ liệu từ MySQL
- Tiền xử lý văn bản tiếng Việt
- Tạo embeddings bằng Sentence Transformers
- Lưu vào Weaviate vector database

### Bước 3: Khởi động FastAPI server
```bash
python fastAPI.py
```
Server sẽ chạy tại `http://localhost:8000` với 2 endpoints:
- `POST /v1/chat` - Chatbot V1 (RAG + Semantic Routing)
- `POST /v2/chat` - Chatbot V2 (NER-based)

### Bước 4: Khởi động Streamlit UI
```bash
cd user_interface
streamlit run Home.py
```
Truy cập `http://localhost:8501` để sử dụng giao diện web.

## 🔄 Quy trình hoạt động

### Chatbot V1 - RAG với Semantic Routing
```
User Input
    ↓
Semantic Router (phân loại: law/chitchat)
    ↓
[Nếu law]
    ↓
Reflection (tinh chỉnh câu hỏi dựa trên context)
    ↓
Retriever (tìm kiếm vector similarity trong Weaviate)
    ↓
LLM Generator (sinh câu trả lời + nguồn tham khảo)
    ↓
Stream Response
```

### Chatbot V2 - NER-based Retrieval
```
User Input
    ↓
NER Model (BiLSTM) - trích xuất thực thể pháp lý
    ↓
Multi-Retrieval (tìm kiếm dựa trên entities)
    ↓
Gemini 2.0 Flash (sinh câu trả lời)
    ↓
Stream Response
```

## 🛠️ Công nghệ sử dụng

### Backend
- **FastAPI**: Web framework cho API
- **SQLAlchemy**: ORM cho MySQL
- **PyMySQL**: MySQL driver
- **BeautifulSoup4**: Parse HTML
- **python-dotenv**: Quản lý environment variables

### AI/ML
- **LangChain**: Framework cho LLM applications
- **Google Gemini**: LLM (gemini-2.0-flash)
- **Sentence Transformers**: Tạo embeddings
- **PyTorch**: Deep learning framework cho NER
- **PyVi**: Xử lý tiếng Việt

### Database
- **MySQL 8.0**: Relational database
- **Weaviate**: Vector database

### Frontend
- **Streamlit**: Web UI framework
- **Requests**: HTTP client

### DevOps
- **Docker**: Container cho Weaviate
- **Docker Compose**: Orchestration

## 📡 API Documentation

### POST /v1/chat
**Request Body:**
```json
{
  "message": "Tôi có thể bị phạt bao nhiêu nếu vượt đèn đỏ?",
  "context": [
    {"role": "user", "content": "..."},
    {"role": "assistant", "content": "..."}
  ],
  "sessionId": "uuid-string",
  "stream": true
}
```

**Response:** Streaming text/plain hoặc JSON

### POST /v2/chat
**Request Body:** Giống `/v1/chat`

**Response:** Streaming text/plain hoặc JSON

## 📈 So sánh 2 phiên bản

| Tiêu chí | Chatbot V1 | Chatbot V2 |
|----------|-----------|-----------|
| **Kỹ thuật chính** | RAG + Semantic Routing | NER + Entity-based Retrieval |
| **Routing** | Semantic Router | Không có |
| **Query refinement** | Reflection | Không có |
| **Entity extraction** | Không có | BiLSTM NER |
| **LLM** | Google Gemini | Google Gemini 2.0 Flash |
| **Retrieval** | Vector similarity | Entity-based + Multi-retrieval |
| **Nguồn tham khảo** | Có (với link) | Có (với metadata) |
| **Phù hợp** | Câu hỏi chung, cần context | Câu hỏi cụ thể, có thực thể pháp lý |

## 🎯 Ví dụ sử dụng

**Câu hỏi mẫu:**
- "Tôi có thể bị phạt bao nhiêu nếu vượt đèn đỏ?"
- "Quy định về hành vi gây rối trật tự công cộng là gì?"
- "Mức phạt cho hành vi say rượu lái xe?"
- "Điều kiện để được cấp giấy phép kinh doanh?"

## 👥 Đội ngũ phát triển

**Team CuliData** - Nhóm sinh viên đam mê ứng dụng công nghệ vào lĩnh vực luật pháp

## 📝 License

Dự án này được phát triển cho mục đích học tập và nghiên cứu.

## 🔗 Liên hệ

- **GitHub**: [PhamXuanKhang/Vietnamese_Law_Assistant_Chatbot](https://github.com/PhamXuanKhang/Vietnamese_Law_Assistant_Chatbot)
- **Email**: contact@culidata.com

---

**Lưu ý**: Chatbot chỉ cung cấp thông tin tham khảo từ pháp điển. Để có tư vấn pháp lý chính thức, vui lòng liên hệ luật sư hoặc cơ quan có thẩm quyền.
