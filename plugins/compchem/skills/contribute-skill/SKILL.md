---
name: contribute-skill
description: Add a new skill or subagent to the Computer Chemistry Lab's shared ai-skills repo (GitHub compchem-lab-uni-stuttgart/ai-skills, plugin "compchem"), or update one that is already there, and open a pull request. Use this whenever the user wants to share, contribute, publish, upload or "put on GitHub" a skill, SKILL.md, subagent or reusable prompt for the group, lab or colleagues, wants to turn a workflow into a shared skill, or wants to fix or improve a compchem skill, even if they never name the repo.
---

# Contribute to ai-skills

The group shares its skills through one public GitHub repo, which works as a Claude Code plugin marketplace:

- Repo: `https://github.com/compchem-lab-uni-stuttgart/ai-skills`
- Skills: `plugins/compchem/skills/<skill-name>/SKILL.md` (plus `scripts/`, reference files)
- Subagents: `plugins/compchem/agents/<agent-name>.md`
- Template: `templates/skill-template/SKILL.md`
- Everyone installs it with `claude plugin marketplace add compchem-lab-uni-stuttgart/ai-skills` and `claude plugin install compchem@ai-skills`.

Every change goes in as a pull request, also for org owners. A second person looks at it before it reaches the whole group. Never push to `main`.

The repo is **public**. Anything committed can be read by anyone, and git history keeps it even after a later deletion. Catch private content before the commit, not after.

## 1. Find out what is being contributed

Ask, unless it's already clear:

- **An existing skill**, e.g. in `~/.claude/skills/<name>/`, a project's `.claude/skills/<name>/`, or a `.zip` / `.skill` exported from claude.ai (unzip it into a scratch folder first).
- **An existing subagent**, e.g. `~/.claude/agents/<name>.md` or a project's `.claude/agents/<name>.md`.
- **A new skill from scratch.** If the `skill-creator` skill is available, use it to draft and test the skill, then come back here for the repo steps. Otherwise start from the repo template.
- **A change to a skill already in the repo.**

Read the source files completely before copying them, so you know what you're about to publish.

## 2. Get an up-to-date copy of the repo

Look for an existing clone first. The current directory may be one, or the user may know where theirs is. Check it with `git -C <dir> remote -v`: the URL must contain `compchem-lab-uni-stuttgart/ai-skills`. If there is no clone, ask where to put one, then clone it:

```bash
git clone https://github.com/compchem-lab-uni-stuttgart/ai-skills.git <dir>
```

In the clone, make sure the working tree is clean (`git status`). Then get the latest `main` and branch off it:

```bash
git switch main && git pull --ff-only
git switch -c add-<name>        # or update-<name>
```

Uncommitted changes in the clone may be the user's own work. Ask before stashing or discarding anything.

## 3. Put the files in place

- **Skill:** copy the whole folder to `plugins/compchem/skills/<name>/`. Leave out `__pycache__/`, `.DS_Store`, outputs, caches and data.
- **Subagent:** copy it to `plugins/compchem/agents/<name>.md`.
- **New skill:** `cp -R templates/skill-template plugins/compchem/skills/<name>`, then fill it in.

The folder name and the `name:` in the frontmatter must be identical. Use lowercase letters, digits and hyphens only. Run `ls plugins/compchem/skills plugins/compchem/agents` first. If the name is taken, it's either an update to that skill or the new one needs a different name. Ask which.

## 4. Make it work for everyone

A personal skill often only works on its author's machine. Fix that, but keep what the skill does and how the author wants it done:

- **Description.** It decides when Claude loads the skill, so it must say what the skill does *and* when to use it. List the phrases people actually use, and be a little pushy ("Use this whenever ..., even if they don't say ..."). Keep it under 1024 characters.
- **Paths.** Replace personal paths (`/Users/<name>/...`, thesis folders, cluster scratch dirs) with placeholders like `<project_dir>`, or with paths relative to the skill folder. In Claude Code, scripts in the skill are reached through the skill's base directory, which Claude is told when the skill loads.
- **Dependencies.** If scripts need packages (numpy, matplotlib, ase, ...), say so in the SKILL.md.
- **Project-specific rules.** Drop or generalize them unless they are the point of the skill.

