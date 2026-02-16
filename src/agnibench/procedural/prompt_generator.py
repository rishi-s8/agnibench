"""
Prompt generator that converts a TaskDAG + entity_bindings into
natural language task prompts.

Two-stage: template-based generation + optional LLM polish.
"""

import hashlib
import json
import os
import random
from typing import Any, Dict, List, Optional

from agnibench.procedural.archetypes import DomainArchetypeSet
from agnibench.procedural.dag import NodeType, TaskDAG

# Intent classification: maps terminal archetype_id -> intent
_TERMINAL_INTENTS = {
    "send_email": "reply_to_email",
    "create_event": "schedule_meeting",
    "send_slack": "send_slack_message",
    "lookup_contact": "find_contact_info",
    "search_emails": "find_emails",
    "read_email": "read_specific_email",
    "search_calendar": "check_schedule",
    "check_availability": "check_availability",
    "search_slack": "find_slack_messages",
    "web_search": "research_topic",
}

# Intent -> list of prompt templates
# Templates use {entity} placeholders filled from entity_bindings
_PROMPT_TEMPLATES: Dict[str, List[str]] = {
    "reply_to_email": [
        "Find the email from {primary_person_name} about {topic} and reply saying {reply_content}.",
        "Look up the message from {primary_person_name} regarding {topic}, then send a reply with {reply_content}.",
        "Search for {primary_person_name}'s email about {topic} and respond to it saying {reply_content}.",
    ],
    "schedule_meeting": [
        "Schedule a meeting about {topic} with {primary_person_name}. Find a time that works and create the event.",
        "Set up a {topic} meeting with {primary_person_name}. Check their availability first, then book it.",
        "Organize a meeting for {topic} with {primary_person_name} tomorrow. Create the calendar event.",
    ],
    "send_slack_message": [
        "Send a message to {slack_channel} about the {topic} update.",
        "Post an update about {topic} to the {slack_channel} Slack channel.",
        "Notify {slack_channel} about the latest {topic} developments.",
    ],
    "find_contact_info": [
        "Find {primary_person_name}'s contact information and email them about {topic}.",
        "Look up {primary_person_name} in the directory and send them a message about {topic}.",
        "Get {primary_person_name}'s email address and reach out regarding {topic}.",
    ],
    "find_emails": [
        "Search for emails about {topic} from the past week.",
        "Find all messages related to {topic}.",
        "Look through your inbox for emails about {topic}.",
    ],
    "read_specific_email": [
        "Read the latest email from {primary_person_name} about {topic}.",
        "Open the message from {primary_person_name} regarding {topic}.",
        "Check the email from {primary_person_name} about {topic}.",
    ],
    "check_schedule": [
        "Check the calendar for any {topic} meetings this week.",
        "Look up upcoming events related to {topic}.",
        "Find calendar events about {topic}.",
    ],
    "check_availability": [
        "Check when {primary_person_name} is free tomorrow for a {topic} meeting.",
        "Find available time slots for a meeting with {primary_person_name} about {topic}.",
        "Look up {primary_person_name}'s availability for a {topic} discussion.",
    ],
    "find_slack_messages": [
        "Search Slack for recent messages about {topic}.",
        "Find Slack discussions related to {topic}.",
        "Look for {topic} updates in Slack.",
    ],
    "research_topic": [
        "Search the web for information about {topic}.",
        "Find online resources about {topic}.",
        "Research {topic} using web search.",
    ],
}

# Multi-step combination templates for complex tasks
_MULTI_STEP_TEMPLATES = [
    "First, {step1}. Then, {step2}.",
    "{step1}. After that, {step2}.",
    "I need you to {step1} and then {step2}.",
    "{step1}. Once done, {step2}.",
]

# Reply content variants
_REPLY_CONTENTS = [
    "I can meet tomorrow afternoon",
    "let's schedule the meeting for this week",
    "I've reviewed the proposal and have some feedback",
    "sounds good, I'll prepare the materials",
    "I'll follow up with the team on this",
    "let me check with the team and get back to you",
    "thanks for the update, I'll look into it",
]


