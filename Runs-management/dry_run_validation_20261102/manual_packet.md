# Bộ 60 prompt — chờ hai người đọc độc lập

30 Devign + 30 REVEAL. Mỗi người đọc cùng 60 prompt, điền phiếu riêng theo RUBRIC.md; không cung cấp nhãn target, score hoặc metric.

## 1. devign/B0/42/devign:validation:5510

SHA-256: f4ed394faf8e1f476897b3b322cef78916bf25319dfcdaf9521ef843abe29cbd

Nguồn: Runs-management/dry_run_validation_20261102/devign/validation/B0/42/prompts.jsonl

```text
You are now an excellent programmer. You are conducting a function vulnerability detection task for C/C++ language.

struct GuestAgentInfo *qmp_guest_info(Error **errp)

{

    GuestAgentInfo *info = g_malloc0(sizeof(GuestAgentInfo));



    info->version = g_strdup(QEMU_VERSION);

    qmp_for_each_command(qmp_command_info, info);

    return info;

}

In the above code snippet, check for potential security vulnerabilities and answer with a single digit: 1 if Vulnerable, 0 if Non-vulnerable.

The node information of the code snippet is as follows:

The edge information of the code snippet is as follows:


The following is an example, and it is .


Answer (0 or 1):
```

## 2. devign/B1/42/devign:validation:25921

SHA-256: af09b969fdb37967b6a91efd91d5fffcfa3b544105ac8ea89628a1cee804d0c2

Nguồn: Runs-management/dry_run_validation_20261102/devign/validation/B1/42/prompts.jsonl

```text
You are now an excellent programmer. You are conducting a function vulnerability detection task for C/C++ language.

static void sigp_store_status_at_address(CPUState *cs, run_on_cpu_data arg)

{

    S390CPU *cpu = S390_CPU(cs);

    SigpInfo *si = arg.host_ptr;

    uint32_t address = si->param & 0x7ffffe00u;



    /* cpu has to be stopped */

    if (s390_cpu_get_state(cpu) != CPU_STATE_STOPPED) {

        set_sigp_status(si, SIGP_STAT_INCORRECT_STATE);

        return;

    }



    cpu_synchronize_state(cs);



    if (s390_store_status(cpu, address, false)) {

        set_sigp_status(si, SIGP_STAT_INVALID_PARAMETER);

        return;

    }

    si->cc = SIGP_CC_ORDER_CODE_ACCEPTED;

}

In the above code snippet, check for potential security vulnerabilities and answer with a single digit: 1 if Vulnerable, 0 if Non-vulnerable.

The node information of the code snippet is as follows:
Node 25769803776: (BLOCK) '{      S390CPU *cpu = S390_CPU(cs);     ...'
Node 25769803777: (BLOCK) '{ set_sigp_status(si, SIGP_STAT_INCORREC...'
Node 25769803778: (BLOCK) '{ set_sigp_status(si, SIGP_STAT_INVALID_...'
Node 30064771072: (CALL) 'cpu = S390_CPU(cs)'
Node 30064771073: (CALL) 'S390_CPU(cs)'
Node 30064771074: (CALL) 'si = arg.host_ptr'
Node 30064771075: (CALL) 'arg.host_ptr'
Node 30064771076: (CALL) 'address = si->param & 0x7ffffe00u'
Node 30064771077: (CALL) 'si->param & 0x7ffffe00u'
Node 30064771078: (CALL) 'si->param'
Node 30064771079: (CALL) 's390_cpu_get_state(cpu) != CPU_STATE_STO...'
Node 30064771080: (CALL) 's390_cpu_get_state(cpu)'
Node 30064771081: (CALL) 'set_sigp_status(si, SIGP_STAT_INCORRECT_...'
Node 30064771082: (CALL) 'cpu_synchronize_state(cs)'
Node 30064771083: (CALL) 's390_store_status(cpu, address, false)'
Node 30064771084: (CALL) 'set_sigp_status(si, SIGP_STAT_INVALID_PA...'
Node 30064771085: (CALL) 'si->cc = SIGP_CC_ORDER_CODE_ACCEPTED'
Node 30064771086: (CALL) 'si->cc'
Node 47244640256: (CONTROL_STRUCTURE) 'if (s390_cpu_get_state(cpu) != CPU_STATE...'
Node 47244640257: (CONTROL_STRUCTURE) 'if (s390_store_status(cpu, address, fals...'
Node 55834574848: (FIELD_IDENTIFIER) 'host_ptr'
Node 55834574849: (FIELD_IDENTIFIER) 'param'
Node 55834574850: (FIELD_IDENTIFIER) 'cc'
Node 68719476736: (IDENTIFIER) 'cpu'
Node 68719476737: (IDENTIFIER) 'cs'
Node 68719476738: (IDENTIFIER) 'si'
Node 68719476739: (IDENTIFIER) 'arg'
Node 68719476740: (IDENTIFIER) 'address'
Node 68719476741: (IDENTIFIER) 'si'
Node 68719476742: (IDENTIFIER) 'cpu'
Node 68719476743: (IDENTIFIER) '<unknown> CPU_STATE_STOPPED'
Node 68719476744: (IDENTIFIER) 'si'
Node 68719476745: (IDENTIFIER) '<unknown> SIGP_STAT_INCORRECT_STATE'
Node 68719476746: (IDENTIFIER) 'cs'
Node 68719476747: (IDENTIFIER) 'cpu'
Node 68719476748: (IDENTIFIER) 'address'
Node 68719476749: (IDENTIFIER) '<unknown> false'
Node 68719476750: (IDENTIFIER) 'si'
Node 68719476751: (IDENTIFIER) '<unknown> SIGP_STAT_INVALID_PARAMETER'
Node 68719476752: (IDENTIFIER) 'si'
The edge information of the code snippet is as follows:
Edge: Node 25769803776 -> AST -> Node 30064771072
Edge: Node 25769803776 -> AST -> Node 30064771074
Edge: Node 25769803776 -> AST -> Node 30064771076
Edge: Node 25769803776 -> AST -> Node 47244640256
Edge: Node 25769803776 -> AST -> Node 30064771082
Edge: Node 25769803776 -> AST -> Node 47244640257
Edge: Node 25769803776 -> AST -> Node 30064771085
Edge: Node 25769803777 -> AST -> Node 30064771081
Edge: Node 25769803778 -> AST -> Node 30064771084
Edge: Node 30064771072 -> ARGUMENT -> Node 68719476736
Edge: Node 30064771072 -> ARGUMENT -> Node 30064771073
Edge: Node 30064771072 -> AST -> Node 68719476736
Edge: Node 30064771072 -> AST -> Node 30064771073
Edge: Node 30064771072 -> CFG -> Node 68719476738

The following is an example, and it is .


Answer (0 or 1):
```

## 3. devign/B1-full/42/devign:validation:11657

SHA-256: 5b31b6553f3cd749f02de3da86892d7a155cf6e4e916af52fa3f2fa6a2b124dd

Nguồn: Runs-management/dry_run_validation_20261102/devign/validation/B1-full/42/prompts.jsonl

```text
You are now an excellent programmer. You are conducting a function vulnerability detection task for C/C++ language.

static void sh_serial_write(void *opaque, hwaddr offs,

                            uint64_t val, unsigned size)

{

    sh_serial_state *s = opaque;

    unsigned char ch;



#ifdef DEBUG_SERIAL

    printf("sh_serial: write offs=0x%02x val=0x%02x\n",

	   offs, val);

#endif

    switch(offs) {

    case 0x00: /* SMR */

        s->smr = val & ((s->feat & SH_SERIAL_FEAT_SCIF) ? 0x7b : 0xff);

        return;

    case 0x04: /* BRR */

        s->brr = val;

	return;

    case 0x08: /* SCR */

        /* TODO : For SH7751, SCIF mask should be 0xfb. */

        s->scr = val & ((s->feat & SH_SERIAL_FEAT_SCIF) ? 0xfa : 0xff);

        if (!(val & (1 << 5)))

            s->flags |= SH_SERIAL_FLAG_TEND;

        if ((s->feat & SH_SERIAL_FEAT_SCIF) && s->txi) {

	    qemu_set_irq(s->txi, val & (1 << 7));

        }

        if (!(val & (1 << 6))) {

	    qemu_set_irq(s->rxi, 0);

        }

        return;

    case 0x0c: /* FTDR / TDR */

        if (s->chr) {

            ch = val;

            qemu_chr_fe_write(s->chr, &ch, 1);

	}

	s->dr = val;

	s->flags &= ~SH_SERIAL_FLAG_TDE;

        return;

#if 0

    case 0x14: /* FRDR / RDR */

        ret = 0;

        break;

#endif

    }

    if (s->feat & SH_SERIAL_FEAT_SCIF) {

        switch(offs) {

        case 0x10: /* FSR */

            if (!(val & (1 << 6)))

                s->flags &= ~SH_SERIAL_FLAG_TEND;

            if (!(val & (1 << 5)))

                s->flags &= ~SH_SERIAL_FLAG_TDE;

            if (!(val & (1 << 4)))

                s->flags &= ~SH_SERIAL_FLAG_BRK;

            if (!(val & (1 << 1)))

                s->flags &= ~SH_SERIAL_FLAG_RDF;

            if (!(val & (1 << 0)))

                s->flags &= ~SH_SERIAL_FLAG_DR;



            if (!(val & (1 << 1)) || !(val & (1 << 0))) {

                if (s->rxi) {

                    qemu_set_irq(s->rxi, 0);

                }

            }

            return;

        case 0x18: /* FCR */

            s->fcr = val;

            switch ((val >> 6) & 3) {

            case 0:

                s->rtrg = 1;

                break;

            case 1:

                s->rtrg = 4;

                break;

            case 2:

                s->rtrg = 8;

                break;

            case 3:

                s->rtrg = 14;

                break;

            }

            if (val & (1 << 1)) {

                sh_serial_clear_fifo(s);

                s->sr &= ~(1 << 1);

            }



            return;

        case 0x20: /* SPTR */

            s->sptr = val & 0xf3;

            return;

        case 0x24: /* LSR */

            return;

        }

    }

    else {

        switch(offs) {

#if 0

        case 0x0c:

            ret = s->dr;

            break;

        case 0x10:

            ret = 0;

            break;

#endif

        case 0x1c:

            s->sptr = val & 0x8f;

            return;

        }

    }



    fprintf(stderr, "sh_serial: unsupported write to 0x%02"

            HWADDR_PRIx "\n", offs);

    abort();

}

In the above code snippet, check for potential security vulnerabilities and answer with a single digit: 1 if Vulnerable, 0 if Non-vulnerable.

The node information of the code snippet is as follows:
Node 25769803776: (BLOCK) '{      sh_serial_state *s = opaque;     ...'
Node 25769803777: (BLOCK) '{      case 0x00: /* SMR */          s->...'
Node 25769803778: (BLOCK) '<empty>'
Node 25769803779: (BLOCK) '{ qemu_set_irq(s->txi, val & (1 << 7)); ...'
Node 25769803780: (BLOCK) '{ qemu_set_irq(s->rxi, 0); }'
Node 25769803781: (BLOCK) '{ ch = val; qemu_chr_fe_write(s->chr, &c...'
Node 25769803782: (BLOCK) '{          switch(offs) {          case ...'
Node 25769803783: (BLOCK) '{          case 0x10: /* FSR */         ...'
Node 25769803784: (BLOCK) '<empty>'
Node 25769803785: (BLOCK) '<empty>'
Node 25769803786: (BLOCK) '<empty>'
Node 25769803787: (BLOCK) '<empty>'
Node 25769803788: (BLOCK) '<empty>'
Node 25769803789: (BLOCK) '{ if (s->rxi) { qemu_set_irq(s->rxi, 0);...'
Node 25769803790: (BLOCK) '{ qemu_set_irq(s->rxi, 0); }'
Node 25769803791: (BLOCK) '{              case 0:                  ...'
Node 25769803792: (BLOCK) '{ sh_serial_clear_fifo(s); s->sr &= ~(1 ...'
Node 25769803793: (BLOCK) '{          switch(offs) {  #if 0        ...'
Node 25769803794: (BLOCK) '{  #if 0          case 0x0c:            ...'
Node 30064771072: (CALL) 's = opaque'
Node 30064771073: (CALL) 's->smr = val & ((s->feat & SH_SERIAL_FEA...'
Node 30064771074: (CALL) 's->smr'
Node 30064771075: (CALL) 'val & ((s->feat & SH_SERIAL_FEAT_SCIF) ?...'
Node 30064771076: (CALL) '(s->feat & SH_SERIAL_FEAT_SCIF) ? 0x7b :...'
The edge information of the code snippet is as follows:
Edge: Node 25769803776 -> AST -> Node 30064771072
Edge: Node 25769803777 -> AST -> Node 30064771073
Edge: Node 30064771073 -> ARGUMENT -> Node 30064771074
Edge: Node 30064771073 -> ARGUMENT -> Node 30064771075
Edge: Node 30064771073 -> AST -> Node 30064771074
Edge: Node 30064771073 -> AST -> Node 30064771075
Edge: Node 30064771073 -> POST_DOMINATE -> Node 30064771075
Edge: Node 30064771074 -> REACHING_DEF -> Node 30064771073
Edge: Node 30064771075 -> ARGUMENT -> Node 30064771076
Edge: Node 30064771075 -> AST -> Node 30064771076
Edge: Node 30064771075 -> CFG -> Node 30064771073
Edge: Node 30064771075 -> DOMINATE -> Node 30064771073
Edge: Node 30064771075 -> POST_DOMINATE -> Node 30064771076
Edge: Node 30064771075 -> REACHING_DEF -> Node 30064771074
Edge: Node 30064771075 -> REACHING_DEF -> Node 30064771073
Edge: Node 30064771076 -> CFG -> Node 30064771075
Edge: Node 30064771076 -> DOMINATE -> Node 30064771075
Edge: Node 30064771076 -> REACHING_DEF -> Node 30064771075

The following is an example, and it is .


Answer (0 or 1):
```

## 4. devign/B1-shuf/42/devign:validation:26984

SHA-256: 89e3fef5a461ee584e03b96d516691a2784e76bd793f7a1028da651aabd5b658

Nguồn: Runs-management/dry_run_validation_20261102/devign/validation/B1-shuf/42/prompts.jsonl

```text
You are now an excellent programmer. You are conducting a function vulnerability detection task for C/C++ language.

static void QEMU_NORETURN force_sig(int target_sig)

{

    CPUState *cpu = thread_cpu;

    CPUArchState *env = cpu->env_ptr;

    TaskState *ts = (TaskState *)cpu->opaque;

    int host_sig, core_dumped = 0;

    struct sigaction act;



    host_sig = target_to_host_signal(target_sig);

    trace_user_force_sig(env, target_sig, host_sig);

    gdb_signalled(env, target_sig);



    /* dump core if supported by target binary format */

    if (core_dump_signal(target_sig) && (ts->bprm->core_dump != NULL)) {

        stop_all_tasks();

        core_dumped =

            ((*ts->bprm->core_dump)(target_sig, env) == 0);

    }

    if (core_dumped) {

        /* we already dumped the core of target process, we don't want

         * a coredump of qemu itself */

        struct rlimit nodump;

        getrlimit(RLIMIT_CORE, &nodump);

        nodump.rlim_cur=0;

        setrlimit(RLIMIT_CORE, &nodump);

        (void) fprintf(stderr, "qemu: uncaught target signal %d (%s) - %s\n",

            target_sig, strsignal(host_sig), "core dumped" );

    }



    /* The proper exit code for dying from an uncaught signal is

     * -<signal>.  The kernel doesn't allow exit() or _exit() to pass

     * a negative value.  To get the proper exit code we need to

     * actually die from an uncaught signal.  Here the default signal

     * handler is installed, we send ourself a signal and we wait for

     * it to arrive. */

    sigfillset(&act.sa_mask);

    act.sa_handler = SIG_DFL;

    act.sa_flags = 0;

    sigaction(host_sig, &act, NULL);



    /* For some reason raise(host_sig) doesn't send the signal when

     * statically linked on x86-64. */

    kill(getpid(), host_sig);



    /* Make sure the signal isn't masked (just reuse the mask inside

    of act) */

    sigdelset(&act.sa_mask, host_sig);

    sigsuspend(&act.sa_mask);



    /* unreachable */

    abort();

}

In the above code snippet, check for potential security vulnerabilities and answer with a single digit: 1 if Vulnerable, 0 if Non-vulnerable.

The node information of the code snippet is as follows:
Node 25769803881: (BLOCK) '{      BDRVQcow2State *s = bs->opaque;  ...'
Node 25769803882: (BLOCK) '{ return ret; }'
Node 25769803883: (BLOCK) '{          uint64_t old_offset;         ...'
Node 25769803884: (BLOCK) '{              l2_table[l2_index + i] = ...'
Node 25769803885: (BLOCK) '{ l2_table[l2_index + i] |= cpu_to_be64(...'
Node 30064771993: (CALL) 's = bs->opaque'
Node 30064771994: (CALL) 'bs->opaque'
Node 30064771995: (CALL) 'ret = get_cluster_table(bs, offset, &l2_...'
Node 30064771996: (CALL) 'get_cluster_table(bs, offset, &l2_table,...'
Node 30064771997: (CALL) '&l2_table'
Node 30064771998: (CALL) '&l2_index'
Node 30064771999: (CALL) 'ret < 0'
Node 30064772000: (CALL) 'nb_clusters = MIN(nb_clusters, s->l2_siz...'
Node 30064772001: (CALL) 'MIN(nb_clusters, s->l2_size - l2_index)'
Node 30064772002: (CALL) 's->l2_size - l2_index'
Node 30064772003: (CALL) 's->l2_size'
Node 30064772004: (CALL) 'assert(nb_clusters <= INT_MAX)'
Node 30064772005: (CALL) 'nb_clusters <= INT_MAX'
Node 30064772006: (CALL) 'i = 0'
Node 30064772007: (CALL) 'i < nb_clusters'
Node 30064772008: (CALL) 'i++'
Node 30064772009: (CALL) 'old_offset = be64_to_cpu(l2_table[l2_ind...'
Node 30064772010: (CALL) 'be64_to_cpu(l2_table[l2_index + i])'
Node 30064772011: (CALL) 'l2_table[l2_index + i]'
Node 30064772012: (CALL) 'l2_index + i'
Node 30064772013: (CALL) 'qcow2_cache_entry_mark_dirty(bs, s->l2_t...'
Node 30064772014: (CALL) 's->l2_table_cache'
Node 30064772015: (CALL) 'old_offset & QCOW_OFLAG_COMPRESSED || fl...'
Node 30064772016: (CALL) 'old_offset & QCOW_OFLAG_COMPRESSED'
Node 30064772017: (CALL) 'flags & BDRV_REQ_MAY_UNMAP'
Node 30064772018: (CALL) 'l2_table[l2_index + i] = cpu_to_be64(QCO...'
Node 30064772019: (CALL) 'l2_table[l2_index + i]'
Node 30064772020: (CALL) 'l2_index + i'
Node 30064772021: (CALL) 'cpu_to_be64(QCOW_OFLAG_ZERO)'
Node 30064772022: (CALL) 'qcow2_free_any_clusters(bs, old_offset, ...'
Node 30064772023: (CALL) 'l2_table[l2_index + i] |= cpu_to_be64(QC...'
Node 30064772024: (CALL) 'l2_table[l2_index + i]'
Node 30064772025: (CALL) 'l2_index + i'
Node 30064772026: (CALL) 'cpu_to_be64(QCOW_OFLAG_ZERO)'
Node 30064772027: (CALL) 'qcow2_cache_put(bs, s->l2_table_cache, (...'
The edge information of the code snippet is as follows:
Edge: Node 25769803881 -> AST -> Node 30064771993
Edge: Node 25769803881 -> AST -> Node 30064771995
Edge: Node 25769803881 -> AST -> Node 30064772000
Edge: Node 25769803881 -> AST -> Node 30064772004
Edge: Node 25769803881 -> AST -> Node 30064772027
Edge: Node 25769803883 -> AST -> Node 30064772009
Edge: Node 25769803883 -> AST -> Node 30064772013
Edge: Node 25769803884 -> AST -> Node 30064772018
Edge: Node 25769803884 -> AST -> Node 30064772022
Edge: Node 25769803885 -> AST -> Node 30064772023
Edge: Node 30064771993 -> ARGUMENT -> Node 30064771994

The following is an example, and it is .


Answer (0 or 1):
```

## 5. devign/B1-shuf/43/devign:validation:17654

SHA-256: 8d6880f4ed390958213c794df6b948202f0213fa4f400e67ace39b1efdae3994

Nguồn: Runs-management/dry_run_validation_20261102/devign/validation/B1-shuf/43/prompts.jsonl

```text
You are now an excellent programmer. You are conducting a function vulnerability detection task for C/C++ language.

int sclp_service_call(uint32_t sccb, uint64_t code)

{

    int r = 0;

    SCCB work_sccb;



    hwaddr sccb_len = sizeof(SCCB);



    /* first some basic checks on program checks */

    if (cpu_physical_memory_is_io(sccb)) {

        r = -PGM_ADDRESSING;

        goto out;

    }

    if (sccb & ~0x7ffffff8ul) {

        r = -PGM_SPECIFICATION;

        goto out;

    }



    /*

     * we want to work on a private copy of the sccb, to prevent guests

     * from playing dirty tricks by modifying the memory content after

     * the host has checked the values

     */

    cpu_physical_memory_read(sccb, &work_sccb, sccb_len);



    /* Valid sccb sizes */

    if (be16_to_cpu(work_sccb.h.length) < sizeof(SCCBHeader) ||

        be16_to_cpu(work_sccb.h.length) > SCCB_SIZE) {

        r = -PGM_SPECIFICATION;

        goto out;

    }



    sclp_execute((SCCB *)&work_sccb, code);



    cpu_physical_memory_write(sccb, &work_sccb,

                              be16_to_cpu(work_sccb.h.length));



    sclp_service_interrupt(sccb);



out:

    return r;

}

In the above code snippet, check for potential security vulnerabilities and answer with a single digit: 1 if Vulnerable, 0 if Non-vulnerable.

The node information of the code snippet is as follows:
Node 25769803815: (BLOCK) '{      CPUState *cpu;      ARMCPU *armcp...'
Node 25769803816: (BLOCK) '{          armcpu = ARM_CPU(cpu);       ...'
Node 25769803817: (BLOCK) '{ return; }'
Node 25769803818: (BLOCK) '{          irqflags = deposit32(irqflags...'
Node 25769803819: (BLOCK) '{          const char compat[] = "arm,ar...'
Node 30064771292: (CALL) 'irqflags = GIC_FDT_IRQ_FLAGS_LEVEL_HI'
Node 30064771293: (CALL) 'CPU_FOREACH(cpu)'
Node 30064771294: (CALL) 'armcpu = ARM_CPU(cpu)'
Node 30064771295: (CALL) 'ARM_CPU(cpu)'
Node 30064771296: (CALL) '!arm_feature(&armcpu->env, ARM_FEATURE_P...'
Node 30064771297: (CALL) '!arm_feature(&armcpu->env, ARM_FEATURE_P...'
Node 30064771298: (CALL) 'arm_feature(&armcpu->env, ARM_FEATURE_PM...'
Node 30064771299: (CALL) '&armcpu->env'
Node 30064771300: (CALL) 'armcpu->env'
Node 30064771301: (CALL) '!kvm_arm_pmu_create(cpu, PPI(VIRTUAL_PMU...'
Node 30064771302: (CALL) 'kvm_arm_pmu_create(cpu, PPI(VIRTUAL_PMU_...'
Node 30064771303: (CALL) 'PPI(VIRTUAL_PMU_IRQ)'
Node 30064771304: (CALL) 'vms->gic_version == 2'
Node 30064771305: (CALL) 'vms->gic_version'
Node 30064771306: (CALL) 'irqflags = deposit32(irqflags, GIC_FDT_I...'
Node 30064771307: (CALL) 'deposit32(irqflags, GIC_FDT_IRQ_PPI_CPU_...'
Node 30064771308: (CALL) '(1 << vms->smp_cpus) - 1'
Node 30064771309: (CALL) '1 << vms->smp_cpus'
Node 30064771310: (CALL) 'vms->smp_cpus'
Node 30064771311: (CALL) 'armcpu = ARM_CPU(qemu_get_cpu(0))'
Node 30064771312: (CALL) 'ARM_CPU(qemu_get_cpu(0))'
Node 30064771313: (CALL) 'qemu_get_cpu(0)'
Node 30064771314: (CALL) 'qemu_fdt_add_subnode(vms->fdt, "/pmu")'
Node 30064771315: (CALL) 'vms->fdt'
Node 30064771316: (CALL) 'arm_feature(&armcpu->env, ARM_FEATURE_V8...'
Node 30064771317: (CALL) '&armcpu->env'
Node 30064771318: (CALL) 'armcpu->env'
Node 30064771319: (CALL) 'compat[] = "arm,armv8-pmuv3"'
Node 30064771320: (CALL) 'qemu_fdt_setprop(vms->fdt, "/pmu", "comp...'
Node 30064771321: (CALL) 'vms->fdt'
Node 30064771322: (CALL) 'sizeof(compat)'
Node 30064771323: (CALL) 'qemu_fdt_setprop_cells(vms->fdt, "/pmu",...'
Node 30064771324: (CALL) 'vms->fdt'
Node 47244640279: (CONTROL_STRUCTURE) 'if (!arm_feature(&armcpu->env, ARM_FEATU...'
Node 47244640280: (CONTROL_STRUCTURE) 'if (vms->gic_version == 2) {          ir...'
The edge information of the code snippet is as follows:
Edge: Node 25769803815 -> AST -> Node 30064771292
Edge: Node 25769803815 -> AST -> Node 30064771293
Edge: Node 25769803815 -> AST -> Node 25769803816
Edge: Node 25769803815 -> AST -> Node 47244640280
Edge: Node 25769803815 -> AST -> Node 30064771311
Edge: Node 25769803815 -> AST -> Node 30064771314
Edge: Node 25769803816 -> AST -> Node 30064771294
Edge: Node 25769803816 -> AST -> Node 47244640279
Edge: Node 25769803818 -> AST -> Node 30064771306
Edge: Node 25769803819 -> AST -> Node 30064771319

The following is an example, and it is .


Answer (0 or 1):
```

## 6. devign/B1-shuf/44/devign:validation:23929

SHA-256: a1f2d2ce3318e068db1a26650fff8e935c004ef926712d3d5f0d38d0c8658611

Nguồn: Runs-management/dry_run_validation_20261102/devign/validation/B1-shuf/44/prompts.jsonl

```text
You are now an excellent programmer. You are conducting a function vulnerability detection task for C/C++ language.

unsigned ff_dxva2_get_surface_index(const AVCodecContext *avctx,

                                    const AVDXVAContext *ctx,

                                    const AVFrame *frame)

{

    void *surface = get_surface(frame);

    unsigned i;



    for (i = 0; i < DXVA_CONTEXT_COUNT(avctx, ctx); i++) {

#if CONFIG_D3D11VA

        if (avctx->pix_fmt == AV_PIX_FMT_D3D11VA_VLD && ctx->d3d11va.surface[i] == surface)

        {

            D3D11_VIDEO_DECODER_OUTPUT_VIEW_DESC viewDesc;

            ID3D11VideoDecoderOutputView_GetDesc(ctx->d3d11va.surface[i], &viewDesc);

            return viewDesc.Texture2D.ArraySlice;

        }

#endif

#if CONFIG_DXVA2

        if (avctx->pix_fmt == AV_PIX_FMT_DXVA2_VLD && ctx->dxva2.surface[i] == surface)

            return i;

#endif

    }



    assert(0);

    return 0;

}

In the above code snippet, check for potential security vulnerabilities and answer with a single digit: 1 if Vulnerable, 0 if Non-vulnerable.

The node information of the code snippet is as follows:
Node 25769803788: (BLOCK) '{      int iomemtype;      icp_control_s...'
Node 30064771151: (CALL) 's = (icp_control_state *)qemu_mallocz(si...'
Node 30064771152: (CALL) '(icp_control_state *)qemu_mallocz(sizeof...'
Node 30064771153: (CALL) 'qemu_mallocz(sizeof(icp_control_state))'
Node 30064771154: (CALL) 'sizeof(icp_control_state)'
Node 30064771155: (CALL) 'iomemtype = cpu_register_io_memory(0, ic...'
Node 30064771156: (CALL) 'cpu_register_io_memory(0, icp_control_re...'
Node 30064771157: (CALL) 'cpu_register_physical_memory(base, 0x007...'
Node 30064771158: (CALL) 's->base = base'
Node 30064771159: (CALL) 's->base'
Node 55834574882: (FIELD_IDENTIFIER) 'base'
Node 68719476801: (IDENTIFIER) 's'
Node 68719476802: (IDENTIFIER) 'icp_control_state'
Node 68719476803: (IDENTIFIER) 'iomemtype'
Node 68719476804: (IDENTIFIER) '<unknown> icp_control_readfn'
Node 68719476805: (IDENTIFIER) '<unknown> icp_control_writefn'
Node 68719476806: (IDENTIFIER) 's'
Node 68719476807: (IDENTIFIER) 'base'
Node 68719476808: (IDENTIFIER) 'iomemtype'
Node 68719476809: (IDENTIFIER) 's'
Node 68719476810: (IDENTIFIER) 'base'
Node 90194313225: (LITERAL) '0'
Node 90194313226: (LITERAL) '0x007fffff'
Node 94489280524: (LOCAL) 'int iomemtype'
Node 94489280525: (LOCAL) 'icp_control_state *s'
Node 94489280526: (LOCAL) '<unknown> icp_control_writefn'
Node 94489280527: (LOCAL) '<unknown> icp_control_readfn'
Node 94489280528: (LOCAL) 'icp_control_state'
Node 107374182404: (METHOD) 'static void icp_control_init(uint32_t ba...'
Node 111669149698: (METHOD_PARAMETER_IN) 'uint32_t base'
Node 115964116994: (METHOD_PARAMETER_OUT) 'uint32_t base'
Node 124554051588: (METHOD_RETURN) 'RET'
Node 128849018880: (MODIFIER) '<empty>'
Node 176093659136: (TYPE_REF) 'icp_control_state *'
The edge information of the code snippet is as follows:
Edge: Node 25769803788 -> AST -> Node 94489280524
Edge: Node 25769803788 -> AST -> Node 94489280525
Edge: Node 25769803788 -> AST -> Node 30064771151
Edge: Node 25769803788 -> AST -> Node 30064771155
Edge: Node 25769803788 -> AST -> Node 30064771157
Edge: Node 25769803788 -> AST -> Node 30064771158
Edge: Node 25769803788 -> AST -> Node 94489280526
Edge: Node 25769803788 -> AST -> Node 94489280527
Edge: Node 25769803788 -> AST -> Node 94489280528
Edge: Node 30064771151 -> ARGUMENT -> Node 68719476801
Edge: Node 30064771151 -> ARGUMENT -> Node 30064771152
Edge: Node 30064771151 -> AST -> Node 68719476801
Edge: Node 30064771151 -> AST -> Node 30064771152
Edge: Node 30064771151 -> CFG -> Node 68719476803
Edge: Node 30064771151 -> DOMINATE -> Node 68719476803
Edge: Node 30064771151 -> POST_DOMINATE -> Node 30064771152
Edge: Node 30064771151 -> REACHING_DEF -> Node 124554051588
Edge: Node 30064771152 -> ARGUMENT -> Node 176093659136

The following is an example, and it is .


Answer (0 or 1):
```

## 7. devign/B2/42/devign:validation:6866

SHA-256: 66b08ddf6bf2709f2b26f5ea99775373ff25507b31f65ff8382206eef6911d86

Nguồn: Runs-management/dry_run_validation_20261102/devign/validation/B2/42/prompts.jsonl

```text
You are now an excellent programmer. You are conducting a function vulnerability detection task for C/C++ language.

static int write_f(BlockBackend *blk, int argc, char **argv)

{

    struct timeval t1, t2;

    int Cflag = 0, pflag = 0, qflag = 0, bflag = 0, Pflag = 0, zflag = 0;

    int cflag = 0;

    int c, cnt;

    char *buf = NULL;

    int64_t offset;

    int count;

    /* Some compilers get confused and warn if this is not initialized.  */

    int total = 0;

    int pattern = 0xcd;



    while ((c = getopt(argc, argv, "bcCpP:qz")) != EOF) {

        switch (c) {

        case 'b':

            bflag = 1;

            break;

        case 'c':

            cflag = 1;

            break;

        case 'C':

            Cflag = 1;

            break;

        case 'p':

            pflag = 1;

            break;

        case 'P':

            Pflag = 1;

            pattern = parse_pattern(optarg);

            if (pattern < 0) {

                return 0;

            }

            break;

        case 'q':

            qflag = 1;

            break;

        case 'z':

            zflag = 1;

            break;

        default:

            return qemuio_command_usage(&write_cmd);

        }

    }



    if (optind != argc - 2) {

        return qemuio_command_usage(&write_cmd);

    }



    if (bflag + pflag + zflag > 1) {

        printf("-b, -p, or -z cannot be specified at the same time\n");

        return 0;

    }



    if (zflag && Pflag) {

        printf("-z and -P cannot be specified at the same time\n");

        return 0;

    }



    offset = cvtnum(argv[optind]);

    if (offset < 0) {

        printf("non-numeric length argument -- %s\n", argv[optind]);

        return 0;

    }



    optind++;

    count = cvtnum(argv[optind]);

    if (count < 0) {

        printf("non-numeric length argument -- %s\n", argv[optind]);

        return 0;

    }



    if (!pflag) {

        if (offset & 0x1ff) {

            printf("offset %" PRId64 " is not sector aligned\n",

                   offset);

            return 0;

        }



        if (count & 0x1ff) {

            printf("count %d is not sector aligned\n",

                   count);

            return 0;

        }

    }



    if (!zflag) {

        buf = qemu_io_alloc(blk, count, pattern);

    }



    gettimeofday(&t1, NULL);

    if (pflag) {

        cnt = do_pwrite(blk, buf, offset, count, &total);

    } else if (bflag) {

        cnt = do_save_vmstate(blk, buf, offset, count, &total);

    } else if (zflag) {

        cnt = do_co_write_zeroes(blk, offset, count, &total);

    } else if (cflag) {

        cnt = do_write_compressed(blk, buf, offset, count, &total);

    } else {

        cnt = do_write(blk, buf, offset, count, &total);

    }

    gettimeofday(&t2, NULL);



    if (cnt < 0) {

        printf("write failed: %s\n", strerror(-cnt));

        goto out;

    }



    if (qflag) {

        goto out;

    }



    /* Finally, report back -- -C gives a parsable format */

    t2 = tsub(t2, t1);

    print_report("wrote", &t2, offset, count, total, cnt, Cflag);



out:

    if (!zflag) {

        qemu_io_free(buf);

    }



    return 0;

}

In the above code snippet, check for potential security vulnerabilities and answer with a single digit: 1 if Vulnerable, 0 if Non-vulnerable.

The node information of the code snippet is as follows:
Node 25769803776: (BLOCK) '{      struct timeval t1, t2;      int C...'
Node 25769803777: (BLOCK) '{          switch (c) {          case 'b...'
Node 25769803778: (BLOCK) '{          case 'b':              bflag ...'
Node 25769803779: (BLOCK) '{ return 0; }'
Node 25769803780: (BLOCK) '{ return qemuio_command_usage(&write_cmd...'
Node 25769803781: (BLOCK) '{          printf("-b, -p, or -z cannot ...'
Node 25769803782: (BLOCK) '{          printf("-z and -P cannot be s...'
Node 25769803783: (BLOCK) '{          printf("non-numeric length ar...'
Node 25769803784: (BLOCK) '{          printf("non-numeric length ar...'
Node 25769803785: (BLOCK) '{          if (offset & 0x1ff) {        ...'
Node 25769803786: (BLOCK) '{              printf("offset %" PRId64 ...'
Node 25769803787: (BLOCK) '{ printf("count %d is not sector aligned...'
Node 25769803788: (BLOCK) '{ buf = qemu_io_alloc(blk, count, patter...'
Node 25769803789: (BLOCK) '{ cnt = do_pwrite(blk, buf, offset, coun...'
Node 25769803790: (BLOCK) '<empty>'
Node 25769803791: (BLOCK) '{ cnt = do_save_vmstate(blk, buf, offset...'
Node 25769803792: (BLOCK) '<empty>'
Node 25769803793: (BLOCK) '{ cnt = do_co_write_zeroes(blk, offset, ...'
Node 25769803794: (BLOCK) '<empty>'
Node 25769803795: (BLOCK) '{ cnt = do_write_compressed(blk, buf, of...'
Node 25769803796: (BLOCK) '{ cnt = do_write(blk, buf, offset, count...'
Node 25769803797: (BLOCK) '{ printf("write failed: %s\n", strerror(...'
Node 25769803798: (BLOCK) '{ goto out; }'
Node 25769803799: (BLOCK) '{ qemu_io_free(buf); }'
Node 30064771072: (CALL) 'Cflag = 0'
Node 30064771073: (CALL) 'pflag = 0'
Node 30064771074: (CALL) 'qflag = 0'
Node 30064771075: (CALL) 'bflag = 0'
Node 30064771076: (CALL) 'Pflag = 0'
Node 30064771077: (CALL) 'zflag = 0'
Node 30064771078: (CALL) 'cflag = 0'
Node 30064771079: (CALL) 'buf = NULL'
Node 30064771080: (CALL) 'total = 0'
Node 30064771081: (CALL) 'pattern = 0xcd'
Node 30064771082: (CALL) '(c = getopt(argc, argv, "bcCpP:qz")) != ...'
Node 30064771083: (CALL) 'c = getopt(argc, argv, "bcCpP:qz")'
Node 30064771084: (CALL) 'getopt(argc, argv, "bcCpP:qz")'
Node 30064771085: (CALL) 'bflag = 1'
Node 30064771086: (CALL) 'cflag = 1'
Node 30064771087: (CALL) 'Cflag = 1'
The edge information of the code snippet is as follows:
Edge: Node 25769803776 -> AST -> Node 30064771072
Edge: Node 25769803776 -> AST -> Node 30064771073
Edge: Node 25769803776 -> AST -> Node 30064771074
Edge: Node 25769803776 -> AST -> Node 30064771075
Edge: Node 25769803776 -> AST -> Node 30064771076
Edge: Node 25769803776 -> AST -> Node 30064771077
Edge: Node 25769803776 -> AST -> Node 30064771078
Edge: Node 25769803776 -> AST -> Node 30064771079
Edge: Node 25769803776 -> AST -> Node 30064771080
Edge: Node 25769803776 -> AST -> Node 30064771081
Edge: Node 25769803778 -> AST -> Node 30064771085
Edge: Node 25769803778 -> AST -> Node 30064771086

The following is an example, and it is Vulnerable.
static int write_f(BlockBackend *blk, int argc, char **argv)

{

    struct timeval t1, t2;

    bool Cflag = false, qflag = false, bflag = false;

    bool Pflag = false, zflag = false, cflag = false;

    int flags = 0;

    int c, cnt;

    char *buf = NULL;

    int64_t offset;

    int64_t count;

    /* Some compilers get confused and warn if this is not initialized.  */

    int64_t total = 0;

    int pattern = 0xcd;



    while ((c = getopt(argc, argv, "bcCfpP:quz")) != -1) {

        switch (c) {

        case 'b':

            bflag = true;

            break;

        case 'c':

            cflag = true;

            break;

        case 'C':

            Cflag = true;

            break;

        case 'f':

            flags |= BDRV_REQ_FUA;

            break;

        case 'p':

            /* Ignored for backwards compatibility */

            break;

        case 'P':

            Pflag = true;

            pattern = parse_pattern(optarg);

            if (pattern < 0) {

                return 0;

            }

            break;

        case 'q':

            qflag = true;

            break;

        case 'u':

            flags |= BDRV_REQ_MAY_UNMAP;

            break;

        case 'z':

            zflag = true;

            break;

        default:

            return qemuio_command_usage(&write_cmd);

        }

    }



    if (optind != argc - 2) {

        return qemuio_command_usage(&write_cmd);

    }



    if (bflag && zflag) {

        printf("-b and -z cannot be specified at the same time\n");

        return 0;

    }



    if ((flags & BDRV_REQ_FUA) && (bflag || cflag)) {

        printf("-f and -b or -c cannot be specified at the same time\n");

        return 0;

    }



    if ((flags & BDRV_REQ_MAY_UNMAP) && !zflag) {

        printf("-u requires -z to be specified\n");

        return 0;

    }



    if (zflag && Pflag) {

        printf("-z and -P cannot be specified at the same time\n");

        return 0;

    }



    offset = cvtnum(argv[optind]);

    if (offset < 0) {

        print_cvtnum_err(offset, argv[optind]);

        return 0;

    }



    optind++;

    count = cvtnum(argv[optind]);

    if (count < 0) {

        print_cvtnum_err(count, argv[optind]);

        return 0;

    } else if (count > SIZE_MAX) {

        printf("length cannot exceed %" PRIu64 ", given %s\n",

               (uint64_t) SIZE_MAX, argv[optind]);

        return 0;

    }



    if (bflag || cflag) {

        if (offset & 0x1ff) {

            printf("offset %" PRId64 " is not sector aligned\n",

                   offset);

            return 0;

        }



        if (count & 0x1ff) {

            printf("count %"PRId64" is not sector aligned\n",

                   count);

            return 0;

        }

    }



    if (!zflag) {

        buf = qemu_io_alloc(blk, count, pattern);

    }



    gettimeofday(&t1, NULL);

    if (bflag) {

        cnt = do_save_vmstate(blk, buf, offset, count, &total);

    } else if (zflag) {

        cnt = do_co_pwrite_zeroes(blk, offset, count, flags, &total);

    } else if (cflag) {

        cnt = do_write_compressed(blk, buf, offset, count, &total);

    } else {

        cnt = do_pwrite(blk, buf, offset, count, flags, &total);

    }

    gettimeofday(&t2, NULL);



    if (cnt < 0) {

        printf("write failed: %s\n", strerror(-cnt));

        goto out;

    }



    if (qflag) {

        goto out;

    }



    /* Finally, report back -- -C gives a parsable format */

    t2 = tsub(t2, t1);

    print_report("wrote", &t2, offset, count, total, cnt, Cflag);



out:

    if (!zflag) {

        qemu_io_free(buf);

    }



    return 0;

}

Answer (0 or 1):
```

## 8. devign/B2-flip/42/devign:validation:24502

SHA-256: 94564d7307b5db1e465d9d582ed95f0ffe39e16b6d0f5025eba55c7c89727695

Nguồn: Runs-management/dry_run_validation_20261102/devign/validation/B2-flip/42/prompts.jsonl

```text
You are now an excellent programmer. You are conducting a function vulnerability detection task for C/C++ language.

int bdrv_snapshot_list(BlockDriverState *bs,

                       QEMUSnapshotInfo **psn_info)

{

    BlockDriver *drv = bs->drv;

    if (!drv)

        return -ENOMEDIUM;

    if (drv->bdrv_snapshot_list)

        return drv->bdrv_snapshot_list(bs, psn_info);

    if (bs->file)

        return bdrv_snapshot_list(bs->file, psn_info);

    return -ENOTSUP;

}

In the above code snippet, check for potential security vulnerabilities and answer with a single digit: 1 if Vulnerable, 0 if Non-vulnerable.

The node information of the code snippet is as follows:
Node 25769803776: (BLOCK) '{      BlockDriver *drv = bs->drv;      ...'
Node 25769803777: (BLOCK) '<empty>'
Node 25769803778: (BLOCK) '<empty>'
Node 25769803779: (BLOCK) '<empty>'
Node 30064771072: (CALL) 'drv = bs->drv'
Node 30064771073: (CALL) 'bs->drv'
Node 30064771074: (CALL) '!drv'
Node 30064771075: (CALL) '-ENOMEDIUM'
Node 30064771076: (CALL) 'drv->bdrv_snapshot_list'
Node 30064771077: (CALL) 'drv->bdrv_snapshot_list(bs, psn_info)'
Node 30064771078: (CALL) 'drv->bdrv_snapshot_list'
Node 30064771079: (CALL) 'bs->file'
Node 30064771080: (CALL) 'bdrv_snapshot_list(bs->file, psn_info)'
Node 30064771081: (CALL) 'bs->file'
Node 30064771082: (CALL) '-ENOTSUP'
Node 47244640256: (CONTROL_STRUCTURE) 'if (!drv) return -ENOMEDIUM;'
Node 47244640257: (CONTROL_STRUCTURE) 'if (drv->bdrv_snapshot_list)          re...'
Node 47244640258: (CONTROL_STRUCTURE) 'if (bs->file) return bdrv_snapshot_list(...'
Node 55834574848: (FIELD_IDENTIFIER) 'drv'
Node 55834574849: (FIELD_IDENTIFIER) 'bdrv_snapshot_list'
Node 55834574850: (FIELD_IDENTIFIER) 'bdrv_snapshot_list'
Node 55834574851: (FIELD_IDENTIFIER) 'file'
Node 55834574852: (FIELD_IDENTIFIER) 'file'
Node 68719476736: (IDENTIFIER) 'drv'
Node 68719476737: (IDENTIFIER) 'bs'
Node 68719476738: (IDENTIFIER) 'drv'
Node 68719476739: (IDENTIFIER) '<unknown> ENOMEDIUM'
Node 68719476740: (IDENTIFIER) 'drv'
Node 68719476741: (IDENTIFIER) 'drv'
Node 68719476742: (IDENTIFIER) 'bs'
Node 68719476743: (IDENTIFIER) 'psn_info'
Node 68719476744: (IDENTIFIER) 'bs'
Node 68719476745: (IDENTIFIER) 'bs'
Node 68719476746: (IDENTIFIER) 'psn_info'
Node 68719476747: (IDENTIFIER) '<unknown> ENOTSUP'
Node 94489280512: (LOCAL) 'BlockDriver *drv'
Node 94489280513: (LOCAL) '<unknown> ENOTSUP'
Node 94489280514: (LOCAL) '<unknown> ENOMEDIUM'
Node 107374182400: (METHOD) 'int bdrv_snapshot_list(BlockDriverState ...'
Node 111669149696: (METHOD_PARAMETER_IN) 'BlockDriverState *bs'
The edge information of the code snippet is as follows:
Edge: Node 25769803776 -> AST -> Node 94489280512
Edge: Node 25769803776 -> AST -> Node 30064771072
Edge: Node 25769803776 -> AST -> Node 47244640256
Edge: Node 25769803776 -> AST -> Node 47244640257
Edge: Node 25769803776 -> AST -> Node 47244640258
Edge: Node 25769803776 -> AST -> Node 94489280513
Edge: Node 25769803776 -> AST -> Node 94489280514
Edge: Node 30064771072 -> ARGUMENT -> Node 68719476736
Edge: Node 30064771072 -> ARGUMENT -> Node 30064771073
Edge: Node 30064771072 -> AST -> Node 68719476736
Edge: Node 30064771072 -> AST -> Node 30064771073
Edge: Node 30064771072 -> CFG -> Node 68719476738
Edge: Node 30064771072 -> DOMINATE -> Node 68719476738
Edge: Node 30064771072 -> POST_DOMINATE -> Node 30064771073
Edge: Node 30064771073 -> ARGUMENT -> Node 68719476737
Edge: Node 30064771073 -> ARGUMENT -> Node 55834574848

The following is an example, and it is Vulnerable.
int bdrv_snapshot_create(BlockDriverState *bs,

                         QEMUSnapshotInfo *sn_info)

{

    BlockDriver *drv = bs->drv;

    if (!drv)

        return -ENOMEDIUM;

    if (drv->bdrv_snapshot_create)

        return drv->bdrv_snapshot_create(bs, sn_info);

    if (bs->file)

        return bdrv_snapshot_create(bs->file, sn_info);

    return -ENOTSUP;

}

Answer (0 or 1):
```

## 9. devign/B2-labelonly/42/devign:validation:6185

SHA-256: 7609e5b1bd910ba65108a4c352508b520f3ccf4d8a20fd5c787e5cc1f7044170

Nguồn: Runs-management/dry_run_validation_20261102/devign/validation/B2-labelonly/42/prompts.jsonl

```text
You are now an excellent programmer. You are conducting a function vulnerability detection task for C/C++ language.

static void dummy_event_handler(void *opaque)

{

}

In the above code snippet, check for potential security vulnerabilities and answer with a single digit: 1 if Vulnerable, 0 if Non-vulnerable.

The node information of the code snippet is as follows:
Node 25769803776: (BLOCK) '{ }'
Node 107374182400: (METHOD) 'static void dummy_event_handler(void *op...'
Node 111669149696: (METHOD_PARAMETER_IN) 'void *opaque'
Node 115964116992: (METHOD_PARAMETER_OUT) 'void *opaque'
Node 124554051584: (METHOD_RETURN) 'RET'
Node 128849018880: (MODIFIER) '<empty>'
The edge information of the code snippet is as follows:
Edge: Node 107374182400 -> AST -> Node 111669149696
Edge: Node 107374182400 -> AST -> Node 25769803776
Edge: Node 107374182400 -> AST -> Node 128849018880
Edge: Node 107374182400 -> AST -> Node 124554051584
Edge: Node 107374182400 -> AST -> Node 115964116992
Edge: Node 107374182400 -> CFG -> Node 124554051584
Edge: Node 107374182400 -> CONTAINS -> Node 25769803776
Edge: Node 107374182400 -> DOMINATE -> Node 124554051584
Edge: Node 107374182400 -> REACHING_DEF -> Node 111669149696
Edge: Node 111669149696 -> PARAMETER_LINK -> Node 115964116992
Edge: Node 111669149696 -> REACHING_DEF -> Node 115964116992
Edge: Node 111669149696 -> REACHING_DEF -> Node 124554051584
Edge: Node 124554051584 -> POST_DOMINATE -> Node 107374182400

A function similar to the one above was labelled Non-vulnerable.

Answer (0 or 1):
```

## 10. devign/B2-nolabel/42/devign:validation:14776

SHA-256: 6e130de6f24ca18702da52ef57c7f5bc815e9e8fedc5fa2362f935c0a03befea

Nguồn: Runs-management/dry_run_validation_20261102/devign/validation/B2-nolabel/42/prompts.jsonl

```text
You are now an excellent programmer. You are conducting a function vulnerability detection task for C/C++ language.

static int dxtory_decode_v1_444(AVCodecContext *avctx, AVFrame *pic,

                                const uint8_t *src, int src_size)

{

    int h, w;

    uint8_t *Y, *U, *V;

    int ret;



    if (src_size < avctx->width * avctx->height * 3) {

        av_log(avctx, AV_LOG_ERROR, "packet too small\n");

        return AVERROR_INVALIDDATA;

    }



    avctx->pix_fmt = AV_PIX_FMT_YUV444P;

    if ((ret = ff_get_buffer(avctx, pic, 0)) < 0)

        return ret;



    Y = pic->data[0];

    U = pic->data[1];

    V = pic->data[2];

    for (h = 0; h < avctx->height; h++) {

        for (w = 0; w < avctx->width; w++) {

            Y[w] = *src++;

            U[w] = *src++ ^ 0x80;

            V[w] = *src++ ^ 0x80;

        }

        Y += pic->linesize[0];

        U += pic->linesize[1];

        V += pic->linesize[2];

    }



    return 0;

}

In the above code snippet, check for potential security vulnerabilities and answer with a single digit: 1 if Vulnerable, 0 if Non-vulnerable.

The node information of the code snippet is as follows:
Node 25769803776: (BLOCK) '{      int h, w;      uint8_t *Y, *U, *V...'
Node 25769803777: (BLOCK) '{          av_log(avctx, AV_LOG_ERROR, "...'
Node 25769803778: (BLOCK) '<empty>'
Node 25769803779: (BLOCK) '{          for (w = 0; w < avctx->width;...'
Node 25769803780: (BLOCK) '{ Y[w] = *src++; U[w] = *src++ ^ 0x80; V...'
Node 30064771072: (CALL) 'src_size < avctx->width * avctx->height ...'
Node 30064771073: (CALL) 'avctx->width * avctx->height * 3'
Node 30064771074: (CALL) 'avctx->width * avctx->height'
Node 30064771075: (CALL) 'avctx->width'
Node 30064771076: (CALL) 'avctx->height'
Node 30064771077: (CALL) 'av_log(avctx, AV_LOG_ERROR, "packet too ...'
Node 30064771078: (CALL) 'avctx->pix_fmt = AV_PIX_FMT_YUV444P'
Node 30064771079: (CALL) 'avctx->pix_fmt'
Node 30064771080: (CALL) '(ret = ff_get_buffer(avctx, pic, 0)) < 0'
Node 30064771081: (CALL) 'ret = ff_get_buffer(avctx, pic, 0)'
Node 30064771082: (CALL) 'ff_get_buffer(avctx, pic, 0)'
Node 30064771083: (CALL) 'Y = pic->data[0]'
Node 30064771084: (CALL) 'pic->data[0]'
Node 30064771085: (CALL) 'pic->data'
Node 30064771086: (CALL) 'U = pic->data[1]'
Node 30064771087: (CALL) 'pic->data[1]'
Node 30064771088: (CALL) 'pic->data'
Node 30064771089: (CALL) 'V = pic->data[2]'
Node 30064771090: (CALL) 'pic->data[2]'
Node 30064771091: (CALL) 'pic->data'
Node 30064771092: (CALL) 'h = 0'
Node 30064771093: (CALL) 'h < avctx->height'
Node 30064771094: (CALL) 'avctx->height'
Node 30064771095: (CALL) 'h++'
Node 30064771096: (CALL) 'w = 0'
Node 30064771097: (CALL) 'w < avctx->width'
Node 30064771098: (CALL) 'avctx->width'
Node 30064771099: (CALL) 'w++'
Node 30064771100: (CALL) 'Y[w] = *src++'
Node 30064771101: (CALL) 'Y[w]'
Node 30064771102: (CALL) '*src++'
Node 30064771103: (CALL) 'src++'
Node 30064771104: (CALL) 'U[w] = *src++ ^ 0x80'
Node 30064771105: (CALL) 'U[w]'
Node 30064771106: (CALL) '*src++ ^ 0x80'
The edge information of the code snippet is as follows:
Edge: Node 25769803776 -> AST -> Node 30064771078
Edge: Node 25769803776 -> AST -> Node 30064771083
Edge: Node 25769803776 -> AST -> Node 30064771086
Edge: Node 25769803776 -> AST -> Node 30064771089
Edge: Node 25769803777 -> AST -> Node 30064771077
Edge: Node 25769803780 -> AST -> Node 30064771100
Edge: Node 25769803780 -> AST -> Node 30064771104
Edge: Node 30064771072 -> ARGUMENT -> Node 30064771073
Edge: Node 30064771072 -> AST -> Node 30064771073
Edge: Node 30064771072 -> CDG -> Node 30064771077
Edge: Node 30064771072 -> CDG -> Node 30064771078
Edge: Node 30064771072 -> CDG -> Node 30064771079
Edge: Node 30064771072 -> CDG -> Node 30064771080

The following is a related example.
static int dxtory_decode_v1_420(AVCodecContext *avctx, AVFrame *pic,

                                const uint8_t *src, int src_size)

{

    int h, w;

    uint8_t *Y1, *Y2, *U, *V;

    int ret;



    if (src_size < avctx->width * avctx->height * 3 / 2) {

        av_log(avctx, AV_LOG_ERROR, "packet too small\n");

        return AVERROR_INVALIDDATA;

    }



    avctx->pix_fmt = AV_PIX_FMT_YUV420P;

    if ((ret = ff_get_buffer(avctx, pic, 0)) < 0)

        return ret;



    Y1 = pic->data[0];

    Y2 = pic->data[0] + pic->linesize[0];

    U  = pic->data[1];

    V  = pic->data[2];

    for (h = 0; h < avctx->height; h += 2) {

        for (w = 0; w < avctx->width; w += 2) {

            AV_COPY16(Y1 + w, src);

            AV_COPY16(Y2 + w, src + 2);

            U[w >> 1] = src[4] + 0x80;

            V[w >> 1] = src[5] + 0x80;

            src += 6;

        }

        Y1 += pic->linesize[0] << 1;

        Y2 += pic->linesize[0] << 1;

        U  += pic->linesize[1];

        V  += pic->linesize[2];

    }



    return 0;

}

Answer (0 or 1):
```

## 11. devign/B2-rand/42/devign:validation:18898

SHA-256: dace267918643a8cc49c611b145dd6b683111345404257afb2d53e457d9512af

Nguồn: Runs-management/dry_run_validation_20261102/devign/validation/B2-rand/42/prompts.jsonl

```text
You are now an excellent programmer. You are conducting a function vulnerability detection task for C/C++ language.

static int ftp_write(URLContext *h, const unsigned char *buf, int size)

{

    int err;

    FTPContext *s = h->priv_data;

    int written;



    av_dlog(h, "ftp protocol write %d bytes\n", size);



    if (s->state == DISCONNECTED) {

        if ((err = ftp_connect_data_connection(h)) < 0)

            return err;

    }

    if (s->state == READY) {

        if ((err = ftp_store(s)) < 0)

            return err;

    }

    if (s->conn_data && s->state == UPLOADING) {

        written = ffurl_write(s->conn_data, buf, size);

        if (written > 0) {

            s->position += written;

            s->filesize = FFMAX(s->filesize, s->position);

        }

        return written;

    }



    av_log(h, AV_LOG_ERROR, "FTP write failed\n");

    return AVERROR(EIO);

}

In the above code snippet, check for potential security vulnerabilities and answer with a single digit: 1 if Vulnerable, 0 if Non-vulnerable.

The node information of the code snippet is as follows:
Node 25769803776: (BLOCK) '{      int err;      FTPContext *s = h->...'
Node 25769803777: (BLOCK) '{ if ((err = ftp_connect_data_connection...'
Node 25769803778: (BLOCK) '<empty>'
Node 25769803779: (BLOCK) '{ if ((err = ftp_store(s)) < 0) return e...'
Node 25769803780: (BLOCK) '<empty>'
Node 25769803781: (BLOCK) '{          written = ffurl_write(s->conn...'
Node 25769803782: (BLOCK) '{              s->position += written;  ...'
Node 30064771072: (CALL) 's = h->priv_data'
Node 30064771073: (CALL) 'h->priv_data'
Node 30064771074: (CALL) 'av_dlog(h, "ftp protocol write %d bytes\...'
Node 30064771075: (CALL) 's->state == DISCONNECTED'
Node 30064771076: (CALL) 's->state'
Node 30064771077: (CALL) '(err = ftp_connect_data_connection(h)) <...'
Node 30064771078: (CALL) 'err = ftp_connect_data_connection(h)'
Node 30064771079: (CALL) 'ftp_connect_data_connection(h)'
Node 30064771080: (CALL) 's->state == READY'
Node 30064771081: (CALL) 's->state'
Node 30064771082: (CALL) '(err = ftp_store(s)) < 0'
Node 30064771083: (CALL) 'err = ftp_store(s)'
Node 30064771084: (CALL) 'ftp_store(s)'
Node 30064771085: (CALL) 's->conn_data && s->state == UPLOADING'
Node 30064771086: (CALL) 's->conn_data'
Node 30064771087: (CALL) 's->state == UPLOADING'
Node 30064771088: (CALL) 's->state'
Node 30064771089: (CALL) 'written = ffurl_write(s->conn_data, buf,...'
Node 30064771090: (CALL) 'ffurl_write(s->conn_data, buf, size)'
Node 30064771091: (CALL) 's->conn_data'
Node 30064771092: (CALL) 'written > 0'
Node 30064771093: (CALL) 's->position += written'
Node 30064771094: (CALL) 's->position'
Node 30064771095: (CALL) 's->filesize = FFMAX(s->filesize, s->posi...'
Node 30064771096: (CALL) 's->filesize'
Node 30064771097: (CALL) 'FFMAX(s->filesize, s->position)'
Node 30064771098: (CALL) 's->filesize'
Node 30064771099: (CALL) 's->position'
Node 30064771100: (CALL) 'av_log(h, AV_LOG_ERROR, "FTP write faile...'
Node 30064771101: (CALL) 'AVERROR(EIO)'
Node 47244640256: (CONTROL_STRUCTURE) 'if (s->state == DISCONNECTED) {         ...'
Node 47244640257: (CONTROL_STRUCTURE) 'if ((err = ftp_connect_data_connection(h...'
Node 47244640258: (CONTROL_STRUCTURE) 'if (s->state == READY) {          if ((e...'
The edge information of the code snippet is as follows:
Edge: Node 25769803776 -> AST -> Node 30064771072
Edge: Node 25769803776 -> AST -> Node 30064771074
Edge: Node 25769803776 -> AST -> Node 47244640256
Edge: Node 25769803776 -> AST -> Node 47244640258
Edge: Node 25769803776 -> AST -> Node 30064771100
Edge: Node 25769803777 -> AST -> Node 47244640257
Edge: Node 25769803781 -> AST -> Node 30064771089
Edge: Node 25769803782 -> AST -> Node 30064771093
Edge: Node 25769803782 -> AST -> Node 30064771095
Edge: Node 30064771072 -> ARGUMENT -> Node 30064771073
Edge: Node 30064771072 -> AST -> Node 30064771073
Edge: Node 30064771072 -> POST_DOMINATE -> Node 30064771073
Edge: Node 30064771073 -> CFG -> Node 30064771072

The following is an example, and it is Non-vulnerable.
static void nvdimm_build_ssdt(GSList *device_list, GArray *table_offsets,

                              GArray *table_data, BIOSLinker *linker,

                              GArray *dsm_dma_arrea)

{

    Aml *ssdt, *sb_scope, *dev;

    int mem_addr_offset, nvdimm_ssdt;



    acpi_add_table(table_offsets, table_data);



    ssdt = init_aml_allocator();

    acpi_data_push(ssdt->buf, sizeof(AcpiTableHeader));



    sb_scope = aml_scope("\\_SB");



    dev = aml_device("NVDR");



    /*

     * ACPI 6.0: 9.20 NVDIMM Devices:

     *

     * The ACPI Name Space device uses _HID of ACPI0012 to identify the root

     * NVDIMM interface device. Platform firmware is required to contain one

     * such device in _SB scope if NVDIMMs support is exposed by platform to

     * OSPM.

     * For each NVDIMM present or intended to be supported by platform,

     * platform firmware also exposes an ACPI Namespace Device under the

     * root device.

     */

    aml_append(dev, aml_name_decl("_HID", aml_string("ACPI0012")));



    nvdimm_build_common_dsm(dev);



    /* 0 is reserved for root device. */

    nvdimm_build_device_dsm(dev, 0);



    nvdimm_build_nvdimm_devices(device_list, dev);



    aml_append(sb_scope, dev);

    aml_append(ssdt, sb_scope);



    nvdimm_ssdt = table_data->len;



    /* copy AML table into ACPI tables blob and patch header there */

    g_array_append_vals(table_data, ssdt->buf->data, ssdt->buf->len);

    mem_addr_offset = build_append_named_dword(table_data,

                                               NVDIMM_ACPI_MEM_ADDR);



    bios_linker_loader_alloc(linker,

                             NVDIMM_DSM_MEM_FILE, dsm_dma_arrea,

                             sizeof(NvdimmDsmIn), false /* high memory */);

    bios_linker_loader_add_pointer(linker,

        ACPI_BUILD_TABLE_FILE, mem_addr_offset, sizeof(uint32_t),

        NVDIMM_DSM_MEM_FILE, 0);

    build_header(linker, table_data,

        (void *)(table_data->data + nvdimm_ssdt),

        "SSDT", table_data->len - nvdimm_ssdt, 1, NULL, "NVDIMM");

    free_aml_allocator();

}

Answer (0 or 1):
```

## 12. devign/B2-rand/43/devign:validation:1572

SHA-256: 06ed2f36e1f14059a70be1498f6a7bcede00411cbbb4de422fe184d9fa579ad7

Nguồn: Runs-management/dry_run_validation_20261102/devign/validation/B2-rand/43/prompts.jsonl

```text
You are now an excellent programmer. You are conducting a function vulnerability detection task for C/C++ language.

int kvmppc_fixup_cpu(PowerPCCPU *cpu)

{

    CPUState *cs = CPU(cpu);

    int smt;



    /* Adjust cpu index for SMT */

    smt = kvmppc_smt_threads();

    cs->cpu_index = (cs->cpu_index / smp_threads) * smt

        + (cs->cpu_index % smp_threads);



    return 0;

}

In the above code snippet, check for potential security vulnerabilities and answer with a single digit: 1 if Vulnerable, 0 if Non-vulnerable.

The node information of the code snippet is as follows:
Node 25769803776: (BLOCK) '{      CPUState *cs = CPU(cpu);      int...'
Node 30064771072: (CALL) 'cs = CPU(cpu)'
Node 30064771073: (CALL) 'CPU(cpu)'
Node 30064771074: (CALL) 'smt = kvmppc_smt_threads()'
Node 30064771075: (CALL) 'kvmppc_smt_threads()'
Node 30064771076: (CALL) 'cs->cpu_index = (cs->cpu_index / smp_thr...'
Node 30064771077: (CALL) 'cs->cpu_index'
Node 30064771078: (CALL) '(cs->cpu_index / smp_threads) * smt + (c...'
Node 30064771079: (CALL) '(cs->cpu_index / smp_threads) * smt'
Node 30064771080: (CALL) 'cs->cpu_index / smp_threads'
Node 30064771081: (CALL) 'cs->cpu_index'
Node 30064771082: (CALL) 'cs->cpu_index % smp_threads'
Node 30064771083: (CALL) 'cs->cpu_index'
Node 55834574848: (FIELD_IDENTIFIER) 'cpu_index'
Node 55834574849: (FIELD_IDENTIFIER) 'cpu_index'
Node 55834574850: (FIELD_IDENTIFIER) 'cpu_index'
Node 68719476736: (IDENTIFIER) 'cs'
Node 68719476737: (IDENTIFIER) 'cpu'
Node 68719476738: (IDENTIFIER) 'smt'
Node 68719476739: (IDENTIFIER) 'cs'
Node 68719476740: (IDENTIFIER) 'cs'
Node 68719476741: (IDENTIFIER) '<unknown> smp_threads'
Node 68719476742: (IDENTIFIER) 'smt'
Node 68719476743: (IDENTIFIER) 'cs'
Node 68719476744: (IDENTIFIER) '<unknown> smp_threads'
Node 90194313216: (LITERAL) '0'
Node 94489280512: (LOCAL) 'CPUState *cs'
Node 94489280513: (LOCAL) 'int smt'
Node 94489280514: (LOCAL) '<unknown> smp_threads'
Node 107374182400: (METHOD) 'int kvmppc_fixup_cpu(PowerPCCPU *cpu)  {...'
Node 111669149696: (METHOD_PARAMETER_IN) 'PowerPCCPU *cpu'
Node 115964116992: (METHOD_PARAMETER_OUT) 'PowerPCCPU *cpu'
Node 124554051584: (METHOD_RETURN) 'RET'
Node 141733920768: (RETURN) 'return 0;'
The edge information of the code snippet is as follows:
Edge: Node 25769803776 -> AST -> Node 94489280512
Edge: Node 25769803776 -> AST -> Node 30064771072
Edge: Node 25769803776 -> AST -> Node 94489280513
Edge: Node 25769803776 -> AST -> Node 30064771074
Edge: Node 25769803776 -> AST -> Node 30064771076
Edge: Node 25769803776 -> AST -> Node 141733920768
Edge: Node 25769803776 -> AST -> Node 94489280514
Edge: Node 30064771072 -> ARGUMENT -> Node 68719476736
Edge: Node 30064771072 -> ARGUMENT -> Node 30064771073
Edge: Node 30064771072 -> AST -> Node 68719476736
Edge: Node 30064771072 -> AST -> Node 30064771073
Edge: Node 30064771072 -> CFG -> Node 68719476738
Edge: Node 30064771072 -> DOMINATE -> Node 68719476738
Edge: Node 30064771072 -> POST_DOMINATE -> Node 30064771073
Edge: Node 30064771072 -> REACHING_DEF -> Node 124554051584
Edge: Node 30064771073 -> ARGUMENT -> Node 68719476737
Edge: Node 30064771073 -> AST -> Node 68719476737
Edge: Node 30064771073 -> CFG -> Node 30064771072
Edge: Node 30064771073 -> DOMINATE -> Node 30064771072

The following is an example, and it is Vulnerable.
static int poll_frame(AVFilterLink *link)

{

    AVFilterContext   *s = link->src;

    OverlayContext *over = s->priv;

    int ret = avfilter_poll_frame(s->inputs[OVERLAY]);



    if (ret == AVERROR_EOF)

        ret = !!over->overpicref;



    return ret && avfilter_poll_frame(s->inputs[MAIN]);

}

Answer (0 or 1):
```

## 13. devign/B2-rand/44/devign:validation:7309

SHA-256: 98b43309933ecbef54d5a00713d4530979db444ce250483e0f63e2d361112f2e

Nguồn: Runs-management/dry_run_validation_20261102/devign/validation/B2-rand/44/prompts.jsonl

```text
You are now an excellent programmer. You are conducting a function vulnerability detection task for C/C++ language.

pci_e1000_init(PCIBus *bus, NICInfo *nd, int devfn)

{

    E1000State *d;

    uint8_t *pci_conf;

    uint16_t checksum = 0;

    static const char info_str[] = "e1000";

    int i;



    d = (E1000State *)pci_register_device(bus, "e1000",

                sizeof(E1000State), devfn, NULL, NULL);



    pci_conf = d->dev.config;

    memset(pci_conf, 0, 256);



    pci_config_set_vendor_id(pci_conf, PCI_VENDOR_ID_INTEL);

    pci_config_set_device_id(pci_conf, E1000_DEVID);

    *(uint16_t *)(pci_conf+0x04) = cpu_to_le16(0x0407);

    *(uint16_t *)(pci_conf+0x06) = cpu_to_le16(0x0010);

    pci_conf[0x08] = 0x03;

    pci_config_set_class(pci_conf, PCI_CLASS_NETWORK_ETHERNET);

    pci_conf[0x0c] = 0x10;



    pci_conf[0x3d] = 1; // interrupt pin 0



    d->mmio_index = cpu_register_io_memory(0, e1000_mmio_read,

            e1000_mmio_write, d);



    pci_register_io_region((PCIDevice *)d, 0, PNPMMIO_SIZE,

                           PCI_ADDRESS_SPACE_MEM, e1000_mmio_map);



    pci_register_io_region((PCIDevice *)d, 1, IOPORT_SIZE,

                           PCI_ADDRESS_SPACE_IO, ioport_map);



    memmove(d->eeprom_data, e1000_eeprom_template,

        sizeof e1000_eeprom_template);

    for (i = 0; i < 3; i++)

        d->eeprom_data[i] = (nd->macaddr[2*i+1]<<8) | nd->macaddr[2*i];

    for (i = 0; i < EEPROM_CHECKSUM_REG; i++)

        checksum += d->eeprom_data[i];

    checksum = (uint16_t) EEPROM_SUM - checksum;

    d->eeprom_data[EEPROM_CHECKSUM_REG] = checksum;



    memset(d->phy_reg, 0, sizeof d->phy_reg);

    memmove(d->phy_reg, phy_reg_init, sizeof phy_reg_init);

    memset(d->mac_reg, 0, sizeof d->mac_reg);

    memmove(d->mac_reg, mac_reg_init, sizeof mac_reg_init);

    d->rxbuf_min_shift = 1;

    memset(&d->tx, 0, sizeof d->tx);



    d->vc = qemu_new_vlan_client(nd->vlan, nd->model, nd->name,

                                 e1000_receive, e1000_can_receive, d);

    d->vc->link_status_changed = e1000_set_link_status;



    qemu_format_nic_info_str(d->vc, nd->macaddr);



    register_savevm(info_str, -1, 2, nic_save, nic_load, d);

    d->dev.unregister = pci_e1000_uninit;



    return (PCIDevice *)d;

}

In the above code snippet, check for potential security vulnerabilities and answer with a single digit: 1 if Vulnerable, 0 if Non-vulnerable.

The node information of the code snippet is as follows:
Node 25769803776: (BLOCK) '{      E1000State *d;      uint8_t *pci_...'
Node 30064771072: (CALL) 'checksum = 0'
Node 30064771073: (CALL) 'info_str[] = "e1000"'
Node 30064771074: (CALL) 'd = (E1000State *)pci_register_device(bu...'
Node 30064771075: (CALL) '(E1000State *)pci_register_device(bus, "...'
Node 30064771076: (CALL) 'pci_register_device(bus, "e1000", sizeof...'
Node 30064771077: (CALL) 'sizeof(E1000State)'
Node 30064771078: (CALL) 'pci_conf = d->dev.config'
Node 30064771079: (CALL) 'd->dev.config'
Node 30064771080: (CALL) 'd->dev'
Node 30064771081: (CALL) 'memset(pci_conf, 0, 256)'
Node 30064771082: (CALL) 'pci_config_set_vendor_id(pci_conf, PCI_V...'
Node 30064771083: (CALL) 'pci_config_set_device_id(pci_conf, E1000...'
Node 30064771084: (CALL) '*(uint16_t *)(pci_conf+0x04) = cpu_to_le...'
Node 30064771085: (CALL) '*(uint16_t *)(pci_conf+0x04)'
Node 30064771086: (CALL) '(uint16_t *)(pci_conf+0x04)'
Node 30064771087: (CALL) 'pci_conf+0x04'
Node 30064771088: (CALL) 'cpu_to_le16(0x0407)'
Node 30064771089: (CALL) '*(uint16_t *)(pci_conf+0x06) = cpu_to_le...'
Node 30064771090: (CALL) '*(uint16_t *)(pci_conf+0x06)'
Node 30064771091: (CALL) '(uint16_t *)(pci_conf+0x06)'
Node 30064771092: (CALL) 'pci_conf+0x06'
Node 30064771093: (CALL) 'cpu_to_le16(0x0010)'
Node 30064771094: (CALL) 'pci_conf[0x08] = 0x03'
Node 30064771095: (CALL) 'pci_conf[0x08]'
Node 30064771096: (CALL) 'pci_config_set_class(pci_conf, PCI_CLASS...'
Node 30064771097: (CALL) 'pci_conf[0x0c] = 0x10'
Node 30064771098: (CALL) 'pci_conf[0x0c]'
Node 30064771099: (CALL) 'pci_conf[0x3d] = 1'
Node 30064771100: (CALL) 'pci_conf[0x3d]'
Node 30064771101: (CALL) 'd->mmio_index = cpu_register_io_memory(0...'
Node 30064771102: (CALL) 'd->mmio_index'
Node 30064771103: (CALL) 'cpu_register_io_memory(0, e1000_mmio_rea...'
Node 30064771104: (CALL) 'pci_register_io_region((PCIDevice *)d, 0...'
Node 30064771105: (CALL) '(PCIDevice *)d'
Node 30064771106: (CALL) 'pci_register_io_region((PCIDevice *)d, 1...'
Node 30064771107: (CALL) '(PCIDevice *)d'
Node 30064771108: (CALL) 'memmove(d->eeprom_data, e1000_eeprom_tem...'
Node 30064771109: (CALL) 'd->eeprom_data'
Node 30064771110: (CALL) 'sizeof e1000_eeprom_template'
The edge information of the code snippet is as follows:
Edge: Node 25769803776 -> AST -> Node 30064771072
Edge: Node 25769803776 -> AST -> Node 30064771073
Edge: Node 25769803776 -> AST -> Node 30064771074
Edge: Node 25769803776 -> AST -> Node 30064771078
Edge: Node 25769803776 -> AST -> Node 30064771081
Edge: Node 25769803776 -> AST -> Node 30064771082
Edge: Node 25769803776 -> AST -> Node 30064771083
Edge: Node 25769803776 -> AST -> Node 30064771084
Edge: Node 25769803776 -> AST -> Node 30064771089

The following is an example, and it is Non-vulnerable.
int av_open_input_file(AVFormatContext **ic_ptr, const char *filename, 

                       AVInputFormat *fmt,

                       int buf_size,

                       AVFormatParameters *ap)

{

    AVFormatContext *ic = NULL;

    int err;

    char buf[PROBE_BUF_SIZE];

    AVProbeData probe_data, *pd = &probe_data;



    ic = av_mallocz(sizeof(AVFormatContext));

    if (!ic) {

        err = AVERROR_NOMEM;

        goto fail;

    }

    pstrcpy(ic->filename, sizeof(ic->filename), filename);

    pd->filename = ic->filename;

    pd->buf = buf;

    pd->buf_size = 0;



    if (!fmt) {

        /* guess format if no file can be opened  */

        fmt = probe_input_format(pd, 0);

    }



    /* if no file needed do not try to open one */

    if (!fmt || !(fmt->flags & AVFMT_NOFILE)) {

        if (url_fopen(&ic->pb, filename, URL_RDONLY) < 0) {

            err = AVERROR_IO;

            goto fail;

        }

        if (buf_size > 0) {

            url_setbufsize(&ic->pb, buf_size);

        }

        /* read probe data */

        pd->buf_size = get_buffer(&ic->pb, buf, PROBE_BUF_SIZE);

        url_fseek(&ic->pb, 0, SEEK_SET);

    }

    

    /* guess file format */

    if (!fmt) {

        fmt = probe_input_format(pd, 1);

    }



    /* if still no format found, error */

    if (!fmt) {

        err = AVERROR_NOFMT;

        goto fail;

    }

        

    ic->iformat = fmt;



    /* allocate private data */

    ic->priv_data = av_mallocz(fmt->priv_data_size);

    if (!ic->priv_data) {

        err = AVERROR_NOMEM;

        goto fail;

    }



    /* check filename in case of an image number is expected */

    if (ic->iformat->flags & AVFMT_NEEDNUMBER) {

        if (filename_number_test(ic->filename) < 0) { 

            err = AVERROR_NUMEXPECTED;

            goto fail1;

        }

    }

    

    err = ic->iformat->read_header(ic, ap);

    if (err < 0)

        goto fail1;

    *ic_ptr = ic;

    return 0;

 fail1:

    if (!(fmt->flags & AVFMT_NOFILE)) {

        url_fclose(&ic->pb);

    }

 fail:

    if (ic) {

        av_free(ic->priv_data);

    }

    av_free(ic);

    *ic_ptr = NULL;

    return err;

}

Answer (0 or 1):
```

## 14. devign/B2-rep/42/devign:validation:22187

SHA-256: 8a13552e9a1c3549d773d11e497a9a42d3e1d8aeafb3a2db6c4238bb6afb67fb

Nguồn: Runs-management/dry_run_validation_20261102/devign/validation/B2-rep/42/prompts.jsonl

```text
You are now an excellent programmer. You are conducting a function vulnerability detection task for C/C++ language.

PCIBus *pci_find_bus(PCIBus *bus, int bus_num)

{

    PCIBus *sec;



    if (!bus)

        return NULL;



    if (pci_bus_num(bus) == bus_num) {

        return bus;

    }



    /* try child bus */

    QLIST_FOREACH(sec, &bus->child, sibling) {



        if (!bus->parent_dev /* pci host bridge */

            || (pci_bus_num(sec) <= bus_num &&

                bus->parent_dev->config[PCI_SUBORDINATE_BUS])) {

            return pci_find_bus(sec, bus_num);

        }

    }



    return NULL;

}

In the above code snippet, check for potential security vulnerabilities and answer with a single digit: 1 if Vulnerable, 0 if Non-vulnerable.

The node information of the code snippet is as follows:
Node 25769803776: (BLOCK) '{      PCIBus *sec;        if (!bus)    ...'
Node 25769803777: (BLOCK) '<empty>'
Node 25769803778: (BLOCK) '{ return bus; }'
Node 25769803779: (BLOCK) '{            if (!bus->parent_dev /* pci...'
Node 25769803780: (BLOCK) '{ return pci_find_bus(sec, bus_num); }'
Node 30064771072: (CALL) '!bus'
Node 30064771073: (CALL) 'pci_bus_num(bus) == bus_num'
Node 30064771074: (CALL) 'pci_bus_num(bus)'
Node 30064771075: (CALL) 'QLIST_FOREACH(sec, &bus->child, sibling)'
Node 30064771076: (CALL) '&bus->child'
Node 30064771077: (CALL) 'bus->child'
Node 30064771078: (CALL) '!bus->parent_dev /* pci host bridge */  ...'
Node 30064771079: (CALL) '!bus->parent_dev'
Node 30064771080: (CALL) 'bus->parent_dev'
Node 30064771081: (CALL) 'pci_bus_num(sec) <= bus_num &&          ...'
Node 30064771082: (CALL) 'pci_bus_num(sec) <= bus_num'
Node 30064771083: (CALL) 'pci_bus_num(sec)'
Node 30064771084: (CALL) 'bus->parent_dev->config[PCI_SUBORDINATE_...'
Node 30064771085: (CALL) 'bus->parent_dev->config'
Node 30064771086: (CALL) 'bus->parent_dev'
Node 30064771087: (CALL) 'pci_find_bus(sec, bus_num)'
Node 47244640256: (CONTROL_STRUCTURE) 'if (!bus) return NULL;'
Node 47244640257: (CONTROL_STRUCTURE) 'if (pci_bus_num(bus) == bus_num) { retur...'
Node 47244640258: (CONTROL_STRUCTURE) 'if (!bus->parent_dev /* pci host bridge ...'
Node 55834574848: (FIELD_IDENTIFIER) 'child'
Node 55834574849: (FIELD_IDENTIFIER) 'parent_dev'
Node 55834574850: (FIELD_IDENTIFIER) 'parent_dev'
Node 55834574851: (FIELD_IDENTIFIER) 'config'
Node 68719476736: (IDENTIFIER) 'bus'
Node 68719476737: (IDENTIFIER) '<unknown> NULL'
Node 68719476738: (IDENTIFIER) 'bus'
Node 68719476739: (IDENTIFIER) 'bus_num'
Node 68719476740: (IDENTIFIER) 'bus'
Node 68719476741: (IDENTIFIER) 'sec'
Node 68719476742: (IDENTIFIER) 'bus'
Node 68719476743: (IDENTIFIER) '<unknown> sibling'
Node 68719476744: (IDENTIFIER) 'bus'
Node 68719476745: (IDENTIFIER) 'sec'
Node 68719476746: (IDENTIFIER) 'bus_num'
Node 68719476747: (IDENTIFIER) 'bus'
The edge information of the code snippet is as follows:
Edge: Node 25769803776 -> AST -> Node 47244640256
Edge: Node 25769803776 -> AST -> Node 47244640257
Edge: Node 25769803776 -> AST -> Node 30064771075
Edge: Node 25769803776 -> AST -> Node 25769803779
Edge: Node 25769803779 -> AST -> Node 47244640258
Edge: Node 30064771072 -> ARGUMENT -> Node 68719476736
Edge: Node 30064771072 -> AST -> Node 68719476736
Edge: Node 30064771072 -> CDG -> Node 30064771074
Edge: Node 30064771072 -> CDG -> Node 30064771073
Edge: Node 30064771072 -> CDG -> Node 68719476739
Edge: Node 30064771072 -> CDG -> Node 68719476738
Edge: Node 30064771072 -> CDG -> Node 68719476737
Edge: Node 30064771072 -> CFG -> Node 68719476737
Edge: Node 30064771072 -> CFG -> Node 68719476738
Edge: Node 30064771072 -> DOMINATE -> Node 68719476737

The following is an example, and it is Non-vulnerable.
static void pxb_register_bus(PCIDevice *dev, PCIBus *pxb_bus, Error **errp)

{

    PCIBus *bus = dev->bus;

    int pxb_bus_num = pci_bus_num(pxb_bus);



    if (bus->parent_dev) {

        error_setg(errp, "PXB devices can be attached only to root bus");

        return;

    }



    QLIST_FOREACH(bus, &bus->child, sibling) {

        if (pci_bus_num(bus) == pxb_bus_num) {

            error_setg(errp, "Bus %d is already in use", pxb_bus_num);

            return;

        }

    }

    QLIST_INSERT_HEAD(&dev->bus->child, pxb_bus, sibling);

}

Answer (0 or 1):
```

## 15. devign/B1-full/42/devign:validation:7152

SHA-256: 3a24fa5e7b1e5cabfe58d7f1c4c9470ba0e25576e18b7842a7d01e281f6dbde1

Nguồn: Runs-management/dry_run_validation_20261102/devign/validation/B1-full/42/prompts.jsonl

```text
You are now an excellent programmer. You are conducting a function vulnerability detection task for C/C++ language.

void qemu_mutex_unlock_iothread(void) {}

In the above code snippet, check for potential security vulnerabilities and answer with a single digit: 1 if Vulnerable, 0 if Non-vulnerable.

The node information of the code snippet is as follows:
Node 25769803776: (BLOCK) '{}'
Node 107374182400: (METHOD) 'void qemu_mutex_unlock_iothread(void) {}'
Node 111669149696: (METHOD_PARAMETER_IN) 'void'
Node 115964116992: (METHOD_PARAMETER_OUT) 'void'
Node 124554051584: (METHOD_RETURN) 'RET'
The edge information of the code snippet is as follows:
Edge: Node 107374182400 -> AST -> Node 111669149696
Edge: Node 107374182400 -> AST -> Node 25769803776
Edge: Node 107374182400 -> AST -> Node 124554051584
Edge: Node 107374182400 -> AST -> Node 115964116992
Edge: Node 107374182400 -> CFG -> Node 124554051584
Edge: Node 107374182400 -> CONTAINS -> Node 25769803776
Edge: Node 107374182400 -> DOMINATE -> Node 124554051584
Edge: Node 107374182400 -> REACHING_DEF -> Node 111669149696
Edge: Node 111669149696 -> PARAMETER_LINK -> Node 115964116992
Edge: Node 111669149696 -> REACHING_DEF -> Node 115964116992
Edge: Node 111669149696 -> REACHING_DEF -> Node 124554051584
Edge: Node 124554051584 -> POST_DOMINATE -> Node 107374182400

The following is an example, and it is .


Answer (0 or 1):
```

## 16. devign/B0/42/devign:validation:16235

SHA-256: 439fc51444b5615eeb7e24c15c7214d953371800438b099e720d3b29856886da

Nguồn: Runs-management/dry_run_validation_20261102/devign/validation/B0/42/prompts.jsonl

```text
You are now an excellent programmer. You are conducting a function vulnerability detection task for C/C++ language.

static void pxa2xx_timer_write(void *opaque, target_phys_addr_t offset,

                uint32_t value)

{

    int i, tm = 0;

    PXA2xxTimerInfo *s = (PXA2xxTimerInfo *) opaque;



    switch (offset) {

    case OSMR3:  tm ++;

    case OSMR2:  tm ++;

    case OSMR1:  tm ++;

    case OSMR0:

        s->timer[tm].value = value;

        pxa2xx_timer_update(s, qemu_get_clock(vm_clock));

        break;

    case OSMR11: tm ++;

    case OSMR10: tm ++;

    case OSMR9:  tm ++;

    case OSMR8:  tm ++;

    case OSMR7:  tm ++;

    case OSMR6:  tm ++;

    case OSMR5:  tm ++;

    case OSMR4:

        if (!pxa2xx_timer_has_tm4(s))

            goto badreg;

        s->tm4[tm].tm.value = value;

        pxa2xx_timer_update4(s, qemu_get_clock(vm_clock), tm);

        break;

    case OSCR:

        s->oldclock = s->clock;

        s->lastload = qemu_get_clock(vm_clock);

        s->clock = value;

        pxa2xx_timer_update(s, s->lastload);

        break;

    case OSCR11: tm ++;

    case OSCR10: tm ++;

    case OSCR9:  tm ++;

    case OSCR8:  tm ++;

    case OSCR7:  tm ++;

    case OSCR6:  tm ++;

    case OSCR5:  tm ++;

    case OSCR4:

        if (!pxa2xx_timer_has_tm4(s))

            goto badreg;

        s->tm4[tm].oldclock = s->tm4[tm].clock;

        s->tm4[tm].lastload = qemu_get_clock(vm_clock);

        s->tm4[tm].clock = value;

        pxa2xx_timer_update4(s, s->tm4[tm].lastload, tm);

        break;

    case OIER:

        s->irq_enabled = value & 0xfff;

        break;

    case OSSR:	/* Status register */

        s->events &= ~value;

        for (i = 0; i < 4; i ++, value >>= 1) {

            if (s->timer[i].level && (value & 1)) {

                s->timer[i].level = 0;

                qemu_irq_lower(s->timer[i].irq);

            }

        }

        if (pxa2xx_timer_has_tm4(s)) {

            for (i = 0; i < 8; i ++, value >>= 1)

                if (s->tm4[i].tm.level && (value & 1))

                    s->tm4[i].tm.level = 0;

            if (!(s->events & 0xff0))

                qemu_irq_lower(s->tm4->tm.irq);

        }

        break;

    case OWER:	/* XXX: Reset on OSMR3 match? */

        s->reset3 = value;

        break;

    case OMCR7:  tm ++;

    case OMCR6:  tm ++;

    case OMCR5:  tm ++;

    case OMCR4:

        if (!pxa2xx_timer_has_tm4(s))

            goto badreg;

        s->tm4[tm].control = value & 0x0ff;

        /* XXX Stop if running (shouldn't happen) */

        if ((value & (1 << 7)) || tm == 0)

            s->tm4[tm].freq = pxa2xx_timer4_freq[value & 7];

        else {

            s->tm4[tm].freq = 0;

            pxa2xx_timer_update4(s, qemu_get_clock(vm_clock), tm);

        }

        break;

    case OMCR11: tm ++;

    case OMCR10: tm ++;

    case OMCR9:  tm ++;

    case OMCR8:  tm += 4;

        if (!pxa2xx_timer_has_tm4(s))

            goto badreg;

        s->tm4[tm].control = value & 0x3ff;

        /* XXX Stop if running (shouldn't happen) */

        if ((value & (1 << 7)) || !(tm & 1))

            s->tm4[tm].freq =

                    pxa2xx_timer4_freq[(value & (1 << 8)) ?  0 : (value & 7)];

        else {

            s->tm4[tm].freq = 0;

            pxa2xx_timer_update4(s, qemu_get_clock(vm_clock), tm);

        }

        break;

    default:

    badreg:

        hw_error("pxa2xx_timer_write: Bad offset " REG_FMT "\n", offset);

    }

}

In the above code snippet, check for potential security vulnerabilities and answer with a single digit: 1 if Vulnerable, 0 if Non-vulnerable.

The node information of the code snippet is as follows:

The edge information of the code snippet is as follows:


The following is an example, and it is .


Answer (0 or 1):
```

## 17. devign/B0/42/devign:validation:24048

SHA-256: 863d5e0625a748b6aa892a79b1da4685bda47cd5ba77c2c8bdf639de32d67a05

Nguồn: Runs-management/dry_run_validation_20261102/devign/validation/B0/42/prompts.jsonl

```text
You are now an excellent programmer. You are conducting a function vulnerability detection task for C/C++ language.

static void ts_str(char buffer[60], int64_t ts, AVRational base)

{

    if (ts == AV_NOPTS_VALUE) {

        strcpy(buffer, " NOPTS   ");

        return;

    }

    ts= av_rescale_q(ts, base, (AVRational){1, 1000000});

    snprintf(buffer, 60, "%c%Ld.%06Ld", ts<0 ? '-' : ' ', FFABS(ts)/1000000, FFABS(ts)%1000000);

}

In the above code snippet, check for potential security vulnerabilities and answer with a single digit: 1 if Vulnerable, 0 if Non-vulnerable.

The node information of the code snippet is as follows:

The edge information of the code snippet is as follows:


The following is an example, and it is .


Answer (0 or 1):
```

## 18. devign/B0/42/devign:validation:3757

SHA-256: 2481de53ce5c82bf4eee59857184072620f936e3db70312a9ef0e600206aad7d

Nguồn: Runs-management/dry_run_validation_20261102/devign/validation/B0/42/prompts.jsonl

```text
You are now an excellent programmer. You are conducting a function vulnerability detection task for C/C++ language.

static int nbd_co_send_request(BDRVNBDState *s, struct nbd_request *request,

                               struct iovec *iov, int offset)

{

    int rc, ret;



    qemu_co_mutex_lock(&s->send_mutex);

    s->send_coroutine = qemu_coroutine_self();

    qemu_aio_set_fd_handler(s->sock, nbd_reply_ready, nbd_restart_write,

                            nbd_have_request, NULL, s);

    rc = nbd_send_request(s->sock, request);

    if (rc >= 0 && iov) {

        ret = qemu_co_sendv(s->sock, iov, request->len, offset);

        if (ret != request->len) {

            errno = -EIO;

            rc = -1;

        }

    }

    qemu_aio_set_fd_handler(s->sock, nbd_reply_ready, NULL,

                            nbd_have_request, NULL, s);

    s->send_coroutine = NULL;

    qemu_co_mutex_unlock(&s->send_mutex);

    return rc;

}

In the above code snippet, check for potential security vulnerabilities and answer with a single digit: 1 if Vulnerable, 0 if Non-vulnerable.

The node information of the code snippet is as follows:

The edge information of the code snippet is as follows:


The following is an example, and it is .


Answer (0 or 1):
```

## 19. devign/B0/42/devign:validation:15954

SHA-256: e14d29b6b3cff4988b300eee3f00f532b296cb22341bfb11d0a72bee8d5cb29f

Nguồn: Runs-management/dry_run_validation_20261102/devign/validation/B0/42/prompts.jsonl

```text
You are now an excellent programmer. You are conducting a function vulnerability detection task for C/C++ language.

static void migration_bitmap_sync_range(ram_addr_t start, ram_addr_t length)

{

    migration_dirty_pages +=

        cpu_physical_memory_sync_dirty_bitmap(migration_bitmap, start, length);

}

In the above code snippet, check for potential security vulnerabilities and answer with a single digit: 1 if Vulnerable, 0 if Non-vulnerable.

The node information of the code snippet is as follows:

The edge information of the code snippet is as follows:


The following is an example, and it is .


Answer (0 or 1):
```

## 20. devign/B2-rep/42/devign:validation:15973

SHA-256: ca53ec6206f1b30be7cfb17e0f5dbf66b426fadd7743321774593f38575e43ae

Nguồn: Runs-management/dry_run_validation_20261102/devign/validation/B2-rep/42/prompts.jsonl

```text
You are now an excellent programmer. You are conducting a function vulnerability detection task for C/C++ language.

static int pci_unin_map_irq(PCIDevice *pci_dev, int irq_num)

{

    int retval;

    int devfn = pci_dev->devfn & 0x00FFFFFF;



    retval = (((devfn >> 11) & 0x1F) + irq_num) & 3;



    return retval;

}

In the above code snippet, check for potential security vulnerabilities and answer with a single digit: 1 if Vulnerable, 0 if Non-vulnerable.

The node information of the code snippet is as follows:
Node 25769803776: (BLOCK) '{      int retval;      int devfn = pci_...'
Node 30064771072: (CALL) 'devfn = pci_dev->devfn & 0x00FFFFFF'
Node 30064771073: (CALL) 'pci_dev->devfn & 0x00FFFFFF'
Node 30064771074: (CALL) 'pci_dev->devfn'
Node 30064771075: (CALL) 'retval = (((devfn >> 11) & 0x1F) + irq_n...'
Node 30064771076: (CALL) '(((devfn >> 11) & 0x1F) + irq_num) & 3'
Node 30064771077: (CALL) '((devfn >> 11) & 0x1F) + irq_num'
Node 30064771078: (CALL) '(devfn >> 11) & 0x1F'
Node 30064771079: (CALL) 'devfn >> 11'
Node 55834574848: (FIELD_IDENTIFIER) 'devfn'
Node 68719476736: (IDENTIFIER) 'devfn'
Node 68719476737: (IDENTIFIER) 'pci_dev'
Node 68719476738: (IDENTIFIER) 'retval'
Node 68719476739: (IDENTIFIER) 'devfn'
Node 68719476740: (IDENTIFIER) 'irq_num'
Node 68719476741: (IDENTIFIER) 'retval'
Node 90194313216: (LITERAL) '0x00FFFFFF'
Node 90194313217: (LITERAL) '11'
Node 90194313218: (LITERAL) '0x1F'
Node 90194313219: (LITERAL) '3'
Node 94489280512: (LOCAL) 'int retval'
Node 94489280513: (LOCAL) 'int devfn'
Node 107374182400: (METHOD) 'static int pci_unin_map_irq(PCIDevice *p...'
Node 111669149696: (METHOD_PARAMETER_IN) 'PCIDevice *pci_dev'
Node 111669149697: (METHOD_PARAMETER_IN) 'int irq_num'
Node 115964116992: (METHOD_PARAMETER_OUT) 'PCIDevice *pci_dev'
Node 115964116993: (METHOD_PARAMETER_OUT) 'int irq_num'
Node 124554051584: (METHOD_RETURN) 'RET'
Node 128849018880: (MODIFIER) '<empty>'
Node 141733920768: (RETURN) 'return retval;'
The edge information of the code snippet is as follows:
Edge: Node 25769803776 -> AST -> Node 94489280512
Edge: Node 25769803776 -> AST -> Node 94489280513
Edge: Node 25769803776 -> AST -> Node 30064771072
Edge: Node 25769803776 -> AST -> Node 30064771075
Edge: Node 25769803776 -> AST -> Node 141733920768
Edge: Node 30064771072 -> ARGUMENT -> Node 68719476736
Edge: Node 30064771072 -> ARGUMENT -> Node 30064771073
Edge: Node 30064771072 -> AST -> Node 68719476736
Edge: Node 30064771072 -> AST -> Node 30064771073
Edge: Node 30064771072 -> CFG -> Node 68719476738
Edge: Node 30064771072 -> DOMINATE -> Node 68719476738
Edge: Node 30064771072 -> POST_DOMINATE -> Node 30064771073
Edge: Node 30064771072 -> REACHING_DEF -> Node 124554051584
Edge: Node 30064771073 -> ARGUMENT -> Node 30064771074
Edge: Node 30064771073 -> ARGUMENT -> Node 90194313216
Edge: Node 30064771073 -> AST -> Node 30064771074
Edge: Node 30064771073 -> AST -> Node 90194313216
Edge: Node 30064771073 -> CFG -> Node 30064771072
Edge: Node 30064771073 -> DOMINATE -> Node 30064771072
Edge: Node 30064771073 -> POST_DOMINATE -> Node 90194313216
Edge: Node 30064771073 -> REACHING_DEF -> Node 68719476736

The following is an example, and it is Non-vulnerable.
static int pci_apb_map_irq(PCIDevice *pci_dev, int irq_num)

{

    return ((pci_dev->devfn & 0x18) >> 1) + irq_num;

}

Answer (0 or 1):
```

## 21. devign/B1/42/devign:validation:22511

SHA-256: 1fa0478180b3621da53e188d378ea9c885a6fefe482a466036d4edf231b284df

Nguồn: Runs-management/dry_run_validation_20261102/devign/validation/B1/42/prompts.jsonl

```text
You are now an excellent programmer. You are conducting a function vulnerability detection task for C/C++ language.

static char *time_value_string(char *buf, int buf_size, int64_t val, const AVRational *time_base)

{

    if (val == AV_NOPTS_VALUE) {

        snprintf(buf, buf_size, "N/A");

    } else {

        double d = val * av_q2d(*time_base);

        value_string(buf, buf_size, (struct unit_value){.val.d=d, .unit=unit_second_str});

    }



    return buf;

}

In the above code snippet, check for potential security vulnerabilities and answer with a single digit: 1 if Vulnerable, 0 if Non-vulnerable.

The node information of the code snippet is as follows:
Node 25769803776: (BLOCK) '{      if (val == AV_NOPTS_VALUE) {     ...'
Node 25769803777: (BLOCK) '{ snprintf(buf, buf_size, "N/A"); }'
Node 25769803778: (BLOCK) '{          double d = val * av_q2d(*time...'
Node 25769803779: (BLOCK) '<empty>'
Node 25769803780: (BLOCK) '<empty>'
Node 30064771072: (CALL) 'val == AV_NOPTS_VALUE'
Node 30064771073: (CALL) 'snprintf(buf, buf_size, "N/A")'
Node 30064771074: (CALL) 'd = val * av_q2d(*time_base)'
Node 30064771075: (CALL) 'val * av_q2d(*time_base)'
Node 30064771076: (CALL) 'av_q2d(*time_base)'
Node 30064771077: (CALL) '*time_base'
Node 30064771078: (CALL) 'value_string(buf, buf_size, (struct unit...'
Node 30064771079: (CALL) '(struct unit_value){.val.d=d, .unit=unit...'
Node 30064771080: (CALL) '{.val.d=d, .unit=unit_second_str}'
Node 30064771081: (CALL) '.val.d=d'
Node 30064771082: (CALL) '.val.d=d'
Node 30064771083: (CALL) '.unit=unit_second_str'
Node 47244640256: (CONTROL_STRUCTURE) 'if (val == AV_NOPTS_VALUE) {          sn...'
Node 68719476736: (IDENTIFIER) 'val'
Node 68719476737: (IDENTIFIER) '<unknown> AV_NOPTS_VALUE'
Node 68719476738: (IDENTIFIER) 'buf'
Node 68719476739: (IDENTIFIER) 'buf_size'
Node 68719476740: (IDENTIFIER) 'd'
Node 68719476741: (IDENTIFIER) 'val'
Node 68719476742: (IDENTIFIER) 'time_base'
Node 68719476743: (IDENTIFIER) 'buf'
Node 68719476744: (IDENTIFIER) 'buf_size'
Node 68719476745: (IDENTIFIER) 'val'
Node 68719476746: (IDENTIFIER) 'd'
Node 68719476747: (IDENTIFIER) 'd'
Node 68719476748: (IDENTIFIER) 'd'
Node 68719476749: (IDENTIFIER) 'unit'
Node 68719476750: (IDENTIFIER) '<unknown> unit_second_str'
Node 68719476751: (IDENTIFIER) 'buf'
Node 90194313216: (LITERAL) '"N/A"'
Node 94489280512: (LOCAL) 'double d'
Node 94489280513: (LOCAL) '<unknown> unit_second_str'
Node 94489280514: (LOCAL) 'unit'
Node 94489280515: (LOCAL) '<unknown> AV_NOPTS_VALUE'
Node 107374182400: (METHOD) 'static char *time_value_string(char *buf...'
The edge information of the code snippet is as follows:
Edge: Node 25769803776 -> AST -> Node 47244640256
Edge: Node 25769803776 -> AST -> Node 94489280513
Edge: Node 25769803776 -> AST -> Node 94489280514
Edge: Node 25769803776 -> AST -> Node 94489280515
Edge: Node 25769803777 -> AST -> Node 30064771073
Edge: Node 25769803778 -> AST -> Node 94489280512
Edge: Node 25769803778 -> AST -> Node 30064771074
Edge: Node 25769803778 -> AST -> Node 30064771078
Edge: Node 25769803779 -> AST -> Node 30064771081
Edge: Node 25769803779 -> AST -> Node 30064771082
Edge: Node 25769803779 -> CFG -> Node 68719476749
Edge: Node 25769803779 -> DOMINATE -> Node 68719476749
Edge: Node 25769803779 -> POST_DOMINATE -> Node 30064771082
Edge: Node 25769803779 -> REACHING_DEF -> Node 30064771080
Edge: Node 25769803779 -> REACHING_DEF -> Node 30064771080

The following is an example, and it is .


Answer (0 or 1):
```

## 22. devign/B1-shuf/44/devign:validation:10075

SHA-256: 56dc899d14a2c66e37bb5374aac01cf4ac01bbf4bc17a5b918bbcd8d7b8d3276

Nguồn: Runs-management/dry_run_validation_20261102/devign/validation/B1-shuf/44/prompts.jsonl

```text
You are now an excellent programmer. You are conducting a function vulnerability detection task for C/C++ language.

static av_cold int common_init(AVCodecContext *avctx){

    FFV1Context *s = avctx->priv_data;



    s->avctx= avctx;

    s->flags= avctx->flags;



    avcodec_get_frame_defaults(&s->picture);



    ff_dsputil_init(&s->dsp, avctx);



    s->width = avctx->width;

    s->height= avctx->height;



    assert(s->width && s->height);

    //defaults

    s->num_h_slices=1;

    s->num_v_slices=1;





    return 0;

}

In the above code snippet, check for potential security vulnerabilities and answer with a single digit: 1 if Vulnerable, 0 if Non-vulnerable.

The node information of the code snippet is as follows:
Node 25769803814: (BLOCK) '{      int i;      AVFormatContext *ic; ...'
Node 25769803815: (BLOCK) '<empty>'
Node 25769803816: (BLOCK) '{          AVStream *st;          st = a...'
Node 30064771357: (CALL) 'ic = av_open_input_file(filename, FFM_PA...'
Node 30064771358: (CALL) 'av_open_input_file(filename, FFM_PACKET_...'
Node 30064771359: (CALL) '!ic'
Node 30064771360: (CALL) '-EIO'
Node 30064771361: (CALL) 's->nb_streams = ic->nb_streams'
Node 30064771362: (CALL) 's->nb_streams'
Node 30064771363: (CALL) 'ic->nb_streams'
Node 30064771364: (CALL) 'i=0'
Node 30064771365: (CALL) 'i<ic->nb_streams'
Node 30064771366: (CALL) 'ic->nb_streams'
Node 30064771367: (CALL) 'i++'
Node 30064771368: (CALL) 'st = av_mallocz(sizeof(AVFormatContext))'
Node 30064771369: (CALL) 'av_mallocz(sizeof(AVFormatContext))'
Node 30064771370: (CALL) 'sizeof(AVFormatContext)'
Node 30064771371: (CALL) 'memcpy(st, ic->streams[i], sizeof(AVStre...'
Node 30064771372: (CALL) 'ic->streams[i]'
Node 30064771373: (CALL) 'ic->streams'
Node 30064771374: (CALL) 'sizeof(AVStream)'
Node 30064771375: (CALL) 's->streams[i] = st'
Node 30064771376: (CALL) 's->streams[i]'
Node 30064771377: (CALL) 's->streams'
Node 30064771378: (CALL) 'av_close_input_file(ic)'
Node 47244640291: (CONTROL_STRUCTURE) 'if (!ic) return -EIO;'
Node 47244640292: (CONTROL_STRUCTURE) 'for (i=0;i<ic->nb_streams;i++)'
Node 55834574881: (FIELD_IDENTIFIER) 'nb_streams'
Node 55834574882: (FIELD_IDENTIFIER) 'nb_streams'
Node 55834574883: (FIELD_IDENTIFIER) 'nb_streams'
Node 55834574884: (FIELD_IDENTIFIER) 'streams'
Node 55834574885: (FIELD_IDENTIFIER) 'streams'
Node 68719477115: (IDENTIFIER) 'ic'
Node 68719477116: (IDENTIFIER) 'filename'
Node 68719477117: (IDENTIFIER) '<unknown> FFM_PACKET_SIZE'
Node 68719477118: (IDENTIFIER) 'ic'
Node 68719477119: (IDENTIFIER) '<unknown> EIO'
Node 68719477120: (IDENTIFIER) 's'
Node 68719477121: (IDENTIFIER) 'ic'
Node 68719477122: (IDENTIFIER) 'i'
The edge information of the code snippet is as follows:
Edge: Node 25769803814 -> AST -> Node 30064771357
Edge: Node 25769803814 -> AST -> Node 47244640291
Edge: Node 25769803814 -> AST -> Node 30064771361
Edge: Node 25769803814 -> AST -> Node 47244640292
Edge: Node 25769803814 -> AST -> Node 30064771378
Edge: Node 25769803816 -> AST -> Node 30064771368
Edge: Node 25769803816 -> AST -> Node 30064771371
Edge: Node 25769803816 -> AST -> Node 30064771375
Edge: Node 30064771357 -> ARGUMENT -> Node 68719477115
Edge: Node 30064771357 -> ARGUMENT -> Node 30064771358
Edge: Node 30064771357 -> AST -> Node 68719477115
Edge: Node 30064771357 -> AST -> Node 30064771358
Edge: Node 30064771357 -> CFG -> Node 68719477118
Edge: Node 30064771357 -> DOMINATE -> Node 68719477118
Edge: Node 30064771357 -> POST_DOMINATE -> Node 30064771358

The following is an example, and it is .


Answer (0 or 1):
```

## 23. devign/B2-nolabel/42/devign:validation:19520

SHA-256: 2357443376fa4ed61cc1408bd1a23151454d5bc53e16c73e8050465ce2a0f2a2

Nguồn: Runs-management/dry_run_validation_20261102/devign/validation/B2-nolabel/42/prompts.jsonl

```text
You are now an excellent programmer. You are conducting a function vulnerability detection task for C/C++ language.

void qdev_prop_set_defaults(DeviceState *dev, Property *props)

{

    if (!props)

        return;

    while (props->name) {

        if (props->defval) {

            qdev_prop_cpy(dev, props, props->defval);

        }

        props++;

    }

}

In the above code snippet, check for potential security vulnerabilities and answer with a single digit: 1 if Vulnerable, 0 if Non-vulnerable.

The node information of the code snippet is as follows:
Node 25769803776: (BLOCK) '{      if (!props)          return;     ...'
Node 25769803777: (BLOCK) '<empty>'
Node 25769803778: (BLOCK) '{          if (props->defval) {         ...'
Node 25769803779: (BLOCK) '{ qdev_prop_cpy(dev, props, props->defva...'
Node 30064771072: (CALL) '!props'
Node 30064771073: (CALL) 'props->name'
Node 30064771074: (CALL) 'props->defval'
Node 30064771075: (CALL) 'qdev_prop_cpy(dev, props, props->defval)'
Node 30064771076: (CALL) 'props->defval'
Node 30064771077: (CALL) 'props++'
Node 47244640256: (CONTROL_STRUCTURE) 'if (!props) return;'
Node 47244640257: (CONTROL_STRUCTURE) 'while (props->name)'
Node 47244640258: (CONTROL_STRUCTURE) 'if (props->defval) { qdev_prop_cpy(dev, ...'
Node 55834574848: (FIELD_IDENTIFIER) 'name'
Node 55834574849: (FIELD_IDENTIFIER) 'defval'
Node 55834574850: (FIELD_IDENTIFIER) 'defval'
Node 68719476736: (IDENTIFIER) 'props'
Node 68719476737: (IDENTIFIER) 'props'
Node 68719476738: (IDENTIFIER) 'props'
Node 68719476739: (IDENTIFIER) 'dev'
Node 68719476740: (IDENTIFIER) 'props'
Node 68719476741: (IDENTIFIER) 'props'
Node 68719476742: (IDENTIFIER) 'props'
Node 107374182400: (METHOD) 'void qdev_prop_set_defaults(DeviceState ...'
Node 111669149696: (METHOD_PARAMETER_IN) 'DeviceState *dev'
Node 111669149697: (METHOD_PARAMETER_IN) 'Property *props'
Node 115964116992: (METHOD_PARAMETER_OUT) 'DeviceState *dev'
Node 115964116993: (METHOD_PARAMETER_OUT) 'Property *props'
Node 124554051584: (METHOD_RETURN) 'RET'
Node 141733920768: (RETURN) 'return;'
The edge information of the code snippet is as follows:
Edge: Node 25769803776 -> AST -> Node 47244640256
Edge: Node 25769803776 -> AST -> Node 47244640257
Edge: Node 25769803777 -> AST -> Node 141733920768
Edge: Node 25769803778 -> AST -> Node 47244640258
Edge: Node 25769803778 -> AST -> Node 30064771077
Edge: Node 25769803779 -> AST -> Node 30064771075
Edge: Node 30064771072 -> ARGUMENT -> Node 68719476736
Edge: Node 30064771072 -> AST -> Node 68719476736
Edge: Node 30064771072 -> CDG -> Node 141733920768
Edge: Node 30064771072 -> CDG -> Node 30064771073
Edge: Node 30064771072 -> CDG -> Node 55834574848
Edge: Node 30064771072 -> CDG -> Node 68719476737
Edge: Node 30064771072 -> CFG -> Node 141733920768
Edge: Node 30064771072 -> CFG -> Node 68719476737
Edge: Node 30064771072 -> DOMINATE -> Node 124554051584
Edge: Node 30064771072 -> DOMINATE -> Node 141733920768
Edge: Node 30064771072 -> DOMINATE -> Node 68719476737
Edge: Node 30064771072 -> POST_DOMINATE -> Node 68719476736
Edge: Node 30064771072 -> REACHING_DEF -> Node 124554051584
Edge: Node 30064771073 -> ARGUMENT -> Node 68719476737
Edge: Node 30064771073 -> ARGUMENT -> Node 55834574848
Edge: Node 30064771073 -> AST -> Node 68719476737

The following is a related example.
static void qdev_prop_cpy(DeviceState *dev, Property *props, void *src)

{

    if (props->info->type == PROP_TYPE_BIT) {

        bool *defval = src;

        bit_prop_set(dev, props, *defval);

    } else {

        char *dst = qdev_get_prop_ptr(dev, props);

        memcpy(dst, src, props->info->size);

    }

}

Answer (0 or 1):
```

## 24. devign/B2-nolabel/42/devign:validation:8374

SHA-256: bb36c56cf11bb2c70d6db69e0f24c58bea2a795d6bcdde9e337472c00960878e

Nguồn: Runs-management/dry_run_validation_20261102/devign/validation/B2-nolabel/42/prompts.jsonl

```text
You are now an excellent programmer. You are conducting a function vulnerability detection task for C/C++ language.

static void rng_egd_finalize(Object *obj)

{

    RngEgd *s = RNG_EGD(obj);



    if (s->chr) {

        qemu_chr_add_handlers(s->chr, NULL, NULL, NULL, NULL);

        qemu_chr_fe_release(s->chr);

    }



    g_free(s->chr_name);



    rng_egd_free_requests(s);

}

In the above code snippet, check for potential security vulnerabilities and answer with a single digit: 1 if Vulnerable, 0 if Non-vulnerable.

The node information of the code snippet is as follows:
Node 25769803776: (BLOCK) '{      RngEgd *s = RNG_EGD(obj);        ...'
Node 25769803777: (BLOCK) '{          qemu_chr_add_handlers(s->chr,...'
Node 30064771072: (CALL) 's = RNG_EGD(obj)'
Node 30064771073: (CALL) 'RNG_EGD(obj)'
Node 30064771074: (CALL) 's->chr'
Node 30064771075: (CALL) 'qemu_chr_add_handlers(s->chr, NULL, NULL...'
Node 30064771076: (CALL) 's->chr'
Node 30064771077: (CALL) 'qemu_chr_fe_release(s->chr)'
Node 30064771078: (CALL) 's->chr'
Node 30064771079: (CALL) 'g_free(s->chr_name)'
Node 30064771080: (CALL) 's->chr_name'
Node 30064771081: (CALL) 'rng_egd_free_requests(s)'
Node 47244640256: (CONTROL_STRUCTURE) 'if (s->chr) {          qemu_chr_add_hand...'
Node 55834574848: (FIELD_IDENTIFIER) 'chr'
Node 55834574849: (FIELD_IDENTIFIER) 'chr'
Node 55834574850: (FIELD_IDENTIFIER) 'chr'
Node 55834574851: (FIELD_IDENTIFIER) 'chr_name'
Node 68719476736: (IDENTIFIER) 's'
Node 68719476737: (IDENTIFIER) 'obj'
Node 68719476738: (IDENTIFIER) 's'
Node 68719476739: (IDENTIFIER) 's'
Node 68719476740: (IDENTIFIER) '<unknown> NULL'
Node 68719476741: (IDENTIFIER) '<unknown> NULL'
Node 68719476742: (IDENTIFIER) '<unknown> NULL'
Node 68719476743: (IDENTIFIER) '<unknown> NULL'
Node 68719476744: (IDENTIFIER) 's'
Node 68719476745: (IDENTIFIER) 's'
Node 68719476746: (IDENTIFIER) 's'
Node 94489280512: (LOCAL) 'RngEgd *s'
Node 94489280513: (LOCAL) '<unknown> NULL'
Node 107374182400: (METHOD) 'static void rng_egd_finalize(Object *obj...'
Node 111669149696: (METHOD_PARAMETER_IN) 'Object *obj'
Node 115964116992: (METHOD_PARAMETER_OUT) 'Object *obj'
Node 124554051584: (METHOD_RETURN) 'RET'
Node 128849018880: (MODIFIER) '<empty>'
The edge information of the code snippet is as follows:
Edge: Node 25769803776 -> AST -> Node 94489280512
Edge: Node 25769803776 -> AST -> Node 30064771072
Edge: Node 25769803776 -> AST -> Node 47244640256
Edge: Node 25769803776 -> AST -> Node 30064771079
Edge: Node 25769803776 -> AST -> Node 30064771081
Edge: Node 25769803776 -> AST -> Node 94489280513
Edge: Node 25769803777 -> AST -> Node 30064771075
Edge: Node 25769803777 -> AST -> Node 30064771077
Edge: Node 30064771072 -> ARGUMENT -> Node 68719476736
Edge: Node 30064771072 -> ARGUMENT -> Node 30064771073
Edge: Node 30064771072 -> AST -> Node 68719476736
Edge: Node 30064771072 -> AST -> Node 30064771073
Edge: Node 30064771072 -> CFG -> Node 68719476738
Edge: Node 30064771072 -> DOMINATE -> Node 68719476738
Edge: Node 30064771072 -> POST_DOMINATE -> Node 30064771073
Edge: Node 30064771072 -> REACHING_DEF -> Node 124554051584
Edge: Node 30064771073 -> ARGUMENT -> Node 68719476737
Edge: Node 30064771073 -> AST -> Node 68719476737
Edge: Node 30064771073 -> CFG -> Node 30064771072

The following is a related example.
static void rng_egd_finalize(Object *obj)

{

    RngEgd *s = RNG_EGD(obj);



    if (s->chr) {

        qemu_chr_add_handlers(s->chr, NULL, NULL, NULL, NULL);


    }



    g_free(s->chr_name);



    rng_egd_free_requests(s);

}

Answer (0 or 1):
```

## 25. devign/B1-shuf/42/devign:validation:21148

SHA-256: 9ebe1f3806b7a8435e0ebe5340eb83f60937518d3e9dcd8445cf712e8e407b2b

Nguồn: Runs-management/dry_run_validation_20261102/devign/validation/B1-shuf/42/prompts.jsonl

```text
You are now an excellent programmer. You are conducting a function vulnerability detection task for C/C++ language.

static inline void RENAME(yuv2yuv1_ar)(SwsContext *c, const int16_t *lumSrc,

                                       const int16_t *chrUSrc, const int16_t *chrVSrc,

                                       const int16_t *alpSrc,

                                       uint8_t *dest, uint8_t *uDest, uint8_t *vDest,

                                       uint8_t *aDest, int dstW, int chrDstW)

{

    int p= 4;

    const uint8_t *src[4]= { alpSrc + dstW, lumSrc + dstW, chrUSrc + chrDstW, chrVSrc + chrDstW };

    uint8_t *dst[4]= { aDest, dest, uDest, vDest };

    x86_reg counter[4]= { dstW, dstW, chrDstW, chrDstW };



    while (p--) {

        if (dst[p]) {

            __asm__ volatile(

                "mov %2, %%"REG_a"                    \n\t"

                "pcmpeqw %%mm7, %%mm7                 \n\t"

                "psrlw                 $15, %%mm7     \n\t"

                "psllw                  $6, %%mm7     \n\t"

                ".p2align                4            \n\t" /* FIXME Unroll? */

                "1:                                   \n\t"

                "movq  (%0, %%"REG_a", 2), %%mm0      \n\t"

                "movq 8(%0, %%"REG_a", 2), %%mm1      \n\t"

                "paddsw             %%mm7, %%mm0      \n\t"

                "paddsw             %%mm7, %%mm1      \n\t"

                "psraw                 $7, %%mm0      \n\t"

                "psraw                 $7, %%mm1      \n\t"

                "packuswb           %%mm1, %%mm0      \n\t"

                MOVNTQ(%%mm0, (%1, %%REGa))

                "add                   $8, %%"REG_a"  \n\t"

                "jnc                   1b             \n\t"

                :: "r" (src[p]), "r" (dst[p] + counter[p]),

                   "g" (-counter[p])

                : "%"REG_a

            );

        }

    }

}

In the above code snippet, check for potential security vulnerabilities and answer with a single digit: 1 if Vulnerable, 0 if Non-vulnerable.

The node information of the code snippet is as follows:
Node 25769803776: (BLOCK) '{  #if CONFIG_NETWORK      int ret;     ...'
Node 90194313216: (LITERAL) '0'
Node 107374182400: (METHOD) 'int avformat_network_init(void)  {  #if ...'
Node 111669149696: (METHOD_PARAMETER_IN) 'void'
Node 115964116992: (METHOD_PARAMETER_OUT) 'void'
Node 124554051584: (METHOD_RETURN) 'RET'
Node 141733920768: (RETURN) 'return 0;'
The edge information of the code snippet is as follows:
Edge: Node 25769803776 -> AST -> Node 141733920768
Edge: Node 90194313216 -> CFG -> Node 141733920768
Edge: Node 90194313216 -> DOMINATE -> Node 141733920768
Edge: Node 90194313216 -> POST_DOMINATE -> Node 107374182400
Edge: Node 90194313216 -> REACHING_DEF -> Node 141733920768
Edge: Node 107374182400 -> AST -> Node 111669149696
Edge: Node 107374182400 -> AST -> Node 25769803776
Edge: Node 107374182400 -> AST -> Node 124554051584
Edge: Node 107374182400 -> AST -> Node 115964116992
Edge: Node 107374182400 -> CFG -> Node 90194313216
Edge: Node 107374182400 -> CONTAINS -> Node 25769803776
Edge: Node 107374182400 -> CONTAINS -> Node 141733920768
Edge: Node 107374182400 -> CONTAINS -> Node 90194313216
Edge: Node 107374182400 -> DOMINATE -> Node 90194313216
Edge: Node 107374182400 -> REACHING_DEF -> Node 111669149696
Edge: Node 107374182400 -> REACHING_DEF -> Node 90194313216
Edge: Node 107374182400 -> REACHING_DEF -> Node 141733920768
Edge: Node 111669149696 -> PARAMETER_LINK -> Node 115964116992
Edge: Node 111669149696 -> REACHING_DEF -> Node 115964116992
Edge: Node 111669149696 -> REACHING_DEF -> Node 115964116992
Edge: Node 111669149696 -> REACHING_DEF -> Node 124554051584
Edge: Node 124554051584 -> POST_DOMINATE -> Node 141733920768
Edge: Node 141733920768 -> ARGUMENT -> Node 90194313216
Edge: Node 141733920768 -> AST -> Node 90194313216
Edge: Node 141733920768 -> CFG -> Node 124554051584
Edge: Node 141733920768 -> DOMINATE -> Node 124554051584
Edge: Node 141733920768 -> POST_DOMINATE -> Node 90194313216
Edge: Node 141733920768 -> REACHING_DEF -> Node 124554051584

The following is an example, and it is .


Answer (0 or 1):
```

## 26. devign/B2-rand/44/devign:validation:18828

SHA-256: a1f04130ceac9f4a76bc3c233bdf9384bfb0c6871657d909b24bf8b56c279ddc

Nguồn: Runs-management/dry_run_validation_20261102/devign/validation/B2-rand/44/prompts.jsonl

```text
You are now an excellent programmer. You are conducting a function vulnerability detection task for C/C++ language.

static void FUNCC(pred4x4_dc)(uint8_t *_src, const uint8_t *topright, int _stride){

    pixel *src = (pixel*)_src;

    int stride = _stride/sizeof(pixel);

    const int dc= (  src[-stride] + src[1-stride] + src[2-stride] + src[3-stride]

                   + src[-1+0*stride] + src[-1+1*stride] + src[-1+2*stride] + src[-1+3*stride] + 4) >>3;



    ((pixel4*)(src+0*stride))[0]=

    ((pixel4*)(src+1*stride))[0]=

    ((pixel4*)(src+2*stride))[0]=

    ((pixel4*)(src+3*stride))[0]= PIXEL_SPLAT_X4(dc);

}

In the above code snippet, check for potential security vulnerabilities and answer with a single digit: 1 if Vulnerable, 0 if Non-vulnerable.

The node information of the code snippet is as follows:
Node 25769803778: (BLOCK) '<empty>'
Node 107374182402: (METHOD) 'static void FUNCC(pred4x4_dc)'
Node 111669149696: (METHOD_PARAMETER_IN) 'pred4x4_dc'
Node 115964116992: (METHOD_PARAMETER_OUT) 'pred4x4_dc'
Node 124554051586: (METHOD_RETURN) 'RET'
Node 128849018880: (MODIFIER) '<empty>'
The edge information of the code snippet is as follows:
Edge: Node 107374182402 -> AST -> Node 111669149696
Edge: Node 107374182402 -> AST -> Node 25769803778
Edge: Node 107374182402 -> AST -> Node 128849018880
Edge: Node 107374182402 -> AST -> Node 124554051586
Edge: Node 107374182402 -> AST -> Node 115964116992
Edge: Node 107374182402 -> CFG -> Node 124554051586
Edge: Node 107374182402 -> CONTAINS -> Node 25769803778
Edge: Node 107374182402 -> DOMINATE -> Node 124554051586
Edge: Node 107374182402 -> REACHING_DEF -> Node 111669149696
Edge: Node 111669149696 -> PARAMETER_LINK -> Node 115964116992
Edge: Node 111669149696 -> REACHING_DEF -> Node 115964116992
Edge: Node 111669149696 -> REACHING_DEF -> Node 124554051586
Edge: Node 124554051586 -> POST_DOMINATE -> Node 107374182402

The following is an example, and it is Non-vulnerable.
static inline void tcg_out_tlb_load(TCGContext *s, TCGReg addrlo, TCGReg addrhi,

                                    int mem_index, TCGMemOp opc,

                                    tcg_insn_unit **label_ptr, int which)

{

    const TCGReg r0 = TCG_REG_L0;

    const TCGReg r1 = TCG_REG_L1;

    TCGType ttype = TCG_TYPE_I32;

    TCGType tlbtype = TCG_TYPE_I32;

    int trexw = 0, hrexw = 0, tlbrexw = 0;

    int s_mask = (1 << (opc & MO_SIZE)) - 1;

    bool aligned = (opc & MO_AMASK) == MO_ALIGN || s_mask == 0;



    if (TCG_TARGET_REG_BITS == 64) {

        if (TARGET_LONG_BITS == 64) {

            ttype = TCG_TYPE_I64;

            trexw = P_REXW;

        }

        if (TCG_TYPE_PTR == TCG_TYPE_I64) {

            hrexw = P_REXW;

            if (TARGET_PAGE_BITS + CPU_TLB_BITS > 32) {

                tlbtype = TCG_TYPE_I64;

                tlbrexw = P_REXW;

            }

        }

    }



    tcg_out_mov(s, tlbtype, r0, addrlo);

    if (aligned) {

        tcg_out_mov(s, ttype, r1, addrlo);

    } else {

        /* For unaligned access check that we don't cross pages using

           the page address of the last byte.  */

        tcg_out_modrm_offset(s, OPC_LEA + trexw, r1, addrlo, s_mask);

    }



    tcg_out_shifti(s, SHIFT_SHR + tlbrexw, r0,

                   TARGET_PAGE_BITS - CPU_TLB_ENTRY_BITS);



    tgen_arithi(s, ARITH_AND + trexw, r1,

                TARGET_PAGE_MASK | (aligned ? s_mask : 0), 0);

    tgen_arithi(s, ARITH_AND + tlbrexw, r0,

                (CPU_TLB_SIZE - 1) << CPU_TLB_ENTRY_BITS, 0);



    tcg_out_modrm_sib_offset(s, OPC_LEA + hrexw, r0, TCG_AREG0, r0, 0,

                             offsetof(CPUArchState, tlb_table[mem_index][0])

                             + which);



    /* cmp 0(r0), r1 */

    tcg_out_modrm_offset(s, OPC_CMP_GvEv + trexw, r1, r0, 0);



    /* Prepare for both the fast path add of the tlb addend, and the slow

       path function argument setup.  There are two cases worth note:

       For 32-bit guest and x86_64 host, MOVL zero-extends the guest address

       before the fastpath ADDQ below.  For 64-bit guest and x32 host, MOVQ

       copies the entire guest address for the slow path, while truncation

       for the 32-bit host happens with the fastpath ADDL below.  */

    tcg_out_mov(s, ttype, r1, addrlo);



    /* jne slow_path */

    tcg_out_opc(s, OPC_JCC_long + JCC_JNE, 0, 0, 0);

    label_ptr[0] = s->code_ptr;

    s->code_ptr += 4;



    if (TARGET_LONG_BITS > TCG_TARGET_REG_BITS) {

        /* cmp 4(r0), addrhi */

        tcg_out_modrm_offset(s, OPC_CMP_GvEv, addrhi, r0, 4);



        /* jne slow_path */

        tcg_out_opc(s, OPC_JCC_long + JCC_JNE, 0, 0, 0);

        label_ptr[1] = s->code_ptr;

        s->code_ptr += 4;

    }



    /* TLB Hit.  */



    /* add addend(r0), r1 */

    tcg_out_modrm_offset(s, OPC_ADD_GvEv + hrexw, r1, r0,

                         offsetof(CPUTLBEntry, addend) - which);

}

Answer (0 or 1):
```

## 27. devign/B1-full/42/devign:validation:772

SHA-256: 15e261f0f06d3a71dc3bf18184b5653ed52522492735248798e7499b073ee5fe

Nguồn: Runs-management/dry_run_validation_20261102/devign/validation/B1-full/42/prompts.jsonl

```text
You are now an excellent programmer. You are conducting a function vulnerability detection task for C/C++ language.

static inline void RENAME(bgr24ToY)(uint8_t *dst, uint8_t *src, long width)

{

#ifdef HAVE_MMX

	asm volatile(

		"mov %2, %%"REG_a"		\n\t"

		"movq "MANGLE(bgr2YCoeff)", %%mm6		\n\t"

		"movq "MANGLE(w1111)", %%mm5		\n\t"

		"pxor %%mm7, %%mm7		\n\t"

		"lea (%%"REG_a", %%"REG_a", 2), %%"REG_d"\n\t"

		ASMALIGN(4)

		"1:				\n\t"

		PREFETCH" 64(%0, %%"REG_d")	\n\t"

		"movd (%0, %%"REG_d"), %%mm0	\n\t"

		"movd 3(%0, %%"REG_d"), %%mm1	\n\t"

		"punpcklbw %%mm7, %%mm0		\n\t"

		"punpcklbw %%mm7, %%mm1		\n\t"

		"movd 6(%0, %%"REG_d"), %%mm2	\n\t"

		"movd 9(%0, %%"REG_d"), %%mm3	\n\t"

		"punpcklbw %%mm7, %%mm2		\n\t"

		"punpcklbw %%mm7, %%mm3		\n\t"

		"pmaddwd %%mm6, %%mm0		\n\t"

		"pmaddwd %%mm6, %%mm1		\n\t"

		"pmaddwd %%mm6, %%mm2		\n\t"

		"pmaddwd %%mm6, %%mm3		\n\t"

#ifndef FAST_BGR2YV12

		"psrad $8, %%mm0		\n\t"

		"psrad $8, %%mm1		\n\t"

		"psrad $8, %%mm2		\n\t"

		"psrad $8, %%mm3		\n\t"

#endif

		"packssdw %%mm1, %%mm0		\n\t"

		"packssdw %%mm3, %%mm2		\n\t"

		"pmaddwd %%mm5, %%mm0		\n\t"

		"pmaddwd %%mm5, %%mm2		\n\t"

		"packssdw %%mm2, %%mm0		\n\t"

		"psraw $7, %%mm0		\n\t"



		"movd 12(%0, %%"REG_d"), %%mm4	\n\t"

		"movd 15(%0, %%"REG_d"), %%mm1	\n\t"

		"punpcklbw %%mm7, %%mm4		\n\t"

		"punpcklbw %%mm7, %%mm1		\n\t"

		"movd 18(%0, %%"REG_d"), %%mm2	\n\t"

		"movd 21(%0, %%"REG_d"), %%mm3	\n\t"

		"punpcklbw %%mm7, %%mm2		\n\t"

		"punpcklbw %%mm7, %%mm3		\n\t"

		"pmaddwd %%mm6, %%mm4		\n\t"

		"pmaddwd %%mm6, %%mm1		\n\t"

		"pmaddwd %%mm6, %%mm2		\n\t"

		"pmaddwd %%mm6, %%mm3		\n\t"

#ifndef FAST_BGR2YV12

		"psrad $8, %%mm4		\n\t"

		"psrad $8, %%mm1		\n\t"

		"psrad $8, %%mm2		\n\t"

		"psrad $8, %%mm3		\n\t"

#endif

		"packssdw %%mm1, %%mm4		\n\t"

		"packssdw %%mm3, %%mm2		\n\t"

		"pmaddwd %%mm5, %%mm4		\n\t"

		"pmaddwd %%mm5, %%mm2		\n\t"

		"add $24, %%"REG_d"		\n\t"

		"packssdw %%mm2, %%mm4		\n\t"

		"psraw $7, %%mm4		\n\t"



		"packuswb %%mm4, %%mm0		\n\t"

		"paddusb "MANGLE(bgr2YOffset)", %%mm0	\n\t"



		"movq %%mm0, (%1, %%"REG_a")	\n\t"

		"add $8, %%"REG_a"		\n\t"

		" js 1b				\n\t"

		: : "r" (src+width*3), "r" (dst+width), "g" (-width)

		: "%"REG_a, "%"REG_d

	);

#else

	int i;

	for(i=0; i<width; i++)

	{

		int b= src[i*3+0];

		int g= src[i*3+1];

		int r= src[i*3+2];



		dst[i]= ((RY*r + GY*g + BY*b + (33<<(RGB2YUV_SHIFT-1)) )>>RGB2YUV_SHIFT);

	}

#endif

}

In the above code snippet, check for potential security vulnerabilities and answer with a single digit: 1 if Vulnerable, 0 if Non-vulnerable.

The node information of the code snippet is as follows:
Node 25769803778: (BLOCK) '<empty>'
Node 107374182402: (METHOD) 'static inline void RENAME(bgr24ToY)'
Node 111669149696: (METHOD_PARAMETER_IN) 'bgr24ToY'
Node 115964116992: (METHOD_PARAMETER_OUT) 'bgr24ToY'
Node 124554051586: (METHOD_RETURN) 'RET'
Node 128849018880: (MODIFIER) '<empty>'
The edge information of the code snippet is as follows:
Edge: Node 107374182402 -> AST -> Node 111669149696
Edge: Node 107374182402 -> AST -> Node 25769803778
Edge: Node 107374182402 -> AST -> Node 128849018880
Edge: Node 107374182402 -> AST -> Node 124554051586
Edge: Node 107374182402 -> AST -> Node 115964116992
Edge: Node 107374182402 -> CFG -> Node 124554051586
Edge: Node 107374182402 -> CONTAINS -> Node 25769803778
Edge: Node 107374182402 -> DOMINATE -> Node 124554051586
Edge: Node 107374182402 -> REACHING_DEF -> Node 111669149696
Edge: Node 111669149696 -> PARAMETER_LINK -> Node 115964116992
Edge: Node 111669149696 -> REACHING_DEF -> Node 115964116992
Edge: Node 111669149696 -> REACHING_DEF -> Node 124554051586
Edge: Node 124554051586 -> POST_DOMINATE -> Node 107374182402

The following is an example, and it is .


Answer (0 or 1):
```

## 28. devign/B0/42/devign:validation:25184

SHA-256: 45e2eb9b6a7481a571769cc8a3c641e48524d68ce518a8e31abb1a38bee30eb0

Nguồn: Runs-management/dry_run_validation_20261102/devign/validation/B0/42/prompts.jsonl

```text
You are now an excellent programmer. You are conducting a function vulnerability detection task for C/C++ language.

static inline void RENAME(yuvPlanartoyuy2)(const uint8_t *ysrc, const uint8_t *usrc, const uint8_t *vsrc, uint8_t *dst,

	unsigned int width, unsigned int height,

	int lumStride, int chromStride, int dstStride, int vertLumPerChroma)

{

	unsigned y;

	const unsigned chromWidth= width>>1;

	for(y=0; y<height; y++)

	{

#ifdef HAVE_MMX

//FIXME handle 2 lines a once (fewer prefetch, reuse some chrom, but very likely limited by mem anyway)

		asm volatile(

			"xor %%"REG_a", %%"REG_a"	\n\t"

			".balign 16			\n\t"

			"1:				\n\t"

			PREFETCH" 32(%1, %%"REG_a", 2)	\n\t"

			PREFETCH" 32(%2, %%"REG_a")	\n\t"

			PREFETCH" 32(%3, %%"REG_a")	\n\t"

			"movq (%2, %%"REG_a"), %%mm0	\n\t" // U(0)

			"movq %%mm0, %%mm2		\n\t" // U(0)

			"movq (%3, %%"REG_a"), %%mm1	\n\t" // V(0)

			"punpcklbw %%mm1, %%mm0		\n\t" // UVUV UVUV(0)

			"punpckhbw %%mm1, %%mm2		\n\t" // UVUV UVUV(8)



			"movq (%1, %%"REG_a",2), %%mm3	\n\t" // Y(0)

			"movq 8(%1, %%"REG_a",2), %%mm5	\n\t" // Y(8)

			"movq %%mm3, %%mm4		\n\t" // Y(0)

			"movq %%mm5, %%mm6		\n\t" // Y(8)

			"punpcklbw %%mm0, %%mm3		\n\t" // YUYV YUYV(0)

			"punpckhbw %%mm0, %%mm4		\n\t" // YUYV YUYV(4)

			"punpcklbw %%mm2, %%mm5		\n\t" // YUYV YUYV(8)

			"punpckhbw %%mm2, %%mm6		\n\t" // YUYV YUYV(12)



			MOVNTQ" %%mm3, (%0, %%"REG_a", 4)\n\t"

			MOVNTQ" %%mm4, 8(%0, %%"REG_a", 4)\n\t"

			MOVNTQ" %%mm5, 16(%0, %%"REG_a", 4)\n\t"

			MOVNTQ" %%mm6, 24(%0, %%"REG_a", 4)\n\t"



			"add $8, %%"REG_a"		\n\t"

			"cmp %4, %%"REG_a"		\n\t"

			" jb 1b				\n\t"

			::"r"(dst), "r"(ysrc), "r"(usrc), "r"(vsrc), "g" ((long)chromWidth)

			: "%"REG_a

		);

#else



#if defined ARCH_ALPHA && defined HAVE_MVI

#define pl2yuy2(n)					\

	y1 = yc[n];					\

	y2 = yc2[n];					\

	u = uc[n];					\

	v = vc[n];					\

	asm("unpkbw %1, %0" : "=r"(y1) : "r"(y1));	\

	asm("unpkbw %1, %0" : "=r"(y2) : "r"(y2));	\

	asm("unpkbl %1, %0" : "=r"(u) : "r"(u));	\

	asm("unpkbl %1, %0" : "=r"(v) : "r"(v));	\

	yuv1 = (u << 8) + (v << 24);			\

	yuv2 = yuv1 + y2;				\

	yuv1 += y1;					\

	qdst[n] = yuv1;					\

	qdst2[n] = yuv2;



		int i;

		uint64_t *qdst = (uint64_t *) dst;

		uint64_t *qdst2 = (uint64_t *) (dst + dstStride);

		const uint32_t *yc = (uint32_t *) ysrc;

		const uint32_t *yc2 = (uint32_t *) (ysrc + lumStride);

		const uint16_t *uc = (uint16_t*) usrc, *vc = (uint16_t*) vsrc;

		for(i = 0; i < chromWidth; i += 8){

			uint64_t y1, y2, yuv1, yuv2;

			uint64_t u, v;

			/* Prefetch */

			asm("ldq $31,64(%0)" :: "r"(yc));

			asm("ldq $31,64(%0)" :: "r"(yc2));

			asm("ldq $31,64(%0)" :: "r"(uc));

			asm("ldq $31,64(%0)" :: "r"(vc));



			pl2yuy2(0);

			pl2yuy2(1);

			pl2yuy2(2);

			pl2yuy2(3);



			yc += 4;

			yc2 += 4;

			uc += 4;

			vc += 4;

			qdst += 4;

			qdst2 += 4;

		}

		y++;

		ysrc += lumStride;

		dst += dstStride;



#elif __WORDSIZE >= 64

		int i;

		uint64_t *ldst = (uint64_t *) dst;

		const uint8_t *yc = ysrc, *uc = usrc, *vc = vsrc;

		for(i = 0; i < chromWidth; i += 2){

			uint64_t k, l;

			k = yc[0] + (uc[0] << 8) +

			    (yc[1] << 16) + (vc[0] << 24);

			l = yc[2] + (uc[1] << 8) +

			    (yc[3] << 16) + (vc[1] << 24);

			*ldst++ = k + (l << 32);

			yc += 4;

			uc += 2;

			vc += 2;

		}



#else

		int i, *idst = (int32_t *) dst;

		const uint8_t *yc = ysrc, *uc = usrc, *vc = vsrc;

		for(i = 0; i < chromWidth; i++){

#ifdef WORDS_BIGENDIAN

			*idst++ = (yc[0] << 24)+ (uc[0] << 16) +

			    (yc[1] << 8) + (vc[0] << 0);

#else

			*idst++ = yc[0] + (uc[0] << 8) +

			    (yc[1] << 16) + (vc[0] << 24);

#endif

			yc += 2;

			uc++;

			vc++;

		}

#endif

#endif

		if((y&(vertLumPerChroma-1))==(vertLumPerChroma-1) )

		{

			usrc += chromStride;

			vsrc += chromStride;

		}

		ysrc += lumStride;

		dst += dstStride;

	}

#ifdef HAVE_MMX

asm(    EMMS" \n\t"

        SFENCE" \n\t"

        :::"memory");

#endif

}

In the above code snippet, check for potential security vulnerabilities and answer with a single digit: 1 if Vulnerable, 0 if Non-vulnerable.

The node information of the code snippet is as follows:

The edge information of the code snippet is as follows:


The following is an example, and it is .


Answer (0 or 1):
```

## 29. devign/B0/42/devign:validation:13034

SHA-256: d4c2b0438c19e9c7eac29fe441b85651411e2928ef7cab6540ace236eb4cb93a

Nguồn: Runs-management/dry_run_validation_20261102/devign/validation/B0/42/prompts.jsonl

```text
You are now an excellent programmer. You are conducting a function vulnerability detection task for C/C++ language.

static void render_fragments(Vp3DecodeContext *s,
                             int first_fragment,
                             int width,
                             int height,
                             int plane /* 0 = Y, 1 = U, 2 = V */) 
{
    int x, y;
    int m, n;
    int i = first_fragment;
    int16_t *dequantizer;
    DCTELEM __align16 output_samples[64];
    unsigned char *output_plane;
    unsigned char *last_plane;
    unsigned char *golden_plane;
    int stride;
    int motion_x = 0xdeadbeef, motion_y = 0xdeadbeef;
    int upper_motion_limit, lower_motion_limit;
    int motion_halfpel_index;
    uint8_t *motion_source;
    debug_vp3("  vp3: rendering final fragments for %s\n",
        (plane == 0) ? "Y plane" : (plane == 1) ? "U plane" : "V plane");
    /* set up plane-specific parameters */
    if (plane == 0) {
        dequantizer = s->intra_y_dequant;
        output_plane = s->current_frame.data[0];
        last_plane = s->last_frame.data[0];
        golden_plane = s->golden_frame.data[0];
        stride = s->current_frame.linesize[0];
	if (!s->flipped_image) stride = -stride;
        upper_motion_limit = 7 * s->current_frame.linesize[0];
        lower_motion_limit = height * s->current_frame.linesize[0] + width - 8;
    } else if (plane == 1) {
        dequantizer = s->intra_c_dequant;
        output_plane = s->current_frame.data[1];
        last_plane = s->last_frame.data[1];
        golden_plane = s->golden_frame.data[1];
        stride = s->current_frame.linesize[1];
	if (!s->flipped_image) stride = -stride;
        upper_motion_limit = 7 * s->current_frame.linesize[1];
        lower_motion_limit = height * s->current_frame.linesize[1] + width - 8;
    } else {
        dequantizer = s->intra_c_dequant;
        output_plane = s->current_frame.data[2];
        last_plane = s->last_frame.data[2];
        golden_plane = s->golden_frame.data[2];
        stride = s->current_frame.linesize[2];
	if (!s->flipped_image) stride = -stride;
        upper_motion_limit = 7 * s->current_frame.linesize[2];
        lower_motion_limit = height * s->current_frame.linesize[2] + width - 8;
    }
    /* for each fragment row... */
    for (y = 0; y < height; y += 8) {
        /* for each fragment in a row... */
        for (x = 0; x < width; x += 8, i++) {
            if ((i < 0) || (i >= s->fragment_count)) {
                av_log(s->avctx, AV_LOG_ERROR, "  vp3:render_fragments(): bad fragment number (%d)\n", i);
                return;
            }
            /* transform if this block was coded */
            if ((s->all_fragments[i].coding_method != MODE_COPY) &&
		!((s->avctx->flags & CODEC_FLAG_GRAY) && plane)) {
                if ((s->all_fragments[i].coding_method == MODE_USING_GOLDEN) ||
                    (s->all_fragments[i].coding_method == MODE_GOLDEN_MV))
                    motion_source= golden_plane;
                else 
                    motion_source= last_plane;
                motion_source += s->all_fragments[i].first_pixel;
                motion_halfpel_index = 0;
                /* sort out the motion vector if this fragment is coded
                 * using a motion vector method */
                if ((s->all_fragments[i].coding_method > MODE_INTRA) &&
                    (s->all_fragments[i].coding_method != MODE_USING_GOLDEN)) {
                    int src_x, src_y;
                    motion_x = s->all_fragments[i].motion_x;
                    motion_y = s->all_fragments[i].motion_y;
                    if(plane){
                        motion_x= (motion_x>>1) | (motion_x&1);
                        motion_y= (motion_y>>1) | (motion_y&1);
                    }
                    src_x= (motion_x>>1) + x;
                    src_y= (motion_y>>1) + y;
if ((motion_x == 0xbeef) || (motion_y == 0xbeef))
av_log(s->avctx, AV_LOG_ERROR, " help! got beefy vector! (%X, %X)\n", motion_x, motion_y);
                    motion_halfpel_index = motion_x & 0x01;
                    motion_source += (motion_x >> 1);
//                    motion_y = -motion_y;
                    motion_halfpel_index |= (motion_y & 0x01) << 1;
                    motion_source += ((motion_y >> 1) * stride);
                    if(src_x<0 || src_y<0 || src_x + 9 >= width || src_y + 9 >= height){
                        uint8_t *temp= s->edge_emu_buffer;
                        if(stride<0) temp -= 9*stride;
			else temp += 9*stride;
                        ff_emulated_edge_mc(temp, motion_source, stride, 9, 9, src_x, src_y, width, height);
                        motion_source= temp;
                    }
                }
                /* first, take care of copying a block from either the
                 * previous or the golden frame */
                if (s->all_fragments[i].coding_method != MODE_INTRA) {
                    //Note, it is possible to implement all MC cases with put_no_rnd_pixels_l2 which would look more like the VP3 source but this would be slower as put_no_rnd_pixels_tab is better optimzed
                    if(motion_halfpel_index != 3){
                        s->dsp.put_no_rnd_pixels_tab[1][motion_halfpel_index](
                            output_plane + s->all_fragments[i].first_pixel,
                            motion_source, stride, 8);
                    }else{
                        int d= (motion_x ^ motion_y)>>31; // d is 0 if motion_x and _y have the same sign, else -1
                        s->dsp.put_no_rnd_pixels_l2[1](
                            output_plane + s->all_fragments[i].first_pixel,
                            motion_source - d, 
                            motion_source + stride + 1 + d, 
                            stride, 8);
                    }
                }
                /* dequantize the DCT coefficients */
                debug_idct("fragment %d, coding mode %d, DC = %d, dequant = %d:\n", 
                    i, s->all_fragments[i].coding_method, 
                    s->all_fragments[i].coeffs[0], dequantizer[0]);
                /* invert DCT and place (or add) in final output */
                s->dsp.vp3_idct(s->all_fragments[i].coeffs,
                    dequantizer,
                    s->all_fragments[i].coeff_count,
                    output_samples);
                if (s->all_fragments[i].coding_method == MODE_INTRA) {
                    s->dsp.put_signed_pixels_clamped(output_samples,
                        output_plane + s->all_fragments[i].first_pixel,
                        stride);
                } else {
                    s->dsp.add_pixels_clamped(output_samples,
                        output_plane + s->all_fragments[i].first_pixel,
                        stride);
                }
                debug_idct("block after idct_%s():\n",
                    (s->all_fragments[i].coding_method == MODE_INTRA)?
                    "put" : "add");
                for (m = 0; m < 8; m++) {
                    for (n = 0; n < 8; n++) {
                        debug_idct(" %3d", *(output_plane + 
                            s->all_fragments[i].first_pixel + (m * stride + n)));
                    }
                    debug_idct("\n");
                }
                debug_idct("\n");
            } else {
                /* copy directly from the previous frame */
                s->dsp.put_pixels_tab[1][0](
                    output_plane + s->all_fragments[i].first_pixel,
                    last_plane + s->all_fragments[i].first_pixel,
                    stride, 8);
            }
        }
    }
    emms_c();
}

In the above code snippet, check for potential security vulnerabilities and answer with a single digit: 1 if Vulnerable, 0 if Non-vulnerable.

The node information of the code snippet is as follows:

The edge information of the code snippet is as follows:


The following is an example, and it is .


Answer (0 or 1):
```

## 30. devign/B2-rand/43/devign:validation:5825

SHA-256: ce6ccdf8e790ba183c6bf9dd1177c761d3e484c1c9c7a8317c9a525d686bc402

Nguồn: Runs-management/dry_run_validation_20261102/devign/validation/B2-rand/43/prompts.jsonl

```text
You are now an excellent programmer. You are conducting a function vulnerability detection task for C/C++ language.

static void channel_store_d(struct fs_dma_ctrl *ctrl, int c)

{

	target_phys_addr_t addr = channel_reg(ctrl, c, RW_SAVED_DATA);



	/* Encode and store. FIXME: handle endianness.  */

	D(printf("%s ch=%d addr=" TARGET_FMT_plx "\n", __func__, c, addr));

	cpu_physical_memory_write (addr,

				  (void *) &ctrl->channels[c].current_d, 

				  sizeof ctrl->channels[c].current_d);

}

In the above code snippet, check for potential security vulnerabilities and answer with a single digit: 1 if Vulnerable, 0 if Non-vulnerable.

The node information of the code snippet is as follows:
Node 25769803776: (BLOCK) '{  	target_phys_addr_t addr = channel_re...'
Node 30064771072: (CALL) 'addr = channel_reg(ctrl, c, RW_SAVED_DAT...'
Node 30064771073: (CALL) 'channel_reg(ctrl, c, RW_SAVED_DATA)'
Node 30064771074: (CALL) 'cpu_physical_memory_write (addr,  				  ...'
Node 30064771075: (CALL) '(void *) &ctrl->channels[c].current_d'
Node 30064771076: (CALL) '&ctrl->channels[c].current_d'
Node 30064771077: (CALL) 'ctrl->channels[c].current_d'
Node 30064771078: (CALL) 'ctrl->channels[c]'
Node 30064771079: (CALL) 'ctrl->channels'
Node 30064771080: (CALL) 'sizeof ctrl->channels[c].current_d'
Node 30064771081: (CALL) 'ctrl->channels[c].current_d'
Node 30064771082: (CALL) 'ctrl->channels[c]'
Node 30064771083: (CALL) 'ctrl->channels'
Node 55834574848: (FIELD_IDENTIFIER) 'channels'
Node 55834574849: (FIELD_IDENTIFIER) 'current_d'
Node 55834574850: (FIELD_IDENTIFIER) 'channels'
Node 55834574851: (FIELD_IDENTIFIER) 'current_d'
Node 68719476736: (IDENTIFIER) 'addr'
Node 68719476737: (IDENTIFIER) 'ctrl'
Node 68719476738: (IDENTIFIER) 'c'
Node 68719476739: (IDENTIFIER) '<unknown> RW_SAVED_DATA'
Node 68719476740: (IDENTIFIER) 'addr'
Node 68719476741: (IDENTIFIER) 'ctrl'
Node 68719476742: (IDENTIFIER) 'c'
Node 68719476743: (IDENTIFIER) 'ctrl'
Node 68719476744: (IDENTIFIER) 'c'
Node 94489280512: (LOCAL) 'target_phys_addr_t addr'
Node 94489280513: (LOCAL) '<unknown> RW_SAVED_DATA'
Node 107374182400: (METHOD) 'static void channel_store_d(struct fs_dm...'
Node 111669149696: (METHOD_PARAMETER_IN) 'struct fs_dma_ctrl *ctrl'
Node 111669149697: (METHOD_PARAMETER_IN) 'int c'
Node 115964116992: (METHOD_PARAMETER_OUT) 'struct fs_dma_ctrl *ctrl'
Node 115964116993: (METHOD_PARAMETER_OUT) 'int c'
Node 124554051584: (METHOD_RETURN) 'RET'
Node 128849018880: (MODIFIER) '<empty>'
Node 176093659136: (TYPE_REF) 'void *'
The edge information of the code snippet is as follows:
Edge: Node 25769803776 -> AST -> Node 94489280512
Edge: Node 25769803776 -> AST -> Node 30064771072
Edge: Node 25769803776 -> AST -> Node 30064771074
Edge: Node 25769803776 -> AST -> Node 94489280513
Edge: Node 30064771072 -> ARGUMENT -> Node 68719476736
Edge: Node 30064771072 -> ARGUMENT -> Node 30064771073
Edge: Node 30064771072 -> AST -> Node 68719476736
Edge: Node 30064771072 -> AST -> Node 30064771073
Edge: Node 30064771072 -> CFG -> Node 68719476740
Edge: Node 30064771072 -> DOMINATE -> Node 68719476740
Edge: Node 30064771072 -> POST_DOMINATE -> Node 30064771073
Edge: Node 30064771072 -> REACHING_DEF -> Node 124554051584
Edge: Node 30064771073 -> ARGUMENT -> Node 68719476737
Edge: Node 30064771073 -> ARGUMENT -> Node 68719476738
Edge: Node 30064771073 -> ARGUMENT -> Node 68719476739
Edge: Node 30064771073 -> AST -> Node 68719476737
Edge: Node 30064771073 -> AST -> Node 68719476738
Edge: Node 30064771073 -> AST -> Node 68719476739

The following is an example, and it is Vulnerable.
iscsi_co_generic_cb(struct iscsi_context *iscsi, int status,

                        void *command_data, void *opaque)

{

    struct IscsiTask *iTask = opaque;

    struct scsi_task *task = command_data;



    iTask->status = status;

    iTask->do_retry = 0;

    iTask->task = task;



    if (status != SCSI_STATUS_GOOD) {

        if (iTask->retries++ < ISCSI_CMD_RETRIES) {

            if (status == SCSI_STATUS_CHECK_CONDITION

                && task->sense.key == SCSI_SENSE_UNIT_ATTENTION) {

                error_report("iSCSI CheckCondition: %s",

                             iscsi_get_error(iscsi));

                iTask->do_retry = 1;

                goto out;

            }

            /* status 0x28 is SCSI_TASK_SET_FULL. It was first introduced

             * in libiscsi 1.10.0. Hardcode this value here to avoid

             * the need to bump the libiscsi requirement to 1.10.0 */

            if (status == SCSI_STATUS_BUSY || status == 0x28) {

                unsigned retry_time =

                    exp_random(iscsi_retry_times[iTask->retries - 1]);

                error_report("iSCSI Busy/TaskSetFull (retry #%u in %u ms): %s",

                             iTask->retries, retry_time,

                             iscsi_get_error(iscsi));

                aio_timer_init(iTask->iscsilun->aio_context,

                               &iTask->retry_timer, QEMU_CLOCK_REALTIME,

                               SCALE_MS, iscsi_retry_timer_expired, iTask);

                timer_mod(&iTask->retry_timer,

                          qemu_clock_get_ms(QEMU_CLOCK_REALTIME) + retry_time);

                iTask->do_retry = 1;

                return;

            }

        }

        error_report("iSCSI Failure: %s", iscsi_get_error(iscsi));

    } else {

        iTask->iscsilun->force_next_flush |= iTask->force_next_flush;

    }



out:

    if (iTask->co) {

        iTask->bh = aio_bh_new(iTask->iscsilun->aio_context,

                               iscsi_co_generic_bh_cb, iTask);

        qemu_bh_schedule(iTask->bh);

    } else {

        iTask->complete = 1;

    }

}

Answer (0 or 1):
```

## 31. reveal/B0/42/reveal:validation:910

SHA-256: 6c2741a38126cc15e97cda0134542209e49a3adf5ee0d25b24479080d8476107

Nguồn: Runs-management/dry_run_validation_20261102/reveal/validation/B0/42/prompts.jsonl

```text
You are now an excellent programmer. You are conducting a function vulnerability detection task for C/C++ language.

static int selinux_binder_set_context_mgr ( struct task_struct * mgr ) {
 u32 mysid = current_sid ( ) ;
 u32 mgrsid = task_sid ( mgr ) ;
 return avc_has_perm ( mysid , mgrsid , SECCLASS_BINDER , BINDER__SET_CONTEXT_MGR , NULL ) ;
 }

In the above code snippet, check for potential security vulnerabilities and answer with a single digit: 1 if Vulnerable, 0 if Non-vulnerable.

The node information of the code snippet is as follows:

The edge information of the code snippet is as follows:


The following is an example, and it is .


Answer (0 or 1):
```

## 32. reveal/B1/42/reveal:validation:1906

SHA-256: 16ae8dc5da5a3957ef533dfeaa12dae0b92b9be02ebfee667ca7329accb0df92

Nguồn: Runs-management/dry_run_validation_20261102/reveal/validation/B1/42/prompts.jsonl

```text
You are now an excellent programmer. You are conducting a function vulnerability detection task for C/C++ language.

static Image * ReadVIFFImage ( const ImageInfo * image_info , ExceptionInfo * exception ) {
 # define VFF_CM_genericRGB 15 # define VFF_CM_ntscRGB 1 # define VFF_CM_NONE 0 # define VFF_DEP_DECORDER 0x4 # define VFF_DEP_NSORDER 0x8 # define VFF_DES_RAW 0 # define VFF_LOC_IMPLICIT 1 # define VFF_MAPTYP_NONE 0 # define VFF_MAPTYP_1_BYTE 1 # define VFF_MAPTYP_2_BYTE 2 # define VFF_MAPTYP_4_BYTE 4 # define VFF_MAPTYP_FLOAT 5 # define VFF_MAPTYP_DOUBLE 7 # define VFF_MS_NONE 0 # define VFF_MS_ONEPERBAND 1 # define VFF_MS_SHARED 3 # define VFF_TYP_BIT 0 # define VFF_TYP_1_BYTE 1 # define VFF_TYP_2_BYTE 2 # define VFF_TYP_4_BYTE 4 # define VFF_TYP_FLOAT 5 # define VFF_TYP_DOUBLE 9 typedef struct _ViffInfo {
 unsigned char identifier , file_type , release , version , machine_dependency , reserve [ 3 ] ;
 char comment [ 512 ] ;
 unsigned int rows , columns , subrows ;
 int x_offset , y_offset ;
 float x_bits_per_pixel , y_bits_per_pixel ;
 unsigned int location_type , location_dimension , number_of_images , number_data_bands , data_storage_type , data_encode_scheme , map_scheme , map_storage_type , map_rows , map_columns , map_subrows , map_enable , maps_per_cycle , color_space_model ;
 }
 ViffInfo ;
 double min_value , scale_factor , value ;
 Image * image ;
 int bit ;
 MagickBooleanType status ;
 MagickSizeType number_pixels ;
 register IndexPacket * indexes ;
 register ssize_t x ;
 register PixelPacket * q ;
 register ssize_t i ;
 register unsigned char * p ;
 size_t bytes_per_pixel , max_packets , quantum ;
 ssize_t count , y ;
 unsigned char * pixels ;
 unsigned long lsb_first ;
 ViffInfo viff_info ;
 assert ( image_info != ( const ImageInfo * ) NULL ) ;
 assert ( image_info -> signature == MagickSignature ) ;
 if ( image_info -> debug != MagickFalse ) ( void ) LogMagickEvent ( TraceEvent , GetMagickModule ( ) , "%s" , image_info -> filename ) ;
 assert ( exception != ( ExceptionInfo * ) NULL ) ;
 assert ( exception -> signature == MagickSignature ) ;
 image = AcquireImage ( image_info ) ;
 status = OpenBlob ( image_info , image , ReadBinaryBlobMode , exception ) ;
 if ( status == MagickFalse ) {
 image = DestroyImageList ( image ) ;
 return ( ( Image * ) NULL ) ;
 }
 count = ReadBlob ( image , 1 , & viff_info . identifier ) ;
 do {
 if ( ( count != 1 ) || ( ( unsigned char ) viff_info . identifier != 0xab ) ) ThrowReaderException ( CorruptImageError , "NotAVIFFImage" ) ;
 ( void ) ReadBlob ( image , sizeof ( viff_info . file_type ) , & viff_info . file_type ) ;
 ( void ) ReadBlob ( image , sizeof ( viff_info . release ) , & viff_info . release ) ;
 ( void ) ReadBlob ( image , sizeof ( viff_info . version ) , & viff_info . version ) ;
 ( void ) ReadBlob ( image , sizeof ( viff_info . machine_dependency ) , & viff_info . machine_dependency ) ;
 ( void ) ReadBlob ( image , sizeof ( viff_info . reserve ) , viff_info . reserve ) ;
 ( void ) ReadBlob ( image , 512 , ( unsigned char * ) viff_info . comment ) ;
 viff_info . comment [ 511 ] = '\0' ;
 if ( strlen ( viff_info . comment ) > 4 ) ( void ) SetImageProperty ( image , "comment" , viff_info . comment ) ;
 if ( ( viff_info . machine_dependency == VFF_DEP_DECORDER ) || ( viff_info . machine_dependency == VFF_DEP_NSORDER ) ) image -> endian = LSBEndian ;
 else image -> endian = MSBEndian ;
 viff_info . rows = ReadBlobLong ( image ) ;
 viff_info . columns = ReadBlobLong ( image ) ;
 viff_info . subrows = ReadBlobLong ( image ) ;
 viff_info . x_offset = ( int ) ReadBlobLong ( image ) ;
 viff_info . y_offset = ( int ) ReadBlobLong ( image ) ;
 viff_info . x_bits_per_pixel = ( float ) ReadBlobLong ( image ) ;
 viff_info . y_bits_per_pixel = ( float ) ReadBlobLong ( image ) ;
 viff_info . location_type = ReadBlobLong ( image ) ;
 viff_info . location_dimension = ReadBlobLong ( image ) ;
 viff_info . number_of_images = ReadBlobLong ( image ) ;
 viff_info . number_data_bands = ReadBlobLong ( image ) ;
 viff_info . data_storage_type = ReadBlobLong ( image ) ;
 viff_info . data_encode_scheme = ReadBlobLong ( image ) ;
 viff_info . map_scheme = ReadBlobLong ( image ) ;
 viff_info . map_storage_type = ReadBlobLong ( image ) ;
 viff_info . map_rows = ReadBlobLong ( image ) ;
 viff_info . map_columns = ReadBlobLong ( image ) ;
 viff_info . map_subrows = ReadBlobLong ( image ) ;
 viff_info . map_enable = ReadBlobLong ( image ) ;
 viff_info . maps_per_cycle = ReadBlobLong ( image ) ;
 viff_info . color_space_model = ReadBlobLong ( image ) ;
 for ( i = 0 ;
 i < 420 ;
 i ++ ) ( void ) ReadBlobByte ( image ) ;
 if ( EOFBlob ( image ) != MagickFalse ) ThrowReaderException ( CorruptImageError , "UnexpectedEndOfFile" ) ;
 image -> columns = viff_info . rows ;
 image -> rows = viff_info . columns ;
 image -> depth = viff_info . x_bits_per_pixel <= 8 ? 8UL : MAGICKCORE_QUANTUM_DEPTH ;
 number_pixels = ( MagickSizeType ) viff_info . columns * viff_info . rows ;
 if ( number_pixels != ( size_t ) number_pixels ) ThrowReaderException ( ResourceLimitError , "MemoryAllocationFailed" ) ;
 if ( number_pixels == 0 ) ThrowReaderException ( CoderError , "ImageColumnOrRowSizeIsNotSupported" ) ;
 if ( ( viff_info . number_data_bands < 1 ) || ( viff_info . number_data_bands > 4 ) ) ThrowReaderException ( CorruptImageError , "ImproperImageHeader" ) ;
 if ( ( viff_info . data_storage_type != VFF_TYP_BIT ) && ( viff_info . data_storage_type != VFF_TYP_1_BYTE ) && ( viff_info . data_storage_type != VFF_TYP_2_BYTE ) && ( viff_info . data_storage_type != VFF_TYP_4_BYTE ) && ( viff_info . data_storage_type != VFF_TYP_FLOAT ) && ( viff_info . data_storage_type != VFF_TYP_DOUBLE ) ) ThrowReaderException ( CoderError , "DataStorageTypeIsNotSupported" ) ;
 if ( viff_info . data_encode_scheme != VFF_DES_RAW ) ThrowReaderException ( CoderError , "DataEncodingSchemeIsNotSupported" ) ;
 if ( ( viff_info . map_storage_type != VFF_MAPTYP_NONE ) && ( viff_info . map_storage_type != VFF_MAPTYP_1_BYTE ) && ( viff_info . map_storage_type != VFF_MAPTYP_2_BYTE ) && ( viff_info . map_storage_type != VFF_MAPTYP_4_BYTE ) && ( viff_info . map_storage_type != VFF_MAPTYP_FLOAT ) && ( viff_info . map_storage_type != VFF_MAPTYP_DOUBLE ) ) ThrowReaderException ( CoderError , "MapStorageTypeIsNotSupported" ) ;
 if ( ( viff_info . color_space_model != VFF_CM_NONE ) && ( viff_info . color_space_model != VFF_CM_ntscRGB ) && ( viff_info . color_space_model != VFF_CM_genericRGB ) ) ThrowReaderException ( CoderError , "ColorspaceModelIsNotSupported" ) ;
 if ( viff_info . location_type != VFF_LOC_IMPLICIT ) ThrowReaderException ( CoderError , "LocationTypeIsNotSupported" ) ;
 if ( viff_info . number_of_images != 1 ) ThrowReaderException ( CoderError , "NumberOfImagesIsNotSupported" ) ;
 if ( viff_info . map_rows == 0 ) viff_info . map_scheme = VFF_MS_NONE ;
 switch ( ( int ) viff_info . map_scheme ) {
 case VFF_MS_NONE : {
 if ( viff_info . number_data_bands < 3 ) {
 if ( viff_info . data_storage_type == VFF_TYP_BIT ) image -> colors = 2 ;
 else if ( viff_info . data_storage_type == VFF_MAPTYP_1_BYTE ) image -> colors = 256UL ;
 else image -> colors = image -> depth <= 8 ? 256UL : 65536UL ;
 if ( AcquireImageColormap ( image , image -> colors ) == MagickFalse ) ThrowReaderException ( ResourceLimitError , "MemoryAllocationFailed" ) ;
 }
 break ;
 }
 case VFF_MS_ONEPERBAND : case VFF_MS_SHARED : {
 unsigned char * viff_colormap ;
 switch ( ( int ) viff_info . map_storage_type ) {
 case VFF_MAPTYP_1_BYTE : bytes_per_pixel = 1 ;
 break ;
 case VFF_MAPTYP_2_BYTE : bytes_per_pixel = 2 ;
 break ;
 case VFF_MAPTYP_4_BYTE : bytes_per_pixel = 4 ;
 break ;
 case VFF_MAPTYP_FLOAT : bytes_per_pixel = 4 ;
 break ;
 case VFF_MAPTYP_DOUBLE : bytes_per_pixel = 8 ;
 break ;
 default : bytes_per_pixel = 1 ;
 break ;
 }
 image -> colors = viff_info . map_columns ;
 if ( AcquireImageColormap ( image , image -> colors ) == MagickFalse ) ThrowReaderException ( ResourceLimitError , "MemoryAllocationFailed" ) ;
 if ( viff_info . map_rows > ( viff_info . map_rows * bytes_per_pixel * sizeof ( * viff_colormap ) ) ) ThrowReaderException ( CorruptImageError , "ImproperImageHeader" ) ;
 viff_colormap = ( unsigned char * ) AcquireQuantumMemory ( image -> colors , viff_info . map_rows * bytes_per_pixel * sizeof ( * viff_colormap ) ) ;
 if ( viff_colormap == ( unsigned char * ) NULL ) ThrowReaderException ( ResourceLimitError , "MemoryAllocationFailed" ) ;
 ( void ) ReadBlob ( image , bytes_per_pixel * image -> colors * viff_info . map_rows , viff_colormap ) ;
 lsb_first = 1 ;
 if ( * ( char * ) & lsb_first && ( ( viff_info . machine_dependency != VFF_DEP_DECORDER ) && ( viff_info . machine_dependency != VFF_DEP_NSORDER ) ) ) switch ( ( int ) viff_info . map_storage_type ) {
 case VFF_MAPTYP_2_BYTE : {
 MSBOrderShort ( viff_colormap , ( bytes_per_pixel * image -> colors * viff_info . map_rows ) ) ;
 break ;
 }
 case VFF_MAPTYP_4_BYTE : case VFF_MAPTYP_FLOAT : {
 MSBOrderLong ( viff_colormap , ( bytes_per_pixel * image -> colors * viff_info . map_rows ) ) ;
 break ;
 }
 default : break ;
 }
 for ( i = 0 ;
 i < ( ssize_t ) ( viff_info . map_rows * image -> colors ) ;
 i ++ ) {
 switch ( ( int ) viff_info . map_storage_type ) {
 case VFF_MAPTYP_2_BYTE : value = 1.0 * ( ( short * ) viff_colormap ) [ i ] ;
 break ;
 case VFF_MAPTYP_4_BYTE : value = 1.0 * ( ( int * ) viff_colormap ) [ i ] ;
 break ;
 case VFF_MAPTYP_FLOAT : value = ( ( float * ) viff_colormap ) [ i ] ;
 break ;
 case VFF_MAPTYP_DOUBLE : value = ( ( double * ) viff_colormap ) [ i ] ;
 break ;
 default : value = 1.0 * viff_colormap [ i ] ;
 break ;
 }
 if ( i < ( ssize_t ) image -> colors ) {
 image -> colormap [ i ] . red = ScaleCharToQuantum ( ( unsigned char ) value ) ;
 image -> colormap [ i ] . green = ScaleCharToQuantum ( ( unsigned char ) value ) ;
 image -> colormap [ i ] . blue = ScaleCharToQuantum ( ( unsigned char ) value ) ;
 }
 else if ( i < ( ssize_t ) ( 2 * image -> colors ) ) image -> colormap [ i % image -> colors ] . green = ScaleCharToQuantum ( ( unsigned char ) value ) ;
 else if ( i < ( ssize_t ) ( 3 * image -> colors ) ) image -> colormap [ i % image -> colors ] . blue = ScaleCharToQuantum ( ( unsigned char ) value ) ;
 }
 viff_colormap = ( unsigned char * ) RelinquishMagickMemory ( viff_colormap ) ;
 break ;
 }
 default : ThrowReaderException ( CoderError , "ColormapTypeNotSupported" ) ;
 }
 image -> matte = viff_info . number_data_bands == 4 ? MagickTrue : MagickFalse ;
 image -> storage_class = ( viff_info . number_data_bands < 3 ? PseudoClass : DirectClass ) ;
 image -> columns = viff_info . rows ;
 image -> rows = viff_info . columns ;
 if ( (
/* [TRUNCATED TARGET] */

In the above code snippet, check for potential security vulnerabilities and answer with a single digit: 1 if Vulnerable, 0 if Non-vulnerable.

The node information of the code snippet is as follows:
Node 25769803815: (BLOCK) '{  # define VFF_CM_genericRGB 15 # defin...'
Node 30064771200: (CALL) 'reserve [ 3 ]'
Node 30064771201: (CALL) 'reserve [ 3 ]'
Node 30064771202: (CALL) 'comment [ 512 ]'
Node 30064771203: (CALL) 'comment [ 512 ]'
Node 68719476890: (IDENTIFIER) 'reserve'
Node 68719476891: (IDENTIFIER) 'unsigned char[3]'
Node 68719476892: (IDENTIFIER) 'comment'
Node 68719476893: (IDENTIFIER) 'char[512]'
Node 90194313225: (LITERAL) '3'
Node 90194313226: (LITERAL) '512'
Node 94489280553: (LOCAL) 'unsigned char identifier'
Node 94489280554: (LOCAL) 'unsigned char file_type'
Node 94489280555: (LOCAL) 'unsigned char release'
Node 94489280556: (LOCAL) 'unsigned char version'
Node 94489280557: (LOCAL) 'unsigned char machine_dependency'
Node 94489280558: (LOCAL) 'unsigned char reserve [ 3 ]'
Node 94489280559: (LOCAL) 'char comment [ 512 ]'
Node 94489280560: (LOCAL) 'unsigned int rows'
Node 94489280561: (LOCAL) 'unsigned int columns'
Node 94489280562: (LOCAL) 'unsigned int subrows'
Node 94489280563: (LOCAL) 'int x_offset'
Node 94489280564: (LOCAL) 'int y_offset'
Node 94489280565: (LOCAL) 'float x_bits_per_pixel'
Node 94489280566: (LOCAL) 'float y_bits_per_pixel'
Node 94489280567: (LOCAL) 'unsigned int location_type'
Node 94489280568: (LOCAL) 'unsigned int location_dimension'
Node 94489280569: (LOCAL) 'unsigned int number_of_images'
Node 94489280570: (LOCAL) 'unsigned int number_data_bands'
Node 94489280571: (LOCAL) 'unsigned int data_storage_type'
Node 94489280572: (LOCAL) 'unsigned int data_encode_scheme'
Node 94489280573: (LOCAL) 'unsigned int map_scheme'
Node 94489280574: (LOCAL) 'unsigned int map_storage_type'
Node 94489280575: (LOCAL) 'unsigned int map_rows'
Node 94489280576: (LOCAL) 'unsigned int map_columns'
Node 94489280577: (LOCAL) 'unsigned int map_subrows'
Node 94489280578: (LOCAL) 'unsigned int map_enable'
Node 94489280579: (LOCAL) 'unsigned int maps_per_cycle'
Node 94489280580: (LOCAL) 'unsigned int color_space_model'
Node 107374182411: (METHOD) 'static Image * ReadVIFFImage ( const Ima...'
The edge information of the code snippet is as follows:
Edge: Node 25769803815 -> AST -> Node 94489280553
Edge: Node 25769803815 -> AST -> Node 94489280554
Edge: Node 25769803815 -> AST -> Node 94489280555
Edge: Node 25769803815 -> AST -> Node 94489280556
Edge: Node 25769803815 -> AST -> Node 94489280557
Edge: Node 25769803815 -> AST -> Node 94489280558
Edge: Node 25769803815 -> AST -> Node 30064771200
Edge: Node 25769803815 -> AST -> Node 94489280559
Edge: Node 25769803815 -> AST -> Node 30064771202
Edge: Node 25769803815 -> AST -> Node 94489280560
Edge: Node 25769803815 -> AST -> Node 94489280561
Edge: Node 25769803815 -> AST -> Node 94489280562
Edge: Node 25769803815 -> AST -> Node 94489280563
Edge: Node 25769803815 -> AST -> Node 94489280564
Edge: Node 25769803815 -> AST -> Node 94489280565
Edge: Node 25769803815 -> AST -> Node 94489280566

The following is an example, and it is .


Answer (0 or 1):
```

## 33. reveal/B1-full/42/reveal:validation:708

SHA-256: 4168360f7144c0d998a2b5f3211607efa6fe750cd80e8774b2987de9b7c02744

Nguồn: Runs-management/dry_run_validation_20261102/reveal/validation/B1-full/42/prompts.jsonl

```text
You are now an excellent programmer. You are conducting a function vulnerability detection task for C/C++ language.

static int dissect_h225_Facility_UUIE ( tvbuff_t * tvb _U_ , int offset _U_ , asn1_ctx_t * actx _U_ , proto_tree * tree _U_ , int hf_index _U_ ) {
 # line 445 "./asn1/h225/h225.cnf" h225_packet_info * h225_pi ;
 offset = dissect_per_sequence ( tvb , offset , actx , tree , hf_index , ett_h225_Facility_UUIE , Facility_UUIE_sequence ) ;
 # line 449 "./asn1/h225/h225.cnf" h225_pi = ( h225_packet_info * ) p_get_proto_data ( wmem_packet_scope ( ) , actx -> pinfo , proto_h225 , 0 ) ;
 if ( h225_pi != NULL ) {
 h225_pi -> cs_type = H225_FACILITY ;
 g_snprintf ( h225_pi -> frame_label , 50 , "%s" , val_to_str ( h225_pi -> cs_type , T_h323_message_body_vals , "<unknown>" ) ) ;
 }
 return offset ;
 }

In the above code snippet, check for potential security vulnerabilities and answer with a single digit: 1 if Vulnerable, 0 if Non-vulnerable.

The node information of the code snippet is as follows:
Node 25769803794: (BLOCK) '{  # line 445 "./asn1/h225/h225.cnf" h22...'
Node 25769803795: (BLOCK) '{  h225_pi -> cs_type = H225_FACILITY ; ...'
Node 30064771162: (CALL) 'offset = dissect_per_sequence ( tvb , of...'
Node 30064771163: (CALL) 'dissect_per_sequence ( tvb , offset , ac...'
Node 30064771164: (CALL) 'h225_pi != NULL'
Node 30064771165: (CALL) 'h225_pi -> cs_type = H225_FACILITY'
Node 30064771166: (CALL) 'h225_pi -> cs_type'
Node 30064771167: (CALL) 'g_snprintf ( h225_pi -> frame_label , 50...'
Node 30064771168: (CALL) 'h225_pi -> frame_label'
Node 30064771169: (CALL) 'val_to_str ( h225_pi -> cs_type , T_h323...'
Node 30064771170: (CALL) 'h225_pi -> cs_type'
Node 47244640259: (CONTROL_STRUCTURE) 'if ( h225_pi != NULL ) {  h225_pi -> cs_...'
Node 55834574862: (FIELD_IDENTIFIER) 'cs_type'
Node 55834574863: (FIELD_IDENTIFIER) 'frame_label'
Node 55834574864: (FIELD_IDENTIFIER) 'cs_type'
Node 68719476830: (IDENTIFIER) 'offset'
The edge information of the code snippet is as follows:
Edge: Node 25769803794 -> AST -> Node 30064771162
Edge: Node 25769803794 -> AST -> Node 47244640259
Edge: Node 25769803795 -> AST -> Node 30064771165
Edge: Node 25769803795 -> AST -> Node 30064771167
Edge: Node 30064771162 -> ARGUMENT -> Node 68719476830
Edge: Node 30064771162 -> ARGUMENT -> Node 30064771163
Edge: Node 30064771162 -> AST -> Node 68719476830
Edge: Node 30064771162 -> AST -> Node 30064771163
Edge: Node 30064771162 -> POST_DOMINATE -> Node 30064771163
Edge: Node 30064771163 -> CFG -> Node 30064771162
Edge: Node 30064771163 -> DOMINATE -> Node 30064771162
Edge: Node 30064771163 -> REACHING_DEF -> Node 68719476830
Edge: Node 30064771163 -> REACHING_DEF -> Node 30064771162
Edge: Node 30064771164 -> CDG -> Node 30064771165
Edge: Node 30064771164 -> CDG -> Node 30064771170
Edge: Node 30064771164 -> CDG -> Node 30064771167
Edge: Node 30064771164 -> CDG -> Node 30064771166
Edge: Node 30064771164 -> CDG -> Node 30064771169
Edge: Node 30064771164 -> CDG -> Node 30064771168
Edge: Node 30064771164 -> CDG -> Node 55834574864
Edge: Node 30064771164 -> CDG -> Node 55834574863
Edge: Node 30064771164 -> CDG -> Node 55834574862
Edge: Node 30064771165 -> ARGUMENT -> Node 30064771166
Edge: Node 30064771165 -> AST -> Node 30064771166
Edge: Node 30064771166 -> ARGUMENT -> Node 55834574862
Edge: Node 30064771166 -> AST -> Node 55834574862
Edge: Node 30064771166 -> POST_DOMINATE -> Node 55834574862
Edge: Node 30064771166 -> REACHING_DEF -> Node 30064771165
Edge: Node 30064771166 -> REACHING_DEF -> Node 30064771170

The following is an example, and it is .


Answer (0 or 1):
```

## 34. reveal/B1-shuf/42/reveal:validation:1672

SHA-256: 9fe75bf43acc9b5ef7d0c537cf534212b47ddebe9b6f52bcd2bc03731ad469f5

Nguồn: Runs-management/dry_run_validation_20261102/reveal/validation/B1-shuf/42/prompts.jsonl

```text
You are now an excellent programmer. You are conducting a function vulnerability detection task for C/C++ language.

static void update_coef_probs_common ( vp9_writer * const bc , VP9_COMP * cpi , TX_SIZE tx_size , vp9_coeff_stats * frame_branch_ct , vp9_coeff_probs_model * new_coef_probs ) {
 vp9_coeff_probs_model * old_coef_probs = cpi -> common . fc . coef_probs [ tx_size ] ;
 const vp9_prob upd = DIFF_UPDATE_PROB ;
 const int entropy_nodes_update = UNCONSTRAINED_NODES ;
 int i , j , k , l , t ;
 switch ( cpi -> sf . use_fast_coef_updates ) {
 case TWO_LOOP : {
 int savings = 0 ;
 int update [ 2 ] = {
 0 , 0 }
 ;
 for ( i = 0 ;
 i < PLANE_TYPES ;
 ++ i ) {
 for ( j = 0 ;
 j < REF_TYPES ;
 ++ j ) {
 for ( k = 0 ;
 k < COEF_BANDS ;
 ++ k ) {
 for ( l = 0 ;
 l < BAND_COEFF_CONTEXTS ( k ) ;
 ++ l ) {
 for ( t = 0 ;
 t < entropy_nodes_update ;
 ++ t ) {
 vp9_prob newp = new_coef_probs [ i ] [ j ] [ k ] [ l ] [ t ] ;
 const vp9_prob oldp = old_coef_probs [ i ] [ j ] [ k ] [ l ] [ t ] ;
 int s ;
 int u = 0 ;
 if ( t == PIVOT_NODE ) s = vp9_prob_diff_update_savings_search_model ( frame_branch_ct [ i ] [ j ] [ k ] [ l ] [ 0 ] , old_coef_probs [ i ] [ j ] [ k ] [ l ] , & newp , upd ) ;
 else s = vp9_prob_diff_update_savings_search ( frame_branch_ct [ i ] [ j ] [ k ] [ l ] [ t ] , oldp , & newp , upd ) ;
 if ( s > 0 && newp != oldp ) u = 1 ;
 if ( u ) savings += s - ( int ) ( vp9_cost_zero ( upd ) ) ;
 else savings -= ( int ) ( vp9_cost_zero ( upd ) ) ;
 update [ u ] ++ ;
 }
 }
 }
 }
 }
 if ( update [ 1 ] == 0 || savings < 0 ) {
 vp9_write_bit ( bc , 0 ) ;
 return ;
 }
 vp9_write_bit ( bc , 1 ) ;
 for ( i = 0 ;
 i < PLANE_TYPES ;
 ++ i ) {
 for ( j = 0 ;
 j < REF_TYPES ;
 ++ j ) {
 for ( k = 0 ;
 k < COEF_BANDS ;
 ++ k ) {
 for ( l = 0 ;
 l < BAND_COEFF_CONTEXTS ( k ) ;
 ++ l ) {
 for ( t = 0 ;
 t < entropy_nodes_update ;
 ++ t ) {
 vp9_prob newp = new_coef_probs [ i ] [ j ] [ k ] [ l ] [ t ] ;
 vp9_prob * oldp = old_coef_probs [ i ] [ j ] [ k ] [ l ] + t ;
 const vp9_prob upd = DIFF_UPDATE_PROB ;
 int s ;
 int u = 0 ;
 if ( t == PIVOT_NODE ) s = vp9_prob_diff_update_savings_search_model ( frame_branch_ct [ i ] [ j ] [ k ] [ l ] [ 0 ] , old_coef_probs [ i ] [ j ] [ k ] [ l ] , & newp , upd ) ;
 else s = vp9_prob_diff_update_savings_search ( frame_branch_ct [ i ] [ j ] [ k ] [ l ] [ t ] , * oldp , & newp , upd ) ;
 if ( s > 0 && newp != * oldp ) u = 1 ;
 vp9_write ( bc , u , upd ) ;
 if ( u ) {
 vp9_write_prob_diff_update ( bc , newp , * oldp ) ;
 * oldp = newp ;
 }
 }
 }
 }
 }
 }
 return ;
 }
 case ONE_LOOP : case ONE_LOOP_REDUCED : {
 const int prev_coef_contexts_to_update = cpi -> sf . use_fast_coef_updates == ONE_LOOP_REDUCED ? COEFF_CONTEXTS >> 1 : COEFF_CONTEXTS ;
 const int coef_band_to_update = cpi -> sf . use_fast_coef_updates == ONE_LOOP_REDUCED ? COEF_BANDS >> 1 : COEF_BANDS ;
 int updates = 0 ;
 int noupdates_before_first = 0 ;
 for ( i = 0 ;
 i < PLANE_TYPES ;
 ++ i ) {
 for ( j = 0 ;
 j < REF_TYPES ;
 ++ j ) {
 for ( k = 0 ;
 k < COEF_BANDS ;
 ++ k ) {
 for ( l = 0 ;
 l < BAND_COEFF_CONTEXTS ( k ) ;
 ++ l ) {
 for ( t = 0 ;
 t < entropy_nodes_update ;
 ++ t ) {
 vp9_prob newp = new_coef_probs [ i ] [ j ] [ k ] [ l ] [ t ] ;
 vp9_prob * oldp = old_coef_probs [ i ] [ j ] [ k ] [ l ] + t ;
 int s ;
 int u = 0 ;
 if ( l >= prev_coef_contexts_to_update || k >= coef_band_to_update ) {
 u = 0 ;
 }
 else {
 if ( t == PIVOT_NODE ) s = vp9_prob_diff_update_savings_search_model ( frame_branch_ct [ i ] [ j ] [ k ] [ l ] [ 0 ] , old_coef_probs [ i ] [ j ] [ k ] [ l ] , & newp , upd ) ;
 else s = vp9_prob_diff_update_savings_search ( frame_branch_ct [ i ] [ j ] [ k ] [ l ] [ t ] , * oldp , & newp , upd ) ;
 if ( s > 0 && newp != * oldp ) u = 1 ;
 }
 updates += u ;
 if ( u == 0 && updates == 0 ) {
 noupdates_before_first ++ ;
 continue ;
 }
 if ( u == 1 && updates == 1 ) {
 int v ;
 vp9_write_bit ( bc , 1 ) ;
 for ( v = 0 ;
 v < noupdates_before_first ;
 ++ v ) vp9_write ( bc , 0 , upd ) ;
 }
 vp9_write ( bc , u , upd ) ;
 if ( u ) {
 vp9_write_prob_diff_update ( bc , newp , * oldp ) ;
 * oldp = newp ;
 }
 }
 }
 }
 }
 }
 if ( updates == 0 ) {
 vp9_write_bit ( bc , 0 ) ;
 }
 return ;
 }
 default : assert ( 0 ) ;
 }
 }

In the above code snippet, check for potential security vulnerabilities and answer with a single digit: 1 if Vulnerable, 0 if Non-vulnerable.

The node information of the code snippet is as follows:
Node 25769803781: (BLOCK) '{  AMRWBContext * ctx = avctx -> priv_da...'
Node 25769803782: (BLOCK) '{  av_log ( avctx , AV_LOG_ERROR , "get_...'
Node 25769803783: (BLOCK) '{  av_log ( avctx , AV_LOG_ERROR , "Inva...'
Node 25769803784: (BLOCK) '{  av_log ( avctx , AV_LOG_ERROR , "Fram...'
Node 25769803785: (BLOCK) '<empty>'
Node 25769803786: (BLOCK) '{  av_log_missing_feature ( avctx , "SID...'
Node 25769803787: (BLOCK) '{ decode_isf_indices_36b ( cf -> isp_id ...'
Node 25769803788: (BLOCK) '{ decode_isf_indices_46b ( cf -> isp_id ...'
Node 25769803789: (BLOCK) '{  ctx -> first_frame = 0 ;  memcpy ( ct...'
Node 25769803790: (BLOCK) '{  const AMRWBSubFrame * cur_subframe = ...'
Node 25769803791: (BLOCK) '{  ctx -> excitation [ i ] *= ctx -> pit...'
Node 25769803792: (BLOCK) '<empty>'
Node 30064771098: (CALL) 'ctx = avctx -> priv_data'
Node 30064771099: (CALL) 'avctx -> priv_data'
Node 30064771100: (CALL) 'frame = data'
Node 30064771101: (CALL) 'cf = & ctx -> frame'
Node 30064771102: (CALL) '& ctx -> frame'
Node 30064771103: (CALL) 'ctx -> frame'
Node 30064771104: (CALL) 'buf = avpkt -> data'
Node 30064771105: (CALL) 'avpkt -> data'
Node 30064771106: (CALL) 'buf_size = avpkt -> size'
Node 30064771107: (CALL) 'avpkt -> size'
Node 30064771108: (CALL) 'spare_vector [ AMRWB_SFR_SIZE ]'
Node 30064771109: (CALL) 'spare_vector [ AMRWB_SFR_SIZE ]'
Node 30064771110: (CALL) 'synth_exc [ AMRWB_SFR_SIZE ]'
Node 30064771111: (CALL) 'synth_exc [ AMRWB_SFR_SIZE ]'
Node 30064771112: (CALL) 'hb_exc [ AMRWB_SFR_SIZE_16k ]'
Node 30064771113: (CALL) 'hb_exc [ AMRWB_SFR_SIZE_16k ]'
Node 30064771114: (CALL) 'hb_samples [ AMRWB_SFR_SIZE_16k ]'
Node 30064771115: (CALL) 'hb_samples [ AMRWB_SFR_SIZE_16k ]'
Node 30064771116: (CALL) 'frame -> nb_samples = 4 * AMRWB_SFR_SIZE...'
Node 30064771117: (CALL) 'frame -> nb_samples'
Node 30064771118: (CALL) '4 * AMRWB_SFR_SIZE_16k'
Node 30064771119: (CALL) '( ret = ff_get_buffer ( avctx , frame ) ...'
Node 30064771120: (CALL) 'ret = ff_get_buffer ( avctx , frame )'
Node 30064771121: (CALL) 'ff_get_buffer ( avctx , frame )'
Node 30064771122: (CALL) 'av_log ( avctx , AV_LOG_ERROR , "get_buf...'
Node 30064771123: (CALL) 'buf_out = ( float * ) frame -> data [ 0 ...'
Node 30064771124: (CALL) '( float * ) frame -> data [ 0 ]'
Node 30064771125: (CALL) 'frame -> data [ 0 ]'
The edge information of the code snippet is as follows:
Edge: Node 25769803781 -> AST -> Node 30064771098
Edge: Node 25769803781 -> AST -> Node 30064771100
Edge: Node 25769803781 -> AST -> Node 30064771101
Edge: Node 25769803781 -> AST -> Node 30064771104
Edge: Node 25769803781 -> AST -> Node 30064771106
Edge: Node 25769803781 -> AST -> Node 30064771108
Edge: Node 25769803781 -> AST -> Node 30064771110
Edge: Node 25769803781 -> AST -> Node 30064771112
Edge: Node 25769803781 -> AST -> Node 30064771114
Edge: Node 25769803781 -> AST -> Node 30064771116

The following is an example, and it is .


Answer (0 or 1):
```

## 35. reveal/B1-shuf/43/reveal:validation:281

SHA-256: a0a01dabc29ffa05c417b3774e09dd02943ab8e97d003d90d0aacac1b083de1c

Nguồn: Runs-management/dry_run_validation_20261102/reveal/validation/B1-shuf/43/prompts.jsonl

```text
You are now an excellent programmer. You are conducting a function vulnerability detection task for C/C++ language.

bool statistic_proc_security_check ( VariableStatData * vardata , Oid func_oid ) {
 if ( vardata -> acl_ok ) return true ;
 if ( ! OidIsValid ( func_oid ) ) return false ;
 if ( get_func_leakproof ( func_oid ) ) return true ;
 ereport ( DEBUG2 , ( errmsg_internal ( "not using statistics because function \"%s\" is not leak-proof" , get_func_name ( func_oid ) ) ) ) ;
 return false ;
 }

In the above code snippet, check for potential security vulnerabilities and answer with a single digit: 1 if Vulnerable, 0 if Non-vulnerable.

The node information of the code snippet is as follows:
Node 25769803860: (BLOCK) '{  gs_memory_gc_status_t stat ;  gs_ref_...'
Node 30064771657: (CALL) 'stable = ( gs_ref_memory_t * ) mem -> st...'
Node 30064771658: (CALL) '( gs_ref_memory_t * ) mem -> stable_memo...'
Node 30064771659: (CALL) 'mem -> stable_memory'
Node 30064771660: (CALL) 'gs_memory_gc_status ( mem , & stat )'
Node 30064771661: (CALL) '& stat'
Node 30064771662: (CALL) 'stat . vm_threshold = val'
Node 30064771663: (CALL) 'stat . vm_threshold'
Node 30064771664: (CALL) 'gs_memory_set_gc_status ( mem , & stat )'
Node 30064771665: (CALL) '& stat'
Node 30064771666: (CALL) 'gs_memory_gc_status ( stable , & stat )'
Node 30064771667: (CALL) '& stat'
Node 30064771668: (CALL) 'stat . vm_threshold = val'
Node 30064771669: (CALL) 'stat . vm_threshold'
Node 30064771670: (CALL) 'gs_memory_set_gc_status ( stable , & sta...'
Node 30064771671: (CALL) '& stat'
Node 55834574905: (FIELD_IDENTIFIER) 'stable_memory'
Node 55834574906: (FIELD_IDENTIFIER) 'vm_threshold'
Node 55834574907: (FIELD_IDENTIFIER) 'vm_threshold'
Node 68719477332: (IDENTIFIER) 'stable'
Node 68719477333: (IDENTIFIER) 'mem'
Node 68719477334: (IDENTIFIER) 'mem'
Node 68719477335: (IDENTIFIER) 'stat'
Node 68719477336: (IDENTIFIER) 'stat'
Node 68719477337: (IDENTIFIER) 'val'
Node 68719477338: (IDENTIFIER) 'mem'
Node 68719477339: (IDENTIFIER) 'stat'
Node 68719477340: (IDENTIFIER) 'stable'
Node 68719477341: (IDENTIFIER) 'stat'
Node 68719477342: (IDENTIFIER) 'stat'
Node 68719477343: (IDENTIFIER) 'val'
Node 68719477344: (IDENTIFIER) 'stable'
Node 68719477345: (IDENTIFIER) 'stat'
Node 94489280614: (LOCAL) 'gs_memory_gc_status_t stat'
Node 94489280615: (LOCAL) 'gs_ref_memory_t * stable'
Node 107374182412: (METHOD) 'void gs_memory_set_vm_threshold ( gs_ref...'
Node 111669149710: (METHOD_PARAMETER_IN) 'gs_ref_memory_t * mem'
Node 111669149711: (METHOD_PARAMETER_IN) 'long val'
Node 115964117006: (METHOD_PARAMETER_OUT) 'gs_ref_memory_t * mem'
Node 115964117007: (METHOD_PARAMETER_OUT) 'long val'
The edge information of the code snippet is as follows:
Edge: Node 25769803860 -> AST -> Node 94489280614
Edge: Node 25769803860 -> AST -> Node 94489280615
Edge: Node 25769803860 -> AST -> Node 30064771657
Edge: Node 25769803860 -> AST -> Node 30064771660
Edge: Node 25769803860 -> AST -> Node 30064771662
Edge: Node 25769803860 -> AST -> Node 30064771664
Edge: Node 25769803860 -> AST -> Node 30064771666
Edge: Node 25769803860 -> AST -> Node 30064771668
Edge: Node 25769803860 -> AST -> Node 30064771670
Edge: Node 30064771657 -> ARGUMENT -> Node 68719477332
Edge: Node 30064771657 -> ARGUMENT -> Node 30064771658
Edge: Node 30064771657 -> AST -> Node 68719477332
Edge: Node 30064771657 -> AST -> Node 30064771658
Edge: Node 30064771657 -> CFG -> Node 68719477334
Edge: Node 30064771657 -> DOMINATE -> Node 68719477334
Edge: Node 30064771657 -> POST_DOMINATE -> Node 30064771658

The following is an example, and it is .


Answer (0 or 1):
```

## 36. reveal/B1-shuf/44/reveal:validation:940

SHA-256: e9c60d7f01c3c35916fae59d78e636c7bf7ee33866ff3f152a31f7654e9f9798

Nguồn: Runs-management/dry_run_validation_20261102/reveal/validation/B1-shuf/44/prompts.jsonl

```text
You are now an excellent programmer. You are conducting a function vulnerability detection task for C/C++ language.

static guint strcase_hash ( gconstpointer key ) {
 const char * p = ( const char * ) key ;
 guint h = * p ;
 char c ;
 if ( h ) {
 if ( h >= 'A' && h <= 'Z' ) h = h - 'A' + 'a' ;
 for ( p += 1 ;
 * p != '\0' ;
 p ++ ) {
 c = * p ;
 if ( c >= 'A' && c <= 'Z' ) c = c - 'A' + 'a' ;
 h = ( h << 5 ) - h + c ;
 }
 }
 return h ;
 }

In the above code snippet, check for potential security vulnerabilities and answer with a single digit: 1 if Vulnerable, 0 if Non-vulnerable.

The node information of the code snippet is as follows:
Node 25769803828: (BLOCK) '{  int update = 0 ;  cm -> base_qindex =...'
Node 25769803829: (BLOCK) '<empty>'
Node 30064771292: (CALL) 'update = 0'
Node 30064771293: (CALL) 'cm -> base_qindex = vp9_rb_read_literal ...'
Node 30064771294: (CALL) 'cm -> base_qindex'
Node 30064771295: (CALL) 'vp9_rb_read_literal ( rb , QINDEX_BITS )'
Node 30064771296: (CALL) 'update |= read_delta_q ( rb , & cm -> y_...'
Node 30064771297: (CALL) 'read_delta_q ( rb , & cm -> y_dc_delta_q...'
Node 30064771298: (CALL) '& cm -> y_dc_delta_q'
Node 30064771299: (CALL) 'cm -> y_dc_delta_q'
Node 30064771300: (CALL) 'update |= read_delta_q ( rb , & cm -> uv...'
Node 30064771301: (CALL) 'read_delta_q ( rb , & cm -> uv_dc_delta_...'
Node 30064771302: (CALL) '& cm -> uv_dc_delta_q'
Node 30064771303: (CALL) 'cm -> uv_dc_delta_q'
Node 30064771304: (CALL) 'update |= read_delta_q ( rb , & cm -> uv...'
Node 30064771305: (CALL) 'read_delta_q ( rb , & cm -> uv_ac_delta_...'
Node 30064771306: (CALL) '& cm -> uv_ac_delta_q'
Node 30064771307: (CALL) 'cm -> uv_ac_delta_q'
Node 30064771308: (CALL) 'update != 0'
Node 30064771309: (CALL) 'vp9_init_dequantizer ( cm )'
Node 30064771310: (CALL) 'xd -> lossless = cm -> base_qindex == 0 ...'
Node 30064771311: (CALL) 'xd -> lossless'
Node 30064771312: (CALL) 'cm -> base_qindex == 0 && cm -> y_dc_del...'
Node 30064771313: (CALL) 'cm -> base_qindex == 0 && cm -> y_dc_del...'
Node 30064771314: (CALL) 'cm -> base_qindex == 0 && cm -> y_dc_del...'
Node 30064771315: (CALL) 'cm -> base_qindex == 0'
Node 30064771316: (CALL) 'cm -> base_qindex'
Node 30064771317: (CALL) 'cm -> y_dc_delta_q == 0'
Node 30064771318: (CALL) 'cm -> y_dc_delta_q'
Node 30064771319: (CALL) 'cm -> uv_dc_delta_q == 0'
Node 30064771320: (CALL) 'cm -> uv_dc_delta_q'
Node 30064771321: (CALL) 'cm -> uv_ac_delta_q == 0'
Node 30064771322: (CALL) 'cm -> uv_ac_delta_q'
Node 47244640285: (CONTROL_STRUCTURE) 'if ( update ) vp9_init_dequantizer ( cm ...'
Node 55834574877: (FIELD_IDENTIFIER) 'base_qindex'
Node 55834574878: (FIELD_IDENTIFIER) 'y_dc_delta_q'
Node 55834574879: (FIELD_IDENTIFIER) 'uv_dc_delta_q'
Node 55834574880: (FIELD_IDENTIFIER) 'uv_ac_delta_q'
Node 55834574881: (FIELD_IDENTIFIER) 'lossless'
Node 55834574882: (FIELD_IDENTIFIER) 'base_qindex'
The edge information of the code snippet is as follows:
Edge: Node 25769803828 -> AST -> Node 30064771292
Edge: Node 25769803828 -> AST -> Node 30064771293
Edge: Node 25769803828 -> AST -> Node 30064771296
Edge: Node 25769803828 -> AST -> Node 30064771300
Edge: Node 25769803828 -> AST -> Node 30064771304
Edge: Node 25769803828 -> AST -> Node 47244640285
Edge: Node 25769803828 -> AST -> Node 30064771310
Edge: Node 25769803829 -> AST -> Node 30064771309
Edge: Node 30064771293 -> ARGUMENT -> Node 30064771294
Edge: Node 30064771293 -> ARGUMENT -> Node 30064771295
Edge: Node 30064771293 -> AST -> Node 30064771294
Edge: Node 30064771293 -> AST -> Node 30064771295

The following is an example, and it is .


Answer (0 or 1):
```

## 37. reveal/B2/42/reveal:validation:1159

SHA-256: 0cc939cda3423371d24052d3d356fa08d9518ee9b41a89c7535ed710079d0182

Nguồn: Runs-management/dry_run_validation_20261102/reveal/validation/B2/42/prompts.jsonl

```text
You are now an excellent programmer. You are conducting a function vulnerability detection task for C/C++ language.

void jpc_enc_destroy ( jpc_enc_t * enc ) {
 if ( enc -> curtile ) {
 jpc_enc_tile_destroy ( enc -> curtile ) ;
 }
 if ( enc -> cp ) {
 jpc_enc_cp_destroy ( enc -> cp ) ;
 }
 if ( enc -> cstate ) {
 jpc_cstate_destroy ( enc -> cstate ) ;
 }
 if ( enc -> tmpstream ) {
 jas_stream_close ( enc -> tmpstream ) ;
 }
 jas_free ( enc ) ;
 }

In the above code snippet, check for potential security vulnerabilities and answer with a single digit: 1 if Vulnerable, 0 if Non-vulnerable.

The node information of the code snippet is as follows:
Node 25769803805: (BLOCK) '{  if ( enc -> curtile ) {  jpc_enc_tile...'
Node 25769803806: (BLOCK) '{ jpc_enc_tile_destroy ( enc -> curtile ...'
Node 25769803807: (BLOCK) '{ jpc_enc_cp_destroy ( enc -> cp ) ; }'
Node 25769803808: (BLOCK) '{ jpc_cstate_destroy ( enc -> cstate ) ;...'
Node 25769803809: (BLOCK) '{ jas_stream_close ( enc -> tmpstream ) ...'
Node 30064771219: (CALL) 'enc -> curtile'
Node 30064771220: (CALL) 'jpc_enc_tile_destroy ( enc -> curtile )'
Node 30064771221: (CALL) 'enc -> curtile'
Node 30064771222: (CALL) 'enc -> cp'
Node 30064771223: (CALL) 'jpc_enc_cp_destroy ( enc -> cp )'
Node 30064771224: (CALL) 'enc -> cp'
Node 30064771225: (CALL) 'enc -> cstate'
Node 30064771226: (CALL) 'jpc_cstate_destroy ( enc -> cstate )'
Node 30064771227: (CALL) 'enc -> cstate'
Node 30064771228: (CALL) 'enc -> tmpstream'
Node 30064771229: (CALL) 'jas_stream_close ( enc -> tmpstream )'
Node 30064771230: (CALL) 'enc -> tmpstream'
Node 30064771231: (CALL) 'jas_free ( enc )'
Node 47244640269: (CONTROL_STRUCTURE) 'if ( enc -> curtile ) {  jpc_enc_tile_de...'
Node 47244640270: (CONTROL_STRUCTURE) 'if ( enc -> cp ) { jpc_enc_cp_destroy ( ...'
Node 47244640271: (CONTROL_STRUCTURE) 'if ( enc -> cstate ) { jpc_cstate_destro...'
Node 47244640272: (CONTROL_STRUCTURE) 'if ( enc -> tmpstream ) {  jas_stream_cl...'
Node 55834574896: (FIELD_IDENTIFIER) 'curtile'
Node 55834574897: (FIELD_IDENTIFIER) 'curtile'
Node 55834574898: (FIELD_IDENTIFIER) 'cp'
Node 55834574899: (FIELD_IDENTIFIER) 'cp'
Node 55834574900: (FIELD_IDENTIFIER) 'cstate'
Node 55834574901: (FIELD_IDENTIFIER) 'cstate'
Node 55834574902: (FIELD_IDENTIFIER) 'tmpstream'
Node 55834574903: (FIELD_IDENTIFIER) 'tmpstream'
Node 68719476862: (IDENTIFIER) 'enc'
Node 68719476863: (IDENTIFIER) 'enc'
Node 68719476864: (IDENTIFIER) 'enc'
Node 68719476865: (IDENTIFIER) 'enc'
Node 68719476866: (IDENTIFIER) 'enc'
Node 68719476867: (IDENTIFIER) 'enc'
Node 68719476868: (IDENTIFIER) 'enc'
Node 68719476869: (IDENTIFIER) 'enc'
Node 68719476870: (IDENTIFIER) 'enc'
Node 107374182417: (METHOD) 'void jpc_enc_destroy ( jpc_enc_t * enc )...'
The edge information of the code snippet is as follows:
Edge: Node 25769803805 -> AST -> Node 47244640269
Edge: Node 25769803805 -> AST -> Node 47244640270
Edge: Node 25769803805 -> AST -> Node 47244640271
Edge: Node 25769803805 -> AST -> Node 47244640272
Edge: Node 25769803805 -> AST -> Node 30064771231
Edge: Node 25769803806 -> AST -> Node 30064771220
Edge: Node 25769803807 -> AST -> Node 30064771223
Edge: Node 25769803808 -> AST -> Node 30064771226
Edge: Node 25769803809 -> AST -> Node 30064771229
Edge: Node 30064771219 -> ARGUMENT -> Node 68719476862
Edge: Node 30064771219 -> ARGUMENT -> Node 55834574896
Edge: Node 30064771219 -> AST -> Node 68719476862
Edge: Node 30064771219 -> AST -> Node 55834574896
Edge: Node 30064771219 -> CDG -> Node 30064771221

The following is an example, and it is Non-vulnerable.
void jpc_enc_cp_destroy ( jpc_enc_cp_t * cp ) {
 if ( cp -> ccps ) {
 if ( cp -> tcp . ilyrrates ) {
 jas_free ( cp -> tcp . ilyrrates ) ;
 }
 jas_free ( cp -> ccps ) ;
 }
 jas_free ( cp ) ;
 }

Answer (0 or 1):
```

## 38. reveal/B2-flip/42/reveal:validation:110

SHA-256: fe2853bde5fe0af7de4e74b3305a206adb2fef849a4e349aa97ae8bf8c918ba8

Nguồn: Runs-management/dry_run_validation_20261102/reveal/validation/B2-flip/42/prompts.jsonl

```text
You are now an excellent programmer. You are conducting a function vulnerability detection task for C/C++ language.

static Node * substitute_actual_srf_parameters_mutator ( Node * node , substitute_actual_srf_parameters_context * context ) {
 Node * result ;
 if ( node == NULL ) return NULL ;
 if ( IsA ( node , Query ) ) {
 context -> sublevels_up ++ ;
 result = ( Node * ) query_tree_mutator ( ( Query * ) node , substitute_actual_srf_parameters_mutator , ( void * ) context , 0 ) ;
 context -> sublevels_up -- ;
 return result ;
 }
 if ( IsA ( node , Param ) ) {
 Param * param = ( Param * ) node ;
 if ( param -> paramkind == PARAM_EXTERN ) {
 if ( param -> paramid <= 0 || param -> paramid > context -> nargs ) elog ( ERROR , "invalid paramid: %d" , param -> paramid ) ;
 result = copyObject ( list_nth ( context -> args , param -> paramid - 1 ) ) ;
 IncrementVarSublevelsUp ( result , context -> sublevels_up , 0 ) ;
 return result ;
 }
 }
 return expression_tree_mutator ( node , substitute_actual_srf_parameters_mutator , ( void * ) context ) ;
 }

In the above code snippet, check for potential security vulnerabilities and answer with a single digit: 1 if Vulnerable, 0 if Non-vulnerable.

The node information of the code snippet is as follows:
Node 25769803776: (BLOCK) '{  Node * result ;  if ( node == NULL ) ...'
Node 25769803777: (BLOCK) '<empty>'
Node 25769803778: (BLOCK) '{  context -> sublevels_up ++ ;  result ...'
Node 25769803779: (BLOCK) '{  Param * param = ( Param * ) node ;  i...'
Node 25769803780: (BLOCK) '{  if ( param -> paramid <= 0 || param -...'
Node 25769803781: (BLOCK) '<empty>'
Node 30064771072: (CALL) 'node == NULL'
Node 30064771073: (CALL) 'IsA ( node , Query )'
Node 30064771074: (CALL) 'context -> sublevels_up ++'
Node 30064771075: (CALL) 'context -> sublevels_up'
Node 30064771076: (CALL) 'result = ( Node * ) query_tree_mutator (...'
Node 30064771077: (CALL) '( Node * ) query_tree_mutator ( ( Query ...'
Node 30064771078: (CALL) 'query_tree_mutator ( ( Query * ) node , ...'
Node 30064771079: (CALL) '( Query * ) node'
Node 30064771080: (CALL) '( void * ) context'
Node 30064771081: (CALL) 'context -> sublevels_up --'
Node 30064771082: (CALL) 'context -> sublevels_up'
Node 30064771083: (CALL) 'IsA ( node , Param )'
Node 30064771084: (CALL) 'param = ( Param * ) node'
Node 30064771085: (CALL) '( Param * ) node'
Node 30064771086: (CALL) 'param -> paramkind == PARAM_EXTERN'
Node 30064771087: (CALL) 'param -> paramkind'
Node 30064771088: (CALL) 'param -> paramid <= 0 || param -> parami...'
Node 30064771089: (CALL) 'param -> paramid <= 0'
Node 30064771090: (CALL) 'param -> paramid'
Node 30064771091: (CALL) 'param -> paramid > context -> nargs'
Node 30064771092: (CALL) 'param -> paramid'
Node 30064771093: (CALL) 'context -> nargs'
Node 30064771094: (CALL) 'elog ( ERROR , "invalid paramid: %d" , p...'
Node 30064771095: (CALL) 'param -> paramid'
Node 30064771096: (CALL) 'result = copyObject ( list_nth ( context...'
Node 30064771097: (CALL) 'copyObject ( list_nth ( context -> args ...'
Node 30064771098: (CALL) 'list_nth ( context -> args , param -> pa...'
Node 30064771099: (CALL) 'context -> args'
Node 30064771100: (CALL) 'param -> paramid - 1'
Node 30064771101: (CALL) 'param -> paramid'
Node 30064771102: (CALL) 'IncrementVarSublevelsUp ( result , conte...'
Node 30064771103: (CALL) 'context -> sublevels_up'
Node 30064771104: (CALL) 'expression_tree_mutator ( node , substit...'
Node 30064771105: (CALL) '( void * ) context'
The edge information of the code snippet is as follows:
Edge: Node 25769803778 -> AST -> Node 30064771074
Edge: Node 25769803778 -> AST -> Node 30064771076
Edge: Node 25769803778 -> AST -> Node 30064771081
Edge: Node 25769803779 -> AST -> Node 30064771084
Edge: Node 25769803780 -> AST -> Node 30064771096
Edge: Node 25769803780 -> AST -> Node 30064771102
Edge: Node 25769803781 -> AST -> Node 30064771094
Edge: Node 30064771072 -> CDG -> Node 30064771073
Edge: Node 30064771073 -> CDG -> Node 30064771076
Edge: Node 30064771073 -> CDG -> Node 30064771077
Edge: Node 30064771073 -> CDG -> Node 30064771074
Edge: Node 30064771073 -> CDG -> Node 30064771075
Edge: Node 30064771073 -> CDG -> Node 30064771080

The following is an example, and it is Vulnerable.
static bool has_parallel_hazard_walker ( Node * node , has_parallel_hazard_arg * context ) {
 if ( node == NULL ) return false ;
 if ( check_functions_in_node ( node , has_parallel_hazard_checker , context ) ) return true ;
 if ( IsA ( node , CoerceToDomain ) ) {
 if ( ! context -> allow_restricted ) return true ;
 }
 else if ( IsA ( node , RestrictInfo ) ) {
 RestrictInfo * rinfo = ( RestrictInfo * ) node ;
 return has_parallel_hazard_walker ( ( Node * ) rinfo -> clause , context ) ;
 }
 else if ( IsA ( node , SubLink ) || IsA ( node , SubPlan ) || IsA ( node , AlternativeSubPlan ) ) {
 if ( ! context -> allow_restricted ) return true ;
 }
 else if ( IsA ( node , Param ) ) {
 if ( ! context -> allow_restricted ) return true ;
 }
 else if ( IsA ( node , Query ) ) {
 Query * query = ( Query * ) node ;
 if ( query -> rowMarks != NULL ) return true ;
 return query_tree_walker ( query , has_parallel_hazard_walker , context , 0 ) ;
 }
 return expression_tree_walker ( node , has_parallel_hazard_walker , context ) ;
 }

Answer (0 or 1):
```

## 39. reveal/B2-labelonly/42/reveal:validation:2242

SHA-256: e881f937d1bcda0d1555292fd0c9e2d4df040192dfc46dd5e20ebbac158b6763

Nguồn: Runs-management/dry_run_validation_20261102/reveal/validation/B2-labelonly/42/prompts.jsonl

```text
You are now an excellent programmer. You are conducting a function vulnerability detection task for C/C++ language.

zend_object_iterator * spl_filesystem_tree_get_iterator ( zend_class_entry * ce , zval * object , int by_ref TSRMLS_DC ) {
 spl_filesystem_iterator * iterator ;
 spl_filesystem_object * dir_object ;
 if ( by_ref ) {
 zend_error ( E_ERROR , "An iterator cannot be used with foreach by reference" ) ;
 }
 dir_object = ( spl_filesystem_object * ) zend_object_store_get_object ( object TSRMLS_CC ) ;
 iterator = spl_filesystem_object_to_iterator ( dir_object ) ;
 if ( iterator -> intern . data == NULL ) {
 iterator -> intern . data = object ;
 iterator -> intern . funcs = & spl_filesystem_tree_it_funcs ;
 }
 zval_add_ref ( & object ) ;
 return ( zend_object_iterator * ) iterator ;
 }

In the above code snippet, check for potential security vulnerabilities and answer with a single digit: 1 if Vulnerable, 0 if Non-vulnerable.

The node information of the code snippet is as follows:
Node 25769803809: (BLOCK) '{  spl_filesystem_iterator * iterator ; ...'
Node 25769803810: (BLOCK) '{  zend_error ( E_ERROR , "An iterator c...'
Node 25769803811: (BLOCK) '{  iterator -> intern . data = object ; ...'
Node 30064771173: (CALL) 'by_ref != 0'
Node 30064771174: (CALL) 'zend_error ( E_ERROR , "An iterator cann...'
Node 30064771175: (CALL) 'dir_object = ( spl_filesystem_object * )...'
Node 30064771176: (CALL) '( spl_filesystem_object * ) zend_object_...'
Node 30064771177: (CALL) 'zend_object_store_get_object ( object TS...'
Node 30064771178: (CALL) 'iterator = spl_filesystem_object_to_iter...'
Node 30064771179: (CALL) 'spl_filesystem_object_to_iterator ( dir_...'
Node 30064771180: (CALL) 'iterator -> intern . data == NULL'
Node 30064771181: (CALL) 'iterator -> intern . data'
Node 30064771182: (CALL) 'iterator -> intern'
Node 30064771183: (CALL) 'iterator -> intern . data = object'
Node 30064771184: (CALL) 'iterator -> intern . data'
Node 30064771185: (CALL) 'iterator -> intern'
Node 30064771186: (CALL) 'iterator -> intern . funcs = & spl_files...'
Node 30064771187: (CALL) 'iterator -> intern . funcs'
Node 30064771188: (CALL) 'iterator -> intern'
Node 30064771189: (CALL) '& spl_filesystem_tree_it_funcs'
Node 30064771190: (CALL) 'zval_add_ref ( & object )'
Node 30064771191: (CALL) '& object'
Node 30064771192: (CALL) '( zend_object_iterator * ) iterator'
Node 47244640271: (CONTROL_STRUCTURE) 'if ( by_ref ) {  zend_error ( E_ERROR , ...'
Node 47244640272: (CONTROL_STRUCTURE) 'if ( iterator -> intern . data == NULL )...'
Node 55834574852: (FIELD_IDENTIFIER) 'intern'
Node 55834574853: (FIELD_IDENTIFIER) 'data'
Node 55834574854: (FIELD_IDENTIFIER) 'intern'
Node 55834574855: (FIELD_IDENTIFIER) 'data'
Node 55834574856: (FIELD_IDENTIFIER) 'intern'
Node 55834574857: (FIELD_IDENTIFIER) 'funcs'
Node 68719476891: (IDENTIFIER) 'by_ref'
Node 68719476892: (IDENTIFIER) '<unknown> E_ERROR'
Node 68719476893: (IDENTIFIER) 'dir_object'
Node 68719476894: (IDENTIFIER) 'object'
Node 68719476895: (IDENTIFIER) 'iterator'
Node 68719476896: (IDENTIFIER) 'dir_object'
Node 68719476897: (IDENTIFIER) 'iterator'
Node 68719476898: (IDENTIFIER) '<unknown> NULL'
Node 68719476899: (IDENTIFIER) 'iterator'
The edge information of the code snippet is as follows:
Edge: Node 25769803809 -> AST -> Node 47244640271
Edge: Node 25769803809 -> AST -> Node 30064771175
Edge: Node 25769803809 -> AST -> Node 30064771178
Edge: Node 25769803809 -> AST -> Node 47244640272
Edge: Node 25769803809 -> AST -> Node 30064771190
Edge: Node 25769803810 -> AST -> Node 30064771174
Edge: Node 25769803811 -> AST -> Node 30064771183
Edge: Node 25769803811 -> AST -> Node 30064771186
Edge: Node 30064771173 -> ARGUMENT -> Node 68719476891
Edge: Node 30064771173 -> AST -> Node 68719476891
Edge: Node 30064771173 -> CDG -> Node 30064771174
Edge: Node 30064771173 -> CDG -> Node 68719476892
Edge: Node 30064771173 -> CFG -> Node 68719476892
Edge: Node 30064771173 -> CFG -> Node 68719476893
Edge: Node 30064771173 -> DOMINATE -> Node 68719476893

A function similar to the one above was labelled Non-vulnerable.

Answer (0 or 1):
```

## 40. reveal/B2-nolabel/42/reveal:validation:1338

SHA-256: 1bac7ba10e526010a2ea3d666da8609e40efcdc98af7439ecba42918820eeb02

Nguồn: Runs-management/dry_run_validation_20261102/reveal/validation/B2-nolabel/42/prompts.jsonl

```text
You are now an excellent programmer. You are conducting a function vulnerability detection task for C/C++ language.

static int selinux_sb_remount ( struct super_block * sb , void * data ) {
 int rc , i , * flags ;
 struct security_mnt_opts opts ;
 char * secdata , * * mount_options ;
 struct superblock_security_struct * sbsec = sb -> s_security ;
 if ( ! ( sbsec -> flags & SE_SBINITIALIZED ) ) return 0 ;
 if ( ! data ) return 0 ;
 if ( sb -> s_type -> fs_flags & FS_BINARY_MOUNTDATA ) return 0 ;
 security_init_mnt_opts ( & opts ) ;
 secdata = alloc_secdata ( ) ;
 if ( ! secdata ) return - ENOMEM ;
 rc = selinux_sb_copy_data ( data , secdata ) ;
 if ( rc ) goto out_free_secdata ;
 rc = selinux_parse_opts_str ( secdata , & opts ) ;
 if ( rc ) goto out_free_secdata ;
 mount_options = opts . mnt_opts ;
 flags = opts . mnt_opts_flags ;
 for ( i = 0 ;
 i < opts . num_mnt_opts ;
 i ++ ) {
 u32 sid ;
 if ( flags [ i ] == SBLABEL_MNT ) continue ;
 rc = security_context_str_to_sid ( mount_options [ i ] , & sid , GFP_KERNEL ) ;
 if ( rc ) {
 printk ( KERN_WARNING "SELinux: security_context_str_to_sid" "(%s) failed for (dev %s, type %s) errno=%d\n" , mount_options [ i ] , sb -> s_id , sb -> s_type -> name , rc ) ;
 goto out_free_opts ;
 }
 rc = - EINVAL ;
 switch ( flags [ i ] ) {
 case FSCONTEXT_MNT : if ( bad_option ( sbsec , FSCONTEXT_MNT , sbsec -> sid , sid ) ) goto out_bad_option ;
 break ;
 case CONTEXT_MNT : if ( bad_option ( sbsec , CONTEXT_MNT , sbsec -> mntpoint_sid , sid ) ) goto out_bad_option ;
 break ;
 case ROOTCONTEXT_MNT : {
 struct inode_security_struct * root_isec ;
 root_isec = backing_inode_security ( sb -> s_root ) ;
 if ( bad_option ( sbsec , ROOTCONTEXT_MNT , root_isec -> sid , sid ) ) goto out_bad_option ;
 break ;
 }
 case DEFCONTEXT_MNT : if ( bad_option ( sbsec , DEFCONTEXT_MNT , sbsec -> def_sid , sid ) ) goto out_bad_option ;
 break ;
 default : goto out_free_opts ;
 }
 }
 rc = 0 ;
 out_free_opts : security_free_mnt_opts ( & opts ) ;
 out_free_secdata : free_secdata ( secdata ) ;
 return rc ;
 out_bad_option : printk ( KERN_WARNING "SELinux: unable to change security options " "during remount (dev %s, type=%s)\n" , sb -> s_id , sb -> s_type -> name ) ;
 goto out_free_opts ;
 }

In the above code snippet, check for potential security vulnerabilities and answer with a single digit: 1 if Vulnerable, 0 if Non-vulnerable.

The node information of the code snippet is as follows:
Node 25769803826: (BLOCK) '{  int rc , i , * flags ;  struct securi...'
Node 25769803827: (BLOCK) '<empty>'
Node 25769803828: (BLOCK) '<empty>'
Node 25769803829: (BLOCK) '<empty>'
Node 25769803830: (BLOCK) '<empty>'
Node 25769803831: (BLOCK) '<empty>'
Node 25769803832: (BLOCK) '<empty>'
Node 25769803833: (BLOCK) '{  u32 sid ;  if ( flags [ i ] == SBLABE...'
Node 25769803834: (BLOCK) '<empty>'
Node 25769803835: (BLOCK) '{  printk ( KERN_WARNING "SELinux: secur...'
Node 25769803836: (BLOCK) '{  case FSCONTEXT_MNT : if ( bad_option ...'
Node 25769803837: (BLOCK) '<empty>'
Node 25769803838: (BLOCK) '<empty>'
Node 25769803839: (BLOCK) '{  struct inode_security_struct * root_i...'
Node 25769803840: (BLOCK) '<empty>'
Node 25769803841: (BLOCK) '<empty>'
Node 30064771337: (CALL) 'sbsec = sb -> s_security'
Node 30064771338: (CALL) 'sb -> s_security'
Node 30064771339: (CALL) '! ( sbsec -> flags & SE_SBINITIALIZED )'
Node 30064771340: (CALL) 'sbsec -> flags & SE_SBINITIALIZED'
Node 30064771341: (CALL) 'sbsec -> flags'
Node 30064771342: (CALL) '! data'
Node 30064771343: (CALL) 'sb -> s_type -> fs_flags & FS_BINARY_MOU...'
Node 30064771344: (CALL) 'sb -> s_type -> fs_flags'
Node 30064771345: (CALL) 'sb -> s_type'
Node 30064771346: (CALL) 'security_init_mnt_opts ( & opts )'
Node 30064771347: (CALL) '& opts'
Node 30064771348: (CALL) 'secdata = alloc_secdata ( )'
Node 30064771349: (CALL) 'alloc_secdata ( )'
Node 30064771350: (CALL) '! secdata'
Node 30064771351: (CALL) '- ENOMEM'
Node 30064771352: (CALL) 'rc = selinux_sb_copy_data ( data , secda...'
Node 30064771353: (CALL) 'selinux_sb_copy_data ( data , secdata )'
Node 30064771354: (CALL) 'rc != 0'
Node 30064771355: (CALL) 'rc = selinux_parse_opts_str ( secdata , ...'
Node 30064771356: (CALL) 'selinux_parse_opts_str ( secdata , & opt...'
Node 30064771357: (CALL) '& opts'
Node 30064771358: (CALL) 'rc != 0'
Node 30064771359: (CALL) 'mount_options = opts . mnt_opts'
Node 30064771360: (CALL) 'opts . mnt_opts'
The edge information of the code snippet is as follows:
Edge: Node 25769803826 -> AST -> Node 30064771337
Edge: Node 25769803826 -> AST -> Node 30064771346
Edge: Node 25769803826 -> AST -> Node 30064771348
Edge: Node 25769803826 -> AST -> Node 30064771352
Edge: Node 25769803826 -> AST -> Node 30064771355
Edge: Node 25769803826 -> AST -> Node 30064771359
Edge: Node 25769803836 -> AST -> Node 25769803839
Edge: Node 30064771337 -> ARGUMENT -> Node 30064771338
Edge: Node 30064771337 -> AST -> Node 30064771338
Edge: Node 30064771337 -> POST_DOMINATE -> Node 30064771338
Edge: Node 30064771338 -> CFG -> Node 30064771337
Edge: Node 30064771338 -> DOMINATE -> Node 30064771337
Edge: Node 30064771338 -> REACHING_DEF -> Node 30064771337
Edge: Node 30064771339 -> ARGUMENT -> Node 30064771340

The following is a related example.
static int selinux_get_mnt_opts ( const struct super_block * sb , struct security_mnt_opts * opts ) {
 int rc = 0 , i ;
 struct superblock_security_struct * sbsec = sb -> s_security ;
 char * context = NULL ;
 u32 len ;
 char tmp ;
 security_init_mnt_opts ( opts ) ;
 if ( ! ( sbsec -> flags & SE_SBINITIALIZED ) ) return - EINVAL ;
 if ( ! ss_initialized ) return - EINVAL ;
 BUILD_BUG_ON ( SE_MNTMASK >= ( 1 << NUM_SEL_MNT_OPTS ) ) ;
 tmp = sbsec -> flags & SE_MNTMASK ;
 for ( i = 0 ;
 i < NUM_SEL_MNT_OPTS ;
 i ++ ) {
 if ( tmp & 0x01 ) opts -> num_mnt_opts ++ ;
 tmp >>= 1 ;
 }
 if ( sbsec -> flags & SBLABEL_MNT ) opts -> num_mnt_opts ++ ;
 opts -> mnt_opts = kcalloc ( opts -> num_mnt_opts , sizeof ( char * ) , GFP_ATOMIC ) ;
 if ( ! opts -> mnt_opts ) {
 rc = - ENOMEM ;
 goto out_free ;
 }
 opts -> mnt_opts_flags = kcalloc ( opts -> num_mnt_opts , sizeof ( int ) , GFP_ATOMIC ) ;
 if ( ! opts -> mnt_opts_flags ) {
 rc = - ENOMEM ;
 goto out_free ;
 }
 i = 0 ;
 if ( sbsec -> flags & FSCONTEXT_MNT ) {
 rc = security_sid_to_context ( sbsec -> sid , & context , & len ) ;
 if ( rc ) goto out_free ;
 opts -> mnt_opts [ i ] = context ;
 opts -> mnt_opts_flags [ i ++ ] = FSCONTEXT_MNT ;
 }
 if ( sbsec -> flags & CONTEXT_MNT ) {
 rc = security_sid_to_context ( sbsec -> mntpoint_sid , & context , & len ) ;
 if ( rc ) goto out_free ;
 opts -> mnt_opts [ i ] = context ;
 opts -> mnt_opts_flags [ i ++ ] = CONTEXT_MNT ;
 }
 if ( sbsec -> flags & DEFCONTEXT_MNT ) {
 rc = security_sid_to_context ( sbsec -> def_sid , & context , & len ) ;
 if ( rc ) goto out_free ;
 opts -> mnt_opts [ i ] = context ;
 opts -> mnt_opts_flags [ i ++ ] = DEFCONTEXT_MNT ;
 }
 if ( sbsec -> flags & ROOTCONTEXT_MNT ) {
 struct dentry * root = sbsec -> sb -> s_root ;
 struct inode_security_struct * isec = backing_inode_security ( root ) ;
 rc = security_sid_to_context ( isec -> sid , & context , & len ) ;
 if ( rc ) goto out_free ;
 opts -> mnt_opts [ i ] = context ;
 opts -> mnt_opts_flags [ i ++ ] = ROOTCONTEXT_MNT ;
 }
 if ( sbsec -> flags & SBLABEL_MNT ) {
 opts -> mnt_opts [ i ] = NULL ;
 opts -> mnt_opts_flags [ i ++ ] = SBLABEL_MNT ;
 }
 BUG_ON ( i != opts -> num_mnt_opts ) ;
 return 0 ;
 out_free : security_free_mnt_opts ( opts ) ;
 return rc ;
 }

Answer (0 or 1):
```

## 41. reveal/B2-rand/42/reveal:validation:1857

SHA-256: 894f3ded2cfedcfa22f286398aaa5f2ec469617f6f082b5152a1549ab82b9f15

Nguồn: Runs-management/dry_run_validation_20261102/reveal/validation/B2-rand/42/prompts.jsonl

```text
You are now an excellent programmer. You are conducting a function vulnerability detection task for C/C++ language.

TSReturnCode TSUrlDestroy ( TSMBuffer , TSMLoc ) {
 return TS_SUCCESS ;
 }

In the above code snippet, check for potential security vulnerabilities and answer with a single digit: 1 if Vulnerable, 0 if Non-vulnerable.

The node information of the code snippet is as follows:
Node 25769803798: (BLOCK) '{ return TS_SUCCESS ; }'
Node 68719476828: (IDENTIFIER) '<unknown> TS_SUCCESS'
Node 94489280532: (LOCAL) '<unknown> TS_SUCCESS'
Node 107374182414: (METHOD) 'TSReturnCode TSUrlDestroy ( TSMBuffer , ...'
Node 111669149710: (METHOD_PARAMETER_IN) 'TSMBuffer'
Node 111669149711: (METHOD_PARAMETER_IN) 'TSMLoc'
Node 115964117006: (METHOD_PARAMETER_OUT) 'TSMBuffer'
Node 115964117007: (METHOD_PARAMETER_OUT) 'TSMLoc'
Node 124554051598: (METHOD_RETURN) 'RET'
Node 141733920780: (RETURN) 'return TS_SUCCESS ;'
The edge information of the code snippet is as follows:
Edge: Node 25769803798 -> AST -> Node 141733920780
Edge: Node 25769803798 -> AST -> Node 94489280532
Edge: Node 68719476828 -> CFG -> Node 141733920780
Edge: Node 68719476828 -> DOMINATE -> Node 141733920780
Edge: Node 68719476828 -> POST_DOMINATE -> Node 107374182414
Edge: Node 68719476828 -> REACHING_DEF -> Node 141733920780
Edge: Node 68719476828 -> REF -> Node 94489280532
Edge: Node 107374182414 -> AST -> Node 111669149710
Edge: Node 107374182414 -> AST -> Node 111669149711
Edge: Node 107374182414 -> AST -> Node 25769803798
Edge: Node 107374182414 -> AST -> Node 124554051598
Edge: Node 107374182414 -> AST -> Node 115964117006
Edge: Node 107374182414 -> AST -> Node 115964117007
Edge: Node 107374182414 -> CFG -> Node 68719476828
Edge: Node 107374182414 -> CONTAINS -> Node 25769803798
Edge: Node 107374182414 -> CONTAINS -> Node 141733920780
Edge: Node 107374182414 -> CONTAINS -> Node 68719476828
Edge: Node 107374182414 -> DOMINATE -> Node 68719476828
Edge: Node 107374182414 -> REACHING_DEF -> Node 111669149710
Edge: Node 107374182414 -> REACHING_DEF -> Node 68719476828
Edge: Node 107374182414 -> REACHING_DEF -> Node 111669149711
Edge: Node 107374182414 -> REACHING_DEF -> Node 141733920780
Edge: Node 111669149710 -> PARAMETER_LINK -> Node 115964117006
Edge: Node 111669149710 -> REACHING_DEF -> Node 115964117006
Edge: Node 111669149710 -> REACHING_DEF -> Node 115964117006
Edge: Node 111669149710 -> REACHING_DEF -> Node 124554051598
Edge: Node 111669149711 -> PARAMETER_LINK -> Node 115964117007
Edge: Node 111669149711 -> REACHING_DEF -> Node 115964117007
Edge: Node 111669149711 -> REACHING_DEF -> Node 115964117007
Edge: Node 111669149711 -> REACHING_DEF -> Node 124554051598
Edge: Node 124554051598 -> POST_DOMINATE -> Node 141733920780
Edge: Node 141733920780 -> ARGUMENT -> Node 68719476828
Edge: Node 141733920780 -> AST -> Node 68719476828
Edge: Node 141733920780 -> CFG -> Node 124554051598
Edge: Node 141733920780 -> DOMINATE -> Node 124554051598

The following is an example, and it is Non-vulnerable.
static void dumpTimestamp ( const char * msg ) {
 char buf [ 64 ] ;
 time_t now = time ( NULL ) ;
 if ( strftime ( buf , sizeof ( buf ) , PGDUMP_STRFTIME_FMT , localtime ( & now ) ) != 0 ) fprintf ( OPF , "-- %s %s\n\n" , msg , buf ) ;
 }

Answer (0 or 1):
```

## 42. reveal/B2-rand/43/reveal:validation:318

SHA-256: 4e75046e249dd5a7390733a46e08260278fe88bf077b2f7f48676f554781d69e

Nguồn: Runs-management/dry_run_validation_20261102/reveal/validation/B2-rand/43/prompts.jsonl

```text
You are now an excellent programmer. You are conducting a function vulnerability detection task for C/C++ language.

int TSHttpHdrLengthGet ( TSMBuffer bufp , TSMLoc obj ) {
 sdk_assert ( sdk_sanity_check_mbuffer ( bufp ) == TS_SUCCESS ) ;
 sdk_assert ( sdk_sanity_check_http_hdr_handle ( obj ) == TS_SUCCESS ) ;
 HTTPHdr h ;
 SET_HTTP_HDR ( h , bufp , obj ) ;
 ink_assert ( h . m_http -> m_type == HDR_HEAP_OBJ_HTTP_HEADER ) ;
 return h . length_get ( ) ;
 }

In the above code snippet, check for potential security vulnerabilities and answer with a single digit: 1 if Vulnerable, 0 if Non-vulnerable.

The node information of the code snippet is as follows:
Node 25769803839: (BLOCK) '{  sdk_assert ( sdk_sanity_check_mbuffer...'
Node 30064771435: (CALL) 'sdk_assert ( sdk_sanity_check_mbuffer ( ...'
Node 30064771436: (CALL) 'sdk_sanity_check_mbuffer ( bufp ) == TS_...'
Node 30064771437: (CALL) 'sdk_sanity_check_mbuffer ( bufp )'
Node 30064771438: (CALL) 'sdk_assert ( sdk_sanity_check_http_hdr_h...'
Node 30064771439: (CALL) 'sdk_sanity_check_http_hdr_handle ( obj )...'
Node 30064771440: (CALL) 'sdk_sanity_check_http_hdr_handle ( obj )'
Node 30064771441: (CALL) 'SET_HTTP_HDR ( h , bufp , obj )'
Node 30064771442: (CALL) 'ink_assert ( h . m_http -> m_type == HDR...'
Node 30064771443: (CALL) 'h . m_http -> m_type == HDR_HEAP_OBJ_HTT...'
Node 30064771444: (CALL) 'h . m_http -> m_type'
Node 30064771445: (CALL) 'h . m_http'
Node 30064771446: (CALL) 'h . length_get ( )'
Node 30064771447: (CALL) 'h . length_get'
Node 55834574898: (FIELD_IDENTIFIER) 'm_http'
Node 55834574899: (FIELD_IDENTIFIER) 'm_type'
Node 55834574900: (FIELD_IDENTIFIER) 'length_get'
Node 68719477067: (IDENTIFIER) 'bufp'
Node 68719477068: (IDENTIFIER) '<unknown> TS_SUCCESS'
Node 68719477069: (IDENTIFIER) 'obj'
Node 68719477070: (IDENTIFIER) '<unknown> TS_SUCCESS'
Node 68719477071: (IDENTIFIER) 'h'
Node 68719477072: (IDENTIFIER) 'bufp'
Node 68719477073: (IDENTIFIER) 'obj'
Node 68719477074: (IDENTIFIER) 'h'
Node 68719477075: (IDENTIFIER) '<unknown> HDR_HEAP_OBJ_HTTP_HEADER'
Node 68719477076: (IDENTIFIER) 'h'
Node 94489280614: (LOCAL) 'HTTPHdr h'
Node 94489280615: (LOCAL) '<unknown> HDR_HEAP_OBJ_HTTP_HEADER'
Node 94489280616: (LOCAL) '<unknown> TS_SUCCESS'
Node 107374182416: (METHOD) 'int TSHttpHdrLengthGet ( TSMBuffer bufp ...'
Node 111669149711: (METHOD_PARAMETER_IN) 'TSMBuffer bufp'
Node 111669149712: (METHOD_PARAMETER_IN) 'TSMLoc obj'
Node 115964117007: (METHOD_PARAMETER_OUT) 'TSMBuffer bufp'
Node 115964117008: (METHOD_PARAMETER_OUT) 'TSMLoc obj'
Node 124554051600: (METHOD_RETURN) 'RET'
Node 141733920788: (RETURN) 'return h . length_get ( ) ;'
The edge information of the code snippet is as follows:
Edge: Node 25769803839 -> AST -> Node 30064771435
Edge: Node 25769803839 -> AST -> Node 30064771438
Edge: Node 25769803839 -> AST -> Node 94489280614
Edge: Node 25769803839 -> AST -> Node 30064771441
Edge: Node 25769803839 -> AST -> Node 30064771442
Edge: Node 25769803839 -> AST -> Node 141733920788
Edge: Node 25769803839 -> AST -> Node 94489280615
Edge: Node 25769803839 -> AST -> Node 94489280616
Edge: Node 30064771435 -> ARGUMENT -> Node 30064771436
Edge: Node 30064771435 -> AST -> Node 30064771436
Edge: Node 30064771435 -> CFG -> Node 68719477069
Edge: Node 30064771435 -> DOMINATE -> Node 68719477069
Edge: Node 30064771435 -> POST_DOMINATE -> Node 30064771436
Edge: Node 30064771435 -> REACHING_DEF -> Node 124554051600
Edge: Node 30064771436 -> ARGUMENT -> Node 30064771437
Edge: Node 30064771436 -> ARGUMENT -> Node 68719477068

The following is an example, and it is Non-vulnerable.
void WriteData ( Archive * AHX , const void * data , size_t dLen ) {
 ArchiveHandle * AH = ( ArchiveHandle * ) AHX ;
 if ( ! AH -> currToc ) exit_horribly ( modulename , "internal error -- WriteData cannot be called outside the context of a DataDumper routine\n" ) ;
 ( * AH -> WriteDataPtr ) ( AH , data , dLen ) ;
 return ;
 }

Answer (0 or 1):
```

## 43. reveal/B2-rand/44/reveal:validation:436

SHA-256: e00a71574b07869dbe5f6487ce10e7321ea98e63e26c58a9ec50de1fdb8700d5

Nguồn: Runs-management/dry_run_validation_20261102/reveal/validation/B2-rand/44/prompts.jsonl

```text
You are now an excellent programmer. You are conducting a function vulnerability detection task for C/C++ language.

void dissect_q931_high_layer_compat_ie ( tvbuff_t * tvb , int offset , int len , proto_tree * tree ) {
 guint8 octet ;
 guint8 coding_standard ;
 guint8 pres_method ;
 guint8 characteristics ;
 if ( len == 0 ) return ;
 octet = tvb_get_guint8 ( tvb , offset ) ;
 coding_standard = octet & 0x60 ;
 pres_method = octet & 0x03 ;
 proto_tree_add_item ( tree , hf_q931_extension_ind , tvb , offset , 1 , ENC_BIG_ENDIAN ) ;
 proto_tree_add_uint ( tree , hf_q931_coding_standard , tvb , offset , 1 , octet ) ;
 proto_tree_add_uint ( tree , hf_q931_interpretation , tvb , offset , 1 , octet ) ;
 proto_tree_add_uint ( tree , hf_q931_pres_meth_prot_prof , tvb , offset , 1 , octet ) ;
 offset += 1 ;
 len -= 1 ;
 if ( ( coding_standard != Q931_ITU_STANDARDIZED_CODING ) || ( pres_method != Q931_HIGH_LAYER_PROTOCOL_PROFILE ) ) {
 proto_tree_add_item ( tree , hf_q931_high_layer_compat_data , tvb , offset , len , ENC_NA ) ;
 return ;
 }
 if ( len == 0 ) return ;
 octet = tvb_get_guint8 ( tvb , offset ) ;
 characteristics = octet & 0x7F ;
 proto_tree_add_item ( tree , hf_q931_extension_ind , tvb , offset , 1 , ENC_BIG_ENDIAN ) ;
 proto_tree_add_uint ( tree , hf_q931_high_layer_characteristics , tvb , offset , 1 , octet ) ;
 offset += 1 ;
 len -= 1 ;
 if ( ! ( octet & Q931_IE_VL_EXTENSION ) ) {
 if ( len == 0 ) return ;
 octet = tvb_get_guint8 ( tvb , offset ) ;
 if ( ( characteristics == Q931_AUDIOVISUAL ) || ( characteristics == 0x61 ) || ( characteristics == 0x62 ) || ( characteristics == 0x68 ) ) {
 proto_tree_add_item ( tree , hf_q931_extension_ind , tvb , offset , 1 , ENC_BIG_ENDIAN ) ;
 proto_tree_add_uint ( tree , hf_q931_extended_audiovisual_characteristics , tvb , offset , 1 , octet ) ;
 }
 else if ( ( characteristics == Q931_MANAGEMENT ) || ( characteristics == Q931_MAINTENANCE ) ) {
 proto_tree_add_item ( tree , hf_q931_extension_ind , tvb , offset , 1 , ENC_BIG_ENDIAN ) ;
 proto_tree_add_uint ( tree , hf_q931_extended_high_layer_characteristics , tvb , offset , 1 , octet ) ;
 }
 }
 }

In the above code snippet, check for potential security vulnerabilities and answer with a single digit: 1 if Vulnerable, 0 if Non-vulnerable.

The node information of the code snippet is as follows:
Node 25769803792: (BLOCK) '{  guint8 octet ;  guint8 coding_standar...'
Node 25769803793: (BLOCK) '<empty>'
Node 25769803794: (BLOCK) '{  proto_tree_add_item ( tree , hf_q931_...'
Node 25769803795: (BLOCK) '<empty>'
Node 25769803796: (BLOCK) '{  if ( len == 0 ) return ;  octet = tvb...'
Node 25769803797: (BLOCK) '<empty>'
Node 25769803798: (BLOCK) '{  proto_tree_add_item ( tree , hf_q931_...'
Node 25769803799: (BLOCK) '<empty>'
Node 25769803800: (BLOCK) '{  proto_tree_add_item ( tree , hf_q931_...'
Node 30064771260: (CALL) 'len == 0'
Node 30064771261: (CALL) 'octet = tvb_get_guint8 ( tvb , offset )'
Node 30064771262: (CALL) 'tvb_get_guint8 ( tvb , offset )'
Node 30064771263: (CALL) 'coding_standard = octet & 0x60'
Node 30064771264: (CALL) 'octet & 0x60'
Node 30064771265: (CALL) 'pres_method = octet & 0x03'
Node 30064771266: (CALL) 'octet & 0x03'
Node 30064771267: (CALL) 'proto_tree_add_item ( tree , hf_q931_ext...'
Node 30064771268: (CALL) 'proto_tree_add_uint ( tree , hf_q931_cod...'
Node 30064771269: (CALL) 'proto_tree_add_uint ( tree , hf_q931_int...'
Node 30064771270: (CALL) 'proto_tree_add_uint ( tree , hf_q931_pre...'
Node 30064771271: (CALL) 'offset += 1'
Node 30064771272: (CALL) 'len -= 1'
Node 30064771273: (CALL) '( coding_standard != Q931_ITU_STANDARDIZ...'
Node 30064771274: (CALL) 'coding_standard != Q931_ITU_STANDARDIZED...'
Node 30064771275: (CALL) 'pres_method != Q931_HIGH_LAYER_PROTOCOL_...'
Node 30064771276: (CALL) 'proto_tree_add_item ( tree , hf_q931_hig...'
Node 30064771277: (CALL) 'len == 0'
Node 30064771278: (CALL) 'octet = tvb_get_guint8 ( tvb , offset )'
Node 30064771279: (CALL) 'tvb_get_guint8 ( tvb , offset )'
Node 30064771280: (CALL) 'characteristics = octet & 0x7F'
Node 30064771281: (CALL) 'octet & 0x7F'
Node 30064771282: (CALL) 'proto_tree_add_item ( tree , hf_q931_ext...'
Node 30064771283: (CALL) 'proto_tree_add_uint ( tree , hf_q931_hig...'
Node 30064771284: (CALL) 'offset += 1'
Node 30064771285: (CALL) 'len -= 1'
Node 30064771286: (CALL) '! ( octet & Q931_IE_VL_EXTENSION )'
Node 30064771287: (CALL) 'octet & Q931_IE_VL_EXTENSION'
Node 30064771288: (CALL) 'len == 0'
Node 30064771289: (CALL) 'octet = tvb_get_guint8 ( tvb , offset )'
Node 30064771290: (CALL) 'tvb_get_guint8 ( tvb , offset )'
The edge information of the code snippet is as follows:
Edge: Node 25769803792 -> AST -> Node 30064771261
Edge: Node 25769803792 -> AST -> Node 30064771263
Edge: Node 25769803792 -> AST -> Node 30064771265
Edge: Node 25769803792 -> AST -> Node 30064771267
Edge: Node 25769803792 -> AST -> Node 30064771268
Edge: Node 25769803792 -> AST -> Node 30064771269
Edge: Node 25769803792 -> AST -> Node 30064771270
Edge: Node 25769803792 -> AST -> Node 30064771271
Edge: Node 25769803792 -> AST -> Node 30064771272
Edge: Node 25769803792 -> AST -> Node 30064771278

The following is an example, and it is Non-vulnerable.
static void encode_sb ( VP9_COMP * cpi , const TileInfo * const tile , TOKENEXTRA * * tp , int mi_row , int mi_col , int output_enabled , BLOCK_SIZE bsize , PC_TREE * pc_tree ) {
 VP9_COMMON * const cm = & cpi -> common ;
 MACROBLOCK * const x = & cpi -> mb ;
 MACROBLOCKD * const xd = & x -> e_mbd ;
 const int bsl = b_width_log2 ( bsize ) , hbs = ( 1 << bsl ) / 4 ;
 int ctx ;
 PARTITION_TYPE partition ;
 BLOCK_SIZE subsize = bsize ;
 if ( mi_row >= cm -> mi_rows || mi_col >= cm -> mi_cols ) return ;
 if ( bsize >= BLOCK_8X8 ) {
 ctx = partition_plane_context ( xd , mi_row , mi_col , bsize ) ;
 subsize = get_subsize ( bsize , pc_tree -> partitioning ) ;
 }
 else {
 ctx = 0 ;
 subsize = BLOCK_4X4 ;
 }
 partition = partition_lookup [ bsl ] [ subsize ] ;
 if ( output_enabled && bsize != BLOCK_4X4 ) cm -> counts . partition [ ctx ] [ partition ] ++ ;
 switch ( partition ) {
 case PARTITION_NONE : encode_b ( cpi , tile , tp , mi_row , mi_col , output_enabled , subsize , & pc_tree -> none ) ;
 break ;
 case PARTITION_VERT : encode_b ( cpi , tile , tp , mi_row , mi_col , output_enabled , subsize , & pc_tree -> vertical [ 0 ] ) ;
 if ( mi_col + hbs < cm -> mi_cols && bsize > BLOCK_8X8 ) {
 encode_b ( cpi , tile , tp , mi_row , mi_col + hbs , output_enabled , subsize , & pc_tree -> vertical [ 1 ] ) ;
 }
 break ;
 case PARTITION_HORZ : encode_b ( cpi , tile , tp , mi_row , mi_col , output_enabled , subsize , & pc_tree -> horizontal [ 0 ] ) ;
 if ( mi_row + hbs < cm -> mi_rows && bsize > BLOCK_8X8 ) {
 encode_b ( cpi , tile , tp , mi_row + hbs , mi_col , output_enabled , subsize , & pc_tree -> horizontal [ 1 ] ) ;
 }
 break ;
 case PARTITION_SPLIT : if ( bsize == BLOCK_8X8 ) {
 encode_b ( cpi , tile , tp , mi_row , mi_col , output_enabled , subsize , pc_tree -> leaf_split [ 0 ] ) ;
 }
 else {
 encode_sb ( cpi , tile , tp , mi_row , mi_col , output_enabled , subsize , pc_tree -> split [ 0 ] ) ;
 encode_sb ( cpi , tile , tp , mi_row , mi_col + hbs , output_enabled , subsize , pc_tree -> split [ 1 ] ) ;
 encode_sb ( cpi , tile , tp , mi_row + hbs , mi_col , output_enabled , subsize , pc_tree -> split [ 2 ] ) ;
 encode_sb ( cpi , tile , tp , mi_row + hbs , mi_col + hbs , output_enabled , subsize , pc_tree -> split [ 3 ] ) ;
 }
 break ;
 default : assert ( "Invalid partition type." ) ;
 break ;
 }
 if ( partition != PARTITION_SPLIT || bsize == BLOCK_8X8 ) update_partition_context ( xd , mi_row , mi_col , subsize , bsize ) ;
 }

Answer (0 or 1):
```

## 44. reveal/B2-rep/42/reveal:validation:458

SHA-256: 709bfc2a078d6f35352eb213bda0f3131ce0f1178b714cec13767b37f69253c5

Nguồn: Runs-management/dry_run_validation_20261102/reveal/validation/B2-rep/42/prompts.jsonl

```text
You are now an excellent programmer. You are conducting a function vulnerability detection task for C/C++ language.

static int proc_do_submiturb ( struct usb_dev_state * ps , struct usbdevfs_urb * uurb , struct usbdevfs_iso_packet_desc __user * iso_frame_desc , void __user * arg ) {
 struct usbdevfs_iso_packet_desc * isopkt = NULL ;
 struct usb_host_endpoint * ep ;
 struct async * as = NULL ;
 struct usb_ctrlrequest * dr = NULL ;
 unsigned int u , totlen , isofrmlen ;
 int i , ret , is_in , num_sgs = 0 , ifnum = - 1 ;
 int number_of_packets = 0 ;
 unsigned int stream_id = 0 ;
 void * buf ;
 if ( uurb -> flags & ~ ( USBDEVFS_URB_ISO_ASAP | USBDEVFS_URB_SHORT_NOT_OK | USBDEVFS_URB_BULK_CONTINUATION | USBDEVFS_URB_NO_FSBR | USBDEVFS_URB_ZERO_PACKET | USBDEVFS_URB_NO_INTERRUPT ) ) return - EINVAL ;
 if ( uurb -> buffer_length > 0 && ! uurb -> buffer ) return - EINVAL ;
 if ( ! ( uurb -> type == USBDEVFS_URB_TYPE_CONTROL && ( uurb -> endpoint & ~ USB_ENDPOINT_DIR_MASK ) == 0 ) ) {
 ifnum = findintfep ( ps -> dev , uurb -> endpoint ) ;
 if ( ifnum < 0 ) return ifnum ;
 ret = checkintf ( ps , ifnum ) ;
 if ( ret ) return ret ;
 }
 ep = ep_to_host_endpoint ( ps -> dev , uurb -> endpoint ) ;
 if ( ! ep ) return - ENOENT ;
 is_in = ( uurb -> endpoint & USB_ENDPOINT_DIR_MASK ) != 0 ;
 u = 0 ;
 switch ( uurb -> type ) {
 case USBDEVFS_URB_TYPE_CONTROL : if ( ! usb_endpoint_xfer_control ( & ep -> desc ) ) return - EINVAL ;
 if ( uurb -> buffer_length < 8 ) return - EINVAL ;
 dr = kmalloc ( sizeof ( struct usb_ctrlrequest ) , GFP_KERNEL ) ;
 if ( ! dr ) return - ENOMEM ;
 if ( copy_from_user ( dr , uurb -> buffer , 8 ) ) {
 ret = - EFAULT ;
 goto error ;
 }
 if ( uurb -> buffer_length < ( le16_to_cpup ( & dr -> wLength ) + 8 ) ) {
 ret = - EINVAL ;
 goto error ;
 }
 ret = check_ctrlrecip ( ps , dr -> bRequestType , dr -> bRequest , le16_to_cpup ( & dr -> wIndex ) ) ;
 if ( ret ) goto error ;
 uurb -> buffer_length = le16_to_cpup ( & dr -> wLength ) ;
 uurb -> buffer += 8 ;
 if ( ( dr -> bRequestType & USB_DIR_IN ) && uurb -> buffer_length ) {
 is_in = 1 ;
 uurb -> endpoint |= USB_DIR_IN ;
 }
 else {
 is_in = 0 ;
 uurb -> endpoint &= ~ USB_DIR_IN ;
 }
 snoop ( & ps -> dev -> dev , "control urb: bRequestType=%02x " "bRequest=%02x wValue=%04x " "wIndex=%04x wLength=%04x\n" , dr -> bRequestType , dr -> bRequest , __le16_to_cpup ( & dr -> wValue ) , __le16_to_cpup ( & dr -> wIndex ) , __le16_to_cpup ( & dr -> wLength ) ) ;
 u = sizeof ( struct usb_ctrlrequest ) ;
 break ;
 case USBDEVFS_URB_TYPE_BULK : switch ( usb_endpoint_type ( & ep -> desc ) ) {
 case USB_ENDPOINT_XFER_CONTROL : case USB_ENDPOINT_XFER_ISOC : return - EINVAL ;
 case USB_ENDPOINT_XFER_INT : uurb -> type = USBDEVFS_URB_TYPE_INTERRUPT ;
 goto interrupt_urb ;
 }
 num_sgs = DIV_ROUND_UP ( uurb -> buffer_length , USB_SG_SIZE ) ;
 if ( num_sgs == 1 || num_sgs > ps -> dev -> bus -> sg_tablesize ) num_sgs = 0 ;
 if ( ep -> streams ) stream_id = uurb -> stream_id ;
 break ;
 case USBDEVFS_URB_TYPE_INTERRUPT : if ( ! usb_endpoint_xfer_int ( & ep -> desc ) ) return - EINVAL ;
 interrupt_urb : break ;
 case USBDEVFS_URB_TYPE_ISO : if ( uurb -> number_of_packets < 1 || uurb -> number_of_packets > 128 ) return - EINVAL ;
 if ( ! usb_endpoint_xfer_isoc ( & ep -> desc ) ) return - EINVAL ;
 number_of_packets = uurb -> number_of_packets ;
 isofrmlen = sizeof ( struct usbdevfs_iso_packet_desc ) * number_of_packets ;
 isopkt = memdup_user ( iso_frame_desc , isofrmlen ) ;
 if ( IS_ERR ( isopkt ) ) {
 ret = PTR_ERR ( isopkt ) ;
 isopkt = NULL ;
 goto error ;
 }
 for ( totlen = u = 0 ;
 u < number_of_packets ;
 u ++ ) {
 if ( isopkt [ u ] . length > 49152 ) {
 ret = - EINVAL ;
 goto error ;
 }
 totlen += isopkt [ u ] . length ;
 }
 u *= sizeof ( struct usb_iso_packet_descriptor ) ;
 uurb -> buffer_length = totlen ;
 break ;
 default : return - EINVAL ;
 }
 if ( uurb -> buffer_length >= USBFS_XFER_MAX ) {
 ret = - EINVAL ;
 goto error ;
 }
 if ( uurb -> buffer_length > 0 && ! access_ok ( is_in ? VERIFY_WRITE : VERIFY_READ , uurb -> buffer , uurb -> buffer_length ) ) {
 ret = - EFAULT ;
 goto error ;
 }
 as = alloc_async ( number_of_packets ) ;
 if ( ! as ) {
 ret = - ENOMEM ;
 goto error ;
 }
 as -> usbm = find_memory_area ( ps , uurb ) ;
 if ( IS_ERR ( as -> usbm ) ) {
 ret = PTR_ERR ( as -> usbm ) ;
 as -> usbm = NULL ;
 goto error ;
 }
 if ( as -> usbm ) num_sgs = 0 ;
 u += sizeof ( struct async ) + sizeof ( struct urb ) + uurb -> buffer_length + num_sgs * sizeof ( struct scatterlist ) ;
 ret = usbfs_increase_memory_usage ( u ) ;
 if ( ret ) goto error ;
 as -> mem_usage = u ;
 if ( num_sgs ) {
 as -> urb -> sg = kmalloc ( num_sgs * sizeof ( struct scatterlist ) , GFP_KERNEL ) ;
 if ( ! as -> urb -> sg ) {
 ret = - ENOMEM ;
 goto error ;
 }
 as -> urb -> num_sgs = num_sgs ;
 sg_init_table ( as -> urb -> sg , as -> urb -> num_sgs ) ;
 totlen = uurb -> buffer_length ;
 for ( i = 0 ;
 i < as -> urb -> num_sgs ;
 i ++ ) {
 u = ( totlen > USB_SG_SIZE ) ? USB_SG_SIZE : totlen ;
 buf = kmalloc ( u , GFP_KERNEL ) ;
 if ( ! buf ) {
 ret = - ENOMEM ;
 goto error ;
 }
 sg_set_buf ( & as -> urb -> sg [ i ] , buf , u ) ;
 if ( ! is_in ) {
 if ( copy_from_user ( buf , uurb -> buffer , u ) ) {
 ret = - EFAULT ;
 goto error ;
 }
 uurb -> buffer += u ;
 }
 totlen -= u ;
 }
 }
 else if ( uurb -> buffer_length > 0 ) {
 if ( as -> usbm ) {
 unsigned long uurb_start = ( unsigned long ) uurb -> buffer ;
 as -> urb -> transfer_buffer = as -> usbm -> mem + ( uurb_start - as -> usbm -> vm_start ) ;
 }
 else {
 as -> urb -> transfer_buffer = kmalloc ( uurb -> buffer_length , GFP_KERNEL ) ;
 if ( ! as -> urb -> transfer_buffer ) {
 ret = - ENOMEM ;
 goto error ;
 }
 if ( ! is_in ) {
 if ( copy_from_user ( as -> urb -> transfer_buffer , uurb -> buffer , uurb -> buffer_length ) ) {
 ret = - EFAULT ;
 goto error ;
 }
 }
 else if ( uurb -> type == USBDEVFS_URB_TYPE_ISO ) {
 memset ( as -> urb -> transfer_buffer , 0 , uurb -> buffer_length ) ;
 }
 }
 }
 as -> urb -> dev = ps -> dev ;
 as -> urb -> pipe = ( uurb -> type << 30 ) | __create_pipe ( ps -> dev , uurb -> endpoint & 0xf ) | ( uurb -> endpoint & USB_DIR_IN ) ;
 u = ( is_in ? URB_DIR_IN : URB_DIR_OUT ) ;
 if ( uurb -> flags & USBDEVFS_URB_ISO_ASAP ) u |= URB_ISO_ASAP ;
 if ( uurb -> flags & USBDEVFS_URB_SHORT_NOT_OK && is_in ) u |= URB_SHORT_NOT_OK ;
 if ( uurb -> flags & USBDEVFS_URB_NO_FSBR ) u |= URB_NO_FSBR ;
 if ( uurb -> flags & USBDEVFS_URB_ZERO_PACKET ) u |= URB_ZERO_PACKET ;
 if ( uurb -> flags & USBDEVFS_URB_NO_INTERRUPT ) u |= URB_NO_INTERRUPT ;
 as -> urb -> transfer_flags = u ;
 as -> urb -> transfer_buffer_length = uurb -> buffer_length ;
 as -> urb -> setup_packet = ( unsigned char * ) dr ;
 dr = NULL ;
 as -> urb -> start_frame = uurb -> start_frame ;
 as -> urb -> number_of_packets = number_of_packets ;
 as -> urb -> stream_id = stream_id ;
 if ( uurb -> type == USBDEVFS_URB_TYPE_ISO || ps -> dev -> speed == USB_SPEED_HIGH ) as -> urb -> interval = 1 << min ( 15 , ep -> desc . bInterval - 1 ) ;
 else as -> urb -> interval = ep -> desc . bInterval ;
 as -> urb -> context = as ;
 as -> urb -> complete = async_completed ;
 for ( totlen = u = 0 ;
 u < number_of_packets ;
 u ++ ) {
 as -> urb -> iso_frame_desc [ u ] . offset = totlen ;
 as -> urb -> iso_frame_desc [ u ] . length = isopkt [ u ] . length ;
 totlen += isopkt [ u ] . length ;
 }
 kfree ( isopkt ) ;
 isopkt = NULL ;
 as -> ps = ps ;
 as -> userurb = arg ;
 if ( as -> usbm ) {
 unsigned long uurb_start = ( unsigned long ) uurb -> buffer ;
 as -> urb -> transfer_flags |= URB_NO_TRANSFER_DMA_MAP ;
 as -> urb -> transfer_dma = as -> usbm -> dma_handle + ( uurb_start - as -> usbm -> vm_start ) ;
 }
 else if ( is_in && uurb -> buffer_length > 0 ) as -> userbuffer = uurb -> buffer ;
 as -> signr = uurb -> signr ;
 as -> ifnum = ifnum ;
 as -> pid = get_pid ( task_pid ( current ) ) ;
 as -> cred = get_current_cred ( ) ;
 security_task_getsecid ( current , & as -> secid ) ;
 snoop_urb ( ps -> dev , as -> userurb , as -> urb -> pipe , as -> urb -> transfer_buffer_length , 0 , SUBMIT , NULL , 0 ) ;
 if ( ! is_in ) snoop_urb_data ( as -> urb , as -> urb -> transfer_buffer_length ) ;
 async_newpending ( as ) ;
 if ( usb_endpoint_xfer_bulk ( & ep -> desc ) ) {
 spin_lock_irq ( & ps -> lock ) ;
 as -> bulk_addr = usb_endpoint_num ( & ep -> desc ) | ( ( ep -> desc . bEndpointAddress & USB_ENDPOINT_DIR_MASK ) >> 3 ) ;
 if ( uurb -> flags & USBDEVFS_URB_BULK_CONTINUATION ) as -> bulk_status = AS_CONTINUATION ;
 else ps -> disabled_bulk_eps &= ~ ( 1 << as -> bulk_addr ) ;
 if ( ps -> disabled_bulk_eps & ( 1 << as -> bulk_addr ) ) ret = - EREMOTEIO ;
 else ret = usb_submit_urb ( as -> urb , GFP_ATOMIC ) ;
 spin_unlock_irq ( & ps -> lock ) ;
 }
 else {
 ret = usb_submit_urb ( as -> urb , GFP_KERNEL ) ;
 }
 if ( ret ) {
 dev_printk ( KERN_DEBUG , & ps -> dev -> dev , "usbfs: usb_submit_urb returned %d\n" , ret ) ;
 snoop_urb ( ps -> dev , as -> userurb , as -> urb -> pipe , 0 , ret , COMPLETE , NULL , 0 ) ;
 async_removepending ( as ) ;
 goto error ;
 }
 return 0 ;
 error : if ( as && as -> usbm ) dec_usb_memory_use_count ( as -> usbm , & as -> usbm -> urb_use_count ) ;
 kfree ( isopkt ) ;
 kfree ( dr ) ;
 if ( as ) free_async ( as ) ;
 return ret ;
 }

In the above code snippet, check for potential security vulnerabilities and answer with a single digit: 1 if Vulnerable, 0 if Non-vulnerable.

The node information of the code snippet is as follows:
Node 25769803778: (BLOCK) '{  struct usbdevfs_iso_packet_desc * iso...'
Node 25769803779: (BLOCK) '<empty>'
Node 25769803780: (BLOCK) '<empty>'
Node 25769803781: (BLOCK) '{  ifnum = findintfep ( ps -> dev , uurb...'
Node 25769803782: (BLOCK) '<empty>'
Node 25769803783: (BLOCK) '<empty>'
Node 25769803784: (BLOCK) '<empty>'
Node 25769803785: (BLOCK) '{  case USBDEVFS_URB_TYPE_CONTROL : if (...'
Node 25769803786: (BLOCK) '<empty>'
Node 25769803787: (BLOCK) '<empty>'
Node 25769803788: (BLOCK) '<empty>'
Node 25769803789: (BLOCK) '{ ret = - EFAULT ; goto error ; }'
Node 25769803790: (BLOCK) '{ ret = - EINVAL ; goto error ; }'
Node 25769803791: (BLOCK) '<empty>'
Node 25769803792: (BLOCK) '{ is_in = 1 ; uurb -> endpoint |= USB_DI...'
Node 25769803793: (BLOCK) '{ is_in = 0 ; uurb -> endpoint &= ~ USB_...'
Node 25769803794: (BLOCK) '{  case USB_ENDPOINT_XFER_CONTROL : case...'
Node 25769803795: (BLOCK) '<empty>'
Node 25769803796: (BLOCK) '<empty>'
Node 25769803797: (BLOCK) '<empty>'
Node 25769803798: (BLOCK) '<empty>'
Node 25769803799: (BLOCK) '<empty>'
Node 25769803800: (BLOCK) '{ ret = PTR_ERR ( isopkt ) ; isopkt = NU...'
Node 25769803801: (BLOCK) '{  if ( isopkt [ u ] . length > 49152 ) ...'
Node 25769803802: (BLOCK) '{ ret = - EINVAL ; goto error ; }'
Node 25769803803: (BLOCK) '{ ret = - EINVAL ; goto error ; }'
Node 25769803804: (BLOCK) '{ ret = - EFAULT ; goto error ; }'
Node 25769803805: (BLOCK) '{ ret = - ENOMEM ; goto error ; }'
Node 25769803806: (BLOCK) '{ ret = PTR_ERR ( as -> usbm ) ; as -> u...'
Node 25769803807: (BLOCK) '<empty>'
Node 25769803808: (BLOCK) '<empty>'
Node 25769803809: (BLOCK) '{  as -> urb -> sg = kmalloc ( num_sgs *...'
Node 25769803810: (BLOCK) '{ ret = - ENOMEM ; goto error ; }'
Node 25769803811: (BLOCK) '{  u = ( totlen > USB_SG_SIZE ) ? USB_SG...'
Node 25769803812: (BLOCK) '{ ret = - ENOMEM ; goto error ; }'
Node 25769803813: (BLOCK) '{  if ( copy_from_user ( buf , uurb -> b...'
Node 25769803814: (BLOCK) '{ ret = - EFAULT ; goto error ; }'
Node 25769803815: (BLOCK) '<empty>'
Node 25769803816: (BLOCK) '{  if ( as -> usbm ) {  unsigned long uu...'
Node 25769803817: (BLOCK) '{  unsigned long uurb_start = ( unsigned...'
The edge information of the code snippet is as follows:
[No Edge Information Available]

The following is an example, and it is Non-vulnerable.
static int processcompl ( struct async * as , void __user * __user * arg ) {
 struct urb * urb = as -> urb ;
 struct usbdevfs_urb __user * userurb = as -> userurb ;
 void __user * addr = as -> userurb ;
 unsigned int i ;
 if ( as -> userbuffer && urb -> actual_length ) {
 if ( copy_urb_data_to_user ( as -> userbuffer , urb ) ) goto err_out ;
 }
 if ( put_user ( as -> status , & userurb -> status ) ) goto err_out ;
 if ( put_user ( urb -> actual_length , & userurb -> actual_length ) ) goto err_out ;
 if ( put_user ( urb -> error_count , & userurb -> error_count ) ) goto err_out ;
 if ( usb_endpoint_xfer_isoc ( & urb -> ep -> desc ) ) {
 for ( i = 0 ;
 i < urb -> number_of_packets ;
 i ++ ) {
 if ( put_user ( urb -> iso_frame_desc [ i ] . actual_length , & userurb -> iso_frame_desc [ i ] . actual_length ) ) goto err_out ;
 if ( put_user ( urb -> iso_frame_desc [ i ] . status , & userurb -> iso_frame_desc [ i ] . status ) ) goto err_out ;
 }
 }
 if ( put_user ( addr , ( void __user * __user * ) arg ) ) return - EFAULT ;
 return 0 ;
 err_out : return - EFAULT ;
 }

Answer (0 or 1):
```

## 45. reveal/B1-shuf/43/reveal:validation:168

SHA-256: fbe6e821d06e385c2681372ebd122eccb5cc42fa3d29cc6bb620fcbab5a1ae45

Nguồn: Runs-management/dry_run_validation_20261102/reveal/validation/B1-shuf/43/prompts.jsonl

```text
You are now an excellent programmer. You are conducting a function vulnerability detection task for C/C++ language.

int vp9_denoiser_alloc ( VP9_DENOISER * denoiser , int width , int height , int ssx , int ssy , # if CONFIG_VP9_HIGHBITDEPTH int use_highbitdepth , # endif int border ) {
 int i , fail ;
 assert ( denoiser != NULL ) ;
 for ( i = 0 ;
 i < MAX_REF_FRAMES ;
 ++ i ) {
 fail = vp9_alloc_frame_buffer ( & denoiser -> running_avg_y [ i ] , width , height , ssx , ssy , # if CONFIG_VP9_HIGHBITDEPTH use_highbitdepth , # endif border ) ;
 if ( fail ) {
 vp9_denoiser_free ( denoiser ) ;
 return 1 ;
 }
 # ifdef OUTPUT_YUV_DENOISED make_grayscale ( & denoiser -> running_avg_y [ i ] ) ;
 # endif }
 fail = vp9_alloc_frame_buffer ( & denoiser -> mc_running_avg_y , width , height , ssx , ssy , # if CONFIG_VP9_HIGHBITDEPTH use_highbitdepth , # endif border ) ;
 if ( fail ) {
 vp9_denoiser_free ( denoiser ) ;
 return 1 ;
 }
 # ifdef OUTPUT_YUV_DENOISED make_grayscale ( & denoiser -> running_avg_y [ i ] ) ;
 # endif denoiser -> increase_denoising = 0 ;
 return 0 ;
 }

In the above code snippet, check for potential security vulnerabilities and answer with a single digit: 1 if Vulnerable, 0 if Non-vulnerable.

The node information of the code snippet is as follows:

The edge information of the code snippet is as follows:


The following is an example, and it is .


Answer (0 or 1):
```

## 46. reveal/B0/42/reveal:validation:1452

SHA-256: 7fd3ae859084a38b34b4f2cc4407095275a68b31576d17418d5c754f20b60bd8

Nguồn: Runs-management/dry_run_validation_20261102/reveal/validation/B0/42/prompts.jsonl

```text
You are now an excellent programmer. You are conducting a function vulnerability detection task for C/C++ language.

static void one_remote_ref ( const char * refname ) {
 struct ref * ref ;
 struct object * obj ;
 ref = alloc_ref ( refname ) ;
 if ( http_fetch_ref ( repo -> url , ref ) != 0 ) {
 fprintf ( stderr , "Unable to fetch ref %s from %s\n" , refname , repo -> url ) ;
 free ( ref ) ;
 return ;
 }
 if ( repo -> can_update_info_refs && ! has_object_file ( & ref -> old_oid ) ) {
 obj = lookup_unknown_object ( ref -> old_oid . hash ) ;
 if ( obj ) {
 fprintf ( stderr , " fetch %s for %s\n" , oid_to_hex ( & ref -> old_oid ) , refname ) ;
 add_fetch_request ( obj ) ;
 }
 }
 ref -> next = remote_refs ;
 remote_refs = ref ;
 }

In the above code snippet, check for potential security vulnerabilities and answer with a single digit: 1 if Vulnerable, 0 if Non-vulnerable.

The node information of the code snippet is as follows:

The edge information of the code snippet is as follows:


The following is an example, and it is .


Answer (0 or 1):
```

## 47. reveal/B0/42/reveal:validation:2152

SHA-256: d0715bc4b75cb5bab629fc1d054e4e24c4038b284845451686c65bddc3204197

Nguồn: Runs-management/dry_run_validation_20261102/reveal/validation/B0/42/prompts.jsonl

```text
You are now an excellent programmer. You are conducting a function vulnerability detection task for C/C++ language.

static int dissect_pvfs_string ( tvbuff_t * tvb , proto_tree * tree , int hfindex , int offset , const char * * string_buffer_ret ) {
 return dissect_pvfs_opaque_data ( tvb , offset , tree , NULL , hfindex , FALSE , 0 , TRUE , string_buffer_ret ) ;
 }

In the above code snippet, check for potential security vulnerabilities and answer with a single digit: 1 if Vulnerable, 0 if Non-vulnerable.

The node information of the code snippet is as follows:

The edge information of the code snippet is as follows:


The following is an example, and it is .


Answer (0 or 1):
```

## 48. reveal/B0/42/reveal:validation:300

SHA-256: 382b3b156ef72023784f517bc60bdb3706f5f4d36cb56126b0f662c9ab208311

Nguồn: Runs-management/dry_run_validation_20261102/reveal/validation/B0/42/prompts.jsonl

```text
You are now an excellent programmer. You are conducting a function vulnerability detection task for C/C++ language.

CharList * pkg_appendUniqueDirToList ( CharList * l , CharList * * end , const char * strAlias ) {
 char aBuf [ 1024 ] ;
 char * rPtr ;
 rPtr = uprv_strrchr ( strAlias , U_FILE_SEP_CHAR ) ;
 # if ( U_FILE_SEP_CHAR != U_FILE_ALT_SEP_CHAR ) {
 char * aPtr = uprv_strrchr ( strAlias , U_FILE_ALT_SEP_CHAR ) ;
 if ( ! rPtr || ( aPtr && ( aPtr > rPtr ) ) ) {
 rPtr = aPtr ;
 }
 }
 # endif if ( ! rPtr ) {
 return l ;
 }
 if ( ( rPtr - strAlias ) >= UPRV_LENGTHOF ( aBuf ) ) {
 fprintf ( stderr , "## ERR: Path too long [%d chars]: %s\n" , ( int ) sizeof ( aBuf ) , strAlias ) ;
 return l ;
 }
 strncpy ( aBuf , strAlias , ( rPtr - strAlias ) ) ;
 aBuf [ rPtr - strAlias ] = 0 ;
 convertToNativePathSeparators ( aBuf ) ;
 if ( ! pkg_listContains ( l , aBuf ) ) {
 return pkg_appendToList ( l , end , uprv_strdup ( aBuf ) ) ;
 }
 else {
 return l ;
 }
 }

In the above code snippet, check for potential security vulnerabilities and answer with a single digit: 1 if Vulnerable, 0 if Non-vulnerable.

The node information of the code snippet is as follows:

The edge information of the code snippet is as follows:


The following is an example, and it is .


Answer (0 or 1):
```

## 49. reveal/B0/42/reveal:validation:1432

SHA-256: 313375f0c9b614eb3767bb6848a3883ae2c12aa755181227a230bc224ef50eed

Nguồn: Runs-management/dry_run_validation_20261102/reveal/validation/B0/42/prompts.jsonl

```text
You are now an excellent programmer. You are conducting a function vulnerability detection task for C/C++ language.

int ReconnectToServer ( ArchiveHandle * AH , const char * dbname , const char * username ) {
 PGconn * newConn ;
 const char * newdbname ;
 const char * newusername ;
 if ( ! dbname ) newdbname = PQdb ( AH -> connection ) ;
 else newdbname = dbname ;
 if ( ! username ) newusername = PQuser ( AH -> connection ) ;
 else newusername = username ;
 if ( strcmp ( newdbname , PQdb ( AH -> connection ) ) == 0 && strcmp ( newusername , PQuser ( AH -> connection ) ) == 0 ) return 1 ;
 newConn = _connectDB ( AH , newdbname , newusername ) ;
 set_archive_cancel_info ( AH , newConn ) ;
 PQfinish ( AH -> connection ) ;
 AH -> connection = newConn ;
 return 1 ;
 }

In the above code snippet, check for potential security vulnerabilities and answer with a single digit: 1 if Vulnerable, 0 if Non-vulnerable.

The node information of the code snippet is as follows:

The edge information of the code snippet is as follows:


The following is an example, and it is .


Answer (0 or 1):
```

## 50. reveal/B2-rep/42/reveal:validation:1049

SHA-256: 10fa37c92ac64c6eec4a755bc12097d536d861cfd6384a90cb04e82f494daa0f

Nguồn: Runs-management/dry_run_validation_20261102/reveal/validation/B2-rep/42/prompts.jsonl

```text
You are now an excellent programmer. You are conducting a function vulnerability detection task for C/C++ language.

uchar * get_table_key ( const char * entry , size_t * length , my_bool not_used __attribute__ ( ( unused ) ) ) {
 * length = strlen ( entry ) ;
 return ( uchar * ) entry ;
 }

In the above code snippet, check for potential security vulnerabilities and answer with a single digit: 1 if Vulnerable, 0 if Non-vulnerable.

The node information of the code snippet is as follows:
Node 25769803818: (BLOCK) '{ * length = strlen ( entry ) ; return (...'
Node 30064771332: (CALL) '* length = strlen ( entry )'
Node 30064771333: (CALL) '* length'
Node 30064771334: (CALL) 'strlen ( entry )'
Node 30064771335: (CALL) '( uchar * ) entry'
Node 68719476997: (IDENTIFIER) 'length'
Node 68719476998: (IDENTIFIER) 'entry'
Node 68719476999: (IDENTIFIER) 'entry'
Node 107374182416: (METHOD) 'uchar * get_table_key ( const char * ent...'
Node 111669149719: (METHOD_PARAMETER_IN) 'const char * entry'
Node 111669149720: (METHOD_PARAMETER_IN) 'size_t * length'
Node 111669149721: (METHOD_PARAMETER_IN) 'my_bool not_used'
Node 115964117015: (METHOD_PARAMETER_OUT) 'const char * entry'
Node 115964117016: (METHOD_PARAMETER_OUT) 'size_t * length'
Node 115964117017: (METHOD_PARAMETER_OUT) 'my_bool not_used'
Node 124554051600: (METHOD_RETURN) 'RET'
Node 141733920779: (RETURN) 'return ( uchar * ) entry ;'
Node 176093659138: (TYPE_REF) 'uchar *'
The edge information of the code snippet is as follows:
Edge: Node 25769803818 -> AST -> Node 30064771332
Edge: Node 25769803818 -> AST -> Node 141733920779
Edge: Node 30064771332 -> ARGUMENT -> Node 30064771333
Edge: Node 30064771332 -> ARGUMENT -> Node 30064771334
Edge: Node 30064771332 -> AST -> Node 30064771333
Edge: Node 30064771332 -> AST -> Node 30064771334
Edge: Node 30064771332 -> CFG -> Node 176093659138
Edge: Node 30064771332 -> DOMINATE -> Node 176093659138
Edge: Node 30064771332 -> POST_DOMINATE -> Node 30064771334
Edge: Node 30064771332 -> REACHING_DEF -> Node 124554051600
Edge: Node 30064771333 -> ARGUMENT -> Node 68719476997
Edge: Node 30064771333 -> AST -> Node 68719476997
Edge: Node 30064771333 -> CFG -> Node 68719476998
Edge: Node 30064771333 -> DOMINATE -> Node 68719476998
Edge: Node 30064771333 -> POST_DOMINATE -> Node 68719476997
Edge: Node 30064771333 -> REACHING_DEF -> Node 30064771332
Edge: Node 30064771333 -> REACHING_DEF -> Node 115964117016
Edge: Node 30064771333 -> REACHING_DEF -> Node 124554051600
Edge: Node 30064771334 -> ARGUMENT -> Node 68719476998
Edge: Node 30064771334 -> AST -> Node 68719476998
Edge: Node 30064771334 -> CFG -> Node 30064771332
Edge: Node 30064771334 -> DOMINATE -> Node 30064771332
Edge: Node 30064771334 -> POST_DOMINATE -> Node 68719476998
Edge: Node 30064771334 -> REACHING_DEF -> Node 30064771333
Edge: Node 30064771334 -> REACHING_DEF -> Node 30064771332
Edge: Node 30064771334 -> REACHING_DEF -> Node 124554051600
Edge: Node 30064771335 -> ARGUMENT -> Node 176093659138
Edge: Node 30064771335 -> ARGUMENT -> Node 68719476999
Edge: Node 30064771335 -> AST -> Node 176093659138
Edge: Node 30064771335 -> AST -> Node 68719476999

The following is an example, and it is Non-vulnerable.
static uchar * acl_entry_get_key ( acl_entry * entry , size_t * length , my_bool not_used __attribute__ ( ( unused ) ) ) {
 * length = ( uint ) entry -> length ;
 return ( uchar * ) entry -> key ;
 }

Answer (0 or 1):
```

## 51. reveal/B1/42/reveal:validation:1749

SHA-256: 7326acad565e6256d25977cd5d5953bf99bb660b1d9d5b173d9fab520726a1fd

Nguồn: Runs-management/dry_run_validation_20261102/reveal/validation/B1/42/prompts.jsonl

```text
You are now an excellent programmer. You are conducting a function vulnerability detection task for C/C++ language.

void * hb_blob_get_user_data ( hb_blob_t * blob , hb_user_data_key_t * key ) {
 return hb_object_get_user_data ( blob , key ) ;
 }

In the above code snippet, check for potential security vulnerabilities and answer with a single digit: 1 if Vulnerable, 0 if Non-vulnerable.

The node information of the code snippet is as follows:
Node 25769803813: (BLOCK) '{ return hb_object_get_user_data ( blob ...'
Node 30064771282: (CALL) 'hb_object_get_user_data ( blob , key )'
Node 68719476894: (IDENTIFIER) 'blob'
Node 68719476895: (IDENTIFIER) 'key'
Node 107374182418: (METHOD) 'void * hb_blob_get_user_data ( hb_blob_t...'
Node 111669149715: (METHOD_PARAMETER_IN) 'hb_blob_t * blob'
Node 111669149716: (METHOD_PARAMETER_IN) 'hb_user_data_key_t * key'
Node 115964117011: (METHOD_PARAMETER_OUT) 'hb_blob_t * blob'
Node 115964117012: (METHOD_PARAMETER_OUT) 'hb_user_data_key_t * key'
Node 124554051602: (METHOD_RETURN) 'RET'
Node 141733920774: (RETURN) 'return hb_object_get_user_data ( blob , ...'
The edge information of the code snippet is as follows:
Edge: Node 25769803813 -> AST -> Node 141733920774
Edge: Node 30064771282 -> ARGUMENT -> Node 68719476894
Edge: Node 30064771282 -> ARGUMENT -> Node 68719476895
Edge: Node 30064771282 -> AST -> Node 68719476894
Edge: Node 30064771282 -> AST -> Node 68719476895
Edge: Node 30064771282 -> CFG -> Node 141733920774
Edge: Node 30064771282 -> DOMINATE -> Node 141733920774
Edge: Node 30064771282 -> POST_DOMINATE -> Node 68719476895
Edge: Node 30064771282 -> REACHING_DEF -> Node 141733920774
Edge: Node 30064771282 -> REACHING_DEF -> Node 124554051602
Edge: Node 68719476894 -> CFG -> Node 68719476895
Edge: Node 68719476894 -> DOMINATE -> Node 68719476895
Edge: Node 68719476894 -> POST_DOMINATE -> Node 107374182418
Edge: Node 68719476894 -> REACHING_DEF -> Node 115964117011
Edge: Node 68719476894 -> REACHING_DEF -> Node 68719476895
Edge: Node 68719476894 -> REACHING_DEF -> Node 30064771282
Edge: Node 68719476894 -> REACHING_DEF -> Node 124554051602
Edge: Node 68719476894 -> REF -> Node 111669149715
Edge: Node 68719476895 -> CFG -> Node 30064771282
Edge: Node 68719476895 -> DOMINATE -> Node 30064771282
Edge: Node 68719476895 -> POST_DOMINATE -> Node 68719476894
Edge: Node 68719476895 -> REACHING_DEF -> Node 68719476894
Edge: Node 68719476895 -> REACHING_DEF -> Node 30064771282
Edge: Node 68719476895 -> REACHING_DEF -> Node 115964117012
Edge: Node 68719476895 -> REACHING_DEF -> Node 124554051602
Edge: Node 68719476895 -> REF -> Node 111669149716
Edge: Node 107374182418 -> AST -> Node 111669149715
Edge: Node 107374182418 -> AST -> Node 111669149716
Edge: Node 107374182418 -> AST -> Node 25769803813
Edge: Node 107374182418 -> AST -> Node 124554051602
Edge: Node 107374182418 -> AST -> Node 115964117011
Edge: Node 107374182418 -> AST -> Node 115964117012
Edge: Node 107374182418 -> CFG -> Node 68719476894
Edge: Node 107374182418 -> CONTAINS -> Node 25769803813

The following is an example, and it is .


Answer (0 or 1):
```

## 52. reveal/B1-shuf/44/reveal:validation:62

SHA-256: b0488f4233c557691b54f8e5314b92cc292e3d229b7ec6f98964088613a70d95

Nguồn: Runs-management/dry_run_validation_20261102/reveal/validation/B1-shuf/44/prompts.jsonl

```text
You are now an excellent programmer. You are conducting a function vulnerability detection task for C/C++ language.

static void prepare_dummy_password ( char * buf , size_t sz ) {
 size_t i ;
 strlcpy ( buf , "6F a[" , sz ) ;
 for ( i = strlen ( buf ) ;
 i < sz - 1 ;
 i ++ ) buf [ i ] = 'a' + ( i % 26 ) ;
 buf [ sz - 1 ] = '\0' ;
 }

In the above code snippet, check for potential security vulnerabilities and answer with a single digit: 1 if Vulnerable, 0 if Non-vulnerable.

The node information of the code snippet is as follows:
Node 25769803790: (BLOCK) '{  pdf_drop_material ( ctx , & gs -> str...'
Node 30064771096: (CALL) 'pdf_drop_material ( ctx , & gs -> stroke...'
Node 30064771097: (CALL) '& gs -> stroke'
Node 30064771098: (CALL) 'gs -> stroke'
Node 30064771099: (CALL) 'pdf_drop_material ( ctx , & gs -> fill )'
Node 30064771100: (CALL) '& gs -> fill'
Node 30064771101: (CALL) 'gs -> fill'
Node 30064771102: (CALL) 'pdf_drop_font ( ctx , gs -> text . font ...'
Node 30064771103: (CALL) 'gs -> text . font'
Node 30064771104: (CALL) 'gs -> text'
Node 30064771105: (CALL) 'pdf_drop_xobject ( ctx , gs -> softmask ...'
Node 30064771106: (CALL) 'gs -> softmask'
Node 30064771107: (CALL) 'pdf_drop_obj ( ctx , gs -> softmask_reso...'
Node 30064771108: (CALL) 'gs -> softmask_resources'
Node 30064771109: (CALL) 'fz_drop_stroke_state ( ctx , gs -> strok...'
Node 30064771110: (CALL) 'gs -> stroke_state'
Node 55834574852: (FIELD_IDENTIFIER) 'stroke'
Node 55834574853: (FIELD_IDENTIFIER) 'fill'
Node 55834574854: (FIELD_IDENTIFIER) 'text'
Node 55834574855: (FIELD_IDENTIFIER) 'font'
Node 55834574856: (FIELD_IDENTIFIER) 'softmask'
Node 55834574857: (FIELD_IDENTIFIER) 'softmask_resources'
Node 55834574858: (FIELD_IDENTIFIER) 'stroke_state'
Node 68719476779: (IDENTIFIER) 'ctx'
Node 68719476780: (IDENTIFIER) 'gs'
Node 68719476781: (IDENTIFIER) 'ctx'
Node 68719476782: (IDENTIFIER) 'gs'
Node 68719476783: (IDENTIFIER) 'ctx'
Node 68719476784: (IDENTIFIER) 'gs'
Node 68719476785: (IDENTIFIER) 'ctx'
Node 68719476786: (IDENTIFIER) 'gs'
Node 68719476787: (IDENTIFIER) 'ctx'
Node 68719476788: (IDENTIFIER) 'gs'
Node 68719476789: (IDENTIFIER) 'ctx'
Node 68719476790: (IDENTIFIER) 'gs'
Node 107374182411: (METHOD) 'static void pdf_drop_gstate ( fz_context...'
Node 111669149710: (METHOD_PARAMETER_IN) 'fz_context * ctx'
Node 111669149711: (METHOD_PARAMETER_IN) 'pdf_gstate * gs'
Node 115964117006: (METHOD_PARAMETER_OUT) 'fz_context * ctx'
Node 115964117007: (METHOD_PARAMETER_OUT) 'pdf_gstate * gs'
The edge information of the code snippet is as follows:
Edge: Node 25769803790 -> AST -> Node 30064771096
Edge: Node 25769803790 -> AST -> Node 30064771099
Edge: Node 25769803790 -> AST -> Node 30064771102
Edge: Node 25769803790 -> AST -> Node 30064771105
Edge: Node 25769803790 -> AST -> Node 30064771107
Edge: Node 25769803790 -> AST -> Node 30064771109
Edge: Node 30064771096 -> ARGUMENT -> Node 68719476779
Edge: Node 30064771096 -> ARGUMENT -> Node 30064771097
Edge: Node 30064771096 -> AST -> Node 68719476779
Edge: Node 30064771096 -> AST -> Node 30064771097
Edge: Node 30064771096 -> CFG -> Node 68719476781
Edge: Node 30064771096 -> DOMINATE -> Node 68719476781
Edge: Node 30064771096 -> POST_DOMINATE -> Node 30064771097
Edge: Node 30064771097 -> ARGUMENT -> Node 30064771098
Edge: Node 30064771097 -> AST -> Node 30064771098
Edge: Node 30064771097 -> CFG -> Node 30064771096

The following is an example, and it is .


Answer (0 or 1):
```

## 53. reveal/B2-nolabel/42/reveal:validation:1036

SHA-256: bbb9c182c889a6213f1c86f930c81163da030118c6dbaf010a1967fe93a60ffc

Nguồn: Runs-management/dry_run_validation_20261102/reveal/validation/B2-nolabel/42/prompts.jsonl

```text
You are now an excellent programmer. You are conducting a function vulnerability detection task for C/C++ language.

static int dsa_bits ( const EVP_PKEY * pkey ) {
 return BN_num_bits ( pkey -> pkey . dsa -> p ) ;
 }

In the above code snippet, check for potential security vulnerabilities and answer with a single digit: 1 if Vulnerable, 0 if Non-vulnerable.

The node information of the code snippet is as follows:
Node 25769803809: (BLOCK) '{ return BN_num_bits ( pkey -> pkey . ds...'
Node 30064771304: (CALL) 'BN_num_bits ( pkey -> pkey . dsa -> p )'
Node 30064771305: (CALL) 'pkey -> pkey . dsa -> p'
Node 30064771306: (CALL) 'pkey -> pkey . dsa'
Node 30064771307: (CALL) 'pkey -> pkey'
Node 55834574899: (FIELD_IDENTIFIER) 'pkey'
Node 55834574900: (FIELD_IDENTIFIER) 'dsa'
Node 55834574901: (FIELD_IDENTIFIER) 'p'
Node 68719476919: (IDENTIFIER) 'pkey'
Node 107374182412: (METHOD) 'static int dsa_bits ( const EVP_PKEY * p...'
Node 111669149711: (METHOD_PARAMETER_IN) 'const EVP_PKEY * pkey'
Node 115964117007: (METHOD_PARAMETER_OUT) 'const EVP_PKEY * pkey'
Node 124554051596: (METHOD_RETURN) 'RET'
Node 128849018883: (MODIFIER) '<empty>'
Node 141733920777: (RETURN) 'return BN_num_bits ( pkey -> pkey . dsa ...'
The edge information of the code snippet is as follows:
Edge: Node 25769803809 -> AST -> Node 141733920777
Edge: Node 30064771304 -> ARGUMENT -> Node 30064771305
Edge: Node 30064771304 -> AST -> Node 30064771305
Edge: Node 30064771304 -> CFG -> Node 141733920777
Edge: Node 30064771304 -> DOMINATE -> Node 141733920777
Edge: Node 30064771304 -> POST_DOMINATE -> Node 30064771305
Edge: Node 30064771304 -> REACHING_DEF -> Node 141733920777
Edge: Node 30064771304 -> REACHING_DEF -> Node 124554051596
Edge: Node 30064771305 -> ARGUMENT -> Node 30064771306
Edge: Node 30064771305 -> ARGUMENT -> Node 55834574901
Edge: Node 30064771305 -> AST -> Node 30064771306
Edge: Node 30064771305 -> AST -> Node 55834574901
Edge: Node 30064771305 -> CFG -> Node 30064771304
Edge: Node 30064771305 -> DOMINATE -> Node 30064771304
Edge: Node 30064771305 -> POST_DOMINATE -> Node 55834574901
Edge: Node 30064771305 -> REACHING_DEF -> Node 30064771304
Edge: Node 30064771305 -> REACHING_DEF -> Node 124554051596
Edge: Node 30064771306 -> ARGUMENT -> Node 30064771307
Edge: Node 30064771306 -> ARGUMENT -> Node 55834574900
Edge: Node 30064771306 -> AST -> Node 30064771307
Edge: Node 30064771306 -> AST -> Node 55834574900
Edge: Node 30064771306 -> CFG -> Node 55834574901
Edge: Node 30064771306 -> DOMINATE -> Node 55834574901
Edge: Node 30064771306 -> POST_DOMINATE -> Node 55834574900
Edge: Node 30064771307 -> ARGUMENT -> Node 68719476919
Edge: Node 30064771307 -> ARGUMENT -> Node 55834574899
Edge: Node 30064771307 -> AST -> Node 68719476919
Edge: Node 30064771307 -> AST -> Node 55834574899
Edge: Node 30064771307 -> CFG -> Node 55834574900
Edge: Node 30064771307 -> DOMINATE -> Node 55834574900
Edge: Node 30064771307 -> POST_DOMINATE -> Node 55834574899
Edge: Node 55834574899 -> CFG -> Node 30064771307

The following is a related example.
static int dsa_security_bits ( const EVP_PKEY * pkey ) {
 return DSA_security_bits ( pkey -> pkey . dsa ) ;
 }

Answer (0 or 1):
```

## 54. reveal/B2-rand/44/reveal:validation:1844

SHA-256: 179a15a1778ea892e5cded362c06f3559453e2d655758c8de73bf4f4340dbabc

Nguồn: Runs-management/dry_run_validation_20261102/reveal/validation/B2-rand/44/prompts.jsonl

```text
You are now an excellent programmer. You are conducting a function vulnerability detection task for C/C++ language.

static void SkipEOLN ( cmsIT8 * it8 ) {
 while ( it8 -> sy == SEOLN ) {
 InSymbol ( it8 ) ;
 }
 }

In the above code snippet, check for potential security vulnerabilities and answer with a single digit: 1 if Vulnerable, 0 if Non-vulnerable.

The node information of the code snippet is as follows:
Node 25769803792: (BLOCK) '{ while ( it8 -> sy == SEOLN ) { InSymbo...'
Node 25769803793: (BLOCK) '{ InSymbol ( it8 ) ; }'
Node 30064771130: (CALL) 'it8 -> sy == SEOLN'
Node 30064771131: (CALL) 'it8 -> sy'
Node 30064771132: (CALL) 'InSymbol ( it8 )'
Node 47244640265: (CONTROL_STRUCTURE) 'while (it8 -> sy == SEOLN)'
Node 55834574857: (FIELD_IDENTIFIER) 'sy'
Node 68719476806: (IDENTIFIER) 'it8'
Node 68719476807: (IDENTIFIER) '<unknown> SEOLN'
Node 68719476808: (IDENTIFIER) 'it8'
Node 94489280527: (LOCAL) '<unknown> SEOLN'
Node 107374182408: (METHOD) 'static void SkipEOLN ( cmsIT8 * it8 ) { ...'
Node 111669149706: (METHOD_PARAMETER_IN) 'cmsIT8 * it8'
Node 115964117002: (METHOD_PARAMETER_OUT) 'cmsIT8 * it8'
Node 124554051592: (METHOD_RETURN) 'RET'
Node 128849018884: (MODIFIER) '<empty>'
The edge information of the code snippet is as follows:
Edge: Node 25769803792 -> AST -> Node 47244640265
Edge: Node 25769803792 -> AST -> Node 94489280527
Edge: Node 25769803793 -> AST -> Node 30064771132
Edge: Node 30064771130 -> ARGUMENT -> Node 30064771131
Edge: Node 30064771130 -> ARGUMENT -> Node 68719476807
Edge: Node 30064771130 -> AST -> Node 30064771131
Edge: Node 30064771130 -> AST -> Node 68719476807
Edge: Node 30064771130 -> CDG -> Node 30064771130
Edge: Node 30064771130 -> CDG -> Node 30064771131
Edge: Node 30064771130 -> CDG -> Node 30064771132
Edge: Node 30064771130 -> CDG -> Node 68719476806
Edge: Node 30064771130 -> CDG -> Node 68719476807
Edge: Node 30064771130 -> CDG -> Node 68719476808
Edge: Node 30064771130 -> CDG -> Node 55834574857
Edge: Node 30064771130 -> CFG -> Node 68719476808
Edge: Node 30064771130 -> CFG -> Node 124554051592
Edge: Node 30064771130 -> DOMINATE -> Node 68719476808
Edge: Node 30064771130 -> DOMINATE -> Node 124554051592
Edge: Node 30064771130 -> POST_DOMINATE -> Node 68719476807
Edge: Node 30064771130 -> REACHING_DEF -> Node 124554051592
Edge: Node 30064771131 -> ARGUMENT -> Node 68719476806
Edge: Node 30064771131 -> ARGUMENT -> Node 55834574857
Edge: Node 30064771131 -> AST -> Node 68719476806
Edge: Node 30064771131 -> AST -> Node 55834574857
Edge: Node 30064771131 -> CFG -> Node 68719476807
Edge: Node 30064771131 -> DOMINATE -> Node 68719476807
Edge: Node 30064771131 -> POST_DOMINATE -> Node 55834574857
Edge: Node 30064771131 -> REACHING_DEF -> Node 68719476808
Edge: Node 30064771131 -> REACHING_DEF -> Node 68719476807
Edge: Node 30064771131 -> REACHING_DEF -> Node 30064771130
Edge: Node 30064771131 -> REACHING_DEF -> Node 115964117002

The following is an example, and it is Non-vulnerable.
static int loop_filter_row_worker ( TileWorkerData * const tile_data , void * unused ) {
 LFWorkerData * const lf_data = & tile_data -> lfdata ;
 ( void ) unused ;
 loop_filter_rows_mt ( lf_data -> frame_buffer , lf_data -> cm , lf_data -> planes , lf_data -> start , lf_data -> stop , lf_data -> y_only , lf_data -> lf_sync , lf_data -> num_lf_workers ) ;
 return 1 ;
 }

Answer (0 or 1):
```

## 55. reveal/B2-rand/42/reveal:validation:795

SHA-256: a07f0432c53ffe5921342cccb4cd5ad0ed2747a4f65b032f3f025a478d10668f

Nguồn: Runs-management/dry_run_validation_20261102/reveal/validation/B2-rand/42/prompts.jsonl

```text
You are now an excellent programmer. You are conducting a function vulnerability detection task for C/C++ language.

extern int name ( int , locale_t ) __THROW __exctype_l ( isalnum_l ) ;
 __exctype_l ( isalpha_l ) ;
 __exctype_l ( iscntrl_l ) ;
 __exctype_l ( isdigit_l )

In the above code snippet, check for potential security vulnerabilities and answer with a single digit: 1 if Vulnerable, 0 if Non-vulnerable.

The node information of the code snippet is as follows:
Node 25769803817: (BLOCK) '<empty>'
Node 25769803818: (BLOCK) '<empty>'
Node 107374182418: (METHOD) 'extern int name ( int , locale_t )'
Node 107374182419: (METHOD) '__THROW __exctype_l ( isalnum_l ) ;'
Node 111669149715: (METHOD_PARAMETER_IN) 'int'
Node 111669149716: (METHOD_PARAMETER_IN) 'locale_t'
Node 111669149717: (METHOD_PARAMETER_IN) 'isalnum_l'
Node 115964117011: (METHOD_PARAMETER_OUT) 'int'
Node 115964117012: (METHOD_PARAMETER_OUT) 'locale_t'
Node 115964117013: (METHOD_PARAMETER_OUT) 'isalnum_l'
Node 124554051602: (METHOD_RETURN) 'RET'
Node 124554051603: (METHOD_RETURN) 'RET'
The edge information of the code snippet is as follows:
Edge: Node 107374182418 -> AST -> Node 111669149715
Edge: Node 107374182418 -> AST -> Node 111669149716
Edge: Node 107374182418 -> AST -> Node 25769803817
Edge: Node 107374182418 -> AST -> Node 124554051602
Edge: Node 107374182418 -> AST -> Node 115964117011
Edge: Node 107374182418 -> AST -> Node 115964117012
Edge: Node 107374182418 -> CFG -> Node 124554051602
Edge: Node 107374182418 -> CONTAINS -> Node 25769803817
Edge: Node 107374182418 -> DOMINATE -> Node 124554051602
Edge: Node 107374182418 -> REACHING_DEF -> Node 111669149716
Edge: Node 107374182418 -> REACHING_DEF -> Node 111669149715
Edge: Node 107374182419 -> AST -> Node 111669149717
Edge: Node 107374182419 -> AST -> Node 25769803818
Edge: Node 107374182419 -> AST -> Node 124554051603
Edge: Node 107374182419 -> AST -> Node 115964117013
Edge: Node 107374182419 -> CFG -> Node 124554051603
Edge: Node 107374182419 -> CONTAINS -> Node 25769803818
Edge: Node 107374182419 -> DOMINATE -> Node 124554051603
Edge: Node 107374182419 -> REACHING_DEF -> Node 111669149717
Edge: Node 111669149715 -> PARAMETER_LINK -> Node 115964117011
Edge: Node 111669149715 -> REACHING_DEF -> Node 115964117011
Edge: Node 111669149715 -> REACHING_DEF -> Node 124554051602
Edge: Node 111669149716 -> PARAMETER_LINK -> Node 115964117012
Edge: Node 111669149716 -> REACHING_DEF -> Node 115964117012
Edge: Node 111669149716 -> REACHING_DEF -> Node 124554051602
Edge: Node 111669149717 -> PARAMETER_LINK -> Node 115964117013
Edge: Node 111669149717 -> REACHING_DEF -> Node 115964117013
Edge: Node 111669149717 -> REACHING_DEF -> Node 124554051603
Edge: Node 124554051602 -> POST_DOMINATE -> Node 107374182418
Edge: Node 124554051603 -> POST_DOMINATE -> Node 107374182419

The following is an example, and it is Non-vulnerable.
static bfd_boolean srec_write_section ( bfd * abfd , tdata_type * tdata , srec_data_list_type * list ) {
 unsigned int octets_written = 0 ;
 bfd_byte * location = list -> data ;
 if ( Chunk == 0 ) Chunk = 1 ;
 else if ( Chunk > MAXCHUNK - tdata -> type - 2 ) Chunk = MAXCHUNK - tdata -> type - 2 ;
 while ( octets_written < list -> size ) {
 bfd_vma address ;
 unsigned int octets_this_chunk = list -> size - octets_written ;
 if ( octets_this_chunk > Chunk ) octets_this_chunk = Chunk ;
 address = list -> where + octets_written / bfd_octets_per_byte ( abfd ) ;
 if ( ! srec_write_record ( abfd , tdata -> type , address , location , location + octets_this_chunk ) ) return FALSE ;
 octets_written += octets_this_chunk ;
 location += octets_this_chunk ;
 }
 return TRUE ;
 }

Answer (0 or 1):
```

## 56. reveal/B2-nolabel/42/reveal:validation:2211

SHA-256: 2d6957bea6d3c42ff405c3c7f50c9f319f4be09e6b105017970acbfdfdc3cc78

Nguồn: Runs-management/dry_run_validation_20261102/reveal/validation/B2-nolabel/42/prompts.jsonl

```text
You are now an excellent programmer. You are conducting a function vulnerability detection task for C/C++ language.

TEST_F ( TemplateURLTest , ReplaceSearchTermsInUTF8URL ) {
 TemplateURLData data ;
 data . SetURL ( "http://utf-8.ru/?q={
searchTerms}
" ) ;
 data . alternate_urls . push_back ( "http://utf-8.ru/#q={
searchTerms}
" ) ;
 data . alternate_urls . push_back ( "http://utf-8.ru/path/{
searchTerms}
" ) ;
 TemplateURL url ( data ) ;
 TemplateURLRef : : SearchTermsArgs search_terms ( base : : WideToUTF16 ( L"\x0442\x0435\x043A\x0441\x0442" ) ) ;
 GURL result ;
 EXPECT_TRUE ( url . ReplaceSearchTermsInURL ( GURL ( "http://utf-8.ru/?q=a+b" ) , search_terms , search_terms_data_ , & result ) ) ;
 EXPECT_EQ ( GURL ( "http://utf-8.ru/?q=%D1%82%D0%B5%D0%BA%D1%81%D1%82" ) , result ) ;
 EXPECT_TRUE ( url . ReplaceSearchTermsInURL ( GURL ( "http://utf-8.ru/#q=a+b" ) , search_terms , search_terms_data_ , & result ) ) ;
 EXPECT_EQ ( GURL ( "http://utf-8.ru/#q=%D1%82%D0%B5%D0%BA%D1%81%D1%82" ) , result ) ;
 EXPECT_TRUE ( url . ReplaceSearchTermsInURL ( GURL ( "http://utf-8.ru/path/a%20b" ) , search_terms , search_terms_data_ , & result ) ) ;
 EXPECT_EQ ( GURL ( "http://utf-8.ru/path/%D1%82%D0%B5%D0%BA%D1%81%D1%82" ) , result ) ;
 }

In the above code snippet, check for potential security vulnerabilities and answer with a single digit: 1 if Vulnerable, 0 if Non-vulnerable.

The node information of the code snippet is as follows:
Node 25769803778: (BLOCK) '{ TemplateURLData data ; data . SetURL (...'
Node 94489280513: (LOCAL) 'TemplateURLData data'
Node 107374182402: (METHOD) 'TEST_F ( TemplateURLTest , ReplaceSearch...'
Node 111669149697: (METHOD_PARAMETER_IN) 'TemplateURLTest'
Node 111669149698: (METHOD_PARAMETER_IN) 'ReplaceSearchTermsInUTF8URL'
Node 115964116993: (METHOD_PARAMETER_OUT) 'TemplateURLTest'
Node 115964116994: (METHOD_PARAMETER_OUT) 'ReplaceSearchTermsInUTF8URL'
Node 124554051586: (METHOD_RETURN) 'RET'
The edge information of the code snippet is as follows:
Edge: Node 25769803778 -> AST -> Node 94489280513
Edge: Node 107374182402 -> AST -> Node 111669149697
Edge: Node 107374182402 -> AST -> Node 111669149698
Edge: Node 107374182402 -> AST -> Node 25769803778
Edge: Node 107374182402 -> AST -> Node 124554051586
Edge: Node 107374182402 -> AST -> Node 115964116993
Edge: Node 107374182402 -> AST -> Node 115964116994
Edge: Node 107374182402 -> CFG -> Node 124554051586
Edge: Node 107374182402 -> CONTAINS -> Node 25769803778
Edge: Node 107374182402 -> DOMINATE -> Node 124554051586
Edge: Node 107374182402 -> REACHING_DEF -> Node 111669149698
Edge: Node 107374182402 -> REACHING_DEF -> Node 111669149697
Edge: Node 111669149697 -> PARAMETER_LINK -> Node 115964116993
Edge: Node 111669149697 -> REACHING_DEF -> Node 115964116993
Edge: Node 111669149697 -> REACHING_DEF -> Node 124554051586
Edge: Node 111669149698 -> PARAMETER_LINK -> Node 115964116994
Edge: Node 111669149698 -> REACHING_DEF -> Node 115964116994
Edge: Node 111669149698 -> REACHING_DEF -> Node 124554051586
Edge: Node 124554051586 -> POST_DOMINATE -> Node 107374182402

The following is a related example.
TEST_F ( TemplateURLTest , ExtractSearchTermsFromUTF8URL ) {
 TemplateURLData data ;
 data . SetURL ( "http://utf-8.ru/?q={
searchTerms}
" ) ;
 data . alternate_urls . push_back ( "http://utf-8.ru/#q={
searchTerms}
" ) ;
 data . alternate_urls . push_back ( "http://utf-8.ru/path/{
searchTerms}
" ) ;
 TemplateURL url ( data ) ;
 base : : string16 result ;
 EXPECT_TRUE ( url . ExtractSearchTermsFromURL ( GURL ( "http://utf-8.ru/?q=%D0%97%D0%B4%D1%80%D0%B0%D0%B2%D1%81%D1%82" "%D0%B2%D1%83%D0%B9,+%D0%BC%D0%B8%D1%80!" ) , search_terms_data_ , & result ) ) ;
 EXPECT_EQ ( base : : WideToUTF16 ( L"\x0417\x0434\x0440\x0430\x0432\x0441\x0442\x0432\x0443\x0439, " L"\x043C\x0438\x0440!" ) , result ) ;
 EXPECT_TRUE ( url . ExtractSearchTermsFromURL ( GURL ( "http://utf-8.ru/#q=%D0%B4%D0%B2%D0%B0+%D1%81%D0%BB%D0%BE%D0%B2" "%D0%B0" ) , search_terms_data_ , & result ) ) ;
 EXPECT_EQ ( base : : WideToUTF16 ( L"\x0434\x0432\x0430 \x0441\x043B\x043E\x0432\x0430" ) , result ) ;
 EXPECT_TRUE ( url . ExtractSearchTermsFromURL ( GURL ( "http://utf-8.ru/path/%D0%B1%D1%83%D0%BA%D0%B2%D1%8B%20%D0%90%20" "%D0%B8%20A" ) , search_terms_data_ , & result ) ) ;
 EXPECT_EQ ( base : : WideToUTF16 ( L"\x0431\x0443\x043A\x0432\x044B \x0410 \x0438 A" ) , result ) ;
 }

Answer (0 or 1):
```

## 57. reveal/B2/42/reveal:validation:1933

SHA-256: 29cf40e46da4495fc3b2bf659ba2e24afb4acf7b14937d4422ed844e1b6cacef

Nguồn: Runs-management/dry_run_validation_20261102/reveal/validation/B2/42/prompts.jsonl

```text
You are now an excellent programmer. You are conducting a function vulnerability detection task for C/C++ language.

static ossl_inline int sk_ ## t1 ## _insert ( STACK_OF ( t1 ) * sk , t2 * ptr , int idx ) {
 return OPENSSL_sk_insert ( ( OPENSSL_STACK * ) sk , ( const void * ) ptr , idx ) ;
 }
 static ossl_inline t2 * sk_ ## t1 ## _set ( STACK_OF ( t1 ) * sk , int idx , t2 * ptr ) {
 return ( t2 * ) OPENSSL_sk_set ( ( OPENSSL_STACK * ) sk , idx , ( const void * ) ptr ) ;
 }
 static ossl_inline int sk_ ## t1 ## _find ( STACK_OF ( t1 ) * sk , t2 * ptr ) {
 return OPENSSL_sk_find ( ( OPENSSL_STACK * ) sk , ( const void * ) ptr ) ;
 }
 static ossl_inline int sk_ ## t1 ## _find_ex ( STACK_OF ( t1 ) * sk , t2 * ptr ) {
 return OPENSSL_sk_find_ex ( ( OPENSSL_STACK * ) sk , ( const void * ) ptr ) ;
 }
 static ossl_inline void sk_ ## t1 ## _sort ( STACK_OF ( t1 ) * sk ) {
 OPENSSL_sk_sort ( ( OPENSSL_STACK * ) sk ) ;
 }
 static ossl_inline int sk_ ## t1 ## _is_sorted ( const STACK_OF ( t1 ) * sk ) {
 return OPENSSL_sk_is_sorted ( ( const OPENSSL_STACK * ) sk ) ;
 }
 static ossl_inline STACK_OF ( t1 ) * sk_ ## t1 ## _dup ( const STACK_OF ( t1 ) * sk ) {
 return ( STACK_OF ( t1 ) * ) OPENSSL_sk_dup ( ( const OPENSSL_STACK * ) sk ) ;
 }
 static ossl_inline STACK_OF ( t1 ) * sk_ ## t1 ## _deep_copy ( const STACK_OF ( t1 ) * sk , sk_ ## t1 ## _copyfunc copyfunc , sk_ ## t1 ## _freefunc freefunc ) {
 return ( STACK_OF ( t1 ) * ) OPENSSL_sk_deep_copy ( ( const OPENSSL_STACK * ) sk , ( OPENSSL_sk_copyfunc ) copyfunc , ( OPENSSL_sk_freefunc ) freefunc ) ;
 }
 static ossl_inline sk_ ## t1 ## _compfunc sk_ ## t1 ## _set_cmp_func ( STACK_OF ( t1 ) * sk , sk_ ## t1 ## _compfunc compare ) {
 return ( sk_ ## t1 ## _compfunc ) OPENSSL_sk_set_cmp_func ( ( OPENSSL_STACK * ) sk , ( OPENSSL_sk_compfunc ) compare ) ;
 }
 # define DEFINE_SPECIAL_STACK_OF ( t1 , t2 ) SKM_DEFINE_STACK_OF ( t1 , t2 , t2 ) # define DEFINE_STACK_OF ( t ) SKM_DEFINE_STACK_OF ( t , t , t ) # define DEFINE_SPECIAL_STACK_OF_CONST ( t1 , t2 ) SKM_DEFINE_STACK_OF ( t1 , const t2 , t2 ) # define DEFINE_STACK_OF_CONST ( t ) SKM_DEFINE_STACK_OF ( t , const t , t ) typedef char * OPENSSL_STRING ;
 typedef const char * OPENSSL_CSTRING ;
 DEFINE_SPECIAL_STACK_OF ( OPENSSL_STRING , char ) DEFINE_SPECIAL_STACK_OF_CONST ( OPENSSL_CSTRING , char ) typedef void * OPENSSL_BLOCK ;
 DEFINE_SPECIAL_STACK_OF ( OPENSSL_BLOCK , void )

In the above code snippet, check for potential security vulnerabilities and answer with a single digit: 1 if Vulnerable, 0 if Non-vulnerable.

The node information of the code snippet is as follows:
Node 25769803801: (BLOCK) '<empty>'
Node 107374182418: (METHOD) 'static ossl_inline STACK_OF ( t1 )'
Node 111669149726: (METHOD_PARAMETER_IN) 't1'
Node 115964117022: (METHOD_PARAMETER_OUT) 't1'
Node 124554051602: (METHOD_RETURN) 'RET'
Node 128849018883: (MODIFIER) '<empty>'
The edge information of the code snippet is as follows:
Edge: Node 107374182418 -> AST -> Node 111669149726
Edge: Node 107374182418 -> AST -> Node 25769803801
Edge: Node 107374182418 -> AST -> Node 128849018883
Edge: Node 107374182418 -> AST -> Node 124554051602
Edge: Node 107374182418 -> AST -> Node 115964117022
Edge: Node 107374182418 -> CFG -> Node 124554051602
Edge: Node 107374182418 -> CONTAINS -> Node 25769803801
Edge: Node 107374182418 -> DOMINATE -> Node 124554051602
Edge: Node 107374182418 -> REACHING_DEF -> Node 111669149726
Edge: Node 111669149726 -> PARAMETER_LINK -> Node 115964117022
Edge: Node 111669149726 -> REACHING_DEF -> Node 115964117022
Edge: Node 111669149726 -> REACHING_DEF -> Node 124554051602
Edge: Node 124554051602 -> POST_DOMINATE -> Node 107374182418

The following is an example, and it is Non-vulnerable.
unsigned int vp9_sad ## m ## x ## n ## _c ( const uint8_t * src , int src_stride , const uint8_t * ref , int ref_stride ) {
 return sad ( src , src_stride , ref , ref_stride , m , n ) ;
 \ }
 unsigned int vp9_sad ## m ## x ## n ## _avg_c ( const uint8_t * src , int src_stride , const uint8_t * ref , int ref_stride , const uint8_t * second_pred ) {
 uint8_t comp_pred [ m * n ] ;
 vp9_comp_avg_pred ( comp_pred , second_pred , m , n , ref , ref_stride ) ;
 return sad ( src , src_stride , comp_pred , m , m , n ) ;
 \ }
 # define sadMxNxK ( m , n , k ) void vp9_sad ## m ## x ## n ## x ## k ## _c ( const uint8_t * src , int src_stride , const uint8_t * ref , int ref_stride , unsigned int * sads ) {
 int i ;
 for ( i = 0 ;
 i < k ;
 ++ i ) sads [ i ] = vp9_sad ## m ## x ## n ## _c ( src , src_stride , & ref [ i ] , ref_stride ) ;
 \ }
 # define sadMxNx4D ( m , n ) void vp9_sad ## m ## x ## n ## x4d_c ( const uint8_t * src , int src_stride , const uint8_t * const refs [ ] , int ref_stride , unsigned int * sads ) {
 int i ;
 for ( i = 0 ;
 i < 4 ;
 ++ i ) sads [ i ] = vp9_sad ## m ## x ## n ## _c ( src , src_stride , refs [ i ] , ref_stride ) ;
 \ }
 sadMxN ( 64 , 64 ) sadMxNxK ( 64 , 64 , 3 ) sadMxNxK ( 64 , 64 , 8 ) sadMxNx4D ( 64 , 64 ) sadMxN ( 64 , 32 ) sadMxNx4D ( 64 , 32 ) sadMxN ( 32 , 64 ) sadMxNx4D ( 32 , 64 ) sadMxN ( 32 , 32 )

Answer (0 or 1):
```

## 58. reveal/B1-shuf/44/reveal:validation:1254

SHA-256: bf2fe6d6616f9f3bf9801dbe7207ad2cd66a63480e2c01e95f635f91a2a5da89

Nguồn: Runs-management/dry_run_validation_20261102/reveal/validation/B1-shuf/44/prompts.jsonl

```text
You are now an excellent programmer. You are conducting a function vulnerability detection task for C/C++ language.

static ossl_inline STACK_OF ( t1 ) * sk_ ## t1 ## _new_reserve ( sk_ ## t1 ## _compfunc compare , int n ) {
 return ( STACK_OF ( t1 ) * ) OPENSSL_sk_new_reserve ( ( OPENSSL_sk_compfunc ) compare , n ) ;
 }
 static ossl_inline int sk_ ## t1 ## _reserve ( STACK_OF ( t1 ) * sk , int n ) {
 return OPENSSL_sk_reserve ( ( OPENSSL_STACK * ) sk , n ) ;
 }
 static ossl_inline void sk_ ## t1 ## _free ( STACK_OF ( t1 ) * sk ) {
 OPENSSL_sk_free ( ( OPENSSL_STACK * ) sk ) ;
 }
 static ossl_inline void sk_ ## t1 ## _zero ( STACK_OF ( t1 ) * sk ) {
 OPENSSL_sk_zero ( ( OPENSSL_STACK * ) sk ) ;
 }
 static ossl_inline t2 * sk_ ## t1 ## _delete ( STACK_OF ( t1 ) * sk , int i ) {
 return ( t2 * ) OPENSSL_sk_delete ( ( OPENSSL_STACK * ) sk , i ) ;
 }
 static ossl_inline t2 * sk_ ## t1 ## _delete_ptr ( STACK_OF ( t1 ) * sk , t2 * ptr ) {
 return ( t2 * ) OPENSSL_sk_delete_ptr ( ( OPENSSL_STACK * ) sk , ( const void * ) ptr ) ;
 }
 static ossl_inline int sk_ ## t1 ## _push ( STACK_OF ( t1 ) * sk , t2 * ptr ) {
 return OPENSSL_sk_push ( ( OPENSSL_STACK * ) sk , ( const void * ) ptr ) ;
 }
 static ossl_inline int sk_ ## t1 ## _unshift ( STACK_OF ( t1 ) * sk , t2 * ptr ) {
 return OPENSSL_sk_unshift ( ( OPENSSL_STACK * ) sk , ( const void * ) ptr ) ;
 }
 static ossl_inline t2 * sk_ ## t1 ## _pop ( STACK_OF ( t1 ) * sk ) {
 return ( t2 * ) OPENSSL_sk_pop ( ( OPENSSL_STACK * ) sk ) ;
 }
 static ossl_inline t2 * sk_ ## t1 ## _shift ( STACK_OF ( t1 ) * sk ) {
 return ( t2 * ) OPENSSL_sk_shift ( ( OPENSSL_STACK * ) sk ) ;
 }
 static ossl_inline void sk_ ## t1 ## _pop_free ( STACK_OF ( t1 ) * sk , sk_ ## t1 ## _freefunc freefunc ) {
 OPENSSL_sk_pop_free ( ( OPENSSL_STACK * ) sk , ( OPENSSL_sk_freefunc ) freefunc ) ;
 }
 static ossl_inline int sk_ ## t1 ## _insert ( STACK_OF ( t1 ) * sk , t2 * ptr , int idx ) {
 return OPENSSL_sk_insert ( ( OPENSSL_STACK * ) sk , ( const void * ) ptr , idx ) ;
 }
 static ossl_inline t2 * sk_ ## t1 ## _set ( STACK_OF ( t1 ) * sk , int idx , t2 * ptr ) {
 return ( t2 * ) OPENSSL_sk_set ( ( OPENSSL_STACK * ) sk , idx , ( const void * ) ptr ) ;
 }
 static ossl_inline int sk_ ## t1 ## _find ( STACK_OF ( t1 ) * sk , t2 * ptr ) {
 return OPENSSL_sk_find ( ( OPENSSL_STACK * ) sk , ( const void * ) ptr ) ;
 }
 static ossl_inline int sk_ ## t1 ## _find_ex ( STACK_OF ( t1 ) * sk , t2 * ptr ) {
 return OPENSSL_sk_find_ex ( ( OPENSSL_STACK * ) sk , ( const void * ) ptr ) ;
 }
 static ossl_inline void sk_ ## t1 ## _sort ( STACK_OF ( t1 ) * sk ) {
 OPENSSL_sk_sort ( ( OPENSSL_STACK * ) sk ) ;
 }
 static ossl_inline int sk_ ## t1 ## _is_sorted ( const STACK_OF ( t1 ) * sk ) {
 return OPENSSL_sk_is_sorted ( ( const OPENSSL_STACK * ) sk ) ;
 }
 static ossl_inline STACK_OF ( t1 ) * sk_ ## t1 ## _dup ( const STACK_OF ( t1 ) * sk ) {
 return ( STACK_OF ( t1 ) * ) OPENSSL_sk_dup ( ( const OPENSSL_STACK * ) sk ) ;
 }
 static ossl_inline STACK_OF ( t1 ) * sk_ ## t1 ## _deep_copy ( const STACK_OF ( t1 ) * sk , sk_ ## t1 ## _copyfunc copyfunc , sk_ ## t1 ## _freefunc freefunc ) {
 return ( STACK_OF ( t1 ) * ) OPENSSL_sk_deep_copy ( ( const OPENSSL_STACK * ) sk , ( OPENSSL_sk_copyfunc ) copyfunc , ( OPENSSL_sk_freefunc ) freefunc ) ;
 }
 static ossl_inline sk_ ## t1 ## _compfunc sk_ ## t1 ## _set_cmp_func ( STACK_OF ( t1 ) * sk , sk_ ## t1 ## _compfunc compare ) {
 return ( sk_ ## t1 ## _compfunc ) OPENSSL_sk_set_cmp_func ( ( OPENSSL_STACK * ) sk , ( OPENSSL_sk_compfunc ) compare ) ;
 }
 # define DEFINE_SPECIAL_STACK_OF ( t1 , t2 ) SKM_DEFINE_STACK_OF ( t1 , t2 , t2 ) # define DEFINE_STACK_OF ( t ) SKM_DEFINE_STACK_OF ( t , t , t ) # define DEFINE_SPECIAL_STACK_OF_CONST ( t1 , t2 ) SKM_DEFINE_STACK_OF ( t1 , const t2 , t2 ) # define DEFINE_STACK_OF_CONST ( t ) SKM_DEFINE_STACK_OF ( t , const t , t ) typedef char * OPENSSL_STRING ;
 typedef const char * OPENSSL_CSTRING ;
 DEFINE_SPECIAL_STACK_OF ( OPENSSL_STRING , char ) DEFINE_SPECIAL_STACK_OF_CONST ( OPENSSL_CSTRING , char )

In the above code snippet, check for potential security vulnerabilities and answer with a single digit: 1 if Vulnerable, 0 if Non-vulnerable.

The node information of the code snippet is as follows:
Node 25769803828: (BLOCK) '<empty>'
Node 107374182419: (METHOD) 'int yyparse ( void )'
Node 111669149716: (METHOD_PARAMETER_IN) 'void'
Node 115964117012: (METHOD_PARAMETER_OUT) 'void'
Node 124554051603: (METHOD_RETURN) 'RET'
The edge information of the code snippet is as follows:
Edge: Node 107374182419 -> AST -> Node 111669149716
Edge: Node 107374182419 -> AST -> Node 25769803828
Edge: Node 107374182419 -> AST -> Node 124554051603
Edge: Node 107374182419 -> AST -> Node 115964117012
Edge: Node 107374182419 -> CFG -> Node 124554051603
Edge: Node 107374182419 -> CONTAINS -> Node 25769803828
Edge: Node 107374182419 -> DOMINATE -> Node 124554051603
Edge: Node 107374182419 -> REACHING_DEF -> Node 111669149716
Edge: Node 111669149716 -> PARAMETER_LINK -> Node 115964117012
Edge: Node 111669149716 -> REACHING_DEF -> Node 115964117012
Edge: Node 111669149716 -> REACHING_DEF -> Node 124554051603
Edge: Node 124554051603 -> POST_DOMINATE -> Node 107374182419

The following is an example, and it is .


Answer (0 or 1):
```

## 59. reveal/B1/42/reveal:validation:1503

SHA-256: ede51c729368c6b9b4d3a761d832dd23ea2710eefa745e859850a8bd17a74f07

Nguồn: Runs-management/dry_run_validation_20261102/reveal/validation/B1/42/prompts.jsonl

```text
You are now an excellent programmer. You are conducting a function vulnerability detection task for C/C++ language.

static ossl_inline void sk_ ## t1 ## _zero ( STACK_OF ( t1 ) * sk ) {
 OPENSSL_sk_zero ( ( OPENSSL_STACK * ) sk ) ;
 }
 static ossl_inline t2 * sk_ ## t1 ## _delete ( STACK_OF ( t1 ) * sk , int i ) {
 return ( t2 * ) OPENSSL_sk_delete ( ( OPENSSL_STACK * ) sk , i ) ;
 }
 static ossl_inline t2 * sk_ ## t1 ## _delete_ptr ( STACK_OF ( t1 ) * sk , t2 * ptr ) {
 return ( t2 * ) OPENSSL_sk_delete_ptr ( ( OPENSSL_STACK * ) sk , ( const void * ) ptr ) ;
 }
 static ossl_inline int sk_ ## t1 ## _push ( STACK_OF ( t1 ) * sk , t2 * ptr ) {
 return OPENSSL_sk_push ( ( OPENSSL_STACK * ) sk , ( const void * ) ptr ) ;
 }
 static ossl_inline int sk_ ## t1 ## _unshift ( STACK_OF ( t1 ) * sk , t2 * ptr ) {
 return OPENSSL_sk_unshift ( ( OPENSSL_STACK * ) sk , ( const void * ) ptr ) ;
 }
 static ossl_inline t2 * sk_ ## t1 ## _pop ( STACK_OF ( t1 ) * sk ) {
 return ( t2 * ) OPENSSL_sk_pop ( ( OPENSSL_STACK * ) sk ) ;
 }
 static ossl_inline t2 * sk_ ## t1 ## _shift ( STACK_OF ( t1 ) * sk ) {
 return ( t2 * ) OPENSSL_sk_shift ( ( OPENSSL_STACK * ) sk ) ;
 }
 static ossl_inline void sk_ ## t1 ## _pop_free ( STACK_OF ( t1 ) * sk , sk_ ## t1 ## _freefunc freefunc ) {
 OPENSSL_sk_pop_free ( ( OPENSSL_STACK * ) sk , ( OPENSSL_sk_freefunc ) freefunc ) ;
 }
 static ossl_inline int sk_ ## t1 ## _insert ( STACK_OF ( t1 ) * sk , t2 * ptr , int idx ) {
 return OPENSSL_sk_insert ( ( OPENSSL_STACK * ) sk , ( const void * ) ptr , idx ) ;
 }
 static ossl_inline t2 * sk_ ## t1 ## _set ( STACK_OF ( t1 ) * sk , int idx , t2 * ptr ) {
 return ( t2 * ) OPENSSL_sk_set ( ( OPENSSL_STACK * ) sk , idx , ( const void * ) ptr ) ;
 }
 static ossl_inline int sk_ ## t1 ## _find ( STACK_OF ( t1 ) * sk , t2 * ptr ) {
 return OPENSSL_sk_find ( ( OPENSSL_STACK * ) sk , ( const void * ) ptr ) ;
 }
 static ossl_inline int sk_ ## t1 ## _find_ex ( STACK_OF ( t1 ) * sk , t2 * ptr ) {
 return OPENSSL_sk_find_ex ( ( OPENSSL_STACK * ) sk , ( const void * ) ptr ) ;
 }
 static ossl_inline void sk_ ## t1 ## _sort ( STACK_OF ( t1 ) * sk ) {
 OPENSSL_sk_sort ( ( OPENSSL_STACK * ) sk ) ;
 }
 static ossl_inline int sk_ ## t1 ## _is_sorted ( const STACK_OF ( t1 ) * sk ) {
 return OPENSSL_sk_is_sorted ( ( const OPENSSL_STACK * ) sk ) ;
 }
 static ossl_inline STACK_OF ( t1 ) * sk_ ## t1 ## _dup ( const STACK_OF ( t1 ) * sk ) {
 return ( STACK_OF ( t1 ) * ) OPENSSL_sk_dup ( ( const OPENSSL_STACK * ) sk ) ;
 }
 static ossl_inline STACK_OF ( t1 ) * sk_ ## t1 ## _deep_copy ( const STACK_OF ( t1 ) * sk , sk_ ## t1 ## _copyfunc copyfunc , sk_ ## t1 ## _freefunc freefunc ) {
 return ( STACK_OF ( t1 ) * ) OPENSSL_sk_deep_copy ( ( const OPENSSL_STACK * ) sk , ( OPENSSL_sk_copyfunc ) copyfunc , ( OPENSSL_sk_freefunc ) freefunc ) ;
 }
 static ossl_inline sk_ ## t1 ## _compfunc sk_ ## t1 ## _set_cmp_func ( STACK_OF ( t1 ) * sk , sk_ ## t1 ## _compfunc compare ) {
 return ( sk_ ## t1 ## _compfunc ) OPENSSL_sk_set_cmp_func ( ( OPENSSL_STACK * ) sk , ( OPENSSL_sk_compfunc ) compare ) ;
 }
 # define DEFINE_SPECIAL_STACK_OF ( t1 , t2 ) SKM_DEFINE_STACK_OF ( t1 , t2 , t2 ) # define DEFINE_STACK_OF ( t ) SKM_DEFINE_STACK_OF ( t , t , t ) # define DEFINE_SPECIAL_STACK_OF_CONST ( t1 , t2 ) SKM_DEFINE_STACK_OF ( t1 , const t2 , t2 ) # define DEFINE_STACK_OF_CONST ( t ) SKM_DEFINE_STACK_OF ( t , const t , t ) typedef char * OPENSSL_STRING ;
 typedef const char * OPENSSL_CSTRING ;
 DEFINE_SPECIAL_STACK_OF ( OPENSSL_STRING , char ) DEFINE_SPECIAL_STACK_OF_CONST ( OPENSSL_CSTRING , char )

In the above code snippet, check for potential security vulnerabilities and answer with a single digit: 1 if Vulnerable, 0 if Non-vulnerable.

The node information of the code snippet is as follows:
Node 25769803838: (BLOCK) '<empty>'
Node 107374182420: (METHOD) 'static ossl_inline STACK_OF ( t1 )'
Node 111669149722: (METHOD_PARAMETER_IN) 't1'
Node 115964117018: (METHOD_PARAMETER_OUT) 't1'
Node 124554051604: (METHOD_RETURN) 'RET'
Node 128849018886: (MODIFIER) '<empty>'
The edge information of the code snippet is as follows:
Edge: Node 107374182420 -> AST -> Node 111669149722
Edge: Node 107374182420 -> AST -> Node 25769803838
Edge: Node 107374182420 -> AST -> Node 128849018886
Edge: Node 107374182420 -> AST -> Node 124554051604
Edge: Node 107374182420 -> AST -> Node 115964117018
Edge: Node 107374182420 -> CFG -> Node 124554051604
Edge: Node 107374182420 -> CONTAINS -> Node 25769803838
Edge: Node 107374182420 -> DOMINATE -> Node 124554051604
Edge: Node 107374182420 -> REACHING_DEF -> Node 111669149722
Edge: Node 111669149722 -> PARAMETER_LINK -> Node 115964117018
Edge: Node 111669149722 -> REACHING_DEF -> Node 115964117018
Edge: Node 111669149722 -> REACHING_DEF -> Node 124554051604
Edge: Node 124554051604 -> POST_DOMINATE -> Node 107374182420

The following is an example, and it is .


Answer (0 or 1):
```

## 60. reveal/B2-rand/43/reveal:validation:981

SHA-256: 1f8c03bf878cfa3ed0794a9e5fd51387a4a6db8677dc6debc0dbe9c42c1f9793

Nguồn: Runs-management/dry_run_validation_20261102/reveal/validation/B2-rand/43/prompts.jsonl

```text
You are now an excellent programmer. You are conducting a function vulnerability detection task for C/C++ language.

static int SpoolssEndPagePrinter_q ( tvbuff_t * tvb , int offset , packet_info * pinfo , proto_tree * tree , dcerpc_info * di , guint8 * drep ) {
 e_ctx_hnd policy_hnd ;
 char * pol_name ;
 offset = dissect_nt_policy_hnd ( tvb , offset , pinfo , tree , di , drep , hf_hnd , & policy_hnd , NULL , FALSE , FALSE ) ;
 dcerpc_fetch_polhnd_data ( & policy_hnd , & pol_name , NULL , NULL , NULL , pinfo -> num ) ;
 if ( pol_name ) col_append_fstr ( pinfo -> cinfo , COL_INFO , ", %s" , pol_name ) ;
 return offset ;
 }

In the above code snippet, check for potential security vulnerabilities and answer with a single digit: 1 if Vulnerable, 0 if Non-vulnerable.

The node information of the code snippet is as follows:
Node 25769803778: (BLOCK) '{  e_ctx_hnd policy_hnd ;  char * pol_na...'
Node 25769803779: (BLOCK) '<empty>'
Node 30064771073: (CALL) 'offset = dissect_nt_policy_hnd ( tvb , o...'
Node 30064771074: (CALL) 'dissect_nt_policy_hnd ( tvb , offset , p...'
Node 30064771075: (CALL) '& policy_hnd'
Node 30064771076: (CALL) 'dcerpc_fetch_polhnd_data ( & policy_hnd ...'
Node 30064771077: (CALL) '& policy_hnd'
Node 30064771078: (CALL) '& pol_name'
Node 30064771079: (CALL) 'pinfo -> num'
Node 30064771080: (CALL) 'pol_name != NULL'
Node 30064771081: (CALL) 'col_append_fstr ( pinfo -> cinfo , COL_I...'
Node 30064771082: (CALL) 'pinfo -> cinfo'
Node 47244640256: (CONTROL_STRUCTURE) 'if ( pol_name ) col_append_fstr ( pinfo ...'
Node 55834574848: (FIELD_IDENTIFIER) 'num'
Node 55834574849: (FIELD_IDENTIFIER) 'cinfo'
Node 68719476738: (IDENTIFIER) 'offset'
Node 68719476739: (IDENTIFIER) 'tvb'
Node 68719476740: (IDENTIFIER) 'offset'
Node 68719476741: (IDENTIFIER) 'pinfo'
Node 68719476742: (IDENTIFIER) 'tree'
Node 68719476743: (IDENTIFIER) 'di'
Node 68719476744: (IDENTIFIER) 'drep'
Node 68719476745: (IDENTIFIER) '<unknown> hf_hnd'
Node 68719476746: (IDENTIFIER) 'policy_hnd'
Node 68719476747: (IDENTIFIER) '<unknown> NULL'
Node 68719476748: (IDENTIFIER) '<unknown> FALSE'
Node 68719476749: (IDENTIFIER) '<unknown> FALSE'
Node 68719476750: (IDENTIFIER) 'policy_hnd'
Node 68719476751: (IDENTIFIER) 'pol_name'
Node 68719476752: (IDENTIFIER) '<unknown> NULL'
Node 68719476753: (IDENTIFIER) '<unknown> NULL'
Node 68719476754: (IDENTIFIER) '<unknown> NULL'
Node 68719476755: (IDENTIFIER) 'pinfo'
Node 68719476756: (IDENTIFIER) 'pol_name'
Node 68719476757: (IDENTIFIER) 'pinfo'
Node 68719476758: (IDENTIFIER) '<unknown> COL_INFO'
Node 68719476759: (IDENTIFIER) 'pol_name'
Node 68719476760: (IDENTIFIER) 'offset'
Node 90194313217: (LITERAL) 'NULL'
Node 90194313218: (LITERAL) '", %s"'
The edge information of the code snippet is as follows:
Edge: Node 25769803778 -> AST -> Node 30064771073
Edge: Node 25769803778 -> AST -> Node 30064771076
Edge: Node 25769803778 -> AST -> Node 47244640256
Edge: Node 25769803779 -> AST -> Node 30064771081
Edge: Node 30064771073 -> ARGUMENT -> Node 68719476738
Edge: Node 30064771073 -> ARGUMENT -> Node 30064771074
Edge: Node 30064771073 -> AST -> Node 68719476738
Edge: Node 30064771073 -> AST -> Node 30064771074
Edge: Node 30064771073 -> CFG -> Node 68719476750
Edge: Node 30064771073 -> DOMINATE -> Node 68719476750
Edge: Node 30064771073 -> POST_DOMINATE -> Node 30064771074
Edge: Node 30064771074 -> ARGUMENT -> Node 68719476739
Edge: Node 30064771074 -> ARGUMENT -> Node 68719476740
Edge: Node 30064771074 -> ARGUMENT -> Node 68719476741
Edge: Node 30064771074 -> ARGUMENT -> Node 68719476742
Edge: Node 30064771074 -> ARGUMENT -> Node 68719476743

The following is an example, and it is Non-vulnerable.
static int dissect_h245_Params ( tvbuff_t * tvb _U_ , int offset _U_ , asn1_ctx_t * actx _U_ , proto_tree * tree _U_ , int hf_index _U_ ) {
 offset = dissect_per_sequence ( tvb , offset , actx , tree , hf_index , ett_h245_Params , Params_sequence ) ;
 return offset ;
 }

Answer (0 or 1):
```

