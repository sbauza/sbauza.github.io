# AGENTS.md — OpenStack Nova

## Project Overview

Nova is OpenStack's compute service for provisioning and managing virtual machines. It is a large, mission-critical Python project with strict compatibility, versioning, and review requirements.

- **Repository**: https://opendev.org/openstack/nova (NOT GitHub — GitHub is a mirror only)
- **Bug tracking**: https://bugs.launchpad.net/nova
- **Code review**: Gerrit at https://review.opendev.org (not GitHub PRs)
- **Docs**: https://docs.openstack.org/nova/latest/
- **Architecture decisions**: Tracked in **nova-specs** (`openstack/nova-specs`):
  - `specs/<release>/approved/` — accepted specs for a given release cycle
  - `specs/<release>/implemented/` — specs that have landed in code
  - `specs/backlog/` — approved ideas not yet targeted to a release
  - `specs/abandoned/` — withdrawn or superseded proposals
  - Releases span from Juno (2014) through the current cycle (2026.2)

## Directory Structure

```
nova/
├── api/          # REST API endpoints and WSGI apps
├── compute/      # Compute service core
├── conductor/    # Conductor service (centralized DB operations)
├── scheduler/    # VM scheduling logic
├── virt/         # Virtualization drivers (libvirt, vmwareapi, ironic, zvm)
├── network/      # Neutron integration
├── storage/      # Storage backends
├── db/           # Database layer and migrations
├── objects/      # Versioned data objects (ORM-like)
├── cmd/          # CLI entry points
├── conf/         # All configuration option definitions
├── policies/     # Policy registration
├── pci/          # PCI passthrough support
├── console/      # Console access
├── image/        # Glance integration
├── notifications/# Event notifications
├── privsep/      # Privileged operations (rootwrap)
├── hacking/      # Custom flake8 lint checks (N-codes)
├── tests/        # Unit and functional tests
│   ├── unit/
│   └── functional/
```

---

## Core Services

Nova uses a distributed microservices architecture where long-running daemon processes communicate via RPC messaging. Each service registers itself in the database, listens on a topic-based message queue, and runs periodic background tasks.

### nova-compute (Compute Agent)
- **Manager**: `nova/compute/manager.py:642` — `ComputeManager`
- **Runs on**: Every compute (hypervisor) node
- **Role**: Manages the full VM lifecycle — build, run, migrate, snapshot, destroy
- Communicates with hypervisors via pluggable virt drivers (`nova/virt/`): libvirt (KVM, Xen, LXC), VMware, Ironic, zVM
- Never accesses the database directly — proxies all DB operations through nova-conductor
- Integrates with: Neutron (networking), Cinder (volumes), Glance (images), Manila (shares), Placement (resource inventory)
- Runs ~17 periodic tasks including:
  - `_sync_power_states` — reconcile hypervisor power state with DB
  - `update_available_resource` — report compute node resources to Placement
  - `_heal_instance_info_cache` — refresh network info from Neutron
  - `_poll_shelved_instances` — clean up expired shelved instances
  - `_cleanup_incomplete_migrations` — finish incomplete migration cleanup
- Concurrency controls: semaphores for builds/snapshots, dedicated executor for live migrations
- Transitioning from Eventlet to native threads (`nova/compute/manager.py:679`)
- Scaling: Single process per host (except VMware/Ironic drivers)
- RPC API version: `6.5`

### nova-scheduler
- **Manager**: `nova/scheduler/manager.py:58` — `SchedulerManager`
- **Runs on**: Controller node(s)
- **Role**: Selects the best host to place a new or migrating instance
- Uses `HostManager` (`nova/scheduler/host_manager.py:341`) to track compute node state
- Queries Placement API for allocation candidates matching resource requirements
- Applies request filters (`nova/scheduler/request_filter.py`) and weighers (`nova/weights.py`)
- Interacts with `servicegroup` API to determine host liveness
- Scaling: Multiple workers, stateless
- RPC API version: `4.5`

