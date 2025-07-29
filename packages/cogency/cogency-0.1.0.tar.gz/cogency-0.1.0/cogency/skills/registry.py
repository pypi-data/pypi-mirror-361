"""
Skill registry for dynamic skill discovery and extension.

Provides opt-in registry system for extensibility while preserving
manual wiring for core flows.
"""

from typing import Dict, Any, Callable, List, Optional, Type
from dataclasses import dataclass
import inspect
import logging
from functools import wraps

from ..core.result import SkillResult
from ..core.context import SkillContext

logger = logging.getLogger(__name__)


@dataclass
class SkillInfo:
    """Information about a registered skill."""
    
    name: str
    function: Callable
    description: str
    parameters: Dict[str, Any]
    category: str = "general"
    version: str = "1.0.0"
    author: str = "unknown"
    aliases: List[str] = None
    tags: List[str] = None
    
    def __post_init__(self):
        if self.aliases is None:
            self.aliases = []
        if self.tags is None:
            self.tags = []
    
    @classmethod
    def from_function(cls, name: str, function: Callable, **kwargs) -> 'SkillInfo':
        """Create SkillInfo from a function."""
        sig = inspect.signature(function)
        doc = inspect.getdoc(function) or "No description available"
        
        # Use provided description or fall back to function docstring
        description = kwargs.pop('description', None) or doc
        
        return cls(
            name=name,
            function=function,
            description=description,
            parameters={
                param_name: {
                    "annotation": param.annotation,
                    "default": param.default if param.default != inspect.Parameter.empty else None,
                    "kind": param.kind.name
                }
                for param_name, param in sig.parameters.items()
            },
            **kwargs
        )


