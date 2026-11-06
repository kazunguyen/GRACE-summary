# Manual review packet — B1-H2 v6

## Sample 01 · devign · B1-H2 · seed 42

ID: `devign:validation:11075`  
Prompt SHA-256: `80b1e415291a5a3ec15c814314250c42179ebdc08a8925c0333be4f87b607aa0`

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

ID: `devign:validation:1324`  
Prompt SHA-256: `13fd5a82e6885e15580ac48e80ece1ef4d9339aed517ec0a3c8bc1449b04f1f6`

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

## Sample 03 · devign · B1-H2 · seed 42

ID: `devign:validation:14587`  
Prompt SHA-256: `ad2aed04cfd60b5ac30737c949255ca88aa11033d244f137b7c66db233d52c27`

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

## Sample 04 · devign · B1-H2 · seed 42

ID: `devign:validation:14819`  
Prompt SHA-256: `8e7b151e26d78aa5fc4eb57b740d3e1f74e01e656967734a027b35c4986efa56`

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

The guarded evidence of the code snippet is as follows:
CPG_UNAVAILABLE: flagged Joern extraction error; no H2 graph evidence is available. Do not treat this as evidence that the code is safe.

The following is an example, and it is .


Answer (0 or 1):
~~~~~

## Sample 05 · devign · B1-H2 · seed 42

ID: `devign:validation:15296`  
Prompt SHA-256: `389617a49a6b42b593770df38e3f261528472f5a1e2dd659e43b0e25959ab1b7`

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

## Sample 06 · devign · B1-H2 · seed 42

ID: `devign:validation:16307`  
Prompt SHA-256: `9afa7a0afae3455f5cc48c3474549fcd658b28eca7be747358f6df953531c990`

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

The guarded evidence of the code snippet is as follows:
CPG_UNAVAILABLE: flagged Joern extraction error; no H2 graph evidence is available. Do not treat this as evidence that the code is safe.

The following is an example, and it is .


Answer (0 or 1):
~~~~~

## Sample 07 · devign · B1-H2 · seed 42

ID: `devign:validation:16709`  
Prompt SHA-256: `dc005516b83dfeb3e2f84099315ece34a1b4cdcab7c58e76e157223c1b56505c`

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

## Sample 08 · devign · B1-H2 · seed 42

ID: `devign:validation:17336`  
Prompt SHA-256: `af9b61d260e72403d0c411c2a3e29b9f5f5b2d1b916c512913af493e6f82cfc9`

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

## Sample 09 · devign · B1-H2 · seed 42

ID: `devign:validation:17398`  
Prompt SHA-256: `9cf7308cfab33bf29fbd16fefecbdb6debb69050abfb9674b3afb59908f64fb1`

~~~~~text
You are now an excellent programmer. You are conducting a function vulnerability detection task for C/C++ language.

DECLARE_LOOP_FILTER(mmxext)

DECLARE_LOOP_FILTER(sse2)

DECLARE_LOOP_FILTER(ssse3)

DECLARE_LOOP_FILTER(sse4)



#endif



#define VP8_LUMA_MC_FUNC(IDX, SIZE, OPT) \

    c->put_vp8_epel_pixels_tab[IDX][0][2] = ff_put_vp8_epel ## SIZE ## _h6_ ## OPT; \

    c->put_vp8_epel_pixels_tab[IDX][2][0] = ff_put_vp8_epel ## SIZE ## _v6_ ## OPT; \

    c->put_vp8_epel_pixels_tab[IDX][2][2] = ff_put_vp8_epel ## SIZE ## _h6v6_ ## OPT



#define VP8_MC_FUNC(IDX, SIZE, OPT) \

    c->put_vp8_epel_pixels_tab[IDX][0][1] = ff_put_vp8_epel ## SIZE ## _h4_ ## OPT; \

    c->put_vp8_epel_pixels_tab[IDX][1][0] = ff_put_vp8_epel ## SIZE ## _v4_ ## OPT; \

    c->put_vp8_epel_pixels_tab[IDX][1][1] = ff_put_vp8_epel ## SIZE ## _h4v4_ ## OPT; \

    c->put_vp8_epel_pixels_tab[IDX][1][2] = ff_put_vp8_epel ## SIZE ## _h6v4_ ## OPT; \

    c->put_vp8_epel_pixels_tab[IDX][2][1] = ff_put_vp8_epel ## SIZE ## _h4v6_ ## OPT; \

    VP8_LUMA_MC_FUNC(IDX, SIZE, OPT)



#define VP8_BILINEAR_MC_FUNC(IDX, SIZE, OPT) \

    c->put_vp8_bilinear_pixels_tab[IDX][0][1] = ff_put_vp8_bilinear ## SIZE ## _h_ ## OPT; \

    c->put_vp8_bilinear_pixels_tab[IDX][0][2] = ff_put_vp8_bilinear ## SIZE ## _h_ ## OPT; \

    c->put_vp8_bilinear_pixels_tab[IDX][1][0] = ff_put_vp8_bilinear ## SIZE ## _v_ ## OPT; \

    c->put_vp8_bilinear_pixels_tab[IDX][1][1] = ff_put_vp8_bilinear ## SIZE ## _hv_ ## OPT; \

    c->put_vp8_bilinear_pixels_tab[IDX][1][2] = ff_put_vp8_bilinear ## SIZE ## _hv_ ## OPT; \

    c->put_vp8_bilinear_pixels_tab[IDX][2][0] = ff_put_vp8_bilinear ## SIZE ## _v_ ## OPT; \

    c->put_vp8_bilinear_pixels_tab[IDX][2][1] = ff_put_vp8_bilinear ## SIZE ## _hv_ ## OPT; \

    c->put_vp8_bilinear_pixels_tab[IDX][2][2] = ff_put_vp8_bilinear ## SIZE ## _hv_ ## OPT





av_cold void ff_vp8dsp_init_x86(VP8DSPContext* c)

{

    mm_flags = mm_support();



#if HAVE_YASM

    if (mm_flags & FF_MM_MMX) {

        c->vp8_idct_dc_add    = ff_vp8_idct_dc_add_mmx;

        c->vp8_idct_dc_add4y  = ff_vp8_idct_dc_add4y_mmx;

        c->vp8_idct_dc_add4uv = ff_vp8_idct_dc_add4uv_mmx;

        c->vp8_idct_add       = ff_vp8_idct_add_mmx;

        c->vp8_luma_dc_wht    = ff_vp8_luma_dc_wht_mmx;

        c->put_vp8_epel_pixels_tab[0][0][0]     =

        c->put_vp8_bilinear_pixels_tab[0][0][0] = ff_put_vp8_pixels16_mmx;

        c->put_vp8_epel_pixels_tab[1][0][0]     =

        c->put_vp8_bilinear_pixels_tab[1][0][0] = ff_put_vp8_pixels8_mmx;



        c->vp8_v_loop_filter_simple = ff_vp8_v_loop_filter_simple_mmx;

        c->vp8_h_loop_filter_simple = ff_vp8_h_loop_filter_simple_mmx;



        c->vp8_v_loop_filter16y_inner = ff_vp8_v_loop_filter16y_inner_mmx;

        c->vp8_h_loop_filter16y_inner = ff_vp8_h_loop_filter16y_inner_mmx;

        c->vp8_v_loop_filter8uv_inner = ff_vp8_v_loop_filter8uv_inner_mmx;

        c->vp8_h_loop_filter8uv_inner = ff_vp8_h_loop_filter8uv_inner_mmx;



        c->vp8_v_loop_filter16y       = ff_vp8_v_loop_filter16y_mbedge_mmx;

        c->vp8_h_loop_filter16y       = ff_vp8_h_loop_filter16y_mbedge_mmx;

        c->vp8_v_loop_filter8uv       = ff_vp8_v_loop_filter8uv_mbedge_mmx;

        c->vp8_h_loop_filter8uv       = ff_vp8_h_loop_filter8uv_mbedge_mmx;

    }



    /* note that 4-tap width=16 functions are missing because w=16

     * is only used for luma, and luma is always a copy or sixtap. */

    if (mm_flags & FF_MM_MMX2) {

        VP8_LUMA_MC_FUNC(0, 16, mmxext);

        VP8_MC_FUNC(1, 8, mmxext);

        VP8_MC_FUNC(2, 4, mmxext);

        VP8_BILINEAR_MC_FUNC(0, 16, mmxext);

        VP8_BILINEAR_MC_FUNC(1, 8, mmxext);

        VP8_BILINEAR_MC_FUNC(2, 4, mmxext);



        c->vp8_v_loop_filter_simple = ff_vp8_v_loop_filter_simple_mmxext;

        c->vp8_h_loop_filter_simple = ff_vp8_h_loop_filter_simple_mmxext;



        c->vp8_v_loop_filter16y_inner = ff_vp8_v_loop_filter16y_inner_mmxext;

        c->vp8_h_loop_filter16y_inner = ff_vp8_h_loop_filter16y_inner_mmxext;

        c->vp8_v_loop_filter8uv_inner = ff_vp8_v_loop_filter8uv_inner_mmxext;

        c->vp8_h_loop_filter8uv_inner = ff_vp8_h_loop_filter8uv_inner_mmxext;



        c->vp8_v_loop_filter16y       = ff_vp8_v_loop_filter16y_mbedge_mmxext;

        c->vp8_h_loop_filter16y       = ff_vp8_h_loop_filter16y_mbedge_mmxext;

        c->vp8_v_loop_filter8uv       = ff_vp8_v_loop_filter8uv_mbedge_mmxext;

        c->vp8_h_loop_filter8uv       = ff_vp8_h_loop_filter8uv_mbedge_mmxext;

    }



    if (mm_flags & FF_MM_SSE) {

        c->vp8_idct_add                         = ff_vp8_idct_add_sse;

        c->put_vp8_epel_pixels_tab[0][0][0]     =

        c->put_vp8_bilinear_pixels_tab[0][0][0] = ff_put_vp8_pixels16_sse;

    }



    if (mm_flags & (FF_MM_SSE2|FF_MM_SSE2SLOW)) {

        VP8_LUMA_MC_FUNC(0, 16, sse2);

        VP8_MC_FUNC(1, 8, sse2);

        VP8_BILINEAR_MC_FUNC(0, 16, sse2);

        VP8_BILINEAR_MC_FUNC(1, 8, sse2);



        c->vp8_v_loop_filter_simple = ff_vp8_v_loop_filter_simple_sse2;

        c->vp8_h_loop_filter_simple = ff_vp8_h_loop_filter_simple_sse2;



        c->vp8_v_loop_filter16y_inner = ff_vp8_v_loop_filter16y_inner_sse2;

        c->vp8_v_loop_filter8uv_inner = ff_vp8_v_loop_filter8uv_inner_sse2;



        c->vp8_v_loop_filter16y       = ff_vp8_v_loop_filter16y_mbedge_sse2;

        c->vp8_v_loop_filter8uv       = ff_vp8_v_loop_filter8uv_mbedge_sse2;

    }



    if (mm_flags & FF_MM_SSE2) {

        c->vp8_idct_dc_add4y          = ff_vp8_idct_dc_add4y_sse2;



        c->vp8_h_loop_filter16y_inner = ff_vp8_h_loop_filter16y_inner_sse2;

        c->vp8_h_loop_filter8uv_inner = ff_vp8_h_loop_filter8uv_inner_sse2;



        c->vp8_h_loop_filter16y       = ff_vp8_h_loop_filter16y_mbedge_sse2;

        c->vp8_h_loop_filter8uv       = ff_vp8_h_loop_filter8uv_mbedge_sse2;

    }



    if (mm_flags & FF_MM_SSSE3) {

        VP8_LUMA_MC_FUNC(0, 16, ssse3);

        VP8_MC_FUNC(1, 8, ssse3);

        VP8_MC_FUNC(2, 4, ssse3);

        VP8_BILINEAR_MC_FUNC(0, 16, ssse3);

        VP8_BILINEAR_MC_FUNC(1, 8, ssse3);

        VP8_BILINEAR_MC_FUNC(2, 4, ssse3);



        c->vp8_v_loop_filter_simple = ff_vp8_v_loop_filter_simple_ssse3;

        c->vp8_h_loop_filter_simple = ff_vp8_h_loop_filter_simple_ssse3;



        c->vp8_v_loop_filter16y_inner = ff_vp8_v_loop_filter16y_inner_ssse3;

        c->vp8_h_loop_filter16y_inner = ff_vp8_h_loop_filter16y_inner_ssse3;

        c->vp8_v_loop_filter8uv_inner = ff_vp8_v_loop_filter8uv_inner_ssse3;

        c->vp8_h_loop_filter8uv_inner = ff_vp8_h_loop_filter8uv_inner_ssse3;



        c->vp8_v_loop_filter16y       = ff_vp8_v_loop_filter16y_mbedge_ssse3;

        c->vp8_h_loop_filter16y       = ff_vp8_h_loop_filter16y_mbedge_ssse3;

        c->vp8_v_loop_filter8uv       = ff_vp8_v_loop_filter8uv_mbedge_ssse3;

        c->vp8_h_loop_filter8uv       = ff_vp8_h_loop_filter8uv_mbedge_ssse3;

    }



    if (mm_flags & FF_MM_SSE4) {

        c->vp8_idct_dc_add                  = ff_vp8_idct_dc_add_sse4;



        c->vp8_h_loop_filter16y       = ff_vp8_h_loop_filter16y_mbedge_sse4;

        c->vp8_h_loop_filter8uv       = ff_vp8_h_loop_filter8uv_mbedge_sse4;

    }

#endif

}

In the above code snippet, check for potential security vulnerabilities and answer with a single digit: 1 if Vulnerable, 0 if Non-vulnerable.

The guarded evidence of the code snippet is as follows:
NO_USABLE_GUARDED_EVIDENCE: no_operation_nodes. Do not infer safety from missing evidence.

The following is an example, and it is .


Answer (0 or 1):
~~~~~

## Sample 10 · devign · B1-H2 · seed 42

ID: `devign:validation:18320`  
Prompt SHA-256: `7e3fb1a5ae543b21baae6129f7f16c10eab19d58dfea69da6b1c20563d652efb`

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

## Sample 11 · devign · B1-H2 · seed 42

ID: `devign:validation:1836`  
Prompt SHA-256: `a96a90de451a24b273c573a3983cfac409d6edc392b0a058f6b338eb5b343f10`

~~~~~text
You are now an excellent programmer. You are conducting a function vulnerability detection task for C/C++ language.

static int RENAME(swScale)(SwsContext *c, uint8_t* src[], int srcStride[], int srcSliceY,

                           int srcSliceH, uint8_t* dst[], int dstStride[])

