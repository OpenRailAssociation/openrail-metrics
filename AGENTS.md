# Agent Instructions

## Working with this codebase

When working on this project, follow these guidelines:

1. **Never commit automatically** - Always wait for explicit instruction to commit changes
2. **Check lessons learned** - Review `tasks/lessons.md` before making design decisions
3. **Write tests first** - For new commands or features, add unit tests instead of manual testing
4. **Be concise** - Keep commit messages short and focused

## Specifications

Specifications for work to be done are kept at `specs`. The contain requirements specified by the user.

## Todos

There is a file with todos in `tasks/TODO.md`. This is used to note down todos while working on something else. It's input for you. When you complete a todo, remove it from the TODO.md file and make sure this change is included in the commit which fixes the todo.

## Testing approach

- Use unit tests in `tests/` directory
- Use pytest with Click's CliRunner for CLI command testing

## Documentation

- Update `docs/architecture.md` for fundamental design decisions
- Update `tasks/lessons.md` when corrected on design or implementation choices
