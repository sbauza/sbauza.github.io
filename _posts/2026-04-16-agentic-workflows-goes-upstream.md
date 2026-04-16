---
layout: single
title: "OpenStack Agentic Workflows Goes Upstream"
date: 2026-04-16
categories:
  - AI
  - OpenStack
tags:
  - openstack
  - ai
  - agentic
---

In my [previous post](/ai/openstack/openstack-agentic-workflows/), I introduced the `openstack-agentic-workflows` repository — a set of AI-agent workflows tailored for OpenStack development. I mentioned that at the [PTG](https://ptg.openinfra.org/) I would discuss landing these workflows and knowledge files upstream with the Nova community.

The PTG is next week, but I didn't want to wait. I proposed the idea on the [openstack-discuss mailing list](https://lists.openstack.org/archives/list/openstack-discuss@lists.openstack.org/thread/6M43NTTOI3ZUQBIEJIJZTKJVCZZE5WLC/), and the community reached a consensus: let's create an upstream project. Shortly after, the repository was created on OpenDev and we now have **[openstack/agentic-workflows](https://opendev.org/openstack/agentic-workflows)**.

### From Personal Experiment to Community Project

The original repository at [github.com/sbauza/openstack-agentic-workflows](https://github.com/sbauza/openstack-agentic-workflows) was a personal experiment — a proof of concept that AI agents could be genuinely useful for OpenStack if given the right context. Moving it upstream means the entire community can now contribute, iterate, and build on top of it.

The project will been registered under the **[Testing and Collaboration Tools (TaCT) SIG](https://governance.openstack.org/sigs/tact-sig.html)**, which felt like the natural home: these workflows are tooling that helps contributors collaborate more effectively, not a new OpenStack service. I'll continue the conversation at the PTG next week to discuss the roadmap and get more contributors on board.

### The Initial Patch Series

I've already pushed an initial series of patches to seed the repository:

| Change | Description |
|--------|-------------|
| [#985021](https://review.opendev.org/c/openstack/agentic-workflows/+/985021) | **Add initial project scaffold** — the base structure with `CLAUDE.md`, `rules.md`, and the repository layout conventions |
| [#985022](https://review.opendev.org/c/openstack/agentic-workflows/+/985022) | **Add skill validation with tox and Zuul** — CI integration so that skills and knowledge files can be validated in gating jobs |
| [#985027](https://review.opendev.org/c/openstack/agentic-workflows/+/985027) | **Add AGENTS.md with skill authoring guidelines** — the contributor guide for writing new skills, rules, and personas |
| [#985035](https://review.opendev.org/c/openstack/agentic-workflows/+/985035) | **Add Nova personas and knowledge** — the shared Nova knowledge base and specialized agent personas (Nova Core Reviewer, Bug Triager, etc.) |
| [#985034](https://review.opendev.org/c/openstack/agentic-workflows/+/985034) | **Add code-review skill** — the first concrete workflow: a Nova code-review skill that can analyze Gerrit patches |

You can follow the full series at [review.opendev.org](https://review.opendev.org/q/project:openstack/agentic-workflows).

### What's Different from the GitHub Version?

The upstream version isn't a 1:1 copy of the GitHub repository. The goal is to land content incrementally, one reviewable piece at a time, and let the community shape the direction. Some key differences:

*   **Gated by Zuul:** Every change goes through CI. The second patch in the series adds `tox` environments and Zuul jobs that validate skill definitions and lint knowledge files. This directly addresses one of the [open questions from my first post](/ai/openstack/openstack-agentic-workflows/#the-remainder-missing-bits) — how do we test changes to agentic context?
*   **Community-governed:** Unlike a personal GitHub repo, this project follows the standard OpenStack governance model. Anyone with an OpenStack account can review, comment, and contribute patches via Gerrit.
*   **Scoped for growth:** The initial series focuses on Nova, but the project structure is designed to host workflows for any OpenStack service. A Neutron contributor could add `knowledge/neutron.md` and build skills tailored to their project without affecting the Nova workflows.

### How to Get Involved

If this interests you, here's how to jump in:

1.  **Review the patches.** The series is up on Gerrit — constructive feedback is welcome, especially from people who have tried using AI tools with OpenStack code.
2.  **Try the workflows.** Clone the repo and point your favorite AI tool at it (Cursor, Claude Code, or ACP all work). The `AGENTS.md` file documents how to get started.
3.  **Add your project.** If you maintain another OpenStack service and want to create workflows for it, the contributor guide in [#985027](https://review.opendev.org/c/openstack/agentic-workflows/+/985027) explains how.

### What's Next

The immediate priority is landing the initial series and iterating based on community feedback. Beyond that, I'd like to see:

*   **More services covered** — Neutron, Cinder, and other projects would benefit from the same approach.
*   **Skill evaluation frameworks** — building on the testing infrastructure to measure whether workflow changes improve or regress agent performance.
*   **Cross-project knowledge** — shared knowledge files for common patterns like Oslo libraries, Keystone auth, and the release process.

This is still early days, but having an upstream home means the work can scale beyond one person. I'm looking forward to seeing what the community builds with it.
