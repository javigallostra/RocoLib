# RocoLib

Simple Web App to create and share boulders & routes for any climbing wall.

Check it out at:

- [https://rocolib.herokuapp.com/](https://rocolib.herokuapp.com/)
  
We also offer a public API. Its documentation can be found at:

- [https://rocolib.herokuapp.com/api/v1/docs](https://rocolib.herokuapp.com/api/v1/docs)

Powered by [Flask](https://flask.palletsprojects.com/en/1.1.x/), [Python 3.9.7](https://www.python.org/) and [Bootstrap](https://getbootstrap.com/). API docs are generated with [Swagger](https://swagger.io/). Also using [MongoDB Atlas](https://www.mongodb.com/cloud/atlas2) and being hosted on [Heroku](https://www.heroku.com/home).

## Features

* Create problems on any climbing wall, just from an image.
* Explore and climb problems created by other users.
* Create your own ticklist, save problems that you want to climb and log your sends.
* Sort problems by difficulty, rating, creation date or setter and find your ideal climb or project.
* Rate problems so that other users can get feedback and find the best climbs.

Would like to contribute? PRs and feature requests are welcome!

Check the [issue tracker](https://github.com/javigallostra/RocoLib/issues) or [project board](https://github.com/javigallostra/RocoLib/projects/2) to see what features are being worked on or submit your request.

###### Some of the features on our TODO list are

* Public API
* ~~Localize app~~ Thanks to [Pan6ora](https://github.com/Pan6ora)
* Include a map to locate registered gyms
* ~~Show the number of repetitions of each problem~~ PR #133
* For registered users: Include a stats page
* Enable setting routes as well as problems
* Enable setting routes that span multiple images
* Enable to configure each gym independently (difficulties, colors, problem styles, etc.)
* Enable logging a climb more than once
* Add a comments section for each problem
* Enable users to suggest a difficulty after climbing a problem

## Screenshots

#### Home

<p align="center" style="text-align:center;">
<img src="/extras/images/home.JPG"><br>
Home
</p>

#### Explore problems

<p align="center" style="text-align:center;">
<img src="/extras/images/explore.JPG"><br>
Explore Boulders
</p>

#### Create problems

<p align="center" style="text-align:center;">
<img src="/extras/images/create.jpg"><br>
Create Boulders
</p>

#### Load problems

<p align="center" style="text-align:center;">
<img src="/extras/images/view.jpg"><br>
Load Boulders
</p>

## Development

### Run from Docker image

A docker image to run the app locally can be found [here](https://hub.docker.com/repository/docker/juangallostra/rocolib). To run it execute in a terminal:

```
docker pull juangallostra/rocolib
docker run -p 9090:80 juangallostra/rocolib
```

Once the container is up and running, the app can be accessed at http://localhost:9090. Note that you can replace 9090 by the port of your choice.

### Run locally

1. Clone the repository and, optionally, create a [virtual environment](https://docs.python.org/3/tutorial/venv.html) -recommended but not shown here-.
   ```
   git clone https://github.com/javigallostra/RocoLib.git
   ```
2. Install dependencies
   ```
   pip install -r requirements.txt
   ```
3. Set up [MongoDB](https://www.mongodb.com). This can either be a local instance of MongoDB or an instance running on the cloud. We are currently using MongoDB Atlas free tier.
4. Configure MongoDB connection so that the application code can talk with the DDBB.
5. Run
   ```
   python application.py
   ```

## Links of interest

* [Yolo Bouldering](https://github.com/yarkhinephyo/yolo_bouldering)
* [Climbnet](https://github.com/cydivision/climbnet)