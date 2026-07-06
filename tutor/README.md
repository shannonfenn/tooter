# tutor/ — tutor-core sources

The canonical prose for the tutor: agent role, commands (the named pedagogical
moves), always-loaded instructions, skills, and the enforced opencode config.
This is the portable asset; surfaces are rented (redesign-plan.md §3.2).

Nothing here is read in place. `just deploy` compiles these sources into the
study workspace (`~/dev/src/github/tooter-studies`):

| source                          | deploys to (in tooter-studies)              |
| ------------------------------- | ------------------------------------------- |
| `agents/`                       | `.opencode/agents/`                         |
| `commands/`                     | `.opencode/commands/`                       |
| `instructions/`                 | `.opencode/instructions/`                   |
| `skills/`                       | `.opencode/skills/`                         |
| `opencode.jsonc`                | `opencode.jsonc`                            |
| `deployed-readme.md`            | `.opencode/README.md`                       |
| `../docs/pedagogy-for-tutoring.md` | `.opencode/reference/pedagogy-for-tutoring.md` |

The compiler (`scripts/deploy.py`) is dumb file copying from that manifest —
no templating — so `just deploy --check` is plain byte equality. Run the check
on a weekly schedule, never at study-session start.

Phase 1 adds the remaining moves (`/start`, `/review-paper`, `/progress`), the
photo protocols (§4.4), and the rendering-era pedagogy hardening (§6).
