.PHONY: run start test seed install clean

install:
	pip install -r requirements.txt

run:
	python main.py

start:
	python main.py

test:
	pytest tests/ -v

seed:
	python -m scripts.seed

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
