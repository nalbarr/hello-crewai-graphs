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
