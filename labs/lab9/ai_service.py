import os
from pathlib import Path

from dotenv import load_dotenv
from openai import APIConnectionError, APIStatusError, OpenAI
from pydantic import BaseModel, Field

load_dotenv(Path(__file__).resolve().parent / ".env")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None


class ProjectDetails(BaseModel):
    title: str = Field(min_length=1, max_length=120)
    summary: str = Field(min_length=1)
    technologies: list[str] = Field(min_length=1)


class ProjectExtractionRefused(Exception):
    pass


class ProjectExtractionUnavailable(Exception):
    pass


def extract_project_details(notes: str) -> ProjectDetails:
    if client is None:
        raise ProjectExtractionUnavailable("The AI provider is not configured.")

    try:
        completion = client.chat.completions.parse(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Turn the project notes into a concise project title, a "
                        "summary of one or two sentences, and a list of technologies. "
                        "Only include technologies supported by the notes."
                    ),
                },
                {"role": "user", "content": notes},
            ],
            response_format=ProjectDetails,
            temperature=0.1,
        )
    except (APIConnectionError, APIStatusError) as error:
        raise ProjectExtractionUnavailable("The AI provider is unavailable.") from error

    message = completion.choices[0].message
    if message.refusal:
        raise ProjectExtractionRefused("The AI provider refused this request.")
    if message.parsed is None:
        raise ProjectExtractionUnavailable("The AI provider returned no project details.")

    return message.parsed
