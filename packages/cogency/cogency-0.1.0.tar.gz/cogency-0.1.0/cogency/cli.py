"""
CLI interface for cogency skill management.

Provides command-line tools for skill discovery, validation, and documentation.
"""

import argparse
import json
import sys
from typing import Dict, Any, List
from pathlib import Path

from .skills.registry import get_skill_registry, create_skill_factory
from .discovery import (
    get_skill_discovery, 
    discover_skills, 
    validate_oss_readiness,
    generate_skill_docs
)


def cmd_list_skills(args) -> None:
    """List all registered skills."""
    registry = get_skill_registry()
    
    if args.category:
        skills = registry.list_skills(args.category)
        print(f"Skills in category '{args.category}':")
    else:
        skills = registry.list_skills()
        print("All registered skills:")
    
    for skill_name in sorted(skills):
        skill_info = registry.get_info(skill_name)
        if skill_info:
            print(f"  {skill_name} - {skill_info.description}")
            if args.verbose:
                print(f"    Author: {skill_info.author}")
                print(f"    Version: {skill_info.version}")
                print(f"    Category: {skill_info.category}")
                if skill_info.aliases:
                    print(f"    Aliases: {', '.join(skill_info.aliases)}")
                if skill_info.tags:
                    print(f"    Tags: {', '.join(skill_info.tags)}")
                print()


def cmd_search_skills(args) -> None:
    """Search for skills by query."""
    registry = get_skill_registry()
    results = registry.search(args.query)
    
    print(f"Skills matching '{args.query}':")
    for skill_name in sorted(results):
        skill_info = registry.get_info(skill_name)
        if skill_info:
            print(f"  {skill_name} - {skill_info.description}")


def cmd_skill_info(args) -> None:
    """Show detailed information about a skill."""
    registry = get_skill_registry()
    skill_info = registry.get_info(args.skill_name)
    
    if not skill_info:
        print(f"Skill '{args.skill_name}' not found")
        sys.exit(1)
    
    print(f"Skill: {skill_info.name}")
    print(f"Description: {skill_info.description}")
    print(f"Category: {skill_info.category}")
    print(f"Author: {skill_info.author}")
    print(f"Version: {skill_info.version}")
    
    if skill_info.aliases:
        print(f"Aliases: {', '.join(skill_info.aliases)}")
    
    if skill_info.tags:
        print(f"Tags: {', '.join(skill_info.tags)}")
    
    if skill_info.parameters:
        print("\nParameters:")
        for param_name, param_info in skill_info.parameters.items():
            annotation = param_info.get('annotation', 'Any')
            default = param_info.get('default')
            default_str = f" = {default}" if default is not None else ""
            print(f"  {param_name}: {annotation}{default_str}")


def cmd_discover_skills(args) -> None:
    """Discover skills from configured paths."""
    if args.paths:
        paths = args.paths
    else:
        discovery = get_skill_discovery()
        paths = discovery.get_discovery_paths()
    
    results = discover_skills(paths)
    
    print("Skill discovery results:")
    for path, count in results.items():
        print(f"  {path}: {count} skills")
    
    total = sum(results.values())
    print(f"\nTotal skills discovered: {total}")


def cmd_validate_oss(args) -> None:
    """Validate skills for OSS readiness."""
    discovery = get_skill_discovery()
    lint_results = discovery.lint_all_skills()
    
    if not lint_results:
        print("✅ All skills pass OSS readiness validation")
        return
    
    print("❌ OSS readiness validation failed:")
    for skill_name, errors in lint_results.items():
        print(f"\n{skill_name}:")
        for error in errors:
            print(f"  - {error}")
    
    if args.fix:
        print("\n💡 Suggestions:")
        print("  - Add descriptions to skills missing them")
        print("  - Set proper author names instead of 'unknown'")
        print("  - Use semantic versioning")
        print("  - Add appropriate categories")
        print("  - Document parameters in function signatures")


