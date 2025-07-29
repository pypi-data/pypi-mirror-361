# Quaestor

> 🏛️ Keep your AI assistant on track and actually useful

[![Python](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PyPI](https://img.shields.io/pypi/v/quaestor.svg)](https://pypi.org/project/quaestor/)

Quaestor gives your AI assistant the context it needs to actually help you code. It analyzes your project, generates smart documentation, and keeps Claude from going off the rails.

## 🎯 Why?

Ever had Claude forget what you were working on? Or suggest patterns that don't match your codebase? Yeah, us too.

Quaestor fixes that by:

- **🧠 Understanding your code**: Detects your stack, patterns, and architecture automatically
- **📚 Keeping context**: Maintains what's been done and what's next across sessions
- **🎮 Enforcing standards**: Makes sure AI follows YOUR project's patterns, not generic ones
- **📊 Tracking progress**: Knows what's done, what's in progress, what's next
- **✅ Quality gates**: Won't let AI claim "done" until tests pass and linters are happy

## 📦 Installation

### Quickest (no install needed)
```bash
# Just run it
uvx quaestor init
```

### If you want it installed
```bash
# Global install with uv
uv tool install quaestor

# Or add to your project
uv add quaestor

# Old school pip works too
pip install quaestor
```

## 🚀 Getting Started

### 1. Initialize in your project:
```bash
quaestor init
```

This will:
- 🔍 Scan your code to figure out what you're building
- 💬 Ask a few smart questions based on what it finds
- 📝 Generate context files that AI assistants actually understand
- ✨ Set you up for success

### 2. What you get:
- `CLAUDE.md` - Instructions for your AI assistant (root dir so Claude auto-reads it)
- `.quaestor/ARCHITECTURE.md` - Your actual architecture (not hallucinated)
- `.quaestor/MEMORY.md` - What's been done, what's next
- `.quaestor/commands/` - Battle-tested workflows

### 3. Just start coding:
When you open your project with Claude, it automatically reads these files and knows:
- Your project structure
- Your coding standards
- What you're working on
- How to test and validate changes

## 📁 What goes where

```
your-project/
├── CLAUDE.md              # AI reads this first
└── .quaestor/
    ├── ARCHITECTURE.md    # Your real architecture
    ├── MEMORY.md          # Progress tracking
    └── commands/          # Workflows that work
        ├── project-init.md # Smart project analysis
        ├── task-py.md     # Python workflows
        ├── task-rs.md     # Rust workflows
        ├── check.md       # Quality checks
        └── compose.md     # Template combos
```

## 🌟 What it does

### Right now

- **🔍 Smart Analysis**: 
  - Figures out your stack (React? Django? FastAPI? etc.)
  - Detects your patterns (MVC? DDD? Microservices?)
  - Finds your tools (PostgreSQL? Redis? Docker?)
  
- **🤖 Context Generation**:
  - Writes docs FROM your code, not assumptions
  - Tracks progress from git history
  - Asks the right questions
  
- **📝 AI-Friendly Format**: 
  - Special markers for precise edits
  - Structured data that won't get mangled
  - Designed for LLMs, not humans
  
- **🎯 Command System**: 
  - `init` - Smart setup with code analysis
  - `task-py` / `task-rs` - Language-specific workflows  
  - `check` - Make sure everything's clean
  - `compose` - Combine templates for complex stuff
  - `milestone-commit` - Auto-commit completed work with PRs

### Coming soon

- **Git Review**: Automated PR reviews that actually understand your code
- **Auto Docs**: Keep docs in sync with code automatically
- **More Languages**: task-js, task-go, etc.
- **Team Sync**: Share context across your team

## 🏗️ How it actually works

### When you run `quaestor init`:

1. **Scans your project**:
   - Looks for package.json, requirements.txt, Cargo.toml, etc.
   - Detects frameworks from imports and dependencies
   - Figures out your architecture from folder structure

2. **Asks smart questions**:
   - Only asks what it can't figure out
   - Questions based on what it found
   - Skips the obvious stuff

3. **Generates real docs**:
   - Architecture based on your actual code
   - Progress from your git history
   - Standards from your existing patterns

### The special format

We use a markdown format that LLMs can reliably parse and edit:

```markdown
<!-- SECTION:architecture:database:START -->
```yaml
database:
  type: PostgreSQL
  orm: SQLAlchemy
  migrations: Alembic
```
<!-- SECTION:architecture:database:END -->
```

This lets AI make precise edits without breaking your docs.

## 🔗 Part of something bigger

Quaestor is part of Praetor - tools for engineers who actually like coding but want AI to handle the boring stuff. You stay in control, AI does the grunt work. It's just that most of it is my head.

## 💻 Contributing

```bash
# Get the code
git clone https://github.com/jeanluciano/quaestor.git
cd quaestor

# Setup
uv sync

# Test it
uv run pytest

# Try it
uv run python main.py init
```

## 📚 Command Templates

- **`project-init.md`** - Analyzes your project and sets everything up
- **`task-py.md`** - Python implementation with all the checks
- **`task-rs.md`** - Rust implementation with clippy and all
- **`check.md`** - Fix all the things
- **`compose.md`** - Combine templates for complex operations
- **`milestone-commit.md`** - Auto-commit completed TODOs and create PRs

### 🔄 Workflow Hooks

Quaestor now includes automatic workflow hooks that trigger after certain events:

- **After completing a TODO**: Automatically commits your work
- **After updating MEMORY.md**: Checks for completed items and commits them
- **When milestone is complete**: Creates a pull request automatically

These hooks are configured in `CLAUDE.md` and integrated into the task commands. They ensure:
- Clean git history with atomic commits
- Automatic quality checks before commits
- Progress tracking stays in sync
- PRs are created when milestones are done

### 🎯 How Milestones & Project Management Work

When you run `/quaestor:project:init`, the system creates a complete project management framework:

```yaml
.quaestor/
├── MANIFEST.yaml        # Project metadata and milestone tracking
├── milestones/          # Detailed milestone documentation
│   └── foundation/      # Current milestone directory
│       └── README.md    # Milestone details and tasks
├── ARCHITECTURE.md      # AI-optimized architecture
└── MEMORY.md           # Progress tracking
```

The system uses **THREE synchronized tracking systems**:

1. **MANIFEST.yaml** - High-level milestone state
   - Current milestone, progress percentages
   - Project metadata and dependencies
   - Links to all documentation

2. **milestones/[name]/README.md** - Detailed task lists
   - Checkbox task lists (✅ completed, 🔄 in progress, 📋 to do)
   - Success criteria and technical requirements
   - Milestone-specific documentation

3. **MEMORY.md** - Daily progress and context
   - What's been done, what's in progress
   - Lessons learned and blockers
   - Next immediate actions

#### How It All Works Together

```
compose.md loads task template
         ↓
task.md reads MANIFEST.yaml → finds current: "foundation"
         ↓
task.md reads .quaestor/milestones/foundation/README.md
         ↓
Executes work → Updates task checkboxes
         ↓
Updates MEMORY.md progress → Updates MANIFEST.yaml progress
         ↓
milestone-commit creates atomic commits
         ↓
When all tasks complete → PR for milestone
```

This provides:
- **Strategic view** (MANIFEST.yaml) - Where are we overall?
- **Tactical view** (milestone READMEs) - What needs to be done?
- **Operational view** (MEMORY.md) - What are we doing today?

The commands stay milestone-aware by reading this context, ensuring your AI assistant always knows where you are in the project!

## 📄 License

[MIT](LICENSE) - Use it however you want.

## 🤝 Contributing

PRs welcome! Just make sure tests pass and linters are happy.
