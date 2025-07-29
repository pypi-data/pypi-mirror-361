# Optiverse

Optiverse is a framework that uses Large Language Models (LLMs) to iteratively evolve code and algorithms. It's like [AlphaEvolve](https://deepmind.google/discover/blog/alphaevolve-a-gemini-powered-coding-agent-for-designing-advanced-algorithms/) by DeepMind.


## Installation

```bash
pip install optiverse
```

## Quick Start

```python
import optiverse
from openai import OpenAI

# Configure the optimizer
config = optiverse.config.Config(
    llm=optiverse.config.LLM(
        model="gpt-4",
        client=OpenAI(api_key="your-api-key"),
    ),
    max_iterations=10,
    problem=optiverse.config.Problem(
        description="Your optimization problem description",
        initial_solution="Initial solution code",
    ),
)

# Create optimizer and run
optimizer = optiverse.optimizer.Optimizer(
    config=config,
    evaluator=YourCustomEvaluator(),
    prompt_generator=optiverse.prompt_generator.EvolutionaryPromptGenerator(),
    store=optiverse.store.FileSystemStore(directory="results"),
)
optimizer.run()
```

## Example

See the [TSP example](examples/tsp/) for a complete implementation solving the Traveling Salesman Problem.

## License

GPL-3.0
