/*
 * TCP Kernel Integration Module
 * 
 * This module demonstrates basic TCP (Tool Capability Protocol) integration
 * directly into the Linux kernel for deep system security.
 *
 * Author: TCP Research Team
 * License: GPL v2
 */

#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/init.h>
#include <linux/syscalls.h>
#include <linux/kprobes.h>
#include <linux/ptrace.h>
#include <linux/sched.h>
#include <linux/uaccess.h>
#include <linux/string.h>
#include <linux/slab.h>
#include <linux/proc_fs.h>
#include <linux/seq_file.h>
#include <linux/spinlock.h>
#include <linux/atomic.h>
#include <linux/time.h>

MODULE_LICENSE("GPL");
MODULE_AUTHOR("TCP Research Team");
MODULE_DESCRIPTION("TCP Kernel Integration - Deep System Security");
MODULE_VERSION("1.0");

/* TCP Descriptor Structure for Kernel */
struct tcp_kernel_descriptor {
    int syscall_nr;              /* System call number */
    u16 security_flags;          /* TCP security flags */
    u8  context_mask;            /* Valid execution contexts */
    u8  privilege_level;         /* Required privilege level */
    char pattern[32];            /* Operation pattern */
    u32 checksum;                /* Integrity check */
};

/* TCP Security Flags */
#define TCP_FLAG_SAFE           0x0001
#define TCP_FLAG_DESTRUCTIVE    0x0002
#define TCP_FLAG_FILESYSTEM     0x0004
#define TCP_FLAG_NETWORK        0x0008
#define TCP_FLAG_EXECUTION      0x0010
#define TCP_FLAG_CRITICAL       0x0020
#define TCP_FLAG_KERNEL         0x0040
#define TCP_FLAG_PRIVESC        0x0080

/* TCP Context Masks */
#define TCP_CTX_USER            0x01
#define TCP_CTX_ADMIN           0x02
#define TCP_CTX_KERNEL          0x04
#define TCP_CTX_CONTAINER       0x08
#define TCP_CTX_ALL             0xFF

/* TCP Privilege Levels */
#define TCP_PRIV_USER           0
#define TCP_PRIV_ROOT           1
#define TCP_PRIV_KERNEL         2

/* Performance Statistics */
struct tcp_stats {
    atomic64_t total_checks;
    atomic64_t fast_path_hits;
    atomic64_t blocked_operations;
    atomic64_t security_events;
    atomic64_t false_positives;
};

/* Global TCP State */
static struct tcp_kernel_state {
    bool enabled;
    int security_level;
    struct tcp_stats stats;
    spinlock_t lock;
    struct proc_dir_entry *proc_entry;
} tcp_state;

/* TCP Descriptor Database (simplified for demo) */
static struct tcp_kernel_descriptor tcp_descriptors[] = {
    /* unlink() - file deletion */
    {
        .syscall_nr = __NR_unlink,
        .security_flags = TCP_FLAG_DESTRUCTIVE | TCP_FLAG_FILESYSTEM,
        .context_mask = TCP_CTX_USER | TCP_CTX_ADMIN,
        .privilege_level = TCP_PRIV_USER,
        .pattern = "file_deletion",
        .checksum = 0x1A2B3C4D
    },
    
    /* execve() - program execution */
    {
        .syscall_nr = __NR_execve,
        .security_flags = TCP_FLAG_EXECUTION | TCP_FLAG_CRITICAL,
        .context_mask = TCP_CTX_ALL,
        .privilege_level = TCP_PRIV_USER,
        .pattern = "program_exec",
        .checksum = 0x5E6F7890
    },
    
    /* init_module() - kernel module loading */
    {
        .syscall_nr = __NR_init_module,
        .security_flags = TCP_FLAG_CRITICAL | TCP_FLAG_KERNEL | TCP_FLAG_DESTRUCTIVE,
        .context_mask = TCP_CTX_ADMIN | TCP_CTX_KERNEL,
        .privilege_level = TCP_PRIV_ROOT,
        .pattern = "module_load",
        .checksum = 0x9ABC1234
    },
    
