help:
	@echo make init
	@echo ""
	@echo make run
	@echo make run-1
	@echo make run-2
	@echo make run-3

init:
	uv venv --python 3.12

run: run-2

run-1:
	uv run research_write_article.py

run-2:
	uv run customer_support.py

run-3:
	uv run customer_outreach.py