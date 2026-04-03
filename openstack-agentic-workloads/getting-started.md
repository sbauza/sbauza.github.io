---
layout: page
title: "Getting Started"
---

This guide walks you through setting up OpenStack for running agentic AI workloads.

## Prerequisites

- An OpenStack deployment with Nova, Placement, Neutron, and Glance services
- At least one compute node with GPU resources (for vGPU workloads)
- Admin access to create flavors and manage resources

## Step 1: Configure GPU Resources

Register vGPU resources in Placement so Nova can schedule GPU workloads:

```bash
# Verify GPU inventory on compute nodes
openstack resource provider inventory list <compute-node-uuid>

# Check available vGPU resource classes
openstack resource class list | grep VGPU
```

## Step 2: Create an Agent Flavor

Create a Nova flavor tailored for AI agent workloads:

```bash
openstack flavor create agent-gpu \
  --vcpus 4 --ram 8192 --disk 40 \
  --property resources:VGPU=1
```

For CPU-only agents:

```bash
openstack flavor create agent-cpu \
  --vcpus 2 --ram 4096 --disk 20
```

## Step 3: Prepare an Agent Image

Upload a base image with your agent runtime pre-installed:

```bash
openstack image create agent-base \
  --file ubuntu-agent.qcow2 \
  --disk-format qcow2 \
  --container-format bare
```

## Step 4: Launch an Agent Instance

```bash
openstack server create my-agent \
  --flavor agent-gpu \
  --image agent-base \
  --network agent-net \
  --key-name my-key
```

## Step 5: Verify

```bash
# Check instance status
openstack server show my-agent -f value -c status

# Get console access
openstack console url show my-agent
```

## Next Steps

- Configure auto-scaling for agent workloads
- Set up monitoring and logging
- Explore [live migration](../vgpu/vgpu_live_migration.html) for GPU workloads

Back to [OpenStack Agentic Workloads](./)
