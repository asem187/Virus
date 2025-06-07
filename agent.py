"""Multi-agent evolving chat assistant example.

This script demonstrates a command-line chat program that coordinates multiple
OpenAI powered agents.  Each agent keeps its own memory of the conversation and
contributes a response in turn.  New agents can be added at runtime with the
command ``add agent`` to illustrate how the system can grow.

LangChain is used to provide a simple memory buffer for each agent.

Requirements:
    - openai
    - langchain

Set the ``OPENAI_API_KEY`` environment variable before running.
"""

import os
import argparse
from dataclasses import dataclass

from typing import Callable

from storage import storage

import tools

from langchain.memory import ConversationBufferMemory
from langchain.chat_models import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler

try:  # optional voice support
    import voice
except Exception:  # pragma: no cover - voice is optional
    voice = None


@dataclass
class SimpleAgent:
    """Represents a single conversational agent."""

    name: str
    chat: ChatOpenAI
    memory: ConversationBufferMemory
    system_prompt: str

    def respond(self, prompt: str) -> str:
        """Generate a response to ``prompt`` using the agent's memory."""
        messages = [SystemMessage(content=self.system_prompt)]
        for msg in self.memory.chat_memory.messages:
            messages.append(msg)
        messages.append(HumanMessage(content=prompt))
        resp = self.chat(messages)
        answer = resp.content
        self.memory.chat_memory.add_user_message(prompt)
        self.memory.chat_memory.add_ai_message(answer)
        # evolve prompt with simple summary of last answer
        summary = f"Previously you said: {answer}"
        self.system_prompt += "\n" + summary
        if len(self.system_prompt) > 2000:
            self.system_prompt = self.system_prompt[-2000:]
        return answer


def main() -> None:
    parser = argparse.ArgumentParser(description="Multi-agent chat")
    parser.add_argument("--model", default="gpt-3.5-turbo", help="OpenAI model name")
    parser.add_argument("--temperature", type=float, default=0.7, help="Sampling temperature")
    parser.add_argument("--agents", type=int, default=2, help="Initial number of agents")
    parser.add_argument("--voice", action="store_true", help="Enable voice input/output")
    parser.add_argument("--stream", action="store_true", help="Stream responses in real time")
    args = parser.parse_args()

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY environment variable is required")

    def new_agent(n: int) -> SimpleAgent:
        return SimpleAgent(
            name=f"Agent{n}",
            chat=ChatOpenAI(
                openai_api_key=api_key,
                model_name=args.model,
                temperature=args.temperature,
                streaming=args.stream,
                callbacks=[StreamingStdOutCallbackHandler()] if args.stream else None,
            ),
            memory=ConversationBufferMemory(),
            system_prompt=f"You are Agent{n}, a helpful assistant.",
        )

    agents = [new_agent(i + 1) for i in range(args.agents)]

    print("Type 'add agent' to create a new agent. Type 'quit' to exit.")
    while True:
        if args.voice and voice:
            try:
                user_input = voice.record_and_transcribe()
            except Exception as exc:
                print(f"[Voice error] {exc}")
                continue
        else:
            user_input = input("User: ")
        if user_input.lower() in {"quit", "exit"}:
            break

        if user_input.startswith("search "):
            query = user_input[len("search "):]
            try:
                result = tools.search_web(query)
            except Exception as exc:
                print(f"[Search error] {exc}")
                continue
            print(result)
            continue

        if user_input.startswith("clone "):
            repo = user_input[len("clone "):]
            try:
                path = tools.pull_from_github(repo)
            except Exception as exc:
                print(f"[Git error] {exc}")
                continue
            print(f"Cloned to {path}")
            continue

        if user_input.lower() == "add agent":
            idx = len(agents) + 1
            agents.append(new_agent(idx))
            print(f"[System] Added Agent{idx}")
            continue

        if storage:
            storage.save("user", "user", user_input)
        prompt = user_input
        for agent in agents:
            answer = agent.respond(prompt)
            if not args.stream:
                print(f"{agent.name}: {answer}")
            if args.voice and voice:
                voice.speak(answer)
            if args.stream:
                print()  # newline after streaming tokens
                print(f"[{agent.name} done]")
            if storage:
                storage.save(agent.name, "assistant", answer)
            prompt = answer  # pass along to the next agent


if __name__ == "__main__":
    main()
