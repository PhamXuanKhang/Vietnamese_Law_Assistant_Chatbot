from transformers import AutoTokenizer, AutoModelForCausalLM

# Tải tokenizer và model về cache
tokenizer = AutoTokenizer.from_pretrained("infCapital/viet-llama2-ft")
model = AutoModelForCausalLM.from_pretrained("infCapital/viet-llama2-ft")