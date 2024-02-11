import json


def test_home(test_app):
    response = test_app.get("/")
    assert response.status_code == 200


def test_task_status(test_app):
    response = test_app.post("/tasks", data=json.dumps({"type": 1}))
    content = response.json()
    task_id = content["task_id"]
    assert task_id

    response = test_app.get(f"/tasks/{task_id}")
    content = response.json()
    assert content == {
        "task_id": task_id,
        "task_status": "PENDING",
        "task_result": None,
    }
    assert response.status_code == 200

    while content["task_status"] == "PENDING":
        response = test_app.get(f"/tasks/{task_id}")
        content = response.json()
    assert content == {
        "task_id": task_id,
        "task_status": "SUCCESS",
        "task_result": True,
    }
