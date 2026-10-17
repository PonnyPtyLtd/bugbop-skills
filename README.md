# Bugbop skills

A skill that lets Claude Code (and other agents that support skills) work with your [Bugbop](https://bugbop.com) programs through the [REST API](https://bugbop.com/docs/api). It can pull in new reports, triage them, comment back to hunters and sync everything to Jira, Linear or wherever your team works.

## Install

In Claude Code:

```
/plugin marketplace add PonnyPtyLtd/bugbop-skills
/plugin install bugbop@bugbop-skills
```

Or copy `skills/bugbop` into `~/.claude/skills/`.

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
