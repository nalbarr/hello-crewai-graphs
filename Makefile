help:
	@echo make init
	@echo ""
	@echo make run
	@echo ""
	@echo make run-1
	@echo make run-2
	@echo make run-3
	@echo make run-4

init:
	uv venv --python 3.12

run: run-1

run-1:
	uv run research_write_article.py

run-2:
	uv run customer_support.py

run-3:
	uv run customer_outreach.py

run-4:
	uv run event_planning.py