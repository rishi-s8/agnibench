"""
Inspect a procedurally generated benchmark suite.

Shows the generated tool APIs, tasks, environment data, and verifier configs
without running any model.

Usage:
    python inspect_procedural.py                    # seed 42
    python inspect_procedural.py --seed 99          # different seed
    python inspect_procedural.py --seed 42 --seed 99  # compare two seeds side-by-side
    python inspect_procedural.py --tools             # tools only
    python inspect_procedural.py --tasks             # tasks only
    python inspect_procedural.py --data              # environment data only
    python inspect_procedural.py --dag               # show all three DAGs per task
    python inspect_procedural.py --json              # dump full suite as JSON
"""

import argparse
import json
import sys
import textwrap

from agnibench.core.abstractions import DifficultyLevel
from agnibench.procedural import create_procedural_suite


def show_tools(suite, seed):
    print(f"\n{'='*70}")
    print(f"  TOOLS (seed={seed}) — {len(suite.tools)} tools")
    print(f"{'='*70}")

    for i, tool in enumerate(suite.tools, 1):
        props = tool.parameters.get("properties", {})
        required = tool.parameters.get("required", [])

        print(f"\n  [{i}] {tool.name}")
        print(f"      {tool.description}")
        print(f"      Parameters:")
        for pname, pinfo in props.items():
            req = "*" if pname in required else " "
            ptype = pinfo.get("type", "?")
            desc = pinfo.get("description", "")
            default = f" (default: {pinfo['default']})" if "default" in pinfo else ""
            print(f"        {req} {pname}: {ptype} — {desc}{default}")


def show_tasks(suite, seed):
    print(f"\n{'='*70}")
    print(f"  TASKS (seed={seed}) — {suite.task_count} tasks")
    print(f"{'='*70}")

    for task in suite.tasks:
        print(f"\n  [{task.difficulty.value.upper()}] {task.id}")
        print(f"  Name: {task.name}")
        print(f"  Info flow: {task.information_flow.value}")
        print()
        print(f"  Prompt:")
        for line in textwrap.wrap(task.prompt, width=64):
            print(f"    {line}")
        print()
        print(f"  Expected tools: {task.expected_tool_calls}")
        print(f"  Tool calls: {task.min_tool_calls}-{task.max_tool_calls}")
        print()
        print(f"  Verifier config:")
        vc = task.verifier_config
        if "tools" in vc:
            print(f"    tools.required: {vc['tools']['required']}")
            print(f"    tools.calls:    {vc['tools']['min_calls']}-{vc['tools']['max_calls']}")
        if "state" in vc:
            print(f"    state:")
            for key, cond in vc["state"].items():
                print(f"      {key}: {json.dumps(cond, default=str)}")
        if "answer" in vc:
            print(f"    answer keywords: {vc['answer']}")
        print()
        print(f"  DAG metadata:")
        print(f"    dag_id:     {task.metadata.get('dag_id')}")
        print(f"    depth:      {task.metadata.get('dag_depth')}")
        print(f"    breadth:    {task.metadata.get('dag_breadth', 'N/A')}")
        print(f"    tool_calls: {task.metadata.get('tool_call_count')}")

        chars = task.characteristics
        flags = []
        if chars.requires_cross_reference: flags.append("cross_reference")
        if chars.requires_conditional_logic: flags.append("conditional")
        if chars.requires_error_recovery: flags.append("error_recovery")
        if chars.requires_plan_adaptation: flags.append("plan_adaptation")
        if chars.requires_state_tracking: flags.append("state_tracking")
        if chars.requires_long_reasoning_chain: flags.append("long_chain")
        if flags:
            print(f"    requires:   {', '.join(flags)}")

        print(f"  {'-'*50}")


