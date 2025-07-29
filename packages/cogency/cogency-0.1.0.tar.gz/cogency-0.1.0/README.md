# 🧠 Cogency

[![PyPI version](https://img.shields.io/pypi/v/cogency)](https://pypi.org/project/cogency/)
[![Python Support](https://img.shields.io/pypi/pyversions/cogency)](https://pypi.org/project/cogency/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://img.shields.io/github/workflow/status/tysonchan/cogency/Tests)](https://github.com/tysonchan/cogency/actions)

**Cognitive architecture for AI agents** - Skills, Tools, and Services framework for building intelligent agents.

## 🚀 Quick Start

```bash
pip install cogency
```

```python
from cogency import SkillFactory, SkillContext
from cogency.core import AgentState, RoutingDecision

# Create a skill factory
factory = SkillFactory()

# Create execution context
context = SkillContext(
    user_intent="analyze_content",
    session_id="session_123"
)

# Execute cognitive skills
analyze_skill = factory.get("analyze")
result = await analyze_skill(
    context=context,
    content="Your content here",
    focus="key_insights"
)

print(f"Analysis: {result.data}")
```

## 🎯 Core Concepts

### Skills
Atomic cognitive operations that can be composed and orchestrated:

```python
from cogency.skills.registry import skill

@skill(
    name="custom_analyzer",
    description="Custom content analysis skill",
    category="analysis"
)
async def custom_analyzer(context: SkillContext, content: str) -> SkillResult:
    # Your cognitive logic here
    return SkillResult(
        data={"analysis": "processed content"},
        status=SkillStatus.COMPLETED,
        confidence=0.9
    )
```

### Services
Abstracted AI services with dependency injection:

```python
from cogency.services.llm import LLMService
from cogency.registry import register_service

# Register your LLM service
register_service(LLMService, your_llm_implementation)
```

### Tools
Reusable utilities for content processing:

```python
from cogency.tools.content_analysis import ContentAnalysisTool

tool = ContentAnalysisTool()
result = await tool.analyze_content(content="Your content")
```

## 🏗️ Architecture

Cogency provides a **dual-mode architecture**:

1. **Manual Wiring**: Direct skill instantiation for core workflows
2. **Registry-based**: Auto-discovery and composition for extensibility

```python
# Manual wiring (explicit, debuggable)
from cogency.skills.analyze import analyze_skill
result = await analyze_skill(context, content="data")

# Registry-based (composable, extensible)
factory = SkillFactory()
analyze = factory.get("analyze")
result = await analyze(context, content="data")
```

## 📊 Agent Workflows

Built-in support for complex agent orchestration:

```python
from cogency.core import AgentState, RoutingDecision

# Create agent state
state = AgentState(
    message="User query",
    session_id="session_123",
    routing_decision=RoutingDecision.STANDARD
)

# Execute workflow
workflow = CognitiveWorkflow(skills=["analyze", "synthesize"])
result = await workflow.execute(state)
```

## 🔧 Built-in Skills

- **`analyze`**: Content analysis and insight extraction
- **`extract`**: Information extraction and structuring  
- **`synthesize`**: Multi-source content synthesis

## 🎨 Interface Types

Support for rich response rendering:

```python
from cogency.core import InterfaceType

# Specify response format
result.interface_type = InterfaceType.KEY_INSIGHTS
result.interface_data = {
    "insights": ["insight1", "insight2"],
    "categories": ["category1", "category2"]
}
```

## 📈 Observability

Comprehensive tracing and metrics:

```python
from cogency.core import ComprehensiveTrace, TraceStep

# Automatic execution tracing
trace = ComprehensiveTrace(
    session_id="session_123",
    steps=[
        TraceStep(
            step_name="analyze",
            duration_ms=150.0,
            confidence=0.9
        )
    ]
)
```

## 🧪 Testing

Built-in testing utilities:

```python
from cogency.skills.registry import SkillFactory
import pytest

@pytest.fixture
def skill_factory():
    return SkillFactory()

@pytest.mark.asyncio
async def test_analyze_skill(skill_factory):
    context = SkillContext(user_intent="test")
    skill = skill_factory.get("analyze")
    result = await skill(context=context, content="test content")
    assert result.status == SkillStatus.COMPLETED
```

## 🔧 CLI Tools

Generate documentation and manage skills:

```bash
# Generate skill documentation
cogency docs --format github

# List available skills
cogency skills list

# Validate skill registry
cogency skills validate
```

## 📚 Documentation

- **Skills**: Atomic cognitive operations
- **Services**: AI service abstractions  
- **Tools**: Content processing utilities
- **Workflows**: Agent orchestration patterns
- **Registry**: Skill discovery and composition

## 🤝 Contributing

Cogency is designed for extensibility:

1. **Core Skills**: Submit via pull request
2. **Extension Skills**: Use registry system
3. **Custom Services**: Implement service interfaces
4. **Tools**: Extend tool abstractions

## 📄 License

MIT License - see LICENSE file for details.

## 🙏 Acknowledgments

Built for the AI agent developer community. Inspired by cognitive architectures and modern AI frameworks.