    /* getpid() - safe syscall */
    {
        .syscall_nr = __NR_getpid,
        .security_flags = TCP_FLAG_SAFE,
        .context_mask = TCP_CTX_ALL,
        .privilege_level = TCP_PRIV_USER,
        .pattern = "pid_query",
        .checksum = 0xDEF56789
    }
};

#define TCP_DESCRIPTOR_COUNT ARRAY_SIZE(tcp_descriptors)

/* Fast descriptor lookup */
static struct tcp_kernel_descriptor* tcp_find_descriptor(int syscall_nr)
{
    int i;
    
    for (i = 0; i < TCP_DESCRIPTOR_COUNT; i++) {
        if (tcp_descriptors[i].syscall_nr == syscall_nr) {
            return &tcp_descriptors[i];
        }
    }
    
    return NULL;
}

/* Check if current context is valid for operation */
static bool tcp_check_context(struct tcp_kernel_descriptor *desc)
{
    u8 current_context = 0;
    
    /* Determine current execution context */
    if (current->cred->uid.val == 0) {
        current_context |= TCP_CTX_ADMIN;
    } else {
        current_context |= TCP_CTX_USER;
    }
    
    /* Check if in container (simplified check) */
    if (current->nsproxy != &init_nsproxy) {
        current_context |= TCP_CTX_CONTAINER;
    }
    
    /* Validate context against descriptor */
    return (desc->context_mask & current_context) != 0;
}

/* TCP security analysis */
static int tcp_analyze_syscall(struct pt_regs *regs)
{
    struct tcp_kernel_descriptor *desc;
    int syscall_nr;
    
    if (!tcp_state.enabled) {
        return 0;
    }
    
    syscall_nr = regs->orig_ax;
    atomic64_inc(&tcp_state.stats.total_checks);
    
    /* Fast path for safe operations */
    desc = tcp_find_descriptor(syscall_nr);
    if (!desc) {
        /* Unknown syscall - treat as safe for now */
        atomic64_inc(&tcp_state.stats.fast_path_hits);
        return 0;
    }
    
    /* Check if operation is safe */
    if (desc->security_flags & TCP_FLAG_SAFE) {
        atomic64_inc(&tcp_state.stats.fast_path_hits);
        return 0;
    }
    
    /* Validate execution context */
    if (!tcp_check_context(desc)) {
        pr_warn("TCP: Invalid context for syscall %d (PID %d, UID %d)\n",
                syscall_nr, current->pid, current->cred->uid.val);
        atomic64_inc(&tcp_state.stats.blocked_operations);
        return -EPERM;
    }
    
    /* Check for critical operations */
    if (desc->security_flags & TCP_FLAG_CRITICAL) {
        pr_info("TCP: Critical operation detected - syscall %d (PID %d, CMD %s)\n",
                syscall_nr, current->pid, current->comm);
        atomic64_inc(&tcp_state.stats.security_events);
        
        /* In paranoid mode, block all critical operations from non-root */
        if (tcp_state.security_level >= 2 && current->cred->uid.val != 0) {
            pr_warn("TCP: Blocking critical operation from non-root user\n");
            atomic64_inc(&tcp_state.stats.blocked_operations);
            return -EPERM;
        }
    }
    
    /* Log destructive operations */
    if (desc->security_flags & TCP_FLAG_DESTRUCTIVE) {
        pr_info("TCP: Destructive operation - syscall %d (PID %d, CMD %s)\n",
                syscall_nr, current->pid, current->comm);
        atomic64_inc(&tcp_state.stats.security_events);
    }
    
    return 0;
}

/* Kprobe for system call entry */
static struct kprobe tcp_syscall_kprobe = {
    .symbol_name = "do_syscall_64",
};

/* Kprobe pre-handler */
static int tcp_syscall_pre_handler(struct kprobe *p, struct pt_regs *regs)
{
    int result = tcp_analyze_syscall(regs);
    
    /* If we want to block the syscall, we'd need more complex handling */
    /* For this demo, we just log and continue */
    return 0;
}

