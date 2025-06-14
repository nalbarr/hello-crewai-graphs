from crewai import Agent, Task, Crew
import os
import yaml


def filter_warnings():
    import warnings

    warnings.filterwarnings("ignore")


def init():
    from utils import get_openai_api_key, register_phoenix_otel

    get_openai_api_key()
    os.environ["OPENAI_MODEL_NAME"] = "gpt-4o-mini"

    register_phoenix_otel(
        project_name="default",
        endpoint="http://localhost:6006/v1/traces",
    )


def load_configs():
    files = {
        "agents": "config/support_data_analysis_agents.yaml",
        "tasks": "config/support_data_analysis_tasks.yaml",
    }

    configs = {}
    for config_type, file_path in files.items():
        with open(file_path, "r") as file:
            configs[config_type] = yaml.safe_load(file)

    return configs


async def get_emails(flow):
    emails = await flow.kickoff()
    return emails


def main():
    filter_warnings()

    init()
    configs = load_configs()

    agents_config = configs["agents"]
    tasks_config = configs["tasks"]

    # tools
    from crewai_tools import FileReadTool

    csv_tool = FileReadTool(file_path="./support_tickets_data.csv")

    suggestion_generation_agent = Agent(
        config=agents_config["suggestion_generation_agent"], tools=[csv_tool]
    )

    reporting_agent = Agent(config=agents_config["reporting_agent"], tools=[csv_tool])

    chart_generation_agent = Agent(
        config=agents_config["chart_generation_agent"], allow_code_execution=False
    )

    # Creating Tasks
    suggestion_generation = Task(
        config=tasks_config["suggestion_generation"], agent=suggestion_generation_agent
    )

    table_generation = Task(
        config=tasks_config["table_generation"], agent=reporting_agent
    )

    chart_generation = Task(
        config=tasks_config["chart_generation"], agent=chart_generation_agent
    )

    final_report_assembly = Task(
        config=tasks_config["final_report_assembly"],
        agent=reporting_agent,
        context=[suggestion_generation, table_generation, chart_generation],
    )

    support_report_crew = Crew(
        agents=[suggestion_generation_agent, reporting_agent, chart_generation_agent],
        tasks=[
            suggestion_generation,
            table_generation,
            chart_generation,
            final_report_assembly,
        ],
        verbose=True,
    )

    # support_report_crew.test(n_iterations=1, eval_llm=="gpt-4o")
    support_report_crew.test(n_iterations=1, eval_llm="gpt-4o")

    support_report_crew.train(n_iterations=1, filename="training.pkl")

    # support_report_crew.test(n_iterations=1, eval_llm=="gpt-4o")

    result = support_report_crew.kickoff()
    print(f"result: {result}")


if __name__ == "__main__":
    main()
