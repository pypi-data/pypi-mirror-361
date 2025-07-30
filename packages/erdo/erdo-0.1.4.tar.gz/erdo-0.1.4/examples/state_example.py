"""
Example agent demonstrating the new state syntax.

This agent shows how to use state.field references in parameters,
conditions, and f-strings. When synced, these will be converted to
Go template strings automatically.
"""

from erdo import Agent, state, setup_test_state
from erdo.actions import llm, memory, utils
from erdo.conditions import IsSuccess, GreaterThan

# Setup test state for local development
setup_test_state(
    code="print('hello world')",
    dataset={"id": "dataset123", "config": {"type": "csv", "columns": ["name", "age"]}},
    query="analyze this code for security issues",
    context="security analysis request",
    user={"id": "user123", "name": "Alice"},
)

# Create the agent
security_analyzer = Agent(
    name="security_analyzer_with_state",
    description=f"Analyzes code for security issues. Current user: {state.user.name}",
    persona=f"You are a security expert analyzing {state.dataset.config.type} data.",
)

# Step 1: Extract context about the code
context_step = security_analyzer.step(
    utils.echo(message=f"Starting security analysis for: {state.code}")
)

# Step 2: Analyze the code with LLM
analyze_step = security_analyzer.step(
    llm.message(
        system_prompt="You are a security expert. Analyze code for vulnerabilities.",
        query=f"Analyze this code for security issues: {state.code}",
        context=f"Dataset type: {state.dataset.config.type}, User query: {state.query}",
    ),
    depends_on=context_step,
)

# Step 3: Search memory for similar vulnerabilities
search_step = security_analyzer.step(
    memory.search(
        query=f"security vulnerabilities in {state.dataset.config.type} processing",
        limit=5,
    ),
    depends_on=analyze_step,
)

# Step 4: Generate final report
report_step = security_analyzer.step(
    llm.message(
        system_prompt="Generate a comprehensive security report.",
        query=f"Based on analysis of '{state.code}' and similar cases, create a security report",
        context=f"Analysis: {analyze_step.output.content}, Similar cases: {search_step.output.results}",
    ),
    depends_on=[analyze_step, search_step],
)


# Result handlers with state references
analyze_step.on(
    IsSuccess() & GreaterThan("confidence", "0.8"),
    utils.echo(message=f"High confidence analysis for {state.user.name}"),
)

search_step.on(
    IsSuccess(),
    utils.echo(message=f"Found similar cases for dataset {state.dataset.id}"),
)


# Export for sync
agents = [security_analyzer]
