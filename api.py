import json
import re

import torch
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    BitsAndBytesConfig,
)

from normalizer import normalize_intent


# ============================================================
# CONFIG
# ============================================================

MODEL_PATH = r"models\Qwen3-8B"

app = FastAPI(
    title="Vinly Qwen API",
    version="1.0.0",
)


# ============================================================
# REQUEST
# ============================================================

class IntentRequest(BaseModel):
    message: str
    language: str = "auto"


# ============================================================
# LOAD MODEL
# ============================================================

print("Loading tokenizer...")

tokenizer = AutoTokenizer.from_pretrained(
    MODEL_PATH
)

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

model.eval()

print("Model loaded!")

if torch.cuda.is_available():
    print(
        "GPU:",
        torch.cuda.get_device_name(0),
    )

    print(
        "VRAM allocated:",
        round(
            torch.cuda.memory_allocated(0) / 1024**3,
            2,
        ),
        "GB",
    )


# ============================================================
# SYSTEM PROMPT
# ============================================================

SYSTEM_PROMPT = """
Ты AI-парсер сообщений клиентов магазина автозапчастей Vinly.

Твоя задача — понять сообщение клиента и вернуть структурированный JSON.

ТЫ НЕ ДОЛЖЕН ОТВЕЧАТЬ КЛИЕНТУ.

ТЫ НЕ ДОЛЖЕН ПИСАТЬ ОБЪЯСНЕНИЯ.

ТЫ НЕ ДОЛЖЕН ПИСАТЬ РАССУЖДЕНИЯ.

ТЫ ДОЛЖЕН ВЕРНУТЬ ТОЛЬКО JSON.

------------------------------------------------------------
INTENTS
------------------------------------------------------------

Разрешены только:

search_part
check_stock
check_price
order_status
installation_warranty
engine_origin
unknown

------------------------------------------------------------
JSON FORMAT
------------------------------------------------------------

{
  "intent": "check_stock",
  "language": "ru",
  "vehicle": {
    "brand": null,
    "model": null,
    "generation": null,
    "year": null,
    "engine": null,
    "body": null
  },
  "part": {
    "name": null,
    "position": null
  },
  "order": {
    "number": null
  }
}

------------------------------------------------------------
RULES
------------------------------------------------------------

1. Если значение неизвестно — используй null.

2. Никогда не выдумывай отсутствующие данные.

3. Понимай русский язык.

4. Понимай казахский язык.

5. Понимай смешанный русский/казахский.

6. Понимай автомобильный сленг.

7. Понимай сокращения.

8. W211, W210, W204, W220 и подобные обозначения могут быть
   обозначением кузова/поколения автомобиля.

9. E46, E39, F10, G30 и подобные обозначения BMW могут быть
   обозначением кузова/поколения.

10. "колодки" = brake_pad.

11. "тормозные колодки" = brake_pad.

12. "передние колодки" = brake_pad + position front.

13. "задние колодки" = brake_pad + position rear.

14. "масляный фильтр" = oil_filter.

15. "воздушный фильтр" = air_filter.

16. "салонный фильтр" = cabin_filter.

17. "автомат" в контексте автомобильной запчасти =
    automatic_transmission.

18. "АКПП" = automatic_transmission.

19. "механика" / "МКПП" = manual_transmission.

20. Если клиент спрашивает наличие:
    check_stock.

21. Если клиент спрашивает цену:
    check_price.

22. Если клиент ищет или подбирает запчасть:
    search_part.

23. Если клиент спрашивает статус заказа:
    order_status.

24. Если клиент спрашивает гарантию установки:
    installation_warranty.

25. Если клиент спрашивает происхождение двигателя или его пробег:
    engine_origin.

26. Если невозможно определить намерение:
    unknown.

------------------------------------------------------------
LANGUAGE
------------------------------------------------------------

Используй:

ru — русский
kk — казахский

Если сообщение смешанное, выбери язык, который преобладает.

------------------------------------------------------------
IMPORTANT
------------------------------------------------------------

Не придумывай:

- наличие;
- цену;
- статус заказа;
- характеристики автомобиля;
- характеристики запчасти;
- артикул;
- производителя;
- VIN.

Ты только извлекаешь информацию из сообщения клиента.

------------------------------------------------------------
OUTPUT
------------------------------------------------------------

Верни только один JSON-объект.

Без Markdown.

Без ```json.

Без объяснений.

Без текста до JSON.

Без текста после JSON.
"""


# ============================================================
# JSON EXTRACTION
# ============================================================

