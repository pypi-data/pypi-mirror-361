"""
Auto-discovery system for skills and extensions.

Provides centralized discovery hooks for OSS-ready skill management.
"""

from typing import List, Dict, Any
import logging
from pathlib import Path

from .skills.registry import get_skill_registry, SkillRegistry

logger = logging.getLogger(__name__)


class SkillDiscovery:
    """
    Centralized skill discovery system.
    
    Manages auto-discovery of skills from predefined paths and
    provides hooks for extension systems.
    """
    
    def __init__(self, registry: SkillRegistry = None):
        self.registry = registry or get_skill_registry()
        self.discovery_paths = [
            "cogency.skills.core",
            "cogency.skills.community",
            "cogency.skills.extensions"
        ]
        self.discovered_skills: Dict[str, List[str]] = {}
    
    def discover_all(self) -> Dict[str, int]:
        """
        Discover skills from all configured paths.
        
        Returns:
            Dict mapping path to number of skills discovered
        """
        results = {}
        
        for path in self.discovery_paths:
            try:
                count = self.registry.auto_discover(path)
                results[path] = count
                self.discovered_skills[path] = self.registry.list_skills()
                logger.info(f"Discovered {count} skills from {path}")
            except Exception as e:
                logger.warning(f"Failed to discover skills from {path}: {e}")
                results[path] = 0
        
        return results
    
    def add_discovery_path(self, path: str) -> None:
        """Add a new discovery path."""
        if path not in self.discovery_paths:
            self.discovery_paths.append(path)
            logger.info(f"Added discovery path: {path}")
    
    def remove_discovery_path(self, path: str) -> None:
        """Remove a discovery path."""
        if path in self.discovery_paths:
            self.discovery_paths.remove(path)
            logger.info(f"Removed discovery path: {path}")
    
    def get_discovery_paths(self) -> List[str]:
        """Get all configured discovery paths."""
        return self.discovery_paths.copy()
    
    def validate_skill_metadata(self, skill_name: str) -> List[str]:
        """
        Validate that a skill has proper metadata for OSS contribution.
        
        Args:
            skill_name: Name of skill to validate
            
        Returns:
            List of validation errors (empty if valid)
        """
        skill_info = self.registry.get_info(skill_name)
        if not skill_info:
            return [f"Skill '{skill_name}' not found"]
        
        errors = []
        
        # Required metadata checks
        if not skill_info.description or skill_info.description == "No description available":
            errors.append(f"Skill '{skill_name}' missing description")
        
        if skill_info.author == "unknown":
            errors.append(f"Skill '{skill_name}' missing author")
        
        if skill_info.version == "1.0.0" and skill_info.author == "unknown":
            errors.append(f"Skill '{skill_name}' using default version with unknown author")
        
        # Category validation
        if skill_info.category == "general":
            logger.warning(f"Skill '{skill_name}' using generic category")
        
        # Parameter validation
        if not skill_info.parameters:
            errors.append(f"Skill '{skill_name}' has no documented parameters")
        
        return errors
    
    def generate_skill_index(self) -> Dict[str, Any]:
        """
        Generate a comprehensive skill index for documentation.
        
        Returns:
            Dict with skill metadata organized by category
        """
        index = {
            "total_skills": len(self.registry.list_skills()),
            "categories": {},
            "skills": {}
        }
        
        # Organize by category
        for category in self.registry.list_categories():
            skills_in_category = self.registry.list_skills(category)
            index["categories"][category] = {
                "count": len(skills_in_category),
                "skills": skills_in_category
            }
            
            # Add detailed skill info
            for skill_name in skills_in_category:
                skill_info = self.registry.get_info(skill_name)
                if skill_info:
                    index["skills"][skill_name] = {
                        "category": skill_info.category,
                        "description": skill_info.description,
                        "author": skill_info.author,
                        "version": skill_info.version,
                        "aliases": skill_info.aliases,
                        "tags": skill_info.tags,
                        "parameters": list(skill_info.parameters.keys())
                    }
        
        return index
    
    def lint_all_skills(self) -> Dict[str, List[str]]:
        """
        Lint all registered skills for OSS readiness.
        
        Returns:
            Dict mapping skill names to validation errors
        """
        results = {}
        
        for skill_name in self.registry.list_skills():
            errors = self.validate_skill_metadata(skill_name)
            if errors:
                results[skill_name] = errors
        
        return results
    
    def create_skill_manifest(self) -> Dict[str, Any]:
        """
        Create a manifest file for skill distribution.
        
        Returns:
            Manifest data suitable for packaging
        """
        return {
            "cogency_version": "1.0.0",
            "manifest_version": "1.0",
            "discovery_paths": self.discovery_paths,
            "skill_index": self.generate_skill_index(),
            "validation_results": self.lint_all_skills()
        }


# Global discovery instance
_global_discovery = SkillDiscovery()


def get_skill_discovery() -> SkillDiscovery:
    """Get the global skill discovery instance."""
    return _global_discovery


def discover_skills(paths: List[str] = None) -> Dict[str, int]:
    """
    Convenience function to discover skills.
    
    Args:
        paths: Optional list of discovery paths (uses defaults if None)
        
    Returns:
        Dict mapping path to number of skills discovered
    """
    discovery = get_skill_discovery()
    
    if paths:
        # Temporarily set paths
        original_paths = discovery.get_discovery_paths()
        discovery.discovery_paths = paths
        results = discovery.discover_all()
        discovery.discovery_paths = original_paths
    else:
        results = discovery.discover_all()
    
    return results


def validate_oss_readiness() -> bool:
    """
    Validate that all skills are ready for OSS contribution.
    
    Returns:
        True if all skills pass validation
    """
    discovery = get_skill_discovery()
    lint_results = discovery.lint_all_skills()
    
    if lint_results:
        logger.error("OSS readiness validation failed:")
        for skill_name, errors in lint_results.items():
            logger.error(f"  {skill_name}: {errors}")
        return False
    
    logger.info("All skills pass OSS readiness validation")
    return True


def generate_skill_docs() -> str:
    """Generate comprehensive skill documentation."""
    discovery = get_skill_discovery()
    return discovery.registry.generate_docs()