### nova-conductor
- **Manager**: `nova/conductor/manager.py:107` — `ConductorManager`
- **Runs on**: Controller node(s)
- **Role**: Database proxy and orchestrator for long-running workflows
- Mediates all database access for nova-compute (security boundary)
- Handles object serialization/versioning across RPC (rolling upgrades)
- Contains `ComputeTaskManager` (`nova/conductor/manager.py:254`) for complex orchestration:
  - Instance builds, cold migrations, live migrations, resize, evacuate
  - Cross-cell migrations (`nova/conductor/tasks/cross_cell_migrate.py`)
- Scaling: Horizontal — multiple workers
- Variants:
  - **Per-cell conductor**: Manages operations within a single cell
  - **Super conductor**: API-level conductor that coordinates across cells
- RPC API version: `3.0`

### nova-api (WSGI)
- **Entry point**: `nova/cmd/compute.py`
- **Runs on**: Controller node(s)
- **Role**: REST API frontend for all user/operator interactions
- Validates requests, enforces policy and quota
- Delegates to conductor/scheduler via RPC for state-changing operations
- Supports microversioned API for backwards compatibility
- Scaling: Multiple WSGI workers behind a load balancer

### nova-metadata (WSGI)
- Serves instance metadata (cloud-init config, SSH keys) to VMs via the metadata service

### Console Proxies

| Service | Entry Point | Protocol |
|---------|-------------|----------|
| nova-novncproxy | `nova/cmd/novncproxy.py` | VNC/WebSocket |
| nova-spicehtml5proxy | `nova/cmd/spicehtml5proxy.py` | SPICE/WebSocket |
| nova-serialproxy | `nova/cmd/serialproxy.py` | Serial/WebSocket |

---

## Service Architecture

### Base Manager Pattern
All major services inherit from `nova/manager.py:89` — `Manager`:

```
Manager(PeriodicTasks)
  ├── init_host()         # startup initialization
  ├── pre_start_hook()    # before RPC consumers start
  ├── post_start_hook()   # after service is "running"
  ├── periodic_tasks()    # run background tasks on interval
  ├── graceful_shutdown() # clean stop
  ├── cleanup_host()      # teardown on shutdown
  └── reset()             # SIGHUP handler for live reconfig
```

### Service Registration (`nova/service.py:50`)

```python
SERVICE_MANAGERS = {
    'nova-compute':    'nova.compute.manager.ComputeManager',
    'nova-conductor':  'nova.conductor.manager.ConductorManager',
    'nova-scheduler':  'nova.scheduler.manager.SchedulerManager',
}
```

Each service creates a `Service` DB record with host, binary, topic, and version. Services heartbeat via `servicegroup` (`nova/servicegroup/api.py:37`) to signal liveness.

### RPC Communication (`nova/rpc.py`)
- Built on `oslo.messaging`
- Topic-based routing: each service listens on its binary name as the topic
- Supports `call` (synchronous) and `cast` (async fire-and-forget)
- Heartbeating enabled when `rpc_response_timeout > 60s` (`nova/rpc.py:58`)
- Versioned RPC endpoints allow rolling upgrades (old compute + new conductor)

### Communication Flow

```
User -> nova-api -> [RPC/oslo.messaging] -> nova-conductor -> nova-scheduler
                                                |
                                                v
                                           nova-compute -> hypervisor
                                                |
                                                v
                                           nova-conductor -> database
```

### Periodic Tasks
- Decorated with `@periodic_task.periodic_task` from `oslo.service`
- Configurable intervals via `nova.conf` (e.g., `sync_power_state_interval`, `update_resources_interval`)
- Fuzzy delay at startup prevents thundering herd (`periodic_fuzzy_delay`)
- `ComputeManager` has the most periodic tasks (~17), covering resource sync, cache healing, cleanup

---

## Multi-Cell Architecture (Cells v2)

```
                    API cell
                 (super conductor)
                /        |        \
           Cell A      Cell B     Cell C
        (conductor)  (conductor)  (conductor)
        (computes)   (computes)   (computes)
        (msg queue)  (msg queue)  (msg queue)
        (cell DB)    (cell DB)    (cell DB)
```

- **API cell**: Global database with instance-to-cell mappings
- **Cell N**: Each cell has its own database and message queue (isolated failure domain)
- **Cell0**: Special cell for instances that failed to schedule
- **Super conductor**: API-level conductor that routes across cells
- **Per-cell conductor**: Handles operations within a single cell

---

## Virt Drivers (`nova/virt/`)

