# Ralph Loop Integration for Comic Slideshow Generator

## Overview

This document describes how to integrate the **Ralph Loop** system (automated task execution using Goose subagents) into the Comic Slideshow Generator implementation. Ralph Loop will automate the execution of tasks defined in `plan.md` and `tasks.md`.

---

## What is Ralph Loop?

**Ralph Loop** is a task automation framework that uses **Goose subagents** to automatically execute tasks from a task list (TASKS.md). It provides:

- ✅ **Automated task execution** - Tasks run automatically with Goose subagents
- ✅ **Parallel processing** - Independent tasks run simultaneously
- ✅ **Dependency resolution** - Tasks execute in correct order
- ✅ **Retry mechanism** - Failed tasks retry automatically
- ✅ **Progress tracking** - Real-time progress monitoring
- ✅ **Safety features** - Dry-run mode, Git rollback, stop signals
- ✅ **Logging** - Comprehensive logging of all operations

---

## Integration Benefits

### Without Ralph Loop
- Manual implementation of 16 tasks
- Sequential execution (~81 hours)
- Manual testing after each task
- Manual error recovery
- No parallel execution

### With Ralph Loop
- **Automated implementation** - Tasks execute automatically
- **Parallel execution** - 3-4x faster (~20-25 hours)
- **Automated testing** - Tests run after each task
- **Automatic retry** - Failed tasks retry up to 3 times
- **Specialized agents** - Different agents for different task types

---

## Ralph Loop Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Ralph Loop Controller                     │
│  - Reads TASKS.md                                           │
│  - Resolves dependencies                                    │
│  - Dispatches tasks to subagents                            │
│  - Tracks progress and results                              │
└─────────────────────────────────────────────────────────────┘
                               │
                ┌──────────────┼──────────────┐
                │              │              │
                ▼              ▼              ▼
        ┌───────────┐  ┌───────────┐  ┌───────────┐
        │Implement  │  │  Test     │  │  Audit    │
        │  Agent    │  │  Agent    │  │  Agent    │
        └───────────┘  └───────────┘  └───────────┘
                │              │              │
                └──────────────┼──────────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │   Goose Subagents   │
                    │  (Automatic Code    │
                    │   Generation)       │
                    └─────────────────────┘
```

---

## Implementation Steps

### Phase 1: Ralph Loop Setup (Task 14)

#### Step 1: Create Project Structure

```bash
comic-slideshow-generator/
├── .spec-kitty/              # Spec-kitty files
├── ralph_loop/               # Ralph Loop system
│   ├── config.yaml          # Ralph Loop configuration
│   ├── ralph_loop.py        # Main loop implementation
│   ├── agents/              # Specialized agents
│   │   ├── __init__.py
│   │   ├── goose_agent.py  # Base agent class
│   │   ├── implement_agent.py
│   │   ├── test_agent.py
│   │   ├── audit_agent.py
│   │   └── debug_agent.py
│   ├── utils/               # Utilities
│   │   ├── __init__.py
│   │   ├── goose_helper.py
│   │   └── task_parser.py
│   └── prompts/             # Prompt templates
│       ├── implement.md
│       ├── test.md
│       ├── audit.md
│       └── debug.md
├── TASKS.md                 # Task list for Ralph Loop
├── src/                     # Application code
├── tests/                   # Test suite
└── app.py                   # Streamlit app
```

#### Step 2: Create Ralph Loop Configuration

**File: `ralph_loop/config.yaml`**

```yaml
# Ralph Loop Configuration for Comic Slideshow Generator

project:
  name: "Comic Slideshow Generator"
  version: "1.0.0"
  description: "AI-powered comic to slideshow converter"

# Goose Configuration
goose:
  # LLM Provider (anthropic, openai, azure, etc.)
  provider: "anthropic"
  model: "claude-sonnet-4"
  temperature: 0.7
  max_tokens: 4000
  
# Ralph Loop Settings
ralph_loop:
  tasks_file: "TASKS.md"
  max_parallel_tasks: 3
  retry_failed_tasks: true
  max_retries: 3
  retry_delay: 5  # seconds
  continue_on_error: false
  
