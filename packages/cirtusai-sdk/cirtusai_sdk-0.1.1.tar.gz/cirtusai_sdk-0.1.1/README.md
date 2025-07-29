# CirtusAI Python SDK

The CirtusAI Python SDK provides a simple, robust interface for developers to interact with the CirtusAI backend. It enables seamless agent management, wallet and asset provisioning, decentralized identity (DID) operations, and verifiable credential workflows—all through a modern, well-documented Python API and CLI.

- **Sync and async support:** Use either synchronous or asynchronous clients.
- **Comprehensive CLI:** Manage agents, wallets, and credentials from the command line.
- **Pydantic models:** Typed request/response validation for reliability.
- **Easy integration:** Designed for third-party developers to get started in minutes.
- **Automated tests and CI:** Ensures reliability and compatibility with the CirtusAI backend.

Whether you’re building identity-driven apps, automating agent provisioning, or issuing verifiable credentials, the CirtusAI SDK makes integration fast and developer-friendly.

---

## Installation

```bash
pip install cirtusai-sdk
# or to install the dev extras:
pip install cirtusai-sdk[dev]
```

---

## Quickstart

```python
from cirtusai import CirtusAIClient

client = CirtusAIClient(base_url="https://api.cirtus.ai", token="YOUR_JWT_TOKEN")
agents = client.agents.list_agents()
child = client.agents.create_child_agent(parent_id=agents[0]["id"], name="MyChild")
email_asset = client.agents.provision_email(child["id"])
vc = client.identity.issue_credential(
    subject_id=child["id"],
    types=["VerifiableCredential"],
    claim={"role": "member"}
)
client.close()
```

---

## Features

- Manage agents and child agents
- Provision email and wallet assets
- Issue and verify verifiable credentials
- Full CLI for agent and asset management
- Sync and async Python API

---

## Command-Line Interface (CLI)

After installation, use the `cirtusai` command:

```bash
export CIRTUSAI_TOKEN="..."
cirtusai agents list
cirtusai agents provision-email
```

Run `cirtusai --help` for all commands.

---

## Documentation

- [Technical Documentation](docs/TECHNICAL_DOCUMENTATION.md): Advanced usage, API models, and error handling.

---

## Contributing

Contributions are welcome! Please open issues or pull requests on [GitHub](https://github.com/cirtus-ai/cirtusai-sdk).

---

## License

This project is licensed under the MIT License.

---

Happy coding with CirtusAI! 🎉
