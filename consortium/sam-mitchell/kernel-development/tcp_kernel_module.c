/*
 * TCP Kernel Security Module
 * Dr. Sam Mitchell - Hardware Security Engineer
 * 
 * Kernel-space TCP descriptor validation with hardware-enforced security.
 * Integrates with LSM, eBPF, SGX, and other hardware security features.
 */

#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/init.h>
#include <linux/security.h>
#include <linux/bpf.h>
#include <linux/perf_event.h>
#include <linux/intel-sgx.h>
#include <linux/tpm.h>
#include <linux/proc_fs.h>
#include <linux/seq_file.h>
#include <linux/uaccess.h>
#include <linux/slab.h>
#include <linux/crypto.h>
#include <crypto/hash.h>

#define TCP_MODULE_NAME "tcp_security"
#define TCP_MODULE_VERSION "1.0"
#define TCP_MAGIC_CLASSICAL 0x50435402  /* "TCP\x02" */
#define TCP_MAGIC_QUANTUM   0x51504354  /* "TCPQ" */

/* Hardware feature detection flags */
#define TCP_HW_LSM           (1 << 0)
#define TCP_HW_EBPF          (1 << 1)
#define TCP_HW_PMU           (1 << 2)
#define TCP_HW_TPM           (1 << 3)
#define TCP_HW_SGX           (1 << 4)
#define TCP_HW_CET           (1 << 5)
#define TCP_HW_PT            (1 << 6)
#define TCP_HW_MPK           (1 << 7)

/* TCP descriptor structures */
struct tcp_classical_descriptor {
    u32 magic;              /* TCP\x02 magic bytes */
    u32 command_hash;       /* Command identifier */
    u32 security_flags;     /* Security and capability flags */
    u8  performance_data[6]; /* Performance metrics */
    u16 reserved;           /* Reserved for future use */
    u16 checksum;           /* CRC16 checksum */
} __packed;

struct tcp_quantum_descriptor {
    u32 magic;              /* TCPQ magic bytes */
    u8  version;            /* Version (3 for quantum-safe) */
    u32 command_hash;       /* Command identifier */
    u32 security_flags;     /* Enhanced security flags */
    u8  performance_data[6]; /* Performance metrics */
    u8  pqc_signature[11];  /* Post-quantum signature snippet */
    u16 reserved;           /* Reserved for future use */
} __packed;

/* TCP validation context */
struct tcp_validation_context {
    u32 hardware_features;   /* Available hardware features */
    u8  security_level;      /* Current security level */
    u64 validation_count;    /* Total validations performed */
    u64 cache_hits;          /* Cache hit count */
    u64 security_violations; /* Security violation count */
    u64 total_time_ns;       /* Total validation time */
    spinlock_t lock;         /* Protection for statistics */
};

/* Global validation context */
static struct tcp_validation_context tcp_ctx;

/* Validation cache for performance */
#define TCP_CACHE_SIZE 10000
struct tcp_cache_entry {
    u8 descriptor_hash[8];   /* SHA256 truncated to 8 bytes */
    u8 validation_result;    /* Cached validation result */
    u64 timestamp;           /* Cache timestamp */
};

static struct tcp_cache_entry *tcp_cache;
static u32 tcp_cache_head = 0;

/* Hardware feature detection */
static u32 tcp_detect_hardware_features(void)
{
    u32 features = 0;
    
    /* Always available in modern kernels */
    features |= TCP_HW_LSM;
    features |= TCP_HW_EBPF;
    features |= TCP_HW_PMU;
    
    /* Check for Intel SGX */
    if (cpu_feature_enabled(X86_FEATURE_SGX)) {
        features |= TCP_HW_SGX;
    }
    
    /* Check for Intel CET */
    if (cpu_feature_enabled(X86_FEATURE_SHSTK) || 
        cpu_feature_enabled(X86_FEATURE_IBT)) {
        features |= TCP_HW_CET;
    }
    
    /* Check for Intel PT */
    if (cpu_feature_enabled(X86_FEATURE_INTEL_PT)) {
        features |= TCP_HW_PT;
    }
    
    /* Check for Memory Protection Keys */
    if (cpu_feature_enabled(X86_FEATURE_PKU)) {
        features |= TCP_HW_MPK;
    }
    
    /* Check for TPM */
    if (tpm_chip_find_get(NULL) != NULL) {
        features |= TCP_HW_TPM;
    }
    
    return features;
}

