import re
import json
from typing import Any


# ============================================================
# HELPERS
# ============================================================

def clean_text(text: str) -> str:
    return " ".join(text.lower().strip().split())


# ============================================================
# LANGUAGE
# ============================================================

def detect_language(text: str, requested_language: str = "auto") -> str:
    if requested_language in ("ru", "kk"):
        return requested_language

    t = clean_text(text)

    kazakh_markers = [
        "барма",
        "бар ма",
        "багасы",
        "бағасы",
        "канша",
        "қанша",
        "тұрады",
        "турады",
        "қандай",
        "қайдан",
        "пробегы",
        "пробег",
    ]

    russian_markers = [
        "есть",
        "цена",
        "сколько",
        "стоит",
        "где",
        "какой",
        "какая",
        "откуда",
        "двигатель",
        "мотор",
        "заказ",
        "гарантия",
        "установка",
    ]

    kk_score = 0
    ru_score = 0

    for marker in kazakh_markers:
        if marker in t:
            kk_score += 1

    for marker in russian_markers:
        if marker in t:
            ru_score += 1

    if kk_score > ru_score:
        return "kk"

    return "ru"


# ============================================================
# INTENT DETECTION
# ============================================================

def has_stock_question(text: str) -> bool:
    t = clean_text(text)

    patterns = [
        r"\bесть\b",
        r"\bесть ли\b",
        r"\bв наличии\b",
        r"\bналичии\b",
        r"\bимеется\b",
        r"\bимеются\b",
        r"\bнайдется\b",
        r"\bнайдётся\b",
        r"\bбарма\b",
        r"\bбар ма\b",
        r"\bбар\b",
    ]

    return any(re.search(pattern, t) for pattern in patterns)


def has_price_question(text: str) -> bool:
    t = clean_text(text)

    patterns = [
        r"\bцена\b",
        r"\bцену\b",
        r"\bцены\b",
        r"\bсколько стоит\b",
        r"\bсколько стоят\b",
        r"\bпочем\b",
        r"\bпо чем\b",
        r"\bбагасы\b",
        r"\bбағасы\b",
        r"\bқанша\b",
        r"\bканша\b",
        r"\bтұрады\b",
        r"\bтурады\b",
    ]

    return any(re.search(pattern, t) for pattern in patterns)


def has_order_question(text: str) -> bool:
    t = clean_text(text)

    patterns = [
        r"\bзаказ\b",
        r"\bзаказа\b",
        r"\bзаказу\b",
        r"\bзаказом\b",
        r"\bгде мой заказ\b",
        r"\bстатус заказа\b",
        r"\bстатус\b",
    ]

    return any(re.search(pattern, t) for pattern in patterns)


def has_warranty_question(text: str) -> bool:
    t = clean_text(text)

    warranty_words = [
        "гарантия",
        "гарантию",
        "гарантии",
        "гарантий",
        "гарант",
    ]

    installation_words = [
        "установка",
        "установку",
        "установке",
        "установки",
        "установить",
        "монтаж",
        "монтажа",
        "монтажу",
        "монтажом",
    ]

    has_warranty = any(word in t for word in warranty_words)
    has_installation = any(word in t for word in installation_words)

    return has_warranty and has_installation


def has_engine_origin_question(text: str) -> bool:
    t = clean_text(text)

    patterns = [
        # Origin / source
        r"\bоткуда двигатель\b",
        r"\bоткуда мотор\b",
        r"\bоткуда этот двигатель\b",
        r"\bоткуда этот мотор\b",

        # Mileage
        r"\bкакой пробег\b",
        r"\bкакой пробег у мотора\b",
        r"\bкакой пробег у двигателя\b",
        r"\bпробег двигателя\b",
        r"\bпробег мотора\b",
        r"\bпробег у двигателя\b",
        r"\bпробег у мотора\b",

        # Contract engine
        r"\bмотор контрактный\b",
        r"\bдвигатель контрактный\b",
        r"\bконтрактный мотор\b",
        r"\bконтрактный двигатель\b",
        r"\bконтрактный\b",

        # Imported / origin wording
        r"\bоткуда привезен\b",
        r"\bоткуда привезён\b",
        r"\bоткуда привезли\b",
        r"\bгде стоял двигатель\b",
        r"\bгде стоял мотор\b",

        # Kazakh
        r"\bқайдан келген\b",
        r"\bқайдан әкелінген\b",
        r"\bпробегі қанша\b",
        r"\bпробеги қанша\b",
        r"\bконтрактный ма\b",
        r"\bконтрактныйма\b",
    ]

    return any(re.search(pattern, t) for pattern in patterns)


