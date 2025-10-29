"""Main entry point for converting test execution to workflow."""

import logging
from src.converter import TestExecutionConverter

# Constants
INPUT_FILE = "test_execution.json"
OUTPUT_FILE = "workflow.json"

# Optional: Set to True for detailed logging
VERBOSE = False


def main():
    """Convert test execution JSON to workflow JSON."""
    # Setup logging
    if VERBOSE:
        logging.basicConfig(
            level=logging.DEBUG,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )
    else:
        logging.basicConfig(
            level=logging.INFO,
            format="%(levelname)s: %(message)s",
        )

    print(f"Converting {INPUT_FILE} to {OUTPUT_FILE}...")

    try:
        # Create converter
        converter = TestExecutionConverter()

        # Perform conversion
        workflow = converter.convert(INPUT_FILE, verbose=VERBOSE)

        # Save workflow
        converter.save_workflow(workflow, OUTPUT_FILE)

        print(f"\n✓ Conversion successful!")
        print(f"✓ Workflow saved to: {OUTPUT_FILE}")

    except FileNotFoundError as e:
        print(f"Error: {e}")
        exit(1)
    except ValueError as e:
        print(f"Error: {e}")
        exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        if VERBOSE:
            import traceback
            traceback.print_exc()
        exit(1)


if __name__ == "__main__":
    main()

