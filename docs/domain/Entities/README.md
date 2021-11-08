# RocoLib entities

Below is the list of entities and relations between them (as stored in the DDBB). 

Actual wall images are currently stored with the code, inside the `static/images/walls` path. For each gym there is a `static/images/walls/{gym_id}` folder used to store the gym images.


## Gyms

**Collection**: `walls` 
**Fields**:

* **id** (`str`): Gym identifier for internal use. 
* **name** (`str`): Display name for the gym. This is the name that the user will see.
* **coordinates** (`double[]`): Array containing the coordinates of the gym location in the form: `[Longitude, Latitude]`.

## Walls

A gym entity has an associated collection of walls. 

For each gym there is a collection `{gym_id}_walls` -where `{gym_id}` is the value of the `id` field of the gym- that contains the list of walls related to that gym. 

**Collection**: `{gym_id}_walls` 
**Fields**:

* **image** (`str`): the name of the image that should be shown when creating/showing a problem on that wall. 
* **name** (`str`): Display name of the gym section/wall. This is the name that the user will see when referring to this section/wall. 
* **radius** (`double`): the radius of the circle to be used when drawing problems in that wall.

## Problems

**Collection** `{gym_id}_boulders`
**Fields**:
* rating (`double`): Problem rating computed as the mean rating.
* raters (`int`): Number of raters.
* name (`str`): Problem name.
* creator (`str`): Username of problem creator.
* difficulty (`str`): Suggested problem difficulty.
* feet (`str`): Feet restrictions for the problem.
* holds (`holds[]`): Array of holds making the problem.
* section (`str`): Image name of the section where the climb is located.
* time (`datetime`): Creation time of the problem. The datetime is stored as a string which can be easily parsed.

**`holds` fields**:
* x (`double`): x coordinate of the center of the circle used to highlight the hold.
* y (`double`): y coordinate of the center of the circle used to highlight the hold.
* color (`str`): Hex color to use for the circle highlighting the hold.

## Users

**Collection**: `users`

**Fields**:
* email (`str`): User email.
* id (`str`): User id.
* is_admin (`bool`): Boolean value that indicates if the user has administrator privileges.
* name (`str`): User Name.
* password (`str`): Hashed user password.
* ticklist (`boulder_data[]`): Array containing the list of problems the user has climbed or wishes to climb.

**`boulder_data` fields**:
* gym (`str`): Id of the gym where the problem is located.
* iden (`str`): Problem id.
* is_done (`bool`): Boolean value that indicates wether the user has climbed the problem or not.
* section (`str`): Wall image name.
* date_climbed (`datetime[]`): Array of datetimes specifying the dates where the user climbed the problem.