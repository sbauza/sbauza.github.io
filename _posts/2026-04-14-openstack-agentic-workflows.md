---
layout: single
title: "OpenStack Agentic Workflows: Bridging Context and Code Reasoning"
date: 2026-04-14
categories:
  - AI
  - OpenStack
tags:
  - openstack
  - ai
  - agentic
---

As part of my company's directive to transition toward an Agentic Software Development Lifecycle (ASDLC), I have been heavily focused on integrating AI agents into the OpenStack ecosystem, specifically for Nova.

### The Challenge: The Semantic Gap

Out-of-the-box LLMs and generic AI tools often fail when interacting with complex open-source ecosystems like OpenStack because they lack "institutional memory". Agents operating in a vacuum suffer from tooling blindspots, decoupled ecosystems, and an inability to guess unwritten human conventions.

Over the last six months I have been testing the **[Ambient Code Platform (ACP)](https://ambient.github.io/)**—a Kubernetes-native platform that orchestrates AI-powered "agentic sessions." ACP manages the full session lifecycle: you define a workflow once (skills, personas, rules) and it spins up containerized jobs that execute Claude Code CLI with multi-agent collaboration. Think of it as CI/CD, but for AI reasoning tasks instead of builds.

One of ACP's built-in tools is **AgentReady**, which scores a repository on how well an AI agent can navigate it autonomously. To quantify this AI-readiness, I ran AgentReady against the upstream OpenStack Nova repository. The vanilla repository [scored a low 20.8/100](/agentready/report-nova_no_claude/). The AI was missing fundamental OpenStack knowledge—it had no awareness of the Oslo common libraries that underpin every service, nor of the [Vulnerability Management Team (VMT)](https://security.openstack.org/vmt.html) process that governs how security issues are reported, embargoed, and disclosed across projects.

For testing purposes, I asked Claude to generate a standard `CLAUDE.md` file for the Nova repository. Even with this additional guidance, the AgentReady evaluation reached only 30.7/100. You can examine the full report [here](/agentready/report-nova_with_claude/).

### The Solution: Educated Guesses via Agentic Workflows

This is why I believe that in order to support long reasoning chains, we must proactively supply explicit context. To address this, I created the [`openstack-agentic-workflows`](https://github.com/sbauza/openstack-agentic-workflows) repository more as a demonstration than a prioritized new project ;-)

Here are the core pillars of what I built:

*   **Unified Workflows (Zero Duplication):** I designed a repository structure that avoids duplicating logic across different LLM UIs. Skills, behavioral rules, and project context (`AGENTS.md`) are authored once and natively discovered via symlinks and pointer files by **Cursor**, **Claude Code**, and the **Ambient Code Platform (ACP)**.
*   **Seamless External Integration:** The workflows map cross-repo visibility by integrating Model Context Protocol (MCP) servers. This allows the agents to fetch change metadata from Gerrit, interact with Atlassian (JIRA) for issue triage, and use GitLab for backporting workflows.
*   **Specialized Domain Personas:** Instead of generic software roles, I injected deep OpenStack domain expertise through specialized agent personas. Workflows invoke subagents like the *Nova Core Reviewer* (for versioning and API microversions), *Nova Core Security* (for privsep and RBAC), and the *OpenStack Bug Triager*.
*   **Layered Context, Not a Single File:** A monolithic `AGENTS.md` can provide baseline context, but it scales better to separate concerns — *rules* define behavioral guardrails, *knowledge files* capture domain-specific facts, and *skills* encode reusable task procedures. This layering also lets skills be per-user, so each contributor can bring their own task-specific toolbox. As a bonus, new contributors benefit too: knowledge files and rules double as human-readable documentation of the project's tribal knowledge, without needing to wade through `AGENTS.md` or skill definitions that are meant for LLMs.
*   **Human Decides, Agent Assists:** AI doesn't replace the OpenStack developer. The reasoning edge is still too blunt for autonomous merging. Instead, the agent drafts, traces, and analyzes complex workflows—like triaging Launchpad bugs or generating `nova-specs` proposals—while the human oversight provides the final decisions.

The repository is public — feel free to explore it, try the workflows, browse the knowledge files, and open issues or pull requests if something catches your eye. You can either use it to test the skills or to ask LLMs Nova-specific questions using the personas I created.

Eventually, next week at the [PTG](https://ptg.openinfra.org/), I'll discuss with the Nova community whether we should land those knowledge files directly in the upstream Nova repository. This would require an `AGENTS.md` bootstrap file, but from there any LLM invoked by a contributor could leverage the embedded context to reason about Nova, right?


## The Remainder: Missing Bits

That said, I know we still have gaps, even with better context.

* **More context isn't always better.** A telling example is the [VeNCrypt false positive](https://github.com/sbauza/openstack-agentic-workflows/issues/17) tracked in the repository. Even with curated context, an AI agent reviewing a Gerrit patch consistently flagged a `None` default in a method parameter as a critical security bug. It fundamentally misunderstood the system's configuration prerequisites. This suggests that we may need to add more docstrings or inline comments directly in our code to guide the models.
* **Testing needs:** How do we review changes to the openstack-agentic-workflows repository? How do we know that adding or modifying context won't cause regressions? The same question applies to skills. AgentSkills proposes [assertions for skills](https://agentskills.io/skill-creation/evaluating-skills#writing-assertions) — could we adopt a similar approach for our workflows and knowledge context, and if so, how? Should we score each workflow with rubrics like [ACP proposes](https://ambient-code.github.io/platform/workflows/custom/#rubrics)? These are open questions, but I believe we need answers before we scale our LLM usage further.

## Conclusion

This is just the beginning, and I don't have all the answers yet. I'd love your help — try the repository, tell me where I'm wrong, and share your own ideas. Community feedback is what will make this work.
