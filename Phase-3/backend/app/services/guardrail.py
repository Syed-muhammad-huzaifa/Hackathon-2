"""
Input guardrail — restricts the agent to todo/task-management queries only.
Uses a lightweight classification agent to decide if the input is on-topic.
@spec: specs/001-chatbot-backend/spec.md (NFR-guardrail)
"""
import logging
import re
from pydantic import BaseModel
from openai import AsyncOpenAI
from agents import (
    Agent,
    GuardrailFunctionOutput,
    RunContextWrapper,
    Runner,
    TResponseInputItem,
    input_guardrail,
)
from agents.models.openai_chatcompletions import OpenAIChatCompletionsModel

from app.core.config import settings

logger = logging.getLogger(__name__)

# ── Classification schema ──────────────────────────────────────
class TodoRelevanceCheck(BaseModel):
    is_todo_related: bool
    reasoning: str


# ── Dedicated client + model for the guardrail agent ──────────
# Intentionally separate from the main _grok_client to avoid
# sharing state between the guardrail run and the main agent run.
_guardrail_client = AsyncOpenAI(
    base_url=settings.GROK_BASE_URL,
    api_key=settings.GROK_API_KEY,
)

_guardrail_model = OpenAIChatCompletionsModel(
    model=settings.GROK_MODEL,
    openai_client=_guardrail_client,
)

# ── Guardrail agent ────────────────────────────────────────────
_guardrail_agent = Agent(
    name="Topic Classifier",
    instructions=(
        "You classify whether a user message is related to task or to-do list management. "
        "Return is_todo_related=true ONLY when the message explicitly concerns managing a "
        "personal task or to-do list (create, list, complete, delete, update, view tasks). "
        "Everything else is off-topic, including greetings, chit-chat, math, coding help, "
        "writing essays, weather, news, cooking, and general knowledge questions. "
        "When in doubt, set is_todo_related=false."
    ),
    output_type=TodoRelevanceCheck,
    model=_guardrail_model,
)

# ── Refusal message ────────────────────────────────────────────
REFUSAL_MESSAGE = (
    "I'm a task management assistant and can only help you with your to-do list.\n\n"
    "Here's what I can do for you:\n"
    "• **Add a task** — \"Add task: buy groceries\"\n"
    "• **List your tasks** — \"Show my tasks\"\n"
    "• **Complete a task** — \"Mark task <id> as done\"\n"
    "• **Delete a task** — \"Delete task <id>\"\n"
    "• **Update a task** — \"Rename task <id> to '...'\"\n\n"
    "Please ask me something related to your tasks!"
)


# ── Guardrail function ─────────────────────────────────────────
@input_guardrail
async def todo_only_guardrail(
    ctx: RunContextWrapper[None],
    agent: Agent,
    input: str | list[TResponseInputItem],
) -> GuardrailFunctionOutput:
    """
    Blocks any input that is not related to task/todo management.
    Extracts the most recent user message for classification.
    """
    if isinstance(input, str):
        user_text = input
    else:
        # input is a list of messages — grab the last user turn
        user_text = ""
        for item in reversed(input):
            if isinstance(item, dict) and item.get("role") == "user":
                content = item.get("content", "")
                user_text = content if isinstance(content, str) else str(content)
                break

    user_text = user_text.strip()
    if not user_text:
        # Empty input — let the agent handle it gracefully
        return GuardrailFunctionOutput(output_info=None, tripwire_triggered=False)

    # Fast-path allowlist for obvious task commands (avoid LLM misclassifying)
    lowered = user_text.lower()
    task_keywords = (
        "task", "tasks", "todo", "to-do", "to do", "reminder", "remind",
    )
    command_verbs = (
        "add", "create", "remember", "remind", "list", "show", "view",
        "complete", "finish", "done", "delete", "remove", "update", "rename",
        "change", "edit", "mark",
    )
    starts_with_command = bool(
        re.match(r"^(add|create|remember|remind|list|show|view|complete|finish|delete|remove|update|rename|change|edit|mark)\b", lowered)
    )
    has_task_keyword = any(k in lowered for k in task_keywords)
    if starts_with_command or has_task_keyword:
        return GuardrailFunctionOutput(output_info=None, tripwire_triggered=False)

    try:
        result = await Runner.run(_guardrail_agent, user_text, context=ctx.context)
        check: TodoRelevanceCheck = result.final_output
        logger.info(
            "Guardrail: is_todo_related=%s reason=%s input=%.60s",
            check.is_todo_related,
            check.reasoning,
            user_text,
        )
        return GuardrailFunctionOutput(
            output_info=check,
            tripwire_triggered=not check.is_todo_related,
        )
    except Exception as e:
        # On guardrail failure, fail closed (block to avoid off-topic answers)
        logger.error("Guardrail classification failed, failing closed: %s", e)
        return GuardrailFunctionOutput(output_info=None, tripwire_triggered=True)
