# Agent Harnesses

This repo uses v0 CLI/app harness configuration only. Do not build a custom tutoring UI, orchestration service, or agent ecosystem until the plain Pi and OpenCode setups hit a clear capability limit.

## Design Goal

Keep development and teaching roles separated:

- Codex is the intended software-engineering agent for repository maintenance, documentation refactors, scripts, tests, harness setup, and commits.
- Pi and OpenCode are intended teaching harnesses for tutoring, solution assessment, study planning, and programming exercises.
- Teaching agents may update learner state or pack-local programming exercise files when that is part of a study interaction.
- Teaching agents should not carry repository-development process instructions.
- Do not reintroduce `AGENTS.md` for this project unless the goal changes to cross-harness always-on instructions.

## Pi

Pi uses:

- `.pi/APPEND_SYSTEM.md` for teaching-harness orientation and guardrails.
- `.pi/skills/*/SKILL.md` for generic mathematics pedagogical roles.
- `.pi/prompts/*.md` for common tutoring and planning prompts.

Use Pi for pedagogy through the relevant prompt template or skill command, such as `/hint`, `/assess-solution`, `/chapter-plan`, `/exit-check`, `/transfer-problem`, or `/skill:math-tutoring`. Do not use Pi for repository development work; use Codex for that.

## OpenCode

OpenCode uses:

- `opencode.jsonc` for OpenCode project configuration.
- `.opencode/instructions/math-study-context.md` for teaching-harness orientation and guardrails.
- `.opencode/agents/math-pedagogy.md` as the explicit pedagogical primary agent.
- `.opencode/skills/*/SKILL.md` for generic mathematics pedagogical roles.
- `.opencode/commands/*.md` for common tutoring and planning commands.

Use OpenCode for pedagogy by switching to the `math-pedagogy` agent or using one of the OpenCode commands: `/hint`, `/assess-solution`, `/chapter-plan`, `/exit-check`, or `/transfer-problem`. Do not use OpenCode for repository development work in this project; use Codex for that.

## Study Packs

The generic pedagogy roles read `studies/active.md` and then use the active study pack for text-specific policy, source priority, workflow, progress, exercise indexes, and edition notes. Add new mathematics texts under `studies/<slug>/` rather than hard-coding text-specific behavior into harness skills.

## Running Location

For v0, run Pi or OpenCode with the repository root as the working directory so project-local teaching resources are discovered automatically. If launching from elsewhere, point the tool at this repository or use the harness-specific mechanism for selecting the project working directory.

## V1 Boundary

Consider a v1 harness only if the CLI/app setup cannot support a required workflow, such as persistent learner state outside the repo, structured assessment records, cross-session scheduling, or more reliable automatic role selection than prompts, skills, and native OpenCode agents can provide.
