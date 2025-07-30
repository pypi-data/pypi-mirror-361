test:
	uv run pytest -v -p no:cacheprovider --exitfirst --benchmark-time-unit="s" --benchmark-autosave

cov:
	uv run pytest -p no:cacheprovider --cov-report html --cov=babylab tests/

lint:
	uv run pylint $(git ls-files '*.py')