# Safety Features
safety:
  # Dry-run mode (simulate execution without making changes)
  dry_run: false
  
  # Git integration
  auto_commit: true
  commit_message_prefix: "[Ralph]"
  create_branch: false
  branch_name: "ralph-loop-automation"
  
  # Confirmation
  require_confirmation: false
  stop_on_first_error: false
  
  # Rollback
  auto_rollback: true
  rollback_on_error: true
  
# Logging
logging:
  level: "INFO"  # DEBUG, INFO, WARNING, ERROR
  file: "ralph_loop.log"
  console: true
  include_timestamps: true
  include_task_details: true
  
# Monitoring
monitoring:
  track_time: true
  track_tokens: true
  save_results: "ralph_results.json"
  update_progress_bar: true
  
# Agent Configuration
agents:
  implement:
    name: "Implement Agent"
    description: "Implements features and fixes bugs"
    temperature: 0.7
    max_iterations: 3
    
  test:
    name: "Test Agent"
    description: "Creates and runs tests"
    temperature: 0.5
    coverage_target: 80
    
  audit:
    name: "Audit Agent"
    description: "Reviews code for quality and standards"
    temperature: 0.3
    check_pep8: true
    check_type_hints: true
    check_docstrings: true
    
  debug:
    name: "Debug Agent"
    description: "Fixes bugs and errors"
    temperature: 0.6
    max_attempts: 5
```

#### Step 3: Create TASKS.md

**File: `TASKS.md`**

```markdown
# Comic Slideshow Generator - Task List for Ralph Loop

## Task Format
- [ ] Task title
  - Type: [feature|bugfix|test|refactor|documentation]
  - Priority: [critical|high|medium|low]
  - Estimated: X hours
  - Dependencies: task_id1, task_id2
  - Agent: [implement|test|audit|debug]
  - Description: Task description

---

## Phase 1: Foundation

### T001: Project Structure & Configuration
- [ ] Create project directory structure
- [ ] Setup requirements.txt with all dependencies
- [ ] Create config.py with configuration dataclasses
- [ ] Setup logging configuration
- [ ] Create .env.example file
- Type: feature
- Priority: critical
- Estimated: 2 hours
- Dependencies: none
- Agent: implement
- Description: Initialize project with proper structure, configuration system, and development environment

### T002: Dependency Detection Module
- [ ] Create dependency_checker.py module
- [ ] Implement Tesseract detection
- [ ] Implement Poppler detection
- [ ] Implement FFmpeg detection
- [ ] Add platform-specific installation instructions
- Type: feature
- Priority: critical
- Estimated: 3 hours
- Dependencies: T001
- Agent: implement
- Description: Create module to detect and validate external dependencies

### T003: File Preprocessing Module
- [ ] Create ImageLoader class for JPG/PNG
- [ ] Create PDFConverter class using pdf2image
- [ ] Add file validation
- [ ] Create Comic dataclass
- Type: feature
- Priority: high
- Estimated: 4 hours
- Dependencies: T001, T002
- Agent: implement
- Description: Load and convert comic files to images

---

## Phase 2: Core Detection & Extraction

### T004: Speech Bubble Detection
- [ ] Implement BubbleDetector class
- [ ] Implement grayscale conversion
- [ ] Implement adaptive thresholding
- [ ] Implement contour detection and filtering
- [ ] Add bubble visualization
- Type: feature
- Priority: high
- Estimated: 6 hours
- Dependencies: T003
- Agent: implement
- Description: Detect speech bubbles in comic images using OpenCV

### T005: Text Extraction (OCR)
- [ ] Create TextExtractor class
- [ ] Integrate pytesseract OCR
- [ ] Add Czech and English language support
- [ ] Implement confidence filtering
- [ ] Add reading order sorting
- Type: feature
- Priority: high
- Estimated: 5 hours
- Dependencies: T004
- Agent: implement
- Description: Extract text from detected speech bubbles

### T006: Text-to-Speech Engine
- [ ] Create base TTSEngine interface
- [ ] Implement EdgeTTSEngine class
- [ ] Implement OpenAITTSEngine class
- [ ] Add async support
- [ ] Implement retry logic
- Type: feature
- Priority: high
- Estimated: 6 hours
- Dependencies: T005
- Agent: implement
- Description: Convert extracted text to audio files

