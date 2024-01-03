from bson import ObjectId
from fastapi import APIRouter, status

from models.todos import ToDo

from .database import collection
from .schemas import list_serial

router = APIRouter()


# GET Request Method
@router.get("/")
async def get_todos():
    todos = list_serial(collection.find())
    return todos


# POST Request Method
@router.post("/", status_code=status.HTTP_201_CREATED)
async def post_todo(todo: ToDo):
    collection.insert_one(dict(todo))
    return {"message": "Inserted successfully"}


# PUT Request Method
@router.put("/{id}", status_code=status.HTTP_200_OK)
async def put_todo(id: str, todo: ToDo):
    collection.find_one_and_update({"_id": ObjectId(id)}, {"$set": dict(todo)})
    return {"message": "Updated successfully"}


# DELETE Request Method
@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(id: str):
    collection.find_one_and_delete({"_id": ObjectId(id)})
    return {"message": "Deleted successfully"}
