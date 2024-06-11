start:
	gunicorn -w 4 share_trip_experience:app

lint:
	poetry run flake8 share_trip_experience
	poetry run flake8 tests

test:
	make lint
	pytest
