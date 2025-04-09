poetry env activate
poetry run alembic revision --autogenerate -m "Add user"
poetry run alembic upgrade head
