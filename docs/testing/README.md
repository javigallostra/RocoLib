# Tests

Run tests by executing `python -m tests.entity_tests` from the project root.

## Integration Tests

1. Make sure docker is installed and running.
2. Run `docker-compose up` to launch the integration test environment, mainly a local instance of mongoDB.
3. Run `python -m tests.integration_tests` from the project root.