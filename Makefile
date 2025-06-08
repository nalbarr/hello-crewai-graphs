help:
	@echo make init
	@echo make run

init:
	uv venv --python 3.12

run: run-1

run-1:
	python research_write_article.py
