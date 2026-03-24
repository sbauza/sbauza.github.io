# Skills Reference — OpenStack Nova

Reusable skills for Claude Code workflows on the Nova codebase. Skills are shorthand prompts invoked with `/<skill-name>` that automate common development tasks.

---

## Built-in Skills

### /commit
Create a well-structured git commit with conventional message format.

### /simplify
Review changed code for reuse, quality, and efficiency. Finds unnecessary complexity, duplicated logic, or missed abstractions, then fixes issues found.

### /loop `<interval>` `<command>`
Run a prompt or slash command on a recurring interval. Useful for polling, monitoring, or recurring checks.
- Example: `/loop 5m /nova-test`
- Default interval: 10 minutes

---

## Custom Skill Patterns

You can create custom skills by adding `.md` files to your project's `.claude/skills/` directory. Each file defines a reusable prompt.

### Anatomy of a Skill File

```markdown
---
description: Short description of what this skill does
user_invocable: true  # Can be called with /skill-name
---

Prompt content goes here. This is the instruction Claude follows
when the skill is invoked.
```

---

## Nova-Specific Skills

### /nova-test
```markdown
---
description: Run Nova unit tests for changed files
user_invocable: true
---
Run unit tests relevant to the current changes:
1. Identify changed files via `git diff --name-only`
2. Map each changed file to its test counterpart in `nova/tests/unit/`
3. Run `tox -e py3 -- <test_paths>` for the relevant tests
4. If tests fail, read the failing test and source, then suggest a fix
5. If all pass, report a summary

For broader validation, also run:
- `tox -e pre-commit` for lint (includes N-code hacking checks)
- `tox -e functional` if compute/conductor/scheduler logic changed
- `tox -e api-samples` if REST API behavior changed
```

### /nova-review
```markdown
---
description: Review Nova code changes against project conventions
user_invocable: true
---
Review the current git diff against Nova's coding conventions:

1. **Versioning violations** (CRITICAL — block merges):
   - RPC method changes without version bump
   - Object attribute/method changes without version increment
   - DB schema changes that are not additive-only
   - API changes without a new microversion

2. **Hacking checks** (N-codes):
   - No DB imports in virt drivers (N307)
   - No cross-driver imports (N311), no config borrowing (N312)
   - Config options in `nova/conf/` only (N342), policies in `nova/policies/` (N350)
   - `timeutils.utcnow()` not `datetime.utcnow()` (N310)
   - `nova.utils.spawn()` not raw eventlet (N340)
   - Log messages not translated (N319), `LOG.warning` not `LOG.warn` (N352)

3. **Security boundaries**:
   - nova-compute must not access DB directly (route through conductor)
   - Privileged ops must use `nova.privsep` paths (N362)
   - No secrets in log output or notification payloads

4. **Testing**:
   - New features have unit tests
   - Bug fixes have tests that fail before and pass after
   - Proper assertion methods (N316/N317, N334, N356)

Be concise. Only flag real violations, not style preferences.
```

### /nova-bugfix
```markdown
---
description: Guided Nova bug fix workflow
user_invocable: true
---
Follow the Nova bug fix workflow:
1. Read the Launchpad bug report (user provides bug ID or URL)
2. Identify the affected service (compute, conductor, scheduler, API, virt driver)
3. Locate the relevant code using the manager class:
   - ComputeManager: `nova/compute/manager.py:642`
   - ConductorManager: `nova/conductor/manager.py:107`
   - SchedulerManager: `nova/scheduler/manager.py:58`
4. Write a failing test in the corresponding `nova/tests/unit/` path
5. Implement the minimal fix
6. Run `tox -e py3 -- <test_path>` to verify
7. Run `tox -e pre-commit` for lint
8. Check: does this fix require a version bump (RPC, object, or API)?
9. Flag if human review is needed (DB migration, privsep, config/policy defaults)
```

### /nova-rpc-check
```markdown
---
description: Validate RPC and object versioning for Nova changes
user_invocable: true
---
Check the current diff for versioning compliance:

1. **RPC changes** — scan `nova/compute/rpcapi.py`, `nova/conductor/rpcapi.py`, `nova/scheduler/rpcapi.py`:
   - Any new or modified RPC method requires a version bump
   - New arguments must have defaults (backwards compatibility)
   - Check `VERSION` constant matches the change

2. **Object changes** — scan `nova/objects/`:
   - Attribute additions/removals require `VERSION` increment
   - Method signature changes require version increment
   - `obj_make_compatible()` must handle downlevel versions

3. **DB migrations** — scan `nova/db/`:
   - Must be additive-only (no column drops, no type changes)
   - Must work online (no downtime)

4. **API microversions** — scan `nova/api/`:
   - New behavior requires a microversion bump
   - API version decorator must be the first decorator (N332)

Report: PASS (no version issues) or FAIL (list each violation with file:line).
```

