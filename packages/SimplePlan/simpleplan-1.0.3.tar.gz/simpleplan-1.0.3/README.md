# SimplePlan

🎯 **The First AI-Native Project Management Tool with Universal AI Access**

[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![MCP Compatible](https://img.shields.io/badge/MCP-Compatible-green.svg)](https://modelcontextprotocol.io/)
[![Tests](https://github.com/bjornjohnson/SimplePlan/actions/workflows/test.yml/badge.svg)](https://github.com/bjornjohnson/SimplePlan/actions/workflows/test.yml)
[![Publish](https://github.com/bjornjohnson/SimplePlan/actions/workflows/publish.yml/badge.svg)](https://github.com/bjornjohnson/SimplePlan/actions/workflows/publish.yml)

## 🚀 What is SimplePlan?

SimplePlan revolutionizes project management by enabling **direct AI control** over project plans. Unlike traditional tools where AI can only suggest actions, SimplePlan's Model Context Protocol (MCP) integration allows AI systems to:

- **Create and manage** project plans autonomously
- **Track progress** in real-time  
- **Add and complete** project steps with dependency validation
- **Optimize workflows** based on project status
- **Coordinate teams** through intelligent step assignment

## ✨ Key Features

### 🧠 **AI-Native Design**
- **7 MCP Tools** for complete project control via AI
- **Universal AI Access** through Claude Desktop and other MCP hosts
- **Real-time Collaboration** between humans and AI systems

### 📋 **Comprehensive Project Management**
- **Dependency Validation** ensures logical project flow
- **Progress Tracking** with completion percentages
- **Step Management** with types, assignments, and timestamps
- **Project Validation** catches errors before they cause problems

### 🔌 **Modern Integration**
- **FastMCP Framework** for efficient AI communication
- **CLI Interface** for manual project management
- **JSON Storage** for portable, version-controllable plans
- **Rich Terminal UI** for beautiful command-line experience

## 🛠️ MCP Tools Available

1. **`create_project_plan`** - Start new projects with AI
2. **`get_project_status`** - Check progress and completion
3. **`add_project_step`** - Add work items with dependencies
4. **`complete_step`** - Mark work done with validation
5. **`get_next_steps`** - Find available work (no blockers)
6. **`list_all_steps`** - Show complete project overview
7. **`validate_project_plan`** - Check for errors and issues

## 🚀 Quick Start

### Installation
```bash
git clone https://github.com/bjornjohnson/SimplePlan.git
cd SimplePlan
poetry install
```

### CLI Usage
```bash
# Create a new project
poetry run simpleplan create "My Web App" "Build a React todo application"

# Add project steps
poetry run simpleplan add "Set up development environment" --type setup
poetry run simpleplan add "Create React components" --type development --depends STEP-001

# Track progress
poetry run simpleplan status
poetry run simpleplan next

# Complete work
poetry run simpleplan complete STEP-001
```

### MCP Integration (AI Access)
1. **Configure Claude Desktop** with SimplePlan MCP server
2. **Ask AI** to manage your projects directly
3. **Watch AI** create, track, and optimize your project plans autonomously

See [MCP_INTEGRATION.md](MCP_INTEGRATION.md) for complete setup instructions.

## 📚 Documentation

- **[MCP Integration Guide](MCP_INTEGRATION.md)** - Complete setup and usage
- **[Usage Examples](MCP_USAGE_EXAMPLES.md)** - Real-world AI scenarios  
- **[Intellectual Property Guide](INTELLECTUAL_PROPERTY.md)** - Ownership and protection

## 🎯 Why SimplePlan?

### **Before SimplePlan:**
- AI: "You should run `npm install react`"
- Human: *manually runs command*
- AI: "Now create components..."
- Human: *manually executes each suggestion*

### **After SimplePlan:**
- AI: *directly creates project plan with React setup*
- AI: *adds development steps with proper dependencies*
- AI: *tracks progress as human completes work*
- AI: *suggests optimizations and next priorities*

**Result:** Seamless human-AI collaboration instead of suggestion-based workflows.

## 🏗️ Architecture

```
Claude Desktop (Host) 
    ↓ JSON-RPC 2.0 via stdio
SimplePlan MCP Server (FastMCP)
    ↓ Function calls
SimplePlan Core (project_plan_io.py)
    ↓ File operations  
Project Plan JSON Files
```

## 🧪 Development

### Setup
```bash
poetry install
poetry shell  # Activate virtual environment

# Run tests
poetry run pytest

# Development commands
poetry run black .         # Format code
poetry run ruff .          # Lint code  
poetry run isort .         # Sort imports
poetry run mypy .          # Type checking
```

### Project Status
- **Phase 1 Complete**: Full CLI functionality with comprehensive tests
- **Phase 2 Complete**: MCP integration with 7 AI tools
- **Current Status**: 100% complete, production-ready

## 📄 License & Copyright

**Copyright © 2025 Sunset Code Collaborative, LLC. All rights reserved.**

Licensed under the [MIT License](LICENSE). This means:
- ✅ **Free to use** for any purpose
- ✅ **Free to modify** and distribute
- ✅ **Commercial use** permitted
- ⚠️ **Attribution required** - must include copyright notice
- ⚠️ **No warranty** - use at your own risk

## 🤝 Contributing

SimplePlan is open to contributions! Please:
1. **Fork** the repository
2. **Create** a feature branch
3. **Add** tests for new functionality
4. **Submit** a pull request with clear description

All contributors must respect the copyright and licensing terms.

## 📞 Contact

**Sunset Code Collaborative, LLC** - Creator & Maintainer
- Contact: Bjorn Johnson, Member
- GitHub: [@bjornjohnson](https://github.com/bjornjohnson)
- Email: bjorn@sunsetcodecollaborative.com

## 🎉 Acknowledgments

- **FastMCP** - Excellent MCP framework for Python
- **Claude Desktop** - First-class MCP host implementation
- **Model Context Protocol** - Revolutionary AI integration standard

---

**🏆 SimplePlan: Pioneering the future of AI-human project collaboration since 2025**

*Built with ❤️ and cutting-edge AI integration*
