# 🐠 Goldfish CLI

> AI-First Personal Knowledge Management from the Command Line

Goldfish CLI is an intelligent command-line tool that helps you capture, organize, and retrieve your thoughts with AI assistance. It uses advanced entity recognition to automatically extract people, projects, and topics from your notes, while providing human-in-the-loop verification to ensure accuracy.

## ✨ Features

- **🤖 AI-Powered Entity Recognition**: Automatically extracts @mentions, #hashtags, and topics
- **🔗 Smart Entity Linking**: Prevents duplicates by linking similar entities intelligently  
- **💬 Interactive REPL Mode**: Persistent session for seamless thought capture
- **🎯 Human-in-the-Loop**: Verify AI suggestions with create/link/reject/skip options
- **📊 Rich Terminal UI**: Beautiful tables, panels, and color-coded confidence scores
- **⚡ Quick Capture**: Natural language processing for rapid note-taking
- **🔍 Smart Search**: Find entities with fuzzy matching and alias support

## 🚀 Installation

### From PyPI (Recommended)

```bash
pip install goldfish-cli
```

### From Source

```bash
git clone https://github.com/linxichen/goldfish.git
cd goldfish/goldfish-cli
pip install -e .
```

## 🎮 Quick Start

### Interactive Mode
```bash
# Start interactive session
goldfish

# Just type naturally
🐠 Meeting with @sarah about #project-alpha tomorrow

# AI processes and shows suggestions
🤖 Analyzing with AI...
📊 Found 2 entities, 1 task

# Verify suggestions inline
💾 Save this capture? (Y/n): y
```

### Command Mode  
```bash
# Quick capture
goldfish capture quick "TODO: Follow up with @john about #ai-research"

# Review AI suggestions
goldfish suggestions pending

# View dashboard
goldfish dashboard status
```

## 📋 Core Commands

| Command | Description |
|---------|-------------|
| `goldfish` | Start interactive REPL mode |
| `goldfish capture quick <text>` | Quick capture with AI processing |
| `goldfish suggestions pending` | View pending AI suggestions |
| `goldfish suggestions verify-all` | Interactive verification workflow |
| `goldfish dashboard status` | Show overview and statistics |
| `goldfish dashboard entities` | List all entities |
| `goldfish config setup` | Initial configuration |

## 🎯 Entity Recognition

Goldfish automatically recognizes:

- **👥 People**: `@sarah` → Links to person entities
- **📁 Projects**: `#project-alpha` → Links to project entities  
- **🧠 Topics**: Natural language detection of research topics
- **✅ Tasks**: `TODO:`, `follow up`, `need to` patterns

## 🔗 Smart Entity Linking

When AI suggests entities, you have four options:

- **Create** (`c`): Make new entity from suggestion
- **Link** (`l`): Connect to existing entity (shows candidates with match scores)
- **Reject** (`r`): Mark as incorrect (helps AI learn)
- **Skip** (`s`): Leave for later review

```
🔗 Found existing entities to link to:
┌────────┬─────────────────┬─────────┬─────────────────┐
│ Option │ Name            │ Match   │ Details         │
├────────┼─────────────────┼─────────┼─────────────────┤
│ 1      │ Sarah Johnson   │ 85%     │ aliases: sarah  │
│ 2      │ Sarah Martinez  │ 70%     │ aliases: s.m    │
│ 0      │ Create new      │ 100%    │ New entity      │
└────────┴─────────────────┴─────────┴─────────────────┘

Select entity to link to (0-2) [0]: 1
🔗 Linked to existing entity: Sarah Johnson
```

## 🏗️ Architecture

Goldfish CLI is built with:

- **Click**: Command-line interface framework
- **Rich**: Beautiful terminal formatting  
- **SQLModel**: Database ORM with SQLite storage
- **Prompt Toolkit**: Interactive prompts with history
- **Pydantic**: Configuration and data validation

## 🛠️ Development

### Setup Development Environment

```bash
git clone https://github.com/linxichen/goldfish.git
cd goldfish/goldfish-cli

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest

# Run linting
ruff check .
black --check .
mypy .
```

### Project Structure

```
goldfish-cli/
├── src/goldfish_cli/          # Main package
│   ├── __init__.py
│   ├── main.py               # CLI entry point
│   ├── commands/             # Command implementations
│   ├── core/                 # Core functionality
│   ├── models/               # Database models
│   └── services/             # Business logic
├── tests/                    # Test suite
├── docs/                     # Documentation
└── pyproject.toml           # Package configuration
```

## 📖 Documentation

- [Installation Guide](docs/installation.md)
- [User Guide](docs/user-guide.md)
- [Developer Guide](docs/development.md)
- [API Reference](docs/api.md)

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests and documentation
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

Built with modern Python tools and inspired by the best CLI experiences:
- [Click](https://click.palletsprojects.com/) for the CLI framework
- [Rich](https://rich.readthedocs.io/) for beautiful terminal output
- [SQLModel](https://sqlmodel.tiangolo.com/) for type-safe database operations

---

<div align="center">

**[🏠 Homepage](https://github.com/linxichen/goldfish)** • 
**[📚 Documentation](https://github.com/linxichen/goldfish/tree/main/goldfish-cli)** • 
**[🐛 Report Bug](https://github.com/linxichen/goldfish/issues)** • 
**[💡 Request Feature](https://github.com/linxichen/goldfish/issues)**

Made with ❤️ for knowledge workers everywhere

</div>