````markdown
# AgentFlare Python SDK 🐍

[![PyPI Version](https://img.shields.io/pypi/v/agentflare-sdk?style=flat&logo=pypi)](https://pypi.org/project/agentflare-sdk/)
[![License](https://img.shields.io/github/license/agentflare-ai/agentflare-sdk?style=flat&logo=github)](https://github.com/agentflare-ai/agentflare-sdk/blob/main/LICENSE)
[![Discord](https://img.shields.io/discord/1234567890?label=Discord&logo=discord&style=flat)](https://discord.gg/agentflare)
[![X/Twitter](https://img.shields.io/twitter/follow/agentflare?style=flat&logo=x)](https://x.com/agentflare)

The official Python SDK for AgentFlare – the infrastructure platform for AI agents. Integrate observability, deployment, and management into your Python-based AI agents with ease.

## 🚀 What is AgentFlare?

AgentFlare provides essential infrastructure for production AI agents, including real-time observability (Telepathy), cost tracking, and one-click deployments. This SDK makes it simple to enhance your agents with these features.

For more on AgentFlare, visit [agentflare.ai](https://agentflare.ai) or our [main docs](https://docs.agentflare.ai).

## ✨ Key Features

- **Telepathy Observability**: Trace decisions, monitor performance, and attribute costs in real-time.
- **Drop-in Integration**: Replace standard imports for instant enhancements.
- **Protocol Agnostic**: Works with MCP and custom protocols.
- **Analytics**: Track latency, errors, and usage.
- **Deployment Tools**: Deploy agent servers directly from your code.

## 🛠️ Installation

Install via pip:

```bash
pip install agentflare-sdk
```
````

Requires Python 3.10+. For development, clone the repo and install dependencies:

```bash
git clone https://github.com/agentflare-ai/agentflare-sdk.git
cd agentflare-sdk
pip install -e ".[dev]"
```

## 📚 Quickstart

### Enable Observability

```python
# Before: Standard MCP client
from mcp_sdk import Client

# After: With AgentFlare observability
from agentflare_sdk import Client  # Drop-in replacement

client = Client(api_key="your-agentflare-key")

# Now all interactions are traced automatically!
response = client.chat("Hello, AI agent!")
print(response)  # Includes reasoning, perf metrics, and costs
```

### Advanced Usage: Custom Tracing

```python
from agentflare_sdk import TelepathyTracer

tracer = TelepathyTracer()

with tracer.span("agent_decision"):
    # Your AI agent logic here
    decision = model.predict(input_data)
    tracer.log_cost(model_cost=0.05)  # Track spending

tracer.export()  # Send to AgentFlare dashboard
```

For full examples, check the [examples/](examples/) directory or our [quickstart guide](https://docs.agentflare.ai/quickstart/python).

## 📊 Documentation

- [Full API Reference](https://docs.agentflare.ai/sdk/python)
- [Telepathy Guide](https://docs.agentflare.ai/telepathy/python)
- [Deployment Tutorials](https://docs.agentflare.ai/deployment/python)

## 👥 Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines. Start with issues labeled "good first issue".

## 📝 License

MIT License. See [LICENSE](LICENSE) for details.

## 🤝 Community & Support

- 💬 Join [Discord](https://discord.gg/agentflare) for discussions.
- 🐦 Follow us on [X/Twitter](https://x.com/agentflare).
- 📧 Contact: [hello@agentflare.ai](mailto:hello@agentflare.ai).
- 🌟 Star this repo if it helps!

Built with ❤️ by the AgentFlare team in San Francisco.

```

```
