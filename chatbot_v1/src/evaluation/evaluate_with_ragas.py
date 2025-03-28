import pandas as pd
from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy
from ragas.dataset_schema import SingleTurnSample
from chatbot_v1.src.LLM_response.LLM_generator import answerModel
from chatbot_v1.src.embedding.load_embedding_model import model2
from ragas.llms import LangchainLLMWrapper
from ragas.embeddings import LangchainEmbeddingsWrapper
import time
from google.api_core import exceptions

# Bước 1: Giả định bạn đã có testset (list of SingleTurnSample objects)
# Thay thế "samples" bằng testset thực tế của bạn
# Ví dụ: samples = [SingleTurnSample(user_input="...", response="...", retrieved_contexts=["..."]), ...]
samples = []  # Thay bằng testset của bạn

# Bước 2: Tối ưu hóa số token (cắt ngắn context)
def truncate_text(text, max_tokens=100):
    tokens = text.split()[:max_tokens]  # Giả lập cắt token
    return " ".join(tokens)

# Chuẩn bị samples với context đã cắt ngắn
for item in samples:
    item.retrieved_contexts = [truncate_text(ctx, max_tokens=100) for ctx in item.retrieved_contexts]

# Bước 3: Batching để giảm số lượng yêu cầu
batch_size = 2  # Gộp 2 mẫu mỗi lần để tuân thủ 2 RPM
batched_samples = [samples[i:i + batch_size] for i in range(0, len(samples), batch_size)]

eval_llm = LangchainLLMWrapper(answerModel)
eval_embeddings = LangchainEmbeddingsWrapper(model2)

# Đánh giá từng batch với retry logic
results = []
for batch in batched_samples:
    retries = 3
    for attempt in range(retries):
        try:
            result = evaluate(
                dataset=batch,
                metrics=[faithfulness, answer_relevancy],
                llm=eval_llm,
                embeddings=eval_embeddings
            )
            results.append(result.to_pandas())
            break  # Thoát nếu thành công
        except exceptions.ResourceExhausted as e:
            if attempt < retries - 1:
                delay = 30  # Delay 30 giây để tuân thủ 2 RPM
                print(f"Rate limit exceeded, retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                raise e
    time.sleep(30)  # Delay 30 giây giữa các batch

# Bước 4: Gộp và xuất kết quả
final_result = pd.concat(results, ignore_index=True)
final_result.to_csv("./chatbot_v1/data/evaluate/evaluation_results.csv", index=False)
print(final_result)