#!/usr/bin/python3.8
import sys
import psutil
from psutil._common import bytes2human
import time


def discfunc():
    partitions = []
    # print(templ % ("Device", "Total", "Used", "Free", "Use ", "Type",  "Mount"))
    for part in psutil.disk_partitions(all=False):
        usage = psutil.disk_usage(part.mountpoint)
        disc = [part.device, bytes2human(usage.total), bytes2human(usage.used), bytes2human(usage.free), int(usage.percent), part.fstype, part.mountpoint]
        partitions.append(disc)
    return partitions


def uptime():
    uptimesec = time.time() - psutil.boot_time()
    return round(uptimesec/60)


if __name__ == '__main__':
    sys.exit(discfunc())