class SkillRegistry:
    """
    Registry for dynamic skill discovery and extension.
    
    Supports both manual registration and auto-discovery of skills.
    Designed to complement manual wiring, not replace it.
    """
    
    def __init__(self):
        self._skills: Dict[str, SkillInfo] = {}
        self._categories: Dict[str, List[str]] = {}
        self._aliases: Dict[str, str] = {}
    
    def register(
        self,
        name: str,
        function: Callable,
        description: Optional[str] = None,
        category: str = "general",
        version: str = "1.0.0",
        author: str = "unknown",
        aliases: Optional[List[str]] = None,
        tags: Optional[List[str]] = None
    ) -> None:
        """
        Register a skill function.
        
        Args:
            name: Skill name (unique identifier)
            function: Skill function
            description: Skill description (defaults to function docstring)
            category: Skill category for organization
            version: Skill version
            author: Skill author
            aliases: Optional aliases for the skill
            tags: Optional tags for search and filtering
        """
        if name in self._skills:
            logger.warning(f"Skill '{name}' already registered, overwriting")
        
        # Use provided description or extract from docstring
        if description is None:
            description = inspect.getdoc(function) or "No description available"
        
        skill_info = SkillInfo.from_function(
            name=name,
            function=function,
            description=description,
            category=category,
            version=version,
            author=author,
            aliases=aliases or [],
            tags=tags or []
        )
        
        self._skills[name] = skill_info
        
        # Update category index
        if category not in self._categories:
            self._categories[category] = []
        if name not in self._categories[category]:
            self._categories[category].append(name)
        
        # Register aliases
        for alias in skill_info.aliases:
            self._aliases[alias] = name
        
        logger.info(f"Registered skill: {name} (category: {category}, aliases: {skill_info.aliases})")
    
    def get(self, name: str) -> Optional[Callable]:
        """Get a skill function by name or alias."""
        # Check direct name
        if name in self._skills:
            return self._skills[name].function
        
        # Check aliases
        if name in self._aliases:
            actual_name = self._aliases[name]
            return self._skills[actual_name].function
        
        return None
    
    def get_info(self, name: str) -> Optional[SkillInfo]:
        """Get skill information by name or alias."""
        # Check direct name
        if name in self._skills:
            return self._skills[name]
        
        # Check aliases
        if name in self._aliases:
            actual_name = self._aliases[name]
            return self._skills[actual_name]
        
        return None
    
    def list_skills(self, category: Optional[str] = None) -> List[str]:
        """List all registered skills, optionally filtered by category."""
        if category:
            return self._categories.get(category, [])
        return list(self._skills.keys())
    
    def list_categories(self) -> List[str]:
        """List all skill categories."""
        return list(self._categories.keys())
    
    def search(self, query: str) -> List[str]:
        """Search skills by name, description, or tags."""
        query_lower = query.lower()
        matches = []
        
        for name, skill_info in self._skills.items():
            # Check name
            if query_lower in name.lower():
                matches.append(name)
                continue
            
            # Check description
            if query_lower in skill_info.description.lower():
                matches.append(name)
                continue
            
            # Check tags
            if any(query_lower in tag.lower() for tag in skill_info.tags):
                matches.append(name)
                continue
            
            # Check aliases
            if any(query_lower in alias.lower() for alias in skill_info.aliases):
                matches.append(name)
                continue
        
        return matches
    
    def create_factory(self) -> 'SkillFactory':
        """Create a skill factory for dynamic skill creation."""
        return SkillFactory(self)
    
    def auto_discover(self, module_path: str) -> int:
        """
        Auto-discover skills in a module path.
        
        Looks for functions decorated with @skill decorator.
        
        Args:
            module_path: Python module path to scan
            
        Returns:
            Number of skills discovered
        """
        import importlib
        import pkgutil
        
        discovered = 0
        
        try:
            # Import the module
            module = importlib.import_module(module_path)
            
            # Check if it's a package
            if hasattr(module, '__path__'):
                # Scan all submodules
                for importer, modname, ispkg in pkgutil.iter_modules(module.__path__, module.__name__ + "."):
                    try:
                        submodule = importlib.import_module(modname)
                        discovered += self._discover_in_module(submodule)
                    except Exception as e:
                        logger.warning(f"Failed to discover skills in {modname}: {e}")
            else:
                # Single module
                discovered += self._discover_in_module(module)
                
        except Exception as e:
            logger.error(f"Failed to auto-discover skills in {module_path}: {e}")
        
        logger.info(f"Auto-discovered {discovered} skills from {module_path}")
        return discovered
    
    def _discover_in_module(self, module) -> int:
        """Discover skills in a specific module."""
        discovered = 0
        
        for name in dir(module):
            obj = getattr(module, name)
            
            # Check if it's a skill function
            if (callable(obj) and 
                hasattr(obj, '_skill_metadata') and
                not name.startswith('_')):
                
                metadata = obj._skill_metadata
                self.register(
                    name=metadata.get('name', name),
                    function=obj,
                    description=metadata.get('description'),
                    category=metadata.get('category', 'general'),
                    version=metadata.get('version', '1.0.0'),
                    author=metadata.get('author', 'unknown'),
                    aliases=metadata.get('aliases', []),
                    tags=metadata.get('tags', [])
                )
                discovered += 1
        
        return discovered
    
    def generate_docs(self, format_type: str = "markdown") -> str:
        """Generate documentation for all registered skills."""
        if format_type == "github":
            return self._generate_github_docs()
        else:
            return self._generate_markdown_docs()
    
    def _generate_markdown_docs(self) -> str:
        """Generate basic markdown documentation."""
        docs = ["# Skill Registry Documentation\n"]
        
        for category in sorted(self._categories.keys()):
            docs.append(f"## {category.title()} Skills\n")
            
            for skill_name in sorted(self._categories[category]):
                skill_info = self._skills[skill_name]
                docs.append(f"### {skill_name}")
                docs.append(f"**Author:** {skill_info.author}")
                docs.append(f"**Version:** {skill_info.version}")
                docs.append(f"**Description:** {skill_info.description}")
                
                # Aliases
                if skill_info.aliases:
                    docs.append(f"**Aliases:** {', '.join(skill_info.aliases)}")
                
                # Tags
                if skill_info.tags:
                    docs.append(f"**Tags:** {', '.join(skill_info.tags)}")
                
                # Parameters
                if skill_info.parameters:
                    docs.append("\n**Parameters:**")
                    for param_name, param_info in skill_info.parameters.items():
                        annotation = param_info.get('annotation', 'Any')
                        default = param_info.get('default')
                        default_str = f" = {default}" if default is not None else ""
                        docs.append(f"- `{param_name}: {annotation}{default_str}`")
                
                docs.append("")
        
        return "\n".join(docs)
    
    def _generate_github_docs(self) -> str:
        """Generate GitHub-optimized markdown documentation with badges and collapsible sections."""
        docs = ["# 🧠 Cogency Skills Registry\n"]
        
        # Add summary stats
        total_skills = len(self._skills)
        total_categories = len(self._categories)
        
        docs.append(f"![Skills](https://img.shields.io/badge/skills-{total_skills}-blue)")
        docs.append(f"![Categories](https://img.shields.io/badge/categories-{total_categories}-green)")
        docs.append(f"![Version](https://img.shields.io/badge/version-0.1.0-orange)")
        docs.append("")
        
        # Add table of contents
        docs.append("## 📋 Table of Contents\n")
        for category in sorted(self._categories.keys()):
            category_title = category.title().replace('-', ' ')
            skill_count = len(self._categories[category])
            docs.append(f"- [{category_title} Skills](#{category.lower().replace(' ', '-')}-skills) ({skill_count} skills)")
        docs.append("")
        
        # Generate documentation for each category
        for category in sorted(self._categories.keys()):
            category_emoji = self._get_category_emoji(category)
            category_title = category.title().replace('-', ' ')
            docs.append(f"## {category_emoji} {category_title} Skills\n")
            
            for skill_name in sorted(self._categories[category]):
                skill_info = self._skills[skill_name]
                docs.append(f"### {skill_name}")
                docs.append("")
                
                # Add badges
                author_badge = f"https://img.shields.io/badge/author-{skill_info.author.replace(' ', '%20').replace('-', '--')}-lightgrey"
                version_badge = f"https://img.shields.io/badge/version-{skill_info.version}-blue"
                docs.append(f"![Author]({author_badge}) ![Version]({version_badge})")
                
                if skill_info.tags:
                    for tag in skill_info.tags:
                        tag_badge = f"https://img.shields.io/badge/tag-{tag.replace(' ', '%20').replace('-', '--')}-purple"
                        docs.append(f"![{tag}]({tag_badge})")
                
                docs.append("")
                docs.append(f"**Description:** {skill_info.description}")
                
                if skill_info.aliases:
                    docs.append(f"**Aliases:** `{', '.join(skill_info.aliases)}`")
                
                # Collapsible parameters section
                if skill_info.parameters:
                    docs.append("\n<details>")
                    docs.append("<summary><strong>Parameters</strong></summary>\n")
                    docs.append("| Parameter | Type | Default | Description |")
                    docs.append("|-----------|------|---------|-------------|")
                    for param_name, param_info in skill_info.parameters.items():
                        param_type = str(param_info.get('annotation', 'Any'))
                        param_default = str(param_info.get('default', 'N/A'))
                        param_desc = param_info.get('description', 'No description')
                        docs.append(f"| `{param_name}` | `{param_type}` | `{param_default}` | {param_desc} |")
                    docs.append("\n</details>")
                
                docs.append("\n---\n")
        
        # Add footer
        docs.append("## 🚀 Getting Started\n")
        docs.append("```bash")
        docs.append("# Install cogency")
        docs.append("pip install cogency")
        docs.append("")
        docs.append("# Use CLI to explore skills")
        docs.append("cogency list")
        docs.append("cogency search <query>")
        docs.append("cogency info <skill_name>")
        docs.append("```")
        docs.append("")
        docs.append("Generated automatically by cogency CLI. 🤖")
        
        return "\n".join(docs)
    
    def _get_category_emoji(self, category: str) -> str:
        """Get emoji for category."""
        emoji_map = {
            'cognitive': '🧠',
            'analysis': '🔍',
            'extraction': '📄',
            'synthesis': '🔗',
            'general': '⚙️',
            'test': '🧪',
            'content': '📝',
            'data': '📊',
            'communication': '💬',
            'reasoning': '🤔',
            'research': '🔬',
            'validation': '✅'
        }
        return emoji_map.get(category, '📦')


