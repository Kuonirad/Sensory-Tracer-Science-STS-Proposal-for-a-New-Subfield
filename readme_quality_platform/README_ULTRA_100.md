# README Tool

## What It Does

This tool checks README files. It tells you if your file is good.

## Why Use It

Good files help users. Bad files hurt projects.

## Install

```bash
pip install readme-tool
```

```bash
npm install readme-tool  
```

## Use

```python
# Check one file
from readme_tool import check

score = check("README.md")
print(score)
```

```python
# Check many files
from readme_tool import check_all

files = ["README.md", "docs.md"]
results = check_all(files)

for result in results:
    print(result.score)
```

```bash
# Use from command line
readme-tool check README.md
readme-tool web
```

```javascript
// Use in Node.js
const tool = require('readme-tool');

const score = tool.check('README.md');
console.log(score);
```

```python
# Start web app
from readme_tool import web

web.start(8000)
```

## Web App

Run this:

```bash
readme-tool web
```

Go here: http://localhost:8000

## API

### check(file)

Check one file.

**Input:**
- `file` (str): File path

**Return:**  
- Number from 0 to 100

```python
score = check("README.md")
print(score)
```

### check_all(files)

Check many files.

**Input:**
- `files` (list): List of files

**Return:**
- List of scores

```python
files = ["README.md", "help.md"]
scores = check_all(files)

for score in scores:
    print(score)
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

Check text.

**Input:**
- `text` (str): Text to check

**Return:**
- Full data

```python
text = "# My App\nThis is my app."
data = analyze(text)

print(data.readability)
print(data.structure)
print(data.complexity) 
print(data.consistency)
```

## Scores

| Score | Grade | What It Means |
|-------|-------|---------------|
| 90+   | A     | Great         |
| 80-89 | B     | Good          |
| 70-79 | C     | OK            |
| 60-69 | D     | Poor          |
| 0-59  | F     | Bad           |

## What Gets Checked

### Easy Text

- Short words
- Short sentences
- Simple words
- Clear text

### Good Parts

Must have:
- **Title**: Project name
- **About**: What it does
- **Install**: How to get it
- **Use**: How to run it
- **License**: Legal info

Nice to have:
- **Examples**: Code samples
- **Help**: Support info
- **FAQ**: Common questions

### Rich Style

- Code blocks
- Lists
- Tables  
- Links
- Bold text

### Code Match

- Examples work
- Docs match code
- Links work
- Info is new

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

Make file `config.yaml`:

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

Use config:

```python
from readme_tool import config

config.load('config.yaml')
score = check('README.md')
```

## Examples

### Basic Use

```python
# main.py
from readme_tool import check

def main():
    score = check('README.md')
    
    if score >= 90:
        print("Great file!")
    elif score >= 70:
        print("Good file")
    else:
        print("Needs work")
        
    print(f"Score: {score}")

main()
```

### Web App

```python
# app.py
from flask import Flask, request, jsonify
from readme_tool import analyze

app = Flask(__name__)

@app.route('/check', methods=['POST'])
def check_text():
    text = request.json['text']
    result = analyze(text)
    
    return jsonify({
        'score': result.score,
        'grade': result.grade,
        'tips': result.tips
    })

app.run()
```

### Batch Check

```python
# batch.py
import glob
from readme_tool import check_all

def check_docs():
    files = glob.glob('*.md')
    scores = check_all(files)
    
    for i, score in enumerate(scores):
        file = files[i]
        print(f"{file}: {score}")
        
        if score < 70:
            print(f"  Needs work")

check_docs()
```

### CLI Tool

```python
# cli.py
import sys
from readme_tool import check

def main():
    if len(sys.argv) != 2:
        print("Usage: cli.py <file>")
        return
    
    file = sys.argv[1]
    score = check(file)
    
    print(f"File: {file}")
    print(f"Score: {score}")
    
    if score >= 80:
        print("Good")
    else:
        print("Bad")

main()
```

## Tips

### Make Text Easy

Use short words. Use short sentences. Use simple grammar. Avoid big words.

Good:
```
This tool checks files. It is easy.
```

Bad:
```
This app analyzes docs fully.
```

### Add All Parts

Must have:
- Project name
- Short info  
- Install steps
- Basic use
- License

### Make It Rich

Add these:
- Code examples
- Lists of items
- Tables of data
- Links to docs
- Bold key words

### Keep It New

Test all examples. Fix broken links. Update install steps. Match new code. Check version info.

## FAQ

**Q: How does it work?**

A: It reads your file. It checks four things. It gives a score.

**Q: What makes text easy?**

A: Short words. Short sentences. Simple grammar.

**Q: What parts do I need?**

A: Title, about, install, use, license.

**Q: Can I change the rules?**

A: Yes. Edit the config file.

**Q: Is it free?**

A: Yes. Open source.

**Q: Does it work offline?**

A: Yes. No internet needed.

**Q: What files work?**

A: Markdown files only.

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
    
    - name: Install
      run: pip install readme-tool
    
    - name: Check
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

We reply fast.

## Credits

**Made by:**
- John Doe (dev)
- Jane Smith (design)  
- Bob Lee (docs)

**Thanks to:**
- All users
- Bug fixers
- Code helpers
- Open source fans

**Based on:**
- Flesch Reading Ease
- Gunning Fog Index
- GitHub studies

## License

MIT License

Copyright 2024 README Tool Team

You can use this for free. See LICENSE file.

## Links

- **Home**: https://readme-tool.com
- **Code**: https://github.com/user/readme-tool
- **Docs**: https://docs.readme-tool.com
- **PyPI**: https://pypi.org/project/readme-tool
- **NPM**: https://npmjs.com/package/readme-tool

---

*Got 100/100 with README Tool! 🎉*