{

    /* load a few things into local vars to make the code more readable? and faster */

    const int srcW= c->srcW;

    const int dstW= c->dstW;

    const int dstH= c->dstH;

    const int chrDstW= c->chrDstW;

    const int chrSrcW= c->chrSrcW;

    const int lumXInc= c->lumXInc;

    const int chrXInc= c->chrXInc;

    const enum PixelFormat dstFormat= c->dstFormat;

    const enum PixelFormat srcFormat= c->srcFormat;

    const int flags= c->flags;

    int16_t *vLumFilterPos= c->vLumFilterPos;

    int16_t *vChrFilterPos= c->vChrFilterPos;

    int16_t *hLumFilterPos= c->hLumFilterPos;

    int16_t *hChrFilterPos= c->hChrFilterPos;

    int16_t *vLumFilter= c->vLumFilter;

    int16_t *vChrFilter= c->vChrFilter;

    int16_t *hLumFilter= c->hLumFilter;

    int16_t *hChrFilter= c->hChrFilter;

    int32_t *lumMmxFilter= c->lumMmxFilter;

    int32_t *chrMmxFilter= c->chrMmxFilter;

    int32_t *alpMmxFilter= c->alpMmxFilter;

    const int vLumFilterSize= c->vLumFilterSize;

    const int vChrFilterSize= c->vChrFilterSize;

    const int hLumFilterSize= c->hLumFilterSize;

    const int hChrFilterSize= c->hChrFilterSize;

    int16_t **lumPixBuf= c->lumPixBuf;

    int16_t **chrPixBuf= c->chrPixBuf;

    int16_t **alpPixBuf= c->alpPixBuf;

    const int vLumBufSize= c->vLumBufSize;

    const int vChrBufSize= c->vChrBufSize;

    uint8_t *formatConvBuffer= c->formatConvBuffer;

    const int chrSrcSliceY= srcSliceY >> c->chrSrcVSubSample;

    const int chrSrcSliceH= -((-srcSliceH) >> c->chrSrcVSubSample);

    int lastDstY;

    uint32_t *pal=c->pal_yuv;



    /* vars which will change and which we need to store back in the context */

    int dstY= c->dstY;

    int lumBufIndex= c->lumBufIndex;

    int chrBufIndex= c->chrBufIndex;

    int lastInLumBuf= c->lastInLumBuf;

    int lastInChrBuf= c->lastInChrBuf;



    if (isPacked(c->srcFormat)) {

        src[0]=

        src[1]=

        src[2]=

        src[3]= src[0];

        srcStride[0]=

        srcStride[1]=

        srcStride[2]=

        srcStride[3]= srcStride[0];

    }

    srcStride[1]<<= c->vChrDrop;

    srcStride[2]<<= c->vChrDrop;



    DEBUG_BUFFERS("swScale() %p[%d] %p[%d] %p[%d] %p[%d] -> %p[%d] %p[%d] %p[%d] %p[%d]\n",

                  src[0], srcStride[0], src[1], srcStride[1], src[2], srcStride[2], src[3], srcStride[3],

                  dst[0], dstStride[0], dst[1], dstStride[1], dst[2], dstStride[2], dst[3], dstStride[3]);

    DEBUG_BUFFERS("srcSliceY: %d srcSliceH: %d dstY: %d dstH: %d\n",

                   srcSliceY,    srcSliceH,    dstY,    dstH);

    DEBUG_BUFFERS("vLumFilterSize: %d vLumBufSize: %d vChrFilterSize: %d vChrBufSize: %d\n",

                   vLumFilterSize,    vLumBufSize,    vChrFilterSize,    vChrBufSize);



    if (dstStride[0]%8 !=0 || dstStride[1]%8 !=0 || dstStride[2]%8 !=0 || dstStride[3]%8 != 0) {

        static int warnedAlready=0; //FIXME move this into the context perhaps

        if (flags & SWS_PRINT_INFO && !warnedAlready) {

            av_log(c, AV_LOG_WARNING, "Warning: dstStride is not aligned!\n"

                   "         ->cannot do aligned memory accesses anymore\n");

            warnedAlready=1;

        }

    }



    /* Note the user might start scaling the picture in the middle so this

       will not get executed. This is not really intended but works

       currently, so people might do it. */

    if (srcSliceY ==0) {

        lumBufIndex=0;

        chrBufIndex=0;

        dstY=0;

        lastInLumBuf= -1;

        lastInChrBuf= -1;

    }



    lastDstY= dstY;



    for (;dstY < dstH; dstY++) {

        unsigned char *dest =dst[0]+dstStride[0]*dstY;

        const int chrDstY= dstY>>c->chrDstVSubSample;

        unsigned char *uDest=dst[1]+dstStride[1]*chrDstY;

        unsigned char *vDest=dst[2]+dstStride[2]*chrDstY;

        unsigned char *aDest=(CONFIG_SWSCALE_ALPHA && alpPixBuf) ? dst[3]+dstStride[3]*dstY : NULL;



        const int firstLumSrcY= vLumFilterPos[dstY]; //First line needed as input

        const int firstChrSrcY= vChrFilterPos[chrDstY]; //First line needed as input

        int lastLumSrcY= firstLumSrcY + vLumFilterSize -1; // Last line needed as input

        int lastChrSrcY= firstChrSrcY + vChrFilterSize -1; // Last line needed as input

        int enough_lines;



        //handle holes (FAST_BILINEAR & weird filters)

        if (firstLumSrcY > lastInLumBuf) lastInLumBuf= firstLumSrcY-1;

        if (firstChrSrcY > lastInChrBuf) lastInChrBuf= firstChrSrcY-1;

        assert(firstLumSrcY >= lastInLumBuf - vLumBufSize + 1);

        assert(firstChrSrcY >= lastInChrBuf - vChrBufSize + 1);



        // Do we have enough lines in this slice to output the dstY line

        enough_lines = lastLumSrcY < srcSliceY + srcSliceH && lastChrSrcY < -((-srcSliceY - srcSliceH)>>c->chrSrcVSubSample);

        if (!enough_lines) {

            lastLumSrcY = srcSliceY + srcSliceH - 1;

            lastChrSrcY = chrSrcSliceY + chrSrcSliceH - 1;

        }



        DEBUG_BUFFERS("dstY: %d\n", dstY);

        DEBUG_BUFFERS("\tfirstLumSrcY: %d lastLumSrcY: %d lastInLumBuf: %d\n",

                         firstLumSrcY,    lastLumSrcY,    lastInLumBuf);

        DEBUG_BUFFERS("\tfirstChrSrcY: %d lastChrSrcY: %d lastInChrBuf: %d\n",

                         firstChrSrcY,    lastChrSrcY,    lastInChrBuf);



        //Do horizontal scaling

        while(lastInLumBuf < lastLumSrcY) {

            uint8_t *src1= src[0]+(lastInLumBuf + 1 - srcSliceY)*srcStride[0];

            uint8_t *src2= src[3]+(lastInLumBuf + 1 - srcSliceY)*srcStride[3];

            lumBufIndex++;

            DEBUG_BUFFERS("\t\tlumBufIndex %d: lastInLumBuf: %d\n",

                               lumBufIndex,    lastInLumBuf);

            assert(lumBufIndex < 2*vLumBufSize);

            assert(lastInLumBuf + 1 - srcSliceY < srcSliceH);

            assert(lastInLumBuf + 1 - srcSliceY >= 0);

            RENAME(hyscale)(c, lumPixBuf[ lumBufIndex ], dstW, src1, srcW, lumXInc,

                            flags, hLumFilter, hLumFilterPos, hLumFilterSize,

                            c->srcFormat, formatConvBuffer,

                            pal, 0);

            if (CONFIG_SWSCALE_ALPHA && alpPixBuf)

                RENAME(hyscale)(c, alpPixBuf[ lumBufIndex ], dstW, src2, srcW, lumXInc,

                                flags, hLumFilter, hLumFilterPos, hLumFilterSize,

                                c->srcFormat, formatConvBuffer,

                                pal, 1);

            lastInLumBuf++;

        }

        while(lastInChrBuf < lastChrSrcY) {

            uint8_t *src1= src[1]+(lastInChrBuf + 1 - chrSrcSliceY)*srcStride[1];

            uint8_t *src2= src[2]+(lastInChrBuf + 1 - chrSrcSliceY)*srcStride[2];

            chrBufIndex++;

            DEBUG_BUFFERS("\t\tchrBufIndex %d: lastInChrBuf: %d\n",

                               chrBufIndex,    lastInChrBuf);

            assert(chrBufIndex < 2*vChrBufSize);

            assert(lastInChrBuf + 1 - chrSrcSliceY < (chrSrcSliceH));

            assert(lastInChrBuf + 1 - chrSrcSliceY >= 0);

            //FIXME replace parameters through context struct (some at least)



            if (!(isGray(srcFormat) || isGray(dstFormat)))

                RENAME(hcscale)(c, chrPixBuf[ chrBufIndex ], chrDstW, src1, src2, chrSrcW, chrXInc,

                                flags, hChrFilter, hChrFilterPos, hChrFilterSize,

                                c->srcFormat, formatConvBuffer,

                                pal);

            lastInChrBuf++;

        }

        //wrap buf index around to stay inside the ring buffer

        if (lumBufIndex >= vLumBufSize) lumBufIndex-= vLumBufSize;

        if (chrBufIndex >= vChrBufSize) chrBufIndex-= vChrBufSize;

        if (!enough_lines)

            break; //we can't output a dstY line so let's try with the next slice



#if COMPILE_TEMPLATE_MMX

        c->blueDither= ff_dither8[dstY&1];

        if (c->dstFormat == PIX_FMT_RGB555 || c->dstFormat == PIX_FMT_BGR555)

            c->greenDither= ff_dither8[dstY&1];

        else

            c->greenDither= ff_dither4[dstY&1];

        c->redDither= ff_dither8[(dstY+1)&1];

#endif

        if (dstY < dstH-2) {

            const int16_t **lumSrcPtr= (const int16_t **) lumPixBuf + lumBufIndex + firstLumSrcY - lastInLumBuf + vLumBufSize;

            const int16_t **chrSrcPtr= (const int16_t **) chrPixBuf + chrBufIndex + firstChrSrcY - lastInChrBuf + vChrBufSize;

            const int16_t **alpSrcPtr= (CONFIG_SWSCALE_ALPHA && alpPixBuf) ? (const int16_t **) alpPixBuf + lumBufIndex + firstLumSrcY - lastInLumBuf + vLumBufSize : NULL;

#if COMPILE_TEMPLATE_MMX

            int i;

            if (flags & SWS_ACCURATE_RND) {

                int s= APCK_SIZE / 8;

                for (i=0; i<vLumFilterSize; i+=2) {

                    *(void**)&lumMmxFilter[s*i              ]= lumSrcPtr[i  ];

                    *(void**)&lumMmxFilter[s*i+APCK_PTR2/4  ]= lumSrcPtr[i+(vLumFilterSize>1)];

                              lumMmxFilter[s*i+APCK_COEF/4  ]=

                              lumMmxFilter[s*i+APCK_COEF/4+1]= vLumFilter[dstY*vLumFilterSize + i    ]

                        + (vLumFilterSize>1 ? vLumFilter[dstY*vLumFilterSize + i + 1]<<16 : 0);

                    if (CONFIG_SWSCALE_ALPHA && alpPixBuf) {

                        *(void**)&alpMmxFilter[s*i              ]= alpSrcPtr[i  ];

                        *(void**)&alpMmxFilter[s*i
/* [TRUNCATED TARGET] */

In the above code snippet, check for potential security vulnerabilities and answer with a single digit: 1 if Vulnerable, 0 if Non-vulnerable.

The guarded evidence of the code snippet is as follows:
NO_USABLE_GUARDED_EVIDENCE: no_operation_nodes. Do not infer safety from missing evidence.

The following is an example, and it is .


Answer (0 or 1):
~~~~~

## Sample 12 · devign · B1-H2 · seed 42

ID: `devign:validation:19012`  
Prompt SHA-256: `c80d4aa9d1337cfc4d840bc48978b39e4c758126060bee8bd953ab609aabce7c`

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

ID: `devign:validation:2091`  
Prompt SHA-256: `2f105d19fd6654b0179eef02b96e54b8f85157d002070d933101128f52f5b631`

~~~~~text
You are now an excellent programmer. You are conducting a function vulnerability detection task for C/C++ language.

void avcodec_register_all(void)

{

    static int initialized;



    if (initialized)

        return;

    initialized = 1;



    /* hardware accelerators */

    REGISTER_HWACCEL(H263_VAAPI,        h263_vaapi);

    REGISTER_HWACCEL(H264_D3D11VA,      h264_d3d11va);

    REGISTER_HWACCEL(H264_DXVA2,        h264_dxva2);

    REGISTER_HWACCEL(H264_MMAL,         h264_mmal);

    REGISTER_HWACCEL(H264_QSV,          h264_qsv);

    REGISTER_HWACCEL(H264_VAAPI,        h264_vaapi);

    REGISTER_HWACCEL(H264_VDA,          h264_vda);

    REGISTER_HWACCEL(H264_VDA_OLD,      h264_vda_old);

    REGISTER_HWACCEL(H264_VDPAU,        h264_vdpau);

    REGISTER_HWACCEL(HEVC_D3D11VA,      hevc_d3d11va);

    REGISTER_HWACCEL(HEVC_DXVA2,        hevc_dxva2);

    REGISTER_HWACCEL(HEVC_QSV,          hevc_qsv);

    REGISTER_HWACCEL(HEVC_VAAPI,        hevc_vaapi);

    REGISTER_HWACCEL(HEVC_VDPAU,        hevc_vdpau);

    REGISTER_HWACCEL(MPEG1_VDPAU,       mpeg1_vdpau);

    REGISTER_HWACCEL(MPEG2_D3D11VA,     mpeg2_d3d11va);

    REGISTER_HWACCEL(MPEG2_DXVA2,       mpeg2_dxva2);

    REGISTER_HWACCEL(MPEG2_MMAL,        mpeg2_mmal);

    REGISTER_HWACCEL(MPEG2_QSV,         mpeg2_qsv);

    REGISTER_HWACCEL(MPEG2_VAAPI,       mpeg2_vaapi);

    REGISTER_HWACCEL(MPEG2_VDPAU,       mpeg2_vdpau);

    REGISTER_HWACCEL(MPEG4_VAAPI,       mpeg4_vaapi);

    REGISTER_HWACCEL(MPEG4_VDPAU,       mpeg4_vdpau);

    REGISTER_HWACCEL(VC1_D3D11VA,       vc1_d3d11va);

    REGISTER_HWACCEL(VC1_DXVA2,         vc1_dxva2);

    REGISTER_HWACCEL(VC1_QSV,           vc1_qsv);

    REGISTER_HWACCEL(VC1_VAAPI,         vc1_vaapi);

    REGISTER_HWACCEL(VC1_VDPAU,         vc1_vdpau);

    REGISTER_HWACCEL(VC1_MMAL,          vc1_mmal);

    REGISTER_HWACCEL(VP8_QSV,           vp8_qsv);

    REGISTER_HWACCEL(VP8_VAAPI,         vp8_vaapi);

    REGISTER_HWACCEL(WMV3_D3D11VA,      wmv3_d3d11va);

    REGISTER_HWACCEL(WMV3_DXVA2,        wmv3_dxva2);

    REGISTER_HWACCEL(WMV3_VAAPI,        wmv3_vaapi);

    REGISTER_HWACCEL(WMV3_VDPAU,        wmv3_vdpau);



    /* video codecs */

    REGISTER_ENCODER(A64MULTI,          a64multi);

    REGISTER_ENCODER(A64MULTI5,         a64multi5);

    REGISTER_DECODER(AASC,              aasc);

    REGISTER_DECODER(AIC,               aic);

    REGISTER_ENCDEC (ALIAS_PIX,         alias_pix);

    REGISTER_DECODER(AMV,               amv);

    REGISTER_DECODER(ANM,               anm);

    REGISTER_DECODER(ANSI,              ansi);

    REGISTER_ENCDEC (ASV1,              asv1);

    REGISTER_ENCDEC (ASV2,              asv2);

    REGISTER_DECODER(AURA,              aura);

    REGISTER_DECODER(AURA2,             aura2);

    REGISTER_DECODER(AVS,               avs);

    REGISTER_DECODER(BETHSOFTVID,       bethsoftvid);

    REGISTER_DECODER(BFI,               bfi);

    REGISTER_DECODER(BINK,              bink);

    REGISTER_ENCDEC (BMP,               bmp);

    REGISTER_DECODER(BMV_VIDEO,         bmv_video);

    REGISTER_DECODER(BRENDER_PIX,       brender_pix);

    REGISTER_DECODER(C93,               c93);

    REGISTER_DECODER(CAVS,              cavs);

    REGISTER_DECODER(CDGRAPHICS,        cdgraphics);

    REGISTER_DECODER(CDXL,              cdxl);

    REGISTER_DECODER(CFHD,              cfhd);

    REGISTER_DECODER(CINEPAK,           cinepak);

    REGISTER_ENCDEC (CLJR,              cljr);

    REGISTER_DECODER(CLLC,              cllc);

    REGISTER_ENCDEC (COMFORTNOISE,      comfortnoise);

    REGISTER_DECODER(CSCD,              cscd);

    REGISTER_DECODER(CYUV,              cyuv);

    REGISTER_DECODER(DDS,               dds);

    REGISTER_DECODER(DFA,               dfa);

    REGISTER_ENCDEC (DNXHD,             dnxhd);

    REGISTER_ENCDEC (DPX,               dpx);

    REGISTER_DECODER(DSICINVIDEO,       dsicinvideo);

    REGISTER_ENCDEC (DVVIDEO,           dvvideo);

    REGISTER_DECODER(DXA,               dxa);

    REGISTER_DECODER(DXTORY,            dxtory);

    REGISTER_DECODER(DXV,               dxv);

    REGISTER_DECODER(EACMV,             eacmv);

    REGISTER_DECODER(EAMAD,             eamad);

    REGISTER_DECODER(EATGQ,             eatgq);

    REGISTER_DECODER(EATGV,             eatgv);

    REGISTER_DECODER(EATQI,             eatqi);

    REGISTER_DECODER(EIGHTBPS,          eightbps);

    REGISTER_DECODER(EIGHTSVX_EXP,      eightsvx_exp);

    REGISTER_DECODER(EIGHTSVX_FIB,      eightsvx_fib);

    REGISTER_DECODER(ESCAPE124,         escape124);

    REGISTER_DECODER(ESCAPE130,         escape130);

    REGISTER_DECODER(EXR,               exr);

    REGISTER_ENCDEC (FFV1,              ffv1);

    REGISTER_ENCDEC (FFVHUFF,           ffvhuff);

    REGISTER_DECODER(FIC,               fic);

    REGISTER_ENCDEC (FLASHSV,           flashsv);

    REGISTER_DECODER(FLASHSV2,          flashsv2);

    REGISTER_DECODER(FLIC,              flic);

    REGISTER_ENCDEC (FLV,               flv);

    REGISTER_DECODER(FOURXM,            fourxm);

    REGISTER_DECODER(FRAPS,             fraps);

    REGISTER_DECODER(FRWU,              frwu);

    REGISTER_DECODER(G2M,               g2m);

    REGISTER_ENCDEC (GIF,               gif);

    REGISTER_ENCDEC (H261,              h261);

    REGISTER_ENCDEC (H263,              h263);

    REGISTER_DECODER(H263I,             h263i);

    REGISTER_ENCODER(H263P,             h263p);

    REGISTER_DECODER(H264,              h264);

    REGISTER_DECODER(H264_MMAL,         h264_mmal);

    REGISTER_DECODER(H264_QSV,          h264_qsv);

    REGISTER_ENCDEC (HAP,               hap);

    REGISTER_DECODER(HEVC,              hevc);

    REGISTER_DECODER(HEVC_QSV,          hevc_qsv);

    REGISTER_DECODER(HNM4_VIDEO,        hnm4_video);

    REGISTER_DECODER(HQ_HQA,            hq_hqa);

    REGISTER_DECODER(HQX,               hqx);

    REGISTER_ENCDEC (HUFFYUV,           huffyuv);

    REGISTER_DECODER(IDCIN,             idcin);

    REGISTER_DECODER(IFF_BYTERUN1,      iff_byterun1);

    REGISTER_DECODER(IFF_ILBM,          iff_ilbm);

    REGISTER_DECODER(INDEO2,            indeo2);

    REGISTER_DECODER(INDEO3,            indeo3);

    REGISTER_DECODER(INDEO4,            indeo4);

    REGISTER_DECODER(INDEO5,            indeo5);

    REGISTER_DECODER(INTERPLAY_VIDEO,   interplay_video);

    REGISTER_DECODER(JPEG2000,          jpeg2000);

    REGISTER_ENCDEC (JPEGLS,            jpegls);

    REGISTER_DECODER(JV,                jv);

    REGISTER_DECODER(KGV1,              kgv1);

    REGISTER_DECODER(KMVC,              kmvc);

    REGISTER_DECODER(LAGARITH,          lagarith);

    REGISTER_ENCODER(LJPEG,             ljpeg);

    REGISTER_DECODER(LOCO,              loco);

    REGISTER_DECODER(MAGICYUV,          magicyuv);

    REGISTER_DECODER(MDEC,              mdec);

    REGISTER_DECODER(MIMIC,             mimic);

    REGISTER_ENCDEC (MJPEG,             mjpeg);

    REGISTER_DECODER(MJPEGB,            mjpegb);

    REGISTER_DECODER(MMVIDEO,           mmvideo);

    REGISTER_DECODER(MOTIONPIXELS,      motionpixels);

#if FF_API_XVMC

    REGISTER_DECODER(MPEG_XVMC,         mpeg_xvmc);

#endif /* FF_API_XVMC */

    REGISTER_ENCDEC (MPEG1VIDEO,        mpeg1video);

    REGISTER_ENCDEC (MPEG2VIDEO,        mpeg2video);

    REGISTER_DECODER(MPEG2_MMAL,        mpeg2_mmal);

    REGISTER_DECODER(MPEG2_QSV,         mpeg2_qsv);

    REGISTER_ENCDEC (MPEG4,             mpeg4);

    REGISTER_DECODER(MSA1,              msa1);

    REGISTER_DECODER(MSMPEG4V1,         msmpeg4v1);

    REGISTER_ENCDEC (MSMPEG4V2,         msmpeg4v2);

    REGISTER_ENCDEC (MSMPEG4V3,         msmpeg4v3);

    REGISTER_DECODER(MSRLE,             msrle);

    REGISTER_DECODER(MSS1,              mss1);

    REGISTER_DECODER(MSS2,              mss2);

    REGISTER_DECODER(MSVIDEO1,          msvideo1);

    REGISTER_DECODER(MSZH,              mszh);

    REGISTER_DECODER(MTS2,              mts2);

    REGISTER_DECODER(MVC1,              mvc1);

    REGISTER_DECODER(MVC2,              mvc2);

    REGISTER_DECODER(MXPEG,             mxpeg);

    REGISTER_DECODER(NUV,               nuv);

    REGISTER_DECODER(PAF_VIDEO,         paf_video);

    REGISTER_ENCDEC (PAM,               pam);

    REGISTER_ENCDEC (PBM,               pbm);

    REGISTER_ENCDEC (PCX,               pcx);

    REGISTER_ENCDEC (PGM,               pgm);

    REGISTER_ENCDEC (PGMYUV,            pgmyuv);

    REGISTER_DECODER(PICTOR,            pictor);

    REGISTER_DECODER(PIXLET,            pixlet);

    REGISTER_ENCDEC (PNG,               png);

    REGISTER_ENCDEC (PPM,               ppm);

    REGISTER_ENCDEC (PRORES,            prores);

    REGISTER_DECODER(PTX,               ptx);

    REGISTER_DECODER(QDRAW,             qdraw);

    REGISTER_DECODER(QPEG,              qpeg);

    REGISTER_ENCDEC (QTRLE,             qtrle);

    REGISTER_DECODER(R10K,              r10k);

    REGISTER_DECODER(R210,              r210);

    REGISTER_ENCDEC (RAWVIDEO,          rawvideo);

    REGISTER_DECODER(RL2,               rl2);

    REGISTER_ENCDEC (ROQ,               roq);

    REGISTER_DECODER(RPZA,              rpza);

    REGISTER_DECODER(RSCC,              rscc);

    REGISTER_ENCDEC (RV10,              rv10);

    REGISTER_ENCDEC (RV20,              rv20);

    REGISTER_DECODER(RV30,              rv30);

    REGISTER_DECODER(RV40,              rv40);

    REGISTER_DECODER(S302M,             s302m);

    REGISTER_DECODER(SANM,              sanm);

    REGISTER_DECODER(SCREENPRESSO,      screenpresso);

    REGISTER_ENCDEC (SGI,               sgi);

    REGISTER_DECODER(SGIRLE,            sgirle);

    REGISTER_DECODER(SMACKER,           smacker);

    REGISTER_DECODER(SMC,               smc);

    REGISTER_DECODER(SP5X,              sp5x);

    REGISTER_ENCDEC (SUNRAST,           sunrast);

    REGISTER_ENCDEC (SVQ1,              svq1);

    REGISTER_DECODER(SVQ3,              svq3);

    REGISTER_ENCDEC (TARGA,             targa);

    REGISTER_DECODER(TDSC,
/* [TRUNCATED TARGET] */

In the above code snippet, check for potential security vulnerabilities and answer with a single digit: 1 if Vulnerable, 0 if Non-vulnerable.

The guarded evidence of the code snippet is as follows:
GUARDED EVIDENCE: operation-specific observed relations; not a safety proof.
N1 CALL "initialized != 0"
N2 CALL "REGISTER_HWACCEL(H263_VAAPI, h263_vaapi)"
N3 CALL "REGISTER_HWACCEL(H264_D3D11VA, h264_d3d11va)"
N4 CALL "REGISTER_HWACCEL(H264_DXVA2, h264_dxva2)"
N5 CALL "REGISTER_HWACCEL(H264_MMAL, h264_mmal)"
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

## Sample 18 · devign · B1-H2 · seed 42

ID: `devign:validation:21124`  
Prompt SHA-256: `e7d3f107e6d97087fc8e5e5652b20cdf99451d5c115aaf2660d7821c5366f1c6`

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

## Sample 19 · devign · B1-H2 · seed 42

ID: `devign:validation:21280`  
Prompt SHA-256: `8ac84723d98e61498e7b47a033dcdcfb7c43f32c5de829492e15f09991d3d5a4`

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

## Sample 20 · devign · B1-H2 · seed 42

ID: `devign:validation:24935`  
Prompt SHA-256: `047c9ddae934b1455447988a8dd5406921b50384acaad139e98a423c68e3f4c6`

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

## Sample 21 · devign · B1-H2 · seed 42

ID: `devign:validation:25232`  
Prompt SHA-256: `2dad73ceaded26e83d02159debeaeb463f28691a9cac82dc865bccb471d9862a`

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

## Sample 22 · devign · B1-H2 · seed 42

ID: `devign:validation:25726`  
Prompt SHA-256: `2ba8b639dbcb9b4b7e07e82cd15ebef3964f5d46c684a9d12a498d2dfa4db0b7`

~~~~~text
You are now an excellent programmer. You are conducting a function vulnerability detection task for C/C++ language.

static void spapr_phb_realize(DeviceState *dev, Error **errp)

{

    sPAPRMachineState *spapr = SPAPR_MACHINE(qdev_get_machine());

    SysBusDevice *s = SYS_BUS_DEVICE(dev);

    sPAPRPHBState *sphb = SPAPR_PCI_HOST_BRIDGE(s);

    PCIHostState *phb = PCI_HOST_BRIDGE(s);

    sPAPRPHBClass *info = SPAPR_PCI_HOST_BRIDGE_GET_CLASS(s);

    char *namebuf;

    int i;

    PCIBus *bus;

    uint64_t msi_window_size = 4096;



    if (sphb->index != (uint32_t)-1) {

        hwaddr windows_base;



        if ((sphb->buid != (uint64_t)-1) || (sphb->dma_liobn != (uint32_t)-1)

            || (sphb->mem_win_addr != (hwaddr)-1)

            || (sphb->io_win_addr != (hwaddr)-1)) {

            error_setg(errp, "Either \"index\" or other parameters must"

                       " be specified for PAPR PHB, not both");

            return;

        }



        if (sphb->index > SPAPR_PCI_MAX_INDEX) {

            error_setg(errp, "\"index\" for PAPR PHB is too large (max %u)",

                       SPAPR_PCI_MAX_INDEX);

            return;

        }



        sphb->buid = SPAPR_PCI_BASE_BUID + sphb->index;

        sphb->dma_liobn = SPAPR_PCI_LIOBN(sphb->index, 0);



        windows_base = SPAPR_PCI_WINDOW_BASE

            + sphb->index * SPAPR_PCI_WINDOW_SPACING;

        sphb->mem_win_addr = windows_base + SPAPR_PCI_MMIO_WIN_OFF;

        sphb->io_win_addr = windows_base + SPAPR_PCI_IO_WIN_OFF;

    }



    if (sphb->buid == (uint64_t)-1) {

        error_setg(errp, "BUID not specified for PHB");

        return;

    }



    if (sphb->dma_liobn == (uint32_t)-1) {

        error_setg(errp, "LIOBN not specified for PHB");

        return;

    }



    if (sphb->mem_win_addr == (hwaddr)-1) {

        error_setg(errp, "Memory window address not specified for PHB");

        return;

    }



    if (sphb->io_win_addr == (hwaddr)-1) {

        error_setg(errp, "IO window address not specified for PHB");

        return;

    }



    if (spapr_pci_find_phb(spapr, sphb->buid)) {

        error_setg(errp, "PCI host bridges must have unique BUIDs");

        return;

    }



    sphb->dtbusname = g_strdup_printf("pci@%" PRIx64, sphb->buid);



    namebuf = alloca(strlen(sphb->dtbusname) + 32);



    /* Initialize memory regions */

    sprintf(namebuf, "%s.mmio", sphb->dtbusname);

    memory_region_init(&sphb->memspace, OBJECT(sphb), namebuf, UINT64_MAX);



    sprintf(namebuf, "%s.mmio-alias", sphb->dtbusname);

    memory_region_init_alias(&sphb->memwindow, OBJECT(sphb),

                             namebuf, &sphb->memspace,

                             SPAPR_PCI_MEM_WIN_BUS_OFFSET, sphb->mem_win_size);

    memory_region_add_subregion(get_system_memory(), sphb->mem_win_addr,

                                &sphb->memwindow);



    /* Initialize IO regions */

    sprintf(namebuf, "%s.io", sphb->dtbusname);

    memory_region_init(&sphb->iospace, OBJECT(sphb),

                       namebuf, SPAPR_PCI_IO_WIN_SIZE);



    sprintf(namebuf, "%s.io-alias", sphb->dtbusname);

    memory_region_init_alias(&sphb->iowindow, OBJECT(sphb), namebuf,

                             &sphb->iospace, 0, SPAPR_PCI_IO_WIN_SIZE);

    memory_region_add_subregion(get_system_memory(), sphb->io_win_addr,

                                &sphb->iowindow);



    bus = pci_register_bus(dev, NULL,

                           pci_spapr_set_irq, pci_spapr_map_irq, sphb,

                           &sphb->memspace, &sphb->iospace,

                           PCI_DEVFN(0, 0), PCI_NUM_PINS, TYPE_PCI_BUS);

    phb->bus = bus;

    qbus_set_hotplug_handler(BUS(phb->bus), DEVICE(sphb), NULL);



    /*

     * Initialize PHB address space.

     * By default there will be at least one subregion for default

     * 32bit DMA window.

     * Later the guest might want to create another DMA window

     * which will become another memory subregion.

     */

    sprintf(namebuf, "%s.iommu-root", sphb->dtbusname);



    memory_region_init(&sphb->iommu_root, OBJECT(sphb),

                       namebuf, UINT64_MAX);

    address_space_init(&sphb->iommu_as, &sphb->iommu_root,

                       sphb->dtbusname);



    /*

     * As MSI/MSIX interrupts trigger by writing at MSI/MSIX vectors,

     * we need to allocate some memory to catch those writes coming

     * from msi_notify()/msix_notify().

     * As MSIMessage:addr is going to be the same and MSIMessage:data

     * is going to be a VIRQ number, 4 bytes of the MSI MR will only

     * be used.

     *

     * For KVM we want to ensure that this memory is a full page so that

     * our memory slot is of page size granularity.

     */

#ifdef CONFIG_KVM

    if (kvm_enabled()) {

        msi_window_size = getpagesize();

    }

#endif



    memory_region_init_io(&sphb->msiwindow, NULL, &spapr_msi_ops, spapr,

                          "msi", msi_window_size);

    memory_region_add_subregion(&sphb->iommu_root, SPAPR_PCI_MSI_WINDOW,

                                &sphb->msiwindow);



    pci_setup_iommu(bus, spapr_pci_dma_iommu, sphb);



    pci_bus_set_route_irq_fn(bus, spapr_route_intx_pin_to_irq);



    QLIST_INSERT_HEAD(&spapr->phbs, sphb, list);



    /* Initialize the LSI table */

    for (i = 0; i < PCI_NUM_PINS; i++) {

        uint32_t irq;



        irq = xics_alloc_block(spapr->icp, 0, 1, true, false);

        if (!irq) {

            error_setg(errp, "spapr_allocate_lsi failed");

            return;

        }



        sphb->lsi_table[i].irq = irq;

    }



    /* allocate connectors for child PCI devices */

    if (sphb->dr_enabled) {

        for (i = 0; i < PCI_SLOT_MAX * 8; i++) {

            spapr_dr_connector_new(OBJECT(phb),

                                   SPAPR_DR_CONNECTOR_TYPE_PCI,

                                   (sphb->index << 16) | i);

        }

    }



    if (!info->finish_realize) {

        error_setg(errp, "finish_realize not defined");

        return;

    }



    info->finish_realize(sphb, errp);



    sphb->msi = g_hash_table_new_full(g_int_hash, g_int_equal, g_free, g_free);

}

In the above code snippet, check for potential security vulnerabilities and answer with a single digit: 1 if Vulnerable, 0 if Non-vulnerable.

The guarded evidence of the code snippet is as follows:
GUARDED EVIDENCE: operation-specific observed relations; not a safety proof.
N1 CALL "sphb->index != (uint32_t)-1"
N2 CALL "sphb->index"
N3 CALL "(uint32_t)-1"
N4 CALL "(sphb->buid != (uint64_t)-1) || (sphb->dma_liobn != (uint32_t)-1)"
N5 CALL "sphb->buid"
N6 CALL "(uint64_t)-1"
N7 CALL "sphb->mem_win_addr"
N1 --CDG--> N5
N1 --CDG--> N6
N2 --REACHING_DEF--> N3
N3 --REACHING_DEF--> N2
N4 --CDG--> N7
OP N5
  INPUTS not included/unknown
  DIRECT_CONTROL N1 via=CDG branch=unknown check=cdg_observed_cfg_unknown
OP N7
  INPUTS not included/unknown
  DIRECT_CONTROL N4 via=CDG branch=unknown check=cdg_observed_cfg_unknown
OP N6
  INPUTS not included/unknown
  DIRECT_CONTROL N1 via=CDG branch=unknown check=cdg_observed_cfg_unknown
OP N2
  INPUTS not included/unknown
  DIRECT_CONTROL none observed; not proof of absence
UNKNOWN: guard sufficiency, aliasing and feasible execution paths. Missing polarity is unknown.
BOUNDED: omitted operations/context and shortened snippets are not proof of absence.

The following is an example, and it is .


Answer (0 or 1):
~~~~~

## Sample 23 · devign · B1-H2 · seed 42

ID: `devign:validation:27036`  
Prompt SHA-256: `1683633aa2788c0db10a663cdcd09f964ef79f875b2b2ace6a710f875cbb1b2d`

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

## Sample 24 · devign · B1-H2 · seed 42

ID: `devign:validation:4239`  
Prompt SHA-256: `d1dfb8127bc3f8e83deff5a461fa706e8e1a9120f3e3b5452672bfaf8c992d0e`

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

## Sample 25 · devign · B1-H2 · seed 42

ID: `devign:validation:6401`  
Prompt SHA-256: `fbbc02e7a5628c7a8658d59956d407e048cff12611eb271dcdcfa0a0663335a8`

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
Prompt SHA-256: `8e01968ce468dd9a78c9256235484d6746fac4922f1c7a1d71963b2fa0ea4930`

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

The guarded evidence of the code snippet is as follows:
CPG_UNAVAILABLE: flagged Joern extraction error; no H2 graph evidence is available. Do not treat this as evidence that the code is safe.

The following is an example, and it is .


Answer (0 or 1):
~~~~~

## Sample 29 · devign · B1-H2 · seed 42

ID: `devign:validation:7231`  
Prompt SHA-256: `b123ae9d4c0ac10a01cc98f665035af7b8c02f6d321d6cc072fb07336436f530`

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

ID: `reveal:validation:1023`  
Prompt SHA-256: `99dfc1a50862362ffd716cf7f6dc477e179c2c9c2b227db52112650c5662befe`

~~~~~text
You are now an excellent programmer. You are conducting a function vulnerability detection task for C/C++ language.

int phar_tar_flush ( phar_archive_data * phar , char * user_stub , long len , int defaultstub , char * * error TSRMLS_DC ) {
 phar_entry_info entry = {
 0 }
 ;
 static const char newstub [ ] = "<?php // tar-based phar archive stub file\n__HALT_COMPILER();
" ;
 php_stream * oldfile , * newfile , * stubfile ;
 int closeoldfile , free_user_stub , signature_length ;
 struct _phar_pass_tar_info pass ;
 char * buf , * signature , * tmp , sigbuf [ 8 ] ;
 char halt_stub [ ] = "__HALT_COMPILER();
" ;
 entry . flags = PHAR_ENT_PERM_DEF_FILE ;
 entry . timestamp = time ( NULL ) ;
 entry . is_modified = 1 ;
 entry . is_crc_checked = 1 ;
 entry . is_tar = 1 ;
 entry . tar_type = '0' ;
 entry . phar = phar ;
 entry . fp_type = PHAR_MOD ;
 if ( phar -> is_persistent ) {
 if ( error ) {
 spprintf ( error , 0 , "internal error: attempt to flush cached tar-based phar \"%s\"" , phar -> fname ) ;
 }
 return EOF ;
 }
 if ( phar -> is_data ) {
 goto nostub ;
 }
 if ( ! phar -> is_temporary_alias && phar -> alias_len ) {
 entry . filename = estrndup ( ".phar/alias.txt" , sizeof ( ".phar/alias.txt" ) - 1 ) ;
 entry . filename_len = sizeof ( ".phar/alias.txt" ) - 1 ;
 entry . fp = php_stream_fopen_tmpfile ( ) ;
 if ( entry . fp == NULL ) {
 spprintf ( error , 0 , "phar error: unable to create temporary file" ) ;
 return - 1 ;
 }
 if ( phar -> alias_len != ( int ) php_stream_write ( entry . fp , phar -> alias , phar -> alias_len ) ) {
 if ( error ) {
 spprintf ( error , 0 , "unable to set alias in tar-based phar \"%s\"" , phar -> fname ) ;
 }
 return EOF ;
 }
 entry . uncompressed_filesize = phar -> alias_len ;
 if ( SUCCESS != zend_hash_update ( & phar -> manifest , entry . filename , entry . filename_len , ( void * ) & entry , sizeof ( phar_entry_info ) , NULL ) ) {
 if ( error ) {
 spprintf ( error , 0 , "unable to set alias in tar-based phar \"%s\"" , phar -> fname ) ;
 }
 return EOF ;
 }
 }
 else {
 zend_hash_del ( & phar -> manifest , ".phar/alias.txt" , sizeof ( ".phar/alias.txt" ) - 1 ) ;
 }
 if ( user_stub && ! defaultstub ) {
 char * pos ;
 if ( len < 0 ) {
 if ( ! ( php_stream_from_zval_no_verify ( stubfile , ( zval * * ) user_stub ) ) ) {
 if ( error ) {
 spprintf ( error , 0 , "unable to access resource to copy stub to new tar-based phar \"%s\"" , phar -> fname ) ;
 }
 return EOF ;
 }
 if ( len == - 1 ) {
 len = PHP_STREAM_COPY_ALL ;
 }
 else {
 len = - len ;
 }
 user_stub = 0 ;
 if ( ! ( len = php_stream_copy_to_mem ( stubfile , & user_stub , len , 0 ) ) || ! user_stub ) {
 if ( error ) {
 spprintf ( error , 0 , "unable to read resource to copy stub to new tar-based phar \"%s\"" , phar -> fname ) ;
 }
 return EOF ;
 }
 free_user_stub = 1 ;
 }
 else {
 free_user_stub = 0 ;
 }
 tmp = estrndup ( user_stub , len ) ;
 if ( ( pos = php_stristr ( tmp , halt_stub , len , sizeof ( halt_stub ) - 1 ) ) == NULL ) {
 efree ( tmp ) ;
 if ( error ) {
 spprintf ( error , 0 , "illegal stub for tar-based phar \"%s\"" , phar -> fname ) ;
 }
 if ( free_user_stub ) {
 efree ( user_stub ) ;
 }
 return EOF ;
 }
 pos = user_stub + ( pos - tmp ) ;
 efree ( tmp ) ;
 len = pos - user_stub + 18 ;
 entry . fp = php_stream_fopen_tmpfile ( ) ;
 if ( entry . fp == NULL ) {
 spprintf ( error , 0 , "phar error: unable to create temporary file" ) ;
 return EOF ;
 }
 entry . uncompressed_filesize = len + 5 ;
 if ( ( size_t ) len != php_stream_write ( entry . fp , user_stub , len ) || 5 != php_stream_write ( entry . fp , " ?>\r\n" , 5 ) ) {
 if ( error ) {
 spprintf ( error , 0 , "unable to create stub from string in new tar-based phar \"%s\"" , phar -> fname ) ;
 }
 if ( free_user_stub ) {
 efree ( user_stub ) ;
 }
 php_stream_close ( entry . fp ) ;
 return EOF ;
 }
 entry . filename = estrndup ( ".phar/stub.php" , sizeof ( ".phar/stub.php" ) - 1 ) ;
 entry . filename_len = sizeof ( ".phar/stub.php" ) - 1 ;
 zend_hash_update ( & phar -> manifest , entry . filename , entry . filename_len , ( void * ) & entry , sizeof ( phar_entry_info ) , NULL ) ;
 if ( free_user_stub ) {
 efree ( user_stub ) ;
 }
 }
 else {
 entry . fp = php_stream_fopen_tmpfile ( ) ;
 if ( entry . fp == NULL ) {
 spprintf ( error , 0 , "phar error: unable to create temporary file" ) ;
 return EOF ;
 }
 if ( sizeof ( newstub ) - 1 != php_stream_write ( entry . fp , newstub , sizeof ( newstub ) - 1 ) ) {
 php_stream_close ( entry . fp ) ;
 if ( error ) {
 spprintf ( error , 0 , "unable to %s stub in%star-based phar \"%s\", failed" , user_stub ? "overwrite" : "create" , user_stub ? " " : " new " , phar -> fname ) ;
 }
 return EOF ;
 }
 entry . uncompressed_filesize = entry . compressed_filesize = sizeof ( newstub ) - 1 ;
 entry . filename = estrndup ( ".phar/stub.php" , sizeof ( ".phar/stub.php" ) - 1 ) ;
 entry . filename_len = sizeof ( ".phar/stub.php" ) - 1 ;
 if ( ! defaultstub ) {
 if ( ! zend_hash_exists ( & phar -> manifest , ".phar/stub.php" , sizeof ( ".phar/stub.php" ) - 1 ) ) {
 if ( SUCCESS != zend_hash_add ( & phar -> manifest , entry . filename , entry . filename_len , ( void * ) & entry , sizeof ( phar_entry_info ) , NULL ) ) {
 php_stream_close ( entry . fp ) ;
 efree ( entry . filename ) ;
 if ( error ) {
 spprintf ( error , 0 , "unable to create stub in tar-based phar \"%s\"" , phar -> fname ) ;
 }
 return EOF ;
 }
 }
 else {
 php_stream_close ( entry . fp ) ;
 efree ( entry . filename ) ;
 }
 }
 else {
 if ( SUCCESS != zend_hash_update ( & phar -> manifest , entry . filename , entry . filename_len , ( void * ) & entry , sizeof ( phar_entry_info ) , NULL ) ) {
 php_stream_close ( entry . fp ) ;
 efree ( entry . filename ) ;
 if ( error ) {
 spprintf ( error , 0 , "unable to overwrite stub in tar-based phar \"%s\"" , phar -> fname ) ;
 }
 return EOF ;
 }
 }
 }
 nostub : if ( phar -> fp && ! phar -> is_brandnew ) {
 oldfile = phar -> fp ;
 closeoldfile = 0 ;
 php_stream_rewind ( oldfile ) ;
 }
 else {
 oldfile = php_stream_open_wrapper ( phar -> fname , "rb" , 0 , NULL ) ;
 closeoldfile = oldfile != NULL ;
 }
 newfile = php_stream_fopen_tmpfile ( ) ;
 if ( ! newfile ) {
 if ( error ) {
 spprintf ( error , 0 , "unable to create temporary file" ) ;
 }
 if ( closeoldfile ) {
 php_stream_close ( oldfile ) ;
 }
 return EOF ;
 }
 pass . old = oldfile ;
 pass . new = newfile ;
 pass . error = error ;
 pass . free_fp = 1 ;
 pass . free_ufp = 1 ;
 if ( phar -> metadata ) {
 phar_entry_info * mentry ;
 if ( SUCCESS == zend_hash_find ( & ( phar -> manifest ) , ".phar/.metadata.bin" , sizeof ( ".phar/.metadata.bin" ) - 1 , ( void * * ) & mentry ) ) {
 if ( ZEND_HASH_APPLY_KEEP != phar_tar_setmetadata ( phar -> metadata , mentry , error TSRMLS_CC ) ) {
 if ( closeoldfile ) {
 php_stream_close ( oldfile ) ;
 }
 return EOF ;
 }
 }
 else {
 phar_entry_info newentry = {
 0 }
 ;
 newentry . filename = estrndup ( ".phar/.metadata.bin" , sizeof ( ".phar/.metadata.bin" ) - 1 ) ;
 newentry . filename_len = sizeof ( ".phar/.metadata.bin" ) - 1 ;
 newentry . phar = phar ;
 newentry . tar_type = TAR_FILE ;
 newentry . is_tar = 1 ;
 if ( SUCCESS != zend_hash_add ( & ( phar -> manifest ) , ".phar/.metadata.bin" , sizeof ( ".phar/.metadata.bin" ) - 1 , ( void * ) & newentry , sizeof ( phar_entry_info ) , ( void * * ) & mentry ) ) {
 spprintf ( error , 0 , "phar tar error: unable to add magic metadata file to manifest for phar archive \"%s\"" , phar -> fname ) ;
 if ( closeoldfile ) {
 php_stream_close ( oldfile ) ;
 }
 return EOF ;
 }
 if ( ZEND_HASH_APPLY_KEEP != phar_tar_setmetadata ( phar -> metadata , mentry , error TSRMLS_CC ) ) {
 zend_hash_del ( & ( phar -> manifest ) , ".phar/.metadata.bin" , sizeof ( ".phar/.metadata.bin" ) - 1 ) ;
 if ( closeoldfile ) {
 php_stream_close ( oldfile ) ;
 }
 return EOF ;
 }
 }
 }
 zend_hash_apply_with_argument ( & phar -> manifest , ( apply_func_arg_t ) phar_tar_setupmetadata , ( void * ) & pass TSRMLS_CC ) ;
 if ( error && * error ) {
 if ( closeoldfile ) {
 php_stream_close ( oldfile ) ;
 }
 php_stream_close ( newfile ) ;
 return EOF ;
 }
 zend_hash_apply_with_argument ( & phar -> manifest , ( apply_func_arg_t ) phar_tar_writeheaders , ( void * ) & pass TSRMLS_CC ) ;
 if ( ! phar -> is_data || phar -> sig_flags ) {
 if ( FAILURE == phar_create_signature ( phar , newfile , & signature , & signature_length , error TSRMLS_CC ) ) {
 if ( error ) {
 char * save = * error ;
 spprintf ( error , 0 , "phar error: unable to write signature to tar-based phar: %s" , save ) ;
 efree ( save ) ;
 }
 if ( closeoldfile ) {
 php_stream_close ( oldfile ) ;
 }
 php_stream_close ( newfile ) ;
 return EOF ;
 }
 entry . filename = ".phar/signature.bin" ;
 entry . filename_len = sizeof ( ".phar/signature.bin" ) - 1 ;
 entry . fp = php_stream_fopen_tmpfile ( ) ;
 if ( entry . fp == NULL ) {
 spprintf ( error , 0 , "phar error: unable to create temporary file" ) ;
 return EOF ;
 }
 # ifdef WORDS_BIGENDIAN # define PHAR_SET_32 ( var , buffer ) \ * ( php_uint32 * ) ( var ) = ( ( ( ( ( unsigned char * ) & ( buffer ) ) [ 3 ] ) << 24 ) \ | ( ( ( ( unsigned char * ) & ( buffer ) ) [ 2 ] ) << 16 ) \ | ( ( ( ( unsigned char * ) & ( buffer ) ) [ 1 ] ) << 8 ) \ | ( ( ( unsigned char * ) & ( buffer ) ) [ 0 ] ) ) # else # define PHAR_SET_32 ( var , buffer ) * ( php_uint32 * ) ( var ) = ( php_uint32 ) ( buffer ) # endif PHAR_SET_32 ( sigbuf , phar -> sig_flags ) ;
 PHAR_SET_32 ( sigbuf + 4 , signature_length ) ;
 if ( 8 != ( int ) php_stream_write ( entry . fp , sigbuf , 8 ) || signature_length != ( int ) php_stream_write ( entry . fp , signature , signature_length ) ) {
 efree ( signature ) ;
 if ( error ) {
 spprintf ( error , 0 , "phar error: unable to write signature to tar-based phar %s" , phar -> fname ) ;
 }
 if ( closeoldfile ) {
 php_stream_close ( oldfile ) ;
 }
 php_stream_close ( newfile ) ;
 return EOF ;
 }
 efree ( signature ) ;
 entry . uncompressed_filesize = entry . compressed_filesize = signature_length + 8 ;
 entry . filename_len = phar_tar_writeheaders ( ( void * ) & entry , ( void * ) & pass TSRMLS_CC ) ;
 if ( error && * error ) {
 if ( closeoldfile ) {
 php_stream_close ( oldfile ) ;
 }
/* [TRUNCATED TARGET] */

In the above code snippet, check for potential security vulnerabilities and answer with a single digit: 1 if Vulnerable, 0 if Non-vulnerable.

The guarded evidence of the code snippet is as follows:
GUARDED EVIDENCE: operation-specific observed relations; not a safety proof.
N1 CALL "phar -> is_persistent"
N2 CALL "error != NULL"
N3 CALL "phar -> fname"
N4 CALL "phar -> is_data"
N5 CALL "phar -> is_temporary_alias"
N6 CALL "\n        ( size_t ) len != php_stream_write ( entry . fp , user_stub , len ) || 5 != php_stream_write ( entry . fp , \" ?>\\r\\n\" , 5 )\n      "
N7 CALL "\n        ! zend_hash_exists ( & phar -> manifest , \".phar/stub.php\" , sizeof ( \".phar/stub.php\" ) - 1 )\n      "
N8 CALL "\n        SUCCESS != zend_hash_add ( & phar -> manifest , entry . filename , entry . filename_len , ( void * ) & entry , sizeof ( phar_entry_info ) , NULL )\n      "
N9 CALL "phar -> fp"
N10 FIELD_IDENTIFIER "fname"
N11 IDENTIFIER "phar"
N12 IDENTIFIER "phar"
N1 --CDG--> N4
N2 --CDG--> N3
N3 --ARGUMENT--> N10
N3 --ARGUMENT--> N11
N4 --CDG--> N5
N4 --CDG--> N9
N4 --ARGUMENT--> N12
N6 --CDG--> N9
N7 --CDG--> N9
N8 --CDG--> N9
OP N3
  INPUTS N10,N11
  DIRECT_CONTROL N2 via=CDG branch=unknown check=cdg_observed_cfg_unknown
  DATA_NOTE: predicates on related data are not operation controls.
OP N4
  INPUTS N12
  DIRECT_CONTROL N1 via=CDG branch=unknown check=cdg_observed_cfg_unknown
  DATA_NOTE: predicates on related data are not operation controls.
OP N5
  INPUTS not included/unknown
  DIRECT_CONTROL N4 via=CDG branch=unknown check=cdg_observed_cfg_unknown
OP N9
  INPUTS not included/unknown
  DIRECT_CONTROL N4 via=CDG branch=unknown check=cdg_observed_cfg_unknown
  DIRECT_CONTROL N6 via=CDG branch=unknown check=cdg_observed_cfg_unknown
  DIRECT_CONTROL N7 via=CDG branch=unknown check=cdg_observed_cfg_unknown
  DIRECT_CONTROL N8 via=CDG branch=unknown check=cdg_observed_cfg_unknown
UNKNOWN: guard sufficiency, aliasing and feasible execution paths. Missing polarity is unknown.
BOUNDED: omitted operations/context and shortened snippets are not proof of absence.

The following is an example, and it is .


Answer (0 or 1):
~~~~~

## Sample 32 · reveal · B1-H2 · seed 42

ID: `reveal:validation:1024`  
Prompt SHA-256: `d8fea65b57ac7bb467fc73f527fa961bae1730f69fdf7bcb121765b2f7c31fe3`

~~~~~text
You are now an excellent programmer. You are conducting a function vulnerability detection task for C/C++ language.

void vp9_ ## type ## _predictor_ ## size ## x ## size ## _c ( uint8_t * dst , ptrdiff_t stride , const uint8_t * above , const uint8_t * left ) {
 type ## _predictor ( dst , stride , size , above , left ) ;
 }
 # define intra_pred_allsizes ( type ) intra_pred_sized ( type , 4 ) intra_pred_sized ( type , 8 ) intra_pred_sized ( type , 16 ) intra_pred_sized ( type , 32 ) static INLINE void d207_predictor ( uint8_t * dst , ptrdiff_t stride , int bs , const uint8_t * above , const uint8_t * left ) {
 int r , c ;
 ( void ) above ;
 for ( r = 0 ;
 r < bs - 1 ;
 ++ r ) dst [ r * stride ] = ROUND_POWER_OF_TWO ( left [ r ] + left [ r + 1 ] , 1 ) ;
 dst [ ( bs - 1 ) * stride ] = left [ bs - 1 ] ;
 dst ++ ;
 for ( r = 0 ;
 r < bs - 2 ;
 ++ r ) dst [ r * stride ] = ROUND_POWER_OF_TWO ( left [ r ] + left [ r + 1 ] * 2 + left [ r + 2 ] , 2 ) ;
 dst [ ( bs - 2 ) * stride ] = ROUND_POWER_OF_TWO ( left [ bs - 2 ] + left [ bs - 1 ] * 3 , 2 ) ;
 dst [ ( bs - 1 ) * stride ] = left [ bs - 1 ] ;
 dst ++ ;
 for ( c = 0 ;
 c < bs - 2 ;
 ++ c ) dst [ ( bs - 1 ) * stride + c ] = left [ bs - 1 ] ;
 for ( r = bs - 2 ;
 r >= 0 ;
 -- r ) for ( c = 0 ;
 c < bs - 2 ;
 ++ c ) dst [ r * stride + c ] = dst [ ( r + 1 ) * stride + c - 2 ] ;
 }
 intra_pred_allsizes ( d207 ) static INLINE void d63_predictor ( uint8_t * dst , ptrdiff_t stride , int bs , const uint8_t * above , const uint8_t * left ) {
 int r , c ;
 ( void ) left ;
 for ( r = 0 ;
 r < bs ;
 ++ r ) {
 for ( c = 0 ;
 c < bs ;
 ++ c ) dst [ c ] = r & 1 ? ROUND_POWER_OF_TWO ( above [ r / 2 + c ] + above [ r / 2 + c + 1 ] * 2 + above [ r / 2 + c + 2 ] , 2 ) : ROUND_POWER_OF_TWO ( above [ r / 2 + c ] + above [ r / 2 + c + 1 ] , 1 ) ;
 dst += stride ;
 }
 }
 intra_pred_allsizes ( d63 ) static INLINE void d45_predictor ( uint8_t * dst , ptrdiff_t stride , int bs , const uint8_t * above , const uint8_t * left ) {
 int r , c ;
 ( void ) left ;
 for ( r = 0 ;
 r < bs ;
 ++ r ) {
 for ( c = 0 ;
 c < bs ;
 ++ c ) dst [ c ] = r + c + 2 < bs * 2 ? ROUND_POWER_OF_TWO ( above [ r + c ] + above [ r + c + 1 ] * 2 + above [ r + c + 2 ] , 2 ) : above [ bs * 2 - 1 ] ;
 dst += stride ;
 }
 }
 intra_pred_allsizes ( d45 ) static INLINE void d117_predictor ( uint8_t * dst , ptrdiff_t stride , int bs , const uint8_t * above , const uint8_t * left ) {
 int r , c ;
 for ( c = 0 ;
 c < bs ;
 c ++ ) dst [ c ] = ROUND_POWER_OF_TWO ( above [ c - 1 ] + above [ c ] , 1 ) ;
 dst += stride ;
 dst [ 0 ] = ROUND_POWER_OF_TWO ( left [ 0 ] + above [ - 1 ] * 2 + above [ 0 ] , 2 ) ;
 for ( c = 1 ;
 c < bs ;
 c ++ ) dst [ c ] = ROUND_POWER_OF_TWO ( above [ c - 2 ] + above [ c - 1 ] * 2 + above [ c ] , 2 ) ;
 dst += stride ;
 dst [ 0 ] = ROUND_POWER_OF_TWO ( above [ - 1 ] + left [ 0 ] * 2 + left [ 1 ] , 2 ) ;
 for ( r = 3 ;
 r < bs ;
 ++ r ) dst [ ( r - 2 ) * stride ] = ROUND_POWER_OF_TWO ( left [ r - 3 ] + left [ r - 2 ] * 2 + left [ r - 1 ] , 2 ) ;
 for ( r = 2 ;
 r < bs ;
 ++ r ) {
 for ( c = 1 ;
 c < bs ;
 c ++ ) dst [ c ] = dst [ - 2 * stride + c - 1 ] ;
 dst += stride ;
 }
 }
 intra_pred_allsizes ( d117 ) static INLINE void d135_predictor ( uint8_t * dst , ptrdiff_t stride , int bs , const uint8_t * above , const uint8_t * left ) {
 int r , c ;
 dst [ 0 ] = ROUND_POWER_OF_TWO ( left [ 0 ] + above [ - 1 ] * 2 + above [ 0 ] , 2 ) ;
 for ( c = 1 ;
 c < bs ;
 c ++ ) dst [ c ] = ROUND_POWER_OF_TWO ( above [ c - 2 ] + above [ c - 1 ] * 2 + above [ c ] , 2 ) ;
 dst [ stride ] = ROUND_POWER_OF_TWO ( above [ - 1 ] + left [ 0 ] * 2 + left [ 1 ] , 2 ) ;
 for ( r = 2 ;
 r < bs ;
 ++ r ) dst [ r * stride ] = ROUND_POWER_OF_TWO ( left [ r - 2 ] + left [ r - 1 ] * 2 + left [ r ] , 2 ) ;
 dst += stride ;
 for ( r = 1 ;
 r < bs ;
 ++ r ) {
 for ( c = 1 ;
 c < bs ;
 c ++ ) dst [ c ] = dst [ - stride + c - 1 ] ;
 dst += stride ;
 }
 }
 intra_pred_allsizes ( d135 ) static INLINE void d153_predictor ( uint8_t * dst , ptrdiff_t stride , int bs , const uint8_t * above , const uint8_t * left ) {
 int r , c ;
 dst [ 0 ] = ROUND_POWER_OF_TWO ( above [ - 1 ] + left [ 0 ] , 1 ) ;
 for ( r = 1 ;
 r < bs ;
 r ++ ) dst [ r * stride ] = ROUND_POWER_OF_TWO ( left [ r - 1 ] + left [ r ] , 1 ) ;
 dst ++ ;
 dst [ 0 ] = ROUND_POWER_OF_TWO ( left [ 0 ] + above [ - 1 ] * 2 + above [ 0 ] , 2 ) ;
 dst [ stride ] = ROUND_POWER_OF_TWO ( above [ - 1 ] + left [ 0 ] * 2 + left [ 1 ] , 2 ) ;
 for ( r = 2 ;
 r < bs ;
 r ++ ) dst [ r * stride ] = ROUND_POWER_OF_TWO ( left [ r - 2 ] + left [ r - 1 ] * 2 + left [ r ] , 2 ) ;
 dst ++ ;
 for ( c = 0 ;
 c < bs - 2 ;
 c ++ ) dst [ c ] = ROUND_POWER_OF_TWO ( above [ c - 1 ] + above [ c ] * 2 + above [ c + 1 ] , 2 ) ;
 dst += stride ;
 for ( r = 1 ;
 r < bs ;
 ++ r ) {
 for ( c = 0 ;
 c < bs - 2 ;
 c ++ ) dst [ c ] = dst [ - stride + c - 2 ] ;
 dst += stride ;
 }
 }
 intra_pred_allsizes ( d153 ) static INLINE void v_predictor ( uint8_t * dst , ptrdiff_t stride , int bs , const uint8_t * above , const uint8_t * left ) {
 int r ;
 ( void ) left ;
 for ( r = 0 ;
 r < bs ;
 r ++ ) {
 vpx_memcpy ( dst , above , bs ) ;
 dst += stride ;
 }
 }
 intra_pred_allsizes ( v ) static INLINE void h_predictor ( uint8_t * dst , ptrdiff_t stride , int bs , const uint8_t * above , const uint8_t * left ) {
 int r ;
 ( void ) above ;
 for ( r = 0 ;
 r < bs ;
 r ++ ) {
 vpx_memset ( dst , left [ r ] , bs ) ;
 dst += stride ;
 }
 }
 intra_pred_allsizes ( h ) static INLINE void tm_predictor ( uint8_t * dst , ptrdiff_t stride , int bs , const uint8_t * above , const uint8_t * left ) {
 int r , c ;
 int ytop_left = above [ - 1 ] ;
 for ( r = 0 ;
 r < bs ;
 r ++ ) {
 for ( c = 0 ;
 c < bs ;
 c ++ ) dst [ c ] = clip_pixel ( left [ r ] + above [ c ] - ytop_left ) ;
 dst += stride ;
 }
 }
 intra_pred_allsizes ( tm ) static INLINE void dc_128_predictor ( uint8_t * dst , ptrdiff_t stride , int bs , const uint8_t * above , const uint8_t * left ) {
 int r ;
 ( void ) above ;
 ( void ) left ;
 for ( r = 0 ;
 r < bs ;
 r ++ ) {
 vpx_memset ( dst , 128 , bs ) ;
 dst += stride ;
 }
 }
 intra_pred_allsizes ( dc_128 ) static INLINE void dc_left_predictor ( uint8_t * dst , ptrdiff_t stride , int bs , const uint8_t * above , const uint8_t * left ) {
 int i , r , expected_dc , sum = 0 ;
 ( void ) above ;
 for ( i = 0 ;
 i < bs ;
 i ++ ) sum += left [ i ] ;
 expected_dc = ( sum + ( bs >> 1 ) ) / bs ;
 for ( r = 0 ;
 r < bs ;
 r ++ ) {
 vpx_memset ( dst , expected_dc , bs ) ;
 dst += stride ;
 }
 }
 intra_pred_allsizes ( dc_left ) static INLINE void dc_top_predictor ( uint8_t * dst , ptrdiff_t stride , int bs , const uint8_t * above , const uint8_t * left ) {
 int i , r , expected_dc , sum = 0 ;
 ( void ) left ;
 for ( i = 0 ;
 i < bs ;
 i ++ ) sum += above [ i ] ;
 expected_dc = ( sum + ( bs >> 1 ) ) / bs ;
 for ( r = 0 ;
 r < bs ;
 r ++ ) {
 vpx_memset ( dst , expected_dc , bs ) ;
 dst += stride ;
 }
 }
 intra_pred_allsizes ( dc_top )

In the above code snippet, check for potential security vulnerabilities and answer with a single digit: 1 if Vulnerable, 0 if Non-vulnerable.

The guarded evidence of the code snippet is as follows:
CPG_UNAVAILABLE: flagged Joern extraction error; no H2 graph evidence is available. Do not treat this as evidence that the code is safe.

The following is an example, and it is .


Answer (0 or 1):
~~~~~

## Sample 33 · reveal · B1-H2 · seed 42

ID: `reveal:validation:1044`  
Prompt SHA-256: `01a98f36c78492eeb31ce83c2fc7de77ed8ab0bb8af1bf819c398cc5929bdcfa`

~~~~~text
You are now an excellent programmer. You are conducting a function vulnerability detection task for C/C++ language.

php_stream * php_stream_url_wrap_http_ex ( php_stream_wrapper * wrapper , const char * path , const char * mode , int options , char * * opened_path , php_stream_context * context , int redirect_max , int flags STREAMS_DC TSRMLS_DC ) {
 php_stream * stream = NULL ;
 php_url * resource = NULL ;
 int use_ssl ;
 int use_proxy = 0 ;
 char * scratch = NULL ;
 char * tmp = NULL ;
 char * ua_str = NULL ;
 zval * * ua_zval = NULL , * * tmpzval = NULL , * ssl_proxy_peer_name = NULL ;
 int scratch_len = 0 ;
 int body = 0 ;
 char location [ HTTP_HEADER_BLOCK_SIZE ] ;
 zval * response_header = NULL ;
 int reqok = 0 ;
 char * http_header_line = NULL ;
 char tmp_line [ 128 ] ;
 size_t chunk_size = 0 , file_size = 0 ;
 int eol_detect = 0 ;
 char * transport_string , * errstr = NULL ;
 int transport_len , have_header = 0 , request_fulluri = 0 , ignore_errors = 0 ;
 char * protocol_version = NULL ;
 int protocol_version_len = 3 ;
 struct timeval timeout ;
 char * user_headers = NULL ;
 int header_init = ( ( flags & HTTP_WRAPPER_HEADER_INIT ) != 0 ) ;
 int redirected = ( ( flags & HTTP_WRAPPER_REDIRECTED ) != 0 ) ;
 int follow_location = 1 ;
 php_stream_filter * transfer_encoding = NULL ;
 int response_code ;
 tmp_line [ 0 ] = '\0' ;
 if ( redirect_max < 1 ) {
 php_stream_wrapper_log_error ( wrapper , options TSRMLS_CC , "Redirection limit reached, aborting" ) ;
 return NULL ;
 }
 resource = php_url_parse ( path ) ;
 if ( resource == NULL ) {
 return NULL ;
 }
 if ( strncasecmp ( resource -> scheme , "http" , sizeof ( "http" ) ) && strncasecmp ( resource -> scheme , "https" , sizeof ( "https" ) ) ) {
 if ( ! context || php_stream_context_get_option ( context , wrapper -> wops -> label , "proxy" , & tmpzval ) == FAILURE || Z_TYPE_PP ( tmpzval ) != IS_STRING || Z_STRLEN_PP ( tmpzval ) <= 0 ) {
 php_url_free ( resource ) ;
 return php_stream_open_wrapper_ex ( path , mode , REPORT_ERRORS , NULL , context ) ;
 }
 request_fulluri = 1 ;
 use_ssl = 0 ;
 use_proxy = 1 ;
 transport_len = Z_STRLEN_PP ( tmpzval ) ;
 transport_string = estrndup ( Z_STRVAL_PP ( tmpzval ) , Z_STRLEN_PP ( tmpzval ) ) ;
 }
 else {
 if ( strpbrk ( mode , "awx+" ) ) {
 php_stream_wrapper_log_error ( wrapper , options TSRMLS_CC , "HTTP wrapper does not support writeable connections" ) ;
 php_url_free ( resource ) ;
 return NULL ;
 }
 use_ssl = resource -> scheme && ( strlen ( resource -> scheme ) > 4 ) && resource -> scheme [ 4 ] == 's' ;
 if ( use_ssl && resource -> port == 0 ) resource -> port = 443 ;
 else if ( resource -> port == 0 ) resource -> port = 80 ;
 if ( context && php_stream_context_get_option ( context , wrapper -> wops -> label , "proxy" , & tmpzval ) == SUCCESS && Z_TYPE_PP ( tmpzval ) == IS_STRING && Z_STRLEN_PP ( tmpzval ) > 0 ) {
 use_proxy = 1 ;
 transport_len = Z_STRLEN_PP ( tmpzval ) ;
 transport_string = estrndup ( Z_STRVAL_PP ( tmpzval ) , Z_STRLEN_PP ( tmpzval ) ) ;
 }
 else {
 transport_len = spprintf ( & transport_string , 0 , "%s://%s:%d" , use_ssl ? "ssl" : "tcp" , resource -> host , resource -> port ) ;
 }
 }
 if ( context && php_stream_context_get_option ( context , wrapper -> wops -> label , "timeout" , & tmpzval ) == SUCCESS ) {
 SEPARATE_ZVAL ( tmpzval ) ;
 convert_to_double_ex ( tmpzval ) ;
 timeout . tv_sec = ( time_t ) Z_DVAL_PP ( tmpzval ) ;
 timeout . tv_usec = ( size_t ) ( ( Z_DVAL_PP ( tmpzval ) - timeout . tv_sec ) * 1000000 ) ;
 }
 else {
 timeout . tv_sec = FG ( default_socket_timeout ) ;
 timeout . tv_usec = 0 ;
 }
 stream = php_stream_xport_create ( transport_string , transport_len , options , STREAM_XPORT_CLIENT | STREAM_XPORT_CONNECT , NULL , & timeout , context , & errstr , NULL ) ;
 if ( stream ) {
 php_stream_set_option ( stream , PHP_STREAM_OPTION_READ_TIMEOUT , 0 , & timeout ) ;
 }
 if ( errstr ) {
 php_stream_wrapper_log_error ( wrapper , options TSRMLS_CC , "%s" , errstr ) ;
 efree ( errstr ) ;
 errstr = NULL ;
 }
 efree ( transport_string ) ;
 if ( stream && use_proxy && use_ssl ) {
 smart_str header = {
 0 }
 ;
 if ( ! context || php_stream_context_get_option ( context , "ssl" , "peer_name" , & tmpzval ) == FAILURE ) {
 MAKE_STD_ZVAL ( ssl_proxy_peer_name ) ;
 ZVAL_STRING ( ssl_proxy_peer_name , resource -> host , 1 ) ;
 php_stream_context_set_option ( stream -> context , "ssl" , "peer_name" , ssl_proxy_peer_name ) ;
 }
 smart_str_appendl ( & header , "CONNECT " , sizeof ( "CONNECT " ) - 1 ) ;
 smart_str_appends ( & header , resource -> host ) ;
 smart_str_appendc ( & header , ':' ) ;
 smart_str_append_unsigned ( & header , resource -> port ) ;
 smart_str_appendl ( & header , " HTTP/1.0\r\n" , sizeof ( " HTTP/1.0\r\n" ) - 1 ) ;
 if ( context && php_stream_context_get_option ( context , "http" , "header" , & tmpzval ) == SUCCESS ) {
 char * s , * p ;
 if ( Z_TYPE_PP ( tmpzval ) == IS_ARRAY ) {
 HashPosition pos ;
 zval * * tmpheader = NULL ;
 for ( zend_hash_internal_pointer_reset_ex ( Z_ARRVAL_PP ( tmpzval ) , & pos ) ;
 SUCCESS == zend_hash_get_current_data_ex ( Z_ARRVAL_PP ( tmpzval ) , ( void * ) & tmpheader , & pos ) ;
 zend_hash_move_forward_ex ( Z_ARRVAL_PP ( tmpzval ) , & pos ) ) {
 if ( Z_TYPE_PP ( tmpheader ) == IS_STRING ) {
 s = Z_STRVAL_PP ( tmpheader ) ;
 do {
 while ( * s == ' ' || * s == '\t' ) s ++ ;
 p = s ;
 while ( * p != 0 && * p != ':' && * p != '\r' && * p != '\n' ) p ++ ;
 if ( * p == ':' ) {
 p ++ ;
 if ( p - s == sizeof ( "Proxy-Authorization:" ) - 1 && zend_binary_strcasecmp ( s , sizeof ( "Proxy-Authorization:" ) - 1 , "Proxy-Authorization:" , sizeof ( "Proxy-Authorization:" ) - 1 ) == 0 ) {
 while ( * p != 0 && * p != '\r' && * p != '\n' ) p ++ ;
 smart_str_appendl ( & header , s , p - s ) ;
 smart_str_appendl ( & header , "\r\n" , sizeof ( "\r\n" ) - 1 ) ;
 goto finish ;
 }
 else {
 while ( * p != 0 && * p != '\r' && * p != '\n' ) p ++ ;
 }
 }
 s = p ;
 while ( * s == '\r' || * s == '\n' ) s ++ ;
 }
 while ( * s != 0 ) ;
 }
 }
 }
 else if ( Z_TYPE_PP ( tmpzval ) == IS_STRING && Z_STRLEN_PP ( tmpzval ) ) {
 s = Z_STRVAL_PP ( tmpzval ) ;
 do {
 while ( * s == ' ' || * s == '\t' ) s ++ ;
 p = s ;
 while ( * p != 0 && * p != ':' && * p != '\r' && * p != '\n' ) p ++ ;
 if ( * p == ':' ) {
 p ++ ;
 if ( p - s == sizeof ( "Proxy-Authorization:" ) - 1 && zend_binary_strcasecmp ( s , sizeof ( "Proxy-Authorization:" ) - 1 , "Proxy-Authorization:" , sizeof ( "Proxy-Authorization:" ) - 1 ) == 0 ) {
 while ( * p != 0 && * p != '\r' && * p != '\n' ) p ++ ;
 smart_str_appendl ( & header , s , p - s ) ;
 smart_str_appendl ( & header , "\r\n" , sizeof ( "\r\n" ) - 1 ) ;
 goto finish ;
 }
 else {
 while ( * p != 0 && * p != '\r' && * p != '\n' ) p ++ ;
 }
 }
 s = p ;
 while ( * s == '\r' || * s == '\n' ) s ++ ;
 }
 while ( * s != 0 ) ;
 }
 }
 finish : smart_str_appendl ( & header , "\r\n" , sizeof ( "\r\n" ) - 1 ) ;
 if ( php_stream_write ( stream , header . c , header . len ) != header . len ) {
 php_stream_wrapper_log_error ( wrapper , options TSRMLS_CC , "Cannot connect to HTTPS server through proxy" ) ;
 php_stream_close ( stream ) ;
 stream = NULL ;
 }
 smart_str_free ( & header ) ;
 if ( stream ) {
 char header_line [ HTTP_HEADER_BLOCK_SIZE ] ;
 while ( php_stream_gets ( stream , header_line , HTTP_HEADER_BLOCK_SIZE - 1 ) != NULL ) {
 if ( header_line [ 0 ] == '\n' || header_line [ 0 ] == '\r' || header_line [ 0 ] == '\0' ) {
 break ;
 }
 }
 }
 if ( stream ) {
 if ( php_stream_xport_crypto_setup ( stream , STREAM_CRYPTO_METHOD_SSLv23_CLIENT , NULL TSRMLS_CC ) < 0 || php_stream_xport_crypto_enable ( stream , 1 TSRMLS_CC ) < 0 ) {
 php_stream_wrapper_log_error ( wrapper , options TSRMLS_CC , "Cannot connect to HTTPS server through proxy" ) ;
 php_stream_close ( stream ) ;
 stream = NULL ;
 }
 }
 }
 if ( stream == NULL ) goto out ;
 if ( options & STREAM_WILL_CAST ) chunk_size = php_stream_set_chunk_size ( stream , 1 ) ;
 eol_detect = stream -> flags & ( PHP_STREAM_FLAG_DETECT_EOL | PHP_STREAM_FLAG_EOL_MAC ) ;
 stream -> flags &= ~ ( PHP_STREAM_FLAG_DETECT_EOL | PHP_STREAM_FLAG_EOL_MAC ) ;
 php_stream_context_set ( stream , context ) ;
 php_stream_notify_info ( context , PHP_STREAM_NOTIFY_CONNECT , NULL , 0 ) ;
 if ( header_init && context && php_stream_context_get_option ( context , "http" , "max_redirects" , & tmpzval ) == SUCCESS ) {
 SEPARATE_ZVAL ( tmpzval ) ;
 convert_to_long_ex ( tmpzval ) ;
 redirect_max = Z_LVAL_PP ( tmpzval ) ;
 }
 if ( context && php_stream_context_get_option ( context , "http" , "method" , & tmpzval ) == SUCCESS ) {
 if ( Z_TYPE_PP ( tmpzval ) == IS_STRING && Z_STRLEN_PP ( tmpzval ) > 0 ) {
 if ( ! redirected || ( Z_STRLEN_PP ( tmpzval ) == 3 && memcmp ( "GET" , Z_STRVAL_PP ( tmpzval ) , 3 ) == 0 ) || ( Z_STRLEN_PP ( tmpzval ) == 4 && memcmp ( "HEAD" , Z_STRVAL_PP ( tmpzval ) , 4 ) == 0 ) ) {
 scratch_len = strlen ( path ) + 29 + Z_STRLEN_PP ( tmpzval ) ;
 scratch = emalloc ( scratch_len ) ;
 strlcpy ( scratch , Z_STRVAL_PP ( tmpzval ) , Z_STRLEN_PP ( tmpzval ) + 1 ) ;
 strncat ( scratch , " " , 1 ) ;
 }
 }
 }
 if ( context && php_stream_context_get_option ( context , "http" , "protocol_version" , & tmpzval ) == SUCCESS ) {
 SEPARATE_ZVAL ( tmpzval ) ;
 convert_to_double_ex ( tmpzval ) ;
 protocol_version_len = spprintf ( & protocol_version , 0 , "%.1F" , Z_DVAL_PP ( tmpzval ) ) ;
 }
 if ( ! scratch ) {
 scratch_len = strlen ( path ) + 29 + protocol_version_len ;
 scratch = emalloc ( scratch_len ) ;
 strncpy ( scratch , "GET " , scratch_len ) ;
 }
 if ( ! request_fulluri && context && php_stream_context_get_option ( context , "http" , "request_fulluri" , & tmpzval ) == SUCCESS ) {
 zval ztmp = * * tmpzval ;
 zval_copy_ctor ( & ztmp ) ;
 convert_to_boolean ( & ztmp ) ;
 request_fulluri = Z_BVAL ( ztmp ) ? 1 : 0 ;
 zval_dtor ( & ztmp ) ;
 }
 if ( request_fulluri ) {
 strcat ( scratch , path ) ;
 }
 else {
 if ( resource -> path && * resource -> path ) {
 strlcat ( scratch , resource -> path , scratch_len ) ;
 }
 else {
 strlcat ( scratch , "/" , scratch_len ) ;
 }
 if ( resource -> query ) {
 strlcat ( scratch , "?" , scratch_len ) ;
 strlcat ( scratch , resource -> query , scratch_len ) ;
 }
 }
 if ( protocol_version ) {
 str
/* [TRUNCATED TARGET] */

In the above code snippet, check for potential security vulnerabilities and answer with a single digit: 1 if Vulnerable, 0 if Non-vulnerable.

The guarded evidence of the code snippet is as follows:
CPG_UNAVAILABLE: flagged Joern extraction error; no H2 graph evidence is available. Do not treat this as evidence that the code is safe.

The following is an example, and it is .


Answer (0 or 1):
~~~~~

## Sample 34 · reveal · B1-H2 · seed 42

ID: `reveal:validation:108`  
Prompt SHA-256: `8b1db759fdedbdcd90d476f7225a9d68a4486407704ac3e0634d169c1f2183ae`

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

## Sample 35 · reveal · B1-H2 · seed 42

ID: `reveal:validation:1088`  
Prompt SHA-256: `d97f87ba09bedb243c380f11c7119cb102daa39b9670ae308ffb4c4029526764`

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

## Sample 36 · reveal · B1-H2 · seed 42

ID: `reveal:validation:1089`  
Prompt SHA-256: `40d14f25f86a679522b2fc87c4195fc650122998c7fb98cff28c0a7c335c9208`

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

## Sample 37 · reveal · B1-H2 · seed 42

ID: `reveal:validation:1210`  
Prompt SHA-256: `dcf7331709d33f73f31d7b3bb1a93d3a0f7e573f92fa1851c05779ab1836ccc5`

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

The guarded evidence of the code snippet is as follows:
CPG_UNAVAILABLE: flagged Joern extraction error; no H2 graph evidence is available. Do not treat this as evidence that the code is safe.

The following is an example, and it is .


Answer (0 or 1):
~~~~~

## Sample 38 · reveal · B1-H2 · seed 42

ID: `reveal:validation:1238`  
Prompt SHA-256: `a0bd089bc2bcc328e6539c4b4cf667b13dc85423b2139125087fd3f8a83bf8e1`

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

## Sample 39 · reveal · B1-H2 · seed 42

ID: `reveal:validation:1240`  
Prompt SHA-256: `5e9da448ada89cb9a3cf28130cddd642b7b5c98338d5609a151e7e7c76336ceb`

~~~~~text
You are now an excellent programmer. You are conducting a function vulnerability detection task for C/C++ language.

static void U_CALLCONV _LMBCSOpen ## n ( UConverter * _this , UConverterLoadArgs * pArgs , UErrorCode * err ) \ {
 _LMBCSOpenWorker ( _this , pArgs , err , n ) ;
 }
 static void _LMBCSOpenWorker ( UConverter * _this , UConverterLoadArgs * pArgs , UErrorCode * err , ulmbcs_byte_t OptGroup ) {
 UConverterDataLMBCS * extraInfo = ( UConverterDataLMBCS * ) uprv_malloc ( sizeof ( UConverterDataLMBCS ) ) ;
 _this -> extraInfo = extraInfo ;
 if ( extraInfo != NULL ) {
 UConverterNamePieces stackPieces ;
 UConverterLoadArgs stackArgs = UCNV_LOAD_ARGS_INITIALIZER ;
 ulmbcs_byte_t i ;
 uprv_memset ( extraInfo , 0 , sizeof ( UConverterDataLMBCS ) ) ;
 stackArgs . onlyTestIsLoadable = pArgs -> onlyTestIsLoadable ;
 for ( i = 0 ;
 i <= ULMBCS_GRP_LAST && U_SUCCESS ( * err ) ;
 i ++ ) {
 if ( OptGroupByteToCPName [ i ] != NULL ) {
 extraInfo -> OptGrpConverter [ i ] = ucnv_loadSharedData ( OptGroupByteToCPName [ i ] , & stackPieces , & stackArgs , err ) ;
 }
 }
 if ( U_FAILURE ( * err ) || pArgs -> onlyTestIsLoadable ) {
 _LMBCSClose ( _this ) ;
 return ;
 }
 extraInfo -> OptGroup = OptGroup ;
 extraInfo -> localeConverterIndex = FindLMBCSLocale ( pArgs -> locale ) ;
 }
 else {
 * err = U_MEMORY_ALLOCATION_ERROR ;
 }
 }
 U_CDECL_BEGIN static void U_CALLCONV _LMBCSClose ( UConverter * _this ) {
 if ( _this -> extraInfo != NULL ) {
 ulmbcs_byte_t Ix ;
 UConverterDataLMBCS * extraInfo = ( UConverterDataLMBCS * ) _this -> extraInfo ;
 for ( Ix = 0 ;
 Ix <= ULMBCS_GRP_LAST ;
 Ix ++ ) {
 if ( extraInfo -> OptGrpConverter [ Ix ] != NULL ) ucnv_unloadSharedDataIfReady ( extraInfo -> OptGrpConverter [ Ix ] ) ;
 }
 if ( ! _this -> isExtraLocal ) {
 uprv_free ( _this -> extraInfo ) ;
 _this -> extraInfo = NULL ;
 }
 }
 }
 typedef struct LMBCSClone {
 UConverter cnv ;
 UConverterDataLMBCS lmbcs ;
 }
 LMBCSClone ;
 static UConverter * U_CALLCONV _LMBCSSafeClone ( const UConverter * cnv , void * stackBuffer , int32_t * pBufferSize , UErrorCode * status ) {
 ( void ) status ;
 LMBCSClone * newLMBCS ;
 UConverterDataLMBCS * extraInfo ;
 int32_t i ;
 if ( * pBufferSize <= 0 ) {
 * pBufferSize = ( int32_t ) sizeof ( LMBCSClone ) ;
 return NULL ;
 }
 extraInfo = ( UConverterDataLMBCS * ) cnv -> extraInfo ;
 newLMBCS = ( LMBCSClone * ) stackBuffer ;
 uprv_memcpy ( & newLMBCS -> lmbcs , extraInfo , sizeof ( UConverterDataLMBCS ) ) ;
 for ( i = 0 ;
 i <= ULMBCS_GRP_LAST ;
 ++ i ) {
 if ( extraInfo -> OptGrpConverter [ i ] != NULL ) {
 ucnv_incrementRefCount ( extraInfo -> OptGrpConverter [ i ] ) ;
 }
 }
 newLMBCS -> cnv . extraInfo = & newLMBCS -> lmbcs ;
 newLMBCS -> cnv . isExtraLocal = TRUE ;
 return & newLMBCS -> cnv ;
 }
 static size_t LMBCSConversionWorker ( UConverterDataLMBCS * extraInfo , ulmbcs_byte_t group , ulmbcs_byte_t * pStartLMBCS , UChar * pUniChar , ulmbcs_byte_t * lastConverterIndex , UBool * groups_tried ) {
 ulmbcs_byte_t * pLMBCS = pStartLMBCS ;
 UConverterSharedData * xcnv = extraInfo -> OptGrpConverter [ group ] ;
 int bytesConverted ;
 uint32_t value ;
 ulmbcs_byte_t firstByte ;
 U_ASSERT ( xcnv ) ;
 U_ASSERT ( group < ULMBCS_GRP_UNICODE ) ;
 bytesConverted = ucnv_MBCSFromUChar32 ( xcnv , * pUniChar , & value , FALSE ) ;
 if ( bytesConverted > 0 ) {
 firstByte = ( ulmbcs_byte_t ) ( value >> ( ( bytesConverted - 1 ) * 8 ) ) ;
 }
 else {
 groups_tried [ group ] = TRUE ;
 return 0 ;
 }
 * lastConverterIndex = group ;
 U_ASSERT ( ( firstByte <= ULMBCS_C0END ) || ( firstByte >= ULMBCS_C1START ) || ( group == ULMBCS_GRP_EXCEPT ) ) ;
 if ( group != ULMBCS_GRP_EXCEPT && extraInfo -> OptGroup != group ) {
 * pLMBCS ++ = group ;
 if ( bytesConverted == 1 && group >= ULMBCS_DOUBLEOPTGROUP_START ) {
 * pLMBCS ++ = group ;
 }
 }
 if ( bytesConverted == 1 && firstByte < 0x20 ) return 0 ;
 switch ( bytesConverted ) {
 case 4 : * pLMBCS ++ = ( ulmbcs_byte_t ) ( value >> 24 ) ;
 U_FALLTHROUGH ;
 case 3 : * pLMBCS ++ = ( ulmbcs_byte_t ) ( value >> 16 ) ;
 U_FALLTHROUGH ;
 case 2 : * pLMBCS ++ = ( ulmbcs_byte_t ) ( value >> 8 ) ;
 U_FALLTHROUGH ;
 case 1 : * pLMBCS ++ = ( ulmbcs_byte_t ) value ;
 U_FALLTHROUGH ;
 default : break ;
 }
 return ( pLMBCS - pStartLMBCS ) ;
 }
 static size_t LMBCSConvertUni ( ulmbcs_byte_t * pLMBCS , UChar uniChar ) {
 uint8_t LowCh = ( uint8_t ) ( uniChar & 0x00FF ) ;
 uint8_t HighCh = ( uint8_t ) ( uniChar >> 8 ) ;
 * pLMBCS ++ = ULMBCS_GRP_UNICODE ;
 if ( LowCh == 0 ) {
 * pLMBCS ++ = ULMBCS_UNICOMPATZERO ;
 * pLMBCS ++ = HighCh ;
 }
 else {
 * pLMBCS ++ = HighCh ;
 * pLMBCS ++ = LowCh ;
 }
 return ULMBCS_UNICODE_SIZE ;
 }
 static void U_CALLCONV _LMBCSFromUnicode ( UConverterFromUnicodeArgs * args , UErrorCode * err ) {
 ulmbcs_byte_t lastConverterIndex = 0 ;
 UChar uniChar ;
 ulmbcs_byte_t LMBCS [ ULMBCS_CHARSIZE_MAX ] ;
 ulmbcs_byte_t * pLMBCS ;
 int32_t bytes_written ;
 UBool groups_tried [ ULMBCS_GRP_LAST + 1 ] ;
 UConverterDataLMBCS * extraInfo = ( UConverterDataLMBCS * ) args -> converter -> extraInfo ;
 int sourceIndex = 0 ;
 ulmbcs_byte_t OldConverterIndex = 0 ;
 while ( args -> source < args -> sourceLimit && ! U_FAILURE ( * err ) ) {
 OldConverterIndex = extraInfo -> localeConverterIndex ;
 if ( args -> target >= args -> targetLimit ) {
 * err = U_BUFFER_OVERFLOW_ERROR ;
 break ;
 }
 uniChar = * ( args -> source ) ;
 bytes_written = 0 ;
 pLMBCS = LMBCS ;
 if ( ( uniChar >= 0x80 ) && ( uniChar <= 0xff ) && ( uniChar != 0xB1 ) && ( uniChar != 0xD7 ) && ( uniChar != 0xF7 ) && ( uniChar != 0xB0 ) && ( uniChar != 0xB4 ) && ( uniChar != 0xB6 ) && ( uniChar != 0xA7 ) && ( uniChar != 0xA8 ) ) {
 extraInfo -> localeConverterIndex = ULMBCS_GRP_L1 ;
 }
 if ( ( ( uniChar > ULMBCS_C0END ) && ( uniChar < ULMBCS_C1START ) ) || uniChar == 0 || uniChar == ULMBCS_HT || uniChar == ULMBCS_CR || uniChar == ULMBCS_LF || uniChar == ULMBCS_123SYSTEMRANGE ) {
 * pLMBCS ++ = ( ulmbcs_byte_t ) uniChar ;
 bytes_written = 1 ;
 }
 if ( ! bytes_written ) {
 ulmbcs_byte_t group = FindLMBCSUniRange ( uniChar ) ;
 if ( group == ULMBCS_GRP_UNICODE ) {
 pLMBCS += LMBCSConvertUni ( pLMBCS , uniChar ) ;
 bytes_written = ( int32_t ) ( pLMBCS - LMBCS ) ;
 }
 else if ( group == ULMBCS_GRP_CTRL ) {
 if ( uniChar <= ULMBCS_C0END ) {
 * pLMBCS ++ = ULMBCS_GRP_CTRL ;
 * pLMBCS ++ = ( ulmbcs_byte_t ) ( ULMBCS_CTRLOFFSET + uniChar ) ;
 }
 else if ( uniChar >= ULMBCS_C1START && uniChar <= ULMBCS_C1START + ULMBCS_CTRLOFFSET ) {
 * pLMBCS ++ = ULMBCS_GRP_CTRL ;
 * pLMBCS ++ = ( ulmbcs_byte_t ) ( uniChar & 0x00FF ) ;
 }
 bytes_written = ( int32_t ) ( pLMBCS - LMBCS ) ;
 }
 else if ( group < ULMBCS_GRP_UNICODE ) {
 bytes_written = ( int32_t ) LMBCSConversionWorker ( extraInfo , group , pLMBCS , & uniChar , & lastConverterIndex , groups_tried ) ;
 }
 if ( ! bytes_written ) {
 uprv_memset ( groups_tried , 0 , sizeof ( groups_tried ) ) ;
 if ( ( extraInfo -> OptGroup != 1 ) && ( ULMBCS_AMBIGUOUS_MATCH ( group , extraInfo -> OptGroup ) ) ) {
 if ( extraInfo -> localeConverterIndex < ULMBCS_DOUBLEOPTGROUP_START ) {
 bytes_written = LMBCSConversionWorker ( extraInfo , ULMBCS_GRP_L1 , pLMBCS , & uniChar , & lastConverterIndex , groups_tried ) ;
 if ( ! bytes_written ) {
 bytes_written = LMBCSConversionWorker ( extraInfo , ULMBCS_GRP_EXCEPT , pLMBCS , & uniChar , & lastConverterIndex , groups_tried ) ;
 }
 if ( ! bytes_written ) {
 bytes_written = LMBCSConversionWorker ( extraInfo , extraInfo -> localeConverterIndex , pLMBCS , & uniChar , & lastConverterIndex , groups_tried ) ;
 }
 }
 else {
 bytes_written = LMBCSConversionWorker ( extraInfo , extraInfo -> localeConverterIndex , pLMBCS , & uniChar , & lastConverterIndex , groups_tried ) ;
 }
 }
 if ( ! bytes_written && ( extraInfo -> localeConverterIndex ) && ( ULMBCS_AMBIGUOUS_MATCH ( group , extraInfo -> localeConverterIndex ) ) ) {
 bytes_written = ( int32_t ) LMBCSConversionWorker ( extraInfo , extraInfo -> localeConverterIndex , pLMBCS , & uniChar , & lastConverterIndex , groups_tried ) ;
 }
 if ( ! bytes_written && ( lastConverterIndex ) && ( ULMBCS_AMBIGUOUS_MATCH ( group , lastConverterIndex ) ) ) {
 bytes_written = ( int32_t ) LMBCSConversionWorker ( extraInfo , lastConverterIndex , pLMBCS , & uniChar , & lastConverterIndex , groups_tried ) ;
 }
 if ( ! bytes_written ) {
 ulmbcs_byte_t grp_start ;
 ulmbcs_byte_t grp_end ;
 ulmbcs_byte_t grp_ix ;
 grp_start = ( ulmbcs_byte_t ) ( ( group == ULMBCS_AMBIGUOUS_MBCS ) ? ULMBCS_DOUBLEOPTGROUP_START : ULMBCS_GRP_L1 ) ;
 grp_end = ( ulmbcs_byte_t ) ( ( group == ULMBCS_AMBIGUOUS_MBCS ) ? ULMBCS_GRP_LAST : ULMBCS_GRP_TH ) ;
 if ( group == ULMBCS_AMBIGUOUS_ALL ) {
 grp_start = ULMBCS_GRP_L1 ;
 grp_end = ULMBCS_GRP_LAST ;
 }
 for ( grp_ix = grp_start ;
 grp_ix <= grp_end && ! bytes_written ;
 grp_ix ++ ) {
 if ( extraInfo -> OptGrpConverter [ grp_ix ] && ! groups_tried [ grp_ix ] ) {
 bytes_written = ( int32_t ) LMBCSConversionWorker ( extraInfo , grp_ix , pLMBCS , & uniChar , & lastConverterIndex , groups_tried ) ;
 }
 }
 if ( ! bytes_written && grp_start == ULMBCS_GRP_L1 ) {
 bytes_written = ( int32_t ) LMBCSConversionWorker ( extraInfo , ULMBCS_GRP_EXCEPT , pLMBCS , & uniChar , & lastConverterIndex , groups_tried ) ;
 }
 }
 if ( ! bytes_written ) {
 pLMBCS += LMBCSConvertUni ( pLMBCS , uniChar ) ;
 bytes_written = ( int32_t ) ( pLMBCS - LMBCS ) ;
 }
/* [TRUNCATED TARGET] */

In the above code snippet, check for potential security vulnerabilities and answer with a single digit: 1 if Vulnerable, 0 if Non-vulnerable.

The guarded evidence of the code snippet is as follows:
GUARDED EVIDENCE: operation-specific observed relations; not a safety proof.
N1 CALL "extraInfo != NULL"
N2 CALL "uprv_memset ( extraInfo , 0 , sizeof ( UConverterDataLMBCS ) )"
N3 CALL "sizeof ( UConverterDataLMBCS )"
N4 CALL "pArgs -> onlyTestIsLoadable"
N5 CALL "i <= ULMBCS_GRP_LAST && U_SUCCESS ( * err )"
N6 CALL "i <= ULMBCS_GRP_LAST"
N7 CALL "* err"
N8 CALL "OptGroupByteToCPName [ i ]"
N1 --CDG--> N2
N1 --CDG--> N4
N2 --ARGUMENT--> N3
N5 --CDG--> N8
N6 --CDG--> N7
OP N4
  INPUTS not included/unknown
  DIRECT_CONTROL N1 via=CDG branch=unknown check=cdg_observed_cfg_unknown
OP N7
  INPUTS not included/unknown
  DIRECT_CONTROL N6 via=CDG branch=unknown check=cdg_observed_cfg_unknown
OP N8
  INPUTS not included/unknown
  DIRECT_CONTROL N5 via=CDG branch=unknown check=cdg_observed_cfg_unknown
OP N2
  INPUTS N3
  DIRECT_CONTROL N1 via=CDG branch=unknown check=cdg_observed_cfg_unknown
  DATA_NOTE: predicates on related data are not operation controls.
UNKNOWN: guard sufficiency, aliasing and feasible execution paths. Missing polarity is unknown.
BOUNDED: omitted operations/context and shortened snippets are not proof of absence.

The following is an example, and it is .


Answer (0 or 1):
~~~~~

## Sample 40 · reveal · B1-H2 · seed 42

ID: `reveal:validation:1259`  
Prompt SHA-256: `efc8b003a6337d4673630a7c33419a5f23e66b59558bef2f897eebf6f0bafcf3`

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

The guarded evidence of the code snippet is as follows:
CPG_UNAVAILABLE: flagged Joern extraction error; no H2 graph evidence is available. Do not treat this as evidence that the code is safe.

The following is an example, and it is .


Answer (0 or 1):
~~~~~

## Sample 41 · reveal · B1-H2 · seed 42

ID: `reveal:validation:1324`  
Prompt SHA-256: `4bc0618f7e439299eae5efae7a5a046565f497cf5800e9e44c89b7dc721b2b4c`

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

## Sample 42 · reveal · B1-H2 · seed 42

ID: `reveal:validation:1550`  
Prompt SHA-256: `9b72ccf305cc252eac51b645576f4c01eedd071e0fdad90defb1a056d339544c`

~~~~~text
You are now an excellent programmer. You are conducting a function vulnerability detection task for C/C++ language.

static int iso9660_options ( struct archive_write * a , const char * key , const char * value ) {
 struct iso9660 * iso9660 = a -> format_data ;
 const char * p ;
 int r ;
 switch ( key [ 0 ] ) {
 case 'a' : if ( strcmp ( key , "abstract-file" ) == 0 ) {
 r = get_str_opt ( a , & ( iso9660 -> abstract_file_identifier ) , ABSTRACT_FILE_SIZE , key , value ) ;
 iso9660 -> opt . abstract_file = r == ARCHIVE_OK ;
 return ( r ) ;
 }
 if ( strcmp ( key , "application-id" ) == 0 ) {
 r = get_str_opt ( a , & ( iso9660 -> application_identifier ) , APPLICATION_IDENTIFIER_SIZE , key , value ) ;
 iso9660 -> opt . application_id = r == ARCHIVE_OK ;
 return ( r ) ;
 }
 if ( strcmp ( key , "allow-vernum" ) == 0 ) {
 iso9660 -> opt . allow_vernum = value != NULL ;
 return ( ARCHIVE_OK ) ;
 }
 break ;
 case 'b' : if ( strcmp ( key , "biblio-file" ) == 0 ) {
 r = get_str_opt ( a , & ( iso9660 -> bibliographic_file_identifier ) , BIBLIO_FILE_SIZE , key , value ) ;
 iso9660 -> opt . biblio_file = r == ARCHIVE_OK ;
 return ( r ) ;
 }
 if ( strcmp ( key , "boot" ) == 0 ) {
 if ( value == NULL ) iso9660 -> opt . boot = 0 ;
 else {
 iso9660 -> opt . boot = 1 ;
 archive_strcpy ( & ( iso9660 -> el_torito . boot_filename ) , value ) ;
 }
 return ( ARCHIVE_OK ) ;
 }
 if ( strcmp ( key , "boot-catalog" ) == 0 ) {
 r = get_str_opt ( a , & ( iso9660 -> el_torito . catalog_filename ) , 1024 , key , value ) ;
 iso9660 -> opt . boot_catalog = r == ARCHIVE_OK ;
 return ( r ) ;
 }
 if ( strcmp ( key , "boot-info-table" ) == 0 ) {
 iso9660 -> opt . boot_info_table = value != NULL ;
 return ( ARCHIVE_OK ) ;
 }
 if ( strcmp ( key , "boot-load-seg" ) == 0 ) {
 uint32_t seg ;
 iso9660 -> opt . boot_load_seg = 0 ;
 if ( value == NULL ) goto invalid_value ;
 seg = 0 ;
 p = value ;
 if ( p [ 0 ] == '0' && ( p [ 1 ] == 'x' || p [ 1 ] == 'X' ) ) p += 2 ;
 while ( * p ) {
 if ( seg ) seg <<= 4 ;
 if ( * p >= 'A' && * p <= 'F' ) seg += * p - 'A' + 0x0a ;
 else if ( * p >= 'a' && * p <= 'f' ) seg += * p - 'a' + 0x0a ;
 else if ( * p >= '0' && * p <= '9' ) seg += * p - '0' ;
 else goto invalid_value ;
 if ( seg > 0xffff ) {
 archive_set_error ( & a -> archive , ARCHIVE_ERRNO_MISC , "Invalid value(over 0xffff) for " "option ``%s''" , key ) ;
 return ( ARCHIVE_FATAL ) ;
 }
 p ++ ;
 }
 iso9660 -> el_torito . boot_load_seg = ( uint16_t ) seg ;
 iso9660 -> opt . boot_load_seg = 1 ;
 return ( ARCHIVE_OK ) ;
 }
 if ( strcmp ( key , "boot-load-size" ) == 0 ) {
 int num = 0 ;
 r = get_num_opt ( a , & num , 0xffff , 1 , key , value ) ;
 iso9660 -> opt . boot_load_size = r == ARCHIVE_OK ;
 if ( r != ARCHIVE_OK ) return ( ARCHIVE_FATAL ) ;
 iso9660 -> el_torito . boot_load_size = ( uint16_t ) num ;
 return ( ARCHIVE_OK ) ;
 }
 if ( strcmp ( key , "boot-type" ) == 0 ) {
 if ( value == NULL ) goto invalid_value ;
 if ( strcmp ( value , "no-emulation" ) == 0 ) iso9660 -> opt . boot_type = OPT_BOOT_TYPE_NO_EMU ;
 else if ( strcmp ( value , "fd" ) == 0 ) iso9660 -> opt . boot_type = OPT_BOOT_TYPE_FD ;
 else if ( strcmp ( value , "hard-disk" ) == 0 ) iso9660 -> opt . boot_type = OPT_BOOT_TYPE_HARD_DISK ;
 else goto invalid_value ;
 return ( ARCHIVE_OK ) ;
 }
 break ;
 case 'c' : if ( strcmp ( key , "compression-level" ) == 0 ) {
 # ifdef HAVE_ZLIB_H if ( value == NULL || ! ( value [ 0 ] >= '0' && value [ 0 ] <= '9' ) || value [ 1 ] != '\0' ) goto invalid_value ;
 iso9660 -> zisofs . compression_level = value [ 0 ] - '0' ;
 iso9660 -> opt . compression_level = 1 ;
 return ( ARCHIVE_OK ) ;
 # else archive_set_error ( & a -> archive , ARCHIVE_ERRNO_MISC , "Option ``%s'' " "is not supported on this platform." , key ) ;
 return ( ARCHIVE_FATAL ) ;
 # endif }
 if ( strcmp ( key , "copyright-file" ) == 0 ) {
 r = get_str_opt ( a , & ( iso9660 -> copyright_file_identifier ) , COPYRIGHT_FILE_SIZE , key , value ) ;
 iso9660 -> opt . copyright_file = r == ARCHIVE_OK ;
 return ( r ) ;
 }
 # ifdef DEBUG if ( strcmp ( key , "creation" ) == 0 ) {
 struct tm tm ;
 char buf [ 5 ] ;
 p = value ;
 if ( p == NULL || strlen ( p ) < 14 ) goto invalid_value ;
 memset ( & tm , 0 , sizeof ( tm ) ) ;
 memcpy ( buf , p , 4 ) ;
 buf [ 4 ] = '\0' ;
 p += 4 ;
 tm . tm_year = strtol ( buf , NULL , 10 ) - 1900 ;
 memcpy ( buf , p , 2 ) ;
 buf [ 2 ] = '\0' ;
 p += 2 ;
 tm . tm_mon = strtol ( buf , NULL , 10 ) - 1 ;
 memcpy ( buf , p , 2 ) ;
 buf [ 2 ] = '\0' ;
 p += 2 ;
 tm . tm_mday = strtol ( buf , NULL , 10 ) ;
 memcpy ( buf , p , 2 ) ;
 buf [ 2 ] = '\0' ;
 p += 2 ;
 tm . tm_hour = strtol ( buf , NULL , 10 ) ;
 memcpy ( buf , p , 2 ) ;
 buf [ 2 ] = '\0' ;
 p += 2 ;
 tm . tm_min = strtol ( buf , NULL , 10 ) ;
 memcpy ( buf , p , 2 ) ;
 buf [ 2 ] = '\0' ;
 tm . tm_sec = strtol ( buf , NULL , 10 ) ;
 iso9660 -> birth_time = mktime ( & tm ) ;
 return ( ARCHIVE_OK ) ;
 }
 # endif break ;
 case 'i' : if ( strcmp ( key , "iso-level" ) == 0 ) {
 if ( value != NULL && value [ 1 ] == '\0' && ( value [ 0 ] >= '1' && value [ 0 ] <= '4' ) ) {
 iso9660 -> opt . iso_level = value [ 0 ] - '0' ;
 return ( ARCHIVE_OK ) ;
 }
 goto invalid_value ;
 }
 break ;
 case 'j' : if ( strcmp ( key , "joliet" ) == 0 ) {
 if ( value == NULL ) iso9660 -> opt . joliet = OPT_JOLIET_DISABLE ;
 else if ( strcmp ( value , "1" ) == 0 ) iso9660 -> opt . joliet = OPT_JOLIET_ENABLE ;
 else if ( strcmp ( value , "long" ) == 0 ) iso9660 -> opt . joliet = OPT_JOLIET_LONGNAME ;
 else goto invalid_value ;
 return ( ARCHIVE_OK ) ;
 }
 break ;
 case 'l' : if ( strcmp ( key , "limit-depth" ) == 0 ) {
 iso9660 -> opt . limit_depth = value != NULL ;
 return ( ARCHIVE_OK ) ;
 }
 if ( strcmp ( key , "limit-dirs" ) == 0 ) {
 iso9660 -> opt . limit_dirs = value != NULL ;
 return ( ARCHIVE_OK ) ;
 }
 break ;
 case 'p' : if ( strcmp ( key , "pad" ) == 0 ) {
 iso9660 -> opt . pad = value != NULL ;
 return ( ARCHIVE_OK ) ;
 }
 if ( strcmp ( key , "publisher" ) == 0 ) {
 r = get_str_opt ( a , & ( iso9660 -> publisher_identifier ) , PUBLISHER_IDENTIFIER_SIZE , key , value ) ;
 iso9660 -> opt . publisher = r == ARCHIVE_OK ;
 return ( r ) ;
 }
 break ;
 case 'r' : if ( strcmp ( key , "rockridge" ) == 0 || strcmp ( key , "Rockridge" ) == 0 ) {
 if ( value == NULL ) iso9660 -> opt . rr = OPT_RR_DISABLED ;
 else if ( strcmp ( value , "1" ) == 0 ) iso9660 -> opt . rr = OPT_RR_USEFUL ;
 else if ( strcmp ( value , "strict" ) == 0 ) iso9660 -> opt . rr = OPT_RR_STRICT ;
 else if ( strcmp ( value , "useful" ) == 0 ) iso9660 -> opt . rr = OPT_RR_USEFUL ;
 else goto invalid_value ;
 return ( ARCHIVE_OK ) ;
 }
 break ;
 case 'v' : if ( strcmp ( key , "volume-id" ) == 0 ) {
 r = get_str_opt ( a , & ( iso9660 -> volume_identifier ) , VOLUME_IDENTIFIER_SIZE , key , value ) ;
 iso9660 -> opt . volume_id = r == ARCHIVE_OK ;
 return ( r ) ;
 }
 break ;
 case 'z' : if ( strcmp ( key , "zisofs" ) == 0 ) {
 if ( value == NULL ) iso9660 -> opt . zisofs = OPT_ZISOFS_DISABLED ;
 else {
 # ifdef HAVE_ZLIB_H iso9660 -> opt . zisofs = OPT_ZISOFS_DIRECT ;
 # else archive_set_error ( & a -> archive , ARCHIVE_ERRNO_MISC , "``zisofs'' " "is not supported on this platform." ) ;
 return ( ARCHIVE_FATAL ) ;
 # endif }
 return ( ARCHIVE_OK ) ;
 }
 break ;
 }
 return ( ARCHIVE_WARN ) ;
 invalid_value : archive_set_error ( & a -> archive , ARCHIVE_ERRNO_MISC , "Invalid value for option ``%s''" , key ) ;
 return ( ARCHIVE_FAILED ) ;
 }

In the above code snippet, check for potential security vulnerabilities and answer with a single digit: 1 if Vulnerable, 0 if Non-vulnerable.

The guarded evidence of the code snippet is as follows:
GUARDED EVIDENCE: operation-specific observed relations; not a safety proof.
N1 CALL "a -> format_data"
N2 CALL "key [ 0 ]"
N3 CALL "strcmp ( key , \"abstract-file\" ) == 0"
N4 CALL "strcmp ( key , \"abstract-file\" )"
N5 CALL "\n        get_str_opt ( a , & ( iso9660 -> abstract_file_identifier ) , ABSTRACT_FILE_SIZE , key , value )\n      "
N2 --CDG--> N4
N3 --CDG--> N5
OP N4
  INPUTS not included/unknown
  DIRECT_CONTROL N2 via=CDG branch=unknown check=cdg_observed_cfg_unknown
OP N5
  INPUTS not included/unknown
  DIRECT_CONTROL N3 via=CDG branch=unknown check=cdg_observed_cfg_unknown
OP N1
  INPUTS not included/unknown
  DIRECT_CONTROL none observed; not proof of absence
OP N2
  INPUTS not included/unknown
  DIRECT_CONTROL none observed; not proof of absence
UNKNOWN: guard sufficiency, aliasing and feasible execution paths. Missing polarity is unknown.
BOUNDED: omitted operations/context and shortened snippets are not proof of absence.

The following is an example, and it is .


Answer (0 or 1):
~~~~~

## Sample 43 · reveal · B1-H2 · seed 42

ID: `reveal:validation:1551`  
Prompt SHA-256: `26c5ffdeeaf758d2c45e425c86dae024592bc0bb58222230e955d8589d4b3554`

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

## Sample 44 · reveal · B1-H2 · seed 42

ID: `reveal:validation:168`  
Prompt SHA-256: `e870f461cbcee46e63f948faddacc78bab28e7568c1b1de5ac075ac8202db620`

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

The guarded evidence of the code snippet is as follows:
CPG_UNAVAILABLE: flagged Joern extraction error; no H2 graph evidence is available. Do not treat this as evidence that the code is safe.

The following is an example, and it is .


Answer (0 or 1):
~~~~~

## Sample 45 · reveal · B1-H2 · seed 42

ID: `reveal:validation:175`  
Prompt SHA-256: `ad6f4e221f8ecda3b46f2971b71084c73ff91a7d1d5327e837aa6519e7a7c2cc`

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

## Sample 46 · reveal · B1-H2 · seed 42

ID: `reveal:validation:1792`  
Prompt SHA-256: `dd61575cb05353a1e015fa91e85cc896654566f98ad4b2eade6928265a7aeaaf`

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

The guarded evidence of the code snippet is as follows:
CPG_UNAVAILABLE: flagged Joern extraction error; no H2 graph evidence is available. Do not treat this as evidence that the code is safe.

The following is an example, and it is .


Answer (0 or 1):
~~~~~

## Sample 47 · reveal · B1-H2 · seed 42

ID: `reveal:validation:1810`  
Prompt SHA-256: `12b6a13d04aa790a8e1ccb05d7825d4e48d19a5141802c6754a7e2feb4ae8825`

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

## Sample 48 · reveal · B1-H2 · seed 42

ID: `reveal:validation:1834`  
Prompt SHA-256: `95bd4b73ae626965610f449ea1d27d954568d68e95a7b456b4dae0cf07cdeec5`

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

## Sample 49 · reveal · B1-H2 · seed 42

ID: `reveal:validation:1923`  
Prompt SHA-256: `bbcecba9fe86b0081ee363fb56df8a136c4cd1eeeb0736872c91956ca843bf33`

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

## Sample 50 · reveal · B1-H2 · seed 42

ID: `reveal:validation:1977`  
Prompt SHA-256: `488e81fdad5a1840c89dbf59e592af0f40d3173d81577a3542bdbc2a2150d124`

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

## Sample 51 · reveal · B1-H2 · seed 42

ID: `reveal:validation:216`  
Prompt SHA-256: `80a8fc859dab7cbb12110fb3997cdbdbab99cda2c7bcbbdcb214508172abb00c`

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

## Sample 52 · reveal · B1-H2 · seed 42

ID: `reveal:validation:394`  
Prompt SHA-256: `b93768b2319d16dfe68c109f7414bec20f2d73fc76bcb21ee41d995143bdf512`

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

## Sample 53 · reveal · B1-H2 · seed 42

ID: `reveal:validation:554`  
Prompt SHA-256: `32c635cf08c8bccb7d30f7dc0be4b51a61d95dbba0d56d69b902f74cbd600aa4`

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

ID: `reveal:validation:593`  
Prompt SHA-256: `99b18e42e814effa5e59c6ed0646d7f1157f830948d911be967397254d1641e5`

~~~~~text
You are now an excellent programmer. You are conducting a function vulnerability detection task for C/C++ language.

static void iadst16_8col ( __m128i * in ) {
 __m128i s [ 16 ] , x [ 16 ] , u [ 32 ] , v [ 32 ] ;
 const __m128i k__cospi_p01_p31 = pair_set_epi16 ( cospi_1_64 , cospi_31_64 ) ;
 const __m128i k__cospi_p31_m01 = pair_set_epi16 ( cospi_31_64 , - cospi_1_64 ) ;
 const __m128i k__cospi_p05_p27 = pair_set_epi16 ( cospi_5_64 , cospi_27_64 ) ;
 const __m128i k__cospi_p27_m05 = pair_set_epi16 ( cospi_27_64 , - cospi_5_64 ) ;
 const __m128i k__cospi_p09_p23 = pair_set_epi16 ( cospi_9_64 , cospi_23_64 ) ;
 const __m128i k__cospi_p23_m09 = pair_set_epi16 ( cospi_23_64 , - cospi_9_64 ) ;
 const __m128i k__cospi_p13_p19 = pair_set_epi16 ( cospi_13_64 , cospi_19_64 ) ;
 const __m128i k__cospi_p19_m13 = pair_set_epi16 ( cospi_19_64 , - cospi_13_64 ) ;
 const __m128i k__cospi_p17_p15 = pair_set_epi16 ( cospi_17_64 , cospi_15_64 ) ;
 const __m128i k__cospi_p15_m17 = pair_set_epi16 ( cospi_15_64 , - cospi_17_64 ) ;
 const __m128i k__cospi_p21_p11 = pair_set_epi16 ( cospi_21_64 , cospi_11_64 ) ;
 const __m128i k__cospi_p11_m21 = pair_set_epi16 ( cospi_11_64 , - cospi_21_64 ) ;
 const __m128i k__cospi_p25_p07 = pair_set_epi16 ( cospi_25_64 , cospi_7_64 ) ;
 const __m128i k__cospi_p07_m25 = pair_set_epi16 ( cospi_7_64 , - cospi_25_64 ) ;
 const __m128i k__cospi_p29_p03 = pair_set_epi16 ( cospi_29_64 , cospi_3_64 ) ;
 const __m128i k__cospi_p03_m29 = pair_set_epi16 ( cospi_3_64 , - cospi_29_64 ) ;
 const __m128i k__cospi_p04_p28 = pair_set_epi16 ( cospi_4_64 , cospi_28_64 ) ;
 const __m128i k__cospi_p28_m04 = pair_set_epi16 ( cospi_28_64 , - cospi_4_64 ) ;
 const __m128i k__cospi_p20_p12 = pair_set_epi16 ( cospi_20_64 , cospi_12_64 ) ;
 const __m128i k__cospi_p12_m20 = pair_set_epi16 ( cospi_12_64 , - cospi_20_64 ) ;
 const __m128i k__cospi_m28_p04 = pair_set_epi16 ( - cospi_28_64 , cospi_4_64 ) ;
 const __m128i k__cospi_m12_p20 = pair_set_epi16 ( - cospi_12_64 , cospi_20_64 ) ;
 const __m128i k__cospi_p08_p24 = pair_set_epi16 ( cospi_8_64 , cospi_24_64 ) ;
 const __m128i k__cospi_p24_m08 = pair_set_epi16 ( cospi_24_64 , - cospi_8_64 ) ;
 const __m128i k__cospi_m24_p08 = pair_set_epi16 ( - cospi_24_64 , cospi_8_64 ) ;
 const __m128i k__cospi_m16_m16 = _mm_set1_epi16 ( - cospi_16_64 ) ;
 const __m128i k__cospi_p16_p16 = _mm_set1_epi16 ( cospi_16_64 ) ;
 const __m128i k__cospi_p16_m16 = pair_set_epi16 ( cospi_16_64 , - cospi_16_64 ) ;
 const __m128i k__cospi_m16_p16 = pair_set_epi16 ( - cospi_16_64 , cospi_16_64 ) ;
 const __m128i k__DCT_CONST_ROUNDING = _mm_set1_epi32 ( DCT_CONST_ROUNDING ) ;
 const __m128i kZero = _mm_set1_epi16 ( 0 ) ;
 u [ 0 ] = _mm_unpacklo_epi16 ( in [ 15 ] , in [ 0 ] ) ;
 u [ 1 ] = _mm_unpackhi_epi16 ( in [ 15 ] , in [ 0 ] ) ;
 u [ 2 ] = _mm_unpacklo_epi16 ( in [ 13 ] , in [ 2 ] ) ;
 u [ 3 ] = _mm_unpackhi_epi16 ( in [ 13 ] , in [ 2 ] ) ;
 u [ 4 ] = _mm_unpacklo_epi16 ( in [ 11 ] , in [ 4 ] ) ;
 u [ 5 ] = _mm_unpackhi_epi16 ( in [ 11 ] , in [ 4 ] ) ;
 u [ 6 ] = _mm_unpacklo_epi16 ( in [ 9 ] , in [ 6 ] ) ;
 u [ 7 ] = _mm_unpackhi_epi16 ( in [ 9 ] , in [ 6 ] ) ;
 u [ 8 ] = _mm_unpacklo_epi16 ( in [ 7 ] , in [ 8 ] ) ;
 u [ 9 ] = _mm_unpackhi_epi16 ( in [ 7 ] , in [ 8 ] ) ;
 u [ 10 ] = _mm_unpacklo_epi16 ( in [ 5 ] , in [ 10 ] ) ;
 u [ 11 ] = _mm_unpackhi_epi16 ( in [ 5 ] , in [ 10 ] ) ;
 u [ 12 ] = _mm_unpacklo_epi16 ( in [ 3 ] , in [ 12 ] ) ;
 u [ 13 ] = _mm_unpackhi_epi16 ( in [ 3 ] , in [ 12 ] ) ;
 u [ 14 ] = _mm_unpacklo_epi16 ( in [ 1 ] , in [ 14 ] ) ;
 u [ 15 ] = _mm_unpackhi_epi16 ( in [ 1 ] , in [ 14 ] ) ;
 v [ 0 ] = _mm_madd_epi16 ( u [ 0 ] , k__cospi_p01_p31 ) ;
 v [ 1 ] = _mm_madd_epi16 ( u [ 1 ] , k__cospi_p01_p31 ) ;
 v [ 2 ] = _mm_madd_epi16 ( u [ 0 ] , k__cospi_p31_m01 ) ;
 v [ 3 ] = _mm_madd_epi16 ( u [ 1 ] , k__cospi_p31_m01 ) ;
 v [ 4 ] = _mm_madd_epi16 ( u [ 2 ] , k__cospi_p05_p27 ) ;
 v [ 5 ] = _mm_madd_epi16 ( u [ 3 ] , k__cospi_p05_p27 ) ;
 v [ 6 ] = _mm_madd_epi16 ( u [ 2 ] , k__cospi_p27_m05 ) ;
 v [ 7 ] = _mm_madd_epi16 ( u [ 3 ] , k__cospi_p27_m05 ) ;
 v [ 8 ] = _mm_madd_epi16 ( u [ 4 ] , k__cospi_p09_p23 ) ;
 v [ 9 ] = _mm_madd_epi16 ( u [ 5 ] , k__cospi_p09_p23 ) ;
 v [ 10 ] = _mm_madd_epi16 ( u [ 4 ] , k__cospi_p23_m09 ) ;
 v [ 11 ] = _mm_madd_epi16 ( u [ 5 ] , k__cospi_p23_m09 ) ;
 v [ 12 ] = _mm_madd_epi16 ( u [ 6 ] , k__cospi_p13_p19 ) ;
 v [ 13 ] = _mm_madd_epi16 ( u [ 7 ] , k__cospi_p13_p19 ) ;
 v [ 14 ] = _mm_madd_epi16 ( u [ 6 ] , k__cospi_p19_m13 ) ;
 v [ 15 ] = _mm_madd_epi16 ( u [ 7 ] , k__cospi_p19_m13 ) ;
 v [ 16 ] = _mm_madd_epi16 ( u [ 8 ] , k__cospi_p17_p15 ) ;
 v [ 17 ] = _mm_madd_epi16 ( u [ 9 ] , k__cospi_p17_p15 ) ;
 v [ 18 ] = _mm_madd_epi16 ( u [ 8 ] , k__cospi_p15_m17 ) ;
 v [ 19 ] = _mm_madd_epi16 ( u [ 9 ] , k__cospi_p15_m17 ) ;
 v [ 20 ] = _mm_madd_epi16 ( u [ 10 ] , k__cospi_p21_p11 ) ;
 v [ 21 ] = _mm_madd_epi16 ( u [ 11 ] , k__cospi_p21_p11 ) ;
 v [ 22 ] = _mm_madd_epi16 ( u [ 10 ] , k__cospi_p11_m21 ) ;
 v [ 23 ] = _mm_madd_epi16 ( u [ 11 ] , k__cospi_p11_m21 ) ;
 v [ 24 ] = _mm_madd_epi16 ( u [ 12 ] , k__cospi_p25_p07 ) ;
 v [ 25 ] = _mm_madd_epi16 ( u [ 13 ] , k__cospi_p25_p07 ) ;
 v [ 26 ] = _mm_madd_epi16 ( u [ 12 ] , k__cospi_p07_m25 ) ;
 v [ 27 ] = _mm_madd_epi16 ( u [ 13 ] , k__cospi_p07_m25 ) ;
 v [ 28 ] = _mm_madd_epi16 ( u [ 14 ] , k__cospi_p29_p03 ) ;
 v [ 29 ] = _mm_madd_epi16 ( u [ 15 ] , k__cospi_p29_p03 ) ;
 v [ 30 ] = _mm_madd_epi16 ( u [ 14 ] , k__cospi_p03_m29 ) ;
 v [ 31 ] = _mm_madd_epi16 ( u [ 15 ] , k__cospi_p03_m29 ) ;
 u [ 0 ] = _mm_add_epi32 ( v [ 0 ] , v [ 16 ] ) ;
 u [ 1 ] = _mm_add_epi32 ( v [ 1 ] , v [ 17 ] ) ;
 u [ 2 ] = _mm_add_epi32 ( v [ 2 ] , v [ 18 ] ) ;
 u [ 3 ] = _mm_add_epi32 ( v [ 3 ] , v [ 19 ] ) ;
 u [ 4 ] = _mm_add_epi32 ( v [ 4 ] , v [ 20 ] ) ;
 u [ 5 ] = _
/* [TRUNCATED TARGET] */

In the above code snippet, check for potential security vulnerabilities and answer with a single digit: 1 if Vulnerable, 0 if Non-vulnerable.

The guarded evidence of the code snippet is as follows:
GUARDED EVIDENCE: operation-specific observed relations; not a safety proof.
N1 CALL "s [ 16 ]"
N2 CALL "x [ 16 ]"
N3 CALL "u [ 32 ]"
N4 CALL "v [ 32 ]"
OP N1
  INPUTS not included/unknown
  DIRECT_CONTROL unknown: CDG unavailable
OP N2
  INPUTS not included/unknown
  DIRECT_CONTROL unknown: CDG unavailable
OP N3
  INPUTS not included/unknown
  DIRECT_CONTROL unknown: CDG unavailable
OP N4
  INPUTS not included/unknown
  DIRECT_CONTROL unknown: CDG unavailable
UNKNOWN: guard sufficiency, aliasing and feasible execution paths. Missing polarity is unknown.
BOUNDED: omitted operations/context and shortened snippets are not proof of absence.

The following is an example, and it is .


Answer (0 or 1):
~~~~~

## Sample 56 · reveal · B1-H2 · seed 42

ID: `reveal:validation:599`  
Prompt SHA-256: `c96b14c02d657c310603d7d979d37e0a298ebd6df81f1247a78cd0597e6c432f`

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

## Sample 57 · reveal · B1-H2 · seed 42

ID: `reveal:validation:67`  
Prompt SHA-256: `f3af3098c0921ce32d71067d92f1249920f16a164ca5f6bebdae67fddcbafa8f`

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

## Sample 58 · reveal · B1-H2 · seed 42

ID: `reveal:validation:673`  
Prompt SHA-256: `9800cb57e1e3189e9ab11ea9f5fab123f25a96a7bd19ff824604cd678c77fc01`

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

## Sample 59 · reveal · B1-H2 · seed 42

ID: `reveal:validation:688`  
Prompt SHA-256: `55d8280110829baf120fae4b32ddded149d813b57763bcab925e30334e6619df`

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

## Sample 60 · reveal · B1-H2 · seed 42

ID: `reveal:validation:886`  
Prompt SHA-256: `2adc891582646a4e56fbeaf6e97eaaca0c0e520ec6c60f74481c4cabcd12ac74`

~~~~~text
You are now an excellent programmer. You are conducting a function vulnerability detection task for C/C++ language.

int i2d_ ## name ( type * a , unsigned char * * out ) ;
 DECLARE_ASN1_ITEM ( itname ) # define DECLARE_ASN1_ENCODE_FUNCTIONS_const ( type , name ) type * d2i_ ## name ( type * * a , const unsigned char * * in , long len ) ;
 int i2d_ ## name ( const type * a , unsigned char * * out ) ;
 DECLARE_ASN1_ITEM ( name ) # define DECLARE_ASN1_NDEF_FUNCTION ( name ) int i2d_ ## name ## _NDEF ( name * a , unsigned char * * out ) ;
 # define DECLARE_ASN1_FUNCTIONS_const ( name ) DECLARE_ASN1_ALLOC_FUNCTIONS ( name ) DECLARE_ASN1_ENCODE_FUNCTIONS_const ( name , name ) # define DECLARE_ASN1_ALLOC_FUNCTIONS_name ( type , name ) type * name ## _new ( void ) ;
 void name ## _free ( type * a ) ;
 # define DECLARE_ASN1_PRINT_FUNCTION ( stname ) DECLARE_ASN1_PRINT_FUNCTION_fname ( stname , stname ) # define DECLARE_ASN1_PRINT_FUNCTION_fname ( stname , fname ) int fname ## _print_ctx ( BIO * out , stname * x , int indent , const ASN1_PCTX * pctx ) ;
 # define D2I_OF ( type ) type * ( * ) ( type * * , const unsigned char * * , long ) # define I2D_OF ( type ) int ( * ) ( type * , unsigned char * * ) # define I2D_OF_const ( type ) int ( * ) ( const type * , unsigned char * * ) # define CHECKED_D2I_OF ( type , d2i ) ( ( d2i_of_void * ) ( 1 ? d2i : ( ( D2I_OF ( type ) ) 0 ) ) ) # define CHECKED_I2D_OF ( type , i2d ) ( ( i2d_of_void * ) ( 1 ? i2d : ( ( I2D_OF ( type ) ) 0 ) ) ) # define CHECKED_NEW_OF ( type , xnew ) ( ( void * ( * ) ( void ) ) ( 1 ? xnew : ( ( type * ( * ) ( void ) ) 0 ) ) ) # define CHECKED_PTR_OF ( type , p ) ( ( void * ) ( 1 ? p : ( type * ) 0 ) ) # define CHECKED_PPTR_OF ( type , p ) ( ( void * * ) ( 1 ? p : ( type * * ) 0 ) ) # define TYPEDEF_D2I_OF ( type ) typedef type * d2i_of_ ## type ( type * * , const unsigned char * * , long ) # define TYPEDEF_I2D_OF ( type ) typedef int i2d_of_ ## type ( type * , unsigned char * * ) # define TYPEDEF_D2I2D_OF ( type ) TYPEDEF_D2I_OF ( type ) ;
 TYPEDEF_I2D_OF ( type ) TYPEDEF_D2I2D_OF ( void ) ;
 # ifndef OPENSSL_EXPORT_VAR_AS_FUNCTION typedef const ASN1_ITEM ASN1_ITEM_EXP ;
 # define ASN1_ITEM_ptr ( iptr ) ( iptr ) # define ASN1_ITEM_ref ( iptr ) ( & ( iptr ## _it ) ) # define ASN1_ITEM_rptr ( ref ) ( & ( ref ## _it ) ) # define DECLARE_ASN1_ITEM ( name ) OPENSSL_EXTERN const ASN1_ITEM name ## _it ;
 # else typedef const ASN1_ITEM * ASN1_ITEM_EXP ( void ) ;
 # define ASN1_ITEM_ptr ( iptr ) ( iptr ( ) ) # define ASN1_ITEM_ref ( iptr ) ( iptr ## _it ) # define ASN1_ITEM_rptr ( ref ) ( ref ## _it ( ) ) # define DECLARE_ASN1_ITEM ( name ) const ASN1_ITEM * name ## _it ( void ) ;
 # endif # define ASN1_STRFLGS_ESC_2253 1 # define ASN1_STRFLGS_ESC_CTRL 2 # define ASN1_STRFLGS_ESC_MSB 4 # define ASN1_STRFLGS_ESC_QUOTE 8 # define CHARTYPE_PRINTABLESTRING 0x10 # define CHARTYPE_FIRST_ESC_2253 0x20 # define CHARTYPE_LAST_ESC_2253 0x40 # define ASN1_STRFLGS_UTF8_CONVERT 0x10 # define ASN1_STRFLGS_IGNORE_TYPE 0x20 # define ASN1_STRFLGS_SHOW_TYPE 0x40 # define ASN1_STRFLGS_DUMP_ALL 0x80 # define ASN1_STRFLGS_DUMP_UNKNOWN 0x100 # define ASN1_STRFLGS_DUMP_DER 0x200 # define ASN1_STRFLGS_ESC_2254 0x400 # define ASN1_STRFLGS_RFC2253 ( ASN1_STRFLGS_ESC_2253 | ASN1_STRFLGS_ESC_CTRL | ASN1_STRFLGS_ESC_MSB | ASN1_STRFLGS_UTF8_CONVERT | ASN1_STRFLGS_DUMP_UNKNOWN | ASN1_STRFLGS_DUMP_DER ) DEFINE_STACK_OF ( ASN1_INTEGER ) DEFINE_STACK_OF ( ASN1_GENERALSTRING ) DEFINE_STACK_OF ( ASN1_UTF8STRING ) typedef struct asn1_type_st {
 int type ;
 union {
 char * ptr ;
 ASN1_BOOLEAN boolean ;
 ASN1_STRING * asn1_string ;
 ASN1_OBJECT * object ;
 ASN1_INTEGER * integer ;
 ASN1_ENUMERATED * enumerated ;
 ASN1_BIT_STRING * bit_string ;
 ASN1_OCTET_STRING * octet_string ;
 ASN1_PRINTABLESTRING * printablestring ;
 ASN1_T61STRING * t61string ;
 ASN1_IA5STRING * ia5string ;
 ASN1_GENERALSTRING * generalstring ;
 ASN1_BMPSTRING * bmpstring ;
 ASN1_UNIVERSALSTRING * universalstring ;
 ASN1_UTCTIME * utctime ;
 ASN1_GENERALIZEDTIME * generalizedtime ;
 ASN1_VISIBLESTRING * visiblestring ;
 ASN1_UTF8STRING * utf8string ;
 ASN1_STRING * set ;
 ASN1_STRING * sequence ;
 ASN1_VALUE * asn1_value ;
 }
 value ;
 }
 ASN1_TYPE ;
 DEFINE_STACK_OF ( ASN1_TYPE ) typedef STACK_OF ( ASN1_TYPE ) ASN1_SEQUENCE_ANY ;
 DECLARE_ASN1_ENCODE_FUNCTIONS_const ( ASN1_SEQUENCE_ANY , ASN1_SEQUENCE_ANY ) DECLARE_ASN1_ENCODE_FUNCTIONS_const ( ASN1_SEQUENCE_ANY , ASN1_SET_ANY ) typedef struct BIT_STRING_BITNAME_st {
 int bitnum ;
 const char * lname ;
 const char * sname ;
 }
 BIT_STRING_BITNAME ;
 # define B_ASN1_TIME B_ASN1_UTCTIME | B_ASN1_GENERALIZEDTIME # define B_ASN1_PRINTABLE B_ASN1_NUMERICSTRING | B_ASN1_PRINTABLESTRING | B_ASN1_T61STRING | B_ASN1_IA5STRING | B_ASN1_BIT_STRING | B_ASN1_UNIVERSALSTRING | B_ASN1_BMPSTRING | B_ASN1_UTF8STRING | B_ASN1_SEQUENCE | B_ASN1_UNKNOWN # define B_ASN1_DIRECTORYSTRING B_ASN1_PRINTABLESTRING | B_ASN1_TELETEXSTRING | B_ASN1_BMPSTRING | B_ASN1_UNIVERSALSTRING | B_ASN1_UTF8STRING # define B_ASN1_DISPLAYTEXT B_ASN1_IA5STRING | B_ASN1_VISIBLESTRING | B_ASN1_BMPSTRING | B_ASN1_UTF8STRING DECLARE_ASN1_FUNCTIONS_fname ( ASN1_TYPE , ASN1_ANY , ASN1_TYPE ) int ASN1_TYPE_get ( const ASN1_TYPE * a ) ;
 void ASN1_TYPE_set ( ASN1_TYPE * a , int type , void * value ) ;
 int ASN1_TYPE_set1 ( ASN1_TYPE * a , int type , const void * value ) ;
 int ASN1_TYPE_cmp ( const ASN1_TYPE * a , const ASN1_TYPE * b ) ;
 ASN1_TYPE * ASN1_TYPE_pack_sequence ( const ASN1_ITEM * it , void * s , ASN1_TYPE * * t ) ;
 void * ASN1_TYPE_unpack_sequence ( const ASN1_ITEM * it , const ASN1_TYPE * t ) ;
 ASN1_OBJECT * ASN1_OBJECT_new ( void ) ;
 void ASN1_OBJECT_free ( ASN1_OBJECT * a ) ;
 int i2d_ASN1_OBJECT ( const ASN1_OBJECT * a , unsigned char * * pp ) ;
 ASN1_OBJECT * d2i_ASN1_OBJECT ( ASN1_OBJECT * * a , const unsigned char * * pp , long length ) ;
 DECLARE_ASN1_ITEM ( ASN1_OBJECT ) DEFINE_STACK_OF ( ASN1_OBJECT ) ASN1_STRING * ASN1_STRING_new ( void ) ;
 void ASN1_STRING_free ( ASN1_STRING * a ) ;
 void ASN1_STRING_clear_free ( ASN1_STRING * a ) ;
 int ASN1_STRING_copy ( ASN1_STRING * dst , const ASN1_STRING * str ) ;
 ASN1_STRING * ASN1_STRING_dup ( const ASN1_STRING * a ) ;
 ASN1_STRING * ASN1_STRING_type_new ( int type ) ;
 int ASN1_STRING_cmp ( const ASN1_STRING * a , const ASN1_STRING * b ) ;
 int ASN1_STRING_set ( ASN1_STRING * str , const void * data , int len ) ;
 void ASN1_STRING_set0 ( ASN1_STRING * str , void * data , int len ) ;
 int ASN1_STRING_length ( const ASN1_STRING * x ) ;
 void ASN1_STRING_length_set ( ASN1_STRING * x , int n ) ;
 int ASN1_STRING_type ( const ASN1_STRING * x ) ;
 DEPRECATEDIN_1_1_0 ( unsigned char * ASN1_STRING_data ( ASN1_STRING * x ) ) const unsigned char * ASN1_STRING_get0_data ( const ASN1_STRING * x ) ;
 DECLARE_ASN1_FUNCTIONS ( ASN1_BIT_STRING ) int ASN1_BIT_STRING_set ( ASN1_BIT_STRING * a , unsigned char * d , int length ) ;
 int ASN1_BIT_STRING_set_bit ( ASN1_BIT_STRING * a , int n , int value ) ;
 int ASN1_BIT_STRING_get_bit ( const ASN1_BIT_STRING * a , int n ) ;
 int ASN1_BIT_STRING_check ( const ASN1_BIT_STRING * a , const unsigned char * flags , int flags_len ) ;
 int ASN1_BIT_STRING_name_print ( BIO * out , ASN1_BIT_STRING * bs , BIT_STRING_BITNAME * tbl , int indent ) ;
 int ASN1_BIT_STRING_num_asc ( const char * name , BIT_STRING_BITNAME * tbl ) ;
 int ASN1_BIT_STRING_set_asc ( ASN1_BIT_STRING * bs , const char * name , int value , BIT_STRING_BITNAME * tbl ) ;
 DECLARE_ASN1_FUNCTIONS ( ASN1_INTEGER ) ASN1_INTEGER * d2i_ASN1_UINTEGER ( ASN1_INTEGER * * a , const unsigned char * * pp , long length ) ;
 ASN1_INTEGER * ASN1_INTEGER_dup ( const ASN1_INTEGER * x ) ;
 int ASN1_INTEGER_cmp ( const ASN1_INTEGER * x , const ASN1_INTEGER * y ) ;
 DECLARE_ASN1_FUNCTIONS ( ASN1_ENUMERATED ) int ASN1_UTCTIME_check ( const ASN1_UTCTIME * a ) ;
 ASN1_UTCTIME * ASN1_UTCTIME_set ( ASN1_UTCTIME * s , time_t t ) ;
 ASN1_UTCTIME * ASN1_UTCTIME_adj ( ASN1_UTCTIME * s , time_t t , int offset_day , long offset_sec ) ;
 int ASN1_UTCTIME_set_string ( ASN1_UTCTIME * s , const char * str ) ;
 int ASN1_UTCTIME_cmp_time_t ( const ASN1_UTCTIME * s , time_t t ) ;
 int ASN1_GENERALIZEDTIME_check ( const ASN1_GENERALIZEDTIME * a ) ;
 ASN1_GENERALIZEDTIME * ASN1_GENERALIZEDTIME_set ( ASN1_GENERALIZEDTIME * s , time_t t ) ;
 ASN1_GENERALIZEDTIME * ASN1_GENERALIZEDTIME_adj ( ASN1_GENERALIZEDTIME * s , time_t t , int offset_day , long offset_sec ) ;
 int ASN1_GENERALIZEDTIME_set_string ( ASN1_GENERALIZEDTIME * s , const char * str ) ;
 int ASN1_TIME_diff ( int * pday , int * psec , const ASN1_TIME * from , const ASN1_TIME * to ) ;
 DECLARE_ASN1_FUNCTIONS ( ASN1_OCTET_STRING ) ASN1_OCTET_STRING * ASN1_OCTET_STRING_dup ( const ASN1_OCTET_STRING * a ) ;
 int ASN1_OCTET_STRING_cmp ( const ASN1_OCTET_STRING * a , const ASN1_OCTET_STRING * b ) ;
 int ASN1_OCTET_STRING_set ( ASN1_OCTET_STRING * str , const unsigned char * data , int len ) ;
 DECLARE_ASN1_FUNCTIONS ( ASN1_VISIBLESTRING ) DECLARE_ASN1_FUNCTIONS ( ASN1_UNIVERSALSTRING ) DECLARE_ASN1_FUNCTIONS ( ASN1_UTF8STRING ) DECLARE_ASN1_FUNCTIONS ( ASN1_NULL ) DECLARE_ASN1_FUNCTIONS ( ASN1_BMPSTRING ) int UTF8_getc ( const unsigned char * str , int len , unsigned long * val ) ;
 int UTF8_putc ( unsigned char * str , int len , unsigned long value ) ;
 DECLARE_ASN1_FUNCTIONS_name ( ASN1_STRING , ASN1_PRINTABLE ) DECLARE_ASN1_FUNCTIONS_name ( ASN1_STRING , DIRECTORYSTRING ) DECLARE_ASN1_FUNCTIONS_name ( ASN1_STRING , DISPLAYTEXT ) DECLARE_ASN1_FUNCTIONS ( ASN1_PRINTABLESTRING ) DECLARE_ASN1_FUNCTIONS ( ASN1_T61STRING )

In the above code snippet, check for potential security vulnerabilities and answer with a single digit: 1 if Vulnerable, 0 if Non-vulnerable.

The guarded evidence of the code snippet is as follows:
NO_USABLE_GUARDED_EVIDENCE: no_operation_nodes. Do not infer safety from missing evidence.

The following is an example, and it is .


Answer (0 or 1):
~~~~~
