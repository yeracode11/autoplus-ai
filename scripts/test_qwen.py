import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig

MODEL_PATH = r"models\Qwen3-8B"

print("Loading tokenizer...")

tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)

quantization_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.bfloat16,
    bnb_4bit_use_double_quant=True,
)

print("Loading Qwen3-8B 4-bit...")

model = AutoModelForCausalLM.from_pretrained(
    MODEL_PATH,
    quantization_config=quantization_config,
    device_map="auto",
)

print("Model loaded!")
print("GPU:", torch.cuda.get_device_name(0))
print(
    "VRAM allocated:",
    round(torch.cuda.memory_allocated(0) / 1024**3, 2),
    "GB"
)

messages = [
    {
        "role": "system",
        "content": (
            "Ты AI-помощник автомобильного сервиса AutoPlus. "
            "Отвечай кратко и понятно на русском языке."
        ),
    },
    {
        "role": "user",
        "content": "Салам, на Камри 70 передние колодки есть?",
    },
]

text = tokenizer.apply_chat_template(
    messages,
    tokenize=False,
    add_generation_prompt=True,
)

inputs = tokenizer(
    text,
    return_tensors="pt"
).to(model.device)

with torch.no_grad():
    outputs = model.generate(
        **inputs,
        max_new_tokens=300,
        temperature=0.7,
        top_p=0.8,
    )

answer = tokenizer.decode(
    outputs[0][inputs["input_ids"].shape[1]:],
    skip_special_tokens=True,
)

print("\n========== QWEN ==========\n")
print(answer)