| Driver | Directory | Use Case |
|--------|-----------|----------|
| libvirt | `nova/virt/libvirt/` | KVM, QEMU, Xen, LXC (primary) |
| VMware | `nova/virt/vmwareapi/` | vSphere integration |
| Ironic | `nova/virt/ironic/` | Bare-metal provisioning |
| z/VM | `nova/virt/zvm/` | IBM z/VM mainframes |
| Fake | `nova/virt/fake.py` | Testing and CI |

---

## Versioning Rules (Critical for Agents)

These are hard constraints that agents must never violate:

- **RPC methods**: Any modification requires a version bump. New arguments must be optional.
- **Objects**: Attribute or method changes require version increments. Wireline stability is required for live upgrades.
- **Database schema**: Changes must be additive-only. No column removals or type alterations. Migrations must work online (no downtime).
- **Microversions**: API changes require a new microversion with simultaneous client and Tempest updates.

---

## Concurrency Model

Nova is transitioning from **Eventlet** green threads to **native OS threads**:
- `executor_thread_pool_size` — RPC executor thread pool
- `cell_worker_thread_pool_size` — cell-level worker threads
- `sync_power_state_pool_size` — power state sync parallelism
- `ComputeManager` uses `_long_task_executor` for builds/snapshots and a separate `_live_migration_executor`

---

## Key External Dependencies

| Service | Purpose | Nova Integration |
|---------|---------|-----------------|
| Keystone | Identity/Auth | `keystoneauth1` for service credentials |
| Placement | Resource inventory & claims | `SchedulerReportClient` in compute + scheduler |
| Neutron | Networking | `nova/network/neutron.py` |
| Glance | VM images | `nova/image/glance.py` |
| Cinder | Block storage | `nova/volume/` |
| Manila | Shared filesystems | `nova/share/` |
| Cyborg | Accelerators (GPUs, FPGAs) | `nova/accelerator/cyborg.py` |

---

## Oslo Libraries

Nova depends on a shared set of OpenStack Oslo libraries (`requirements.txt`) that provide cross-project infrastructure:

| Library | Purpose |
|---------|---------|
| `oslo.messaging` | RPC and notification transport (RabbitMQ, Kafka) |
| `oslo.service` | Daemon lifecycle, periodic tasks, thread management |
| `oslo.config` | Configuration file parsing and CLI options |
| `oslo.db` | Database session management, migrations, model utilities |
| `oslo.policy` | RBAC policy enforcement for API requests |
| `oslo.versionedobjects` | Serializable objects with schema versioning (rolling upgrades) |
| `oslo.concurrency` | File locking, external process management |
| `oslo.privsep` | Privilege separation — run specific operations as root safely |
| `oslo.rootwrap` | Legacy root command wrapper (being replaced by privsep) |
| `oslo.cache` | Caching layer (memcached/Redis backends) |
| `oslo.context` | Request context propagation (user, project, roles) |
| `oslo.log` | Structured logging with context-aware formatters |
| `oslo.middleware` | WSGI middleware (CORS, request ID, healthcheck) |
| `oslo.serialization` | JSON/MessagePack serialization helpers |
| `oslo.utils` | Common utilities (time, import, network, string helpers) |
| `oslo.i18n` | Internationalization and string translation |
| `oslo.limit` | Unified limit enforcement (quota system) |
| `oslo.reports` | Guru meditation reports for debugging live processes |
| `oslo.upgradecheck` | Pre-upgrade validation CLI (`nova-status upgrade check`) |

---

## Vulnerability Management

Nova follows the OpenStack Vulnerability Management process:

- **OSSA (OpenStack Security Advisory)**: Published for confirmed vulnerabilities in supported releases (e.g., `OSSA-2017-005`)
- **CVEs**: Tracked and referenced in release notes under "Security Issues" sections (`releasenotes/source/<release>.rst`)
- **Reporting**: Security issues are reported privately to the OpenStack Security team (not via public bug trackers)
- **Hardening guide**: `doc/source/admin/security.rst` covers metadata encryption, secure boot, and TLS for live migration
- **Security scanning**: `bandit` is used for static analysis of security issues
- **Key security boundaries**:
  - nova-compute has **no direct DB access** — conductor mediates all queries
  - `oslo.policy` enforces RBAC on every API call
  - `oslo.privsep` / `oslo.rootwrap` limit privileged operations to specific allow-listed commands
  - Console proxy tokens prevent unauthorized VNC/SPICE access

