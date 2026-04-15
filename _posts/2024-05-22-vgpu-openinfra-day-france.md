---
layout: single
title: "How can I give virtual GPU resources to my end users seamlessly?"
date: 2024-05-22
categories:
  - Presentations
tags:
  - openstack
  - nova
  - vgpu
  - gpu
---

Presentation given at **OpenInfra Day France 2024** about virtual GPU support in OpenStack Nova — covering VFIO-mdev, SR-IOV GPUs, vGPU live migration, and unified limits.

## Slides

<embed src="/2024/05/22/How%20can%20I%20give%20virtual%20GPU%20resources%20to%20my%20endusers%20seamlessly_.pdf" type="application/pdf" width="100%" height="600px">

[Download PDF](/2024/05/22/How%20can%20I%20give%20virtual%20GPU%20resources%20to%20my%20endusers%20seamlessly_.pdf){: .btn .btn--primary}

## Summary

- **VFIO-mdev**: How the kernel interface exposes GPU profiles (mediated device types) to Nova
- **SR-IOV GPUs** (Caracal): Support for GPUs with virtual functions and the `max_instances` config option
- **vGPU Live Migration**: Requirements (libvirt 8.6+, QEMU 8.1+, kernel 5.18+) and configuration limits
- **Unified Limits**: New quota system using Keystone for VGPU resource quotas

## Demo

During the presentation, I demonstrated GPU-accelerated prime number computation using [numba](https://numba.pydata.org/) with CUDA inside an OpenStack VM with a virtual GPU.

The demo script ([`get_primes.py`](/2024/05/22/get_primes.py)) uses numba's `@vectorize` decorator to run a prime checker on either the GPU (`target='cuda'`) or CPU (`target='parallel'`):

```python
{% raw %}
import numba as nb
import numpy as np

@nb.vectorize(['int32(int32)'], target='cuda')
def check_prime_gpu(num):
    for i in range(2, (num // 2) + 1):
       if (num % i) == 0:
           return 0
    return num

@nb.vectorize(['int32(int32)'], target='parallel')
def check_prime_no_gpu(num):
    for i in range(2, (num // 2) + 1):
       if (num % i) == 0:
           return 0
    return num
{% endraw %}
```

### Terminal recordings

The following recordings show the live demo on a server with an NVIDIA Quadro RTX 6000 GPU.

#### Part 1: GPU setup and nvidia-smi

<link rel="stylesheet" type="text/css" href="https://cdn.jsdelivr.net/npm/asciinema-player@3.8.2/dist/bundle/asciinema-player.css" />

<div id="demo-part1"></div>

#### Part 2: Creating vGPU mediated devices

<div id="demo-part2"></div>

#### Part 3: Launching a VM with vGPU

<div id="demo-part3"></div>

#### Part 4: Running get_primes.py with GPU

<div id="demo-part4"></div>

#### Part 5: Performance comparison (GPU vs CPU)

<div id="demo-part5"></div>

#### Part 6: SR-IOV GPU demo

<div id="demo-part6"></div>

<script src="https://cdn.jsdelivr.net/npm/asciinema-player@3.8.2/dist/bundle/asciinema-player.min.js"></script>
<script>
  const opts = {cols: 120, rows: 30, fit: 'width', idleTimeLimit: 3, speed: 2};
  AsciinemaPlayer.create('/2024/05/22/asciicasts/demo_part1.cast', document.getElementById('demo-part1'), opts);
  AsciinemaPlayer.create('/2024/05/22/asciicasts/demo_part2.cast', document.getElementById('demo-part2'), opts);
  AsciinemaPlayer.create('/2024/05/22/asciicasts/demo_part3.cast', document.getElementById('demo-part3'), opts);
  AsciinemaPlayer.create('/2024/05/22/asciicasts/demo_part4.cast', document.getElementById('demo-part4'), opts);
  AsciinemaPlayer.create('/2024/05/22/asciicasts/demo_part5.cast', document.getElementById('demo-part5'), opts);
  AsciinemaPlayer.create('/2024/05/22/asciicasts/demo_part6.cast', document.getElementById('demo-part6'), opts);
</script>
