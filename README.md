# Vietnamese Law Assistant Chatbot

Chatbot hỗ trợ tìm kiếm và trả lời câu hỏi về luật pháp Việt Nam, sử dụng dữ liệu từ Bộ Pháp điển điện tử. Dự án này giúp người dùng dễ dàng tìm kiếm và hiểu các quy định pháp luật thông qua giao diện chat thân thiện.

## Giới thiệu

**Vietnamese Law Assistant Chatbot** là một dự án được phát triển bởi **Team CuliData**, nhằm hỗ trợ người dùng tại Việt Nam tra cứu và tư vấn pháp luật một cách nhanh chóng và chính xác.

### Mục tiêu của chúng tôi:
- Cung cấp thông tin pháp lý chính xác dựa trên các văn bản luật trong pháp điển (chủ đề trật tự, an toàn xã hội)
- Hỗ trợ người dùng tìm kiếm và hiểu các điều luật liên quan đến vấn đề của họ
- Tăng cường khả năng tiếp cận pháp luật thông qua công nghệ AI

## Tính năng

- Crawl và lưu trữ dữ liệu từ Bộ Pháp điển điện tử
- Tìm kiếm thông tin luật pháp thông minh sử dụng vector similarity
- Trả lời câu hỏi tự động sử dụng Large Language Model (LLM)
- Hỗ trợ tiếng Việt
- Giao diện web thân thiện với người dùng
- Tìm kiếm theo chủ đề, đề mục, chương
- Hiển thị các điều luật liên quan
- Hỗ trợ tìm kiếm nâng cao với bộ lọc
- Xuất kết quả tìm kiếm dưới dạng PDF

## Cấu trúc dự án

```
chatbot_v1/
├── src/                          # Mã nguồn
│   ├── crawl_and_insert_to_db/  # Code crawl và lưu dữ liệu
│   │   ├── __init__.py
│   │   ├── main.py              # File chính chứa logic crawl
│   │   ├── models.py            # Định nghĩa cấu trúc database
│   │   ├── db.py                # Xử lý kết nối database
│   │   ├── utils.py             # Các hàm tiện ích
│   │   └── checkpoint.txt       # Lưu trạng thái crawl
│   │
│   ├── embedding/               # Xử lý embedding
│   │   ├── __init__.py
│   │   ├── embedding.py         # Code tạo embedding
│   │   └── vector_store.py      # Lưu trữ vector
│   │
│   ├── LLM_response/           # Xử lý phản hồi từ LLM
│   │   ├── __init__.py
│   │   ├── llm.py              # Tích hợp với LLM
│   │   └── response.py         # Xử lý phản hồi
│   │
│   ├── eda_analysis.py         # Phân tích dữ liệu
│   └── eda_chude39.py          # Phân tích chủ đề 39
│
├── data/                       # Dữ liệu
│   ├── embeddings/            # Lưu trữ embeddings
│   └── processed/             # Dữ liệu đã xử lý
│
├── BoPhapDienDienTu/         # Dữ liệu gốc từ pháp điển
│   ├── ChuDe.json           # Dữ liệu chủ đề
│   ├── DeMuc.json           # Dữ liệu đề mục
│   ├── TreeNode.json        # Cấu trúc cây dữ liệu
│   └── demuc/               # Thư mục chứa file HTML
│       ├── 1.html
│       ├── 2.html
│       ├── 3.html
│       ├── 4.html
│       ├── 5.html
│       ├── 6.html
│       ├── 7.html
│       ├── 8.html
│       ├── 9.html
│       ├── 10.html
│       ├── 11.html
│       ├── 12.html
│       ├── 13.html
│       ├── 14.html
│       ├── 15.html
│       ├── 16.html
│       ├── 17.html
│       ├── 18.html
│       ├── 19.html
│       ├── 20.html
│       ├── 21.html
│       ├── 22.html
│       ├── 23.html
│       ├── 24.html
│       ├── 25.html
│       ├── 26.html
│       ├── 27.html
│       ├── 28.html
│       ├── 29.html
│       ├── 30.html
│       ├── 31.html
│       ├── 32.html
│       ├── 33.html
│       ├── 34.html
│       ├── 35.html
│       ├── 36.html
│       ├── 37.html
│       ├── 38.html
│       └── 39.html
│
├── weaviate-docker/         # Cấu hình Weaviate vector database
│   ├── docker-compose.yml
│   └── config.yaml
│
├── .env                     # File cấu hình môi trường
├── requirements.txt         # Các thư viện cần thiết
└── __init__.py
```

## Yêu cầu hệ thống