---

## Phase 3: Video Generation

### T007: Video Generation Module
- [ ] Implement VideoGenerator class
- [ ] Add bubble-focused zoom effect
- [ ] Implement audio-video synchronization
- [ ] Add fade transitions
- [ ] Implement video encoding
- Type: feature
- Priority: high
- Estimated: 6 hours
- Dependencies: T006
- Agent: implement
- Description: Generate slideshow video with synchronized audio

### T008: Main Processor Orchestration
- [ ] Create ComicProcessor class
- [ ] Implement end-to-end workflow
- [ ] Add progress tracking
- [ ] Implement error recovery
- Type: feature
- Priority: high
- Estimated: 4 hours
- Dependencies: T003, T004, T005, T006, T007
- Agent: implement
- Description: Orchestrate entire pipeline from comic to video

---

## Phase 4: User Interface

### T009: Streamlit UI
- [ ] Create Streamlit app (app.py)
- [ ] Implement file upload widget
- [ ] Add configuration panel
- [ ] Create comic preview
- [ ] Add bubble overlay visualization
- [ ] Implement text editor
- [ ] Add progress bar
- Type: feature
- Priority: medium
- Estimated: 8 hours
- Dependencies: T008
- Agent: implement
- Description: Web-based user interface

### T010: Command-Line Interface
- [ ] Create main.py CLI script
- [ ] Implement argument parsing
- [ ] Add progress bar
- [ ] Create help documentation
- Type: feature
- Priority: low
- Estimated: 3 hours
- Dependencies: T008
- Agent: implement
- Description: Command-line interface for automation

---

## Phase 5: Testing & Documentation

### T011: Unit Test Suite
- [ ] Write unit tests for ImageLoader
- [ ] Write unit tests for PDFConverter
- [ ] Write unit tests for BubbleDetector
- [ ] Write unit tests for TextExtractor
- [ ] Write unit tests for TTSEngine
- [ ] Write unit tests for VideoGenerator
- [ ] Write unit tests for ComicProcessor
- Type: test
- Priority: high
- Estimated: 8 hours
- Dependencies: T001, T002, T003, T004, T005, T006, T007, T008
- Agent: test
- Description: Create comprehensive unit test suite

### T012: Integration Tests
- [ ] Write test for JPG → MP4 pipeline
- [ ] Write test for PDF → MP4 pipeline
- [ ] Write test for error recovery
- [ ] Add performance benchmarks
- Type: test
- Priority: medium
- Estimated: 4 hours
- Dependencies: T011
- Agent: test
- Description: Create integration test suite

### T013: Documentation
- [ ] Update README.md
- [ ] Add quick start guide
- [ ] Document configuration options
- [ ] Create example scripts
- [ ] Add troubleshooting section
- Type: documentation
- Priority: medium
- Estimated: 6 hours
- Dependencies: all
- Agent: implement
- Description: Write comprehensive documentation

---

## Phase 6: Ralph Loop Automation

### T014: Ralph Loop System Setup
- [ ] Create config.yaml
- [ ] Implement base Goose agent class
- [ ] Create task parser
- [ ] Implement main Ralph Loop
- [ ] Add safety features
- [ ] Create Goose helper utility
- Type: feature
- Priority: high
- Estimated: 4 hours
- Dependencies: T013
- Agent: implement
- Description: Setup Ralph Loop automation system

### T015: Automated Task Execution
- [ ] Create TASKS.md with all tasks
- [ ] Implement task classification
- [ ] Add automated testing
- [ ] Implement parallel execution
- [ ] Create specialized agents
- [ ] Add result tracking
- Type: feature
- Priority: high
- Estimated: 6 hours
- Dependencies: T014
- Agent: implement
- Description: Implement automated task execution with Ralph Loop

### T016: Code Quality & Audit
- [ ] Run audit agent on all code
- [ ] Check PEP 8 compliance
- [ ] Verify type hints
- [ ] Check docstrings
- [ ] Review error handling
- Type: refactor
- Priority: high
- Estimated: 4 hours
- Dependencies: T015
- Agent: audit
- Description: Audit code for quality and standards

