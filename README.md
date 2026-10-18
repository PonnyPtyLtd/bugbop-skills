# Bugbop skills

A skill that lets an AI coding agent work with your [Bugbop](https://bugbop.com) programs through the [REST API](https://bugbop.com/docs/api). It can pull in new reports, triage them, comment back to hunters, submit reports and sync everything to Jira, Linear or wherever your team works.

It uses the open [Agent Skills](https://agentskills.io) format, so it works in Claude Code, Codex, Cursor, GitHub Copilot, Gemini CLI, OpenCode, Goose and anything else that reads a `SKILL.md`.

## Install

Claude Code:

```
/plugin marketplace add PonnyPtyLtd/bugbop-skills
/plugin install bugbop@bugbop-skills
```

Anything else: copy `skills/bugbop` into wherever your tool keeps skills. For most that's `.agents/skills/` or `.claude/skills/` in the project, or the equivalent folder under your home directory. The skill needs `python3` and nothing else.

Then create a token on the **API Tokens** tab of your Bugbop profile and export it:

```bash
export BUGBOP_TOKEN=bugbop_pat_...
```

## Try it

- "What new reports came in on Bugbop this week?"
- "Triage the open criticals and draft replies to the hunters."
- "Create Jira tickets for every high or critical report that's open."

Anything that notifies people (comments, status changes, new reports) gets shown to you before it's sent.

## The script

`skills/bugbop/scripts/bugbop.py` is a tiny client with no dependencies, and it works fine on its own:

```bash
python3 skills/bugbop/scripts/bugbop.py GET "/reports?status=new,open&severity=critical" --all
```

It handles the token, pagination and per-minute rate limits.

## License

MIT
