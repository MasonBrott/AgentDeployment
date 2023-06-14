/*
SysinternalsEBPF

Copyright (c) Microsoft Corporation

All rights reserved.

This library is free software; you can redistribute it and/or
modify it under the terms of the GNU Lesser General Public
License as published by the Free Software Foundation; either
version 2.1 of the License, or (at your option) any later version.

This library is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public
License along with this library; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA
*/

#ifndef SYSINTERNALS_EBPF_OFFSETS_H
#define SYSINTERNALS_EBPF_OFFSETS_H

#include <stdbool.h>

#define NUM_REDIRECTS 4
#define DEREF_END -1

// offsets
typedef struct {
    unsigned int       parent[NUM_REDIRECTS];
    unsigned int       pid[NUM_REDIRECTS];
    unsigned int       ppid[NUM_REDIRECTS];
    unsigned int       start_time[NUM_REDIRECTS];
    unsigned int       cred[NUM_REDIRECTS];
    unsigned int       cred_uid[NUM_REDIRECTS];
    unsigned int       cred_gid[NUM_REDIRECTS];
    unsigned int       cred_euid[NUM_REDIRECTS];
    unsigned int       cred_suid[NUM_REDIRECTS];
    unsigned int       cred_fsuid[NUM_REDIRECTS];
    unsigned int       cred_egid[NUM_REDIRECTS];
    unsigned int       cred_sgid[NUM_REDIRECTS];
    unsigned int       cred_fsgid[NUM_REDIRECTS];
    unsigned int       tty[NUM_REDIRECTS];
    unsigned int       comm[NUM_REDIRECTS];
    unsigned int       exe_path[NUM_REDIRECTS];
    unsigned int       mm_arg_start[NUM_REDIRECTS];
    unsigned int       mm_arg_end[NUM_REDIRECTS];
    unsigned int       mm_start_code[NUM_REDIRECTS];
    unsigned int       mm_end_code[NUM_REDIRECTS];
    unsigned int       pwd_path[NUM_REDIRECTS];
    unsigned int       path_vfsmount[NUM_REDIRECTS];
    unsigned int       path_dentry[NUM_REDIRECTS];
    unsigned int       dentry_parent[NUM_REDIRECTS];
    unsigned int       dentry_iname[NUM_REDIRECTS];
    unsigned int       dentry_name[NUM_REDIRECTS];
    unsigned int       dentry_inode[NUM_REDIRECTS];
    unsigned int       inode_mode[NUM_REDIRECTS];
    unsigned int       inode_atime[NUM_REDIRECTS];
    unsigned int       inode_mtime[NUM_REDIRECTS];
    unsigned int       inode_ctime[NUM_REDIRECTS];
    unsigned int       inode_ouid[NUM_REDIRECTS];
    unsigned int       inode_ogid[NUM_REDIRECTS];
    unsigned int       mount_mnt[NUM_REDIRECTS];
    unsigned int       mount_parent[NUM_REDIRECTS];
    unsigned int       mount_mountpoint[NUM_REDIRECTS];
    unsigned int       max_fds[NUM_REDIRECTS];
    unsigned int       fd_table[NUM_REDIRECTS];
    unsigned int       fd_path[NUM_REDIRECTS];
    unsigned int       skb_network_header[NUM_REDIRECTS];
    unsigned int       skb_head[NUM_REDIRECTS];
    unsigned int       skb_data[NUM_REDIRECTS];
    unsigned int       auid[NUM_REDIRECTS];
    unsigned int       ses[NUM_REDIRECTS];
} Offsets;

#endif

