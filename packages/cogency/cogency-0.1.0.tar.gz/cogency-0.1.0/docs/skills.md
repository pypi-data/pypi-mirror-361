# Skills Specification

## What Are Skills?

Skills are **cognitive verbs** - atomic mental processes that represent "what the agent can think" rather than "what it can do to the world."

Each skill performs exactly one cognitive operation and orchestrates tools internally while presenting a clean cognitive interface.

## Universal Interface

All skills follow the same interface pattern for perfect composability:

```python
async def skill_name(
    context: Context,     # Execution state and user intent
    **params             # Skill-specific parameters
) -> SkillResult:        # Structured result with confidence
    pass
```

## Context Object

The Context carries execution state and reasoning history:

```python
@dataclass
class Context:
    user_intent: str                    # What the user is trying to accomplish
    memory: MemorySnapshot              # Persistent memory state
    history: List[Exchange]             # Conversation history
    state: Dict[str, Any]              # Flexible key-value state
    budget: Optional[float]             # Resource constraints
    preferences: Dict[str, Any]         # User preferences
```

## Result Structure

All skills return structured results with confidence scoring:

```python
@dataclass
class SkillResult:
    data: Any                          # Primary result
    confidence: float                  # Confidence score (0.0-1.0)
    metadata: Dict[str, Any]          # Execution metadata
    errors: List[SkillError] = None   # Non-fatal errors
    
    @property
    def is_success(self) -> bool:
        return self.confidence >= 0.5
```

## Atomicity Doctrine

A skill is atomic if it satisfies all criteria:

1. **Single Verb** - Can be described with one cognitive action word
2. **Clear Input/Output** - Deterministic transformation
3. **Deterministic Goal** - Same inputs produce equivalent outputs  
4. **Tool Independence** - May use tools but doesn't require specific ones

### Good Examples
```python
# ✅ Single cognitive operation
async def analyze(context: Context, content: str) -> AnalysisResult:
    """Understand structure, meaning, and context of content."""
    
# ✅ Clear evaluation criteria
async def evaluate(context: Context, content: str, criteria: str) -> EvaluationResult:
    """Judge quality, relevance, or fit against specific criteria."""
    
# ✅ Focused extraction
async def extract(context: Context, content: str, target: str) -> ExtractionResult:
    """Pull specific sections, quotes, or data points from content."""
```

### Bad Examples
```python
# ❌ Multiple verbs
async def analyze_and_evaluate(context: Context, content: str) -> CombinedResult:
    pass

# ❌ Vague boundaries  
async def smart_process(context: Context, content: str) -> SmartResult:
    pass
```

## Core Skills Inventory

### Reasoning
- **analyze** - Understand structure, meaning, and context
- **evaluate** - Judge quality, relevance, or fit against criteria
- **plan** - Sequence actions or approaches to achieve goals
- **synthesize** - Combine multiple sources into coherent understanding

### Perception  
- **search** - Find information using multiple strategies
- **extract** - Pull specific sections, quotes, or data points
- **parse** - Convert unstructured content into structured data
- **classify** - Categorize content by type, topic, or intent

### Expression
- **visualize** - Select optimal UI component for content presentation
- **format** - Structure data according to interface requirements
- **summarize** - Condense content while preserving key information
- **generate** - Create new content based on inputs and constraints

## Composability Patterns

### Natural Chaining
```python
content = await search(context, query="ML projects")
analysis = await analyze(context, content=content.data)
summary = await summarize(context, content=analysis.data)
```

### Parallel Processing
```python
results = await asyncio.gather(
    analyze(context, content=content),
    classify(context, content=content),
    extract(context, content=content)
)
```

### Conditional Branching
```python
if context.user_intent == "technical":
    result = await parse(context, content=content)
else:
    result = await summarize(context, content=content)
```

### Feedback Loops
```python
result = await generate(context, prompt=prompt)
evaluation = await evaluate(context, content=result.data, criteria=criteria)
if evaluation.confidence < threshold:
    result = await generate(context, prompt=refined_prompt)
```

## Error Handling

Skills use structured error handling with graceful degradation:

```python
async def analyze(context: Context, content: str) -> AnalysisResult:
    try:
        # Primary analysis path
        insights = await analysis_tool.analyze(content, context.user_intent)
        return AnalysisResult(data=insights, confidence=0.9)
        
    except ToolError as e:
        # Fallback to simpler analysis
        basic_insights = fallback_analyze(content)
        return AnalysisResult(
            data=basic_insights,
            confidence=0.6,
            errors=[SkillError("tool_failure", str(e), recoverable=True)]
        )
```

## Tool Integration

Skills orchestrate tools but don't implement logic:

```python
class AnalyzeSkill:
    def __init__(self, analysis_tool: ContentAnalysisTool):
        self.analysis_tool = analysis_tool
        
    async def execute(self, context: Context, content: str) -> AnalysisResult:
        # Cognitive decision: HOW to analyze
        if context.requires_deep_analysis:
            return await self.analysis_tool.deep_analyze(content, context.user_intent)
        else:
            return await self.analysis_tool.quick_analyze(content)
```

## Key Benefits

1. **Cognitive Clarity** - Maps directly to how humans think about thinking
2. **Perfect Composability** - Lego block design with universal interface
3. **Testable Components** - Each skill can be tested independently
4. **Natural Language Alignment** - Direct mapping from problem to code
5. **Graceful Degradation** - Structured error handling prevents failures

Skills transform AI development from managing implementation complexity to building cognitive capabilities.