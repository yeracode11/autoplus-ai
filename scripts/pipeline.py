import json
import re
import sys

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig

from normalizer import normalize_intent


MODEL_NAME = "Qwen/Qwen3-8B"


SYSTEM_PROMPT = """
Ты NLP-модуль автомобильного WhatsApp-бота.

Твоя задача — понять сообщение клиента и вернуть ТОЛЬКО JSON.
Никаких пояснений, markdown, ``` и текста вне JSON.

Ты должен понимать:
- русский язык
- казахский язык
- смешанный русский + казахский
- сленг
- сокращения
- опечатки
- разговорную речь
- автомобильные термины

Никогда не придумывай цену, наличие, продавца или другие данные.
Ты только извлекаешь намерение и сущности из сообщения.

Допустимые intent:
- search_part
- check_price
- check_stock
- part_compatibility
- product_info
- warranty_info
- delivery_info
- seller_info
- unknown

Допустимые language:
- ru
- kk
- mixed

Формат JSON:

{
  "intent": "search_part",
  "language": "mixed",
  "vehicle": {
    "brand": null,
    "model": null,
    "generation": null,
    "year": null,
    "engine": null,
    "body": null
  },
  "part": {
    "category": null,
    "subcategory": null,
    "position": null,
    "side": null
  },
  "actions": [],
  "delivery": {
    "city": null
  },
  "query": null
}

Правила:

1. "камри20" = Toyota Camry XV20.
2. "камри 20" = Toyota Camry XV20.
3. "камри50" = Toyota Camry XV50.
4. "акпп" = automatic_transmission.
5. "автомат" в контексте автомобиля = automatic_transmission.
6. "механика" в контексте автомобиля = manual_transmission.
7. "цапфа" = steering_knuckle.
8. "ступица" = wheel_hub.
9. "колодки" = brake_pad.
10. "мотор" = engine.
11. "фара" = headlight.
12. "задняя фара" / "фонарь" = taillight.
13. "алдыңғы" = front.
14. "артқы" = rear.
15. "оң жақ" = right.
16. "сол жақ" = left.

Если клиент говорит:
"нужна", "нужен", "нужны", "надо", "ищу", "керек", "керек еді"
— это обычно означает search_part.

Если клиент спрашивает:
"сколько стоит", "цена", "багасы канша"
— добавь check_price.

Если спрашивает:
"есть", "есть ли", "барма", "бар ма"
— добавь check_stock ТОЛЬКО если вопрос именно о наличии детали.

Если спрашивает:
"подойдет?", "встанет?", "келема?", "келе ма?"
— это part_compatibility.

Если спрашивает про:
"гарантия", "гарантия қанша"
— это warranty_info.

Если спрашивает про:
"доставка", "отправите", "салып жібересіңдер"
— это delivery_info.

Если спрашивает:
"что это", "что за деталь", характеристики или описание
— это product_info.

Если клиент одновременно просит несколько действий,
intent должен быть главным действием,
а остальные действия записывай в actions.

Пример:

Клиент:
"брат камри20 2000ж цапфа керек еди багасы канша немен салып жибересиндер актобеге"

Ответ:

{
  "intent": "search_part",
  "language": "mixed",
  "vehicle": {
    "brand": "Toyota",
    "model": "Camry",
    "generation": "XV20",
    "year": 2000,
    "engine": null,
    "body": null
  },
  "part": {
    "category": "steering_knuckle",
    "subcategory": null,
    "position": null,
    "side": null
  },
  "actions": [
    "search_part",
    "check_price",
    "delivery_info"
  ],
  "delivery": {
    "city": "Актобе"
  },
  "query": "цапфа"
}
"""


def load_model():
    print("Loading tokenizer...")

    tokenizer = AutoTokenizer.from_pretrained(
        MODEL_NAME,
        trust_remote_code=True
    )

    print("Loading Qwen3-8B 4-bit...")

    quantization_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.float16,
        bnb_4bit_use_double_quant=True
    )

    model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME,
        device_map="auto",
        quantization_config=quantization_config,
        torch_dtype=torch.float16,
        trust_remote_code=True
    )

    model.eval()

    print("Model loaded.")
    print()

    return tokenizer, model


