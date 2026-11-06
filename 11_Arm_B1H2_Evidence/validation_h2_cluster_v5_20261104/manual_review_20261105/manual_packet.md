# Manual review packet — B1-H2 v5

## Sample 01 · devign · B1-H2 · seed 42

ID: `devign:validation:11075`  
Prompt SHA-256: `80b1e415291a5a3ec15c814314250c42179ebdc08a8925c0333be4f87b607aa0`  
Stratum: `closed_prefix`

~~~~~text
You are now an excellent programmer. You are conducting a function vulnerability detection task for C/C++ language.

int kvm_init(void)

{

    static const char upgrade_note[] =

        "Please upgrade to at least kernel 2.6.29 or recent kvm-kmod\n"

        "(see http://sourceforge.net/projects/kvm).\n";

    KVMState *s;

    const KVMCapabilityInfo *missing_cap;

    int ret;

    int i;



    s = g_malloc0(sizeof(KVMState));



#ifdef KVM_CAP_SET_GUEST_DEBUG

    QTAILQ_INIT(&s->kvm_sw_breakpoints);

#endif

    for (i = 0; i < ARRAY_SIZE(s->slots); i++) {

        s->slots[i].slot = i;

    }

    s->vmfd = -1;

    s->fd = qemu_open("/dev/kvm", O_RDWR);

    if (s->fd == -1) {

        fprintf(stderr, "Could not access KVM kernel module: %m\n");

        ret = -errno;

        goto err;

    }



    ret = kvm_ioctl(s, KVM_GET_API_VERSION, 0);

    if (ret < KVM_API_VERSION) {

        if (ret > 0) {

            ret = -EINVAL;

        }

        fprintf(stderr, "kvm version too old\n");

        goto err;

    }



    if (ret > KVM_API_VERSION) {

        ret = -EINVAL;

        fprintf(stderr, "kvm version not supported\n");

        goto err;

    }



    s->vmfd = kvm_ioctl(s, KVM_CREATE_VM, 0);

    if (s->vmfd < 0) {

#ifdef TARGET_S390X

        fprintf(stderr, "Please add the 'switch_amode' kernel parameter to "

                        "your host kernel command line\n");

#endif

        ret = s->vmfd;

        goto err;

    }



    missing_cap = kvm_check_extension_list(s, kvm_required_capabilites);

    if (!missing_cap) {

        missing_cap =

            kvm_check_extension_list(s, kvm_arch_required_capabilities);

    }

    if (missing_cap) {

        ret = -EINVAL;

        fprintf(stderr, "kvm does not support %s\n%s",

                missing_cap->name, upgrade_note);

        goto err;

    }



    s->coalesced_mmio = kvm_check_extension(s, KVM_CAP_COALESCED_MMIO);



    s->broken_set_mem_region = 1;

    ret = kvm_check_extension(s, KVM_CAP_JOIN_MEMORY_REGIONS_WORKS);

    if (ret > 0) {

        s->broken_set_mem_region = 0;

    }



#ifdef KVM_CAP_VCPU_EVENTS

    s->vcpu_events = kvm_check_extension(s, KVM_CAP_VCPU_EVENTS);

#endif



    s->robust_singlestep =

        kvm_check_extension(s, KVM_CAP_X86_ROBUST_SINGLESTEP);



#ifdef KVM_CAP_DEBUGREGS

    s->debugregs = kvm_check_extension(s, KVM_CAP_DEBUGREGS);

#endif



#ifdef KVM_CAP_XSAVE

    s->xsave = kvm_check_extension(s, KVM_CAP_XSAVE);

#endif



#ifdef KVM_CAP_XCRS

    s->xcrs = kvm_check_extension(s, KVM_CAP_XCRS);

#endif



    ret = kvm_arch_init(s);

    if (ret < 0) {

        goto err;

    }



    kvm_state = s;

    cpu_register_phys_memory_client(&kvm_cpu_phys_memory_client);



    s->many_ioeventfds = kvm_check_many_ioeventfds();



    cpu_interrupt_handler = kvm_handle_interrupt;



    return 0;



err:

    if (s) {

        if (s->vmfd >= 0) {

            close(s->vmfd);

        }

        if (s->fd != -1) {

            close(s->fd);

        }

    }

    g_free(s);



    return ret;

}

In the above code snippet, check for potential security vulnerabilities and answer with a single digit: 1 if Vulnerable, 0 if Non-vulnerable.

The guarded evidence of the code snippet is as follows:
GUARDED EVIDENCE: operation-specific observed relations; not a safety proof.
N1 CALL "i < ARRAY_SIZE(s->slots)"
N2 CALL "s->slots"
N3 CALL "s->slots[i]"
N4 CALL "s->slots"
N5 CALL "s->fd == -1"
N6 CALL "-errno"
N1 --CDG--> N2
N1 --CDG--> N3
N1 --CDG--> N4
N2 --REACHING_DEF--> N4
N3 --ARGUMENT--> N4
N5 --CDG--> N6
OP N2
  INPUTS not included/unknown
  DIRECT_CONTROL N1 via=CDG branch=unknown check=cdg_observed_cfg_unknown
OP N3
  INPUTS N4
  DIRECT_CONTROL N1 via=CDG branch=unknown check=cdg_observed_cfg_unknown
  DATA_NOTE: predicates on related data are not operation controls.
OP N4
  INPUTS not included/unknown
  DIRECT_CONTROL N1 via=CDG branch=unknown check=cdg_observed_cfg_unknown
  DATA_NOTE: predicates on related data are not operation controls.
OP N6
  INPUTS not included/unknown
  DIRECT_CONTROL N5 via=CDG branch=unknown check=cdg_observed_cfg_unknown
UNKNOWN: guard sufficiency, aliasing and feasible execution paths. Missing polarity is unknown.
BOUNDED: omitted operations/context and shortened snippets are not proof of absence.

The following is an example, and it is .


Answer (0 or 1):
~~~~~

## Sample 02 · devign · B1-H2 · seed 42

ID: `devign:validation:11611`  
Prompt SHA-256: `c7cd3a2eec8349d4ff8cfebe388f7cc1115a4beaf10c66e4f5cc0fe7bd0c2973`  
Stratum: `closed_prefix`

~~~~~text
You are now an excellent programmer. You are conducting a function vulnerability detection task for C/C++ language.

static int pte64_check(struct mmu_ctx_hash64 *ctx, target_ulong pte0,

                       target_ulong pte1, int h, int rwx)

{

    target_ulong mmask;

    int access, ret, pp;



    ret = -1;

    /* Check validity and table match */

    if ((pte0 & HPTE64_V_VALID) && (h == !!(pte0 & HPTE64_V_SECONDARY))) {

        bool nx;



        /* Check vsid & api */

        mmask = PTE64_CHECK_MASK;

        pp = (pte1 & HPTE64_R_PP) | ((pte1 & HPTE64_R_PP0) >> 61);

        /* No execute if either noexec or guarded bits set */

        nx = (pte1 & HPTE64_R_N) || (pte1 & HPTE64_R_G);

        if (HPTE64_V_COMPARE(pte0, ctx->ptem)) {

            if (ctx->raddr != (hwaddr)-1ULL) {

                /* all matches should have equal RPN, WIMG & PP */

                if ((ctx->raddr & mmask) != (pte1 & mmask)) {

                    qemu_log("Bad RPN/WIMG/PP\n");

                    return -3;

                }

            }

            /* Compute access rights */

            access = ppc_hash64_pp_check(ctx->key, pp, nx);

            /* Keep the matching PTE informations */

            ctx->raddr = pte1;

            ctx->prot = access;

            ret = ppc_hash64_check_prot(ctx->prot, rwx);

            if (ret == 0) {

                /* Access granted */

                LOG_MMU("PTE access granted !\n");

            } else {

                /* Access right violation */

                LOG_MMU("PTE access rejected\n");

            }

        }

    }



    return ret;

}

In the above code snippet, check for potential security vulnerabilities and answer with a single digit: 1 if Vulnerable, 0 if Non-vulnerable.

The guarded evidence of the code snippet is as follows:
GUARDED EVIDENCE: operation-specific observed relations; not a safety proof.
N1 CALL "(pte0 & HPTE64_V_VALID) && (h == !!(pte0 & HPTE64_V_SECONDARY))"
N2 CALL "HPTE64_V_COMPARE(pte0, ctx->ptem)"
N3 CALL "ctx->ptem"
N4 CALL "ctx->raddr"
N5 CALL "ctx->raddr"
N1 --CDG--> N2
N1 --CDG--> N3
OP N3
  INPUTS not included/unknown
  DIRECT_CONTROL N1 via=CDG branch=unknown check=cdg_observed_cfg_unknown
OP N2
  INPUTS not included/unknown
  DIRECT_CONTROL N1 via=CDG branch=unknown check=cdg_observed_cfg_unknown
OP N4
  INPUTS not included/unknown
  DIRECT_CONTROL none observed; not proof of absence
OP N5
  INPUTS not included/unknown
  DIRECT_CONTROL none observed; not proof of absence
UNKNOWN: guard sufficiency, aliasing and feasible execution paths. Missing polarity is unknown.
BOUNDED: omitted operations/context and shortened snippets are not proof of absence.

The following is an example, and it is .


Answer (0 or 1):
~~~~~

## Sample 03 · devign · B1-H2 · seed 42

ID: `devign:validation:1324`  
Prompt SHA-256: `13fd5a82e6885e15580ac48e80ece1ef4d9339aed517ec0a3c8bc1449b04f1f6`  
Stratum: `no_usable_evidence`

~~~~~text
You are now an excellent programmer. You are conducting a function vulnerability detection task for C/C++ language.

av_cold void ff_videodsp_init_x86(VideoDSPContext *ctx, int bpc)

{

#if HAVE_YASM

    int cpu_flags = av_get_cpu_flags();



#if ARCH_X86_32

    if (EXTERNAL_MMX(cpu_flags) && bpc <= 8) {

        ctx->emulated_edge_mc = emulated_edge_mc_mmx;

    }

    if (EXTERNAL_AMD3DNOW(cpu_flags)) {

        ctx->prefetch = ff_prefetch_3dnow;

    }

#endif /* ARCH_X86_32 */

    if (EXTERNAL_MMXEXT(cpu_flags)) {

        ctx->prefetch = ff_prefetch_mmxext;

#if ARCH_X86_32

        if (bpc <= 8)

            ctx->emulated_edge_mc = emulated_edge_mc_mmxext;

#endif /* ARCH_X86_32 */

    }

#if ARCH_X86_32

    if (EXTERNAL_SSE(cpu_flags) && bpc <= 8) {

        ctx->emulated_edge_mc = emulated_edge_mc_sse;

    }

#endif /* ARCH_X86_32 */

    if (EXTERNAL_SSE2(cpu_flags) && bpc <= 8) {

        ctx->emulated_edge_mc = emulated_edge_mc_sse2;

    }

#endif /* HAVE_YASM */

}

In the above code snippet, check for potential security vulnerabilities and answer with a single digit: 1 if Vulnerable, 0 if Non-vulnerable.

The guarded evidence of the code snippet is as follows:
NO_USABLE_GUARDED_EVIDENCE: no_operation_nodes. Do not infer safety from missing evidence.

The following is an example, and it is .


Answer (0 or 1):
~~~~~

## Sample 04 · devign · B1-H2 · seed 42

ID: `devign:validation:14587`  
Prompt SHA-256: `ad2aed04cfd60b5ac30737c949255ca88aa11033d244f137b7c66db233d52c27`  
Stratum: `cdg_cluster`

~~~~~text
You are now an excellent programmer. You are conducting a function vulnerability detection task for C/C++ language.

static uint64_t pxa2xx_cm_read(void *opaque, hwaddr addr,

                               unsigned size)

{

    PXA2xxState *s = (PXA2xxState *) opaque;



    switch (addr) {

    case CCCR:

    case CKEN:

    case OSCC:

        return s->cm_regs[addr >> 2];



    case CCSR:

        return s->cm_regs[CCCR >> 2] | (3 << 28);



    default:

        printf("%s: Bad register " REG_FMT "\n", __FUNCTION__, addr);

        break;

    }

    return 0;

}

In the above code snippet, check for potential security vulnerabilities and answer with a single digit: 1 if Vulnerable, 0 if Non-vulnerable.

The guarded evidence of the code snippet is as follows:
GUARDED EVIDENCE: operation-specific observed relations; not a safety proof.
N1 RETURN "return 0;"
N2 CALL "s->cm_regs[addr >> 2]"
N3 CALL "s->cm_regs"
N4 CALL "addr >> 2"
N5 CALL "s->cm_regs[CCCR >> 2]"
N6 CALL "s->cm_regs"
N7 CONTROL_STRUCTURE "break;"
N8 FIELD_IDENTIFIER "cm_regs"
N9 IDENTIFIER "addr"
N10 IDENTIFIER "s"
N11 IDENTIFIER "addr"
N12 JUMP_TARGET "default:"
N13 LITERAL "2"
N14 LITERAL "0"
N2 --ARGUMENT--> N3
N2 --ARGUMENT--> N4
N3 --ARGUMENT--> N8
N3 --ARGUMENT--> N10
N4 --ARGUMENT--> N11
N4 --ARGUMENT--> N13
N7 --CFG--> N14
N9 --CDG--> N2
N9 --CDG--> N3
N9 --CDG--> N5
N9 --CDG--> N6
N9 --CFG--> N12
N12 --CFG--> N7
N14 --CFG--> N1
OP N2
  INPUTS N3,N4
  DIRECT_CONTROL N9 via=CDG branch=unknown check=cdg_observed_cfg_unknown
  OBSERVED_EXIT N1 from=N9 branch=unknown
  DATA_NOTE: predicates on related data are not operation controls.
OP N3
  INPUTS N8,N10
  DIRECT_CONTROL N9 via=CDG branch=unknown check=cdg_observed_cfg_unknown
  OBSERVED_EXIT N1 from=N9 branch=unknown
OP N5
  INPUTS not included/unknown
  DIRECT_CONTROL N9 via=CDG branch=unknown check=cfg_one_branch_witness
  OBSERVED_EXIT N1 from=N9 branch=unknown
OP N6
  INPUTS not included/unknown
  DIRECT_CONTROL N9 via=CDG branch=unknown check=cfg_one_branch_witness
  OBSERVED_EXIT N1 from=N9 branch=unknown
UNKNOWN: guard sufficiency, aliasing and feasible execution paths. Missing polarity is unknown.
BOUNDED: omitted operations/context and shortened snippets are not proof of absence.

The following is an example, and it is .


Answer (0 or 1):
~~~~~

## Sample 05 · devign · B1-H2 · seed 42

ID: `devign:validation:14819`  
Prompt SHA-256: `fe66c147d54d84e377f54f546373d3c8b32e29f9e5154457a60c8af85434a449`  
Stratum: `missing_cpg`

~~~~~text
You are now an excellent programmer. You are conducting a function vulnerability detection task for C/C++ language.

static av_noinline void FUNC(hl_decode_mb)(H264Context *h)