class PromptGenerator:
    """
    Converts a TaskDAG + entity_bindings into a natural language prompt.

    Stage 1 (always): Template-based generation
    Stage 2 (optional): LLM polish for naturalness
    """

    def __init__(
        self,
        archetype_set: DomainArchetypeSet,
        seed: int,
        llm_polish: bool = False,
        cache_dir: Optional[str] = None,
    ):
        self.archetype_set = archetype_set
        self.rng = random.Random(seed)
        self.seed = seed
        self.llm_polish = llm_polish
        self.cache_dir = cache_dir
        self._cache: Dict[str, str] = {}

        if cache_dir and os.path.exists(cache_dir):
            cache_file = os.path.join(cache_dir, f"prompt_cache_{seed}.json")
            if os.path.exists(cache_file):
                with open(cache_file, "r") as f:
                    self._cache = json.load(f)

    def _classify_intent(self, dag: TaskDAG) -> str:
        """Classify the task intent from terminal nodes."""
        terminal_tool_nodes = dag.get_terminal_tool_nodes()
        if not terminal_tool_nodes:
            return "find_emails"  # Default fallback

        # Use the last terminal tool call as primary intent
        terminal = terminal_tool_nodes[-1]
        return _TERMINAL_INTENTS.get(terminal.archetype_id, "find_emails")

    def _fill_template(self, template: str, bindings: Dict[str, Any]) -> str:
        """Fill a template with entity bindings."""
        replacements = {
            "primary_person_name": bindings.get("primary_person", {}).get("name", "the sender"),
            "primary_person_email": bindings.get("primary_person", {}).get("email", ""),
            "topic": bindings.get("topic", "the project"),
            "slack_channel": bindings.get("slack_channel", "#general"),
            "reply_content": self.rng.choice(_REPLY_CONTENTS),
            "reply_subject": bindings.get("reply_subject", f"Re: {bindings.get('topic', 'Update')}"),
        }

        result = template
        for key, value in replacements.items():
            result = result.replace(f"{{{key}}}", str(value))
        return result

    def _dag_structure_hash(self, dag: TaskDAG) -> str:
        """Hash the DAG structure for caching."""
        structure = {
            "tool_calls": [
                n.archetype_id
                for n in dag.get_tool_call_nodes()
            ],
            "edges": [
                (e.source_node_id, e.target_node_id, e.edge_type.value)
                for e in dag.edges
            ],
        }
        return hashlib.md5(json.dumps(structure, sort_keys=True).encode()).hexdigest()

    def generate(self, dag: TaskDAG, entity_bindings: Dict[str, Any]) -> str:
        """
        Generate a natural language prompt from a DAG and entity bindings.

        Args:
            dag: The task DAG
            entity_bindings: Maps abstract roles to concrete values

        Returns:
            Natural language task prompt string
        """
        # Check cache
        cache_key = f"{self._dag_structure_hash(dag)}_{self.seed}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        intent = self._classify_intent(dag)

        # Get templates for this intent
        templates = _PROMPT_TEMPLATES.get(intent, _PROMPT_TEMPLATES["find_emails"])
        template = self.rng.choice(templates)
        prompt = self._fill_template(template, entity_bindings)

        # For multi-step tasks, combine multiple intent prompts
        tool_nodes = dag.get_tool_call_nodes()
        if len(tool_nodes) > 3:
            # Build a multi-step prompt
            steps = []
            seen_intents = set()

            for node in tool_nodes:
                node_intent = _TERMINAL_INTENTS.get(node.archetype_id, None)
                if node_intent and node_intent not in seen_intents:
                    node_templates = _PROMPT_TEMPLATES.get(node_intent, [])
                    if node_templates:
                        step = self._fill_template(self.rng.choice(node_templates), entity_bindings)
                        steps.append(step.rstrip("."))
                        seen_intents.add(node_intent)

            if len(steps) >= 2:
                combo_template = self.rng.choice(_MULTI_STEP_TEMPLATES)
                prompt = combo_template.format(
                    step1=steps[0].lower(),
                    step2=steps[-1].lower(),
                )

        # Cache the result
        self._cache[cache_key] = prompt

        # Save cache if cache_dir is set
        if self.cache_dir:
            os.makedirs(self.cache_dir, exist_ok=True)
            cache_file = os.path.join(self.cache_dir, f"prompt_cache_{self.seed}.json")
            with open(cache_file, "w") as f:
                json.dump(self._cache, f, indent=2)

        return prompt
