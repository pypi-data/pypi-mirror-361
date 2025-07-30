from robot.libraries.BuiltIn import BuiltIn
from robot.api import logger
import json
from datetime import datetime
import os
import traceback
import re
from bs4 import BeautifulSoup
from self_healing_agent import SelfHealingAgent
# from .self_healing_agent import SelfHealingAgent
import time

class SelfHealListener:
    ROBOT_LISTENER_API_VERSION = 2

    def __init__(self):
        logger.console("\n=== Initializing SelfHealListener ===")
        
        # Initialize tracking variables
        self.current_test = None
        self.current_suite = None
        self.current_test_locators = {}
        self.failed_locators = {"failures": []}
        
        # Add retry configuration
        self.max_retries = 3  # Maximum number of retries
        self.retry_delay = 1  # Delay between retries in seconds
        
        # Setup directory structure
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            base_dir = os.path.dirname(current_dir)
            
            # Load config
            config_path = os.path.join(base_dir, 'Environment', 'config.json')
            with open(config_path, 'r') as f:
                self.config = json.load(f)
            
            # Define directories with proper structure from config
            self.locator_data_dir = os.path.join(base_dir, self.config.get('data_path'))
            self.page_sources_dir = os.path.join(base_dir, self.config.get('page_sources_dir'))
            self.failed_locators_file = os.path.join(self.locator_data_dir, 
                                                    self.config['locator_data']['locator_failures'])
            
            # Create directories if they don't exist
            for directory in [self.locator_data_dir, self.page_sources_dir]:
                if not os.path.exists(directory):
                    os.makedirs(directory)
                    logger.console(f"Created directory: {directory}")
            
            # Initialize failed locators file if it doesn't exist
            if not os.path.exists(self.failed_locators_file):
                with open(self.failed_locators_file, 'w', encoding='utf-8') as f:
                    json.dump({"failures": []}, f, indent=4)
                logger.console(f"Created failed locators file: {self.failed_locators_file}")
            
            # Load existing failed locators
            self._load_failed_locators()
            
            # Add after other initializations
            self.healing_agent = SelfHealingAgent()
            
            # Add locator patterns as class attribute for reuse
            self.locator_patterns = [
                (r"Element '([^']+)'", 1),  # Standard format
                (r"Page should have contained element '([^']+)'", 1),  # Page should contain format
                (r"Element locator '([^']+)'", 1),  # Alternative format
                (r"Unable to locate element: \"([^\"]+)\"", 1),  # Selenium format
                (r"no such element: .*?'([^']+)'", 1),  # No such element format
            ]
            
        except Exception as e:
            logger.console(f"Error in initialization: {str(e)}")
            logger.console(traceback.format_exc())

    def _load_failed_locators(self):
        """Load existing failed locators from JSON file"""
        try:
            if os.path.exists(self.failed_locators_file):
                with open(self.failed_locators_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.failed_locators = data if isinstance(data, dict) else {"failures": []}
            else:
                self.failed_locators = {"failures": []}
            logger.console(f"Loaded existing failed locators: {len(self.failed_locators['failures'])}")
        except Exception as e:
            logger.console(f"Error loading failed locators: {str(e)}")
            self.failed_locators = {"failures": []}

    def _save_failed_locators(self):
        """Save failed locators to JSON file"""
        try:
            with open(self.failed_locators_file, 'w', encoding='utf-8') as f:
                json.dump(self.failed_locators, f, indent=4, ensure_ascii=False)
            logger.console("Successfully saved failed locators to file")
        except Exception as e:
            logger.console(f"Error saving failed locators: {str(e)}")

    def start_test(self, name, attributes):
        """Called when a test starts"""
        logger.console(f"\n=== Starting Test: {name} ===")
        self.current_test = name
        self.current_test_locators = {}

    def end_test(self, name, attributes):
        """Called when a test ends"""
        logger.console(f"\n=== Ending Test: {name} with status: {attributes['status']} ===")
        
        if attributes['status'] == 'FAIL':
            error_msg = attributes.get('message', '')
            logger.console(f"\nTest Failed with error message: {error_msg}")
            
            # Extract locator from error message first
            failed_locator = self._extract_locator_from_error(error_msg)
            
            if failed_locator:
                # Check if the failed locator is a valid locator
                if self._is_locator(failed_locator):
                    logger.console(f"\n🔍 Saving locator failure: {failed_locator}")
                    # Get the full error message from the test attributes
                    full_error = self._get_formatted_error_message(attributes)
                    file_path = self._get_file_path_from_error(error_msg)
                    self._save_locator_failure(name, full_error, failed_locator, file_path)
                else:
                    logger.console(f"\n⚠️ Extracted value is not a valid locator: {failed_locator}")

    def _extract_locator_from_error(self, error_msg):
        """Extract complete locator from error message"""
        try:
            # First, try to find the pattern "Element '...' not visible after X seconds"
            pattern1 = r"Element '([^']*(?:'[^']*'[^']*)*)' not visible after \d+ seconds"
            match = re.search(pattern1, error_msg)
            if match:
                complete_locator = match.group(1)
                logger.console(f"📍 Found locator in error message: {complete_locator}")
                return complete_locator
            
            # Try other patterns
            patterns = [
                r"Element '([^']*(?:'[^']*'[^']*)*)' did not appear",
                r"Element '([^']*(?:'[^']*'[^']*)*)' not found",
                r"Element '([^']*(?:'[^']*'[^']*)*)' not visible",
                r"Element '([^']*(?:'[^']*'[^']*)*)'",
                r"Page should have contained element '([^']*(?:'[^']*'[^']*)*)' but did not"
            ]

            for pattern in patterns:
                match = re.search(pattern, error_msg)
                if match:
                    complete_locator = match.group(1)
                    logger.console(f"📍 Found locator in error message: {complete_locator}")
                    return complete_locator

            return None

        except Exception as e:
            logger.console(f"❌ Error extracting locator: {str(e)}")
            return None

    def _is_locator_failure(self, error_msg):
        """Check if the failure is related to locator or UI interaction issues"""
        # We'll now consider all element-related failures as potential locator issues
        failure_patterns = [
            # Element not found/visible patterns
            r"Element .* not found",
            r"Element .* did not appear",
            r"Element .* was not visible",
            r"Element .* is not clickable",
            
            # Timeout patterns (include these now)
            r"Element .* did not appear in \d+ seconds",
            r"Element .* was not visible in \d+ seconds",
            r"Element .* not visible after \d+ seconds",
            
            # # Other common patterns
            # r"NoSuchElementException",
            # r"ElementNotVisibleException",
            # r"ElementClickInterceptedException",
            # r"StaleElementReferenceException",
            # r"InvalidElementStateException",
            # r"ElementNotInteractableException",
            # r"Unable to locate element",
            # r"no such element",
            # r"Page should have contained element"
        ]
        
        return any(re.search(pattern, error_msg, re.IGNORECASE) for pattern in failure_patterns)

    def _get_formatted_error_message(self, attributes):
        """Extract and format the complete error message from test attributes"""
        try:
            # Get the main error message
            error_msg = attributes.get("message", "")
            
            # Get additional error details if available
            error_details = []
            if "args" in attributes:
                error_details.extend(str(arg) for arg in attributes["args"])
            
            # Get stack trace if available
            if "traceback" in attributes:
                error_details.append(attributes["traceback"])
            
            # Combine all error information
            full_error = error_msg
            if error_details:
                full_error = f"{error_msg}\n{''.join(error_details)}"
            
            return full_error.strip()
            
        except Exception as e:
            logger.console(f"⚠️ Error formatting error message: {str(e)}")
            return attributes.get("message", "Unknown error")

    def _capture_page_source(self, keyword_name):
        """Capture and save page source for any web application"""
        try:
            # Get SeleniumLibrary instance
            selib = BuiltIn().get_library_instance('SeleniumLibrary')
            if not selib:
                logger.console("⚠️ SeleniumLibrary instance not found")
                return None

            # Store current window/frame info
            current_handles = []
            try:
                current_handles = selib.driver.window_handles
                current_window = selib.driver.current_window_handle
            except:
                pass

            try:
                # Switch to default content first
                selib.driver.switch_to.default_content()
                
                # Get main page source
                page_source = selib.get_source()
                
                # Handle iframes if present
                iframes = selib.driver.find_elements("tag name", "iframe")
                for iframe in iframes:
                    try:
                        selib.driver.switch_to.frame(iframe)
                        iframe_source = selib.get_source()
                        # Add iframe content to main source
                        page_source = page_source.replace("</body>", 
                            f"{iframe_source}</body>")
                    except:
                        continue
                    finally:
                        selib.driver.switch_to.default_content()
                    
                # Handle additional windows if present
                for handle in current_handles:
                    try:
                        if handle != current_window:
                            selib.driver.switch_to.window(handle)
                            window_source = selib.get_source()
                            # Add window content
                            page_source = page_source.replace("</body>", 
                                f"<!-- New Window Content -->{window_source}</body>")
                    except:
                        continue

            finally:
                # Restore original context
                try:
                    if current_handles:
                        selib.driver.switch_to.window(current_window)
                    selib.driver.switch_to.default_content()
                except:
                    pass

            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            try:
                test_name = BuiltIn().get_variable_value("${TEST_NAME}")
                if not test_name:
                    test_name = "unknown_test"
            except:
                test_name = "unknown_test"

            # Clean filename
            test_name = re.sub(r'[^\w\-_]', '_', test_name)
            test_name = test_name[:50] if len(test_name) > 50 else test_name
            filename = f"{test_name}_{timestamp}.html"

            # Ensure directory exists
            os.makedirs(self.page_sources_dir, exist_ok=True)
            filepath = os.path.join(self.page_sources_dir, filename)

            # Save page source with error handling
            try:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(page_source)
                logger.console(f"\n✅ Saved page source: {filename}")
                return filepath
            except Exception as e:
                logger.console(f"⚠️ Error saving page source: {str(e)}")
                return None

        except Exception as e:
            logger.console(f"❌ Error capturing page source: {str(e)}")
            if 'selib' in locals() and selib:
                try:
                    # Emergency capture
                    emergency_source = selib.get_source()
                    emergency_path = os.path.join(self.page_sources_dir, 
                        f"emergency_capture_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html")
                    with open(emergency_path, 'w', encoding='utf-8') as f:
                        f.write(emergency_source)
                    logger.console("✅ Saved emergency page source")
                    return emergency_path
                except:
                    pass
            return None

    def start_keyword(self, name, attributes):
        """Track locators used in keywords"""
        try:
            element_keywords = [
                "Click Element",
                "Input Text",
                "Wait Until Element Is Visible",
                "Element Should Be Visible",
                "Element Should Not Be Visible",
                "Page Should Contain Element",
                "Wait Until Page Contains Element",
                "Scroll Element Into View"
            ]

            if any(keyword in name for keyword in element_keywords):
                args = attributes.get("args", [])
                if args:
                    locator = args[0]
                    logger.console(f"\n🔍 Tracking keyword: {name}")
                    logger.console(f"📍 Locator used: {locator}")
                    
                    # Resolve variable if it's a variable reference
                    if str(locator).startswith('${'):
                        try:
                            actual_value = BuiltIn().get_variable_value(locator)
                            logger.console(f"✅ Variable {locator} resolved to: {actual_value}")
                            locator = actual_value
                        except Exception as e:
                            logger.console(f"⚠️ Could not resolve variable {locator}: {str(e)}")
                    
                    page_source_path = self._capture_page_source(name)
                    self._track_locator(name, locator, page_source_path)
                    
        except Exception as e:
            logger.console(f"❌ Error in start_keyword: {str(e)}")
            logger.console(traceback.format_exc())

    def end_keyword(self, name, attrs):
        """Handle keyword failures"""
        try:
            if attrs['status'] == 'FAIL':
                args = attrs.get("args", [])
                if args:
                    locator = args[0]
                    error_msg = attrs.get('message', 'Element interaction failed')
                    self._save_locator_failure(
                        test_name=self.current_test,
                        error_msg=error_msg,
                        locator=locator
                    )
        except Exception as e:
            logger.console(f"Error in end_keyword: {str(e)}")

    def _track_locator(self, keyword_name, locator, page_source_path):
        """Track locator usage with page source reference"""
        try:
            if keyword_name not in self.current_test_locators:
                self.current_test_locators[keyword_name] = []
            
            # Get the current test case file path
            current_test = BuiltIn().get_variable_value("${TEST_NAME}")
            test_file_path = BuiltIn().get_variable_value("${SUITE_SOURCE}")
            
            locator_info = {
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'page_source_file': page_source_path,
                'test_case': current_test,
                'test_file': test_file_path
            }
            
            if str(locator).startswith('${'):
                try:
                    # Get the variable value
                    actual_value = BuiltIn().get_variable_value(locator)
                    # Get variable source info
                    var_source = BuiltIn().get_variable_file_name(locator)
                    
                    locator_info.update({
                        'variable': locator,
                        'value': actual_value,
                        'locator': actual_value,
                        'file_path': var_source or "Unknown"
                    })
                    logger.console(f"📝 Tracked variable locator: {locator} = {actual_value}")
                    logger.console(f"   Source file: {var_source}")
                except Exception as e:
                    logger.console(f"⚠️ Error resolving variable {locator}: {str(e)}")
                    locator_info.update({
                        'variable': locator,
                        'value': 'ERROR_RESOLVING_VARIABLE'
                    })
            else:
                locator_info.update({
                    'variable': 'Direct Locator',
                    'value': locator,
                    'locator': locator
                })
            
            self.current_test_locators[keyword_name].append(locator_info)
            
        except Exception as e:
            logger.console(f"❌ Error tracking locator: {str(e)}")

    def _find_locator_file(self, locator_value):
        """Find the file containing the locator"""
        try:
            if not locator_value:
                return "Unknown"

            # Normalize locator by removing quotes for searching
            search_value = re.sub(r"['\"](.*?)['\"]", r"\1", locator_value)
            
            page_objects_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'PageObjects')
            
            for root, _, files in os.walk(page_objects_dir):
                for file in files:
                    if file.endswith('.py'):
                        file_path = os.path.join(root, file)
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                content = f.read()
                                # Look for the locator with or without quotes
                                if search_value in content:
                                    relative_path = os.path.relpath(file_path, os.path.dirname(os.path.dirname(__file__)))
                                    return relative_path.replace('/', '\\')
                        except Exception as e:
                            logger.console(f"⚠️ Error reading {file}: {str(e)}")

            return "Unknown"
        except Exception as e:
            logger.console(f"❌ Error finding file: {str(e)}")
            return "Unknown"

    def _find_variable_and_file(self, locator_value):
        """Find variable name and file path by searching in PageObjects"""
        try:
            page_objects_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'PageObjects')
            
            # Normalize the search locator by removing quotes and spaces
            search_locator = locator_value.replace("'", "").replace('"', "").strip()
            logger.console(f"\n🔍 Searching for locator: {search_locator}")
            
            # Search all Python files in PageObjects directory
            for root, _, files in os.walk(page_objects_dir):
                for file in files:
                    if file.endswith('.py'):
                        file_path = os.path.join(root, file)
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                lines = f.readlines()
                                for line in lines:
                                    # Skip comments and empty lines
                                    if line.strip().startswith('#') or not line.strip():
                                        continue
                                    
                                    # Look for variable assignment
                                    if '=' in line:
                                        # Normalize the line content
                                        line_content = line.split('=')[1].strip()
                                        line_content = line_content.replace("'", "").replace('"', "").strip()
                                        
                                        # Compare normalized values
                                        if search_locator == line_content:
                                            var_name = line.split('=')[0].strip()
                                            relative_path = os.path.relpath(file_path, os.path.dirname(os.path.dirname(__file__)))
                                            logger.console(f"✅ Found in {relative_path}")
                                            logger.console(f"✅ Variable name: {var_name}")
                                            return {
                                                "variable_name": f"${{{var_name}}}",
                                                "file_path": relative_path.replace('/', '\\')
                                            }
                        except Exception as e:
                            logger.console(f"⚠️ Error reading file {file}: {str(e)}")
            
            # If not found with exact match, try with contains
            for root, _, files in os.walk(page_objects_dir):
                for file in files:
                    if file.endswith('.py'):
                        file_path = os.path.join(root, file)
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                content = f.read()
                                # Remove quotes and spaces for comparison
                                content_normalized = content.replace("'", "").replace('"', "").replace(" ", "")
                                if search_locator.replace(" ", "") in content_normalized:
                                    # Found a match, now find the variable name
                                    lines = content.split('\n')
                                    for line in lines:
                                        if search_locator in line.replace("'", "").replace('"', "") and '=' in line:
                                            var_name = line.split('=')[0].strip()
                                            relative_path = os.path.relpath(file_path, os.path.dirname(os.path.dirname(__file__)))
                                            logger.console(f"✅ Found in {relative_path}")
                                            logger.console(f"✅ Variable name: {var_name}")
                                            return {
                                                "variable_name": f"${{{var_name}}}",
                                                "file_path": relative_path.replace('/', '\\')
                                            }
                        except Exception as e:
                            logger.console(f"⚠️ Error reading file {file}: {str(e)}")
            
            logger.console("⚠️ Locator not found in any PageObject file")
            return {"variable_name": "Direct Locator", "file_path": "Unknown"}
            
        except Exception as e:
            logger.console(f"❌ Error finding variable and file: {str(e)}")
            return {"variable_name": "Direct Locator", "file_path": "Unknown"}

    def _process_failed_locator(self, test_name, error_msg, failed_locator):
        """Process and track failed locator"""
        try:
            # Find variable name and file path
            variable_name = self._find_variable_and_file(failed_locator)
            file_path = self._find_locator_file(failed_locator)
            
            # Create failure entry
            failure_info = {
                "test_name": test_name,
                "locator_value": failed_locator,
                "variable_name": variable_name["variable_name"],
                "file_path": file_path or "Unknown",
                "error_message": error_msg,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            # Add to failures list
            self.failed_locators["failures"].append(failure_info)
            
            # Save updated failed locators
            self._save_failed_locators()
            
            logger.console(f"Tracked failed locator: {failed_locator}")
            
        except Exception as e:
            logger.console(f"Error processing failed locator: {str(e)}")
            logger.console(traceback.format_exc())

    def _process_healing_response(self, locator, response, attempt=1):
        """Process healing response with retry logic"""
        try:
            # Add debug logging
            logger.console(f"\n�� Processing healing response for locator: {locator}")
            logger.console(f"📄 Response type: {type(response)}")
            logger.console(f"📄 Response content: {response}")

            # Check if response is None
            if response is None:
                logger.console("⚠️ Received None response from healing agent")
                return None

            # Check if response is a string containing error message
            if isinstance(response, str) and "Invalid response format" in response:
                logger.console(f"\n⚠️ Invalid response received (Attempt {attempt}/{self.max_retries})")
                
                if attempt < self.max_retries:
                    logger.console(f"🔄 Retrying healing for locator: {locator}")
                    
                    # Add delay before retry
                    time.sleep(self.retry_delay)
                    
                    try:
                        # Add debug logging for retry attempt
                        logger.console(f"\n📝 Making retry attempt {attempt + 1}")
                        new_response = self.healing_agent.heal_locator(locator)
                        logger.console(f"📄 New response received: {new_response}")
                        
                        return self._process_healing_response(locator, new_response, attempt + 1)
                    except Exception as retry_error:
                        logger.console(f"❌ Error during retry: {str(retry_error)}")
                        return None
                else:
                    logger.console(f"\n❌ Max retries ({self.max_retries}) reached for locator: {locator}")
                    return None

            # Try to parse response as JSON if it's a string
            if isinstance(response, str):
                try:
                    import json
                    parsed_response = json.loads(response)
                    logger.console("✅ Successfully parsed response as JSON")
                    return parsed_response
                except json.JSONDecodeError as json_error:
                    logger.console(f"⚠️ Failed to parse response as JSON: {str(json_error)}")
                    if attempt < self.max_retries:
                        return self._process_healing_response(locator, response, attempt + 1)
                    return None

            return response
            
        except Exception as e:
            logger.console(f"\n❌ Error processing healing response: {str(e)}")
            logger.console(f"📑 Stack trace:\n{traceback.format_exc()}")
            return None

    def _save_locator_failure(self, test_name, error_msg, locator=None, file_path=None):
        """Save locator failure details to JSON file with retry logic"""
        try:
            # Get the complete locator from error message
            failed_locator = self._extract_locator_from_error(error_msg)
            if not failed_locator:
                logger.console("\n⚠️ Could not extract locator from error message")
                return

            # Find variable name and file path by searching PageObjects
            source_info = self._find_variable_and_file(failed_locator)
            
            # Create failure details
            failure_details = {
                "test_name": test_name,
                "locator_value": failed_locator,
                "variable_name": source_info["variable_name"],
                "file_path": source_info["file_path"],
                "error_message": error_msg,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }

            # Load existing failures
            if os.path.exists(self.failed_locators_file):
                with open(self.failed_locators_file, 'r') as f:
                    self.failed_locators = json.load(f)
            
            # Add new failure
            self.failed_locators["failures"].append(failure_details)
            
            # Save to file
            with open(self.failed_locators_file, 'w', encoding='utf-8') as f:
                json.dump(self.failed_locators, f, indent=4, ensure_ascii=False)

            if locator:
                try:
                    # Add debug logging before healing attempt
                    logger.console(f"\n🔄 Attempting to heal locator: {locator}")
                    
                    # Get healing response with retry logic
                    healing_response = self.healing_agent.heal_locator(locator)
                    logger.console(f"📄 Initial healing response: {healing_response}")
                    
                    processed_response = self._process_healing_response(locator, healing_response)
                    logger.console(f"📄 Processed response: {processed_response}")
                    
                    if processed_response:
                        # Add healing result to failure details
                        failure_details["healing_result"] = processed_response
                        logger.console(f"\n✅ Successfully healed locator: {locator}")
                        
                        # Log the healed locator details
                        if isinstance(processed_response, dict):
                            logger.console(f"🔧 Healed locator value: {processed_response.get('healed_locator', 'N/A')}")
                            logger.console(f"📝 Healing method: {processed_response.get('method', 'N/A')}")
                    else:
                        failure_details["healing_result"] = "Healing failed after retries"
                        logger.console(f"\n⚠️ Could not heal locator: {locator}")
                    
                except Exception as healing_error:
                    logger.console(f"\n❌ Error during healing process: {str(healing_error)}")
                    logger.console(f"📑 Stack trace:\n{traceback.format_exc()}")
                    failure_details["healing_result"] = f"Error during healing: {str(healing_error)}"

        except Exception as e:
            logger.console(f"\n❌ Error saving locator failure: {str(e)}")
            logger.console(f"📑 Stack trace:\n{traceback.format_exc()}")

    def _normalize_locator(self, locator):
        """Normalize locator for comparison"""
        if not locator:
            return ""
        # Remove spaces and quotes
        normalized = re.sub(r'\s+', '', str(locator))
        normalized = normalized.replace("'", "").replace('"', "")
        return normalized.lower()

    def _get_variable_source_for_locator(self, locator):
        """Find variable name and source path for a locator value"""
        try:
            variables = BuiltIn().get_variables()
            
            # Handle variable reference
            if str(locator).startswith('${'):
                var_name = str(locator)
                var_value = variables.get(var_name, locator)
                
                # Clean up variable name for display
                var_name = var_name.strip('${').strip('}')
                
                # Find the file containing this variable
                file_path = self._find_locator_file(var_value)
                
                return {
                    "variable_name": f"${{{var_name}}}",
                    "file_path": file_path or "Unknown"
                }
            else:
                # For direct locators, search if it exists as a variable value
                for var_name, var_value in variables.items():
                    if str(var_value) == str(locator):
                        file_path = self._find_locator_file(locator)
                        return {
                            "variable_name": str(var_name),
                            "file_path": file_path or "Unknown"
                        }
                
                return {
                    "variable_name": "Direct Locator",
                    "file_path": self._find_locator_file(locator) or "Unknown"
                }
                
        except Exception as e:
            logger.console(f"Error finding variable source: {str(e)}")
            return {"variable_name": "Unknown", "file_path": "Unknown"}

    def _get_file_path_from_error(self, error_msg):
        """Extract the file path from the error message if available."""
        import re
        
        # Use a regular expression to find a file path in the error message
        match = re.search(r'["\'](.*?)["\']', error_msg)
        if match:
            return match.group(1)  # Return the extracted file path
        return "Unknown"  # Default if no file path is found

    def verify_locator_failures(self):
        """Verify saved locator failures against page sources"""
        logger.console("\n🔍 Verifying locator failures...")
        
        try:
            with open(self.failed_locators_file, 'r') as f:
                failed_locators = json.load(f)
            
            verified_failures = {"failures": []}
            page_sources = [f for f in os.listdir(self.page_sources_dir) if f.endswith('.html')]
            
            if not page_sources:
                logger.console("⚠️ No page sources found")
                return
            
            for failure in failed_locators.get("failures", []):
                locator = failure.get("locator_value")
                if not locator:
                    continue
                    
                logger.console(f"\nVerifying: {locator}")
                verification_status = []
                
                for source_file in page_sources:
                    try:
                        with open(os.path.join(self.page_sources_dir, source_file), 'r', encoding='utf-8') as f:
                            result = self._check_locator_in_source(locator, f.read())
                            verification_status.append(result)
                    except Exception as e:
                        verification_status.append(None)
                        logger.console(f"⚠️ Error checking source file: {str(e)}")
                
                if all(status is None for status in verification_status):
                    logger.console("⚠️ Could not verify locator (all checks resulted in errors)")
                    verified_failures["failures"].append(failure)
                elif not any(verification_status):
                    logger.console(f"✅ Confirmed change")
                    verified_failures["failures"].append(failure)
                else:
                    logger.console("❌ Locator still exists in some page sources - not a genuine failure")
            
            with open(self.failed_locators_file, 'w') as f:
                json.dump(verified_failures, f, indent=4)
                
            logger.console(f"\n✅ Found {len(verified_failures['failures'])} confirmed changes")
            
        except Exception as e:
            logger.console(f"❌ Error in verify_locator_failures: {str(e)}")

    def _check_locator_in_source(self, locator, page_source):
        """Check if locator exists in page source"""
        try:
            soup = BeautifulSoup(page_source, 'html.parser')
            
            if locator.startswith('//'):
                # XPath handling
                for attr in ['class', 'id', 'name', 'data-testid', 'title', 'role']:
                    attr_pattern = f'@{attr}=[\'"](.*?)[\'"]'
                    match = re.search(attr_pattern, locator)
                    if match:
                        value = match.group(1)
                        return bool(soup.find(attrs={attr: value}))
                        
                # Text content check
                tag_match = re.match(r'//(\w+)\[text\(\)=[\'"](.*?)[\'"]\]', locator)
                if tag_match:
                    tag, text = tag_match.groups()
                    return bool(soup.find(tag, string=text))
                    
            elif '=' in locator:
                locator_type, value = locator.split('=', 1)
                value = value.strip('"\'')
                
                if locator_type == 'id':
                    return bool(soup.find(id=value))
                elif locator_type == 'class':
                    return bool(soup.find(class_=value))
                elif locator_type == 'name':
                    return bool(soup.find(attrs={"name": value}))
                elif locator_type == 'css':
                    return bool(soup.select(value))
            
            return locator in page_source
            
        except Exception as e:
            return None

    def close(self):
        """Called when Robot Framework execution ends"""
        try:
            logger.console("\n🤖 Starting self-healing process...")
            
            # Verify locator failures before healing
            self.verify_locator_failures()
            
            # This triggers the self-healing process
            self.healing_agent.end_session()
            
            # Add healing summary to Robot log
            self._add_healing_summary_to_log()
            
            # Add retry summary
            retry_summary = self._get_retry_summary()
            if retry_summary:
                logger.console("\n📊 Healing Retry Summary:")
                for locator, attempts in retry_summary.items():
                    logger.console(f"  - {locator}: {attempts} attempt(s)")
            
            logger.console("\n✨ Self-healing process completed!")
            
            # Clean up data directories
            self._cleanup_data_directories()
            
        except Exception as e:
            logger.warn(f"Error in close: {str(e)}")

    def _add_healing_summary_to_log(self):
        """Add self-healing summary to Robot Framework's log.html"""
        try:
            # Get paths from config
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            config_path = os.path.join(base_dir, 'Environment', 'config.json')
            
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            results_dir = os.path.join(base_dir, config.get('results_dir', 'results'))
            healed_locators_file = os.path.join(base_dir, 'locator_data', 'healed_locators.json')
            log_file = os.path.join(results_dir, "log.html")
            
            if not os.path.exists(healed_locators_file):
                logger.console("ℹ️ No healed locators found to add to report")
                return
            
            if not os.path.exists(log_file):
                logger.console(f"⚠️ Could not find log.html in {results_dir}")
                return
            
            # Load healed locators
            with open(healed_locators_file, 'r') as f:
                healed_data = json.load(f)
            
            if not healed_data:
                logger.console("ℹ️ No healing data to report")
                return
            
            # Create the healing HTML summary
            healing_html = """
            <div style="margin: 30px 0; background-color: #F8F9FA; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                <div style="background-color: #0EA5E9; color: white; padding: 15px 20px; border-radius: 8px 8px 0 0;">
                    <h2 style="margin: 0; font-size: 1.4em;">🔧 Self-Healing Summary</h2>
                </div>
                <div style="padding: 20px;">
                    <table style="width: 100%; border-collapse: collapse; margin-bottom: 10px;">
                        <thead>
                            <tr style="background-color: #E0F2FE; text-align: left;">
                                <th style="padding: 12px 15px; border-bottom: 2px solid #0EA5E9;">Variable Info</th>
                                <th style="padding: 12px 15px; border-bottom: 2px solid #0EA5E9;">Healed Locator</th>
                                <th style="padding: 12px 15px; border-bottom: 2px solid #0EA5E9;">Solution Description</th>
                            </tr>
                        </thead>
                        <tbody>
            """
            
            # Add each healed locator to the summary
            for healing in healed_data:
                variable_info = healing.get('variable_info', {})
                source_file = variable_info.get('source_file', 'Unknown Location')
                variable_name = variable_info.get('variable_name', '')
                
                # Make the file path more readable
                readable_path = source_file.split('\\')[-1] if '\\' in source_file else source_file.split('/')[-1]
                
                healing_html += f"""
                    <tr style="border-bottom: 1px solid #E2E8F0;">
                        <td style="padding: 12px 15px;">
                            <div style="color: #1E40AF; font-weight: bold;">{variable_name}</div>
                            <div style="color: #6B7280; font-size: 0.9em;">Source: {readable_path}</div>
                        </td>
                        <td style="padding: 12px 15px;">
                            <div style="color: #059669; font-family: monospace; font-size: 0.9em; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">
                                {healing.get('healed_locator', '')}
                            </div>
                        </td>
                        <td style="padding: 12px 15px;">
                            <div style="color: #4B5563; font-size: 0.95em;">
                                {healing.get('solution_description', '')}
                            </div>
                        </td>
                    </tr>
                """
            
            healing_html += """
                        </tbody>
                    </table>
                    <div style="text-align: right; padding-top: 10px; color: #6B7280; font-size: 0.9em;">
                        ✨ Powered by Self-Healing Framework
                    </div>
                </div>
            </div>
            """
            
            # Read the log file content
            with open(log_file, 'r', encoding='utf-8') as f:
                log_content = f.read()
            
            # Insert healing summary before </body>
            if '</body>' in log_content:
                modified_content = log_content.replace('</body>', f'{healing_html}</body>')
            
                # Write the updated content back to log.html
                with open(log_file, 'w', encoding='utf-8') as f:
                    f.write(modified_content)
            
                logger.console(f"\n✅ Added self-healing summary to {log_file}")
            else:
                logger.console("\n⚠️ Could not find suitable location to insert healing summary")
            
        except Exception as e:
            logger.console(f"❌ Error adding healing summary to log: {str(e)}")
            logger.console(traceback.format_exc())

    def _cleanup_data_directories(self):
        """Clean up data directories after processing"""
        try:
            import shutil
            
            logger.console("\n🧹 Starting cleanup process...")
            
            # Clean up locator_data directory
            if os.path.exists(self.locator_data_dir):
                shutil.rmtree(self.locator_data_dir)
                logger.console(f"✅ Removed locator data directory: {self.locator_data_dir}")
                
            # Clean up page sources directory
            if os.path.exists(self.page_sources_dir):
                shutil.rmtree(self.page_sources_dir)
                logger.console(f"✅ Removed page sources directory: {self.page_sources_dir}")
                
            logger.console("🎉 Cleanup completed successfully!")
            
        except Exception as e:
            logger.console(f"⚠️ Error during cleanup: {str(e)}")
            logger.console(traceback.format_exc())

    def _is_locator(self, value):
        """Check if a value is a locator"""
        if isinstance(value, str):
            # Common locator patterns
            patterns = [
                r"^//",  # XPath
                r"^id=",
                r"^name=",
                r"^css=",
                r"^class=",
                r"^xpath=",
                r"^link=",
                r"^partial link="
            ]
            return any(re.match(pattern, value) for pattern in patterns)
        return False

    def _extract_locators(self, args):
        """Extract locators from keyword arguments"""
        locators = []
        
        for arg in args:
            arg_str = str(arg)
            
            # Check for common locator patterns
            if any(arg_str.startswith(prefix) for prefix in [
                "xpath=", "id=", "name=", "css=", "class=", "//",
                "tag=", "link=", "partial link=", "dom=", "jquery=",
                "sizzle=", "chain=", "accessibility_id=", "android=", "ios=",
                "data-testid=", "data-test=", "data-qa=", "data-cy=",
                "aria-label=", "aria-labelledby=", "aria-describedby=",
                "title=", "alt=", "text=", "partial text=", "image=",
                "index=", "model=", "binding=", "button=", "radio=",
                "checkbox=", "file=", "pl"
            ]):
                locator_data = {
                    "locator": arg_str,
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "type": self._determine_locator_type(arg_str)
                }
                locators.append(locator_data)
                
            # Try to resolve if it's a variable
            elif arg_str.startswith("${") and arg_str.endswith("}"):
                try:
                    resolved_value = BuiltIn().get_variable_value(arg_str)
                    if resolved_value and self._is_locator(resolved_value):
                        locator_data = {
                            "locator": resolved_value,
                            "variable_name": arg_str,
                            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "type": self._determine_locator_type(resolved_value)
                        }
                        locators.append(locator_data)
                except:
                    pass
                
        return locators

    def _determine_locator_type(self, locator):
        """Determine the type of locator"""
        if locator.startswith("//"):
            return "xpath"
        for prefix in ["id=", "name=", "css=", "class="]:
            if locator.startswith(prefix):
                return prefix[:-1]  # Remove the '=' from prefix
        return "unknown"

    def _get_retry_summary(self):
        """Get summary of healing retries"""
        try:
            retry_summary = {}
            
            # Load failed locators
            if os.path.exists(self.failed_locators_file):
                with open(self.failed_locators_file, 'r') as f:
                    failed_locators = json.load(f)
                
                for failure in failed_locators.get("failures", []):
                    locator = failure.get("locator_value")
                    healing_result = failure.get("healing_result", "")
                    
                    if isinstance(healing_result, str) and "attempt" in healing_result.lower():
                        # Extract attempt count from healing result
                        attempts = int(re.search(r'Attempt (\d+)', healing_result).group(1))
                        retry_summary[locator] = attempts
            
            return retry_summary
            
        except Exception as e:
            logger.console(f"⚠️ Error getting retry summary: {str(e)}")
            return {}