---

## Running Tests

```bash
# Unit tests (primary — always run before submitting)
tox -e py3

# Specific test file or class
tox -e py3 -- nova/tests/unit/path/to/test_file.py
tox -e py3 -- nova.tests.unit.path.to.test_file.TestClassName

# Functional tests
tox -e functional

# API sample tests
tox -e api-samples
```

The test runner is `stestr`. Inside a tox env you can also run:
```bash
stestr run <test_path>
```

## Linting and Style

```bash
# Full lint check (preferred)
tox -e pre-commit

# Or directly
pre-commit run --all-files --show-diff-on-failure

# Fast check on recent changes only
bash tools/flake8wrap.sh -HEAD

# Type checking
tox -e mypy
```

---

## Critical Coding Conventions

### Imports and modules
- **No database imports in virt drivers** (N307)
- **No cross-driver imports** — use common modules (N311)
- **No config borrowing** from other drivers (N312)
- Privilege escalation must use explicit paths: `import nova.privsep.path` (N362)
- Mock must come from `unittest.mock` (N371)

### Configuration and policy
- **All config options go in `nova/conf/`** (N342)
- **All policies go in `nova/policies/`** (N350)
- Help strings must be capitalized (N313)

### Time, concurrency, UUIDs
- Use `timeutils.utcnow()` — never `datetime.datetime.utcnow()` (N310)
- Use `nova.utils.spawn()` — never raw greenthread/eventlet (N340)
- Use `nova.utils.cooperative_yield()` for yielding (N374)
- Use `nova.utils.ReaderWriterLock()` — not eventlet/fasteners (N369)
- UUIDs via `oslo_utils.uuidutils` or `uuidsentinel` (N357)

### Logging
- Log messages must NOT be translated (N319)
- Use `LOG.warning` not `LOG.warn` (N352)
- Do not pass context objects to logging (N353)

### Testing
- Use `self.assertIsInstance()` not `assertTrue(isinstance())` (N316/N317)
- Use `self.assertIn/NotIn()` not `assertTrue(x in y)` (N334)
- Use `assertIs/assertIsNot` for identity checks (N356)
- No mutable default arguments (N322)
- New features MUST have unit tests
- Bug fixes MUST have tests that fail before the fix and pass after

### REST API
- Use "project" not "tenant", "server" not "instance"
- URLs use hyphens; request bodies use snake_case
- 201 for synchronous creation, 202 for async
- API version decorators must be the first decorator (N332)

---

## Commit and Review Process

- Nova uses **Gerrit**, not GitHub PRs.
- Third-party CI must vote +1 before core approval on driver changes.
- Release notes are mandatory for upgrade, security, or feature-impacting changes (use `reno`).
- Follow OpenStack commit message conventions: reference Launchpad bug IDs with `Closes-Bug: #NNNNNN` or `Related-Bug: #NNNNNN`.

---

## Agent Workflows

### Bug fix workflow
1. Read the bug report on Launchpad
2. Reproduce with a failing test
3. Implement the fix
4. Run `tox -e py3 -- <relevant_test_path>` to verify
5. Run `tox -e pre-commit` for lint
6. Ensure no versioning rules are violated

### Feature workflow
1. Check for an approved blueprint/spec
2. Write unit tests documenting expected usage
3. Implement the feature
4. Add release notes via `reno new <slug>`
5. Run full unit and functional test suites
6. Run lint

### Safe operations (agents can do freely)
- Read any file
- Run unit tests
- Run linters
- Search the codebase
- Generate diffs for review

### Operations requiring human review
- Any database migration
- RPC or object version bumps
- REST API microversion changes
- Changes to `nova/conf/` defaults
- Changes to `nova/policies/` defaults
- Anything touching `nova/privsep/`

---

## Dev Environment Setup

```bash
# Clone
git clone https://opendev.org/openstack/nova.git
cd nova

# Install system deps
tox -e bindep   # lists required system packages

# Run tests (creates virtualenv automatically)
tox -e py3

# Install pre-commit hooks
pip install pre-commit
pre-commit install
```
