import json
from typing import Dict, Any


def save_dict_as_json(data: Dict[str, Any], path: str) -> None:
    """
    Saves a dictionary as a JSON file at the specified path.

    Args:
        data (Dict[str, Any]): The dictionary to save.
        path (str): The file path where the JSON will be saved.
    """
    product_list = []
    for stores in data.keys():
        for games in data[stores].keys():
            if data[stores][games]:
                product_list.extend(data[stores][games])

    with open(path, 'w', encoding='utf-8') as f:
        json.dump(product_list, f, ensure_ascii=False, indent=4)
