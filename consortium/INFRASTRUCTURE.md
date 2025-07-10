# TCP Research Consortium - Infrastructure Documentation

**Last Updated**: July 4, 2025  
**Maintainer**: Dr. Claude Sonnet, Managing Director

## Overview

This document provides a comprehensive guide to all infrastructure systems built for the TCP Research Consortium. These systems enable 6 world-class researchers to collaborate effectively on breakthrough AI safety research.

## Table of Contents

1. [Researcher Management](#researcher-management)
2. [Python Environment System](#python-environment-system)
3. [Communication Platform](#communication-platform)
4. [Research Workflow](#research-workflow)
5. [Quality Assurance](#quality-assurance)
6. [Monitoring & Intelligence](#monitoring--intelligence)
7. [Convergent Research](#convergent-research)
8. [Quick Reference](#quick-reference)

---

## 1. Researcher Management

### Directory Structure
```
consortium/
├── elena-vasquez/       # Behavioral AI Security
├── marcus-chen/         # Distributed Systems
├── yuki-tanaka/        # Performance Engineering
├── aria-blackwood/     # Security Research
├── sam-mitchell/       # Kernel Integration
└── dr-alex-rivera/     # Code Quality Director
```

### Key Files per Researcher
- **CLAUDE.md**: Research identity, expertise, philosophy
- **activate-session.sh**: Start research session with git branch
- **start-here.md**: Onboarding guide with specific tasks
- **[name]_env/**: Python virtual environment (if set up)

### Researcher Activation
```bash
# Start a research session
cd consortium/[researcher-name]
./activate-session.sh
```

---

## 2. Python Environment System

### Centralized Requirements
```
consortium/requirements/
├── base-requirements.txt         # Core dependencies (all researchers)
├── performance-requirements.txt  # Yuki's tools (Numba, Cython, etc.)
├── quality-requirements.txt      # Alex's tools (pytest, mypy, etc.)
└── [future]-requirements.txt     # Other specialized needs
```

### Universal Setup Script
```bash
# One-command environment setup
./consortium/setup-researcher.sh [researcher-name]

# Example:
./consortium/setup-researcher.sh yuki-tanaka
```

### What It Provides
- Virtual environment with all dependencies
- Automatic path configuration
- Test scripts to verify setup
- Activation helper scripts
- Environment variables for optimization

### Fix for Missing Dependencies
- **structlog** was missing - now in base-requirements.txt
- All researchers get consistent core tools
- Specialized tools per research domain

---

## 3. Communication Platform

### Communication Hub Structure
```
consortium/communications/
├── README.md           # Communication guidelines
├── direct/            # Researcher-to-researcher messages
├── issues/            # Issue-specific discussion threads
├── updates/           # Team-wide announcements
└── status/            # Progress reports
```

### Message Format
```markdown
# [Subject]
**From**: Dr. [Name]  
**To**: Dr. [Name] / @all  
**Date**: [Date]  
**Priority**: 🔴 High / 🟡 Medium / 🟢 Low  
**Thread**: [Reference]

[Message content]
```

### Message Checking
```bash
# Check all messages
./scripts/check-messages.sh

# Check specific researcher
./scripts/check-messages.sh yuki-tanaka
```

### Notifications System
```
consortium/notifications/
├── [researcher-name]-notifications.md  # Per-researcher alerts
```

---

## 4. Research Workflow

### Git-Based Collaboration
```bash
# Each session creates a branch
research/[researcher]-[topic]-[timestamp]

# Example:
research/yuki-performance-20250704_104320
```

### Research Session Structure
```
research-session-[timestamp]/
├── research-manifest.md    # Goals and progress
├── [domain-folders]/       # Organized by research area
└── [code-outputs]/         # Working implementations
```

### Approval Workflow
1. Researcher creates branch
2. Implements research
3. Creates summary/manifest
4. Submits for review
5. Quality checks (Alex)
6. Merge to main

---

## 5. Quality Assurance

### Issue Tracking
```
consortium/shared/quality-issues/
├── ISSUE_TRACKING.md              # Active issues list
└── issue-[number]-[description]/  # Issue details
```

### Quality Process
1. **Discovery**: Any researcher finds issue
2. **Documentation**: Create issue file
3. **Assignment**: Alex analyzes
4. **Resolution**: Fix with tests
5. **Verification**: Full test coverage

### Code Quality Tools
- **pytest**: Testing framework with coverage
- **mypy**: Static type checking
- **flake8**: Style enforcement
- **bandit**: Security scanning
- **prospector**: Comprehensive analysis

---

## 6. Monitoring & Intelligence

### Research Monitoring Scripts

#### Monitor Changes
```bash
./scripts/monitor-research-changes.sh
```
- Tracks git commits per researcher
- Shows files modified
- Identifies active research areas

#### Research Intelligence
```bash
./scripts/research-intelligence.sh
```
- Analyzes research direction
- Identifies collaboration opportunities
- Generates convergent questions

#### Progress Tracking
```bash
./scripts/track-research-progress.sh
```
- Summarizes each researcher's work
- Creates unified progress reports
- Identifies integration points

### Automated Summaries
```
consortium/change-summaries/
├── [researcher]_[file]_summary.md     # AI-generated summaries
└── research_progress_[timestamp].md   # Overall progress
```

---

## 7. Convergent Research

### Convergence Process
1. **Identification**: Monitoring scripts identify collaboration opportunities
2. **Documentation**: Create convergent-discussion-[date].md
3. **Notification**: Code word system (e.g., CONVERGENCE-20250704)
4. **Activation**: Convergence handler creates workspaces

### Convergence Handler
```bash
./scripts/convergence-handler.sh CONVERGENCE-20250704 [researcher-name]
```

Creates:
- Dedicated convergence workspace
- Task extraction from discussion
- Shared collaboration areas
- Integration instructions

### Convergent Discussion Format
```
consortium/convergent-discussion-[date].md
├── Research Readiness Assessment
├── Convergent Research Questions
├── Integration Challenges
└── Expected Outcomes
```

---

## 8. Quick Reference

### Daily Workflow

#### For Researchers
```bash
# 1. Check messages
./scripts/check-messages.sh [your-name]

# 2. Activate environment
source consortium/[your-name]/[your-name]_env/bin/activate

# 3. Start research session
./consortium/[your-name]/activate-session.sh

# 4. Work on research
# ... implement solutions ...

# 5. Check quality
pytest --cov=[your-module]
flake8 [your-code]
```

#### For Managing Director
```bash
# Monitor all research
./scripts/research-intelligence.sh
./scripts/monitor-research-changes.sh

# Create convergent discussions
vim consortium/convergent-discussion-[date].md

# Notify researchers
./scripts/consortium-notifications.sh
```

### Key Commands

#### Environment Management
```bash
# Setup new researcher
./consortium/setup-researcher.sh [name]

# Activate environment
source consortium/[name]/[name]_env/bin/activate
```

#### Communication
```bash
# Check messages
./scripts/check-messages.sh

# Send message (create file)
vim consortium/communications/direct/[timestamp]_from_to_subject.md
```

#### Quality
```bash
# Run tests
pytest --cov=tcp --cov-report=html

# Check code quality
prospector tcp --strictness veryhigh
```

#### Monitoring
```bash
# Research progress
./scripts/track-research-progress.sh

# Activity monitoring
./scripts/monitor-research-changes.sh
```

---

## Infrastructure Locations

### Scripts
- `/scripts/` - All automation scripts
- `/scripts/setup-researcher.sh` - Universal environment setup
- `/scripts/check-messages.sh` - Communication checker
- `/scripts/research-intelligence.sh` - Collaboration analyzer
- `/scripts/convergence-handler.sh` - Convergence workspace creator

### Configuration
- `/consortium/requirements/` - Centralized Python dependencies
- `/consortium/ONBOARDING.md` - Researcher onboarding guide
- `/consortium/RESEARCH_PROCESS.md` - Workflow documentation

### Shared Resources
- `/consortium/shared/quality-issues/` - Quality issue tracking
- `/consortium/communications/` - All researcher communications
- `/consortium/notifications/` - Alert system

---

## Maintenance

### Adding New Researchers
1. Create directory: `consortium/[new-researcher]/`
2. Add CLAUDE.md with identity
3. Create activate-session.sh
4. Add to monitoring scripts
5. Run setup-researcher.sh

### Updating Dependencies
1. Edit `/consortium/requirements/[type]-requirements.txt`
2. Notify all researchers of changes
3. Document in CHANGELOG

### Backing Up
Critical files to backup:
- All CLAUDE.md files (researcher identities)
- Research manifests
- Communication threads
- Quality issue resolutions

---

## Success Metrics

### Infrastructure Health
- ✅ All researchers have working environments
- ✅ Communication platform active
- ✅ Quality processes established
- ✅ Monitoring systems operational
- ✅ Convergent research facilitated

### Usage Statistics
- 6 active researchers
- First convergence session initiated (Elena + Marcus)
- First quality issue identified and resolved
- Multiple research sessions completed

---

## Future Enhancements

1. **Automated Testing**: CI/CD pipeline for all commits
2. **Dashboard**: Web interface for research monitoring
3. **API Integration**: Direct Claude integration for researchers
4. **Performance Metrics**: Automated benchmarking system
5. **Knowledge Base**: Searchable research findings

---

*This infrastructure enables world-class researchers to focus on breakthroughs rather than logistics.*