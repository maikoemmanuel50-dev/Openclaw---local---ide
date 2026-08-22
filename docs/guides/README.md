# Knowledge & Guides — Convention

The IDE's **Knowledge & Guides** panel auto-indexes this folder. Any `.md` file
here becomes a guide card; add a file and restart (or the running server rescans)
to surface it in the IDE.

## Front matter

Every guide starts with YAML:

```
---
title: <Card Title>
category: <Category Name>
tags: tag1, tag2
source: where the content came from (docs, web, telegram)
---
```

`category` groups cards in the sidebar (or `category` defaults to the folder
name). Keep `title` short — it's the card label.

## Layout

| Folder | Category |
|---|---|
| `01_software_manuals/` | Software Manuals |
| `02_production_standards/` | Production Standards |
| `03_creative_direction/` | Creative Direction |
| `04_tutorials_and_reference/` | Tutorials & References |
| `05_templates/` | Templates |
| `06_reference/` | Technical Reference |

## Future episodes

- Software manuals, production standards, tutorials, and reference apply to
  every episode — keep them episode-agnostic.
- Put episode-specific creative briefs in `03_creative_direction/` named
  `episode_N_creative_direction.md`, mirroring
  `episode_1_creative_direction.md`.
- The server auto-discovers new guides on startup (rescan). Video index lives
  in `docs/video_library/tutorial_index.json`.

## Sources of truth

These guides are derivations. Authority stays with the Vault docs:
`Africa Season 1\docs\*`, `PRODUCTION_STATUS.md`, `.cursor\rules\*.mdc`, and the
live status files. If a guide and a status/gate disagree, the live gate/status
wins — stop and ask when uncertain.