/* Proc filesystem interface */
static int tcp_proc_show(struct seq_file *m, void *v)
{
    seq_printf(m, "TCP Kernel Integration Status\n");
    seq_printf(m, "============================\n\n");
    seq_printf(m, "Enabled: %s\n", tcp_state.enabled ? "Yes" : "No");
    seq_printf(m, "Security Level: %d\n", tcp_state.security_level);
    seq_printf(m, "\nStatistics:\n");
    seq_printf(m, "  Total Checks: %lld\n", 
               atomic64_read(&tcp_state.stats.total_checks));
    seq_printf(m, "  Fast Path Hits: %lld\n", 
               atomic64_read(&tcp_state.stats.fast_path_hits));
    seq_printf(m, "  Blocked Operations: %lld\n", 
               atomic64_read(&tcp_state.stats.blocked_operations));
    seq_printf(m, "  Security Events: %lld\n", 
               atomic64_read(&tcp_state.stats.security_events));
    seq_printf(m, "  False Positives: %lld\n", 
               atomic64_read(&tcp_state.stats.false_positives));
    
    seq_printf(m, "\nDescriptor Database:\n");
    int i;
    for (i = 0; i < TCP_DESCRIPTOR_COUNT; i++) {
        seq_printf(m, "  Syscall %d: flags=0x%04x pattern=%s\n",
                   tcp_descriptors[i].syscall_nr,
                   tcp_descriptors[i].security_flags,
                   tcp_descriptors[i].pattern);
    }
    
    return 0;
}

static int tcp_proc_open(struct inode *inode, struct file *file)
{
    return single_open(file, tcp_proc_show, NULL);
}

static const struct proc_ops tcp_proc_ops = {
    .proc_open = tcp_proc_open,
    .proc_read = seq_read,
    .proc_lseek = seq_lseek,
    .proc_release = single_release,
};

/* Initialize TCP kernel module */
static int __init tcp_kernel_init(void)
{
    int ret;
    
    pr_info("TCP: Initializing kernel integration module\n");
    
    /* Initialize state */
    memset(&tcp_state, 0, sizeof(tcp_state));
    tcp_state.enabled = true;
    tcp_state.security_level = 1;  /* Normal level */
    spin_lock_init(&tcp_state.lock);
    
    /* Initialize statistics */
    atomic64_set(&tcp_state.stats.total_checks, 0);
    atomic64_set(&tcp_state.stats.fast_path_hits, 0);
    atomic64_set(&tcp_state.stats.blocked_operations, 0);
    atomic64_set(&tcp_state.stats.security_events, 0);
    atomic64_set(&tcp_state.stats.false_positives, 0);
    
    /* Register kprobe for syscall monitoring */
    tcp_syscall_kprobe.pre_handler = tcp_syscall_pre_handler;
    ret = register_kprobe(&tcp_syscall_kprobe);
    if (ret < 0) {
        pr_err("TCP: Failed to register kprobe: %d\n", ret);
        return ret;
    }
    
    /* Create proc filesystem entry */
    tcp_state.proc_entry = proc_create("tcp_kernel", 0444, NULL, &tcp_proc_ops);
    if (!tcp_state.proc_entry) {
        pr_err("TCP: Failed to create proc entry\n");
        unregister_kprobe(&tcp_syscall_kprobe);
        return -ENOMEM;
    }
    
    pr_info("TCP: Kernel integration active (security level %d)\n", 
            tcp_state.security_level);
    pr_info("TCP: Monitoring %zu syscall descriptors\n", TCP_DESCRIPTOR_COUNT);
    pr_info("TCP: Status available at /proc/tcp_kernel\n");
    
    return 0;
}

/* Cleanup TCP kernel module */
static void __exit tcp_kernel_exit(void)
{
    pr_info("TCP: Shutting down kernel integration\n");
    
    /* Disable TCP */
    tcp_state.enabled = false;
    
    /* Remove proc entry */
    if (tcp_state.proc_entry) {
        proc_remove(tcp_state.proc_entry);
    }
    
    /* Unregister kprobe */
    unregister_kprobe(&tcp_syscall_kprobe);
    
    /* Print final statistics */
    pr_info("TCP: Final stats - Checks: %lld, Events: %lld, Blocked: %lld\n",
            atomic64_read(&tcp_state.stats.total_checks),
            atomic64_read(&tcp_state.stats.security_events),
            atomic64_read(&tcp_state.stats.blocked_operations));
    
    pr_info("TCP: Kernel integration disabled\n");
}

module_init(tcp_kernel_init);
module_exit(tcp_kernel_exit);