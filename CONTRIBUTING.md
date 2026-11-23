# Adding a skill

**Easiest way:** install the `compchem` plugin (see the [README](README.md)) and tell Claude "add my skill X to the group repo". The `contribute-skill` skill does the steps below for you and asks before anything goes public. The rest of this page is the manual route.

## Rules

This repo is public, so everything you commit is visible to anyone.

- No unpublished results, data, or manuscript text.
- No API keys, passwords, tokens, or cluster login details.
- No personal paths (`/Users/<name>/...`) or email addresses. Write `<project_dir>` or similar instead.
- Write skills so that any group member can use them, not only for your own project.

## Steps

1. **Get the repo.**

   ```bash
   git clone https://github.com/compchem-lab-uni-stuttgart/ai-skills.git
   cd ai-skills
   git switch -c add-<skill-name>
   ```

2. **Copy the template.** Use lowercase letters and hyphens for the folder name.

   ```bash
   cp -R templates/skill-template plugins/compchem/skills/<skill-name>
   ```

3. **Write `SKILL.md`.**
   - `name` must match the folder name.
   - `description` decides when Claude uses the skill. Say what the skill does and list the requests that should trigger it, in the words people actually use.
   - Keep the body short and concrete. Put long reference material in extra files next to `SKILL.md` and link to them from the body.
   - Put helper code in a `scripts/` folder. See `plugins/compchem/skills/pub-figures/` for an example.
   - The `skill-creator` skill in Claude can draft and test a skill with you. Ask Claude: "help me write a skill that ...".

4. **Test it locally.** Start Claude Code with the plugin loaded from your clone:

   ```bash
   claude --plugin-dir plugins/compchem
   ```

   Ask something that should trigger the skill and check that Claude uses it. You can also call it directly with `/compchem:<skill-name>`.

5. **Check and validate.** The check script catches what the validator misses: a bad `name`, personal paths, emails, keys, and data files. Fix every ERROR and think about every WARN.

   ```bash
   python3 plugins/compchem/skills/contribute-skill/scripts/check_skill.py plugins/compchem/skills/<skill-name>
   claude plugin validate .
   claude plugin validate plugins/compchem
   ```

6. **Add a row** for your skill to the table in `README.md`.

7. **Open a pull request.**

   ```bash
   git add plugins/compchem/skills/<skill-name> README.md
   git commit -m "Add <skill-name> skill"
   git push -u origin add-<skill-name>
   ```

   Then open the pull request on GitHub. If you are not a member of the GitHub organization yet, fork the repo and open the pull request from your fork, or ask an owner to add you.

## Sharing a subagent

Subagents go in `plugins/compchem/agents/<agent-name>.md`. The same rules apply.
