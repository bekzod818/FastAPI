# Asynchronous Tasks with FastAPI and Celery

Example of how to handle background processes with FastAPI, Celery, and Docker.

### Quick Start

Spin up the containers:

```sh
$ docker-compose up -d --build
```

Try adding a few more workers to see how that affects things:
```sh
$ docker-compose up -d --build --scale worker=3
```

Test
```sh
$ docker-compose exec web python -m pytest
```

Open your browser to [http://localhost:8000](http://localhost:8000)

TUTORIAL ARTICLE: [Read More](https://testdriven.io/blog/fastapi-and-celery/)

ANOTHER ARTICLES:
1. [Dockerizing Celery and FastAPI
](https://testdriven.io/courses/fastapi-celery/docker/)
2. [Empowering Applications with Asynchronous Magic: The Celery, FastAPI, Docker, and Flower](https://medium.com/@youssefchamrah/empowering-applications-with-asynchronous-magic-the-celery-fastapi-docker-and-flower-ac119efc2e04)
