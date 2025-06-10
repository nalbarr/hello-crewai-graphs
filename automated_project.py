from crewai import Agent, Task, Crew
from typing import List
from pydantic import BaseModel, Field
import os
import yaml
import pandas as pd


def filter_warnings():
    import warnings

    warnings.filterwarnings("ignore")


def init():
    from utils import get_openai_api_key

    get_openai_api_key()
    os.environ["OPENAI_MODEL_NAME"] = "gpt-4o-mini"

    files = {"agents": "config/agents.yaml", "tasks": "config/tasks.yaml"}

    configs = {}
    for config_type, file_path in files.items():
        with open(file_path, "r") as file:
            configs[config_type] = yaml.safe_load(file)

    agents_config = configs["agents"]
    tasks_config = configs["tasks"]

    return agents_config, tasks_config


def project_costs(crew: Crew):
    costs = (
        0.150
        * (crew.usage_metrics.prompt_tokens + crew.usage_metrics.completion_tokens)
        / 1_000_000
    )
    print(f"Total costs: ${costs:.4f}")

    # Convert UsageMetrics instance to a DataFrame
    df_usage_metrics = pd.DataFrame([crew.usage_metrics.dict()])
    df_usage_metrics


def main():
    filter_warnings()

    agents_config, tasks_config = init()

    # models
    class TaskEstimate(BaseModel):
        task_name: str = Field(..., description="Name of the task")
        estimated_time_hours: float = Field(
            ..., description="Estimated time to complete the task in hours"
        )
        required_resources: List[str] = Field(
            ..., description="List of resources required to complete the task"
        )

    class Milestone(BaseModel):
        milestone_name: str = Field(..., description="Name of the milestone")
        tasks: List[str] = Field(
            ..., description="List of task IDs associated with this milestone"
        )

    class ProjectPlan(BaseModel):
        tasks: List[TaskEstimate] = Field(
            ..., description="List of tasks with their estimates"
        )
        milestones: List[Milestone] = Field(
            ..., description="List of project milestones"
        )

    # agents
    project_planning_agent = Agent(config=agents_config["project_planning_agent"])

    estimation_agent = Agent(config=agents_config["estimation_agent"])

    resource_allocation_agent = Agent(config=agents_config["resource_allocation_agent"])

    # task 1
    task_breakdown = Task(
        config=tasks_config["task_breakdown"], agent=project_planning_agent
    )

    # task 2
    time_resource_estimation = Task(
        config=tasks_config["time_resource_estimation"], agent=estimation_agent
    )

    # task 3
    resource_allocation = Task(
        config=tasks_config["resource_allocation"],
        agent=resource_allocation_agent,
        output_pydantic=ProjectPlan,
    )

    crew = Crew(
        agents=[project_planning_agent, estimation_agent, resource_allocation_agent],
        tasks=[task_breakdown, time_resource_estimation, resource_allocation],
        verbose=True,
    )

    from IPython.display import display, Markdown

    project = "Website"
    industry = "Technology"
    project_objectives = "Create a website for a small business"
    team_members = """
        - John Doe (Project Manager)
        - Jane Doe (Software Engineer)
        - Bob Smith (Designer)
        - Alice Johnson (QA Engineer)
        - Tom Brown (QA Engineer)
    """
    project_requirements = """
        - Create a responsive design that works well on desktop and mobile devices
        - Implement a modern, visually appealing user interface with a clean look
        - Develop a user-friendly navigation system with intuitive menu structure
        - Include an "About Us" page highlighting the company's history and values
        - Design a "Services" page showcasing the business's offerings with descriptions
        - Create a "Contact Us" page with a form and integrated map for communication
        - Implement a blog section for sharing industry news and company updates
        - Ensure fast loading times and optimize for search engines (SEO)
        - Integrate social media links and sharing capabilities
        - Include a testimonials section to showcase customer feedback and build trust
    """

    formatted_output = f"""
        **Project Type:** {project}

        **Project Objectives:** {project_objectives}

        **Industry:** {industry}

        **Team Members:** {team_members}
        **Project Requirements:**
        {project_requirements}
        """

    # project crew costs
    # TODO:
    # - NA. Fix later.  Seems some attributed are deprecated
    # e.g., crew.usage_metrics.completion_tokens
    # project_costs(crew)

    inputs = {
        "project_type": project,
        "project_objectives": project_objectives,
        "industry": industry,
        "team_members": team_members,
        "project_requirements": project_requirements,
    }

    result = crew.kickoff(inputs=inputs)
    # NOTE:
    # - result.pydantic.dict is deprecated
    print(result.pydantic.model_dump())

    # more inspection
    tasks = result.pydantic.model_dump()["tasks"]
    df_tasks = pd.DataFrame(tasks)

    # Display the DataFrame as an HTML table
    df_tasks.style.set_table_attributes('border="1"').set_caption(
        "Task Details"
    ).set_table_styles([{"selector": "th, td", "props": [("font-size", "120%")]}])

    tasks = result.pydantic.dict()["tasks"]
    df_tasks = pd.DataFrame(tasks)

    # Display the DataFrame as an HTML table
    df_tasks.style.set_table_attributes('border="1"').set_caption(
        "Task Details"
    ).set_table_styles([{"selector": "th, td", "props": [("font-size", "120%")]}])


if __name__ == "__main__":
    main()