{

    const int mb_x    = h->mb_x;

    const int mb_y    = h->mb_y;

    const int mb_xy   = h->mb_xy;

    const int mb_type = h->cur_pic.f.mb_type[mb_xy];

    uint8_t *dest_y, *dest_cb, *dest_cr;

    int linesize, uvlinesize /*dct_offset*/;

    int i, j;

    int *block_offset = &h->block_offset[0];

    const int transform_bypass = !SIMPLE && (h->qscale == 0 && h->sps.transform_bypass);

    /* is_h264 should always be true if SVQ3 is disabled. */

    const int is_h264 = !CONFIG_SVQ3_DECODER || SIMPLE || h->avctx->codec_id == AV_CODEC_ID_H264;

    void (*idct_add)(uint8_t *dst, int16_t *block, int stride);

    const int block_h   = 16 >> h->chroma_y_shift;

    const int chroma422 = CHROMA422;



    dest_y  = h->cur_pic.f.data[0] + ((mb_x << PIXEL_SHIFT)     + mb_y * h->linesize)  * 16;

    dest_cb = h->cur_pic.f.data[1] +  (mb_x << PIXEL_SHIFT) * 8 + mb_y * h->uvlinesize * block_h;

    dest_cr = h->cur_pic.f.data[2] +  (mb_x << PIXEL_SHIFT) * 8 + mb_y * h->uvlinesize * block_h;



    h->vdsp.prefetch(dest_y  + (h->mb_x & 3) * 4 * h->linesize   + (64 << PIXEL_SHIFT), h->linesize,       4);

    h->vdsp.prefetch(dest_cb + (h->mb_x & 7)     * h->uvlinesize + (64 << PIXEL_SHIFT), dest_cr - dest_cb, 2);



    h->list_counts[mb_xy] = h->list_count;



    if (!SIMPLE && MB_FIELD) {

        linesize     = h->mb_linesize = h->linesize * 2;

        uvlinesize   = h->mb_uvlinesize = h->uvlinesize * 2;

        block_offset = &h->block_offset[48];

        if (mb_y & 1) { // FIXME move out of this function?

            dest_y  -= h->linesize * 15;

            dest_cb -= h->uvlinesize * (block_h - 1);

            dest_cr -= h->uvlinesize * (block_h - 1);

        }

        if (FRAME_MBAFF) {

            int list;

            for (list = 0; list < h->list_count; list++) {

                if (!USES_LIST(mb_type, list))

                    continue;

                if (IS_16X16(mb_type)) {

                    int8_t *ref = &h->ref_cache[list][scan8[0]];

                    fill_rectangle(ref, 4, 4, 8, (16 + *ref) ^ (h->mb_y & 1), 1);

                } else {

                    for (i = 0; i < 16; i += 4) {

                        int ref = h->ref_cache[list][scan8[i]];

                        if (ref >= 0)

                            fill_rectangle(&h->ref_cache[list][scan8[i]], 2, 2,

                                           8, (16 + ref) ^ (h->mb_y & 1), 1);

                    }

                }

            }

        }

    } else {

        linesize   = h->mb_linesize   = h->linesize;

        uvlinesize = h->mb_uvlinesize = h->uvlinesize;

        // dct_offset = s->linesize * 16;

    }



    if (!SIMPLE && IS_INTRA_PCM(mb_type)) {

        const int bit_depth = h->sps.bit_depth_luma;

        if (PIXEL_SHIFT) {

            int j;

            GetBitContext gb;

            init_get_bits(&gb, (uint8_t *)h->intra_pcm_ptr,

                          ff_h264_mb_sizes[h->sps.chroma_format_idc] * bit_depth);



            for (i = 0; i < 16; i++) {

                uint16_t *tmp_y = (uint16_t *)(dest_y + i * linesize);

                for (j = 0; j < 16; j++)

                    tmp_y[j] = get_bits(&gb, bit_depth);

            }

            if (SIMPLE || !CONFIG_GRAY || !(h->flags & CODEC_FLAG_GRAY)) {

                if (!h->sps.chroma_format_idc) {

                    for (i = 0; i < block_h; i++) {

                        uint16_t *tmp_cb = (uint16_t *)(dest_cb + i * uvlinesize);

                        uint16_t *tmp_cr = (uint16_t *)(dest_cr + i * uvlinesize);

                        for (j = 0; j < 8; j++) {

                            tmp_cb[j] = tmp_cr[j] = 1 << (bit_depth - 1);

                        }

                    }

                } else {

                    for (i = 0; i < block_h; i++) {

                        uint16_t *tmp_cb = (uint16_t *)(dest_cb + i * uvlinesize);

                        for (j = 0; j < 8; j++)

                            tmp_cb[j] = get_bits(&gb, bit_depth);

                    }

                    for (i = 0; i < block_h; i++) {

                        uint16_t *tmp_cr = (uint16_t *)(dest_cr + i * uvlinesize);

                        for (j = 0; j < 8; j++)

                            tmp_cr[j] = get_bits(&gb, bit_depth);

                    }

                }

            }

        } else {

            for (i = 0; i < 16; i++)

                memcpy(dest_y + i * linesize, (uint8_t *)h->intra_pcm_ptr + i * 16, 16);

            if (SIMPLE || !CONFIG_GRAY || !(h->flags & CODEC_FLAG_GRAY)) {

                if (!h->sps.chroma_format_idc) {

                    for (i = 0; i < 8; i++) {

                        memset(dest_cb + i*uvlinesize, 1 << (bit_depth - 1), 8);

                        memset(dest_cr + i*uvlinesize, 1 << (bit_depth - 1), 8);

                    }

                } else {

                    uint8_t *src_cb = (uint8_t *)h->intra_pcm_ptr + 256;

                    uint8_t *src_cr = (uint8_t *)h->intra_pcm_ptr + 256 + block_h * 8;

                    for (i = 0; i < block_h; i++) {

                        memcpy(dest_cb + i * uvlinesize, src_cb + i * 8, 8);

                        memcpy(dest_cr + i * uvlinesize, src_cr + i * 8, 8);

                    }

                }

            }

        }

    } else {

        if (IS_INTRA(mb_type)) {

            if (h->deblocking_filter)

                xchg_mb_border(h, dest_y, dest_cb, dest_cr, linesize,

                               uvlinesize, 1, 0, SIMPLE, PIXEL_SHIFT);



            if (SIMPLE || !CONFIG_GRAY || !(h->flags & CODEC_FLAG_GRAY)) {

                h->hpc.pred8x8[h->chroma_pred_mode](dest_cb, uvlinesize);

                h->hpc.pred8x8[h->chroma_pred_mode](dest_cr, uvlinesize);

            }



            hl_decode_mb_predict_luma(h, mb_type, is_h264, SIMPLE,

                                      transform_bypass, PIXEL_SHIFT,

                                      block_offset, linesize, dest_y, 0);



            if (h->deblocking_filter)

                xchg_mb_border(h, dest_y, dest_cb, dest_cr, linesize,

                               uvlinesize, 0, 0, SIMPLE, PIXEL_SHIFT);

        } else if (is_h264) {

            if (chroma422) {

                FUNC(hl_motion_422)(h, dest_y, dest_cb, dest_cr,

                              h->me.qpel_put, h->h264chroma.put_h264_chroma_pixels_tab,

                              h->me.qpel_avg, h->h264chroma.avg_h264_chroma_pixels_tab,

                              h->h264dsp.weight_h264_pixels_tab,

                              h->h264dsp.biweight_h264_pixels_tab);

            } else {

                FUNC(hl_motion_420)(h, dest_y, dest_cb, dest_cr,

                              h->me.qpel_put, h->h264chroma.put_h264_chroma_pixels_tab,

                              h->me.qpel_avg, h->h264chroma.avg_h264_chroma_pixels_tab,

                              h->h264dsp.weight_h264_pixels_tab,

                              h->h264dsp.biweight_h264_pixels_tab);

            }

        }



        hl_decode_mb_idct_luma(h, mb_type, is_h264, SIMPLE, transform_bypass,

                               PIXEL_SHIFT, block_offset, linesize, dest_y, 0);



        if ((SIMPLE || !CONFIG_GRAY || !(h->flags & CODEC_FLAG_GRAY)) &&

            (h->cbp & 0x30)) {

            uint8_t *dest[2] = { dest_cb, dest_cr };

            if (transform_bypass) {

                if (IS_INTRA(mb_type) && h->sps.profile_idc == 244 &&

                    (h->chroma_pred_mode == VERT_PRED8x8 ||

                     h->chroma_pred_mode == HOR_PRED8x8)) {

                    h->hpc.pred8x8_add[h->chroma_pred_mode](dest[0],

                                                            block_offset + 16,

                                                            h->mb + (16 * 16 * 1 << PIXEL_SHIFT),

                                                            uvlinesize);

                    h->hpc.pred8x8_add[h->chroma_pred_mode](dest[1],

                                                            block_offset + 32,

                                                            h->mb + (16 * 16 * 2 << PIXEL_SHIFT),

                                                            uvlinesize);

                } else {

                    idct_add = h->h264dsp.h264_add_pixels4;

                    for (j = 1; j < 3; j++) {

                        for (i = j * 16; i < j * 16 + 4; i++)

                            if (h->non_zero_count_cache[scan8[i]] ||

                                dctcoef_get(h->mb, PIXEL_SHIFT, i * 16))

                                idct_add(dest[j - 1] + block_offset[i],

                                         h->mb + (i * 16 << PIXEL_SHIFT),

                                         uvlinesize);

                        if (chroma422) {

                            for (i = j * 16 + 4; i < j * 16 + 8; i++)

                                if (h->non_zero_count_cache[scan8[i + 4]] ||

                                    dctcoef_get(h->mb, PIXEL_SHIFT, i * 16))

                                    idct_add(dest[j - 1] + block_offset[i + 4],

                                             h->mb + (i * 16 << PIXEL_SHIFT),

                                             uvlinesize);

                        }

                    }

                }

            } else {

                if (is_h264) {

                    int qp[2];

                    if (chroma422) {

                        qp[0] = h->chroma_qp[0] + 3;

                        qp[1] = h->chroma_qp[1] + 3;

                    } else {

                        qp[0] = h->chroma_qp[0];

                        qp[1] = h->chroma_qp[1];

                    }

                    if (h->non_zero_count_cache[scan8[CHROMA_DC_BLOCK_INDEX + 0]])

                        h->h264dsp.h264_chroma_dc_dequant_idct(h->mb + (16 * 16 * 1 << PIXEL_SHIFT),

                                                               h->dequant4_coeff[IS_INTRA(mb_type) ? 1 : 4][qp[0]][0]);

                    if (h->non_zero_count_cache[scan8[CHROMA_DC_BLOCK_INDEX + 1]])

                        h->h264dsp.h264_chroma_dc_dequant_idct(h->mb + (16 * 16 * 2 << PIXEL_SHIFT),

                                                               h->dequant4_coeff[IS_INTRA(mb_type) ? 2 : 5][qp[1]][0]);

                    h->h264dsp.h264_idct_add8(dest, block_offset,

                                              h->mb, uvlinesize,

                                              h->non_zero_count_cache);

                } else if (CONFIG_SVQ3_DECODER) {

                    h->h264dsp.h264_chroma_dc_dequant_idct(h->mb + 16 * 16 * 1,

                                                           h->dequant4_coeff[IS_INTRA(mb_type) ? 1 : 4][h->chroma_qp[0]][0]);

                    h->h264dsp.h264_chroma_dc_dequant
/* [TRUNCATED TARGET] */

In the above code snippet, check for potential security vulnerabilities and answer with a single digit: 1 if Vulnerable, 0 if Non-vulnerable.

The node information of the code snippet is as follows:

The edge information of the code snippet is as follows:


The following is an example, and it is .


Answer (0 or 1):
~~~~~

## Sample 06 · devign · B1-H2 · seed 42

ID: `devign:validation:15296`  
Prompt SHA-256: `389617a49a6b42b593770df38e3f261528472f5a1e2dd659e43b0e25959ab1b7`  
Stratum: `cdg_cluster`

~~~~~text
You are now an excellent programmer. You are conducting a function vulnerability detection task for C/C++ language.

static int decode_nal_sei_prefix(GetBitContext *gb, HEVCSEIContext *s, const HEVCParamSets *ps,

                                 int type, int size, void *logctx)

{

    switch (type) {

    case 256:  // Mismatched value from HM 8.1

        return decode_nal_sei_decoded_picture_hash(&s->picture_hash, gb);

    case HEVC_SEI_TYPE_FRAME_PACKING:

        return decode_nal_sei_frame_packing_arrangement(&s->frame_packing, gb);

    case HEVC_SEI_TYPE_DISPLAY_ORIENTATION:

        return decode_nal_sei_display_orientation(&s->display_orientation, gb);

    case HEVC_SEI_TYPE_PICTURE_TIMING:

        {

            int ret = decode_pic_timing(s, gb, ps, logctx);

            av_log(logctx, AV_LOG_DEBUG, "Skipped PREFIX SEI %d\n", type);

            skip_bits(gb, 8 * size);

            return ret;

        }

    case HEVC_SEI_TYPE_MASTERING_DISPLAY_INFO:

        return decode_nal_sei_mastering_display_info(&s->mastering_display, gb);

    case HEVC_SEI_TYPE_CONTENT_LIGHT_LEVEL_INFO:

        return decode_nal_sei_content_light_info(&s->content_light, gb);

    case HEVC_SEI_TYPE_ACTIVE_PARAMETER_SETS:

        active_parameter_sets(s, gb, logctx);

        av_log(logctx, AV_LOG_DEBUG, "Skipped PREFIX SEI %d\n", type);

        return 0;

    case HEVC_SEI_TYPE_USER_DATA_REGISTERED_ITU_T_T35:

        return decode_nal_sei_user_data_registered_itu_t_t35(s, gb, size);

    default:

        av_log(logctx, AV_LOG_DEBUG, "Skipped PREFIX SEI %d\n", type);

        skip_bits_long(gb, 8 * size);

        return 0;

    }

}

In the above code snippet, check for potential security vulnerabilities and answer with a single digit: 1 if Vulnerable, 0 if Non-vulnerable.

The guarded evidence of the code snippet is as follows:
GUARDED EVIDENCE: operation-specific observed relations; not a safety proof.
N1 CALL "s->picture_hash"
N2 CALL "s->frame_packing"
N3 CALL "s->display_orientation"
N4 CALL "s->mastering_display"
N5 FIELD_IDENTIFIER "picture_hash"
N6 FIELD_IDENTIFIER "frame_packing"
N7 FIELD_IDENTIFIER "display_orientation"
N8 IDENTIFIER "type"
N9 IDENTIFIER "s"
N10 IDENTIFIER "s"
N11 IDENTIFIER "s"
N1 --ARGUMENT--> N5
N1 --ARGUMENT--> N9
N2 --ARGUMENT--> N6
N2 --ARGUMENT--> N10
N3 --ARGUMENT--> N7
N3 --ARGUMENT--> N11
N8 --CDG--> N1
N8 --CDG--> N2
N8 --CDG--> N3
N8 --CDG--> N4
OP N1
  INPUTS N5,N9
  DIRECT_CONTROL N8 via=CDG branch=unknown check=cdg_observed_cfg_unknown
OP N2
  INPUTS N6,N10
  DIRECT_CONTROL N8 via=CDG branch=unknown check=cdg_observed_cfg_unknown
OP N3
  INPUTS N7,N11
  DIRECT_CONTROL N8 via=CDG branch=unknown check=cdg_observed_cfg_unknown
OP N4
  INPUTS not included/unknown
  DIRECT_CONTROL N8 via=CDG branch=unknown check=cdg_observed_cfg_unknown
UNKNOWN: guard sufficiency, aliasing and feasible execution paths. Missing polarity is unknown.
BOUNDED: omitted operations/context and shortened snippets are not proof of absence.

The following is an example, and it is .


Answer (0 or 1):
~~~~~

## Sample 07 · devign · B1-H2 · seed 42

ID: `devign:validation:15976`  
Prompt SHA-256: `9b2abf87d6aa08c4d3179a042ab34084f5c711aecb2f2cf717844e7c26710838`  
Stratum: `closed_prefix`

~~~~~text
You are now an excellent programmer. You are conducting a function vulnerability detection task for C/C++ language.

static int check_refcounts_l2(BlockDriverState *bs, BdrvCheckResult *res,

                              void **refcount_table,

                              int64_t *refcount_table_size, int64_t l2_offset,

                              int flags)

{

    BDRVQcow2State *s = bs->opaque;

    uint64_t *l2_table, l2_entry;

    uint64_t next_contiguous_offset = 0;

    int i, l2_size, nb_csectors, ret;



    /* Read L2 table from disk */

    l2_size = s->l2_size * sizeof(uint64_t);

    l2_table = g_malloc(l2_size);



    ret = bdrv_pread(bs->file, l2_offset, l2_table, l2_size);

    if (ret < 0) {

        fprintf(stderr, "ERROR: I/O error in check_refcounts_l2\n");

        res->check_errors++;

        goto fail;

    }



    /* Do the actual checks */

    for(i = 0; i < s->l2_size; i++) {

        l2_entry = be64_to_cpu(l2_table[i]);



        switch (qcow2_get_cluster_type(l2_entry)) {

        case QCOW2_CLUSTER_COMPRESSED:

            /* Compressed clusters don't have QCOW_OFLAG_COPIED */

            if (l2_entry & QCOW_OFLAG_COPIED) {

                fprintf(stderr, "ERROR: cluster %" PRId64 ": "

                    "copied flag must never be set for compressed "

                    "clusters\n", l2_entry >> s->cluster_bits);

                l2_entry &= ~QCOW_OFLAG_COPIED;

                res->corruptions++;

            }



            /* Mark cluster as used */

            nb_csectors = ((l2_entry >> s->csize_shift) &

                           s->csize_mask) + 1;

            l2_entry &= s->cluster_offset_mask;

            ret = inc_refcounts(bs, res, refcount_table, refcount_table_size,

                                l2_entry & ~511, nb_csectors * 512);

            if (ret < 0) {

                goto fail;

            }



            if (flags & CHECK_FRAG_INFO) {

                res->bfi.allocated_clusters++;

                res->bfi.compressed_clusters++;



                /* Compressed clusters are fragmented by nature.  Since they

                 * take up sub-sector space but we only have sector granularity

                 * I/O we need to re-read the same sectors even for adjacent

                 * compressed clusters.

                 */

                res->bfi.fragmented_clusters++;

            }

            break;



        case QCOW2_CLUSTER_ZERO:

            if ((l2_entry & L2E_OFFSET_MASK) == 0) {

                break;

            }

            /* fall through */



        case QCOW2_CLUSTER_NORMAL:

        {

            uint64_t offset = l2_entry & L2E_OFFSET_MASK;



            if (flags & CHECK_FRAG_INFO) {

                res->bfi.allocated_clusters++;

                if (next_contiguous_offset &&

                    offset != next_contiguous_offset) {

                    res->bfi.fragmented_clusters++;

                }

                next_contiguous_offset = offset + s->cluster_size;

            }



            /* Mark cluster as used */

            ret = inc_refcounts(bs, res, refcount_table, refcount_table_size,

                                offset, s->cluster_size);

            if (ret < 0) {

                goto fail;

            }



            /* Correct offsets are cluster aligned */

            if (offset_into_cluster(s, offset)) {

                fprintf(stderr, "ERROR offset=%" PRIx64 ": Cluster is not "

                    "properly aligned; L2 entry corrupted.\n", offset);

                res->corruptions++;

            }

            break;

        }



        case QCOW2_CLUSTER_UNALLOCATED:

            break;



        default:

            abort();

        }

    }



    g_free(l2_table);

    return 0;



fail:

    g_free(l2_table);

    return ret;

}

In the above code snippet, check for potential security vulnerabilities and answer with a single digit: 1 if Vulnerable, 0 if Non-vulnerable.

The guarded evidence of the code snippet is as follows:
GUARDED EVIDENCE: operation-specific observed relations; not a safety proof.
N1 CALL "s->l2_size"
N2 CALL "ret < 0"
N3 CALL "fprintf(stderr, \"ERROR: I/O error in check_refcounts_l2\\n\")"
N4 CALL "res->check_errors"
N5 CALL "i < s->l2_size"
N6 CALL "s->l2_size"
N7 CALL "l2_table[i]"
N1 --REACHING_DEF--> N6
N2 --CDG--> N3
N2 --CDG--> N4
N2 --CDG--> N6
N5 --CDG--> N7
OP N4
  INPUTS not included/unknown
  DIRECT_CONTROL N2 via=CDG branch=unknown check=cdg_observed_cfg_unknown
OP N6
  INPUTS not included/unknown
  DIRECT_CONTROL N2 via=CDG branch=unknown check=cdg_observed_cfg_unknown
OP N7
  INPUTS not included/unknown
  DIRECT_CONTROL N5 via=CDG branch=unknown check=cdg_observed_cfg_unknown
OP N3
  INPUTS not included/unknown
  DIRECT_CONTROL N2 via=CDG branch=unknown check=cdg_observed_cfg_unknown
UNKNOWN: guard sufficiency, aliasing and feasible execution paths. Missing polarity is unknown.
BOUNDED: omitted operations/context and shortened snippets are not proof of absence.

The following is an example, and it is .


Answer (0 or 1):
~~~~~

## Sample 08 · devign · B1-H2 · seed 42

ID: `devign:validation:16307`  
Prompt SHA-256: `ca932becf870cac95fb6bd37dc61a117cc8b1dd6511d753ae9a4fd426d70356d`  
Stratum: `missing_cpg`

~~~~~text
You are now an excellent programmer. You are conducting a function vulnerability detection task for C/C++ language.

_syscall3(int,sys_faccessat,int,dirfd,const char *,pathname,int,mode)

#endif

#if defined(TARGET_NR_fchmodat) && defined(__NR_fchmodat)

_syscall3(int,sys_fchmodat,int,dirfd,const char *,pathname, mode_t,mode)

#endif

#if defined(TARGET_NR_fchownat) && defined(__NR_fchownat) && defined(USE_UID16)

_syscall5(int,sys_fchownat,int,dirfd,const char *,pathname,

          uid_t,owner,gid_t,group,int,flags)

#endif

#if (defined(TARGET_NR_fstatat64) || defined(TARGET_NR_newfstatat)) && \

        defined(__NR_fstatat64)

_syscall4(int,sys_fstatat64,int,dirfd,const char *,pathname,

          struct stat *,buf,int,flags)

#endif

#if defined(TARGET_NR_futimesat) && defined(__NR_futimesat)

_syscall3(int,sys_futimesat,int,dirfd,const char *,pathname,

         const struct timeval *,times)

#endif

#if (defined(TARGET_NR_newfstatat) || defined(TARGET_NR_fstatat64) ) && \

        defined(__NR_newfstatat)

_syscall4(int,sys_newfstatat,int,dirfd,const char *,pathname,

          struct stat *,buf,int,flags)

#endif

#if defined(TARGET_NR_linkat) && defined(__NR_linkat)

_syscall5(int,sys_linkat,int,olddirfd,const char *,oldpath,

      int,newdirfd,const char *,newpath,int,flags)

#endif

#if defined(TARGET_NR_mkdirat) && defined(__NR_mkdirat)

_syscall3(int,sys_mkdirat,int,dirfd,const char *,pathname,mode_t,mode)

#endif

#if defined(TARGET_NR_mknodat) && defined(__NR_mknodat)

_syscall4(int,sys_mknodat,int,dirfd,const char *,pathname,

          mode_t,mode,dev_t,dev)

#endif

#if defined(TARGET_NR_openat) && defined(__NR_openat)

_syscall4(int,sys_openat,int,dirfd,const char *,pathname,int,flags,mode_t,mode)

#endif

#if defined(TARGET_NR_readlinkat) && defined(__NR_readlinkat)

_syscall4(int,sys_readlinkat,int,dirfd,const char *,pathname,

          char *,buf,size_t,bufsize)

#endif

#if defined(TARGET_NR_renameat) && defined(__NR_renameat)

_syscall4(int,sys_renameat,int,olddirfd,const char *,oldpath,

          int,newdirfd,const char *,newpath)

#endif

#if defined(TARGET_NR_symlinkat) && defined(__NR_symlinkat)

_syscall3(int,sys_symlinkat,const char *,oldpath,

          int,newdirfd,const char *,newpath)

#endif

#if defined(TARGET_NR_unlinkat) && defined(__NR_unlinkat)

_syscall3(int,sys_unlinkat,int,dirfd,const char *,pathname,int,flags)

#endif



#endif /* CONFIG_ATFILE */



#ifdef CONFIG_UTIMENSAT

static int sys_utimensat(int dirfd, const char *pathname,

    const struct timespec times[2], int flags)

{

    if (pathname == NULL)

        return futimens(dirfd, times);

    else

        return utimensat(dirfd, pathname, times, flags);

}

In the above code snippet, check for potential security vulnerabilities and answer with a single digit: 1 if Vulnerable, 0 if Non-vulnerable.

The node information of the code snippet is as follows:

The edge information of the code snippet is as follows:


The following is an example, and it is .


Answer (0 or 1):
~~~~~

## Sample 09 · devign · B1-H2 · seed 42

ID: `devign:validation:16709`  
Prompt SHA-256: `dc005516b83dfeb3e2f84099315ece34a1b4cdcab7c58e76e157223c1b56505c`  
Stratum: `cdg_cluster`

~~~~~text
You are now an excellent programmer. You are conducting a function vulnerability detection task for C/C++ language.

static av_always_inline void encode_mb_internal(MpegEncContext *s,

                                                int motion_x, int motion_y,

                                                int mb_block_height,

                                                int mb_block_width,

                                                int mb_block_count)

{

    int16_t weight[12][64];

    int16_t orig[12][64];

    const int mb_x = s->mb_x;

    const int mb_y = s->mb_y;

    int i;

    int skip_dct[12];

    int dct_offset = s->linesize * 8; // default for progressive frames

    int uv_dct_offset = s->uvlinesize * 8;

    uint8_t *ptr_y, *ptr_cb, *ptr_cr;

    int wrap_y, wrap_c;



    for (i = 0; i < mb_block_count; i++)

        skip_dct[i] = s->skipdct;



    if (s->adaptive_quant) {

        const int last_qp = s->qscale;

        const int mb_xy = mb_x + mb_y * s->mb_stride;



        s->lambda = s->lambda_table[mb_xy];

        update_qscale(s);



        if (!(s->mpv_flags & FF_MPV_FLAG_QP_RD)) {

            s->qscale = s->current_picture_ptr->qscale_table[mb_xy];

            s->dquant = s->qscale - last_qp;



            if (s->out_format == FMT_H263) {

                s->dquant = av_clip(s->dquant, -2, 2);



                if (s->codec_id == AV_CODEC_ID_MPEG4) {

                    if (!s->mb_intra) {

                        if (s->pict_type == AV_PICTURE_TYPE_B) {

                            if (s->dquant & 1 || s->mv_dir & MV_DIRECT)

                                s->dquant = 0;

                        }

                        if (s->mv_type == MV_TYPE_8X8)

                            s->dquant = 0;

                    }

                }

            }

        }

        ff_set_qscale(s, last_qp + s->dquant);

    } else if (s->mpv_flags & FF_MPV_FLAG_QP_RD)

        ff_set_qscale(s, s->qscale + s->dquant);



    wrap_y = s->linesize;

    wrap_c = s->uvlinesize;

    ptr_y  = s->new_picture.f.data[0] +

             (mb_y * 16 * wrap_y)              + mb_x * 16;

    ptr_cb = s->new_picture.f.data[1] +

             (mb_y * mb_block_height * wrap_c) + mb_x * mb_block_width;

    ptr_cr = s->new_picture.f.data[2] +

             (mb_y * mb_block_height * wrap_c) + mb_x * mb_block_width;



    if((mb_x*16+16 > s->width || mb_y*16+16 > s->height) && s->codec_id != AV_CODEC_ID_AMV){

        uint8_t *ebuf = s->edge_emu_buffer + 32;

        int cw = (s->width  + s->chroma_x_shift) >> s->chroma_x_shift;

        int ch = (s->height + s->chroma_y_shift) >> s->chroma_y_shift;

        s->vdsp.emulated_edge_mc(ebuf, ptr_y, wrap_y, 16, 16, mb_x * 16,

                                 mb_y * 16, s->width, s->height);

        ptr_y = ebuf;

        s->vdsp.emulated_edge_mc(ebuf + 18 * wrap_y, ptr_cb, wrap_c, mb_block_width,

                                 mb_block_height, mb_x * mb_block_width, mb_y * mb_block_height,

                                 cw, ch);

        ptr_cb = ebuf + 18 * wrap_y;

        s->vdsp.emulated_edge_mc(ebuf + 18 * wrap_y + 16, ptr_cr, wrap_c, mb_block_width,

                                 mb_block_height, mb_x * mb_block_width, mb_y * mb_block_height,

                                 cw, ch);

        ptr_cr = ebuf + 18 * wrap_y + 16;

    }



    if (s->mb_intra) {

        if (s->flags & CODEC_FLAG_INTERLACED_DCT) {

            int progressive_score, interlaced_score;



            s->interlaced_dct = 0;

            progressive_score = s->dsp.ildct_cmp[4](s, ptr_y,

                                                    NULL, wrap_y, 8) +

                                s->dsp.ildct_cmp[4](s, ptr_y + wrap_y * 8,

                                                    NULL, wrap_y, 8) - 400;



            if (progressive_score > 0) {

                interlaced_score = s->dsp.ildct_cmp[4](s, ptr_y,

                                                       NULL, wrap_y * 2, 8) +

                                   s->dsp.ildct_cmp[4](s, ptr_y + wrap_y,

                                                       NULL, wrap_y * 2, 8);

                if (progressive_score > interlaced_score) {

                    s->interlaced_dct = 1;



                    dct_offset = wrap_y;

                    uv_dct_offset = wrap_c;

                    wrap_y <<= 1;

                    if (s->chroma_format == CHROMA_422 ||

                        s->chroma_format == CHROMA_444)

                        wrap_c <<= 1;

                }

            }

        }



        s->dsp.get_pixels(s->block[0], ptr_y                  , wrap_y);

        s->dsp.get_pixels(s->block[1], ptr_y              + 8 , wrap_y);

        s->dsp.get_pixels(s->block[2], ptr_y + dct_offset     , wrap_y);

        s->dsp.get_pixels(s->block[3], ptr_y + dct_offset + 8 , wrap_y);



        if (s->flags & CODEC_FLAG_GRAY) {

            skip_dct[4] = 1;

            skip_dct[5] = 1;

        } else {

            s->dsp.get_pixels(s->block[4], ptr_cb, wrap_c);

            s->dsp.get_pixels(s->block[5], ptr_cr, wrap_c);

            if (!s->chroma_y_shift && s->chroma_x_shift) { /* 422 */

                s->dsp.get_pixels(s->block[6], ptr_cb + uv_dct_offset, wrap_c);

                s->dsp.get_pixels(s->block[7], ptr_cr + uv_dct_offset, wrap_c);

            } else if (!s->chroma_y_shift && !s->chroma_x_shift) { /* 444 */

                s->dsp.get_pixels(s->block[6], ptr_cb + 8, wrap_c);

                s->dsp.get_pixels(s->block[7], ptr_cr + 8, wrap_c);

                s->dsp.get_pixels(s->block[8], ptr_cb + uv_dct_offset, wrap_c);

                s->dsp.get_pixels(s->block[9], ptr_cr + uv_dct_offset, wrap_c);

                s->dsp.get_pixels(s->block[10], ptr_cb + uv_dct_offset + 8, wrap_c);

                s->dsp.get_pixels(s->block[11], ptr_cr + uv_dct_offset + 8, wrap_c);

            }

        }

    } else {

        op_pixels_func (*op_pix)[4];

        qpel_mc_func (*op_qpix)[16];

        uint8_t *dest_y, *dest_cb, *dest_cr;



        dest_y  = s->dest[0];

        dest_cb = s->dest[1];

        dest_cr = s->dest[2];



        if ((!s->no_rounding) || s->pict_type == AV_PICTURE_TYPE_B) {

            op_pix  = s->hdsp.put_pixels_tab;

            op_qpix = s->dsp.put_qpel_pixels_tab;

        } else {

            op_pix  = s->hdsp.put_no_rnd_pixels_tab;

            op_qpix = s->dsp.put_no_rnd_qpel_pixels_tab;

        }



        if (s->mv_dir & MV_DIR_FORWARD) {

            ff_MPV_motion(s, dest_y, dest_cb, dest_cr, 0,

                          s->last_picture.f.data,

                          op_pix, op_qpix);

            op_pix  = s->hdsp.avg_pixels_tab;

            op_qpix = s->dsp.avg_qpel_pixels_tab;

        }

        if (s->mv_dir & MV_DIR_BACKWARD) {

            ff_MPV_motion(s, dest_y, dest_cb, dest_cr, 1,

                          s->next_picture.f.data,

                          op_pix, op_qpix);

        }



        if (s->flags & CODEC_FLAG_INTERLACED_DCT) {

            int progressive_score, interlaced_score;



            s->interlaced_dct = 0;

            progressive_score = s->dsp.ildct_cmp[0](s, dest_y,

                                                    ptr_y,              wrap_y,

                                                    8) +

                                s->dsp.ildct_cmp[0](s, dest_y + wrap_y * 8,

                                                    ptr_y + wrap_y * 8, wrap_y,

                                                    8) - 400;



            if (s->avctx->ildct_cmp == FF_CMP_VSSE)

                progressive_score -= 400;



            if (progressive_score > 0) {

                interlaced_score = s->dsp.ildct_cmp[0](s, dest_y,

                                                       ptr_y,

                                                       wrap_y * 2, 8) +

                                   s->dsp.ildct_cmp[0](s, dest_y + wrap_y,

                                                       ptr_y + wrap_y,

                                                       wrap_y * 2, 8);



                if (progressive_score > interlaced_score) {

                    s->interlaced_dct = 1;



                    dct_offset = wrap_y;

                    uv_dct_offset = wrap_c;

                    wrap_y <<= 1;

                    if (s->chroma_format == CHROMA_422)

                        wrap_c <<= 1;

                }

            }

        }



        s->dsp.diff_pixels(s->block[0], ptr_y, dest_y, wrap_y);

        s->dsp.diff_pixels(s->block[1], ptr_y + 8, dest_y + 8, wrap_y);

        s->dsp.diff_pixels(s->block[2], ptr_y + dct_offset,

                           dest_y + dct_offset, wrap_y);

        s->dsp.diff_pixels(s->block[3], ptr_y + dct_offset + 8,

                           dest_y + dct_offset + 8, wrap_y);



        if (s->flags & CODEC_FLAG_GRAY) {

            skip_dct[4] = 1;

            skip_dct[5] = 1;

        } else {

            s->dsp.diff_pixels(s->block[4], ptr_cb, dest_cb, wrap_c);

            s->dsp.diff_pixels(s->block[5], ptr_cr, dest_cr, wrap_c);

            if (!s->chroma_y_shift) { /* 422 */

                s->dsp.diff_pixels(s->block[6], ptr_cb + uv_dct_offset,

                                   dest_cb + uv_dct_offset, wrap_c);

                s->dsp.diff_pixels(s->block[7], ptr_cr + uv_dct_offset,

                                   dest_cr + uv_dct_offset, wrap_c);

            }

        }

        /* pre quantization */

        if (s->current_picture.mc_mb_var[s->mb_stride * mb_y + mb_x] <

                2 * s->qscale * s->qscale) {

            // FIXME optimize

            if (s->dsp.sad[1](NULL, ptr_y , dest_y,

                              wrap_y, 8) < 20 * s->qscale)

                skip_dct[0] = 1;

            if (s->dsp.sad[1](NULL, ptr_y + 8,

                              dest_y + 8, wrap_y, 8) < 20 * s->qscale)

                skip_dct[1] = 1;

            if (s->dsp.sad[1](NULL, ptr_y + dct_offset,

                              dest_y + dct_offset, wrap_y, 8) < 20 * s->qscale)

                skip_dct[2] = 1;

            if (s->dsp.sad[1](NULL, ptr_y + dct_offset + 8,

                              dest_y + dct_offset + 8,

                              wrap_y, 8) < 20 * s->qscale)

                skip_dct[3] = 1;

            if (s->dsp.sad[1](NULL, ptr_cb, dest_cb,

                              wrap_c, 8) < 20 * s->qscale)

                skip_dct[4] = 1;

            if (s->dsp.sad[1](NULL, ptr_cr, dest_cr,

                              wrap_c, 8) < 20 * s->qscale)

                skip_dct[5] = 1;

            if (!s->chroma_y_shift) { /* 422 */

                if (s->dsp.sad[1](NULL, ptr_cb + uv_dct_offset,

                                  dest_cb + uv_dct_offset,

                                  wrap_c, 8) < 20 * s->qscale)

                    skip_dct[6] = 1;

                if (s->dsp.sad[1](NULL, ptr_cr + uv_dct_offset,

                                  dest_cr + uv_dct_offset,

                                  wrap_c, 8) < 20 * s->qscale)

                    skip_dct[7] = 1;

            }

        }

    }



    if (s->quantizer_noise_shaping)
/* [TRUNCATED TARGET] */

In the above code snippet, check for potential security vulnerabilities and answer with a single digit: 1 if Vulnerable, 0 if Non-vulnerable.

The guarded evidence of the code snippet is as follows:
GUARDED EVIDENCE: operation-specific observed relations; not a safety proof.
N1 CALL "i < mb_block_count"
N2 CALL "skip_dct[i]"
N3 CALL "s->skipdct"
N4 CALL "s->adaptive_quant"
N5 CALL "s->mb_stride"
N6 CALL "s->quantizer_noise_shaping"
N7 CALL "memcpy(orig[0], s->block[0], sizeof(int16_t) * 64 * mb_block_count)"
N8 FIELD_IDENTIFIER "skipdct"
N9 IDENTIFIER "skip_dct"
N10 IDENTIFIER "i"
N11 IDENTIFIER "s"
N1 --CDG--> N2
N1 --CDG--> N3
N2 --ARGUMENT--> N9
N2 --REACHING_DEF--> N9
N2 --ARGUMENT--> N10
N3 --ARGUMENT--> N8
N3 --ARGUMENT--> N11
N4 --CDG--> N5
N6 --CDG--> N7
OP N7
  INPUTS not included/unknown
  DIRECT_CONTROL N6 via=CDG branch=unknown check=cdg_observed_cfg_unknown
OP N2
  INPUTS N9,N10
  DIRECT_CONTROL N1 via=CDG branch=unknown check=cdg_observed_cfg_unknown
  DATA_NOTE: predicates on related data are not operation controls.
OP N3
  INPUTS N8,N11
  DIRECT_CONTROL N1 via=CDG branch=unknown check=cdg_observed_cfg_unknown
  DATA_NOTE: predicates on related data are not operation controls.
OP N5
  INPUTS not included/unknown
  DIRECT_CONTROL N4 via=CDG branch=unknown check=cdg_observed_cfg_unknown
UNKNOWN: guard sufficiency, aliasing and feasible execution paths. Missing polarity is unknown.
BOUNDED: omitted operations/context and shortened snippets are not proof of absence.

The following is an example, and it is .


Answer (0 or 1):
~~~~~

## Sample 10 · devign · B1-H2 · seed 42

ID: `devign:validation:17336`  
Prompt SHA-256: `af9b61d260e72403d0c411c2a3e29b9f5f5b2d1b916c512913af493e6f82cfc9`  
Stratum: `cdg_cluster`

~~~~~text
You are now an excellent programmer. You are conducting a function vulnerability detection task for C/C++ language.

void ff_af_queue_log_state(AudioFrameQueue *afq)

{

    AudioFrame *f;

    av_log(afq->avctx, AV_LOG_DEBUG, "remaining delay   = %d\n",

           afq->remaining_delay);

    av_log(afq->avctx, AV_LOG_DEBUG, "remaining samples = %d\n",

           afq->remaining_samples);

    av_log(afq->avctx, AV_LOG_DEBUG, "frames:\n");

    f = afq->frame_queue;

    while (f) {

        av_log(afq->avctx, AV_LOG_DEBUG, "  [ pts=%9"PRId64" duration=%d ]\n",

               f->pts, f->duration);

        f = f->next;

    }

}

In the above code snippet, check for potential security vulnerabilities and answer with a single digit: 1 if Vulnerable, 0 if Non-vulnerable.

The guarded evidence of the code snippet is as follows:
GUARDED EVIDENCE: operation-specific observed relations; not a safety proof.
N1 METHOD_RETURN "RET"
N2 CALL "afq->avctx"
N3 CALL "afq->remaining_delay"
N4 CALL "afq->avctx"
N5 CALL "f != NULL"
N6 CALL "f->next"
N7 FIELD_IDENTIFIER "avctx"
N8 FIELD_IDENTIFIER "remaining_delay"
N9 IDENTIFIER "afq"
N10 IDENTIFIER "afq"
N2 --REACHING_DEF--> N3
N2 --REACHING_DEF--> N4
N2 --ARGUMENT--> N7
N2 --ARGUMENT--> N9
N3 --REACHING_DEF--> N2
N3 --ARGUMENT--> N8
N3 --ARGUMENT--> N10
N5 --CFG--> N1
N5 --CDG--> N6
OP N6
  INPUTS not included/unknown
  DIRECT_CONTROL N5 via=CDG branch=unknown check=cfg_one_branch_witness
  OBSERVED_EXIT N1 from=N5 branch=unknown
OP N2
  INPUTS N7,N9
  DIRECT_CONTROL none observed; not proof of absence
OP N3
  INPUTS N8,N10
  DIRECT_CONTROL none observed; not proof of absence
OP N4
  INPUTS not included/unknown
  DIRECT_CONTROL none observed; not proof of absence
UNKNOWN: guard sufficiency, aliasing and feasible execution paths. Missing polarity is unknown.
BOUNDED: omitted operations/context and shortened snippets are not proof of absence.

The following is an example, and it is .


Answer (0 or 1):
~~~~~

## Sample 11 · devign · B1-H2 · seed 42

ID: `devign:validation:18320`  
Prompt SHA-256: `7e3fb1a5ae543b21baae6129f7f16c10eab19d58dfea69da6b1c20563d652efb`  
Stratum: `closed_prefix`

~~~~~text
You are now an excellent programmer. You are conducting a function vulnerability detection task for C/C++ language.

static inline void code_gen_alloc(size_t tb_size)

{

    tcg_ctx.code_gen_buffer_size = size_code_gen_buffer(tb_size);

    tcg_ctx.code_gen_buffer = alloc_code_gen_buffer();

    if (tcg_ctx.code_gen_buffer == NULL) {

        fprintf(stderr, "Could not allocate dynamic translator buffer\n");

        exit(1);

    }



    qemu_madvise(tcg_ctx.code_gen_buffer, tcg_ctx.code_gen_buffer_size,

                 QEMU_MADV_HUGEPAGE);



    /* Estimate a good size for the number of TBs we can support.  We

       still haven't deducted the prologue from the buffer size here,

       but that's minimal and won't affect the estimate much.  */

    tcg_ctx.code_gen_max_blocks

        = tcg_ctx.code_gen_buffer_size / CODE_GEN_AVG_BLOCK_SIZE;

    tcg_ctx.tb_ctx.tbs = g_new(TranslationBlock, tcg_ctx.code_gen_max_blocks);



    qemu_mutex_init(&tcg_ctx.tb_ctx.tb_lock);

}

In the above code snippet, check for potential security vulnerabilities and answer with a single digit: 1 if Vulnerable, 0 if Non-vulnerable.

The guarded evidence of the code snippet is as follows:
GUARDED EVIDENCE: operation-specific observed relations; not a safety proof.
N1 CALL "size_code_gen_buffer(tb_size)"
N2 CALL "tcg_ctx.code_gen_buffer == NULL"
N3 CALL "fprintf(stderr, \"Could not allocate dynamic translator buffer\\n\")"
N4 CALL "exit(1)"
N5 CALL "tcg_ctx.code_gen_buffer_size"
N6 CALL "tcg_ctx.code_gen_buffer_size / CODE_GEN_AVG_BLOCK_SIZE"
N7 CALL "tcg_ctx.code_gen_buffer_size"
N2 --CDG--> N3
N2 --CDG--> N4
N5 --REACHING_DEF--> N7
N6 --ARGUMENT--> N7
OP N3
  INPUTS not included/unknown
  DIRECT_CONTROL N2 via=CDG branch=unknown check=cdg_observed_cfg_unknown
OP N4
  INPUTS not included/unknown
  DIRECT_CONTROL N2 via=CDG branch=unknown check=cdg_observed_cfg_unknown
OP N6
  INPUTS N7
  DIRECT_CONTROL none observed; not proof of absence
OP N1
  INPUTS not included/unknown
  DIRECT_CONTROL none observed; not proof of absence
UNKNOWN: guard sufficiency, aliasing and feasible execution paths. Missing polarity is unknown.
BOUNDED: omitted operations/context and shortened snippets are not proof of absence.

The following is an example, and it is .


Answer (0 or 1):
~~~~~

## Sample 12 · devign · B1-H2 · seed 42

ID: `devign:validation:19012`  
Prompt SHA-256: `c80d4aa9d1337cfc4d840bc48978b39e4c758126060bee8bd953ab609aabce7c`  
Stratum: `cdg_cluster`

~~~~~text
You are now an excellent programmer. You are conducting a function vulnerability detection task for C/C++ language.

static int mpeg_decode_frame(AVCodecContext *avctx,

                             void *data, int *data_size,

                             uint8_t *buf, int buf_size)

{

    Mpeg1Context *s = avctx->priv_data;

    const uint8_t *buf_end;

    const uint8_t *buf_ptr;

    uint32_t start_code;

    int ret, input_size;

    AVFrame *picture = data;

    MpegEncContext *s2 = &s->mpeg_enc_ctx;

    dprintf(avctx, "fill_buffer\n");



    if (buf_size == 0 || (buf_size == 4 && AV_RB32(buf) == SEQ_END_CODE)) {

        /* special case for last picture */

        if (s2->low_delay==0 && s2->next_picture_ptr) {

            *picture= *(AVFrame*)s2->next_picture_ptr;

            s2->next_picture_ptr= NULL;



            *data_size = sizeof(AVFrame);

        }

        return 0;

    }



    if(s2->flags&CODEC_FLAG_TRUNCATED){

        int next= ff_mpeg1_find_frame_end(&s2->parse_context, buf, buf_size);



        if( ff_combine_frame(&s2->parse_context, next, (const uint8_t **)&buf, &buf_size) < 0 )

            return buf_size;

    }



    buf_ptr = buf;

    buf_end = buf + buf_size;



#if 0

    if (s->repeat_field % 2 == 1) {

        s->repeat_field++;

        //fprintf(stderr,"\nRepeating last frame: %d -> %d! pict: %d %d", avctx->frame_number-1, avctx->frame_number,

        //        s2->picture_number, s->repeat_field);

        if (avctx->flags & CODEC_FLAG_REPEAT_FIELD) {

            *data_size = sizeof(AVPicture);

            goto the_end;

        }

    }

#endif



    if(s->mpeg_enc_ctx_allocated==0 && avctx->codec_tag == ff_get_fourcc("VCR2"))

        vcr2_init_sequence(avctx);



    s->slice_count= 0;



    for(;;) {

        /* find start next code */

        start_code = -1;

        buf_ptr = ff_find_start_code(buf_ptr,buf_end, &start_code);

        if (start_code > 0x1ff){

            if(s2->pict_type != B_TYPE || avctx->skip_frame <= AVDISCARD_DEFAULT){

                if(avctx->thread_count > 1){

                    int i;



                    avctx->execute(avctx, slice_decode_thread,  (void**)&(s2->thread_context[0]), NULL, s->slice_count);

                    for(i=0; i<s->slice_count; i++)

                        s2->error_count += s2->thread_context[i]->error_count;

                }

                if (slice_end(avctx, picture)) {

                    if(s2->last_picture_ptr || s2->low_delay) //FIXME merge with the stuff in mpeg_decode_slice

                        *data_size = sizeof(AVPicture);

                }

            }

            return FFMAX(0, buf_ptr - buf - s2->parse_context.last_index);

        }



        input_size = buf_end - buf_ptr;



        if(avctx->debug & FF_DEBUG_STARTCODE){

            av_log(avctx, AV_LOG_DEBUG, "%3X at %zd left %d\n", start_code, buf_ptr-buf, input_size);

        }



        /* prepare data for next start code */

        switch(start_code) {

        case SEQ_START_CODE:

            mpeg1_decode_sequence(avctx, buf_ptr,

                                    input_size);

            break;



        case PICTURE_START_CODE:

            /* we have a complete image : we try to decompress it */

            mpeg1_decode_picture(avctx,

                                    buf_ptr, input_size);

            break;

        case EXT_START_CODE:

            mpeg_decode_extension(avctx,

                                    buf_ptr, input_size);

            break;

        case USER_START_CODE:

            mpeg_decode_user_data(avctx,

                                    buf_ptr, input_size);

            break;

        case GOP_START_CODE:

            s2->first_field=0;

            mpeg_decode_gop(avctx,

                                    buf_ptr, input_size);

            break;

        default:

            if (start_code >= SLICE_MIN_START_CODE &&

                start_code <= SLICE_MAX_START_CODE) {

                int mb_y= start_code - SLICE_MIN_START_CODE;



                if(s2->last_picture_ptr==NULL){

                /* Skip B-frames if we do not have reference frames. */

                    if(s2->pict_type==B_TYPE) break;

                /* Skip P-frames if we do not have reference frame no valid header. */

//                    if(s2->pict_type==P_TYPE && s2->first_field && !s2->first_slice) break;

                }

                /* Skip B-frames if we are in a hurry. */

                if(avctx->hurry_up && s2->pict_type==B_TYPE) break;

                if(  (avctx->skip_frame >= AVDISCARD_NONREF && s2->pict_type==B_TYPE)

                    ||(avctx->skip_frame >= AVDISCARD_NONKEY && s2->pict_type!=I_TYPE)

                    || avctx->skip_frame >= AVDISCARD_ALL)

                    break;

                /* Skip everything if we are in a hurry>=5. */

                if(avctx->hurry_up>=5) break;



                if (!s->mpeg_enc_ctx_allocated) break;



                if(s2->codec_id == CODEC_ID_MPEG2VIDEO){

                    if(mb_y < avctx->skip_top || mb_y >= s2->mb_height - avctx->skip_bottom)

                        break;

                }



                if(s2->first_slice){

                    s2->first_slice=0;

                            if(mpeg_field_start(s2) < 0)

                        return -1;

                    }

                if(!s2->current_picture_ptr){

                    av_log(avctx, AV_LOG_ERROR, "current_picture not initialized\n");

                    return -1;

                }



                if(avctx->thread_count > 1){

                    int threshold= (s2->mb_height*s->slice_count + avctx->thread_count/2) / avctx->thread_count;

                    if(threshold <= mb_y){

                        MpegEncContext *thread_context= s2->thread_context[s->slice_count];



                        thread_context->start_mb_y= mb_y;

                        thread_context->end_mb_y  = s2->mb_height;

                        if(s->slice_count){

                            s2->thread_context[s->slice_count-1]->end_mb_y= mb_y;

                            ff_update_duplicate_context(thread_context, s2);

                        }

                        init_get_bits(&thread_context->gb, buf_ptr, input_size*8);

                        s->slice_count++;

                    }

                    buf_ptr += 2; //FIXME add minimum num of bytes per slice

                }else{

                    ret = mpeg_decode_slice(s, mb_y, &buf_ptr, input_size);

                    emms_c();



                    if(ret < 0){

                        if(s2->resync_mb_x>=0 && s2->resync_mb_y>=0)

                            ff_er_add_slice(s2, s2->resync_mb_x, s2->resync_mb_y, s2->mb_x, s2->mb_y, AC_ERROR|DC_ERROR|MV_ERROR);

                    }else{

                        ff_er_add_slice(s2, s2->resync_mb_x, s2->resync_mb_y, s2->mb_x-1, s2->mb_y, AC_END|DC_END|MV_END);

                    }

                }

            }

            break;

        }

    }

}

In the above code snippet, check for potential security vulnerabilities and answer with a single digit: 1 if Vulnerable, 0 if Non-vulnerable.

The guarded evidence of the code snippet is as follows:
GUARDED EVIDENCE: operation-specific observed relations; not a safety proof.
N1 RETURN "return 0;"
N2 CALL "buf_size == 0 || (buf_size == 4 && AV_RB32(buf) == SEQ_END_CODE)"
N3 CALL "s2->low_delay==0 && s2->next_picture_ptr"
N4 CALL "s2->low_delay"
N5 CALL "*picture"
N6 CALL "*(AVFrame*)s2->next_picture_ptr"
N7 CALL "s2->flags"
N8 LITERAL "0"
N2 --CDG--> N4
N2 --CDG--> N7
N3 --CDG--> N5
N3 --CDG--> N6
N3 --CFG--> N8
N8 --CFG--> N1
OP N4
  INPUTS not included/unknown
  DIRECT_CONTROL N2 via=CDG branch=unknown check=cdg_observed_cfg_unknown
OP N5
  INPUTS not included/unknown
  DIRECT_CONTROL N3 via=CDG branch=unknown check=cfg_one_branch_witness
  OBSERVED_EXIT N1 from=N3 branch=unknown
OP N6
  INPUTS not included/unknown
  DIRECT_CONTROL N3 via=CDG branch=unknown check=cfg_one_branch_witness
  OBSERVED_EXIT N1 from=N3 branch=unknown
OP N7
  INPUTS not included/unknown
  DIRECT_CONTROL N2 via=CDG branch=unknown check=cdg_observed_cfg_unknown
UNKNOWN: guard sufficiency, aliasing and feasible execution paths. Missing polarity is unknown.
BOUNDED: omitted operations/context and shortened snippets are not proof of absence.

The following is an example, and it is .


Answer (0 or 1):
~~~~~

## Sample 13 · devign · B1-H2 · seed 42

ID: `devign:validation:19014`  
Prompt SHA-256: `555b1ed42a9f0e3c225af242c70a32a28ff26f9e343e65a44f513ecc02523835`  
Stratum: `closed_prefix`

~~~~~text
You are now an excellent programmer. You are conducting a function vulnerability detection task for C/C++ language.

static void pci_msix_write(void *opaque, hwaddr addr,

                           uint64_t val, unsigned size)

{

    XenPCIPassthroughState *s = opaque;

    XenPTMSIX *msix = s->msix;

    XenPTMSIXEntry *entry;

    int entry_nr, offset;



    entry_nr = addr / PCI_MSIX_ENTRY_SIZE;

    if (entry_nr < 0 || entry_nr >= msix->total_entries) {

        XEN_PT_ERR(&s->dev, "asked MSI-X entry '%i' invalid!\n", entry_nr);

        return;

    }

    entry = &msix->msix_entry[entry_nr];

    offset = addr % PCI_MSIX_ENTRY_SIZE;



    if (offset != PCI_MSIX_ENTRY_VECTOR_CTRL) {

        const volatile uint32_t *vec_ctrl;



        if (get_entry_value(entry, offset) == val

            && entry->pirq != XEN_PT_UNASSIGNED_PIRQ) {

            return;

        }



        /*

         * If Xen intercepts the mask bit access, entry->vec_ctrl may not be

         * up-to-date. Read from hardware directly.

         */

        vec_ctrl = s->msix->phys_iomem_base + entry_nr * PCI_MSIX_ENTRY_SIZE

            + PCI_MSIX_ENTRY_VECTOR_CTRL;



        if (msix->enabled && !(*vec_ctrl & PCI_MSIX_ENTRY_CTRL_MASKBIT)) {

            XEN_PT_ERR(&s->dev, "Can't update msix entry %d since MSI-X is"

                       " already enabled.\n", entry_nr);

            return;

        }



        entry->updated = true;

    }



    set_entry_value(entry, offset, val);



    if (offset == PCI_MSIX_ENTRY_VECTOR_CTRL) {

        if (msix->enabled && !(val & PCI_MSIX_ENTRY_CTRL_MASKBIT)) {

            xen_pt_msix_update_one(s, entry_nr);

        }

    }

}

In the above code snippet, check for potential security vulnerabilities and answer with a single digit: 1 if Vulnerable, 0 if Non-vulnerable.

The guarded evidence of the code snippet is as follows:
GUARDED EVIDENCE: operation-specific observed relations; not a safety proof.
N1 CALL "entry_nr < 0 || entry_nr >= msix->total_entries"
N2 CALL "entry_nr < 0"
N3 CALL "msix->total_entries"
N4 CALL "s->dev"
N5 CALL "msix->msix_entry[entry_nr]"
N6 CALL "msix->msix_entry"
N1 --CDG--> N4
N1 --CDG--> N5
N1 --CDG--> N6
N2 --CDG--> N3
N5 --ARGUMENT--> N6
OP N3
  INPUTS not included/unknown
  DIRECT_CONTROL N2 via=CDG branch=unknown check=cdg_observed_cfg_unknown
OP N4
  INPUTS not included/unknown
  DIRECT_CONTROL N1 via=CDG branch=unknown check=cdg_observed_cfg_unknown
OP N5
  INPUTS N6
  DIRECT_CONTROL N1 via=CDG branch=unknown check=cdg_observed_cfg_unknown
  DATA_NOTE: predicates on related data are not operation controls.
OP N6
  INPUTS not included/unknown
  DIRECT_CONTROL N1 via=CDG branch=unknown check=cdg_observed_cfg_unknown
UNKNOWN: guard sufficiency, aliasing and feasible execution paths. Missing polarity is unknown.
BOUNDED: omitted operations/context and shortened snippets are not proof of absence.

The following is an example, and it is .


Answer (0 or 1):
~~~~~

## Sample 14 · devign · B1-H2 · seed 42

ID: `devign:validation:19357`  
Prompt SHA-256: `16c3d70c7ca02e73ce72708eb8b5297b87742fc7f92405a877473977737da17d`  
Stratum: `closed_prefix`

~~~~~text
You are now an excellent programmer. You are conducting a function vulnerability detection task for C/C++ language.

static uint32_t qvirtio_pci_config_readl(QVirtioDevice *d, uint64_t off)

{

    QVirtioPCIDevice *dev = (QVirtioPCIDevice *)d;

    uint32_t value;



    value = qpci_io_readl(dev->pdev, CONFIG_BASE(dev) + off);

    if (qvirtio_is_big_endian(d)) {

        value = bswap32(value);

    }

    return value;

}

In the above code snippet, check for potential security vulnerabilities and answer with a single digit: 1 if Vulnerable, 0 if Non-vulnerable.

The guarded evidence of the code snippet is as follows:
GUARDED EVIDENCE: operation-specific observed relations; not a safety proof.
N1 CALL "qpci_io_readl(dev->pdev, CONFIG_BASE(dev) + off)"
N2 CALL "dev->pdev"
N3 CALL "CONFIG_BASE(dev) + off"
N4 CALL "CONFIG_BASE(dev)"
N5 CALL "qvirtio_is_big_endian(d)"
N6 CALL "bswap32(value)"
N7 FIELD_IDENTIFIER "pdev"
N8 IDENTIFIER "dev"
N9 IDENTIFIER "dev"
N10 IDENTIFIER "off"
N1 --ARGUMENT--> N2
N1 --ARGUMENT--> N3
N2 --REACHING_DEF--> N1
N2 --REACHING_DEF--> N3
N2 --ARGUMENT--> N7
N2 --ARGUMENT--> N8
N3 --REACHING_DEF--> N1
N3 --REACHING_DEF--> N2
N3 --ARGUMENT--> N4
N3 --ARGUMENT--> N10
N4 --REACHING_DEF--> N3
N4 --ARGUMENT--> N9
N5 --CDG--> N6
OP N6
  INPUTS not included/unknown
  DIRECT_CONTROL N5 via=CDG branch=unknown check=cdg_observed_cfg_unknown
OP N2
  INPUTS N7,N8
  DIRECT_CONTROL none observed; not proof of absence
OP N3
  INPUTS N4,N10
  DIRECT_CONTROL none observed; not proof of absence
OP N1
  INPUTS N2,N3
  DIRECT_CONTROL none observed; not proof of absence
UNKNOWN: guard sufficiency, aliasing and feasible execution paths. Missing polarity is unknown.
BOUNDED: omitted operations/context and shortened snippets are not proof of absence.

The following is an example, and it is .


Answer (0 or 1):
~~~~~

## Sample 15 · devign · B1-H2 · seed 42

ID: `devign:validation:19366`  
Prompt SHA-256: `2583e2059ae5a7449747c9ecec5908e2c82255ea7f1af2a8bb9c69007d779feb`  
Stratum: `no_usable_evidence`

~~~~~text
You are now an excellent programmer. You are conducting a function vulnerability detection task for C/C++ language.

int blk_mig_active(void)

{

    return !QSIMPLEQ_EMPTY(&block_mig_state.bmds_list);

}

In the above code snippet, check for potential security vulnerabilities and answer with a single digit: 1 if Vulnerable, 0 if Non-vulnerable.

The guarded evidence of the code snippet is as follows:
GUARDED EVIDENCE: operation-specific observed relations; not a safety proof.
N1 CALL "QSIMPLEQ_EMPTY(&block_mig_state.bmds_list)"
N2 CALL "&block_mig_state.bmds_list"
N3 CALL "block_mig_state.bmds_list"
N1 --ARGUMENT--> N2
N2 --REACHING_DEF--> N1
N2 --ARGUMENT--> N3
N3 --REACHING_DEF--> N2
OP N1
  INPUTS N2
  DIRECT_CONTROL unknown: CDG unavailable
UNKNOWN: guard sufficiency, aliasing and feasible execution paths. Missing polarity is unknown.
BOUNDED: omitted operations/context and shortened snippets are not proof of absence.

The following is an example, and it is .


Answer (0 or 1):
~~~~~

## Sample 16 · devign · B1-H2 · seed 42

ID: `devign:validation:19662`  
Prompt SHA-256: `e1a2ac0e93cf340b0526e1c016c36999e25b1d5b8fa35258dbf885a6616f5aaf`  
Stratum: `cdg_cluster`

~~~~~text
You are now an excellent programmer. You are conducting a function vulnerability detection task for C/C++ language.

static int decode_p_block(FourXContext *f, uint16_t *dst, uint16_t *src,

                          int log2w, int log2h, int stride)

{

    const int index = size2index[log2h][log2w];

    const int h     = 1 << log2h;

    int code        = get_vlc2(&f->gb,

                               block_type_vlc[1 - (f->version > 1)][index].table,

                               BLOCK_TYPE_VLC_BITS, 1);

    uint16_t *start = (uint16_t *)f->last_picture->data[0];

    uint16_t *end   = start + stride * (f->avctx->height - h + 1) - (1 << log2w);

    int ret;



    if (code < 0 || code > 6 || log2w < 0)

        return AVERROR_INVALIDDATA;



    if (code == 0) {

        src += f->mv[bytestream2_get_byte(&f->g)];

        if (start > src || src > end) {

            av_log(f->avctx, AV_LOG_ERROR, "mv out of pic\n");

            return AVERROR_INVALIDDATA;

        }

        mcdc(dst, src, log2w, h, stride, 1, 0);

    } else if (code == 1) {

        log2h--;

        if ((ret = decode_p_block(f, dst, src, log2w, log2h, stride)) < 0)

            return ret;

        if ((ret = decode_p_block(f, dst + (stride << log2h),

                                  src + (stride << log2h),

                                  log2w, log2h, stride)) < 0)

            return ret;

    } else if (code == 2) {

        log2w--;

        if ((ret = decode_p_block(f, dst , src, log2w, log2h, stride)) < 0)

            return ret;

        if ((ret = decode_p_block(f, dst + (1 << log2w),

                                  src + (1 << log2w),

                                  log2w, log2h, stride)) < 0)

            return ret;

    } else if (code == 3 && f->version < 2) {

        if (start > src || src > end) {

            av_log(f->avctx, AV_LOG_ERROR, "mv out of pic\n");

            return AVERROR_INVALIDDATA;

        }

        mcdc(dst, src, log2w, h, stride, 1, 0);

    } else if (code == 4) {

        src += f->mv[bytestream2_get_byte(&f->g)];

        if (start > src || src > end) {

            av_log(f->avctx, AV_LOG_ERROR, "mv out of pic\n");

            return AVERROR_INVALIDDATA;

        }

        mcdc(dst, src, log2w, h, stride, 1, bytestream2_get_le16(&f->g2));

    } else if (code == 5) {

        if (start > src || src > end) {

            av_log(f->avctx, AV_LOG_ERROR, "mv out of pic\n");

            return AVERROR_INVALIDDATA;

        }

        mcdc(dst, src, log2w, h, stride, 0, bytestream2_get_le16(&f->g2));

    } else if (code == 6) {

        if (log2w) {

            dst[0]      = bytestream2_get_le16(&f->g2);

            dst[1]      = bytestream2_get_le16(&f->g2);

        } else {

            dst[0]      = bytestream2_get_le16(&f->g2);

            dst[stride] = bytestream2_get_le16(&f->g2);

        }

    }

    return 0;

}

In the above code snippet, check for potential security vulnerabilities and answer with a single digit: 1 if Vulnerable, 0 if Non-vulnerable.

The guarded evidence of the code snippet is as follows:
GUARDED EVIDENCE: operation-specific observed relations; not a safety proof.
N1 CALL "code == 0"
N2 CALL "f->mv[bytestream2_get_byte(&f->g)]"
N3 CALL "f->mv"
N4 CALL "f->g"
N5 CALL "start > src || src > end"
N6 CALL "f->avctx"
N1 --CDG--> N2
N1 --CDG--> N3
N1 --CDG--> N4
N5 --CDG--> N6
OP N2
  INPUTS not included/unknown
  DIRECT_CONTROL N1 via=CDG branch=unknown check=cdg_observed_cfg_unknown
OP N3
  INPUTS not included/unknown
  DIRECT_CONTROL N1 via=CDG branch=unknown check=cdg_observed_cfg_unknown
OP N4
  INPUTS not included/unknown
  DIRECT_CONTROL N1 via=CDG branch=unknown check=cdg_observed_cfg_unknown
OP N6
  INPUTS not included/unknown
  DIRECT_CONTROL N5 via=CDG branch=unknown check=cdg_observed_cfg_unknown
UNKNOWN: guard sufficiency, aliasing and feasible execution paths. Missing polarity is unknown.
BOUNDED: omitted operations/context and shortened snippets are not proof of absence.

The following is an example, and it is .


Answer (0 or 1):
~~~~~

## Sample 17 · devign · B1-H2 · seed 42

ID: `devign:validation:21124`  
Prompt SHA-256: `e7d3f107e6d97087fc8e5e5652b20cdf99451d5c115aaf2660d7821c5366f1c6`  
Stratum: `no_usable_evidence`

~~~~~text
You are now an excellent programmer. You are conducting a function vulnerability detection task for C/C++ language.

static int hdev_has_zero_init(BlockDriverState *bs)

{

    return 0;

}

In the above code snippet, check for potential security vulnerabilities and answer with a single digit: 1 if Vulnerable, 0 if Non-vulnerable.

The guarded evidence of the code snippet is as follows:
NO_USABLE_GUARDED_EVIDENCE: no_operation_nodes. Do not infer safety from missing evidence.

The following is an example, and it is .


Answer (0 or 1):
~~~~~

## Sample 18 · devign · B1-H2 · seed 42

ID: `devign:validation:21280`  
Prompt SHA-256: `8ac84723d98e61498e7b47a033dcdcfb7c43f32c5de829492e15f09991d3d5a4`  
Stratum: `cdg_cluster`

~~~~~text
You are now an excellent programmer. You are conducting a function vulnerability detection task for C/C++ language.

static int nvdec_mpeg12_start_frame(AVCodecContext *avctx, const uint8_t *buffer, uint32_t size)

{

    MpegEncContext *s = avctx->priv_data;



    NVDECContext      *ctx = avctx->internal->hwaccel_priv_data;

    CUVIDPICPARAMS     *pp = &ctx->pic_params;

    CUVIDMPEG2PICPARAMS *ppc = &pp->CodecSpecific.mpeg2;

    FrameDecodeData *fdd;

    NVDECFrame *cf;

    AVFrame *cur_frame = s->current_picture.f;



    int ret, i;



    ret = ff_nvdec_start_frame(avctx, cur_frame);

    if (ret < 0)

        return ret;



    fdd = (FrameDecodeData*)cur_frame->private_ref->data;

    cf  = (NVDECFrame*)fdd->hwaccel_priv;



    *pp = (CUVIDPICPARAMS) {

        .PicWidthInMbs     = (cur_frame->width  + 15) / 16,

        .FrameHeightInMbs  = (cur_frame->height + 15) / 16,

        .CurrPicIdx        = cf->idx,



        .intra_pic_flag    = s->pict_type == AV_PICTURE_TYPE_I,

        .ref_pic_flag      = s->pict_type == AV_PICTURE_TYPE_I ||

                             s->pict_type == AV_PICTURE_TYPE_P,



        .CodecSpecific.mpeg2 = {

            .ForwardRefIdx     = get_ref_idx(s->last_picture.f),

            .BackwardRefIdx    = get_ref_idx(s->next_picture.f),



            .picture_coding_type        = s->pict_type,

            .full_pel_forward_vector    = s->full_pel[0],

            .full_pel_backward_vector   = s->full_pel[1],

            .f_code                     = { { s->mpeg_f_code[0][0],

                                              s->mpeg_f_code[0][1] },

                                            { s->mpeg_f_code[1][0],

                                              s->mpeg_f_code[1][1] } },

            .intra_dc_precision         = s->intra_dc_precision,

            .frame_pred_frame_dct       = s->frame_pred_frame_dct,

            .concealment_motion_vectors = s->concealment_motion_vectors,

            .q_scale_type               = s->q_scale_type,

            .intra_vlc_format           = s->intra_vlc_format,

            .alternate_scan             = s->alternate_scan,

            .top_field_first            = s->top_field_first,

        }

    };



    for (i = 0; i < 64; ++i) {

        ppc->QuantMatrixIntra[i] = s->intra_matrix[i];

        ppc->QuantMatrixInter[i] = s->inter_matrix[i];

    }



    return 0;

}

In the above code snippet, check for potential security vulnerabilities and answer with a single digit: 1 if Vulnerable, 0 if Non-vulnerable.

The guarded evidence of the code snippet is as follows:
GUARDED EVIDENCE: operation-specific observed relations; not a safety proof.
N1 RETURN "return ret;"
N2 CALL "ret < 0"
N3 CALL "s->mpeg_f_code[0][0]"
N4 CALL "s->mpeg_f_code[0]"
N5 CALL "s->mpeg_f_code[0][1]"
N6 CALL "s->mpeg_f_code[0]"
N7 IDENTIFIER "ret"
N2 --CDG--> N3
N2 --CDG--> N4
N2 --CDG--> N5
N2 --CDG--> N6
N2 --CFG--> N7
N7 --CFG--> N1
OP N3
  INPUTS not included/unknown
  DIRECT_CONTROL N2 via=CDG branch=unknown check=cdg_observed_cfg_unknown
  OBSERVED_EXIT N1 from=N2 branch=unknown
OP N4
  INPUTS not included/unknown
  DIRECT_CONTROL N2 via=CDG branch=unknown check=cdg_observed_cfg_unknown
  OBSERVED_EXIT N1 from=N2 branch=unknown
OP N5
  INPUTS not included/unknown
  DIRECT_CONTROL N2 via=CDG branch=unknown check=cdg_observed_cfg_unknown
  OBSERVED_EXIT N1 from=N2 branch=unknown
OP N6
  INPUTS not included/unknown
  DIRECT_CONTROL N2 via=CDG branch=unknown check=cdg_observed_cfg_unknown
  OBSERVED_EXIT N1 from=N2 branch=unknown
UNKNOWN: guard sufficiency, aliasing and feasible execution paths. Missing polarity is unknown.
BOUNDED: omitted operations/context and shortened snippets are not proof of absence.

The following is an example, and it is .


Answer (0 or 1):
~~~~~

## Sample 19 · devign · B1-H2 · seed 42

ID: `devign:validation:24935`  
Prompt SHA-256: `047c9ddae934b1455447988a8dd5406921b50384acaad139e98a423c68e3f4c6`  
Stratum: `no_usable_evidence`

~~~~~text
You are now an excellent programmer. You are conducting a function vulnerability detection task for C/C++ language.

static int i6300esb_init(PCIDevice *dev)

{

    I6300State *d = DO_UPCAST(I6300State, dev, dev);

    uint8_t *pci_conf;

    int io_mem;

    static CPUReadMemoryFunc * const mem_read[3] = {

        i6300esb_mem_readb,

        i6300esb_mem_readw,

        i6300esb_mem_readl,

    };

    static CPUWriteMemoryFunc * const mem_write[3] = {

        i6300esb_mem_writeb,

        i6300esb_mem_writew,

        i6300esb_mem_writel,

    };



    i6300esb_debug("I6300State = %p\n", d);



    d->timer = qemu_new_timer_ns(vm_clock, i6300esb_timer_expired, d);

    d->previous_reboot_flag = 0;



    pci_conf = d->dev.config;

    pci_config_set_vendor_id(pci_conf, PCI_VENDOR_ID_INTEL);

    pci_config_set_device_id(pci_conf, PCI_DEVICE_ID_INTEL_ESB_9);

    pci_config_set_class(pci_conf, PCI_CLASS_SYSTEM_OTHER);



    io_mem = cpu_register_io_memory(mem_read, mem_write, d,

                                    DEVICE_NATIVE_ENDIAN);

    pci_register_bar_simple(&d->dev, 0, 0x10, 0, io_mem);

    /* qemu_register_coalesced_mmio (addr, 0x10); ? */



    return 0;

}

In the above code snippet, check for potential security vulnerabilities and answer with a single digit: 1 if Vulnerable, 0 if Non-vulnerable.

The guarded evidence of the code snippet is as follows:
GUARDED EVIDENCE: operation-specific observed relations; not a safety proof.
N1 CALL "\n        * const mem_read[3] = {\n\n        i6300esb_mem_readb,\n\n        i6300esb_mem_readw,\n\n        i6300esb_mem_readl,\n\n    }\n      "
N2 CALL "\n        * const mem_write[3] = {\n\n        i6300esb_mem_writeb,\n\n        i6300esb_mem_writew,\n\n        i6300esb_mem_writel,\n\n    }\n      "
N3 CALL "d->timer"
N4 CALL "qemu_new_timer_ns(vm_clock, i6300esb_timer_expired, d)"
N5 CALL "d->previous_reboot_flag"
N6 FIELD_IDENTIFIER "timer"
N7 IDENTIFIER "CPUReadMemoryFunc*const*[3]"
N1 --ARGUMENT--> N7
N3 --ARGUMENT--> N6
N4 --REACHING_DEF--> N3
OP N1
  INPUTS N7
  DIRECT_CONTROL unknown: CDG unavailable
OP N2
  INPUTS not included/unknown
  DIRECT_CONTROL unknown: CDG unavailable
OP N3
  INPUTS N6
  DIRECT_CONTROL unknown: CDG unavailable
OP N5
  INPUTS not included/unknown
  DIRECT_CONTROL unknown: CDG unavailable
UNKNOWN: guard sufficiency, aliasing and feasible execution paths. Missing polarity is unknown.
BOUNDED: omitted operations/context and shortened snippets are not proof of absence.

The following is an example, and it is .


Answer (0 or 1):
~~~~~

## Sample 20 · devign · B1-H2 · seed 42

ID: `devign:validation:25232`  
Prompt SHA-256: `2dad73ceaded26e83d02159debeaeb463f28691a9cac82dc865bccb471d9862a`  
Stratum: `no_usable_evidence`

~~~~~text
You are now an excellent programmer. You are conducting a function vulnerability detection task for C/C++ language.

void kvmppc_update_sdr1(target_ulong sdr1)

{

    CPUState *cs;



    CPU_FOREACH(cs) {

        run_on_cpu(cs, kvmppc_pivot_hpt_cpu, RUN_ON_CPU_TARGET_PTR(sdr1));

    }

}

In the above code snippet, check for potential security vulnerabilities and answer with a single digit: 1 if Vulnerable, 0 if Non-vulnerable.

The guarded evidence of the code snippet is as follows:
GUARDED EVIDENCE: operation-specific observed relations; not a safety proof.
N1 METHOD_PARAMETER_IN "target_ulong sdr1"
N2 CALL "CPU_FOREACH(cs)"
N3 CALL "run_on_cpu(cs, kvmppc_pivot_hpt_cpu, RUN_ON_CPU_TARGET_PTR(sdr1))"
N4 CALL "RUN_ON_CPU_TARGET_PTR(sdr1)"
N5 IDENTIFIER "cs"
N6 IDENTIFIER "cs"
N7 IDENTIFIER "<unknown> kvmppc_pivot_hpt_cpu"
N8 IDENTIFIER "sdr1"
N9 LOCAL "CPUState *cs"
N10 LOCAL "<unknown> kvmppc_pivot_hpt_cpu"
N2 --ARGUMENT--> N5
N3 --ARGUMENT--> N4
N3 --ARGUMENT--> N6
N3 --ARGUMENT--> N7
N4 --REACHING_DEF--> N3
N4 --REACHING_DEF--> N6
N4 --REACHING_DEF--> N7
N4 --ARGUMENT--> N8
N5 --REACHING_DEF--> N2
N5 --REACHING_DEF--> N6
N5 --REF--> N9
N6 --REACHING_DEF--> N3
N6 --REACHING_DEF--> N4
N6 --REACHING_DEF--> N7
N6 --REF--> N9
N7 --REACHING_DEF--> N3
N7 --REACHING_DEF--> N4
N7 --REACHING_DEF--> N6
N7 --REF--> N10
N8 --REF--> N1
N8 --REACHING_DEF--> N4
OP N2
  INPUTS N5
  DIRECT_CONTROL unknown: CDG unavailable
OP N3
  INPUTS N4,N6,N7
  DIRECT_CONTROL unknown: CDG unavailable
OP N4
  INPUTS N8
  DIRECT_CONTROL unknown: CDG unavailable
UNKNOWN: guard sufficiency, aliasing and feasible execution paths. Missing polarity is unknown.
BOUNDED: omitted operations/context and shortened snippets are not proof of absence.

The following is an example, and it is .


Answer (0 or 1):
~~~~~

## Sample 21 · devign · B1-H2 · seed 42

ID: `devign:validation:26049`  
Prompt SHA-256: `837c45e41153a63c788bad7b72b51b060bd5adf4a600caf9d16a641cf5dc649d`  
Stratum: `no_usable_evidence`

~~~~~text
You are now an excellent programmer. You are conducting a function vulnerability detection task for C/C++ language.

void laio_cleanup(void *s_)
{
    struct qemu_laio_state *s = s_;
    event_notifier_cleanup(&s->e);
    g_free(s);

In the above code snippet, check for potential security vulnerabilities and answer with a single digit: 1 if Vulnerable, 0 if Non-vulnerable.

The guarded evidence of the code snippet is as follows:
GUARDED EVIDENCE: operation-specific observed relations; not a safety proof.
N1 CALL "event_notifier_cleanup(&s->e)"
N2 CALL "&s->e"
N3 CALL "s->e"
N4 FIELD_IDENTIFIER "e"
N5 IDENTIFIER "s"
N6 IDENTIFIER "s_"
N7 IDENTIFIER "s"
N8 LOCAL "struct qemu_laio_state *s"
N1 --ARGUMENT--> N2
N2 --REACHING_DEF--> N1
N2 --ARGUMENT--> N3
N3 --REACHING_DEF--> N2
N3 --ARGUMENT--> N4
N3 --ARGUMENT--> N7
N5 --REACHING_DEF--> N3
N5 --REACHING_DEF--> N7
N5 --REF--> N8
N6 --REACHING_DEF--> N5
N7 --REF--> N8
OP N3
  INPUTS N4,N7
  DIRECT_CONTROL unknown: CDG unavailable
OP N1
  INPUTS N2
  DIRECT_CONTROL unknown: CDG unavailable
UNKNOWN: guard sufficiency, aliasing and feasible execution paths. Missing polarity is unknown.
BOUNDED: omitted operations/context and shortened snippets are not proof of absence.

The following is an example, and it is .


Answer (0 or 1):
~~~~~

## Sample 22 · devign · B1-H2 · seed 42

ID: `devign:validation:27036`  
Prompt SHA-256: `1683633aa2788c0db10a663cdcd09f964ef79f875b2b2ace6a710f875cbb1b2d`  
Stratum: `no_usable_evidence`

~~~~~text
You are now an excellent programmer. You are conducting a function vulnerability detection task for C/C++ language.

static inline void cris_fidx_i(unsigned int x)

{

	register unsigned int v asm("$r10") = x;

	asm ("fidxi\t[%0]\n" : : "r" (v) );

}

In the above code snippet, check for potential security vulnerabilities and answer with a single digit: 1 if Vulnerable, 0 if Non-vulnerable.

The guarded evidence of the code snippet is as follows:
NO_USABLE_GUARDED_EVIDENCE: no_operation_nodes. Do not infer safety from missing evidence.

The following is an example, and it is .


Answer (0 or 1):
~~~~~

## Sample 23 · devign · B1-H2 · seed 42

ID: `devign:validation:4239`  
Prompt SHA-256: `d1dfb8127bc3f8e83deff5a461fa706e8e1a9120f3e3b5452672bfaf8c992d0e`  
Stratum: `cdg_cluster`

~~~~~text
You are now an excellent programmer. You are conducting a function vulnerability detection task for C/C++ language.

static int normalize_bits(int num, int width)

{

    int i = 0;

    int bits = (width) ? 31 : 15;

    int limit = 1 << (bits - 1);



    if (num) {

        if (num == -1)

            return bits;

        if (num < 0)

            num = ~num;

        for (i = 0; num < limit; i++)

            num <<= 1;

    }

    return i;

}

In the above code snippet, check for potential security vulnerabilities and answer with a single digit: 1 if Vulnerable, 0 if Non-vulnerable.

The guarded evidence of the code snippet is as follows:
GUARDED EVIDENCE: operation-specific observed relations; not a safety proof.
N1 RETURN "return i;"
N2 CALL "1 << (bits - 1)"
N3 CALL "bits - 1"
N4 CALL "num < limit"
N5 CALL "num <<= 1"
N6 IDENTIFIER "bits"
N7 IDENTIFIER "i"
N8 LITERAL "1"
N9 LITERAL "1"
N2 --ARGUMENT--> N3
N2 --ARGUMENT--> N8
N3 --REACHING_DEF--> N2
N3 --ARGUMENT--> N6
N3 --ARGUMENT--> N9
N4 --CDG--> N5
N4 --CFG--> N7
N7 --CFG--> N1
OP N5
  INPUTS not included/unknown
  DIRECT_CONTROL N4 via=CDG branch=unknown check=cfg_one_branch_witness
  OBSERVED_EXIT N1 from=N4 branch=unknown
OP N2
  INPUTS N3,N8
  DIRECT_CONTROL none observed; not proof of absence
OP N3
  INPUTS N6,N9
  DIRECT_CONTROL none observed; not proof of absence
UNKNOWN: guard sufficiency, aliasing and feasible execution paths. Missing polarity is unknown.
BOUNDED: omitted operations/context and shortened snippets are not proof of absence.

The following is an example, and it is .


Answer (0 or 1):
~~~~~

## Sample 24 · devign · B1-H2 · seed 42

ID: `devign:validation:4991`  
Prompt SHA-256: `709799be52dcb764cfd2ea0a4668bd0a48be942572bfaa0a8cd61f4482e82d5f`  
Stratum: `no_usable_evidence`

~~~~~text
You are now an excellent programmer. You are conducting a function vulnerability detection task for C/C++ language.

static void FUNCC(pred8x8_horizontal)(uint8_t *_src, int stride){

    int i;

    pixel *src = (pixel*)_src;

    stride /= sizeof(pixel);



    for(i=0; i<8; i++){

        ((pixel4*)(src+i*stride))[0]=

        ((pixel4*)(src+i*stride))[1]= PIXEL_SPLAT_X4(src[-1+i*stride]);

    }

}

In the above code snippet, check for potential security vulnerabilities and answer with a single digit: 1 if Vulnerable, 0 if Non-vulnerable.

The guarded evidence of the code snippet is as follows:
NO_USABLE_GUARDED_EVIDENCE: no_operation_nodes. Do not infer safety from missing evidence.

The following is an example, and it is .


Answer (0 or 1):
~~~~~

## Sample 25 · devign · B1-H2 · seed 42

ID: `devign:validation:6401`  
Prompt SHA-256: `fbbc02e7a5628c7a8658d59956d407e048cff12611eb271dcdcfa0a0663335a8`  
Stratum: `cdg_cluster`

~~~~~text
You are now an excellent programmer. You are conducting a function vulnerability detection task for C/C++ language.

static void a9_scu_write(void *opaque, target_phys_addr_t offset,

                         uint64_t value, unsigned size)

{

    a9mp_priv_state *s = (a9mp_priv_state *)opaque;

    uint32_t mask;

    uint32_t shift;

    switch (size) {

    case 1:

        mask = 0xff;

        break;

    case 2:

        mask = 0xffff;

        break;

    case 4:

        mask = 0xffffffff;

        break;

    default:

        fprintf(stderr, "Invalid size %u in write to a9 scu register %x\n",

                size, (unsigned)offset);

        return;

    }



    switch (offset) {

    case 0x00: /* Control */

        s->scu_control = value & 1;

        break;

    case 0x4: /* Configuration: RO */

        break;

    case 0x08: case 0x09: case 0x0A: case 0x0B: /* Power Control */

        shift = (offset - 0x8) * 8;

        s->scu_status &= ~(mask << shift);

        s->scu_status |= ((value & mask) << shift);

        break;

    case 0x0c: /* Invalidate All Registers In Secure State */

        /* no-op as we do not implement caches */

        break;

    case 0x40: /* Filtering Start Address Register */

    case 0x44: /* Filtering End Address Register */

        /* RAZ/WI, like an implementation with only one AXI master */

        break;

    case 0x50: /* SCU Access Control Register */

    case 0x54: /* SCU Non-secure Access Control Register */

        /* unimplemented, fall through */

    default:

        break;

    }

}

In the above code snippet, check for potential security vulnerabilities and answer with a single digit: 1 if Vulnerable, 0 if Non-vulnerable.

The guarded evidence of the code snippet is as follows:
GUARDED EVIDENCE: operation-specific observed relations; not a safety proof.
N1 CALL "s->scu_control"
N2 CALL "s->scu_status"
N3 CALL "~(mask << shift)"
N4 CALL "mask << shift"
N5 CALL "s->scu_status"
N6 FIELD_IDENTIFIER "scu_control"
N7 FIELD_IDENTIFIER "scu_status"
N8 IDENTIFIER "offset"
N9 IDENTIFIER "s"
N10 IDENTIFIER "s"
N11 IDENTIFIER "mask"
N12 IDENTIFIER "shift"
N1 --ARGUMENT--> N6
N1 --ARGUMENT--> N9
N2 --REACHING_DEF--> N5
N2 --ARGUMENT--> N7
N2 --ARGUMENT--> N10
N3 --REACHING_DEF--> N2
N3 --ARGUMENT--> N4
N4 --REACHING_DEF--> N3
N4 --ARGUMENT--> N11
N4 --ARGUMENT--> N12
N8 --CDG--> N1
N8 --CDG--> N2
N8 --CDG--> N4
N8 --CDG--> N5
OP N1
  INPUTS N6,N9
  DIRECT_CONTROL N8 via=CDG branch=unknown check=cdg_observed_cfg_unknown
OP N2
  INPUTS N7,N10
  DIRECT_CONTROL N8 via=CDG branch=unknown check=cdg_observed_cfg_unknown
  DATA_NOTE: predicates on related data are not operation controls.
OP N5
  INPUTS not included/unknown
  DIRECT_CONTROL N8 via=CDG branch=unknown check=cdg_observed_cfg_unknown
  DATA_NOTE: predicates on related data are not operation controls.
OP N4
  INPUTS N11,N12
  DIRECT_CONTROL N8 via=CDG branch=unknown check=cdg_observed_cfg_unknown
UNKNOWN: guard sufficiency, aliasing and feasible execution paths. Missing polarity is unknown.
BOUNDED: omitted operations/context and shortened snippets are not proof of absence.

The following is an example, and it is .


Answer (0 or 1):
~~~~~

## Sample 26 · devign · B1-H2 · seed 42

ID: `devign:validation:6440`  
Prompt SHA-256: `3a5c08307858ab3a7828461f7a23ed445239e04df5faa0e21f8deb6b442a1fba`  
Stratum: `no_usable_evidence`

~~~~~text
You are now an excellent programmer. You are conducting a function vulnerability detection task for C/C++ language.

static void t_gen_lsl(TCGv d, TCGv a, TCGv b)

{

	TCGv t0, t_31;



	t0 = tcg_temp_new(TCG_TYPE_TL);

	t_31 = tcg_temp_new(TCG_TYPE_TL);

	tcg_gen_shl_tl(d, a, b);



	tcg_gen_movi_tl(t_31, 31);

	tcg_gen_sub_tl(t0, t_31, b);

	tcg_gen_sar_tl(t0, t0, t_31);

	tcg_gen_and_tl(t0, t0, d);

	tcg_gen_xor_tl(d, d, t0);

	tcg_temp_free(t0);

	tcg_temp_free(t_31);

}

In the above code snippet, check for potential security vulnerabilities and answer with a single digit: 1 if Vulnerable, 0 if Non-vulnerable.

The guarded evidence of the code snippet is as follows:
GUARDED EVIDENCE: operation-specific observed relations; not a safety proof.
N1 CALL "tcg_temp_new(TCG_TYPE_TL)"
N2 CALL "tcg_temp_new(TCG_TYPE_TL)"
N3 CALL "tcg_gen_shl_tl(d, a, b)"
N4 CALL "tcg_gen_movi_tl(t_31, 31)"
N5 IDENTIFIER "<unknown> TCG_TYPE_TL"
N6 IDENTIFIER "<unknown> TCG_TYPE_TL"
N7 IDENTIFIER "d"
N8 IDENTIFIER "a"
N9 IDENTIFIER "b"
N10 IDENTIFIER "t_31"
N11 LITERAL "31"
N1 --ARGUMENT--> N5
N2 --ARGUMENT--> N6
N3 --ARGUMENT--> N7
N3 --ARGUMENT--> N8
N3 --ARGUMENT--> N9
N4 --ARGUMENT--> N10
N4 --ARGUMENT--> N11
OP N1
  INPUTS N5
  DIRECT_CONTROL unknown: CDG unavailable
OP N2
  INPUTS N6
  DIRECT_CONTROL unknown: CDG unavailable
OP N3
  INPUTS N7,N8,N9
  DIRECT_CONTROL unknown: CDG unavailable
OP N4
  INPUTS N10,N11
  DIRECT_CONTROL unknown: CDG unavailable
UNKNOWN: guard sufficiency, aliasing and feasible execution paths. Missing polarity is unknown.
BOUNDED: omitted operations/context and shortened snippets are not proof of absence.

The following is an example, and it is .


Answer (0 or 1):
~~~~~

## Sample 27 · devign · B1-H2 · seed 42

ID: `devign:validation:6612`  
Prompt SHA-256: `2f22cea3f03107303c9bb385ecf8c7b00d522f5c1edeed5947027d6e8e3913a6`  
Stratum: `cdg_cluster`

~~~~~text
You are now an excellent programmer. You are conducting a function vulnerability detection task for C/C++ language.

static void an5206_init(MachineState *machine)

{

    ram_addr_t ram_size = machine->ram_size;

    const char *cpu_model = machine->cpu_model;

    const char *kernel_filename = machine->kernel_filename;

    M68kCPU *cpu;

    CPUM68KState *env;

    int kernel_size;

    uint64_t elf_entry;

    hwaddr entry;

    MemoryRegion *address_space_mem = get_system_memory();

    MemoryRegion *ram = g_new(MemoryRegion, 1);

    MemoryRegion *sram = g_new(MemoryRegion, 1);



    if (!cpu_model) {

        cpu_model = "m5206";

    }

    cpu = M68K_CPU(cpu_generic_init(TYPE_M68K_CPU, cpu_model));

    env = &cpu->env;



    /* Initialize CPU registers.  */

    env->vbr = 0;

    /* TODO: allow changing MBAR and RAMBAR.  */

    env->mbar = AN5206_MBAR_ADDR | 1;

    env->rambar0 = AN5206_RAMBAR_ADDR | 1;



    /* DRAM at address zero */

    memory_region_allocate_system_memory(ram, NULL, "an5206.ram", ram_size);

    memory_region_add_subregion(address_space_mem, 0, ram);



    /* Internal SRAM.  */

    memory_region_init_ram(sram, NULL, "an5206.sram", 512, &error_fatal);

    memory_region_add_subregion(address_space_mem, AN5206_RAMBAR_ADDR, sram);



    mcf5206_init(address_space_mem, AN5206_MBAR_ADDR, cpu);



    /* Load kernel.  */

    if (!kernel_filename) {

        if (qtest_enabled()) {

            return;

        }

        fprintf(stderr, "Kernel image must be specified\n");

        exit(1);

    }



    kernel_size = load_elf(kernel_filename, NULL, NULL, &elf_entry,

                           NULL, NULL, 1, EM_68K, 0, 0);

    entry = elf_entry;

    if (kernel_size < 0) {

        kernel_size = load_uimage(kernel_filename, &entry, NULL, NULL,

                                  NULL, NULL);

    }

    if (kernel_size < 0) {

        kernel_size = load_image_targphys(kernel_filename, KERNEL_LOAD_ADDR,

                                          ram_size - KERNEL_LOAD_ADDR);

        entry = KERNEL_LOAD_ADDR;

    }

    if (kernel_size < 0) {

        fprintf(stderr, "qemu: could not load kernel '%s'\n", kernel_filename);

        exit(1);

    }



    env->pc = entry;

}

In the above code snippet, check for potential security vulnerabilities and answer with a single digit: 1 if Vulnerable, 0 if Non-vulnerable.

The guarded evidence of the code snippet is as follows:
GUARDED EVIDENCE: operation-specific observed relations; not a safety proof.
N1 RETURN "return;"
N2 CALL "!kernel_filename"
N3 CALL "qtest_enabled()"
N4 CALL "exit(1)"
N5 CALL "kernel_size < 0"
N6 CALL "ram_size - KERNEL_LOAD_ADDR"
N7 CALL "env->pc"
N2 --CDG--> N3
N2 --CFG--> N3
N2 --CDG--> N7
N3 --CFG--> N1
N3 --CDG--> N4
N3 --CDG--> N7
N5 --CDG--> N6
OP N7
  INPUTS not included/unknown
  DIRECT_CONTROL N2 via=CDG branch=unknown check=cdg_observed_cfg_unknown
  DIRECT_CONTROL N3 via=CDG branch=unknown check=cdg_observed_cfg_unknown
  OBSERVED_EXIT N1 from=N2 branch=unknown
  OBSERVED_EXIT N1 from=N3 branch=unknown
OP N6
  INPUTS not included/unknown
  DIRECT_CONTROL N5 via=CDG branch=unknown check=cfg_one_branch_witness
OP N3
  INPUTS not included/unknown
  DIRECT_CONTROL N2 via=CDG branch=unknown check=cdg_observed_cfg_unknown
OP N4
  INPUTS not included/unknown
  DIRECT_CONTROL N3 via=CDG branch=unknown check=cdg_observed_cfg_unknown
  OBSERVED_EXIT N1 from=N3 branch=unknown
UNKNOWN: guard sufficiency, aliasing and feasible execution paths. Missing polarity is unknown.
BOUNDED: omitted operations/context and shortened snippets are not proof of absence.

The following is an example, and it is .


Answer (0 or 1):
~~~~~

## Sample 28 · devign · B1-H2 · seed 42

ID: `devign:validation:6686`  
Prompt SHA-256: `bfb13a2ab23246bb43e28f021d35d8ff5a594c40d072f831ae85dd9d3130e083`  
Stratum: `missing_cpg`

~~~~~text
You are now an excellent programmer. You are conducting a function vulnerability detection task for C/C++ language.

void CALLBACK host_alarm_handler(UINT uTimerID, UINT uMsg,

                                 DWORD_PTR dwUser, DWORD_PTR dw1, DWORD_PTR dw2)

#else

static void host_alarm_handler(int host_signum)

#endif

{

#if 0

#define DISP_FREQ 1000

    {

        static int64_t delta_min = INT64_MAX;

        static int64_t delta_max, delta_cum, last_clock, delta, ti;

        static int count;

        ti = qemu_get_clock(vm_clock);

        if (last_clock != 0) {

            delta = ti - last_clock;

            if (delta < delta_min)

                delta_min = delta;

            if (delta > delta_max)

                delta_max = delta;

            delta_cum += delta;

            if (++count == DISP_FREQ) {

                printf("timer: min=%" PRId64 " us max=%" PRId64 " us avg=%" PRId64 " us avg_freq=%0.3f Hz\n",

                       muldiv64(delta_min, 1000000, ticks_per_sec),

                       muldiv64(delta_max, 1000000, ticks_per_sec),

                       muldiv64(delta_cum, 1000000 / DISP_FREQ, ticks_per_sec),

                       (double)ticks_per_sec / ((double)delta_cum / DISP_FREQ));

                count = 0;

                delta_min = INT64_MAX;

                delta_max = 0;

                delta_cum = 0;

            }

        }

        last_clock = ti;

    }

#endif

    if (alarm_has_dynticks(alarm_timer) ||

        qemu_timer_expired(active_timers[QEMU_TIMER_VIRTUAL],

                           qemu_get_clock(vm_clock)) ||

        qemu_timer_expired(active_timers[QEMU_TIMER_REALTIME],

                           qemu_get_clock(rt_clock))) {

#ifdef _WIN32

        struct qemu_alarm_win32 *data = ((struct qemu_alarm_timer*)dwUser)->priv;

        SetEvent(data->host_alarm);

#endif

        CPUState *env = next_cpu;



        /* stop the currently executing cpu because a timer occured */

        cpu_interrupt(env, CPU_INTERRUPT_EXIT);

#ifdef USE_KQEMU

        if (env->kqemu_enabled) {

            kqemu_cpu_interrupt(env);

        }

#endif

        event_pending = 1;

    }

}

In the above code snippet, check for potential security vulnerabilities and answer with a single digit: 1 if Vulnerable, 0 if Non-vulnerable.

The node information of the code snippet is as follows:

The edge information of the code snippet is as follows:


The following is an example, and it is .


Answer (0 or 1):
~~~~~

## Sample 29 · devign · B1-H2 · seed 42

ID: `devign:validation:7231`  
Prompt SHA-256: `b123ae9d4c0ac10a01cc98f665035af7b8c02f6d321d6cc072fb07336436f530`  
Stratum: `no_usable_evidence`

~~~~~text
You are now an excellent programmer. You are conducting a function vulnerability detection task for C/C++ language.

static inline int fp_reg_offset(int regno, TCGMemOp size)

{

    int offs = offsetof(CPUARMState, vfp.regs[regno * 2]);

#ifdef HOST_WORDS_BIGENDIAN

    offs += (8 - (1 << size));

#endif

    return offs;

}

In the above code snippet, check for potential security vulnerabilities and answer with a single digit: 1 if Vulnerable, 0 if Non-vulnerable.

The guarded evidence of the code snippet is as follows:
GUARDED EVIDENCE: operation-specific observed relations; not a safety proof.
N1 METHOD_PARAMETER_IN "int regno"
N2 CALL "offsetof(CPUARMState, vfp.regs[regno * 2])"
N3 CALL "vfp.regs[regno * 2]"
N4 CALL "vfp.regs"
N5 CALL "regno * 2"
N6 FIELD_IDENTIFIER "regs"
N7 IDENTIFIER "<unknown> CPUARMState"
N8 IDENTIFIER "<unknown> vfp"
N9 IDENTIFIER "regno"
N10 LITERAL "2"
N11 LOCAL "<unknown> CPUARMState"
N2 --ARGUMENT--> N3
N2 --ARGUMENT--> N7
N3 --REACHING_DEF--> N2
N3 --ARGUMENT--> N4
N3 --ARGUMENT--> N5
N3 --REACHING_DEF--> N7
N4 --ARGUMENT--> N6
N4 --ARGUMENT--> N8
N5 --ARGUMENT--> N9
N5 --ARGUMENT--> N10
N7 --REACHING_DEF--> N2
N7 --REACHING_DEF--> N3
N7 --REF--> N11
N9 --REF--> N1
N9 --REACHING_DEF--> N5
OP N3
  INPUTS N4,N5
  DIRECT_CONTROL unknown: CDG unavailable
OP N5
  INPUTS N9,N10
  DIRECT_CONTROL unknown: CDG unavailable
OP N2
  INPUTS N3,N7
  DIRECT_CONTROL unknown: CDG unavailable
UNKNOWN: guard sufficiency, aliasing and feasible execution paths. Missing polarity is unknown.
BOUNDED: omitted operations/context and shortened snippets are not proof of absence.

The following is an example, and it is .


Answer (0 or 1):
~~~~~

## Sample 30 · devign · B1-H2 · seed 42

ID: `devign:validation:8160`  
Prompt SHA-256: `9bc6fee24a164940e80cea12bc18d1178eaa7707c57cf674c1f47574b3149241`  
Stratum: `closed_prefix`

~~~~~text
You are now an excellent programmer. You are conducting a function vulnerability detection task for C/C++ language.

static int vpx_decode(AVCodecContext *avctx,

                      void *data, int *got_frame, AVPacket *avpkt)

{

    VPxContext *ctx = avctx->priv_data;

    AVFrame *picture = data;

    const void *iter = NULL;

    const void *iter_alpha = NULL;

    struct vpx_image *img, *img_alpha;

    int ret;

    uint8_t *side_data = NULL;

    int side_data_size = 0;



    ret = decode_frame(avctx, &ctx->decoder, avpkt->data, avpkt->size);

    if (ret)

        return ret;



    side_data = av_packet_get_side_data(avpkt,

                                        AV_PKT_DATA_MATROSKA_BLOCKADDITIONAL,

                                        &side_data_size);

    if (side_data_size > 1) {

        const uint64_t additional_id = AV_RB64(side_data);

        side_data += 8;

        side_data_size -= 8;

        if (additional_id == 1) {  // 1 stands for alpha channel data.

            if (!ctx->has_alpha_channel) {

                ctx->has_alpha_channel = 1;

                ret = vpx_init(avctx,

#if CONFIG_LIBVPX_VP8_DECODER && CONFIG_LIBVPX_VP9_DECODER

                               (avctx->codec_id == AV_CODEC_ID_VP8) ?

                               &vpx_codec_vp8_dx_algo : &vpx_codec_vp9_dx_algo,

#elif CONFIG_LIBVPX_VP8_DECODER

                               &vpx_codec_vp8_dx_algo,

#else

                               &vpx_codec_vp9_dx_algo,

#endif

                               1);

                if (ret)

                    return ret;

            }

            ret = decode_frame(avctx, &ctx->decoder_alpha, side_data,

                               side_data_size);

            if (ret)

                return ret;

        }

    }



    if ((img = vpx_codec_get_frame(&ctx->decoder, &iter)) &&

        (!ctx->has_alpha_channel ||

         (img_alpha = vpx_codec_get_frame(&ctx->decoder_alpha, &iter_alpha)))) {

        uint8_t *planes[4];

        int linesizes[4];



        if (img->d_w > img->w || img->d_h > img->h) {

            av_log(avctx, AV_LOG_ERROR, "Display dimensions %dx%d exceed storage %dx%d\n",

                   img->d_w, img->d_h, img->w, img->h);

            return AVERROR_EXTERNAL;

        }



        if ((ret = set_pix_fmt(avctx, img, ctx->has_alpha_channel)) < 0) {

#ifdef VPX_IMG_FMT_HIGHBITDEPTH

            av_log(avctx, AV_LOG_ERROR, "Unsupported output colorspace (%d) / bit_depth (%d)\n",

                   img->fmt, img->bit_depth);

#else

            av_log(avctx, AV_LOG_ERROR, "Unsupported output colorspace (%d) / bit_depth (%d)\n",

                   img->fmt, 8);

#endif

            return ret;

        }



        if ((int) img->d_w != avctx->width || (int) img->d_h != avctx->height) {

            av_log(avctx, AV_LOG_INFO, "dimension change! %dx%d -> %dx%d\n",

                   avctx->width, avctx->height, img->d_w, img->d_h);

            ret = ff_set_dimensions(avctx, img->d_w, img->d_h);

            if (ret < 0)

                return ret;

        }

        if ((ret = ff_get_buffer(avctx, picture, 0)) < 0)

            return ret;



        planes[0] = img->planes[VPX_PLANE_Y];

        planes[1] = img->planes[VPX_PLANE_U];

        planes[2] = img->planes[VPX_PLANE_V];

        planes[3] =

            ctx->has_alpha_channel ? img_alpha->planes[VPX_PLANE_Y] : NULL;

        linesizes[0] = img->stride[VPX_PLANE_Y];

        linesizes[1] = img->stride[VPX_PLANE_U];

        linesizes[2] = img->stride[VPX_PLANE_V];

        linesizes[3] =

            ctx->has_alpha_channel ? img_alpha->stride[VPX_PLANE_Y] : 0;

        av_image_copy(picture->data, picture->linesize, (const uint8_t**)planes,

                      linesizes, avctx->pix_fmt, img->d_w, img->d_h);

        *got_frame           = 1;

    }

    return avpkt->size;

}

In the above code snippet, check for potential security vulnerabilities and answer with a single digit: 1 if Vulnerable, 0 if Non-vulnerable.

The guarded evidence of the code snippet is as follows:
GUARDED EVIDENCE: operation-specific observed relations; not a safety proof.
N1 CALL "avctx->priv_data"
N2 CALL "ret != 0"
N3 CALL "\n        av_packet_get_side_data(avpkt,\n\n                                        AV_PKT_DATA_MATROSKA_BLOCKADDITIONAL,\n\n                                        &side_data_size)\n…"
N4 CALL "&side_data_size"
N5 CALL "side_data_size > 1"
N6 CALL "AV_RB64(side_data)"
N7 CALL "additional_id == 1"
N8 CALL "ctx->has_alpha_channel"
N2 --CDG--> N3
N3 --ARGUMENT--> N4
N4 --REACHING_DEF--> N3
N5 --CDG--> N6
N7 --CDG--> N8
OP N8
  INPUTS not included/unknown
  DIRECT_CONTROL N7 via=CDG branch=unknown check=cdg_observed_cfg_unknown
OP N3
  INPUTS N4
  DIRECT_CONTROL N2 via=CDG branch=unknown check=cdg_observed_cfg_unknown
  DATA_NOTE: predicates on related data are not operation controls.
OP N6
  INPUTS not included/unknown
  DIRECT_CONTROL N5 via=CDG branch=unknown check=cdg_observed_cfg_unknown
OP N1
  INPUTS not included/unknown
  DIRECT_CONTROL none observed; not proof of absence
UNKNOWN: guard sufficiency, aliasing and feasible execution paths. Missing polarity is unknown.
BOUNDED: omitted operations/context and shortened snippets are not proof of absence.

The following is an example, and it is .


Answer (0 or 1):
~~~~~

## Sample 31 · reveal · B1-H2 · seed 42

ID: `reveal:validation:108`  
Prompt SHA-256: `8b1db759fdedbdcd90d476f7225a9d68a4486407704ac3e0634d169c1f2183ae`  
Stratum: `no_usable_evidence`

~~~~~text
You are now an excellent programmer. You are conducting a function vulnerability detection task for C/C++ language.

int kvm_device_intx_set_mask ( KVMState * s , uint32_t dev_id , bool masked ) {
 struct kvm_assigned_pci_dev dev_data = {
 . assigned_dev_id = dev_id , . flags = masked ? KVM_DEV_ASSIGN_MASK_INTX : 0 , }
 ;
 return kvm_vm_ioctl ( s , KVM_ASSIGN_SET_INTX_MASK , & dev_data ) ;
 }

In the above code snippet, check for potential security vulnerabilities and answer with a single digit: 1 if Vulnerable, 0 if Non-vulnerable.

The guarded evidence of the code snippet is as follows:
GUARDED EVIDENCE: operation-specific observed relations; not a safety proof.
N1 CALL "kvm_vm_ioctl ( s , KVM_ASSIGN_SET_INTX_MASK , & dev_data )"
N2 CALL "& dev_data"
N3 IDENTIFIER "s"
N4 IDENTIFIER "<unknown> KVM_ASSIGN_SET_INTX_MASK"
N1 --ARGUMENT--> N2
N1 --ARGUMENT--> N3
N1 --ARGUMENT--> N4
OP N1
  INPUTS N2,N3,N4
  DIRECT_CONTROL unknown: CDG unavailable
UNKNOWN: guard sufficiency, aliasing and feasible execution paths. Missing polarity is unknown.
BOUNDED: omitted operations/context and shortened snippets are not proof of absence.

The following is an example, and it is .


Answer (0 or 1):
~~~~~

## Sample 32 · reveal · B1-H2 · seed 42

ID: `reveal:validation:1088`  
Prompt SHA-256: `d97f87ba09bedb243c380f11c7119cb102daa39b9670ae308ffb4c4029526764`  
Stratum: `no_usable_evidence`

~~~~~text
You are now an excellent programmer. You are conducting a function vulnerability detection task for C/C++ language.

static void ps2_set_ledstate ( PS2KbdState * s , int ledstate ) {
 trace_ps2_set_ledstate ( s , ledstate ) ;
 s -> ledstate = ledstate ;
 kbd_put_ledstate ( ledstate ) ;
 }

In the above code snippet, check for potential security vulnerabilities and answer with a single digit: 1 if Vulnerable, 0 if Non-vulnerable.

The guarded evidence of the code snippet is as follows:
GUARDED EVIDENCE: operation-specific observed relations; not a safety proof.
N1 METHOD_PARAMETER_IN "PS2KbdState * s"
N2 METHOD_PARAMETER_IN "int ledstate"
N3 CALL "trace_ps2_set_ledstate ( s , ledstate )"
N4 CALL "s -> ledstate"
N5 CALL "kbd_put_ledstate ( ledstate )"
N6 FIELD_IDENTIFIER "ledstate"
N7 IDENTIFIER "s"
N8 IDENTIFIER "ledstate"
N9 IDENTIFIER "s"
N10 IDENTIFIER "ledstate"
N11 IDENTIFIER "ledstate"
N3 --ARGUMENT--> N7
N3 --ARGUMENT--> N8
N4 --ARGUMENT--> N6
N4 --ARGUMENT--> N9
N5 --ARGUMENT--> N11
N7 --REF--> N1
N7 --REACHING_DEF--> N3
N7 --REACHING_DEF--> N8
N7 --REACHING_DEF--> N9
N8 --REF--> N2
N8 --REACHING_DEF--> N3
N8 --REACHING_DEF--> N7
N8 --REACHING_DEF--> N10
N9 --REF--> N1
N10 --REF--> N2
N10 --REACHING_DEF--> N4
N10 --REACHING_DEF--> N11
N11 --REF--> N2
N11 --REACHING_DEF--> N5
OP N4
  INPUTS N6,N9
  DIRECT_CONTROL unknown: CDG unavailable
OP N3
  INPUTS N7,N8
  DIRECT_CONTROL unknown: CDG unavailable
OP N5
  INPUTS N11
  DIRECT_CONTROL unknown: CDG unavailable
UNKNOWN: guard sufficiency, aliasing and feasible execution paths. Missing polarity is unknown.
BOUNDED: omitted operations/context and shortened snippets are not proof of absence.

The following is an example, and it is .


Answer (0 or 1):
~~~~~

## Sample 33 · reveal · B1-H2 · seed 42

ID: `reveal:validation:1089`  
Prompt SHA-256: `40d14f25f86a679522b2fc87c4195fc650122998c7fb98cff28c0a7c335c9208`  
Stratum: `no_usable_evidence`

~~~~~text
You are now an excellent programmer. You are conducting a function vulnerability detection task for C/C++ language.

void * TSHttpTxnArgGet ( TSHttpTxn txnp , int arg_idx ) {
 sdk_assert ( sdk_sanity_check_txn ( txnp ) == TS_SUCCESS ) ;
 sdk_assert ( arg_idx >= 0 && arg_idx < HTTP_SSN_TXN_MAX_USER_ARG ) ;
 HttpSM * sm = ( HttpSM * ) txnp ;
 return sm -> t_state . user_args [ arg_idx ] ;
 }

In the above code snippet, check for potential security vulnerabilities and answer with a single digit: 1 if Vulnerable, 0 if Non-vulnerable.

The guarded evidence of the code snippet is as follows:
GUARDED EVIDENCE: operation-specific observed relations; not a safety proof.
N1 CALL "sdk_assert ( sdk_sanity_check_txn ( txnp ) == TS_SUCCESS )"
N2 CALL "sdk_sanity_check_txn ( txnp ) == TS_SUCCESS"
N3 CALL "sdk_sanity_check_txn ( txnp )"
N4 CALL "sm -> t_state . user_args [ arg_idx ]"
N5 CALL "sm -> t_state"
N6 IDENTIFIER "txnp"
N7 IDENTIFIER "<unknown> TS_SUCCESS"
N1 --ARGUMENT--> N2
N2 --REACHING_DEF--> N1
N2 --ARGUMENT--> N3
N2 --ARGUMENT--> N7
N3 --REACHING_DEF--> N2
N3 --ARGUMENT--> N6
OP N4
  INPUTS not included/unknown
  DIRECT_CONTROL none observed; not proof of absence
OP N5
  INPUTS not included/unknown
  DIRECT_CONTROL none observed; not proof of absence
OP N1
  INPUTS N2
  DIRECT_CONTROL none observed; not proof of absence
OP N3
  INPUTS N6
  DIRECT_CONTROL none observed; not proof of absence
UNKNOWN: guard sufficiency, aliasing and feasible execution paths. Missing polarity is unknown.
BOUNDED: omitted operations/context and shortened snippets are not proof of absence.

The following is an example, and it is .


Answer (0 or 1):
~~~~~

## Sample 34 · reveal · B1-H2 · seed 42

ID: `reveal:validation:1202`  
Prompt SHA-256: `b7a2ffa52cea13b5598eafe5aae1014bd7fc635b2adf4ef4fad6b18dcf1f845e`  
Stratum: `closed_prefix`

~~~~~text
You are now an excellent programmer. You are conducting a function vulnerability detection task for C/C++ language.

static cmsBool Type_ParametricCurve_Write ( struct _cms_typehandler_struct * self , cmsIOHANDLER * io , void * Ptr , cmsUInt32Number nItems ) {
 cmsToneCurve * Curve = ( cmsToneCurve * ) Ptr ;
 int i , nParams , typen ;
 static const int ParamsByType [ ] = {
 0 , 1 , 3 , 4 , 5 , 7 }
 ;
 typen = Curve -> Segments [ 0 ] . Type ;
 if ( Curve -> nSegments > 1 || typen < 1 ) {
 cmsSignalError ( self -> ContextID , cmsERROR_UNKNOWN_EXTENSION , "Multisegment or Inverted parametric curves cannot be written" ) ;
 return FALSE ;
 }
 if ( typen > 5 ) {
 cmsSignalError ( self -> ContextID , cmsERROR_UNKNOWN_EXTENSION , "Unsupported parametric curve" ) ;
 return FALSE ;
 }
 nParams = ParamsByType [ typen ] ;
 if ( ! _cmsWriteUInt16Number ( io , ( cmsUInt16Number ) ( Curve -> Segments [ 0 ] . Type - 1 ) ) ) return FALSE ;
 if ( ! _cmsWriteUInt16Number ( io , 0 ) ) return FALSE ;
 for ( i = 0 ;
 i < nParams ;
 i ++ ) {
 if ( ! _cmsWrite15Fixed16Number ( io , Curve -> Segments [ 0 ] . Params [ i ] ) ) return FALSE ;
 }
 return TRUE ;
 cmsUNUSED_PARAMETER ( nItems ) ;
 }

In the above code snippet, check for potential security vulnerabilities and answer with a single digit: 1 if Vulnerable, 0 if Non-vulnerable.

The guarded evidence of the code snippet is as follows:
GUARDED EVIDENCE: operation-specific observed relations; not a safety proof.
N1 CALL "Curve -> Segments [ 0 ] . Type"
N2 CALL "Curve -> Segments [ 0 ]"
N3 CALL "Curve -> nSegments > 1 || typen < 1"
N4 CALL "self -> ContextID"
N5 CALL "typen > 5"
N6 CALL "self -> ContextID"
N7 CALL "ParamsByType [ typen ]"
N8 CALL "Curve -> Segments [ 0 ]"
N1 --ARGUMENT--> N2
N1 --REACHING_DEF--> N8
N3 --CDG--> N4
N5 --CDG--> N6
N5 --CDG--> N7
N5 --CDG--> N8
OP N4
  INPUTS not included/unknown
  DIRECT_CONTROL N3 via=CDG branch=unknown check=cdg_observed_cfg_unknown
OP N6
  INPUTS not included/unknown
  DIRECT_CONTROL N5 via=CDG branch=unknown check=cdg_observed_cfg_unknown
OP N7
  INPUTS not included/unknown
  DIRECT_CONTROL N5 via=CDG branch=unknown check=cdg_observed_cfg_unknown
OP N8
  INPUTS not included/unknown
  DIRECT_CONTROL N5 via=CDG branch=unknown check=cdg_observed_cfg_unknown
UNKNOWN: guard sufficiency, aliasing and feasible execution paths. Missing polarity is unknown.
BOUNDED: omitted operations/context and shortened snippets are not proof of absence.

The following is an example, and it is .


Answer (0 or 1):
~~~~~

## Sample 35 · reveal · B1-H2 · seed 42

ID: `reveal:validation:1210`  
Prompt SHA-256: `56cfd610f9d3731840ca665cc92e4dcc87fd6494b9a2679246570ae47e4e5f25`  
Stratum: `missing_cpg`

~~~~~text
You are now an excellent programmer. You are conducting a function vulnerability detection task for C/C++ language.

static ossl_inline void lh_ ## type ## _set_down_load ( LHASH_OF ( type ) * lh , unsigned long dl ) {
 OPENSSL_LH_set_down_load ( ( OPENSSL_LHASH * ) lh , dl ) ;
 }
 static ossl_inline void lh_ ## type ## _doall ( LHASH_OF ( type ) * lh , void ( * doall ) ( type * ) ) {
 OPENSSL_LH_doall ( ( OPENSSL_LHASH * ) lh , ( OPENSSL_LH_DOALL_FUNC ) doall ) ;
 }
 LHASH_OF ( type ) # define IMPLEMENT_LHASH_DOALL_ARG_CONST ( type , argtype ) int_implement_lhash_doall ( type , argtype , const type ) # define IMPLEMENT_LHASH_DOALL_ARG ( type , argtype ) int_implement_lhash_doall ( type , argtype , type ) # define int_implement_lhash_doall ( type , argtype , cbargtype ) static ossl_inline void lh_ ## type ## _doall_ ## argtype ( LHASH_OF ( type ) * lh , void ( * fn ) ( cbargtype * , argtype * ) , argtype * arg ) {
 OPENSSL_LH_doall_arg ( ( OPENSSL_LHASH * ) lh , ( OPENSSL_LH_DOALL_FUNCARG ) fn , ( void * ) arg ) ;
 }
 LHASH_OF ( type ) DEFINE_LHASH_OF ( OPENSSL_STRING )

In the above code snippet, check for potential security vulnerabilities and answer with a single digit: 1 if Vulnerable, 0 if Non-vulnerable.

The node information of the code snippet is as follows:

The edge information of the code snippet is as follows:


The following is an example, and it is .


Answer (0 or 1):
~~~~~

## Sample 36 · reveal · B1-H2 · seed 42

ID: `reveal:validation:1238`  
Prompt SHA-256: `a0bd089bc2bcc328e6539c4b4cf667b13dc85423b2139125087fd3f8a83bf8e1`  
Stratum: `cdg_cluster`

~~~~~text
You are now an excellent programmer. You are conducting a function vulnerability detection task for C/C++ language.

static int decode_udvm_multitype_operand ( guint8 * buff , guint operand_address , guint16 * value ) {
 guint test_bits ;
 guint bytecode ;
 guint offset = operand_address ;
 guint16 operand ;
 guint32 result ;
 guint8 temp_data ;
 guint16 temp_data16 ;
 guint16 memmory_addr = 0 ;
 * value = 0 ;
 bytecode = buff [ operand_address ] ;
 test_bits = ( bytecode & 0xc0 ) >> 6 ;
 switch ( test_bits ) {
 case 0 : operand = buff [ operand_address ] ;
 * value = operand ;
 offset ++ ;
 break ;
 case 1 : memmory_addr = ( bytecode & 0x3f ) * 2 ;
 temp_data16 = buff [ memmory_addr ] << 8 ;
 temp_data16 = temp_data16 | buff [ ( memmory_addr + 1 ) & 0xffff ] ;
 * value = temp_data16 ;
 offset ++ ;
 break ;
 case 2 : test_bits = ( bytecode & 0xe0 ) >> 5 ;
 if ( test_bits == 5 ) {
 temp_data = buff [ operand_address ] & 0x1f ;
 operand = temp_data << 8 ;
 temp_data = buff [ ( operand_address + 1 ) & 0xffff ] ;
 operand = operand | temp_data ;
 * value = operand ;
 offset = offset + 2 ;
 }
 else {
 test_bits = ( bytecode & 0xf0 ) >> 4 ;
 if ( test_bits == 9 ) {
 temp_data = buff [ operand_address ] & 0x0f ;
 operand = temp_data << 8 ;
 temp_data = buff [ ( operand_address + 1 ) & 0xffff ] ;
 operand = operand | temp_data ;
 operand = operand + 61440 ;
 * value = operand ;
 offset = offset + 2 ;
 }
 else {
 test_bits = ( bytecode & 0x08 ) >> 3 ;
 if ( test_bits == 1 ) {
 result = 1 << ( ( buff [ operand_address ] & 0x07 ) + 8 ) ;
 operand = result & 0xffff ;
 * value = operand ;
 offset ++ ;
 }
 else {
 test_bits = ( bytecode & 0x0e ) >> 1 ;
 if ( test_bits == 3 ) {
 result = 1 << ( ( buff [ operand_address ] & 0x01 ) + 6 ) ;
 operand = result & 0xffff ;
 * value = operand ;
 offset ++ ;
 }
 else {
 offset ++ ;
 temp_data16 = buff [ ( operand_address + 1 ) & 0xffff ] << 8 ;
 temp_data16 = temp_data16 | buff [ ( operand_address + 2 ) & 0xffff ] ;
 if ( ( bytecode & 0x01 ) == 1 ) {
 memmory_addr = temp_data16 ;
 temp_data16 = buff [ memmory_addr ] << 8 ;
 temp_data16 = temp_data16 | buff [ ( memmory_addr + 1 ) & 0xffff ] ;
 }
 * value = temp_data16 ;
 offset = offset + 2 ;
 }
 }
 }
 }
 break ;
 case 3 : test_bits = ( bytecode & 0x20 ) >> 5 ;
 if ( test_bits == 1 ) {
 operand = ( buff [ operand_address ] & 0x1f ) + 65504 ;
 * value = operand ;
 offset ++ ;
 }
 else {
 memmory_addr = buff [ operand_address ] & 0x1f ;
 memmory_addr = memmory_addr << 8 ;
 memmory_addr = memmory_addr | buff [ ( operand_address + 1 ) & 0xffff ] ;
 temp_data16 = buff [ memmory_addr ] << 8 ;
 temp_data16 = temp_data16 | buff [ ( memmory_addr + 1 ) & 0xffff ] ;
 * value = temp_data16 ;
 offset = offset + 2 ;
 }
 default : break ;
 }
 return offset ;
 }

In the above code snippet, check for potential security vulnerabilities and answer with a single digit: 1 if Vulnerable, 0 if Non-vulnerable.

The guarded evidence of the code snippet is as follows:
GUARDED EVIDENCE: operation-specific observed relations; not a safety proof.
N1 CALL "test_bits == 5"
N2 CALL "buff [ operand_address ]"
N3 CALL "buff [ ( operand_address + 1 ) & 0xffff ]"
N4 CALL "* value"
N5 CALL "test_bits == 9"
N6 CALL "buff [ ( operand_address + 1 ) & 0xffff ]"
N1 --CDG--> N2
N1 --CDG--> N3
N1 --CDG--> N4
N5 --CDG--> N6
OP N2
  INPUTS not included/unknown
  DIRECT_CONTROL N1 via=CDG branch=unknown check=cdg_observed_cfg_unknown
OP N3
  INPUTS not included/unknown
  DIRECT_CONTROL N1 via=CDG branch=unknown check=cdg_observed_cfg_unknown
OP N4
  INPUTS not included/unknown
  DIRECT_CONTROL N1 via=CDG branch=unknown check=cdg_observed_cfg_unknown
OP N6
  INPUTS not included/unknown
  DIRECT_CONTROL N5 via=CDG branch=unknown check=cdg_observed_cfg_unknown
UNKNOWN: guard sufficiency, aliasing and feasible execution paths. Missing polarity is unknown.
BOUNDED: omitted operations/context and shortened snippets are not proof of absence.

The following is an example, and it is .


Answer (0 or 1):
~~~~~

## Sample 37 · reveal · B1-H2 · seed 42

ID: `reveal:validation:1259`  
Prompt SHA-256: `6d8ffa4cec111660cb881f050bdae2b1cb029143690aafc56b92f75a16c0a274`  
Stratum: `missing_cpg`

~~~~~text
You are now an excellent programmer. You are conducting a function vulnerability detection task for C/C++ language.

void # ifdef M_DEBUG mpi_debug_resize ( MPI a , unsigned nlimbs , const char * info ) # else mpi_resize ( MPI a , unsigned nlimbs ) # endif {
 if ( nlimbs <= a -> alloced ) return ;
 # ifdef M_DEBUG if ( a -> d ) a -> d = m_debug_realloc ( a -> d , nlimbs * sizeof ( mpi_limb_t ) , info ) ;
 else a -> d = m_debug_alloc_clear ( nlimbs * sizeof ( mpi_limb_t ) , info ) ;
 # else if ( a -> d ) a -> d = xrealloc ( a -> d , nlimbs * sizeof ( mpi_limb_t ) ) ;
 else a -> d = xmalloc_clear ( nlimbs * sizeof ( mpi_limb_t ) ) ;
 # endif a -> alloced = nlimbs ;
 }

In the above code snippet, check for potential security vulnerabilities and answer with a single digit: 1 if Vulnerable, 0 if Non-vulnerable.

The node information of the code snippet is as follows:

The edge information of the code snippet is as follows:


The following is an example, and it is .


Answer (0 or 1):
~~~~~

## Sample 38 · reveal · B1-H2 · seed 42

ID: `reveal:validation:1324`  
Prompt SHA-256: `4bc0618f7e439299eae5efae7a5a046565f497cf5800e9e44c89b7dc721b2b4c`  
Stratum: `cdg_cluster`

~~~~~text
You are now an excellent programmer. You are conducting a function vulnerability detection task for C/C++ language.

double double_from_string_with_check ( CHARSET_INFO * cs , const char * cptr , const char * end ) {
 int error ;
 char * end_of_num = ( char * ) end ;
 double tmp ;
 tmp = my_strntod ( cs , ( char * ) cptr , end - cptr , & end_of_num , & error ) ;
 if ( error || ( end != end_of_num && ! check_if_only_end_space ( cs , end_of_num , end ) ) ) {
 ErrConvString err ( cptr , end - cptr , cs ) ;
 push_warning_printf ( current_thd , MYSQL_ERROR : : WARN_LEVEL_WARN , ER_TRUNCATED_WRONG_VALUE , ER ( ER_TRUNCATED_WRONG_VALUE ) , "DOUBLE" , err . ptr ( ) ) ;
 }
 return tmp ;
 }

In the above code snippet, check for potential security vulnerabilities and answer with a single digit: 1 if Vulnerable, 0 if Non-vulnerable.

The guarded evidence of the code snippet is as follows:
GUARDED EVIDENCE: operation-specific observed relations; not a safety proof.
N1 RETURN "return tmp ;"
N2 CALL "end - cptr"
N3 CALL "\n        error || ( end != end_of_num && ! check_if_only_end_space ( cs , end_of_num , end ) )\n      "
N4 CALL "end != end_of_num && ! check_if_only_end_space ( cs , end_of_num , end )"
N5 CALL "end != end_of_num"
N6 CALL "check_if_only_end_space ( cs , end_of_num , end )"
N7 CALL "err ( cptr , end - cptr , cs )"
N8 CALL "end - cptr"
N9 IDENTIFIER "tmp"
N3 --CDG--> N7
N3 --CDG--> N8
N3 --CFG--> N9
N4 --CFG--> N3
N5 --CFG--> N4
N5 --CDG--> N6
N9 --CFG--> N1
OP N8
  INPUTS not included/unknown
  DIRECT_CONTROL N3 via=CDG branch=unknown check=cfg_one_branch_witness
  OBSERVED_EXIT N1 from=N3 branch=unknown
OP N6
  INPUTS not included/unknown
  DIRECT_CONTROL N5 via=CDG branch=unknown check=cdg_observed_cfg_unknown
  OBSERVED_EXIT N1 from=N5 branch=unknown
OP N7
  INPUTS not included/unknown
  DIRECT_CONTROL N3 via=CDG branch=unknown check=cfg_one_branch_witness
  OBSERVED_EXIT N1 from=N3 branch=unknown
OP N2
  INPUTS not included/unknown
  DIRECT_CONTROL none observed; not proof of absence
UNKNOWN: guard sufficiency, aliasing and feasible execution paths. Missing polarity is unknown.
BOUNDED: omitted operations/context and shortened snippets are not proof of absence.

The following is an example, and it is .


Answer (0 or 1):
~~~~~

## Sample 39 · reveal · B1-H2 · seed 42

ID: `reveal:validation:1551`  
Prompt SHA-256: `26c5ffdeeaf758d2c45e425c86dae024592bc0bb58222230e955d8589d4b3554`  
Stratum: `no_usable_evidence`

~~~~~text
You are now an excellent programmer. You are conducting a function vulnerability detection task for C/C++ language.

static int dissect_h245_TransparencyParameters ( tvbuff_t * tvb _U_ , int offset _U_ , asn1_ctx_t * actx _U_ , proto_tree * tree _U_ , int hf_index _U_ ) {
 offset = dissect_per_sequence ( tvb , offset , actx , tree , hf_index , ett_h245_TransparencyParameters , TransparencyParameters_sequence ) ;
 return offset ;
 }

In the above code snippet, check for potential security vulnerabilities and answer with a single digit: 1 if Vulnerable, 0 if Non-vulnerable.

The guarded evidence of the code snippet is as follows:
GUARDED EVIDENCE: operation-specific observed relations; not a safety proof.
N1 METHOD_PARAMETER_IN "tvbuff_t * tvb"
N2 METHOD_PARAMETER_IN "int offset"
N3 METHOD_PARAMETER_IN "asn1_ctx_t * actx"
N4 CALL "\n        dissect_per_sequence ( tvb , offset , actx , tree , hf_index , ett_h245_TransparencyParameters , TransparencyParameters_sequence )\n      "
N5 IDENTIFIER "tvb"
N6 IDENTIFIER "offset"
N7 IDENTIFIER "actx"
N8 IDENTIFIER "tree"
N9 IDENTIFIER "hf_index"
N10 IDENTIFIER "<unknown> ett_h245_TransparencyParameters"
N11 IDENTIFIER "<unknown> TransparencyParameters_sequence"
N4 --ARGUMENT--> N5
N4 --ARGUMENT--> N6
N4 --ARGUMENT--> N7
N4 --ARGUMENT--> N8
N4 --ARGUMENT--> N9
N4 --ARGUMENT--> N10
N4 --ARGUMENT--> N11
N5 --REF--> N1
N5 --REACHING_DEF--> N4
N5 --REACHING_DEF--> N6
N5 --REACHING_DEF--> N7
N5 --REACHING_DEF--> N8
N5 --REACHING_DEF--> N9
N5 --REACHING_DEF--> N10
N5 --REACHING_DEF--> N11
N6 --REF--> N2
N6 --REACHING_DEF--> N4
N6 --REACHING_DEF--> N5
N6 --REACHING_DEF--> N7
N6 --REACHING_DEF--> N8
N6 --REACHING_DEF--> N9
N6 --REACHING_DEF--> N10
N6 --REACHING_DEF--> N11
N7 --REF--> N3
N7 --REACHING_DEF--> N4
N7 --REACHING_DEF--> N5
N7 --REACHING_DEF--> N6
N7 --REACHING_DEF--> N8
N7 --REACHING_DEF--> N9
N7 --REACHING_DEF--> N10
N7 --REACHING_DEF--> N11
OP N4
  INPUTS N5,N6,N7,N8,N9,N10,N11
  DIRECT_CONTROL unknown: CDG unavailable
UNKNOWN: guard sufficiency, aliasing and feasible execution paths. Missing polarity is unknown.
BOUNDED: omitted operations/context and shortened snippets are not proof of absence.

The following is an example, and it is .


Answer (0 or 1):
~~~~~

## Sample 40 · reveal · B1-H2 · seed 42

ID: `reveal:validation:1571`  
Prompt SHA-256: `e713306c6868ffa5fe423426e33c1724c4f9c897a1243171f9c7e20bd9baf7f7`  
Stratum: `no_usable_evidence`

~~~~~text
You are now an excellent programmer. You are conducting a function vulnerability detection task for C/C++ language.

static int vvalue_tvb_get0 ( tvbuff_t * tvb _U_ , int offset _U_ , void * val _U_ ) {
 return 0 ;
 }

In the above code snippet, check for potential security vulnerabilities and answer with a single digit: 1 if Vulnerable, 0 if Non-vulnerable.

The guarded evidence of the code snippet is as follows:
NO_USABLE_GUARDED_EVIDENCE: no_operation_nodes. Do not infer safety from missing evidence.

The following is an example, and it is .


Answer (0 or 1):
~~~~~

## Sample 41 · reveal · B1-H2 · seed 42

ID: `reveal:validation:168`  
Prompt SHA-256: `fbe6e821d06e385c2681372ebd122eccb5cc42fa3d29cc6bb620fcbab5a1ae45`  
Stratum: `missing_cpg`

~~~~~text
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
~~~~~

## Sample 42 · reveal · B1-H2 · seed 42

ID: `reveal:validation:175`  
Prompt SHA-256: `ad6f4e221f8ecda3b46f2971b71084c73ff91a7d1d5327e837aa6519e7a7c2cc`  
Stratum: `no_usable_evidence`

~~~~~text
You are now an excellent programmer. You are conducting a function vulnerability detection task for C/C++ language.

int get_ber_length ( tvbuff_t * tvb , int offset , guint32 * length , gboolean * ind ) {
 return try_get_ber_length ( tvb , offset , length , ind , 1 ) ;
 }

In the above code snippet, check for potential security vulnerabilities and answer with a single digit: 1 if Vulnerable, 0 if Non-vulnerable.

The guarded evidence of the code snippet is as follows:
GUARDED EVIDENCE: operation-specific observed relations; not a safety proof.
N1 METHOD_PARAMETER_IN "tvbuff_t * tvb"
N2 METHOD_PARAMETER_IN "int offset"
N3 METHOD_PARAMETER_IN "guint32 * length"
N4 METHOD_PARAMETER_IN "gboolean * ind"
N5 CALL "try_get_ber_length ( tvb , offset , length , ind , 1 )"
N6 IDENTIFIER "tvb"
N7 IDENTIFIER "offset"
N8 IDENTIFIER "length"
N9 IDENTIFIER "ind"
N10 LITERAL "1"
N5 --ARGUMENT--> N6
N5 --ARGUMENT--> N7
N5 --ARGUMENT--> N8
N5 --ARGUMENT--> N9
N5 --ARGUMENT--> N10
N6 --REF--> N1
N6 --REACHING_DEF--> N5
N6 --REACHING_DEF--> N7
N6 --REACHING_DEF--> N8
N6 --REACHING_DEF--> N9
N7 --REF--> N2
N7 --REACHING_DEF--> N5
N7 --REACHING_DEF--> N6
N7 --REACHING_DEF--> N8
N7 --REACHING_DEF--> N9
N8 --REF--> N3
N8 --REACHING_DEF--> N5
N8 --REACHING_DEF--> N6
N8 --REACHING_DEF--> N7
N8 --REACHING_DEF--> N9
N9 --REF--> N4
N9 --REACHING_DEF--> N5
N9 --REACHING_DEF--> N6
N9 --REACHING_DEF--> N7
N9 --REACHING_DEF--> N8
N10 --REACHING_DEF--> N5
N10 --REACHING_DEF--> N6
N10 --REACHING_DEF--> N7
N10 --REACHING_DEF--> N8
N10 --REACHING_DEF--> N9
OP N5
  INPUTS N6,N7,N8,N9,N10
  DIRECT_CONTROL unknown: CDG unavailable
UNKNOWN: guard sufficiency, aliasing and feasible execution paths. Missing polarity is unknown.
BOUNDED: omitted operations/context and shortened snippets are not proof of absence.

The following is an example, and it is .


Answer (0 or 1):
~~~~~

## Sample 43 · reveal · B1-H2 · seed 42

ID: `reveal:validation:1792`  
Prompt SHA-256: `880fabb9282d32cb7603d1ed7bf4cef60b312a22a0db380bf68b9b38c7fe40df`  
Stratum: `missing_cpg`

~~~~~text
You are now an excellent programmer. You are conducting a function vulnerability detection task for C/C++ language.

static ossl_inline void lh_ ## type ## _set_down_load ( LHASH_OF ( type ) * lh , unsigned long dl ) {
 OPENSSL_LH_set_down_load ( ( OPENSSL_LHASH * ) lh , dl ) ;
 }
 static ossl_inline void lh_ ## type ## _doall ( LHASH_OF ( type ) * lh , void ( * doall ) ( type * ) ) {
 OPENSSL_LH_doall ( ( OPENSSL_LHASH * ) lh , ( OPENSSL_LH_DOALL_FUNC ) doall ) ;
 }
 LHASH_OF ( type ) # define IMPLEMENT_LHASH_DOALL_ARG_CONST ( type , argtype ) int_implement_lhash_doall ( type , argtype , const type ) # define IMPLEMENT_LHASH_DOALL_ARG ( type , argtype ) int_implement_lhash_doall ( type , argtype , type ) # define int_implement_lhash_doall ( type , argtype , cbargtype ) static ossl_inline void lh_ ## type ## _doall_ ## argtype ( LHASH_OF ( type ) * lh , void ( * fn ) ( cbargtype * , argtype * ) , argtype * arg ) {
 OPENSSL_LH_doall_arg ( ( OPENSSL_LHASH * ) lh , ( OPENSSL_LH_DOALL_FUNCARG ) fn , ( void * ) arg ) ;
 }
 LHASH_OF ( type ) DEFINE_LHASH_OF ( OPENSSL_STRING ) ;
 # ifdef _MSC_VER # pragma warning ( push ) # pragma warning ( disable : 4090 ) # endif DEFINE_LHASH_OF ( OPENSSL_CSTRING )

