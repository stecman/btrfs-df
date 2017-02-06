#!/usr/bin/env python3

# List BTFS subvolume space use information similar to `df -h`
#
# Note: this requires the "hurry.filesize" module. Install it with:
#
#     pip install hurry.filesize
#
# This is rewritten from a shell script that was too slow:
# https://github.com/agronick/btrfs-size

from __future__ import print_function

from hurry.filesize import size

import argparse
import subprocess
import sys
import os
import re

parser = argparse.ArgumentParser(description="List subvolume and snapshot sizes on BTRFS volumes")
parser.add_argument("path", help="Path or UUID of the BTRFS volume to inspect")
parser.add_argument(
    "-s",
    dest="sort",
    choices=[
        "exclusive",
        "total"
    ],
    help="Sort output instead of using the order from btrfs"
)


class BtrfsQuota:
    def __init__(self, raw_id, total_bytes, exclusive_bytes):
        self.id = raw_id.split("/")[1]
        self.total_bytes = int(total_bytes)
        self.exclusive_bytes = int(exclusive_bytes)

def btrfs_subvols_get(path):
    """Return a dictionary of subvolume names indexed by their subvolume ID"""
    try:
        raw = subprocess.check_output(["btrfs", "subvolume", "list", path])
        volumes = re.findall(r'^ID (\d+) .* path (.*)$', raw.decode("utf8"), re.MULTILINE)

        return dict(volumes)

    except subprocess.CalledProcessError as e:
        if e.returncode != 0:
            print("\nFailed to list subvolumes")
            print("Is '%s' really a BTRFS volume?" % path)
            sys.exit(1)

def btrfs_quotas_get(path):
    """Return a list of BtrfsQuota objects for path"""
    try:
        # Get the lines of output, ignoring the two header lines
        raw = subprocess.check_output(["btrfs", "qgroup", "show", "--raw", path])
        lines = raw.decode("utf8").split("\n")[2:]

        return [BtrfsQuota(*line.split()) for line in lines if line != '']

    except subprocess.CalledProcessError as e:
        if e.returncode != 0:
            print("\nFailed to get subvolume quotas. Have you enabled quotas on this volume?")
            print("(You can do so with: sudo btrfs quota enable '%s')" % path)
            sys.exit(1)

def print_table(subvols, quotas):
    # Get the column size right for the path
    max_path_length = 0
    for path in subvols.values():
        max_path_length = max(len(path), max_path_length)

    template = "{path:<{path_len}}{bytes:>16}{exclusive:>16}"

    # Print table header
    header = template.format(
        path="Subvolume",
        bytes="Total size",
        exclusive="Exclusive size",
        path_len=max_path_length
    )

    print(header)
    print("-" * len(header))

    # Print table rows
    for quota in quotas:
        if quota.id in subvols:
            print(template.format(
                path_len=max_path_length,
                path=subvols[quota.id],
                bytes=size(quota.total_bytes),
                exclusive=size(quota.exclusive_bytes)
            ))


# Re-run the script as root if started with a non-priveleged account
if os.getuid() != 0:
    cmd = 'sudo "' + '" "'.join(sys.argv) + '"'
    sys.exit(subprocess.call(cmd, shell=True))

args = parser.parse_args()

subvols = btrfs_subvols_get(args.path)
quotas = btrfs_quotas_get(args.path)

if args.sort == "exclusive":
    quotas.sort(key=lambda q: q.exclusive_bytes, reverse=True)
elif args.sort == "bytes":
    quotas.sort(key=lambda q: q.total_bytes, reverse=True)

print_table(subvols, quotas)
