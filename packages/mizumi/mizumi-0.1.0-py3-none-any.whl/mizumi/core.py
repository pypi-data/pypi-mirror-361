# Copyright 2025 Fedwin Chatelier
# Licensed under the Apache License, Version 2.0 (the "License");
# You may not use this file except in compliance with the License.
# http://www.apache.org/licenses/LICENSE-2.0




import json
import openai
from typing import Type
from pydantic import BaseModel, ValidationError
from tenacity import retry, stop_after_attempt, wait_fixed
from .exceptions import LLMOutputError


class Mizumi:
    def __init__(self, model: str = "gpt-4", api_key: str = None):
        openai.api_key = api_key
        self.model = model
        self.prefix = "Respond ONLY with valid JSON matching the given schema."

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
    def ask(self, prompt: str, schema: Type[BaseModel]) -> BaseModel:
        example_schema = schema.model_json_schema()
        messages = [
            {"role": "system", "content": f"{self.prefix}\nSchema:\n{example_schema}"},
            {"role": "user", "content": prompt}
        ]

        response = openai.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0
        )
        print('Response:', response)
        raw = response.choices[0].message.content
        try:
            data = json.loads(raw)
            return schema.parse_obj(data)
        except (json.JSONDecodeError, ValidationError) as e:
            raise LLMOutputError(f"Failed to parse LLM output: {e}\n\nRaw Output:\n{raw}")
