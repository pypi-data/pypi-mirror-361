"""
Tests for the skill registry and discovery system.

Ensures OSS-ready functionality is working correctly.
"""

import pytest
from unittest.mock import Mock, AsyncMock
from typing import Dict, Any

from cogency.skills.registry import (
    SkillRegistry, 
    SkillFactory, 
    SkillInfo,
    skill,
    get_skill_registry
)
from cogency.discovery import SkillDiscovery, validate_oss_readiness
from cogency.core.context import SkillContext
from cogency.core.result import SkillResult, SkillStatus


class TestSkillRegistry:
    """Test the skill registry functionality."""
    
    def setup_method(self):
        """Setup for each test."""
        self.registry = SkillRegistry()
    
    def test_skill_registration(self):
        """Test basic skill registration."""
        async def test_skill(context: SkillContext, content: str) -> SkillResult:
            return SkillResult(data={"result": "test"}, status=SkillStatus.COMPLETED)
        
        self.registry.register(
            name="test_skill",
            function=test_skill,
            description="A test skill",
            category="test",
            author="test_author",
            aliases=["test", "demo"],
            tags=["testing", "demo"]
        )
        
        # Check registration
        assert self.registry.get("test_skill") == test_skill
        assert self.registry.get("test") == test_skill  # Alias
        assert self.registry.get("demo") == test_skill  # Alias
        
        # Check metadata
        info = self.registry.get_info("test_skill")
        assert info.name == "test_skill"
        assert info.description == "A test skill"
        assert info.category == "test"
        assert info.author == "test_author"
        assert "test" in info.aliases
        assert "demo" in info.aliases
        assert "testing" in info.tags
        assert "demo" in info.tags
    
    def test_skill_decorator(self):
        """Test the @skill decorator."""
        @skill(
            name="decorated_skill",
            description="A decorated skill",
            category="test",
            author="test_author",
            aliases=["decorated"],
            tags=["decorator"],
            auto_register=False  # Don't register with global registry
        )
        async def decorated_skill(context: SkillContext) -> SkillResult:
            return SkillResult(data={"decorated": True}, status=SkillStatus.COMPLETED)
        
        # Check metadata was added
        assert hasattr(decorated_skill, '_skill_metadata')
        metadata = decorated_skill._skill_metadata
        assert metadata['name'] == 'decorated_skill'
        assert metadata['description'] == 'A decorated skill'
        assert metadata['category'] == 'test'
        assert metadata['author'] == 'test_author'
        assert 'decorated' in metadata['aliases']
        assert 'decorator' in metadata['tags']
    
    def test_skill_search(self):
        """Test skill search functionality."""
        async def skill1(context: SkillContext) -> SkillResult:
            return SkillResult(data={}, status=SkillStatus.COMPLETED)
        
        async def skill2(context: SkillContext) -> SkillResult:
            return SkillResult(data={}, status=SkillStatus.COMPLETED)
        
        self.registry.register(
            name="analyze_content",
            function=skill1,
            description="Analyze content structure",
            tags=["analysis", "content"]
        )
        
        self.registry.register(
            name="extract_data",
            function=skill2,
            description="Extract data from content",
            tags=["extraction", "data"]
        )
        
        # Test search
        results = self.registry.search("analyze")
        assert "analyze_content" in results
        
        results = self.registry.search("content")
        assert "analyze_content" in results
        assert "extract_data" in results
        
        results = self.registry.search("extraction")
        assert "extract_data" in results
    
    def test_skill_factory(self):
        """Test skill factory functionality."""
        async def test_skill(context: SkillContext, param: str = "default") -> SkillResult:
            return SkillResult(data={"param": param}, status=SkillStatus.COMPLETED)
        
        self.registry.register("test_skill", test_skill)
        factory = self.registry.create_factory()
        
        # Test getting skill
        skill_func = factory.get("test_skill")
        assert skill_func == test_skill
        
        # Test creating bound skill
        bound_skill = factory.create("test_skill", param="bound_value")
        assert bound_skill is not None
    
    def test_documentation_generation(self):
        """Test automatic documentation generation."""
        async def documented_skill(context: SkillContext, content: str) -> SkillResult:
            """A well-documented skill for testing."""
            return SkillResult(data={}, status=SkillStatus.COMPLETED)
        
        self.registry.register(
            name="documented_skill",
            function=documented_skill,
            description="A well-documented skill",
            category="test",
            author="test_author",
            aliases=["doc_skill"],
            tags=["documentation", "test"]
        )
        
        docs = self.registry.generate_docs()
        assert "documented_skill" in docs
        assert "A well-documented skill" in docs
        assert "test_author" in docs
        assert "doc_skill" in docs
        assert "documentation" in docs