# ============================================================
# ENGINE CODE DETECTION
# ============================================================

def detect_engine_code(text: str) -> str | None:
    t = clean_text(text)

    # Cyrillic "м" -> Latin "m"
    #
    # м113 -> m113
    # м112 -> m112
    # м272 -> m272
    normalized = t.replace("м", "m")

    patterns = [
        # Mercedes
        r"\b(m\d{3})\b",
        r"\b(om\d{3})\b",

        # BMW
        r"\b(n\d{2})\b",
        r"\b(b\d{2})\b",

        # Toyota
        r"\b(1jz)\b",
        r"\b(2jz)\b",
        r"\b(4jz)\b",

        # Mitsubishi
        r"\b(4g63)\b",
        r"\b(4g64)\b",
        r"\b(4b11)\b",
        r"\b(4b12)\b",

        # VAG
        r"\b(2\.0\s*tfsi)\b",
        r"\b(2\.0\s*tsi)\b",
        r"\b(1\.8\s*tfsi)\b",
        r"\b(1\.8\s*tsi)\b",
    ]

    for pattern in patterns:
        match = re.search(
            pattern,
            normalized,
            re.IGNORECASE,
        )

        if match:
            return match.group(1).upper().replace(" ", "")

    return None


def has_engine_word(text: str) -> bool:
    t = clean_text(text)

    engine_words = [
        "двигатель",
        "двигателя",
        "двигателю",
        "двигателем",
        "мотор",
        "мотора",
        "мотору",
        "мотором",
        "engine",
        "моторчик",
    ]

    return any(word in t for word in engine_words)


# ============================================================
# PART DETECTION
# ============================================================

