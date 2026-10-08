from typing import List


def comma_separated_items(value: str) -> List[str]:
    return [item.strip() for item in value.split(",") if item.strip()]
