from typing import Set, Tuple, List, Dict, Union, Optional


# Python 3.6 and above
def get_items(items: List[str]):
    for item in items:
        print(item.title())


# Python 3.9 and above
def get_items(items: list[str]):
    for item in items:
        print(item.title())


# Python 3.6 and above
def process_items(items_t: Tuple[int, int, str], items_s: Set[bytes]):
    return items_t, items_s


# Python 3.9 and above
def process_items(items_t: tuple[int, int, str], items_s: set[bytes]):
    return items_t, items_s


# Python 3.6 and above
def process_items(prices: Dict[str, float]):
    for item_name, item_price in prices.items():
        print(item_name)
        print(item_price)


# Python 3.9 and above
def process_items(prices: dict[str, float]):
    for item_name, item_price in prices.items():
        print(item_name)
        print(item_price)


# Python 3.6 and above
def process_item(item: Union[int, str]):
    print(item)


# Python 3.10 and above
def process_item(item: int | str):
    print(item)


# 🚨 Avoid using Optional[SomeType]
# Instead ✨ use Union[SomeType, None] 


# Python 3.6 and above
def say_hi(name: Optional[str] = None):
    if name is not None:
        print(f"Hey {name}!")
    else:
        print("Hello World")


# Python 3.6 and above - alternative
def say_hi(name: Union[str, None] = None):
    if name is not None:
        print(f"Hey {name}!")
    else:
        print("Hello World")


# Python 3.10 and above
def say_hi(name: str | None = None):
    if name is not None:
        print(f"Hey {name}!")
    else:
        print("Hello World")
