# Speak Easy

## Installing

### Install [pipenv](https://github.com/pypa/pipenv)

#### Debian and Ubuntu based
```shell
sudo apt update
sudo apt install pipenv
```

#### Arch based

```shell
sudo pacman -Sy python-pipenv
```

### Install dependencies

```shell
pipenv install
```

## Running

### Enter to pipenv shell

```shell
pipenv shell
```

### Start the server

```shell
uvicorn src.main:app
```
> [!NOTE]
> You can also append `--reload` flag for development.

## Docs

Go to http://127.0.0.1:8000/docs for swagger documentation.

FastAPI also provides redocly. You can find it at http://127.0.0.1:8000/redoc
