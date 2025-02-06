# Bridge Postmortem API Server

A FastAPI-based server providing bridge game analysis endpoints.

## Setup

### Virtual Environment Setup
1. Create a new virtual environment:
```bash
python -m venv bridge12
```

2. Activate the virtual environment:
- On Windows:
```bash
bridge12\Scripts\activate
```
- On Unix or MacOS:
```bash
source bridge12/bin/activate
```

3. Install required packages:
```bash
pip install -r requirements.txt
```

### Prerequisites
- Python 3.12 or higher
- see requirements.txt

## Running the Server

Start the server with:
```uvicorn app.main:app --reload --log-level debug```

## Testing

### Running Tests
You can run tests in several ways:

1. Run all tests:
```bash
python -m pytest
```

2. Run tests with extra verbose output:
```bash
python -m pytest -s
```

3. Run specific test files:
```bash
python -m pytest app/bridge/tests/test_api.py
python -m pytest app/bridge/tests/test_deal_parser.py
```

4. Run tests with print statement output:
```bash
python -m pytest -s
```

### Debug Tests in VS Code/Cursor
1. Open any test file (e.g., `app/bridge/tests/test_api.py`)
2. Set breakpoints where needed
3. Press F5 or use the Debug button
4. Select "Python: Debug Tests"

## API Endpoints

- GET /: Welcome message
- POST /get_auction: Get suggested auction for a deal
  - Request body: {"pbn": "N:T5.J98643.K95.76 432.KQ5.863.T984 ..."}
  - Returns: {"auction": ["1H", "Pass", "4H", "Pass", "Pass", "Pass"], "explanation": "..."}

## Documentation

API documentation available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Project Structure

```app/
├── __init__.py
├── main.py
├── models.py
└── bridge/
    ├── __init__.py
    ├── deal_parser.py
    └── tests/
        ├── __init__.py
        ├── test_api.py
        └── test_deal_parser.py
```