- Python 3.8+
- MySQL 8.0+
- Docker và Docker Compose
- Google API Key (cho Google Palm LLM)
- RAM: Tối thiểu 8GB
- Ổ cứng: Tối thiểu 20GB trống
- GPU: Khuyến nghị (không bắt buộc)

## Cài đặt

1. Clone repository:
```bash
git clone https://github.com/PhamXuanKhang/Vietnamese_Law_Assistant_Chatbot.git
cd Vietnamese_Law_Assistant_Chatbot
```

2. Tạo môi trường ảo và kích hoạt:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Cài đặt các thư viện cần thiết:
```bash
pip install -r requirements.txt
```

4. Tạo file .env và cấu hình:
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

# LLM configuration
GOOGLE_API_KEY=your_api_key

# Application configuration
APP_HOST=0.0.0.0
APP_PORT=8000
DEBUG_MODE=False
```

5. Khởi động Weaviate:
```bash
cd weaviate-docker
docker-compose up -d
```

6. Tạo database MySQL:
```sql
CREATE DATABASE phap_dien_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

## Sử dụng

1. Crawl dữ liệu từ pháp điển:
```bash
python -m chatbot_v1.src.crawl_and_insert_to_db.main
```

2. Tạo embeddings cho dữ liệu:
```bash
python -m chatbot_v1.src.embedding.create_embeddings
```

3. Khởi động chatbot:
```bash
python -m chatbot_v1.src.LLM_response.main
```

4. Truy cập giao diện web:
```
http://localhost:8000
```

## Cấu trúc dữ liệu

### Database Schema

#### pd_chude (Chủ đề)
```sql
CREATE TABLE pd_chude (
    id VARCHAR(128) PRIMARY KEY,
    ten TEXT,
    stt INT
);
```

#### pd_demuc (Đề mục)
```sql
CREATE TABLE pd_demuc (
    id VARCHAR(128) PRIMARY KEY,
    ten TEXT,
    stt INT,
    chude_id VARCHAR(128),
    FOREIGN KEY (chude_id) REFERENCES pd_chude(id)
);
```

#### pd_chuong (Chương)
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

#### pd_dieu (Điều)
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

#### pd_table (Bảng)
```sql
CREATE TABLE pd_table (
    id INT PRIMARY KEY AUTO_INCREMENT,
    dieu_id VARCHAR(128),
    html TEXT,
    FOREIGN KEY (dieu_id) REFERENCES pd_dieu(mapc)
);
```

#### pd_file (File)
```sql
CREATE TABLE pd_file (
    id INT PRIMARY KEY AUTO_INCREMENT,
    dieu_id VARCHAR(128),
    link TEXT,
    path TEXT,
    FOREIGN KEY (dieu_id) REFERENCES pd_dieu(mapc)
);
```

#### pd_muclienquan (Mục liên quan)
```sql
CREATE TABLE pd_muclienquan (
    dieu_id VARCHAR(128),
    dieu_id_lienquan VARCHAR(128),
    PRIMARY KEY (dieu_id, dieu_id_lienquan),
    FOREIGN KEY (dieu_id) REFERENCES pd_dieu(mapc),
    FOREIGN KEY (dieu_id_lienquan) REFERENCES pd_dieu(mapc)
);
```

### Vector Database (Weaviate)

#### Class: LawArticle
```json
{
  "class": "LawArticle",
  "description": "A law article from the Vietnamese legal system",
  "properties": [
    {
      "name": "content",
      "dataType": ["text"],
    },
    {
      "name": "title",
      "dataType": ["text"],
    },
    {
      "name": "article_id",
      "dataType": ["text"],
    }
  ],
  "vectorizer": "none"
}
```

## Công nghệ sử dụng

### Backend
- Python 3.8+
- FastAPI
- SQLAlchemy
- BeautifulSoup4
- PyMySQL

### Database
- MySQL 8.0+
- Weaviate (Vector Database)

### LLM & AI
- Google Palm
- Sentence Transformers
- LangChain

### Frontend
- React
- Tailwind CSS
- Axios
- React Query

### DevOps
- Docker
- Docker Compose
- Git

## API Endpoints

### 1. Tìm kiếm
```
GET /api/search
Query Parameters:
- q: Câu hỏi cần tìm kiếm
- limit: Số kết quả trả về (mặc định: 5)
- filter: Bộ lọc (tùy chọn)
```

### 2. Chi tiết điều luật
```
GET /api/articles/{article_id}
```

### 3. Chủ đề
```
GET /api/topics
GET /api/topics/{topic_id}
```

### 4. Đề mục
```
GET /api/sections
GET /api/sections/{section_id}
```