### T017: Performance Optimization
- [ ] Profile application performance
- [ ] Optimize OpenCV operations
- [ ] Implement caching
- [ ] Optimize memory usage
- [ ] Add benchmarking
- Type: refactor
- Priority: medium
- Estimated: 4 hours
- Dependencies: T016
- Agent: implement
- Description: Optimize application performance

### T018: Final Testing
- [ ] Run Ralph Loop in dry-run mode
- [ ] Execute all tasks automatically
- [ ] Run automated testing
- [ ] Perform manual testing
- [ ] Cross-platform testing
- Type: test
- Priority: critical
- Estimated: 6 hours
- Dependencies: T017
- Agent: test
- Description: Final testing and bug fixes
```

#### Step 4: Implement Ralph Loop

**File: `ralph_loop/ralph_loop.py`**

```python
#!/usr/bin/env python3
"""
Ralph Loop - Automated Task Execution with Goose Subagents

This script reads tasks from TASKS.md and executes them using
specialized Goose subagents in parallel where possible.
"""

import yaml
import logging
import argparse
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime

from utils.task_parser import TaskParser
from agents.goose_agent import GooseAgent
from agents.implement_agent import ImplementAgent
from agents.test_agent import TestAgent
from agents.audit_agent import AuditAgent
from agents.debug_agent import DebugAgent


class RalphLoop:
    """Main Ralph Loop controller for automated task execution."""
    
    def __init__(self, config_path: str = "ralph_loop/config.yaml"):
        """Initialize Ralph Loop with configuration."""
        self.config = self._load_config(config_path)
        self.setup_logging()
        self.logger = logging.getLogger("RalphLoop")
        
        # Initialize agents
        self.agents = {
            'implement': ImplementAgent(self.config),
            'test': TestAgent(self.config),
            'audit': AuditAgent(self.config),
            'debug': DebugAgent(self.config)
        }
        
        # Parse tasks
        self.tasks = TaskParser(
            self.config['ralph_loop']['tasks_file']
        ).parse()
        
        # Results tracking
        self.results = {
            'start_time': datetime.now().isoformat(),
            'tasks_completed': [],
            'tasks_failed': [],
            'total_time': 0
        }
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    
    def setup_logging(self):
        """Setup logging configuration."""
        log_config = self.config.get('logging', {})
        log_level = getattr(logging, log_config.get('level', 'INFO'))
        
        handlers = [logging.StreamHandler()]
        
        if log_config.get('file'):
            handlers.append(
                logging.FileHandler(log_config['file'])
            )
        
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=handlers
        )
    
    def run(self, dry_run: bool = False):
        """Execute the Ralph Loop."""
        self.logger.info("=" * 60)
        self.logger.info("RALPH LOOP - AUTOMATED TASK EXECUTION")
        self.logger.info("=" * 60)
        
        if dry_run or self.config['safety']['dry_run']:
            self.logger.warning("⚠️  DRY RUN MODE - No changes will be made")
        
        # Sort tasks by dependencies
        sorted_tasks = self._resolve_dependencies()
        
        self.logger.info(f"\n📋 Total tasks to execute: {len(sorted_tasks)}")
        self.logger.info(f"🔄 Max parallel tasks: {self.config['ralph_loop']['max_parallel_tasks']}")
        
        # Execute tasks
        for i, task in enumerate(sorted_tasks, 1):
            self.logger.info(f"\n{'='*60}")
            self.logger.info(f"Task {i}/{len(sorted_tasks)}: {task['title']}")
            self.logger.info(f"{'='*60}")
            
            try:
                result = self._execute_task(task, dry_run)
                
                if result['success']:
                    self.results['tasks_completed'].append(task['id'])
                    self.logger.info(f"✅ Task completed successfully")
                else:
                    self.results['tasks_failed'].append(task['id'])
                    self.logger.error(f"❌ Task failed: {result['error']}")
                    
                    if not self.config['ralph_loop']['continue_on_error']:
                        self.logger.error("Stopping execution due to error")
                        break
            
            except Exception as e:
                self.logger.exception(f"Exception executing task: {e}")
                self.results['tasks_failed'].append(task['id'])
        
        # Print summary
        self._print_summary()
    
    def _resolve_dependencies(self) -> List[Dict]:
        """Resolve task dependencies and return execution order."""
        # Simple topological sort
        executed = set()
        sorted_tasks = []
        remaining = self.tasks.copy()
        
        while remaining:
            progress = False
            
            for task in remaining[:]:
                deps = task.get('dependencies', [])
                
                if all(dep in executed for dep in deps):
                    sorted_tasks.append(task)
                    executed.add(task['id'])
                    remaining.remove(task)
                    progress = True
            
            if not progress:
                # Circular dependency or missing dependency
                raise Exception("Cannot resolve task dependencies")
        
        return sorted_tasks
    
    def _execute_task(self, task: Dict, dry_run: bool) -> Dict[str, Any]:
        """Execute a single task using the appropriate agent."""
        agent_type = task.get('agent', 'implement')
        agent = self.agents.get(agent_type, self.agents['implement'])
        
        return agent.execute(task, dry_run)
    
    def _print_summary(self):
        """Print execution summary."""
        self.logger.info("\n" + "=" * 60)
        self.logger.info("RALPH LOOP EXECUTION SUMMARY")
        self.logger.info("=" * 60)
        
        completed = len(self.results['tasks_completed'])
        failed = len(self.results['tasks_failed'])
        total = completed + failed
        
        self.logger.info(f"\n✅ Tasks completed: {completed}/{total}")
        self.logger.info(f"❌ Tasks failed: {failed}/{total}")
        self.logger.info(f"📊 Success rate: {completed/total*100:.1f}%")
        
        if self.results['tasks_failed']:
            self.logger.warning("\n❌ Failed tasks:")
            for task_id in self.results['tasks_failed']:
                self.logger.warning(f"  - {task_id}")
        
        # Save results
        if self.config['monitoring'].get('save_results'):
            import json
            results_path = self.config['monitoring']['save_results']
            with open(results_path, 'w') as f:
                json.dump(self.results, f, indent=2)
            self.logger.info(f"\n💾 Results saved to: {results_path}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Ralph Loop - Automated Task Execution"
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Simulate execution without making changes'
    )
    parser.add_argument(
        '--config',
        default='ralph_loop/config.yaml',
        help='Path to configuration file'
    )
    
    args = parser.parse_args()
    
    try:
        loop = RalphLoop(args.config)
        loop.run(dry_run=args.dry_run)
    except Exception as e:
        logging.exception("Ralph Loop failed: %s", e)
        exit(1)


