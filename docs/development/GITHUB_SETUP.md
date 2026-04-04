# GitHub Setup & Workflow Guide

## Prerequisites

Before starting, you'll need:
1. GitHub account (https://github.com)
2. Git installed locally (https://git-scm.com)
3. VS Code or preferred editor

---

## Step 1: Create GitHub Repository

### 1.1 Create New Repository on GitHub

1. Go to https://github.com/new
2. **Repository name:** `sulfate-methos` (or your preferred name)
3. **Description:** "USGS AMD/Iron Sulfate Detection Tool - Multi-sensor satellite analysis"
4. **Visibility:** Public (for collaboration) or Private (for security)
5. **Initialize with:**
   - ✅ Add a README file
   - ✅ Add .gitignore (select "Python" template)
   - ✅ Add a license (MIT recommended)

6. Click **Create repository**

### 1.2 Copy Repository URL

On your new repo page, click **Code** button and copy the HTTPS URL:
```
https://github.com/YOUR_USERNAME/sulfate-methos.git
```

---

## Step 2: Local Git Setup

### 2.1 Configure Git (First Time Only)

```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

### 2.2 Clone Repository

Navigate to your project directory and clone:

```bash
cd "OneDrive - Kent State University\Documents\Windsurf-Projects"
git clone https://github.com/YOUR_USERNAME/sulfate-methos.git
cd sulfate-methos
```

### 2.3 Verify Connection

```bash
git remote -v
```

Should show:
```
origin  https://github.com/YOUR_USERNAME/sulfate-methos.git (fetch)
origin  https://github.com/YOUR_USERNAME/sulfate-methos.git (push)
```

---

## Step 3: Create Project Structure

### 3.1 Create Folders

```bash
mkdir -p docs earth-engine python/amd_detection python/tests config web
```

### 3.2 Create Initial Files

```bash
# Create documentation files
touch docs/ARCHITECTURE.md
touch docs/API_REFERENCE.md
touch CHANGELOG.md

# Create config files
touch config/study_areas.json
touch config/thresholds.json
touch config/band_config.json

# Create Python files
touch python/requirements.txt
touch python/amd_detection/__init__.py
touch python/amd_detection/processor.py
touch python/amd_detection/indices.py
touch python/amd_detection/classification.py
touch python/amd_detection/visualization.py
touch python/tests/__init__.py
touch python/tests/test_indices.py

# Create GEE files
touch earth-engine/amd_detection_v1.0.0.js
touch earth-engine/amd_detection_dev.js
```

---

## Step 4: Create .gitignore

Create `.gitignore` file in root:

```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Jupyter Notebook
.ipynb_checkpoints
*.ipynb

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Project specific
*.log
.env
config/local.json
results/
temp/
cache/

# Credentials (NEVER commit these!)
credentials.json
*.pem
*.key
.env.local
```

---

## Step 5: Initial Commit

### 5.1 Stage Files

```bash
git add .
```

### 5.2 Create Initial Commit

```bash
git commit -m "chore: Initialize project structure with documentation"
```

### 5.3 Push to GitHub

```bash
git push -u origin main
```

---

## Step 6: Branch Strategy

### 6.1 Create Development Branch

```bash
git checkout -b develop
git push -u origin develop
```

### 6.2 Set Branch Protection Rules (On GitHub)

1. Go to repository **Settings** → **Branches**
2. Click **Add rule** under "Branch protection rules"
3. **Branch name pattern:** `main`
4. Enable:
   - ✅ Require pull request reviews before merging
   - ✅ Require status checks to pass before merging
   - ✅ Require branches to be up to date before merging
   - ✅ Dismiss stale pull request approvals when new commits are pushed

5. Click **Create**

Repeat for `develop` branch with slightly less strict rules.

---

## Step 7: Workflow for Making Changes

### 7.1 Create Feature Branch

```bash
git checkout develop
git pull origin develop
git checkout -b feature/your-feature-name
```

**Branch naming convention:**
- `feature/` - New features
- `bugfix/` - Bug fixes
- `docs/` - Documentation
- `refactor/` - Code refactoring
- `test/` - Tests

### 7.2 Make Changes

Edit files as needed.

### 7.3 Stage & Commit

```bash
git add .
git commit -m "feat: Add new spectral index calculation

- Implemented ferric iron index
- Added unit tests
- Updated documentation

Fixes: #123"
```

**Commit message format:**
```
[TYPE] Brief description (50 chars max)

Detailed explanation (72 chars per line)
- Bullet points for changes
- Reference issues with #123

Fixes: #123
Related: #456
```

### 7.4 Push to GitHub

```bash
git push origin feature/your-feature-name
```

### 7.5 Create Pull Request

1. Go to GitHub repository
2. Click **Pull requests** tab
3. Click **New pull request**
4. **Base:** `develop` | **Compare:** `feature/your-feature-name`
5. Fill in PR template:

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests added
- [ ] Manual testing completed
- [ ] No new warnings generated

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex logic
- [ ] Documentation updated
- [ ] No new warnings
```

6. Click **Create pull request**

### 7.6 Code Review & Merge

1. Wait for review (if team project)
2. Address any comments
3. Once approved, click **Squash and merge** or **Create a merge commit**
4. Delete branch after merge

---

## Step 8: Versioning & Releases

### 8.1 Semantic Versioning

Format: `MAJOR.MINOR.PATCH`

- **MAJOR** (1.0.0): Breaking changes
- **MINOR** (1.1.0): New features (backward compatible)
- **PATCH** (1.0.1): Bug fixes

### 8.2 Create Release

When ready to release (e.g., v1.0.0):

```bash
git checkout main
git pull origin main
git tag -a v1.0.0 -m "Release version 1.0.0: Initial production release"
git push origin v1.0.0
```

### 8.3 Create GitHub Release

1. Go to **Releases** tab
2. Click **Draft a new release**
3. **Tag version:** `v1.0.0`
4. **Release title:** `Version 1.0.0 - Initial Release`
5. **Description:**

```markdown
## Features
- Multi-sensor support (Landsat 8, 9, Sentinel-2)
- 19-class Boolean classification
- Contaminated water detection
- Real-time statistics

## Bug Fixes
- Fixed negative reflectance values
- Improved water masking

## Breaking Changes
None

## Installation
Copy `earth-engine/amd_detection_v1.0.0.js` to Earth Engine Code Editor

## Documentation
See README.md and docs/ folder
```

6. Click **Publish release**

---

## Step 9: Updating CHANGELOG.md

Keep this updated with each release:

```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-11-15

### Added
- Multi-sensor support (Landsat 8, 9, Sentinel-2)
- 19-class Boolean classification system
- Contaminated water detection
- Real-time statistics panel
- Interactive map visualization
- Paper validation sites (Goldfield, Bauer Mill, Silverton, Marysvale)

### Fixed
- Fixed negative reflectance values with .clamp(0.0, 1.0)
- Improved water masking with MNDWI + AWEInsh
- Corrected Landsat Collection 2 scaling formula

### Changed
- Updated documentation structure
- Improved code comments and documentation

## [0.9.0] - 2025-11-10

### Added
- Initial project setup
- Core algorithm implementation
- Basic documentation

[1.0.0]: https://github.com/YOUR_USERNAME/sulfate-methos/releases/tag/v1.0.0
[0.9.0]: https://github.com/YOUR_USERNAME/sulfate-methos/releases/tag/v0.9.0
```

---

## Step 10: Common Git Commands

### Daily Workflow

```bash
# Check status
git status

# See recent commits
git log --oneline -10

# See changes before committing
git diff

# Undo last commit (keep changes)
git reset --soft HEAD~1

# Undo last commit (discard changes)
git reset --hard HEAD~1

# Switch branches
git checkout branch-name

# Pull latest changes
git pull origin develop

# Push changes
git push origin feature-name
```

### Troubleshooting

```bash
# Merge conflicts
git status  # See conflicts
# Edit files to resolve
git add .
git commit -m "Resolve merge conflicts"

# Accidentally committed to main
git reset --soft HEAD~1
git checkout -b feature/new-branch
git commit -m "feat: description"

# Need to update branch with latest develop
git fetch origin
git rebase origin/develop
git push origin feature-name --force-with-lease
```

---

## Step 11: Continuous Integration (Optional)

### 11.1 Add GitHub Actions Workflow

Create `.github/workflows/tests.yml`:

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.9
    
    - name: Install dependencies
      run: |
        pip install -r python/requirements.txt
        pip install pytest pytest-cov
    
    - name: Run tests
      run: |
        pytest python/tests/ -v --cov=python/amd_detection
```

---

## Your GitHub Info

**Please provide:**

```
GitHub Username: [YOUR_USERNAME]
GitHub Email: [YOUR_EMAIL]
Repository Name: sulfate-methos (or preferred)
Visibility: Public / Private
```

Once you provide this, I can help you:
1. Create the initial commit
2. Set up branch protection rules
3. Create the first release
4. Configure CI/CD pipeline

---

## Next Steps

1. Create GitHub account (if needed)
2. Provide your GitHub username
3. Run through Steps 1-5 above
4. Confirm repository is created
5. I'll help with initial commits and structure
