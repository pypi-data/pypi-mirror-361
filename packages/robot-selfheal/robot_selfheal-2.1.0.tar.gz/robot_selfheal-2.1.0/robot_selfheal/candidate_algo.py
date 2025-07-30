"""
Comprehensive Candidate Algorithm for Self-Healing
=================================================

This is a merged version combining features from both original and enhanced algorithms:
1. Enhanced scoring mechanisms with multiple strategies
2. Improved tag mismatch detection and semantic equivalency 
3. Multiple text similarity calculation methods
4. DOM context analysis and structure scoring
5. Locator simplification strategies
6. Adaptive thresholds for different locator types
7. Backward compatibility with original functions
"""

import json
import os
from bs4 import BeautifulSoup
from lxml import etree
from rapidfuzz import fuzz
from robot.libraries.BuiltIn import BuiltIn
import re
from typing import List, Dict, Optional, Tuple
from datetime import datetime

def load_config():
    """Load configuration from config.json"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.dirname(current_dir)
    config_path = os.path.join(base_dir, 'Environment', 'config.json')
    
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuration file not found at {config_path}")

    with open(config_path, 'r') as config_file:
        config = json.load(config_file)
    
    return config, base_dir

# Load configuration
config, base_dir = load_config()
page_sources_dir = os.path.join(base_dir, config.get('page_sources_dir'))

# ============================================================================
# UTILITY FUNCTIONS (Enhanced versions with backward compatibility)
# ============================================================================

def load_page_source(page_source_path):
    """Loads the page source from an HTML file."""
    with open(page_source_path, 'r', encoding='utf-8') as source_file:
        return source_file.read()

def is_unique_xpath(tree, xpath_expr):
    """Check if XPath expression returns exactly one element"""
    try:
        return len(tree.xpath(xpath_expr)) == 1
    except Exception:
        return False

def get_dom_depth(element):
    """Calculate DOM depth of an element"""
    depth = 0
    current = element.parent
    while current and current.name and current.name != '[document]':
        depth += 1
        current = current.parent
    return depth

def extract_tag_from_locator(locator):
    """Extract expected tag type from locator"""
    if locator.startswith('//'):
        # Extract tag from XPath like //div, //input[@id='test'], etc.
        match = re.match(r'//([a-zA-Z0-9\-_]+)', locator)
        if match:
            return match.group(1).lower()
    elif locator.startswith('id=') or locator.startswith('name=') or locator.startswith('class='):
        # For attribute-based locators, we can't determine tag type
        return None
    return None

def extract_text_from_locator(locator):
    """Enhanced text extraction from text-based locators"""
    text_patterns = [
        # contains(text(), 'text')
        r"contains\(text\(\),\s*['\"]([^'\"]+)['\"]",
        # text()='text'
        r"text\(\)\s*=\s*['\"]([^'\"]+)['\"]",
        # [text()='text']
        r"\[text\(\)\s*=\s*['\"]([^'\"]+)['\"]\]",
        # [@text='text'] or similar
        r"@text\s*=\s*['\"]([^'\"]+)['\"]"
    ]
    
    for pattern in text_patterns:
        match = re.search(pattern, locator, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    
    return None

def normalize_text(text):
    """Enhanced text normalization for better matching"""
    if not text:
        return ""
    # Remove extra whitespace, newlines, and normalize
    normalized = re.sub(r'\s+', ' ', text.strip())
    # Remove common suffixes that might cause mismatches
    normalized = re.sub(r'\s+(item|element|link|button|text)\s*$', '', normalized, flags=re.IGNORECASE)
    # Remove special characters that might cause issues
    normalized = re.sub(r'[^\w\s]', '', normalized)
    return normalized.lower()

def calculate_text_similarity(target_text, element_text, locator):
    """Enhanced text similarity calculation for text-based locators"""
    if not target_text or not element_text:
        return 0
    
    target_normalized = normalize_text(target_text)
    element_normalized = normalize_text(element_text)
    
    # Exact match gets highest score
    if target_normalized == element_normalized:
        return 100
    
    # Check if target text is contained in element text (for contains() locators)
    if "contains(text()" in locator:
        if target_normalized in element_normalized:
            return 95
        
        # Partial word matching for contains
        target_words = target_normalized.split()
        element_words = element_normalized.split()
        
        # Check if all target words are present
        matches = sum(1 for word in target_words if word in element_words)
        if matches == len(target_words):
            return 85
        
        # Partial word matching
        if matches > 0:
            return 60 + (matches / len(target_words)) * 25
    
    # Use fuzzy matching as fallback
    ratio = fuzz.ratio(target_normalized, element_normalized)
    partial_ratio = fuzz.partial_ratio(target_normalized, element_normalized)
    token_ratio = fuzz.token_sort_ratio(target_normalized, element_normalized)
    
    return max(ratio, partial_ratio, token_ratio)

def calculate_dom_similarity(original_locator, candidate_element):
    """Calculate DOM context similarity between original locator and candidate"""
    score = 0
    
    # Extract attributes from original locator for context comparison
    original_attrs = {}
    
    # Parse XPath attributes
    if original_locator.startswith('//'):
        # Extract attributes from XPath like [@id='test'] or [@class='btn']
        attr_matches = re.findall(r'@([a-zA-Z-]+)\s*=\s*[\'"]([^\'"]*)[\'"]', original_locator)
        for attr_name, attr_value in attr_matches:
            original_attrs[attr_name] = attr_value
    
    # Compare attributes if we found any in original locator
    if original_attrs:
        for attr_name, attr_value in original_attrs.items():
            candidate_attr = candidate_element.get(attr_name, "")
            if attr_name == 'class':
                candidate_attr = " ".join(candidate_element.get("class", []))
            
            if candidate_attr:
                # Use fuzzy matching for attribute values
                attr_similarity = fuzz.ratio(attr_value.lower(), candidate_attr.lower())
                score += attr_similarity * 0.3  # Weight attribute similarity
    
    # Check sibling context (elements at same level)
    siblings = candidate_element.parent.find_all(recursive=False) if candidate_element.parent else []
    sibling_tags = [s.name for s in siblings if s.name]
    
    # Extract expected sibling context from original locator
    if 'following-sibling' in original_locator or 'preceding-sibling' in original_locator:
        score += 20  # Bonus for having sibling-aware locators
    
    return min(score, 100)  # Cap at 100

# ============================================================================
# ENHANCED SCORING SYSTEM
# ============================================================================

class EnhancedCandidateScorer:
    """Enhanced scoring system for better candidate evaluation"""
    
    def __init__(self):
        # Enhanced scoring weights based on reliability
        self.attribute_weights = {
            'id': 50,           # Most reliable
            'data-testid': 45,  # Test-specific attributes
            'data-cy': 45,      # Cypress test attributes
            'data-qa': 45,      # QA test attributes
            'name': 40,         # Form elements
            'aria-label': 35,   # Accessibility attributes
            'role': 30,         # Semantic roles
            'class': 25,        # Can be fragile but useful
            'type': 20,         # Input types
            'href': 15,         # Links
            'src': 10,          # Images
            'title': 10,        # Tooltip text
            'placeholder': 8,   # Input placeholders
            'alt': 5            # Image alt text
        }
        
        # Tag reliability scores
        self.tag_reliability = {
            'input': 10,    # Form elements are stable
            'button': 9,    # Buttons are stable
            'a': 8,         # Links are fairly stable
            'select': 8,    # Form selects
            'textarea': 8,  # Form textareas
            'label': 7,     # Labels
            'img': 6,       # Images
            'span': 4,      # Generic inline elements
            'div': 3,       # Generic block elements
            'p': 5,         # Paragraphs
            'h1': 8, 'h2': 8, 'h3': 8, 'h4': 8, 'h5': 8, 'h6': 8,  # Headers
        }
        
        # Text matching improvements
        self.text_weight_multiplier = {
            'exact_match': 3.0,
            'case_insensitive_exact': 2.8,
            'contains_all_words': 2.5,
            'contains_most_words': 2.0,
            'partial_match': 1.5,
            'fuzzy_high': 1.3,
            'fuzzy_medium': 1.0
        }
    
    def calculate_enhanced_score(self, original_locator, candidate_element, dom_context=None):
        """Calculate enhanced similarity score with multiple factors"""
        
        scores = {
            'attribute_score': 0,
            'tag_score': 0,
            'text_score': 0,
            'structure_score': 0,
            'reliability_score': 0,
            'total_score': 0
        }
        
        # 1. Enhanced Attribute Scoring
        scores['attribute_score'] = self._calculate_attribute_score(original_locator, candidate_element)
        
        # 2. Tag Matching and Mismatch Detection
        scores['tag_score'] = self._calculate_tag_score(original_locator, candidate_element)
        
        # 3. Enhanced Text Matching
        scores['text_score'] = self._calculate_text_score(original_locator, candidate_element)
        
        # 4. DOM Structure Analysis
        scores['structure_score'] = self._calculate_structure_score(original_locator, candidate_element, dom_context)
        
        # 5. Element Reliability Score
        scores['reliability_score'] = self._calculate_reliability_score(candidate_element)
        
        # Calculate weighted total
        weights = {
            'attribute_score': 0.35,
            'tag_score': 0.20,
            'text_score': 0.25,
            'structure_score': 0.10,
            'reliability_score': 0.10
        }
        
        total_score = sum(scores[key] * weights[key] for key in weights)
        scores['total_score'] = min(100, total_score)  # Cap at 100
        
        return scores, total_score
    
    def _calculate_attribute_score(self, original_locator, candidate_element):
        """Enhanced attribute scoring with better weight distribution"""
        score = 0
        max_possible_score = 0
        
        # Extract attributes from original locator
        original_attributes = self._extract_attributes_from_locator(original_locator)
        
        for attr_name, expected_value in original_attributes.items():
            weight = self.attribute_weights.get(attr_name, 5)  # Default weight for unknown attributes
            max_possible_score += weight
            
            # Get candidate's attribute value
            candidate_value = candidate_element.get(attr_name, '')
            if attr_name == 'class':
                candidate_value = ' '.join(candidate_element.get('class', []))
            
            if not candidate_value:
                continue
            
            # Calculate attribute similarity
            if attr_name == 'class':
                # Special handling for class attributes
                similarity = self._calculate_class_similarity(expected_value, candidate_value)
            else:
                # Exact match gets full score
                if expected_value == candidate_value:
                    similarity = 100
                # Partial match for contains operations
                elif expected_value in candidate_value or candidate_value in expected_value:
                    similarity = 80
                # Fuzzy matching for typos
                else:
                    similarity = fuzz.ratio(expected_value, candidate_value)
            
            # Apply similarity to weight
            score += (similarity / 100) * weight
        
        # Normalize score (0-100)
        if max_possible_score > 0:
            return (score / max_possible_score) * 100
        
        return 0
    
    def _calculate_class_similarity(self, expected_classes, candidate_classes):
        """Calculate similarity for class attributes"""
        expected_set = set(expected_classes.split())
        candidate_set = set(candidate_classes.split())
        
        if not expected_set:
            return 0
        
        # Calculate Jaccard similarity
        intersection = expected_set.intersection(candidate_set)
        union = expected_set.union(candidate_set)
        
        if not union:
            return 0
        
        jaccard_similarity = len(intersection) / len(union)
        
        # Bonus for exact subset match
        if expected_set.issubset(candidate_set):
            jaccard_similarity += 0.3
        
        return min(100, jaccard_similarity * 100)
    
    def _calculate_tag_score(self, original_locator, candidate_element):
        """Enhanced tag scoring with mismatch detection"""
        expected_tag = self._extract_tag_from_locator(original_locator)
        if not expected_tag:
            return 50  # Neutral score if no tag specified
        
        candidate_tag = candidate_element.name.lower()
        expected_tag = expected_tag.lower()
        
        # Exact tag match
        if candidate_tag == expected_tag:
            return 100
        
        # Check for semantically equivalent tags
        semantic_equivalents = {
            'span': ['a', 'label', 'div'],
            'div': ['section', 'article', 'span'],
            'a': ['button', 'span'],
            'button': ['a', 'input'],
            'input': ['button'],
        }
        
        if expected_tag in semantic_equivalents:
            if candidate_tag in semantic_equivalents[expected_tag]:
                return 70  # Good score for semantic equivalent
        
        # Fuzzy tag matching for typos
        tag_similarity = fuzz.ratio(expected_tag, candidate_tag)
        if tag_similarity > 80:
            return 60
        
        # Check for functional equivalence (both are interactive elements)
        interactive_tags = {'a', 'button', 'input', 'select', 'textarea'}
        if expected_tag in interactive_tags and candidate_tag in interactive_tags:
            return 50
        
        # Poor tag match
        return 20
    
    def _calculate_text_score(self, original_locator, candidate_element):
        """Enhanced text matching with multiple strategies"""
        expected_text = self._extract_text_from_locator(original_locator)
        if not expected_text:
            return 50  # Neutral score if no text expected
        
        candidate_text = candidate_element.get_text(strip=True)
        if not candidate_text:
            return 0
        
        # Normalize texts
        expected_normalized = normalize_text(expected_text)
        candidate_normalized = normalize_text(candidate_text)
        
        # Multiple text matching strategies
        strategies = []
        
        # 1. Exact match
        if expected_normalized == candidate_normalized:
            strategies.append(('exact_match', 100))
        
        # 2. Case-insensitive exact match
        elif expected_normalized.lower() == candidate_normalized.lower():
            strategies.append(('case_insensitive_exact', 95))
        
        # 3. Contains all words
        expected_words = set(expected_normalized.lower().split())
        candidate_words = set(candidate_normalized.lower().split())
        
        if expected_words and expected_words.issubset(candidate_words):
            strategies.append(('contains_all_words', 90))
        
        # 4. Contains most words
        if expected_words:
            word_overlap = len(expected_words.intersection(candidate_words)) / len(expected_words)
            if word_overlap >= 0.8:
                strategies.append(('contains_most_words', 80))
            elif word_overlap >= 0.6:
                strategies.append(('partial_match', 60))
        
        # 5. Fuzzy matching
        fuzzy_score = fuzz.ratio(expected_normalized.lower(), candidate_normalized.lower())
        if fuzzy_score >= 80:
            strategies.append(('fuzzy_high', fuzzy_score))
        elif fuzzy_score >= 60:
            strategies.append(('fuzzy_medium', fuzzy_score))
        
        # 6. Partial ratio for contains operations
        partial_ratio = fuzz.partial_ratio(expected_normalized.lower(), candidate_normalized.lower())
        if partial_ratio >= 80:
            strategies.append(('partial_match', partial_ratio))
        
        # Return best strategy result
        if strategies:
            best_strategy, score = max(strategies, key=lambda x: x[1])
            multiplier = self.text_weight_multiplier.get(best_strategy, 1.0)
            return min(100, score * multiplier)
        
        return 0
    
    def _calculate_structure_score(self, original_locator, candidate_element, dom_context):
        """Calculate DOM structure similarity score"""
        score = 50  # Base score
        
        # Analyze parent/child relationships
        if candidate_element.parent:
            parent_tag = candidate_element.parent.name
            
            # Check if parent context makes sense
            semantic_parents = {
                'a': ['nav', 'ul', 'ol', 'li', 'div'],
                'li': ['ul', 'ol'],
                'option': ['select'],
                'td': ['tr'],
                'tr': ['table', 'tbody', 'thead']
            }
            
            candidate_tag = candidate_element.name
            if candidate_tag in semantic_parents:
                if parent_tag in semantic_parents[candidate_tag]:
                    score += 20
        
        # Check sibling context
        siblings = [s.name for s in candidate_element.parent.children if hasattr(s, 'name')]
        if len(siblings) > 1:
            # Multiple similar siblings suggest a list/menu structure
            if siblings.count(candidate_element.name) > 1:
                score += 10
        
        # Check for navigation/menu context
        nav_indicators = ['nav', 'menu', 'sidebar', 'toolbar']
        element_context = str(candidate_element.parent)[:200].lower()
        
        if any(indicator in element_context for indicator in nav_indicators):
            score += 15
        
        return min(100, score)
    
    def _calculate_reliability_score(self, candidate_element):
        """Calculate element reliability based on its characteristics"""
        score = 50  # Base score
        
        # Tag reliability
        tag_reliability = self.tag_reliability.get(candidate_element.name, 3)
        score += tag_reliability * 2
        
        # Presence of stable attributes
        stable_attrs = ['id', 'data-testid', 'data-cy', 'data-qa', 'name']
        for attr in stable_attrs:
            if candidate_element.get(attr):
                score += 10
                break  # Only count once
        
        # Avoid elements with generated/dynamic classes
        classes = candidate_element.get('class', [])
        dynamic_patterns = [r'\d{4,}', r'[a-f0-9]{8,}', r'tmp-', r'gen-', r'auto-']
        
        for class_name in classes:
            if any(re.search(pattern, class_name) for pattern in dynamic_patterns):
                score -= 10
                break
        
        # Check for semantic HTML
        semantic_tags = ['button', 'nav', 'main', 'section', 'article', 'header', 'footer']
        if candidate_element.name in semantic_tags:
            score += 10
        
        return min(100, max(0, score))
    
    def _extract_attributes_from_locator(self, locator):
        """Extract attribute-value pairs from XPath locator"""
        attributes = {}
        
        # Pattern to match [@attribute='value'] or [@attribute="value"]
        attr_pattern = r'@([a-zA-Z-]+)\s*=\s*[\'"]([^\'"]*)[\'"]'
        matches = re.findall(attr_pattern, locator)
        
        for attr_name, attr_value in matches:
            attributes[attr_name] = attr_value
        
        return attributes
    
    def _extract_tag_from_locator(self, locator):
        """Extract expected tag from XPath locator"""
        if locator.startswith('//'):
            match = re.match(r'//([a-zA-Z0-9\-_]+)', locator)
            if match:
                return match.group(1).lower()
        return None
    
    def _extract_text_from_locator(self, locator):
        """Enhanced text extraction from text-based locators"""
        text_patterns = [
            r"contains\(text\(\),\s*['\"]([^'\"]+)['\"]",
            r"text\(\)\s*=\s*['\"]([^'\"]+)['\"]",
            r"\[text\(\)\s*=\s*['\"]([^'\"]+)['\"]\]",
            r"@text\s*=\s*['\"]([^'\"]+)['\"]"
        ]
        
        for pattern in text_patterns:
            match = re.search(pattern, locator, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return None

# ============================================================================
# ASSESSMENT AND CORRECTION FUNCTIONS (Enhanced versions)
# ============================================================================

def assess_correction_rate(original, candidate):
    """Enhanced assessment with better text matching consideration"""
    confidence_score = 0
    
    # High confidence indicators
    if candidate["id"] and candidate["id"] in original:
        confidence_score += 40
    if candidate["name"] and candidate["name"] in original:
        confidence_score += 35
    if candidate["class"] and any(cls in original for cls in candidate["class"].split()):
        confidence_score += 25
    
    # Medium confidence indicators
    if candidate["tag"] and candidate["tag"] in original:
        confidence_score += 20
    if candidate["type"] and candidate["type"] in original:
        confidence_score += 15
    
    # Enhanced text relevance scoring
    target_text = extract_text_from_locator(original)
    if target_text and candidate["text"]:
        text_similarity = calculate_text_similarity(target_text, candidate["text"], original)
        if text_similarity >= 95:
            confidence_score += 30  # High bonus for excellent text match
        elif text_similarity >= 80:
            confidence_score += 20  # Good text match
        elif text_similarity >= 60:
            confidence_score += 10  # Decent text match
    
    # DOM stability factors
    dom_depth = candidate.get("dom_depth", 0)
    if dom_depth <= 5:  # Shallow elements are generally more stable
        confidence_score += 10
    elif dom_depth > 10:  # Very deep elements might be unstable
        confidence_score -= 5
    
    # Determine correction rate based on total confidence
    if confidence_score >= 85:
        return "HIGH"
    elif confidence_score >= 60:
        return "MEDIUM"
    elif confidence_score >= 35:
        return "LOW"
    else:
        return "VERY_LOW"

def determine_adaptive_threshold(locator):
    """Enhanced threshold determination with better text-based locator handling"""
    base_threshold = 60  # Lowered base threshold
    
    # Much lower threshold for text-based locators
    if "contains(text()" in locator or "text()=" in locator:
        return 40  # Very lenient for text matching
    
    # Lower threshold for complex locators
    if len(locator) > 100:
        return base_threshold - 15
    elif 'contains(' in locator:
        return base_threshold - 10
    elif locator.count('[') > 2:  # Multiple conditions
        return base_threshold - 5
    
    # Higher threshold for simple, specific locators
    if locator.startswith('//') and locator.count('/') <= 3:
        return base_threshold + 10
    
    return base_threshold

# ============================================================================
# LOCATOR SIMPLIFICATION STRATEGIES
# ============================================================================

class EnhancedLocatorSimplifier:
    """Generates simplified variants of complex locators"""
    
    def __init__(self):
        self.simplification_strategies = [
            self._remove_visibility_conditions,
            self._remove_ancestor_conditions,
            self._remove_context_path,
            self._simplify_text_matching,
            self._remove_complex_attributes,
            self._try_direct_selectors
        ]
    
    def generate_simplified_variants(self, original_locator):
        """Generate progressively simpler variants of the locator"""
        variants = []
        current_locator = original_locator
        
        print(f"🔧 Generating simplified variants for: {original_locator}")
        
        for strategy in self.simplification_strategies:
            try:
                simplified = strategy(current_locator)
                if simplified and simplified != current_locator and simplified not in variants:
                    variants.append(simplified)
                    print(f"   📝 {strategy.__name__}: {simplified}")
                    current_locator = simplified  # Chain simplifications
            except Exception as e:
                print(f"   ⚠️ Strategy {strategy.__name__} failed: {e}")
                continue
        
        return variants
    
    def _remove_visibility_conditions(self, locator):
        """Remove visibility-related conditions"""
        # Remove display:none checks
        simplified = re.sub(r'\s*and\s*not\(ancestor::div\[contains\(@style,\s*[\'"]display:\s*none[\'\"]\)\]\)', '', locator)
        # Remove visibility checks
        simplified = re.sub(r'\s*and\s*not\(@style\s*=\s*[\'"]display:\s*none[\'\"]\)', '', simplified)
        # Remove opacity checks
        simplified = re.sub(r'\s*and\s*not\(contains\(@style,\s*[\'"]opacity:\s*0[\'\"]\)\)', '', simplified)
        return simplified.strip()
    
    def _remove_ancestor_conditions(self, locator):
        """Remove ancestor-based conditions"""
        # Remove ancestor checks
        simplified = re.sub(r'\s*and\s*not\(ancestor::[^)]+\)', '', locator)
        # Remove parent checks
        simplified = re.sub(r'\s*and\s*not\(parent::[^)]+\)', '', simplified)
        return simplified.strip()
    
    def _remove_context_path(self, locator):
        """Remove unnecessary path context like sidebar, container, etc."""
        # Remove common container contexts
        contexts_to_remove = [
            r'//div\[contains\(@class,\s*[\'"]sidebar[\'\"]\)\]//',
            r'//div\[contains\(@class,\s*[\'"]container[\'\"]\)\]//',
            r'//div\[contains\(@class,\s*[\'"]main[\'\"]\)\]//',
            r'//nav\[contains\(@class,\s*[^)]+\)\]//',
            r'//section\[contains\(@class,\s*[^)]+\)\]//',
        ]
        
        simplified = locator
        for context_pattern in contexts_to_remove:
            simplified = re.sub(context_pattern, '//', simplified)
        
        return simplified.strip()
    
    def _simplify_text_matching(self, locator):
        """Simplify text matching conditions"""
        # Extract text from contains(text(), 'text')
        text_match = re.search(r"contains\(text\(\),\s*['\"]([^'\"]+)['\"]", locator)
        if text_match:
            text_content = text_match.group(1)
            
            # Extract tag from the locator
            tag_match = re.match(r'.*//([a-zA-Z0-9\-_]+)', locator)
            if tag_match:
                tag = tag_match.group(1)
                # Create simplified text-based locator
                return f"//{tag}[contains(text(), '{text_content}')]"
        
        return locator
    
    def _remove_complex_attributes(self, locator):
        """Remove complex attribute conditions"""
        # Remove multiple attribute conditions, keep the most important one
        attr_matches = re.findall(r'@([a-zA-Z-]+)\s*=\s*[\'"]([^\'"]*)[\'"]', locator)
        
        if len(attr_matches) > 1:
            # Priority order for attributes
            attr_priority = ['id', 'data-testid', 'name', 'class', 'type']
            
            # Find the highest priority attribute
            best_attr = None
            for priority_attr in attr_priority:
                for attr_name, attr_value in attr_matches:
                    if attr_name == priority_attr:
                        best_attr = (attr_name, attr_value)
                        break
                if best_attr:
                    break
            
            if best_attr:
                # Extract tag
                tag_match = re.match(r'.*//([a-zA-Z0-9\-_]+)', locator)
                if tag_match:
                    tag = tag_match.group(1)
                    return f"//{tag}[@{best_attr[0]}='{best_attr[1]}']"
        
        return locator
    
    def _try_direct_selectors(self, locator):
        """Try to create most direct selector possible"""
        # Extract text content if available
        text_match = re.search(r"contains\(text\(\),\s*['\"]([^'\"]+)['\"]", locator)
        if text_match:
            text_content = text_match.group(1)
            
            # Extract tag
            tag_match = re.match(r'.*//([a-zA-Z0-9\-_]+)', locator)
            if tag_match:
                tag = tag_match.group(1)
                # Most direct: just tag and text
                return f"//{tag}[contains(text(), '{text_content}')]"
        
        # If no text, try with just tag and most important attribute
        attr_match = re.search(r'@(id|data-testid|name)\s*=\s*[\'"]([^\'"]*)[\'"]', locator)
        if attr_match:
            attr_name, attr_value = attr_match.groups()
            tag_match = re.match(r'.*//([a-zA-Z0-9\-_]+)', locator)
            if tag_match:
                tag = tag_match.group(1)
                return f"//{tag}[@{attr_name}='{attr_value}']"
        
        return locator

# ============================================================================
# ADVANCED XPATH GENERATION
# ============================================================================

def generate_xpath_optimized(html_content, target_element):
    """
    Generates a simple, unique, and optimized XPath using text, id, name, or class.
    Avoids overfitting to DOM context (like sidebar containers).
    """
    parser = etree.HTMLParser()
    tree = etree.fromstring(html_content, parser)

    tag = target_element.name
    element_text = normalize_text(target_element.get_text(strip=True))

    # 1. Minimal text-based XPath
    if element_text:
        simple_text_xpath = f"//{tag}[contains(normalize-space(text()), '{element_text}')]"
        if is_unique_xpath(tree, simple_text_xpath):
            return simple_text_xpath

    # 2. ID-based XPath
    attr_id = target_element.get("id")
    if attr_id:
        id_xpath = f"//{tag}[@id='{attr_id}']"
        if is_unique_xpath(tree, id_xpath):
            return id_xpath

    # 3. Name-based XPath
    attr_name = target_element.get("name")
    if attr_name:
        name_xpath = f"//{tag}[@name='{attr_name}']"
        if is_unique_xpath(tree, name_xpath):
            return name_xpath

    # 4. Class-based XPath
    attr_class = target_element.get("class", [])
    if attr_class:
        class_expr = " and ".join([f"contains(@class, '{cls}')" for cls in attr_class])
        class_xpath = f"//{tag}[{class_expr}]"
        if is_unique_xpath(tree, class_xpath):
            return class_xpath

    # 5. Fallback: full DOM traversal with index
    parts = []
    current = target_element
    while current and current.name and current.name != '[document]':
        parent = current.parent
        siblings = parent.find_all(current.name, recursive=False) if parent else []
        index = siblings.index(current) + 1 if len(siblings) > 1 else None
        segment = current.name + (f"[{index}]" if index else "")
        parts.insert(0, segment)
        current = parent

    full_path = "/" + "/".join(parts)
    if is_unique_xpath(tree, full_path):
        return full_path

    # 6. As a last resort only, try sibling/parent context
    if target_element.parent:
        sibling = target_element.find_previous_sibling()
        if sibling and sibling.name:
            sib_text = normalize_text(sibling.get_text(strip=True))
            if sib_text:
                sibling_xpath = f"//*[contains(normalize-space(text()), '{sib_text}')]/following-sibling::{tag}"
                if is_unique_xpath(tree, sibling_xpath):
                    return sibling_xpath

        parent = target_element.parent
        par_text = normalize_text(parent.get_text(strip=True))
        if par_text:
            parent_xpath = f"//*[contains(normalize-space(text()), '{par_text}')]/descendant::{tag}"
            if is_unique_xpath(tree, parent_xpath):
                return parent_xpath

    return full_path  # Return fallback even if not unique

# ============================================================================
# WEIGHTED SIMILARITY FUNCTIONS
# ============================================================================

def calculate_weighted_similarity(locator, candidate_locator):
    """Enhanced weighted similarity with better text handling"""
    
    # Check if this is a text-based locator
    is_text_based = "contains(text()" in locator or "text()=" in locator
    
    if is_text_based:
        # Special weights for text-based locators
        weights = {
            'text': 0.6,     # Text is most important for text-based locators
            'xpath': 0.2,    # XPath structure less important
            'id': 0.1,       # ID still somewhat important
            'name': 0.05,    # Lower priority
            'class': 0.03,   # Lower priority
            'type': 0.02,    # Least important
        }
        
        # Enhanced text similarity for text-based locators
        target_text = extract_text_from_locator(locator)
        text_score = 0
        if target_text:
            text_score = calculate_text_similarity(target_text, candidate_locator["text"], locator)
        
        similarity_scores = {
            'text': text_score,
            'xpath': fuzz.token_sort_ratio(locator, candidate_locator["xpath"]),
            'id': fuzz.token_sort_ratio(locator, candidate_locator["id"] or ""),
            'name': fuzz.token_sort_ratio(locator, candidate_locator["name"] or ""),
            'class': fuzz.token_sort_ratio(locator, candidate_locator["class"] or ""),
            'type': fuzz.partial_ratio(locator, candidate_locator["type"] or "")
        }
    else:
        # Original weights for non-text locators
        weights = {
            'xpath': 0.4,    # XPath structure is very important
            'id': 0.25,      # ID is highly reliable
            'name': 0.15,    # Name is quite reliable
            'class': 0.1,    # Class can be useful but less reliable
            'type': 0.05,    # Type provides some context
            'text': 0.05,    # Text can be noisy but sometimes helpful
        }
        
        similarity_scores = {
            'xpath': fuzz.token_sort_ratio(locator, candidate_locator["xpath"]),
            'id': fuzz.token_sort_ratio(locator, candidate_locator["id"] or ""),
            'name': fuzz.token_sort_ratio(locator, candidate_locator["name"] or ""),
            'class': fuzz.token_sort_ratio(locator, candidate_locator["class"] or ""),
            'type': fuzz.partial_ratio(locator, candidate_locator["type"] or ""),
            'text': fuzz.partial_ratio(locator, candidate_locator["text"] or "")
        }
    
    # Calculate weighted score
    weighted_score = sum(similarity_scores[key] * weights[key] for key in weights)
    
    return round(weighted_score, 2), similarity_scores

def generate_simple_text_fix(locator, similar_text_elements):
    """Generate simple text substitution fixes for obvious text mismatches."""
    target_text = extract_text_from_locator(locator)
    if not target_text:
        return None

    target_normalized = normalize_text(target_text)

    for elem in similar_text_elements:
        candidate_text = elem["text"]
        candidate_normalized = normalize_text(candidate_text)

        similarity = elem["similarity"]

        # 1. Case-insensitive exact match
        if target_normalized == candidate_normalized:
            fixed_locator = locator.replace(target_text, candidate_text)
            return {
                "fixed_locator": fixed_locator,
                "original_text": target_text,
                "corrected_text": candidate_text,
                "fix_type": "case_correction",
                "confidence": similarity,
                "xpath": elem["xpath"]
            }

        # 2. Target text has extra suffix (e.g., Product Categories-ifbdf)
        if candidate_normalized in target_normalized and similarity >= 70:
            suffix = target_normalized.replace(candidate_normalized, "")
            if re.fullmatch(r"[\W_]*[a-zA-Z0-9\-_\(\)\s]+", suffix):
                fixed_locator = locator.replace(target_text, candidate_text)
                return {
                    "fixed_locator": fixed_locator,
                    "original_text": target_text,
                    "corrected_text": candidate_text,
                    "fix_type": "text_suffix_removal",
                    "confidence": similarity,
                    "xpath": elem["xpath"]
                }

        # 3. Fuzzy match (optional, fallback only)
        if similarity >= 85:
            fixed_locator = locator.replace(target_text, candidate_text)
            return {
                "fixed_locator": fixed_locator,
                "original_text": target_text,
                "corrected_text": candidate_text,
                "fix_type": "fuzzy_match_replacement",
                "confidence": similarity,
                "xpath": elem["xpath"]
            }

    return None

# ============================================================================
# ENHANCED CANDIDATE GENERATOR (Main Class)
# ============================================================================

class EnhancedCandidateGenerator:
    """Enhanced candidate generation with improved algorithms"""
    
    def __init__(self):
        self.scorer = EnhancedCandidateScorer()
        self.simplifier = EnhancedLocatorSimplifier()
        
    def generate_enhanced_candidates(self, locator, threshold=None, expected_tag=None, mode="balanced"):
        """
        Generate enhanced candidates with improved scoring
        
        Args:
            locator: The failed locator to find alternatives for
            threshold: Similarity threshold (None for adaptive)
            expected_tag: Expected HTML tag type for filtering
            mode: Matching mode - "strict", "balanced", or "lenient"
        """
        
        print(f"\n🔧 ENHANCED: Processing locator: {locator}")
        print(f"📊 Analysis mode: {mode}")
        
        # Phase 1: Try simplified variants first (NEW APPROACH)
        print(f"\n🔧 Phase 1: Locator Simplification")
        simplified_variants = self.simplifier.generate_simplified_variants(locator)
        
        # Test each simplified variant (would be tested in real execution)
        best_simplified = None
        for variant in simplified_variants:
            print(f"   🧪 Would test: {variant}")
            # In real execution, this would test the variant
            # For now, we'll use the most direct one as potential solution
            if "contains(text()," in variant and "//" in variant and variant.count('[') == 1:
                best_simplified = variant
                print(f"   ✅ Best simplified candidate: {variant}")
                break
        
        # If we found a good simplified variant, prioritize it
        enhanced_results = []
        if best_simplified:
            enhanced_results.append({
                "xpath": best_simplified,
                "tag": extract_tag_from_locator(best_simplified) or "unknown",
                "text": extract_text_from_locator(best_simplified) or "",
                "similarity": 95,  # High confidence for simplified variants
                "correction_rate": "VERY_HIGH",
                "source": "locator_simplification",
                "simplified": True,
                "original_locator": locator
            })
        
        # Phase 2: Enhanced DOM Analysis
        print(f"\n🔍 Phase 2: Enhanced DOM Analysis")
        
        # Determine adaptive threshold
        if threshold is None:
            threshold = self._determine_enhanced_threshold(locator, mode)
            print(f"🎯 Enhanced threshold: {threshold}")
        
        # Extract expected tag if not provided
        if expected_tag is None:
            expected_tag = self.scorer._extract_tag_from_locator(locator)
            if expected_tag:
                print(f"🏷️ Expected tag: {expected_tag}")
        
        all_candidates = []
        seen_xpaths = set()
        processed_files = 0
        
        if not os.path.exists(page_sources_dir):
            print(f"❌ Page sources directory not found: {page_sources_dir}")
            return {
                "original_locator": locator,
                "candidates": enhanced_results,  # Return simplified results if available
                "total_found": len(enhanced_results),
                "message": "No page sources found"
            }

        print(f"📁 Scanning HTML files in: {page_sources_dir}")
        
        for filename in os.listdir(page_sources_dir):
            if not filename.endswith('.html'):
                continue

            try:
                processed_files += 1
                filepath = os.path.join(page_sources_dir, filename)
                print(f"📄 Processing: {filename}")
                
                with open(filepath, 'r', encoding='utf-8') as f:
                    html = f.read()

                soup = BeautifulSoup(html, 'html.parser')
                elements_processed = 0
                dom_context = self._analyze_dom_context(soup)

                for element in soup.find_all():
                    if not element.name:
                        continue
                    
                    elements_processed += 1

                    # Apply tag filtering if expected tag is known
                    if expected_tag and element.name.lower() != expected_tag.lower():
                        # Also check semantically equivalent tags
                        if not self._is_semantically_equivalent_tag(expected_tag, element.name):
                            continue

                    xpath = self._generate_optimized_xpath(html, element)
                    if xpath in seen_xpaths:
                        continue
                    seen_xpaths.add(xpath)

                    # Create candidate info
                    candidate_info = {
                        "tag": element.name,
                        "class": " ".join(element.get("class", [])),
                        "type": element.get("type", ""),
                        "name": element.get("name", ""),
                        "id": element.get("id", ""),
                        "text": element.get_text(strip=True),
                        "source_page": filename,
                        "xpath": xpath,
                        "dom_depth": self._get_dom_depth(element),
                        "attributes": dict(element.attrs)
                    }

                    # Calculate enhanced score
                    score_breakdown, final_score = self.scorer.calculate_enhanced_score(
                        locator, element, dom_context
                    )

                    if final_score >= threshold:
                        # Assess correction confidence
                        correction_rate = self._assess_enhanced_correction_rate(
                            locator, candidate_info, score_breakdown
                        )
                        
                        enhanced_candidate = {
                            **candidate_info,
                            "similarity": round(final_score, 2),
                            "score_breakdown": score_breakdown,
                            "correction_rate": correction_rate,
                            "enhanced": True,
                            "tag_mismatch_detected": self._detect_tag_mismatch(locator, element),
                            "reliability_factors": self._get_reliability_factors(element)
                        }
                        all_candidates.append(enhanced_candidate)
                        
                        print(f"✅ Enhanced candidate: {xpath[:60]}... (Score: {final_score:.1f})")

                print(f"   📊 Processed {elements_processed} elements")

            except Exception as e:
                print(f"❌ Error processing {filename}: {str(e)}")
                continue

        print(f"\n📈 Enhanced Analysis Summary:")
        print(f"   📁 Files processed: {processed_files}")
        print(f"   🎯 DOM candidates found: {len(all_candidates)}")
        
        # Enhanced sorting by multiple criteria
        all_candidates = sorted(
            all_candidates, 
            key=lambda x: (
                x["similarity"], 
                x["correction_rate"] == "HIGH",
                x["score_breakdown"]["reliability_score"]
            ), 
            reverse=True
        )
        
        # Combine simplified results with DOM analysis results
        final_candidates = enhanced_results + all_candidates
        
        # Apply enhanced filtering
        final_candidates = self._apply_enhanced_filtering(final_candidates, threshold)
        
        # Print enhanced summary
        if final_candidates:
            print(f"\n🏆 Enhanced Top {len(final_candidates)} Candidates:")
            for i, candidate in enumerate(final_candidates[:5], 1):
                print(f"   {i}. XPath: {candidate['xpath'][:80]}...")
                print(f"      Tag: {candidate['tag']}, ID: {candidate.get('id') or 'N/A'}")
                print(f"      Score: {candidate['similarity']:.1f}%, Confidence: {candidate['correction_rate']}")
                if candidate.get('simplified'):
                    print(f"      🔧 SIMPLIFIED from original locator")
                if candidate.get('tag_mismatch_detected'):
                    print(f"      🔄 Tag mismatch detected and corrected")
                print()
        
        return {
            "original_locator": locator,
            "candidates": final_candidates,
            "total_found": len(all_candidates) + len(enhanced_results),
            "files_processed": processed_files,
            "threshold_used": threshold,
            "mode_used": mode,
            "enhanced": True,
            "simplified_variants": simplified_variants
        }
    
    def _determine_enhanced_threshold(self, locator, mode):
        """Determine enhanced adaptive threshold"""
        base_threshold = 60
        
        # Adjust based on locator complexity
        if "contains(text()" in locator or "text()=" in locator:
            base_threshold = 45  # More lenient for text-based locators
        
        # Adjust based on mode
        mode_adjustments = {
            "strict": 15,
            "balanced": 0,
            "lenient": -20
        }
        
        return base_threshold + mode_adjustments.get(mode, 0)
    
    def _is_semantically_equivalent_tag(self, expected_tag, candidate_tag):
        """Check if tags are semantically equivalent"""
        equivalents = {
            'span': ['a', 'label', 'div'],
            'div': ['section', 'article', 'span'],
            'a': ['button', 'span'],
            'button': ['a', 'input'],
        }
        
        expected_lower = expected_tag.lower()
        candidate_lower = candidate_tag.lower()
        
        return (
            expected_lower == candidate_lower or
            candidate_lower in equivalents.get(expected_lower, [])
        )
    
    def _analyze_dom_context(self, soup):
        """Analyze DOM context for better scoring"""
        return {
            'total_elements': len(soup.find_all()),
            'has_navigation': bool(soup.find_all(['nav', 'ul', 'ol'])),
            'interactive_elements': len(soup.find_all(['a', 'button', 'input'])),
            'semantic_structure': bool(soup.find_all(['main', 'section', 'article', 'header', 'footer']))
        }
    
    def _generate_optimized_xpath(self, html_content, target_element):
        """Generate optimized XPath with preference for stable attributes"""
        # Prioritize stable attributes
        stable_attrs = ['id', 'data-testid', 'data-cy', 'data-qa', 'name']
        
        for attr in stable_attrs:
            if target_element.get(attr):
                attr_value = target_element.get(attr)
                xpath = f"//{target_element.name}[@{attr}='{attr_value}']"
                if self._is_unique_xpath_in_soup(xpath, html_content):
                    return xpath
        
        # Fallback to original optimized generation
        return generate_xpath_optimized(html_content, target_element)
    
    def _is_unique_xpath_in_soup(self, xpath, html_content):
        """Check if XPath is unique using lxml"""
        try:
            parser = etree.HTMLParser()
            tree = etree.fromstring(html_content, parser)
            return len(tree.xpath(xpath)) == 1
        except Exception:
            return False
    
    def _get_dom_depth(self, element):
        """Calculate DOM depth of an element"""
        return get_dom_depth(element)
    
    def _assess_enhanced_correction_rate(self, original_locator, candidate_info, score_breakdown):
        """Enhanced correction rate assessment"""
        confidence_score = 0
        
        # High confidence factors
        if score_breakdown['attribute_score'] >= 80:
            confidence_score += 40
        if score_breakdown['tag_score'] >= 90:
            confidence_score += 30
        if score_breakdown['text_score'] >= 85:
            confidence_score += 25
        if score_breakdown['reliability_score'] >= 80:
            confidence_score += 20
        
        # Medium confidence factors
        if score_breakdown['structure_score'] >= 70:
            confidence_score += 15
        if candidate_info.get('id'):
            confidence_score += 25
        if any(attr in candidate_info.get('attributes', {}) for attr in ['data-testid', 'data-cy', 'data-qa']):
            confidence_score += 20
        
        # Determine rate
        if confidence_score >= 90:
            return "VERY_HIGH"
        elif confidence_score >= 70:
            return "HIGH"
        elif confidence_score >= 50:
            return "MEDIUM"
        elif confidence_score >= 30:
            return "LOW"
        else:
            return "VERY_LOW"
    
    def _detect_tag_mismatch(self, original_locator, candidate_element):
        """Detect if there's a tag mismatch that was corrected"""
        expected_tag = self.scorer._extract_tag_from_locator(original_locator)
        if expected_tag and expected_tag.lower() != candidate_element.name.lower():
            return {
                'expected': expected_tag,
                'found': candidate_element.name,
                'corrected': True
            }
        return False
    
    def _get_reliability_factors(self, element):
        """Get factors that make an element reliable"""
        factors = []
        
        if element.get('id'):
            factors.append('has_id')
        if any(attr.startswith('data-') for attr in element.attrs):
            factors.append('has_data_attributes')
        if element.name in ['button', 'input', 'select', 'textarea']:
            factors.append('form_element')
        if element.get('role'):
            factors.append('has_semantic_role')
        
        return factors
    
    def _apply_enhanced_filtering(self, candidates, threshold):
        """Apply enhanced filtering logic"""
        if not candidates:
            return []
        
        # Priority 1: Simplified variants (always highest priority)
        simplified = [c for c in candidates if c.get("simplified")]
        if simplified:
            return simplified[:3] + [c for c in candidates if not c.get("simplified")][:7]
        
        # Priority 2: Very high confidence candidates
        very_high_conf = [c for c in candidates if c["correction_rate"] == "VERY_HIGH"]
        if very_high_conf:
            return very_high_conf[:5]
        
        # Priority 3: High confidence candidates
        high_conf = [c for c in candidates if c["correction_rate"] in ["HIGH", "VERY_HIGH"]]
        if high_conf:
            return high_conf[:8]
        
        # Priority 4: Good scoring candidates
        good_score = [c for c in candidates if c["similarity"] >= threshold + 20]
        if good_score:
            return good_score[:10]
        
        # Fallback: Top scoring candidates
        return candidates[:12]