def extract_json(text: str):
    """
    Достает JSON даже если модель случайно добавила текст
    или <think>...</think>.
    """

    text = re.sub(
        r"<think>.*?</think>",
        "",
        text,
        flags=re.DOTALL
    ).strip()

    start = text.find("{")
    end = text.rfind("}")

    if start == -1 or end == -1 or end <= start:
        raise ValueError(
            f"JSON not found in model response:\n{text}"
        )

    json_text = text[start:end + 1]

    return json.loads(json_text)


def ask_qwen(text: str, tokenizer, model):
    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        },
        {
            "role": "user",
            "content": text
        }
    ]

    prompt = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True,
        enable_thinking=False
    )

    inputs = tokenizer(
        prompt,
        return_tensors="pt"
    )

    inputs = {
        key: value.to(model.device)
        for key, value in inputs.items()
    }

    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=512,
            do_sample=False
        )

    generated_tokens = outputs[0][
        inputs["input_ids"].shape[-1]:
    ]

    response = tokenizer.decode(
        generated_tokens,
        skip_special_tokens=True
    ).strip()

    return response


def print_json(title, data):
    print("=" * 70)
    print(title)
    print("=" * 70)

    print(
        json.dumps(
            data,
            ensure_ascii=False,
            indent=2
        )
    )

    print()


def run_pipeline(text, tokenizer, model):
    print()
    print("=" * 70)
    print("USER MESSAGE")
    print("=" * 70)
    print(text)
    print()

    # ---------------------------------------------------------
    # 1. QWEN
    # ---------------------------------------------------------

    raw_response = ask_qwen(
        text,
        tokenizer,
        model
    )

    print("=" * 70)
    print("QWEN RAW")
    print("=" * 70)
    print(raw_response)
    print()

    # ---------------------------------------------------------
    # 2. JSON PARSE
    # ---------------------------------------------------------

    try:
        qwen_result = extract_json(raw_response)

    except Exception as e:
        print("=" * 70)
        print("JSON ERROR")
        print("=" * 70)
        print(str(e))
        print()

        return None

    print_json(
        "QWEN JSON",
        qwen_result
    )

    # ---------------------------------------------------------
    # 3. NORMALIZER
    # ---------------------------------------------------------

    normalized = normalize_intent(
        text,
        qwen_result
    )

    print_json(
        "FINAL NORMALIZED REQUEST",
        normalized
    )

    # ---------------------------------------------------------
    # 4. IMPORTANT FIELDS
    # ---------------------------------------------------------

    print("=" * 70)
    print("IMPORTANT FIELDS")
    print("=" * 70)

    print(
        "Intent:",
        normalized.get("intent")
    )

    print(
        "Language:",
        normalized.get("language")
    )

    print(
        "Actions:",
        normalized.get("actions")
    )

    print(
        "Vehicle:",
        normalized.get("vehicle")
    )

    print(
        "Part:",
        normalized.get("part")
    )

    delivery = normalized.get("delivery") or {}

    print(
        "City:",
        delivery.get("city")
    )

    print()

    return normalized


def main():
    tokenizer, model = load_model()

    # ---------------------------------------------------------
    # CLI mode:
    #
    # python scripts\pipeline.py "текст"
    # ---------------------------------------------------------

    if len(sys.argv) > 1:
        text = " ".join(sys.argv[1:])

        run_pipeline(
            text,
            tokenizer,
            model
        )

        return

    # ---------------------------------------------------------
    # Interactive mode
    # ---------------------------------------------------------

    print("=" * 70)
    print("Vinly AI NLP Pipeline")
    print("=" * 70)
    print()
    print("Введите сообщение клиента.")
    print("Для выхода: exit")
    print()

    while True:
        try:
            text = input("USER > ").strip()

        except (KeyboardInterrupt, EOFError):
            print()
            break

        if not text:
            continue

        if text.lower() in {
            "exit",
            "quit",
            "q"
        }:
            break

        run_pipeline(
            text,
            tokenizer,
            model
        )


if __name__ == "__main__":
    main()