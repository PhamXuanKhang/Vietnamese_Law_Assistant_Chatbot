from langchain.llms import HuggingFaceHub
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from huggingface_hub import login

login(token='')

llm = HuggingFaceHub(
    repo_id="vinai/PhoGPT-4B-Chat",  
    model_kwargs={"temperature": 0.7},
    task="summarization",  
    huggingfacehub_api_token='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'
)

prompt_template = """
Bạn là một trợ lý AI chuyên trích xuất thực thể và mối quan hệ từ văn bản luật.
Trích xuất tất cả các thực thể (nodes) và mối quan hệ (edges) từ văn bản dưới đây. Các thực thể và mối quan hệ PHẢI được viết bằng tiếng Việt. LƯU Ý: PHẢI ĐẦY ĐỦ TẤT CẢ và CHÍNH XÁC. Chỉ cẩn Phần, Chương, mục, điều

Thông tin của thực thể cần bao gồm:

- **Tên**: Tên đầy đủ của thực thể (ví dụ: "Điều 1: Phạm vi điều chỉnh").
- **Label**: Loại của thực thể (ví dụ: "Luật", "Phần", "Chương", "Mục", "Điều").
- **Value**: Nội dung chi tiết của thực thể nếu có (ví dụ: với "Điều", ghi rõ nội dung của điều luật). Nếu không có nội dung cụ thể, để trống hoặc ghi chú là không có nội dung chi tiết.

Hướng dẫn cụ thể về cách đặt tên:

- Đối với "Mục", sử dụng định dạng "Mục [số]: [tên]" mà không bao gồm thông tin chương hoặc phần trong ngoặc. Ví dụ: "Mục 1: CÁC HÌNH THỨC XỬ PHẠT".
- Áp dụng quy tắc đặt tên này cho các thực thể tương tự như "Chương", "Phần", bằng cách loại bỏ các tham chiếu đến cấu trúc cấp cao hơn trong ngoặc.

Mối quan hệ sử dụng định dạng:

- (**Thực thể 1**, **Loại quan hệ**, **Thực thể 2**), trong đó **Loại quan hệ** là "có" (nghĩa là "chứa" hoặc "bao gồm").

Định dạng đầu ra:

Thực thể:

**Tên**: [Tên thực thể]  
**Label**: [Loại thực thể]  
**Value**: [Nội dung thực thể hoặc để trống]

Mối quan hệ:

(**Thực thể 1**, **có**, **Thực thể 2**)

Văn bản:
{input_text}
"""

prompt = PromptTemplate(input_variables=["input_text"], template=prompt_template)

chain = LLMChain(prompt=prompt, llm=llm)
input_text = 'Phần thứ sáu ĐIỀU KHOẢN THI HÀNH Điều 141. Hiệu lực thi hành 1. Luật này có hiệu lực thi hành từ ngày 01 tháng 7 năm 2013, trừ các quy định liên quan đến việc áp dụng các biện pháp xử lý hành chính do Tòa án nhân dân xem xét, quyết định thì có hiệu lực kể từ ngày 01 tháng 01 năm 2014.'

#with open('/home/maianhtruong/Github/FPTChat/Law_Chatbot/database/LUẬT  Xử lý vi phạm hành chính/Phan_6.txt', 'r') as f:
#    input_text = f.read()

response = chain.run(input_text)


print(response)