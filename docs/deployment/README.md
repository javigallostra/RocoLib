# RocoLib deployment options

## Docker Image

To deploy the application from the provided Docker Image follow the next steps.

### Build and push RocoLib image

This step is not required, it is just a reminder on how to build and push the image from source. Go to the next step to pull the image with the latest version. 

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

Open a new terminal at the directory in which you want the source to be located and clone the repo.

```
git clone https://github.com/javigallostra/RocoLib.git
```

### Install dependencies

Install the required dependencies via `pip`. I would recommend to do so via a virtual environment.  

```
pip install -r requirements.txt
```

### DDBB Connection

Create a `creds.txt` file at the root of the project and add your mongoDB connection string.

### Launch

Launch with

```
python application.py
```

This will launch a local version of the webapp running at `localhost:5050`. If you want to listen on another port change the value of the constant `PORT` found in the `config.py` file, line 7.

## DDBB configuration

TODO