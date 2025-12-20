# Git

# Git

**Git** is a free and open-source **distributed version control system (DVCS)** designed to handle everything from small to very large projects with speed and efficiency. It is the most widely used version control tool in modern software development.

## History
- Created by **Linus Torvalds** in **2005** to manage the development of the Linux kernel.  
- Designed to be fast, distributed, and secure.  
- Currently maintained by **Junio Hamano** and a large community of contributors.  

## Key Features
- **Distributed system:** Every developer has a full copy of the repository, including history.  
- **Branching and merging:** Lightweight branches allow flexible workflows and experimentation.  
- **Speed and efficiency:** Optimized for performance even with large codebases.  
- **Data integrity:** Uses cryptographic hashing (SHA-1, now SHA-256) to ensure history cannot be altered unnoticed.  
- **Collaboration:** Supports multiple workflows (centralized, feature branching, forking).  
- **Staging area:** Allows fine-grained control over commits.  

## Basic Workflow
1. **Initialize repository:** `git init`  
2. **Add files:** `git add filename`  
3. **Commit changes:** `git commit -m "message"`  
4. **Branching:** `git branch new-feature`  
5. **Merging:** `git merge new-feature`  
6. **Remote collaboration:** `git push` and `git pull`  

## Example
```bash
# Create a new repository
git init

# Add a file
git add hello.py

# Commit changes
git commit -m "Add hello world script"

# Create and switch to a new branch
git checkout -b feature-branch