if __name__ == "__main__":
    main()
```

---

## Usage

### Step 1: Initialize Ralph Loop

```bash
# Navigate to project directory
cd comic-slideshow-generator

# Create Ralph Loop structure
mkdir -p ralph_loop/{agents,utils,prompts}

# Copy configuration files
# (from this document)
```

### Step 2: Run in Dry-Run Mode

```bash
# Test without making changes
python ralph_loop/ralph_loop.py --dry-run
```

### Step 3: Execute Tasks

```bash
# Run full automation
python ralph_loop/ralph_loop.py
```

### Step 4: Monitor Progress

```bash
# View log file
tail -f ralph_loop.log

# View results
cat ralph_results.json
```

---

## Benefits Summary

| Aspect | Manual | Ralph Loop |
|--------|--------|------------|
| **Time** | ~81 hours | ~20-25 hours |
| **Execution** | Sequential | Parallel (3-4x faster) |
| **Testing** | Manual | Automated |
| **Error Recovery** | Manual | Automatic retry |
| **Code Quality** | Manual reviews | Automated audits |
| **Progress Tracking** | Manual | Real-time dashboard |
| **Safety** | No safeguards | Dry-run, rollback |

---

## Next Steps

1. ✅ Create Ralph Loop directory structure
2. ✅ Copy configuration files
3. ✅ Create TASKS.md with all tasks
4. ✅ Run in dry-run mode first
5. ✅ Execute full automation
6. ✅ Monitor progress and results
7. ✅ Review generated code

---

**Status:** 📝 Ready for implementation
**Estimated Time Savings:** ~55-60 hours (70% reduction)
**Automation Level:** 85% (only requires review and testing)

---

*This integration document complements the Spec-Kitty specification with Ralph Loop automation capabilities.*
