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

## Evidence and limits

- [Source and current status matrix](https://github.com/shubhamtrivedi95/yocto-board-lab/tree/develop)
- [Board build configurations](https://github.com/shubhamtrivedi95/yocto-board-lab/tree/develop/kas/boards)
- [Board documentation](https://github.com/shubhamtrivedi95/yocto-board-lab/tree/develop/docs)

The README reports boot results for several boards and explicitly records pending AI validation, QEMU wrapper issues, and uncompleted targets. Those are repository-reported observations, not independent validation performed for this portfolio. RISC-V and further BSP exploration remain ongoing work.

## Related work

The same concepts underpin my [Yocto knowledge-sharing sessions](/posts/yocto-bootcamps.html).
