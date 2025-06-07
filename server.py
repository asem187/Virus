import os
import argparse
from flask import Flask, request, jsonify, render_template_string
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory

from agent import SimpleAgent
from storage import storage

app = Flask(__name__)

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise RuntimeError("OPENAI_API_KEY environment variable is required")

agents = [
    SimpleAgent(
        name="Agent1",
        chat=ChatOpenAI(openai_api_key=api_key),
        memory=ConversationBufferMemory(),
        system_prompt="You are Agent1, a helpful assistant.",
    )
]

@app.route("/", methods=["GET"])
def index():
    return render_template_string(
        """
        <html><body>
        <h3>Multi-Agent Chat</h3>
        <form method='post' action='/chat'>
          <input name='message' style='width:70%%' autofocus>
          <input type='submit'>
        </form>
        </body></html>
        """
    )

@app.route("/chat", methods=["POST"])
def chat():
    message = request.form.get("message") or request.json.get("message", "")
    if storage:
        storage.save("user", "user", message)
    prompt = message
    for agent in agents:
        answer = agent.respond(prompt)
        if storage:
            storage.save(agent.name, "assistant", answer)
        prompt = answer
    return jsonify({"reply": prompt})


def main() -> None:
    parser = argparse.ArgumentParser(description="Run chat server")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=5000)
    args = parser.parse_args()
    app.run(host=args.host, port=args.port)


if __name__ == "__main__":
    main()
