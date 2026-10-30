# GitHub Setup

## Initialize the repository
```bash
git init
git add .
git commit -m "Initial FinGuard project scaffold"
```

## Create a remote repository
1. Create a new GitHub repository named `finguard-fraud-risk-analytics`.
2. Push the branch to the remote.

```bash
git remote add origin https://github.com/<username>/finguard-fraud-risk-analytics.git
git branch -M main
git push -u origin main
```

## Recommended contents for the repository
- README with actual instructions
- Source code and SQL scripts
- Data directory placeholders
- Tests and documentation
- No raw dataset or `.env` files committed to GitHub
