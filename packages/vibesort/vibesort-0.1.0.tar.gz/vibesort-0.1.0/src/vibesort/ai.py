import os
from typing_extensions import Literal
import openai
from pydantic import BaseModel
from typing import TypeVar


class VibesortResponse(BaseModel):
    sorted_array: list[int]


class VibesortRequest(BaseModel):
    array: list[int]
    order: Literal["asc", "desc"] = "asc"


def vibesort(array: list[int]) -> VibesortResponse:
    return structured_output(
        content=VibesortRequest(array=array).model_dump_json(),
        response_format=VibesortResponse,
    ).sorted_array


T = TypeVar("T", bound=BaseModel)


def structured_output(
    content: str,
    response_format: T,
    model: str = "gpt-4.1-mini",
) -> T:
    api_key = os.environ["OPENAI_API_KEY"]
    client = openai.OpenAI(api_key=api_key)

    response = client.beta.chat.completions.parse(
        model=model,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": content,
                    },
                ],
            }
        ],
        response_format=response_format,
    )
    response_model = response.choices[0].message.parsed
    return response_model
