# Tests

## Unit tests

Run tests by executing `python -m tests.tests` from the project root.

## Integration Tests

1. Make sure docker is installed and running.
2. Run `docker-compose up` to launch the integration test environment, mainly a local instance of mongoDB that will be used as the test DDBB. Alternatively, you can run the script `.\scripts\test-env.bat`. **OBSOLETE due to changing `.env` to `.ddbb.env`**: If you are running docker compose V2, you might be required to run `docker compose --env-file .empty.env up` for the command to work. It seems that when using V2, the environment file `.env` is read by default (even if its contents are not docker related) and since it has not been created for docker, its contents are invalid and the command will fail. See this [issue](https://github.com/docker/compose/issues/6741) and this [PR](https://github.com/docker/compose/pull/6850) for more details.
3. Run `python -m tests.integration_tests` from the project root.

### Test DDBB

Once docker is up and the mongoDB container is running, you can connect to the test DDBB using the following command (make sure that [mongosh](https://docs.mongodb.com/mongodb-shell/install/) is installed):

```
mongosh mongodb://admin:admin@127.0.0.1:27017/RocoLib?authSource=admin 
```

Once connected to the test DDBB, the following commands might be useful:

* ` db.getCollectionInfos()`: to list all collections in the DDBB.
* `db['COLLECTION_NAME'].find()`: to list all documents in a collection.