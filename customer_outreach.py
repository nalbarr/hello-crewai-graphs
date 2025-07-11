from crewai import Agent, Task, Crew
from crewai_tools import DirectoryReadTool
from crewai_tools import FileReadTool
from crewai_tools import SerperDevTool

# NOTE:
# - Below does not work
# from crewai_tools import BaseTool
from crewai.tools import BaseTool


def filter_warnings():
    import warnings

    warnings.filterwarnings("ignore")


def init():
    import os
    from utils import get_openai_api_key, get_serper_api_key, register_phoenix_otel

    get_openai_api_key()
    os.environ["OPENAI_MODEL_NAME"] = "gpt-3.5-turbo"
    os.environ["SERPER_API_KEY"] = get_serper_api_key()

    register_phoenix_otel(
        project_name="default",
        endpoint="http://localhost:6006/v1/traces",
    )


def create_support_agent():
    support_agent = Agent(
        role="Senior Support Representative",
        goal="Be the most friendly and helpful support representative in your team",
        backstory=(
            "You work at crewAI (https://crewai.com) and "
            " are now working on providing "
            "support to {customer}, a super important customer "
            " for your company."
            "You need to make sure that you provide the best support!"
            "Make sure to provide full complete answers, "
            " and make no assumptions."
        ),
        allow_delegation=False,
        verbose=True,
    )
    return support_agent


def create_sales_rep_agent():
    sales_rep_agent = Agent(
        role="Sales Representative",
        goal="Identify high-value leads that match our ideal customer profile",
        backstory=(
            "As a part of the dynamic sales team at CrewAI, "
            "your mission is to scour "
            "the digital landscape for potential leads. "
            "Armed with cutting-edge tools "
            "and a strategic mindset, you analyze data, "
            "trends, and interactions to "
            "unearth opportunities that others might overlook. "
            "Your work is crucial in paving the way "
            "for meaningful engagements and driving the company's growth."
        ),
        allow_delegation=False,
        verbose=True,
    )
    return sales_rep_agent


def create_lead_sales_rep_agent():
    lead_sales_rep_agent = Agent(
        role="Lead Sales Representative",
        goal="Nurture leads with personalized, compelling communications",
        backstory=(
            "Within the vibrant ecosystem of CrewAI's sales department, "
            "you stand out as the bridge between potential clients "
            "and the solutions they need."
            "By creating engaging, personalized messages, "
            "you not only inform leads about our offerings "
            "but also make them feel seen and heard."
            "Your role is pivotal in converting interest "
            "into action, guiding leads through the journey "
            "from curiosity to commitment."
        ),
        allow_delegation=False,
        verbose=True,
    )
    return lead_sales_rep_agent


def create_directoryread_tool():
    directory_read_tool = DirectoryReadTool(directory="./instructions")
    return directory_read_tool


def create_fileread_tool():
    return FileReadTool()


def create_serperdev_tool():
    return SerperDevTool()


class SentimentAnalysisTool(BaseTool):
    name: str = "Sentiment Analysis Tool"
    description: str = (
        "Analyzes the sentiment of test to ensure positive and engaging communication."
    )

    def _run(self, test: str) -> str:
        return "positive"


def create_sentiment_analysis_tool():
    return SentimentAnalysisTool()


def create_lead_profiling(tools, sales_rep_agent):
    lead_profiling_task = Task(
        description=(
            "Conduct an in-depth analysis of {lead_name}, "
            "a company in the {industry} sector "
            "that recently showed interest in our solutions. "
            "Utilize all available data sources "
            "to compile a detailed profile, "
            "focusing on key decision-makers, recent business "
            "developments, and potential needs "
            "that align with our offerings. "
            "This task is crucial for tailoring "
            "our engagement strategy effectively.\n"
            "Don't make assumptions and "
            "only use information you absolutely sure about."
        ),
        expected_output=(
            "A comprehensive report on {lead_name}, "
            "including company background, "
            "key personnel, recent milestones, and identified needs. "
            "Highlight potential areas where "
            "our solutions can provide value, "
            "and suggest personalized engagement strategies."
        ),
        tools=tools,
        agent=sales_rep_agent,
    )
    return lead_profiling_task


def create_personalized_outreach(other_tools, lead_sales_rep_agent):
    personalized_outreach_task = Task(
        description=(
            "Using the insights gathered from "
            "the lead profiling report on {lead_name}, "
            "craft a personalized outreach campaign "
            "aimed at {key_decision_maker}, "
            "the {position} of {lead_name}. "
            "The campaign should address their recent {milestone} "
            "and how our solutions can support their goals. "
            "Your communication must resonate "
            "with {lead_name}'s company culture and values, "
            "demonstrating a deep understanding of "
            "their business and needs.\n"
            "Don't make assumptions and only "
            "use information you absolutely sure about."
        ),
        expected_output=(
            "A series of personalized email drafts "
            "tailored to {lead_name}, "
            "specifically targeting {key_decision_maker}."
            "Each draft should include "
            "a compelling narrative that connects our solutions "
            "with their recent achievements and future goals. "
            "Ensure the tone is engaging, professional, "
            "and aligned with {lead_name}'s corporate identity."
        ),
        tools=other_tools,
        agent=lead_sales_rep_agent,
    )
    return personalized_outreach_task


def main():
    filter_warnings()
    init()

    # agents
    sales_rep_agent = create_sales_rep_agent()
    lead_sales_rep_agent = create_lead_sales_rep_agent()

    # tools
    directory_read_tool = create_directoryread_tool()
    file_read_tool = create_fileread_tool()
    search_tool = create_serperdev_tool()
    sentiment_analysis_tool = SentimentAnalysisTool()

    # tasks
    tools = [directory_read_tool, file_read_tool, search_tool]
    lead_profiling_task = create_lead_profiling(tools, sales_rep_agent)

    other_tools = [sentiment_analysis_tool, search_tool]
    personalized_outreach_task = create_personalized_outreach(
        other_tools, lead_sales_rep_agent
    )

    # crew
    crew = Crew(
        agents=[sales_rep_agent, lead_sales_rep_agent],
        tasks=[lead_profiling_task, personalized_outreach_task],
        verbose=True,
    )

    inputs = {
        "lead_name": "DeepLearningAI",
        "industry": "Online Learning Platform",
        "key_decision_maker": "Andrew Ng",
        "position": "CEO",
        "milestone": "product launch",
    }
    result = crew.kickoff(inputs=inputs)
    print(f"result: {result}")


if __name__ == "__main__":
    main()
