#!/usr/bin/env python3
"""
Command Line Interface for Robot Framework Self-Healing Library
==============================================================

Provides easy command-line access to self-healing functionality.
"""

import argparse
import sys
import os
import subprocess
from robot_selfheal import __version__
from robot_selfheal.candidate_algo import generate_enhanced_candidates
from robot_selfheal.self_healing_agent import SelfHealingAgent


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description=f"Robot Framework Self-Healing Library v{__version__}",
        epilog="For more help, visit: https://github.com/samarthindex9/selfhealing_library"
    )
    
    parser.add_argument(
        "--version", 
        action="version", 
        version=f"robot-selfheal {__version__}"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Test command - run Robot Framework with self-healing
    test_parser = subparsers.add_parser(
        "test", 
        help="Run Robot Framework tests with self-healing enabled"
    )
    test_parser.add_argument("test_files", nargs="+", help="Robot test files to run")
    test_parser.add_argument("--browser", default="chrome", help="Browser to use (default: chrome)")
    test_parser.add_argument("--output-dir", default="results", help="Output directory (default: results)")
    test_parser.add_argument("--extra-args", default="", help="Additional Robot Framework arguments")
    
    # Heal command - manually heal a locator
    heal_parser = subparsers.add_parser(
        "heal", 
        help="Manually heal a broken locator"
    )
    heal_parser.add_argument("locator", help="The broken locator to heal")
    heal_parser.add_argument("--mode", choices=["strict", "balanced", "lenient"], 
                           default="balanced", help="Healing mode (default: balanced)")
    heal_parser.add_argument("--threshold", type=int, help="Similarity threshold (0-100)")
    
    # Candidates command - generate candidate locators
    candidates_parser = subparsers.add_parser(
        "candidates", 
        help="Generate candidate locators for a broken locator"
    )
    candidates_parser.add_argument("locator", help="The broken locator")
    candidates_parser.add_argument("--mode", choices=["strict", "balanced", "lenient"], 
                                 default="balanced", help="Search mode (default: balanced)")
    candidates_parser.add_argument("--threshold", type=int, help="Similarity threshold (0-100)")
    candidates_parser.add_argument("--limit", type=int, default=10, help="Max candidates to show (default: 10)")
    
    # Init command - initialize self-healing in a project
    init_parser = subparsers.add_parser(
        "init", 
        help="Initialize self-healing in a Robot Framework project"
    )
    init_parser.add_argument("--project-dir", default=".", help="Project directory (default: current)")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    try:
        if args.command == "test":
            return run_tests(args)
        elif args.command == "heal":
            return heal_locator(args)
        elif args.command == "candidates":
            return generate_candidates_cmd(args)
        elif args.command == "init":
            return init_project(args)
    except Exception as e:
        print(f"❌ Error: {str(e)}", file=sys.stderr)
        return 1
    
    return 0


def run_tests(args):
    """Run Robot Framework tests with self-healing enabled"""
    print(f"🤖 Running Robot Framework tests with self-healing enabled...")
    
    # Build Robot Framework command
    robot_cmd = [
        "robot", 
        "--listener", "robot_selfheal.SelfHealListener",
        "--outputdir", args.output_dir,
        "--variable", f"BROWSER:{args.browser}"
    ]
    
    # Add extra arguments if provided
    if args.extra_args:
        robot_cmd.extend(args.extra_args.split())
    
    # Add test files
    robot_cmd.extend(args.test_files)
    
    print(f"🚀 Executing: {' '.join(robot_cmd)}")
    
    # Run Robot Framework
    result = subprocess.run(robot_cmd)
    
    if result.returncode == 0:
        print("✅ Tests completed successfully with self-healing!")
    else:
        print("⚠️ Tests completed with some failures (self-healing may have helped)")
    
    return result.returncode


def heal_locator(args):
    """Manually heal a broken locator"""
    print(f"🔧 Healing locator: {args.locator}")
    
    try:
        agent = SelfHealingAgent()
        result = agent.heal_locator(args.locator)
        
        if result:
            print("\n✅ Healing successful!")
            print(f"📝 Suggested locator: {result.get('correct_locator', 'N/A')}")
            print(f"💡 Solution: {result.get('solution_description', 'N/A')}")
            
            # Display variable info if available
            var_info = result.get('variable_info', {})
            if var_info:
                print(f"📄 Variable: {var_info.get('variable_name', 'N/A')}")
                print(f"📁 Source file: {var_info.get('source_file', 'N/A')}")
        else:
            print("❌ Healing failed - no suitable alternatives found")
            return 1
            
    except Exception as e:
        print(f"❌ Healing error: {str(e)}")
        return 1
    
    return 0


def generate_candidates_cmd(args):
    """Generate candidate locators"""
    print(f"🔍 Generating candidates for: {args.locator}")
    print(f"🎯 Mode: {args.mode}")
    if args.threshold:
        print(f"📊 Threshold: {args.threshold}")
    
    try:
        result = generate_enhanced_candidates(
            args.locator, 
            threshold=args.threshold,
            mode=args.mode
        )
        
        candidates = result.get("candidates", [])
        
        if not candidates:
            print("❌ No candidates found")
            return 1
        
        print(f"\n✅ Found {len(candidates)} candidates:")
        print("=" * 80)
        
        # Display top candidates
        for i, candidate in enumerate(candidates[:args.limit], 1):
            print(f"\n{i}. Similarity: {candidate.get('similarity', 'N/A')}%")
            print(f"   XPath: {candidate.get('xpath', 'N/A')}")
            print(f"   Tag: {candidate.get('tag', 'N/A')}")
            print(f"   ID: {candidate.get('id', 'N/A') or 'None'}")
            print(f"   Class: {candidate.get('class', 'N/A') or 'None'}")
            print(f"   Text: {candidate.get('text', 'N/A')[:50]}{'...' if len(candidate.get('text', '')) > 50 else ''}")
            print(f"   Confidence: {candidate.get('correction_rate', 'N/A')}")
        
        if len(candidates) > args.limit:
            print(f"\n... and {len(candidates) - args.limit} more candidates")
        
        print(f"\n📊 Total candidates found: {result.get('total_found', 0)}")
        print(f"📁 Files processed: {result.get('files_processed', 0)}")
        
    except Exception as e:
        print(f"❌ Error generating candidates: {str(e)}")
        return 1
    
    return 0


def init_project(args):
    """Initialize self-healing in a Robot Framework project"""
    project_dir = os.path.abspath(args.project_dir)
    print(f"🏗️ Initializing self-healing in: {project_dir}")
    
    try:
        # Create Environment directory
        env_dir = os.path.join(project_dir, "Environment")
        os.makedirs(env_dir, exist_ok=True)
        print(f"✅ Created directory: {env_dir}")
        
        # Create config.json
        config_path = os.path.join(env_dir, "config.json")
        if not os.path.exists(config_path):
            config_content = '''{
    "data_path": "locator_data",
    "page_objects_dir": "PageObjects",
    "page_sources_dir": "locator_data/page_sources",
    "results_dir": "results",
    "locator_data": {
        "healing_prompts": "healing_prompts.json",
        "healed_locators": "healed_locators.json",
        "locator_failures": "locator_failures.json"
    }
}'''
            with open(config_path, 'w') as f:
                f.write(config_content)
            print(f"✅ Created config file: {config_path}")
        else:
            print(f"ℹ️ Config file already exists: {config_path}")
        
        # Create .env template
        env_file_path = os.path.join(env_dir, ".env")
        if not os.path.exists(env_file_path):
            env_content = '''# OpenAI API Key for self-healing
OPENAI_API_KEY=your_openai_api_key_here
'''
            with open(env_file_path, 'w') as f:
                f.write(env_content)
            print(f"✅ Created .env template: {env_file_path}")
            print("⚠️ Don't forget to add your OpenAI API key to the .env file!")
        else:
            print(f"ℹ️ .env file already exists: {env_file_path}")
        
        # Create PageObjects directory
        pageobjects_dir = os.path.join(project_dir, "PageObjects")
        os.makedirs(pageobjects_dir, exist_ok=True)
        print(f"✅ Created directory: {pageobjects_dir}")
        
        # Create example test file
        testcases_dir = os.path.join(project_dir, "TestCases")
        os.makedirs(testcases_dir, exist_ok=True)
        
        example_test_path = os.path.join(testcases_dir, "example_selfheal.robot")
        if not os.path.exists(example_test_path):
            example_test_content = '''*** Settings ***
Library    robot_selfheal.SelfHeal

*** Test Cases ***
Example Test With Self-Healing
    [Documentation]    Example test demonstrating self-healing capabilities
    Log    Self-healing is now enabled for this test!
    # Your test steps here - any failing locators will be automatically healed
'''
            with open(example_test_path, 'w') as f:
                f.write(example_test_content)
            print(f"✅ Created example test: {example_test_path}")
        
        print(f"\n🎉 Self-healing initialization complete!")
        print(f"\n📖 Next steps:")
        print(f"   1. Add your OpenAI API key to: {env_file_path}")
        print(f"   2. Create your page object files in: {pageobjects_dir}")
        print(f"   3. Run tests with: robot-selfheal test TestCases/")
        print(f"   4. Or use as library: Library    robot_selfheal.SelfHeal")
        
    except Exception as e:
        print(f"❌ Initialization error: {str(e)}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main()) 