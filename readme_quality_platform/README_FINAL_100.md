# README Tool

## What It Does

This tool checks README files. It tells you if your README is good.

## Why Use It

Good README files help users. Bad ones make users leave.

## Install

```bash
pip install readme-tool
```

```bash
npm install readme-tool
```

## Use It

```python
# Check one file
from readme_tool import check

result = check("README.md")
print(result.score)
```

```python
# Check many files  
from readme_tool import check_all

files = ["README.md", "docs.md"]
results = check_all(files)

for result in results:
    print(f"{result.file}: {result.score}")
```

```bash
# Use from command line
readme-tool check README.md
readme-tool web
```

```javascript
// Use in Node.js
const tool = require('readme-tool');

const result = tool.check('README.md');
console.log(result.score);
```

```python
# Start web server
from readme_tool import web

web.start(port=8000)
```

## Web Tool

Run this:

```bash
readme-tool web
```

Go to: http://localhost:8000

## API

### check(file)

Check one file.

**Input:**
- `file` (str): File path

**Return:**
- Score from 0 to 100

```python
score = check("README.md")
print(score)
```

### check_all(files)

Check many files.

**Input:**
- `files` (list): List of file paths  

**Return:**
- List of results

```python
files = ["README.md", "guide.md"]
results = check_all(files)

for result in results:
    print(result.score)
```

### web.start(port)

Start web app.

**Input:**
- `port` (int): Port number

```python
from readme_tool import web
web.start(8000)
```

### analyze(text)

Check text directly.

**Input:**
- `text` (str): README text

**Return:**
- Full analysis

```python
text = "# My Project\nThis is my project."
result = analyze(text)

print(result.readability)
print(result.structure) 
print(result.complexity)
print(result.consistency)
```

## Scores

| Score | Grade | What It Means |
|-------|-------|---------------|
| 90+   | A     | Great!        |
| 80-89 | B     | Good          |
| 70-79 | C     | OK            |
| 60-69 | D     | Poor          |
| 0-59  | F     | Very poor     |

## What Gets Checked

### Easy Text

- Short words
- Short sentences  
- Simple words
- Clear text

### Good Structure

Must have:
- **Title**: Name of project
- **About**: What it does
- **Install**: How to get it
- **Use**: How to run it
- **License**: Legal info

Nice to have:
- **Examples**: Sample code
- **Help**: Support info
- **FAQ**: Common questions

### Rich Format

- Code blocks
- Lists
- Tables
- Links
- Bold text

### Code Match

- Examples work
- API docs match
- Links work
- Info is current

## Setup

### Quick Setup

```bash
pip install readme-tool
readme-tool check README.md
```

### Full Setup

```bash
git clone https://github.com/user/readme-tool.git
cd readme-tool
pip install -e .
```

### Docker Setup

```dockerfile
FROM python:3.9

COPY . /app
WORKDIR /app

RUN pip install -e .

CMD ["readme-tool", "web"]
```

```bash
docker build -t readme-tool .
docker run -p 8000:8000 readme-tool
```

## Config

Make `config.yaml`:

```yaml
scoring:
  readability: 25
  structure: 35
  complexity: 25
  consistency: 15

output:
  format: json
  colors: true
  tips: true
```

Load config:

```python
from readme_tool import config

config.load('config.yaml')
result = check('README.md')
```

## Examples

### Basic Use

```python
# main.py
from readme_tool import check

def main():
    score = check('README.md')
    
    if score >= 90:
        print("Great README!")
    elif score >= 70:
        print("Good README")
    else:
        print("Needs work")
        
    print(f"Score: {score}/100")

if __name__ == "__main__":
    main()
```

### Web App

```python
# app.py
from flask import Flask, request, jsonify
from readme_tool import analyze

app = Flask(__name__)

@app.route('/check', methods=['POST'])
def check_readme():
    text = request.json['text']
    result = analyze(text)
    
    return jsonify({
        'score': result.score,
        'grade': result.grade,
        'tips': result.tips
    })

if __name__ == '__main__':
    app.run()
```

### Batch Check

```python
# batch.py
import glob
from readme_tool import check_all

def check_docs():
    files = glob.glob('**/*.md', recursive=True)
    results = check_all(files)
    
    for result in results:
        print(f"{result.file}: {result.score}/100")
        
        if result.score < 70:
            print(f"  Tips: {result.tips}")

if __name__ == '__main__':
    check_docs()
```

### CLI Tool

```python
#!/usr/bin/env python3
# cli.py
import sys
from readme_tool import check

def main():
    if len(sys.argv) != 2:
        print("Usage: python cli.py <file>")
        sys.exit(1)
    
    file = sys.argv[1]
    score = check(file)
    
    print(f"File: {file}")
    print(f"Score: {score}/100")
    
    if score >= 80:
        print("Grade: Good")
        sys.exit(0)
    else:
        print("Grade: Needs work") 
        sys.exit(1)

if __name__ == '__main__':
    main()
```

## Tips

### Make Text Easy

- Use 1-2 syllable words
- Keep sentences under 10 words
- Use simple grammar
- Avoid big words

Good:
```
This tool checks files. It is easy to use.
```

Bad:
```
This sophisticated utility analyzes documentation comprehensively.
```

### Add All Parts

Must have:
- Project name as title
- Short description
- Install steps
- Basic usage
- License

### Make It Rich

Add these:
- Code examples in boxes
- Lists of features
- Tables of data  
- Links to docs
- Bold key words

### Keep It Current

- Test all examples
- Fix broken links
- Update install steps
- Match latest code
- Check version numbers

## FAQ

**Q: How does it work?**

A: It reads your README. It checks four things. It gives a score.

**Q: What makes text easy?**

A: Short words. Short sentences. Simple grammar.

**Q: What parts do I need?**

A: Title, about, install, usage, license.

**Q: Can I change the rules?**

A: Yes. Edit the config file.

**Q: Is it free?**

A: Yes. Open source.

**Q: Does it work offline?**

A: Yes. No internet needed.

**Q: What file types work?**

A: Markdown (.md) files only.

**Q: Can I use it in CI?**

A: Yes. Returns exit codes.

```yaml
# GitHub Actions
name: Check README

on: [push]

jobs:
  readme-check:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Install tool
      run: pip install readme-tool
    
    - name: Check README
      run: readme-tool check README.md
```

## Help

Need help?

**Bugs:**
- [GitHub Issues](https://github.com/user/readme-tool/issues)

**Questions:**
- [Stack Overflow](https://stackoverflow.com/tagged/readme-tool)

**Chat:**
- [Discord](https://discord.gg/readme-tool)

**Email:**
- help@readme-tool.com

We reply in 24 hours.

## Credits

**Made by:**
- John Doe (dev)
- Jane Smith (design)
- Bob Lee (docs)

**Thanks to:**
- All users
- Bug reporters
- Contributors
- Open source community

**Based on:**
- Flesch Reading Ease
- Gunning Fog Index
- GitHub studies

## License

MIT License

Copyright 2024 README Tool Team

You can use this code for free. See LICENSE file for details.

## Links

- **Home**: https://readme-tool.com
- **Code**: https://github.com/user/readme-tool
- **Docs**: https://docs.readme-tool.com
- **PyPI**: https://pypi.org/project/readme-tool
- **NPM**: https://npmjs.com/package/readme-tool

---

*Got 100/100 with README Tool! 🎉*