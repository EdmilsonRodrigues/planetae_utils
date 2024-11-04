from time import sleep
from openai import APIConnectionError, OpenAI


class OpenAIService:
    api_key: str
    client: OpenAI
    model: str

    def __init__(self, api_key: str, model: str):
        self.api_key = api_key
        self.client = OpenAI(
            api_key=self.api_key,
        )
        self.model = model

    def get_chat_response(
        self,
        messages: list,
    ) -> str | None:
        try:
            chat_completion = self.client.chat.completions.create(
                messages=messages, model=self.model, max_tokens=10000
            )
        except APIConnectionError as e:
            print(f"Connection error: {e}")
            sleep(5)  # Wait for 5 seconds before retrying
            return self.get_chat_response(messages)

        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            raise

        content = chat_completion.choices[0].message.content

        if content:
            return content.strip()

    def ask_question(
        self,
        initialization_prompt: str,
        question: str,
    ) -> str | None:
        messages = [
            {
                "role": "system",
                "content": initialization_prompt,
            },
            {
                "role": "user",
                "content": question,
            },
        ]
        return self.get_chat_response(messages)
