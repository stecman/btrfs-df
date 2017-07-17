#!/usr/bin/env python3

# List BTRFS subvolume space use information similar to df -h (with snapshot paths)
#
# Btrfsprogs is able to list and sort snapshots on a volume, but it only prints their
# id, not their path. This script wraps `btrfs qgroup show` to add filesystem paths
# to the generated table.
#
# For this to work on a BTRFS volume, you first need to enable quotas on the volume:
#
#    btrfs quota enable /mnt/some-volume
#
# Note that the current version of this script does not allow sorting by path, as it
# passes all arugments through to btrfsprogs. If you need that and don't mind being
# limited to only sorting by path, see this previous version:
#
#    https://gist.github.com/stecman/3fd04a36111874f67c484c74e15ef311/6690edbd6a88380a1712024bb4115969b2545509
#
# This is based on a shell script that was too slow:
# https://github.com/agronick/btrfs-size

from __future__ import print_function

import subprocess
import sys
import os
import re

def get_btrfs_subvols(path):
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

def get_data_raw(args):
    """Return lines of output from a call to 'btrfs qgroup show' with args appended"""
    try:
        # Get the lines of output, ignoring the two header lines
        raw = subprocess.check_output(["btrfs", "qgroup", "show"] + args)
        return raw.decode("utf8").split("\n")

    except subprocess.CalledProcessError as e:
        if e.returncode != 0:
            print("\nFailed to get subvolume quotas. Have you enabled quotas on this volume?")
            print("(You can do so with: sudo btrfs quota enable <path-to-volume>)")
            sys.exit(1)

def get_qgroup_id(line):
    """Extract qgroup id from a line of btrfs qgroup show output
    Returns None if the line wasn't valid
    """
    id_match = re.match(r"\d+/(\d+)", line)

    if not id_match:
        return None

    return id_match.group(1)

def guess_path_argument(argv):
    """Return an argument most likely to be the <path> arg for 'btrfs qgroup show'
    This is a cheap way to pass through to btrfsprogs without duplicating the options here.
    Currently only easier than duplication because the option/argument list is simple.
    """
    # Path can't be the first argument (program)
    args = argv[1:]

    # Filter out arguments to options
    # Only the sort option currently takes an argument
    option_follows = [
        "--sort"
    ]

    for text in option_follows:
        try:
            position = args.index(text)
            del args[position + 1]
        except:
            pass

    # Ignore options
    args = [arg for arg in args if re.match(r"^-", arg) is None]

    # Prefer the item at the end of the list as this is the suggested argument order
    return args[-1]


# Re-run the script as root if started with a non-priveleged account
if os.getuid() != 0:
    cmd = 'sudo "' + '" "'.join(sys.argv) + '"'
    sys.exit(subprocess.call(cmd, shell=True))


# Fetch command output to work with
output = get_data_raw(sys.argv[1:])
subvols = get_btrfs_subvols(guess_path_argument(sys.argv))

# Data for the new column
path_column = [
    "path",
    "----"
]

# Iterate through all lines except for the table header
for index,line in enumerate(output):
    # Ignore header rows
    if index < 1:
        continue

    groupid = get_qgroup_id(line)

    if groupid in subvols:
        path_column.append(subvols[groupid])
    else:
        path_column.append("")

# Find the required width for the new column
column_width = len(max(path_column, key=len)) + 2

# Output data with extra column for path
for index,line in enumerate(output):
    print(path_column[index].ljust(column_width) + output[index])