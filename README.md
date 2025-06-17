# FastAPI_Projects

## Setup Instructions

### 1. Install `uv` (Python package manager)

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Create and initialize a virtual environment

```bash
uv venv
uv init
```

### 3. Activate the virtual environment

```bash
source .venv/bin/activate
```

### 4. Install project dependencies

```bash
uv pip install -r requirements.txt
```

Or, to sync with `pyproject.toml`:

```bash
uv sync
```

### 5. (Optional) Freeze current dependencies

```bash
uv pip freeze > requirements.txt
```
