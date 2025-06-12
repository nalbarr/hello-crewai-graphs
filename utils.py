import os
from dotenv import load_dotenv, find_dotenv


def load_env():
    _ = load_dotenv(find_dotenv())


def get_openai_api_key():
    load_env()
    openai_api_key = os.getenv("OPENAI_API_KEY")
    return openai_api_key


def get_serper_api_key():
    load_env()
    openai_api_key = os.getenv("SERPER_API_KEY")
    return openai_api_key


# break line every 80 characters
def pretty_print_result(result):
    parsed_result = []
    for line in result.split("\n"):
        if len(line) > 80:
            words = line.split(" ")
            new_line = ""
            for word in words:
                if len(new_line) + len(word) + 1 > 80:
                    parsed_result.append(new_line)
                    new_line = word
                else:
                    if new_line == "":
                        new_line = word
                    else:
                        new_line += " " + word
            parsed_result.append(new_line)
        else:
            parsed_result.append(line)
    return "\n".join(parsed_result)


# https://community.deeplearning.ai/t/track-token-usage/633154/2
def calculate_costs(
    crew_usage_metrics, model_input_price, model_output_price, unit_of_tokens
):
    """
    Calculate the costs based on crew usage metrics and token pricing.

    Parameters:
    crew_usage_metrics (dict): A dictionary containing the usage metrics with the keys:
        - 'total_tokens': Total number of tokens used.
        - 'prompt_tokens': Number of tokens used for input prompts.
        - 'completion_tokens': Number of tokens used for completions.
        - 'successful_requests': Number of successful requests made.
    model_input_price (float): Cost per unit of input tokens.
    model_output_price (float): Cost per unit of output tokens.
    unit_of_tokens (int): The number of tokens per unit cost (e.g., per 1000 tokens).

    Returns:
    dict: A dictionary with the calculated costs:
        - 'total_cost': Total cost of the usage.
        - 'input_cost': Cost of the input tokens.
        - 'output_cost': Cost of the output tokens.
    """

    prompt_tokens = crew_usage_metrics.get("prompt_tokens")
    completion_tokens = crew_usage_metrics.get("completion_tokens")

    input_cost = (prompt_tokens / unit_of_tokens) * model_input_price
    output_cost = (completion_tokens / unit_of_tokens) * model_output_price
    total_cost = input_cost + output_cost

    return {
        "total_cost": total_cost,
        "input_cost": input_cost,
        "output_cost": output_cost,
    }


def get_usage_metrics(context):
    import pandas as pd

    df_usage_metrics = pd.DataFrame([context[0].token_usage.dict()])

    costs = 0.150 * df_usage_metrics["total_tokens"].sum() / 1_000_000
    print(f"Total costs: ${costs:.4f}")


def register_phoenix_otel(project_name, endpoint):
    from opentelemetry import trace as trace_api
    from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
    from opentelemetry.sdk import trace as trace_sdk
    from opentelemetry.sdk.trace.export import SimpleSpanProcessor

    tracer_provider = trace_sdk.TracerProvider()
    span_exporter = OTLPSpanExporter("http://localhost:6006/v1/traces")
    span_processor = SimpleSpanProcessor(span_exporter)
    tracer_provider.add_span_processor(span_processor)
    trace_api.set_tracer_provider(tracer_provider)

    from openinference.instrumentation.crewai import CrewAIInstrumentor

    CrewAIInstrumentor().instrument(
        skip_dep_check=True, tracer_provider=tracer_provider
    )
