"""Simple evolving chat using OpenAI's Assistants API.

This script demonstrates how to use the OpenAI Assistants API to create a
self‑updating assistant that evolves based on the conversation.
"""
import os
import time
from dataclasses import dataclass
from typing import Optional

from openai import OpenAI


@dataclass
class AssistantAgent:
    client: OpenAI
    assistant_id: str
    thread_id: str
    instructions: str

    def respond(self, user_message: str) -> str:
        self.client.beta.threads.messages.create(
            thread_id=self.thread_id,
            role="user",
            content=user_message,
        )
        run = self.client.beta.threads.runs.create(
            thread_id=self.thread_id,
            assistant_id=self.assistant_id,
            instructions=self.instructions,
        )
        while True:
            run = self.client.beta.threads.runs.retrieve(
                thread_id=self.thread_id, run_id=run.id
            )
            if run.status in {"completed", "failed"}:
                break
            time.sleep(0.5)
        messages = self.client.beta.threads.messages.list(thread_id=self.thread_id)
        for msg in reversed(messages.data):
            if msg.role == "assistant":
                answer = msg.content[0].text.value
                break
        else:
            answer = ""
        self.instructions += f"\nPreviously you said: {answer}"
        if len(self.instructions) > 2000:
            self.instructions = self.instructions[-2000:]
        return answer


def main() -> None:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY environment variable is required")
    client = OpenAI(api_key=api_key)
    assistant = client.beta.assistants.create(
        name="EvolvingAssistant",
        model="gpt-4-turbo-preview",
        instructions="You are a helpful assistant.",
    )
    thread = client.beta.threads.create()

    agent = AssistantAgent(
        client=client,
        assistant_id=assistant.id,
        thread_id=thread.id,
        instructions="You are a helpful assistant.",
    )

    print("Type 'quit' to exit.")
    while True:
        user_input = input("User: ")
        if user_input.lower() in {"quit", "exit"}:
            break
        answer = agent.respond(user_input)
        print(f"Assistant: {answer}")


if __name__ == "__main__":
    main()
