# Agent Architecture Overview

## Core Principles

**Cognitive Clarity** - The architecture mirrors how humans think about thinking. Skills are cognitive verbs (analyze, evaluate, synthesize) that map directly to mental processes.

**Layered Abstraction** - Each layer has a single responsibility and depends only downward:
```
Flow → Node → Skill → Tool → Service
```

**Opt-in Complexity** - Start simple, add sophistication as needed. Every layer is swappable and extensible.

## Architecture Layers

### Service Layer
**Raw capabilities** - External systems, APIs, models
- `LLMService` - Language model calls
- `EmbeddingService` - Vector operations  
- `ArtifactService` - Document storage/retrieval
- `VectorService` - Vector database operations

**Characteristics:**
- Stateless, deterministic operations
- No cognitive logic - just execute commands
- Provided by external vendors or local infrastructure

### Tool Layer  
**Task-specific wrappers** - Smart behavior around services
- `SemanticSearchTool` - Combines embedding + artifact services
- `ContentAnalysisTool` - Combines LLM + embedding for analysis
- `ContentExtractionTool` - Smart extraction with fallbacks

**Characteristics:**
- Adds caching, validation, retries
- Single responsibility per tool
- Can be used by multiple skills

### Skill Layer
**Cognitive operations** - Mental processes that orchestrate tools
- `analyze()` - Understand structure and meaning
- `evaluate()` - Judge quality against criteria
- `synthesize()` - Combine multiple sources
- `extract()` - Pull specific information

**Characteristics:**
- Atomic cognitive operations (single verb)
- Tool-orchestrating abstractions
- Universal composability
- Lego block design

### Node Layer
**Workflow controllers** - Orchestrate skills for complex goals
- `ThinkNode` - Research and analysis workflow
- `ActNode` - Response generation workflow  
- `ReflectNode` - Content curation workflow

**Characteristics:**
- Compose multiple skills
- Handle workflow logic and state transitions
- Map to LangGraph nodes

### Flow Layer
**Execution orchestration** - Complete agent behavior
- Declarative workflow definition
- Conditional paths and retries
- State management across nodes

## Key Design Decisions

**Skills as Cognitive Primitives**
- Skills represent "what the agent can think" not "what it can do"
- Direct mapping from problem description to code
- Natural language alignment

**Universal Interface Pattern**
```python
async def skill_name(context: Context, **params) -> SkillResult:
    pass
```
- Any skill output can become any other skill input
- Perfect composability without adapters

**Dependency Injection**
- Skills get tools injected, not hardcoded
- Full extensibility at every layer
- Easy testing and mocking

**Structured Error Handling**
- Graceful degradation with fallbacks
- Non-fatal errors don't stop execution
- Rich debugging information

## Benefits

1. **Predictable Behavior** - Cognitive abstractions make agent behavior easier to reason about
2. **Modular Development** - Each layer can be developed and tested independently  
3. **Framework Agnostic** - Skills work with any orchestration system
4. **Natural Debugging** - Clear boundaries make issues easier to isolate
5. **Incremental Sophistication** - Add complexity only where needed

This architecture transforms AI agent development from managing graph complexity to building cognitive capabilities.