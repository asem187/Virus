import os
import tkinter as tk
from tkinter.scrolledtext import ScrolledText

from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.callbacks.base import BaseCallbackHandler

from agent import SimpleAgent
from storage import storage

try:  # optional voice support
    import voice
except Exception:  # pragma: no cover - voice is optional
    voice = None


class TextBoxStreamingHandler(BaseCallbackHandler):
    """Stream LLM tokens directly into a Tkinter text widget."""

    def __init__(self, text: ScrolledText) -> None:
        self.text = text

    def on_llm_new_token(self, token: str, **kwargs) -> None:  # type: ignore[override]
        self.text.configure(state="normal")
        self.text.insert(tk.END, token)
        self.text.configure(state="disabled")
        self.text.yview(tk.END)


class ChatGUI:
    """Tkinter-based interface for the multi-agent chat system."""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Multi-Agent Chat")

        self.text = ScrolledText(root, state="disabled", width=80, height=20)
        self.text.pack(padx=10, pady=10)

        self.entry = tk.Entry(root, width=80)
        self.entry.pack(padx=10, pady=5)
        self.entry.bind("<Return>", self.send_message)

        button_frame = tk.Frame(root)
        button_frame.pack(pady=5)

        self.send_btn = tk.Button(button_frame, text="Send", command=self.send_message)
        self.send_btn.pack(side="left", padx=5)

        self.add_btn = tk.Button(button_frame, text="Add Agent", command=self.add_agent)
        self.add_btn.pack(side="left", padx=5)

        self.voice_var = tk.BooleanVar(value=False)
        self.stream_var = tk.BooleanVar(value=False)
        self.voice_chk = tk.Checkbutton(button_frame, text="Voice", variable=self.voice_var)
        self.voice_chk.pack(side="left", padx=5)
        if voice is None:
            self.voice_chk.configure(state="disabled")
        self.stream_chk = tk.Checkbutton(button_frame, text="Stream", variable=self.stream_var)
        self.stream_chk.pack(side="left", padx=5)

        if voice is not None:
            self.rec_btn = tk.Button(button_frame, text="Record", command=self.record_voice)
            self.rec_btn.pack(side="left", padx=5)

        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise RuntimeError("OPENAI_API_KEY environment variable is required")

        self.agents = [self.new_agent(1), self.new_agent(2)]
        self.log("System: Type your message and press Enter. Click 'Add Agent' to create a new agent.")

    def new_agent(self, n: int) -> SimpleAgent:
        streaming = self.stream_var.get()
        callbacks = [TextBoxStreamingHandler(self.text)] if streaming else None
        return SimpleAgent(
            name=f"Agent{n}",
            chat=ChatOpenAI(
                openai_api_key=self.api_key,
                streaming=streaming,
                callbacks=callbacks,
            ),
            memory=ConversationBufferMemory(),
            system_prompt=f"You are Agent{n}, a helpful assistant.",
        )

    def log(self, text: str) -> None:
        self.text.configure(state="normal")
        self.text.insert(tk.END, text + "\n")
        self.text.configure(state="disabled")
        self.text.yview(tk.END)

    def send_message(self, event=None) -> None:
        user_input = self.entry.get().strip()
        if not user_input:
            return
        self.entry.delete(0, tk.END)

        if user_input.lower() == "add agent":
            self.add_agent()
            return

        self.log(f"User: {user_input}")
        if storage:
            storage.save("user", "user", user_input)
        prompt = user_input
        for agent in self.agents:
            streaming = self.stream_var.get()
            agent.chat.streaming = streaming
            agent.chat.callbacks = [TextBoxStreamingHandler(self.text)] if streaming else None
            if streaming:
                self.text.configure(state="normal")
                self.text.insert(tk.END, f"{agent.name}: ")
                self.text.configure(state="disabled")
            answer = agent.respond(prompt)
            if not streaming:
                self.log(f"{agent.name}: {answer}")
            else:
                self.log("")
            if storage:
                storage.save(agent.name, "assistant", answer)
            if self.voice_var.get() and voice:
                voice.speak(answer)
            prompt = answer

    def add_agent(self) -> None:
        idx = len(self.agents) + 1
        self.agents.append(self.new_agent(idx))
        self.log(f"System: Added Agent{idx}")

    def record_voice(self) -> None:
        if voice is None:
            return
        try:
            text = voice.record_and_transcribe()
        except Exception as exc:
            self.log(f"[Voice error] {exc}")
            return
        if text:
            self.entry.delete(0, tk.END)
            self.entry.insert(0, text)
            self.send_message()

    def run(self) -> None:
        self.root.mainloop()


if __name__ == "__main__":
    ChatGUI(tk.Tk()).run()