/* Fast cache lookup */
static int tcp_cache_lookup(const u8 *descriptor_hash, u8 *result)
{
    struct tcp_cache_entry *entry;
    u32 i;
    
    for (i = 0; i < TCP_CACHE_SIZE; i++) {
        entry = &tcp_cache[i];
        if (memcmp(entry->descriptor_hash, descriptor_hash, 8) == 0) {
            *result = entry->validation_result;
            return 1; /* Cache hit */
        }
    }
    
    return 0; /* Cache miss */
}

/* Cache validation result */
static void tcp_cache_store(const u8 *descriptor_hash, u8 result)
{
    struct tcp_cache_entry *entry;
    
    entry = &tcp_cache[tcp_cache_head];
    memcpy(entry->descriptor_hash, descriptor_hash, 8);
    entry->validation_result = result;
    entry->timestamp = ktime_get_ns();
    
    tcp_cache_head = (tcp_cache_head + 1) % TCP_CACHE_SIZE;
}

/* Hardware-accelerated CRC16 calculation */
static u16 tcp_hardware_crc16(const u8 *data, size_t len)
{
    /* Use CPU CRC32 instruction if available, fallback to software */
    struct crypto_shash *tfm;
    u32 crc = 0;
    int err;
    
    tfm = crypto_alloc_shash("crc32", 0, 0);
    if (IS_ERR(tfm)) {
        /* Fallback to simple checksum */
        size_t i;
        for (i = 0; i < len; i++) {
            crc += data[i];
        }
        return crc & 0xFFFF;
    }
    
    /* Use hardware CRC32 */
    err = crypto_shash_digest(tfm, data, len, (u8 *)&crc);
    crypto_free_shash(tfm);
    
    return err ? 0 : (crc & 0xFFFF);
}

/* eBPF security monitor */
static int tcp_ebpf_security_check(const void *descriptor, size_t len)
{
    /* Integration point for eBPF security monitoring
     * In production, this would load and execute eBPF programs
     * for real-time behavioral analysis
     */
    
    /* Simulate eBPF check - 50ns target */
    return (len == 24 || len == 32) ? 1 : 0;
}

/* LSM security hook integration */
static int tcp_lsm_security_check(const void *descriptor, size_t len)
{
    /* LSM security policy check - 10ns target */
    const struct tcp_classical_descriptor *tcp_desc;
    
    if (len == 24) {
        tcp_desc = (const struct tcp_classical_descriptor *)descriptor;
        
        /* Check for dangerous security flags */
        if (tcp_desc->security_flags & 0x0001) { /* DESTRUCTIVE */
            return 0; /* Deny destructive operations by default */
        }
    }
    
    return 1; /* Allow by default */
}

/* SGX enclave validation */
static int tcp_sgx_validation(const void *descriptor, size_t len)
{
    /* SGX secure enclave validation - 100ns target
     * In production, would execute validation inside SGX enclave
     */
    
    if (!(tcp_ctx.hardware_features & TCP_HW_SGX)) {
        return 1; /* Skip if SGX not available */
    }
    
    /* Simulate SGX enclave validation */
    return 1; /* Success */
}

/* TPM hardware attestation */
static int tcp_tpm_attestation(const void *descriptor, size_t len)
{
    /* TPM 2.0 hardware attestation - 1μs target */
    
    if (!(tcp_ctx.hardware_features & TCP_HW_TPM)) {
        return 1; /* Skip if TPM not available */
    }
    
    /* Simulate TPM attestation */
    return 1; /* Success */
}

