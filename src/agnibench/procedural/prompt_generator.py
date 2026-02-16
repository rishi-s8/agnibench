"""
Prompt generator that converts a TaskDAGBundle + entity_bindings into
natural language task prompts.

Information-flow-aware:
- PROMPT_FULL: Explicit step-by-step instructions with data values
- PROMPT_CONTROL_TOOL_DATA: Explicit steps but data must be discovered via tools
- TOOL_DISCOVERY: Vague goal only, agent must discover both steps and data

Two-stage: template-based generation + optional LLM polish.
"""

import hashlib
import json
import os
import random
from typing import Any, Dict, List, Optional

from agnibench.core.abstractions import InformationFlow
from agnibench.procedural.archetypes import DomainArchetypeSet
from agnibench.procedural.dag import ControlSource, NodeType, TaskDAG, TaskDAGBundle

# Maps archetype_id -> intent label
_ARCHETYPE_INTENTS = {
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

# --- PROMPT_FULL templates: explicit steps + explicit data ---
_FULL_TEMPLATES: Dict[str, List[str]] = {
    "reply_to_email": [
        "Find the email from {primary_person_name} about {topic} and reply saying {reply_content}.",
        "Search for {primary_person_name}'s email about {topic} and respond to it saying {reply_content}.",
    ],
    "schedule_meeting": [
        "Check {primary_person_name}'s availability tomorrow, then schedule a {topic} meeting with them.",
        "Find a free slot for {primary_person_name} and create a {topic} meeting.",
    ],
    "send_slack_message": [
        "Send a message to {slack_channel} saying there's an update on {topic}.",
        "Post to {slack_channel} about the {topic} update.",
    ],
    "find_contact_info": [
        "Look up {primary_person_name}'s contact details in the directory.",
        "Find {primary_person_name}'s email address and phone number.",
    ],
    "find_emails": [
        "Search for emails about {topic} from {primary_person_name}.",
        "Find messages related to {topic} in your inbox.",
    ],
    "read_specific_email": [
        "Read the email from {primary_person_name} about {topic}.",
        "Open {primary_person_name}'s message regarding {topic} and read the full content.",
    ],
    "check_schedule": [
        "Check the calendar for {topic} meetings involving {primary_person_name}.",
        "Look up upcoming {topic} events on the calendar.",
    ],
    "check_availability": [
        "Check when {primary_person_name} is free tomorrow for a {topic} meeting.",
        "Find available time slots for {primary_person_name} tomorrow.",
    ],
    "find_slack_messages": [
        "Search Slack for messages about {topic} in {slack_channel}.",
        "Find recent {topic} discussions in Slack.",
    ],
    "research_topic": [
        "Search the web for information about {topic}.",
        "Research {topic} online.",
    ],
}

# --- PROMPT_CONTROL_TOOL_DATA templates: explicit steps, data from tools ---
_CONTROL_TEMPLATES: Dict[str, List[str]] = {
    "reply_to_email": [
        "Find the latest unread email from {primary_person_name} and reply to it with {reply_content}.",
        "Look up {primary_person_name}'s most recent message and send a reply saying {reply_content}.",
    ],
    "schedule_meeting": [
        "Check {primary_person_name}'s availability and schedule a follow-up meeting about {topic}.",
        "Find when {primary_person_name} is free and book a {topic} meeting.",
    ],
    "send_slack_message": [
        "Post an update about {topic} to the appropriate Slack channel.",
        "Send a Slack message about {topic} to {slack_channel}.",
    ],
    "find_contact_info": [
        "Look up {primary_person_name}'s contact information.",
        "Find {primary_person_name} in the company directory.",
    ],
    "find_emails": [
        "Search for recent emails about {topic}.",
        "Find emails related to {topic}.",
    ],
    "read_specific_email": [
        "Find and read the email about {topic} from {primary_person_name}.",
        "Look up the message from {primary_person_name} about {topic} and read it.",
    ],
    "check_schedule": [
        "Check the calendar for any upcoming {topic} events.",
        "Look up {topic}-related meetings on the calendar.",
    ],
    "check_availability": [
        "Check {primary_person_name}'s calendar availability for tomorrow.",
        "Find when {primary_person_name} has free time.",
    ],
    "find_slack_messages": [
        "Search Slack for recent discussions about {topic}.",
        "Check Slack for any {topic} updates.",
    ],
    "research_topic": [
        "Search the web for background on {topic}.",
        "Do some online research about {topic}.",
    ],
}

# --- TOOL_DISCOVERY goal templates: vague goals, agent discovers everything ---
_GOAL_TEMPLATES = [
    "Handle all the {topic} follow-ups — make sure the right people are informed, meetings are scheduled if needed, and any pending replies are sent.",
    "Take care of everything related to {topic}. Check emails, look at the calendar, coordinate with the team, and make sure nothing falls through the cracks.",
    "I need you to manage the {topic} situation end-to-end. Read any relevant messages, check schedules, reach out to the right people, and keep the team updated.",
    "Deal with the {topic} items on my plate. Review what's come in, respond where needed, schedule what needs scheduling, and update the team.",
    "Process all outstanding {topic} items — emails, meetings, Slack updates, the works. Use your best judgment on what needs to happen.",
    "Follow up on {topic}. Figure out what needs attention, who needs to hear back, and whether any meetings need to be set up. Handle it all.",
]

# Step connectors for multi-step FULL/CONTROL prompts
_STEP_CONNECTORS = [
    "{prev}. Then, {next}.",
    "{prev}. After that, {next}.",
    "{prev}. Next, {next}.",
    "{prev}, then {next}.",
    "{prev}. Once that's done, {next}.",
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
    Converts a TaskDAGBundle + entity_bindings into a natural language prompt.

    Varies prompt style based on information_flow:
    - PROMPT_FULL: Lists all steps with concrete data values
    - PROMPT_CONTROL_TOOL_DATA: Lists steps, but data comes from tools
    - TOOL_DISCOVERY: Gives only a high-level goal
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

    def _bundle_structure_hash(self, bundle: TaskDAGBundle) -> str:
        """Hash the bundle structure (control_flow + data_flow) for caching."""
        structure = {
            "control_flow_nodes": [
                (n.node_id, n.archetype_id, n.control_source.value)
                for n in bundle.control_flow.get_topological_order()
            ],
            "control_flow_edges": [
                (e.source_node_id, e.target_node_id, e.control_source.value)
                for e in bundle.control_flow.edges
            ],
            "data_flow_nodes": sorted([
                (n.node_id, n.node_type.value, n.data_source.value)
                for n in bundle.data_flow.nodes.values()
            ]),
            "data_flow_edges": [
                (e.source_node_id, e.target_node_id, e.data_source.value)
                for e in bundle.data_flow.edges
            ],
        }
        return hashlib.md5(json.dumps(structure, sort_keys=True).encode()).hexdigest()

    def _get_distinct_intents(self, bundle: TaskDAGBundle) -> List[str]:
        """
        Get distinct intent labels from the control flow DAG, preserving
        topological order. Only include nodes whose control_source == PROMPT.
        """
        seen = set()
        intents = []
        for node in bundle.control_flow.get_topological_order():
            if node.control_source != ControlSource.PROMPT:
                continue
            intent = _ARCHETYPE_INTENTS.get(node.archetype_id)
            if intent and intent not in seen:
                seen.add(intent)
                intents.append(intent)
        return intents

    def _generate_full_prompt(self, bundle: TaskDAGBundle, bindings: Dict[str, Any]) -> str:
        """Generate a PROMPT_FULL prompt: explicit steps with data values."""
        intents = self._get_distinct_intents(bundle)

        if not intents:
            return self._fill_template("Handle {topic} tasks.", bindings)

        if len(intents) == 1:
            templates = _FULL_TEMPLATES.get(intents[0], ["{topic} task."])
            return self._fill_template(self.rng.choice(templates), bindings)

        # Multi-step: enumerate ALL distinct actions
        steps = []
        for intent in intents:
            templates = _FULL_TEMPLATES.get(intent, [])
            if templates:
                step = self._fill_template(self.rng.choice(templates), bindings)
                steps.append(step)

        return self._chain_steps(steps)

    def _generate_control_prompt(self, bundle: TaskDAGBundle, bindings: Dict[str, Any]) -> str:
        """Generate a PROMPT_CONTROL_TOOL_DATA prompt: explicit steps, data from tools."""
        intents = self._get_distinct_intents(bundle)

        if not intents:
            return self._fill_template("Handle the {topic} follow-ups.", bindings)

        if len(intents) == 1:
            templates = _CONTROL_TEMPLATES.get(intents[0], ["{topic} task."])
            return self._fill_template(self.rng.choice(templates), bindings)

        # Multi-step: enumerate ALL distinct actions
        steps = []
        for intent in intents:
            templates = _CONTROL_TEMPLATES.get(intent, [])
            if templates:
                step = self._fill_template(self.rng.choice(templates), bindings)
                steps.append(step)

        return self._chain_steps(steps)

    def _generate_discovery_prompt(self, bundle: TaskDAGBundle, bindings: Dict[str, Any]) -> str:
        """Generate a TOOL_DISCOVERY prompt: vague goal, agent discovers everything."""
        template = self.rng.choice(_GOAL_TEMPLATES)
        return self._fill_template(template, bindings)

    def _chain_steps(self, steps: List[str]) -> str:
        """Chain multiple step descriptions into a coherent multi-step prompt."""
        if not steps:
            return ""
        if len(steps) == 1:
            return steps[0]

        # Build up the chain incrementally
        result = steps[0].rstrip(".")
        for step in steps[1:]:
            connector = self.rng.choice(_STEP_CONNECTORS)
            next_text = step[0].lower() + step[1:] if step else step
            # Strip all trailing periods from both sides before joining
            result = connector.format(
                prev=result.rstrip("."),
                next=next_text.rstrip("."),
            )

        # Clean up: ensure exactly one trailing period, no doubles anywhere
        result = result.replace("..", ".").replace("..", ".").rstrip(".") + "."
        return result

    def generate(
        self,
        bundle: TaskDAGBundle,
        entity_bindings: Dict[str, Any],
        information_flow: InformationFlow = InformationFlow.PROMPT_FULL,
    ) -> str:
        """
        Generate a natural language prompt from a DAG bundle and entity bindings.

        Args:
            bundle: The TaskDAGBundle containing control flow, data flow, and execution DAGs
            entity_bindings: Maps abstract roles to concrete values
            information_flow: Controls how much the prompt reveals

        Returns:
            Natural language task prompt string
        """
        # Check cache
        cache_key = f"{self._bundle_structure_hash(bundle)}_{self.seed}_{information_flow.value}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        if information_flow == InformationFlow.PROMPT_FULL:
            prompt = self._generate_full_prompt(bundle, entity_bindings)
        elif information_flow == InformationFlow.PROMPT_CONTROL_TOOL_DATA:
            prompt = self._generate_control_prompt(bundle, entity_bindings)
        else:  # TOOL_DISCOVERY
            prompt = self._generate_discovery_prompt(bundle, entity_bindings)

        # Cache the result
        self._cache[cache_key] = prompt

        if self.cache_dir:
            os.makedirs(self.cache_dir, exist_ok=True)
            cache_file = os.path.join(self.cache_dir, f"prompt_cache_{self.seed}.json")
            with open(cache_file, "w") as f:
                json.dump(self._cache, f, indent=2)

        return prompt