In the above code snippet, check for potential security vulnerabilities and answer with a single digit: 1 if Vulnerable, 0 if Non-vulnerable.

The node information of the code snippet is as follows:

The edge information of the code snippet is as follows:


The following is an example, and it is .


Answer (0 or 1):
~~~~~

## Sample 44 · reveal · B1-H2 · seed 42

ID: `reveal:validation:1810`  
Prompt SHA-256: `12b6a13d04aa790a8e1ccb05d7825d4e48d19a5141802c6754a7e2feb4ae8825`  
Stratum: `closed_prefix`

~~~~~text
You are now an excellent programmer. You are conducting a function vulnerability detection task for C/C++ language.

static void deep_count_stop ( NautilusDirectory * directory ) {
 NautilusFile * file ;
 if ( directory -> details -> deep_count_in_progress != NULL ) {
 file = directory -> details -> deep_count_file ;
 if ( file != NULL ) {
 g_assert ( NAUTILUS_IS_FILE ( file ) ) ;
 g_assert ( file -> details -> directory == directory ) ;
 if ( is_needy ( file , lacks_deep_count , REQUEST_DEEP_COUNT ) ) {
 return ;
 }
 }
 deep_count_cancel ( directory ) ;
 }
 }

In the above code snippet, check for potential security vulnerabilities and answer with a single digit: 1 if Vulnerable, 0 if Non-vulnerable.