class SkillFactory:
    """
    Factory for creating skills dynamically from registry.
    
    Provides a clean interface for nodes to access registered skills
    without direct coupling to the registry.
    """
    
    def __init__(self, registry: SkillRegistry):
        self.registry = registry
    
    def get(self, name: str) -> Optional[Callable]:
        """Get a skill function by name."""
        return self.registry.get(name)
    
    def create(self, name: str, **kwargs) -> Optional[Callable]:
        """Create a skill instance with bound parameters."""
        skill_func = self.registry.get(name)
        if not skill_func:
            return None
        
        # Create a wrapper that binds the parameters
        @wraps(skill_func)
        async def bound_skill(context: SkillContext, **additional_kwargs):
            # Merge bound kwargs with call-time kwargs
            final_kwargs = {**kwargs, **additional_kwargs}
            return await skill_func(context, **final_kwargs)
        
        return bound_skill
    
    def list_available(self) -> List[str]:
        """List all available skills."""
        return self.registry.list_skills()


# Global registry instance
_global_registry = SkillRegistry()


def get_skill_registry() -> SkillRegistry:
    """Get the global skill registry."""
    return _global_registry


def skill(
    name: Optional[str] = None,
    description: Optional[str] = None,
    category: str = "general",
    version: str = "1.0.0",
    author: str = "unknown",
    aliases: Optional[List[str]] = None,
    tags: Optional[List[str]] = None,
    auto_register: bool = True
):
    """
    Decorator to mark and optionally register a skill function.
    
    Args:
        name: Skill name (defaults to function name)
        description: Skill description (defaults to function docstring)
        category: Skill category
        version: Skill version
        author: Skill author
        aliases: Optional aliases
        tags: Optional tags for search and filtering
        auto_register: Whether to auto-register with global registry
    """
    def decorator(func):
        skill_name = name or func.__name__
        
        # Add metadata to function
        func._skill_metadata = {
            'name': skill_name,
            'description': description,
            'category': category,
            'version': version,
            'author': author,
            'aliases': aliases or [],
            'tags': tags or []
        }
        
        # Auto-register if requested
        if auto_register:
            _global_registry.register(
                name=skill_name,
                function=func,
                description=description,
                category=category,
                version=version,
                author=author,
                aliases=aliases,
                tags=tags
            )
        
        return func
    
    return decorator


# Convenience functions
def register_skill(
    name: str,
    function: Callable,
    category: str = "general",
    **kwargs
) -> None:
    """Register a skill with the global registry."""
    _global_registry.register(name, function, category, **kwargs)


def get_skill(name: str) -> Optional[Callable]:
    """Get a skill from the global registry."""
    return _global_registry.get(name)


def create_skill_factory() -> SkillFactory:
    """Create a skill factory from the global registry."""
    return _global_registry.create_factory()