Show the user a diff of everything you changed in their content and get their OK. They are the author, and the PR goes out under their name.

## 5. Run the check script

From the repo root:

```bash
python3 plugins/compchem/skills/contribute-skill/scripts/check_skill.py plugins/compchem/skills/<name>
# subagent:  ... check_skill.py plugins/compchem/agents/<name>.md
```

The script checks the frontmatter, which `claude plugin validate` does not fully check. It also looks for personal paths, email addresses, API keys and tokens, research data files, oversized files, and a missing README entry.

- Fix every **ERROR**.
- Go through each **WARN** with the user. A warning is a question, not a verdict: a published example `.xyz` file can be fine, an unpublished trajectory is not.
- If the script finds a real API key or password, tell the user to revoke it. Removing it from the files is not enough if it was ever pushed anywhere.

Also ask the user directly whether the skill contains unpublished results, manuscript text, or internal details of collaborators' projects. No script can recognize those.

## 6. Validate and test

```bash
claude plugin validate .
claude plugin validate plugins/compchem
```

Both must end with "Validation passed". Three warnings are expected and can be ignored:

- **missing `version`:** left out on purpose, so updates follow git commits.
- **README_MISSING and ICON_MISSING:** these only matter for Anthropic's public plugin directory.

To try the skill before the PR, the user starts a session with the plugin loaded from the clone. Give them the command, since you can't drive an interactive session yourself:

```bash
claude --plugin-dir plugins/compchem
```

Then they ask something that should trigger the skill, or call it directly with `/compchem:<name>`. For a quick non-interactive check you can run `claude -p --plugin-dir plugins/compchem "<a realistic request>"` yourself and see whether the skill gets used.

## 7. Add it to the README

Add a row to the **Skills** table in `README.md`, keeping it alphabetical. Link the SKILL.md and write a one-line summary of what the skill does:

```markdown
| [<name>](plugins/compchem/skills/<name>/SKILL.md) | One line: what it does. |
```

For a subagent, add the row to an **Agents** table below the Skills table. Create that table if it doesn't exist yet.

## 8. Commit, push, open the pull request

Stage only the files of this contribution, not `git add -A`, so nothing unrelated slips in:

```bash
git add plugins/compchem/skills/<name> README.md
git status && git diff --cached --stat
git commit -m "Add <name> skill"         # or "Update <name>: <what changed>"
```

**Ask the user before pushing.** The push makes the content public.

Check whether the user can push to the org repo:

```bash
gh repo view compchem-lab-uni-stuttgart/ai-skills --json viewerPermission -q .viewerPermission
```

- **`ADMIN`, `MAINTAIN` or `WRITE`:** `git push -u origin <branch>`.
- **Anything else:** fork first. `gh repo fork --remote` turns the user's fork into `origin` and the org repo into `upstream`. Then `git push -u origin <branch>`.

Open the pull request against the org repo:

```bash
gh pr create --repo compchem-lab-uni-stuttgart/ai-skills --base main \
  --title "Add <name> skill" \
  --body "<what it does, when it triggers, how it was tested, anything reviewers should look at>"
```

**Without a working `gh`** (not installed, or `gh auth status` fails): push the branch anyway, then give the user the link to open the pull request in the browser. For a branch on a fork, write `<fork-owner>:<branch>` instead of `<branch>`:

```
https://github.com/compchem-lab-uni-stuttgart/ai-skills/compare/main...<branch>?expand=1
```

If the push itself fails with 403 / permission denied, the user has no write access. Fork the repo (on github.com or with `gh repo fork`) and push there.

## 9. After the pull request

Tell the user:

- **Merge:** someone else in the group should review and merge it.
- **Update:** after the merge, everyone gets the skill with these commands and a restart of Claude Code:

  ```bash
  claude plugin marketplace update ai-skills
  claude plugin update compchem@ai-skills
  ```

  In the VS Code extension `/plugin` is not available, so run these in a normal terminal.
- **Old copy:** if the user also has the skill installed another way (e.g. in `~/.claude/skills/` or uploaded to claude.ai), they should remove that copy after the merge. Otherwise Claude sees the skill twice.
