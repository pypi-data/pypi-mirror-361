from robot.api import logger
from datetime import datetime
import json
import os
# from enhanced_candidate_algo import generate_enhanced_candidates
from candidate_algo import generate_enhanced_candidates
import openai
from dotenv import load_dotenv
import re
import traceback

class SelfHealingAgent:
    """Agent responsible for self-healing locator failures"""
    
    def __init__(self):
        logger.console("\n🤖 Initializing Self-Healing Agent")
        self.test_execution_complete = False
        
        # Setup paths
        current_dir = os.path.dirname(os.path.abspath(__file__))
        base_dir = os.path.dirname(current_dir)
        
        # Load config.json
        config_path = os.path.join(base_dir, 'Environment', 'config.json')
        try:
            with open(config_path, 'r') as f:
                self.config = json.load(f)
                logger.console(f"✅ Loaded config from: {config_path}")
        except Exception as e:
            logger.console(f"❌ Error loading config.json: {str(e)}")
            raise
        
        # Get paths from config
        self.page_objects_dir = os.path.join(base_dir, self.config.get('page_objects_dir'))
        self.locator_data_dir = os.path.join(base_dir, self.config.get('data_path'))
        
        # Get file paths from config
        locator_data_config = self.config.get('locator_data', {})
        self.failures_file = os.path.join(self.locator_data_dir, locator_data_config.get('locator_failures'))
        self.prompts_file = os.path.join(self.locator_data_dir, locator_data_config.get('healing_prompts'))
        self.healed_locators_file = os.path.join(self.locator_data_dir, locator_data_config.get('healed_locators'))
        
        logger.console(f"📁 Using paths from config:")
        logger.console(f"  PageObjects: {self.page_objects_dir}")
        logger.console(f"  Data Directory: {self.locator_data_dir}")
        logger.console(f"  Failures File: {self.failures_file}")
        logger.console(f"  Prompts File: {self.prompts_file}")
        logger.console(f"  Healed Locators File: {self.healed_locators_file}")
        
        # Create directory if it doesn't exist
        os.makedirs(self.locator_data_dir, exist_ok=True)
        
        # Setup OpenAI
        self._setup_openai()

    def _setup_openai(self):
        """Setup OpenAI configuration"""
        try:
            # Load environment variables from Environment/.env
            env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'Environment', '.env')
            if not os.path.exists(env_path):
                raise FileNotFoundError(f"Environment file not found at {env_path}")
            
            load_dotenv(env_path)
            api_key = os.getenv("OPENAI_API_KEY")
            
            if not api_key:
                raise ValueError("OpenAI API key not found in Environment/.env file")
            
            openai.api_key = api_key
            logger.console("✅ OpenAI API configured successfully")
            
        except Exception as e:
            logger.console(f"❌ Error configuring OpenAI: {str(e)}")
            raise

    def get_healed_locator_from_openai(self, prompt_data):
        """Send prompt to OpenAI API and get healed locator response"""
        try:
            prompt = json.dumps(prompt_data)
            
            # Use the new OpenAI API format
            client = openai.OpenAI(api_key=openai.api_key)
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.4
            )

            # Log the complete response from OpenAI
            logger.console("\n📥 Complete OpenAI Response:")
            logger.console(f"Response object: {response}")
            
            healed_locator = response.choices[0].message.content.strip()
            logger.console(f"\n📝 Extracted content:")
            logger.console(f"{healed_locator}")
            
            # Clean the response - remove markdown code block markers
            cleaned_response = healed_locator.replace('```json', '').replace('```', '').strip()
            
            # Validate response format
            try:
                healed_data = json.loads(cleaned_response)
                if not all(key in healed_data for key in ['correct_locator', 'solution_description', 'variable_info']):
                    raise ValueError("Response missing required fields")
                logger.console("\n✅ Successfully parsed response as valid JSON")
                return healed_data
            except (json.JSONDecodeError, ValueError) as e:
                logger.console(f"❌ Invalid response format: {e}")
                logger.console(f"Failed to parse content as JSON: {cleaned_response}")
                return None
                
        except Exception as e:
            logger.console(f"❌ Error getting response from OpenAI: {e}")
            logger.console(f"📑 Stack trace:\n{traceback.format_exc()}")
            return None

    def update_pageobject_locators(self, healed_locators):
        """Updates the locators in PageObjects files with healed versions"""
        updates_by_file = {}
        
        # First, get all Python files in PageObjects directory
        page_object_files = {}
        for root, _, files in os.walk(self.page_objects_dir):
            for file in files:
                if file.endswith('.py'):
                    full_path = os.path.join(root, file)
                    page_object_files[file] = full_path
                    logger.console(f"📄 Found PageObject file: {full_path}")

        for locator in healed_locators:
            try:
                # Get file info from variable info
                source_file = locator['variable_info']['source_file']
                file_name = os.path.basename(source_file)
                variable_name = locator['variable_info']['variable_name']
                new_locator = locator['healed_locator']
                
                logger.console(f"\n🔍 Looking for {variable_name} in file: {file_name}")
                
                # Find the full path of the file
                if file_name in page_object_files:
                    full_file_path = page_object_files[file_name]
                    logger.console(f"✅ Found file at: {full_file_path}")
                    
                    if full_file_path not in updates_by_file:
                        updates_by_file[full_file_path] = []
                    
                    updates_by_file[full_file_path].append({
                        'variable_name': variable_name,
                        'new_locator': new_locator,
                        'solution': locator['solution_description']
                    })
                else:
                    logger.console(f"❌ Could not find {file_name} in PageObjects directory")
                    # Try to find similar file names
                    similar_files = [f for f in page_object_files.keys() 
                                   if f.lower().replace('_', '') == file_name.lower().replace('_', '')]
                    if similar_files:
                        logger.console(f"💡 Similar files found: {', '.join(similar_files)}")
                    continue
                
            except KeyError as e:
                logger.console(f"❌ Missing required information in healed locator: {e}")
                logger.console(f"Healed locator data: {locator}")
                continue

        # Process updates for each file
        for file_path, updates in updates_by_file.items():
            try:
                logger.console(f"\n📂 Processing file: {file_path}")
                
                # Read file content
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()

                # Track if file was actually modified
                file_modified = False
                updated_lines = []
                i = 0
                
                while i < len(lines):
                    line = lines[i]
                    original_line = line
                    
                    # Preserve existing conflict markers
                    if line.startswith('<<<<<<< Current'):
                        conflict_lines = []
                        while i < len(lines) and not lines[i].startswith('>>>>>>> Healed'):
                            conflict_lines.append(lines[i])
                            i += 1
                        if i < len(lines):
                            conflict_lines.append(lines[i])
                        updated_lines.extend(conflict_lines)
                        i += 1
                        continue

                    # Check for variables to update
                    line_updated = False
                    for update in updates:
                        var_name = update['variable_name'].strip('${}')  # Remove ${} if present
                        
                        # Match variable name at start of line followed by =
                        if re.match(rf'^\s*{var_name}\s*=', line.strip()):
                            logger.console(f"\n🔄 Updating locator: {var_name}")
                            logger.console(f"  Old: {line.strip()}")
                            logger.console(f"  New: {update['new_locator']}")
                            
                            # Check if this variable already has a conflict marker
                            if not any(l.strip().startswith(f"{var_name} =") 
                                     for l in ''.join(updated_lines).split('>>>>>>> Healed')):
                                updated_lines.extend([
                                    "<<<<<<< Current\n",
                                    original_line,
                                    "=======\n",
                                    f"{var_name} = \"{update['new_locator']}\"\n",
                                    f"# Solution: {update['solution']}\n",
                                    ">>>>>>> Healed\n"
                                ])
                                line_updated = True
                                file_modified = True
                                logger.console("  ✅ Update added with conflict markers")
                                break
                    
                    if not line_updated:
                        updated_lines.append(line)
                    i += 1

                # Only write to file if modifications were made
                if file_modified:
                    logger.console(f"\n💾 Writing updates to: {file_path}")
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.writelines(updated_lines)
                    logger.console(f"✅ Successfully updated {file_path}")
                else:
                    logger.console(f"ℹ️ No changes needed in {file_path}")

            except Exception as e:
                logger.console(f"❌ Error updating {file_path}: {str(e)}")
                logger.console(f"Detailed error: {traceback.format_exc()}")

        return True

    def process_failed_locators(self):
        """Process failed locators and generate prompts one by one"""
        try:
            if not os.path.exists(self.failures_file):
                logger.console("No locator failures found to process")
                return

            # Load failed locators
            with open(self.failures_file, 'r', encoding='utf-8') as f:
                failures = json.load(f)

            llm_prompts = []
            healed_locators = []
            updated = False

            for index, failure in enumerate(failures.get("failures", []), start=1):
                locator_value = failure.get("locator_value")
                if not locator_value or not self._is_locator(locator_value):
                    continue  # Skip if it's not a valid locator

                logger.console(f"\n🔍 Analyzing locator: {locator_value}")
                
                # Generate candidates using the enhanced algorithm
                candidates_result = generate_enhanced_candidates(locator_value, mode="lenient")
                candidates = candidates_result.get("candidates", [])
                
                if candidates and not candidates[0].get("message"):
                    # Found valid candidates - update the existing failure entry
                    failure.update({
                        "healing_candidates": candidates,
                        "healing_status": "CANDIDATES_GENERATED"
                    })
                    logger.console(f"✅ Found {len(candidates)} potential healing candidates")
                    updated = True
                    
                    # Generate prompt for this failure
                    prompt_message = self._create_prompt_message(
                        failure.get("test_name", "Unknown Test"),
                        failure.get("error_message", ""),
                        locator_value,
                        candidates,
                        failure
                    )
                    
                    llm_prompts.append({
                        f"Prompt {index}": prompt_message
                    })
                    logger.console(f"📝 Generated prompt for locator: {locator_value}")
                    
                    # Get healed locator from OpenAI
                    healed_data = self.get_healed_locator_from_openai(prompt_message)
                    if healed_data:
                        healed_locators.append({
                            "prompt": f"Prompt {index}",
                            "healed_locator": healed_data.get('correct_locator'),
                            "solution_description": healed_data.get('solution_description'),
                            "variable_info": healed_data.get('variable_info')
                        })
                        logger.console(f"✨ Received healing suggestion for locator: {locator_value}")
                    
                else:
                    failure.update({
                        "healing_status": "NO_CANDIDATES_FOUND"
                    })
                    logger.console("❌ No suitable candidates found")

            if updated:
                # Save updated failures with candidates
                with open(self.failures_file, 'w', encoding='utf-8') as f:
                    json.dump(failures, f, indent=4)
                logger.console("\n💾 Updated locator failures with healing candidates")
                
                # Save prompts
                if llm_prompts:
                    with open(self.prompts_file, 'w', encoding='utf-8') as f:
                        json.dump(llm_prompts, f, indent=4)
                    logger.console(f"\n📝 Saved {len(llm_prompts)} LLM prompts")
                
                # Save healed locators and update PageObjects
                if healed_locators:
                    with open(self.healed_locators_file, 'w', encoding='utf-8') as f:
                        json.dump(healed_locators, f, indent=4)
                    logger.console(f"\n💫 Saved {len(healed_locators)} healed locators")
                    
                    # Update PageObjects with healed locators
                    self.update_pageobject_locators(healed_locators)

            return failures

        except Exception as e:
            logger.console(f"Error processing failed locators: {str(e)}")
            return None

    def generate_llm_prompts(self, failures_data):
        """Generate LLM prompts from failures data"""
        try:
            llm_prompts = []
            
            for index, failure in enumerate(failures_data.get("failures", []), start=1):
                test_case_name = failure.get("test_name", "Unknown Test")
                error_message = failure.get("error_message", "")
                broken_locator = failure.get("locator_value", "")
                candidates = failure.get("healing_candidates", [])
                
                # Create prompt message
                prompt_message = self._create_prompt_message(
                    test_case_name,
                    error_message,
                    broken_locator,
                    candidates,
                    failure
                )
                
                llm_prompts.append({
                    f"Prompt {index}": prompt_message
                })
            
            # Save prompts to file
            if llm_prompts:
                with open(self.prompts_file, 'w', encoding='utf-8') as f:
                    json.dump(llm_prompts, f, indent=4)
                logger.console(f"\n📝 Generated and saved {len(llm_prompts)} LLM prompts")
            
            return llm_prompts

        except Exception as e:
            logger.console(f"Error generating LLM prompts: {str(e)}")
            return []

    def _create_prompt_message(self, test_case_name, error_message, broken_locator, candidates, failure_info):
        """Create a structured prompt message"""
        system_message = "Role: System - You are a web UI test script repair tool."
        
        prompt_message = {
            "system_message": system_message,
            "error_message_content": f"Role: User - Robot Framework Test using SeleniumLibrary failed with the following error message: {error_message}",
            "broken_locator_content": f"Role: User - Broken element locator used: {broken_locator}",
            "test_case_name_content": f"Role: User - Robot Framework Test Name: {test_case_name}",
            "candidate_contents": []
        }

        # Add candidate information
        for idx, candidate in enumerate(candidates, 1):
            candidate_content = {
                "Candidate": f"#{idx}",
                "Tag": candidate.get('tag', 'N/A'),
                "Class": candidate.get('class', 'N/A'),
                "Type": candidate.get('type', 'N/A'),
                "ID": candidate.get('id', 'N/A'),
                "Text": candidate.get('text', 'N/A'),
                "XPath": candidate.get('xpath', 'N/A'),
                "Similarity": candidate.get('similarity', 'N/A')
            }
            prompt_message["candidate_contents"].append(candidate_content)

        # Add variable information
        prompt_message["variable_info"] = {
            "variable_name": failure_info.get("variable_name", "unknown_variable"),
            "source_file": failure_info.get("file_path", "unknown_file")
        }

        # Add solution request format
        prompt_message["solution_request_content"] = {
            "message": "Role: User - Please, give your answer in JSON format important avoid absolute paths, without JSON suffix and try to find dynamic locators. Include the variable name and source file in your response.",
            "example": {
                "correct_locator": "locator_value",
                "solution_description": "solution",
                "variable_info": {
                    "variable_name": "original_variable_name",
                    "source_file": "path/to/source_file.py"
                }
            }
        }

        return prompt_message

    def end_session(self):
        """Complete the healing session"""
        logger.console("\n🔄 Starting self-healing process...")
        self.test_execution_complete = True
        
        # Process failed locators and generate prompts in one pass
        failures_data = self.process_failed_locators()
        
        logger.console("\n✨ Self-healing process completed!")

    def _is_locator(self, locator):
        """Check if the provided string is a valid locator."""
        # Implement logic to determine if the string is a locator
        return locator.startswith(("//", "id=", "name=", "class=", "css="))

    def clean_failed_locators(self):
        """Clean the locator_failures.json file by removing non-locator entries."""
        try:
            # Load existing failures
            if os.path.exists(self.failures_file):
                with open(self.failures_file, 'r', encoding='utf-8') as f:
                    failed_locators = json.load(f)
            else:
                logger.console("No locator failures file found.")
                return

            # Filter out non-locators
            cleaned_failures = []
            for failure in failed_locators.get("failures", []):
                if self._is_locator(failure["locator_value"]):
                    cleaned_failures.append(failure)
                else:
                    logger.console(f"⚠️ Removing non-locator entry: {failure['locator_value']}")

            # Save cleaned failures back to the file
            with open(self.failures_file, 'w', encoding='utf-8') as f:
                json.dump({"failures": cleaned_failures}, f, indent=4, ensure_ascii=False)

            logger.console("✅ Cleaned locator failures file, removed non-locator entries.")

        except Exception as e:
            logger.console(f"❌ Error cleaning locator failures: {str(e)}")
            logger.console(traceback.format_exc())

    # Call this method before starting candidate generation
    def start_candidate_generation(self):
        """Start the candidate generation process after cleaning locator failures."""
        self.clean_failed_locators()  # Clean the locator failures before proceeding
        # Proceed with candidate generation logic...

    def heal_locator(self, locator):
        """Heal a broken locator by generating candidates and getting OpenAI suggestions"""
        try:
            logger.console(f"\n🔍 Analyzing locator: {locator}")
            
            # Generate candidates using the enhanced algorithm
            candidates_result = generate_enhanced_candidates(locator, mode="lenient")
            
            if not candidates_result:
                logger.console("❌ No candidates result returned")
                return None
                
            # Check if there's an error message in the result
            if candidates_result.get("message"):
                logger.console(f"⚠️ Error generating candidates: {candidates_result['message']}")
                return None
                
            # Extract the actual candidates list from the new structure
            candidates = candidates_result.get("candidates", [])
            
            if not candidates:
                logger.console("❌ No healing candidates found")
                total_found = candidates_result.get("total_found", 0)
                files_processed = candidates_result.get("files_processed", 0)
                logger.console(f"📊 Search completed: {files_processed} files processed, {total_found} total elements analyzed")
                return None
                
            logger.console(f"✅ Found {len(candidates)} potential healing candidates")
            
            # Create prompt for OpenAI
            prompt_message = self._create_prompt_message(
                "Unknown Test",  # We don't have test name in this context
                f"Failed to locate element: {locator}",
                locator,
                candidates,
                {"variable_name": "unknown", "file_path": "unknown"}  # Basic failure info
            )
            
            # Get healing suggestion from OpenAI
            healed_data = self.get_healed_locator_from_openai(prompt_message)
            
            if healed_data:
                logger.console(f"✨ Successfully generated healing suggestion")
                return healed_data
            else:
                logger.console("❌ Failed to get healing suggestion from OpenAI")
                return None
                
        except Exception as e:
            logger.console(f"❌ Error healing locator: {str(e)}")
            logger.console(f"📑 Stack trace:\n{traceback.format_exc()}")
            return None 