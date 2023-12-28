from enum import StrEnum

from pydantic import BaseModel


class OrderStatus(StrEnum):
    ORDERED = "ordered"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    DECLINED = "declined"

    @classmethod
    def _missing_(cls, value):
        value = value.lower()
        for member in cls:
            if member.value == value:
                return member
        return None


print(OrderStatus("Ordered"))
print(OrderStatus("oRdErEd"))
print(OrderStatus("OrdeRED").value)

print(OrderStatus("ShIppeD"))
print(OrderStatus("sHiPPEd"))

# https://docs.python.org/3/library/enum.html#enum.StrEnum
"""
StrEnum is the same as Enum, but its members are also strings and can be used in most of the same places that a string can be used. The result of any string operation performed on or with a StrEnum member is not part of the enumeration.
"""


class Order(BaseModel):
    user: str
    status: OrderStatus


order = Order(user="John Doe", status="orDerEd")
print(order)
order = Order(user="John Doe", status="ORDERED")
print(order)
order = Order(user="John Doe", status=OrderStatus.DELIVERED)
print(order)
