# Slough - Generic - CLI tool

This is a CLI tool to work with a Slough configuration file. This configuration file is a YAML file that contains the configuration for Slough. The tool allows you to create, update, and delete Slough configurations. These configurations can be used for CI/CD pipelines, local development, and other use cases.
## Setting up the environment

To set up the environment, you need to have [`uv`](https://github.com/astral-sh/uv) installed. When you have `uv` installed, you can run the following command to set up the environment within the project directory:

```bash
uv sync
```

After this, the application can be used. You can run the unit tests with the following command:

```bash
uv run pytest
```

You can also activate the created virtual environment with the following command:

```bash
source .venv/bin/activate
```
