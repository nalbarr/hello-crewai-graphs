from crewai import Agent, Task, Crew, Process
from crewai_tools import ScrapeWebsiteTool, SerperDevTool
from langchain_openai import ChatOpenAI


def filter_warnings():
    import warnings

    warnings.filterwarnings("ignore")


def init():
    import os
    from utils import get_openai_api_key
    from utils import get_serper_api_key

    openai_api_key = get_openai_api_key()
    os.environ["OPENAI_MODEL_NAME"] = "gpt-3.5-turbo"
    os.environ["SERPER_API_KEY"] = get_serper_api_key()
    return openai_api_key


# agent 1
def create_data_analyst_agent(tools):
    data_analyst_agent = Agent(
        role="Data Analyst",
        goal="Monitor and analyze market data in real-time "
        "to identify trends and predict market movements.",
        backstory="Specializing in financial markets, this agent "
        "uses statistical modeling and machine learning "
        "to provide crucial insights. With a knack for data, "
        "the Data Analyst Agent is the cornerstone for "
        "informing trading decisions.",
        verbose=True,
        allow_delegation=True,
        tools=tools,
    )
    return data_analyst_agent


# agent 2
def create_trading_strategy_agent(tools):
    trading_strategy_agent = Agent(
        role="Trading Strategy Developer",
        goal="Develop and test various trading strategies based "
        "on insights from the Data Analyst Agent.",
        backstory="Equipped with a deep understanding of financial "
        "markets and quantitative analysis, this agent "
        "devises and refines trading strategies. It evaluates "
        "the performance of different approaches to determine "
        "the most profitable and risk-averse options.",
        verbose=True,
        allow_delegation=True,
        tools=tools,
    )
    return trading_strategy_agent


# agent 3
def create_execution_agent(tools):
    execution_agent = Agent(
        role="Trade Advisor",
        goal="Suggest optimal trade execution strategies "
        "based on approved trading strategies.",
        backstory="This agent specializes in analyzing the timing, price, "
        "and logistical details of potential trades. By evaluating "
        "these factors, it provides well-founded suggestions for "
        "when and how trades should be executed to maximize "
        "efficiency and adherence to strategy.",
        verbose=True,
        allow_delegation=True,
        tools=tools,
    )
    return execution_agent


# agent 4
def create_risk_management_agent(tools):
    risk_management_agent = Agent(
        role="Risk Advisor",
        goal="Evaluate and provide insights on the risks "
        "associated with potential trading activities.",
        backstory="Armed with a deep understanding of risk assessment models "
        "and market dynamics, this agent scrutinizes the potential "
        "risks of proposed trades. It offers a detailed analysis of "
        "risk exposure and suggests safeguards to ensure that "
        "trading activities align with the firm’s risk tolerance.",
        verbose=True,
        allow_delegation=True,
        tools=tools,
    )
    return risk_management_agent


# task 1
def create_data_analysis_task(data_analyst_agent):
    data_analysis_task = Task(
        description=(
            "Continuously monitor and analyze market data for "
            "the selected stock ({stock_selection}). "
            "Use statistical modeling and machine learning to "
            "identify trends and predict market movements."
        ),
        expected_output=(
            "Insights and alerts about significant market "
            "opportunities or threats for {stock_selection}."
        ),
        agent=data_analyst_agent,
    )
    return data_analysis_task


# task 2
def create_strategy_development_task(trading_strategy_agent):
    strategy_development_task = Task(
        description=(
            "Develop and refine trading strategies based on "
            "the insights from the Data Analyst and "
            "user-defined risk tolerance ({risk_tolerance}). "
            "Consider trading preferences ({trading_strategy_preference})."
        ),
        expected_output=(
            "A set of potential trading strategies for {stock_selection} "
            "that align with the user's risk tolerance."
        ),
        agent=trading_strategy_agent,
    )
    return strategy_development_task


# task 3
def create_execution_planning_task(execution_agent):
    execution_planning_task = Task(
        description=(
            "Analyze approved trading strategies to determine the "
            "best execution methods for {stock_selection}, "
            "considering current market conditions and optimal pricing."
        ),
        expected_output=(
            "Detailed execution plans suggesting how and when to "
            "execute trades for {stock_selection}."
        ),
        agent=execution_agent,
    )
    return execution_planning_task


# task 4
def create_risk_assessment_task(risk_management_agent):
    risk_assessment_task = Task(
        description=(
            "Evaluate the risks associated with the proposed trading "
            "strategies and execution plans for {stock_selection}. "
            "Provide a detailed analysis of potential risks "
            "and suggest mitigation strategies."
        ),
        expected_output=(
            "A comprehensive risk analysis report detailing potential "
            "risks and mitigation recommendations for {stock_selection}."
        ),
        agent=risk_management_agent,
    )
    return risk_assessment_task


def main():
    filter_warnings()
    init()

    # tools
    search_tool = SerperDevTool()
    scrape_tool = ScrapeWebsiteTool()

    tools = [scrape_tool, search_tool]

    # agents
    data_analyst_agent = create_data_analyst_agent(tools)
    trading_strategy_agent = create_trading_strategy_agent(tools)
    execution_agent = create_execution_agent(tools)
    risk_management_agent = create_risk_management_agent(tools)

    # tasks
    data_analysis_task = create_data_analysis_task(data_analyst_agent)
    strategy_development_task = create_strategy_development_task(trading_strategy_agent)
    execution_planning_task = create_execution_planning_task(execution_agent)
    risk_assessment_task = create_risk_assessment_task(risk_management_agent)

    # crew
    crew = Crew(
        agents=[
            data_analyst_agent,
            trading_strategy_agent,
            execution_agent,
            risk_management_agent,
        ],
        tasks=[
            data_analysis_task,
            strategy_development_task,
            execution_planning_task,
            risk_assessment_task,
        ],
        manager_llm=ChatOpenAI(model="gpt-3.5-turbo", temperature=0.7),
        process=Process.hierarchical,
        verbose=True,
    )

    financial_trading_inputs = {
        "stock_selection": "AAPL",
        "initial_capital": "100000",
        "risk_tolerance": "Medium",
        "trading_strategy_preference": "Day Trading",
        "news_impact_consideration": True,
    }

    ### this execution will take some time to run
    result = crew.kickoff(inputs=financial_trading_inputs)
    print(f"result: {result}")


if __name__ == "__main__":
    main()
