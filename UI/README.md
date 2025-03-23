# Vietnamese-RAG-Chatbot
Create a chatbot that provides responses in Vietnamese, focusing on the products offered by a flower shop

Here is the RAG pipeline in two version:
![image](https://github.com/user-attachments/assets/0db9e99f-3a70-463d-a379-f2c41b7e7e31)
![image](https://github.com/user-attachments/assets/c31d8ffc-393b-433b-a709-1d71609b9e6d)

## Prerequisites

- [Python 3.7+](https://www.python.org/downloads/) for running the Streamlit frontend locally
- [pip](https://pip.pypa.io/en/stable/installation/) for managing Python packages
- A Google account to access [Google Colab](https://colab.research.google.com/)
## Clone the repository (or download the code files):

   ```bash
   git clone https://github.com/protonx-ai-devs-02/cuongtm-vietnamese-rag-chatbot.git
   cd cuongtm-vietnamese-rag-chatbot
  ```
## Backend Setup (Flask + Colab + Ngrok)
1. Open the file `Vietnamese_RAG_Chatbot_Backend.ipynb` in Google Colab.
2. Make sure to add your `ngrok_key` and `open_ai_key` in the Colab secret keys.
3. Change the runtime type to **T4 GPU** to use the Reranker model.
4. Run the cell `0.Packages` to install all the dependencies and set the OpenAI API key in the environment.
5. Run `1.Data Crawling` to crawl the data if you haven’t done so already.
6. Run `2.Data Preprocessing` to preprocess the data and perform basic transformations.
7. Run `3.Retriever Module`, `4.Answer Generator`, and `4'.Agent Tools` to execute all the components of the RAG pipeline.
8. Run `5.API` and set the Ngrok URL in the Streamlit files.

## GUI Setup (Streamlit)
1.**Create and activate a virtual environment**

Using venv
```bash
python -m venv venv
source venv/bin/activate   # On Windows, use `venv\Scripts\activate`
```
Using conda
```bash
conda create --name myenv 
conda activate myenv
```
2.**Install dependencies:**
```bash
pip install -r requirements.txt
```
3.**Running the App**

Remember to set the Ngrok URL before running
```bash
streamlit run Hello.py
```
You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
  
  Network URL: http://<your_ip_address>:8501

----------------------------------------------------------------------------------------------
Khởi động chương trình bằng cách:
streamlit run About_us.py

Khởi chạy API: 
uvicorn fastAPI:app --host 0.0.0.0 --port 8000 --reload