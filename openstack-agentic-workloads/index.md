---
layout: page
title: "OpenStack Agentic Workloads"
---

This project explores running AI agent workloads on OpenStack infrastructure, leveraging Nova's compute capabilities to provision and manage virtual machines for autonomous AI agents.

## Overview

Agentic workloads are AI-driven processes that autonomously execute tasks, make decisions, and interact with their environment. OpenStack provides the ideal infrastructure layer for running these workloads at scale.

### Key Capabilities

- **VM provisioning** for isolated agent environments
- **GPU passthrough** via vGPU for accelerated inference
- **Dynamic scaling** based on workload demand
- **Network isolation** between agent instances

## Architecture

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  Agent API   │────▶│  Nova        │────▶│  Compute     │
│  (Orchestr.) │     │  (Scheduler) │     │  (Hypervisor)│
└──────────────┘     └──────────────┘     └──────────────┘
       │                                         │
       ▼                                         ▼
┌──────────────┐                          ┌──────────────┐
│  Placement   │                          │  Agent VM    │
│  (Resources) │                          │  (Workload)  │
└──────────────┘                          └──────────────┘
```

## Quick Start

1. Deploy an OpenStack cloud with Nova and Placement services
2. Configure a flavor with GPU resources for agent workloads:
   ```bash
   openstack flavor create agent-gpu \
     --vcpus 4 --ram 8192 --disk 40 \
     --property resources:VGPU=1
   ```
3. Launch an agent instance:
   ```bash
   openstack server create my-agent \
     --flavor agent-gpu \
     --image ubuntu-22.04 \
     --network agent-net
   ```

## How It Works

The system uses Nova's scheduling and placement services to match agent workload requirements with available compute resources:

- **Placement API** tracks GPU inventory across compute nodes
- **Nova Scheduler** selects the best host based on resource availability
- **Live migration** enables workload rebalancing without agent downtime
