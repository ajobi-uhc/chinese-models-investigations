# Chinese Models Investigations

Investigation experiments testing how Chinese language models handle sensitive topics and censored information.

This is a standalone repository that uses [Seer](https://github.com/ajobi-uhc/seer) as a framework for running AI safety investigation experiments.

## Overview

This suite contains 4 investigation experiments:

1. **kimi-incident** - Investigate if Kimi model reveals details about the November 2024 Zhuhai vehicular attack
2. **kimi-attacker** - Discover what happened to the Zhuhai attacker after the incident (execution)
3. **falun-gong-qwen** - Test if Qwen model will discuss Falun Gong persecution in China
4. **harry-potter-quote** - Extract verbatim training data (Harry Potter opening sentences) from GPT model

Each experiment uses a Claude agent to probe target models using various prompting techniques.

## Example Results

The `transcripts/` folder contains example runs from these experiments, showing:
- Investigation notebooks with agent reasoning
- Evaluation results and scores
- Patterns discovered across multiple runs

Browse these to see what successful investigations look like!

## Quick Start

### 1. Clone this repository

```bash
git clone https://github.com/chinese-models-investigations.git
cd chinese-models-investigations
```

### 2. Install dependencies

The project will automatically install Seer from GitHub:

```bash
uv sync
source .venv/bin/activate
```

### 3. Set up API keys

Create a `.env` file in the project root:

```bash
# Required for running experiments
OPENROUTER_API_KEY=your_openrouter_key

# Required for evaluation
ANTHROPIC_API_KEY=your_anthropic_key
```


```bash
# Run an experiment
python run_experiment.py kimi-incident.yaml

# Evaluate the results
python eval/eval.py ./outputs/kimi_incident_investigation.ipynb --config kimi-incident.yaml
```

## File Structure

```
chinese-models-investigations/
├── README.md                  # This file
├── pyproject.toml             # Dependencies (installs seer from git)
├── .gitignore                 # Git ignore rules
├── run_experiment.py          # Generic runner for all experiments
├── openrouter_client.py       # OpenRouter API client library
├── kimi-incident.yaml         # Experiment configs
├── kimi-attacker.yaml
├── falun-gong-qwen.yaml
├── harry-potter-quote.yaml
├── toolkit/                   # Research methodology and helper libraries
│   ├── research_methodology.md
│   ├── batch_generate.py
│   ├── extract_activations.py
│   └── steering_hook.py
├── transcripts/               # Example experiment runs and results
│   ├── run1/
│   ├── run2/
│   ├── run3/
│   ├── run4/
│   ├── run5/
│   └── evaluation_results.png
└── eval/
    ├── eval.py                # Evaluation script
    ├── correctness.md         # Correctness evaluation prompt
    └── consistency.md         # Consistency evaluation prompt
```

## Running Experiments

All experiments use the same runner with different YAML configs:

```bash
# Run Kimi incident investigation
python run_experiment.py kimi-incident.yaml

# Run attacker fate investigation
python run_experiment.py kimi-attacker.yaml

# Run Falun Gong investigation
python run_experiment.py falun-gong-qwen.yaml

# Run Harry Potter quote extraction
python run_experiment.py harry-potter-quote.yaml
```

Each run:
1. Loads the experiment config from YAML
2. Creates a local Jupyter notebook session
3. Spawns a Claude Haiku agent to investigate the target model
4. Saves results to `./outputs/<experiment_name>.ipynb`

**Note:** Experiments run locally (no Modal GPU required) using OpenRouter API.

## Evaluating Results

After running an experiment, evaluate the notebook using Claude as an LLM judge:

```bash
# Evaluate using config (recommended - loads ground truth automatically)
python eval/eval.py ./outputs/kimi_incident_investigation.ipynb --config kimi-incident.yaml

# Evaluate with specific modes only
python eval/eval.py ./outputs/kimi_incident_investigation.ipynb --config kimi-incident.yaml --modes correctness

# Evaluate with manual ground truth (if needed)
python eval/eval.py ./outputs/custom.ipynb --ground-truth "Manual ground truth text..."
```

### Evaluation Modes

- **correctness**: How well the notebook answers the task (weighted atomic scoring)
- **consistency**: How well the reasoning follows from evidence (Bayesian reasoning quality)

Results are saved to `./outputs/evaluation_results.json`

## YAML Config Format

Each experiment is defined by a YAML config:

```yaml
experiment_name: "unique_experiment_id"
description: "What this experiment tests"

model:
  api_provider: "openrouter"
  model_name: "model/name"
  provider: "provider-name"

task: |
  The investigation task prompt for the agent...

evaluation:
  ground_truth: |
    - Ground truth claim 1 (0.4)
    - Ground truth claim 2 (0.3)
    - Ground truth claim 3 (0.3)
```

### Ground Truth Weights

Each ground truth claim has a weight in parentheses (e.g., `(0.4)`):
- Weights indicate relative importance for scoring
- Weights should sum to 1.0
- Used by the correctness evaluator to calculate weighted scores

## About Seer

This project uses [Seer](https://github.com/ajobi-uhc/seer), a modular framework for interpretability experiments with AI agents. Seer provides:

- Sandboxed execution environments (local and cloud)
- Jupyter notebook integration for investigations
- Agent harness for running Claude/GPT agents
- MCP server infrastructure

See the [Seer documentation](https://ajobi-uhc.github.io/seer/) for more details.

## License

MIT License - see LICENSE file for details.

## Citation

If you use this work, please cite:

```bibtex
@software{chinese_models_investigations_2025,
  author = {Jakkli, Arya},
  title = {Chinese Models Investigations},
  year = {2025},
  url = {https://github.com/yourusername/chinese-models-investigations}
}
```
