# Test Execution to Workflow Converter

A Python CLI tool that converts raw Playwright test execution JSON files into structured workflow JSON files using OpenAI for intelligent categorization and description generation.

## Features

- Parse and validate Playwright test execution recordings
- Intelligent step categorization using LLM (navigation, interaction, validation)
- Generate human-readable descriptions for each step
- Create comprehensive workflow summaries
- Structured output with metadata, execution context, and categorized steps

## Installation

1. Clone the repository

2. Create and activate a virtual environment:
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
# venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env and add your OpenAI API key
```

## Usage

1. Update the constants in `main.py` if needed:
```python
INPUT_FILE = "test_execution.json"  # Your input file path
OUTPUT_FILE = "workflow.json"       # Your output file path
VERBOSE = False                      # Set to True for detailed logging
```

2. Run the converter:
```bash
# Make sure virtual environment is activated
source venv/bin/activate

python main.py
```

The script will convert the test execution JSON and save the workflow JSON automatically.

## Project Structure

```
gen-workflow/
├── main.py                       # Main entry point
├── src/
│   ├── __init__.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── input_schema.py      # Input JSON validation
│   │   └── output_schema.py     # Output workflow schema
│   ├── parser.py                 # Parse raw test execution
│   ├── llm/
│   │   ├── __init__.py
│   │   ├── client.py            # OpenAI client setup
│   │   └── prompts.py           # Prompt templates
│   └── converter.py              # Main conversion logic
├── requirements.txt
├── README.md
└── .env.example
```

## License

MIT