def detect_part(text: str) -> dict[str, Any]:
    t = clean_text(text)

    result = {
        "name": None,
        "position": None,
    }

    # --------------------------------------------------------
    # ENGINE
    # --------------------------------------------------------

    engine_code = detect_engine_code(t)

    if engine_code or has_engine_word(t):
        result["name"] = "engine"
        result["position"] = None
        return result

    # --------------------------------------------------------
    # BRAKE PADS
    # --------------------------------------------------------

    brake_pad_patterns = [
        "колодки",
        "колодка",
        "тормозные колодки",
        "тормозная колодка",
        "brake pad",
        "brake pads",
    ]

    if any(pattern in t for pattern in brake_pad_patterns):
        result["name"] = "brake_pad"

        if any(
            word in t
            for word in [
                "передние",
                "передняя",
                "передние колодки",
                "front",
            ]
        ):
            result["position"] = "front"

        elif any(
            word in t
            for word in [
                "задние",
                "задняя",
                "задние колодки",
                "rear",
            ]
        ):
            result["position"] = "rear"

        return result

    # --------------------------------------------------------
    # OIL FILTER
    # --------------------------------------------------------

    oil_filter_patterns = [
        "масляный фильтр",
        "масляный",
        "oil filter",
        "oil_filter",
    ]

    if any(pattern in t for pattern in oil_filter_patterns):
        result["name"] = "oil_filter"
        return result

    # --------------------------------------------------------
    # AIR FILTER
    # --------------------------------------------------------

    air_filter_patterns = [
        "воздушный фильтр",
        "воздушный",
        "air filter",
        "air_filter",
    ]

    if any(pattern in t for pattern in air_filter_patterns):
        result["name"] = "air_filter"
        return result

    # --------------------------------------------------------
    # BATTERY
    # --------------------------------------------------------

    battery_patterns = [
        "аккумулятор",
        "акб",
        "battery",
    ]

    if any(pattern in t for pattern in battery_patterns):
        result["name"] = "battery"
        return result

    # --------------------------------------------------------
    # STARTER
    # --------------------------------------------------------

    starter_patterns = [
        "стартер",
        "стартеры",
        "starter",
    ]

    if any(pattern in t for pattern in starter_patterns):
        result["name"] = "starter"
        return result

    # --------------------------------------------------------
    # ALTERNATOR
    # --------------------------------------------------------

    alternator_patterns = [
        "генератор",
        "гену",
        "alternator",
    ]

    if any(pattern in t for pattern in alternator_patterns):
        result["name"] = "alternator"
        return result

    # --------------------------------------------------------
    # RADIATOR
    # --------------------------------------------------------

    radiator_patterns = [
        "радиатор",
        "радиатору",
        "radiator",
    ]

    if any(pattern in t for pattern in radiator_patterns):
        result["name"] = "radiator"
        return result

    # --------------------------------------------------------
    # STEERING RACK
    # --------------------------------------------------------

    steering_rack_patterns = [
        "рулевая рейка",
        "рулевую рейку",
        "рулевой рейка",
        "рулевая",
        "рейка",
        "steering rack",
        "steering_rack",
    ]

    if any(pattern in t for pattern in steering_rack_patterns):
        result["name"] = "steering_rack"
        result["position"] = None
        return result

    # --------------------------------------------------------
    # AUTOMATIC TRANSMISSION
    # --------------------------------------------------------

    transmission_patterns = [
        "акпп",
        "акп",
        "автомат",
        "автоматическая коробка",
        "автоматическая коробка передач",
        "automatic transmission",
        "automatic_transmission",
    ]

    if any(pattern in t for pattern in transmission_patterns):
        result["name"] = "automatic_transmission"
        return result

    return result


# ============================================================
# VEHICLE DETECTION
# ============================================================