The guarded evidence of the code snippet is as follows:
GUARDED EVIDENCE: operation-specific observed relations; not a safety proof.
N1 CALL "directory -> details -> deep_count_in_progress != NULL"
N2 CALL "directory -> details -> deep_count_in_progress"
N3 CALL "directory -> details"
N4 CALL "directory -> details -> deep_count_file"
N5 CALL "directory -> details"
N6 CALL "file != NULL"
N7 CALL "file -> details -> directory"
N8 CALL "file -> details"
N9 FIELD_IDENTIFIER "deep_count_in_progress"
N10 FIELD_IDENTIFIER "details"
N11 FIELD_IDENTIFIER "deep_count_file"
N12 IDENTIFIER "directory"
N1 --CDG--> N4
N1 --CDG--> N5
N2 --ARGUMENT--> N3
N2 --REACHING_DEF--> N5
N2 --ARGUMENT--> N9
N4 --ARGUMENT--> N5
N4 --ARGUMENT--> N11
N5 --ARGUMENT--> N10
N5 --ARGUMENT--> N12
N6 --CDG--> N7
N6 --CDG--> N8
OP N4
  INPUTS N5,N11
  DIRECT_CONTROL N1 via=CDG branch=unknown check=cdg_observed_cfg_unknown
  DATA_NOTE: predicates on related data are not operation controls.
