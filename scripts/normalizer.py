import re
from typing import Any


# ============================================================
# INTENT KEYWORDS
# ============================================================

STOCK_PATTERNS = [
    r"\bесть\b",
    r"\bесть ли\b",
    r"\bв наличии\b",
    r"\bналичи[ие]\b",
    r"\bимеется\b",
    r"\bимеются\b",
    r"\bналичка\b",
    r"\bбарма\b",
    r"\bбар\s+ма\b",
    r"\bбар\s+ма\s+екен\b",
    r"\bбар\s+екен\b",
]

PRICE_PATTERNS = [
    r"\bсколько стоит\b",
    r"\bсколько\b",
    r"\bцена\b",
    r"\bпочем\b",
    r"\bпо\s+чем\b",
    r"\bстоимость\b",
    r"\bбағасы\b",
    r"\bбагасы\b",
    r"\bқанша\b",
    r"\bканша\b",
    r"\bқанша\s+тұрады\b",
    r"\bканша\s+стоит\b",
]

ORDER_STATUS_PATTERNS = [
    r"\bгде мой заказ\b",
    r"\bстатус заказа\b",
    r"\bзаказ готов\b",
    r"\bзаказ когда\b",
    r"\bкогда будет заказ\b",
    r"\bзаказ где\b",
    r"\bтапсырысым қайда\b",
    r"\bтапсырыс қайда\b",
]

INSTALLATION_WARRANTY_PATTERNS = [
    r"\bгарантия на установку\b",
    r"\bгарантия после установки\b",
    r"\bгарантия на работу\b",
    r"\bгарантия установки\b",
    r"\bустановка.*гарантия\b",
]

ENGINE_ORIGIN_PATTERNS = [
    r"\bоткуда двигатель\b",
    r"\bконтрактный двигатель\b",
    r"\bконтрактный мотор\b",
    r"\bпробег двигателя\b",
    r"\bпробег мотора\b",
    r"\bкакой пробег двигателя\b",
    r"\bқайдан келген двигатель\b",
    r"\bдвигатель пробег\b",
]


# ============================================================
# PARTS
# ============================================================

PART_PATTERNS = [
    (
        "brake_pad",
        [
            r"\bколодк",
            r"\bтормозн\w*\s+колодк",
            r"\bтормозные\b",
            r"\bbrake\s+pad",
            r"\bbrake\s+pads",
            r"\bкалодк",
        ],
    ),
    (
        "brake_disc",
        [
            r"\bтормозн\w*\s+диск",
            r"\bтормозные\s+диски",
            r"\bдиск\b",
            r"\bдиски\b",
            r"\bbrake\s+disc",
        ],
    ),
    (
        "oil_filter",
        [
            r"\bмасляный\s+фильтр",
            r"\bмасло\s+фильтр",
            r"\bфильтр\s+масла",
            r"\bмасляник",
            r"\boil\s+filter",
        ],
    ),
    (
        "air_filter",
        [
            r"\bвоздушный\s+фильтр",
            r"\bфильтр\s+воздуха",
            r"\bвоздушник",
            r"\bair\s+filter",
        ],
    ),
    (
        "cabin_filter",
        [
            r"\bсалонный\s+фильтр",
            r"\bфильтр\s+салона",
            r"\bсалонник",
            r"\bcabin\s+filter",
        ],
    ),
    (
        "spark_plug",
        [
            r"\bсвеч",
            r"\bсвечи\s+зажигания",
            r"\bspark\s+plug",
        ],
    ),
    (
        "battery",
        [
            r"\bакб\b",
            r"\bаккумулятор",
            r"\bбатарея\b",
            r"\bbattery",
        ],
    ),
    (
        "radiator",
        [
            r"\bрадиатор",
            r"\bradiator",
        ],
    ),
    (
        "alternator",
        [
            r"\bгенератор",
            r"\balternator",
        ],
    ),
    (
        "starter",
        [
            r"\bстартер",
            r"\bstarter",
        ],
    ),
    (
        "automatic_transmission",
        [
            r"\bакпп\b",
            r"\bавтомат\b",
            r"\bавтоматическая\s+коробка",
            r"\bавтомат\s+коробка",
            r"\bautomatic\s+transmission",
        ],
    ),
    (
        "manual_transmission",
        [
            r"\bмкпп\b",
            r"\bмеханика\b",
            r"\bмеханическая\s+коробка",
            r"\bmanual\s+transmission",
        ],
    ),
    (
        "transmission",
        [
            r"\bкоробка\s+передач",
            r"\bкоробка\b",
            r"\bкпп\b",
            r"\btransmission",
        ],
    ),
]