# ============================================================================
# MAIN GENERATION FUNCTIONS (Enhanced and Legacy Combined)
# ============================================================================

def generate_enhanced_candidates(locator, threshold=None, expected_tag=None, mode="balanced"):
    """Enhanced version with locator simplification and better scoring"""
    generator = EnhancedCandidateGenerator()
    return generator.generate_enhanced_candidates(locator, threshold, expected_tag, mode)

def generate_best_candidates(locator, threshold=None, expected_tag=None, mode="balanced"):
    """
    Enhanced candidate generation combining all improvements from both algorithms.
    
    This function now includes:
    1. Locator simplification strategies (try simple fixes first)
    2. Enhanced scoring with multiple factors
    3. Better text matching with multiple strategies  
    4. Tag mismatch detection and semantic equivalency
    5. DOM context analysis
    6. Improved attribute matching
    7. Backward compatibility with original approach
    
    Args:
        locator: The failed locator to find alternatives for
        threshold: Similarity threshold (None for adaptive)
        expected_tag: Expected HTML tag type for filtering
        mode: Matching mode - "strict", "balanced", or "lenient"
    """
    
    print(f"\n🔍 COMPREHENSIVE: Processing locator: {locator}")
    print(f"📊 Analysis mode: {mode}")
    
    # Use enhanced generation as primary approach
    try:
        enhanced_results = generate_enhanced_candidates(locator, threshold, expected_tag, mode)
        
        # If enhanced approach found good results, return them
        if enhanced_results.get("candidates") and len(enhanced_results["candidates"]) >= 3:
            print(f"✅ Enhanced approach found {len(enhanced_results['candidates'])} high-quality candidates")
            return enhanced_results
        
        print(f"⚠️ Enhanced approach found limited results, falling back to comprehensive scan...")
        
    except Exception as e:
        print(f"❌ Enhanced approach failed: {e}")
        print(f"🔄 Falling back to original approach...")
    
    # Enhanced fallback with combined approach
    print(f"\n🔍 FALLBACK: Comprehensive candidate scan")
    
    # Determine adaptive threshold if not provided
    if threshold is None:
        threshold = determine_adaptive_threshold(locator)
        print(f"🎯 Adaptive threshold: {threshold}")
    
    # Adjust threshold based on mode
    if mode == "strict":
        threshold += 10
    elif mode == "lenient":
        threshold -= 15
    
    # For text-based locators, be more lenient by default
    if "contains(text()" in locator or "text()=" in locator:
        threshold = min(threshold - 20, 30)  # Much more lenient for text matching
        print(f"🔤 Text-based locator detected, reducing threshold to: {threshold}")
    
    # Extract expected tag if not provided
    if expected_tag is None:
        expected_tag = extract_tag_from_locator(locator)
        if expected_tag:
            print(f"🏷️ Expected tag: {expected_tag}")
    
    all_candidates = []
    seen_xpaths = set()
    processed_files = 0
    similar_text_elements = []  # Track elements with similar text for debugging
    
    if not os.path.exists(page_sources_dir):
        print(f"❌ Page sources directory not found: {page_sources_dir}")
        return {
            "original_locator": locator,
            "candidates": [],
            "total_found": 0,
            "message": "No page sources found"
        }

    print(f"📁 Scanning HTML files in: {page_sources_dir}")
    
    for filename in os.listdir(page_sources_dir):
        if not filename.endswith('.html'):
            continue

        try:
            processed_files += 1
            filepath = os.path.join(page_sources_dir, filename)
            print(f"📄 Processing: {filename}")
            
            with open(filepath, 'r', encoding='utf-8') as f:
                html = f.read()

            soup = BeautifulSoup(html, 'html.parser')
            elements_processed = 0

            for element in soup.find_all():
                if not element.name:
                    continue
                
                elements_processed += 1

                # Apply tag filtering if expected tag is known
                if expected_tag and element.name.lower() != expected_tag.lower():
                    continue

                xpath = generate_xpath_optimized(html, element) if not element.get("id") else f"//{element.name}[@id='{element.get('id')}']"

                if xpath in seen_xpaths:
                    continue
                seen_xpaths.add(xpath)

                # Normalize text for better matching
                element_text = normalize_text(element.get_text(strip=True))
                
                candidate_locator = {
                    "tag": element.name,
                    "class": " ".join(element.get("class", [])),
                    "type": element.get("type", ""),
                    "name": element.get("name", ""),
                    "id": element.get("id", ""),
                    "text": element_text,
                    "source_page": filename,
                    "xpath": xpath,
                    "dom_depth": get_dom_depth(element)
                }

                # Enhanced text-based tracking and scoring
                if "contains(text()" in locator or "text()=" in locator:
                    target_text = extract_text_from_locator(locator)
                    if target_text and element_text:
                        text_similarity = calculate_text_similarity(target_text, element_text, locator)
                        if text_similarity > 50:  # Lower threshold for tracking
                            similar_text_elements.append({
                                "text": element_text,
                                "xpath": xpath,
                                "tag": element.name,
                                "similarity": text_similarity,
                                "target_text": target_text
                            })

                # Calculate weighted similarity score
                weighted_score, individual_scores = calculate_weighted_similarity(locator, candidate_locator)
                
                # Calculate DOM context similarity
                dom_similarity = calculate_dom_similarity(locator, element)
                
                # Combine weighted score with DOM similarity (70% weighted, 30% DOM context)
                final_score = (weighted_score * 0.7) + (dom_similarity * 0.3)

                if final_score >= threshold:
                    # Assess correction confidence
                    correction_rate = assess_correction_rate(locator, candidate_locator)
                    
                    best_candidate = {
                        **candidate_locator,
                        "similarity": round(final_score, 2),
                        "weighted_score": weighted_score,
                        "dom_similarity": round(dom_similarity, 2),
                        "correction_rate": correction_rate,
                        "individual_scores": individual_scores
                    }
                    all_candidates.append(best_candidate)
                    
                    print(f"✅ Found candidate: {xpath[:60]}... (Score: {final_score:.1f})")

            print(f"   📊 Processed {elements_processed} elements")

        except Exception as e:
            print(f"❌ Error processing {filename}: {str(e)}")
            continue

    print(f"\n📈 Analysis Summary:")
    print(f"   📁 Files processed: {processed_files}")
    print(f"   🎯 Candidates found: {len(all_candidates)}")
    
    # Enhanced text processing and simple fixes
    if not all_candidates and similar_text_elements:
        print(f"\n🔤 Found {len(similar_text_elements)} elements with similar text:")
        for elem in sorted(similar_text_elements, key=lambda x: x["similarity"], reverse=True)[:5]:
            print(f"   📝 '{elem['text']}' vs '{elem.get('target_text', '')}' ({elem['similarity']:.1f}% match)")
            print(f"      XPath: {elem['xpath'][:80]}...")
        
        # Try simple text fix first
        simple_fix = generate_simple_text_fix(locator, similar_text_elements)
        if simple_fix:
            print(f"\n🎯 Found simple text fix:")
            print(f"   Original: '{simple_fix['original_text']}'")
            print(f"   Corrected: '{simple_fix['corrected_text']}'")
            print(f"   Fix type: {simple_fix['fix_type']}")
            print(f"   Confidence: {simple_fix['confidence']:.1f}%")
            print(f"   Fixed locator: {simple_fix['fixed_locator']}")
            
            # Create a high-confidence candidate from the simple fix
            simple_candidate = {
                "tag": expected_tag or "a",
                "class": "",
                "type": "",
                "name": "",
                "id": "",
                "text": simple_fix['corrected_text'],
                "source_page": "simple_fix",
                "xpath": simple_fix['fixed_locator'],
                "dom_depth": 3,
                "similarity": simple_fix['confidence'],
                "weighted_score": simple_fix['confidence'],
                "dom_similarity": 0,
                "correction_rate": "HIGH",
                "individual_scores": {"text": simple_fix['confidence']},
                "simple_fix": True,
                "fix_type": simple_fix['fix_type']
            }
            all_candidates.append(simple_candidate)
    
    # Sort by final score (combination of weighted similarity + DOM context)
    all_candidates = sorted(all_candidates, key=lambda x: (x["similarity"], x["correction_rate"]), reverse=True)
    
    # Apply confidence-based cutoff instead of hard limit
    high_confidence_candidates = [c for c in all_candidates if c["correction_rate"] in ["HIGH", "MEDIUM"]]
    
    # If we have high confidence candidates, prioritize them
    if high_confidence_candidates:
        final_candidates = high_confidence_candidates[:10]
        print(f"   ⭐ High confidence candidates: {len(high_confidence_candidates)}")
    else:
        # Otherwise, take top candidates by score
        final_candidates = all_candidates[:15]  # Slightly more lenient fallback
    
    # Print top candidates for terminal output
    if final_candidates:
        print(f"\n🏆 Top {len(final_candidates)} Candidates:")
        for i, candidate in enumerate(final_candidates[:5], 1):  # Show top 5 in terminal
            print(f"   {i}. XPath: {candidate['xpath'][:80]}...")
            print(f"      Tag: {candidate['tag']}, ID: {candidate['id'] or 'N/A'}, Class: {candidate['class'][:30] or 'N/A'}")
            print(f"      Score: {candidate['similarity']:.1f}%, Confidence: {candidate['correction_rate']}")
            print(f"      Text: {candidate['text'][:50]}{'...' if len(candidate['text']) > 50 else ''}")
            print()
    
    return {
        "original_locator": locator,
        "candidates": final_candidates,
        "total_found": len(all_candidates),
        "files_processed": processed_files,
        "threshold_used": threshold,
        "mode_used": mode,
        "comprehensive": True
    }

# Backward compatibility
def get_best_candidates(*args, **kwargs):
    """Legacy function name for backward compatibility"""
    return generate_best_candidates(*args, **kwargs)