### /nova-migrate
```markdown
---
description: Generate a Nova database migration
user_invocable: true
---
Generate a database migration for the described schema change:
1. Create the migration in `nova/db/sqlalchemy/migrate_repo/versions/`
2. Migration must be **additive-only** — no column removals or type changes
3. Must work online (zero downtime)
4. Include the `upgrade()` function
5. Update the corresponding object in `nova/objects/` with a version bump
6. Add a unit test for the migration
7. Flag for human review — all DB migrations require core reviewer approval
```

### /nova-releasenote
```markdown
---
description: Generate a Nova release note with reno
user_invocable: true
---
Generate a release note for the current change:
1. Determine the category: feature, bug fix, upgrade, deprecation, security, or other
2. Run `reno new <descriptive-slug>` to create the note file
3. Fill in the appropriate section(s) in the generated YAML:
   - `features:` for new functionality
   - `fixes:` for bug fixes (reference `Closes-Bug: #NNNNNN`)
   - `upgrade:` for changes requiring operator action
   - `deprecations:` for deprecated options/APIs
   - `security:` for vulnerability fixes (reference OSSA/CVE)
4. Keep the note concise — 1-3 sentences per entry
```

### /nova-spec
```markdown
---
description: Look up or summarize a Nova spec from nova-specs
user_invocable: true
---
Find and summarize a Nova spec:
1. Search `specs/` in the nova-specs repo for the topic
   - Check `approved/`, `implemented/`, `backlog/`, and `abandoned/`
2. Summarize:
   - Problem statement
   - Proposed solution
   - Status (approved/implemented/abandoned)
   - Release cycle it targets
3. If no spec exists, note that a new spec may be needed and point to the template:
   `specs/<current-release>-template.rst`
```

### /nova-debug
```markdown
---
description: Diagnose a Nova error from a stack trace or log
user_invocable: true
---
Given an error or stack trace from a Nova service:
1. Identify the service (compute, conductor, scheduler, API) from the trace
2. Identify if it's an RPC error (oslo.messaging timeout, version mismatch)
3. Trace through the manager class to the root cause:
   - ComputeManager: `nova/compute/manager.py:642`
   - ConductorManager: `nova/conductor/manager.py:107`
   - SchedulerManager: `nova/scheduler/manager.py:58`
4. Check if it involves an external service (Neutron, Glance, Cinder, Placement)
5. Check for known periodic task issues (_sync_power_states, update_available_resource)
6. Suggest a fix with minimal code changes
7. If the error is a security issue, flag for private reporting (not public Launchpad)
```

### /nova-explain
```markdown
---
description: Explain a Nova module or class in context
user_invocable: true
---
Explain the specified Nova code in project context:
- Which service does it belong to? (compute, conductor, scheduler, API, virt)
- Where does it sit in the RPC communication flow?
- What periodic tasks does it run (if any)?
- What versioning constraints apply (RPC, objects, API)?
- Which Oslo libraries does it use and why?
- What external services does it interact with?
Keep it under 15 lines unless complexity warrants more.
```

---

## Creating Your Own Skills

1. Create `.claude/skills/` in your Nova project root
2. Add `<skill-name>.md` files with frontmatter
3. Skills are available to anyone working in the repo

### Tips
- Keep skill prompts focused on a single task
- Reference Nova-specific paths (`nova/compute/`, `nova/objects/`, etc.)
- Include versioning checks — they're the most common review blocker
- Test skills against real Nova bugs before sharing with the team
- Skills compose well: `/nova-bugfix` can reference `/nova-test` and `/nova-review`

---

## Skill vs. Hook vs. Memory

| Mechanism | When to use | How it works |
|-----------|-------------|--------------|
| **Skill** | On-demand tasks (`/skill-name`) | User-triggered prompt template |
| **Hook** | Automated reactions to events | Shell commands in settings.json |
| **Memory** | Persistent context across sessions | Files in `.claude/memory/` |
| **CLAUDE.md** | Project onboarding | Loaded every conversation |
