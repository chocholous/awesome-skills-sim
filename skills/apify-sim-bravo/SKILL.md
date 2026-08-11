---
name: apify-sim-bravo
description: Simulation skill Bravo. Second half of the parallel-merge scenario — merged immediately after Alpha from an independent branch, without rebase and without touching the generated catalog. Not a real skill; safe to delete.
author: sim-harness
author_url: https://github.com/chocholous/awesome-skills-sim
metadata:
  category: data-extraction
  keywords: "simulation, parallel-merge, bravo"
---

# apify-sim-bravo

Test fixture for the publication-architecture simulation (scenario 3).

## Purpose

Merged back-to-back with `apify-sim-alpha` to prove the second PR needs no
rebase and no conflict resolution, and that two consecutive regeneration runs
converge to a catalog containing both skills.