def show_data(suite, seed):
    print(f"\n{'='*70}")
    print(f"  ENVIRONMENT DATA (seed={seed})")
    print(f"{'='*70}")

    env = suite.environment_class()
    env.initialize()
    state = env.state

    print(f"\n  Emails ({len(state.get('emails', []))}):")
    for email in state.get("emails", []):
        read = "read" if email.get("read") else "UNREAD"
        print(f"    [{email['id']}] {email['sender']} — {email['subject']} ({read})")

    print(f"\n  Calendar Events ({len(state.get('calendar_events', []))}):")
    for event in state.get("calendar_events", []):
        attendees = ", ".join(event.get("attendees", []))
        print(f"    [{event['id']}] {event['title']} @ {event.get('start_time', '?')[:16]}")
        if attendees:
            print(f"      attendees: {attendees}")

    print(f"\n  Slack Messages ({len(state.get('slack_messages', []))}):")
    for msg in state.get("slack_messages", []):
        print(f"    [{msg['id']}] {msg['channel']} — {msg['sender']}: {msg['content'][:60]}...")

    print(f"\n  Contacts ({len(state.get('contacts', []))}):")
    for contact in state.get("contacts", []):
        print(f"    [{contact['id']}] {contact['name']} <{contact['email']}> — {contact.get('department', '')}")


def show_dags(suite, seed, output_dir=None):
    print(f"\n{'='*70}")
    print(f"  DAGs (seed={seed}) — {suite.task_count} tasks")
    print(f"{'='*70}")

    # Build archetype_to_surface map from the suite tools
    from agnibench.procedural.workspace_archetypes import ALL_WORKSPACE_ARCHETYPES
    from agnibench.procedural.surface_mutator import mutate_all_tools
    from agnibench.procedural.workspace_impl import WORKSPACE_IMPL_REGISTRY

    _, _, archetype_to_surface = mutate_all_tools(
        archetypes=ALL_WORKSPACE_ARCHETYPES,
        impl_registry=WORKSPACE_IMPL_REGISTRY,
        data_store={},
        seed=seed,
    )

    # Recreate DAG bundles (we need the actual DAG objects)
    from agnibench.procedural.dag_generator import DAGGenerator
    from agnibench.procedural.difficulty import get_profile
    from agnibench.procedural.workspace_archetypes import get_workspace_archetype_set

    archetype_set = get_workspace_archetype_set()
    dag_gen = DAGGenerator(archetype_set, seed=seed)

    # Parse difficulty distribution from task metadata
    from collections import Counter
    diff_counts = Counter(t.difficulty for t in suite.tasks)

    bundles = []
    for difficulty in [DifficultyLevel.SIMPLE, DifficultyLevel.MEDIUM, DifficultyLevel.HARD, DifficultyLevel.EXPERT]:
        count = diff_counts.get(difficulty, 0)
        if count > 0:
            bundles.extend(dag_gen.generate_batch(difficulty, count))

    for i, (bundle, task) in enumerate(zip(bundles, suite.tasks)):
        print(f"\n  --- {task.id} ({task.difficulty.value.upper()}) ---")
        print(f"  Depth: {bundle.depth}  Breadth: {bundle.breadth}  Tool calls: {bundle.tool_call_count}")
        print()

        # Control Flow DAG
        cf = bundle.control_flow
        source_label = "PROMPT" if any(
            n.control_source.value == "prompt" for n in cf.nodes.values()
        ) else "DISCOVERY"
        print(f"  [Control Flow DAG]  (source: {source_label})")
        print(cf.to_ascii(archetype_to_surface))
        print()

        # Data Flow DAG
        print(f"  [Data Flow DAG]")
        print(bundle.data_flow.to_ascii(archetype_to_surface))
        print()

        # Execution DAG
        print(f"  [Execution DAG]")
        print(bundle.execution.to_ascii(archetype_to_surface))
        print()

        # Save DOT files if output_dir specified
        if output_dir:
            import os
            os.makedirs(output_dir, exist_ok=True)

            # Control flow DOT
            cf_path = os.path.join(output_dir, f"{task.id}_cf.dot")
            with open(cf_path, "w") as f:
                f.write(cf.to_dot(archetype_to_surface))
            print(f"  DOT saved: {cf_path}")

            # Data flow DOT
            df_path = os.path.join(output_dir, f"{task.id}_df.dot")
            with open(df_path, "w") as f:
                f.write(bundle.data_flow.to_dot(archetype_to_surface))
            print(f"  DOT saved: {df_path}")

            # Execution DOT
            exec_path = os.path.join(output_dir, f"{task.id}_exec.dot")
            with open(exec_path, "w") as f:
                f.write(bundle.execution.to_dot(archetype_to_surface))
            print(f"  DOT saved: {exec_path}")

    if output_dir:
        print(f"\n  Render DOT files with: dot -Tpng <file>.dot -o <file>.png")
        print(f"  Or paste into: https://dreampuf.github.io/GraphvizOnline/")


