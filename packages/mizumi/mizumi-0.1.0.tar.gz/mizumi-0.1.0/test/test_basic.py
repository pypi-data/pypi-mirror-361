import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))


from mizumi.core import Mizumi
from pydantic import BaseModel
from dotenv import load_dotenv
import os

load_dotenv()


class Article(BaseModel):
    author: str
    date: str
    summary: str


def test_mizumi_valid_output():
    api_key = os.getenv("OPENAI_API_KEY")
    model = 'gpt-4o-mini'
    mizumi = Mizumi(api_key=api_key, model=model)
    result = mizumi.ask(
        "Summarize this: 'John Doe wrote an AI article on July 10th.'",
        schema=Article
    )
    print('Output result:', result)
    assert isinstance(result, Article)
    # print(result.json(indent=2))