OP N5
  INPUTS N10,N12
  DIRECT_CONTROL N1 via=CDG branch=unknown check=cdg_observed_cfg_unknown
  DATA_NOTE: predicates on related data are not operation controls.
OP N7
  INPUTS not included/unknown
  DIRECT_CONTROL N6 via=CDG branch=unknown check=cdg_observed_cfg_unknown
OP N8
  INPUTS not included/unknown
  DIRECT_CONTROL N6 via=CDG branch=unknown check=cdg_observed_cfg_unknown
UNKNOWN: guard sufficiency, aliasing and feasible execution paths. Missing polarity is unknown.
BOUNDED: omitted operations/context and shortened snippets are not proof of absence.

The following is an example, and it is .


Answer (0 or 1):
~~~~~

## Sample 45 · reveal · B1-H2 · seed 42

ID: `reveal:validation:1834`  
Prompt SHA-256: `95bd4b73ae626965610f449ea1d27d954568d68e95a7b456b4dae0cf07cdeec5`  
Stratum: `closed_prefix`

~~~~~text
You are now an excellent programmer. You are conducting a function vulnerability detection task for C/C++ language.

static void imc_get_skip_coeff ( IMCContext * q , IMCChannel * chctx ) {
 int i , j ;
 memset ( chctx -> skipFlagBits , 0 , sizeof ( chctx -> skipFlagBits ) ) ;
 memset ( chctx -> skipFlagCount , 0 , sizeof ( chctx -> skipFlagCount ) ) ;
 for ( i = 0 ;
 i < BANDS ;
 i ++ ) {
 if ( ! chctx -> bandFlagsBuf [ i ] || ! chctx -> bandWidthT [ i ] ) continue ;
 if ( ! chctx -> skipFlagRaw [ i ] ) {
 chctx -> skipFlagBits [ i ] = band_tab [ i + 1 ] - band_tab [ i ] ;
 for ( j = band_tab [ i ] ;
 j < band_tab [ i + 1 ] ;
 j ++ ) {
 chctx -> skipFlags [ j ] = get_bits1 ( & q -> gb ) ;
 if ( chctx -> skipFlags [ j ] ) chctx -> skipFlagCount [ i ] ++ ;
 }
 }
 else {
 for ( j = band_tab [ i ] ;
 j < band_tab [ i + 1 ] - 1 ;
 j += 2 ) {
 if ( ! get_bits1 ( & q -> gb ) ) {
 chctx -> skipFlagBits [ i ] ++ ;
 chctx -> skipFlags [ j ] = 1 ;
 chctx -> skipFlags [ j + 1 ] = 1 ;
 chctx -> skipFlagCount [ i ] += 2 ;
 }
 else {
 if ( get_bits1 ( & q -> gb ) ) {
 chctx -> skipFlagBits [ i ] += 2 ;
 chctx -> skipFlags [ j ] = 0 ;
 chctx -> skipFlags [ j + 1 ] = 1 ;
 chctx -> skipFlagCount [ i ] ++ ;
 }
 else {
 chctx -> skipFlagBits [ i ] += 3 ;
 chctx -> skipFlags [ j + 1 ] = 0 ;
 if ( ! get_bits1 ( & q -> gb ) ) {
 chctx -> skipFlags [ j ] = 1 ;
 chctx -> skipFlagCount [ i ] ++ ;
 }
 else {
 chctx -> skipFlags [ j ] = 0 ;
 }
 }
 }
 }
 if ( j < band_tab [ i + 1 ] ) {
 chctx -> skipFlagBits [ i ] ++ ;
 if ( ( chctx -> skipFlags [ j ] = get_bits1 ( & q -> gb ) ) ) chctx -> skipFlagCount [ i ] ++ ;
 }
 }
 }
 }

