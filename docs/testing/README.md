# Tests

## Unit tests

Run tests by executing `python -m tests.tests` from the project root.

## Integration Tests

1. Make sure docker is installed and running.
2. Run `docker-compose up` to launch the integration test environment, mainly a local instance of mongoDB. If you are running docker compose V2, you might be required to run `docker compose --env-file .empty.env up` for the command to work. It seems that when using V2, the environment file `.env` is read by default (even if its contents are not docker related) and since it has not been created for docker, its contents are invalid and the command will fail. See this [issue](https://github.com/docker/compose/issues/6741) and this [PR](https://github.com/docker/compose/pull/6850) for more details. Alternatively, you can run the script `test-env.bat`, which will run the appropriate command depending on the current docker compose version.
3. Run `python -m tests.integration_tests` from the project root.