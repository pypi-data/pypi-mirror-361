"""
Robot Framework Self-Healing Library

A powerful self-healing library that automatically detects and fixes broken locators 
in Robot Framework tests, reducing maintenance overhead and improving test reliability.

Authors: Samarth Math (Manager), Vikas Gupta, Onkar Pawar
License: MIT
"""

__version__ = "2.1.0"
__author__ = "Samarth Math, Vikas Gupta, Onkar Pawar"
__license__ = "MIT"
__email__ = "samarth.math@indexnine.com, vikas.gupta@indexnine.com, onkar.pawar@indexnine.com"

from robot.api import logger
from robot.libraries.BuiltIn import BuiltIn
from robot_selfheal.SelfHealListener import SelfHealListener
from robot_selfheal.self_healing_agent import SelfHealingAgent
from robot_selfheal.candidate_algo import generate_enhanced_candidates, generate_best_candidates

# Make key classes and functions available at package level
__all__ = [
    'SelfHeal',
    'SelfHealListener', 
    'SelfHealingAgent',
    'generate_enhanced_candidates',
    'generate_best_candidates',
]

class SelfHeal:
    """Robot Framework library that auto-registers a self-healing listener."""

    ROBOT_LIBRARY_SCOPE = 'GLOBAL'
    ROBOT_LIBRARY_VERSION = __version__

    def __init__(self):
        """Initialize the SelfHeal library with automatic listener registration."""
        try:
            # Register the listener automatically
            self.listener = SelfHealListener()
            BuiltIn().set_library_search_order('SelfHeal')
            logger.console(f"✅ SelfHeal Library v{__version__} loaded and listener registered successfully.")
        except Exception as e:
            logger.console(f"❌ Error initializing SelfHeal Library: {str(e)}")
            raise

    def get_version(self):
        """Get the library version."""
        return __version__

    def heal_locator(self, locator):
        """
        Manually heal a broken locator.
        
        Args:
            locator (str): The broken locator to heal
            
        Returns:
            dict: Healing result with suggested fixes
        """
        try:
            agent = SelfHealingAgent()
            return agent.heal_locator(locator)
        except Exception as e:
            logger.console(f"❌ Error healing locator: {str(e)}")
            return None

    def generate_candidates(self, locator, mode="balanced", threshold=None):
        """
        Generate candidate locators for a given broken locator.
        
        Args:
            locator (str): The broken locator
            mode (str): Search mode - "strict", "balanced", or "lenient"
            threshold (int): Similarity threshold (0-100)
            
        Returns:
            dict: Candidate generation results
        """
        try:
            return generate_enhanced_candidates(locator, threshold, None, mode)
        except Exception as e:
            logger.console(f"❌ Error generating candidates: {str(e)}")
            return {"candidates": [], "total_found": 0, "error": str(e)}

# For backward compatibility and easy imports
SelfHealingLibrary = SelfHeal  # Alias
