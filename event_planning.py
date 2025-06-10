import crewai
import crewai_tools
import langchain_community

from crewai import Agent, Task, Crew
from crewai_tools import ScrapeWebsiteTool, SerperDevTool


def filter_warnings():
    import warnings

    warnings.filterwarnings("ignore")


def init():
    import os
    from utils import get_openai_api_key, pretty_print_result
    from utils import get_serper_api_key

    openai_api_key = get_openai_api_key()
    os.environ["OPENAI_MODEL_NAME"] = "gpt-3.5-turbo"
    os.environ["SERPER_API_KEY"] = get_serper_api_key()
    return openai_api_key


def create_venue_coordinator_agent(tools):
    venue_coordinator = Agent(
        role="Venue Coordinator",
        goal="Identify and book an appropriate venue " "based on event requirements",
        tools=tools,
        verbose=True,
        backstory=(
            "With a keen sense of space and "
            "understanding of event logistics, "
            "you excel at finding and securing "
            "the perfect venue that fits the event's theme, "
            "size, and budget constraints."
        ),
    )
    return venue_coordinator


def create_logistics_manager_agent(tools):
    logistics_manager = Agent(
        role="Logistics Manager",
        goal=("Manage all logistics for the event " "including catering and equipmen"),
        tools=tools,
        verbose=True,
        backstory=(
            "Organized and detail-oriented, "
            "you ensure that every logistical aspect of the event "
            "from catering to equipment setup "
            "is flawlessly executed to create a seamless experience."
        ),
    )
    return logistics_manager


def create_marketing_communications_agent(tools):
    marketing_communications_agent = Agent(
        role="Marketing and Communications Agent",
        goal="Effectively market the event and " "communicate with participants",
        tools=tools,
        verbose=True,
        backstory=(
            "Creative and communicative, "
            "you craft compelling messages and "
            "engage with potential attendees "
            "to maximize event exposure and participation."
        ),
    )
    return marketing_communications_agent


from pydantic import BaseModel


class VenueDetails(BaseModel):
    name: str
    address: str
    capacity: int
    booking_status: str


def create_venue_task(venue_coordinator):
    venue_task = Task(
        description="Find a venue in {event_city} "
        "that meets criteria for {event_topic}.",
        expected_output="All the details of a specifically chosen"
        "venue you found to accommodate the event.",
        human_input=True,
        output_json=VenueDetails,
        output_file="venue_details.json",
        agent=venue_coordinator,
    )
    return venue_task


def create_logisitics_task(logistics_manager):
    logistics_task = Task(
        description="Coordinate catering and "
        "equipment for an event "
        "with {expected_participants} participants "
        "on {tentative_date}.",
        expected_output="Confirmation of all logistics arrangements "
        "including catering and equipment setup.",
        human_input=True,
        async_execution=True,
        agent=logistics_manager,
    )
    return logistics_task


def create_marketing_task(marketing_communications_agent):
    marketing_task = Task(
        description="Promote the {event_topic} "
        "aiming to engage at least"
        "{expected_participants} potential attendees.",
        expected_output="Report on marketing activities "
        "and attendee engagement formatted as markdown.",
        async_execution=True,
        output_file="marketing_report.md",  # Outputs the report as a text file
        agent=marketing_communications_agent,
    )
    return marketing_task


def dump_venue_details():
    import json
    from pprint import pprint

    with open("venue_details.json") as f:
        data = json.load(f)

    pprint(data)


def main():
    filter_warnings()
    init()

    # tools
    from crewai_tools import ScrapeWebsiteTool, SerperDevTool

    search_tool = SerperDevTool()
    scrape_tool = ScrapeWebsiteTool()

    # agents
    tools = [search_tool, scrape_tool]
    venue_coordinator = create_venue_coordinator_agent(tools)
    logistics_manager = create_logistics_manager_agent(tools)
    marketing_communications_agent = create_marketing_communications_agent(tools)

    # tasks
    venue_task = create_venue_task(venue_coordinator)
    logistics_task = create_logisitics_task(logistics_manager)
    marketing_task = create_marketing_task(marketing_communications_agent)

    # crew

    # NOTE:
    # - Below does not work as there can be only a maximum of one async tasks at the end of list
    # crew = Crew(
    #     agents=[venue_coordinator,
    #             logistics_manager,
    #             marketing_communications_agent],
    #     tasks=[venue_task,
    #         logistics_task,
    #         marketing_task],

    #     verbose=True
    # )
    crew = Crew(
        agents=[venue_coordinator, logistics_manager, marketing_communications_agent],
        tasks=[logistics_task, marketing_task, venue_task],
        verbose=True,
    )

    event_details = {
        "event_topic": "Tech Innovation Conference",
        "event_description": "A gathering of tech innovators "
        "and industry leaders "
        "to explore future technologies.",
        "event_city": "San Francisco",
        "tentative_date": "2024-09-15",
        "expected_participants": 500,
        "budget": 20000,
        "venue_type": "Conference Hall",
    }
    result = crew.kickoff(inputs=event_details)


if __name__ == "__main__":
    main()
