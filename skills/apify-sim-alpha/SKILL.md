---
name: apify-sim-alpha
description: Simulation skill Alpha. Validates the parallel-merge scenario of the generated-marketplace architecture — two concurrent skill PRs must merge without touching .claude-plugin/marketplace.json. Not a real skill; safe to delete.
author: sim-harness
author_url: https://github.com/chocholous/awesome-skills-sim
metadata:
  category: data-extraction
  keywords: "simulation, parallel-merge, alpha"
---

# apify-sim-alpha

Test fixture for the publication-architecture simulation (scenario 3).

## Purpose

This skill exists only to prove that a contributor PR consists of exactly one
directory and never edits the generated catalog. The post-merge bot regenerates
`.claude-plugin/marketplace.json`, `agents/AGENTS.md` and the README table.

## Workflow

1. There is no runtime workflow; this fixture is inert by design.
2. Rollback drill: reverting the merge commit of this skill must remove it from
   the regenerated catalog automatically.
