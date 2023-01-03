coverage run -p -m tests.tests
coverage run -p -m tests.integration_tests
coverage run -p -m tests.db_controller_tests
coverage combine
coverage html