# Implementation Guide

## Quick Start

### 1. Define Services (Raw Capabilities)

```python
class LLMService:
    async def analyze(self, content: str, intent: str) -> LLMResult:
        """Raw LLM analysis call."""
        pass
    
    async def classify(self, content: str, categories: List[str]) -> ClassificationResult:
        """Raw classification call."""
        pass

class EmbeddingService:
    async def embed(self, text: str) -> List[float]:
        """Generate embeddings for text."""
        pass
    
    async def similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between texts."""
        pass
```

### 2. Create Tools (Task-Specific Wrappers)

```python
class ContentAnalysisTool:
    def __init__(self, llm_service: LLMService, embedding_service: EmbeddingService):
        self.llm = llm_service
        self.embeddings = embedding_service
    
    async def analyze_content(self, content: str, intent: str) -> AnalysisResult:
        """Analyze content with caching and validation."""
        # Add caching, retries, validation
        embeddings = await self.embeddings.embed(content)
        analysis = await self.llm.analyze(content, intent)
        
        return AnalysisResult(
            insights=analysis.insights,
            themes=analysis.themes,
            embeddings=embeddings,
            confidence=analysis.confidence
        )
```

### 3. Implement Skills (Cognitive Operations)

```python
class AnalyzeSkill:
    def __init__(self, analysis_tool: ContentAnalysisTool):
        self.analysis_tool = analysis_tool
    
    async def execute(self, context: Context, content: str) -> AnalysisResult:
        """Understand structure, meaning, and context of content."""
        
        # Input validation
        if not content.strip():
            return AnalysisResult(
                data=None,
                confidence=0.0,
                errors=[SkillError("empty_input", "Content is empty", False)]
            )
        
        try:
            # Cognitive decision: How should I analyze this?
            if context.requires_deep_analysis:
                result = await self.analysis_tool.deep_analyze(content, context.user_intent)
            else:
                result = await self.analysis_tool.quick_analyze(content, context.user_intent)
            
            return AnalysisResult(
                data=result.data,
                confidence=result.confidence,
                metadata={"method": result.method}
            )
            
        except ToolError as e:
            # Graceful degradation
            return AnalysisResult(
                data={"insights": ["Analysis unavailable"]},
                confidence=0.3,
                errors=[SkillError("tool_failure", str(e), True)]
            )

# Register as function for easy composition
async def analyze(context: Context, content: str) -> AnalysisResult:
    skill = AnalyzeSkill(get_analysis_tool())
    return await skill.execute(context, content)
```

### 4. Create Nodes (Workflow Controllers)

```python
class ThinkNode:
    def __init__(self, search_skill, analyze_skill, plan_skill):
        self.search = search_skill
        self.analyze = analyze_skill
        self.plan = plan_skill
    
    async def execute(self, context: Context) -> ThinkResult:
        """Research and analysis workflow."""
        
        # Orchestrate skills
        content = await self.search.execute(context, query=context.user_query)
        if not content.is_success:
            return ThinkResult(error="Search failed", confidence=0.0)
        
        analysis = await self.analyze.execute(context, content=content.data)
        plan = await self.plan.execute(context, analysis=analysis.data)
        
        return ThinkResult(
            content=content.data,
            analysis=analysis.data,
            plan=plan.data,
            confidence=min(content.confidence, analysis.confidence, plan.confidence)
        )
```

### 5. Compose Into Flows

```python
# LangGraph integration
from langgraph import StateGraph

def create_agent_flow():
    graph = StateGraph(AgentState)
    
    # Nodes powered by skills
    graph.add_node("think", think_node)
    graph.add_node("act", act_node)
    graph.add_node("reflect", reflect_node)
    
    # Define flow
    graph.add_edge("think", "act")
    graph.add_edge("act", "reflect")
    graph.add_conditional_edge("reflect", should_continue)
    
    return graph.compile()
```

## Dependency Injection

Use singletons for clean DI:

