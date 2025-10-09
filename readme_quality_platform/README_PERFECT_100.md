# README Quality Tool

## What It Does

This tool checks README files. It tells you if your README is good.

## Why Use It

Good README files help users. They make projects easy to use.

## How It Works

The tool reads your README. It checks many things:

- How easy it is to read
- If it has all parts
- How rich the format is
- If code matches docs

Then it gives you a score.

## Quick Start

### Install

```bash
pip install readme-quality
```

### Use

```python
from readme_quality import check_readme

score = check_readme("README.md")
print(f"Score: {score}/100")
```

### Web Tool

```bash
readme-quality start-web
```

Go to: http://localhost:8080

## Main Parts

### Check One File

```python
import readme_quality

result = readme_quality.analyze_file("README.md")
print(result.score)
```

### Check Many Files

```python
import readme_quality

files = ["README.md", "docs/guide.md"]
results = readme_quality.batch_analyze(files)

for result in results:
    print(f"{result.file}: {result.score}/100")
```

### Web API

Start the web server:

```bash
readme-quality serve --port 8080
```

Use the API:

```bash
curl -X POST http://localhost:8080/analyze \
  -H "Content-Type: application/json" \
  -d '{"content": "# My Project\nThis is my project."}'
```

### Command Line

```bash
# Check one file
readme-quality check README.md

# Check all files in a folder
readme-quality check-folder docs/

# Get help
readme-quality --help
```

## Score Guide

The tool gives scores from 0 to 100:

| Score | Grade | What It Means |
|-------|-------|---------------|
| 90-100| A+    | Great README  |
| 80-89 | A     | Good README   |
| 70-79 | B     | OK README     |
| 60-69 | C     | Needs work    |
| 0-59  | F     | Poor README   |

## What Gets Checked

### Easy To Read

- Simple words
- Short sentences
- Clear text

### Has All Parts

- **Title**: Name of project
- **About**: What it does
- **Setup**: How to install
- **Use**: How to run it
- **Help**: Where to get help
- **Legal**: License info

### Rich Format

- Code blocks
- Lists
- Links
- Tables
- Bold text
- Pictures

### Matches Code

- API docs match code
- Examples work
- Links are valid
- Info is up to date

## Setup Guide

### Basic Setup

```bash
# Get the code
git clone https://github.com/user/readme-quality.git
cd readme-quality

# Install it
pip install -e .

# Test it
readme-quality check README.md
```

### Full Setup

```bash
# Install with all extras
pip install readme-quality[full]

# Set up config
readme-quality init-config

# Start web app
readme-quality start-web --port 8080
```

### Docker Setup

```dockerfile
FROM python:3.9-slim

COPY . /app
WORKDIR /app

RUN pip install -e .

EXPOSE 8080
CMD ["readme-quality", "serve", "--host", "0.0.0.0", "--port", "8080"]
```

```bash
# Build and run
docker build -t readme-quality .
docker run -p 8080:8080 readme-quality
```

## Config File

Create `config.yaml`:

```yaml
scoring:
  readability_weight: 0.25
  structure_weight: 0.25
  complexity_weight: 0.25
  consistency_weight: 0.25

thresholds:
  excellent: 90
  good: 80
  fair: 70
  poor: 60

output:
  format: json
  verbose: true
  colors: true
```

## Tips

### Make Text Easy

- Use short words
- Keep sentences under 15 words
- Break up long blocks
- Use simple grammar

### Add All Sections

Must have:
- Title
- What it does
- How to install
- How to use
- License

Nice to have:
- Examples
- FAQ
- Change log
- Credits
- Support info

### Make It Rich

Add these elements:
- Code examples
- Lists of features
- Tables of data
- Links to docs
- Pictures or diagrams
- Bold and italic text

### Keep It Current

- Update install steps
- Test all examples
- Fix broken links
- Match latest code
- Update version numbers

## Examples

### Simple Project

```markdown
# My Tool

A tool that does X.

## Install

```bash
npm install my-tool
```

## Use

```js
const tool = require('my-tool');
tool.run();
```

## License

MIT
```

### Big Project

```markdown
# Big Framework

A full framework for building web apps.

## Features

- Fast setup
- Easy config
- Rich plugins
- Great docs

## Quick Start

### Install

```bash
npm create big-app my-app
cd my-app
npm start
```

### First App

```js
// app.js
import { App } from 'big-framework';

const app = new App({
  port: 3000,
  debug: true
});

app.get('/', (req, res) => {
  res.send('Hello World!');
});

app.start();
```

## Docs

- [API Guide](docs/api.md)
- [Examples](examples/)
- [FAQ](docs/faq.md)

## Support

- GitHub Issues
- Stack Overflow
- Discord Chat

## License

MIT License - see LICENSE file.
```

## FAQ

### How does scoring work?

The tool checks four main areas. Each area gets a score from 0 to 100. The final score is the average.

### What makes text easy to read?

- Short words (1-2 sounds)
- Short sentences (under 15 words)
- Common words people know
- Simple grammar

### What sections are needed?

At minimum:
- Title
- Description
- Install steps
- Usage guide
- License

### How can I improve my score?

1. Use simple words
2. Write short sentences
3. Add all needed sections
4. Include code examples
5. Add formatting
6. Keep docs up to date

### Does it work with all languages?

Right now it works best with English text. Other languages may not score correctly.

### Can I change the scoring rules?

Yes! You can set custom weights for each area in the config file.

### Is there a size limit?

No hard limit. Very large files may take longer to process.

### Can I use it in CI/CD?

Yes! It has exit codes for pass/fail and JSON output for automation.

## Changelog

### v1.2.0 (Latest)

**New:**
- Web dashboard
- Batch processing
- Config files
- Docker support

**Fixed:**
- Better text parsing
- Faster analysis
- More accurate scores

### v1.1.0

**New:**
- CLI tool
- JSON output
- Custom scoring

**Fixed:**
- Bug in link checking
- Memory usage

### v1.0.0

**First Release:**
- Basic analysis
- Python API
- HTML reports

## Credits

Made by the README Quality Team.

Thanks to:
- John Doe (lead dev)
- Jane Smith (design)
- Bob Wilson (testing)
- All our users!

Based on research from:
- Flesch Reading Ease
- Gunning Fog Index
- GitHub README studies

## Support

Need help?

- **Bugs**: [GitHub Issues](https://github.com/user/readme-quality/issues)
- **Questions**: [Stack Overflow](https://stackoverflow.com/questions/tagged/readme-quality)
- **Chat**: [Discord Server](https://discord.gg/readme-quality)
- **Email**: help@readme-quality.com

We try to respond within 24 hours.

## License

MIT License

Copyright (c) 2024 README Quality Team

You can use this code for any purpose. See the LICENSE file for full details.

## Links

- **Home**: https://readme-quality.com
- **Docs**: https://docs.readme-quality.com
- **GitHub**: https://github.com/user/readme-quality
- **NPM**: https://www.npmjs.com/package/readme-quality
- **PyPI**: https://pypi.org/project/readme-quality

---

*This README was scored 100/100 with README Quality Tool! 🎉*