def show_comparison(seeds, difficulty_distribution):
    suites = {}
    for seed in seeds:
        suites[seed] = create_procedural_suite(
            "workspace", seed=seed, difficulty_distribution=difficulty_distribution,
        )

    print(f"\n{'='*70}")
    print(f"  SEED COMPARISON: {' vs '.join(str(s) for s in seeds)}")
    print(f"{'='*70}")

    # Compare tool names
    print(f"\n  Tool name mapping across seeds:")
    print(f"  {'Archetype':<22}", end="")
    for seed in seeds:
        print(f"  seed={seed:<16}", end="")
    print()
    print(f"  {'-'*22}", end="")
    for _ in seeds:
        print(f"  {'-'*20}", end="")
    print()

    # Get archetype order from first suite
    from agnibench.procedural.workspace_archetypes import ALL_WORKSPACE_ARCHETYPES
    archetype_ids = [a.archetype_id for a in ALL_WORKSPACE_ARCHETYPES]

    for i, arch_id in enumerate(archetype_ids):
        print(f"  {arch_id:<22}", end="")
        for seed in seeds:
            tool = suites[seed].tools[i]
            print(f"  {tool.name:<20}", end="")
        print()

    # Compare a sample task prompt
    print(f"\n  Sample task prompt (first MEDIUM):")
    for seed in seeds:
        suite = suites[seed]
        medium_tasks = suite.get_tasks_by_difficulty(DifficultyLevel.MEDIUM)
        if medium_tasks:
            print(f"\n    seed={seed}:")
            for line in textwrap.wrap(medium_tasks[0].prompt, width=60):
                print(f"      {line}")


def main():
    parser = argparse.ArgumentParser(description="Inspect procedural benchmark suite")
    parser.add_argument("--seed", type=int, action="append", default=None, help="Seed(s) to inspect")
    parser.add_argument("--tools", action="store_true", help="Show tools only")
    parser.add_argument("--tasks", action="store_true", help="Show tasks only")
    parser.add_argument("--data", action="store_true", help="Show environment data only")
    parser.add_argument("--dag", action="store_true", help="Show DAG visualizations")
    parser.add_argument("--dag-output", type=str, default=None, help="Save DOT files to this directory")
    parser.add_argument("--json", action="store_true", help="Dump full suite as JSON")
    parser.add_argument("--simple", type=int, default=2)
    parser.add_argument("--medium", type=int, default=2)
    parser.add_argument("--hard", type=int, default=1)
    parser.add_argument("--expert", type=int, default=1)
    args = parser.parse_args()

    seeds = args.seed or [42]
    show_all = not (args.tools or args.tasks or args.data or args.dag or args.json)

    difficulty_distribution = {
        DifficultyLevel.SIMPLE: args.simple,
        DifficultyLevel.MEDIUM: args.medium,
        DifficultyLevel.HARD: args.hard,
        DifficultyLevel.EXPERT: args.expert,
    }

    # Side-by-side comparison for multiple seeds
    if len(seeds) > 1:
        show_comparison(seeds, difficulty_distribution)
        print()

    for seed in seeds:
        suite = create_procedural_suite(
            "workspace", seed=seed, difficulty_distribution=difficulty_distribution,
        )

        if args.json:
            print(json.dumps(suite.to_dict(), indent=2, default=str))
            continue

        if show_all or args.tools:
            show_tools(suite, seed)
        if show_all or args.tasks:
            show_tasks(suite, seed)
        if show_all or args.data:
            show_data(suite, seed)
        if args.dag:
            show_dags(suite, seed, output_dir=args.dag_output)

    print()


if __name__ == "__main__":
    main()
