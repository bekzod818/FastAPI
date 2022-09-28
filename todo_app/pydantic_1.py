from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ValidationError


class User(BaseModel):
    id: int
    name = "John Doe"
    signup_ts: Optional[datetime] = None
    friends: List[int] = []

external_data = {
    'id': 123,
    'signup_ts': '2022-07-27 12:03:00',
    'friends': [1, 2, '3']
}
try:
    user = User(**external_data)
    print(user.dict())
except ValidationError as e:
    print(e.json())
