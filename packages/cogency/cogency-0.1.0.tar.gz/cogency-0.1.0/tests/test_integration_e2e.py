"""
Integration tests for end-to-end cognitive flows using skill factory.

Tests the complete pipeline from skill registration to execution.
"""

import pytest
from unittest.mock import Mock, AsyncMock

from cogency.core.context import SkillContext
from cogency.core.result import SkillResult, SkillStatus
from cogency.skills.registry import SkillRegistry, SkillFactory, skill
from cogency.services.llm import LLMService
from cogency.tools.content_analysis import ContentAnalysisTool
from cogency.tools.content_extraction import ContentExtractionTool
from cogency.registry import register_service


class TestEndToEndSkillExecution:
    """Test complete skill execution flows."""
    
    @pytest.fixture
    def mock_llm_service(self):
        """Mock LLM service for testing."""
        service = Mock(spec=LLMService)
        service.analyze = AsyncMock(return_value=Mock(
            insights=["Test insight 1", "Test insight 2"],
            themes=["theme1", "theme2"],
            confidence=0.9,
            metadata={"method": "test"}
        ))
        service.extract = AsyncMock(return_value=Mock(
            extracted_data={"key": "value"},
            confidence=0.8,
            metadata={"method": "test"}
        ))
        service.synthesize = AsyncMock(return_value=Mock(
            content="Synthesized content",
            confidence=0.85,
            metadata={"method": "test"}
        ))
        return service
    
    @pytest.fixture
    def mock_analysis_tool(self):
        """Mock content analysis tool."""
        tool = Mock(spec=ContentAnalysisTool)
        tool.analyze_content = AsyncMock(return_value=Mock(
            analysis_result={"structure": "analyzed"},
            confidence=0.9,
            metadata={"tool": "analysis"}
        ))
        return tool
    
    @pytest.fixture
    def mock_extraction_tool(self):
        """Mock content extraction tool."""
        tool = Mock(spec=ContentExtractionTool)
        tool.extract_information = AsyncMock(return_value=Mock(
            extracted_data={"extracted": "data"},
            confidence=0.8,
            metadata={"tool": "extraction"}
        ))
        return tool
    
    @pytest.fixture
    def skill_factory(self, mock_llm_service, mock_analysis_tool, mock_extraction_tool):
        """Set up skill factory with mocked services."""
        # Register mocked services
        register_service(LLMService, mock_llm_service)
        register_service(ContentAnalysisTool, mock_analysis_tool)
        register_service(ContentExtractionTool, mock_extraction_tool)
        
        # Import skills to trigger registration
        from cogency.skills import analyze, extract, synthesize
        
        # Create registry and factory
        from cogency.skills.registry import get_skill_registry
        registry = get_skill_registry()
        factory = SkillFactory(registry)
        
        return factory
    
    @pytest.mark.asyncio
    async def test_analyze_skill_full_pipeline(self, skill_factory):
        """Test complete analyze skill pipeline."""
        # Create skill context
        context = SkillContext(
            user_intent="test_user",
            session_id="test_session",
            metadata={"test": True}
        )
        
        # Get analyze skill from registry
        analyze_skill = skill_factory.get("analyze")
        assert analyze_skill is not None
        
        # Execute skill
        result = await analyze_skill(
            context=context,
            content="Test content for analysis",
            focus="themes"
        )
        
        # Verify result
        assert isinstance(result, SkillResult)
        assert result.status == SkillStatus.COMPLETED
        assert result.confidence > 0.0
        assert "insights" in result.data
        assert "themes" in result.data
    
    @pytest.mark.asyncio
    async def test_extract_skill_full_pipeline(self, skill_factory):
        """Test complete extract skill pipeline."""
        context = SkillContext(
            user_intent="test_user",
            session_id="test_session"
        )
        
        # Get extract skill from registry
        extract_skill = skill_factory.get("extract")
        assert extract_skill is not None
        
        # Execute skill
        result = await extract_skill(
            context=context,
            content="Test content with data to extract",
            target="key_points"
        )
        
        # Verify result
        assert isinstance(result, SkillResult)
        assert result.status == SkillStatus.COMPLETED
        assert result.confidence > 0.0
        assert "extracted" in result.data
        assert result.data["target"] == "key_points"
    
    @pytest.mark.asyncio
    async def test_synthesize_skill_full_pipeline(self, skill_factory):
        """Test complete synthesize skill pipeline."""
        context = SkillContext(
            user_intent="test_user",
            session_id="test_session"
        )
        
        # Get synthesize skill from registry
        synthesize_skill = skill_factory.get("synthesize")
        assert synthesize_skill is not None
        
        # Execute skill
        result = await synthesize_skill(
            context=context,
            sources=["Source 1 content", "Source 2 content"],
            focus="summary"
        )
        
        # Verify result
        assert isinstance(result, SkillResult)
        assert result.status == SkillStatus.COMPLETED
        assert result.confidence > 0.0
        assert "content" in result.data
        assert result.data["source_count"] == 2
    
    @pytest.mark.asyncio
    async def test_skill_factory_binding(self, skill_factory):
        """Test skill factory parameter binding."""
        context = SkillContext(
            user_intent="test_user",
            session_id="test_session"
        )
        
        # Create bound skill with preset parameters
        bound_analyze = skill_factory.create("analyze", focus="themes", deep_analysis=True)
        assert bound_analyze is not None
        
        # Execute bound skill
        result = await bound_analyze(
            context=context,
            content="Test content"
        )
        
        # Verify result
        assert isinstance(result, SkillResult)
        assert result.status == SkillStatus.COMPLETED
    
    @pytest.mark.asyncio
    async def test_custom_skill_registration_and_execution(self, skill_factory):
        """Test registering and executing custom skills."""
        # Define custom skill
        @skill(
            name="custom_test_skill",
            description="A custom test skill",
            category="test",
            author="test_author",
            auto_register=False
        )
        async def custom_test_skill(context: SkillContext, input_data: str) -> SkillResult:
            """Custom skill for testing."""
            return SkillResult(
                data={"processed": input_data.upper()},
                status=SkillStatus.COMPLETED,
                confidence=1.0
            )
        
        # Register custom skill
        skill_factory.registry.register(
            name="custom_test_skill",
            function=custom_test_skill,
            description="A custom test skill",
            category="test",
            author="test_author"
        )
        
        # Execute custom skill
        context = SkillContext(user_intent="test_user", session_id="test_session")
        custom_skill = skill_factory.get("custom_test_skill")
        
        result = await custom_skill(
            context=context,
            input_data="test input"
        )
        
        # Verify result
        assert isinstance(result, SkillResult)
        assert result.status == SkillStatus.COMPLETED
        assert result.data["processed"] == "TEST INPUT"
    
    @pytest.mark.asyncio
    async def test_skill_chaining_workflow(self, skill_factory):
        """Test chaining multiple skills together."""
        context = SkillContext(
            user_intent="test_user",
            session_id="test_session"
        )
        
        # Step 1: Analyze content
        analyze_skill = skill_factory.get("analyze")
        analysis_result = await analyze_skill(
            context=context,
            content="Complex content that needs analysis and extraction",
            focus="structure"
        )
        
        assert analysis_result.status == SkillStatus.COMPLETED
        
        # Step 2: Extract specific information
        extract_skill = skill_factory.get("extract")
        extraction_result = await extract_skill(
            context=context,
            content="Complex content that needs analysis and extraction",
            target="key_points"
        )
        
        assert extraction_result.status == SkillStatus.COMPLETED
        
        # Step 3: Synthesize results
        synthesize_skill = skill_factory.get("synthesize")
        synthesis_result = await synthesize_skill(
            context=context,
            sources=[
                str(analysis_result.data),
                str(extraction_result.data)
            ],
            focus="comprehensive"
        )
        
        assert synthesis_result.status == SkillStatus.COMPLETED
        assert synthesis_result.data["source_count"] == 2
    
    def test_skill_factory_error_handling(self, skill_factory):
        """Test skill factory error handling."""
        # Test getting non-existent skill
        non_existent_skill = skill_factory.get("non_existent_skill")
        assert non_existent_skill is None
        
        # Test creating non-existent skill
        non_existent_bound = skill_factory.create("non_existent_skill")
        assert non_existent_bound is None
        
        # Test listing available skills
        available_skills = skill_factory.list_available()
        assert isinstance(available_skills, list)
        assert "analyze" in available_skills
        assert "extract" in available_skills
        assert "synthesize" in available_skills
    
    @pytest.mark.asyncio
    async def test_skill_context_propagation(self, skill_factory):
        """Test that skill context is properly propagated."""
        context = SkillContext(
            user_intent="test_user",
            session_id="test_session",
            metadata={"test_key": "test_value"}
        )
        
        analyze_skill = skill_factory.get("analyze")
        result = await analyze_skill(
            context=context,
            content="Test content"
        )
        
        # Verify context was used (would be tested in actual skill implementation)
        assert result.status == SkillStatus.COMPLETED
        # In real implementation, we'd check that the context was passed to services
    
    @pytest.mark.asyncio
    async def test_skill_performance_metrics(self, skill_factory):
        """Test that skills return performance metrics."""
        context = SkillContext(
            user_intent="test_user",
            session_id="test_session"
        )
        
        analyze_skill = skill_factory.get("analyze")
        result = await analyze_skill(
            context=context,
            content="Test content for performance measurement"
        )
        
        # Verify performance data is included
        assert result.status == SkillStatus.COMPLETED
        assert result.confidence is not None
        assert isinstance(result.confidence, float)
        assert 0.0 <= result.confidence <= 1.0
        assert result.metadata is not None
        assert isinstance(result.metadata, dict)


