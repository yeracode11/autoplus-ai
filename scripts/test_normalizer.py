import json

from normalizer import normalize_intent


TESTS = [
    {
        "name": "Camry 70",
        "input": {
            "intent": "check_stock",
            "vehicle": {
                "brand": "Toyota",
                "model": "Camry",
                "generation": "70",
            },
            "part": {
                "category": "brake_pad",
                "position": "front",
            },
            "query": "передние колодки",
        },
    },

    {
        "name": "Camry 70 Kazakh",
        "input": {
            "intent": "check_stock",
            "vehicle": {
                "brand": "Toyota",
                "model": "Camry",
                "generation": "70",
            },
            "part": {
                "category": "brake_pad",
                "position": "алдыңғы",
            },
            "query": "алдыңғы колодка",
        },
    },

    {
        "name": "Mercedes W211",
        "input": {
            "intent": "check_stock",
            "vehicle": {
                "brand": "мерс",
                "model": "211",
            },
            "part": {
                "category": "капот",
            },
            "query": "капот",
        },
    },

    {
        "name": "BMW F10",
        "input": {
            "intent": "search_part",
            "vehicle": {
                "brand": "bmw",
                "model": "f10",
            },
            "part": {
                "category": "фара",
                "position": "задняя",
            },
            "query": "задняя фара",
        },
    },

    {
        "name": "Hyundai Solaris",
        "input": {
            "intent": "search_part",
            "vehicle": {
                "brand": "хундай",
                "model": "солярис",
            },
            "part": {
                "category": "тормоз",
                "subcategory": "колодка",
            },
            "query": "тормоз колодка",
        },
    },

    {
        "name": "Lada Priora",
        "input": {
            "intent": "search_part",
            "vehicle": {
                "brand": "lada",
                "model": "priora",
            },
            "part": {
                "category": "фара",
                "side": "оң жақ",
            },
            "query": "фара оң жақ priora",
        },
    },
]


def main():
    passed = 0

    for test in TESTS:
        result = normalize_intent(test["input"])

        print("=" * 70)
        print(test["name"])
        print(json.dumps(
            result,
            ensure_ascii=False,
            indent=2
        ))

        passed += 1

    print()
    print(f"Successful: {passed}")
    print(f"Total: {len(TESTS)}")


if __name__ == "__main__":
    main()
