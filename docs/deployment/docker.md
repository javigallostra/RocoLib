# Docker

## Build and push RocoLib image

```
docker build -t rocolib -f .\Dockerfile .
docker tag rocolib:latest juangallostra/rocolib:latest
docker push juangallostra/rocolib:latest
```

## Pull image

```
docker pull juangallostra/rocolib:latest
```

## Run image
```
docker run -p 9090:80 juangallostra/rocolib
```

Replace `9090` by the port of your choice

Go to `http://localhost:9090` to access the application.