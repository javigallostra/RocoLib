# RocoLib

Simple Web App to create and share boulders & routes for any climbing wall

Check it out at:

- [https://rocolib.herokuapp.com/](https://rocolib.herokuapp.com/)

Powered by [Flask](https://flask.palletsprojects.com/en/1.1.x/), [Python 3](https://www.python.org/) and [Bootstrap](https://getbootstrap.com/).
Also using [MongoDB Atlas](https://www.mongodb.com/cloud/atlas2) and being hosted on [Heroku](https://www.heroku.com/home).

### Run from Docker image

A docker image to run the app locally can be found [here](https://hub.docker.com/repository/docker/juangallostra/rocolib). To run it execute in a terminal:

```
> docker pull juangallostra/rocolib
> docker run -p 9090:80 juangallostra/rocolib
```

Once the container is up and running, the app can be accessed at http://localhost:9090. Note that you can replace 9090 by the port of your choice.

### Run locally


## Features

* Create problems on any climbing wall, just from an image.
* Explore and climb problems created by other users.
* Create your own ticklist, save problems that you want to climb and log your sends.
* Sort problems by difficulty, rating, creation date or setter and find your ideal climb or project.
* Rate problems so that other users can get feedback and find the best climbs.

Would like to contribute? PRs and feature requests are welcome!

Check the [issue tracker](https://github.com/javigallostra/RocoLib/issues) or [project board](https://github.com/javigallostra/RocoLib/projects/2) to see what features are being worked on or submit your request.

###### Some of the features on our TODO list are

* Localize app
* Include a map to locate registered gyms
* Enable setting routes as well as problems
* Enable setting routes that span multiple images
* Make a more flexible grading system
* For registered users: Include a stats page
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

## Links of interest

* [Yolo Bouldering](https://github.com/yarkhinephyo/yolo_bouldering)