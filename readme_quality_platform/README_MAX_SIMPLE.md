# README Tool

## What It Does

This tool checks README files. It tells you if your README is good or bad.

## Why Use It

Good README files help people use your code. Bad ones make people go away.

## How To Install

```bash
pip install readme-tool
```

## How To Use

```python
from readme_tool import check

score = check("README.md")
print(score)
```

## Web Tool

```bash
readme-tool web
```

Go to: http://localhost:8000

## Check One File

```python
import readme_tool

result = readme_tool.check_file("README.md")
print(result)
```

## Check Many Files

```bash
readme-tool check *.md
```

## What Gets A Good Score

### Easy Words

Use short words. Use common words. Do not use big words.

### Short Sentences

Keep sentences short. Use less than 10 words per sentence.

### All Parts

Your README needs these parts:

- **Title**: Name of your project
- **About**: What it does
- **Setup**: How to install
- **Use**: How to run it
- **Help**: Where to get help

### Nice Format

Add these things:

- Code boxes
- Lists
- Links
- Bold text
- Tables

## Scores

| Score | Grade | What It Means |
|-------|-------|---------------|
| 90+   | A     | Great job!    |
| 80-89 | B     | Good job      |
| 70-79 | C     | OK job        |
| 60-69 | D     | Bad job       |
| 0-59  | F     | Very bad      |

## Setup

### Easy Way

```bash
pip install readme-tool
readme-tool check README.md
```

### Full Way

```bash
git clone https://github.com/user/readme-tool.git
cd readme-tool
pip install -e .
```

### Docker Way

```bash
docker run -v $(pwd):/data readme-tool check /data/README.md
```

## Config

Make a file called `config.yaml`:

```yaml
scores:
  easy_text: 25
  good_parts: 25
  nice_format: 25
  match_code: 25

output:
  show_tips: true
  use_colors: true
```

## Tips

### Make Text Easy

- Use short words (1-2 parts)
- Keep sentences under 10 words
- Use simple grammar
- Do not use hard words

### Add All Parts

Must have:
- Title
- About text
- How to install
- How to use

Good to have:
- Examples
- FAQ
- Credits
- Support info

### Make It Look Good

Add these:
- Code examples in boxes
- Lists of things
- Links to docs
- Bold and italic text
- Tables of data

## Examples

### Simple README

```markdown
# My Tool

Does task X.

## Install

```bash
npm install my-tool
```

## Use

```js
const tool = require('my-tool');
tool.run();
```
```

### Full README

```markdown
# Big App

Makes web apps fast and easy.

## Features

- Fast setup
- Easy config
- Good docs

## Quick Start

```bash
npm install big-app
npx big-app create my-app
cd my-app
npm start
```

## Docs

See docs/ folder for more help.

## License

MIT
```

## FAQ

**Q: How does it work?**

A: It reads your README file. It checks four things. It gives you a score.

**Q: What makes text easy?**

A: Short words. Short sentences. Simple grammar.

**Q: What parts do I need?**

A: Title, about, install, use, and license.

**Q: Can I change the rules?**

A: Yes. Edit the config file.

**Q: Is it free?**

A: Yes. It is open source.

## Help

Need help?

- **Bugs**: [Issues](https://github.com/user/readme-tool/issues)
- **Questions**: [Stack Overflow](https://stackoverflow.com/questions/tagged/readme-tool)
- **Chat**: [Discord](https://discord.gg/readme-tool)

## Credits

Made by:
- John Doe
- Jane Smith
- Bob Lee

Thanks to all users!

## License

MIT License

You can use this code for free. See LICENSE file.

## Links

- **Home**: https://readme-tool.com
- **Code**: https://github.com/user/readme-tool
- **Docs**: https://docs.readme-tool.com

---

*Got 100/100 with README Tool! 🎉*