def cmd_generate_docs(args) -> None:
    """Generate skill documentation."""
    from .skills.registry import get_skill_registry
    
    registry = get_skill_registry()
    format_type = getattr(args, 'format', 'markdown')
    
    if format_type == 'github':
        docs = registry.generate_docs(format_type='github')
    else:
        docs = registry.generate_docs(format_type='markdown')
    
    if args.output:
        with open(args.output, 'w') as f:
            f.write(docs)
        print(f"Documentation written to {args.output}")
    else:
        print(docs)


def cmd_skill_index(args) -> None:
    """Generate skill index."""
    discovery = get_skill_discovery()
    index = discovery.generate_skill_index()
    
    if args.format == 'json':
        output = json.dumps(index, indent=2)
    else:
        output = _format_index_text(index)
    
    if args.output:
        with open(args.output, 'w') as f:
            f.write(output)
        print(f"Index written to {args.output}")
    else:
        print(output)


def cmd_create_manifest(args) -> None:
    """Create skill manifest."""
    discovery = get_skill_discovery()
    manifest = discovery.create_skill_manifest()
    
    with open(args.output, 'w') as f:
        json.dump(manifest, f, indent=2)
    
    print(f"Manifest written to {args.output}")


def _format_index_text(index: Dict[str, Any]) -> str:
    """Format skill index as text."""
    lines = [f"Skill Index - {index['total_skills']} skills\n"]
    
    for category, info in index['categories'].items():
        lines.append(f"## {category.title()} ({info['count']} skills)")
        
        for skill_name in sorted(info['skills']):
            skill_data = index['skills'][skill_name]
            lines.append(f"  {skill_name} - {skill_data['description']}")
        
        lines.append("")
    
    return "\n".join(lines)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Cogency skill management CLI",
        prog="cogency"
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # List skills command
    list_parser = subparsers.add_parser('list', help='List registered skills')
    list_parser.add_argument('--category', help='Filter by category')
    list_parser.add_argument('--verbose', '-v', action='store_true', help='Show detailed info')
    list_parser.set_defaults(func=cmd_list_skills)
    
    # Search skills command
    search_parser = subparsers.add_parser('search', help='Search for skills')
    search_parser.add_argument('query', help='Search query')
    search_parser.set_defaults(func=cmd_search_skills)
    
    # Skill info command
    info_parser = subparsers.add_parser('info', help='Show skill information')
    info_parser.add_argument('skill_name', help='Name of skill to show')
    info_parser.set_defaults(func=cmd_skill_info)
    
    # Discover skills command
    discover_parser = subparsers.add_parser('discover', help='Discover skills')
    discover_parser.add_argument('--paths', nargs='+', help='Discovery paths')
    discover_parser.set_defaults(func=cmd_discover_skills)
    
    # Validate OSS readiness command
    validate_parser = subparsers.add_parser('validate', help='Validate OSS readiness')
    validate_parser.add_argument('--fix', action='store_true', help='Show fix suggestions')
    validate_parser.set_defaults(func=cmd_validate_oss)
    
    # Generate docs command
    docs_parser = subparsers.add_parser('docs', help='Generate documentation')
    docs_parser.add_argument('--output', '-o', help='Output file (default: stdout)')
    docs_parser.add_argument('--format', choices=['markdown', 'github'], default='markdown', help='Documentation format')
    docs_parser.set_defaults(func=cmd_generate_docs)
    
    # Skill index command
    index_parser = subparsers.add_parser('index', help='Generate skill index')
    index_parser.add_argument('--format', choices=['text', 'json'], default='text', help='Output format')
    index_parser.add_argument('--output', '-o', help='Output file (default: stdout)')
    index_parser.set_defaults(func=cmd_skill_index)
    
    # Create manifest command
    manifest_parser = subparsers.add_parser('manifest', help='Create skill manifest')
    manifest_parser.add_argument('output', help='Output file path')
    manifest_parser.set_defaults(func=cmd_create_manifest)
    
    # Parse and execute
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Auto-discover skills before running commands
    discover_skills()
    
    # Execute command
    args.func(args)


if __name__ == '__main__':
    main()