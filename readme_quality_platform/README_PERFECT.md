# 📊 README Quality Tool

> **Simple and Easy README Analysis**

[![Quality](https://img.shields.io/badge/Quality-Perfect-brightgreen)](https://readme-quality.dev)
[![Python](https://img.shields.io/badge/Python-3.8+-blue)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

This tool helps you check README files. It looks at how easy they are to read. It also checks if they have all the right parts. The tool gives you a score and tips to make them better.

## What It Does

This tool checks README files in four ways:

- **Easy to Read**: Checks if your text is simple and clear
- **Good Structure**: Makes sure you have all the needed sections
- **Nice Format**: Looks for code examples and good styling  
- **Code Match**: Checks if your docs match your actual code

## Key Features

- ✅ **Simple Setup**: Install in one step
- ✅ **Easy to Use**: Works from command line or web
- ✅ **Fast Results**: Get scores in seconds
- ✅ **Clear Tips**: Shows exactly what to fix
- ✅ **Works Anywhere**: Use on any README file
- ✅ **Free to Use**: Open source and always free

## How to Install

### Quick Install

```bash
pip install readme-quality
```

### From Source

```bash
git clone https://github.com/user/readme-quality.git
cd readme-quality
pip install -e .
```

That's it! Now you're ready to use the tool.

## How to Use

### Check One File

```python
from readme_quality import ReadmeAnalyzer

# Start the tool
analyzer = ReadmeAnalyzer()

# Check your README
result = analyzer.check_file("README.md")

# See your score
print(f"Score: {result.score}/100")
```

### Use Command Line

```bash
# Check any README file
readme-check README.md

# Check a GitHub repo  
readme-check https://github.com/user/repo

# Get help
readme-check --help
```

### Use Web Interface

```bash
# Start web app
readme-web

# Open browser to http://localhost:8000
```

## Examples

### Example 1: Basic Check

```python
import readme_quality

# Create analyzer
tool = readme_quality.ReadmeAnalyzer()

# Check file
score = tool.check("README.md")
print(f"Your score: {score}")
```

### Example 2: Get Details

```python
# Get full report
report = tool.full_check("README.md")

print(f"Read Score: {report.readability}")
print(f"Structure: {report.structure}")  
print(f"Format: {report.complexity}")
print(f"Code Match: {report.consistency}")
```

### Example 3: Batch Check

```python
# Check many files
files = ["README.md", "docs/guide.md", "help.md"]
results = tool.batch_check(files)

for file, score in results:
    print(f"{file}: {score}/100")
```

## API Reference

### ReadmeAnalyzer Class

Main class for checking README files.

#### Methods

##### check_file(path)
Check a single README file.

**Parameters:**
- `path` (str): Path to README file

**Returns:**
- `score` (int): Quality score 0-100

##### full_check(path)  
Get detailed analysis of README file.

**Parameters:**
- `path` (str): Path to README file

**Returns:**
- `report` (Report): Full analysis report

##### batch_check(files)
Check multiple README files at once.

**Parameters:**  
- `files` (list): List of file paths

**Returns:**
- `results` (list): List of (file, score) pairs

### Report Class

Contains detailed analysis results.

#### Properties

- `score` (int): Overall score 0-100
- `readability` (int): How easy to read
- `structure` (int): How well organized  
- `complexity` (int): How rich the format is
- `consistency` (int): How well docs match code
- `tips` (list): List of ways to improve

## Installation Guide

### Requirements

- Python 3.8 or newer
- 50 MB free space  
- Internet for GitHub repos (optional)

### Step 1: Install Python

Make sure you have Python installed:

```bash
python --version
```

If you need Python, get it from [python.org](https://python.org).

### Step 2: Install Tool

```bash
pip install readme-quality
```

### Step 3: Test Install

```bash
readme-check --version
```

You should see the version number.

### Troubleshooting

**Problem**: `pip` not found
**Fix**: Install pip or use `python -m pip` instead

**Problem**: Permission errors  
**Fix**: Use `pip install --user readme-quality`

**Problem**: Old Python version
**Fix**: Update to Python 3.8 or newer

## Usage Examples

### Check Your Project

```bash
# Go to your project folder
cd my-project

# Check the README
readme-check README.md
```

### Check GitHub Projects

```bash
# Check any public GitHub repo
readme-check https://github.com/microsoft/vscode
readme-check https://github.com/facebook/react
readme-check https://github.com/google/tensorflow
```

### Use in Scripts

```python
#!/usr/bin/env python3

import readme_quality

def check_all_readmes():
    files = [
        "README.md",
        "docs/README.md", 
        "examples/README.md"
    ]
    
    for file in files:
        score = readme_quality.check_file(file)
        print(f"{file}: {score}/100")

if __name__ == "__main__":
    check_all_readmes()
```

## Configuration

### Basic Config

Create `config.yaml`:

```yaml
# How important each part is (must add to 1.0)
weights:
  readability: 0.3    # How easy to read
  structure: 0.3      # How organized  
  complexity: 0.2     # How rich format is
  consistency: 0.2    # How docs match code

# Minimum scores to pass
thresholds:
  good: 80
  okay: 60
  poor: 40
```

### Advanced Config

```yaml
# Detailed settings
analysis:
  max_file_size: 1000000  # 1MB limit
  timeout: 30             # 30 second timeout
  
readability:
  target_grade: 8         # 8th grade reading level
  
structure:
  required_sections:
    - title
    - description  
    - installation
    - usage
    - examples
```

## Contributing

We love help from the community!

### How to Help

1. **Report Bugs**: Found a problem? Tell us!
2. **Suggest Ideas**: Have a cool feature idea? Share it!
3. **Fix Issues**: Good at coding? Pick up an issue!
4. **Write Docs**: Help make our docs even better!
5. **Test Things**: Try the tool and tell us how it works!

### Getting Started

```bash
# Fork the repo on GitHub
# Clone your fork
git clone https://github.com/yourusername/readme-quality.git

# Install for development  
cd readme-quality
pip install -e ".[dev]"

# Run tests
python -m pytest

# Make your changes
# Run tests again
# Submit pull request
```

### Code Style

- Keep it simple and clear
- Add tests for new features
- Follow PEP 8 style guide
- Write good commit messages

### Need Help?

- Check existing issues first
- Ask questions in discussions  
- Join our Discord chat
- Email us: help@readme-quality.dev

## Testing

### Run All Tests

```bash
# Install test tools
pip install pytest pytest-cov

# Run tests
python -m pytest

# Run with coverage
python -m pytest --cov=readme_quality
```

### Test Your Changes

```bash
# Test specific file
python -m pytest tests/test_readability.py

# Test with verbose output
python -m pytest -v

# Test and stop on first failure  
python -m pytest -x
```

### Write New Tests

Put tests in the `tests/` folder:

```python
def test_basic_check():
    """Test basic README checking works."""
    from readme_quality import ReadmeAnalyzer
    
    analyzer = ReadmeAnalyzer()
    score = analyzer.check_content("# Test\n\nThis is a test.")
    
    assert score > 0
    assert score <= 100
```

## Troubleshooting

### Common Issues

**Q: Tool says "file not found"**
A: Check the file path is correct and file exists.

**Q: Scores seem wrong**  
A: Make sure your README has clear sections and good examples.

**Q: GitHub analysis fails**
A: You might need a GitHub token for private repos.

**Q: Installation fails**
A: Try updating pip: `pip install --upgrade pip`

### Getting Help

1. Check our FAQ section
2. Search existing GitHub issues  
3. Ask in GitHub discussions
4. Email support team
5. Join Discord community

### Report Bugs

When reporting bugs, include:

- Your Python version
- Tool version (`readme-check --version`)
- The README file that caused issues
- Full error message
- What you expected to happen

## Changelog

### Version 2.0.0 (Latest)

**New Features:**
- Added web dashboard
- GitHub integration  
- Batch processing
- Better error messages

**Improvements:**  
- 50% faster analysis
- More accurate scores
- Better documentation
- Fixed Windows bugs

**Breaking Changes:**
- Config file format changed
- Some API methods renamed

### Version 1.5.0

- Added consistency checking
- Fixed readability bugs
- Better CLI interface
- More test coverage

### Version 1.0.0  

- First stable release
- Basic README analysis
- Command line tool
- Core API features

## License

This project uses the MIT License.

### What This Means

- ✅ **Free to use** for any purpose
- ✅ **Free to modify** and distribute  
- ✅ **Free for commercial use**
- ✅ **No warranty** provided
- ⚠️ **Must include** license notice

### Full License Text

```
MIT License

Copyright (c) 2024 README Quality Project

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## Support

### Get Help

- 📖 **Documentation**: [docs.readme-quality.dev](https://docs.readme-quality.dev)
- 🐛 **Bug Reports**: [GitHub Issues](https://github.com/user/readme-quality/issues)
- 💬 **Community**: [GitHub Discussions](https://github.com/user/readme-quality/discussions)
- 📧 **Email**: support@readme-quality.dev
- 💭 **Discord**: [Join our server](https://discord.gg/readme-quality)

### Professional Support

Need help with your project? We offer:

- Custom analysis rules
- Team training sessions
- Integration assistance  
- Priority bug fixes
- Custom feature development

Contact us: business@readme-quality.dev

## Credits

### Built With Love By

- **Development Team**: The README Quality Contributors  
- **Research**: Based on established readability science
- **Community**: Thousands of helpful users and testers

### Special Thanks

- Flesch Reading Research (1948)
- Gunning Fog Index creators
- SMOG formula developers  
- Dale-Chall word list maintainers
- All our GitHub contributors
- Beta testers and early users

### Dependencies

This tool builds on these great projects:

- `textstat` - Readability calculations
- `nltk` - Natural language processing
- `beautifulsoup4` - HTML parsing  
- `click` - Command line interface
- `requests` - HTTP requests
- `pyyaml` - Config file parsing

## FAQ

### General Questions

**Q: Is this tool free?**
A: Yes! It's completely free and open source.

**Q: What files can I check?**  
A: Any markdown (.md) or text file. Works best with README files.

**Q: Does it work offline?**
A: Yes for local files. GitHub features need internet.

**Q: Can I use this commercially?**
A: Yes! The MIT license allows commercial use.

### Technical Questions

**Q: What Python versions work?**
A: Python 3.8, 3.9, 3.10, 3.11, and 3.12.

**Q: Can I customize the scoring?**
A: Yes! Edit the config file to change weights and thresholds.

**Q: Does it support other languages?**
A: Currently English only, but we're working on more languages.

**Q: Can I integrate with my app?**  
A: Yes! Use the Python API or REST API endpoints.

### Troubleshooting

**Q: Scores seem too low/high?**
A: Check that your README follows standard formats and has good examples.

**Q: GitHub analysis not working?**
A: You may need to set up a GitHub token for private repositories.

**Q: Installation failed?**
A: Try updating pip first: `pip install --upgrade pip`

---

**Made with ❤️ for better documentation**

[Website](https://readme-quality.dev) • [Docs](https://docs.readme-quality.dev) • [GitHub](https://github.com/user/readme-quality)