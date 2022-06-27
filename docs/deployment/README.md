# RocoLib deployment options
## Docker Image

### Build and push RocoLib image

```
docker build -t rocolib -f .\Dockerfile .
docker tag rocolib:latest juangallostra/rocolib:latest
docker push juangallostra/rocolib:latest
```

### Pull image

```
docker pull juangallostra/rocolib:latest
```

### Run image

```
docker run -p 9090:80 juangallostra/rocolib
```

If you don't want to make use of the provided swagger API docs, you can replace `9090` by the port of your choice. However, if you want to run the image an be able to test the API via swagger, you must map port `80` on the container to port `9090` on the host. This is so because the Swagger docs expect the server to be running at the port `9090`.

Go to `http://localhost:9090` to access the application.

## From source

### Clone repo

### Install dependencies

### DDBB Connection

### Launch