class TestSkillDiscovery:
    """Test the skill discovery system."""
    
    def setup_method(self):
        """Setup for each test."""
        self.registry = SkillRegistry()
        self.discovery = SkillDiscovery(self.registry)
    
    def test_metadata_validation(self):
        """Test OSS readiness validation."""
        # Good skill
        async def good_skill(context: SkillContext, content: str) -> SkillResult:
            """A properly documented skill."""
            return SkillResult(data={}, status=SkillStatus.COMPLETED)
        
        self.registry.register(
            name="good_skill",
            function=good_skill,
            description="A properly documented skill",
            author="real_author",
            version="1.0.1"
        )
        
        # Bad skill (missing metadata)
        async def bad_skill(context: SkillContext) -> SkillResult:
            return SkillResult(data={}, status=SkillStatus.COMPLETED)
        
        self.registry.register(
            name="bad_skill",
            function=bad_skill
            # Using defaults - no description, author="unknown", etc.
        )
        
        # Test validation
        good_errors = self.discovery.validate_skill_metadata("good_skill")
        bad_errors = self.discovery.validate_skill_metadata("bad_skill")
        
        assert len(good_errors) == 0
        assert len(bad_errors) > 0
        assert any("missing description" in error for error in bad_errors)
        assert any("missing author" in error for error in bad_errors)
    
    def test_skill_index_generation(self):
        """Test skill index generation."""
        async def test_skill(context: SkillContext) -> SkillResult:
            return SkillResult(data={}, status=SkillStatus.COMPLETED)
        
        self.registry.register(
            name="test_skill",
            function=test_skill,
            description="Test skill",
            category="test",
            author="test_author",
            aliases=["test"],
            tags=["testing"]
        )
        
        index = self.discovery.generate_skill_index()
        
        assert index["total_skills"] == 1
        assert "test" in index["categories"]
        assert index["categories"]["test"]["count"] == 1
        assert "test_skill" in index["skills"]
        assert index["skills"]["test_skill"]["category"] == "test"
        assert index["skills"]["test_skill"]["author"] == "test_author"
    
    def test_skill_linting(self):
        """Test skill linting for OSS readiness."""
        # Register a skill with issues
        async def problematic_skill(context: SkillContext) -> SkillResult:
            return SkillResult(data={}, status=SkillStatus.COMPLETED)
        
        self.registry.register("problematic_skill", problematic_skill)
        
        lint_results = self.discovery.lint_all_skills()
        
        assert "problematic_skill" in lint_results
        assert len(lint_results["problematic_skill"]) > 0
    
    def test_manifest_creation(self):
        """Test skill manifest creation."""
        async def test_skill(context: SkillContext) -> SkillResult:
            return SkillResult(data={}, status=SkillStatus.COMPLETED)
        
        self.registry.register(
            name="test_skill",
            function=test_skill,
            description="Test skill",
            author="test_author"
        )
        
        manifest = self.discovery.create_skill_manifest()
        
        assert "cogency_version" in manifest
        assert "manifest_version" in manifest
        assert "skill_index" in manifest
        assert "validation_results" in manifest
        assert manifest["skill_index"]["total_skills"] == 1


class TestOSSReadiness:
    """Test OSS readiness features."""
    
    def test_strict_metadata_schema(self):
        """Test that strict metadata schema is enforced."""
        @skill(
            name="strict_skill",
            description="A strictly validated skill",
            category="cognitive",
            version="1.0.0",
            author="cogency",
            aliases=["strict"],
            tags=["validation", "strict"],
            auto_register=False
        )
        async def strict_skill(context: SkillContext, content: str) -> SkillResult:
            """A skill with strict metadata validation."""
            return SkillResult(data={"validated": True}, status=SkillStatus.COMPLETED)
        
        metadata = strict_skill._skill_metadata
        
        # All required fields should be present
        required_fields = ['name', 'description', 'category', 'version', 'author', 'aliases', 'tags']
        for field in required_fields:
            assert field in metadata
        
        # Values should be correct types
        assert isinstance(metadata['aliases'], list)
        assert isinstance(metadata['tags'], list)
        assert isinstance(metadata['name'], str)
        assert isinstance(metadata['description'], str)
    
    def test_discovery_paths(self):
        """Test discovery path management."""
        registry = SkillRegistry()
        discovery = SkillDiscovery(registry)
        
        # Test default paths
        paths = discovery.get_discovery_paths()
        assert "cogency.skills.core" in paths
        assert "cogency.skills.community" in paths
        assert "cogency.skills.extensions" in paths
        
        # Test adding path
        discovery.add_discovery_path("custom.skills")
        assert "custom.skills" in discovery.get_discovery_paths()
        
        # Test removing path
        discovery.remove_discovery_path("custom.skills")
        assert "custom.skills" not in discovery.get_discovery_paths()


if __name__ == "__main__":
    pytest.main([__file__])