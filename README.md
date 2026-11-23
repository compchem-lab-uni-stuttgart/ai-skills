# ai-skills

This repo collects the AI skills used in the Computer Chemistry Lab at the University of Stuttgart.

A skill is a folder with a `SKILL.md` file, plus scripts or reference files if it needs them. It teaches Claude how to do one task the way we do it. Claude reads the short `description` of every installed skill. It loads the full skill only when a request matches that description.

All skills live in one Claude Code plugin called `compchem`. Install it once and you get every skill in the repo. Updating it brings in new skills and fixes.

## Install

### Claude Code (CLI, VS Code, desktop app)

Run these two commands inside Claude Code:

```
/plugin marketplace add Computer-Chemistry-Lab-Uni-Stuttgart/ai-skills
/plugin install compchem@ai-skills
```

Restart Claude Code afterwards. Skills then show up as `compchem:<skill-name>`. Claude uses them automatically, and you can also call one directly, e.g. `/compchem:pub-figures`.

To get the latest version:

```
/plugin marketplace update ai-skills
```

### claude.ai and the Claude app

1. Download the skill's folder from `plugins/compchem/skills/`.
2. Zip the folder so that `SKILL.md` sits at the top level of the zip.
3. Upload the zip in the Skills section of your Claude settings.

Skills added this way do not update themselves. Upload the new version again when the skill changes.

## Skills

| Skill | What it does |
|---|---|
| [pub-figures](plugins/compchem/skills/pub-figures/SKILL.md) | Publication-quality matplotlib figures: column-width sizing, vector PDF with embedded fonts, colorblind-safe colormaps, font checks before submission. |

## Contributing

Anyone in the group can add a skill. See [CONTRIBUTING.md](CONTRIBUTING.md).

This repo is **public**. Never commit unpublished results or data, API keys, passwords, or personal file paths.

## License

[MIT](LICENSE)
