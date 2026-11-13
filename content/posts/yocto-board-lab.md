---
{
  "title": "yocto-board-lab: reproducible multi-board Linux builds",
  "summary": "A public lab for board metadata, kas configurations, image building, and platform validation.",
  "category": "project",
  "status": "In development",
  "featured": true
}
---

## Engineering goal

Keep board configuration, build tooling, and bring-up notes together so that experiments across embedded platforms can be reproduced and compared.

## What is available

The public repository contains board-specific documentation and build commands using kas and a container wrapper. The README covers BeagleBone Black, BeagleY-AI, Raspberry Pi 5, FRDM-iMX8MP, and Radxa Zero 3W, with other targets under evaluation.

## Explore the repository

- [Source and current status matrix](https://github.com/shubhamtrivedi95/yocto-board-lab/tree/develop)
- [Board build configurations](https://github.com/shubhamtrivedi95/yocto-board-lab/tree/develop/kas/boards)
- [Board documentation](https://github.com/shubhamtrivedi95/yocto-board-lab/tree/develop/docs)

## Current status

The README tracks boot results for each board alongside open items, such as pending AI validation, QEMU wrapper issues, and targets still in progress. RISC-V support and further BSP exploration are next on the roadmap.

## Related work

The same concepts underpin my [Yocto knowledge-sharing sessions](/posts/yocto-bootcamps.html).