def detect_vehicle(text: str) -> dict[str, Any]:
    t = clean_text(text)

    result = {
        "brand": None,
        "model": None,
        "generation": None,
        "year": None,
        "engine": None,
        "body": None,
    }

    # ========================================================
    # TOYOTA CAMRY
    # ========================================================

    camry_patterns = [
        r"\bcamry\b",
        r"\bкамри\b",
    ]

    if any(re.search(pattern, t) for pattern in camry_patterns):
        result["brand"] = "Toyota"
        result["model"] = "Camry"

        # Camry 70 / XV70
        if (
            re.search(r"\b70\b", t)
            or re.search(r"\bxv70\b", t)
        ):
            result["generation"] = "XV70"

        elif re.search(r"\b55\b", t):
            result["generation"] = "XV50"

        elif re.search(r"\b50\b", t):
            result["generation"] = "XV50"

        elif re.search(r"\b40\b", t):
            result["generation"] = "XV40"

        elif re.search(r"\b30\b", t):
            result["generation"] = "XV30"

    # ========================================================
    # MERCEDES
    # ========================================================

    if any(
        word in t
        for word in [
            "мерседес",
            "мерс",
            "mercedes",
            "benz",
        ]
    ):
        result["brand"] = "Mercedes"

    # ========================================================
    # MERCEDES W-CODES
    # ========================================================

    w_match = re.search(
        r"\b(w\d{3})\b",
        t,
        re.IGNORECASE,
    )

    if w_match:
        generation = w_match.group(1).upper()
        result["generation"] = generation

        if result["brand"] is None:
            result["brand"] = "Mercedes"

    # ========================================================
    # MERCEDES E-CLASS
    # ========================================================

    if re.search(r"\be[\s-]?class\b", t):
        if result["brand"] is None:
            result["brand"] = "Mercedes"

        result["model"] = "E-Class"

    # ========================================================
    # BMW
    # ========================================================

    # Russian:
    # бмв
    # бмвшный
    #
    # English:
    # bmw
    #
    # Keep BMW canonical.
    bmw_patterns = [
        r"\bbmw\b",
        r"\bбмв\b",
        r"\bбмвшн",
    ]

    if any(re.search(pattern, t, re.IGNORECASE) for pattern in bmw_patterns):
        result["brand"] = "BMW"

    # ========================================================
    # BMW E / F / G CHASSIS CODES
    # ========================================================

    # Users may write:
    #
    # E60
    # e60
    # е60   <- Cyrillic е
    #
    # Normalize Cyrillic Е to Latin E before matching.
    bmw_normalized = t.replace("е", "e")

    bmw_chassis_patterns = [
        r"\b(e\d{2})\b",
        r"\b(f\d{2})\b",
        r"\b(g\d{2})\b",
    ]

    bmw_generation = None

    for pattern in bmw_chassis_patterns:
        match = re.search(
            pattern,
            bmw_normalized,
            re.IGNORECASE,
        )

        if match:
            bmw_generation = match.group(1).upper()
            break

    if bmw_generation:
        result["generation"] = bmw_generation

        # BMW chassis codes identify the vehicle generation.
        #
        # If BMW was not explicitly written, chassis code itself
        # is enough to identify BMW in this context.
        if result["brand"] is None:
            result["brand"] = "BMW"

    # ========================================================
    # BMW COMMON MODELS
    # ========================================================

    # Keep model separate from chassis generation.
    #
    # E60 = 5 Series
    # E39 = 5 Series
    # E46 = 3 Series
    # E90 = 3 Series
    # F10 = 5 Series
    # F30 = 3 Series
    #
    # This gives the backend useful canonical model information
    # while keeping E60/F10/etc. as generation.

    bmw_model_by_generation = {
        "E39": "5 Series",
        "E60": "5 Series",
        "E61": "5 Series",
        "F10": "5 Series",
        "F11": "5 Series",

        "E46": "3 Series",
        "E90": "3 Series",
        "E91": "3 Series",
        "E92": "3 Series",
        "E93": "3 Series",
        "F30": "3 Series",
        "F31": "3 Series",

        "E65": "7 Series",
        "E66": "7 Series",
        "F01": "7 Series",
        "F02": "7 Series",

        "E53": "X5",
        "E70": "X5",
        "F15": "X5",

        "E83": "X3",
        "F25": "X3",

        "E87": "1 Series",
        "F20": "1 Series",
    }

    if (
        result["brand"] == "BMW"
        and result["generation"] in bmw_model_by_generation
    ):
        result["model"] = bmw_model_by_generation[
            result["generation"]
        ]

    # ========================================================
    # ENGINE CODE
    # ========================================================

    engine_code = detect_engine_code(t)

    if engine_code:
        result["engine"] = engine_code

    return result


# ============================================================
# ORDER NUMBER
# ============================================================

def detect_order_number(text: str) -> str | None:
    t = clean_text(text)

    # "заказ 123456"
    match = re.search(
        r"\bзаказ\s*[#№]?\s*([a-z0-9-]+)\b",
        t,
        re.IGNORECASE,
    )

    if match:
        return match.group(1)

    # "#ABC123"
    match = re.search(
        r"[#№]\s*([a-z0-9-]+)\b",
        t,
        re.IGNORECASE,
    )

    if match:
        return match.group(1)

    # "мой заказ 123456"
    match = re.search(
        r"\bмой заказ\s+([a-z0-9-]+)\b",
        t,
        re.IGNORECASE,
    )

    if match:
        return match.group(1)

    return None


# ============================================================
# MERGE HELPERS
# ============================================================

def merge_values(
    deterministic: Any,
    qwen: Any,
) -> Any:
    if deterministic is not None:
        return deterministic

    return qwen


def merge_vehicle(
    deterministic: dict[str, Any],
    qwen: dict[str, Any],
) -> dict[str, Any]:

    result = {
        "brand": None,
        "model": None,
        "generation": None,
        "year": None,
        "engine": None,
        "body": None,
    }

    for key in result:
        deterministic_value = deterministic.get(key)
        qwen_value = qwen.get(key)

        result[key] = merge_values(
            deterministic_value,
            qwen_value,
        )

    return result