```python
# Service registry
class ServiceRegistry:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._services = {}
        return cls._instance
    
    def register(self, service_type: Type, instance: Any):
        self._services[service_type] = instance
    
    def get(self, service_type: Type):
        return self._services[service_type]

# Usage
registry = ServiceRegistry()
registry.register(LLMService, GeminiService())
registry.register(EmbeddingService, OpenAIEmbeddingService())

# Skills get dependencies injected
def get_analysis_tool():
    return ContentAnalysisTool(
        llm_service=registry.get(LLMService),
        embedding_service=registry.get(EmbeddingService)
    )
```

## Testing Strategy

### Unit Test Skills

```python
async def test_analyze_skill():
    # Mock dependencies
    mock_tool = Mock(spec=ContentAnalysisTool)
    mock_tool.quick_analyze.return_value = AnalysisResult(
        data={"insights": ["test insight"]},
        confidence=0.8
    )
    
    # Test skill
    skill = AnalyzeSkill(mock_tool)
    context = Context(user_intent="understand", requires_deep_analysis=False)
    
    result = await skill.execute(context, "test content")
    
    assert result.confidence == 0.8
    assert result.data["insights"] == ["test insight"]
    mock_tool.quick_analyze.assert_called_once()
```

### Integration Test Nodes

```python
async def test_think_node():
    # Use real skills with mocked tools
    search_skill = SearchSkill(mock_search_tool)
    analyze_skill = AnalyzeSkill(mock_analysis_tool)
    plan_skill = PlanSkill(mock_planning_tool)
    
    node = ThinkNode(search_skill, analyze_skill, plan_skill)
    context = Context(user_query="explain ML")
    
    result = await node.execute(context)
    
    assert result.confidence > 0.5
    assert result.content is not None
```

## Common Patterns

### Skill Composition

```python
# Sequential processing
async def research_pipeline(context: Context, query: str):
    content = await search(context, query=query)
    analysis = await analyze(context, content=content.data)
    summary = await summarize(context, content=analysis.data)
    return summary

# Parallel processing with aggregation
async def multi_perspective_analysis(context: Context, content: str):
    results = await asyncio.gather(
        analyze(context, content=content),
        classify(context, content=content),
        extract(context, content=content, target="key_points")
    )
    
    return await synthesize(context, inputs=results)
```

### Error Recovery

```python
async def robust_analysis(context: Context, content: str):
    # Try primary analysis
    result = await analyze(context, content=content)
    
    # If low confidence, try alternative approaches
    if result.confidence < 0.7:
        fallback_result = await classify(context, content=content)
        if fallback_result.confidence > result.confidence:
            result = fallback_result
    
    return result
```

### Context Evolution

```python
async def iterative_refinement(context: Context, content: str):
    # Initial analysis
    result = await analyze(context, content=content)
    
    # Update context with findings
    context.state['initial_analysis'] = result.data
    
    # Refine based on initial findings
    refined_result = await synthesize(
        context, 
        inputs=[result.data], 
        refinement_criteria=context.user_intent
    )
    
    return refined_result
```

## Performance Optimization

### Caching at Tool Level

```python
class CachedAnalysisTool:
    def __init__(self, llm_service: LLMService):
        self.llm = llm_service
        self.cache = {}
    
    async def analyze(self, content: str, intent: str) -> AnalysisResult:
        cache_key = hash(content + intent)
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        result = await self.llm.analyze(content, intent)
        self.cache[cache_key] = result
        return result
```

### Parallel Skill Execution

```python
async def parallel_skills(context: Context, content: str):
    # Execute independent skills in parallel
    analysis_task = asyncio.create_task(analyze(context, content=content))
    classification_task = asyncio.create_task(classify(context, content=content))
    
    analysis_result = await analysis_task
    classification_result = await classification_task
    
    return await synthesize(context, inputs=[analysis_result.data, classification_result.data])
```

## Best Practices

1. **Keep Skills Atomic** - One cognitive operation per skill
2. **Use Dependency Injection** - Don't hardcode tool dependencies
3. **Handle Errors Gracefully** - Always provide fallback paths
4. **Test Independently** - Each skill should be unit testable
5. **Cache at Tool Level** - Not in skills themselves
6. **Compose Naturally** - Skills should chain without adapters

This architecture enables building sophisticated AI agents through cognitive clarity rather than implementation complexity.