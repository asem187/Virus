from dataclasses import dataclass

import pytest

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

try:
    from agent import SimpleAgent
except ModuleNotFoundError:
    import pytest
    pytest.skip("LangChain not available", allow_module_level=True)


@dataclass
class Message:
    content: str


class SystemMessage(Message):
    pass


class HumanMessage(Message):
    pass


class AIMessage(Message):
    pass


class SimpleMemory:
    def __init__(self):
        self.chat_memory = self
        self.messages = []

    def add_user_message(self, text: str):
        self.messages.append(HumanMessage(text))

    def add_ai_message(self, text: str):
        self.messages.append(AIMessage(text))


class DummyChat:
    def __init__(self, reply):
        self.reply = reply
    def __call__(self, messages):
        return AIMessage(content=self.reply)

def test_agent_respond_appends_memory_and_prompt_truncates():
    mem = SimpleMemory()
    chat = DummyChat('response')
    agent = SimpleAgent(
        name='Agent',
        chat=chat,
        memory=mem,
        system_prompt='x' * 1995
    )
    answer = agent.respond('hello')
    assert answer == 'response'
    msgs = mem.chat_memory.messages
    assert isinstance(msgs[-2], HumanMessage) and msgs[-2].content == 'hello'
    assert isinstance(msgs[-1], AIMessage) and msgs[-1].content == 'response'
    assert len(agent.system_prompt) <= 2000


def test_search_web(monkeypatch):
    from tools import search_web

    def fake_get(url, params, timeout):
        class R:
            def raise_for_status(self):
                pass

            def json(self):
                return {"results": [{"content": "answer"}]}

        return R()

    monkeypatch.setenv("TAVILY_API_KEY", "x")
    monkeypatch.setattr("tools.requests.get", fake_get)
    result = search_web("test")
    assert "answer" in result


def test_pull_from_github(monkeypatch, tmp_path):
    from tools import pull_from_github

    def fake_call(cmd):
        (tmp_path / "repo").mkdir()

    monkeypatch.setattr("tools.subprocess.check_call", lambda cmd: fake_call(cmd))
    path = pull_from_github("https://example.com/repo.git", dest=str(tmp_path))
    assert (tmp_path / "repo").exists()
