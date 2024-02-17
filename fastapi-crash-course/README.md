# FastAPI - Быстрый курс за 1 час [2024]

Разбор фреймворка FastAPI с первых строчек до деплоя на реальный сервер.

#backend #python #fastapi

[Youtube Video](https://www.youtube.com/watch?v=gBfkX9H3szQ)

## Подготовка сервера

### git
```
sudo apt-get update
sudo apt-get install git
```

### docker
Можно воспользоваться инструкцией: https://docs.docker.com/engine/install/ubuntu/ или скопировать код ниже
```
sudo apt-get update
sudo apt-get install ca-certificates curl gnupg
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update

sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

### Запуск приложения

Создание образа (коробки) с приложением

```
docker build . --tag fastapi_app
```

Запуск образа в контейнере с пробросом портов для доступа к контейнеру из интернета

```
docker run -p 80:80 fastapi_app
```

```
docker build . --tag fastapi_app && docker run -p 80:80 fastapi_app
```
