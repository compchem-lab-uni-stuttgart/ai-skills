# ai-skills

This repo collects the AI skills used in the Computer Chemistry Lab at the University of Stuttgart.

A skill is a folder with a `SKILL.md` file, plus scripts or reference files if it needs them. It teaches Claude how to do one task the way we do it. Claude reads the short `description` of every installed skill. It loads the full skill only when a request matches that description.

All skills live in one Claude Code plugin called `compchem`. Install it once and you get every skill in the repo. Updating it brings in new skills and fixes.

## Install

### Claude Code (terminal, VS Code, desktop app)

Run these two commands in a normal terminal. You don't need to download the repo first:

```bash
claude plugin marketplace add compchem-lab-uni-stuttgart/ai-skills
claude plugin install compchem@ai-skills
```

Then restart Claude Code (in VS Code: reload the window or open a new Claude chat). Skills show up as `compchem:<skill-name>`. Claude uses them automatically, and you can also call one directly, e.g. `/compchem:pub-figures`.

To get the latest version, run these and restart Claude Code:

```bash
claude plugin marketplace update ai-skills
claude plugin update compchem@ai-skills
```

If you use Claude Code in the terminal, the same commands also work there as `/plugin marketplace add ...` and `/plugin install ...`. The VS Code extension does not support `/plugin`.

### claude.ai and the Claude app

1. Download the skill's folder from `plugins/compchem/skills/`.
2. Zip the folder so that `SKILL.md` sits at the top level of the zip.
3. Upload the zip in the Skills section of your Claude settings.

Skills added this way do not update themselves. Upload the new version again when the skill changes.

## Skills

| Skill | What it does |
|---|---|
| [contribute-skill](plugins/compchem/skills/contribute-skill/SKILL.md) | Adds your skill or subagent to this repo: copies it in, removes private details, checks and validates it, and opens a pull request. |
| [pub-figures](plugins/compchem/skills/pub-figures/SKILL.md) | Publication-quality matplotlib figures: column-width sizing, vector PDF with embedded fonts, colorblind-safe colormaps, font checks before submission. |
| [text-review](plugins/compchem/skills/text-review/SKILL.md) | Reviews a paper, thesis or SI file and writes every proposed change to a Markdown file, top to bottom, tagged by category, with three suggestions each; applies only the points you pick. |

## Contributing

Anyone in the group can add a skill. With the plugin installed, the easiest way is to tell Claude something like "add my skill X to the group repo". The `contribute-skill` skill then walks through every step. The manual steps are in [CONTRIBUTING.md](CONTRIBUTING.md).

This repo is **public**. Never commit unpublished results or data, API keys, passwords, or personal file paths.

## License

[MIT](LICENSE)