def merge_part(
    deterministic: dict[str, Any],
    qwen: dict[str, Any],
) -> dict[str, Any]:

    result = {
        "name": None,
        "position": None,
    }

    result["name"] = merge_values(
        deterministic.get("name"),
        qwen.get("name"),
    )

    result["position"] = merge_values(
        deterministic.get("position"),
        qwen.get("position"),
    )

    return result


# ============================================================
# NORMALIZE INTENT
# ============================================================

def normalize_intent(
    qwen_result: dict[str, Any],
    original_text: str,
    requested_language: str = "auto",
) -> dict[str, Any]:

    t = clean_text(original_text)

    # --------------------------------------------------------
    # LANGUAGE
    # --------------------------------------------------------

    language = detect_language(
        t,
        requested_language,
    )

    # --------------------------------------------------------
    # QWEN DATA
    # --------------------------------------------------------

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
    # DETERMINISTIC DETECTION
    # --------------------------------------------------------

    deterministic_vehicle = detect_vehicle(t)

    deterministic_part = detect_part(t)

    deterministic_order_number = detect_order_number(t)

    # --------------------------------------------------------
    # MERGE
    # --------------------------------------------------------

    vehicle = merge_vehicle(
        deterministic_vehicle,
        qwen_vehicle,
    )

    part = merge_part(
        deterministic_part,
        qwen_part,
    )

    order = {
        "number": merge_values(
            deterministic_order_number,
            qwen_order.get("number"),
        )
    }

    # --------------------------------------------------------
    # INTENT PRIORITY
    # --------------------------------------------------------

    if has_warranty_question(t):
        intent = "installation_warranty"

    elif has_engine_origin_question(t):
        intent = "engine_origin"

    elif has_order_question(t):
        intent = "order_status"

    elif has_stock_question(t):
        intent = "check_stock"

    elif has_price_question(t):
        intent = "check_price"

    elif qwen_result.get("intent"):
        intent = qwen_result["intent"]

    else:
        intent = "search_part"

    # --------------------------------------------------------
    # ENGINE CODE — AUTHORITATIVE OVERRIDE
    # --------------------------------------------------------

    engine_code = detect_engine_code(t)

    if engine_code:
        vehicle["engine"] = engine_code

        part["name"] = "engine"
        part["position"] = None

    elif has_engine_word(t):
        part["name"] = "engine"
        part["position"] = None

    # --------------------------------------------------------
    # ENGINE ORIGIN
    # --------------------------------------------------------

    if has_engine_origin_question(t):
        intent = "engine_origin"

        if (
            has_engine_word(t)
            or engine_code
            or any(
                word in t
                for word in [
                    "пробег",
                    "контрактный",
                    "контрактная",
                    "контрактное",
                ]
            )
        ):
            part["name"] = "engine"
            part["position"] = None

    # --------------------------------------------------------
    # INSTALLATION WARRANTY
    # --------------------------------------------------------

    if has_warranty_question(t):
        intent = "installation_warranty"

        if any(
            word in t
            for word in [
                "двигатель",
                "двигателя",
                "мотор",
                "мотора",
                "движок",
                "движка",
            ]
        ):
            part["name"] = "engine"
            part["position"] = None

        elif engine_code:
            part["name"] = "engine"
            part["position"] = None

    # --------------------------------------------------------
    # ENGINE STOCK / PRICE
    # --------------------------------------------------------

    if engine_code:
        if has_stock_question(t):
            intent = "check_stock"

        elif has_price_question(t):
            intent = "check_price"

        elif not has_engine_origin_question(t):
            if not has_warranty_question(t):
                if qwen_result.get("intent") == "search_part":
                    intent = "search_part"

    # --------------------------------------------------------
    # ORDER
    # --------------------------------------------------------

    if has_order_question(t):
        intent = "order_status"

    # --------------------------------------------------------
    # FINAL RESULT
    # --------------------------------------------------------

    return {
        "intent": intent,
        "language": language,
        "vehicle": {
            "brand": vehicle.get("brand"),
            "model": vehicle.get("model"),
            "generation": vehicle.get("generation"),
            "year": vehicle.get("year"),
            "engine": vehicle.get("engine"),
            "body": vehicle.get("body"),
        },
        "part": {
            "name": part.get("name"),
            "position": part.get("position"),
        },
        "order": {
            "number": order.get("number"),
        },
    }


