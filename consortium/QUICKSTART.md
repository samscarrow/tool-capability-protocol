# TCP Research Consortium - Quick Start Guide

**For**: New and existing consortium members  
**Purpose**: Get up and running in 5 minutes

## 🚀 For New Researchers

### Step 1: Find Your Identity
```bash
cat /Users/sam/dev/ai-ml/experiments/tool-capability-protocol/consortium/[your-name]/CLAUDE.md
```
This defines who you are in the consortium.

### Step 2: Set Up Your Environment (One Command!)
```bash
/Users/sam/dev/ai-ml/experiments/tool-capability-protocol/consortium/setup-researcher.sh [your-name]
```

### Step 3: Activate and Start
```bash
# Activate Python environment
source /Users/sam/dev/ai-ml/experiments/tool-capability-protocol/consortium/[your-name]/[your-name]_env/bin/activate

# Start research session
/Users/sam/dev/ai-ml/experiments/tool-capability-protocol/consortium/[your-name]/activate-session.sh
```

### Step 4: Check for Messages
```bash
/Users/sam/dev/ai-ml/experiments/tool-capability-protocol/scripts/check-messages.sh [your-name]
```

## 📊 Daily Workflow

### Morning Routine
```bash
# 1. Check messages and notifications
./scripts/check-messages.sh [your-name]

# 2. Review research intelligence
./scripts/research-intelligence.sh

# 3. Start your session
./consortium/[your-name]/activate-session.sh
```

### During Research
```bash
# Test your code
pytest [your-module] --cov

# Check quality
flake8 [your-code]
mypy [your-code] --strict

# Commit with descriptive message
git add .
git commit -m "feat(domain): what you did and why"
```

### End of Day
```bash
# Update research manifest
vim research-session-*/research-manifest.md

# Check in with team
vim consortium/communications/status/[date]_[your-name]_status.md

# Push your branch
git push origin [your-branch]
```

## 🤝 Collaboration

### When You Need Help
```bash
# Send a message
vim consortium/communications/direct/[timestamp]_[you]_to_[them]_[subject].md

# Tag for urgent
Include "Priority: 🔴 High" in your message
```

### When You Find Issues
1. Document it: `vim consortium/shared/quality-issues/issue_[number]_[description].md`
2. Tag Alex Rivera: `@dr-alex-rivera`
3. Continue with workaround if possible

### Convergent Research
If you see code word like `CONVERGENCE-20250704`:
```bash
./scripts/convergence-handler.sh CONVERGENCE-20250704 [your-name]
```

## 🛠️ Common Tasks

### Install Missing Package
```bash
# Add to appropriate requirements file
echo "package-name>=version" >> consortium/requirements/base-requirements.txt

# Reinstall
pip install -r consortium/requirements/base-requirements.txt
```

### Run Quality Checks
```bash
# Comprehensive analysis
prospector [module] --strictness veryhigh

# Quick checks
pytest && flake8 && mypy [module]
```

### Find Other Researchers' Work
```bash
# See what others are doing
ls consortium/*/research-session-*/

# Check specific researcher
find consortium/[researcher-name] -name "*.py" -mtime -7
```

## 🔧 Troubleshooting

### "Module not found"
```bash
# Ensure environment is activated
which python  # Should show your venv path

# Reinstall requirements
pip install -r consortium/requirements/base-requirements.txt
pip install -r consortium/requirements/[your-specialty]-requirements.txt
```

### "Permission denied"
```bash
# Make scripts executable
chmod +x ./scripts/*.sh
chmod +x ./consortium/[your-name]/*.sh
```

### "Git merge conflicts"
```bash
# Always pull latest before starting
git checkout main
git pull origin main
git checkout -b research/[your-topic]-$(date +%Y%m%d_%H%M%S)
```

## 📞 Getting Help

### Technical Issues
- Check: `consortium/INFRASTRUCTURE.md`
- Message: Alex Rivera (code quality)

### Research Questions  
- Check: `scripts/research-intelligence.sh`
- Find collaborator with expertise

### Process Questions
- Check: `consortium/RESEARCH_PROCESS.md`
- Check: `consortium/ONBOARDING.md`

## 🎯 Remember

1. **Use absolute paths** - Never use `cd ../..`
2. **Activate environments** - Always work in your venv
3. **Test everything** - 90% coverage minimum
4. **Communicate** - Check messages daily
5. **Document** - Update manifests and status

---

**Your work matters. Every line of code brings us closer to safe AI.**

*Questions? Run `./scripts/check-messages.sh` and ask your colleagues!*