# ============================================================
# POSITION
# ============================================================

FRONT_PATTERNS = [
    r"\bпередние\b",
    r"\bпередняя\b",
    r"\bпередний\b",
    r"\bперед\b",
    r"\bспереди\b",
    r"\bfront\b",
]

REAR_PATTERNS = [
    r"\bзадние\b",
    r"\bзадняя\b",
    r"\bзадний\b",
    r"\bзад\b",
    r"\bсзади\b",
    r"\brear\b",
]


# ============================================================
# CAR BRANDS / MODELS
# ============================================================

CAR_PATTERNS = [
    (
        "Toyota",
        "Camry",
        [
            r"\bкамри\b",
            r"\bcamry\b",
        ],
    ),
    (
        "Toyota",
        "Corolla",
        [
            r"\bкоролла\b",
            r"\bcorolla\b",
        ],
    ),
    (
        "Toyota",
        "RAV4",
        [
            r"\bрав4\b",
            r"\bрав\s+4\b",
            r"\brav4\b",
            r"\brav\s*4\b",
        ],
    ),
    (
        "Toyota",
        "Land Cruiser Prado",
        [
            r"\bпрадо\b",
            r"\bprado\b",
        ],
    ),
    (
        "Toyota",
        "Land Cruiser",
        [
            r"\bкрузак\b",
            r"\bland\s+cruiser\b",
        ],
    ),
    (
        "Mercedes",
        None,
        [
            r"\bмерс\b",
            r"\bмерседес\b",
            r"\bmercedes\b",
        ],
    ),
    (
        "BMW",
        None,
        [
            r"\bбмв\b",
            r"\bбэха\b",
            r"\bbmw\b",
        ],
    ),
    (
        "Lexus",
        None,
        [
            r"\bлексус\b",
            r"\blexus\b",
        ],
    ),
    (
        "Honda",
        None,
        [
            r"\bхонда\b",
            r"\bhonda\b",
        ],
    ),
    (
        "Hyundai",
        None,
        [
            r"\bхендай\b",
            r"\bхундай\b",
            r"\bhyundai\b",
        ],
    ),
    (
        "Kia",
        None,
        [
            r"\bкиа\b",
            r"\bkia\b",
        ],
    ),
    (
        "Volkswagen",
        None,
        [
            r"\bфольксваген\b",
            r"\bфольц\b",
            r"\bvolkswagen\b",
            r"\bvw\b",
        ],
    ),
]


# ============================================================
# GENERATIONS
# ============================================================

CAMRY_GENERATIONS = [
    (
        "XV70",
        [
            r"\bкамри\s*70\b",
            r"\bcamry\s*70\b",
            r"\bкамри\s*xv70\b",
            r"\bcamry\s*xv70\b",
            r"\bxv70\b",
        ],
    ),
    (
        "XV50",
        [
            r"\bкамри\s*50\b",
            r"\bcamry\s*50\b",
            r"\bкамри\s*xv50\b",
            r"\bcamry\s*xv50\b",
            r"\bxv50\b",
        ],
    ),
    (
        "XV40",
        [
            r"\bкамри\s*40\b",
            r"\bcamry\s*40\b",
            r"\bкамри\s*xv40\b",
            r"\bcamry\s*xv40\b",
            r"\bxv40\b",
        ],
    ),
]


