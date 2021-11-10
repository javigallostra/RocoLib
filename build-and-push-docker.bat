docker build -t rocolib -f .\Dockerfile .
docker tag rocolib:latest juangallostra/rocolib:latest
docker push juangallostra/rocolib:latest