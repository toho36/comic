# Spec-Kitty: Comprehensive Guide

## Table of Contents
1. [Introduction](#introduction)
2. [What is Spec-Kitty?](#what-is-spec-kitty)
3. [Key Concepts](#key-concepts)
4. [Installation](#installation)
5. [Quick Start](#quick-start)
6. [Detailed Workflow](#detailed-workflow)
7. [Commands Reference](#commands-reference)
8. [AI Provider Configuration](#ai-provider-configuration)
9. [File Structure](#file-structure)
10. [Best Practices](#best-practices)
11. [Troubleshooting](#troubleshooting)
12. [Examples](#examples)
13. [Advanced Usage](#advanced-usage)

---

## Introduction

**Spec-Kitty** is a Spec-Driven Development (SDD) tool that helps you build software by writing specifications first, then using AI to implement them. It provides a structured workflow that separates specification from implementation, making AI-assisted development more predictable and maintainable.

### Why Spec-Kitty?

- **Specification-First**: Write detailed specs before coding
- **AI-Powered**: Leverages AI agents (Claude, GPT-4, etc.) to implement your specs
- **Structured Workflow**: Follows a clear process from idea to implementation
- **Test-Driven**: Built on TDD principles with automatic test generation
- **Git Integration**: Seamlessly works with version control
- **Language Agnostic**: Works with any programming language or framework

---

## What is Spec-Kitty?

Spec-Kitty is a CLI tool that implements the **Spec-Driven Development** methodology. It guides you through:

1. **Constitution**: Define project rules and constraints
2. **Specification**: Write detailed feature specifications
3. **Planning**: Break down specs into implementation tasks
4. **Implementation**: Use AI to execute the tasks
5. **Iteration**: Refine and improve through feedback

### Core Philosophy

> "Specs first, code second. Let AI handle the implementation while you focus on the what and why."

---

## Key Concepts

### 1. Constitution
A **constitution** is a set of rules and guidelines that govern your project. It includes:
- Project rules and conventions
- AI agent instructions
- Development standards
- Testing requirements
- Architecture decisions

### 2. Specification (Spec)
A **specification** is a detailed description of a feature or system. It includes:
- User stories and requirements
- Acceptance criteria
- Technical constraints
- Edge cases and error handling
- Success metrics

### 3. Plan
A **plan** breaks down the specification into actionable tasks. It includes:
- Task dependencies
- Implementation order
- Parallel execution opportunities
- Test requirements
- Milestone definitions

### 4. Tasks
**Tasks** are individual units of work that the AI agent executes. Each task:
- Has a clear objective
- Includes test requirements (TDD)
- May depend on other tasks
- Produces verifiable outputs

### 5. The Spec-Kitty Command
The special command `/spec-kitty.implement` instructs your AI agent to:
- Validate all prerequisites
- Execute tasks in order
- Follow dependencies
- Implement TDD approach
- Handle errors gracefully

---

## Installation

### Prerequisites

- **Python 3.8+** installed
- **Git** installed and configured
- **API keys** for your chosen AI provider

### Install via pip (Recommended)

```bash
pip install spec-kitty-cli
```

### Install from Source (Development)

```bash
# Clone the repository
git clone https://github.com/Priivacy-ai/spec-kitty.git
cd spec-kitty

# Install in editable mode
pip install -e .
```

### Verify Installation

```bash
spec-kitty --version
spec-kitty --help
```

### Set Environment Variable (if needed)

If you installed from source and templates aren't found:

```bash
# Linux/Mac
export SPEC_KITTY_TEMPLATE_ROOT=/path/to/spec-kitty

# Windows PowerShell
$env:SPEC_KITTY_TEMPLATE_ROOT="C:\path\to\spec-kitty"

# Windows CMD
set SPEC_KITTY_TEMPLATE_ROOT=C:\path\to\spec-kitty
```

---

## Quick Start

### Step 1: Initialize a New Project

```bash
spec-kitty init my-awesome-project --ai=claude
```

This creates:
```
my-awesome-project/
├── .spec-kitty/
│   ├── constitution.md
│   ├── spec.md
│   ├── plan.md
│   └── tasks.md
└── README.md
```

### Step 2: Define Your Constitution

Edit `.spec-kitty/constitution.md`:

```markdown
# Project Constitution

## Project Rules
- Use TypeScript for all code
- Follow functional programming principles
- Write tests for all functions
- Use ESLint and Prettier for formatting

## AI Agent Instructions
- Write clean, documented code
- Include error handling
- Add comments for complex logic
- Follow TypeScript best practices

## Testing Standards
- Use Jest for testing
- Aim for 80%+ code coverage
- Write unit tests for all functions
- Include integration tests for API endpoints
```

### Step 3: Write Your Specification

Edit `.spec-kitty/spec.md`:

```markdown
# Feature Specification: User Authentication

## Overview
Implement a secure user authentication system with JWT tokens.

## User Stories
1. As a user, I want to register with email and password
2. As a user, I want to login and receive a JWT token
3. As a user, I want to refresh my token when it expires

## Requirements
- Password must be hashed using bcrypt
- JWT tokens should expire after 1 hour
- Refresh tokens should expire after 7 days
- Rate limiting on login attempts

## Acceptance Criteria
- [ ] User can register with valid email/password
- [ ] User receives JWT token on successful login
- [ ] Password is hashed before storage
- [ ] Invalid credentials return 401 error
- [ ] Token validation works correctly
```

### Step 4: Create Your Plan

Edit `.spec-kitty/plan.md`:

```markdown
# Implementation Plan

## Task Breakdown
1. Setup project structure
2. Implement user registration
3. Implement login functionality
4. Add JWT token generation
5. Implement token refresh
6. Add rate limiting
7. Write integration tests

## Dependencies
- Task 2 depends on Task 1
- Task 3 depends on Task 2
- Task 4 depends on Task 3
- Task 5 depends on Task 4
- Task 6 is independent (can run in parallel)
- Task 7 depends on all previous tasks
```

### Step 5: Define Tasks

Edit `.spec-kitty/tasks.md`:

```markdown
# Tasks

## Task 1: Setup Project Structure
**Objective**: Initialize project with necessary files and folders

**Steps**:
1. Create folder structure
2. Initialize package.json
3. Setup TypeScript configuration
4. Configure Jest

**Tests**:
- Verify package.json exists
- Verify tsconfig.json exists
- Verify Jest configuration

## Task 2: Implement User Registration
**Objective**: Create user registration endpoint

**Steps**:
1. Create User model
2. Implement password hashing
3. Create registration endpoint
4. Add input validation

**Tests**:
- Test registration with valid data
- Test registration with duplicate email
- Test password hashing
```

### Step 6: Implement

Open your AI chat (Claude, ChatGPT, etc.) and type:

```
/spec-kitty.implement
```

The AI will:
1. Read all spec-kitty files
2. Validate prerequisites
3. Execute tasks in order
4. Write code following your constitution
5. Create tests as specified
6. Report progress and handle errors

---

## Detailed Workflow

### Phase 1: Project Setup

```bash
# Initialize with specific AI provider
spec-kitty init my-project --ai=claude
spec-kitty init my-project --ai=gpt4
spec-kitty init my-project --ai=o1

# Initialize with custom template root
spec-kitty init my-project --ai=claude --template-root=/path/to/templates

# Initialize with debug output
spec-kitty init my-project --ai=claude --debug
```

### Phase 2: Constitution Development

The constitution is your project's "rulebook". It should include:

**Project Rules Section:**
```markdown
## Project Rules
- Language: Python 3.11+
- Framework: FastAPI
- Database: PostgreSQL
- ORM: SQLAlchemy
```

**AI Instructions Section:**
```markdown
## AI Agent Behavior
- Write docstrings for all functions
- Use type hints everywhere
- Follow PEP 8 style guide
- Add logging for important operations
```

**Testing Requirements Section:**
```markdown
## Testing Standards
- Use pytest for testing
- Mock external dependencies
- Test all error paths
- Maintain >80% coverage
```

### Phase 3: Specification Writing

A good specification follows this structure:

**1. Overview Section:**
- Brief description of the feature
- Goals and objectives
- Success criteria

**2. User Stories Section:**
- Who are the users?
- What do they want to accomplish?
- Why is it valuable?

**3. Functional Requirements:**
- Detailed feature descriptions
- Input/output specifications
- Business logic rules

**4. Non-Functional Requirements:**
- Performance requirements
- Security considerations
- Scalability concerns

**5. Acceptance Criteria:**
- Checkbox list of verifiable outcomes
- Definition of done for each requirement

### Phase 4: Planning Phase

Break down your spec into manageable tasks:

**Task Design Principles:**
- Each task should take <2 hours to implement
- Tasks should be independent when possible
- Include test requirements for each task
- Specify dependencies explicitly

**Example Task:**
```markdown
## Task 3: Implement JWT Token Generation

**Objective**: Create JWT tokens for authenticated users

**Dependencies**: Task 2 (User Authentication)

**Steps**:
1. Install JWT library
2. Create token generation function
3. Add token validation function
4. Implement token expiration logic

**Tests**:
- Test token generation with valid payload
- Test token validation with valid token
- Test token validation with expired token
- Test token validation with invalid signature

**Success Criteria**:
- Token contains user ID and expiration
- Expired tokens are rejected
- Invalid tokens are rejected
```

### Phase 5: Implementation Phase

When you run `/spec-kitty.implement`, the AI will:

1. **Validation Phase:**
   - Check constitution.md exists and is valid
   - Check spec.md exists and is complete
   - Check plan.md exists and has tasks
   - Check tasks.md exists and is detailed
   - Validate git repository is initialized

2. **Execution Phase:**
   - Read and parse all task definitions
   - Build dependency graph
   - Identify parallel execution opportunities
   - Execute tasks in topological order

3. **Implementation Phase:**
   - For each task:
     - Read task description
     - Generate code following constitution rules
     - Create tests as specified
     - Verify tests pass
     - Commit changes (if configured)

4. **Completion Phase:**
   - Report overall success/failure
   - List any errors encountered
   - Provide next steps

---

## Commands Reference

### spec-kitty init

Initialize a new spec-kitty project.

```bash
spec-kitty init <project-name> [options]
```

**Options:**
- `--ai=<provider>`: AI provider to use (claude, gpt4, o1)
- `--template-root=<path>`: Path to templates directory
- `--debug`: Enable debug output

**Examples:**
```bash
# Basic initialization
spec-kitty init my-app --ai=claude

# With custom template path
spec-kitty init my-app --ai=claude --template-root=./templates

# With debug output
spec-kitty init my-app --ai=claude --debug
```

### spec-kitty version

Show version information.

```bash
spec-kitty --version
```

### spec-kitty help

Show help information.

```bash
spec-kitty --help
```

---

## AI Provider Configuration

### Supported AI Providers

1. **Claude (Anthropic)**
   - Model: claude-sonnet-4, claude-opus-4
   - Best for: Complex reasoning, detailed specifications

2. **GPT-4 (OpenAI)**
   - Model: gpt-4-turbo, gpt-4o
   - Best for: Quick iterations, code generation

3. **O1 (OpenAI)**
   - Model: o1-preview, o1-mini
   - Best for: Hard reasoning problems

### API Key Configuration

**For Claude:**
```bash
export ANTHROPIC_API_KEY="your-api-key"
```

**For GPT-4:**
```bash
export OPENAI_API_KEY="your-api-key"
```

### Choosing the Right AI Provider

| Provider | Best For | Speed | Cost | Reasoning |
|----------|----------|-------|------|-----------|
| Claude | Complex specs, detailed code | Medium | Medium | Excellent |
| GPT-4 | Quick iterations, standard apps | Fast | Low-Medium | Good |
| O1 | Hard problems, optimization | Slow | High | Best |

---

## File Structure

### Standard Spec-Kitty Project

```
my-project/
├── .spec-kitty/              # Spec-kitty configuration
│   ├── constitution.md       # Project rules and AI instructions
│   ├── spec.md              # Feature specification
│   ├── plan.md              # Implementation plan
│   └── tasks.md             # Detailed task breakdown
├── src/                     # Generated source code
├── tests/                   # Generated tests
├── package.json             # Project dependencies
└── README.md                # Project documentation
```

### The .spec-kitty Directory

This is the heart of your spec-kitty project:

**constitution.md**
- Project rules and conventions
- AI agent behavior instructions
- Testing standards
- Architecture guidelines

**spec.md**
- Feature overview
- User stories
- Functional requirements
- Non-functional requirements
- Acceptance criteria

**plan.md**
- Task breakdown
- Dependency graph
- Implementation order
- Milestone definitions

**tasks.md**
- Detailed task descriptions
- Step-by-step instructions
- Test requirements
- Success criteria

---

## Best Practices

### 1. Write Clear Constitutions

✅ **Good Constitution:**
```markdown
# Constitution

## Coding Standards
- Use TypeScript strict mode
- All functions must have return types
- Use functional programming patterns
- Avoid mutable state where possible

## AI Instructions
- Write self-documenting code
- Add JSDoc comments to all public functions
- Include error handling for all I/O operations
- Log important events

## Testing Requirements
- Write tests before implementation (TDD)
- Mock all external dependencies
- Test all error paths
- Aim for 90% code coverage
```

❌ **Bad Constitution:**
```markdown
# Constitution
Write good code.
Do tests.
Be careful.
```

### 2. Write Detailed Specifications

✅ **Good Specification:**
```markdown
# User Authentication API

## Overview
Build a REST API for user authentication with JWT tokens.

## Requirements

### Registration Endpoint
- **Route**: POST /api/auth/register
- **Input**: { email: string, password: string }
- **Success**: Returns 201 with user object (without password)
- **Errors**: 
  - 400: Invalid email format
  - 409: Email already exists
  - 500: Server error

### Password Requirements
- Minimum 8 characters
- Must contain uppercase letter
- Must contain number
- Must contain special character

## Acceptance Criteria
- [ ] User can register with valid credentials
- [ ] Password is hashed with bcrypt (salt rounds: 10)
- [ ] Duplicate email returns 409
- [ ] Invalid email returns 400
```

❌ **Bad Specification:**
```markdown
# User Authentication
Make a login system.
Users should be able to sign up.
Use JWT.
```

### 3. Break Down Tasks Properly

✅ **Good Task Breakdown:**
```markdown
## Task 1: Create User Model
**Time Estimate**: 30 minutes
**Dependencies**: None

**Steps**:
1. Define User interface with id, email, passwordHash
2. Create User class with constructor
3. Add method to compare passwords

**Tests**:
- Test creating user with valid data
- Test password comparison with correct password
- Test password comparison with incorrect password
```

❌ **Bad Task Breakdown:**
```markdown
## Task 1: Build Auth System
Create the whole authentication system with login, register, and JWT.
```

### 4. Iterate and Refine

1. Start with a simple spec
2. Implement and test
3. Gather feedback
4. Update spec if needed
5. Re-implement changes

### 5. Use Version Control

```bash
# Commit spec changes
git add .spec-kitty/
git commit -m "Update spec with new requirements"

# Commit implementation
git add src/ tests/
git commit -m "Implement user authentication"
```

---

## Troubleshooting

### Template Discovery Issues

**Error**: "Templates could not be found in any of the expected locations"

**Solution 1: Reinstall Package**
```bash
pip install --upgrade spec-kitty-cli
```

**Solution 2: Set Template Path**
```bash
export SPEC_KITTY_TEMPLATE_ROOT=$(pwd)
spec-kitty init my-project --ai=claude --template-root=$(pwd)
```

**Solution 3: Verify Installation**
```bash
python -c "from importlib.resources import files; print(files('specify_cli').joinpath('templates'))"
```

### AI Implementation Issues

**Problem**: AI generates code that doesn't match your constitution

**Solution**: 
- Make constitution more specific
- Add examples to constitution
- Explicitly forbid certain patterns
- Use negative examples

**Problem**: AI skips tests

**Solution**:
- Make testing requirements explicit in constitution
- Include test requirements in each task
- Set minimum coverage percentage

**Problem**: Tasks execute in wrong order

**Solution**:
- Clearly specify dependencies in plan.md
- Use dependency notation in tasks.md
- Review dependency graph before implementation

### Git Authentication Issues (Linux)

```bash
#!/usr/bin/env bash
set -e
echo "Downloading Git Credential Manager v2.6.1..."
wget https://github.com/git-ecosystem/git-credential-manager/releases/download/v2.6.1/gcm-linux_amd64.2.6.1.deb
echo "Installing Git Credential Manager..."
sudo dpkg -i gcm-linux_amd64.2.6.1.deb
echo "Configuring Git to use GCM..."
git config --global credential.helper manager
echo "Cleaning up..."
rm gcm-linux_amd64.2.6.1.deb
```

### Debug Mode

Enable debug output to see what's happening:

```bash
spec-kitty init my-project --ai=claude --debug
```

This shows:
- Paths being searched
- Files being read
- Validation steps
- Error details

---

## Examples

### Example 1: Simple Web API

**Scenario**: Build a simple todo API

**Constitution**:
```markdown
# Constitution
- Use Python with FastAPI
- Use SQLAlchemy for database
- Follow REST conventions
- Write pytest tests
```

**Spec**:
```markdown
# Todo API
- Create todo items
- List all todos
- Update todo status
- Delete todos
```

**Plan**:
```markdown
1. Setup FastAPI project
2. Create Todo model
3. Implement CRUD endpoints
4. Add tests
```

**Run**: `/spec-kitty.implement`

### Example 2: React Component

**Constitution**:
```markdown
# Constitution
- Use TypeScript
- Use functional components
- Use Tailwind CSS
- Use React Testing Library
```

**Spec**:
```markdown
# Button Component
- Support different sizes (sm, md, lg)
- Support different variants (primary, secondary)
- Support loading state
- Support disabled state
```

**Plan**:
```markdown
1. Create Button component with props
2. Implement variants
3. Implement sizes
4. Add loading state
5. Add tests
```

**Run**: `/spec-kitty.implement`

---

## Advanced Usage

### Custom Templates

You can create custom templates for your organization:

```bash
# Clone spec-kitty
git clone https://github.com/Priivacy-ai/spec-kitty.git
cd spec-kitty

# Edit templates
vim templates/commands/init/

# Use custom templates
spec-kitty init my-project --template-root=/path/to/spec-kitty
```

### Multi-Project Workspaces

```bash
# Setup workspace
mkdir workspace
cd workspace

# Create multiple projects
spec-kitty init backend --ai=claude
spec-kitty init frontend --ai=claude
spec-kitty init shared --ai=claude
```

### Continuous Integration

Add to your CI pipeline:

```yaml
# .github/workflows/test.yml
name: Test
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Install spec-kitty
        run: pip install spec-kitty-cli
      - name: Validate specs
        run: spec-kitty validate
      - name: Run tests
        run: pytest
```

### Integration with Existing Projects

```bash
# Add spec-kitty to existing project
cd existing-project
spec-kitty init . --ai=claude

# This creates .spec-kitty/ directory
# Your existing code remains unchanged
```

---

## Tips and Tricks

1. **Start Small**: Your first spec-kitty project should be simple
2. **Iterate Often**: Don't try to perfect the spec on the first try
3. **Be Explicit**: More detail in spec = better implementation
4. **Test Driven**: Always include test requirements
5. **Version Control**: Commit your specs alongside code
6. **Review Output**: Always review AI-generated code
7. **Refactor**: Update specs when you refactor
8. **Share Specs**: Specs are documentation - share with team

---

## Resources

- **GitHub Repository**: https://github.com/Priivacy-ai/spec-kitty
- **Issues**: https://github.com/Priivacy-ai/spec-kitty/issues
- **License**: MIT
- **Maintainer**: Robert Douglass (@robertDouglass)
- **Inspired by**: John Lam's research

---

## FAQ

### Q: Can I use spec-kitty with any programming language?
**A**: Yes! Spec-kitty is language-agnostic. Just specify your language in the constitution.

### Q: Do I need to be an expert to use spec-kitty?
**A**: No, but you need to understand the basics of software development. The AI helps with implementation details.

### Q: How much does it cost?
**A**: spec-kitty itself is free (MIT licensed). You pay for AI API usage (Claude, GPT-4, etc.).

### Q: Can I use spec-kitty for large projects?
**A**: Yes, but break large projects into smaller, manageable specs.

### Q: What if the AI makes a mistake?
**A**: Review the generated code, update your spec/tasks if needed, and re-run.

### Q: Can I collaborate with a team?
**A**: Yes! Commit .spec-kitty/ to git and collaborate on specs.

---

## Conclusion

Spec-Kitty transforms how you build software by putting specifications first. By following this guide, you should be able to:

✅ Initialize and configure spec-kitty projects
✅ Write clear constitutions, specs, plans, and tasks
✅ Use AI to implement your specifications
✅ Follow best practices for spec-driven development
✅ Troubleshoot common issues
✅ Apply spec-kitty to real-world projects

**Remember**: The key to success with spec-kitty is writing clear, detailed specifications. The better your spec, the better the implementation!

Happy spec-driven development! 🚀

---

*Last Updated: December 2025*
*Version: 1.0*
*License: MIT*
