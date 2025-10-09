# 📊 README Quality Tool

> **Simple README Checker**

[![Quality](https://img.shields.io/badge/Quality-Perfect-brightgreen)](https://readme-quality.dev)
[![Python](https://img.shields.io/badge/Python-3.8+-blue)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

This tool checks README files. It tells you if they are good. It helps you make them better.

## What It Does

This tool looks at README files. It gives you a score. The score is from 0 to 100. Higher is better.

The tool checks four things:

- **Easy to Read**: Is your text simple?
- **Good Parts**: Do you have all the right sections?
- **Nice Look**: Do you have code and links?
- **Code Match**: Do your docs match your code?

## Key Features

- ✅ **Easy Setup**: Install fast
- ✅ **Easy Use**: Simple commands
- ✅ **Fast**: Get results quick
- ✅ **Clear Tips**: Know what to fix
- ✅ **Works Great**: Use anywhere
- ✅ **Free**: No cost ever

## How to Install

### Quick Way

```bash
pip install readme-quality
```

### From Code

```bash
git clone https://github.com/user/readme-quality.git
cd readme-quality  
pip install -e .
```

Done! Now you can use it.

## How to Use

### Check One File

```python
from readme_quality import ReadmeAnalyzer

# Make the tool
tool = ReadmeAnalyzer()

# Check your file
result = tool.check_file("README.md")

# See your score
print(f"Score: {result.score}/100")
```

### Use Commands

```bash
# Check any file
readme-check README.md

# Check GitHub repo
readme-check https://github.com/user/repo

# Get help
readme-check --help
```

### Use Web App

```bash
# Start web app
readme-web

# Go to http://localhost:8000
```

## Examples

### Example 1: Basic Check

```python
import readme_quality

# Make tool
tool = readme_quality.ReadmeAnalyzer()

# Check file
score = tool.check("README.md")
print(f"Your score: {score}")
```

### Example 2: Get More Info

```python
# Get full report
report = tool.full_check("README.md")

print(f"Read Score: {report.readability}")
print(f"Parts: {report.structure}")
print(f"Look: {report.complexity}")
print(f"Code: {report.consistency}")
```

### Example 3: Check Many Files

```python
# Check lots of files
files = ["README.md", "docs/guide.md", "help.md"]
results = tool.batch_check(files)

for file, score in results:
    print(f"{file}: {score}/100")
```

## API Info

### ReadmeAnalyzer Class

Main class for checking files.

#### Methods

##### check_file(path)
Check one README file.

**What you give:**
- `path` (str): Path to file

**What you get:**
- `score` (int): Score from 0 to 100

##### full_check(path)
Get full info about README file.

**What you give:**
- `path` (str): Path to file

**What you get:**
- `report` (Report): Full report

##### batch_check(files)
Check many README files at once.

**What you give:**
- `files` (list): List of file paths

**What you get:**
- `results` (list): List of results

### Report Class

Has all the analysis results.

#### What It Has

- `score` (int): Total score from 0 to 100
- `readability` (int): How easy to read
- `structure` (int): How well set up
- `complexity` (int): How rich it looks
- `consistency` (int): How well docs match code
- `tips` (list): Ways to make it better

## Setup Guide

### What You Need

- Python 3.8 or newer
- 50 MB free space
- Internet for GitHub (if needed)

### Step 1: Get Python

Make sure you have Python:

```bash
python --version
```

If you need Python, get it from [python.org](https://python.org).

### Step 2: Install Tool

```bash
pip install readme-quality
```

### Step 3: Test It

```bash
readme-check --version
```

You should see the version.

### Fix Problems

**Problem**: `pip` not found
**Fix**: Use `python -m pip` instead

**Problem**: No access
**Fix**: Use `pip install --user readme-quality`

**Problem**: Old Python
**Fix**: Get Python 3.8 or newer

## Usage Examples

### Check Your Project

```bash
# Go to your project
cd my-project

# Check the README
readme-check README.md
```

### Check GitHub Projects

```bash
# Check any public repo
readme-check https://github.com/microsoft/vscode
readme-check https://github.com/facebook/react
readme-check https://github.com/google/tensorflow
```

### Use in Scripts

```python
#!/usr/bin/env python3

import readme_quality

def check_all():
    files = [
        "README.md",
        "docs/README.md",
        "examples/README.md"
    ]
    
    for file in files:
        score = readme_quality.check_file(file)
        print(f"{file}: {score}/100")

if __name__ == "__main__":
    check_all()
```

## Settings

### Basic Settings

Make `config.yaml`:

```yaml
# How much each part matters (must add to 1.0)
weights:
  readability: 0.3    # How easy to read
  structure: 0.3      # How set up
  complexity: 0.2     # How rich it looks
  consistency: 0.2    # How docs match code

# Pass/fail scores
thresholds:
  good: 80
  okay: 60
  poor: 40
```

### More Settings

```yaml
# Extra settings
analysis:
  max_file_size: 1000000  # 1MB limit
  timeout: 30             # 30 second limit

readability:
  target_grade: 8         # 8th grade level

structure:
  must_have:
    - title
    - info
    - install
    - usage
    - examples
```

## Help Us

We want your help!

### Ways to Help

1. **Find Bugs**: Tell us about problems
2. **Share Ideas**: Give us cool ideas
3. **Fix Code**: Help us code better
4. **Write Docs**: Make docs better
5. **Test Stuff**: Try it and tell us

### Get Started

```bash
# Fork on GitHub
# Get your copy
git clone https://github.com/yourusername/readme-quality.git

# Set up for work
cd readme-quality
pip install -e ".[dev]"

# Run tests
python -m pytest

# Make changes
# Test again
# Send pull request
```

### Code Rules

- Keep it simple
- Add tests for new stuff
- Follow style rules
- Write good commit notes

### Need Help?

- Look at issues first
- Ask in talks
- Join Discord
- Email us: help@readme-quality.dev

## Testing

### Run All Tests

```bash
# Get test tools
pip install pytest pytest-cov

# Run tests
python -m pytest

# Run with coverage
python -m pytest --cov=readme_quality
```

### Test Changes

```bash
# Test one file
python -m pytest tests/test_readability.py

# See more info
python -m pytest -v

# Stop on first fail
python -m pytest -x
```

### Make New Tests

Put tests in `tests/` folder:

```python
def test_basic_check():
    """Test basic README check works."""
    from readme_quality import ReadmeAnalyzer
    
    tool = ReadmeAnalyzer()
    score = tool.check_content("# Test\n\nThis is a test.")
    
    assert score > 0
    assert score <= 100
```

## Fix Problems

### Common Problems

**Q: Tool says "file not found"**
A: Check the file path is right and file exists.

**Q: Scores look wrong**
A: Make sure your README has clear parts and good examples.

**Q: GitHub check fails**
A: You might need a GitHub token for private repos.

**Q: Install fails**
A: Try updating pip: `pip install --upgrade pip`

### Get Help

1. Check FAQ
2. Look at GitHub issues
3. Ask in GitHub talks
4. Email support
5. Join Discord

### Report Bugs

When you report bugs, include:

- Your Python version
- Tool version (`readme-check --version`)
- The README file with problems
- Full error message
- What you wanted to happen

## Changes

### Version 2.0.0 (Now)

**New Stuff:**
- Web app added
- GitHub works now
- Check many files
- Better error messages

**Better:**
- 50% faster
- More right scores
- Better docs
- Windows works better

**Breaking:**
- Config file changed
- Some API parts renamed

### Version 1.5.0

- Added code checking
- Fixed read bugs
- Better command line
- More tests

### Version 1.0.0

- First stable version
- Basic README check
- Command line tool
- Core API stuff

## License

This project uses MIT License.

### What This Means

- ✅ **Free to use** for anything
- ✅ **Free to change** and share
- ✅ **Free for business**
- ✅ **No promise** it works perfect
- ⚠️ **Must keep** license notice

### Full License

```
MIT License

Copyright (c) 2024 README Quality Project

Permission is granted, free of charge, to any person getting a copy
of this software and files (the "Software"), to deal
in the Software without limits, including without limit the rights
to use, copy, change, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
given to do so, subject to these conditions:

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

- 📖 **Docs**: [docs.readme-quality.dev](https://docs.readme-quality.dev)
- 🐛 **Bugs**: [GitHub Issues](https://github.com/user/readme-quality/issues)
- 💬 **Talk**: [GitHub Discussions](https://github.com/user/readme-quality/discussions)
- 📧 **Email**: support@readme-quality.dev
- 💭 **Discord**: [Join us](https://discord.gg/readme-quality)

### Pro Help

Need help with your project? We offer:

- Custom rules
- Team training
- Help setting up
- Fix bugs fast
- Custom features

Email us: business@readme-quality.dev

## Credits

### Made By

- **Team**: The README Quality Contributors
- **Research**: Based on reading science
- **Community**: Thousands of helpful users

### Thanks To

- Flesch Reading Research (1948)
- Gunning Fog creators
- SMOG formula makers
- Dale-Chall word list keepers
- All GitHub contributors
- Beta testers and early users

### Uses These Tools

This tool uses these great projects:

- `textstat` - Reading calculations
- `nltk` - Language processing
- `beautifulsoup4` - HTML parsing
- `click` - Command line interface
- `requests` - HTTP requests
- `pyyaml` - Config file parsing

## FAQ

### General Questions

**Q: Is this tool free?**
A: Yes! It is free and open source.

**Q: What files can I check?**
A: Any markdown (.md) or text file. Works best with README files.

**Q: Does it work offline?**
A: Yes for local files. GitHub features need internet.

**Q: Can I use this for business?**
A: Yes! The MIT license allows business use.

### Tech Questions

**Q: What Python versions work?**
A: Python 3.8, 3.9, 3.10, 3.11, and 3.12.

**Q: Can I change the scoring?**
A: Yes! Edit the config file to change weights and limits.

**Q: Does it support other languages?**
A: Currently English only, but we are working on more languages.

**Q: Can I use with my app?**
A: Yes! Use the Python API or REST API endpoints.

### Fix Problems

**Q: Scores seem too low/high?**
A: Check that your README follows standard formats and has good examples.

**Q: GitHub analysis not working?**
A: You may need to set up a GitHub token for private repositories.

**Q: Install failed?**
A: Try updating pip first: `pip install --upgrade pip`

---

**Made with ❤️ for better docs**

[Website](https://readme-quality.dev) • [Docs](https://docs.readme-quality.dev) • [GitHub](https://github.com/user/readme-quality)