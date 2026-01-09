"""Generic runner for YAML-configured investigation experiments.

Usage:
    python run_experiment.py kimi-incident.yaml
    python run_experiment.py harry-potter-quote.yaml
"""

import asyncio
import argparse
from pathlib import Path
import yaml
import os
import sys

from src.workspace import Workspace, Library
from src.execution import create_local_notebook_session
from src.harness import run_agent


def check_api_keys():
    """Check if required API keys are set in environment variables."""
    missing_keys = []

    if not os.getenv('OPENROUTER_API_KEY'):
        missing_keys.append('OPENROUTER_API_KEY')

    if not os.getenv('ANTHROPIC_API_KEY'):
        missing_keys.append('ANTHROPIC_API_KEY')

    if missing_keys:
        print("Error: Missing required API keys in environment variables:")
        for key in missing_keys:
            print(f"  - {key}")
        print("\nPlease set these environment variables before running experiments.")
        print("You can:")
        print("  1. Create a .env file based on .env.example")
        print("  2. Export them directly: export OPENROUTER_API_KEY=your_key_here")
        sys.exit(1)


async def run_experiment(config_path: Path):
    """Run an experiment from a YAML config file."""

    # Load config
    with open(config_path) as f:
        config = yaml.safe_load(f)

    experiment_name = config['experiment_name']
    task = config['task']

    print(f"Running experiment: {experiment_name}")
    print(f"Description: {config['description']}")
    print("=" * 80)

    # Setup paths
    current_dir = Path(__file__).parent
    openrouter_client = current_dir / "openrouter_client.py"
    toolkit = current_dir / "toolkit"

    # Create workspace
    workspace = Workspace(
        libraries=[Library.from_file(openrouter_client)]
    )

    # Create local notebook session
    session = create_local_notebook_session(
        workspace=workspace,
        name=experiment_name,
        notebook_dir="./outputs",
    )

    # Load research methodology
    research_methodology = (toolkit / "research_methodology.md").read_text()

    # Create full prompt
    prompt = f"{workspace.get_library_docs()}\n\n{research_methodology}\n\n{task}"

    try:
        async for msg in run_agent(
            prompt=prompt,
            mcp_config=session.mcp_config,
            provider="claude",
            kwargs={"disallowed_tools": ["WebSearch"], "model": "claude-haiku-4-5-20251001"},
        ):
            print(msg, end='', flush=True)
            pass

        print(f"\n✓ Notebook saved to: {session.notebook_dir}")
        print(f"\nTo evaluate, run:")
        print(f"  python eval/eval.py {session.notebook_dir}/{experiment_name}.ipynb --config {config_path}")

    finally:
        session.terminate()


def main():
    parser = argparse.ArgumentParser(
        description='Run investigation experiments from YAML config files'
    )
    parser.add_argument(
        'config',
        type=Path,
        help='Path to YAML config file (e.g., kimi-incident.yaml)'
    )

    args = parser.parse_args()

    if not args.config.exists():
        print(f"Error: Config file not found: {args.config}")
        return 1

    check_api_keys()

    asyncio.run(run_experiment(args.config))
    return 0


if __name__ == "__main__":
    exit(main())