MODEL_CODE_PATTERNS = [
    (
        "Mercedes",
        "W211",
        [
            r"\bw211\b",
        ],
    ),
    (
        "Mercedes",
        "W210",
        [
            r"\bw210\b",
        ],
    ),
    (
        "Mercedes",
        "W204",
        [
            r"\bw204\b",
        ],
    ),
    (
        "BMW",
        "E46",
        [
            r"\be46\b",
        ],
    ),
]


# ============================================================
# LANGUAGE
# ============================================================

RUSSIAN_WORDS = [
    "есть",
    "нужен",
    "нужна",
    "нужны",
    "ищу",
    "найди",
    "сколько",
    "цена",
    "колодки",
    "передние",
    "задние",
    "заказ",
    "гарантия",
    "двигатель",
]

KAZAKH_WORDS = [
    "барма",
    "бар",
    "қанша",
    "канша",
    "бағасы",
    "багасы",
    "керек",
    "қайда",
    "тапсырыс",
    "қозғалтқыш",
    "двигатель",
]


# ============================================================
# HELPERS
# ============================================================

def contains_any(text: str, patterns: list[str]) -> bool:
    for pattern in patterns:
        if re.search(pattern, text, flags=re.IGNORECASE):
            return True

    return False


def normalize_text(text: str) -> str:
    text = text.lower().strip()

    text = text.replace("ё", "е")

    text = re.sub(
        r"\s+",
        " ",
        text,
    )

    return text


def detect_language(text: str) -> str:
    russian = contains_any(
        text,
        RUSSIAN_WORDS,
    )

    kazakh = contains_any(
        text,
        KAZAKH_WORDS,
    )

    if russian and kazakh:
        return "mixed"

    if kazakh:
        return "kk"

    if russian:
        return "ru"

    return "unknown"


def detect_intent(text: str, qwen_intent: str | None = None) -> str:
    """
    Deterministic rules have priority for explicit stock/price/status
    questions. Qwen result is used as fallback.
    """

    if contains_any(
        text,
        ORDER_STATUS_PATTERNS,
    ):
        return "order_status"

    if contains_any(
        text,
        INSTALLATION_WARRANTY_PATTERNS,
    ):
        return "installation_warranty"

    if contains_any(
        text,
        ENGINE_ORIGIN_PATTERNS,
    ):
        return "engine_origin"

    if contains_any(
        text,
        STOCK_PATTERNS,
    ):
        return "check_stock"

    if contains_any(
        text,
        PRICE_PATTERNS,
    ):
        return "check_price"

    if qwen_intent in {
        "search_part",
        "check_stock",
        "check_price",
        "order_status",
        "installation_warranty",
        "engine_origin",
        "unknown",
    }:
        return qwen_intent

    return "unknown"


def detect_part(text: str) -> str | None:
    for part_name, patterns in PART_PATTERNS:
        if contains_any(text, patterns):
            return part_name

    return None


def detect_position(text: str) -> str | None:
    if contains_any(
        text,
        FRONT_PATTERNS,
    ):
        return "front"

    if contains_any(
        text,
        REAR_PATTERNS,
    ):
        return "rear"

    return None


def detect_vehicle(text: str) -> dict[str, Any]:
    vehicle = {
        "brand": None,
        "model": None,
        "generation": None,
        "year": None,
        "engine": None,
        "body": None,
    }

    # --------------------------------------------------------
    # Explicit model codes
    # --------------------------------------------------------

    for brand, model, patterns in MODEL_CODE_PATTERNS:
        if contains_any(text, patterns):
            vehicle["brand"] = brand
            vehicle["model"] = model
            break

    # --------------------------------------------------------
    # Brands / models
    # --------------------------------------------------------

    for brand, model, patterns in CAR_PATTERNS:

        if contains_any(text, patterns):

            if vehicle["brand"] is None:
                vehicle["brand"] = brand

            if model is not None and vehicle["model"] is None:
                vehicle["model"] = model

            break

    # --------------------------------------------------------
    # Camry generations
    # --------------------------------------------------------

    for generation, patterns in CAMRY_GENERATIONS:

        if contains_any(text, patterns):

            vehicle["generation"] = generation

            if vehicle["brand"] is None:
                vehicle["brand"] = "Toyota"

            if vehicle["model"] is None:
                vehicle["model"] = "Camry"

            break

    # --------------------------------------------------------
    # Explicit year
    # --------------------------------------------------------

    year_match = re.search(
        r"\b(19\d{2}|20\d{2})\b",
        text,
    )

    if year_match:
        vehicle["year"] = int(
            year_match.group(1)
        )

    return vehicle