def extract_json(text: str) -> dict:
    """
    Извлекает первый полноценный JSON-объект
    из ответа Qwen.
    """

    text = text.strip()

    # --------------------------------------------------------
    # Remove markdown fences
    # --------------------------------------------------------

    text = re.sub(
        r"```json\s*",
        "",
        text,
        flags=re.IGNORECASE,
    )

    text = re.sub(
        r"```\s*",
        "",
        text,
    )

    # --------------------------------------------------------
    # Find first {
    # --------------------------------------------------------

    start = text.find("{")

    if start == -1:
        raise ValueError(
            f"Qwen did not return JSON: {text}"
        )

    # --------------------------------------------------------
    # Balanced JSON extraction
    # --------------------------------------------------------

    depth = 0
    in_string = False
    escape = False

    for index in range(start, len(text)):

        char = text[index]

        # Handle escaped characters inside strings
        if escape:
            escape = False
            continue

        if char == "\\" and in_string:
            escape = True
            continue

        # Enter / exit JSON string
        if char == '"':
            in_string = not in_string
            continue

        if in_string:
            continue

        # JSON object depth
        if char == "{":
            depth += 1

        elif char == "}":
            depth -= 1

            if depth == 0:

                json_text = text[
                    start:index + 1
                ]

                return json.loads(json_text)

    raise ValueError(
        f"Qwen returned incomplete JSON: {text}"
    )


# ============================================================
# HEALTH
# ============================================================

@app.get("/health")
def health():
    return {
        "status": "ok",
        "model": "Qwen3-8B",
        "cuda": torch.cuda.is_available(),
        "gpu": (
            torch.cuda.get_device_name(0)
            if torch.cuda.is_available()
            else None
        ),
    }


# ============================================================
# QWEN
# ============================================================

def run_qwen(
    message: str,
    language: str,
) -> dict:

    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT,
        },
        {
            "role": "user",
            "content": (
                f"Язык клиента: {language}\n\n"
                f"Сообщение клиента:\n"
                f"{message}\n\n"
                "Верни только JSON."
            ),
        },
    ]

    # --------------------------------------------------------
    # Chat template
    # --------------------------------------------------------

    try:

        prompt = tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True,
            enable_thinking=False,
        )

    except TypeError:

        # Fallback для версии transformers,
        # которая не поддерживает enable_thinking.
        prompt = tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True,
        )

    # --------------------------------------------------------
    # Tokenize
    # --------------------------------------------------------

    inputs = tokenizer(
        prompt,
        return_tensors="pt",
    ).to(model.device)

    # --------------------------------------------------------
    # Generate
    # --------------------------------------------------------

    with torch.no_grad():

        outputs = model.generate(
            **inputs,

            # Qwen должен вернуть маленький JSON.
            max_new_tokens=300,

            # Детерминированный результат.
            do_sample=False,

            # Не повторять бесконечно.
            repetition_penalty=1.05,
        )

    # --------------------------------------------------------
    # Only generated tokens
    # --------------------------------------------------------

    generated_tokens = outputs[0][
        inputs["input_ids"].shape[1]:
    ]

    answer = tokenizer.decode(
        generated_tokens,
        skip_special_tokens=True,
    )

    return extract_json(answer), answer


# ============================================================
# INTENT API
# ============================================================

@app.post("/v1/intent")
def create_intent(
    request: IntentRequest,
):

    # --------------------------------------------------------
    # Validate message
    # --------------------------------------------------------

    message = request.message.strip()

    if not message:

        raise HTTPException(
            status_code=400,
            detail="message is empty",
        )

    # --------------------------------------------------------
    # QWEN
    # --------------------------------------------------------

    try:

        qwen_result, raw_answer = run_qwen(
            message=message,
            language=request.language,
        )

    except json.JSONDecodeError as error:

        raise HTTPException(
            status_code=500,
            detail={
                "error": "Qwen returned invalid JSON",
                "message": str(error),
            },
        )

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail={
                "error": "Qwen processing failed",
                "message": str(error),
            },
        )

    # --------------------------------------------------------
    # NORMALIZER
    # --------------------------------------------------------

    try:

       normalized_result = normalize_intent(
    	   qwen_result=qwen_result,
           original_text=message,
           requested_language=request.language,
	)

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail={
                "error": "Normalizer failed",
                "message": str(error),
            },
        )

    # ========================================================
    # LOGGING
    # ========================================================

    print()
    print("=" * 70)
    print("USER MESSAGE")
    print("=" * 70)
    print(message)

    print()
    print("=" * 70)
    print("QWEN RAW")
    print("=" * 70)
    print(raw_answer)

    print()
    print("=" * 70)
    print("QWEN JSON")
    print("=" * 70)
    print(
        json.dumps(
            qwen_result,
            ensure_ascii=False,
            indent=2,
        )
    )

    print()
    print("=" * 70)
    print("NORMALIZED JSON")
    print("=" * 70)
    print(
        json.dumps(
            normalized_result,
            ensure_ascii=False,
            indent=2,
        )
    )

    print()

    # --------------------------------------------------------
    # RETURN
    # --------------------------------------------------------

    return normalized_result