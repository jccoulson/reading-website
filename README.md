# ReaderHub
This Django web application allows users to interact with books and each other. Useres can favorite books, look at book descriptsions, and rate them. Book information is found
from the Open Library API. Users can message each other and make posts about books for interaction.

## Dependencies

- psycopg2>=2.8
- asgiref==3.2.10
- Django==3.0.9
- sqlparse==0.2.4
- pillow == 7.0.0
- requests == 2.22.0
- coverage == 7.0.0b1

## Running Django project locally

- Run migrations using `python manage.py migrate`
- Run server using `python manage.py runserver`
- The server will run at `http://127.0.0.1:8000/` (default)

## Running with Docker Compose (PREFERRED)

- Re-build the image(s) using `docker-compose build` if any changes have been made to dependencies or the docker files
- Use command `docker-compose up` to run containers
- The server will run at `http://localhost:8000/` (default)
- To close the containers, either use `docker-compose down` in another terminal or interrupt using `CTRL + C`

NOTE: Replace `python` with `python3` if needed

## Running tests with Django

- Django allows the use of `python manage.py test` to run tests
- Append the above command with the specific app name to run app-specific tests (Ex: `python manage.py test posts`)

## Running tests with coverage.py (PREFERRED)

- Use the command `coverage run --source='.' manage.py test` to run tests
- Append the above command with the specific app name to run app-specific tests (Ex: `coverage run --source='.' manage.py test posts`)

## Retrieve coverage report

- Use the command `coverage report` to print a full report of coverage to the terminal

NOTE: The coverage report is generated based on the last test run performed
