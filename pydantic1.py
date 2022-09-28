from pydantic import BaseModel, ValidationError, \
    Field


class Tag(BaseModel):
    id: int
    tag: str


class City(BaseModel):
    city_id: int
    name: str = Field(alias="cityName")
    population: int
    tags: list[Tag]


input_json = """
{
    "city_id": 12,
    "cityName": "Showot",
    "population": 234567,
    "tags": [
        {
            "id": 1,
            "tag": "dim yomon"
        },
        {
            "id": 2,
            "tag": "tozaqu bi"
        }
    ]
}
"""

try:
    city = City.parse_raw(input_json)
except ValidationError as e:
    print("Exception", e.json())
else:
    print(city.json(by_alias=True, exclude={'city_id', 'population'})) # exclude shu maydonlarni chiqarmaydi, alias JSON faylni maydonlarini 2-nom bilan nomlash JS uchun qulay bo'lishi uchun kerak
    x = city.tags[1]
    print(x.json())