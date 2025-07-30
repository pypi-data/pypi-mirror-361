# Robot Framework Self-Healing Library

🤖 **Automated test maintenance for Robot Framework + Selenium**

A powerful self-healing library that automatically detects and fixes broken locators in Robot Framework tests, reducing maintenance overhead and improving test reliability.

## ✨ Features

- 🔧 **Automatic Locator Healing**: Detects failed locators and suggests fixes using AI
- 🎯 **Smart Candidate Generation**: Analyzes DOM to find alternative locators
- 🧠 **AI-Powered Solutions**: Uses OpenAI GPT-4 for intelligent locator suggestions
- 📊 **Detailed Reporting**: Comprehensive healing reports in test results
- 🔄 **Seamless Integration**: Works transparently with existing Robot Framework tests
- 📝 **Code Updates**: Automatically updates PageObject files with healed locators

## 🚀 Installation

### From PyPI (Recommended)

```bash
pip install robot-selfheal
```

### From Source

```bash
git clone https://github.com/samarthindex9/selfhealing_library.git
cd selfhealing_library
pip install -e .
```

## ⚙️ Setup

### 1. Environment Configuration

Create an `.env` file in your `Environment` directory:

```bash
# Environment/.env
OPENAI_API_KEY=your_openai_api_key_here
```

### 2. Configuration File

Create `Environment/config.json`:

```json
{
    "data_path": "locator_data",
    "page_objects_dir": "PageObjects", 
    "page_sources_dir": "locator_data/page_sources",
    "results_dir": "results",
    "locator_data": {
        "healing_prompts": "healing_prompts.json",
        "healed_locators": "healed_locators.json", 
        "locator_failures": "locator_failures.json"
    }
}
```

## 📖 Usage

### Method 1: Import as Library (Recommended)

Add to your Robot Framework test file:

```robot
*** Settings ***
Library    robot_selfheal.SelfHealListener

*** Test Cases ***
Your Test Case
    [Documentation]    Your test with automatic self-healing
    Open Browser    https://example.com    chrome
    Click Element    ${BROKEN_LOCATOR}    # Will auto-heal if it fails
    Close Browser
```

### Method 2: Listener Mode

Run your tests with the listener:

```bash
robot --listener robot_selfheal.SelfHealListener your_test.robot
```

### Method 3: Command Line Integration

```bash
# Run tests with self-healing enabled
robot-selfheal --suite your_test_suite --browser chrome
```

## 🏗️ Project Structure

Your Robot Framework project should follow this structure:

```
your_project/
├── Environment/
│   ├── config.json        # Configuration file
│   └── .env              # OpenAI API key
├── PageObjects/          # Page object files with locators
│   ├── login_page.py
│   └── dashboard_page.py
├── TestCases/           # Your test cases
│   └── login_tests.robot
└── results/             # Test results and reports
```

## 🔧 Configuration Options

The `config.json` file supports these options:

| Option | Description | Default |
|--------|-------------|---------|
| `data_path` | Directory for healing data | `"locator_data"` |
| `page_objects_dir` | PageObjects directory | `"PageObjects"` |
| `page_sources_dir` | HTML captures directory | `"locator_data/page_sources"` |
| `results_dir` | Test results directory | `"results"` |

## 📊 How It Works

1. **Detection**: Monitors test execution for locator failures
2. **Analysis**: Captures page source and analyzes DOM structure
3. **Generation**: Creates candidate alternative locators using smart algorithms
4. **AI Enhancement**: Uses OpenAI GPT-4 to select best healing solution
5. **Application**: Updates PageObject files with healed locators
6. **Reporting**: Adds healing summary to test reports

## 🎯 Supported Locator Types

- ✅ XPath expressions (`//div[@id='example']`)
- ✅ CSS selectors (`css=.my-class`)
- ✅ ID locators (`id=my-element`)
- ✅ Name locators (`name=my-input`)
- ✅ Class locators (`class=my-class`)
- ✅ Text-based locators (`//*[contains(text(), 'Click Me')]`)

## 📈 Example Output

When a locator fails, the library generates a detailed healing report:

```
🔧 Self-Healing Summary
┌─────────────────────────────────────────────────────────┐
│ Variable: ${LOGIN_BUTTON}                               │
│ Source: login_page.py                                   │
│ Original: //button[@id='old-login-btn']                 │
│ Healed: //button[@data-testid='login-submit']           │
│ Solution: Updated to use more stable data-testid        │
└─────────────────────────────────────────────────────────┘
```

## 🔧 Advanced Configuration

### Custom Candidate Generation

```python
from robot_selfheal import generate_enhanced_candidates

# Generate candidates with custom settings
candidates = generate_enhanced_candidates(
    locator="//button[@id='broken']",
    mode="lenient",  # strict, balanced, lenient
    threshold=60     # similarity threshold
)
```

### Programmatic Healing

```python
from robot_selfheal import SelfHealingAgent

agent = SelfHealingAgent()
healed_data = agent.heal_locator("//broken[@locator='value']")
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙋‍♂️ Support

- 📧 **Contact**: 
  - Project Manager: samarth.math@indexnine.com
  - Development Team: vikas.gupta@indexnine.com, onkar.pawar@indexnine.com
- 🐛 Issues: [GitHub Issues](https://github.com/samarthindex9/selfhealing_library/issues)
- 📖 Documentation: [Wiki](https://github.com/samarthindex9/selfhealing_library/blob/pypi-packaging/README.md)

## 🏆 Acknowledgments

- **Project Team**: 
  - **Samarth Math** - Project Manager
  - **Vikas Gupta** -  Developer  
  - **Onkar Pawar** -  Developer
- Robot Framework community for the excellent testing framework
- Selenium WebDriver for web automation capabilities
- OpenAI for providing the GPT-4 API
- BeautifulSoup and lxml for HTML parsing capabilities

---

**Made with ❤️ for the Robot Framework community** 