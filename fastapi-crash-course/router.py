from typing import Annotated

from fastapi import APIRouter, Depends
from repository import TaskRepository
from schemas import STask, STaskAdd, STaskId

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.get("/")
async def get_tasks() -> list[STask]:
    tasks = await TaskRepository.find_all()
    return tasks


@router.post("/")
async def add_task(task: Annotated[STaskAdd, Depends()]) -> STaskId:
    task_id = await TaskRepository.add_one(task)
    return STaskId(task_id=task_id)
