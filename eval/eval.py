"""Evaluation script for investigation notebooks.

Evaluates notebooks using Claude as an LLM judge with two modes:
- Correctness: How well the notebook answers the task
- Consistency: How well the reasoning follows from the evidence

Usage:
    python eval.py <notebook_path> --config <config.yaml>
    python eval.py <notebook_path> --ground-truth "..."

The script will:
1. Load the notebook content
2. Load ground truth from YAML config or command line
3. Run both correctness and consistency evaluations
4. Save results to evaluation_results.json
"""

import argparse
import json
import os
from pathlib import Path
from anthropic import Anthropic
import yaml
import dotenv
dotenv.load_dotenv()


def load_evaluation_prompt(mode: str) -> str:
    """Load the system prompt for the specified evaluation mode."""
    eval_dir = Path(__file__).parent
    mode_file = eval_dir / f"{mode}.md"

    if not mode_file.exists():
        raise FileNotFoundError(f"Evaluation prompt not found: {mode_file}")

    return mode_file.read_text()


def read_notebook(notebook_path: Path) -> str:
    """Read and return the notebook content as a string."""
    if not notebook_path.exists():
        raise FileNotFoundError(f"Notebook not found: {notebook_path}")

    return notebook_path.read_text()


def load_ground_truth_from_config(config_path: Path) -> str:
    """Load ground truth from YAML config file."""
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with open(config_path) as f:
        config = yaml.safe_load(f)

    if 'evaluation' not in config or 'ground_truth' not in config['evaluation']:
        raise ValueError(f"No ground_truth found in config: {config_path}")

    return config['evaluation']['ground_truth'].strip()


def evaluate_notebook(notebook_content: str, ground_truth: str, mode: str, client: Anthropic) -> dict:
    """
    Evaluate a notebook using Claude as an LLM judge.

    Args:
        notebook_content: The full notebook content (JSON)
        ground_truth: The ground truth answer to compare against
        mode: Either "correctness" or "consistency"
        client: Anthropic client instance

    Returns:
        Dictionary with evaluation results including score and reasoning
    """
    system_prompt = load_evaluation_prompt(mode)

    user_prompt = f"""Please evaluate the following research notebook.

## Ground Truth Answer:
{ground_truth}

## Notebook Content to Evaluate:
{notebook_content}

Please provide your evaluation following the format specified in your system prompt.
"""

    print(f"\n{'=' * 80}")
    print(f"Running {mode.upper()} evaluation...")
    print('=' * 80)

    response = client.messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=4096,
        temperature=0.0,
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}]
    )

    result_text = response.content[0].text
    print(result_text)
    print("=" * 80)

    # Parse score from response
    score = None
    try:
        if "<score>" in result_text and "</score>" in result_text:
            score_text = result_text.split("<score>")[1].split("</score>")[0].strip()
            score = float(score_text)
    except Exception as e:
        print(f"Warning: Could not parse score from {mode} response: {e}")

    return {
        "mode": mode,
        "score": score,
        "full_response": result_text
    }


def save_results(results: dict, notebook_path: Path):
    """Save evaluation results to JSON file alongside the notebook."""
    results_file = notebook_path.parent / "evaluation_results.json"

    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\n✅ Results saved to: {results_file}")


def main():
    parser = argparse.ArgumentParser(
        description='Evaluate investigation notebooks using Claude as an LLM judge',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python eval.py ./outputs/kimi_incident_investigation.ipynb --config ../kimi-incident.yaml
  python eval.py ./outputs/harry_potter_quote_extraction.ipynb --config ../harry-potter-quote.yaml --modes correctness
  python eval.py ./outputs/custom.ipynb --ground-truth "Direct ground truth text..."
        """
    )

    parser.add_argument(
        'notebook',
        type=Path,
        help='Path to the notebook file to evaluate'
    )

    parser.add_argument(
        '--config',
        type=Path,
        help='Path to YAML config file (to load ground truth from)'
    )

    parser.add_argument(
        '--ground-truth',
        help='Ground truth answer to evaluate against (alternative to --config)'
    )

    parser.add_argument(
        '--modes',
        nargs='+',
        default=['correctness', 'consistency'],
        choices=['correctness', 'consistency'],
        help='Evaluation modes to run (default: both)'
    )

    args = parser.parse_args()

    # Validate inputs
    if not args.notebook.exists():
        print(f"Error: Notebook not found at {args.notebook}")
        return 1

    # Load ground truth
    if args.config:
        try:
            ground_truth = load_ground_truth_from_config(args.config)
            print(f"Loaded ground truth from: {args.config}")
        except Exception as e:
            print(f"Error loading config: {e}")
            return 1
    elif args.ground_truth:
        ground_truth = args.ground_truth
    else:
        print("Error: Must provide either --config or --ground-truth")
        return 1

    # Initialize Anthropic client
    client = Anthropic()

    # Read notebook
    print(f"Reading notebook: {args.notebook}")
    notebook_content = read_notebook(args.notebook)

    # Run evaluations
    results = {
        "notebook": str(args.notebook),
        "ground_truth": ground_truth,
        "evaluations": []
    }

    for mode in args.modes:
        try:
            eval_result = evaluate_notebook(
                notebook_content,
                ground_truth,
                mode,
                client
            )
            results["evaluations"].append(eval_result)
        except Exception as e:
            print(f"Error running {mode} evaluation: {e}")
            continue

    # Save results
    save_results(results, args.notebook)

    # Print summary
    print("\n" + "=" * 80)
    print("EVALUATION SUMMARY")
    print("=" * 80)
    for eval_result in results["evaluations"]:
        if eval_result['score'] is not None:
            print(f"{eval_result['mode'].capitalize()} Score: {eval_result['score']}/10")
    print("=" * 80)

    return 0


if __name__ == "__main__":
    exit(main())
