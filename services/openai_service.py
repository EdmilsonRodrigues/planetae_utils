from time import sleep
import openai


class OpenAIService:
    api_key: str
    client: openai.AsyncOpenAI
    model: str = "gpt-4o-2024-08-06"

    def __init__(self, api_key: str, model: str = "gpt-4o-2024-08-06"):
        self.api_key = api_key
        self.client = openai.AsyncOpenAI(
            api_key=self.api_key,
        )
        self.model = model

    async def get_chat_response(
        self,
        messages: list,
    ) -> str | None:
        try:
            chat_completion = await self.client.chat.completions.create(
                messages=messages, model=self.model, max_tokens=10000
            )
        except openai.APIConnectionError as e:
            print(f"Connection error: {e}")
            sleep(5)  # Wait for 5 seconds before retrying
            return await self.get_chat_response(messages)

        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            raise

        content = chat_completion.choices[0].message.content

        if content:
            return content.strip()

    async def ask_question(
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
        return await self.get_chat_response(messages)
