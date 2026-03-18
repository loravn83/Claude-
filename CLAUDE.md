# CLAUDE.md

This file provides guidance for AI assistants (Claude and others) working with this repository.

## Repository Status

This repository is currently in its initial state with no source code committed yet. This document will be updated as the project evolves.

## Project Overview

<!-- Update this section as the project takes shape -->
- **Purpose**: TBD
- **Language/Runtime**: TBD
- **Framework**: TBD

## Repository Structure

```
Claude-/
└── CLAUDE.md       # This file — AI assistant guidance
```

<!-- Update the directory tree as files are added. Example:
Claude-/
├── src/            # Application source code
├── tests/          # Test files
├── docs/           # Documentation
├── package.json    # Project metadata and scripts
└── CLAUDE.md       # This file
-->

## Development Setup

<!-- Fill in once the project is initialized. Example steps:
1. Install dependencies: `npm install` / `pip install -r requirements.txt`
2. Copy environment config: `cp .env.example .env`
3. Start development server: `npm run dev`
-->

TBD — no setup steps defined yet.

## Common Commands

<!-- Fill in once scripts/tasks are defined. Examples:
| Command            | Description              |
|--------------------|--------------------------|
| `npm run dev`      | Start dev server         |
| `npm test`         | Run test suite           |
| `npm run build`    | Build for production     |
| `npm run lint`     | Lint source files        |
-->

TBD

## Development Workflow

### Branching Convention

- Feature branches: `feature/<short-description>`
- Bug fix branches: `fix/<short-description>`
- Claude-managed branches: `claude/<task-description>-<id>`
- Main branch: `main` (protected — do not push directly)

### Commit Messages

Write concise, imperative commit messages:
```
Add user authentication module
Fix null pointer in payment handler
Update README with setup instructions
```

### Pull Requests

- Keep PRs focused on a single concern
- Include a short description of what changed and why
- Ensure all tests pass before requesting review

## Code Conventions

<!-- Update these once the language/framework is decided. -->

### General

- Prefer clarity over cleverness
- Keep functions small and single-purpose
- Write self-documenting code; add comments only where the logic is non-obvious
- Delete dead code rather than commenting it out

### Naming

- Use descriptive names for variables, functions, and files
- Follow the naming conventions of the chosen language (e.g., `camelCase` for JS/TS, `snake_case` for Python)

## Testing

<!-- Update once a test framework is chosen. -->

- Write tests for new features and bug fixes
- Tests live alongside or near the code they test
- Aim for meaningful coverage, not 100% line coverage

## AI Assistant Guidelines

When working in this repository:

1. **Read before editing** — always read a file before modifying it
2. **Minimal changes** — make only the changes needed to fulfil the task; avoid unrelated refactors or cleanup
3. **No speculative features** — do not add code for hypothetical future requirements
4. **Security first** — never introduce SQL injection, XSS, command injection, or other OWASP Top 10 vulnerabilities
5. **Commit and push** — after completing a task, commit with a clear message and push to the designated branch
6. **Update this file** — whenever the project structure, tooling, or conventions change, update CLAUDE.md to reflect reality

## Notes for Future Updates

When the project is initialized, update this file to include:

- Actual directory structure
- Real setup and run commands
- Language/framework-specific conventions
- Testing framework and how to run tests
- Environment variable requirements
- Deployment process
- Links to external documentation