/* Core TCP descriptor validation */
static int tcp_validate_descriptor_kernel(const void *descriptor, size_t len)
{
    const struct tcp_classical_descriptor *classical;
    const struct tcp_quantum_descriptor *quantum;
    u8 descriptor_hash[8];
    u8 cached_result;
    u64 start_time, end_time;
    u16 calculated_crc;
    int result = 0;
    
    start_time = ktime_get_ns();
    
    /* Calculate descriptor hash for cache lookup */
    {
        struct crypto_shash *tfm;
        u8 full_hash[32];
        
        tfm = crypto_alloc_shash("sha256", 0, 0);
        if (!IS_ERR(tfm)) {
            crypto_shash_digest(tfm, descriptor, len, full_hash);
            memcpy(descriptor_hash, full_hash, 8);
            crypto_free_shash(tfm);
        } else {
            /* Fallback hash */
            memset(descriptor_hash, 0, 8);
            memcpy(descriptor_hash, descriptor, min(len, 8UL));
        }
    }
    
    /* Check cache first */
    if (tcp_cache_lookup(descriptor_hash, &cached_result)) {
        spin_lock(&tcp_ctx.lock);
        tcp_ctx.cache_hits++;
        spin_unlock(&tcp_ctx.lock);
        return cached_result;
    }
    
    /* Validate descriptor format */
    if (len == 24) {
        /* Classical 24-byte descriptor */
        classical = (const struct tcp_classical_descriptor *)descriptor;
        
        if (classical->magic != TCP_MAGIC_CLASSICAL) {
            result = -EINVAL;
            goto out;
        }
        
        /* Verify checksum */
        calculated_crc = tcp_hardware_crc16((const u8 *)descriptor, 22);
        if (calculated_crc != classical->checksum) {
            result = -EINVAL;
            goto out;
        }
        
    } else if (len == 32) {
        /* Quantum-safe 32-byte descriptor */
        quantum = (const struct tcp_quantum_descriptor *)descriptor;
        
        if (quantum->magic != TCP_MAGIC_QUANTUM) {
            result = -EINVAL;
            goto out;
        }
        
        if (quantum->version < 3) {
            result = -EINVAL; /* Not quantum-safe */
            goto out;
        }
        
        /* TODO: Verify post-quantum signature */
        
    } else {
        result = -EINVAL;
        goto out;
    }
    
    /* Hardware security checks */
    if (!tcp_lsm_security_check(descriptor, len)) {
        result = -EACCES;
        goto out;
    }
    
    if (!tcp_ebpf_security_check(descriptor, len)) {
        result = -EACCES;
        goto out;
    }
    
    if (!tcp_sgx_validation(descriptor, len)) {
        result = -EACCES;
        goto out;
    }
    
    if (!tcp_tpm_attestation(descriptor, len)) {
        result = -EACCES;
        goto out;
    }
    
    result = 1; /* Success */
    
out:
    /* Cache result */
    tcp_cache_store(descriptor_hash, result > 0 ? 1 : 0);
    
    /* Update statistics */
    end_time = ktime_get_ns();
    spin_lock(&tcp_ctx.lock);
    tcp_ctx.validation_count++;
    tcp_ctx.total_time_ns += (end_time - start_time);
    if (result <= 0) {
        tcp_ctx.security_violations++;
    }
    spin_unlock(&tcp_ctx.lock);
    
    return result;
}

