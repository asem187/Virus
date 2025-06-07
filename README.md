# Multi-Agent Evolving Chat

This repository contains a command-line chat program that coordinates several OpenAI-powered agents. Each agent maintains its own memory and slightly updates its behaviour based on past exchanges, giving a tiny glimpse into how a group of specialised assistants might work together.

## Requirements
- Python 3.9+
- [openai](https://pypi.org/project/openai/)
- [langchain](https://pypi.org/project/langchain/)

Install dependencies:
```bash
pip install -r requirements.txt
```

The optional package `requests` is required for the built-in web search and
GitHub cloning tools described below. It is included in `requirements.txt`.

## Installation notes
1. Install dependencies with `pip install -r requirements.txt`. Voice features
   use optional packages `SpeechRecognition` and `pyttsx3`; the program works in
   text mode when they are absent. The local web server relies on `Flask`, and
   persistence to MongoDB requires `pymongo`.
2. Set environment variables before running:
   - `OPENAI_API_KEY` – required for all examples.
   - `TAVILY_API_KEY` – enables the `search` command.
3. Ensure `git` is available if you intend to use the `clone` helper.
4. Try `python assistants_chat.py` for a demo using the new OpenAI Assistants API.

## Usage
Set your OpenAI API key in the `OPENAI_API_KEY` environment variable and run:
```bash
python agent.py [--model MODEL] [--temperature T] [--agents N] [--stream]
```
`--model` sets the OpenAI model name, `--temperature` adjusts randomness, and
`--agents` controls the number of agents created at startup. `--voice` enables
speech input and output if the optional dependencies are installed. `--stream`
streams tokens in real time using LangChain's callback handler. Type messages to
chat with the agents. Enter `quit` or `exit` to stop. Use `add agent` to create
a new agent at runtime. Each agent prints its response in turn, using the
previous reply as context. The system prompt of every agent evolves with a short
summary of its last answer to illustrate adaptation.

### Built-in tools
Two helper commands are available when running `agent.py`:

* `search QUERY` – performs a Tavily web search and prints the results. Set the
  `TAVILY_API_KEY` environment variable before using this command.
* `clone REPO_URL` – clones the specified Git repository into a local `repos/`
  folder using `git`.

These commands run before any agent responses are generated and output their
results directly to the console.

## GUI
A Tkinter interface lets you run the multi-agent chat entirely on your desktop. Set `OPENAI_API_KEY` and run:
```bash
python gui.py
```
Use the **Add Agent** button to spawn more assistants during a session. Enable **Voice** for microphone input and text‑to‑speech replies (if the optional packages are installed). Turn on **Stream** to view tokens as they are generated in real time.

To create a standalone application you can distribute, install [PyInstaller](https://www.pyinstaller.org/) and run:
```bash
pyinstaller --onefile gui.py
```
The resulting executable in the `dist/` directory launches the GUI without needing a local web server.

## Local server
Run a lightweight HTTP server so you can chat from another device on your local network:

```bash
python server.py --host 0.0.0.0 --port 5000
```

Then open `http://<your_pc_ip>:5000` in a browser on your phone. Messages will be processed by the same multi‑agent logic.
Set `CHAT_PERSIST=1` to save all messages to `chat.db`. If `MONGODB_URI` is defined, logs are mirrored to MongoDB as well.

## OpenAI Assistants example
`assistants_chat.py` demonstrates how to use the new OpenAI Assistants API for a
single evolving agent. The assistant's instructions are updated after every
reply, mirroring the behaviour of the CLI but managed by the OpenAI service.

```bash
python assistants_chat.py
```

## Voice mode
Install `SpeechRecognition` and `pyttsx3` (see `requirements.txt`) and run the
CLI with `--voice` to speak to the agents using OpenAI Whisper. Responses are
read aloud using text-to-speech. Voice support is optional and falls back to
text if the libraries are not available.

## Security
Keep your API keys private. Never commit them to source control. This project
relies on `OPENAI_API_KEY` at runtime, so store it as an environment variable.
`.gitignore` prevents common artifacts such as `__pycache__` and `.pytest_cache`
from being tracked.

## Development and training
1. Clone this repository and install the requirements in a virtual environment.
2. Open `agent.py` and adjust the `SimpleAgent` class or create new agent
   types to experiment with different prompts or memory strategies.
3. Run the program with a small number of agents and examine how the
   `system_prompt` evolves after each exchange.
4. Add unit tests under `tests/` using `pytest` to lock in desired behaviour
   before making bigger changes.
5. When the project grows, use the `gui.py` interface to iterate quickly and
   package your build with PyInstaller for distribution.

## LangChain resources
The required version of LangChain is installed automatically when you run

```bash
pip install -r requirements.txt
```

If you would like to explore examples or contribute to LangChain itself, you can
clone the library from GitHub and install it in editable mode:

```bash
git clone https://github.com/langchain-ai/langchain.git
cd langchain
pip install -e .
```

Cloning LangChain is optional; the chat agents in this repository work with the
version pinned in `requirements.txt`.
