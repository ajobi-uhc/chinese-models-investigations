"""Activation Oracles Investigation - Query model activations with natural language.

Demonstrates:
- GPU sandbox with base model and oracle PEFT adapter
- Activation oracle interpretability technique
- Probing hidden states, detecting deception, uncovering secret knowledge

Usage:
    python activation_oracles/run_experiment.py falun-gong.yaml
    python activation_oracles/run_experiment.py tiananmen.yaml
"""

import asyncio
import argparse
from pathlib import Path
import yaml

from src.environment import Sandbox, SandboxConfig, ExecutionMode, ModelConfig
from src.workspace import Workspace, Library
from src.execution import create_notebook_session
from src.harness import run_agent


async def run_experiment(config_path: Path):
    """Run an activation oracle experiment from a YAML config file."""

    # Load config
    with open(config_path) as f:
        config = yaml.safe_load(f)

    experiment_name = config['experiment_name']
    task = config['task']
    model_name = config.get('model', {}).get('name', 'Qwen/Qwen3-32B')

    print(f"Running experiment: {experiment_name}")
    print(f"Description: {config['description']}")
    print(f"Model: {model_name}")
    print("=" * 80)

    example_dir = Path(__file__).parent
    toolkit = example_dir.parent / "toolkit"

    # Configure the sandbox
    # Uses Qwen3-32B with a pretrained activation oracle adapter
    # See: https://github.com/adamkarvonen/activation_oracles
    sandbox_config = SandboxConfig(
        gpu="H100",  # 32B model needs more VRAM
        execution_mode=ExecutionMode.NOTEBOOK,
         models=[
            # Base model - loaded as PeftModel with "default" adapter for oracle library
            ModelConfig(
                name="Qwen/Qwen3-32B",
                var_name="model",
                load_as_peft=True,  # Wrap as PeftModel for activation oracles
            ),
        ],
        python_packages=[
            "torch",
            "transformers",
            "accelerate",
            "peft",
            "datasets",
            "einops",
            "bitsandbytes",
            "tqdm",
            "pydantic",
        ],
        secrets=["HF_TOKEN"],
        timeout=3600,  # 1 hour
    )

    sandbox = Sandbox(sandbox_config).start()

    # Set up workspace with activation oracles package
    workspace = Workspace(
        libraries=[
            Library.from_directory(toolkit / "activation_oracles"),
        ]
    )

    session = create_notebook_session(sandbox, workspace)

    # Activation oracle setup instructions
    ao_setup = """
Setup:
import torch
from activation_oracles.core import load_lora_adapter

# Load the oracle adapter onto the existing PeftModel
oracle_adapter_path = "adamkarvonen/checkpoints_cls_latentqa_past_lens_Qwen3-32B"
oracle_adapter_name = load_lora_adapter(model, oracle_adapter_path)

# Set up global state for oracle functions
import activation_oracles
activation_oracles._model = model
activation_oracles._tokenizer = tokenizer
activation_oracles._device = model.device
activation_oracles._oracle_adapter_name = oracle_adapter_name
activation_oracles._generation_kwargs = {
    "do_sample": False,
    "temperature": 0.0,
    "max_new_tokens": 150,
}

Available Functions:
from activation_oracles import (
    chat,                      # Generate from base model (Qwen)
    chat_ao,                   # Chat with oracle directly (no activation injection)
    probe,                     # Probe segment activations with questions
    probe_before_generation,   # Probe at the generation token
    chat_and_probe,            # Generate and probe in one call
    probe_tokens,              # Token-by-token probing
    show_tokens,               # Display token positions
    pretty_print_probe,        # Format results nicely
)
    """

    research_methodology = (toolkit / "research_methodology.md").read_text()
    ao_guide = (toolkit / "activation_oracle_guide.md").read_text()

    # Create full prompt with model info and library docs
    prompt = f"{session.model_info_text}\n\n{workspace.get_library_docs()}\n\n{ao_setup}\n\n{ao_guide}\n\n{research_methodology}\n\n{task}"

    try:
        async for msg in run_agent(
            prompt=prompt,
            mcp_config=session.mcp_config,
            provider="claude",
            model="claude-opus-4-5-20251101"
        ):
            pass

        print(f"\n✓ Jupyter: {session.jupyter_url}")
        print(f"✓ Results saved to: ./outputs/")

    finally:
        sandbox.terminate()


def main():
    parser = argparse.ArgumentParser(
        description='Run activation oracle experiments from YAML config files'
    )
    parser.add_argument(
        'config',
        type=Path,
        help='Path to YAML config file (e.g., falun-gong.yaml)'
    )

    args = parser.parse_args()

    # Handle relative paths from activation_oracles directory
    config_path = args.config
    if not config_path.exists():
        # Try looking in the activation_oracles directory
        alt_path = Path(__file__).parent / config_path
        if alt_path.exists():
            config_path = alt_path
        else:
            print(f"Error: Config file not found: {args.config}")
            return 1

    try:
        asyncio.run(run_experiment(config_path))
    except KeyboardInterrupt:
        print("\n")
        print("=" * 80)
        print("INTERRUPTED - IMPORTANT REMINDER")
        print("=" * 80)
        print("Please check https://modal.com/apps to ensure your GPU container is stopped!")
        print("Modal containers may still be running and consuming credits.")
        print("=" * 80)

    return 0


if __name__ == "__main__":
    exit(main())
