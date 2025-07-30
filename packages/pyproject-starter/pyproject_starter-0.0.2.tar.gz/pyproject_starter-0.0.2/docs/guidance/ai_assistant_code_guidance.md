# AI Assistant Code Guidance

This document provides best practices and actionable guidance for using AI assistants in code development, review, and automation workflows.

## Principles
- Use clear, information-dense keywords for tasks (e.g., ADD, CREATE, MODIFY, EXECUTE, PRESERVE).
- Ensure every code change is traceable and documented.
- Integrate unit tests for all new and modified code.
- Validate code quality with automated tools (lint, type-check, format).
- Use AI assistant suggestions to accelerate, but always review for correctness and maintainability.

## Workflow
1. Define tasks using information-dense language.
2. Use the AI assistant to generate, refactor, or review code.
3. Run tests and quality checks after each change.
4. Document decisions and changes in the codebase and project history.

## Example Task List
```yaml
Task 1:
STATUS [ ]
CREATE src/new_feature.py:
  - MIRROR pattern from: src/existing_feature.py
  - MODIFY logic for new requirements
  - PRESERVE error handling and test coverage
```

## Review Checklist
- [ ] Code is clear and maintainable
- [ ] All changes are tested
- [ ] Documentation is updated
- [ ] AI suggestions are validated
