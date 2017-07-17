# BTRFS subvolume/snapshot size with paths

List BTRFS subvolume space use information similar to `df -h` with paths displayed.

Normally, `btrfs qgroup show` lists subvolumes, but only by id:

```
qgroupid         rfer         excl
--------         ----         ----
0/259       107.56GiB    107.56GiB
0/2317      848.55GiB     24.35GiB
0/3217      883.62GiB     16.04GiB
0/1998      840.20GiB     16.01GiB
0/489       160.81GiB      8.01GiB
0/5137      146.49GiB      2.06GiB
0/5083      145.47GiB    999.45MiB
```

This script saves looking up path information with `btrfs subvolume list` as paths
are included added the output:

```
path                                        qgroupid         rfer         excl
----                                        --------         ----         ----
???                                         0/259       107.56GiB    107.56GiB
backup/timemachine.20160427                 0/2317      848.55GiB     24.35GiB
Photos/Photos.20160703                      0/3217      883.62GiB     16.04GiB
Photos/Photos.20161106                      0/1998      840.20GiB     16.01GiB
Photos/Photos.20160605                      0/489       160.81GiB      8.01GiB
Archive/Archive.20160504                    0/5137      146.49GiB      2.06GiB
timemachine/timemachine.20170204            0/5083      145.47GiB    999.45MiB
```

## Usage

For this to work on a BTRFS volume, you first need to enable quotas on the volume:

   btrfs quota enable /mnt/some-volume

All arguments are passed through to `btrfs qgroup show`, so you can get started with:

```bash
./btrfs-subvolumes.py /mnt/some-volume -h
```

## Notes

The current version of this script does not allow sorting by path as it passes
all arugments through to btrfsprogs. If you need sorting by path, either submit a PR
or use the original version of the script.

This was originally based on [a shell script that was too slow](https://github.com/agronick/btrfs-size).
