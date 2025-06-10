from crewai import Agent, Task, Crew
from crewai_tools import (
    FileReadTool,
    ScrapeWebsiteTool,
    MDXSearchTool,
    SerperDevTool,
)


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
def create_researcher_agent(research_tools):
    researcher = Agent(
        role="Tech Job Researcher",
        goal="Make sure to do amazing analysis on job posting to help job applicants",
        tools=research_tools,
        verbose=True,
        backstory=(
            "As a Job Researcher, your prowess in "
            "navigating and extracting critical "
            "information from job postings is unmatched."
            "Your skills help pinpoint the necessary "
            "qualifications and skills sought "
            "by employers, forming the foundation for "
            "effective application tailoring."
        ),
    )
    return researcher


# agent 2
def create_profiler_agent(profile_tools):
    profiler = Agent(
        role="Personal Profiler for Engineers",
        goal="Do increditble research on job applicants "
        "to help them stand out in the job market",
        tools=profile_tools,
        verbose=True,
        backstory=(
            "Equipped with analytical prowess, you dissect "
            "and synthesize information "
            "from diverse sources to craft comprehensive "
            "personal and professional profiles, laying the "
            "groundwork for personalized resume enhancements."
        ),
    )
    return profiler


# agent 3
def create_strategy_agent(strategy_tools):
    strategy_agent = Agent(
        role="Resume Strategist for Engineers",
        goal="Find all the best ways to make a resume stand out in the job market.",
        tools=strategy_tools,
        verbose=True,
        backstory=(
            "With a strategic mind and an eye for detail, you "
            "excel at refining resumes to highlight the most "
            "relevant skills and experiences, ensuring they "
            "resonate perfectly with the job's requirements."
        ),
    )
    return strategy_agent


# agent 4
def create_interview_preparation_agent(all_tools):
    interview_preparer = Agent(
        role="Engineering Interview Preparer",
        goal="Create interview questions and talking points "
        "based on the resume and job requirements",
        tools=all_tools,
        verbose=True,
        backstory=(
            "Your role is crucial in anticipating the dynamics of "
            "interviews. With your ability to formulate key questions "
            "and talking points, you prepare candidates for success, "
            "ensuring they can confidently address all aspects of the "
            "job they are applying for."
        ),
    )
    return interview_preparer


# task 1
def create_research_task(researcher):
    research_task = Task(
        description=(
            "Analyze the job posting URL provided ({job_posting_url}) "
            "to extract key skills, experiences, and qualifications "
            "required. Use the tools to gather content and identify "
            "and categorize the requirements."
        ),
        expected_output=(
            "A structured list of job requirements, including necessary "
            "skills, qualifications, and experiences."
        ),
        agent=researcher,
        async_execution=True,
    )
    return research_task


# task 2
def create_profile_task(profiler):
    profile_task = Task(
        description=(
            "Compile a detailed personal and professional profile "
            "using the GitHub ({github_url}) URLs, and personal write-up "
            "({personal_writeup}). Utilize tools to extract and "
            "synthesize information from these sources."
        ),
        expected_output=(
            "A comprehensive profile document that includes skills, "
            "project experiences, contributions, interests, and "
            "communication style."
        ),
        agent=profiler,
        async_execution=True,
    )
    return profile_task


# tasks 3
def create_resume_strategy_task(resume_strategy_context, resume_strategist):
    resume_strategy_task = Task(
        description=(
            "Using the profile and job requirements obtained from "
            "previous tasks, tailor the resume to highlight the most "
            "relevant areas. Employ tools to adjust and enhance the "
            "resume content. Make sure this is the best resume even but "
            "don't make up any information. Update every section, "
            "inlcuding the initial summary, work experience, skills, "
            "and education. All to better reflrect the candidates "
            "abilities and how it matches the job posting."
        ),
        expected_output=(
            "An updated resume that effectively highlights the candidate's "
            "qualifications and experiences relevant to the job."
        ),
        output_file="tailored_resume.md",
        context=resume_strategy_context,
        agent=resume_strategist,
    )
    return resume_strategy_task


def create_interview_preperation_task(interview_prep_context, interview_preparer):
    interview_preparation_task = Task(
        description=(
            "Create a set of potential interview questions and talking "
            "points based on the tailored resume and job requirements. "
            "Utilize tools to generate relevant questions and discussion "
            "points. Make sure to use these question and talking points to "
            "help the candiadte highlight the main points of the resume "
            "and how it matches the job posting."
        ),
        expected_output=(
            "A document containing key questions and talking points "
            "that the candidate should prepare for the initial interview."
        ),
        output_file="interview_materials.md",
        context=interview_prep_context,
        agent=interview_preparer,
    )
    return interview_preparation_task


def main():
    filter_warnings()
    init()

    # tools
    search_tool = SerperDevTool()
    scrape_tool = ScrapeWebsiteTool()
    read_resume = FileReadTool(file_path="./fake_resume.md")
    semantic_search_resume = MDXSearchTool(mdx="./fake_resume.md")

    # agents
    research_tools = [search_tool, scrape_tool]
    profile_tools = [scrape_tool, search_tool, read_resume, semantic_search_resume]
    all_tools = [scrape_tool, search_tool, read_resume, semantic_search_resume]

    researcher = create_researcher_agent(research_tools)
    profiler = create_profiler_agent(profile_tools)
    strategy_agent = create_strategy_agent(all_tools)
    interview_preparer = create_interview_preparation_agent(all_tools)

    research_task = create_research_task(researcher)
    profile_task = create_profile_task(profiler)

    resume_strategy_context = [research_task, profile_task]
    resume_strategy_task = create_resume_strategy_task(
        resume_strategy_context, strategy_agent
    )

    interview_prep_context = [research_task, profile_task, resume_strategy_task]
    interview_preparer_task = create_interview_preperation_task(
        interview_prep_context, interview_preparer
    )

    crew = Crew(
        agents=[researcher, profiler, strategy_agent, interview_preparer],
        tasks=[
            research_task,
            profile_task,
            resume_strategy_task,
            interview_preparer_task,
        ],
        verbose=True,
    )

    job_application_inputs = {
        "job_posting_url": "https://jobs.lever.co/AIFund/6c82e23e-d954-4dd8-a734-c0c2c5ee00f1?lever-origin=applied&lever-source%5B%5D=AI+Fund",
        "github_url": "https://github.com/joaomdmoura",
        "personal_writeup": """Noah is an accomplished Software
        Engineering Leader with 18 years of experience, specializing in
        managing remote and in-office teams, and expert in multiple
        programming languages and frameworks. He holds an MBA and a strong
        background in AI and data science. Noah has successfully led
        major tech initiatives and startups, proving his ability to drive
        innovation and growth in the tech industry. Ideal for leadership
        roles that require a strategic and innovative approach.""",
    }

    result = crew.kickoff(inputs=job_application_inputs)
    print(f"result: {result}")


if __name__ == "__main__":
    main()
