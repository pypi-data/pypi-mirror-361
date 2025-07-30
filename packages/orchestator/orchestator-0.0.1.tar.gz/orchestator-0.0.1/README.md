# 🎼 orchestator

**orchestator** is a lightweight orchestration layer for intelligent agents, inspired by the role of a conductor in an orchestra.  
It provides fast and modular coordination mechanisms for message routing, task execution, and agent collaboration.

---

## 🚀 Features

- 🧠 Orchestrates communication between AI agents
- 🔄 Async-ready and event-driven
- 🪶 Lightweight and extensible
- 🧩 Plug-and-play with MCP-based systems
- 📡 Ideal for microservices, LLM agents, task routers, and distributed tools

---

## 📦 Installation

```bash
pip install orchestator

⚡ Quick Example
python
Copy
Edit
from orchestator import Orchestrator

orch = Orchestrator()

@orch.on("greeting")
async def handle_greeting(payload):
    return f"Hello, {payload.get('name', 'world')}!"

# Simulate a message
response = await orch.dispatch("greeting", {"name": "Federico"})
print(response)  # → Hello, Federico!

🔧 Use Cases
Agent-to-agent orchestration

Task routing and message dispatching

LLM toolchain coordination

Event-based pipelines

📚 Documentation
📘 Wiki: orchestator Wiki

🧪 Examples: Examples Folder

🐛 Issues: Issue Tracker

📦 Part of the Intelligent Agents Platform
pgsql
Copy
Edit
🌐 py-agent-client     → Client SDK for agent communication
🧠 py-agent-core       → Shared utilities and protocols
🔧 py-agent-tool       → Tool wrapping and execution
📡 py-agent-server     → MCP server backend
🎼 orchestator         → Agent orchestrator layer ← you are here

🪪 License
This project is licensed under the MIT License.

🧑‍💻 Author
Built with ❤️ by Federico Monfasani
Part of the Intelligent Agents Platform (IAP) ecosystem

yaml
Copy
Edit

---

¿Querés que te genere también un ejemplo de código real en `orchestator/core.py` o `orchestrator.py` para acompañarlo?