In the above code snippet, check for potential security vulnerabilities and answer with a single digit: 1 if Vulnerable, 0 if Non-vulnerable.

The guarded evidence of the code snippet is as follows:
GUARDED EVIDENCE: operation-specific observed relations; not a safety proof.
N1 CALL "i < BANDS"
N2 CALL "! chctx -> bandFlagsBuf [ i ]"
N3 CALL "chctx -> bandFlagsBuf [ i ]"
N4 CALL "chctx -> bandFlagsBuf"
N5 CALL "chctx -> bandWidthT [ i ]"
N6 CALL "chctx -> bandWidthT"
N1 --CDG--> N3
N1 --CDG--> N4
N2 --CDG--> N5
N2 --CDG--> N6
N3 --ARGUMENT--> N4
N3 --REACHING_DEF--> N4
N5 --ARGUMENT--> N6
N5 --REACHING_DEF--> N6
OP N3
  INPUTS N4
  DIRECT_CONTROL N1 via=CDG branch=unknown check=cdg_observed_cfg_unknown
  DATA_NOTE: predicates on related data are not operation controls.
OP N4
  INPUTS not included/unknown
  DIRECT_CONTROL N1 via=CDG branch=unknown check=cdg_observed_cfg_unknown
  DATA_NOTE: predicates on related data are not operation controls.
OP N5
  INPUTS N6
  DIRECT_CONTROL N2 via=CDG branch=unknown check=cdg_observed_cfg_unknown
  DATA_NOTE: predicates on related data are not operation controls.
OP N6
  INPUTS not included/unknown
  DIRECT_CONTROL N2 via=CDG branch=unknown check=cdg_observed_cfg_unknown
  DATA_NOTE: predicates on related data are not operation controls.
UNKNOWN: guard sufficiency, aliasing and feasible execution paths. Missing polarity is unknown.
BOUNDED: omitted operations/context and shortened snippets are not proof of absence.

The following is an example, and it is .


Answer (0 or 1):
~~~~~

## Sample 46 · reveal · B1-H2 · seed 42

ID: `reveal:validation:1839`  
Prompt SHA-256: `f2e08e37515443b8b81f8fb981935d885d3bd3f982bf1249d0f0e55c934148d3`  
Stratum: `closed_prefix`

~~~~~text
You are now an excellent programmer. You are conducting a function vulnerability detection task for C/C++ language.

static int aes_ccm_ctrl ( EVP_CIPHER_CTX * c , int type , int arg , void * ptr ) {
 EVP_AES_CCM_CTX * cctx = EVP_C_DATA ( EVP_AES_CCM_CTX , c ) ;
 switch ( type ) {
 case EVP_CTRL_INIT : cctx -> key_set = 0 ;
 cctx -> iv_set = 0 ;
 cctx -> L = 8 ;
 cctx -> M = 12 ;
 cctx -> tag_set = 0 ;
 cctx -> len_set = 0 ;
 cctx -> tls_aad_len = - 1 ;
 return 1 ;
 case EVP_CTRL_AEAD_TLS1_AAD : if ( arg != EVP_AEAD_TLS1_AAD_LEN ) return 0 ;
 memcpy ( EVP_CIPHER_CTX_buf_noconst ( c ) , ptr , arg ) ;
 cctx -> tls_aad_len = arg ;
 {
 uint16_t len = EVP_CIPHER_CTX_buf_noconst ( c ) [ arg - 2 ] << 8 | EVP_CIPHER_CTX_buf_noconst ( c ) [ arg - 1 ] ;
 if ( len < EVP_CCM_TLS_EXPLICIT_IV_LEN ) return 0 ;
 len -= EVP_CCM_TLS_EXPLICIT_IV_LEN ;
 if ( ! EVP_CIPHER_CTX_encrypting ( c ) ) {
 if ( len < cctx -> M ) return 0 ;
 len -= cctx -> M ;
 }
 EVP_CIPHER_CTX_buf_noconst ( c ) [ arg - 2 ] = len >> 8 ;
 EVP_CIPHER_CTX_buf_noconst ( c ) [ arg - 1 ] = len & 0xff ;
 }
 return cctx -> M ;
 case EVP_CTRL_CCM_SET_IV_FIXED : if ( arg != EVP_CCM_TLS_FIXED_IV_LEN ) return 0 ;
 memcpy ( EVP_CIPHER_CTX_iv_noconst ( c ) , ptr , arg ) ;
 return 1 ;
 case EVP_CTRL_AEAD_SET_IVLEN : arg = 15 - arg ;
 case EVP_CTRL_CCM_SET_L : if ( arg < 2 || arg > 8 ) return 0 ;
 cctx -> L = arg ;
 return 1 ;
 case EVP_CTRL_AEAD_SET_TAG : if ( ( arg & 1 ) || arg < 4 || arg > 16 ) return 0 ;
 if ( EVP_CIPHER_CTX_encrypting ( c ) && ptr ) return 0 ;
 if ( ptr ) {
 cctx -> tag_set = 1 ;
 memcpy ( EVP_CIPHER_CTX_buf_noconst ( c ) , ptr , arg ) ;
 }
 cctx -> M = arg ;
 return 1 ;
 case EVP_CTRL_AEAD_GET_TAG : if ( ! EVP_CIPHER_CTX_encrypting ( c ) || ! cctx -> tag_set ) return 0 ;
 if ( ! CRYPTO_ccm128_tag ( & cctx -> ccm , ptr , ( size_t ) arg ) ) return 0 ;
 cctx -> tag_set = 0 ;
 cctx -> iv_set = 0 ;
 cctx -> len_set = 0 ;
 return 1 ;
 case EVP_CTRL_COPY : {
 EVP_CIPHER_CTX * out = ptr ;
 EVP_AES_CCM_CTX * cctx_out = EVP_C_DATA ( EVP_AES_CCM_CTX , out ) ;
 if ( cctx -> ccm . key ) {
 if ( cctx -> ccm . key != & cctx -> ks ) return 0 ;
 cctx_out -> ccm . key = & cctx_out -> ks ;
 }
 return 1 ;
 }
 default : return - 1 ;
 }
 }

In the above code snippet, check for potential security vulnerabilities and answer with a single digit: 1 if Vulnerable, 0 if Non-vulnerable.

The guarded evidence of the code snippet is as follows:
GUARDED EVIDENCE: operation-specific observed relations; not a safety proof.
N1 CALL "cctx -> key_set"
N2 CALL "arg != EVP_AEAD_TLS1_AAD_LEN"
N3 CALL "memcpy ( EVP_CIPHER_CTX_buf_noconst ( c ) , ptr , arg )"
N4 CALL "EVP_CIPHER_CTX_buf_noconst ( c )"
N5 CALL "cctx -> tls_aad_len"
N2 --CDG--> N3
N2 --CDG--> N4
N2 --CDG--> N5
N3 --ARGUMENT--> N4
N4 --REACHING_DEF--> N3
OP N3
  INPUTS N4
  DIRECT_CONTROL N2 via=CDG branch=unknown check=cdg_observed_cfg_unknown
  DATA_NOTE: predicates on related data are not operation controls.
OP N5
  INPUTS not included/unknown
  DIRECT_CONTROL N2 via=CDG branch=unknown check=cdg_observed_cfg_unknown
OP N4
  INPUTS not included/unknown
  DIRECT_CONTROL N2 via=CDG branch=unknown check=cdg_observed_cfg_unknown
OP N1
  INPUTS not included/unknown
  DIRECT_CONTROL none observed; not proof of absence
UNKNOWN: guard sufficiency, aliasing and feasible execution paths. Missing polarity is unknown.
BOUNDED: omitted operations/context and shortened snippets are not proof of absence.

The following is an example, and it is .


Answer (0 or 1):
~~~~~

## Sample 47 · reveal · B1-H2 · seed 42

ID: `reveal:validation:1923`  
Prompt SHA-256: `bbcecba9fe86b0081ee363fb56df8a136c4cd1eeeb0736872c91956ca843bf33`  
Stratum: `no_usable_evidence`

~~~~~text
You are now an excellent programmer. You are conducting a function vulnerability detection task for C/C++ language.

void proto_reg_handoff_opcua ( void ) {
 opcua_handle = create_dissector_handle ( dissect_opcua , proto_opcua ) ;
 dissector_add_uint_range_with_preference ( "tcp.port" , OPCUA_PORT_RANGE , opcua_handle ) ;
 }

In the above code snippet, check for potential security vulnerabilities and answer with a single digit: 1 if Vulnerable, 0 if Non-vulnerable.

The guarded evidence of the code snippet is as follows:
GUARDED EVIDENCE: operation-specific observed relations; not a safety proof.
N1 CALL "create_dissector_handle ( dissect_opcua , proto_opcua )"
N2 CALL "\n        dissector_add_uint_range_with_preference ( \"tcp.port\" , OPCUA_PORT_RANGE , opcua_handle )\n      "
N3 IDENTIFIER "<unknown> opcua_handle"
N4 IDENTIFIER "<unknown> dissect_opcua"
N5 IDENTIFIER "<unknown> proto_opcua"
N6 IDENTIFIER "<unknown> OPCUA_PORT_RANGE"
N7 IDENTIFIER "<unknown> opcua_handle"
N8 LITERAL "\"tcp.port\""
N9 LOCAL "<unknown> opcua_handle"
N10 LOCAL "<unknown> OPCUA_PORT_RANGE"
N11 LOCAL "<unknown> proto_opcua"
N12 LOCAL "<unknown> dissect_opcua"
N1 --ARGUMENT--> N4
N1 --ARGUMENT--> N5
N2 --ARGUMENT--> N6
N2 --ARGUMENT--> N7
N2 --ARGUMENT--> N8
N3 --REACHING_DEF--> N7
N4 --REACHING_DEF--> N1
N4 --REACHING_DEF--> N5
N4 --REF--> N12
N5 --REACHING_DEF--> N1
N5 --REACHING_DEF--> N4
N5 --REF--> N11
N6 --REACHING_DEF--> N2
N6 --REACHING_DEF--> N7
N6 --REF--> N10
N7 --REACHING_DEF--> N2
N7 --REACHING_DEF--> N6
N7 --REF--> N9
N8 --REACHING_DEF--> N2
N8 --REACHING_DEF--> N6
N8 --REACHING_DEF--> N7
OP N1
  INPUTS N4,N5
  DIRECT_CONTROL unknown: CDG unavailable
OP N2
  INPUTS N6,N7,N8
  DIRECT_CONTROL unknown: CDG unavailable
UNKNOWN: guard sufficiency, aliasing and feasible execution paths. Missing polarity is unknown.
BOUNDED: omitted operations/context and shortened snippets are not proof of absence.

The following is an example, and it is .


Answer (0 or 1):
~~~~~

## Sample 48 · reveal · B1-H2 · seed 42

ID: `reveal:validation:1977`  
Prompt SHA-256: `488e81fdad5a1840c89dbf59e592af0f40d3173d81577a3542bdbc2a2150d124`  
Stratum: `cdg_cluster`

~~~~~text
You are now an excellent programmer. You are conducting a function vulnerability detection task for C/C++ language.

static int transform_hook_handler ( TSCont contp , TSEvent event , void * edata ) {
 TSHttpTxn txnp = nullptr ;
 TransformTestData * data = nullptr ;
 CHECK_SPURIOUS_EVENT ( contp , event , edata ) ;
 data = ( TransformTestData * ) TSContDataGet ( contp ) ;
 switch ( event ) {
 case TS_EVENT_HTTP_READ_REQUEST_HDR : txnp = ( TSHttpTxn ) edata ;
 TSSkipRemappingSet ( txnp , 1 ) ;
 TSHttpTxnReenable ( txnp , TS_EVENT_HTTP_CONTINUE ) ;
 break ;
 case TS_EVENT_HTTP_READ_RESPONSE_HDR : txnp = ( TSHttpTxn ) edata ;
 if ( transformable ( txnp , data ) ) {
 transform_add ( txnp , data ) ;
 }
 {
 TSMBuffer bufp ;
 TSMLoc hdr ;
 TSMLoc field ;
 if ( TSHttpTxnClientReqGet ( txnp , & bufp , & hdr ) != TS_SUCCESS ) {
 SDK_RPRINT ( data -> test , "TSHttpTxnTransform" , "TestCase" , TC_FAIL , "TSHttpTxnClientReqGet returns 0" ) ;
 }
 else {
 if ( TS_NULL_MLOC == ( field = TSMimeHdrFieldFind ( bufp , hdr , "Request" , - 1 ) ) ) {
 SDK_RPRINT ( data -> test , "TSHttpTxnTransform" , "TestCase" , TC_FAIL , "Didn't find field request" ) ;
 }
 else {
 int reqid = TSMimeHdrFieldValueIntGet ( bufp , hdr , field , 0 ) ;
 if ( reqid == 1 ) {
 TSHttpTxnTransformedRespCache ( txnp , 0 ) ;
 TSHttpTxnUntransformedRespCache ( txnp , 1 ) ;
 }
 if ( reqid == 2 ) {
 TSHttpTxnTransformedRespCache ( txnp , 1 ) ;
 TSHttpTxnUntransformedRespCache ( txnp , 0 ) ;
 }
 if ( TSHandleMLocRelease ( bufp , hdr , field ) != TS_SUCCESS ) {
 SDK_RPRINT ( data -> test , "TSHttpTxnTransform" , "TestCase" , TC_FAIL , "Unable to release handle to field in Client request" ) ;
 }
 }
 if ( TSHandleMLocRelease ( bufp , TS_NULL_MLOC , hdr ) != TS_SUCCESS ) {
 SDK_RPRINT ( data -> test , "TSHttpTxnTransform" , "TestCase" , TC_FAIL , "Unable to release handle to Client request" ) ;
 }
 }
 }
 TSHttpTxnHookAdd ( txnp , TS_HTTP_SEND_RESPONSE_HDR_HOOK , contp ) ;
 TSHttpTxnReenable ( txnp , TS_EVENT_HTTP_CONTINUE ) ;
 break ;
 case TS_EVENT_HTTP_SEND_RESPONSE_HDR : {
 TSMBuffer bufp ;
 TSMLoc hdr ;
 txnp = ( TSHttpTxn ) edata ;
 if ( TSHttpTxnTransformRespGet ( txnp , & bufp , & hdr ) != TS_SUCCESS ) {
 SDK_RPRINT ( data -> test , "TSHttpTxnTransformRespGet" , "TestCase" , TC_FAIL , "TSHttpTxnTransformRespGet returns 0" ) ;
 data -> test_passed_txn_transform_resp_get = false ;
 }
 else {
 if ( ( bufp == reinterpret_cast < TSMBuffer > ( & ( ( ( HttpSM * ) txnp ) -> t_state . hdr_info . transform_response ) ) ) && ( hdr == reinterpret_cast < TSMLoc > ( ( & ( ( ( HttpSM * ) txnp ) -> t_state . hdr_info . transform_response ) ) -> m_http ) ) ) {
 SDK_RPRINT ( data -> test , "TSHttpTxnTransformRespGet" , "TestCase" , TC_PASS , "ok" ) ;
 }
 else {
 SDK_RPRINT ( data -> test , "TSHttpTxnTransformRespGet" , "TestCase" , TC_FAIL , "Value's Mismatch" ) ;
 data -> test_passed_txn_transform_resp_get = false ;
 }
 if ( TSHandleMLocRelease ( bufp , TS_NULL_MLOC , hdr ) != TS_SUCCESS ) {
 SDK_RPRINT ( data -> test , "TSHttpTxnTransformRespGet" , "TestCase" , TC_FAIL , "Unable to release handle to Transform header handle" ) ;
 }
 }
 }
 TSHttpTxnReenable ( txnp , TS_EVENT_HTTP_CONTINUE ) ;
 break ;
 case TS_EVENT_IMMEDIATE : case TS_EVENT_TIMEOUT : switch ( data -> req_no ) {
 case 1 : if ( data -> browser1 -> status == REQUEST_INPROGRESS ) {
 TSContSchedule ( contp , 25 , TS_THREAD_POOL_DEFAULT ) ;
 return 0 ;
 }
 data -> req_no ++ ;
 Debug ( UTDBG_TAG "_transform" , "Running Browser 2" ) ;
 synclient_txn_send_request ( data -> browser2 , data -> request2 ) ;
 TSContSchedule ( contp , 25 , TS_THREAD_POOL_DEFAULT ) ;
 return 0 ;
 case 2 : if ( data -> browser2 -> status == REQUEST_INPROGRESS ) {
 TSContSchedule ( contp , 25 , TS_THREAD_POOL_DEFAULT ) ;
 return 0 ;
 }
 data -> req_no ++ ;
 Debug ( UTDBG_TAG "_transform" , "Running Browser 3" ) ;
 synclient_txn_send_request ( data -> browser3 , data -> request1 ) ;
 TSContSchedule ( contp , 25 , TS_THREAD_POOL_DEFAULT ) ;
 return 0 ;
 case 3 : if ( data -> browser3 -> status == REQUEST_INPROGRESS ) {
 TSContSchedule ( contp , 25 , TS_THREAD_POOL_DEFAULT ) ;
 return 0 ;
 }
 data -> req_no ++ ;
 Debug ( UTDBG_TAG "_transform" , "Running Browser 4" ) ;
 synclient_txn_send_request ( data -> browser4 , data -> request2 ) ;
 TSContSchedule ( contp , 25 , TS_THREAD_POOL_DEFAULT ) ;
 return 0 ;
 case 4 : if ( data -> browser4 -> status == REQUEST_INPROGRESS ) {
 TSContSchedule ( contp , 25 , TS_THREAD_POOL_DEFAULT ) ;
 return 0 ;
 }
 synserver_delete ( data -> os ) ;
 data -> os = nullptr ;
 data -> req_no ++ ;
 TSfree ( data -> request1 ) ;
 TSfree ( data -> request2 ) ;
 break ;
 default : SDK_RPRINT ( data -> test , "TSHttpTxnTransform" , "TestCase" , TC_FAIL , "Something terribly wrong with the test" ) ;
 exit ( 0 ) ;
 }
 {
 if ( ( strstr ( data -> browser1 -> response , TRANSFORM_APPEND_STRING ) != nullptr ) && ( strstr ( data -> browser3 -> response , TRANSFORM_APPEND_STRING ) == nullptr ) ) {
 SDK_RPRINT ( data -> test , "TSHttpTxnUntransformedResponseCache" , "TestCase1" , TC_PASS , "ok" ) ;
 data -> test_passed_txn_untransformed_resp_cache = true ;
 }
 else {
 SDK_RPRINT ( data -> test , "TSHttpTxnUntransformedResponseCache" , "TestCase1" , TC_FAIL , "Value's Mismatch" ) ;
 }
 if ( ( strstr ( data -> browser2 -> response , TRANSFORM_APPEND_STRING ) != nullptr ) && ( strstr ( data -> browser4 -> response , TRANSFORM_APPEND_STRING ) != nullptr ) ) {
 SDK_RPRINT ( data -> test , "TSHttpTxnTransformedResponseCache" , "TestCase1" , TC_PASS , "ok" ) ;
 data -> test_passed_txn_transformed_resp_cache = true ;
 }
 else {
 SDK_RPRINT ( data -> test , "TSHttpTxnTransformedResponseCache" , "TestCase1" , TC_FAIL , "Value's Mismatch" ) ;
 }
 * ( data -> pstatus ) = REGRESSION_TEST_PASSED ;
 if ( data -> browser1 -> status != REQUEST_SUCCESS ) {
 SDK_RPRINT ( data -> test , "TSTransformCreate" , "TestCase1" , TC_FAIL , "Browser 1 status was not REQUEST_SUCCESS" ) ;
 * ( data -> pstatus ) = REGRESSION_TEST_FAILED ;
 }
 if ( data -> browser2 -> status != REQUEST_SUCCESS ) {
 SDK_RPRINT ( data -> test , "TSTransformCreate" , "TestCase1" , TC_FAIL , "Browser 2 status was not REQUEST_SUCCESS" ) ;
 * ( data -> pstatus ) = REGRESSION_TEST_FAILED ;
 }
 if ( data -> browser3 -> status != REQUEST_SUCCESS ) {
 SDK_RPRINT ( data -> test , "TSTransformCreate" , "TestCase1" , TC_FAIL , "Browser 3 status was not REQUEST_SUCCESS" ) ;
 * ( data -> pstatus ) = REGRESSION_TEST_FAILED ;
 }
 if ( data -> browser4 -> status != REQUEST_SUCCESS ) {
 SDK_RPRINT ( data -> test , "TSTransformCreate" , "TestCase1" , TC_FAIL , "Browser 4 status was not REQUEST_SUCCESS" ) ;
 * ( data -> pstatus ) = REGRESSION_TEST_FAILED ;
 }
 if ( data -> test_passed_txn_transform_resp_get != true ) {
 SDK_RPRINT ( data -> test , "TSTransformCreate" , "TestCase1" , TC_FAIL , "did not pass transform_resp_get" ) ;
 * ( data -> pstatus ) = REGRESSION_TEST_FAILED ;
 }
 if ( data -> test_passed_txn_transformed_resp_cache != true ) {
 SDK_RPRINT ( data -> test , "TSTransformCreate" , "TestCase1" , TC_FAIL , "did not pass transformed_resp_cache" ) ;
 * ( data -> pstatus ) = REGRESSION_TEST_FAILED ;
 }
 if ( data -> test_passed_txn_untransformed_resp_cache != true ) {
 SDK_RPRINT ( data -> test , "TSTransformCreate" , "TestCase1" , TC_FAIL , "did not pass untransformed_resp_cache" ) ;
 * ( data -> pstatus ) = REGRESSION_TEST_FAILED ;
 }
 if ( data -> test_passed_transform_create != true ) {
 SDK_RPRINT ( data -> test , "TSTransformCreate" , "TestCase1" , TC_FAIL , "did not pass transform_create" ) ;
 * ( data -> pstatus ) = REGRESSION_TEST_FAILED ;
 }
 synclient_txn_delete ( data -> browser1 ) ;
 synclient_txn_delete ( data -> browser2 ) ;
 synclient_txn_delete ( data -> browser3 ) ;
 synclient_txn_delete ( data -> browser4 ) ;
 TSContDataSet ( contp , nullptr ) ;
 data -> magic = MAGIC_DEAD ;
 TSfree ( data ) ;
 }
 break ;
 default : * ( data -> pstatus ) = REGRESSION_TEST_FAILED ;
 SDK_RPRINT ( data -> test , "TSHttpTxnTransform" , "TestCase1" , TC_FAIL , "Unexpected event %d" , event ) ;
 break ;
 }
 return 0 ;
 }

