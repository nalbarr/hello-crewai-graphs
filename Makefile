SRC= utils.py \
	research_write_article.py \
	customer_support.py \
	customer_outreach.py \
	event_planning.py \
	financial_analysis.py \
	multi_agent.py \
	automated_project.py \

help:
	@echo make init
	@echo ""
	@echo make lint
	@echo make format
	@echo ""
	@echo make run
	@echo ""
	@echo make run-1
	@echo make run-2
	@echo make run-3
	@echo make run-4
	@echo make run-5
	@echo make run-6
	@echo make run-7

init:
	uv venv --python 3.12

lint:
	flake8 $(SRC)

format:
	black $(SRC)

run: run-1

clean:
	rm -rf ./db

run-1:
	uv run research_write_article.py

run-2:
	uv run customer_support.py

run-3:
	uv run customer_outreach.py

run-4:
	uv run event_planning.py

run-5: clean
	uv run financial_analysis.py

run-6:
	uv run multi_agent.py

run-7:
	uv run automated_project.py
