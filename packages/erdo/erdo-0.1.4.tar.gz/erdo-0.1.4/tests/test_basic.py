"""Basic tests for the Erdo Agent SDK."""

import pytest

def test_erdo_import():
    """Test that the main erdo module can be imported."""
    import erdo
    assert hasattr(erdo, '__version__')
    assert hasattr(erdo, 'state')

def test_agent_creation():
    """Test that we can create an Agent like in the examples."""
    from erdo import Agent, state
    
    # Create an agent like in agent_centric_example.py
    test_agent = Agent(
        name="test analyzer",
        description="Test agent for unit tests",
        running_message="Running test...",
        finished_message="Test complete",
    )
    
    # Verify agent properties
    assert test_agent.name == "test analyzer"
    assert test_agent.description == "Test agent for unit tests"
    assert test_agent.running_message == "Running test..."
    assert test_agent.finished_message == "Test complete"

def test_agent_step_creation():
    """Test that we can create steps on agents."""
    from erdo import Agent, state
    from erdo.actions import memory
    
    agent = Agent(name="test_agent")
    
    # Create a step
    step = agent.step(
        memory.search(
            query=state.query, 
            organization_scope="specific", 
            limit=5
        )
    )
    
    # Verify step was created
    assert step is not None

def test_agent_with_execution_mode():
    """Test agent with execution modes like in real agents."""
    from erdo import Agent, ExecutionMode, ExecutionModeType
    from erdo.actions import bot
    from erdo.conditions import IsSuccess
    from erdo.template import TemplateString
    
    agent = Agent(name="test_agent")
    
    # Create a step with execution mode
    step = agent.step(
        action=bot.invoke(
            bot_name="test_bot",
            parameters={"resource": TemplateString("{{resources}}")},
        ),
        key="test_step",
        execution_mode=ExecutionMode(
            mode=ExecutionModeType.ITERATE_OVER,
            data="parameters.resource",
        )
    )
    
    assert step is not None

def test_prompt_loading():
    """Test that Prompt class can load prompts."""
    from erdo import Prompt
    
    # This will fail if prompts directory doesn't exist, but that's expected
    # Just test that the method exists
    assert hasattr(Prompt, 'load_from_directory')

def test_core_types():
    """Test that core types can be imported and instantiated."""
    from erdo.types import PythonFile
    from erdo import ExecutionMode, ExecutionModeType, OutputVisibility
    
    # Test PythonFile creation
    py_file = PythonFile(filename="test.py")
    assert py_file.filename == "test.py"
    
    # Test ExecutionMode
    exec_mode = ExecutionMode(
        mode=ExecutionModeType.ITERATE_OVER,
        data="test.data"
    )
    assert exec_mode.mode == ExecutionModeType.ITERATE_OVER
    assert exec_mode.data == "test.data"

def test_state_object():
    """Test that state object is available."""
    from erdo import state
    assert state is not None

def test_actions_import():
    """Test that action modules can be imported."""
    from erdo.actions import memory, utils, bot, codeexec, resource_definitions
    
    # Test that action functions exist
    assert hasattr(memory, 'search')
    assert hasattr(utils, 'send_status')
    assert hasattr(bot, 'invoke')
    assert hasattr(codeexec, 'execute')

def test_conditions_import():
    """Test that condition classes can be imported."""
    from erdo.conditions import IsSuccess, GreaterThan, And, Or, Not, TextEquals
    
    # Test that conditions can be instantiated
    success_condition = IsSuccess()
    assert success_condition is not None
    
    gt_condition = GreaterThan("confidence", "0.8")
    assert gt_condition is not None
    
    # Test compound conditions
    and_condition = And(success_condition, gt_condition)
    assert and_condition is not None

def test_template_string():
    """Test TemplateString functionality."""
    from erdo.template import TemplateString
    
    template = TemplateString("{{test_value}}")
    assert template is not None
    assert str(template) == "{{test_value}}"

if __name__ == "__main__":
    pytest.main([__file__])