In the above code snippet, check for potential security vulnerabilities and answer with a single digit: 1 if Vulnerable, 0 if Non-vulnerable.

The guarded evidence of the code snippet is as follows:
GUARDED EVIDENCE: operation-specific observed relations; not a safety proof.
N1 CALL "TSHttpTxnClientReqGet ( txnp , & bufp , & hdr ) != TS_SUCCESS"
N2 CALL "data -> test"
N3 CALL "\n        TS_NULL_MLOC == ( field = TSMimeHdrFieldFind ( bufp , hdr , \"Request\" , - 1 ) )\n      "
N4 CALL "data -> test"
N5 CALL "TSHandleMLocRelease ( bufp , hdr , field ) != TS_SUCCESS"
N6 CALL "data -> test"
N7 CALL "TSHandleMLocRelease ( bufp , TS_NULL_MLOC , hdr ) != TS_SUCCESS"
N8 CALL "data -> test"
N9 FIELD_IDENTIFIER "test"
N10 IDENTIFIER "data"
N1 --CDG--> N2
N2 --ARGUMENT--> N9
N2 --ARGUMENT--> N10
N3 --CDG--> N4
N5 --CDG--> N6
N7 --CDG--> N8
OP N2
  INPUTS N9,N10
  DIRECT_CONTROL N1 via=CDG branch=unknown check=cdg_observed_cfg_unknown
  DATA_NOTE: predicates on related data are not operation controls.
OP N4
  INPUTS not included/unknown
  DIRECT_CONTROL N3 via=CDG branch=unknown check=cdg_observed_cfg_unknown
OP N6
  INPUTS not included/unknown
  DIRECT_CONTROL N5 via=CDG branch=unknown check=cdg_observed_cfg_unknown
OP N8
  INPUTS not included/unknown
  DIRECT_CONTROL N7 via=CDG branch=unknown check=cdg_observed_cfg_unknown
UNKNOWN: guard sufficiency, aliasing and feasible execution paths. Missing polarity is unknown.
BOUNDED: omitted operations/context and shortened snippets are not proof of absence.

The following is an example, and it is .


Answer (0 or 1):
~~~~~

## Sample 49 · reveal · B1-H2 · seed 42

ID: `reveal:validation:216`  
Prompt SHA-256: `80a8fc859dab7cbb12110fb3997cdbdbab99cda2c7bcbbdcb214508172abb00c`  
Stratum: `closed_prefix`

~~~~~text
You are now an excellent programmer. You are conducting a function vulnerability detection task for C/C++ language.

bool get_func_retset ( Oid funcid ) {
 HeapTuple tp ;
 bool result ;
 tp = SearchSysCache1 ( PROCOID , ObjectIdGetDatum ( funcid ) ) ;
 if ( ! HeapTupleIsValid ( tp ) ) elog ( ERROR , "cache lookup failed for function %u" , funcid ) ;
 result = ( ( Form_pg_proc ) GETSTRUCT ( tp ) ) -> proretset ;
 ReleaseSysCache ( tp ) ;
 return result ;
 }

In the above code snippet, check for potential security vulnerabilities and answer with a single digit: 1 if Vulnerable, 0 if Non-vulnerable.

The guarded evidence of the code snippet is as follows:
GUARDED EVIDENCE: operation-specific observed relations; not a safety proof.
N1 CALL "SearchSysCache1 ( PROCOID , ObjectIdGetDatum ( funcid ) )"
N2 CALL "ObjectIdGetDatum ( funcid )"
N3 CALL "! HeapTupleIsValid ( tp )"
N4 CALL "elog ( ERROR , \"cache lookup failed for function %u\" , funcid )"
N5 CALL "( ( Form_pg_proc ) GETSTRUCT ( tp ) ) -> proretset"
N6 CALL "( Form_pg_proc ) GETSTRUCT ( tp )"
N7 FIELD_IDENTIFIER "proretset"
N8 IDENTIFIER "<unknown> PROCOID"
N9 IDENTIFIER "funcid"
N10 IDENTIFIER "<unknown> ERROR"
N11 IDENTIFIER "funcid"
N12 LITERAL "\"cache lookup failed for function %u\""
N1 --ARGUMENT--> N2
N1 --ARGUMENT--> N8
N2 --REACHING_DEF--> N1
N2 --REACHING_DEF--> N8
N2 --ARGUMENT--> N9
N3 --CDG--> N4
N4 --ARGUMENT--> N10
N4 --ARGUMENT--> N11
N4 --ARGUMENT--> N12
N5 --ARGUMENT--> N6
N5 --ARGUMENT--> N7
OP N4
  INPUTS N10,N11,N12
  DIRECT_CONTROL N3 via=CDG branch=unknown check=cdg_observed_cfg_unknown
  DATA_NOTE: predicates on related data are not operation controls.
OP N5
  INPUTS N6,N7
  DIRECT_CONTROL none observed; not proof of absence
OP N1
  INPUTS N2,N8
  DIRECT_CONTROL none observed; not proof of absence
OP N2
  INPUTS N9
  DIRECT_CONTROL none observed; not proof of absence
UNKNOWN: guard sufficiency, aliasing and feasible execution paths. Missing polarity is unknown.
BOUNDED: omitted operations/context and shortened snippets are not proof of absence.

The following is an example, and it is .


Answer (0 or 1):
~~~~~

## Sample 50 · reveal · B1-H2 · seed 42

ID: `reveal:validation:389`  
Prompt SHA-256: `27646154e30ebfb73e11e320fafeb05edb25bcaead658e8901e842c56e347965`  
Stratum: `missing_cpg`

~~~~~text
You are now an excellent programmer. You are conducting a function vulnerability detection task for C/C++ language.

static VALUE ossl_asn1_ ## klass ( int argc , VALUE * argv , VALUE self ) \ {
 return rb_funcall3 ( cASN1 ## klass , rb_intern ( "new" ) , argc , argv ) ;
 }
 OSSL_ASN1_IMPL_FACTORY_METHOD ( Boolean ) OSSL_ASN1_IMPL_FACTORY_METHOD ( Integer ) OSSL_ASN1_IMPL_FACTORY_METHOD ( Enumerated ) OSSL_ASN1_IMPL_FACTORY_METHOD ( BitString ) OSSL_ASN1_IMPL_FACTORY_METHOD ( OctetString ) OSSL_ASN1_IMPL_FACTORY_METHOD ( UTF8String ) OSSL_ASN1_IMPL_FACTORY_METHOD ( NumericString ) OSSL_ASN1_IMPL_FACTORY_METHOD ( PrintableString ) OSSL_ASN1_IMPL_FACTORY_METHOD ( T61String ) OSSL_ASN1_IMPL_FACTORY_METHOD ( VideotexString ) OSSL_ASN1_IMPL_FACTORY_METHOD ( IA5String ) OSSL_ASN1_IMPL_FACTORY_METHOD ( GraphicString ) OSSL_ASN1_IMPL_FACTORY_METHOD ( ISO64String ) OSSL_ASN1_IMPL_FACTORY_METHOD ( GeneralString ) OSSL_ASN1_IMPL_FACTORY_METHOD ( UniversalString )

In the above code snippet, check for potential security vulnerabilities and answer with a single digit: 1 if Vulnerable, 0 if Non-vulnerable.

The node information of the code snippet is as follows:

The edge information of the code snippet is as follows:


The following is an example, and it is .


Answer (0 or 1):
~~~~~

## Sample 51 · reveal · B1-H2 · seed 42

ID: `reveal:validation:394`  
Prompt SHA-256: `b93768b2319d16dfe68c109f7414bec20f2d73fc76bcb21ee41d995143bdf512`  
Stratum: `closed_prefix`

~~~~~text
You are now an excellent programmer. You are conducting a function vulnerability detection task for C/C++ language.

static void ac3_upmix_delay ( AC3DecodeContext * s ) {
 int channel_data_size = sizeof ( s -> delay [ 0 ] ) ;
 switch ( s -> channel_mode ) {
 case AC3_CHMODE_DUALMONO : case AC3_CHMODE_STEREO : memcpy ( s -> delay [ 1 ] , s -> delay [ 0 ] , channel_data_size ) ;
 break ;
 case AC3_CHMODE_2F2R : memset ( s -> delay [ 3 ] , 0 , channel_data_size ) ;
 case AC3_CHMODE_2F1R : memset ( s -> delay [ 2 ] , 0 , channel_data_size ) ;
 break ;
 case AC3_CHMODE_3F2R : memset ( s -> delay [ 4 ] , 0 , channel_data_size ) ;
 case AC3_CHMODE_3F1R : memset ( s -> delay [ 3 ] , 0 , channel_data_size ) ;
 case AC3_CHMODE_3F : memcpy ( s -> delay [ 2 ] , s -> delay [ 1 ] , channel_data_size ) ;
 memset ( s -> delay [ 1 ] , 0 , channel_data_size ) ;
 break ;
 }
 }

In the above code snippet, check for potential security vulnerabilities and answer with a single digit: 1 if Vulnerable, 0 if Non-vulnerable.

The guarded evidence of the code snippet is as follows:
GUARDED EVIDENCE: operation-specific observed relations; not a safety proof.
N1 CALL "s -> channel_mode"
N2 CALL "memcpy ( s -> delay [ 1 ] , s -> delay [ 0 ] , channel_data_size )"
N3 CALL "s -> delay [ 1 ]"
N4 CALL "s -> delay"
N5 CALL "s -> delay [ 0 ]"
N6 CALL "s -> delay"
N7 CALL "memcpy ( s -> delay [ 2 ] , s -> delay [ 1 ] , channel_data_size )"
N8 FIELD_IDENTIFIER "delay"
N1 --CDG--> N2
N1 --CDG--> N3
N1 --CDG--> N4
N1 --CDG--> N7
N2 --ARGUMENT--> N3
N2 --ARGUMENT--> N5
N3 --REACHING_DEF--> N2
N3 --ARGUMENT--> N4
N3 --REACHING_DEF--> N5
N4 --ARGUMENT--> N8
N5 --REACHING_DEF--> N2
N5 --REACHING_DEF--> N3
N5 --ARGUMENT--> N6
OP N2
  INPUTS N3,N5
  DIRECT_CONTROL N1 via=CDG branch=unknown check=cdg_observed_cfg_unknown
  DATA_NOTE: predicates on related data are not operation controls.
OP N7
  INPUTS not included/unknown
  DIRECT_CONTROL N1 via=CDG branch=unknown check=cdg_observed_cfg_unknown
OP N3
  INPUTS N4
  DIRECT_CONTROL N1 via=CDG branch=unknown check=cdg_observed_cfg_unknown
  DATA_NOTE: predicates on related data are not operation controls.
OP N4
  INPUTS N8
  DIRECT_CONTROL N1 via=CDG branch=unknown check=cdg_observed_cfg_unknown
  DATA_NOTE: predicates on related data are not operation controls.
UNKNOWN: guard sufficiency, aliasing and feasible execution paths. Missing polarity is unknown.
BOUNDED: omitted operations/context and shortened snippets are not proof of absence.

The following is an example, and it is .


Answer (0 or 1):
~~~~~

## Sample 52 · reveal · B1-H2 · seed 42

ID: `reveal:validation:441`  
Prompt SHA-256: `262e4e8244fdf98673bc31d601db9b69b7c9533caec7fe10fb4ac0635a7d9e8f`  
Stratum: `cdg_cluster`

~~~~~text
You are now an excellent programmer. You are conducting a function vulnerability detection task for C/C++ language.

static void define_gf_group ( VP9_COMP * cpi , FIRSTPASS_STATS * this_frame ) {
 RATE_CONTROL * const rc = & cpi -> rc ;
 const VP9EncoderConfig * const oxcf = & cpi -> oxcf ;
 TWO_PASS * const twopass = & cpi -> twopass ;
 FIRSTPASS_STATS next_frame ;
 const FIRSTPASS_STATS * const start_pos = twopass -> stats_in ;
 int i ;
 double boost_score = 0.0 ;
 double old_boost_score = 0.0 ;
 double gf_group_err = 0.0 ;
 double gf_first_frame_err = 0.0 ;
 double mod_frame_err = 0.0 ;
 double mv_ratio_accumulator = 0.0 ;
 double decay_accumulator = 1.0 ;
 double zero_motion_accumulator = 1.0 ;
 double loop_decay_rate = 1.00 ;
 double last_loop_decay_rate = 1.00 ;
 double this_frame_mv_in_out = 0.0 ;
 double mv_in_out_accumulator = 0.0 ;
 double abs_mv_in_out_accumulator = 0.0 ;
 double mv_ratio_accumulator_thresh ;
 unsigned int allow_alt_ref = is_altref_enabled ( cpi ) ;
 int f_boost = 0 ;
 int b_boost = 0 ;
 int flash_detected ;
 int active_max_gf_interval ;
 int64_t gf_group_bits ;
 double gf_group_error_left ;
 int gf_arf_bits ;
 if ( cpi -> common . frame_type != KEY_FRAME ) {
 vp9_zero ( twopass -> gf_group ) ;
 }
 vp9_clear_system_state ( ) ;
 vp9_zero ( next_frame ) ;
 mod_frame_err = calculate_modified_err ( twopass , oxcf , this_frame ) ;
 gf_first_frame_err = mod_frame_err ;
 if ( cpi -> common . frame_type == KEY_FRAME || rc -> source_alt_ref_active ) gf_group_err -= gf_first_frame_err ;
 mv_ratio_accumulator_thresh = ( cpi -> common . width + cpi -> common . height ) / 4.0 ;
 if ( cpi -> multi_arf_allowed ) {
 active_max_gf_interval = rc -> max_gf_interval ;
 }
 else {
 active_max_gf_interval = + ( ( int ) vp9_convert_qindex_to_q ( rc -> last_q [ INTER_FRAME ] , cpi -> common . bit_depth ) >> 5 ) ;
 if ( active_max_gf_interval > rc -> max_gf_interval ) active_max_gf_interval = rc -> max_gf_interval ;
 }
 i = 0 ;
 while ( i < rc -> static_scene_max_gf_interval && i < rc -> frames_to_key ) {
 ++ i ;
 mod_frame_err = calculate_modified_err ( twopass , oxcf , this_frame ) ;
 gf_group_err += mod_frame_err ;
 if ( EOF == input_stats ( twopass , & next_frame ) ) break ;
 flash_detected = detect_flash ( twopass , 0 ) ;
 accumulate_frame_motion_stats ( & next_frame , & this_frame_mv_in_out , & mv_in_out_accumulator , & abs_mv_in_out_accumulator , & mv_ratio_accumulator ) ;
 if ( ! flash_detected ) {
 last_loop_decay_rate = loop_decay_rate ;
 loop_decay_rate = get_prediction_decay_rate ( & cpi -> common , & next_frame ) ;
 decay_accumulator = decay_accumulator * loop_decay_rate ;
 zero_motion_accumulator = MIN ( zero_motion_accumulator , get_zero_motion_factor ( & cpi -> common , & next_frame ) ) ;
 if ( detect_transition_to_still ( twopass , i , 5 , loop_decay_rate , last_loop_decay_rate ) ) {
 allow_alt_ref = 0 ;
 break ;
 }
 }
 boost_score += decay_accumulator * calc_frame_boost ( cpi , & next_frame , this_frame_mv_in_out , GF_MAX_BOOST ) ;
 if ( ( i >= active_max_gf_interval && ( zero_motion_accumulator < 0.995 ) ) || ( ( i > MIN_GF_INTERVAL ) && ( ! flash_detected ) && ( ( mv_ratio_accumulator > mv_ratio_accumulator_thresh ) || ( abs_mv_in_out_accumulator > 3.0 ) || ( mv_in_out_accumulator < - 2.0 ) || ( ( boost_score - old_boost_score ) < BOOST_FACTOR ) ) ) ) {
 boost_score = old_boost_score ;
 break ;
 }
 * this_frame = next_frame ;
 old_boost_score = boost_score ;
 }
 twopass -> gf_zeromotion_pct = ( int ) ( zero_motion_accumulator * 1000.0 ) ;
 if ( cpi -> common . frame_type == KEY_FRAME || rc -> source_alt_ref_active ) rc -> baseline_gf_interval = i - 1 ;
 else rc -> baseline_gf_interval = i ;
 if ( is_two_pass_svc ( cpi ) && cpi -> svc . number_temporal_layers > 1 ) {
 int count = ( 1 << ( cpi -> svc . number_temporal_layers - 1 ) ) - 1 ;
 int new_gf_interval = ( rc -> baseline_gf_interval + count ) & ( ~ count ) ;
 int j ;
 for ( j = 0 ;
 j < new_gf_interval - rc -> baseline_gf_interval ;
 ++ j ) {
 if ( EOF == input_stats ( twopass , this_frame ) ) break ;
 gf_group_err += calculate_modified_err ( twopass , oxcf , this_frame ) ;
 }
 rc -> baseline_gf_interval = new_gf_interval ;
 }
 rc -> frames_till_gf_update_due = rc -> baseline_gf_interval ;
 if ( allow_alt_ref && ( i < cpi -> oxcf . lag_in_frames ) && ( i >= MIN_GF_INTERVAL ) ) {
 rc -> gfu_boost = calc_arf_boost ( cpi , 0 , ( i - 1 ) , ( i - 1 ) , & f_boost , & b_boost ) ;
 rc -> source_alt_ref_pending = 1 ;
 cpi -> multi_arf_enabled = ( cpi -> multi_arf_allowed && ( rc -> baseline_gf_interval >= 6 ) && ( zero_motion_accumulator < 0.995 ) ) ? 1 : 0 ;
 }
 else {
 rc -> gfu_boost = MAX ( ( int ) boost_score , 125 ) ;
 rc -> source_alt_ref_pending = 0 ;
 }
 reset_fpf_position ( twopass , start_pos ) ;
 gf_group_bits = calculate_total_gf_group_bits ( cpi , gf_group_err ) ;
 {
 int q = rc -> last_q [ INTER_FRAME ] ;
 int boost = ( rc -> gfu_boost * gfboost_qadjust ( q , cpi -> common . bit_depth ) ) / 100 ;
 boost = clamp ( boost , 125 , ( rc -> baseline_gf_interval + 1 ) * 200 ) ;
 gf_arf_bits = calculate_boost_bits ( rc -> baseline_gf_interval , boost , gf_group_bits ) ;
 }
 twopass -> kf_group_error_left -= ( int64_t ) gf_group_err ;
 if ( rc -> source_alt_ref_pending ) {
 gf_group_error_left = gf_group_err - mod_frame_err ;
 }
 else if ( cpi -> common . frame_type != KEY_FRAME ) {
 gf_group_error_left = gf_group_err - gf_first_frame_err ;
 }
 else {
 gf_group_error_left = gf_group_err ;
 }
 allocate_gf_group_bits ( cpi , gf_group_bits , gf_group_error_left , gf_arf_bits ) ;
 reset_fpf_position ( twopass , start_pos ) ;
 if ( cpi -> common . frame_type != KEY_FRAME ) {
 twopass -> section_intra_rating = calculate_section_intra_ratio ( start_pos , twopass -> stats_in_end , rc -> baseline_gf_interval ) ;
 }
 }

In the above code snippet, check for potential security vulnerabilities and answer with a single digit: 1 if Vulnerable, 0 if Non-vulnerable.

The guarded evidence of the code snippet is as follows:
GUARDED EVIDENCE: operation-specific observed relations; not a safety proof.
N1 CALL "cpi -> common . frame_type != KEY_FRAME"
N2 CALL "twopass -> gf_group"
N3 CALL "cpi -> common . frame_type == KEY_FRAME"
N4 CALL "rc -> source_alt_ref_active"
N5 CALL "cpi -> multi_arf_allowed"
N6 CALL "rc -> last_q"
N7 CALL "cpi -> common"
N8 FIELD_IDENTIFIER "gf_group"
N9 IDENTIFIER "twopass"
N1 --CDG--> N2
N2 --ARGUMENT--> N8
N2 --ARGUMENT--> N9
N3 --CDG--> N4
N5 --CDG--> N6
N5 --CDG--> N7
OP N2
  INPUTS N8,N9
  DIRECT_CONTROL N1 via=CDG branch=unknown check=cdg_observed_cfg_unknown
  DATA_NOTE: predicates on related data are not operation controls.
OP N4
  INPUTS not included/unknown
  DIRECT_CONTROL N3 via=CDG branch=unknown check=cdg_observed_cfg_unknown
OP N6
  INPUTS not included/unknown
  DIRECT_CONTROL N5 via=CDG branch=unknown check=cdg_observed_cfg_unknown
OP N7
  INPUTS not included/unknown
  DIRECT_CONTROL N5 via=CDG branch=unknown check=cdg_observed_cfg_unknown
UNKNOWN: guard sufficiency, aliasing and feasible execution paths. Missing polarity is unknown.
BOUNDED: omitted operations/context and shortened snippets are not proof of absence.

The following is an example, and it is .


Answer (0 or 1):
~~~~~

## Sample 53 · reveal · B1-H2 · seed 42

ID: `reveal:validation:554`  
Prompt SHA-256: `32c635cf08c8bccb7d30f7dc0be4b51a61d95dbba0d56d69b902f74cbd600aa4`  
Stratum: `no_usable_evidence`

~~~~~text
You are now an excellent programmer. You are conducting a function vulnerability detection task for C/C++ language.

static void stop_postmaster_atexit ( void ) {
 stop_postmaster ( true ) ;
 }

In the above code snippet, check for potential security vulnerabilities and answer with a single digit: 1 if Vulnerable, 0 if Non-vulnerable.

The guarded evidence of the code snippet is as follows:
GUARDED EVIDENCE: operation-specific observed relations; not a safety proof.
N1 CALL "stop_postmaster ( true )"
N2 IDENTIFIER "<unknown> true"
N3 LOCAL "<unknown> true"
N1 --ARGUMENT--> N2
N2 --REACHING_DEF--> N1
N2 --REF--> N3
OP N1
  INPUTS N2
  DIRECT_CONTROL unknown: CDG unavailable
UNKNOWN: guard sufficiency, aliasing and feasible execution paths. Missing polarity is unknown.
BOUNDED: omitted operations/context and shortened snippets are not proof of absence.

The following is an example, and it is .


Answer (0 or 1):
~~~~~

## Sample 54 · reveal · B1-H2 · seed 42

ID: `reveal:validation:591`  
Prompt SHA-256: `28d31530bf6972cbb809df9d8129739479ef1e39027c26e8e3572638d345e9ab`  
Stratum: `cdg_cluster`

~~~~~text
You are now an excellent programmer. You are conducting a function vulnerability detection task for C/C++ language.

void vp8_de_noise ( VP8_COMMON * cm , YV12_BUFFER_CONFIG * source , YV12_BUFFER_CONFIG * post , int q , int low_var_thresh , int flag ) {
 int mbr ;
 double level = 6.0e-05 * q * q * q - .0067 * q * q + .306 * q + .0065 ;
 int ppl = ( int ) ( level + .5 ) ;
 int mb_rows = cm -> mb_rows ;
 int mb_cols = cm -> mb_cols ;
 unsigned char * limits = cm -> pp_limits_buffer ;
 ;
 ( void ) post ;
 ( void ) low_var_thresh ;
 ( void ) flag ;
 vpx_memset ( limits , ( unsigned char ) ppl , 16 * mb_cols ) ;
 for ( mbr = 0 ;
 mbr < mb_rows ;
 mbr ++ ) {
 vp8_post_proc_down_and_across_mb_row ( source -> y_buffer + 16 * mbr * source -> y_stride , source -> y_buffer + 16 * mbr * source -> y_stride , source -> y_stride , source -> y_stride , source -> y_width , limits , 16 ) ;
 vp8_post_proc_down_and_across_mb_row ( source -> u_buffer + 8 * mbr * source -> uv_stride , source -> u_buffer + 8 * mbr * source -> uv_stride , source -> uv_stride , source -> uv_stride , source -> uv_width , limits , 8 ) ;
 vp8_post_proc_down_and_across_mb_row ( source -> v_buffer + 8 * mbr * source -> uv_stride , source -> v_buffer + 8 * mbr * source -> uv_stride , source -> uv_stride , source -> uv_stride , source -> uv_width , limits , 8 ) ;
 }
 }

In the above code snippet, check for potential security vulnerabilities and answer with a single digit: 1 if Vulnerable, 0 if Non-vulnerable.

The guarded evidence of the code snippet is as follows:
GUARDED EVIDENCE: operation-specific observed relations; not a safety proof.
N1 METHOD_RETURN "RET"
N2 CALL "mbr < mb_rows"
N3 CALL "source -> y_buffer"
N4 CALL "source -> uv_stride"
N5 CALL "source -> uv_width"
N6 CALL "source -> v_buffer"
N2 --CFG--> N1
N2 --CDG--> N3
N2 --CDG--> N4
N2 --CDG--> N5
N2 --CDG--> N6
OP N3
  INPUTS not included/unknown
  DIRECT_CONTROL N2 via=CDG branch=unknown check=cfg_one_branch_witness
  OBSERVED_EXIT N1 from=N2 branch=unknown
OP N4
  INPUTS not included/unknown
  DIRECT_CONTROL N2 via=CDG branch=unknown check=cdg_observed_cfg_unknown
  OBSERVED_EXIT N1 from=N2 branch=unknown
OP N5
  INPUTS not included/unknown
  DIRECT_CONTROL N2 via=CDG branch=unknown check=cdg_observed_cfg_unknown
  OBSERVED_EXIT N1 from=N2 branch=unknown
OP N6
  INPUTS not included/unknown
  DIRECT_CONTROL N2 via=CDG branch=unknown check=cdg_observed_cfg_unknown
  OBSERVED_EXIT N1 from=N2 branch=unknown
UNKNOWN: guard sufficiency, aliasing and feasible execution paths. Missing polarity is unknown.
BOUNDED: omitted operations/context and shortened snippets are not proof of absence.

The following is an example, and it is .


Answer (0 or 1):
~~~~~

## Sample 55 · reveal · B1-H2 · seed 42

ID: `reveal:validation:599`  
Prompt SHA-256: `c96b14c02d657c310603d7d979d37e0a298ebd6df81f1247a78cd0597e6c432f`  
Stratum: `cdg_cluster`

~~~~~text
You are now an excellent programmer. You are conducting a function vulnerability detection task for C/C++ language.

