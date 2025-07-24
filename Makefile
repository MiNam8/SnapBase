# ---------- APP ----------

run:
	poetry run python3 run.py

# ---------- MIGRATIONS ----------
upgrade: 
	poetry run alembic upgrade head

downgrade:
	poetry run alembic downgrade -1