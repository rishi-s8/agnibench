"""
Run the procedural workspace benchmark.

Usage:
    python run_procedural.py                         # defaults: seed=42, all difficulties
    python run_procedural.py --seed 99               # different seed = different tool surfaces
    python run_procedural.py --seed 42 --seed 99     # run multiple seeds
    python run_procedural.py --simple 5 --medium 3   # custom difficulty distribution
    python run_procedural.py --verbose                # show full execution details
    python run_procedural.py --max-iterations 20      # more iterations per task
"""

import argparse
import json
import os
import sys
from datetime import datetime
from typing import Any, Dict, List

from dotenv import load_dotenv

load_dotenv()

from agentbuilder.Client.openai_client import ConversationWrapper
from agentbuilder.Loop.base import AgenticLoop
from agentbuilder.Planner.base import AgenticPlanner

from agnibench.core.abstractions import DifficultyLevel
from agnibench.core.environment import SimulatedEnvironment
from agnibench.core.runner import BenchmarkRunner, RunConfig
from agnibench.procedural import create_procedural_suite


SYSTEM_PROMPT = (
    "You are a helpful assistant with access to workspace tools. "
    "Use the provided tools to complete the user's request. "
    "Read each tool's description and parameters carefully before calling it. "
    "When you're done, provide a brief summary of what you accomplished."
)


class AgentWrapper:
    """Wraps AgenticLoop to match the agent interface expected by BenchmarkRunner."""

    def __init__(self, loop: AgenticLoop):
        self.loop = loop

    def run(self, prompt: str) -> str:
        self.loop.reset()
        return self.loop.run(prompt)


def make_agent_factory(
    model: str,
    api_key: str,
    base_url: str,
    verbose: bool,
    max_iterations: int,
):
    """Create an agent_factory function for BenchmarkRunner."""

    def agent_factory(tools: List[Any], env: SimulatedEnvironment) -> AgentWrapper:
        tool_map = {tool.name: tool for tool in tools}

        wrapper = ConversationWrapper(
            api_key=api_key,
            model=model,
            base_url=base_url if base_url else None,
            verbose=verbose,
            system_prompt=SYSTEM_PROMPT,
        )

        planner = AgenticPlanner(
            conversation_wrapper=wrapper,
            tool_map=tool_map,
            verbose=verbose,
        )

        loop = AgenticLoop(
            conversation_wrapper=wrapper,
            planner=planner,
            tool_map=tool_map,
            verbose=verbose,
            max_iterations=max_iterations,
        )

        return AgentWrapper(loop)

    return agent_factory


def parse_args():
    parser = argparse.ArgumentParser(description="Run procedural workspace benchmark")
    parser.add_argument(
        "--seed", type=int, action="append", default=None,
        help="Random seed(s) for suite generation. Repeat for multiple seeds. Default: 42",
    )
    parser.add_argument("--simple", type=int, default=2, help="Number of SIMPLE tasks (default: 2)")
    parser.add_argument("--medium", type=int, default=2, help="Number of MEDIUM tasks (default: 2)")
    parser.add_argument("--hard", type=int, default=1, help="Number of HARD tasks (default: 1)")
    parser.add_argument("--expert", type=int, default=1, help="Number of EXPERT tasks (default: 1)")
    parser.add_argument("--max-iterations", type=int, default=15, help="Max agent iterations per task (default: 15)")
    parser.add_argument("--verbose", action="store_true", help="Show full execution details")
    parser.add_argument("--output", type=str, default=None, help="Save results JSON to this path")
    return parser.parse_args()


def main():
    args = parse_args()

    # Load config from .env
    model = os.getenv("MODEL")
    api_key = os.getenv("OPENAI_API_KEY")
    base_url = os.getenv("BASE_URL", "")

    if not model:
        print("ERROR: MODEL not set. Fill in your .env file.")
        sys.exit(1)
    if not api_key:
        print("ERROR: OPENAI_API_KEY not set. Fill in your .env file.")
        sys.exit(1)

    seeds = args.seed or [42]
    difficulty_distribution = {
        DifficultyLevel.SIMPLE: args.simple,
        DifficultyLevel.MEDIUM: args.medium,
        DifficultyLevel.HARD: args.hard,
        DifficultyLevel.EXPERT: args.expert,
    }
    total_tasks = sum(difficulty_distribution.values())

    print(f"Model:        {model}")
    print(f"Seeds:        {seeds}")
    print(f"Tasks/seed:   {total_tasks} ({args.simple}S/{args.medium}M/{args.hard}H/{args.expert}E)")
    print(f"Max iters:    {args.max_iterations}")
    print()

    agent_factory = make_agent_factory(
        model=model,
        api_key=api_key,
        base_url=base_url,
        verbose=args.verbose,
        max_iterations=args.max_iterations,
    )

    config = RunConfig(
        model_name=model,
        max_iterations=args.max_iterations,
        verbose=True,
    )

    all_results = {}

    for seed in seeds:
        suite = create_procedural_suite(
            domain="workspace",
            seed=seed,
            difficulty_distribution=difficulty_distribution,
        )

        print(f"{'='*60}")
        print(f"Seed {seed}: {len(suite.tools)} tools, {suite.task_count} tasks")
        print(f"Tools: {', '.join(t.name for t in suite.tools)}")
        print(f"{'='*60}")

        runner = BenchmarkRunner(
            agent_factory=agent_factory,
            verifier_factory=suite.verifier_factory,
            config=config,
        )

        result = runner.run_suite(suite)
        all_results[seed] = result

        print(f"\n--- Seed {seed} Results ---")
        print(f"  Pass rate:     {result.pass_rate:.1%}")
        print(f"  Outcome rate:  {result.outcome_pass_rate:.1%}")
        print(f"  Avg score:     {result.average_score:.2f}")
        print(f"  Avg tool calls: {result.average_tool_calls:.1f}")
        print()

        for tr in result.task_results:
            status = "PASS" if tr.outcome_passed else "FAIL"
            print(f"  [{status}] {tr.task_name} (score: {tr.verification.score:.2f}, tools: {tr.tool_call_count})")

        print()

    # Summary across seeds
    if len(seeds) > 1:
        print(f"{'='*60}")
        print("CROSS-SEED SUMMARY")
        print(f"{'='*60}")
        for seed, result in all_results.items():
            print(f"  Seed {seed:>4}: {result.pass_rate:.1%} pass, {result.outcome_pass_rate:.1%} outcome, {result.average_score:.2f} avg score")

        avg_pass = sum(r.pass_rate for r in all_results.values()) / len(all_results)
        avg_outcome = sum(r.outcome_pass_rate for r in all_results.values()) / len(all_results)
        avg_score = sum(r.average_score for r in all_results.values()) / len(all_results)
        print(f"\n  Average:  {avg_pass:.1%} pass, {avg_outcome:.1%} outcome, {avg_score:.2f} avg score")

    # Save results
    if args.output:
        output_data = {
            "model": model,
            "seeds": seeds,
            "difficulty_distribution": {k.value: v for k, v in difficulty_distribution.items()},
            "timestamp": datetime.now().isoformat(),
            "results": {
                seed: result.to_dict() for seed, result in all_results.items()
            },
        }
        with open(args.output, "w") as f:
            json.dump(output_data, f, indent=2, default=str)
        print(f"\nResults saved to {args.output}")


if __name__ == "__main__":
    main()