void ff_cavs_load_intra_pred_luma ( AVSContext * h , uint8_t * top , uint8_t * * left , int block ) {
 int i ;
 switch ( block ) {
 case 0 : * left = h -> left_border_y ;
 h -> left_border_y [ 0 ] = h -> left_border_y [ 1 ] ;
 memset ( & h -> left_border_y [ 17 ] , h -> left_border_y [ 16 ] , 9 ) ;
 memcpy ( & top [ 1 ] , & h -> top_border_y [ h -> mbx * 16 ] , 16 ) ;
 top [ 17 ] = top [ 16 ] ;
 top [ 0 ] = top [ 1 ] ;
 if ( ( h -> flags & A_AVAIL ) && ( h -> flags & B_AVAIL ) ) h -> left_border_y [ 0 ] = top [ 0 ] = h -> topleft_border_y ;
 break ;
 case 1 : * left = h -> intern_border_y ;
 for ( i = 0 ;
 i < 8 ;
 i ++ ) h -> intern_border_y [ i + 1 ] = * ( h -> cy + 7 + i * h -> l_stride ) ;
 memset ( & h -> intern_border_y [ 9 ] , h -> intern_border_y [ 8 ] , 9 ) ;
 h -> intern_border_y [ 0 ] = h -> intern_border_y [ 1 ] ;
 memcpy ( & top [ 1 ] , & h -> top_border_y [ h -> mbx * 16 + 8 ] , 8 ) ;
 if ( h -> flags & C_AVAIL ) memcpy ( & top [ 9 ] , & h -> top_border_y [ ( h -> mbx + 1 ) * 16 ] , 8 ) ;
 else memset ( & top [ 9 ] , top [ 8 ] , 9 ) ;
 top [ 17 ] = top [ 16 ] ;
 top [ 0 ] = top [ 1 ] ;
 if ( h -> flags & B_AVAIL ) h -> intern_border_y [ 0 ] = top [ 0 ] = h -> top_border_y [ h -> mbx * 16 + 7 ] ;
 break ;
 case 2 : * left = & h -> left_border_y [ 8 ] ;
 memcpy ( & top [ 1 ] , h -> cy + 7 * h -> l_stride , 16 ) ;
 top [ 17 ] = top [ 16 ] ;
 top [ 0 ] = top [ 1 ] ;
 if ( h -> flags & A_AVAIL ) top [ 0 ] = h -> left_border_y [ 8 ] ;
 break ;
 case 3 : * left = & h -> intern_border_y [ 8 ] ;
 for ( i = 0 ;
 i < 8 ;
 i ++ ) h -> intern_border_y [ i + 9 ] = * ( h -> cy + 7 + ( i + 8 ) * h -> l_stride ) ;
 memset ( & h -> intern_border_y [ 17 ] , h -> intern_border_y [ 16 ] , 9 ) ;
 memcpy ( & top [ 0 ] , h -> cy + 7 + 7 * h -> l_stride , 9 ) ;
 memset ( & top [ 9 ] , top [ 8 ] , 9 ) ;
 break ;
 }
 }

In the above code snippet, check for potential security vulnerabilities and answer with a single digit: 1 if Vulnerable, 0 if Non-vulnerable.

The guarded evidence of the code snippet is as follows:
GUARDED EVIDENCE: operation-specific observed relations; not a safety proof.
N1 METHOD_RETURN "RET"
N2 CALL "\n        memcpy ( & top [ 1 ] , & h -> top_border_y [ h -> mbx * 16 + 8 ] , 8 )\n      "
N3 CALL "& h -> top_border_y [ h -> mbx * 16 + 8 ]"
N4 CALL "h -> flags & C_AVAIL"
N5 CALL "\n        memcpy ( & top [ 9 ] , & h -> top_border_y [ ( h -> mbx + 1 ) * 16 ] , 8 )\n      "
N6 CALL "& h -> top_border_y [ ( h -> mbx + 1 ) * 16 ]"
N7 CALL "memcpy ( & top [ 1 ] , h -> cy + 7 * h -> l_stride , 16 )"
N8 CALL "h -> cy + 7 * h -> l_stride"
N9 CALL "memcpy ( & top [ 0 ] , h -> cy + 7 + 7 * h -> l_stride , 9 )"
N10 IDENTIFIER "block"
N11 LITERAL "8"
N12 LITERAL "8"
N13 LITERAL "16"
N2 --ARGUMENT--> N3
N2 --ARGUMENT--> N11
N3 --REACHING_DEF--> N2
N4 --CDG--> N5
N5 --ARGUMENT--> N6
N5 --ARGUMENT--> N12
N6 --REACHING_DEF--> N5
N7 --ARGUMENT--> N8
N7 --ARGUMENT--> N13
N10 --CFG--> N1
N10 --CDG--> N2
N10 --CDG--> N7
N10 --CDG--> N9
OP N2
  INPUTS N3,N11
  DIRECT_CONTROL N10 via=CDG branch=unknown check=cdg_observed_cfg_unknown
  OBSERVED_EXIT N1 from=N10 branch=unknown
OP N5
  INPUTS N6,N12
  DIRECT_CONTROL N4 via=CDG branch=unknown check=cdg_observed_cfg_unknown
  DATA_NOTE: predicates on related data are not operation controls.
OP N7
  INPUTS N8,N13
  DIRECT_CONTROL N10 via=CDG branch=unknown check=cdg_observed_cfg_unknown
  OBSERVED_EXIT N1 from=N10 branch=unknown
OP N9
  INPUTS not included/unknown
  DIRECT_CONTROL N10 via=CDG branch=unknown check=cdg_observed_cfg_unknown
  OBSERVED_EXIT N1 from=N10 branch=unknown
UNKNOWN: guard sufficiency, aliasing and feasible execution paths. Missing polarity is unknown.
BOUNDED: omitted operations/context and shortened snippets are not proof of absence.

The following is an example, and it is .


Answer (0 or 1):
~~~~~

## Sample 56 · reveal · B1-H2 · seed 42

ID: `reveal:validation:67`  
Prompt SHA-256: `f3af3098c0921ce32d71067d92f1249920f16a164ca5f6bebdae67fddcbafa8f`  
Stratum: `cdg_cluster`

~~~~~text
You are now an excellent programmer. You are conducting a function vulnerability detection task for C/C++ language.

static void nonrd_pick_partition ( VP9_COMP * cpi , const TileInfo * const tile , TOKENEXTRA * * tp , int mi_row , int mi_col , BLOCK_SIZE bsize , int * rate , int64_t * dist , int do_recon , int64_t best_rd , PC_TREE * pc_tree ) {
 const SPEED_FEATURES * const sf = & cpi -> sf ;
 const VP9EncoderConfig * const oxcf = & cpi -> oxcf ;
 VP9_COMMON * const cm = & cpi -> common ;
 MACROBLOCK * const x = & cpi -> mb ;
 MACROBLOCKD * const xd = & x -> e_mbd ;
 const int ms = num_8x8_blocks_wide_lookup [ bsize ] / 2 ;
 TOKENEXTRA * tp_orig = * tp ;
 PICK_MODE_CONTEXT * ctx = & pc_tree -> none ;
 int i ;
 BLOCK_SIZE subsize = bsize ;
 int this_rate , sum_rate = 0 , best_rate = INT_MAX ;
 int64_t this_dist , sum_dist = 0 , best_dist = INT64_MAX ;
 int64_t sum_rd = 0 ;
 int do_split = bsize >= BLOCK_8X8 ;
 int do_rect = 1 ;
 const int force_horz_split = ( mi_row + ms >= cm -> mi_rows ) ;
 const int force_vert_split = ( mi_col + ms >= cm -> mi_cols ) ;
 const int xss = x -> e_mbd . plane [ 1 ] . subsampling_x ;
 const int yss = x -> e_mbd . plane [ 1 ] . subsampling_y ;
 int partition_none_allowed = ! force_horz_split && ! force_vert_split ;
 int partition_horz_allowed = ! force_vert_split && yss <= xss && bsize >= BLOCK_8X8 ;
 int partition_vert_allowed = ! force_horz_split && xss <= yss && bsize >= BLOCK_8X8 ;
 ( void ) * tp_orig ;
 assert ( num_8x8_blocks_wide_lookup [ bsize ] == num_8x8_blocks_high_lookup [ bsize ] ) ;
 if ( sf -> auto_min_max_partition_size ) {
 partition_none_allowed &= ( bsize <= sf -> max_partition_size && bsize >= sf -> min_partition_size ) ;
 partition_horz_allowed &= ( ( bsize <= sf -> max_partition_size && bsize > sf -> min_partition_size ) || force_horz_split ) ;
 partition_vert_allowed &= ( ( bsize <= sf -> max_partition_size && bsize > sf -> min_partition_size ) || force_vert_split ) ;
 do_split &= bsize > sf -> min_partition_size ;
 }
 if ( sf -> use_square_partition_only ) {
 partition_horz_allowed &= force_horz_split ;
 partition_vert_allowed &= force_vert_split ;
 }
 if ( partition_none_allowed ) {
 nonrd_pick_sb_modes ( cpi , tile , mi_row , mi_col , & this_rate , & this_dist , bsize , ctx ) ;
 ctx -> mic . mbmi = xd -> mi [ 0 ] . src_mi -> mbmi ;
 ctx -> skip_txfm [ 0 ] = x -> skip_txfm [ 0 ] ;
 ctx -> skip = x -> skip ;
 if ( this_rate != INT_MAX ) {
 int pl = partition_plane_context ( xd , mi_row , mi_col , bsize ) ;
 this_rate += cpi -> partition_cost [ pl ] [ PARTITION_NONE ] ;
 sum_rd = RDCOST ( x -> rdmult , x -> rddiv , this_rate , this_dist ) ;
 if ( sum_rd < best_rd ) {
 int64_t stop_thresh = 4096 ;
 int64_t stop_thresh_rd ;
 best_rate = this_rate ;
 best_dist = this_dist ;
 best_rd = sum_rd ;
 if ( bsize >= BLOCK_8X8 ) pc_tree -> partitioning = PARTITION_NONE ;
 stop_thresh >>= 8 - ( b_width_log2 ( bsize ) + b_height_log2 ( bsize ) ) ;
 stop_thresh_rd = RDCOST ( x -> rdmult , x -> rddiv , 0 , stop_thresh ) ;
 if ( ! x -> e_mbd . lossless && best_rd < stop_thresh_rd ) {
 do_split = 0 ;
 do_rect = 0 ;
 }
 }
 }
 }
 store_pred_mv ( x , ctx ) ;
 sum_rd = 0 ;
 if ( do_split ) {
 int pl = partition_plane_context ( xd , mi_row , mi_col , bsize ) ;
 sum_rate += cpi -> partition_cost [ pl ] [ PARTITION_SPLIT ] ;
 subsize = get_subsize ( bsize , PARTITION_SPLIT ) ;
 for ( i = 0 ;
 i < 4 && sum_rd < best_rd ;
 ++ i ) {
 const int x_idx = ( i & 1 ) * ms ;
 const int y_idx = ( i >> 1 ) * ms ;
 if ( mi_row + y_idx >= cm -> mi_rows || mi_col + x_idx >= cm -> mi_cols ) continue ;
 load_pred_mv ( x , ctx ) ;
 nonrd_pick_partition ( cpi , tile , tp , mi_row + y_idx , mi_col + x_idx , subsize , & this_rate , & this_dist , 0 , best_rd - sum_rd , pc_tree -> split [ i ] ) ;
 if ( this_rate == INT_MAX ) {
 sum_rd = INT64_MAX ;
 }
 else {
 sum_rate += this_rate ;
 sum_dist += this_dist ;
 sum_rd = RDCOST ( x -> rdmult , x -> rddiv , sum_rate , sum_dist ) ;
 }
 }
 if ( sum_rd < best_rd ) {
 best_rate = sum_rate ;
 best_dist = sum_dist ;
 best_rd = sum_rd ;
 pc_tree -> partitioning = PARTITION_SPLIT ;
 }
 else {
 if ( sf -> less_rectangular_check ) do_rect &= ! partition_none_allowed ;
 }
 }
 if ( partition_horz_allowed && do_rect ) {
 subsize = get_subsize ( bsize , PARTITION_HORZ ) ;
 if ( sf -> adaptive_motion_search ) load_pred_mv ( x , ctx ) ;
 nonrd_pick_sb_modes ( cpi , tile , mi_row , mi_col , & this_rate , & this_dist , subsize , & pc_tree -> horizontal [ 0 ] ) ;
 pc_tree -> horizontal [ 0 ] . mic . mbmi = xd -> mi [ 0 ] . src_mi -> mbmi ;
 pc_tree -> horizontal [ 0 ] . skip_txfm [ 0 ] = x -> skip_txfm [ 0 ] ;
 pc_tree -> horizontal [ 0 ] . skip = x -> skip ;
 sum_rd = RDCOST ( x -> rdmult , x -> rddiv , sum_rate , sum_dist ) ;
 if ( sum_rd < best_rd && mi_row + ms < cm -> mi_rows ) {
 load_pred_mv ( x , ctx ) ;
 nonrd_pick_sb_modes ( cpi , tile , mi_row + ms , mi_col , & this_rate , & this_dist , subsize , & pc_tree -> horizontal [ 1 ] ) ;
 pc_tree -> horizontal [ 1 ] . mic . mbmi = xd -> mi [ 0 ] . src_mi -> mbmi ;
 pc_tree -> horizontal [ 1 ] . skip_txfm [ 0 ] = x -> skip_txfm [ 0 ] ;
 pc_tree -> horizontal [ 1 ] . skip = x -> skip ;
 if ( this_rate == INT_MAX ) {
 sum_rd = INT64_MAX ;
 }
 else {
 int pl = partition_plane_context ( xd , mi_row , mi_col , bsize ) ;
 this_rate += cpi -> partition_cost [ pl ] [ PARTITION_HORZ ] ;
 sum_rate += this_rate ;
 sum_dist += this_dist ;
 sum_rd = RDCOST ( x -> rdmult , x -> rddiv , sum_rate , sum_dist ) ;
 }
 }
 if ( sum_rd < best_rd ) {
 best_rd = sum_rd ;
 best_rate = sum_rate ;
 best_dist = sum_dist ;
 pc_tree -> partitioning = PARTITION_HORZ ;
 }
 }
 if ( partition_vert_allowed && do_rect ) {
 subsize = get_subsize ( bsize , PARTITION_VERT ) ;
 if ( sf -> adaptive_motion_search ) load_pred_mv ( x , ctx ) ;
 nonrd_pick_sb_modes ( cpi , tile , mi_row , mi_col , & this_rate , & this_dist , subsize , & pc_tree -> vertical [ 0 ] ) ;
 pc_tree -> vertical [ 0 ] . mic . mbmi = xd -> mi [ 0 ] . src_mi -> mbmi ;
 pc_tree -> vertical [ 0 ] . skip_txfm [ 0 ] = x -> skip_txfm [ 0 ] ;
 pc_tree -> vertical [ 0 ] . skip = x -> skip ;
 sum_rd = RDCOST ( x -> rdmult , x -> rddiv , sum_rate , sum_dist ) ;
 if ( sum_rd < best_rd && mi_col + ms < cm -> mi_cols ) {
 load_pred_mv ( x , ctx ) ;
 nonrd_pick_sb_modes ( cpi , tile , mi_row , mi_col + ms , & this_rate , & this_dist , subsize , & pc_tree -> vertical [ 1 ] ) ;
 pc_tree -> vertical [ 1 ] . mic . mbmi = xd -> mi [ 0 ] . src_mi -> mbmi ;
 pc_tree -> vertical [ 1 ] . skip_txfm [ 0 ] = x -> skip_txfm [ 0 ] ;
 pc_tree -> vertical [ 1 ] . skip = x -> skip ;
 if ( this_rate == INT_MAX ) {
 sum_rd = INT64_MAX ;
 }
 else {
 int pl = partition_plane_context ( xd , mi_row , mi_col , bsize ) ;
 this_rate += cpi -> partition_cost [ pl ] [ PARTITION_VERT ] ;
 sum_rate += this_rate ;
 sum_dist += this_dist ;
 sum_rd = RDCOST ( x -> rdmult , x -> rddiv , sum_rate , sum_dist ) ;
 }
 }
 if ( sum_rd < best_rd ) {
 best_rate = sum_rate ;
 best_dist = sum_dist ;
 best_rd = sum_rd ;
 pc_tree -> partitioning = PARTITION_VERT ;
 }
 }
 ( void ) best_rd ;
 * rate = best_rate ;
 * dist = best_dist ;
 if ( best_rate == INT_MAX ) return ;
 subsize = get_subsize ( bsize , pc_tree -> partitioning ) ;
 fill_mode_info_sb ( cm , x , mi_row , mi_col , bsize , subsize , pc_tree ) ;
 if ( best_rate < INT_MAX && best_dist < INT64_MAX && do_recon ) {
 int output_enabled = ( bsize == BLOCK_64X64 ) ;
 if ( ( oxcf -> aq_mode == COMPLEXITY_AQ ) && cm -> seg . update_map ) {
 vp9_select_in_frame_q_segment ( cpi , mi_row , mi_col , output_enabled , best_rate ) ;
 }
 if ( oxcf -> aq_mode == CYCLIC_REFRESH_AQ ) vp9_cyclic_refresh_set_rate_and_dist_sb ( cpi -> cyclic_refresh , best_rate , best_dist ) ;
 encode_sb_rt ( cpi , tile , tp , mi_row , mi_col , output_enabled , bsize , pc_tree ) ;
 }
 if ( bsize == BLOCK_64X64 ) {
 assert ( tp_orig < * tp ) ;
 assert ( best_rate < INT_MAX ) ;
 assert ( best_dist < INT64_MAX ) ;
 }
 else {
 assert ( tp_orig == * tp ) ;
 }
 }

In the above code snippet, check for potential security vulnerabilities and answer with a single digit: 1 if Vulnerable, 0 if Non-vulnerable.

The guarded evidence of the code snippet is as follows:
GUARDED EVIDENCE: operation-specific observed relations; not a safety proof.
N1 CALL "sf -> auto_min_max_partition_size"
N2 CALL "sf -> max_partition_size"
N3 CALL "sf -> max_partition_size"
N4 CALL "sf -> max_partition_size"
N5 CALL "sf -> min_partition_size"
N1 --CDG--> N2
N1 --CDG--> N3
N1 --CDG--> N4
N1 --CDG--> N5
OP N2
  INPUTS not included/unknown
  DIRECT_CONTROL N1 via=CDG branch=unknown check=cdg_observed_cfg_unknown
OP N3
  INPUTS not included/unknown
  DIRECT_CONTROL N1 via=CDG branch=unknown check=cdg_observed_cfg_unknown
OP N4
  INPUTS not included/unknown
  DIRECT_CONTROL N1 via=CDG branch=unknown check=cdg_observed_cfg_unknown
OP N5
  INPUTS not included/unknown
  DIRECT_CONTROL N1 via=CDG branch=unknown check=cdg_observed_cfg_unknown
UNKNOWN: guard sufficiency, aliasing and feasible execution paths. Missing polarity is unknown.
BOUNDED: omitted operations/context and shortened snippets are not proof of absence.

The following is an example, and it is .


Answer (0 or 1):
~~~~~

## Sample 57 · reveal · B1-H2 · seed 42

ID: `reveal:validation:673`  
Prompt SHA-256: `9800cb57e1e3189e9ab11ea9f5fab123f25a96a7bd19ff824604cd678c77fc01`  
Stratum: `no_usable_evidence`

~~~~~text
You are now an excellent programmer. You are conducting a function vulnerability detection task for C/C++ language.

static UBool action_reverse ( UBiDiTransform * pTransform , UErrorCode * pErrorCode ) {
 ubidi_writeReverse ( pTransform -> src , pTransform -> srcLength , pTransform -> dest , pTransform -> destSize , UBIDI_REORDER_DEFAULT , pErrorCode ) ;
 * pTransform -> pDestLength = pTransform -> srcLength ;
 return TRUE ;
 }

In the above code snippet, check for potential security vulnerabilities and answer with a single digit: 1 if Vulnerable, 0 if Non-vulnerable.

The guarded evidence of the code snippet is as follows:
GUARDED EVIDENCE: operation-specific observed relations; not a safety proof.
N1 CALL "pTransform -> src"
N2 CALL "pTransform -> srcLength"
N3 CALL "pTransform -> dest"
N4 CALL "pTransform -> destSize"
N5 FIELD_IDENTIFIER "src"
N6 FIELD_IDENTIFIER "srcLength"
N7 FIELD_IDENTIFIER "dest"
N8 FIELD_IDENTIFIER "destSize"
N9 IDENTIFIER "pTransform"
N10 IDENTIFIER "pTransform"
N11 IDENTIFIER "pTransform"
N12 IDENTIFIER "pTransform"
N1 --REACHING_DEF--> N2
N1 --REACHING_DEF--> N3
N1 --REACHING_DEF--> N4
N1 --ARGUMENT--> N5
N1 --ARGUMENT--> N9
N2 --REACHING_DEF--> N1
N2 --REACHING_DEF--> N3
N2 --REACHING_DEF--> N4
N2 --ARGUMENT--> N6
N2 --ARGUMENT--> N10
N3 --REACHING_DEF--> N1
N3 --REACHING_DEF--> N2
N3 --REACHING_DEF--> N4
N3 --ARGUMENT--> N7
N3 --ARGUMENT--> N11
N4 --REACHING_DEF--> N1
N4 --ARGUMENT--> N8
N4 --ARGUMENT--> N12
OP N1
  INPUTS N5,N9
  DIRECT_CONTROL unknown: CDG unavailable
OP N2
  INPUTS N6,N10
  DIRECT_CONTROL unknown: CDG unavailable
OP N3
  INPUTS N7,N11
  DIRECT_CONTROL unknown: CDG unavailable
OP N4
  INPUTS N8,N12
  DIRECT_CONTROL unknown: CDG unavailable
UNKNOWN: guard sufficiency, aliasing and feasible execution paths. Missing polarity is unknown.
BOUNDED: omitted operations/context and shortened snippets are not proof of absence.

The following is an example, and it is .


Answer (0 or 1):
~~~~~

## Sample 58 · reveal · B1-H2 · seed 42

ID: `reveal:validation:688`  
Prompt SHA-256: `55d8280110829baf120fae4b32ddded149d813b57763bcab925e30334e6619df`  
Stratum: `cdg_cluster`

~~~~~text
You are now an excellent programmer. You are conducting a function vulnerability detection task for C/C++ language.

static void e1000e_set_ims ( E1000ECore * core , int index , uint32_t val ) {
 static const uint32_t ims_ext_mask = E1000_IMS_RXQ0 | E1000_IMS_RXQ1 | E1000_IMS_TXQ0 | E1000_IMS_TXQ1 | E1000_IMS_OTHER ;
 static const uint32_t ims_valid_mask = E1000_IMS_TXDW | E1000_IMS_TXQE | E1000_IMS_LSC | E1000_IMS_RXDMT0 | E1000_IMS_RXO | E1000_IMS_RXT0 | E1000_IMS_MDAC | E1000_IMS_TXD_LOW | E1000_IMS_SRPD | E1000_IMS_ACK | E1000_IMS_MNG | E1000_IMS_RXQ0 | E1000_IMS_RXQ1 | E1000_IMS_TXQ0 | E1000_IMS_TXQ1 | E1000_IMS_OTHER ;
 uint32_t valid_val = val & ims_valid_mask ;
 trace_e1000e_irq_set_ims ( val , core -> mac [ IMS ] , core -> mac [ IMS ] | valid_val ) ;
 core -> mac [ IMS ] |= valid_val ;
 if ( ( valid_val & ims_ext_mask ) && ( core -> mac [ CTRL_EXT ] & E1000_CTRL_EXT_PBA_CLR ) && msix_enabled ( core -> owner ) ) {
 e1000e_msix_clear ( core , valid_val ) ;
 }
 if ( ( valid_val == ims_valid_mask ) && ( core -> mac [ CTRL_EXT ] & E1000_CTRL_EXT_INT_TIMERS_CLEAR_ENA ) ) {
 trace_e1000e_irq_fire_all_timers ( val ) ;
 e1000e_intrmgr_fire_all_timers ( core ) ;
 }
 e1000e_update_interrupt_state ( core ) ;
 }

In the above code snippet, check for potential security vulnerabilities and answer with a single digit: 1 if Vulnerable, 0 if Non-vulnerable.

The guarded evidence of the code snippet is as follows:
GUARDED EVIDENCE: operation-specific observed relations; not a safety proof.
N1 METHOD_RETURN "RET"
N2 CALL "core -> mac [ IMS ]"
N3 CALL "\n        ( valid_val & ims_ext_mask ) && ( core -> mac [ CTRL_EXT ] & E1000_CTRL_EXT_PBA_CLR )\n      "
N4 CALL "valid_val & ims_ext_mask"
N5 CALL "core -> mac [ CTRL_EXT ]"
N6 CALL "core -> mac"
N7 CALL "core -> owner"
N8 CALL "\n        ( valid_val == ims_valid_mask ) && ( core -> mac [ CTRL_EXT ] & E1000_CTRL_EXT_INT_TIMERS_CLEAR_ENA )\n      "
N9 CALL "valid_val == ims_valid_mask"
N10 CALL "core -> mac"
N11 CALL "e1000e_update_interrupt_state ( core )"
N12 IDENTIFIER "core"
N2 --REACHING_DEF--> N6
N2 --REACHING_DEF--> N10
N3 --CDG--> N7
N4 --CDG--> N5
N4 --CDG--> N6
N8 --CFG--> N12
N9 --CFG--> N8
N9 --CDG--> N10
N11 --CFG--> N1
N12 --CFG--> N11
OP N5
  INPUTS not included/unknown
  DIRECT_CONTROL N4 via=CDG branch=unknown check=cdg_observed_cfg_unknown
OP N6
  INPUTS not included/unknown
  DIRECT_CONTROL N4 via=CDG branch=unknown check=cdg_observed_cfg_unknown
OP N7
  INPUTS not included/unknown
  DIRECT_CONTROL N3 via=CDG branch=unknown check=cdg_observed_cfg_unknown
OP N10
  INPUTS not included/unknown
  DIRECT_CONTROL N9 via=CDG branch=unknown check=cdg_observed_cfg_unknown
  OBSERVED_EXIT N1 from=N9 branch=unknown
UNKNOWN: guard sufficiency, aliasing and feasible execution paths. Missing polarity is unknown.
BOUNDED: omitted operations/context and shortened snippets are not proof of absence.

The following is an example, and it is .


Answer (0 or 1):
~~~~~

## Sample 59 · reveal · B1-H2 · seed 42

ID: `reveal:validation:743`  
Prompt SHA-256: `29c2d1ee53ed64d180b1ae4b344fda7e7edc8bac4c6ff78068ed0cd2c2f6c7b6`  
Stratum: `no_usable_evidence`

~~~~~text
You are now an excellent programmer. You are conducting a function vulnerability detection task for C/C++ language.

static inline void qemu_get_8s ( QEMUFile * f , uint8_t * pv ) {
 * pv = qemu_get_byte ( f ) ;
 }

In the above code snippet, check for potential security vulnerabilities and answer with a single digit: 1 if Vulnerable, 0 if Non-vulnerable.

The guarded evidence of the code snippet is as follows:
GUARDED EVIDENCE: operation-specific observed relations; not a safety proof.
N1 METHOD_PARAMETER_IN "QEMUFile * f"
N2 METHOD_PARAMETER_IN "uint8_t * pv"
N3 CALL "* pv"
N4 CALL "qemu_get_byte ( f )"
N5 IDENTIFIER "pv"
N6 IDENTIFIER "f"
N1 --REACHING_DEF--> N6
N2 --REACHING_DEF--> N5
N3 --ARGUMENT--> N5
N4 --REACHING_DEF--> N3
N4 --ARGUMENT--> N6
N5 --REF--> N2
N6 --REF--> N1
N6 --REACHING_DEF--> N4
OP N3
  INPUTS N5
  DIRECT_CONTROL unknown: CDG unavailable
OP N4
  INPUTS N6
  DIRECT_CONTROL unknown: CDG unavailable
UNKNOWN: guard sufficiency, aliasing and feasible execution paths. Missing polarity is unknown.
BOUNDED: omitted operations/context and shortened snippets are not proof of absence.

The following is an example, and it is .


Answer (0 or 1):
~~~~~

## Sample 60 · reveal · B1-H2 · seed 42

ID: `reveal:validation:803`  
Prompt SHA-256: `f181a42a7e27bf81b48ab9a9de6b74bd78c58458ca84437571a8bb3dc4e24366`  
Stratum: `missing_cpg`

~~~~~text
You are now an excellent programmer. You are conducting a function vulnerability detection task for C/C++ language.

static ossl_inline sk_ ## t1 ## _compfunc sk_ ## t1 ## _set_cmp_func ( STACK_OF ( t1 ) * sk , sk_ ## t1 ## _compfunc compare ) {
 return ( sk_ ## t1 ## _compfunc ) OPENSSL_sk_set_cmp_func ( ( OPENSSL_STACK * ) sk , ( OPENSSL_sk_compfunc ) compare ) ;
 }
 # define DEFINE_SPECIAL_STACK_OF ( t1 , t2 ) SKM_DEFINE_STACK_OF ( t1 , t2 , t2 ) # define DEFINE_STACK_OF ( t ) SKM_DEFINE_STACK_OF ( t , t , t ) # define DEFINE_SPECIAL_STACK_OF_CONST ( t1 , t2 ) SKM_DEFINE_STACK_OF ( t1 , const t2 , t2 ) # define DEFINE_STACK_OF_CONST ( t ) SKM_DEFINE_STACK_OF ( t , const t , t ) typedef char * OPENSSL_STRING ;
 typedef const char * OPENSSL_CSTRING ;
 DEFINE_SPECIAL_STACK_OF ( OPENSSL_STRING , char ) DEFINE_SPECIAL_STACK_OF_CONST ( OPENSSL_CSTRING , char ) typedef void * OPENSSL_BLOCK ;
 DEFINE_SPECIAL_STACK_OF ( OPENSSL_BLOCK , void )

In the above code snippet, check for potential security vulnerabilities and answer with a single digit: 1 if Vulnerable, 0 if Non-vulnerable.

The node information of the code snippet is as follows:

The edge information of the code snippet is as follows:


The following is an example, and it is .


Answer (0 or 1):
~~~~~