# ============================================================
# MERGE QWEN + NORMALIZER
# ============================================================

def normalize_intent(
    message: str,
    qwen_result: dict[str, Any] | None = None,
) -> dict[str, Any]:

    qwen_result = qwen_result or {}

    text = normalize_text(message)

    qwen_vehicle = qwen_result.get(
        "vehicle",
        {},
    ) or {}

    qwen_part = qwen_result.get(
        "part",
        {},
    ) or {}

    qwen_order = qwen_result.get(
        "order",
        {},
    ) or {}

    # --------------------------------------------------------
    # Vehicle
    # --------------------------------------------------------

    detected_vehicle = detect_vehicle(text)

    vehicle = {
        "brand": (
            qwen_vehicle.get("brand")
            or detected_vehicle["brand"]
        ),
        "model": (
            qwen_vehicle.get("model")
            or detected_vehicle["model"]
        ),
        "generation": (
            qwen_vehicle.get("generation")
            or detected_vehicle["generation"]
        ),
        "year": (
            qwen_vehicle.get("year")
            or detected_vehicle["year"]
        ),
        "engine": qwen_vehicle.get("engine"),
        "body": qwen_vehicle.get("body"),
    }

    # --------------------------------------------------------
    # Part
    # --------------------------------------------------------

    detected_part = detect_part(text)
    detected_position = detect_position(text)

    part = {
        "name": (
            qwen_part.get("name")
            or detected_part
        ),
        "position": (
            qwen_part.get("position")
            or detected_position
        ),
    }

    # --------------------------------------------------------
    # Intent
    # --------------------------------------------------------

    intent = detect_intent(
        text,
        qwen_result.get("intent"),
    )

    # --------------------------------------------------------
    # Language
    # --------------------------------------------------------

    detected_language = detect_language(text)

    language = (
        detected_language
        if detected_language != "unknown"
        else qwen_result.get("language", "unknown")
    )

    # --------------------------------------------------------
    # Order
    # --------------------------------------------------------

    order = {
        "number": qwen_order.get("number"),
    }

    # --------------------------------------------------------
    # Final result
    # --------------------------------------------------------

    return {
        "intent": intent,
        "language": language,
        "vehicle": vehicle,
        "part": part,
        "order": order,
    }


# ============================================================
# LOCAL TEST
# ============================================================

if __name__ == "__main__":

    test_messages = [
        "камри 70 передние колодки есть?",
        "Toyota Camry XV70 передние тормозные колодки есть?",
        "камри 70 колодки сколько стоят?",
        "камри 70 задние колодки",
        "мерс w211 автомат барма багасы канша",
        "бмв е46 задние колодки есть?",
        "на камри 50 масляный фильтр есть?",
        "где мой заказ?",
        "какая гарантия на установку?",
    ]

    for message in test_messages:

        result = normalize_intent(
            message,
            {
                "intent": "search_part",
                "language": "ru",
                "vehicle": {
                    "brand": None,
                    "model": None,
                    "generation": None,
                    "year": None,
                    "engine": None,
                    "body": None,
                },
                "part": {
                    "name": None,
                    "position": None,
                },
                "order": {
                    "number": None,
                },
            },
        )

        print()
        print("=" * 70)
        print(message)
        print("=" * 70)
        print(
            json.dumps(
                result,
                ensure_ascii=False,
                indent=2,
            )
        )