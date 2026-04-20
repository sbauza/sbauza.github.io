---
layout: single
title: "Agentic Workflows: One Week In"
date: 2026-04-20
categories:
  - AI
  - OpenStack
tags:
  - openstack
  - ai
  - agentic
---

In my [previous post](/ai/openstack/agentic-workflows-goes-upstream/), I announced the creation of **[openstack/agentic-workflows](https://opendev.org/openstack/agentic-workflows)** on OpenDev and pushed an initial series of patches. That was four days ago. Here's what happened since.

### The Scorecard

Five changes have merged, seventeen are open for review, and three distinct contributors beyond myself have shown up. For a repo that didn't exist a week ago, that's a healthy start.

### What Merged

| Change | Author | Description |
|--------|--------|-------------|
| [#985021](https://review.opendev.org/c/openstack/agentic-workflows/+/985021) | Sylvain Bauza | **Add initial project scaffold** — base structure, `AGENTS.md` pointer, `rules.md`, layout conventions |
| [#985022](https://review.opendev.org/c/openstack/agentic-workflows/+/985022) | Sylvain Bauza | **Add skill validation with tox and Zuul** — CI gating for skill definitions |
| [#985027](https://review.opendev.org/c/openstack/agentic-workflows/+/985027) | Sylvain Bauza | **Add AGENTS.md with skill authoring guidelines** — the contributor guide |
| [#985078](https://review.opendev.org/c/openstack/agentic-workflows/+/985078) | Stephen Finucane | **Convert docs to markdown, drop duplicate information** — consolidates README and AGENTS.md |
| [#985082](https://review.opendev.org/c/openstack/agentic-workflows/+/985082) | Stephen Finucane | **README: Add warning RE: WIP state** — links to the [OpenInfra AI policy](https://openinfra.dev/legal/ai-policy) |

### New Contributors

*   **Stephen Finucane** jumped in within hours. Beyond the doc patches, he sparked a useful RST-vs-Markdown debate and raised the important point about not duplicating information between README and AGENTS.md. His WIP warning also ensures we don't give the impression this is an official, production-ready project yet.

*   **Rodolfo Alonso** proposed [#985072](https://review.opendev.org/c/openstack/agentic-workflows/+/985072) — Neutron-specific knowledge in `knowledge/neutron.md`. This is the first cross-project contribution, exactly the kind of growth the repo was designed for. In my previous post, I wrote "a Neutron contributor could add `knowledge/neutron.md`" as a hypothetical; Rodolfo made it real.

*   **Sean Mooney** opened roughly a dozen patches under a "strawman" topic. He also left detailed review comments on the code-review and Nova knowledge patches. More on that below.

### The Architectural Debate: Skills vs. Orchestration

The most interesting development isn't a patch — it's a design disagreement. Sean's Code-Review -1 on [#985034](https://review.opendev.org/c/openstack/agentic-workflows/+/985034) raises substantive points about how skills should be structured:

*   **Separation of concerns.** The code-review skill currently conflates *orchestration* (fetching context from Gerrit via MCP) with *review* (analyzing the code). Sean argues these should be separate skills — a "gerrit-library" skill that retrieves context, and a pure review skill that works against a locally checked-out repo.
*   **No MCP assumptions.** Skills shouldn't hard-code MCP as the way to get review context. A CLI tool, a local checkout, or a different protocol should all be valid.
*   **Local checkout, not diffs.** Reviewing a diff misses breakages in unmodified files. The review skill should operate on a full local working tree.
*   **Knowledge overlays.** Project-specific rules (versioning, microversions, API extensions) should live in a knowledge layer, not be embedded in skill definitions. He proposed a three-tier model: SKILL.md for the core workflow, a local references directory for compact skill context, and the repository knowledge base for fuller source material.

My current approach optimizes for a different thing — self-contained skills that work end-to-end out of the box, with knowledge embedded close to the skill for discoverability. Both approaches have merit. Sean's architecture is more composable; mine prioritizes a shorter path to a working demo. The project will need to find a middle ground, and that's exactly the kind of design discussion I was hoping the upstream move would enable. Personally, I'm open to revising my approach and reworking my patches to fit whatever consensus we reach at the PTG (see below).

### Sean's Strawman Series

Sean didn't just review — he proposed an alternative architecture. His "strawman" topic includes roughly a dozen patches uploaded over the weekend:

| Change | Description |
|--------|-------------|
| [#985224](https://review.opendev.org/c/openstack/agentic-workflows/+/985224) | **Multi-agent skill distribution** — plugin manifests for Codex, Claude Code, and skills.sh clients |
| [#985252](https://review.opendev.org/c/openstack/agentic-workflows/+/985252) | **Route agent guidance through knowledge** — restructures AGENTS.md as a routing index (+2490 lines) |
| [#985251](https://review.opendev.org/c/openstack/agentic-workflows/+/985251) | **OpenStack commit message skill** — dedicated skill for writing proper commit messages |
| [#985303](https://review.opendev.org/c/openstack/agentic-workflows/+/985303), [#985304](https://review.opendev.org/c/openstack/agentic-workflows/+/985304), [#985305](https://review.opendev.org/c/openstack/agentic-workflows/+/985305), [#985306](https://review.opendev.org/c/openstack/agentic-workflows/+/985306) | **Python typing, testing patterns, and modernization workflows** |
| [#985225](https://review.opendev.org/c/openstack/agentic-workflows/+/985225), [#985250](https://review.opendev.org/c/openstack/agentic-workflows/+/985250) | **Local validation hooks and Nix dev shell** |
| [#985302](https://review.opendev.org/c/openstack/agentic-workflows/+/985302) | **Skill authoring workflow guidance** |

### Still in Flight

My own open patches are being shaped by the review feedback:

| Change | Description |
|--------|-------------|
| [#985034](https://review.opendev.org/c/openstack/agentic-workflows/+/985034) | **Add code-review skill** — analyze Gerrit patches for intent, architecture, and testing adequacy |
| [#985035](https://review.opendev.org/c/openstack/agentic-workflows/+/985035) | **Add Nova personas and knowledge** — specialized agent personas and project-specific context |
| [#985085](https://review.opendev.org/c/openstack/agentic-workflows/+/985085) | **Add bug-triage skill** — classify Launchpad bugs against source code |
| [#985128](https://review.opendev.org/c/openstack/agentic-workflows/+/985128) | **Add backport skill** — cherry-pick upstream changes to stable branches |

### What This Tells Us

A few takeaways from the first week:

*   **The project is alive.** Three new contributors and seventeen open patches in four days! That's an awesome number.
*   **The hard questions are surfacing.** How granular should skills be? Where does knowledge live? How do we balance composability with usability? Should we have OpenStack personas or just subagents per skill? These are the questions that will define the project's architecture, and we're just at the beginning.

### Coming Up: A PTG Session on Friday

The [PTG](https://ptg.openinfra.org/) starts today, and the [TC etherpad](https://etherpad.opendev.org/p/apr2026-ptg-os-tc) already has an AI-related session scheduled for **Friday April 24th** focused on the agentic-workflows project itself.

Key questions for that session:

*   **Project knowledge.** Should we propose a TC community goal asking service projects to document their tribal knowledge in contributor-facing docs? This would benefit both human newcomers and AI agents.
*   **Skill evaluation.** How do we review and score skill proposals? The idea is to reuse the [evaluation pattern from Anthropic](https://agentskills.io/skill-creation/evaluating-skills) so that skill quality is measurable, not subjective.
*   **Skill distribution.** Should we prioritize marketplace deliverables (skills.sh, Claude plugins, Codex plugins) so that contributors can install skills directly into their tools rather than cloning the whole repo into their workspace?

### Finding a Home

The project is also [awaiting TC approval](https://review.opendev.org/c/openstack/governance/+/984958) to sit under the TaCT SIG umbrella, and an IRC channel (`#openstack-agentic-workflows`) already exists for day-to-day discussion. I expect the project to look quite different by the time the next post rolls around.
