poetry env activate
poetry run alembic revision --autogenerate -m "Add user"
poetry run alembic upgrade head

poetry run pytest --cov=src tests/
poetry run pytest -v tests/test_contact_repository_unit.py
poetry run pytest -v tests/test_integration_auth.py
poetry run pytest -v tests/test_integration_contacts.py
poetry run pytest -v tests/test_integration_users.py
