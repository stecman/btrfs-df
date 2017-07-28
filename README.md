# BTRFS subvolume/snapshot size with paths

List BTRFS subvolume space use information similar to `df -h` with paths displayed.

Normally, `btrfs qgroup show` lists subvolumes, but only by id:

```
$ btrfs qgroup show /mnt/somebtrfsvol --human-readable --sort=-excl

qgroupid         rfer         excl
--------         ----         ----
0/2317      848.55GiB     24.35GiB
0/3217      883.62GiB     16.04GiB
0/1998      840.20GiB     16.01GiB
0/489       160.81GiB      8.01GiB
0/7125      227.62GiB      2.21GiB
0/7202      230.20GiB    982.49MiB
```

This script saves looking up path information with `btrfs subvolume list` as paths
are included added the output:

```
$ ./btrfs-subvolumes.py /mnt/somebtrfsvol --human-readable --sort=-excl

path                                        qgroupid         rfer         excl
----                                        --------         ----         ----
Photos/Photos.20160703                      0/2317      848.55GiB     24.35GiB
Photos/Photos.20161106                      0/3217      883.62GiB     16.04GiB
Photos/Photos.20160605                      0/1998      840.20GiB     16.01GiB
Archive/Archive.20160504                    0/489       160.81GiB      8.01GiB
timemachine/timemachine.20170716            0/7125      227.62GiB      2.21GiB
timemachine/timemachine.20170723            0/7202      230.20GiB    982.49MiB
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
or use the original version of the script [here](https://github.com/stecman/btrfs-df/commit/096f480cad6ba5c0573d9523093195a1e33f5808).

This was originally based on [a shell script that was too slow](https://github.com/agronick/btrfs-size).
