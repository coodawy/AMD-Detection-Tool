# Git Quick Reference Guide

## Basic Workflow

### Stage Changes
```bash
git add .                       # Stage all changes
git add <filename>             # Stage specific file
```

### Commit Changes
```bash
git commit -m "Your message"   # Commit with a message
```

### Push Changes
```bash
git push                       # Push to current branch
git push origin <branch>       # Push to specific branch
```

## Version Management

### Create a New Version
```bash
# After committing your changes
git tag -a v1.0.1 -m "Description of changes in this version"
git push --tags
```

### List All Versions
```bash
git tag -l
```

### Checkout a Specific Version
```bash
git checkout v1.0.0
```

## Branch Management

### Create and Switch to New Branch
```bash
git checkout -b feature/new-feature
```

### Switch Between Branches
```bash
git checkout main              # Switch to main branch
git checkout <branch-name>     # Switch to specific branch
```

### Merge Changes
```bash
git checkout main              # Switch to target branch
git merge <branch-name>        # Merge changes from another branch
```

## Common Issues

### Undo Local Changes
```bash
git restore <file>             # Discard changes in working directory
git restore --staged <file>    # Unstage a file
```

### View Status
```bash
git status                     # Show changed files
git log                        # View commit history
```

## GitHub Specific

### Clone Repository
```bash
git clone https://github.com/coodawy/AMD-Detection-Tool.git
```

### Update Local Repository
```bash
git pull origin main           # Pull latest changes from main branch
```

## Example Workflow

1. Make your changes
2. Stage changes: `git add .`
3. Commit changes: `git commit -m "Fix: Resolved negative values in water detection"`
4. Push to GitHub: `git push`
5. (For new version) Create tag: `git tag -a v1.0.1 -m "Fixed water detection algorithm"`
6. Push tags: `git push --tags`

---
*Remember to write clear, descriptive commit messages that explain what changed and why.*