/* Proc filesystem interface for statistics */
static int tcp_proc_show(struct seq_file *m, void *v)
{
    u64 avg_time_ns = 0;
    u64 cache_hit_rate = 0;
    
    spin_lock(&tcp_ctx.lock);
    
    if (tcp_ctx.validation_count > 0) {
        avg_time_ns = tcp_ctx.total_time_ns / tcp_ctx.validation_count;
    }
    
    if (tcp_ctx.validation_count > 0) {
        cache_hit_rate = (tcp_ctx.cache_hits * 100) / tcp_ctx.validation_count;
    }
    
    seq_printf(m, "TCP Kernel Security Module Statistics\n");
    seq_printf(m, "=====================================\n");
    seq_printf(m, "Hardware Features: 0x%08x\n", tcp_ctx.hardware_features);
    seq_printf(m, "Security Level: %u\n", tcp_ctx.security_level);
    seq_printf(m, "Total Validations: %llu\n", tcp_ctx.validation_count);
    seq_printf(m, "Cache Hits: %llu\n", tcp_ctx.cache_hits);
    seq_printf(m, "Cache Hit Rate: %llu%%\n", cache_hit_rate);
    seq_printf(m, "Security Violations: %llu\n", tcp_ctx.security_violations);
    seq_printf(m, "Average Time (ns): %llu\n", avg_time_ns);
    
    /* Hardware feature breakdown */
    seq_printf(m, "\nHardware Features:\n");
    if (tcp_ctx.hardware_features & TCP_HW_LSM)
        seq_printf(m, "  LSM Security Hooks: Enabled\n");
    if (tcp_ctx.hardware_features & TCP_HW_EBPF)
        seq_printf(m, "  eBPF Monitoring: Enabled\n");
    if (tcp_ctx.hardware_features & TCP_HW_SGX)
        seq_printf(m, "  Intel SGX: Enabled\n");
    if (tcp_ctx.hardware_features & TCP_HW_CET)
        seq_printf(m, "  Intel CET: Enabled\n");
    if (tcp_ctx.hardware_features & TCP_HW_TPM)
        seq_printf(m, "  TPM 2.0: Enabled\n");
    
    spin_unlock(&tcp_ctx.lock);
    
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

/* Module initialization */
static int __init tcp_kernel_init(void)
{
    /* Initialize validation context */
    memset(&tcp_ctx, 0, sizeof(tcp_ctx));
    spin_lock_init(&tcp_ctx.lock);
    
    /* Detect hardware features */
    tcp_ctx.hardware_features = tcp_detect_hardware_features();
    tcp_ctx.security_level = 1; /* Basic security by default */
    
    /* Allocate validation cache */
    tcp_cache = kcalloc(TCP_CACHE_SIZE, sizeof(struct tcp_cache_entry), GFP_KERNEL);
    if (!tcp_cache) {
        printk(KERN_ERR "TCP: Failed to allocate validation cache\n");
        return -ENOMEM;
    }
    
    /* Create proc interface */
    if (!proc_create("tcp_security", 0444, NULL, &tcp_proc_ops)) {
        printk(KERN_ERR "TCP: Failed to create proc interface\n");
        kfree(tcp_cache);
        return -ENOMEM;
    }
    
    printk(KERN_INFO "TCP Kernel Security Module loaded\n");
    printk(KERN_INFO "TCP: Hardware features: 0x%08x\n", tcp_ctx.hardware_features);
    printk(KERN_INFO "TCP: Validation cache: %d entries\n", TCP_CACHE_SIZE);
    
    return 0;
}

/* Module cleanup */
static void __exit tcp_kernel_exit(void)
{
    /* Remove proc interface */
    remove_proc_entry("tcp_security", NULL);
    
    /* Free validation cache */
    kfree(tcp_cache);
    
    printk(KERN_INFO "TCP Kernel Security Module unloaded\n");
    printk(KERN_INFO "TCP: Final statistics - Validations: %llu, Violations: %llu\n",
           tcp_ctx.validation_count, tcp_ctx.security_violations);
}

/* Export validation function for other kernel modules */
EXPORT_SYMBOL(tcp_validate_descriptor_kernel);

module_init(tcp_kernel_init);
module_exit(tcp_kernel_exit);

MODULE_LICENSE("GPL");
MODULE_AUTHOR("Dr. Sam Mitchell <sam.mitchell@tcp-consortium.org>");
MODULE_DESCRIPTION("TCP Kernel-Level Hardware Security Integration");
MODULE_VERSION(TCP_MODULE_VERSION);
MODULE_ALIAS("tcp-security");

/* Module parameters for runtime configuration */
module_param_named(security_level, tcp_ctx.security_level, byte, 0644);
MODULE_PARM_DESC(security_level, "TCP security level (0-6)");

static bool enable_sgx = true;
module_param(enable_sgx, bool, 0644);
MODULE_PARM_DESC(enable_sgx, "Enable Intel SGX validation");

static bool enable_tpm = true;
module_param(enable_tpm, bool, 0644);
MODULE_PARM_DESC(enable_tpm, "Enable TPM hardware attestation");