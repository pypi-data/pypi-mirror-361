"""
Erdo Agent SDK - Agent Example

This example demonstrates the key features of Erdo agents:
- Creating agents with clear purposes
- Using the .exec decorator for code execution
- Chaining steps with dependencies
- Handling results with conditions
- Clean state access and templating
"""

from erdo import Agent, state
from erdo.actions import memory, utils, llm
from erdo.conditions import IsSuccess, GreaterThan
from erdo.types import PythonFile


# ============================================================================
# DATA ANALYZER AGENT
# ============================================================================

data_analyzer = Agent(
    name="data analyzer",
    description="Analyzes data files and provides insights",
    running_message="Analyzing data...",
    finished_message="Analysis complete",
)

# Step 1: Search for relevant context
search_step = data_analyzer.step(
    memory.search(
        query=state.query, organization_scope="specific", limit=5, max_distance=0.8
    )
)

# Step 2: Analyze the data with AI
analyze_step = data_analyzer.step(
    llm.message(
        model="claude-sonnet-4-20250514",
        system_prompt="You are a data analyst. Analyze the data and provide insights based on the user's query.",
        query=state.query,
        context=search_step.output.memories,
        response_format={
            "Type": "json_schema",
            "Schema": {
                "type": "object",
                "required": ["insights", "confidence", "recommendations"],
                "properties": {
                    "insights": {"type": "string", "description": "Key insights found"},
                    "confidence": {"type": "number", "description": "Confidence 0-1"},
                    "recommendations": {"type": "array", "items": {"type": "string"}},
                },
            },
        },
    ),
    depends_on=search_step,
)


# Step 3: Execute detailed analysis with code
@data_analyzer.exec(
    code_files=[
        PythonFile(filename="analysis_files/analyze.py"),
        PythonFile(filename="analysis_files/utils.py"),
    ]
)
def execute_analysis():
    """Execute detailed analysis using external code files."""
    from analysis_files.analyze import analyze_data
    from analysis_files.utils import prepare_data, validate_results

    # Prepare the data for analysis
    prepared_data = prepare_data(context.parameters.get("dataset", {}))

    # Run the main analysis
    results = analyze_data(context)

    # Validate and enhance results
    validated_results = validate_results(results, prepared_data)

    return validated_results


# Store high-confidence results
analyze_step.on(
    IsSuccess() & GreaterThan("confidence", "0.8"),
    memory.store(
        memory={
            "content": analyze_step.output.insights,
            "description": "High-confidence data analysis results",
            "type": "analysis",
            "tags": ["analysis", "high-confidence"],
            "extra": {
                "query": state.query,
                "recommendations": analyze_step.output.recommendations,
            },
        }
    ),
)

# Execute detailed analysis for high-confidence results
analyze_step.on(IsSuccess() & GreaterThan("confidence", "0.8"), execute_analysis)

# Send status for low confidence results
analyze_step.on(
    IsSuccess() & GreaterThan("confidence", "0.3") & ~GreaterThan("confidence", "0.8"),
    utils.send_status(
        message="Analysis completed with medium confidence. Review recommended.",
        status="review_needed",
        data=analyze_step.output,
    ),
)


# ============================================================================
# DEMO FUNCTION
# ============================================================================


def show_example():
    """Show what this agent can do."""
    print("🚀 Erdo Agent SDK - Data Analyzer Example")
    print("=" * 50)

    print("\n📊 Data Analyzer Agent:")
    print("  • Analyzes data based on user queries")
    print("  • Searches memory for relevant context")
    print("  • Uses AI to generate insights")
    print("  • Executes detailed analysis code with .exec decorator")
    print("  • Uses multiple code files (analyze.py + utils.py)")
    print("  • Stores high-confidence results automatically")
    print("  • Handles different confidence levels appropriately")

    print("\n✨ Key Features Demonstrated:")
    print("  • agent.step() - Create workflow steps")
    print("  • @agent.exec() - Execute code with external files")
    print("  • step.on() - Handle results with conditions")
    print("  • state.query - Access input data")
    print("  • Condition operators: & (and), ~ (not)")
    print("  • Memory storage and search")
    print("  • AI-powered analysis")
    print("  • Multi-file code execution")

    print("\n🎯 Usage:")
    print("  erdo sync  # Sync this agent")
    print("  # Then use it in your Erdo workflows!")


# Export agents for sync
agents = [data_analyzer]

if __name__ == "__main__":
    show_example()