class TestSkillRegistryIntegration:
    """Test skill registry integration features."""
    
    def test_skill_discovery_and_documentation(self):
        """Test skill discovery and documentation generation."""
        # Import skills to trigger registration
        from cogency.skills import analyze, extract, synthesize
        from cogency.skills.registry import get_skill_registry
        
        registry = get_skill_registry()
        
        # Test skill search
        search_results = registry.search("analyze")
        assert "analyze" in search_results
        
        # Test documentation generation
        docs = registry.generate_docs(format_type="github")
        assert "analyze" in docs
        assert "extract" in docs
        assert "synthesize" in docs
        assert "🧠" in docs  # Cognitive emoji
        assert "shields.io" in docs  # Badges
    
    def test_skill_metadata_validation(self):
        """Test skill metadata validation."""
        # Import skills to trigger registration
        from cogency.skills import analyze, extract, synthesize
        from cogency.skills.registry import get_skill_registry
        
        registry = get_skill_registry()
        
        # Test getting skill info
        analyze_info = registry.get_info("analyze")
        assert analyze_info is not None
        assert analyze_info.name == "analyze"
        assert analyze_info.category == "cognitive"
        assert analyze_info.author == "cogency"
        assert "understand" in analyze_info.aliases
        assert "comprehend" in analyze_info.aliases
        
        # Test parameter documentation
        assert "context" in analyze_info.parameters
        assert "content" in analyze_info.parameters
        assert "focus" in analyze_info.parameters
    
    def test_skill_categorization(self):
        """Test skill categorization."""
        # Import skills to trigger registration
        from cogency.skills import analyze, extract, synthesize
        from cogency.skills.registry import get_skill_registry
        
        registry = get_skill_registry()
        
        # Test category listing
        categories = registry.list_categories()
        assert "cognitive" in categories
        
        # Test skills by category
        cognitive_skills = registry.list_skills("cognitive")
        assert "analyze" in cognitive_skills
        assert "extract" in cognitive_skills
        assert "synthesize" in cognitive_skills