# ============================================================
# LOCAL TESTS
# ============================================================

if __name__ == "__main__":

    test_messages = [

        # ----------------------------------------------------
        # TOYOTA
        # ----------------------------------------------------

        "камри 70 передние колодки есть?",
        "камри 70 задние колодки есть?",
        "камри 70 передние колодки сколько стоят?",

        # ----------------------------------------------------
        # MERCEDES
        # ----------------------------------------------------

        "мерс w211 автомат барма багасы канша",
        "w211 автомат есть?",
        "мерседес w211 передние колодки есть?",

        # ----------------------------------------------------
        # ENGINE M113 — CYRILLIC
        # ----------------------------------------------------

        "м113 мотор барма?",
        "мотор м113 барма?",
        "мотор барма м113?",
        "мотор м113 канша тұрады?",
        "м113 мотор",
        "мерс м113 мотор барма?",
        "мерседес м113 двигатель есть?",
        "w211 м113 двигатель есть?",
        "м113 на w211 есть?",

        # ----------------------------------------------------
        # ENGINE M113 — LATIN
        # ----------------------------------------------------

        "m113 двигатель есть?",
        "двигатель m113 в наличии?",
        "m113 барма?",
        "мотор m113 барма?",
        "m113 мотор багасы канша?",

        # ----------------------------------------------------
        # OTHER ENGINES
        # ----------------------------------------------------

        "m112 мотор есть?",
        "m272 двигатель есть?",
        "om642 мотор есть?",
        "n54 двигатель есть?",
        "b58 мотор есть?",
        "2jz мотор есть?",
        "1jz мотор есть?",
        "4g63 двигатель есть?",
        "4b11 мотор есть?",

        # ----------------------------------------------------
        # PARTS
        # ----------------------------------------------------

        "масляный фильтр камри 70 есть?",
        "воздушный фильтр camry 70 есть?",
        "аккумулятор camry 70 сколько стоит?",
        "стартер w211 есть?",
        "генератор w211 есть?",
        "радиатор w211 есть?",
        "акпп w211 есть?",

        # ----------------------------------------------------
        # STEERING RACK
        # ----------------------------------------------------

        "рулевая рейка барма бмв е60",
        "бмв е60 рулевая рейка есть?",
        "есть рулевая рейка на бмв е60?",
        "рулевая рейка бмв е60",
        "bmw e60 steering rack",
        "бмв е60 рейка",
        "рулевую рейку бмв е60 есть?",
        "рейка на е60 есть?",

        # ----------------------------------------------------
        # BMW OTHER CHASSIS
        # ----------------------------------------------------

        "bmw e46 рулевая рейка есть?",
        "бмв е90 стартер есть?",
        "bmw f10 генератор есть?",
        "бмв f30 радиатор есть?",

        # ----------------------------------------------------
        # ORDERS
        # ----------------------------------------------------

        "где мой заказ 123456?",
        "заказ #ABC123 где?",

        # ----------------------------------------------------
        # WARRANTY
        # ----------------------------------------------------

        "на установку двигателя есть гарантия?",
        "какая гарантия на установку?",
        "есть гарантия на установку мотора?",
        "гарантия на установку двигателя есть?",

        # ----------------------------------------------------
        # ENGINE ORIGIN
        # ----------------------------------------------------

        "откуда двигатель?",
        "какой пробег у мотора?",
        "мотор контрактный?",
        "двигатель контрактный?",
        "какой пробег у двигателя m113?",
        "откуда мотор m113?",
    ]

    # Minimal fake Qwen response.
    empty_qwen = {
        "intent": None,
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
    }

    for message in test_messages:

        result = normalize_intent(
            empty_qwen,
            message,
            "auto",
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