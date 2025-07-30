# Local Development Workflow: Pre-Commit Hooks

Audience: All Developers

Purpose: To explain the project's use of pre-commit hooks for automated quality checks.

## The First Line of Defense

To ensure code quality and a consistent style across all contributions, this project uses the `pre-commit` framework. This framework automatically runs a series of checks on your code _before_ you are allowed to create a commit, acting as an instant feedback loop and our first line of quality assurance.

### What are Pre-Commit Hooks?

Pre-commit hooks are automated scripts that run on your local machine every time you execute the `git commit` command. They act as a local quality gate, catching simple errors and formatting issues before they are ever saved to the project's history.

This process complements the full CI/CD pipeline that runs on GitHub Actions.

## How to Set It Up

After cloning the repository and running `make install` for the first time, you must install the hooks into your local Git configuration. This is a **one-time command** for each developer:

```
pre-commit install
```

Once you have run this, the hooks will be active.

_(Note: `pre-commit` is included in the project's development dependencies.)_

## How It Works

From now on, when you run `git commit`:

1. The `pre-commit` framework will run the configured checks (like `ruff` for formatting and linting) on the files you've staged for commit.

2. If any of the checks fail, the `git commit` process will be **aborted**. The tool will print an error message explaining what failed.

3. Some tools, like `ruff`, may automatically fix the issues for you.

4. After the issues are fixed (either automatically or by you), you will need to `git add` the modified files again and re-run `git commit`.


This process ensures that every commit that enters our repository already meets our baseline quality standards, making our codebase cleaner and more maintainable.
