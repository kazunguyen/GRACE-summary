# Bộ prompt cho hai người chấm độc lập

**Trạng thái: chưa chấm.** Mỗi người đọc cùng 60 prompt (30 Devign + 30 REVEAL) và điền một phiếu riêng; xem [rubric](RUBRIC.md). Không cung cấp nhãn target, score hoặc kết quả model.

## 1. devign:validation:12030

Arm: B0; phiên: legacy; seed: 42; dataset/split: devign/validation.
SHA-256 prompt: `aaf552ddf3beb16d7aaa613dea0fbac29275eb0ba6b271b808a44dfa994abdc8`

~~~~text
You are now an excellent programmer. You are conducting a function vulnerability detection task for C/C++ language.

static void vhost_ccw_scsi_realize(VirtioCcwDevice *ccw_dev, Error **errp)

{

    VHostSCSICcw *dev = VHOST_SCSI_CCW(ccw_dev);

    DeviceState *vdev = DEVICE(&dev->vdev);

    Error *err = NULL;



    qdev_set_parent_bus(vdev, BUS(&ccw_dev->bus));

    object_property_set_bool(OBJECT(vdev), true, "realized", &err);

    if (err) {

        error_propagate(errp, err);

    }

}

In the above code snippet, check for potential security vulnerabilities and answer with a single digit: 1 if Vulnerable, 0 if Non-vulnerable.

The node information of the code snippet is as follows:

The edge information of the code snippet is as follows:


The following is an example, and it is .


Answer (0 or 1):
~~~~

## 2. devign:validation:22666

Arm: B1; phiên: legacy; seed: 42; dataset/split: devign/validation.
SHA-256 prompt: `29e662211dc92c4cf3156b67b9b4bedbb7b9d0159f0e0ffdfb3aec051f6cb14a`

~~~~text
You are now an excellent programmer. You are conducting a function vulnerability detection task for C/C++ language.

static int socket_get_fd(void *opaque)

{

    QEMUFileSocket *s = opaque;



    return s->fd;

}

In the above code snippet, check for potential security vulnerabilities and answer with a single digit: 1 if Vulnerable, 0 if Non-vulnerable.

The node information of the code snippet is as follows:
Node 25769803776: (BLOCK) '{ QEMUFileSocket *s = opaque; return s->...'
Node 30064771072: (CALL) 's = opaque'
Node 30064771073: (CALL) 's->fd'
Node 55834574848: (FIELD_IDENTIFIER) 'fd'
Node 68719476736: (IDENTIFIER) 's'
Node 68719476737: (IDENTIFIER) 'opaque'
Node 68719476738: (IDENTIFIER) 's'
Node 94489280512: (LOCAL) 'QEMUFileSocket *s'
Node 107374182400: (METHOD) 'static int socket_get_fd(void *opaque)  ...'
Node 111669149696: (METHOD_PARAMETER_IN) 'void *opaque'
Node 115964116992: (METHOD_PARAMETER_OUT) 'void *opaque'
Node 124554051584: (METHOD_RETURN) 'RET'
Node 128849018880: (MODIFIER) '<empty>'
Node 141733920768: (RETURN) 'return s->fd;'
The edge information of the code snippet is as follows:
Edge: Node 25769803776 -> AST -> Node 94489280512
Edge: Node 25769803776 -> AST -> Node 30064771072
Edge: Node 25769803776 -> AST -> Node 141733920768
Edge: Node 30064771072 -> ARGUMENT -> Node 68719476736
Edge: Node 30064771072 -> ARGUMENT -> Node 68719476737
Edge: Node 30064771072 -> AST -> Node 68719476736
Edge: Node 30064771072 -> AST -> Node 68719476737
Edge: Node 30064771072 -> CFG -> Node 68719476738
Edge: Node 30064771072 -> DOMINATE -> Node 68719476738
Edge: Node 30064771072 -> POST_DOMINATE -> Node 68719476737
Edge: Node 30064771072 -> REACHING_DEF -> Node 124554051584
Edge: Node 30064771073 -> ARGUMENT -> Node 68719476738
Edge: Node 30064771073 -> ARGUMENT -> Node 55834574848
Edge: Node 30064771073 -> AST -> Node 68719476738
Edge: Node 30064771073 -> AST -> Node 55834574848
Edge: Node 30064771073 -> CFG -> Node 141733920768
Edge: Node 30064771073 -> DOMINATE -> Node 141733920768
Edge: Node 30064771073 -> POST_DOMINATE -> Node 55834574848
Edge: Node 30064771073 -> REACHING_DEF -> Node 141733920768
Edge: Node 55834574848 -> CFG -> Node 30064771073
Edge: Node 55834574848 -> DOMINATE -> Node 30064771073
Edge: Node 55834574848 -> POST_DOMINATE -> Node 68719476738
Edge: Node 68719476736 -> CFG -> Node 68719476737
Edge: Node 68719476736 -> DOMINATE -> Node 68719476737
Edge: Node 68719476736 -> POST_DOMINATE -> Node 107374182400
Edge: Node 68719476736 -> REACHING_DEF -> Node 30064771072
Edge: Node 68719476736 -> REACHING_DEF -> Node 68719476738
Edge: Node 68719476736 -> REACHING_DEF -> Node 30064771073
Edge: Node 68719476736 -> REACHING_DEF -> Node 124554051584
Edge: Node 68719476736 -> REF -> Node 94489280512
Edge: Node 68719476737 -> CFG -> Node 30064771072
Edge: Node 68719476737 -> DOMINATE -> Node 30064771072
Edge: Node 68719476737 -> POST_DOMINATE -> Node 68719476736
Edge: Node 68719476737 -> REACHING_DEF -> Node 68719476736

The following is an example, and it is .


Answer (0 or 1):
~~~~

## 3. devign:test:18384

Arm: B2; phiên: frozen; seed: 42; dataset/split: devign/test.
SHA-256 prompt: `56c46f70879973c6fbe7d34e1ba626d95fb0f24f4bec8f6fa4a3e95d36b8cedd`

~~~~text
You are now an excellent programmer. You are conducting a function vulnerability detection task for C/C++ language.

static void blk_send(QEMUFile *f, BlkMigBlock * blk)

{

    int len;

    uint64_t flags = BLK_MIG_FLAG_DEVICE_BLOCK;



    if (block_mig_state.zero_blocks &&

        buffer_is_zero(blk->buf, BLOCK_SIZE)) {

        flags |= BLK_MIG_FLAG_ZERO_BLOCK;

    }



    /* sector number and flags */

    qemu_put_be64(f, (blk->sector << BDRV_SECTOR_BITS)

                     | flags);



    /* device name */

    len = strlen(bdrv_get_device_name(blk->bmds->bs));

    qemu_put_byte(f, len);

    qemu_put_buffer(f, (uint8_t *)bdrv_get_device_name(blk->bmds->bs), len);



    /* if a block is zero we need to flush here since the network

     * bandwidth is now a lot higher than the storage device bandwidth.

     * thus if we queue zero blocks we slow down the migration */

    if (flags & BLK_MIG_FLAG_ZERO_BLOCK) {

        qemu_fflush(f);

        return;

    }



    qemu_put_buffer(f, blk->buf, BLOCK_SIZE);

}

In the above code snippet, check for potential security vulnerabilities and answer with a single digit: 1 if Vulnerable, 0 if Non-vulnerable.

The node information of the code snippet is as follows:
Node 25769803813: (BLOCK) '{      int len;      uint64_t flags = BL...'
Node 25769803814: (BLOCK) '{ flags |= BLK_MIG_FLAG_ZERO_BLOCK; }'
Node 25769803815: (BLOCK) '{ qemu_fflush(f); return; }'
Node 30064771309: (CALL) 'flags = BLK_MIG_FLAG_DEVICE_BLOCK'
Node 30064771310: (CALL) 'block_mig_state.zero_blocks && buffer_is...'
Node 30064771311: (CALL) 'block_mig_state.zero_blocks'
Node 30064771312: (CALL) 'buffer_is_zero(blk->buf, BLOCK_SIZE)'
Node 30064771313: (CALL) 'blk->buf'
Node 30064771314: (CALL) 'flags |= BLK_MIG_FLAG_ZERO_BLOCK'
Node 30064771315: (CALL) 'qemu_put_be64(f, (blk->sector << BDRV_SE...'
Node 30064771316: (CALL) '(blk->sector << BDRV_SECTOR_BITS) flags'
Node 30064771317: (CALL) 'blk->sector << BDRV_SECTOR_BITS'
Node 30064771318: (CALL) 'blk->sector'
Node 30064771319: (CALL) 'len = strlen(bdrv_get_device_name(blk->b...'
Node 30064771320: (CALL) 'strlen(bdrv_get_device_name(blk->bmds->b...'
Node 30064771321: (CALL) 'bdrv_get_device_name(blk->bmds->bs)'
Node 30064771322: (CALL) 'blk->bmds->bs'
Node 30064771323: (CALL) 'blk->bmds'
Node 30064771324: (CALL) 'qemu_put_byte(f, len)'
Node 30064771325: (CALL) 'qemu_put_buffer(f, (uint8_t *)bdrv_get_d...'
Node 30064771326: (CALL) '(uint8_t *)bdrv_get_device_name(blk->bmd...'
Node 30064771327: (CALL) 'bdrv_get_device_name(blk->bmds->bs)'
Node 30064771328: (CALL) 'blk->bmds->bs'
Node 30064771329: (CALL) 'blk->bmds'
Node 30064771330: (CALL) 'flags & BLK_MIG_FLAG_ZERO_BLOCK'
Node 30064771331: (CALL) 'qemu_fflush(f)'
Node 30064771332: (CALL) 'qemu_put_buffer(f, blk->buf, BLOCK_SIZE)'
Node 30064771333: (CALL) 'blk->buf'
Node 47244640280: (CONTROL_STRUCTURE) 'if (block_mig_state.zero_blocks &&      ...'
Node 47244640281: (CONTROL_STRUCTURE) 'if (flags & BLK_MIG_FLAG_ZERO_BLOCK) { q...'
Node 55834574923: (FIELD_IDENTIFIER) 'zero_blocks'
Node 55834574924: (FIELD_IDENTIFIER) 'buf'
Node 55834574925: (FIELD_IDENTIFIER) 'sector'
Node 55834574926: (FIELD_IDENTIFIER) 'bmds'
Node 55834574927: (FIELD_IDENTIFIER) 'bs'
Node 55834574928: (FIELD_IDENTIFIER) 'bmds'
Node 55834574929: (FIELD_IDENTIFIER) 'bs'
Node 55834574930: (FIELD_IDENTIFIER) 'buf'
Node 68719476947: (IDENTIFIER) 'flags'
Node 68719476948: (IDENTIFIER) '<unknown> BLK_MIG_FLAG_DEVICE_BLOCK'
The edge information of the code snippet is as follows:
Edge: Node 25769803813 -> AST -> Node 30064771309
Edge: Node 25769803813 -> AST -> Node 47244640280
Edge: Node 25769803813 -> AST -> Node 30064771315
Edge: Node 25769803813 -> AST -> Node 30064771319
Edge: Node 25769803813 -> AST -> Node 30064771324
Edge: Node 25769803813 -> AST -> Node 30064771325
Edge: Node 25769803813 -> AST -> Node 47244640281
Edge: Node 25769803813 -> AST -> Node 30064771332
Edge: Node 25769803814 -> AST -> Node 30064771314
Edge: Node 25769803815 -> AST -> Node 30064771331
Edge: Node 30064771309 -> ARGUMENT -> Node 68719476947
Edge: Node 30064771309 -> ARGUMENT -> Node 68719476948

The following is an example, and it is Non-vulnerable.
static int block_save_complete(QEMUFile *f, void *opaque)

{

    int ret;



    DPRINTF("Enter save live complete submitted %d transferred %d\n",

            block_mig_state.submitted, block_mig_state.transferred);



    ret = flush_blks(f);

    if (ret) {

        blk_mig_cleanup();

        return ret;

    }



    blk_mig_reset_dirty_cursor();



    /* we know for sure that save bulk is completed and

       all async read completed */

    assert(block_mig_state.submitted == 0);



    do {

        ret = blk_mig_save_dirty_block(f, 0);

    } while (ret == 0);



    blk_mig_cleanup();

    if (ret) {

        return ret;

    }

    /* report completion */

    qemu_put_be64(f, (100 << BDRV_SECTOR_BITS) | BLK_MIG_FLAG_PROGRESS);



    DPRINTF("Block migration completed\n");



    qemu_put_be64(f, BLK_MIG_FLAG_EOS);



    return 0;

}

Answer (0 or 1):
~~~~

## 4. devign:test:10721

Arm: B2; phiên: legacy; seed: 42; dataset/split: devign/test.
SHA-256 prompt: `c9c045c6b3b3a412e98868dc35fa2caf64062e769a64957728d3f7c1ffbc6b6f`

~~~~text
You are now an excellent programmer. You are conducting a function vulnerability detection task for C/C++ language.

static inline void gen_op_movl_seg_T0_vm(int seg_reg)

{

    tcg_gen_andi_tl(cpu_T[0], cpu_T[0], 0xffff);

    tcg_gen_st32_tl(cpu_T[0], cpu_env, 

                    offsetof(CPUX86State,segs[seg_reg].selector));

    tcg_gen_shli_tl(cpu_T[0], cpu_T[0], 4);

    tcg_gen_st_tl(cpu_T[0], cpu_env, 

                  offsetof(CPUX86State,segs[seg_reg].base));

}

In the above code snippet, check for potential security vulnerabilities and answer with a single digit: 1 if Vulnerable, 0 if Non-vulnerable.

The node information of the code snippet is as follows:
Node 25769803886: (BLOCK) '{      tcg_gen_andi_tl(cpu_T[0], cpu_T[0...'
Node 30064772216: (CALL) 'tcg_gen_andi_tl(cpu_T[0], cpu_T[0], 0xff...'
Node 30064772217: (CALL) 'cpu_T[0]'
Node 30064772218: (CALL) 'cpu_T[0]'
Node 30064772219: (CALL) 'tcg_gen_st32_tl(cpu_T[0], cpu_env, offse...'
Node 30064772220: (CALL) 'cpu_T[0]'
Node 30064772221: (CALL) 'offsetof(CPUX86State,segs[seg_reg].selec...'
Node 30064772222: (CALL) 'segs[seg_reg].selector'
Node 30064772223: (CALL) 'segs[seg_reg]'
Node 30064772224: (CALL) 'tcg_gen_shli_tl(cpu_T[0], cpu_T[0], 4)'
Node 30064772225: (CALL) 'cpu_T[0]'
Node 30064772226: (CALL) 'cpu_T[0]'
Node 30064772227: (CALL) 'tcg_gen_st_tl(cpu_T[0], cpu_env, offseto...'
Node 30064772228: (CALL) 'cpu_T[0]'
Node 30064772229: (CALL) 'offsetof(CPUX86State,segs[seg_reg].base)'
Node 30064772230: (CALL) 'segs[seg_reg].base'
Node 30064772231: (CALL) 'segs[seg_reg]'
Node 55834575223: (FIELD_IDENTIFIER) 'selector'
Node 55834575224: (FIELD_IDENTIFIER) 'base'
Node 68719477539: (IDENTIFIER) '<unknown> cpu_T'
Node 68719477540: (IDENTIFIER) '<unknown> cpu_T'
Node 68719477541: (IDENTIFIER) '<unknown> cpu_T'
Node 68719477542: (IDENTIFIER) '<unknown> cpu_env'
Node 68719477543: (IDENTIFIER) '<unknown> CPUX86State'
Node 68719477544: (IDENTIFIER) '<unknown> segs'
Node 68719477545: (IDENTIFIER) 'seg_reg'
Node 68719477546: (IDENTIFIER) '<unknown> cpu_T'
Node 68719477547: (IDENTIFIER) '<unknown> cpu_T'
Node 68719477548: (IDENTIFIER) '<unknown> cpu_T'
Node 68719477549: (IDENTIFIER) '<unknown> cpu_env'
Node 68719477550: (IDENTIFIER) '<unknown> CPUX86State'
Node 68719477551: (IDENTIFIER) '<unknown> segs'
Node 68719477552: (IDENTIFIER) 'seg_reg'
Node 90194313694: (LITERAL) '0'
Node 90194313695: (LITERAL) '0'
Node 90194313696: (LITERAL) '0xffff'
Node 90194313697: (LITERAL) '0'
Node 90194313698: (LITERAL) '0'
Node 90194313699: (LITERAL) '0'
Node 90194313700: (LITERAL) '4'
The edge information of the code snippet is as follows:
Edge: Node 25769803886 -> AST -> Node 30064772216
Edge: Node 25769803886 -> AST -> Node 30064772219
Edge: Node 25769803886 -> AST -> Node 30064772224
Edge: Node 25769803886 -> AST -> Node 30064772227
Edge: Node 30064772216 -> ARGUMENT -> Node 30064772217
Edge: Node 30064772216 -> ARGUMENT -> Node 30064772218
Edge: Node 30064772216 -> ARGUMENT -> Node 90194313696
Edge: Node 30064772216 -> AST -> Node 30064772217
Edge: Node 30064772216 -> AST -> Node 30064772218
Edge: Node 30064772216 -> AST -> Node 90194313696
Edge: Node 30064772216 -> CFG -> Node 68719477541
Edge: Node 30064772216 -> DOMINATE -> Node 68719477541
Edge: Node 30064772216 -> POST_DOMINATE -> Node 90194313696
Edge: Node 30064772217 -> ARGUMENT -> Node 68719477539

The following is an example, and it is Non-vulnerable.
static inline void gen_op_addq_ESP_im(int32_t val)

{

    tcg_gen_ld_tl(cpu_tmp0, cpu_env, offsetof(CPUState, regs[R_ESP]));

    tcg_gen_addi_tl(cpu_tmp0, cpu_tmp0, val);

    tcg_gen_st_tl(cpu_tmp0, cpu_env, offsetof(CPUState, regs[R_ESP]));

}

Answer (0 or 1):
~~~~

## 5. devign:test:14842

Arm: B2-flip; phiên: frozen; seed: 42; dataset/split: devign/test.
SHA-256 prompt: `9309e2e5f649249e4b9bc333e6f065c6df091133edb33eba98c1471e958c7556`

~~~~text
You are now an excellent programmer. You are conducting a function vulnerability detection task for C/C++ language.

static inline int open_by_handle(int mountfd, const char *fh, int flags)

{

    errno = ENOSYS;

    return -1;

}

In the above code snippet, check for potential security vulnerabilities and answer with a single digit: 1 if Vulnerable, 0 if Non-vulnerable.

The node information of the code snippet is as follows:
Node 25769803776: (BLOCK) '{ errno = ENOSYS; return -1; }'
Node 30064771072: (CALL) 'errno = ENOSYS'
Node 30064771073: (CALL) '-1'
Node 68719476736: (IDENTIFIER) '<unknown> errno'
Node 68719476737: (IDENTIFIER) '<unknown> ENOSYS'
Node 90194313216: (LITERAL) '1'
Node 94489280512: (LOCAL) '<unknown> ENOSYS'
Node 94489280513: (LOCAL) '<unknown> errno'
Node 107374182400: (METHOD) 'static inline int open_by_handle(int mou...'
Node 111669149696: (METHOD_PARAMETER_IN) 'int mountfd'
Node 111669149697: (METHOD_PARAMETER_IN) 'const char *fh'
Node 111669149698: (METHOD_PARAMETER_IN) 'int flags'
Node 115964116992: (METHOD_PARAMETER_OUT) 'int mountfd'
Node 115964116993: (METHOD_PARAMETER_OUT) 'const char *fh'
Node 115964116994: (METHOD_PARAMETER_OUT) 'int flags'
Node 124554051584: (METHOD_RETURN) 'RET'
Node 128849018880: (MODIFIER) '<empty>'
Node 141733920768: (RETURN) 'return -1;'
The edge information of the code snippet is as follows:
Edge: Node 25769803776 -> AST -> Node 30064771072
Edge: Node 25769803776 -> AST -> Node 141733920768
Edge: Node 25769803776 -> AST -> Node 94489280512
Edge: Node 25769803776 -> AST -> Node 94489280513
Edge: Node 30064771072 -> ARGUMENT -> Node 68719476736
Edge: Node 30064771072 -> ARGUMENT -> Node 68719476737
Edge: Node 30064771072 -> AST -> Node 68719476736
Edge: Node 30064771072 -> AST -> Node 68719476737
Edge: Node 30064771072 -> CFG -> Node 90194313216
Edge: Node 30064771072 -> DOMINATE -> Node 90194313216
Edge: Node 30064771072 -> POST_DOMINATE -> Node 68719476737
Edge: Node 30064771072 -> REACHING_DEF -> Node 124554051584
Edge: Node 30064771073 -> ARGUMENT -> Node 90194313216
Edge: Node 30064771073 -> AST -> Node 90194313216
Edge: Node 30064771073 -> CFG -> Node 141733920768
Edge: Node 30064771073 -> DOMINATE -> Node 141733920768
Edge: Node 30064771073 -> POST_DOMINATE -> Node 90194313216
Edge: Node 30064771073 -> REACHING_DEF -> Node 141733920768
Edge: Node 30064771073 -> REACHING_DEF -> Node 124554051584
Edge: Node 68719476736 -> CFG -> Node 68719476737
Edge: Node 68719476736 -> DOMINATE -> Node 68719476737
Edge: Node 68719476736 -> POST_DOMINATE -> Node 107374182400
Edge: Node 68719476736 -> REACHING_DEF -> Node 30064771072
Edge: Node 68719476736 -> REACHING_DEF -> Node 124554051584
Edge: Node 68719476736 -> REF -> Node 94489280513
Edge: Node 68719476737 -> CFG -> Node 30064771072
Edge: Node 68719476737 -> DOMINATE -> Node 30064771072
Edge: Node 68719476737 -> POST_DOMINATE -> Node 68719476736
Edge: Node 68719476737 -> REACHING_DEF -> Node 68719476736
Edge: Node 68719476737 -> REACHING_DEF -> Node 30064771072

The following is an example, and it is Vulnerable.
static int v9fs_synth_rename(FsContext *ctx, const char *oldpath,

                             const char *newpath)

{

    errno = EPERM;

    return -1;

}

Answer (0 or 1):
~~~~

## 6. devign:test:2400

Arm: B2-flip; phiên: legacy; seed: 42; dataset/split: devign/test.
SHA-256 prompt: `4cbe0c47a3f0460d53b3704b633280bd16fa20fd2805e80cd73257b10bb5c11f`

~~~~text
You are now an excellent programmer. You are conducting a function vulnerability detection task for C/C++ language.

static int add_candidate_ref(HEVCContext *s, RefPicList *list,

                             int poc, int ref_flag)

{

    HEVCFrame *ref = find_ref_idx(s, poc);



    if (ref == s->ref)

        return AVERROR_INVALIDDATA;



    if (!ref) {

        ref = generate_missing_ref(s, poc);

        if (!ref)

            return AVERROR(ENOMEM);

    }



    list->list[list->nb_refs] = ref->poc;

    list->ref[list->nb_refs]  = ref;

    list->nb_refs++;



    mark_ref(ref, ref_flag);

    return 0;

}

In the above code snippet, check for potential security vulnerabilities and answer with a single digit: 1 if Vulnerable, 0 if Non-vulnerable.

The node information of the code snippet is as follows:
Node 25769803882: (BLOCK) '{      HEVCFrame *ref = find_ref_idx(s, ...'
Node 25769803883: (BLOCK) '<empty>'
Node 25769803884: (BLOCK) '{ ref = generate_missing_ref(s, poc); if...'
Node 25769803885: (BLOCK) '<empty>'
Node 30064771929: (CALL) 'ref = find_ref_idx(s, poc)'
Node 30064771930: (CALL) 'find_ref_idx(s, poc)'
Node 30064771931: (CALL) 'ref == s->ref'
Node 30064771932: (CALL) 's->ref'
Node 30064771933: (CALL) '!ref'
Node 30064771934: (CALL) 'ref = generate_missing_ref(s, poc)'
Node 30064771935: (CALL) 'generate_missing_ref(s, poc)'
Node 30064771936: (CALL) '!ref'
Node 30064771937: (CALL) 'AVERROR(ENOMEM)'
Node 30064771938: (CALL) 'list->list[list->nb_refs] = ref->poc'
Node 30064771939: (CALL) 'list->list[list->nb_refs]'
Node 30064771940: (CALL) 'list->list'
Node 30064771941: (CALL) 'list->nb_refs'
Node 30064771942: (CALL) 'ref->poc'
Node 30064771943: (CALL) 'list->ref[list->nb_refs] = ref'
Node 30064771944: (CALL) 'list->ref[list->nb_refs]'
Node 30064771945: (CALL) 'list->ref'
Node 30064771946: (CALL) 'list->nb_refs'
Node 30064771947: (CALL) 'list->nb_refs++'
Node 30064771948: (CALL) 'list->nb_refs'
Node 30064771949: (CALL) 'mark_ref(ref, ref_flag)'
Node 47244640371: (CONTROL_STRUCTURE) 'if (ref == s->ref) return AVERROR_INVALI...'
Node 47244640372: (CONTROL_STRUCTURE) 'if (!ref) {          ref = generate_miss...'
Node 47244640373: (CONTROL_STRUCTURE) 'if (!ref) return AVERROR(ENOMEM);'
Node 55834575142: (FIELD_IDENTIFIER) 'ref'
Node 55834575143: (FIELD_IDENTIFIER) 'list'
Node 55834575144: (FIELD_IDENTIFIER) 'nb_refs'
Node 55834575145: (FIELD_IDENTIFIER) 'poc'
Node 55834575146: (FIELD_IDENTIFIER) 'ref'
Node 55834575147: (FIELD_IDENTIFIER) 'nb_refs'
Node 55834575148: (FIELD_IDENTIFIER) 'nb_refs'
Node 68719477440: (IDENTIFIER) 'ref'
Node 68719477441: (IDENTIFIER) 's'
Node 68719477442: (IDENTIFIER) 'poc'
Node 68719477443: (IDENTIFIER) 'ref'
Node 68719477444: (IDENTIFIER) 's'
The edge information of the code snippet is as follows:
Edge: Node 25769803882 -> AST -> Node 30064771929
Edge: Node 25769803882 -> AST -> Node 47244640371
Edge: Node 25769803882 -> AST -> Node 47244640372
Edge: Node 25769803882 -> AST -> Node 30064771938
Edge: Node 25769803882 -> AST -> Node 30064771943
Edge: Node 25769803882 -> AST -> Node 30064771947
Edge: Node 25769803882 -> AST -> Node 30064771949
Edge: Node 25769803884 -> AST -> Node 30064771934
Edge: Node 25769803884 -> AST -> Node 47244640373
Edge: Node 30064771929 -> ARGUMENT -> Node 68719477440
Edge: Node 30064771929 -> ARGUMENT -> Node 30064771930
Edge: Node 30064771929 -> AST -> Node 68719477440
Edge: Node 30064771929 -> AST -> Node 30064771930
Edge: Node 30064771929 -> CFG -> Node 68719477443
Edge: Node 30064771929 -> DOMINATE -> Node 68719477443

The following is an example, and it is Vulnerable.
static av_always_inline void dist_scale(HEVCContext *s, Mv *mv,

                                        int min_pu_width, int x, int y,

                                        int elist, int ref_idx_curr, int ref_idx)

{

    RefPicList *refPicList = s->ref->refPicList;

    MvField *tab_mvf       = s->ref->tab_mvf;

    int ref_pic_elist      = refPicList[elist].list[TAB_MVF(x, y).ref_idx[elist]];

    int ref_pic_curr       = refPicList[ref_idx_curr].list[ref_idx];



    if (ref_pic_elist != ref_pic_curr)

        mv_scale(mv, mv, s->poc - ref_pic_elist, s->poc - ref_pic_curr);

}

Answer (0 or 1):
~~~~

## 7. devign:test:27100

Arm: B2-rand; phiên: frozen; seed: 42; dataset/split: devign/test.
SHA-256 prompt: `5a6fbe3b3f6303e3576f8e6335d4d17e156fcd963c6055afc23c69a49874676a`

~~~~text
You are now an excellent programmer. You are conducting a function vulnerability detection task for C/C++ language.

static bool try_poll_mode(AioContext *ctx, bool blocking)

{

    if (blocking && ctx->poll_max_ns && ctx->poll_disable_cnt == 0) {

        /* See qemu_soonest_timeout() uint64_t hack */

        int64_t max_ns = MIN((uint64_t)aio_compute_timeout(ctx),

                             (uint64_t)ctx->poll_ns);



        if (max_ns) {

            poll_set_started(ctx, true);



            if (run_poll_handlers(ctx, max_ns)) {

                return true;

            }

        }

    }



    poll_set_started(ctx, false);



    /* Even if we don't run busy polling, try polling once in case it can make

     * progress and the caller will be able to avoid ppoll(2)/epoll_wait(2).

     */

    return run_poll_handlers_once(ctx);

}

In the above code snippet, check for potential security vulnerabilities and answer with a single digit: 1 if Vulnerable, 0 if Non-vulnerable.

The node information of the code snippet is as follows:
Node 25769803785: (BLOCK) '{      if (blocking && ctx->poll_max_ns ...'
Node 25769803786: (BLOCK) '{          /* See qemu_soonest_timeout()...'
Node 25769803787: (BLOCK) '{              poll_set_started(ctx, tru...'
Node 25769803788: (BLOCK) '{ return true; }'
Node 30064771116: (CALL) 'blocking && ctx->poll_max_ns && ctx->pol...'
Node 30064771117: (CALL) 'blocking && ctx->poll_max_ns'
Node 30064771118: (CALL) 'ctx->poll_max_ns'
Node 30064771119: (CALL) 'ctx->poll_disable_cnt == 0'
Node 30064771120: (CALL) 'ctx->poll_disable_cnt'
Node 30064771121: (CALL) 'max_ns = MIN((uint64_t)aio_compute_timeo...'
Node 30064771122: (CALL) 'MIN((uint64_t)aio_compute_timeout(ctx), ...'
Node 30064771123: (CALL) '(uint64_t)aio_compute_timeout(ctx)'
Node 30064771124: (CALL) 'aio_compute_timeout(ctx)'
Node 30064771125: (CALL) '(uint64_t)ctx->poll_ns'
Node 30064771126: (CALL) 'ctx->poll_ns'
Node 30064771127: (CALL) 'max_ns != 0'
Node 30064771128: (CALL) 'poll_set_started(ctx, true)'
Node 30064771129: (CALL) 'run_poll_handlers(ctx, max_ns)'
Node 30064771130: (CALL) 'poll_set_started(ctx, false)'
Node 30064771131: (CALL) 'run_poll_handlers_once(ctx)'
Node 47244640260: (CONTROL_STRUCTURE) 'if (blocking && ctx->poll_max_ns && ctx-...'
Node 47244640261: (CONTROL_STRUCTURE) 'if (max_ns) {              poll_set_star...'
Node 47244640262: (CONTROL_STRUCTURE) 'if (run_poll_handlers(ctx, max_ns)) { re...'
Node 55834574848: (FIELD_IDENTIFIER) 'poll_max_ns'
Node 55834574849: (FIELD_IDENTIFIER) 'poll_disable_cnt'
Node 55834574850: (FIELD_IDENTIFIER) 'poll_ns'
Node 68719476779: (IDENTIFIER) 'blocking'
Node 68719476780: (IDENTIFIER) 'ctx'
Node 68719476781: (IDENTIFIER) 'ctx'
Node 68719476782: (IDENTIFIER) 'max_ns'
Node 68719476783: (IDENTIFIER) 'ctx'
Node 68719476784: (IDENTIFIER) 'ctx'
Node 68719476785: (IDENTIFIER) 'max_ns'
Node 68719476786: (IDENTIFIER) 'ctx'
Node 68719476787: (IDENTIFIER) '<unknown> true'
Node 68719476788: (IDENTIFIER) 'ctx'
Node 68719476789: (IDENTIFIER) 'max_ns'
Node 68719476790: (IDENTIFIER) '<unknown> true'
Node 68719476791: (IDENTIFIER) 'ctx'
Node 68719476792: (IDENTIFIER) '<unknown> false'
The edge information of the code snippet is as follows:
Edge: Node 25769803785 -> AST -> Node 47244640260
Edge: Node 25769803785 -> AST -> Node 30064771130
Edge: Node 25769803786 -> AST -> Node 30064771121
Edge: Node 25769803786 -> AST -> Node 47244640261
Edge: Node 25769803787 -> AST -> Node 30064771128
Edge: Node 25769803787 -> AST -> Node 47244640262
Edge: Node 30064771116 -> ARGUMENT -> Node 30064771117
Edge: Node 30064771116 -> ARGUMENT -> Node 30064771119
Edge: Node 30064771116 -> AST -> Node 30064771117
Edge: Node 30064771116 -> AST -> Node 30064771119
Edge: Node 30064771116 -> CDG -> Node 30064771121
Edge: Node 30064771116 -> CDG -> Node 30064771122
Edge: Node 30064771116 -> CDG -> Node 68719476792
Edge: Node 30064771116 -> CDG -> Node 68719476791

The following is an example, and it is Non-vulnerable.
static void sun4m_load_kernel(long vram_size, int ram_size, int boot_device,

                              const char *kernel_filename,

                              const char *kernel_cmdline,

                              const char *initrd_filename,

                              int machine_id)

{

    int ret, linux_boot;

    char buf[1024];

    unsigned int i;

    long prom_offset, initrd_size, kernel_size;



    linux_boot = (kernel_filename != NULL);



    prom_offset = ram_size + vram_size;

    cpu_register_physical_memory(PROM_ADDR, 

                                 (PROM_SIZE_MAX + TARGET_PAGE_SIZE - 1) & TARGET_PAGE_MASK, 

                                 prom_offset | IO_MEM_ROM);



    snprintf(buf, sizeof(buf), "%s/%s", bios_dir, PROM_FILENAME);

    ret = load_elf(buf, 0, NULL, NULL, NULL);

    if (ret < 0) {

	fprintf(stderr, "qemu: could not load prom '%s'\n", 

		buf);

	exit(1);

    }



    kernel_size = 0;

    if (linux_boot) {

        kernel_size = load_elf(kernel_filename, -0xf0000000, NULL, NULL, NULL);

        if (kernel_size < 0)

	    kernel_size = load_aout(kernel_filename, phys_ram_base + KERNEL_LOAD_ADDR);

	if (kernel_size < 0)

	    kernel_size = load_image(kernel_filename, phys_ram_base + KERNEL_LOAD_ADDR);

        if (kernel_size < 0) {

            fprintf(stderr, "qemu: could not load kernel '%s'\n", 

                    kernel_filename);

	    exit(1);

        }



        /* load initrd */

        initrd_size = 0;

        if (initrd_filename) {

            initrd_size = load_image(initrd_filename, phys_ram_base + INITRD_LOAD_ADDR);

            if (initrd_size < 0) {

                fprintf(stderr, "qemu: could not load initial ram disk '%s'\n", 

                        initrd_filename);

                exit(1);

            }

        }

        if (initrd_size > 0) {

	    for (i = 0; i < 64 * TARGET_PAGE_SIZE; i += TARGET_PAGE_SIZE) {

		if (ldl_raw(phys_ram_base + KERNEL_LOAD_ADDR + i)

		    == 0x48647253) { // HdrS

		    stl_raw(phys_ram_base + KERNEL_LOAD_ADDR + i + 16, INITRD_LOAD_ADDR);

		    stl_raw(phys_ram_base + KERNEL_LOAD_ADDR + i + 20, initrd_size);

		    break;

		}

	    }

        }

    }

    nvram_init(nvram, (uint8_t *)&nd_table[0].macaddr, kernel_cmdline,

               boot_device, ram_size, kernel_size, graphic_width,

               graphic_height, graphic_depth, machine_id);

}

Answer (0 or 1):
~~~~

## 8. devign:validation:7180

Arm: B2-rand; phiên: frozen; seed: 43; dataset/split: devign/validation.
SHA-256 prompt: `b72342b3671167ec90efba27bfb8ae98f8e6284c6d7dca50dfe133197207fc10`

~~~~text
You are now an excellent programmer. You are conducting a function vulnerability detection task for C/C++ language.

static void tcg_out_qemu_st_slow_path(TCGContext *s, TCGLabelQemuLdst *l)

{

    TCGMemOp opc = l->opc;

    TCGMemOp s_bits = opc & MO_SIZE;

    uint8_t **label_ptr = &l->label_ptr[0];

    TCGReg retaddr;



    /* resolve label address */

    *(uint32_t *)label_ptr[0] = (uint32_t)(s->code_ptr - label_ptr[0] - 4);

    if (TARGET_LONG_BITS > TCG_TARGET_REG_BITS) {

        *(uint32_t *)label_ptr[1] = (uint32_t)(s->code_ptr - label_ptr[1] - 4);

    }



    if (TCG_TARGET_REG_BITS == 32) {

        int ofs = 0;



        tcg_out_st(s, TCG_TYPE_PTR, TCG_AREG0, TCG_REG_ESP, ofs);

        ofs += 4;



        tcg_out_st(s, TCG_TYPE_I32, l->addrlo_reg, TCG_REG_ESP, ofs);

        ofs += 4;



        if (TARGET_LONG_BITS == 64) {

            tcg_out_st(s, TCG_TYPE_I32, l->addrhi_reg, TCG_REG_ESP, ofs);

            ofs += 4;

        }



        tcg_out_st(s, TCG_TYPE_I32, l->datalo_reg, TCG_REG_ESP, ofs);

        ofs += 4;



        if (s_bits == MO_64) {

            tcg_out_st(s, TCG_TYPE_I32, l->datahi_reg, TCG_REG_ESP, ofs);

            ofs += 4;

        }



        tcg_out_sti(s, TCG_TYPE_I32, TCG_REG_ESP, ofs, l->mem_index);

        ofs += 4;



        retaddr = TCG_REG_EAX;

        tcg_out_movi(s, TCG_TYPE_I32, retaddr, (uintptr_t)l->raddr);

        tcg_out_st(s, TCG_TYPE_I32, retaddr, TCG_REG_ESP, ofs);

    } else {

        tcg_out_mov(s, TCG_TYPE_PTR, tcg_target_call_iarg_regs[0], TCG_AREG0);

        /* The second argument is already loaded with addrlo.  */

        tcg_out_mov(s, (s_bits == MO_64 ? TCG_TYPE_I64 : TCG_TYPE_I32),

                    tcg_target_call_iarg_regs[2], l->datalo_reg);

        tcg_out_movi(s, TCG_TYPE_I32, tcg_target_call_iarg_regs[3],

                     l->mem_index);



        if (ARRAY_SIZE(tcg_target_call_iarg_regs) > 4) {

            retaddr = tcg_target_call_iarg_regs[4];

            tcg_out_movi(s, TCG_TYPE_PTR, retaddr, (uintptr_t)l->raddr);

        } else {

            retaddr = TCG_REG_RAX;

            tcg_out_movi(s, TCG_TYPE_PTR, retaddr, (uintptr_t)l->raddr);

            tcg_out_st(s, TCG_TYPE_PTR, retaddr, TCG_REG_ESP, 0);

        }

    }



    /* "Tail call" to the helper, with the return address back inline.  */

    tcg_out_push(s, retaddr);

    tcg_out_jmp(s, (uintptr_t)qemu_st_helpers[opc]);

}

In the above code snippet, check for potential security vulnerabilities and answer with a single digit: 1 if Vulnerable, 0 if Non-vulnerable.

The node information of the code snippet is as follows:
Node 25769803776: (BLOCK) '{      TCGMemOp opc = l->opc;      TCGMe...'
Node 25769803777: (BLOCK) '{ *(uint32_t *)label_ptr[1] = (uint32_t)...'
Node 25769803778: (BLOCK) '{          int ofs = 0;            tcg_o...'
Node 25769803779: (BLOCK) '{ tcg_out_st(s, TCG_TYPE_I32, l->addrhi_...'
Node 25769803780: (BLOCK) '{ tcg_out_st(s, TCG_TYPE_I32, l->datahi_...'
Node 25769803781: (BLOCK) '{          tcg_out_mov(s, TCG_TYPE_PTR, ...'
Node 25769803782: (BLOCK) '{              retaddr = tcg_target_call...'
Node 25769803783: (BLOCK) '{              retaddr = TCG_REG_RAX;   ...'
Node 30064771072: (CALL) 'opc = l->opc'
Node 30064771073: (CALL) 'l->opc'
Node 30064771074: (CALL) 's_bits = opc & MO_SIZE'
Node 30064771075: (CALL) 'opc & MO_SIZE'
Node 30064771076: (CALL) 'label_ptr = &l->label_ptr[0]'
Node 30064771077: (CALL) '&l->label_ptr[0]'
Node 30064771078: (CALL) 'l->label_ptr[0]'
Node 30064771079: (CALL) 'l->label_ptr'
Node 30064771080: (CALL) '*(uint32_t *)label_ptr[0] = (uint32_t)(s...'
Node 30064771081: (CALL) '*(uint32_t *)label_ptr[0]'
Node 30064771082: (CALL) '(uint32_t *)label_ptr[0]'
Node 30064771083: (CALL) 'label_ptr[0]'
Node 30064771084: (CALL) '(uint32_t)(s->code_ptr - label_ptr[0] - ...'
Node 30064771085: (CALL) 's->code_ptr - label_ptr[0] - 4'
Node 30064771086: (CALL) 's->code_ptr - label_ptr[0]'
Node 30064771087: (CALL) 's->code_ptr'
Node 30064771088: (CALL) 'label_ptr[0]'
Node 30064771089: (CALL) 'TARGET_LONG_BITS > TCG_TARGET_REG_BITS'
Node 30064771090: (CALL) '*(uint32_t *)label_ptr[1] = (uint32_t)(s...'
Node 30064771091: (CALL) '*(uint32_t *)label_ptr[1]'
Node 30064771092: (CALL) '(uint32_t *)label_ptr[1]'
Node 30064771093: (CALL) 'label_ptr[1]'
Node 30064771094: (CALL) '(uint32_t)(s->code_ptr - label_ptr[1] - ...'
Node 30064771095: (CALL) 's->code_ptr - label_ptr[1] - 4'
Node 30064771096: (CALL) 's->code_ptr - label_ptr[1]'
Node 30064771097: (CALL) 's->code_ptr'
Node 30064771098: (CALL) 'label_ptr[1]'
Node 30064771099: (CALL) 'TCG_TARGET_REG_BITS == 32'
Node 30064771100: (CALL) 'ofs = 0'
Node 30064771101: (CALL) 'tcg_out_st(s, TCG_TYPE_PTR, TCG_AREG0, T...'
Node 30064771102: (CALL) 'ofs += 4'
Node 30064771103: (CALL) 'tcg_out_st(s, TCG_TYPE_I32, l->addrlo_re...'
The edge information of the code snippet is as follows:
Edge: Node 25769803776 -> AST -> Node 30064771072
Edge: Node 25769803776 -> AST -> Node 30064771074
Edge: Node 25769803776 -> AST -> Node 30064771076
Edge: Node 25769803776 -> AST -> Node 30064771080
Edge: Node 25769803777 -> AST -> Node 30064771090
Edge: Node 25769803778 -> AST -> Node 30064771100
Edge: Node 25769803778 -> AST -> Node 30064771101
Edge: Node 25769803778 -> AST -> Node 30064771102
Edge: Node 25769803778 -> AST -> Node 30064771103
Edge: Node 30064771072 -> ARGUMENT -> Node 30064771073

The following is an example, and it is Vulnerable.
static void read_len_table(uint8_t *dst, GetBitContext *gb){

    int i, val, repeat;



    for(i=0; i<256;){

        repeat= get_bits(gb, 3);

        val   = get_bits(gb, 5);

        if(repeat==0)

            repeat= get_bits(gb, 8);

//printf("%d %d\n", val, repeat);

        while (repeat--)

            dst[i++] = val;

    }

}

Answer (0 or 1):
~~~~

## 9. devign:validation:25051

Arm: B2-rand; phiên: frozen; seed: 44; dataset/split: devign/validation.
SHA-256 prompt: `42251c777279dc8cb71de957b1971165582f93e1caa6110e66f31b126145cc4a`

~~~~text
You are now an excellent programmer. You are conducting a function vulnerability detection task for C/C++ language.

int avfilter_graph_parse(AVFilterGraph *graph, const char *filters,

                         AVFilterInOut **open_inputs, AVFilterInOut **open_outputs,

                         void *log_ctx)

{

    int index = 0, ret;

    char chr = 0;



    AVFilterInOut *curr_inputs = NULL;



    do {

        AVFilterContext *filter;

        const char *filterchain = filters;

        filters += strspn(filters, WHITESPACES);



        if ((ret = parse_inputs(&filters, &curr_inputs, open_outputs, log_ctx)) < 0)

            goto fail;



        if ((ret = parse_filter(&filter, &filters, graph, index, log_ctx)) < 0)

            goto fail;



        if (filter->input_count == 1 && !curr_inputs && !index) {

            /* First input can be omitted if it is "[in]" */

            const char *tmp = "[in]";

            if ((ret = parse_inputs(&tmp, &curr_inputs, open_outputs, log_ctx)) < 0)

                goto fail;

        }



        if ((ret = link_filter_inouts(filter, &curr_inputs, open_inputs, log_ctx)) < 0)

            goto fail;



        if ((ret = parse_outputs(&filters, &curr_inputs, open_inputs, open_outputs,

                                 log_ctx)) < 0)

            goto fail;



        filters += strspn(filters, WHITESPACES);

        chr = *filters++;



        if (chr == ';' && curr_inputs) {

            av_log(log_ctx, AV_LOG_ERROR,

                   "Invalid filterchain containing an unlabelled output pad: \"%s\"\n",

                   filterchain);

            ret = AVERROR(EINVAL);

            goto fail;

        }

        index++;

    } while (chr == ',' || chr == ';');



    if (chr) {

        av_log(log_ctx, AV_LOG_ERROR,

               "Unable to parse graph description substring: \"%s\"\n",

               filters - 1);

        ret = AVERROR(EINVAL);

        goto fail;

    }



    if (*open_inputs && !strcmp((*open_inputs)->name, "out") && curr_inputs) {

        /* Last output can be omitted if it is "[out]" */

        const char *tmp = "[out]";

        if ((ret = parse_outputs(&tmp, &curr_inputs, open_inputs, open_outputs,

                                 log_ctx)) < 0)

            goto fail;

    }



    return 0;



 fail:

    for (; graph->filter_count > 0; graph->filter_count--)

        avfilter_free(graph->filters[graph->filter_count - 1]);

    av_freep(&graph->filters);

    avfilter_inout_free(open_inputs);

    avfilter_inout_free(open_outputs);

    avfilter_inout_free(&curr_inputs);

    return ret;

}

In the above code snippet, check for potential security vulnerabilities and answer with a single digit: 1 if Vulnerable, 0 if Non-vulnerable.

The node information of the code snippet is as follows:
Node 25769803776: (BLOCK) '{      int index = 0, ret;      char chr...'
Node 25769803777: (BLOCK) '{          AVFilterContext *filter;     ...'
Node 25769803778: (BLOCK) '<empty>'
Node 25769803779: (BLOCK) '<empty>'
Node 25769803780: (BLOCK) '{              /* First input can be omi...'
Node 25769803781: (BLOCK) '<empty>'
Node 25769803782: (BLOCK) '<empty>'
Node 25769803783: (BLOCK) '<empty>'
Node 25769803784: (BLOCK) '{              av_log(log_ctx, AV_LOG_ER...'
Node 25769803785: (BLOCK) '{          av_log(log_ctx, AV_LOG_ERROR,...'
Node 25769803786: (BLOCK) '{          /* Last output can be omitted...'
Node 25769803787: (BLOCK) '<empty>'
Node 25769803788: (BLOCK) '<empty>'
Node 30064771072: (CALL) 'index = 0'
Node 30064771073: (CALL) 'chr = 0'
Node 30064771074: (CALL) 'curr_inputs = NULL'
Node 30064771075: (CALL) 'filterchain = filters'
Node 30064771076: (CALL) 'filters += strspn(filters, WHITESPACES)'
Node 30064771077: (CALL) 'strspn(filters, WHITESPACES)'
Node 30064771078: (CALL) '(ret = parse_inputs(&filters, &curr_inpu...'
Node 30064771079: (CALL) 'ret = parse_inputs(&filters, &curr_input...'
Node 30064771080: (CALL) 'parse_inputs(&filters, &curr_inputs, ope...'
Node 30064771081: (CALL) '&filters'
Node 30064771082: (CALL) '&curr_inputs'
Node 30064771083: (CALL) '(ret = parse_filter(&filter, &filters, g...'
Node 30064771084: (CALL) 'ret = parse_filter(&filter, &filters, gr...'
Node 30064771085: (CALL) 'parse_filter(&filter, &filters, graph, i...'
Node 30064771086: (CALL) '&filter'
Node 30064771087: (CALL) '&filters'
Node 30064771088: (CALL) 'filter->input_count == 1 && !curr_inputs...'
Node 30064771089: (CALL) 'filter->input_count == 1 && !curr_inputs'
Node 30064771090: (CALL) 'filter->input_count == 1'
Node 30064771091: (CALL) 'filter->input_count'
Node 30064771092: (CALL) '!curr_inputs'
Node 30064771093: (CALL) '!index'
Node 30064771094: (CALL) 'tmp = "[in]"'
Node 30064771095: (CALL) '(ret = parse_inputs(&tmp, &curr_inputs, ...'
Node 30064771096: (CALL) 'ret = parse_inputs(&tmp, &curr_inputs, o...'
Node 30064771097: (CALL) 'parse_inputs(&tmp, &curr_inputs, open_ou...'
Node 30064771098: (CALL) '&tmp'
The edge information of the code snippet is as follows:
Edge: Node 25769803776 -> AST -> Node 30064771072
Edge: Node 25769803776 -> AST -> Node 30064771073
Edge: Node 25769803776 -> AST -> Node 30064771074
Edge: Node 25769803777 -> AST -> Node 30064771075
Edge: Node 25769803777 -> AST -> Node 30064771076
Edge: Node 25769803780 -> AST -> Node 30064771094
Edge: Node 30064771076 -> ARGUMENT -> Node 30064771077
Edge: Node 30064771076 -> AST -> Node 30064771077
Edge: Node 30064771076 -> POST_DOMINATE -> Node 30064771077
Edge: Node 30064771077 -> CFG -> Node 30064771076
Edge: Node 30064771077 -> DOMINATE -> Node 30064771076
Edge: Node 30064771077 -> REACHING_DEF -> Node 30064771076
Edge: Node 30064771078 -> ARGUMENT -> Node 30064771079
Edge: Node 30064771078 -> AST -> Node 30064771079

The following is an example, and it is Vulnerable.
static void raw_aio_writev_scrubbed(void *opaque, int ret)

{

    RawScrubberBounce *b = opaque;



    if (ret < 0) {

        b->cb(b->opaque, ret);

    } else {

        b->cb(b->opaque, ret + 512);

    }



    qemu_iovec_destroy(&b->qiov);

    qemu_free(b);

}

Answer (0 or 1):
~~~~

## 10. devign:test:14665

Arm: B2-rep; phiên: legacy; seed: 42; dataset/split: devign/test.
SHA-256 prompt: `fe0da0250bbb63b3b6e269c5b1f62163170ad9aba4af49a92700415515f84f23`

~~~~text
You are now an excellent programmer. You are conducting a function vulnerability detection task for C/C++ language.

static void picmemset(PicContext *s, AVFrame *frame, int value, int run,

                      int *x, int *y, int *plane, int bits_per_plane)

{

    uint8_t *d;

    int shift = *plane * bits_per_plane;

    int mask  = ((1 << bits_per_plane) - 1) << shift;

    value   <<= shift;



    while (run > 0) {

        int j;

        for (j = 8-bits_per_plane; j >= 0; j -= bits_per_plane) {

            d = frame->data[0] + *y * frame->linesize[0];

            d[*x] |= (value >> j) & mask;

            *x += 1;

            if (*x == s->width) {

                *y -= 1;

                *x = 0;

                if (*y < 0) {

                   *y = s->height - 1;

                   *plane += 1;

                   if (*plane >= s->nb_planes)

                       return;

                   value <<= bits_per_plane;

                   mask  <<= bits_per_plane;

                }

            }

        }

        run--;

    }

}

In the above code snippet, check for potential security vulnerabilities and answer with a single digit: 1 if Vulnerable, 0 if Non-vulnerable.

The node information of the code snippet is as follows:
Node 25769803777: (BLOCK) '{      uint8_t *d;      int shift = *pla...'
Node 25769803778: (BLOCK) '{          int j;          for (j = 8-bi...'
Node 25769803779: (BLOCK) '{              d = frame->data[0] + *y *...'
Node 25769803780: (BLOCK) '{                  *y -= 1;             ...'
Node 25769803781: (BLOCK) '{                     *y = s->height - 1...'
Node 25769803782: (BLOCK) '<empty>'
Node 30064771072: (CALL) 'shift = *plane * bits_per_plane'
Node 30064771073: (CALL) '*plane * bits_per_plane'
Node 30064771074: (CALL) '*plane'
Node 30064771075: (CALL) 'mask = ((1 << bits_per_plane) - 1) << sh...'
Node 30064771076: (CALL) '((1 << bits_per_plane) - 1) << shift'
Node 30064771077: (CALL) '(1 << bits_per_plane) - 1'
Node 30064771078: (CALL) '1 << bits_per_plane'
Node 30064771079: (CALL) 'value <<= shift'
Node 30064771080: (CALL) 'run > 0'
Node 30064771081: (CALL) 'j = 8-bits_per_plane'
Node 30064771082: (CALL) '8-bits_per_plane'
Node 30064771083: (CALL) 'j >= 0'
Node 30064771084: (CALL) 'j -= bits_per_plane'
Node 30064771085: (CALL) 'd = frame->data[0] + *y * frame->linesiz...'
Node 30064771086: (CALL) 'frame->data[0] + *y * frame->linesize[0]'
Node 30064771087: (CALL) 'frame->data[0]'
Node 30064771088: (CALL) 'frame->data'
Node 30064771089: (CALL) '*y * frame->linesize[0]'
Node 30064771090: (CALL) '*y'
Node 30064771091: (CALL) 'frame->linesize[0]'
Node 30064771092: (CALL) 'frame->linesize'
Node 30064771093: (CALL) 'd[*x] |= (value >> j) & mask'
Node 30064771094: (CALL) 'd[*x]'
Node 30064771095: (CALL) '*x'
Node 30064771096: (CALL) '(value >> j) & mask'
Node 30064771097: (CALL) 'value >> j'
Node 30064771098: (CALL) '*x += 1'
Node 30064771099: (CALL) '*x'
Node 30064771100: (CALL) '*x == s->width'
Node 30064771101: (CALL) '*x'
Node 30064771102: (CALL) 's->width'
Node 30064771103: (CALL) '*y -= 1'
Node 30064771104: (CALL) '*y'
Node 30064771105: (CALL) '*x = 0'
The edge information of the code snippet is as follows:
Edge: Node 25769803777 -> AST -> Node 30064771072
Edge: Node 25769803777 -> AST -> Node 30064771075
Edge: Node 25769803777 -> AST -> Node 30064771079
Edge: Node 25769803779 -> AST -> Node 30064771085
Edge: Node 25769803779 -> AST -> Node 30064771093
Edge: Node 25769803779 -> AST -> Node 30064771098
Edge: Node 25769803780 -> AST -> Node 30064771103
Edge: Node 25769803780 -> AST -> Node 30064771105
Edge: Node 30064771072 -> ARGUMENT -> Node 30064771073
Edge: Node 30064771072 -> AST -> Node 30064771073
Edge: Node 30064771072 -> POST_DOMINATE -> Node 30064771073
Edge: Node 30064771073 -> ARGUMENT -> Node 30064771074
Edge: Node 30064771073 -> AST -> Node 30064771074
Edge: Node 30064771073 -> CFG -> Node 30064771072

The following is an example, and it is Vulnerable.
static int get_bits(J2kDecoderContext *s, int n)

{

    int res = 0;

    if (s->buf_end - s->buf < ((n - s->bit_index) >> 8))

        return AVERROR(EINVAL);

    while (--n >= 0){

        res <<= 1;

        if (s->bit_index == 0){

            s->bit_index = 7 + (*s->buf != 0xff);

            s->buf++;

        }

        s->bit_index--;

        res |= (*s->buf >> s->bit_index) & 1;

    }

    return res;

}

Answer (0 or 1):
~~~~

## 11. devign:test:18812

Arm: B0; phiên: legacy; seed: 42; dataset/split: devign/test.
SHA-256 prompt: `3fde3d5054c80f6f0612b742018fd313fbe2754a7a97df17f229d9da77b6ec18`

~~~~text
You are now an excellent programmer. You are conducting a function vulnerability detection task for C/C++ language.

static int filter_frame(AVFilterLink *inlink, AVFrame *src_buffer)

{

    AVFilterContext  *ctx = inlink->dst;

    ATempoContext *atempo = ctx->priv;

    AVFilterLink *outlink = ctx->outputs[0];



    int ret = 0;

    int n_in = src_buffer->nb_samples;

    int n_out = (int)(0.5 + ((double)n_in) / atempo->tempo);



    const uint8_t *src = src_buffer->data[0];

    const uint8_t *src_end = src + n_in * atempo->stride;



    while (src < src_end) {

        if (!atempo->dst_buffer) {

            atempo->dst_buffer = ff_get_audio_buffer(outlink, n_out);

            if (!atempo->dst_buffer)

                return AVERROR(ENOMEM);

            av_frame_copy_props(atempo->dst_buffer, src_buffer);



            atempo->dst = atempo->dst_buffer->data[0];

            atempo->dst_end = atempo->dst + n_out * atempo->stride;

        }



        yae_apply(atempo, &src, src_end, &atempo->dst, atempo->dst_end);



        if (atempo->dst == atempo->dst_end) {

            int n_samples = ((atempo->dst - atempo->dst_buffer->data[0]) /

                             atempo->stride);

            ret = push_samples(atempo, outlink, n_samples);

            if (ret < 0)

                goto end;

        }

    }



    atempo->nsamples_in += n_in;

end:

    av_frame_free(&src_buffer);

    return ret;

}

In the above code snippet, check for potential security vulnerabilities and answer with a single digit: 1 if Vulnerable, 0 if Non-vulnerable.

The node information of the code snippet is as follows:

The edge information of the code snippet is as follows:


The following is an example, and it is .


Answer (0 or 1):
~~~~

## 12. devign:validation:4832

Arm: B2-rep; phiên: legacy; seed: 42; dataset/split: devign/validation.
SHA-256 prompt: `bc78d61451dbd714c77a60170ecf9aa56569c4fd8d034558b25d97c3c47ca048`

~~~~text
You are now an excellent programmer. You are conducting a function vulnerability detection task for C/C++ language.

uint32_t HELPER(neon_acgt_f32)(uint32_t a, uint32_t b)

{

    float32 f0 = float32_abs(make_float32(a));

    float32 f1 = float32_abs(make_float32(b));

    if (float32_compare_quiet(f0, f1, NFS) == float_relation_greater) {

        return ~0;

    }

    return 0;

}

In the above code snippet, check for potential security vulnerabilities and answer with a single digit: 1 if Vulnerable, 0 if Non-vulnerable.

The node information of the code snippet is as follows:
Node 25769803778: (BLOCK) '<empty>'
Node 107374182402: (METHOD) 'uint32_t HELPER(neon_acgt_f32)'
Node 111669149696: (METHOD_PARAMETER_IN) 'neon_acgt_f32'
Node 115964116992: (METHOD_PARAMETER_OUT) 'neon_acgt_f32'
Node 124554051586: (METHOD_RETURN) 'RET'
The edge information of the code snippet is as follows:
Edge: Node 107374182402 -> AST -> Node 111669149696
Edge: Node 107374182402 -> AST -> Node 25769803778
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
uint32_t HELPER(neon_max_f32)(uint32_t a, uint32_t b)

{

    float32 f0 = make_float32(a);

    float32 f1 = make_float32(b);

    return (float32_compare_quiet(f0, f1, NFS) == 1) ? a : b;

}

Answer (0 or 1):
~~~~

## 13. devign:test:11070

Arm: B0; phiên: legacy; seed: 42; dataset/split: devign/test.
SHA-256 prompt: `2260567ba1c36a08f16f16e13c4bb7c15c84aea07c003e1e81a9c832fc4d1a02`

~~~~text
You are now an excellent programmer. You are conducting a function vulnerability detection task for C/C++ language.

void qmp_guest_file_flush(int64_t handle, Error **errp)

{

    GuestFileHandle *gfh = guest_file_handle_find(handle, errp);

    FILE *fh;

    int ret;



    if (!gfh) {

        return;

    }



    fh = gfh->fh;

    ret = fflush(fh);

    if (ret == EOF) {

        error_setg_errno(errp, errno, "failed to flush file");



    }

}

In the above code snippet, check for potential security vulnerabilities and answer with a single digit: 1 if Vulnerable, 0 if Non-vulnerable.

The node information of the code snippet is as follows:

The edge information of the code snippet is as follows:


The following is an example, and it is .


Answer (0 or 1):
~~~~

## 14. devign:validation:6107

Arm: B0; phiên: legacy; seed: 42; dataset/split: devign/validation.
SHA-256 prompt: `8449ff2100321ae64cce6b64cf84f0396ff678cf182dd3bc4fbf986694cac5e1`

~~~~text
You are now an excellent programmer. You are conducting a function vulnerability detection task for C/C++ language.

static inline uint32_t vmsvga_fifo_read_raw(struct vmsvga_state_s *s)

{

    uint32_t cmd = s->fifo[CMD(stop) >> 2];



    s->cmd->stop = cpu_to_le32(CMD(stop) + 4);

    if (CMD(stop) >= CMD(max)) {

        s->cmd->stop = s->cmd->min;

    }

    return cmd;

}

In the above code snippet, check for potential security vulnerabilities and answer with a single digit: 1 if Vulnerable, 0 if Non-vulnerable.

The node information of the code snippet is as follows:

The edge information of the code snippet is as follows:


The following is an example, and it is .


Answer (0 or 1):
~~~~

## 15. devign:validation:15526

Arm: B2-flip; phiên: legacy; seed: 42; dataset/split: devign/validation.
SHA-256 prompt: `0c7bba3efa7ba9967142c94023b89d2d14d1359e780d7d6dca5d75f040620f38`

~~~~text
You are now an excellent programmer. You are conducting a function vulnerability detection task for C/C++ language.

void HELPER(wsr_lend)(uint32_t v)

{

    if (env->sregs[LEND] != v) {

        tb_invalidate_phys_page_range(

                env->sregs[LEND] - 1, env->sregs[LEND], 0);

        env->sregs[LEND] = v;

        tb_invalidate_phys_page_range(

                env->sregs[LEND] - 1, env->sregs[LEND], 0);

    }

}

In the above code snippet, check for potential security vulnerabilities and answer with a single digit: 1 if Vulnerable, 0 if Non-vulnerable.

The node information of the code snippet is as follows:
Node 25769803778: (BLOCK) '<empty>'
Node 107374182402: (METHOD) 'void HELPER(wsr_lend)'
Node 111669149696: (METHOD_PARAMETER_IN) 'wsr_lend'
Node 115964116992: (METHOD_PARAMETER_OUT) 'wsr_lend'
Node 124554051586: (METHOD_RETURN) 'RET'
The edge information of the code snippet is as follows:
Edge: Node 107374182402 -> AST -> Node 111669149696
Edge: Node 107374182402 -> AST -> Node 25769803778
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

The following is an example, and it is Vulnerable.
void HELPER(wsr_lbeg)(uint32_t v)

{

    if (env->sregs[LBEG] != v) {

        tb_invalidate_phys_page_range(

                env->sregs[LEND] - 1, env->sregs[LEND], 0);

        env->sregs[LBEG] = v;

    }

}

Answer (0 or 1):
~~~~

## 16. devign:test:5353

Arm: B2-rand; phiên: frozen; seed: 44; dataset/split: devign/test.
SHA-256 prompt: `a2196037be73df7bae0c9c1ac268e7fb2b4b2ed1575db1b90f96e1bc3ed94a54`

~~~~text
You are now an excellent programmer. You are conducting a function vulnerability detection task for C/C++ language.

void ff_er_frame_start(ERContext *s)

{

    if (!s->avctx->err_recognition)

        return;



    memset(s->error_status_table, ER_MB_ERROR | VP_START | ER_MB_END,

           s->mb_stride * s->mb_height * sizeof(uint8_t));

    s->error_count    = 3 * s->mb_num;

    s->error_occurred = 0;

}

In the above code snippet, check for potential security vulnerabilities and answer with a single digit: 1 if Vulnerable, 0 if Non-vulnerable.

The node information of the code snippet is as follows:
Node 25769803811: (BLOCK) '{      if (!s->avctx->err_recognition)  ...'
Node 25769803812: (BLOCK) '<empty>'
Node 30064771286: (CALL) '!s->avctx->err_recognition'
Node 30064771287: (CALL) 's->avctx->err_recognition'
Node 30064771288: (CALL) 's->avctx'
Node 30064771289: (CALL) 'memset(s->error_status_table, ER_MB_ERRO...'
Node 30064771290: (CALL) 's->error_status_table'
Node 30064771291: (CALL) 'ER_MB_ERROR | VP_START | ER_MB_END'
Node 30064771292: (CALL) 'ER_MB_ERROR | VP_START'
Node 30064771293: (CALL) 's->mb_stride * s->mb_height * sizeof(uin...'
Node 30064771294: (CALL) 's->mb_stride * s->mb_height'
Node 30064771295: (CALL) 's->mb_stride'
Node 30064771296: (CALL) 's->mb_height'
Node 30064771297: (CALL) 'sizeof(uint8_t)'
Node 30064771298: (CALL) 's->error_count = 3 * s->mb_num'
Node 30064771299: (CALL) 's->error_count'
Node 30064771300: (CALL) '3 * s->mb_num'
Node 30064771301: (CALL) 's->mb_num'
Node 30064771302: (CALL) 's->error_occurred = 0'
Node 30064771303: (CALL) 's->error_occurred'
Node 47244640279: (CONTROL_STRUCTURE) 'if (!s->avctx->err_recognition) return;'
Node 55834574893: (FIELD_IDENTIFIER) 'avctx'
Node 55834574894: (FIELD_IDENTIFIER) 'err_recognition'
Node 55834574895: (FIELD_IDENTIFIER) 'error_status_table'
Node 55834574896: (FIELD_IDENTIFIER) 'mb_stride'
Node 55834574897: (FIELD_IDENTIFIER) 'mb_height'
Node 55834574898: (FIELD_IDENTIFIER) 'error_count'
Node 55834574899: (FIELD_IDENTIFIER) 'mb_num'
Node 55834574900: (FIELD_IDENTIFIER) 'error_occurred'
Node 68719476993: (IDENTIFIER) 's'
Node 68719476994: (IDENTIFIER) 's'
Node 68719476995: (IDENTIFIER) '<unknown> ER_MB_ERROR'
Node 68719476996: (IDENTIFIER) '<unknown> VP_START'
Node 68719476997: (IDENTIFIER) '<unknown> ER_MB_END'
Node 68719476998: (IDENTIFIER) 's'
Node 68719476999: (IDENTIFIER) 's'
Node 68719477000: (IDENTIFIER) 'uint8_t'
Node 68719477001: (IDENTIFIER) 's'
Node 68719477002: (IDENTIFIER) 's'
Node 68719477003: (IDENTIFIER) 's'
The edge information of the code snippet is as follows:
Edge: Node 25769803811 -> AST -> Node 47244640279
Edge: Node 25769803811 -> AST -> Node 30064771289
Edge: Node 25769803811 -> AST -> Node 30064771298
Edge: Node 25769803811 -> AST -> Node 30064771302
Edge: Node 30064771286 -> ARGUMENT -> Node 30064771287
Edge: Node 30064771286 -> AST -> Node 30064771287
Edge: Node 30064771286 -> CDG -> Node 55834574900
Edge: Node 30064771286 -> CDG -> Node 55834574899
Edge: Node 30064771286 -> CDG -> Node 55834574898
Edge: Node 30064771286 -> CDG -> Node 55834574897
Edge: Node 30064771286 -> CDG -> Node 55834574896
Edge: Node 30064771286 -> CDG -> Node 55834574895
Edge: Node 30064771286 -> CDG -> Node 30064771303
Edge: Node 30064771286 -> CDG -> Node 30064771302
Edge: Node 30064771286 -> CDG -> Node 30064771301

The following is an example, and it is Non-vulnerable.
static void qemu_aio_wait_nonblocking(void)

{

    qemu_notify_event();

    qemu_aio_wait();

}

Answer (0 or 1):
~~~~

## 17. devign:validation:23015

Arm: B1; phiên: legacy; seed: 42; dataset/split: devign/validation.
SHA-256 prompt: `bb61df59a36ae654f83f14a1b15bc13dfed86c3c88591884d0fc0cef2c3eadc3`

~~~~text
You are now an excellent programmer. You are conducting a function vulnerability detection task for C/C++ language.

static void qmp_output_push_obj(QmpOutputVisitor *qov, QObject *value,

                                void *qapi)

{

    QStackEntry *e = g_malloc0(sizeof(*e));



    assert(qov->root);

    assert(value);

    e->value = value;

    e->qapi = qapi;

    QSLIST_INSERT_HEAD(&qov->stack, e, node);

}

In the above code snippet, check for potential security vulnerabilities and answer with a single digit: 1 if Vulnerable, 0 if Non-vulnerable.

The node information of the code snippet is as follows:
Node 25769803776: (BLOCK) '{      QStackEntry *e = g_malloc0(sizeof...'
Node 30064771072: (CALL) 'e = g_malloc0(sizeof(*e))'
Node 30064771073: (CALL) 'g_malloc0(sizeof(*e))'
Node 30064771074: (CALL) 'sizeof(*e)'
Node 30064771075: (CALL) '*e'
Node 30064771076: (CALL) 'assert(qov->root)'
Node 30064771077: (CALL) 'qov->root'
Node 30064771078: (CALL) 'assert(value)'
Node 30064771079: (CALL) 'e->value = value'
Node 30064771080: (CALL) 'e->value'
Node 30064771081: (CALL) 'e->qapi = qapi'
Node 30064771082: (CALL) 'e->qapi'
Node 30064771083: (CALL) 'QSLIST_INSERT_HEAD(&qov->stack, e, node)'
Node 30064771084: (CALL) '&qov->stack'
Node 30064771085: (CALL) 'qov->stack'
Node 55834574848: (FIELD_IDENTIFIER) 'root'
Node 55834574849: (FIELD_IDENTIFIER) 'value'
Node 55834574850: (FIELD_IDENTIFIER) 'qapi'
Node 55834574851: (FIELD_IDENTIFIER) 'stack'
Node 68719476736: (IDENTIFIER) 'e'
Node 68719476737: (IDENTIFIER) 'e'
Node 68719476738: (IDENTIFIER) 'qov'
Node 68719476739: (IDENTIFIER) 'value'
Node 68719476740: (IDENTIFIER) 'e'
Node 68719476741: (IDENTIFIER) 'value'
Node 68719476742: (IDENTIFIER) 'e'
Node 68719476743: (IDENTIFIER) 'qapi'
Node 68719476744: (IDENTIFIER) 'qov'
Node 68719476745: (IDENTIFIER) 'e'
Node 68719476746: (IDENTIFIER) '<unknown> node'
Node 94489280512: (LOCAL) 'QStackEntry *e'
Node 94489280513: (LOCAL) '<unknown> node'
Node 107374182400: (METHOD) 'static void qmp_output_push_obj(QmpOutpu...'
Node 111669149696: (METHOD_PARAMETER_IN) 'QmpOutputVisitor *qov'
Node 111669149697: (METHOD_PARAMETER_IN) 'QObject *value'
Node 111669149698: (METHOD_PARAMETER_IN) 'void *qapi'
Node 115964116992: (METHOD_PARAMETER_OUT) 'QmpOutputVisitor *qov'
Node 115964116993: (METHOD_PARAMETER_OUT) 'QObject *value'
Node 115964116994: (METHOD_PARAMETER_OUT) 'void *qapi'
Node 124554051584: (METHOD_RETURN) 'RET'
The edge information of the code snippet is as follows:
Edge: Node 25769803776 -> AST -> Node 94489280512
Edge: Node 25769803776 -> AST -> Node 30064771072
Edge: Node 25769803776 -> AST -> Node 30064771076
Edge: Node 25769803776 -> AST -> Node 30064771078
Edge: Node 25769803776 -> AST -> Node 30064771079
Edge: Node 25769803776 -> AST -> Node 30064771081
Edge: Node 25769803776 -> AST -> Node 30064771083
Edge: Node 25769803776 -> AST -> Node 94489280513
Edge: Node 30064771072 -> ARGUMENT -> Node 68719476736
Edge: Node 30064771072 -> ARGUMENT -> Node 30064771073
Edge: Node 30064771072 -> AST -> Node 68719476736
Edge: Node 30064771072 -> AST -> Node 30064771073
Edge: Node 30064771072 -> CFG -> Node 68719476738
Edge: Node 30064771072 -> DOMINATE -> Node 68719476738
Edge: Node 30064771072 -> POST_DOMINATE -> Node 30064771073
Edge: Node 30064771072 -> REACHING_DEF -> Node 124554051584

The following is an example, and it is .


Answer (0 or 1):
~~~~

## 18. devign:test:2624

Arm: B1; phiên: legacy; seed: 42; dataset/split: devign/test.
SHA-256 prompt: `0dc36e7bb4e5561dd1c45eb976c4e7a1befefb41aa297d6c604292cf71cd8ac1`

~~~~text
You are now an excellent programmer. You are conducting a function vulnerability detection task for C/C++ language.

static int idreg_init1(SysBusDevice *dev)

{

    IDRegState *s = MACIO_ID_REGISTER(dev);



    memory_region_init_ram(&s->mem, OBJECT(s),

                           "sun4m.idreg", sizeof(idreg_data), &error_abort);

    vmstate_register_ram_global(&s->mem);

    memory_region_set_readonly(&s->mem, true);

    sysbus_init_mmio(dev, &s->mem);

    return 0;

}

In the above code snippet, check for potential security vulnerabilities and answer with a single digit: 1 if Vulnerable, 0 if Non-vulnerable.

The node information of the code snippet is as follows:
Node 25769803793: (BLOCK) '{      IDRegState *s = MACIO_ID_REGISTER...'
Node 30064771146: (CALL) 's = MACIO_ID_REGISTER(dev)'
Node 30064771147: (CALL) 'MACIO_ID_REGISTER(dev)'
Node 30064771148: (CALL) 'memory_region_init_ram(&s->mem, OBJECT(s...'
Node 30064771149: (CALL) '&s->mem'
Node 30064771150: (CALL) 's->mem'
Node 30064771151: (CALL) 'OBJECT(s)'
Node 30064771152: (CALL) 'sizeof(idreg_data)'
Node 30064771153: (CALL) '&error_abort'
Node 30064771154: (CALL) 'vmstate_register_ram_global(&s->mem)'
Node 30064771155: (CALL) '&s->mem'
Node 30064771156: (CALL) 's->mem'
Node 30064771157: (CALL) 'memory_region_set_readonly(&s->mem, true...'
Node 30064771158: (CALL) '&s->mem'
Node 30064771159: (CALL) 's->mem'
Node 30064771160: (CALL) 'sysbus_init_mmio(dev, &s->mem)'
Node 30064771161: (CALL) '&s->mem'
Node 30064771162: (CALL) 's->mem'
Node 55834574865: (FIELD_IDENTIFIER) 'mem'
Node 55834574866: (FIELD_IDENTIFIER) 'mem'
Node 55834574867: (FIELD_IDENTIFIER) 'mem'
Node 55834574868: (FIELD_IDENTIFIER) 'mem'
Node 68719476808: (IDENTIFIER) 's'
Node 68719476809: (IDENTIFIER) 'dev'
Node 68719476810: (IDENTIFIER) 's'
Node 68719476811: (IDENTIFIER) 's'
Node 68719476812: (IDENTIFIER) 'idreg_data'
Node 68719476813: (IDENTIFIER) '<unknown> error_abort'
Node 68719476814: (IDENTIFIER) 's'
Node 68719476815: (IDENTIFIER) 's'
Node 68719476816: (IDENTIFIER) '<unknown> true'
Node 68719476817: (IDENTIFIER) 'dev'
Node 68719476818: (IDENTIFIER) 's'
Node 90194313222: (LITERAL) '"sun4m.idreg"'
Node 90194313223: (LITERAL) '0'
Node 94489280532: (LOCAL) 'IDRegState *s'
Node 94489280533: (LOCAL) '<unknown> true'
Node 94489280534: (LOCAL) '<unknown> error_abort'
Node 94489280535: (LOCAL) 'idreg_data'
Node 107374182408: (METHOD) 'static int idreg_init1(SysBusDevice *dev...'
The edge information of the code snippet is as follows:
Edge: Node 25769803793 -> AST -> Node 94489280532
Edge: Node 25769803793 -> AST -> Node 30064771146
Edge: Node 25769803793 -> AST -> Node 30064771148
Edge: Node 25769803793 -> AST -> Node 30064771154
Edge: Node 25769803793 -> AST -> Node 30064771157
Edge: Node 25769803793 -> AST -> Node 30064771160
Edge: Node 25769803793 -> AST -> Node 94489280533
Edge: Node 25769803793 -> AST -> Node 94489280534
Edge: Node 25769803793 -> AST -> Node 94489280535
Edge: Node 30064771146 -> ARGUMENT -> Node 68719476808
Edge: Node 30064771146 -> ARGUMENT -> Node 30064771147
Edge: Node 30064771146 -> AST -> Node 68719476808
Edge: Node 30064771146 -> AST -> Node 30064771147
Edge: Node 30064771146 -> CFG -> Node 68719476810
Edge: Node 30064771146 -> DOMINATE -> Node 68719476810
Edge: Node 30064771146 -> POST_DOMINATE -> Node 30064771147

The following is an example, and it is .


Answer (0 or 1):
~~~~

## 19. devign:test:11516

Arm: B2-rep; phiên: legacy; seed: 42; dataset/split: devign/test.
SHA-256 prompt: `d9ea2fc1b98e4afa09920bb69c1baf54f56973d3910470732eb9cfe68a416a5c`

~~~~text
You are now an excellent programmer. You are conducting a function vulnerability detection task for C/C++ language.

int qemu_init_main_loop(void)

{

    int ret;



    ret = qemu_signal_init();

    if (ret) {

        return ret;

    }



    qemu_init_sigbus();



    return qemu_event_init();

}

In the above code snippet, check for potential security vulnerabilities and answer with a single digit: 1 if Vulnerable, 0 if Non-vulnerable.

The node information of the code snippet is as follows:
Node 25769803802: (BLOCK) '{      int ret;        ret = qemu_signal...'
Node 25769803803: (BLOCK) '{ return ret; }'
Node 30064771263: (CALL) 'ret = qemu_signal_init()'
Node 30064771264: (CALL) 'qemu_signal_init()'
Node 30064771265: (CALL) 'ret != 0'
Node 30064771266: (CALL) 'qemu_init_sigbus()'
Node 30064771267: (CALL) 'qemu_event_init()'
Node 47244640277: (CONTROL_STRUCTURE) 'if (ret) { return ret; }'
Node 68719476868: (IDENTIFIER) 'ret'
Node 68719476869: (IDENTIFIER) 'ret'
Node 68719476870: (IDENTIFIER) 'ret'
Node 90194313251: (LITERAL) '0'
Node 94489280535: (LOCAL) 'int ret'
Node 107374182405: (METHOD) 'int qemu_init_main_loop(void)  {      in...'
Node 111669149699: (METHOD_PARAMETER_IN) 'void'
Node 115964116995: (METHOD_PARAMETER_OUT) 'void'
Node 124554051589: (METHOD_RETURN) 'RET'
Node 141733920775: (RETURN) 'return ret;'
Node 141733920776: (RETURN) 'return qemu_event_init();'
The edge information of the code snippet is as follows:
Edge: Node 25769803802 -> AST -> Node 94489280535
Edge: Node 25769803802 -> AST -> Node 30064771263
Edge: Node 25769803802 -> AST -> Node 47244640277
Edge: Node 25769803802 -> AST -> Node 30064771266
Edge: Node 25769803802 -> AST -> Node 141733920776
Edge: Node 25769803803 -> AST -> Node 141733920775
Edge: Node 30064771263 -> ARGUMENT -> Node 68719476868
Edge: Node 30064771263 -> ARGUMENT -> Node 30064771264
Edge: Node 30064771263 -> AST -> Node 68719476868
Edge: Node 30064771263 -> AST -> Node 30064771264
Edge: Node 30064771263 -> CFG -> Node 68719476869
Edge: Node 30064771263 -> DOMINATE -> Node 68719476869
Edge: Node 30064771263 -> POST_DOMINATE -> Node 30064771264
Edge: Node 30064771263 -> REACHING_DEF -> Node 124554051589
Edge: Node 30064771264 -> CFG -> Node 30064771263
Edge: Node 30064771264 -> DOMINATE -> Node 30064771263
Edge: Node 30064771264 -> POST_DOMINATE -> Node 68719476868
Edge: Node 30064771264 -> REACHING_DEF -> Node 68719476868
Edge: Node 30064771264 -> REACHING_DEF -> Node 30064771263
Edge: Node 30064771264 -> REACHING_DEF -> Node 124554051589
Edge: Node 30064771265 -> ARGUMENT -> Node 68719476869
Edge: Node 30064771265 -> ARGUMENT -> Node 90194313251
Edge: Node 30064771265 -> AST -> Node 68719476869
Edge: Node 30064771265 -> AST -> Node 90194313251
Edge: Node 30064771265 -> CDG -> Node 30064771266
Edge: Node 30064771265 -> CDG -> Node 141733920776
Edge: Node 30064771265 -> CDG -> Node 141733920775
Edge: Node 30064771265 -> CDG -> Node 68719476870
Edge: Node 30064771265 -> CDG -> Node 30064771267
Edge: Node 30064771265 -> CFG -> Node 68719476870

The following is an example, and it is Non-vulnerable.
int main_loop_init(void)

{

    int ret;



    qemu_mutex_lock_iothread();

    ret = qemu_signal_init();

    if (ret) {

        return ret;

    }



    /* Note eventfd must be drained before signalfd handlers run */

    ret = qemu_event_init();

    if (ret) {

        return ret;

    }



    return 0;

}

Answer (0 or 1):
~~~~

## 20. devign:test:25813

Arm: B2-flip; phiên: legacy; seed: 42; dataset/split: devign/test.
SHA-256 prompt: `3182aae7cb09e9f47383b96eb915cdad06e84a311d02ddf89a964f9c0161e3e9`

~~~~text
You are now an excellent programmer. You are conducting a function vulnerability detection task for C/C++ language.

int slirp_can_output(void)

{

    return !slirp_vc || qemu_can_send_packet(slirp_vc);

}

In the above code snippet, check for potential security vulnerabilities and answer with a single digit: 1 if Vulnerable, 0 if Non-vulnerable.

The node information of the code snippet is as follows:
Node 25769803795: (BLOCK) '{ return !slirp_vc || qemu_can_send_pack...'
Node 30064771266: (CALL) '!slirp_vc || qemu_can_send_packet(slirp_...'
Node 30064771267: (CALL) '!slirp_vc'
Node 30064771268: (CALL) 'qemu_can_send_packet(slirp_vc)'
Node 68719476873: (IDENTIFIER) '<unknown> slirp_vc'
Node 68719476874: (IDENTIFIER) '<unknown> slirp_vc'
Node 94489280547: (LOCAL) '<unknown> slirp_vc'
Node 107374182404: (METHOD) 'int slirp_can_output(void)  {      retur...'
Node 111669149700: (METHOD_PARAMETER_IN) 'void'
Node 115964116996: (METHOD_PARAMETER_OUT) 'void'
Node 124554051588: (METHOD_RETURN) 'RET'
Node 141733920768: (RETURN) 'return !slirp_vc || qemu_can_send_packet...'
The edge information of the code snippet is as follows:
Edge: Node 25769803795 -> AST -> Node 141733920768
Edge: Node 25769803795 -> AST -> Node 94489280547
Edge: Node 30064771266 -> ARGUMENT -> Node 30064771267
Edge: Node 30064771266 -> ARGUMENT -> Node 30064771268
Edge: Node 30064771266 -> AST -> Node 30064771267
Edge: Node 30064771266 -> AST -> Node 30064771268
Edge: Node 30064771266 -> CFG -> Node 141733920768
Edge: Node 30064771266 -> DOMINATE -> Node 141733920768
Edge: Node 30064771266 -> POST_DOMINATE -> Node 30064771267
Edge: Node 30064771266 -> POST_DOMINATE -> Node 30064771268
Edge: Node 30064771266 -> REACHING_DEF -> Node 141733920768
Edge: Node 30064771266 -> REACHING_DEF -> Node 124554051588
Edge: Node 30064771267 -> ARGUMENT -> Node 68719476873
Edge: Node 30064771267 -> AST -> Node 68719476873
Edge: Node 30064771267 -> CDG -> Node 30064771268
Edge: Node 30064771267 -> CDG -> Node 68719476874
Edge: Node 30064771267 -> CFG -> Node 68719476874
Edge: Node 30064771267 -> CFG -> Node 30064771266
Edge: Node 30064771267 -> DOMINATE -> Node 30064771266
Edge: Node 30064771267 -> DOMINATE -> Node 68719476874
Edge: Node 30064771267 -> POST_DOMINATE -> Node 68719476873
Edge: Node 30064771267 -> REACHING_DEF -> Node 30064771268
Edge: Node 30064771267 -> REACHING_DEF -> Node 30064771266
Edge: Node 30064771267 -> REACHING_DEF -> Node 124554051588
Edge: Node 30064771268 -> ARGUMENT -> Node 68719476874
Edge: Node 30064771268 -> AST -> Node 68719476874
Edge: Node 30064771268 -> CFG -> Node 30064771266
Edge: Node 30064771268 -> POST_DOMINATE -> Node 68719476874
Edge: Node 30064771268 -> REACHING_DEF -> Node 30064771267
Edge: Node 30064771268 -> REACHING_DEF -> Node 30064771266
Edge: Node 30064771268 -> REACHING_DEF -> Node 124554051588
Edge: Node 68719476873 -> CFG -> Node 30064771267
Edge: Node 68719476873 -> DOMINATE -> Node 30064771267
Edge: Node 68719476873 -> POST_DOMINATE -> Node 107374182404

The following is an example, and it is Non-vulnerable.
int slirp_can_output(void)

{

    return 1;

}

Answer (0 or 1):
~~~~

## 21. devign:validation:23292

Arm: B2-rand; phiên: frozen; seed: 44; dataset/split: devign/validation.
SHA-256 prompt: `4891138fe7d6271f4ff448766307b12e923b6f42e82ce0b9b06889133d5745f2`

~~~~text
You are now an excellent programmer. You are conducting a function vulnerability detection task for C/C++ language.

uint32_t HELPER(tprot)(CPUS390XState *env, uint64_t a1, uint64_t a2)

{

    S390CPU *cpu = s390_env_get_cpu(env);

    CPUState *cs = CPU(cpu);



    /*

     * TODO: we currently don't handle all access protection types

     * (including access-list and key-controlled) as well as AR mode.

     */

    if (!s390_cpu_virt_mem_check_write(cpu, a1, 0, 1)) {

        /* Fetching permitted; storing permitted */

        return 0;

    }

    switch (env->int_pgm_code) {

    case PGM_PROTECTION:

        /* Fetching permitted; storing not permitted */

        cs->exception_index = 0;

        return 1;

    case PGM_ADDRESSING:

        /* Fetching not permitted; storing not permitted */

        cs->exception_index = 0;

        return 2;

    case PGM_ASCE_TYPE:

    case PGM_REG_FIRST_TRANS:

    case PGM_REG_SEC_TRANS:

    case PGM_REG_THIRD_TRANS:

    case PGM_SEGMENT_TRANS:

    case PGM_PAGE_TRANS:

    case PGM_ALET_SPEC:

    case PGM_ALEN_SPEC:

    case PGM_ALE_SEQ:

    case PGM_ASTE_VALID:

    case PGM_ASTE_SEQ:

    case PGM_EXT_AUTH:

        /* Translation not available */

        cs->exception_index = 0;

        return 3;

    }

    /* any other exception is forwarded to the guest */

    s390_cpu_virt_mem_handle_exc(cpu, GETPC());

    return 0;

}

In the above code snippet, check for potential security vulnerabilities and answer with a single digit: 1 if Vulnerable, 0 if Non-vulnerable.

The node information of the code snippet is as follows:
Node 25769803778: (BLOCK) '<empty>'
Node 107374182402: (METHOD) 'uint32_t HELPER(tprot)'
Node 111669149696: (METHOD_PARAMETER_IN) 'tprot'
Node 115964116992: (METHOD_PARAMETER_OUT) 'tprot'
Node 124554051586: (METHOD_RETURN) 'RET'
The edge information of the code snippet is as follows:
Edge: Node 107374182402 -> AST -> Node 111669149696
Edge: Node 107374182402 -> AST -> Node 25769803778
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
static int img_read_header(AVFormatContext *s1)

{

    VideoDemuxData *s = s1->priv_data;

    int first_index, last_index;

    AVStream *st;

    enum AVPixelFormat pix_fmt = AV_PIX_FMT_NONE;



    s1->ctx_flags |= AVFMTCTX_NOHEADER;



    st = avformat_new_stream(s1, NULL);

    if (!st) {

        return AVERROR(ENOMEM);

    }



    if (s->pixel_format &&

        (pix_fmt = av_get_pix_fmt(s->pixel_format)) == AV_PIX_FMT_NONE) {

        av_log(s1, AV_LOG_ERROR, "No such pixel format: %s.\n",

               s->pixel_format);

        return AVERROR(EINVAL);

    }



    av_strlcpy(s->path, s1->filename, sizeof(s->path));

    s->img_number = 0;

    s->img_count  = 0;



    /* find format */

    if (s1->iformat->flags & AVFMT_NOFILE)

        s->is_pipe = 0;

    else {

        s->is_pipe       = 1;

        st->need_parsing = AVSTREAM_PARSE_FULL;

    }



    if (s->ts_from_file)

        avpriv_set_pts_info(st, 60, 1, 1);

    else

        avpriv_set_pts_info(st, 60, s->framerate.den, s->framerate.num);



    if (s->width && s->height) {

        st->codec->width  = s->width;

        st->codec->height = s->height;

    }



    if (!s->is_pipe) {

        if (s->pattern_type == PT_GLOB_SEQUENCE) {

        s->use_glob = is_glob(s->path);

        if (s->use_glob) {

            char *p = s->path, *q, *dup;

            int gerr;



            av_log(s1, AV_LOG_WARNING, "Pattern type 'glob_sequence' is deprecated: "

                   "use pattern_type 'glob' instead\n");

#if HAVE_GLOB

            dup = q = av_strdup(p);

            while (*q) {

                /* Do we have room for the next char and a \ insertion? */

                if ((p - s->path) >= (sizeof(s->path) - 2))

                  break;

                if (*q == '%' && strspn(q + 1, "%*?[]{}"))

                    ++q;

                else if (strspn(q, "\\*?[]{}"))

                    *p++ = '\\';

                *p++ = *q++;

            }

            *p = 0;

            av_free(dup);



            gerr = glob(s->path, GLOB_NOCHECK|GLOB_BRACE|GLOB_NOMAGIC, NULL, &s->globstate);

            if (gerr != 0) {

                return AVERROR(ENOENT);

            }

            first_index = 0;

            last_index = s->globstate.gl_pathc - 1;

#endif

        }

        }

        if ((s->pattern_type == PT_GLOB_SEQUENCE && !s->use_glob) || s->pattern_type == PT_SEQUENCE) {

            if (find_image_range(&first_index, &last_index, s->path,

                                 s->start_number, s->start_number_range) < 0) {

                av_log(s1, AV_LOG_ERROR,

                       "Could find no file with with path '%s' and index in the range %d-%d\n",

                       s->path, s->start_number, s->start_number + s->start_number_range - 1);

                return AVERROR(ENOENT);

            }

        } else if (s->pattern_type == PT_GLOB) {

#if HAVE_GLOB

            int gerr;

            gerr = glob(s->path, GLOB_NOCHECK|GLOB_BRACE|GLOB_NOMAGIC, NULL, &s->globstate);

            if (gerr != 0) {

                return AVERROR(ENOENT);

            }

            first_index = 0;

            last_index = s->globstate.gl_pathc - 1;

            s->use_glob = 1;

#else

            av_log(s1, AV_LOG_ERROR,

                   "Pattern type 'glob' was selected but globbing "

                   "is not supported by this libavformat build\n");

            return AVERROR(ENOSYS);

#endif

        } else if (s->pattern_type != PT_GLOB_SEQUENCE) {

            av_log(s1, AV_LOG_ERROR,

                   "Unknown value '%d' for pattern_type option\n", s->pattern_type);

            return AVERROR(EINVAL);

        }

        s->img_first  = first_index;

        s->img_last   = last_index;

        s->img_number = first_index;

        /* compute duration */

        st->start_time = 0;

        st->duration   = last_index - first_index + 1;

    }



    if (s1->video_codec_id) {

        st->codec->codec_type = AVMEDIA_TYPE_VIDEO;

        st->codec->codec_id   = s1->video_codec_id;

    } else if (s1->audio_codec_id) {

        st->codec->codec_type = AVMEDIA_TYPE_AUDIO;

        st->codec->codec_id   = s1->audio_codec_id;

    } else {

        const char *str = strrchr(s->path, '.');

        s->split_planes       = str && !av_strcasecmp(str + 1, "y");

        st->codec->codec_type = AVMEDIA_TYPE_VIDEO;

        st->codec->codec_id   = ff_guess_image2_codec(s->path);

        if (st->codec->codec_id == AV_CODEC_ID_LJPEG)

            st->codec->codec_id = AV_CODEC_ID_MJPEG;

    }

    if (st->codec->codec_type == AVMEDIA_TYPE_VIDEO &&

        pix_fmt != AV_PIX_FMT_NONE)

        st->codec->pix_fmt = pix_fmt;



    return 0;

}

Answer (0 or 1):
~~~~

## 22. devign:test:4519

Arm: B2-flip; phiên: frozen; seed: 42; dataset/split: devign/test.
SHA-256 prompt: `28da46dbdf9990af5e7c4654d24ef8018a3d106131df189df4566093b02a237c`

~~~~text
You are now an excellent programmer. You are conducting a function vulnerability detection task for C/C++ language.

static inline void RENAME(rgb24tobgr15)(const uint8_t *src, uint8_t *dst, int src_size)

{

    const uint8_t *s = src;

    const uint8_t *end;

    const uint8_t *mm_end;

    uint16_t *d = (uint16_t *)dst;

    end = s + src_size;

    __asm__ volatile(PREFETCH"    %0"::"m"(*src):"memory");

    __asm__ volatile(

        "movq          %0, %%mm7    \n\t"

        "movq          %1, %%mm6    \n\t"

        ::"m"(red_15mask),"m"(green_15mask));

    mm_end = end - 11;

    while (s < mm_end) {

        __asm__ volatile(

            PREFETCH"    32%1           \n\t"

            "movd          %1, %%mm0    \n\t"

            "movd         3%1, %%mm3    \n\t"

            "punpckldq    6%1, %%mm0    \n\t"

            "punpckldq    9%1, %%mm3    \n\t"

            "movq       %%mm0, %%mm1    \n\t"

            "movq       %%mm0, %%mm2    \n\t"

            "movq       %%mm3, %%mm4    \n\t"

            "movq       %%mm3, %%mm5    \n\t"

            "psrlq         $3, %%mm0    \n\t"

            "psrlq         $3, %%mm3    \n\t"

            "pand          %2, %%mm0    \n\t"

            "pand          %2, %%mm3    \n\t"

            "psrlq         $6, %%mm1    \n\t"

            "psrlq         $6, %%mm4    \n\t"

            "pand       %%mm6, %%mm1    \n\t"

            "pand       %%mm6, %%mm4    \n\t"

            "psrlq         $9, %%mm2    \n\t"

            "psrlq         $9, %%mm5    \n\t"

            "pand       %%mm7, %%mm2    \n\t"

            "pand       %%mm7, %%mm5    \n\t"

            "por        %%mm1, %%mm0    \n\t"

            "por        %%mm4, %%mm3    \n\t"

            "por        %%mm2, %%mm0    \n\t"

            "por        %%mm5, %%mm3    \n\t"

            "psllq        $16, %%mm3    \n\t"

            "por        %%mm3, %%mm0    \n\t"

            MOVNTQ"     %%mm0, %0       \n\t"

            :"=m"(*d):"m"(*s),"m"(blue_15mask):"memory");

        d += 4;

        s += 12;

    }

    __asm__ volatile(SFENCE:::"memory");

    __asm__ volatile(EMMS:::"memory");

    while (s < end) {

        const int b = *s++;

        const int g = *s++;

        const int r = *s++;

        *d++ = (b>>3) | ((g&0xF8)<<2) | ((r&0xF8)<<7);

    }

}

In the above code snippet, check for potential security vulnerabilities and answer with a single digit: 1 if Vulnerable, 0 if Non-vulnerable.

The node information of the code snippet is as follows:
Node 25769803857: (BLOCK) '<empty>'
Node 107374182420: (METHOD) 'static inline void RENAME(rgb24tobgr15)'
Node 111669149714: (METHOD_PARAMETER_IN) 'rgb24tobgr15'
Node 115964117010: (METHOD_PARAMETER_OUT) 'rgb24tobgr15'
Node 124554051604: (METHOD_RETURN) 'RET'
Node 128849018885: (MODIFIER) '<empty>'
The edge information of the code snippet is as follows:
Edge: Node 107374182420 -> AST -> Node 111669149714
Edge: Node 107374182420 -> AST -> Node 25769803857
Edge: Node 107374182420 -> AST -> Node 128849018885
Edge: Node 107374182420 -> AST -> Node 124554051604
Edge: Node 107374182420 -> AST -> Node 115964117010
Edge: Node 107374182420 -> CFG -> Node 124554051604
Edge: Node 107374182420 -> CONTAINS -> Node 25769803857
Edge: Node 107374182420 -> DOMINATE -> Node 124554051604
Edge: Node 107374182420 -> REACHING_DEF -> Node 111669149714
Edge: Node 111669149714 -> PARAMETER_LINK -> Node 115964117010
Edge: Node 111669149714 -> REACHING_DEF -> Node 115964117010
Edge: Node 111669149714 -> REACHING_DEF -> Node 124554051604
Edge: Node 124554051604 -> POST_DOMINATE -> Node 107374182420

The following is an example, and it is Vulnerable.
static inline void RENAME(rgb24tobgr15)(const uint8_t *src, uint8_t *dst, long src_size)

{

    const uint8_t *s = src;

    const uint8_t *end;

#if COMPILE_TEMPLATE_MMX

    const uint8_t *mm_end;

#endif

    uint16_t *d = (uint16_t *)dst;

    end = s + src_size;

#if COMPILE_TEMPLATE_MMX

    __asm__ volatile(PREFETCH"    %0"::"m"(*src):"memory");

    __asm__ volatile(

        "movq          %0, %%mm7    \n\t"

        "movq          %1, %%mm6    \n\t"

        ::"m"(red_15mask),"m"(green_15mask));

    mm_end = end - 11;

    while (s < mm_end) {

        __asm__ volatile(

            PREFETCH"    32%1           \n\t"

            "movd          %1, %%mm0    \n\t"

            "movd         3%1, %%mm3    \n\t"

            "punpckldq    6%1, %%mm0    \n\t"

            "punpckldq    9%1, %%mm3    \n\t"

            "movq       %%mm0, %%mm1    \n\t"

            "movq       %%mm0, %%mm2    \n\t"

            "movq       %%mm3, %%mm4    \n\t"

            "movq       %%mm3, %%mm5    \n\t"

            "psrlq         $3, %%mm0    \n\t"

            "psrlq         $3, %%mm3    \n\t"

            "pand          %2, %%mm0    \n\t"

            "pand          %2, %%mm3    \n\t"

            "psrlq         $6, %%mm1    \n\t"

            "psrlq         $6, %%mm4    \n\t"

            "pand       %%mm6, %%mm1    \n\t"

            "pand       %%mm6, %%mm4    \n\t"

            "psrlq         $9, %%mm2    \n\t"

            "psrlq         $9, %%mm5    \n\t"

            "pand       %%mm7, %%mm2    \n\t"

            "pand       %%mm7, %%mm5    \n\t"

            "por        %%mm1, %%mm0    \n\t"

            "por        %%mm4, %%mm3    \n\t"

            "por        %%mm2, %%mm0    \n\t"

            "por        %%mm5, %%mm3    \n\t"

            "psllq        $16, %%mm3    \n\t"

            "por        %%mm3, %%mm0    \n\t"

            MOVNTQ"     %%mm0, %0       \n\t"

            :"=m"(*d):"m"(*s),"m"(blue_15mask):"memory");

        d += 4;

        s += 12;

    }

    __asm__ volatile(SFENCE:::"memory");

    __asm__ volatile(EMMS:::"memory");

#endif

    while (s < end) {

        const int b = *s++;

        const int g = *s++;

        const int r = *s++;

        *d++ = (b>>3) | ((g&0xF8)<<2) | ((r&0xF8)<<7);

    }

}

Answer (0 or 1):
~~~~

## 23. devign:validation:19725

Arm: B2-rand; phiên: frozen; seed: 43; dataset/split: devign/validation.
SHA-256 prompt: `85c7ceef918114b04a098aff007f5c04f266992900b7ed1be1f28c26a13c8ba3`

~~~~text
You are now an excellent programmer. You are conducting a function vulnerability detection task for C/C++ language.

static void FUNC(hevc_loop_filter_luma)(uint8_t *_pix,

                                        ptrdiff_t _xstride, ptrdiff_t _ystride,

                                        int *_beta, int *_tc,

                                        uint8_t *_no_p, uint8_t *_no_q)

{

    int d, j;

    pixel *pix        = (pixel *)_pix;

    ptrdiff_t xstride = _xstride / sizeof(pixel);

    ptrdiff_t ystride = _ystride / sizeof(pixel);



    for (j = 0; j < 2; j++) {

        const int dp0  = abs(P2  - 2 * P1  + P0);

        const int dq0  = abs(Q2  - 2 * Q1  + Q0);

        const int dp3  = abs(TP2 - 2 * TP1 + TP0);

        const int dq3  = abs(TQ2 - 2 * TQ1 + TQ0);

        const int d0   = dp0 + dq0;

        const int d3   = dp3 + dq3;

        const int beta = _beta[j] << (BIT_DEPTH - 8);

        const int tc   = _tc[j]   << (BIT_DEPTH - 8);

        const int no_p = _no_p[j];

        const int no_q = _no_q[j];



        if (d0 + d3 >= beta) {

            pix += 4 * ystride;

            continue;

        } else {

            const int beta_3 = beta >> 3;

            const int beta_2 = beta >> 2;

            const int tc25   = ((tc * 5 + 1) >> 1);



            if (abs(P3  -  P0) + abs(Q3  -  Q0) < beta_3 && abs(P0  -  Q0) < tc25 &&

                abs(TP3 - TP0) + abs(TQ3 - TQ0) < beta_3 && abs(TP0 - TQ0) < tc25 &&

                                      (d0 << 1) < beta_2 &&      (d3 << 1) < beta_2) {

                // strong filtering

                const int tc2 = tc << 1;

                for (d = 0; d < 4; d++) {

                    const int p3 = P3;

                    const int p2 = P2;

                    const int p1 = P1;

                    const int p0 = P0;

                    const int q0 = Q0;

                    const int q1 = Q1;

                    const int q2 = Q2;

                    const int q3 = Q3;

                    if (!no_p) {

                        P0 = p0 + av_clip(((p2 + 2 * p1 + 2 * p0 + 2 * q0 + q1 + 4) >> 3) - p0, -tc2, tc2);

                        P1 = p1 + av_clip(((p2 + p1 + p0 + q0 + 2) >> 2) - p1, -tc2, tc2);

                        P2 = p2 + av_clip(((2 * p3 + 3 * p2 + p1 + p0 + q0 + 4) >> 3) - p2, -tc2, tc2);

                    }

                    if (!no_q) {

                        Q0 = q0 + av_clip(((p1 + 2 * p0 + 2 * q0 + 2 * q1 + q2 + 4) >> 3) - q0, -tc2, tc2);

                        Q1 = q1 + av_clip(((p0 + q0 + q1 + q2 + 2) >> 2) - q1, -tc2, tc2);

                        Q2 = q2 + av_clip(((2 * q3 + 3 * q2 + q1 + q0 + p0 + 4) >> 3) - q2, -tc2, tc2);

                    }

                    pix += ystride;

                }

            } else { // normal filtering

                int nd_p = 1;

                int nd_q = 1;

                const int tc_2 = tc >> 1;

                if (dp0 + dp3 < ((beta + (beta >> 1)) >> 3))

                    nd_p = 2;

                if (dq0 + dq3 < ((beta + (beta >> 1)) >> 3))

                    nd_q = 2;



                for (d = 0; d < 4; d++) {

                    const int p2 = P2;

                    const int p1 = P1;

                    const int p0 = P0;

                    const int q0 = Q0;

                    const int q1 = Q1;

                    const int q2 = Q2;

                    int delta0   = (9 * (q0 - p0) - 3 * (q1 - p1) + 8) >> 4;

                    if (abs(delta0) < 10 * tc) {

                        delta0 = av_clip(delta0, -tc, tc);

                        if (!no_p)

                            P0 = av_clip_pixel(p0 + delta0);

                        if (!no_q)

                            Q0 = av_clip_pixel(q0 - delta0);

                        if (!no_p && nd_p > 1) {

                            const int deltap1 = av_clip((((p2 + p0 + 1) >> 1) - p1 + delta0) >> 1, -tc_2, tc_2);

                            P1 = av_clip_pixel(p1 + deltap1);

                        }

                        if (!no_q && nd_q > 1) {

                            const int deltaq1 = av_clip((((q2 + q0 + 1) >> 1) - q1 - delta0) >> 1, -tc_2, tc_2);

                            Q1 = av_clip_pixel(q1 + deltaq1);

                        }

                    }

                    pix += ystride;

                }

            }

        }

    }

}

In the above code snippet, check for potential security vulnerabilities and answer with a single digit: 1 if Vulnerable, 0 if Non-vulnerable.

The node information of the code snippet is as follows:
Node 25769803778: (BLOCK) '<empty>'
Node 107374182402: (METHOD) 'static void FUNC(hevc_loop_filter_luma)'
Node 111669149696: (METHOD_PARAMETER_IN) 'hevc_loop_filter_luma'
Node 115964116992: (METHOD_PARAMETER_OUT) 'hevc_loop_filter_luma'
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

The following is an example, and it is Vulnerable.
static inline int array_ensure_allocated(array_t* array, int index)

{

    if((index + 1) * array->item_size > array->size) {

        int new_size = (index + 32) * array->item_size;

        array->pointer = g_realloc(array->pointer, new_size);

        if (!array->pointer)

            return -1;


        array->size = new_size;

        array->next = index + 1;

    }



    return 0;

}

Answer (0 or 1):
~~~~

## 24. devign:validation:19725

Arm: B2-flip; phiên: frozen; seed: 42; dataset/split: devign/validation.
SHA-256 prompt: `40a78300b81fc6f1095d56243ff328e168a14e500ffd1637072321c5e1d9377a`

~~~~text
You are now an excellent programmer. You are conducting a function vulnerability detection task for C/C++ language.

static void FUNC(hevc_loop_filter_luma)(uint8_t *_pix,

                                        ptrdiff_t _xstride, ptrdiff_t _ystride,

                                        int *_beta, int *_tc,

                                        uint8_t *_no_p, uint8_t *_no_q)

{

    int d, j;

    pixel *pix        = (pixel *)_pix;

    ptrdiff_t xstride = _xstride / sizeof(pixel);

    ptrdiff_t ystride = _ystride / sizeof(pixel);



    for (j = 0; j < 2; j++) {

        const int dp0  = abs(P2  - 2 * P1  + P0);

        const int dq0  = abs(Q2  - 2 * Q1  + Q0);

        const int dp3  = abs(TP2 - 2 * TP1 + TP0);

        const int dq3  = abs(TQ2 - 2 * TQ1 + TQ0);

        const int d0   = dp0 + dq0;

        const int d3   = dp3 + dq3;

        const int beta = _beta[j] << (BIT_DEPTH - 8);

        const int tc   = _tc[j]   << (BIT_DEPTH - 8);

        const int no_p = _no_p[j];

        const int no_q = _no_q[j];



        if (d0 + d3 >= beta) {

            pix += 4 * ystride;

            continue;

        } else {

            const int beta_3 = beta >> 3;

            const int beta_2 = beta >> 2;

            const int tc25   = ((tc * 5 + 1) >> 1);



            if (abs(P3  -  P0) + abs(Q3  -  Q0) < beta_3 && abs(P0  -  Q0) < tc25 &&

                abs(TP3 - TP0) + abs(TQ3 - TQ0) < beta_3 && abs(TP0 - TQ0) < tc25 &&

                                      (d0 << 1) < beta_2 &&      (d3 << 1) < beta_2) {

                // strong filtering

                const int tc2 = tc << 1;

                for (d = 0; d < 4; d++) {

                    const int p3 = P3;

                    const int p2 = P2;

                    const int p1 = P1;

                    const int p0 = P0;

                    const int q0 = Q0;

                    const int q1 = Q1;

                    const int q2 = Q2;

                    const int q3 = Q3;

                    if (!no_p) {

                        P0 = p0 + av_clip(((p2 + 2 * p1 + 2 * p0 + 2 * q0 + q1 + 4) >> 3) - p0, -tc2, tc2);

                        P1 = p1 + av_clip(((p2 + p1 + p0 + q0 + 2) >> 2) - p1, -tc2, tc2);

                        P2 = p2 + av_clip(((2 * p3 + 3 * p2 + p1 + p0 + q0 + 4) >> 3) - p2, -tc2, tc2);

                    }

                    if (!no_q) {

                        Q0 = q0 + av_clip(((p1 + 2 * p0 + 2 * q0 + 2 * q1 + q2 + 4) >> 3) - q0, -tc2, tc2);

                        Q1 = q1 + av_clip(((p0 + q0 + q1 + q2 + 2) >> 2) - q1, -tc2, tc2);

                        Q2 = q2 + av_clip(((2 * q3 + 3 * q2 + q1 + q0 + p0 + 4) >> 3) - q2, -tc2, tc2);

                    }

                    pix += ystride;

                }

            } else { // normal filtering

                int nd_p = 1;

                int nd_q = 1;

                const int tc_2 = tc >> 1;

                if (dp0 + dp3 < ((beta + (beta >> 1)) >> 3))

                    nd_p = 2;

                if (dq0 + dq3 < ((beta + (beta >> 1)) >> 3))

                    nd_q = 2;



                for (d = 0; d < 4; d++) {

                    const int p2 = P2;

                    const int p1 = P1;

                    const int p0 = P0;

                    const int q0 = Q0;

                    const int q1 = Q1;

                    const int q2 = Q2;

                    int delta0   = (9 * (q0 - p0) - 3 * (q1 - p1) + 8) >> 4;

                    if (abs(delta0) < 10 * tc) {

                        delta0 = av_clip(delta0, -tc, tc);

                        if (!no_p)

                            P0 = av_clip_pixel(p0 + delta0);

                        if (!no_q)

                            Q0 = av_clip_pixel(q0 - delta0);

                        if (!no_p && nd_p > 1) {

                            const int deltap1 = av_clip((((p2 + p0 + 1) >> 1) - p1 + delta0) >> 1, -tc_2, tc_2);

                            P1 = av_clip_pixel(p1 + deltap1);

                        }

                        if (!no_q && nd_q > 1) {

                            const int deltaq1 = av_clip((((q2 + q0 + 1) >> 1) - q1 - delta0) >> 1, -tc_2, tc_2);

                            Q1 = av_clip_pixel(q1 + deltaq1);

                        }

                    }

                    pix += ystride;

                }

            }

        }

    }

}

In the above code snippet, check for potential security vulnerabilities and answer with a single digit: 1 if Vulnerable, 0 if Non-vulnerable.

The node information of the code snippet is as follows:
Node 25769803778: (BLOCK) '<empty>'
Node 107374182402: (METHOD) 'static void FUNC(hevc_loop_filter_luma)'
Node 111669149696: (METHOD_PARAMETER_IN) 'hevc_loop_filter_luma'
Node 115964116992: (METHOD_PARAMETER_OUT) 'hevc_loop_filter_luma'
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

The following is an example, and it is Vulnerable.
static void FUNC(hevc_loop_filter_chroma)(uint8_t *_pix, ptrdiff_t _xstride,

                                          ptrdiff_t _ystride, int *_tc,

                                          uint8_t *_no_p, uint8_t *_no_q)

{

    int d, j, no_p, no_q;

    pixel *pix        = (pixel *)_pix;

    ptrdiff_t xstride = _xstride / sizeof(pixel);

    ptrdiff_t ystride = _ystride / sizeof(pixel);



    for (j = 0; j < 2; j++) {

        const int tc = _tc[j] << (BIT_DEPTH - 8);

        if (tc <= 0) {

            pix += 4 * ystride;

            continue;

        }

        no_p = _no_p[j];

        no_q = _no_q[j];



        for (d = 0; d < 4; d++) {

            int delta0;

            const int p1 = P1;

            const int p0 = P0;

            const int q0 = Q0;

            const int q1 = Q1;

            delta0 = av_clip((((q0 - p0) << 2) + p1 - q1 + 4) >> 3, -tc, tc);

            if (!no_p)

                P0 = av_clip_pixel(p0 + delta0);

            if (!no_q)

                Q0 = av_clip_pixel(q0 - delta0);

            pix += ystride;

        }

    }

}

Answer (0 or 1):
~~~~

## 25. devign:validation:24806

Arm: B0; phiên: legacy; seed: 42; dataset/split: devign/validation.
SHA-256 prompt: `2c9099cb730d2f593042da083466b1ae2f7cd32af57ee450a1d0148ec95b1c93`

~~~~text
You are now an excellent programmer. You are conducting a function vulnerability detection task for C/C++ language.

static int decode_slice(struct AVCodecContext *avctx, void *arg){

    H264Context *h = *(void**)arg;

    MpegEncContext * const s = &h->s;

    const int part_mask= s->partitioned_frame ? (AC_END|AC_ERROR) : 0x7F;

    int lf_x_start = s->mb_x;



    s->mb_skip_run= -1;



    h->is_complex = FRAME_MBAFF || s->picture_structure != PICT_FRAME || s->codec_id != CODEC_ID_H264 ||

                    (CONFIG_GRAY && (s->flags&CODEC_FLAG_GRAY));



    if( h->pps.cabac ) {

        /* realign */

        align_get_bits( &s->gb );



        /* init cabac */

        ff_init_cabac_states( &h->cabac);

        ff_init_cabac_decoder( &h->cabac,

                               s->gb.buffer + get_bits_count(&s->gb)/8,

                               (get_bits_left(&s->gb) + 7)/8);



        ff_h264_init_cabac_states(h);



        for(;;){

//START_TIMER

            int ret = ff_h264_decode_mb_cabac(h);

            int eos;

//STOP_TIMER("decode_mb_cabac")



            if(ret>=0) ff_h264_hl_decode_mb(h);



            if( ret >= 0 && FRAME_MBAFF ) { //FIXME optimal? or let mb_decode decode 16x32 ?

                s->mb_y++;



                ret = ff_h264_decode_mb_cabac(h);



                if(ret>=0) ff_h264_hl_decode_mb(h);

                s->mb_y--;

            }

            eos = get_cabac_terminate( &h->cabac );



            if((s->workaround_bugs & FF_BUG_TRUNCATED) && h->cabac.bytestream > h->cabac.bytestream_end + 2){

                ff_er_add_slice(s, s->resync_mb_x, s->resync_mb_y, s->mb_x-1, s->mb_y, (AC_END|DC_END|MV_END)&part_mask);

                if (s->mb_x >= lf_x_start) loop_filter(h, lf_x_start, s->mb_x + 1);

                return 0;

            }

            if( ret < 0 || h->cabac.bytestream > h->cabac.bytestream_end + 2) {

                av_log(h->s.avctx, AV_LOG_ERROR, "error while decoding MB %d %d, bytestream (%td)\n", s->mb_x, s->mb_y, h->cabac.bytestream_end - h->cabac.bytestream);

                ff_er_add_slice(s, s->resync_mb_x, s->resync_mb_y, s->mb_x, s->mb_y, (AC_ERROR|DC_ERROR|MV_ERROR)&part_mask);

                return -1;

            }



            if( ++s->mb_x >= s->mb_width ) {

                loop_filter(h, lf_x_start, s->mb_x);

                s->mb_x = lf_x_start = 0;

                decode_finish_row(h);

                ++s->mb_y;

                if(FIELD_OR_MBAFF_PICTURE) {

                    ++s->mb_y;

                    if(FRAME_MBAFF && s->mb_y < s->mb_height)

                        predict_field_decoding_flag(h);

                }

            }



            if( eos || s->mb_y >= s->mb_height ) {

                tprintf(s->avctx, "slice end %d %d\n", get_bits_count(&s->gb), s->gb.size_in_bits);

                ff_er_add_slice(s, s->resync_mb_x, s->resync_mb_y, s->mb_x-1, s->mb_y, (AC_END|DC_END|MV_END)&part_mask);

                if (s->mb_x > lf_x_start) loop_filter(h, lf_x_start, s->mb_x);

                return 0;

            }

        }



    } else {

        for(;;){

            int ret = ff_h264_decode_mb_cavlc(h);



            if(ret>=0) ff_h264_hl_decode_mb(h);



            if(ret>=0 && FRAME_MBAFF){ //FIXME optimal? or let mb_decode decode 16x32 ?

                s->mb_y++;

                ret = ff_h264_decode_mb_cavlc(h);



                if(ret>=0) ff_h264_hl_decode_mb(h);

                s->mb_y--;

            }



            if(ret<0){

                av_log(h->s.avctx, AV_LOG_ERROR, "error while decoding MB %d %d\n", s->mb_x, s->mb_y);

                ff_er_add_slice(s, s->resync_mb_x, s->resync_mb_y, s->mb_x, s->mb_y, (AC_ERROR|DC_ERROR|MV_ERROR)&part_mask);

                return -1;

            }



            if(++s->mb_x >= s->mb_width){

                loop_filter(h, lf_x_start, s->mb_x);

                s->mb_x = lf_x_start = 0;

                decode_finish_row(h);

                ++s->mb_y;

                if(FIELD_OR_MBAFF_PICTURE) {

                    ++s->mb_y;

                    if(FRAME_MBAFF && s->mb_y < s->mb_height)

                        predict_field_decoding_flag(h);

                }

                if(s->mb_y >= s->mb_height){

                    tprintf(s->avctx, "slice end %d %d\n", get_bits_count(&s->gb), s->gb.size_in_bits);



                    if(get_bits_count(&s->gb) == s->gb.size_in_bits ) {

                        ff_er_add_slice(s, s->resync_mb_x, s->resync_mb_y, s->mb_x-1, s->mb_y, (AC_END|DC_END|MV_END)&part_mask);



                        return 0;

                    }else{

                        ff_er_add_slice(s, s->resync_mb_x, s->resync_mb_y, s->mb_x, s->mb_y, (AC_END|DC_END|MV_END)&part_mask);



                        return -1;

                    }

                }

            }



            if(get_bits_count(&s->gb) >= s->gb.size_in_bits && s->mb_skip_run<=0){

                tprintf(s->avctx, "slice end %d %d\n", get_bits_count(&s->gb), s->gb.size_in_bits);

                if(get_bits_count(&s->gb) == s->gb.size_in_bits ){

                    ff_er_add_slice(s, s->resync_mb_x, s->resync_mb_y, s->mb_x-1, s->mb_y, (AC_END|DC_END|MV_END)&part_mask);

                    if (s->mb_x > lf_x_start) loop_filter(h, lf_x_start, s->mb_x);



                    return 0;

                }else{

                    ff_er_add_slice(s, s->resync_mb_x, s->resync_mb_y, s->mb_x, s->mb_y, (AC_ERROR|DC_ERROR|MV_ERROR)&part_mask);



                    return -1;

                }

            }

        }

    }



#if 0

    for(;s->mb_y < s->mb_height; s->mb_y++){

        for(;s->mb_x < s->mb_width; s->mb_x++){

            int ret= decode_mb(h);



            ff_h264_hl_decode_mb(h);



            if(ret<0){

                av_log(s->avctx, AV_LOG_ERROR, "error while decoding MB %d %d\n", s->mb_x, s->mb_y);

                ff_er_add_slice(s, s->resync_mb_x, s->resync_mb_y, s->mb_x, s->mb_y, (AC_ERROR|DC_ERROR|MV_ERROR)&part_mask);



                return -1;

            }



            if(++s->mb_x >= s->mb_width){

                s->mb_x=0;

                if(++s->mb_y >= s->mb_height){

                    if(get_bits_count(s->gb) == s->gb.size_in_bits){

                        ff_er_add_slice(s, s->resync_mb_x, s->resync_mb_y, s->mb_x-1, s->mb_y, (AC_END|DC_END|MV_END)&part_mask);



                        return 0;

                    }else{

                        ff_er_add_slice(s, s->resync_mb_x, s->resync_mb_y, s->mb_x, s->mb_y, (AC_END|DC_END|MV_END)&part_mask);



                        return -1;

                    }

                }

            }



            if(get_bits_count(s->?gb) >= s->gb?.size_in_bits){

                if(get_bits_count(s->gb) == s->gb.size_in_bits){

                    ff_er_add_slice(s, s->resync_mb_x, s->resync_mb_y, s->mb_x-1, s->mb_y, (AC_END|DC_END|MV_END)&part_mask);



                    return 0;

                }else{

                    ff_er_add_slice(s, s->resync_mb_x, s->resync_mb_y, s->mb_x, s->mb_y, (AC_ERROR|DC_ERROR|MV_ERROR)&part_mask);



                    return -1;

                }

            }

        }

        s->mb_x=0;

        ff_draw_horiz_band(s, 16*s->mb_y, 16);

    }

#endif

    return -1; //not reached

}

In the above code snippet, check for potential security vulnerabilities and answer with a single digit: 1 if Vulnerable, 0 if Non-vulnerable.

The node information of the code snippet is as follows:

The edge information of the code snippet is as follows:


The following is an example, and it is .


Answer (0 or 1):
~~~~

## 26. devign:test:25515

Arm: B1; phiên: legacy; seed: 42; dataset/split: devign/test.
SHA-256 prompt: `ca29d78ae2c3ba2369ee176a46acaaba3491c9f2fa1a0aa5ca81041cb7a77078`

~~~~text
You are now an excellent programmer. You are conducting a function vulnerability detection task for C/C++ language.

static void sysctl_write(void *opaque, target_phys_addr_t addr, uint32_t value)

{

    MilkymistSysctlState *s = opaque;



    trace_milkymist_sysctl_memory_write(addr, value);



    addr >>= 2;

    switch (addr) {

    case R_GPIO_OUT:

    case R_GPIO_INTEN:

    case R_TIMER0_COUNTER:

        if (value > s->regs[R_TIMER0_COUNTER]) {

            value = s->regs[R_TIMER0_COUNTER];

            error_report("milkymist_sysctl: timer0: trying to write a "

                    "value greater than the limit. Clipping.");

        }

        /* milkymist timer counts up */

        value = s->regs[R_TIMER0_COUNTER] - value;

        ptimer_set_count(s->ptimer0, value);

        break;

    case R_TIMER1_COUNTER:

        if (value > s->regs[R_TIMER1_COUNTER]) {

            value = s->regs[R_TIMER1_COUNTER];

            error_report("milkymist_sysctl: timer1: trying to write a "

                    "value greater than the limit. Clipping.");

        }

        /* milkymist timer counts up */

        value = s->regs[R_TIMER1_COUNTER] - value;

        ptimer_set_count(s->ptimer1, value);

        break;

    case R_TIMER0_COMPARE:

        ptimer_set_limit(s->ptimer0, value, 0);

        s->regs[addr] = value;

        break;

    case R_TIMER1_COMPARE:

        ptimer_set_limit(s->ptimer1, value, 0);

        s->regs[addr] = value;

        break;

    case R_TIMER0_CONTROL:

        s->regs[addr] = value;

        if (s->regs[R_TIMER0_CONTROL] & CTRL_ENABLE) {

            trace_milkymist_sysctl_start_timer1();

            ptimer_run(s->ptimer0, 0);

        } else {

            trace_milkymist_sysctl_stop_timer1();

            ptimer_stop(s->ptimer0);

        }

        break;

    case R_TIMER1_CONTROL:

        s->regs[addr] = value;

        if (s->regs[R_TIMER1_CONTROL] & CTRL_ENABLE) {

            trace_milkymist_sysctl_start_timer1();

            ptimer_run(s->ptimer1, 0);

        } else {

            trace_milkymist_sysctl_stop_timer1();

            ptimer_stop(s->ptimer1);

        }

        break;

    case R_ICAP:

        sysctl_icap_write(s, value);

        break;

    case R_SYSTEM_ID:

        qemu_system_reset_request();

        break;



    case R_GPIO_IN:

    case R_CAPABILITIES:

        error_report("milkymist_sysctl: write to read-only register 0x"

                TARGET_FMT_plx, addr << 2);

        break;



    default:

        error_report("milkymist_sysctl: write access to unkown register 0x"

                TARGET_FMT_plx, addr << 2);

        break;

    }

}

In the above code snippet, check for potential security vulnerabilities and answer with a single digit: 1 if Vulnerable, 0 if Non-vulnerable.

The node information of the code snippet is as follows:
Node 25769803778: (BLOCK) '{      MilkymistSysctlState *s = opaque;...'
Node 25769803779: (BLOCK) '{      case R_GPIO_OUT:      case R_GPIO...'
Node 25769803780: (BLOCK) '{              value = s->regs[R_TIMER0_...'
Node 25769803781: (BLOCK) '{              value = s->regs[R_TIMER1_...'
Node 25769803782: (BLOCK) '{ trace_milkymist_sysctl_start_timer1();...'
Node 25769803783: (BLOCK) '{ trace_milkymist_sysctl_stop_timer1(); ...'
Node 25769803784: (BLOCK) '{ trace_milkymist_sysctl_start_timer1();...'
Node 25769803785: (BLOCK) '{ trace_milkymist_sysctl_stop_timer1(); ...'
Node 30064771076: (CALL) 's = opaque'
Node 30064771077: (CALL) 'trace_milkymist_sysctl_memory_write(addr...'
Node 30064771078: (CALL) 'addr >>= 2'
Node 30064771079: (CALL) 'value > s->regs[R_TIMER0_COUNTER]'
Node 30064771080: (CALL) 's->regs[R_TIMER0_COUNTER]'
Node 30064771081: (CALL) 's->regs'
Node 30064771082: (CALL) 'value = s->regs[R_TIMER0_COUNTER]'
Node 30064771083: (CALL) 's->regs[R_TIMER0_COUNTER]'
Node 30064771084: (CALL) 's->regs'
Node 30064771085: (CALL) 'error_report("milkymist_sysctl: timer0: ...'
Node 30064771086: (CALL) 'value = s->regs[R_TIMER0_COUNTER] - valu...'
Node 30064771087: (CALL) 's->regs[R_TIMER0_COUNTER] - value'
Node 30064771088: (CALL) 's->regs[R_TIMER0_COUNTER]'
Node 30064771089: (CALL) 's->regs'
Node 30064771090: (CALL) 'ptimer_set_count(s->ptimer0, value)'
Node 30064771091: (CALL) 's->ptimer0'
Node 30064771092: (CALL) 'value > s->regs[R_TIMER1_COUNTER]'
Node 30064771093: (CALL) 's->regs[R_TIMER1_COUNTER]'
Node 30064771094: (CALL) 's->regs'
Node 30064771095: (CALL) 'value = s->regs[R_TIMER1_COUNTER]'
Node 30064771096: (CALL) 's->regs[R_TIMER1_COUNTER]'
Node 30064771097: (CALL) 's->regs'
Node 30064771098: (CALL) 'error_report("milkymist_sysctl: timer1: ...'
Node 30064771099: (CALL) 'value = s->regs[R_TIMER1_COUNTER] - valu...'
Node 30064771100: (CALL) 's->regs[R_TIMER1_COUNTER] - value'
Node 30064771101: (CALL) 's->regs[R_TIMER1_COUNTER]'
Node 30064771102: (CALL) 's->regs'
Node 30064771103: (CALL) 'ptimer_set_count(s->ptimer1, value)'
Node 30064771104: (CALL) 's->ptimer1'
Node 30064771105: (CALL) 'ptimer_set_limit(s->ptimer0, value, 0)'
Node 30064771106: (CALL) 's->ptimer0'
Node 30064771107: (CALL) 's->regs[addr] = value'
The edge information of the code snippet is as follows:
Edge: Node 25769803778 -> AST -> Node 30064771076
Edge: Node 25769803778 -> AST -> Node 30064771077
Edge: Node 25769803778 -> AST -> Node 30064771078
Edge: Node 25769803779 -> AST -> Node 30064771086
Edge: Node 25769803779 -> AST -> Node 30064771090
Edge: Node 25769803779 -> AST -> Node 30064771099
Edge: Node 25769803779 -> AST -> Node 30064771103
Edge: Node 25769803779 -> AST -> Node 30064771105
Edge: Node 25769803779 -> AST -> Node 30064771107
Edge: Node 25769803780 -> AST -> Node 30064771082
Edge: Node 25769803780 -> AST -> Node 30064771085
Edge: Node 25769803781 -> AST -> Node 30064771095

The following is an example, and it is .


Answer (0 or 1):
~~~~

## 27. devign:validation:9211

Arm: B2; phiên: frozen; seed: 42; dataset/split: devign/validation.
SHA-256 prompt: `b1389a4c8a8d66314d86da6b2ddd936b1be985e1edcc7e347c100057bcf470d2`

~~~~text
You are now an excellent programmer. You are conducting a function vulnerability detection task for C/C++ language.

static QEMUCursor *qxl_cursor(PCIQXLDevice *qxl, QXLCursor *cursor,

                              uint32_t group_id)

{

    QEMUCursor *c;

    size_t size;



    c = cursor_alloc(cursor->header.width, cursor->header.height);

    c->hot_x = cursor->header.hot_spot_x;

    c->hot_y = cursor->header.hot_spot_y;

    switch (cursor->header.type) {

    case SPICE_CURSOR_TYPE_ALPHA:

        size = sizeof(uint32_t) * cursor->header.width * cursor->header.height;

        qxl_unpack_chunks(c->data, size, qxl, &cursor->chunk, group_id);

        if (qxl->debug > 2) {

            cursor_print_ascii_art(c, "qxl/alpha");

        }

        break;

    default:

        fprintf(stderr, "%s: not implemented: type %d\n",

                __FUNCTION__, cursor->header.type);

        goto fail;

    }

    return c;



fail:

    cursor_put(c);

    return NULL;

}

In the above code snippet, check for potential security vulnerabilities and answer with a single digit: 1 if Vulnerable, 0 if Non-vulnerable.

The node information of the code snippet is as follows:
Node 25769803776: (BLOCK) '{      QEMUCursor *c;      size_t size; ...'
Node 25769803777: (BLOCK) '{      case SPICE_CURSOR_TYPE_ALPHA:    ...'
Node 25769803778: (BLOCK) '{ cursor_print_ascii_art(c, "qxl/alpha")...'
Node 30064771072: (CALL) 'c = cursor_alloc(cursor->header.width, c...'
Node 30064771073: (CALL) 'cursor_alloc(cursor->header.width, curso...'
Node 30064771074: (CALL) 'cursor->header.width'
Node 30064771075: (CALL) 'cursor->header'
Node 30064771076: (CALL) 'cursor->header.height'
Node 30064771077: (CALL) 'cursor->header'
Node 30064771078: (CALL) 'c->hot_x = cursor->header.hot_spot_x'
Node 30064771079: (CALL) 'c->hot_x'
Node 30064771080: (CALL) 'cursor->header.hot_spot_x'
Node 30064771081: (CALL) 'cursor->header'
Node 30064771082: (CALL) 'c->hot_y = cursor->header.hot_spot_y'
Node 30064771083: (CALL) 'c->hot_y'
Node 30064771084: (CALL) 'cursor->header.hot_spot_y'
Node 30064771085: (CALL) 'cursor->header'
Node 30064771086: (CALL) 'cursor->header.type'
Node 30064771087: (CALL) 'cursor->header'
Node 30064771088: (CALL) 'size = sizeof(uint32_t) * cursor->header...'
Node 30064771089: (CALL) 'sizeof(uint32_t) * cursor->header.width ...'
Node 30064771090: (CALL) 'sizeof(uint32_t) * cursor->header.width'
Node 30064771091: (CALL) 'sizeof(uint32_t)'
Node 30064771092: (CALL) 'cursor->header.width'
Node 30064771093: (CALL) 'cursor->header'
Node 30064771094: (CALL) 'cursor->header.height'
Node 30064771095: (CALL) 'cursor->header'
Node 30064771096: (CALL) 'qxl_unpack_chunks(c->data, size, qxl, &c...'
Node 30064771097: (CALL) 'c->data'
Node 30064771098: (CALL) '&cursor->chunk'
Node 30064771099: (CALL) 'cursor->chunk'
Node 30064771100: (CALL) 'qxl->debug > 2'
Node 30064771101: (CALL) 'qxl->debug'
Node 30064771102: (CALL) 'cursor_print_ascii_art(c, "qxl/alpha")'
Node 30064771103: (CALL) 'fprintf(stderr, "%s: not implemented: ty...'
Node 30064771104: (CALL) 'cursor->header.type'
Node 30064771105: (CALL) 'cursor->header'
Node 30064771106: (CALL) 'cursor_put(c)'
Node 47244640256: (CONTROL_STRUCTURE) 'switch (cursor->header.type) {      case...'
Node 47244640257: (CONTROL_STRUCTURE) 'if (qxl->debug > 2) {              curso...'
The edge information of the code snippet is as follows:
Edge: Node 25769803776 -> AST -> Node 30064771072
Edge: Node 25769803776 -> AST -> Node 30064771078
Edge: Node 25769803776 -> AST -> Node 30064771082
Edge: Node 25769803776 -> AST -> Node 47244640256
Edge: Node 25769803776 -> AST -> Node 30064771106
Edge: Node 25769803777 -> AST -> Node 30064771088
Edge: Node 25769803777 -> AST -> Node 30064771096
Edge: Node 25769803777 -> AST -> Node 47244640257
Edge: Node 25769803777 -> AST -> Node 30064771103
Edge: Node 25769803778 -> AST -> Node 30064771102
Edge: Node 30064771072 -> ARGUMENT -> Node 30064771073
Edge: Node 30064771072 -> AST -> Node 30064771073
Edge: Node 30064771072 -> POST_DOMINATE -> Node 30064771073

The following is an example, and it is Vulnerable.
static QEMUCursor *qxl_cursor(PCIQXLDevice *qxl, QXLCursor *cursor)

{

    QEMUCursor *c;

    uint8_t *image, *mask;

    size_t size;



    c = cursor_alloc(cursor->header.width, cursor->header.height);

    c->hot_x = cursor->header.hot_spot_x;

    c->hot_y = cursor->header.hot_spot_y;

    switch (cursor->header.type) {

    case SPICE_CURSOR_TYPE_ALPHA:

        size = sizeof(uint32_t) * cursor->header.width * cursor->header.height;

        memcpy(c->data, cursor->chunk.data, size);

        if (qxl->debug > 2) {

            cursor_print_ascii_art(c, "qxl/alpha");

        }

        break;

    case SPICE_CURSOR_TYPE_MONO:

        mask  = cursor->chunk.data;

        image = mask + cursor_get_mono_bpl(c) * c->width;

        cursor_set_mono(c, 0xffffff, 0x000000, image, 1, mask);

        if (qxl->debug > 2) {

            cursor_print_ascii_art(c, "qxl/mono");

        }

        break;

    default:

        fprintf(stderr, "%s: not implemented: type %d\n",

                __FUNCTION__, cursor->header.type);

        goto fail;

    }

    return c;



fail:

    cursor_put(c);

    return NULL;

}

Answer (0 or 1):
~~~~

## 28. devign:validation:5158

Arm: B2-rand; phiên: frozen; seed: 44; dataset/split: devign/validation.
SHA-256 prompt: `ac3089a35d1842b04912804bf1d4d203f1b69a381eb7f6751bbb863e633eeffa`

~~~~text
You are now an excellent programmer. You are conducting a function vulnerability detection task for C/C++ language.

static void tcp_chr_read(void *opaque)

{

    CharDriverState *chr = opaque;

    TCPCharDriver *s = chr->opaque;

    uint8_t buf[READ_BUF_LEN];

    int len, size;



    if (!s->connected || s->max_size <= 0)

        return;

    len = sizeof(buf);

    if (len > s->max_size)

        len = s->max_size;

    size = tcp_chr_recv(chr, (void *)buf, len);

    if (size == 0) {

        /* connection closed */

        s->connected = 0;

        if (s->listen_fd >= 0) {

            qemu_set_fd_handler(s->listen_fd, tcp_chr_accept, NULL, chr);

        }

        qemu_set_fd_handler(s->fd, NULL, NULL, NULL);

        closesocket(s->fd);

        s->fd = -1;

        qemu_chr_event(chr, CHR_EVENT_CLOSED);

    } else if (size > 0) {

        if (s->do_telnetopt)

            tcp_chr_process_IAC_bytes(chr, s, buf, &size);

        if (size > 0)

            qemu_chr_read(chr, buf, size);

        if (s->msgfd != -1) {

            close(s->msgfd);

            s->msgfd = -1;

        }

    }

}

In the above code snippet, check for potential security vulnerabilities and answer with a single digit: 1 if Vulnerable, 0 if Non-vulnerable.

The node information of the code snippet is as follows:
Node 25769803776: (BLOCK) '{      CharDriverState *chr = opaque;   ...'
Node 25769803777: (BLOCK) '<empty>'
Node 25769803778: (BLOCK) '<empty>'
Node 25769803779: (BLOCK) '{          /* connection closed */      ...'
Node 25769803780: (BLOCK) '{ qemu_set_fd_handler(s->listen_fd, tcp_...'
Node 25769803781: (BLOCK) '<empty>'
Node 25769803782: (BLOCK) '{          if (s->do_telnetopt)         ...'
Node 25769803783: (BLOCK) '<empty>'
Node 25769803784: (BLOCK) '<empty>'
Node 25769803785: (BLOCK) '{ close(s->msgfd); s->msgfd = -1; }'
Node 30064771072: (CALL) 'chr = opaque'
Node 30064771073: (CALL) 's = chr->opaque'
Node 30064771074: (CALL) 'chr->opaque'
Node 30064771075: (CALL) 'buf[READ_BUF_LEN]'
Node 30064771076: (CALL) 'buf[READ_BUF_LEN]'
Node 30064771077: (CALL) '!s->connected || s->max_size <= 0'
Node 30064771078: (CALL) '!s->connected'
Node 30064771079: (CALL) 's->connected'
Node 30064771080: (CALL) 's->max_size <= 0'
Node 30064771081: (CALL) 's->max_size'
Node 30064771082: (CALL) 'len = sizeof(buf)'
Node 30064771083: (CALL) 'sizeof(buf)'
Node 30064771084: (CALL) 'len > s->max_size'
Node 30064771085: (CALL) 's->max_size'
Node 30064771086: (CALL) 'len = s->max_size'
Node 30064771087: (CALL) 's->max_size'
Node 30064771088: (CALL) 'size = tcp_chr_recv(chr, (void *)buf, le...'
Node 30064771089: (CALL) 'tcp_chr_recv(chr, (void *)buf, len)'
Node 30064771090: (CALL) '(void *)buf'
Node 30064771091: (CALL) 'size == 0'
Node 30064771092: (CALL) 's->connected = 0'
Node 30064771093: (CALL) 's->connected'
Node 30064771094: (CALL) 's->listen_fd >= 0'
Node 30064771095: (CALL) 's->listen_fd'
Node 30064771096: (CALL) 'qemu_set_fd_handler(s->listen_fd, tcp_ch...'
Node 30064771097: (CALL) 's->listen_fd'
Node 30064771098: (CALL) 'qemu_set_fd_handler(s->fd, NULL, NULL, N...'
Node 30064771099: (CALL) 's->fd'
Node 30064771100: (CALL) 'closesocket(s->fd)'
Node 30064771101: (CALL) 's->fd'
The edge information of the code snippet is as follows:
Edge: Node 25769803776 -> AST -> Node 30064771072
Edge: Node 25769803776 -> AST -> Node 30064771073
Edge: Node 25769803776 -> AST -> Node 30064771075
Edge: Node 25769803776 -> AST -> Node 30064771082
Edge: Node 25769803776 -> AST -> Node 30064771088
Edge: Node 25769803778 -> AST -> Node 30064771086
Edge: Node 25769803779 -> AST -> Node 30064771092
Edge: Node 25769803779 -> AST -> Node 30064771098
Edge: Node 25769803779 -> AST -> Node 30064771100
Edge: Node 25769803780 -> AST -> Node 30064771096
Edge: Node 30064771073 -> ARGUMENT -> Node 30064771074
Edge: Node 30064771073 -> AST -> Node 30064771074
Edge: Node 30064771073 -> POST_DOMINATE -> Node 30064771074
Edge: Node 30064771074 -> CFG -> Node 30064771073
Edge: Node 30064771074 -> DOMINATE -> Node 30064771073

The following is an example, and it is Vulnerable.
static HotpluggableCPUList *spapr_query_hotpluggable_cpus(MachineState *machine)

{

    int i;

    HotpluggableCPUList *head = NULL;

    sPAPRMachineState *spapr = SPAPR_MACHINE(machine);

    sPAPRMachineClass *smc = SPAPR_MACHINE_GET_CLASS(machine);

    int spapr_max_cores = max_cpus / smp_threads;



    g_assert(smc->dr_cpu_enabled);



    for (i = 0; i < spapr_max_cores; i++) {

        HotpluggableCPUList *list_item = g_new0(typeof(*list_item), 1);

        HotpluggableCPU *cpu_item = g_new0(typeof(*cpu_item), 1);

        CpuInstanceProperties *cpu_props = g_new0(typeof(*cpu_props), 1);



        cpu_item->type = spapr_get_cpu_core_type(machine->cpu_model);

        cpu_item->vcpus_count = smp_threads;

        cpu_props->has_core_id = true;

        cpu_props->core_id = i * smp_threads;

        /* TODO: add 'has_node/node' here to describe

           to which node core belongs */



        cpu_item->props = cpu_props;

        if (spapr->cores[i]) {

            cpu_item->has_qom_path = true;

            cpu_item->qom_path = object_get_canonical_path(spapr->cores[i]);

        }

        list_item->value = cpu_item;

        list_item->next = head;

        head = list_item;

    }

    return head;

}

Answer (0 or 1):
~~~~

## 29. devign:validation:2183

Arm: B2-rand; phiên: frozen; seed: 44; dataset/split: devign/validation.
SHA-256 prompt: `ae7e1e1c9c8e67f09f28887a6dbb2f9b92437f1b9ffb006ddd4f2e175e568338`

~~~~text
You are now an excellent programmer. You are conducting a function vulnerability detection task for C/C++ language.

static void dma_complete(DMAAIOCB *dbs, int ret)

{

    trace_dma_complete(dbs, ret, dbs->common.cb);



    dma_bdrv_unmap(dbs);

    if (dbs->common.cb) {

        dbs->common.cb(dbs->common.opaque, ret);

    }

    qemu_iovec_destroy(&dbs->iov);

    if (dbs->bh) {

        qemu_bh_delete(dbs->bh);

        dbs->bh = NULL;

    }

    qemu_aio_unref(dbs);

}

In the above code snippet, check for potential security vulnerabilities and answer with a single digit: 1 if Vulnerable, 0 if Non-vulnerable.

The node information of the code snippet is as follows:
Node 25769803776: (BLOCK) '{      trace_dma_complete(dbs, ret, dbs-...'
Node 25769803777: (BLOCK) '{ dbs->common.cb(dbs->common.opaque, ret...'
Node 25769803778: (BLOCK) '{ qemu_bh_delete(dbs->bh); dbs->bh = NUL...'
Node 30064771072: (CALL) 'trace_dma_complete(dbs, ret, dbs->common...'
Node 30064771073: (CALL) 'dbs->common.cb'
Node 30064771074: (CALL) 'dbs->common'
Node 30064771075: (CALL) 'dma_bdrv_unmap(dbs)'
Node 30064771076: (CALL) 'dbs->common.cb'
Node 30064771077: (CALL) 'dbs->common'
Node 30064771078: (CALL) 'dbs->common.cb(dbs->common.opaque, ret)'
Node 30064771079: (CALL) 'dbs->common.cb'
Node 30064771080: (CALL) 'dbs->common'
Node 30064771081: (CALL) 'dbs->common.opaque'
Node 30064771082: (CALL) 'dbs->common'
Node 30064771083: (CALL) 'qemu_iovec_destroy(&dbs->iov)'
Node 30064771084: (CALL) '&dbs->iov'
Node 30064771085: (CALL) 'dbs->iov'
Node 30064771086: (CALL) 'dbs->bh'
Node 30064771087: (CALL) 'qemu_bh_delete(dbs->bh)'
Node 30064771088: (CALL) 'dbs->bh'
Node 30064771089: (CALL) 'dbs->bh = NULL'
Node 30064771090: (CALL) 'dbs->bh'
Node 30064771091: (CALL) 'qemu_aio_unref(dbs)'
Node 47244640256: (CONTROL_STRUCTURE) 'if (dbs->common.cb) {          dbs->comm...'
Node 47244640257: (CONTROL_STRUCTURE) 'if (dbs->bh) { qemu_bh_delete(dbs->bh); ...'
Node 55834574848: (FIELD_IDENTIFIER) 'common'
Node 55834574849: (FIELD_IDENTIFIER) 'cb'
Node 55834574850: (FIELD_IDENTIFIER) 'common'
Node 55834574851: (FIELD_IDENTIFIER) 'cb'
Node 55834574852: (FIELD_IDENTIFIER) 'common'
Node 55834574853: (FIELD_IDENTIFIER) 'cb'
Node 55834574854: (FIELD_IDENTIFIER) 'common'
Node 55834574855: (FIELD_IDENTIFIER) 'opaque'
Node 55834574856: (FIELD_IDENTIFIER) 'iov'
Node 55834574857: (FIELD_IDENTIFIER) 'bh'
Node 55834574858: (FIELD_IDENTIFIER) 'bh'
Node 55834574859: (FIELD_IDENTIFIER) 'bh'
Node 68719476736: (IDENTIFIER) 'dbs'
Node 68719476737: (IDENTIFIER) 'ret'
Node 68719476738: (IDENTIFIER) 'dbs'
The edge information of the code snippet is as follows:
Edge: Node 25769803776 -> AST -> Node 30064771072
Edge: Node 25769803776 -> AST -> Node 30064771075
Edge: Node 25769803776 -> AST -> Node 47244640256
Edge: Node 25769803776 -> AST -> Node 30064771083
Edge: Node 25769803776 -> AST -> Node 47244640257
Edge: Node 25769803776 -> AST -> Node 30064771091
Edge: Node 25769803777 -> AST -> Node 30064771078
Edge: Node 25769803778 -> AST -> Node 30064771087
Edge: Node 25769803778 -> AST -> Node 30064771089
Edge: Node 30064771072 -> ARGUMENT -> Node 68719476736
Edge: Node 30064771072 -> ARGUMENT -> Node 68719476737
Edge: Node 30064771072 -> ARGUMENT -> Node 30064771073
Edge: Node 30064771072 -> AST -> Node 68719476736
Edge: Node 30064771072 -> AST -> Node 68719476737
Edge: Node 30064771072 -> AST -> Node 30064771073

The following is an example, and it is Non-vulnerable.
static void copy_context_before_encode(MpegEncContext *d, MpegEncContext *s, int type){

    int i;



    memcpy(d->last_mv, s->last_mv, 2*2*2*sizeof(int)); //FIXME is memcpy faster then a loop?



    /* mpeg1 */

    d->mb_incr= s->mb_incr;

    for(i=0; i<3; i++)

        d->last_dc[i]= s->last_dc[i];

    

    /* statistics */

    d->mv_bits= s->mv_bits;

    d->i_tex_bits= s->i_tex_bits;

    d->p_tex_bits= s->p_tex_bits;

    d->i_count= s->i_count;

    d->p_count= s->p_count;

    d->skip_count= s->skip_count;

    d->misc_bits= s->misc_bits;

    d->last_bits= 0;



    d->mb_skiped= s->mb_skiped;

}

Answer (0 or 1):
~~~~

## 30. devign:test:2622

Arm: B2-rand; phiên: frozen; seed: 42; dataset/split: devign/test.
SHA-256 prompt: `2b3048c442e0ce8d4b61fe4ccbf8640e9739e39bd8c7e132f4f8b54e1b02fd5f`

~~~~text
You are now an excellent programmer. You are conducting a function vulnerability detection task for C/C++ language.

blkdebug_co_preadv(BlockDriverState *bs, uint64_t offset, uint64_t bytes,
                   QEMUIOVector *qiov, int flags)
{
    BDRVBlkdebugState *s = bs->opaque;
    BlkdebugRule *rule = NULL;
    QSIMPLEQ_FOREACH(rule, &s->active_rules, active_next) {
        uint64_t inject_offset = rule->options.inject.offset;
        if (inject_offset == -1 ||
            (inject_offset >= offset && inject_offset < offset + bytes))
        {
            break;
    if (rule && rule->options.inject.error) {
        return inject_error(bs, rule);
    return bdrv_co_preadv(bs->file, offset, bytes, qiov, flags);

In the above code snippet, check for potential security vulnerabilities and answer with a single digit: 1 if Vulnerable, 0 if Non-vulnerable.

The node information of the code snippet is as follows:
Node 25769803788: (BLOCK) '{     BDRVBlkdebugState *s = bs->opaque;...'
Node 25769803789: (BLOCK) '{         uint64_t inject_offset = rule-...'
Node 25769803790: (BLOCK) '{             break;     if (rule && rul...'
Node 25769803791: (BLOCK) '{         return inject_error(bs, rule);...'
Node 30064771133: (CALL) 's = bs->opaque'
Node 30064771134: (CALL) 'bs->opaque'
Node 30064771135: (CALL) 'rule = NULL'
Node 30064771136: (CALL) 'QSIMPLEQ_FOREACH(rule, &s->active_rules,...'
Node 30064771137: (CALL) '&s->active_rules'
Node 30064771138: (CALL) 's->active_rules'
Node 30064771139: (CALL) 'inject_offset = rule->options.inject.off...'
Node 30064771140: (CALL) 'rule->options.inject.offset'
Node 30064771141: (CALL) 'rule->options.inject'
Node 30064771142: (CALL) 'rule->options'
Node 30064771143: (CALL) 'inject_error(bs, rule)'
Node 30064771144: (CALL) 'bdrv_co_preadv(bs->file, offset, bytes, ...'
Node 30064771145: (CALL) 'bs->file'
Node 47244640261: (CONTROL_STRUCTURE) 'break;'
Node 55834574859: (FIELD_IDENTIFIER) 'opaque'
Node 55834574860: (FIELD_IDENTIFIER) 'active_rules'
Node 55834574861: (FIELD_IDENTIFIER) 'options'
Node 55834574862: (FIELD_IDENTIFIER) 'inject'
Node 55834574863: (FIELD_IDENTIFIER) 'offset'
Node 55834574864: (FIELD_IDENTIFIER) 'file'
Node 68719476792: (IDENTIFIER) 's'
Node 68719476793: (IDENTIFIER) 'bs'
Node 68719476794: (IDENTIFIER) 'rule'
Node 68719476795: (IDENTIFIER) '<unknown> NULL'
Node 68719476796: (IDENTIFIER) 'rule'
Node 68719476797: (IDENTIFIER) 's'
Node 68719476798: (IDENTIFIER) '<unknown> active_next'
Node 68719476799: (IDENTIFIER) 'inject_offset'
Node 68719476800: (IDENTIFIER) 'rule'
Node 68719476801: (IDENTIFIER) 'bs'
Node 68719476802: (IDENTIFIER) 'rule'
Node 68719476803: (IDENTIFIER) 'bs'
Node 68719476804: (IDENTIFIER) 'offset'
Node 68719476805: (IDENTIFIER) 'bytes'
Node 68719476806: (IDENTIFIER) 'qiov'
Node 68719476807: (IDENTIFIER) 'flags'
The edge information of the code snippet is as follows:
Edge: Node 25769803788 -> AST -> Node 30064771133
Edge: Node 25769803788 -> AST -> Node 30064771135
Edge: Node 25769803788 -> AST -> Node 30064771136
Edge: Node 25769803788 -> AST -> Node 25769803789
Edge: Node 25769803789 -> AST -> Node 30064771139
Edge: Node 25769803789 -> AST -> Node 25769803790
Edge: Node 25769803789 -> POST_DOMINATE -> Node 25769803790
Edge: Node 25769803790 -> AST -> Node 47244640261
Edge: Node 25769803790 -> AST -> Node 25769803791
Edge: Node 25769803790 -> CFG -> Node 25769803789
Edge: Node 25769803790 -> POST_DOMINATE -> Node 25769803791
Edge: Node 25769803791 -> CFG -> Node 25769803790
Edge: Node 30064771133 -> ARGUMENT -> Node 68719476792
Edge: Node 30064771133 -> ARGUMENT -> Node 30064771134
Edge: Node 30064771133 -> AST -> Node 68719476792
Edge: Node 30064771133 -> AST -> Node 30064771134

The following is an example, and it is Non-vulnerable.
static void pcnet_aprom_writeb(void *opaque, uint32_t addr, uint32_t val)

{

    PCNetState *s = opaque;

#ifdef PCNET_DEBUG

    printf("pcnet_aprom_writeb addr=0x%08x val=0x%02x\n", addr, val);

#endif

    /* Check APROMWE bit to enable write access */

    if (pcnet_bcr_readw(s,2) & 0x100)

        s->prom[addr & 15] = val;

}

Answer (0 or 1):
~~~~

## 31. reveal:test:809

Arm: B0; phiên: legacy; seed: 42; dataset/split: reveal/test.
SHA-256 prompt: `af036fa498f7b57b68b49c2c8d2da0986a297fc81926d2e146f2556ec2c37706`

~~~~text
You are now an excellent programmer. You are conducting a function vulnerability detection task for C/C++ language.

static inline void set_bits ( uint8_t * tab , int start , int len ) {
 int end , mask , end1 ;
 end = start + len ;
 tab += start >> 3 ;
 mask = 0xff << ( start & 7 ) ;
 if ( ( start & ~ 7 ) == ( end & ~ 7 ) ) {
 if ( start < end ) {
 mask &= ~ ( 0xff << ( end & 7 ) ) ;
 * tab |= mask ;
 }
 }
 else {
 * tab ++ |= mask ;
 start = ( start + 8 ) & ~ 7 ;
 end1 = end & ~ 7 ;
 while ( start < end1 ) {
 * tab ++ = 0xff ;
 start += 8 ;
 }
 if ( start < end ) {
 mask = ~ ( 0xff << ( end & 7 ) ) ;
 * tab |= mask ;
 }
 }
 }

In the above code snippet, check for potential security vulnerabilities and answer with a single digit: 1 if Vulnerable, 0 if Non-vulnerable.

The node information of the code snippet is as follows:

The edge information of the code snippet is as follows:


The following is an example, and it is .


Answer (0 or 1):
~~~~

## 32. reveal:validation:496

Arm: B1; phiên: legacy; seed: 42; dataset/split: reveal/validation.
SHA-256 prompt: `a296e1c286c7de12a337489adebd199a301ab63b7054267ec9e2ad9bae53469a`

~~~~text
You are now an excellent programmer. You are conducting a function vulnerability detection task for C/C++ language.

static void mount_state_free ( MountState * state ) {
 g_object_unref ( state -> cancellable ) ;
 g_free ( state ) ;
 }

In the above code snippet, check for potential security vulnerabilities and answer with a single digit: 1 if Vulnerable, 0 if Non-vulnerable.

The node information of the code snippet is as follows:
Node 25769803799: (BLOCK) '{ g_object_unref ( state -> cancellable ...'
Node 30064771146: (CALL) 'g_object_unref ( state -> cancellable )'
Node 30064771147: (CALL) 'state -> cancellable'
Node 30064771148: (CALL) 'g_free ( state )'
Node 55834574857: (FIELD_IDENTIFIER) 'cancellable'
Node 68719476795: (IDENTIFIER) 'state'
Node 68719476796: (IDENTIFIER) 'state'
Node 107374182411: (METHOD) 'static void mount_state_free ( MountStat...'
Node 111669149706: (METHOD_PARAMETER_IN) 'MountState * state'
Node 115964117002: (METHOD_PARAMETER_OUT) 'MountState * state'
Node 124554051595: (METHOD_RETURN) 'RET'
Node 128849018881: (MODIFIER) '<empty>'
The edge information of the code snippet is as follows:
Edge: Node 25769803799 -> AST -> Node 30064771146
Edge: Node 25769803799 -> AST -> Node 30064771148
Edge: Node 30064771146 -> ARGUMENT -> Node 30064771147
Edge: Node 30064771146 -> AST -> Node 30064771147
Edge: Node 30064771146 -> CFG -> Node 68719476796
Edge: Node 30064771146 -> DOMINATE -> Node 68719476796
Edge: Node 30064771146 -> POST_DOMINATE -> Node 30064771147
Edge: Node 30064771146 -> REACHING_DEF -> Node 124554051595
Edge: Node 30064771147 -> ARGUMENT -> Node 68719476795
Edge: Node 30064771147 -> ARGUMENT -> Node 55834574857
Edge: Node 30064771147 -> AST -> Node 68719476795
Edge: Node 30064771147 -> AST -> Node 55834574857
Edge: Node 30064771147 -> CFG -> Node 30064771146
Edge: Node 30064771147 -> DOMINATE -> Node 30064771146
Edge: Node 30064771147 -> POST_DOMINATE -> Node 55834574857
Edge: Node 30064771147 -> REACHING_DEF -> Node 115964117002
Edge: Node 30064771147 -> REACHING_DEF -> Node 68719476796
Edge: Node 30064771147 -> REACHING_DEF -> Node 30064771146
Edge: Node 30064771147 -> REACHING_DEF -> Node 124554051595
Edge: Node 30064771148 -> ARGUMENT -> Node 68719476796
Edge: Node 30064771148 -> AST -> Node 68719476796
Edge: Node 30064771148 -> CFG -> Node 124554051595
Edge: Node 30064771148 -> DOMINATE -> Node 124554051595
Edge: Node 30064771148 -> POST_DOMINATE -> Node 68719476796
Edge: Node 30064771148 -> REACHING_DEF -> Node 124554051595
Edge: Node 55834574857 -> CFG -> Node 30064771147
Edge: Node 55834574857 -> DOMINATE -> Node 30064771147
Edge: Node 55834574857 -> POST_DOMINATE -> Node 68719476795
Edge: Node 68719476795 -> CFG -> Node 55834574857
Edge: Node 68719476795 -> DOMINATE -> Node 55834574857
Edge: Node 68719476795 -> POST_DOMINATE -> Node 107374182411
Edge: Node 68719476795 -> REF -> Node 111669149706
Edge: Node 68719476796 -> CFG -> Node 30064771148
Edge: Node 68719476796 -> DOMINATE -> Node 30064771148
Edge: Node 68719476796 -> POST_DOMINATE -> Node 30064771146

The following is an example, and it is .


Answer (0 or 1):
~~~~

## 33. reveal:test:1760

Arm: B2; phiên: frozen; seed: 42; dataset/split: reveal/test.
SHA-256 prompt: `3b955cc4841ed99a0fc05df0328d4742828f0d8b39e8ee8de995d8210b4931ae`

~~~~text
You are now an excellent programmer. You are conducting a function vulnerability detection task for C/C++ language.

proto_item * proto_tree_add_boolean ( proto_tree * tree , int hfindex , tvbuff_t * tvb , gint start , gint length , guint32 value ) {
 proto_item * pi ;
 header_field_info * hfinfo ;
 CHECK_FOR_NULL_TREE ( tree ) ;
 TRY_TO_FAKE_THIS_ITEM ( tree , hfindex , hfinfo ) ;
 DISSECTOR_ASSERT_FIELD_TYPE ( hfinfo , FT_BOOLEAN ) ;
 pi = proto_tree_add_pi ( tree , hfinfo , tvb , start , & length ) ;
 proto_tree_set_boolean ( PNODE_FINFO ( pi ) , value ) ;
 return pi ;
 }

In the above code snippet, check for potential security vulnerabilities and answer with a single digit: 1 if Vulnerable, 0 if Non-vulnerable.

The node information of the code snippet is as follows:
Node 25769803776: (BLOCK) '{  proto_item * pi ;  header_field_info ...'
Node 30064771072: (CALL) 'CHECK_FOR_NULL_TREE ( tree )'
Node 30064771073: (CALL) 'TRY_TO_FAKE_THIS_ITEM ( tree , hfindex ,...'
Node 30064771074: (CALL) 'DISSECTOR_ASSERT_FIELD_TYPE ( hfinfo , F...'
Node 30064771075: (CALL) 'pi = proto_tree_add_pi ( tree , hfinfo ,...'
Node 30064771076: (CALL) 'proto_tree_add_pi ( tree , hfinfo , tvb ...'
Node 30064771077: (CALL) '& length'
Node 30064771078: (CALL) 'proto_tree_set_boolean ( PNODE_FINFO ( p...'
Node 30064771079: (CALL) 'PNODE_FINFO ( pi )'
Node 68719476736: (IDENTIFIER) 'tree'
Node 68719476737: (IDENTIFIER) 'tree'
Node 68719476738: (IDENTIFIER) 'hfindex'
Node 68719476739: (IDENTIFIER) 'hfinfo'
Node 68719476740: (IDENTIFIER) 'hfinfo'
Node 68719476741: (IDENTIFIER) '<unknown> FT_BOOLEAN'
Node 68719476742: (IDENTIFIER) 'pi'
Node 68719476743: (IDENTIFIER) 'tree'
Node 68719476744: (IDENTIFIER) 'hfinfo'
Node 68719476745: (IDENTIFIER) 'tvb'
Node 68719476746: (IDENTIFIER) 'start'
Node 68719476747: (IDENTIFIER) 'length'
Node 68719476748: (IDENTIFIER) 'pi'
Node 68719476749: (IDENTIFIER) 'value'
Node 68719476750: (IDENTIFIER) 'pi'
Node 94489280512: (LOCAL) 'proto_item * pi'
Node 94489280513: (LOCAL) 'header_field_info * hfinfo'
Node 94489280514: (LOCAL) '<unknown> FT_BOOLEAN'
Node 107374182400: (METHOD) 'proto_item * proto_tree_add_boolean ( pr...'
Node 111669149696: (METHOD_PARAMETER_IN) 'proto_tree * tree'
Node 111669149697: (METHOD_PARAMETER_IN) 'int hfindex'
Node 111669149698: (METHOD_PARAMETER_IN) 'tvbuff_t * tvb'
Node 111669149699: (METHOD_PARAMETER_IN) 'gint start'
Node 111669149700: (METHOD_PARAMETER_IN) 'gint length'
Node 111669149701: (METHOD_PARAMETER_IN) 'guint32 value'
Node 115964116992: (METHOD_PARAMETER_OUT) 'proto_tree * tree'
Node 115964116993: (METHOD_PARAMETER_OUT) 'int hfindex'
Node 115964116994: (METHOD_PARAMETER_OUT) 'tvbuff_t * tvb'
Node 115964116995: (METHOD_PARAMETER_OUT) 'gint start'
Node 115964116996: (METHOD_PARAMETER_OUT) 'gint length'
Node 115964116997: (METHOD_PARAMETER_OUT) 'guint32 value'
The edge information of the code snippet is as follows:
Edge: Node 25769803776 -> AST -> Node 94489280512
Edge: Node 25769803776 -> AST -> Node 94489280513
Edge: Node 25769803776 -> AST -> Node 30064771072
Edge: Node 25769803776 -> AST -> Node 30064771073
Edge: Node 25769803776 -> AST -> Node 30064771074
Edge: Node 25769803776 -> AST -> Node 30064771075
Edge: Node 25769803776 -> AST -> Node 30064771078
Edge: Node 25769803776 -> AST -> Node 94489280514
Edge: Node 30064771072 -> ARGUMENT -> Node 68719476736
Edge: Node 30064771072 -> AST -> Node 68719476736
Edge: Node 30064771072 -> CFG -> Node 68719476737
Edge: Node 30064771072 -> DOMINATE -> Node 68719476737
Edge: Node 30064771072 -> POST_DOMINATE -> Node 68719476736
Edge: Node 30064771073 -> ARGUMENT -> Node 68719476737
Edge: Node 30064771073 -> ARGUMENT -> Node 68719476738

The following is an example, and it is Non-vulnerable.
static proto_item * proto_tree_add_boolean64 ( proto_tree * tree , int hfindex , tvbuff_t * tvb , gint start , gint length , guint64 value ) {
 proto_item * pi ;
 header_field_info * hfinfo ;
 CHECK_FOR_NULL_TREE ( tree ) ;
 TRY_TO_FAKE_THIS_ITEM ( tree , hfindex , hfinfo ) ;
 DISSECTOR_ASSERT_FIELD_TYPE ( hfinfo , FT_BOOLEAN ) ;
 pi = proto_tree_add_pi ( tree , hfinfo , tvb , start , & length ) ;
 proto_tree_set_boolean ( PNODE_FINFO ( pi ) , value ) ;
 return pi ;
 }

Answer (0 or 1):
~~~~

## 34. reveal:test:1429

Arm: B2; phiên: legacy; seed: 42; dataset/split: reveal/test.
SHA-256 prompt: `52bc731d269af0b0f5e430b6ee37f7908a1fe4e6ec1d3c50c7063f2f4983333a`

~~~~text
You are now an excellent programmer. You are conducting a function vulnerability detection task for C/C++ language.

static void encode_superblock ( VP9_COMP * cpi , TOKENEXTRA * * t , int output_enabled , int mi_row , int mi_col , BLOCK_SIZE bsize , PICK_MODE_CONTEXT * ctx ) {
 VP9_COMMON * const cm = & cpi -> common ;
 MACROBLOCK * const x = & cpi -> mb ;
 MACROBLOCKD * const xd = & x -> e_mbd ;
 MODE_INFO * * mi_8x8 = xd -> mi ;
 MODE_INFO * mi = mi_8x8 [ 0 ] ;
 MB_MODE_INFO * mbmi = & mi -> mbmi ;
 const int seg_skip = vp9_segfeature_active ( & cm -> seg , mbmi -> segment_id , SEG_LVL_SKIP ) ;
 const int mis = cm -> mi_stride ;
 const int mi_width = num_8x8_blocks_wide_lookup [ bsize ] ;
 const int mi_height = num_8x8_blocks_high_lookup [ bsize ] ;
 x -> skip_recode = ! x -> select_tx_size && mbmi -> sb_type >= BLOCK_8X8 && cpi -> oxcf . aq_mode != COMPLEXITY_AQ && cpi -> oxcf . aq_mode != CYCLIC_REFRESH_AQ && cpi -> sf . allow_skip_recode ;
 if ( ! x -> skip_recode && ! cpi -> sf . use_nonrd_pick_mode ) vpx_memset ( x -> skip_txfm , 0 , sizeof ( x -> skip_txfm ) ) ;
 x -> skip_optimize = ctx -> is_coded ;
 ctx -> is_coded = 1 ;
 x -> use_lp32x32fdct = cpi -> sf . use_lp32x32fdct ;
 x -> skip_encode = ( ! output_enabled && cpi -> sf . skip_encode_frame && x -> q_index < QIDX_SKIP_THRESH ) ;
 if ( x -> skip_encode ) return ;
 set_ref_ptrs ( cm , xd , mbmi -> ref_frame [ 0 ] , mbmi -> ref_frame [ 1 ] ) ;
 cpi -> zbin_mode_boost = get_zbin_mode_boost ( mbmi , cpi -> zbin_mode_boost_enabled ) ;
 vp9_update_zbin_extra ( cpi , x ) ;
 if ( ! is_inter_block ( mbmi ) ) {
 int plane ;
 mbmi -> skip = 1 ;
 for ( plane = 0 ;
 plane < MAX_MB_PLANE ;
 ++ plane ) vp9_encode_intra_block_plane ( x , MAX ( bsize , BLOCK_8X8 ) , plane ) ;
 if ( output_enabled ) sum_intra_stats ( & cm -> counts , mi ) ;
 vp9_tokenize_sb ( cpi , t , ! output_enabled , MAX ( bsize , BLOCK_8X8 ) ) ;
 }
 else {
 int ref ;
 const int is_compound = has_second_ref ( mbmi ) ;
 for ( ref = 0 ;
 ref < 1 + is_compound ;
 ++ ref ) {
 YV12_BUFFER_CONFIG * cfg = get_ref_frame_buffer ( cpi , mbmi -> ref_frame [ ref ] ) ;
 vp9_setup_pre_planes ( xd , ref , cfg , mi_row , mi_col , & xd -> block_refs [ ref ] -> sf ) ;
 }
 if ( ! cpi -> sf . reuse_inter_pred_sby || seg_skip ) vp9_build_inter_predictors_sby ( xd , mi_row , mi_col , MAX ( bsize , BLOCK_8X8 ) ) ;
 vp9_build_inter_predictors_sbuv ( xd , mi_row , mi_col , MAX ( bsize , BLOCK_8X8 ) ) ;
 if ( ! x -> skip ) {
 mbmi -> skip = 1 ;
 vp9_encode_sb ( x , MAX ( bsize , BLOCK_8X8 ) ) ;
 vp9_tokenize_sb ( cpi , t , ! output_enabled , MAX ( bsize , BLOCK_8X8 ) ) ;
 }
 else {
 mbmi -> skip = 1 ;
 if ( output_enabled && ! seg_skip ) cm -> counts . skip [ vp9_get_skip_context ( xd ) ] [ 1 ] ++ ;
 reset_skip_context ( xd , MAX ( bsize , BLOCK_8X8 ) ) ;
 }
 }
 if ( output_enabled ) {
 if ( cm -> tx_mode == TX_MODE_SELECT && mbmi -> sb_type >= BLOCK_8X8 && ! ( is_inter_block ( mbmi ) && ( mbmi -> skip || seg_skip ) ) ) {
 ++ get_tx_counts ( max_txsize_lookup [ bsize ] , vp9_get_tx_size_context ( xd ) , & cm -> counts . tx ) [ mbmi -> tx_size ] ;
 }
 else {
 int x , y ;
 TX_SIZE tx_size ;
 if ( is_inter_block ( & mi -> mbmi ) ) {
 tx_size = MIN ( tx_mode_to_biggest_tx_size [ cm -> tx_mode ] , max_txsize_lookup [ bsize ] ) ;
 }
 else {
 tx_size = ( bsize >= BLOCK_8X8 ) ? mbmi -> tx_size : TX_4X4 ;
 }
 for ( y = 0 ;
 y < mi_height ;
 y ++ ) for ( x = 0 ;
 x < mi_width ;
 x ++ ) if ( mi_col + x < cm -> mi_cols && mi_row + y < cm -> mi_rows ) mi_8x8 [ mis * y + x ] -> mbmi . tx_size = tx_size ;
 }
 }
 }

In the above code snippet, check for potential security vulnerabilities and answer with a single digit: 1 if Vulnerable, 0 if Non-vulnerable.

The node information of the code snippet is as follows:
Node 25769803802: (BLOCK) '{  VP9_COMMON * const cm = & cpi -> comm...'
Node 25769803803: (BLOCK) '<empty>'
Node 25769803804: (BLOCK) '<empty>'
Node 25769803805: (BLOCK) '{  int plane ;  mbmi -> skip = 1 ;  for ...'
Node 25769803806: (BLOCK) '<empty>'
Node 25769803807: (BLOCK) '{  int ref ;  const int is_compound = ha...'
Node 25769803808: (BLOCK) '{  YV12_BUFFER_CONFIG * cfg = get_ref_fr...'
Node 25769803809: (BLOCK) '<empty>'
Node 25769803810: (BLOCK) '{  mbmi -> skip = 1 ;  vp9_encode_sb ( x...'
Node 25769803811: (BLOCK) '{  mbmi -> skip = 1 ;  if ( output_enabl...'
Node 25769803812: (BLOCK) '<empty>'
Node 25769803813: (BLOCK) '{  if ( cm -> tx_mode == TX_MODE_SELECT ...'
Node 25769803814: (BLOCK) '{  ++ get_tx_counts ( max_txsize_lookup ...'
Node 25769803815: (BLOCK) '{  int x , y ;  TX_SIZE tx_size ;  if ( ...'
Node 25769803816: (BLOCK) '{  tx_size = MIN ( tx_mode_to_biggest_tx...'
Node 25769803817: (BLOCK) '{ tx_size = ( bsize >= BLOCK_8X8 ) ? mbm...'
Node 25769803818: (BLOCK) '<empty>'
Node 30064771247: (CALL) 'const cm = & cpi -> common'
Node 30064771248: (CALL) '& cpi -> common'
Node 30064771249: (CALL) 'cpi -> common'
Node 30064771250: (CALL) 'const x = & cpi -> mb'
Node 30064771251: (CALL) '& cpi -> mb'
Node 30064771252: (CALL) 'cpi -> mb'
Node 30064771253: (CALL) 'const xd = & x -> e_mbd'
Node 30064771254: (CALL) '& x -> e_mbd'
Node 30064771255: (CALL) 'x -> e_mbd'
Node 30064771256: (CALL) '* mi_8x8 = xd -> mi'
Node 30064771257: (CALL) 'xd -> mi'
Node 30064771258: (CALL) 'mi = mi_8x8 [ 0 ]'
Node 30064771259: (CALL) 'mi_8x8 [ 0 ]'
Node 30064771260: (CALL) 'mbmi = & mi -> mbmi'
Node 30064771261: (CALL) '& mi -> mbmi'
Node 30064771262: (CALL) 'mi -> mbmi'
Node 30064771263: (CALL) 'seg_skip = vp9_segfeature_active ( & cm ...'
Node 30064771264: (CALL) 'vp9_segfeature_active ( & cm -> seg , mb...'
Node 30064771265: (CALL) '& cm -> seg'
Node 30064771266: (CALL) 'cm -> seg'
Node 30064771267: (CALL) 'mbmi -> segment_id'
Node 30064771268: (CALL) 'mis = cm -> mi_stride'
Node 30064771269: (CALL) 'cm -> mi_stride'
The edge information of the code snippet is as follows:
Edge: Node 25769803802 -> AST -> Node 30064771247
Edge: Node 25769803802 -> AST -> Node 30064771250
Edge: Node 25769803802 -> AST -> Node 30064771253
Edge: Node 25769803802 -> AST -> Node 30064771256
Edge: Node 25769803802 -> AST -> Node 30064771258
Edge: Node 25769803802 -> AST -> Node 30064771260
Edge: Node 25769803802 -> AST -> Node 30064771263
Edge: Node 25769803802 -> AST -> Node 30064771268
Edge: Node 30064771247 -> ARGUMENT -> Node 30064771248
Edge: Node 30064771247 -> AST -> Node 30064771248
Edge: Node 30064771247 -> POST_DOMINATE -> Node 30064771248
Edge: Node 30064771248 -> ARGUMENT -> Node 30064771249

The following is an example, and it is Non-vulnerable.
static void encode_superblock ( VP9_COMP * cpi , TOKENEXTRA * * t , int output_enabled , int mi_row , int mi_col , BLOCK_SIZE bsize , PICK_MODE_CONTEXT * ctx ) {
 VP9_COMMON * const cm = & cpi -> common ;
 MACROBLOCK * const x = & cpi -> mb ;
 MACROBLOCKD * const xd = & x -> e_mbd ;
 MODE_INFO * mi_8x8 = xd -> mi ;
 MODE_INFO * mi = mi_8x8 ;
 MB_MODE_INFO * mbmi = & mi -> mbmi ;
 const int seg_skip = vp9_segfeature_active ( & cm -> seg , mbmi -> segment_id , SEG_LVL_SKIP ) ;
 const int mis = cm -> mi_stride ;
 const int mi_width = num_8x8_blocks_wide_lookup [ bsize ] ;
 const int mi_height = num_8x8_blocks_high_lookup [ bsize ] ;
 x -> skip_recode = ! x -> select_tx_size && mbmi -> sb_type >= BLOCK_8X8 && cpi -> oxcf . aq_mode != COMPLEXITY_AQ && cpi -> oxcf . aq_mode != CYCLIC_REFRESH_AQ && cpi -> sf . allow_skip_recode ;
 if ( ! x -> skip_recode && ! cpi -> sf . use_nonrd_pick_mode ) vpx_memset ( x -> skip_txfm , 0 , sizeof ( x -> skip_txfm ) ) ;
 x -> skip_optimize = ctx -> is_coded ;
 ctx -> is_coded = 1 ;
 x -> use_lp32x32fdct = cpi -> sf . use_lp32x32fdct ;
 x -> skip_encode = ( ! output_enabled && cpi -> sf . skip_encode_frame && x -> q_index < QIDX_SKIP_THRESH ) ;
 if ( x -> skip_encode ) return ;
 set_ref_ptrs ( cm , xd , mbmi -> ref_frame [ 0 ] , mbmi -> ref_frame [ 1 ] ) ;
 cpi -> zbin_mode_boost = get_zbin_mode_boost ( mbmi , cpi -> zbin_mode_boost_enabled ) ;
 vp9_update_zbin_extra ( cpi , x ) ;
 if ( ! is_inter_block ( mbmi ) ) {
 int plane ;
 mbmi -> skip = 1 ;
 for ( plane = 0 ;
 plane < MAX_MB_PLANE ;
 ++ plane ) vp9_encode_intra_block_plane ( x , MAX ( bsize , BLOCK_8X8 ) , plane ) ;
 if ( output_enabled ) sum_intra_stats ( & cm -> counts , mi ) ;
 vp9_tokenize_sb ( cpi , t , ! output_enabled , MAX ( bsize , BLOCK_8X8 ) ) ;
 }
 else {
 int ref ;
 const int is_compound = has_second_ref ( mbmi ) ;
 for ( ref = 0 ;
 ref < 1 + is_compound ;
 ++ ref ) {
 YV12_BUFFER_CONFIG * cfg = get_ref_frame_buffer ( cpi , mbmi -> ref_frame [ ref ] ) ;
 vp9_setup_pre_planes ( xd , ref , cfg , mi_row , mi_col , & xd -> block_refs [ ref ] -> sf ) ;
 }
 if ( ! cpi -> sf . reuse_inter_pred_sby || seg_skip ) vp9_build_inter_predictors_sby ( xd , mi_row , mi_col , MAX ( bsize , BLOCK_8X8 ) ) ;
 vp9_build_inter_predictors_sbuv ( xd , mi_row , mi_col , MAX ( bsize , BLOCK_8X8 ) ) ;
 vp9_encode_sb ( x , MAX ( bsize , BLOCK_8X8 ) ) ;
 vp9_tokenize_sb ( cpi , t , ! output_enabled , MAX ( bsize , BLOCK_8X8 ) ) ;
 }
 if ( output_enabled ) {
 if ( cm -> tx_mode == TX_MODE_SELECT && mbmi -> sb_type >= BLOCK_8X8 && ! ( is_inter_block ( mbmi ) && ( mbmi -> skip || seg_skip ) ) ) {
 ++ get_tx_counts ( max_txsize_lookup [ bsize ] , vp9_get_tx_size_context ( xd ) , & cm -> counts . tx ) [ mbmi -> tx_size ] ;
 }
 else {
 int x , y ;
 TX_SIZE tx_size ;
 if ( is_inter_block ( & mi -> mbmi ) ) {
 tx_size = MIN ( tx_mode_to_biggest_tx_size [ cm -> tx_mode ] , max_txsize_lookup [ bsize ] ) ;
 }
 else {
 tx_size = ( bsize >= BLOCK_8X8 ) ? mbmi -> tx_size : TX_4X4 ;
 }
 for ( y = 0 ;
 y < mi_height ;
 y ++ ) for ( x = 0 ;
 x < mi_width ;
 x ++ ) if ( mi_col + x < cm -> mi_cols && mi_row + y < cm -> mi_rows ) mi_8x8 [ mis * y + x ] . src_mi -> mbmi . tx_size = tx_size ;
 }
 }
 }

Answer (0 or 1):
~~~~

## 35. reveal:test:886

Arm: B2-flip; phiên: frozen; seed: 42; dataset/split: reveal/test.
SHA-256 prompt: `169266089157ac9135abd13b0647e8d91da1f7388c137b230fbbee915af49fe9`

~~~~text
You are now an excellent programmer. You are conducting a function vulnerability detection task for C/C++ language.

void proto_register_h245 ( void ) {
 static hf_register_info hf [ ] = {
 {
 & hf_h245_pdu_type , {
 "PDU Type" , "h245.pdu_type" , FT_UINT32 , BASE_DEC , VALS ( h245_MultimediaSystemControlMessage_vals ) , 0 , "Type of H.245 PDU" , HFILL }
 }
 , {
 & hf_h245Manufacturer , {
 "H.245 Manufacturer" , "h245.Manufacturer" , FT_UINT32 , BASE_HEX , VALS ( H221ManufacturerCode_vals ) , 0 , "h245.H.221 Manufacturer" , HFILL }
 }
 , {
 & hf_h245_subMessageIdentifier_standard , {
 "subMessageIdentifier" , "h245.subMessageIdentifier.standard" , FT_UINT32 , BASE_DEC , VALS ( h245_h239subMessageIdentifier_vals ) , 0 , NULL , HFILL }
 }
 , # line 1 "../../asn1/h245/packet-h245-hfarr.c" {
 & hf_h245_OpenLogicalChannel_PDU , {
 "OpenLogicalChannel" , "h245.OpenLogicalChannel_element" , FT_NONE , BASE_NONE , NULL , 0 , NULL , HFILL }
 }
 , {
 & hf_h245_request , {
 "request" , "h245.request" , FT_UINT32 , BASE_DEC , VALS ( h245_RequestMessage_vals ) , 0 , "RequestMessage" , HFILL }
 }
 , {
 & hf_h245_response , {
 "response" , "h245.response" , FT_UINT32 , BASE_DEC , VALS ( h245_ResponseMessage_vals ) , 0 , "ResponseMessage" , HFILL }
 }
 , {
 & hf_h245_command , {
 "command" , "h245.command" , FT_UINT32 , BASE_DEC , VALS ( h245_CommandMessage_vals ) , 0 , "CommandMessage" , HFILL }
 }
 , {
 & hf_h245_indication , {
 "indication" , "h245.indication" , FT_UINT32 , BASE_DEC , VALS ( h245_IndicationMessage_vals ) , 0 , "IndicationMessage" , HFILL }
 }
 , {
 & hf_h245_nonStandardMsg , {
 "nonStandard" , "h245.nonStandard_element" , FT_NONE , BASE_NONE , NULL , 0 , "NonStandardMessage" , HFILL }
 }
 , {
 & hf_h245_masterSlaveDetermination , {
 "masterSlaveDetermination" , "h245.masterSlaveDetermination_element" , FT_NONE , BASE_NONE , NULL , 0 , NULL , HFILL }
 }
 , {
 & hf_h245_terminalCapabilitySet , {
 "terminalCapabilitySet" , "h245.terminalCapabilitySet_element" , FT_NONE , BASE_NONE , NULL , 0 , NULL , HFILL }
 }
 , {
 & hf_h245_openLogicalChannel , {
 "openLogicalChannel" , "h245.openLogicalChannel_element" , FT_NONE , BASE_NONE , NULL , 0 , NULL , HFILL }
 }
 , {
 & hf_h245_closeLogicalChannel , {
 "closeLogicalChannel" , "h245.closeLogicalChannel_element" , FT_NONE , BASE_NONE , NULL , 0 , NULL , HFILL }
 }
 , {
 & hf_h245_requestChannelClose , {
 "requestChannelClose" , "h245.requestChannelClose_element" , FT_NONE , BASE_NONE , NULL , 0 , NULL , HFILL }
 }
 , {
 & hf_h245_multiplexEntrySend , {
 "multiplexEntrySend" , "h245.multiplexEntrySend_element" , FT_NONE , BASE_NONE , NULL , 0 , NULL , HFILL }
 }
 , {
 & hf_h245_requestMultiplexEntry , {
 "requestMultiplexEntry" , "h245.requestMultiplexEntry_element" , FT_NONE , BASE_NONE , NULL , 0 , NULL , HFILL }
 }
 , {
 & hf_h245_requestMode , {
 "requestMode" , "h245.requestMode_element" , FT_NONE , BASE_NONE , NULL , 0 , NULL , HFILL }
 }
 , {
 & hf_h245_roundTripDelayRequest , {
 "roundTripDelayRequest" , "h245.roundTripDelayRequest_element" , FT_NONE , BASE_NONE , NULL , 0 , NULL , HFILL }
 }
 , {
 & hf_h245_maintenanceLoopRequest , {
 "maintenanceLoopRequest" , "h245.maintenanceLoopRequest_element" , FT_NONE , BASE_NONE , NULL , 0 , NULL , HFILL }
 }
 , {
 & hf_h245_communicationModeRequest , {
 "communicationModeRequest" , "h245.communicationModeRequest_element" , FT_NONE , BASE_NONE , NULL , 0 , NULL , HFILL }
 }
 , {
 & hf_h245_conferenceRequest , {
 "conferenceRequest" , "h245.conferenceRequest" , FT_UINT32 , BASE_DEC , VALS ( h245_ConferenceRequest_vals ) , 0 , NULL , HFILL }
 }
 , {
 & hf_h245_multilinkRequest , {
 "multilinkRequest" , "h245.multilinkRequest" , FT_UINT32 , BASE_DEC , VALS ( h245_MultilinkRequest_vals ) , 0 , NULL , HFILL }
 }
 , {
 & hf_h245_logicalChannelRateRequest , {
 "logicalChannelRateRequest" , "h245.logicalChannelRateRequest_element" , FT_NONE , BASE_NONE , NULL , 0 , NULL , HFILL }
 }
 , {
 & hf_h245_genericRequest , {
 "genericRequest" , "h245.genericRequest_element" , FT_NONE , BASE_NONE , NULL , 0 , "GenericMessage" , HFILL }
 }
 , {
 & hf_h245_masterSlaveDeterminationAck , {
 "masterSlaveDeterminationAck" , "h245.masterSlaveDeterminationAck_element" , FT_NONE , BASE_NONE , NULL , 0 , NULL , HFILL }
 }
 , {
 & hf_h245_masterSlaveDeterminationReject , {
 "masterSlaveDeterminationReject" , "h245.masterSlaveDeterminationReject_element" , FT_NONE , BASE_NONE , NULL , 0 , NULL , HFILL }
 }
 , {
 & hf_h245_terminalCapabilitySetAck , {
 "terminalCapabilitySetAck" , "h245.terminalCapabilitySetAck_element" , FT_NONE , BASE_NONE , NULL , 0 , NULL , HFILL }
 }
 , {
 & hf_h245_terminalCapabilitySetReject , {
 "terminalCapabilitySetReject" , "h245.terminalCapabilitySetReject_element" , FT_NONE , BASE_NONE , NULL , 0 , NULL , HFILL }
 }
 , {
 & hf_h245_openLogicalChannelAck , {
 "openLogicalChannelAck" , "h245.openLogicalChannelAck_element" , FT_NONE , BASE_NONE , NULL , 0 , NULL , HFILL }
 }
 , {
 & hf_h245_openLogicalChannelReject , {
 "openLogicalChannelReject" , "h245.openLogicalChannelReject_element" , FT_NONE , BASE_NONE , NULL , 0 , NULL , HFILL }
 }
 , {
 & hf_h245_closeLogicalChannelAck , {
 "closeLogicalChannelAck" , "h245.closeLogicalChannelAck_element" , FT_NONE , BASE_NONE , NULL , 0 , NULL , HFILL }
 }
 , {
 & hf_h245_requestChannelCloseAck , {
 "requestChannelCloseAck" , "h245.requestChannelCloseAck_element" , FT_NONE , BASE_NONE , NULL , 0 , NULL , HFILL }
 }
 , {
 & hf_h245_requestChannelCloseReject , {
 "requestChannelCloseReject" , "h245.requestChannelCloseReject_element" , FT_NONE , BASE_NONE , NULL , 0 , NULL , HFILL }
 }
 , {
 & hf_h245_multiplexEntrySendAck , {
 "multiplexEntrySendAck" , "h245.multiplexEntrySendAck_element" , FT_NONE , BASE_NONE , NULL , 0 , NULL , HFILL }
 }
 , {
 & hf_h245_multiplexEntrySendReject , {
 "multiplexEntrySendReject" , "h245.multiplexEntrySendReject_element" , FT_NONE , BASE_NONE , NULL , 0 , NULL , HFILL }
 }
 , {
 & hf_h245_requestMultiplexEntryAck , {
 "requestMultiplexEntryAck" , "h245.requestMultiplexEntryAck_element" , FT_NONE , BASE_NONE , NULL , 0 , NULL , HFILL }
 }
 , {
 & hf_h245_requestMultiplexEntryReject , {
 "requestMultiplexEntryReject" , "h245.requestMultiplexEntryReject_element" , FT_NONE , BASE_NONE , NULL , 0 , NULL , HFILL }
 }
 , {
 & hf_h245_requestModeAck , {
 "requestModeAck" , "h245.requestModeAck_element" , FT_NONE , BASE_NONE , NULL , 0 , NULL , HFILL }
 }
 , {
 & hf_h245_requestModeReject , {
 "requestModeReject" , "h245.requestModeReject_element" , FT_NONE , BASE_NONE , NULL , 0 , NULL , HFILL }
 }
 , {
 & hf_h245_roundTripDelayResponse , {
 "roundTripDelayResponse" , "h245.roundTripDelayResponse_element" , FT_NONE , BASE_NONE , NULL , 0 , NULL , HFILL }
 }
 , {
 & hf_h245_maintenanceLoopAck , {
 "maintenanceLoopAck" , "h245.maintenanceLoopAck_element" , FT_NONE , BASE_NONE , NULL , 0 , NULL , HFILL }
 }
 , {
 & hf_h245_maintenanceLoopReject , {
 "maintenanceLoopReject" , "h245.maintenanceLoopReject_element" , FT_NONE , BASE_NONE , NULL , 0 , NULL , HFILL }
 }
 , {
 & hf_h245_communicationModeResponse , {
 "communicationModeResponse" , "h245.communicationModeResponse" , FT_UINT32 , BASE_DEC , VALS ( h245_CommunicationModeResponse_vals ) , 0 , NULL , HFILL }
 }
 , {
 & hf_h245_conferenceResponse , {
 "conferenceResponse" , "h245.conferenceResponse" , FT_UINT32 , BASE_DEC , VALS ( h245_ConferenceResponse_vals ) , 0 , NULL , HFILL }
 }
 , {
 & hf_h245_multilinkResponse , {
 "multilinkResponse" , "h245.multilinkResponse" , FT_UINT32 , BASE_DEC , VALS ( h245_MultilinkResponse_vals ) , 0 , NULL , HFILL }
 }
 , {
 & hf_h245_logicalChannelRateAcknowledge , {
 "logicalChannelRateAcknowledge" , "h245.logicalChannelRateAcknowledge_element" , FT_NONE , BASE_NONE , NULL , 0 , NULL , HFILL }
 }
 , {
 & hf_h245_logicalChannelRateReject , {
 "logicalChannelRateReject" , "h245.logicalChannelRateReject_element" , FT_NONE , BASE_NONE , NULL , 0 , NULL , HFILL }
 }
 , {
 & hf_h245_genericResponse , {
 "genericResponse" , "h245.genericResponse_element" , FT_NONE , BASE_NONE , NULL , 0 , "GenericMessage" , HFILL }
 }
 , {
 & hf_h245_maintenanceLoopOffCommand , {
 "maintenanceLoopOffCommand" , "h245.maintenanceLoopOffCommand_element" , FT_NONE , BASE_NONE , NULL , 0 , NULL , HFILL }
 }
 , {
 & hf_h245_sendTerminalCapabilitySet , {
 "sendTerminalCapabilitySet" , "h245.sendTerminalCapabilitySet" , FT_UINT32 , BASE_DEC , VALS ( h245_SendTerminalCapabilitySet_vals ) , 0 , NULL , HFILL }
 }
 , {
 & hf_h245_encryptionCommand , {
 "encryptionCommand" , "h245.encryptionCommand" , FT_UINT32 , BASE_DEC , VALS ( h245_EncryptionCommand_vals ) , 0 , NULL , HFILL }
 }
 , {
 & hf_h245_flowControlCommand , {
 "flowControlCommand" , "h245.flowControlCommand_element" , FT_NONE , BASE_NONE , NULL , 0 , NULL , HFILL }
 }
 , {
 & hf_h245_endSessionCommand , {
 "endSessionCommand" , "h245.endSessionCommand" , FT_UINT32 , BASE_DEC , VALS ( h245_EndSessionCommand_vals ) , 0 , NULL , HFILL }
 }
 , {
 & hf_h245_miscellaneousCommand , {
 "miscellaneousCommand" , "h245.miscellaneousCommand_element" , FT_NONE , BASE_NONE , NULL , 0 , NULL , HFILL }
 }
 , {
 & hf_h245_communicationModeCommand , {
 "communicationModeCommand" , "h245.communicationModeCommand_element" , FT_NONE , BASE_NONE , NULL , 0 , NULL , HFILL }
 }
 , {
 & hf_h245_conferenceCommand , {
 "conferenceCommand" , "h245.conferenceCommand" , FT_UINT32 , BASE_DEC , VALS ( h245_ConferenceCommand_vals ) ,
/* [TRUNCATED TARGET] */

In the above code snippet, check for potential security vulnerabilities and answer with a single digit: 1 if Vulnerable, 0 if Non-vulnerable.

The node information of the code snippet is as follows:
Node 25769803815: (BLOCK) '{  static hf_register_info hf [ ] = {  {...'
Node 25769803857: (BLOCK) '<empty>'
Node 25769803858: (BLOCK) '<empty>'
Node 25769803859: (BLOCK) '<empty>'
Node 107374182412: (METHOD) 'void proto_register_h245 ( void ) {  sta...'
Node 107374182420: (METHOD) 'register_init_routine ( h245_init ) ;'
Node 107374182421: (METHOD) 'proto_register_field_array ( proto_h245 ...'
Node 107374182422: (METHOD) 'proto_register_subtree_array ( ett , arr...'
Node 111669149705: (METHOD_PARAMETER_IN) 'void'
Node 111669149712: (METHOD_PARAMETER_IN) 'h245_init'
Node 111669149713: (METHOD_PARAMETER_IN) 'proto_h245'
Node 111669149714: (METHOD_PARAMETER_IN) 'hf'
Node 111669149715: (METHOD_PARAMETER_IN) 'array_length ( hf )'
Node 111669149716: (METHOD_PARAMETER_IN) 'ett'
Node 111669149717: (METHOD_PARAMETER_IN) 'array_length ( ett )'
Node 115964117001: (METHOD_PARAMETER_OUT) 'void'
Node 115964117008: (METHOD_PARAMETER_OUT) 'h245_init'
Node 115964117009: (METHOD_PARAMETER_OUT) 'proto_h245'
Node 115964117010: (METHOD_PARAMETER_OUT) 'hf'
Node 115964117011: (METHOD_PARAMETER_OUT) 'array_length ( hf )'
Node 115964117012: (METHOD_PARAMETER_OUT) 'ett'
Node 115964117013: (METHOD_PARAMETER_OUT) 'array_length ( ett )'
Node 124554051596: (METHOD_RETURN) 'RET'
Node 124554051604: (METHOD_RETURN) 'RET'
Node 124554051605: (METHOD_RETURN) 'RET'
Node 124554051606: (METHOD_RETURN) 'RET'
The edge information of the code snippet is as follows:
Edge: Node 107374182412 -> AST -> Node 111669149705
Edge: Node 107374182412 -> AST -> Node 25769803815
Edge: Node 107374182412 -> AST -> Node 124554051596
Edge: Node 107374182412 -> AST -> Node 115964117001
Edge: Node 107374182412 -> CFG -> Node 124554051596
Edge: Node 107374182412 -> CONTAINS -> Node 25769803815
Edge: Node 107374182412 -> DOMINATE -> Node 124554051596
Edge: Node 107374182412 -> REACHING_DEF -> Node 111669149705
Edge: Node 107374182420 -> AST -> Node 111669149712
Edge: Node 107374182420 -> AST -> Node 25769803857
Edge: Node 107374182420 -> AST -> Node 124554051604
Edge: Node 107374182420 -> AST -> Node 115964117008
Edge: Node 107374182420 -> CFG -> Node 124554051604
Edge: Node 107374182420 -> CONTAINS -> Node 25769803857
Edge: Node 107374182420 -> DOMINATE -> Node 124554051604
Edge: Node 107374182420 -> REACHING_DEF -> Node 111669149712
Edge: Node 107374182421 -> AST -> Node 111669149713
Edge: Node 107374182421 -> AST -> Node 111669149714
Edge: Node 107374182421 -> AST -> Node 111669149715
Edge: Node 107374182421 -> AST -> Node 25769803858
Edge: Node 107374182421 -> AST -> Node 124554051605
Edge: Node 107374182421 -> AST -> Node 115964117009
Edge: Node 107374182421 -> AST -> Node 115964117010

The following is an example, and it is Non-vulnerable.
void proto_register_h245 ( void ) {
 static hf_register_info hf [ ] = {
 {
 & hf_h245_pdu_type , {
 "PDU Type" , "h245.pdu_type" , FT_UINT32 , BASE_DEC , VALS ( h245_MultimediaSystemControlMessage_vals ) , 0 , "Type of H.245 PDU" , HFILL }
 }
 , {
 & hf_h245Manufacturer , {
 "H.245 Manufacturer" , "h245.Manufacturer" , FT_UINT32 , BASE_HEX , VALS ( H221ManufacturerCode_vals ) , 0 , "h245.H.221 Manufacturer" , HFILL }
 }
 , {
 & hf_h245_subMessageIdentifier_standard , {
 "subMessageIdentifier" , "h245.subMessageIdentifier.standard" , FT_UINT32 , BASE_DEC , VALS ( h245_h239subMessageIdentifier_vals ) , 0 , NULL , HFILL }
 }
 , # line 1 "../../asn1/h245/packet-h245-hfarr.c" {
 & hf_h245_OpenLogicalChannel_PDU , {
 "OpenLogicalChannel" , "h245.OpenLogicalChannel_element" , FT_NONE , BASE_NONE , NULL , 0 , NULL , HFILL }
 }
 , {
 & hf_h245_request , {
 "request" , "h245.request" , FT_UINT32 , BASE_DEC , VALS ( h245_RequestMessage_vals ) , 0 , "RequestMessage" , HFILL }
 }
 , {
 & hf_h245_response , {
 "response" , "h245.response" , FT_UINT32 , BASE_DEC , VALS ( h245_ResponseMessage_vals ) , 0 , "ResponseMessage" , HFILL }
 }
 , {
 & hf_h245_command , {
 "command" , "h245.command" , FT_UINT32 , BASE_DEC , VALS ( h245_CommandMessage_vals ) , 0 , "CommandMessage" , HFILL }
 }
 , {
 & hf_h245_indication , {
 "indication" , "h245.indication" , FT_UINT32 , BASE_DEC , VALS ( h245_IndicationMessage_vals ) , 0 , "IndicationMessage" , HFILL }
 }
 , {
 & hf_h245_nonStandardMsg , {
 "nonStandard" , "h245.nonStandard_element" , FT_NONE , BASE_NONE , NULL , 0 , "NonStandardMessage" , HFILL }
 }
 , {
 & hf_h245_masterSlaveDetermination , {
 "masterSlaveDetermination" , "h245.masterSlaveDetermination_element" , FT_NONE , BASE_NONE , NULL , 0 , NULL , HFILL }
 }
 , {
 & hf_h245_terminalCapabilitySet , {
 "terminalCapabilitySet" , "h245.terminalCapabilitySet_element" , FT_NONE , BASE_NONE , NULL , 0 , NULL , HFILL }
 }
 , {
 & hf_h245_openLogicalChannel , {
 "openLogicalChannel" , "h245.openLogicalChannel_element" , FT_NONE , BASE_NONE , NULL , 0 , NULL , HFILL }
 }
 , {
 & hf_h245_closeLogicalChannel , {
 "closeLogicalChannel" , "h245.closeLogicalChannel_element" , FT_NONE , BASE_NONE , NULL , 0 , NULL , HFILL }
 }
 , {
 & hf_h245_requestChannelClose , {
 "requestChannelClose" , "h245.requestChannelClose_element" , FT_NONE , BASE_NONE , NULL , 0 , NULL , HFILL }
 }
 , {
 & hf_h245_multiplexEntrySend , {
 "multiplexEntrySend" , "h245.multiplexEntrySend_element" , FT_NONE , BASE_NONE , NULL , 0 , NULL , HFILL }
 }
 , {
 & hf_h245_requestMultiplexEntry , {
 "requestMultiplexEntry" , "h245.requestMultiplexEntry_element" , FT_NONE , BASE_NONE , NULL , 0 , NULL , HFILL }
 }
 , {
 & hf_h245_requestMode , {
 "requestMode" , "h245.requestMode_element" , FT_NONE , BASE_NONE , NULL , 0 , NULL , HFILL }
 }
 , {
 & hf_h245_roundTripDelayRequest , {
 "roundTripDelayRequest" , "h245.roundTripDelayRequest_element" , FT_NONE , BASE_NONE , NULL , 0 , NULL , HFILL }
 }
 , {
 & hf_h245_maintenanceLoopRequest , {
 "maintenanceLoopRequest" , "h245.maintenanceLoopRequest_element" , FT_NONE , BASE_NONE , NULL , 0 , NULL , HFILL }
 }
 , {
 & hf_h245_communicationModeRequest , {
 "communicationModeRequest" , "h245.communicationModeRequest_element" , FT_NONE , BASE_NONE , NULL , 0 , NULL , HFILL }
 }
 , {
 & hf_h245_conferenceRequest , {
 "conferenceRequest" , "h245.conferenceRequest" , FT_UINT32 , BASE_DEC , VALS ( h245_ConferenceRequest_vals ) , 0 , NULL , HFILL }
 }
 , {
 & hf_h245_multilinkRequest , {
 "multilinkRequest" , "h245.multilinkRequest" , FT_UINT32 , BASE_DEC , VALS ( h245_MultilinkRequest_vals ) , 0 , NULL , HFILL }
 }
 , {
 & hf_h245_logicalChannelRateRequest , {
 "logicalChannelRateRequest" , "h245.logicalChannelRateRequest_element" , FT_NONE , BASE_NONE , NULL , 0 , NULL , HFILL }
 }
 , {
 & hf_h245_genericRequest , {
 "genericRequest" , "h245.genericRequest_element" , FT_NONE , BASE_NONE , NULL , 0 , "GenericMessage" , HFILL }
 }
 , {
 & hf_h245_masterSlaveDeterminationAck , {
 "masterSlaveDeterminationAck" , "h245.masterSlaveDeterminationAck_element" , FT_NONE , BASE_NONE , NULL , 0 , NULL , HFILL }
 }
 , {
 & hf_h245_masterSlaveDeterminationReject , {
 "masterSlaveDeterminationReject" , "h245.masterSlaveDeterminationReject_element" , FT_NONE , BASE_NONE , NULL , 0 , NULL , HFILL }
 }
 , {
 & hf_h245_terminalCapabilitySetAck , {
 "terminalCapabilitySetAck" , "h245.terminalCapabilitySetAck_element" , FT_NONE , BASE_NONE , NULL , 0 , NULL , HFILL }
 }
 , {
 & hf_h245_terminalCapabilitySetReject , {
 "
/* [TRUNCATED] */

Answer (0 or 1):
~~~~

## 36. reveal:validation:303

Arm: B2-flip; phiên: legacy; seed: 42; dataset/split: reveal/validation.
SHA-256 prompt: `07cb3dc552142648e33f9c6ea255201331fd153386b081d3473a43b07c98c92b`

~~~~text
You are now an excellent programmer. You are conducting a function vulnerability detection task for C/C++ language.

int proto_get_id_by_filter_name ( const gchar * filter_name ) {
 const protocol_t * protocol = NULL ;
 DISSECTOR_ASSERT_HINT ( filter_name , "No filter name present" ) ;
 protocol = ( const protocol_t * ) g_hash_table_lookup ( proto_filter_names , filter_name ) ;
 if ( protocol == NULL ) return - 1 ;
 return protocol -> proto_id ;
 }

In the above code snippet, check for potential security vulnerabilities and answer with a single digit: 1 if Vulnerable, 0 if Non-vulnerable.

The node information of the code snippet is as follows:
Node 25769803808: (BLOCK) '{  const protocol_t * protocol = NULL ; ...'
Node 25769803809: (BLOCK) '<empty>'
Node 30064771316: (CALL) 'protocol = NULL'
Node 30064771317: (CALL) 'DISSECTOR_ASSERT_HINT ( filter_name , "N...'
Node 30064771318: (CALL) 'protocol = ( const protocol_t * ) g_hash...'
Node 30064771319: (CALL) '( const protocol_t * ) g_hash_table_look...'
Node 30064771320: (CALL) 'g_hash_table_lookup ( proto_filter_names...'
Node 30064771321: (CALL) 'protocol == NULL'
Node 30064771322: (CALL) '- 1'
Node 30064771323: (CALL) 'protocol -> proto_id'
Node 47244640280: (CONTROL_STRUCTURE) 'if ( protocol == NULL ) return - 1 ;'
Node 55834574868: (FIELD_IDENTIFIER) 'proto_id'
Node 68719476985: (IDENTIFIER) 'protocol'
Node 68719476986: (IDENTIFIER) '<unknown> NULL'
Node 68719476987: (IDENTIFIER) 'filter_name'
Node 68719476988: (IDENTIFIER) 'protocol'
Node 68719476989: (IDENTIFIER) '<unknown> proto_filter_names'
Node 68719476990: (IDENTIFIER) 'filter_name'
Node 68719476991: (IDENTIFIER) 'protocol'
Node 68719476992: (IDENTIFIER) '<unknown> NULL'
Node 68719476993: (IDENTIFIER) 'protocol'
Node 90194313293: (LITERAL) '"No filter name present"'
Node 90194313294: (LITERAL) '1'
Node 94489280551: (LOCAL) 'const protocol_t * protocol'
Node 94489280552: (LOCAL) '<unknown> NULL'
Node 94489280553: (LOCAL) '<unknown> proto_filter_names'
Node 107374182406: (METHOD) 'int proto_get_id_by_filter_name ( const ...'
Node 111669149710: (METHOD_PARAMETER_IN) 'const gchar * filter_name'
Node 115964117006: (METHOD_PARAMETER_OUT) 'const gchar * filter_name'
Node 124554051590: (METHOD_RETURN) 'RET'
Node 141733920771: (RETURN) 'return - 1 ;'
Node 141733920772: (RETURN) 'return protocol -> proto_id ;'
Node 176093659138: (TYPE_REF) 'const protocol_t *'
The edge information of the code snippet is as follows:
Edge: Node 25769803808 -> AST -> Node 94489280551
Edge: Node 25769803808 -> AST -> Node 30064771316
Edge: Node 25769803808 -> AST -> Node 30064771317
Edge: Node 25769803808 -> AST -> Node 30064771318
Edge: Node 25769803808 -> AST -> Node 47244640280
Edge: Node 25769803808 -> AST -> Node 141733920772
Edge: Node 25769803808 -> AST -> Node 94489280552
Edge: Node 25769803808 -> AST -> Node 94489280553
Edge: Node 25769803809 -> AST -> Node 141733920771
Edge: Node 30064771316 -> ARGUMENT -> Node 68719476985
Edge: Node 30064771316 -> ARGUMENT -> Node 68719476986
Edge: Node 30064771316 -> AST -> Node 68719476985
Edge: Node 30064771316 -> AST -> Node 68719476986
Edge: Node 30064771316 -> CFG -> Node 68719476987
Edge: Node 30064771316 -> DOMINATE -> Node 68719476987
Edge: Node 30064771316 -> POST_DOMINATE -> Node 68719476986
Edge: Node 30064771316 -> REACHING_DEF -> Node 124554051590
Edge: Node 30064771317 -> ARGUMENT -> Node 68719476987
Edge: Node 30064771317 -> ARGUMENT -> Node 90194313293
Edge: Node 30064771317 -> AST -> Node 68719476987

The following is an example, and it is Vulnerable.
int proto_get_id_by_short_name ( const gchar * short_name ) {
 const protocol_t * protocol = NULL ;
 DISSECTOR_ASSERT_HINT ( short_name , "No short name present" ) ;
 protocol = ( const protocol_t * ) g_hash_table_lookup ( proto_short_names , short_name ) ;
 if ( protocol == NULL ) return - 1 ;
 return protocol -> proto_id ;
 }

Answer (0 or 1):
~~~~

## 37. reveal:validation:1995

Arm: B2-rand; phiên: frozen; seed: 42; dataset/split: reveal/validation.
SHA-256 prompt: `879300ec01d065b4a69d6db53f399a1c95689455ea152ceccecaf1ba12d3bc5d`

~~~~text
You are now an excellent programmer. You are conducting a function vulnerability detection task for C/C++ language.

static inline MagickBooleanType IsPixelInfoGray ( const PixelInfo * restrict pixel_info ) {
 if ( ( pixel_info -> colorspace != GRAYColorspace ) && ( pixel_info -> colorspace != RGBColorspace ) ) return ( MagickFalse ) ;
 if ( ( AbsolutePixelValue ( pixel_info -> red - pixel_info -> green ) < MagickEpsilon ) && ( AbsolutePixelValue ( pixel_info -> green - pixel_info -> blue ) < MagickEpsilon ) ) return ( MagickTrue ) ;
 return ( MagickFalse ) ;
 }

In the above code snippet, check for potential security vulnerabilities and answer with a single digit: 1 if Vulnerable, 0 if Non-vulnerable.

The node information of the code snippet is as follows:
Node 25769803794: (BLOCK) '{  if ( ( pixel_info -> colorspace != GR...'
Node 25769803795: (BLOCK) '<empty>'
Node 25769803796: (BLOCK) '<empty>'
Node 30064771129: (CALL) '( pixel_info -> colorspace != GRAYColors...'
Node 30064771130: (CALL) 'pixel_info -> colorspace != GRAYColorspa...'
Node 30064771131: (CALL) 'pixel_info -> colorspace'
Node 30064771132: (CALL) 'pixel_info -> colorspace != RGBColorspac...'
Node 30064771133: (CALL) 'pixel_info -> colorspace'
Node 30064771134: (CALL) '( AbsolutePixelValue ( pixel_info -> red...'
Node 30064771135: (CALL) 'AbsolutePixelValue ( pixel_info -> red -...'
Node 30064771136: (CALL) 'AbsolutePixelValue ( pixel_info -> red -...'
Node 30064771137: (CALL) 'pixel_info -> red - pixel_info -> green'
Node 30064771138: (CALL) 'pixel_info -> red'
Node 30064771139: (CALL) 'pixel_info -> green'
Node 30064771140: (CALL) 'AbsolutePixelValue ( pixel_info -> green...'
Node 30064771141: (CALL) 'AbsolutePixelValue ( pixel_info -> green...'
Node 30064771142: (CALL) 'pixel_info -> green - pixel_info -> blue'
Node 30064771143: (CALL) 'pixel_info -> green'
Node 30064771144: (CALL) 'pixel_info -> blue'
Node 47244640262: (CONTROL_STRUCTURE) 'if ( ( pixel_info -> colorspace != GRAYC...'
Node 47244640263: (CONTROL_STRUCTURE) 'if ( ( AbsolutePixelValue ( pixel_info -...'
Node 55834574861: (FIELD_IDENTIFIER) 'colorspace'
Node 55834574862: (FIELD_IDENTIFIER) 'colorspace'
Node 55834574863: (FIELD_IDENTIFIER) 'red'
Node 55834574864: (FIELD_IDENTIFIER) 'green'
Node 55834574865: (FIELD_IDENTIFIER) 'green'
Node 55834574866: (FIELD_IDENTIFIER) 'blue'
Node 68719476796: (IDENTIFIER) 'pixel_info'
Node 68719476797: (IDENTIFIER) '<unknown> GRAYColorspace'
Node 68719476798: (IDENTIFIER) 'pixel_info'
Node 68719476799: (IDENTIFIER) '<unknown> RGBColorspace'
Node 68719476800: (IDENTIFIER) '<unknown> MagickFalse'
Node 68719476801: (IDENTIFIER) 'pixel_info'
Node 68719476802: (IDENTIFIER) 'pixel_info'
Node 68719476803: (IDENTIFIER) '<unknown> MagickEpsilon'
Node 68719476804: (IDENTIFIER) 'pixel_info'
Node 68719476805: (IDENTIFIER) 'pixel_info'
Node 68719476806: (IDENTIFIER) '<unknown> MagickEpsilon'
Node 68719476807: (IDENTIFIER) '<unknown> MagickTrue'
Node 68719476808: (IDENTIFIER) '<unknown> MagickFalse'
The edge information of the code snippet is as follows:
Edge: Node 25769803794 -> AST -> Node 47244640262
Edge: Node 25769803794 -> AST -> Node 47244640263
Edge: Node 30064771129 -> ARGUMENT -> Node 30064771130
Edge: Node 30064771129 -> ARGUMENT -> Node 30064771132
Edge: Node 30064771129 -> AST -> Node 30064771130
Edge: Node 30064771129 -> AST -> Node 30064771132
Edge: Node 30064771129 -> CDG -> Node 30064771138
Edge: Node 30064771129 -> CDG -> Node 30064771137
Edge: Node 30064771129 -> CDG -> Node 30064771136
Edge: Node 30064771129 -> CDG -> Node 30064771135
Edge: Node 30064771129 -> CDG -> Node 30064771134
Edge: Node 30064771129 -> CDG -> Node 68719476803
Edge: Node 30064771129 -> CDG -> Node 68719476802
Edge: Node 30064771129 -> CDG -> Node 68719476801
Edge: Node 30064771129 -> CDG -> Node 68719476800

The following is an example, and it is Non-vulnerable.
static gcry_err_code_t dummy_verify ( int algorithm , gcry_mpi_t hash , gcry_mpi_t * data , gcry_mpi_t * pkey , int ( * cmp ) ( void * , gcry_mpi_t ) , void * opaquev , int flags , int hashalgo ) {
 ( void ) algorithm ;
 ( void ) hash ;
 ( void ) data ;
 ( void ) pkey ;
 ( void ) cmp ;
 ( void ) opaquev ;
 ( void ) flags ;
 ( void ) hashalgo ;
 fips_signal_error ( "using dummy public key function" ) ;
 return GPG_ERR_NOT_IMPLEMENTED ;
 }

Answer (0 or 1):
~~~~

## 38. reveal:test:802

Arm: B2-rand; phiên: frozen; seed: 43; dataset/split: reveal/test.
SHA-256 prompt: `bed4eff171776bdbd0f3de9b26d5a449d847f032ed00af0be2463be2152d2016`

~~~~text
You are now an excellent programmer. You are conducting a function vulnerability detection task for C/C++ language.

static void decode_filter_coeffs ( TAKDecContext * s , int filter_order , int size , int filter_quant , int16_t * filter ) {
 GetBitContext * gb = & s -> gb ;
 int i , j , a , b ;
 int filter_tmp [ MAX_PREDICTORS ] ;
 int16_t predictors [ MAX_PREDICTORS ] ;
 predictors [ 0 ] = get_sbits ( gb , 10 ) ;
 predictors [ 1 ] = get_sbits ( gb , 10 ) ;
 predictors [ 2 ] = get_sbits ( gb , size ) << ( 10 - size ) ;
 predictors [ 3 ] = get_sbits ( gb , size ) << ( 10 - size ) ;
 if ( filter_order > 4 ) {
 int av_uninit ( code_size ) ;
 int code_size_base = size - get_bits1 ( gb ) ;
 for ( i = 4 ;
 i < filter_order ;
 i ++ ) {
 if ( ! ( i & 3 ) ) code_size = code_size_base - get_bits ( gb , 2 ) ;
 predictors [ i ] = get_sbits ( gb , code_size ) << ( 10 - size ) ;
 }
 }
 filter_tmp [ 0 ] = predictors [ 0 ] << 6 ;
 for ( i = 1 ;
 i < filter_order ;
 i ++ ) {
 int * p1 = & filter_tmp [ 0 ] ;
 int * p2 = & filter_tmp [ i - 1 ] ;
 for ( j = 0 ;
 j < ( i + 1 ) / 2 ;
 j ++ ) {
 int tmp = * p1 + ( predictors [ i ] * * p2 + 256 >> 9 ) ;
 * p2 = * p2 + ( predictors [ i ] * * p1 + 256 >> 9 ) ;
 * p1 = tmp ;
 p1 ++ ;
 p2 -- ;
 }
 filter_tmp [ i ] = predictors [ i ] << 6 ;
 }
 a = 1 << ( 32 - ( 15 - filter_quant ) ) ;
 b = 1 << ( ( 15 - filter_quant ) - 1 ) ;
 for ( i = 0 , j = filter_order - 1 ;
 i < filter_order / 2 ;
 i ++ , j -- ) {
 filter [ j ] = a - ( ( filter_tmp [ i ] + b ) >> ( 15 - filter_quant ) ) ;
 filter [ i ] = a - ( ( filter_tmp [ j ] + b ) >> ( 15 - filter_quant ) ) ;
 }
 }

In the above code snippet, check for potential security vulnerabilities and answer with a single digit: 1 if Vulnerable, 0 if Non-vulnerable.

The node information of the code snippet is as follows:
Node 25769803788: (BLOCK) '{  GetBitContext * gb = & s -> gb ;  int...'
Node 25769803789: (BLOCK) '{  int av_uninit ( code_size ) ;  int co...'
Node 25769803790: (BLOCK) '{  if ( ! ( i & 3 ) ) code_size = code_s...'
Node 25769803791: (BLOCK) '<empty>'
Node 25769803792: (BLOCK) '{  int * p1 = & filter_tmp [ 0 ] ;  int ...'
Node 25769803793: (BLOCK) '{  int tmp = * p1 + ( predictors [ i ] *...'
Node 25769803794: (BLOCK) '<empty>'
Node 25769803795: (BLOCK) '<empty>'
Node 25769803796: (BLOCK) '{  filter [ j ] = a - ( ( filter_tmp [ i...'
Node 25769803837: (BLOCK) '<empty>'
Node 30064771119: (CALL) 'gb = & s -> gb'
Node 30064771120: (CALL) '& s -> gb'
Node 30064771121: (CALL) 's -> gb'
Node 30064771122: (CALL) 'filter_tmp [ MAX_PREDICTORS ]'
Node 30064771123: (CALL) 'filter_tmp [ MAX_PREDICTORS ]'
Node 30064771124: (CALL) 'predictors [ MAX_PREDICTORS ]'
Node 30064771125: (CALL) 'predictors [ MAX_PREDICTORS ]'
Node 30064771126: (CALL) 'predictors [ 0 ] = get_sbits ( gb , 10 )'
Node 30064771127: (CALL) 'predictors [ 0 ]'
Node 30064771128: (CALL) 'get_sbits ( gb , 10 )'
Node 30064771129: (CALL) 'predictors [ 1 ] = get_sbits ( gb , 10 )'
Node 30064771130: (CALL) 'predictors [ 1 ]'
Node 30064771131: (CALL) 'get_sbits ( gb , 10 )'
Node 30064771132: (CALL) 'predictors [ 2 ] = get_sbits ( gb , size...'
Node 30064771133: (CALL) 'predictors [ 2 ]'
Node 30064771134: (CALL) 'get_sbits ( gb , size ) << ( 10 - size )'
Node 30064771135: (CALL) 'get_sbits ( gb , size )'
Node 30064771136: (CALL) '10 - size'
Node 30064771137: (CALL) 'predictors [ 3 ] = get_sbits ( gb , size...'
Node 30064771138: (CALL) 'predictors [ 3 ]'
Node 30064771139: (CALL) 'get_sbits ( gb , size ) << ( 10 - size )'
Node 30064771140: (CALL) 'get_sbits ( gb , size )'
Node 30064771141: (CALL) '10 - size'
Node 30064771142: (CALL) 'filter_order > 4'
Node 30064771143: (CALL) 'code_size_base = size - get_bits1 ( gb )'
Node 30064771144: (CALL) 'size - get_bits1 ( gb )'
Node 30064771145: (CALL) 'get_bits1 ( gb )'
Node 30064771146: (CALL) 'i = 4'
Node 30064771147: (CALL) 'i < filter_order'
Node 30064771148: (CALL) 'i ++'
The edge information of the code snippet is as follows:
Edge: Node 25769803788 -> AST -> Node 30064771119
Edge: Node 25769803788 -> AST -> Node 30064771122
Edge: Node 25769803788 -> AST -> Node 30064771124
Edge: Node 25769803788 -> AST -> Node 30064771126
Edge: Node 25769803788 -> AST -> Node 30064771129
Edge: Node 25769803788 -> AST -> Node 30064771132
Edge: Node 25769803788 -> AST -> Node 30064771137
Edge: Node 25769803789 -> AST -> Node 30064771143
Edge: Node 30064771119 -> ARGUMENT -> Node 30064771120
Edge: Node 30064771119 -> AST -> Node 30064771120
Edge: Node 30064771119 -> POST_DOMINATE -> Node 30064771120

The following is an example, and it is Non-vulnerable.
static inline uint32_t be32_to_cpu ( uint32_t v ) {
 return bswap32 ( v ) ;
 }

Answer (0 or 1):
~~~~

## 39. reveal:validation:399

Arm: B2-rand; phiên: frozen; seed: 44; dataset/split: reveal/validation.
SHA-256 prompt: `e09082e2afd39ccd71785960b9a679278e4a6a5d616a4c6f62e769309c7962dd`

~~~~text
You are now an excellent programmer. You are conducting a function vulnerability detection task for C/C++ language.

static USBEndpoint * xhci_epid_to_usbep ( XHCIEPContext * epctx ) {
 USBPort * uport ;
 uint32_t token ;
 if ( ! epctx ) {
 return NULL ;
 }
 uport = epctx -> xhci -> slots [ epctx -> slotid - 1 ] . uport ;
 token = ( epctx -> epid & 1 ) ? USB_TOKEN_IN : USB_TOKEN_OUT ;
 if ( ! uport ) {
 return NULL ;
 }
 return usb_ep_get ( uport -> dev , token , epctx -> epid >> 1 ) ;
 }

In the above code snippet, check for potential security vulnerabilities and answer with a single digit: 1 if Vulnerable, 0 if Non-vulnerable.

The node information of the code snippet is as follows:
Node 25769803806: (BLOCK) '{  USBPort * uport ;  uint32_t token ;  ...'
Node 25769803807: (BLOCK) '{ return NULL ; }'
Node 25769803808: (BLOCK) '{ return NULL ; }'
Node 30064771266: (CALL) '! epctx'
Node 30064771267: (CALL) 'uport = epctx -> xhci -> slots [ epctx -...'
Node 30064771268: (CALL) 'epctx -> xhci -> slots [ epctx -> slotid...'
Node 30064771269: (CALL) 'epctx -> xhci -> slots [ epctx -> slotid...'
Node 30064771270: (CALL) 'epctx -> xhci -> slots'
Node 30064771271: (CALL) 'epctx -> xhci'
Node 30064771272: (CALL) 'epctx -> slotid - 1'
Node 30064771273: (CALL) 'epctx -> slotid'
Node 30064771274: (CALL) 'token = ( epctx -> epid & 1 ) ? USB_TOKE...'
Node 30064771275: (CALL) '( epctx -> epid & 1 ) ? USB_TOKEN_IN : U...'
Node 30064771276: (CALL) 'epctx -> epid & 1'
Node 30064771277: (CALL) 'epctx -> epid'
Node 30064771278: (CALL) '! uport'
Node 30064771279: (CALL) 'usb_ep_get ( uport -> dev , token , epct...'
Node 30064771280: (CALL) 'uport -> dev'
Node 30064771281: (CALL) 'epctx -> epid >> 1'
Node 30064771282: (CALL) 'epctx -> epid'
Node 47244640274: (CONTROL_STRUCTURE) 'if ( ! epctx ) { return NULL ; }'
Node 47244640275: (CONTROL_STRUCTURE) 'if ( ! uport ) { return NULL ; }'
Node 55834574882: (FIELD_IDENTIFIER) 'xhci'
Node 55834574883: (FIELD_IDENTIFIER) 'slots'
Node 55834574884: (FIELD_IDENTIFIER) 'slotid'
Node 55834574885: (FIELD_IDENTIFIER) 'uport'
Node 55834574886: (FIELD_IDENTIFIER) 'epid'
Node 55834574887: (FIELD_IDENTIFIER) 'dev'
Node 55834574888: (FIELD_IDENTIFIER) 'epid'
Node 68719476893: (IDENTIFIER) 'epctx'
Node 68719476894: (IDENTIFIER) '<unknown> NULL'
Node 68719476895: (IDENTIFIER) 'uport'
Node 68719476896: (IDENTIFIER) 'epctx'
Node 68719476897: (IDENTIFIER) 'epctx'
Node 68719476898: (IDENTIFIER) 'token'
Node 68719476899: (IDENTIFIER) 'epctx'
Node 68719476900: (IDENTIFIER) '<unknown> USB_TOKEN_IN'
Node 68719476901: (IDENTIFIER) '<unknown> USB_TOKEN_OUT'
Node 68719476902: (IDENTIFIER) 'uport'
Node 68719476903: (IDENTIFIER) '<unknown> NULL'
The edge information of the code snippet is as follows:
Edge: Node 25769803806 -> AST -> Node 47244640274
Edge: Node 25769803806 -> AST -> Node 30064771267
Edge: Node 25769803806 -> AST -> Node 30064771274
Edge: Node 25769803806 -> AST -> Node 47244640275
Edge: Node 30064771266 -> ARGUMENT -> Node 68719476893
Edge: Node 30064771266 -> AST -> Node 68719476893
Edge: Node 30064771266 -> CDG -> Node 55834574886
Edge: Node 30064771266 -> CDG -> Node 55834574885
Edge: Node 30064771266 -> CDG -> Node 55834574882
Edge: Node 30064771266 -> CDG -> Node 55834574884
Edge: Node 30064771266 -> CDG -> Node 55834574883
Edge: Node 30064771266 -> CDG -> Node 68719476897
Edge: Node 30064771266 -> CDG -> Node 68719476896
Edge: Node 30064771266 -> CDG -> Node 68719476899

The following is an example, and it is Non-vulnerable.
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
 static void U_CALLCONV _LMBCSFromUnicode ( UConverter
/* [TRUNCATED] */

Answer (0 or 1):
~~~~

## 40. reveal:validation:2011

Arm: B2-rep; phiên: legacy; seed: 42; dataset/split: reveal/validation.
SHA-256 prompt: `5f800597bccc072ab03d14be0221c00c1aaa6971b15e1dc707d6b9b6a204aa4e`

~~~~text
You are now an excellent programmer. You are conducting a function vulnerability detection task for C/C++ language.

static GList * location_list_from_uri_list ( const GList * uris ) {
 const GList * l ;
 GList * files ;
 GFile * f ;
 files = NULL ;
 for ( l = uris ;
 l != NULL ;
 l = l -> next ) {
 f = g_file_new_for_uri ( l -> data ) ;
 files = g_list_prepend ( files , f ) ;
 }
 return g_list_reverse ( files ) ;
 }

In the above code snippet, check for potential security vulnerabilities and answer with a single digit: 1 if Vulnerable, 0 if Non-vulnerable.

The node information of the code snippet is as follows:
Node 25769803779: (BLOCK) '{  const GList * l ;  GList * files ;  G...'
Node 25769803780: (BLOCK) '{  f = g_file_new_for_uri ( l -> data ) ...'
Node 30064771084: (CALL) 'files = NULL'
Node 30064771085: (CALL) 'l = uris'
Node 30064771086: (CALL) 'l != NULL'
Node 30064771087: (CALL) 'l = l -> next'
Node 30064771088: (CALL) 'l -> next'
Node 30064771089: (CALL) 'f = g_file_new_for_uri ( l -> data )'
Node 30064771090: (CALL) 'g_file_new_for_uri ( l -> data )'
Node 30064771091: (CALL) 'l -> data'
Node 30064771092: (CALL) 'files = g_list_prepend ( files , f )'
Node 30064771093: (CALL) 'g_list_prepend ( files , f )'
Node 30064771094: (CALL) 'g_list_reverse ( files )'
Node 47244640258: (CONTROL_STRUCTURE) 'for (l = uris ;l != NULL;l = l -> next)'
Node 55834574850: (FIELD_IDENTIFIER) 'next'
Node 55834574851: (FIELD_IDENTIFIER) 'data'
Node 68719476749: (IDENTIFIER) 'files'
Node 68719476750: (IDENTIFIER) '<unknown> NULL'
Node 68719476751: (IDENTIFIER) 'l'
Node 68719476752: (IDENTIFIER) 'uris'
Node 68719476753: (IDENTIFIER) 'l'
Node 68719476754: (IDENTIFIER) '<unknown> NULL'
Node 68719476755: (IDENTIFIER) 'l'
Node 68719476756: (IDENTIFIER) 'l'
Node 68719476757: (IDENTIFIER) 'f'
Node 68719476758: (IDENTIFIER) 'l'
Node 68719476759: (IDENTIFIER) 'files'
Node 68719476760: (IDENTIFIER) 'files'
Node 68719476761: (IDENTIFIER) 'f'
Node 68719476762: (IDENTIFIER) 'files'
Node 94489280516: (LOCAL) 'const GList * l'
Node 94489280517: (LOCAL) 'GList * files'
Node 94489280518: (LOCAL) 'GFile * f'
Node 94489280519: (LOCAL) '<unknown> NULL'
Node 107374182402: (METHOD) 'static GList * location_list_from_uri_li...'
Node 111669149697: (METHOD_PARAMETER_IN) 'const GList * uris'
Node 115964116993: (METHOD_PARAMETER_OUT) 'const GList * uris'
Node 124554051586: (METHOD_RETURN) 'RET'
Node 128849018881: (MODIFIER) '<empty>'
Node 141733920770: (RETURN) 'return g_list_reverse ( files ) ;'
The edge information of the code snippet is as follows:
Edge: Node 25769803779 -> AST -> Node 94489280516
Edge: Node 25769803779 -> AST -> Node 94489280517
Edge: Node 25769803779 -> AST -> Node 94489280518
Edge: Node 25769803779 -> AST -> Node 30064771084
Edge: Node 25769803779 -> AST -> Node 47244640258
Edge: Node 25769803779 -> AST -> Node 141733920770
Edge: Node 25769803779 -> AST -> Node 94489280519
Edge: Node 25769803780 -> AST -> Node 30064771089
Edge: Node 25769803780 -> AST -> Node 30064771092
Edge: Node 30064771084 -> ARGUMENT -> Node 68719476749
Edge: Node 30064771084 -> ARGUMENT -> Node 68719476750
Edge: Node 30064771084 -> AST -> Node 68719476749
Edge: Node 30064771084 -> AST -> Node 68719476750
Edge: Node 30064771084 -> CFG -> Node 68719476751
Edge: Node 30064771084 -> DOMINATE -> Node 68719476751

The following is an example, and it is Non-vulnerable.
static GList * get_file_list_for_launch_locations ( GList * locations ) {
 GList * files , * l ;
 LaunchLocation * location ;
 files = NULL ;
 for ( l = locations ;
 l != NULL ;
 l = l -> next ) {
 location = l -> data ;
 files = g_list_prepend ( files , nautilus_file_ref ( location -> file ) ) ;
 }
 return g_list_reverse ( files ) ;
 }

Answer (0 or 1):
~~~~

## 41. reveal:test:1546

Arm: B0; phiên: legacy; seed: 42; dataset/split: reveal/test.
SHA-256 prompt: `4222c3e48f108c3c82fa6d8ec53204b01f3750742d655533ec51afe661dd664d`

~~~~text
You are now an excellent programmer. You are conducting a function vulnerability detection task for C/C++ language.

static GVariant * pk_transaction_get_property ( GDBusConnection * connection_ , const gchar * sender , const gchar * object_path , const gchar * interface_name , const gchar * property_name , GError * * error , gpointer user_data ) {
 PkTransaction * transaction = PK_TRANSACTION ( user_data ) ;
 PkTransactionPrivate * priv = transaction -> priv ;
 if ( g_strcmp0 ( property_name , "Role" ) == 0 ) return g_variant_new_uint32 ( priv -> role ) ;
 if ( g_strcmp0 ( property_name , "Status" ) == 0 ) return g_variant_new_uint32 ( priv -> status ) ;
 if ( g_strcmp0 ( property_name , "LastPackage" ) == 0 ) return _g_variant_new_maybe_string ( priv -> last_package_id ) ;
 if ( g_strcmp0 ( property_name , "Uid" ) == 0 ) return g_variant_new_uint32 ( priv -> uid ) ;
 if ( g_strcmp0 ( property_name , "Percentage" ) == 0 ) return g_variant_new_uint32 ( transaction -> priv -> percentage ) ;
 if ( g_strcmp0 ( property_name , "AllowCancel" ) == 0 ) return g_variant_new_boolean ( priv -> allow_cancel ) ;
 if ( g_strcmp0 ( property_name , "CallerActive" ) == 0 ) return g_variant_new_boolean ( priv -> caller_active ) ;
 if ( g_strcmp0 ( property_name , "ElapsedTime" ) == 0 ) return g_variant_new_uint32 ( priv -> elapsed_time ) ;
 if ( g_strcmp0 ( property_name , "Speed" ) == 0 ) return g_variant_new_uint32 ( priv -> speed ) ;
 if ( g_strcmp0 ( property_name , "DownloadSizeRemaining" ) == 0 ) return g_variant_new_uint64 ( priv -> download_size_remaining ) ;
 if ( g_strcmp0 ( property_name , "TransactionFlags" ) == 0 ) return g_variant_new_uint64 ( priv -> cached_transaction_flags ) ;
 return NULL ;
 }

In the above code snippet, check for potential security vulnerabilities and answer with a single digit: 1 if Vulnerable, 0 if Non-vulnerable.

The node information of the code snippet is as follows:

The edge information of the code snippet is as follows:


The following is an example, and it is .


Answer (0 or 1):
~~~~

## 42. reveal:validation:976

Arm: B2-rep; phiên: legacy; seed: 42; dataset/split: reveal/validation.
SHA-256 prompt: `a6b02797177d4ab81daf7c7b489ea76a18dd8abba7418ae9c4ec450866d1466c`

~~~~text
You are now an excellent programmer. You are conducting a function vulnerability detection task for C/C++ language.

static int resize_key_frame ( VP8_COMP * cpi ) {
 # if CONFIG_SPATIAL_RESAMPLING VP8_COMMON * cm = & cpi -> common ;
 if ( cpi -> oxcf . allow_spatial_resampling && ( cpi -> oxcf . end_usage == USAGE_STREAM_FROM_SERVER ) ) {
 int UNINITIALIZED_IS_SAFE ( hr ) , UNINITIALIZED_IS_SAFE ( hs ) ;
 int UNINITIALIZED_IS_SAFE ( vr ) , UNINITIALIZED_IS_SAFE ( vs ) ;
 int new_width , new_height ;
 if ( cpi -> buffer_level < ( cpi -> oxcf . resample_down_water_mark * cpi -> oxcf . optimal_buffer_level / 100 ) ) {
 cm -> horiz_scale = ( cm -> horiz_scale < ONETWO ) ? cm -> horiz_scale + 1 : ONETWO ;
 cm -> vert_scale = ( cm -> vert_scale < ONETWO ) ? cm -> vert_scale + 1 : ONETWO ;
 }
 else if ( cpi -> buffer_level > ( cpi -> oxcf . resample_up_water_mark * cpi -> oxcf . optimal_buffer_level / 100 ) ) {
 cm -> horiz_scale = ( cm -> horiz_scale > NORMAL ) ? cm -> horiz_scale - 1 : NORMAL ;
 cm -> vert_scale = ( cm -> vert_scale > NORMAL ) ? cm -> vert_scale - 1 : NORMAL ;
 }
 Scale2Ratio ( cm -> horiz_scale , & hr , & hs ) ;
 Scale2Ratio ( cm -> vert_scale , & vr , & vs ) ;
 new_width = ( ( hs - 1 ) + ( cpi -> oxcf . Width * hr ) ) / hs ;
 new_height = ( ( vs - 1 ) + ( cpi -> oxcf . Height * vr ) ) / vs ;
 if ( ( cm -> Width != new_width ) || ( cm -> Height != new_height ) ) {
 cm -> Width = new_width ;
 cm -> Height = new_height ;
 vp8_alloc_compressor_data ( cpi ) ;
 scale_and_extend_source ( cpi -> un_scaled_source , cpi ) ;
 return 1 ;
 }
 }
 # endif return 0 ;
 }

In the above code snippet, check for potential security vulnerabilities and answer with a single digit: 1 if Vulnerable, 0 if Non-vulnerable.

The node information of the code snippet is as follows:
Node 25769803803: (BLOCK) '{  # if CONFIG_SPATIAL_RESAMPLING VP8_CO...'
Node 107374182411: (METHOD) 'static int resize_key_frame ( VP8_COMP *...'
Node 111669149704: (METHOD_PARAMETER_IN) 'VP8_COMP * cpi'
Node 115964117000: (METHOD_PARAMETER_OUT) 'VP8_COMP * cpi'
Node 124554051595: (METHOD_RETURN) 'RET'
Node 128849018884: (MODIFIER) '<empty>'
The edge information of the code snippet is as follows:
Edge: Node 107374182411 -> AST -> Node 111669149704
Edge: Node 107374182411 -> AST -> Node 25769803803
Edge: Node 107374182411 -> AST -> Node 128849018884
Edge: Node 107374182411 -> AST -> Node 124554051595
Edge: Node 107374182411 -> AST -> Node 115964117000
Edge: Node 107374182411 -> CFG -> Node 124554051595
Edge: Node 107374182411 -> CONTAINS -> Node 25769803803
Edge: Node 107374182411 -> DOMINATE -> Node 124554051595
Edge: Node 107374182411 -> REACHING_DEF -> Node 111669149704
Edge: Node 111669149704 -> PARAMETER_LINK -> Node 115964117000
Edge: Node 111669149704 -> REACHING_DEF -> Node 115964117000
Edge: Node 111669149704 -> REACHING_DEF -> Node 124554051595
Edge: Node 124554051595 -> POST_DOMINATE -> Node 107374182411

The following is an example, and it is Non-vulnerable.
static void scale_and_extend_source ( YV12_BUFFER_CONFIG * sd , VP8_COMP * cpi ) {
 VP8_COMMON * cm = & cpi -> common ;
 if ( cm -> horiz_scale != 0 || cm -> vert_scale != 0 ) {
 # if CONFIG_SPATIAL_RESAMPLING int UNINITIALIZED_IS_SAFE ( hr ) , UNINITIALIZED_IS_SAFE ( hs ) ;
 int UNINITIALIZED_IS_SAFE ( vr ) , UNINITIALIZED_IS_SAFE ( vs ) ;
 int tmp_height ;
 if ( cm -> vert_scale == 3 ) tmp_height = 9 ;
 else tmp_height = 11 ;
 Scale2Ratio ( cm -> horiz_scale , & hr , & hs ) ;
 Scale2Ratio ( cm -> vert_scale , & vr , & vs ) ;
 vpx_scale_frame ( sd , & cpi -> scaled_source , cm -> temp_scale_frame . y_buffer , tmp_height , hs , hr , vs , vr , 0 ) ;
 vp8_yv12_extend_frame_borders ( & cpi -> scaled_source ) ;
 cpi -> Source = & cpi -> scaled_source ;
 # endif }
 else cpi -> Source = sd ;
 }

Answer (0 or 1):
~~~~

## 43. reveal:test:853

Arm: B0; phiên: legacy; seed: 42; dataset/split: reveal/test.
SHA-256 prompt: `9923c8e27ed7be3d5a3526f98d89832bcc14631a2e70e5b4ee3d89ac1e2ba861`

~~~~text
You are now an excellent programmer. You are conducting a function vulnerability detection task for C/C++ language.

static void pxa2xx_cm_write ( void * opaque , hwaddr addr , uint64_t value , unsigned size ) {
 PXA2xxState * s = ( PXA2xxState * ) opaque ;
 switch ( addr ) {
 case CCCR : case CKEN : s -> cm_regs [ addr >> 2 ] = value ;
 break ;
 case OSCC : s -> cm_regs [ addr >> 2 ] &= ~ 0x6c ;
 s -> cm_regs [ addr >> 2 ] |= value & 0x6e ;
 if ( ( value >> 1 ) & 1 ) s -> cm_regs [ addr >> 2 ] |= 1 << 0 ;
 break ;
 default : printf ( "%s: Bad register " REG_FMT "\n" , __FUNCTION__ , addr ) ;
 break ;
 }
 }

In the above code snippet, check for potential security vulnerabilities and answer with a single digit: 1 if Vulnerable, 0 if Non-vulnerable.

The node information of the code snippet is as follows:

The edge information of the code snippet is as follows:


The following is an example, and it is .


Answer (0 or 1):
~~~~

## 44. reveal:validation:526

Arm: B0; phiên: legacy; seed: 42; dataset/split: reveal/validation.
SHA-256 prompt: `fc5f323f013355037c267b77fa81c561f3edc68679c8a03de1b9dff709e1dde3`

~~~~text
You are now an excellent programmer. You are conducting a function vulnerability detection task for C/C++ language.

static double var_eq_const ( VariableStatData * vardata , Oid operator , Datum constval , bool constisnull , bool varonleft ) {
 double selec ;
 bool isdefault ;
 if ( constisnull ) return 0.0 ;
 if ( vardata -> isunique && vardata -> rel && vardata -> rel -> tuples >= 1.0 ) return 1.0 / vardata -> rel -> tuples ;
 if ( HeapTupleIsValid ( vardata -> statsTuple ) ) {
 Form_pg_statistic stats ;
 Datum * values ;
 int nvalues ;
 float4 * numbers ;
 int nnumbers ;
 bool match = false ;
 int i ;
 stats = ( Form_pg_statistic ) GETSTRUCT ( vardata -> statsTuple ) ;
 if ( get_attstatsslot ( vardata -> statsTuple , vardata -> atttype , vardata -> atttypmod , STATISTIC_KIND_MCV , InvalidOid , NULL , & values , & nvalues , & numbers , & nnumbers ) ) {
 FmgrInfo eqproc ;
 fmgr_info ( get_opcode ( operator ) , & eqproc ) ;
 for ( i = 0 ;
 i < nvalues ;
 i ++ ) {
 if ( varonleft ) match = DatumGetBool ( FunctionCall2Coll ( & eqproc , DEFAULT_COLLATION_OID , values [ i ] , constval ) ) ;
 else match = DatumGetBool ( FunctionCall2Coll ( & eqproc , DEFAULT_COLLATION_OID , constval , values [ i ] ) ) ;
 if ( match ) break ;
 }
 }
 else {
 values = NULL ;
 numbers = NULL ;
 i = nvalues = nnumbers = 0 ;
 }
 if ( match ) {
 selec = numbers [ i ] ;
 }
 else {
 double sumcommon = 0.0 ;
 double otherdistinct ;
 for ( i = 0 ;
 i < nnumbers ;
 i ++ ) sumcommon += numbers [ i ] ;
 selec = 1.0 - sumcommon - stats -> stanullfrac ;
 CLAMP_PROBABILITY ( selec ) ;
 otherdistinct = get_variable_numdistinct ( vardata , & isdefault ) - nnumbers ;
 if ( otherdistinct > 1 ) selec /= otherdistinct ;
 if ( nnumbers > 0 && selec > numbers [ nnumbers - 1 ] ) selec = numbers [ nnumbers - 1 ] ;
 }
 free_attstatsslot ( vardata -> atttype , values , nvalues , numbers , nnumbers ) ;
 }
 else {
 selec = 1.0 / get_variable_numdistinct ( vardata , & isdefault ) ;
 }
 CLAMP_PROBABILITY ( selec ) ;
 return selec ;
 }

In the above code snippet, check for potential security vulnerabilities and answer with a single digit: 1 if Vulnerable, 0 if Non-vulnerable.

The node information of the code snippet is as follows:

The edge information of the code snippet is as follows:


The following is an example, and it is .


Answer (0 or 1):
~~~~

## 45. reveal:validation:145

Arm: B2-rep; phiên: legacy; seed: 42; dataset/split: reveal/validation.
SHA-256 prompt: `b4b60bf6fc445e275618b5cd558dd9cf05a57c5d13b4bf0d81dff15cf356e0b5`

~~~~text
You are now an excellent programmer. You are conducting a function vulnerability detection task for C/C++ language.

static VALUE ossl_asn1_ ## klass ( int argc , VALUE * argv , VALUE self ) \ {
 return rb_funcall3 ( cASN1 ## klass , rb_intern ( "new" ) , argc , argv ) ;
 }
 OSSL_ASN1_IMPL_FACTORY_METHOD ( Boolean ) OSSL_ASN1_IMPL_FACTORY_METHOD ( Integer ) OSSL_ASN1_IMPL_FACTORY_METHOD ( Enumerated ) OSSL_ASN1_IMPL_FACTORY_METHOD ( BitString ) OSSL_ASN1_IMPL_FACTORY_METHOD ( OctetString ) OSSL_ASN1_IMPL_FACTORY_METHOD ( UTF8String ) OSSL_ASN1_IMPL_FACTORY_METHOD ( NumericString ) OSSL_ASN1_IMPL_FACTORY_METHOD ( PrintableString ) OSSL_ASN1_IMPL_FACTORY_METHOD ( T61String )

In the above code snippet, check for potential security vulnerabilities and answer with a single digit: 1 if Vulnerable, 0 if Non-vulnerable.

The following is an example, and it is Non-vulnerable.
static VALUE ossl_asn1_ ## klass ( int argc , VALUE * argv , VALUE self ) \ {
 return rb_funcall3 ( cASN1 ## klass , rb_intern ( "new" ) , argc , argv ) ;
 }
 OSSL_ASN1_IMPL_FACTORY_METHOD ( Boolean ) OSSL_ASN1_IMPL_FACTORY_METHOD ( Integer ) OSSL_ASN1_IMPL_FACTORY_METHOD ( Enumerated ) OSSL_ASN1_IMPL_FACTORY_METHOD ( BitString ) OSSL_ASN1_IMPL_FACTORY_METHOD ( OctetString ) OSSL_ASN1_IMPL_FACTORY_METHOD ( UTF8String ) OSSL_ASN1_IMPL_FACTORY_METHOD ( NumericString ) OSSL_ASN1_IMPL_FACTORY_METHOD ( PrintableString ) OSSL_ASN1_IMPL_FACTORY_METHOD ( T61String ) OSSL_ASN1_IMPL_FACTORY_METHOD ( VideotexString )

Answer (0 or 1):
~~~~

## 46. reveal:test:274

Arm: B2-rand; phiên: frozen; seed: 44; dataset/split: reveal/test.
SHA-256 prompt: `7c3bae35504b1599d8fbb7dd6e8df2ec76488b634a7e13358b3d132573ac3256`

~~~~text
You are now an excellent programmer. You are conducting a function vulnerability detection task for C/C++ language.

IN_PROC_BROWSER_TEST_F ( CrossOriginXHR , AllURLs ) {
 ASSERT_TRUE ( RunExtensionTest ( "cross_origin_xhr/all_urls" ) ) << message_ ;
 }

In the above code snippet, check for potential security vulnerabilities and answer with a single digit: 1 if Vulnerable, 0 if Non-vulnerable.

The node information of the code snippet is as follows:
Node 25769803790: (BLOCK) '{  ASSERT_TRUE ( RunExtensionTest ( "cro...'
Node 30064771140: (CALL) 'ASSERT_TRUE ( RunExtensionTest ( "cross_...'
Node 30064771141: (CALL) 'ASSERT_TRUE ( RunExtensionTest ( "cross_...'
Node 30064771142: (CALL) 'RunExtensionTest ( "cross_origin_xhr/all...'
Node 68719476807: (IDENTIFIER) '<unknown> message_'
Node 90194313240: (LITERAL) '"cross_origin_xhr/all_urls"'
Node 94489280529: (LOCAL) '<unknown> message_'
Node 107374182406: (METHOD) 'IN_PROC_BROWSER_TEST_F ( CrossOriginXHR ...'
Node 111669149700: (METHOD_PARAMETER_IN) 'CrossOriginXHR'
Node 111669149701: (METHOD_PARAMETER_IN) 'AllURLs'
Node 115964116996: (METHOD_PARAMETER_OUT) 'CrossOriginXHR'
Node 115964116997: (METHOD_PARAMETER_OUT) 'AllURLs'
Node 124554051590: (METHOD_RETURN) 'RET'
The edge information of the code snippet is as follows:
Edge: Node 25769803790 -> AST -> Node 30064771140
Edge: Node 25769803790 -> AST -> Node 94489280529
Edge: Node 30064771140 -> ARGUMENT -> Node 30064771141
Edge: Node 30064771140 -> ARGUMENT -> Node 68719476807
Edge: Node 30064771140 -> AST -> Node 30064771141
Edge: Node 30064771140 -> AST -> Node 68719476807
Edge: Node 30064771140 -> CFG -> Node 124554051590
Edge: Node 30064771140 -> DOMINATE -> Node 124554051590
Edge: Node 30064771140 -> POST_DOMINATE -> Node 68719476807
Edge: Node 30064771140 -> REACHING_DEF -> Node 124554051590
Edge: Node 30064771141 -> ARGUMENT -> Node 30064771142
Edge: Node 30064771141 -> AST -> Node 30064771142
Edge: Node 30064771141 -> CFG -> Node 68719476807
Edge: Node 30064771141 -> DOMINATE -> Node 68719476807
Edge: Node 30064771141 -> POST_DOMINATE -> Node 30064771142
Edge: Node 30064771141 -> REACHING_DEF -> Node 68719476807
Edge: Node 30064771141 -> REACHING_DEF -> Node 30064771140
Edge: Node 30064771141 -> REACHING_DEF -> Node 124554051590
Edge: Node 30064771142 -> ARGUMENT -> Node 90194313240
Edge: Node 30064771142 -> AST -> Node 90194313240
Edge: Node 30064771142 -> CFG -> Node 30064771141
Edge: Node 30064771142 -> DOMINATE -> Node 30064771141
Edge: Node 30064771142 -> POST_DOMINATE -> Node 90194313240
Edge: Node 30064771142 -> REACHING_DEF -> Node 30064771141
Edge: Node 30064771142 -> REACHING_DEF -> Node 124554051590
Edge: Node 68719476807 -> CFG -> Node 30064771140
Edge: Node 68719476807 -> DOMINATE -> Node 30064771140
Edge: Node 68719476807 -> POST_DOMINATE -> Node 30064771141
Edge: Node 68719476807 -> REACHING_DEF -> Node 30064771141
Edge: Node 68719476807 -> REACHING_DEF -> Node 30064771140
Edge: Node 68719476807 -> REACHING_DEF -> Node 124554051590
Edge: Node 68719476807 -> REF -> Node 94489280529
Edge: Node 90194313240 -> CFG -> Node 30064771142

The following is an example, and it is Non-vulnerable.
static void cleanst ( struct vars * v ) {
 struct subre * t ;
 struct subre * next ;
 for ( t = v -> treechain ;
 t != NULL ;
 t = next ) {
 next = t -> chain ;
 if ( ! ( t -> flags & INUSE ) ) FREE ( t ) ;
 }
 v -> treechain = NULL ;
 v -> treefree = NULL ;
 }

Answer (0 or 1):
~~~~

## 47. reveal:validation:1799

Arm: B1; phiên: legacy; seed: 42; dataset/split: reveal/validation.
SHA-256 prompt: `44374d1a036e335a01b2bb0b9611c50671a5f9dc665c2ff916a46a43e71d8313`

~~~~text
You are now an excellent programmer. You are conducting a function vulnerability detection task for C/C++ language.

static void curses_destroy_conndata ( void ) {
 conntrack_hook_conn_del ( curr_conn , split_print_po ) ;
 conntrack_hook_conn_del ( curr_conn , join_print_po ) ;
 wdg_conndata = NULL ;
 wdg_c1 = NULL ;
 wdg_c2 = NULL ;
 wdg_join = NULL ;
 curr_conn -> flags &= ~ CONN_VIEWING ;
 curr_conn = NULL ;
 }

In the above code snippet, check for potential security vulnerabilities and answer with a single digit: 1 if Vulnerable, 0 if Non-vulnerable.

The node information of the code snippet is as follows:
Node 25769803873: (BLOCK) '{  conntrack_hook_conn_del ( curr_conn ,...'
Node 30064771630: (CALL) 'conntrack_hook_conn_del ( curr_conn , sp...'
Node 30064771631: (CALL) 'conntrack_hook_conn_del ( curr_conn , jo...'
Node 30064771632: (CALL) 'wdg_conndata = NULL'
Node 30064771633: (CALL) 'wdg_c1 = NULL'
Node 30064771634: (CALL) 'wdg_c2 = NULL'
Node 30064771635: (CALL) 'wdg_join = NULL'
Node 30064771636: (CALL) 'curr_conn -> flags &= ~ CONN_VIEWING'
Node 30064771637: (CALL) 'curr_conn -> flags'
Node 30064771638: (CALL) '~ CONN_VIEWING'
Node 30064771639: (CALL) 'curr_conn = NULL'
Node 55834574942: (FIELD_IDENTIFIER) 'flags'
Node 68719477291: (IDENTIFIER) '<unknown> curr_conn'
Node 68719477292: (IDENTIFIER) '<unknown> split_print_po'
Node 68719477293: (IDENTIFIER) '<unknown> curr_conn'
Node 68719477294: (IDENTIFIER) '<unknown> join_print_po'
Node 68719477295: (IDENTIFIER) '<unknown> wdg_conndata'
Node 68719477296: (IDENTIFIER) '<unknown> NULL'
Node 68719477297: (IDENTIFIER) '<unknown> wdg_c1'
Node 68719477298: (IDENTIFIER) '<unknown> NULL'
Node 68719477299: (IDENTIFIER) '<unknown> wdg_c2'
Node 68719477300: (IDENTIFIER) '<unknown> NULL'
Node 68719477301: (IDENTIFIER) '<unknown> wdg_join'
Node 68719477302: (IDENTIFIER) '<unknown> NULL'
Node 68719477303: (IDENTIFIER) '<unknown> curr_conn'
Node 68719477304: (IDENTIFIER) '<unknown> CONN_VIEWING'
Node 68719477305: (IDENTIFIER) '<unknown> curr_conn'
Node 68719477306: (IDENTIFIER) '<unknown> NULL'
Node 94489280629: (LOCAL) '<unknown> NULL'
Node 94489280630: (LOCAL) '<unknown> curr_conn'
Node 94489280631: (LOCAL) '<unknown> CONN_VIEWING'
Node 94489280632: (LOCAL) '<unknown> wdg_join'
Node 94489280633: (LOCAL) '<unknown> wdg_c2'
Node 94489280634: (LOCAL) '<unknown> wdg_c1'
Node 94489280635: (LOCAL) '<unknown> wdg_conndata'
Node 94489280636: (LOCAL) '<unknown> join_print_po'
Node 94489280637: (LOCAL) '<unknown> split_print_po'
Node 107374182417: (METHOD) 'static void curses_destroy_conndata ( vo...'
Node 111669149719: (METHOD_PARAMETER_IN) 'void'
Node 115964117015: (METHOD_PARAMETER_OUT) 'void'
The edge information of the code snippet is as follows:
Edge: Node 25769803873 -> AST -> Node 30064771630
Edge: Node 25769803873 -> AST -> Node 30064771631
Edge: Node 25769803873 -> AST -> Node 30064771632
Edge: Node 25769803873 -> AST -> Node 30064771633
Edge: Node 25769803873 -> AST -> Node 30064771634
Edge: Node 25769803873 -> AST -> Node 30064771635
Edge: Node 25769803873 -> AST -> Node 30064771636
Edge: Node 25769803873 -> AST -> Node 30064771639
Edge: Node 25769803873 -> AST -> Node 94489280629
Edge: Node 25769803873 -> AST -> Node 94489280630
Edge: Node 25769803873 -> AST -> Node 94489280631
Edge: Node 25769803873 -> AST -> Node 94489280632
Edge: Node 25769803873 -> AST -> Node 94489280633
Edge: Node 25769803873 -> AST -> Node 94489280634
Edge: Node 25769803873 -> AST -> Node 94489280635

The following is an example, and it is .


Answer (0 or 1):
~~~~

## 48. reveal:test:176

Arm: B1; phiên: legacy; seed: 42; dataset/split: reveal/test.
SHA-256 prompt: `c144bdf6c58089c001f4ac02ef6aab22ea2d0fdc7576fbd6fe77c455b24a6fde`

~~~~text
You are now an excellent programmer. You are conducting a function vulnerability detection task for C/C++ language.

static void vmsvga_text_update ( void * opaque , console_ch_t * chardata ) {
 struct vmsvga_state_s * s = opaque ;
 if ( s -> vga . hw_ops -> text_update ) {
 s -> vga . hw_ops -> text_update ( & s -> vga , chardata ) ;
 }
 }

In the above code snippet, check for potential security vulnerabilities and answer with a single digit: 1 if Vulnerable, 0 if Non-vulnerable.

The node information of the code snippet is as follows:
Node 25769803819: (BLOCK) '{  struct vmsvga_state_s * s = opaque ; ...'
Node 25769803820: (BLOCK) '{ s -> vga . hw_ops -> text_update ( & s...'
Node 30064771243: (CALL) 's = opaque'
Node 30064771244: (CALL) 's -> vga . hw_ops -> text_update'
Node 30064771245: (CALL) 's -> vga . hw_ops'
Node 30064771246: (CALL) 's -> vga'
Node 30064771247: (CALL) 's -> vga . hw_ops -> text_update ( & s -...'
Node 30064771248: (CALL) 's -> vga . hw_ops -> text_update'
Node 30064771249: (CALL) 's -> vga . hw_ops'
Node 30064771250: (CALL) 's -> vga'
Node 30064771251: (CALL) '& s -> vga'
Node 30064771252: (CALL) 's -> vga'
Node 47244640293: (CONTROL_STRUCTURE) 'if ( s -> vga . hw_ops -> text_update ) ...'
Node 55834574890: (FIELD_IDENTIFIER) 'vga'
Node 55834574891: (FIELD_IDENTIFIER) 'hw_ops'
Node 55834574892: (FIELD_IDENTIFIER) 'text_update'
Node 55834574893: (FIELD_IDENTIFIER) 'vga'
Node 55834574894: (FIELD_IDENTIFIER) 'hw_ops'
Node 55834574895: (FIELD_IDENTIFIER) 'text_update'
Node 55834574896: (FIELD_IDENTIFIER) 'vga'
Node 68719476899: (IDENTIFIER) 's'
Node 68719476900: (IDENTIFIER) 'opaque'
Node 68719476901: (IDENTIFIER) 's'
Node 68719476902: (IDENTIFIER) 's'
Node 68719476903: (IDENTIFIER) 's'
Node 68719476904: (IDENTIFIER) 'chardata'
Node 94489280540: (LOCAL) 'struct vmsvga_state_s * s'
Node 107374182411: (METHOD) 'static void vmsvga_text_update ( void * ...'
Node 111669149708: (METHOD_PARAMETER_IN) 'void * opaque'
Node 111669149709: (METHOD_PARAMETER_IN) 'console_ch_t * chardata'
Node 115964117004: (METHOD_PARAMETER_OUT) 'void * opaque'
Node 115964117005: (METHOD_PARAMETER_OUT) 'console_ch_t * chardata'
Node 124554051595: (METHOD_RETURN) 'RET'
Node 128849018885: (MODIFIER) '<empty>'
The edge information of the code snippet is as follows:
Edge: Node 25769803819 -> AST -> Node 94489280540
Edge: Node 25769803819 -> AST -> Node 30064771243
Edge: Node 25769803819 -> AST -> Node 47244640293
Edge: Node 25769803820 -> AST -> Node 30064771247
Edge: Node 30064771243 -> ARGUMENT -> Node 68719476899
Edge: Node 30064771243 -> ARGUMENT -> Node 68719476900
Edge: Node 30064771243 -> AST -> Node 68719476899
Edge: Node 30064771243 -> AST -> Node 68719476900
Edge: Node 30064771243 -> CFG -> Node 68719476901
Edge: Node 30064771243 -> DOMINATE -> Node 68719476901
Edge: Node 30064771243 -> POST_DOMINATE -> Node 68719476900
Edge: Node 30064771243 -> REACHING_DEF -> Node 124554051595
Edge: Node 30064771244 -> ARGUMENT -> Node 30064771245
Edge: Node 30064771244 -> ARGUMENT -> Node 55834574892
Edge: Node 30064771244 -> AST -> Node 30064771245
Edge: Node 30064771244 -> AST -> Node 55834574892
Edge: Node 30064771244 -> CDG -> Node 30064771251
Edge: Node 30064771244 -> CDG -> Node 30064771252
Edge: Node 30064771244 -> CDG -> Node 68719476902

The following is an example, and it is .


Answer (0 or 1):
~~~~

## 49. reveal:test:567

Arm: B2-rep; phiên: legacy; seed: 42; dataset/split: reveal/test.
SHA-256 prompt: `46e5c36cbc5efd349d7bf61fa7ee62b665c628f33aecc49ba192e31602eb9cf6`

~~~~text
You are now an excellent programmer. You are conducting a function vulnerability detection task for C/C++ language.

static inline void SetPixelBlackTraits ( Image * image , const PixelTrait traits ) {
 image -> channel_map [ BlackPixelChannel ] . traits = traits ;
 }

In the above code snippet, check for potential security vulnerabilities and answer with a single digit: 1 if Vulnerable, 0 if Non-vulnerable.

The node information of the code snippet is as follows:
Node 25769803807: (BLOCK) '{ image -> channel_map [ BlackPixelChann...'
Node 30064771226: (CALL) 'image -> channel_map [ BlackPixelChannel...'
Node 30064771227: (CALL) 'image -> channel_map [ BlackPixelChannel...'
Node 30064771228: (CALL) 'image -> channel_map [ BlackPixelChannel...'
Node 30064771229: (CALL) 'image -> channel_map'
Node 55834574878: (FIELD_IDENTIFIER) 'channel_map'
Node 55834574879: (FIELD_IDENTIFIER) 'traits'
Node 68719476845: (IDENTIFIER) 'image'
Node 68719476846: (IDENTIFIER) '<unknown> BlackPixelChannel'
Node 68719476847: (IDENTIFIER) 'traits'
Node 94489280545: (LOCAL) '<unknown> BlackPixelChannel'
Node 107374182414: (METHOD) 'static inline void SetPixelBlackTraits (...'
Node 111669149713: (METHOD_PARAMETER_IN) 'Image * image'
Node 111669149714: (METHOD_PARAMETER_IN) 'const PixelTrait traits'
Node 115964117009: (METHOD_PARAMETER_OUT) 'Image * image'
Node 115964117010: (METHOD_PARAMETER_OUT) 'const PixelTrait traits'
Node 124554051598: (METHOD_RETURN) 'RET'
Node 128849018886: (MODIFIER) '<empty>'
The edge information of the code snippet is as follows:
Edge: Node 25769803807 -> AST -> Node 30064771226
Edge: Node 25769803807 -> AST -> Node 94489280545
Edge: Node 30064771226 -> ARGUMENT -> Node 30064771227
Edge: Node 30064771226 -> ARGUMENT -> Node 68719476847
Edge: Node 30064771226 -> AST -> Node 30064771227
Edge: Node 30064771226 -> AST -> Node 68719476847
Edge: Node 30064771226 -> CFG -> Node 124554051598
Edge: Node 30064771226 -> DOMINATE -> Node 124554051598
Edge: Node 30064771226 -> POST_DOMINATE -> Node 68719476847
Edge: Node 30064771226 -> REACHING_DEF -> Node 124554051598
Edge: Node 30064771227 -> ARGUMENT -> Node 30064771228
Edge: Node 30064771227 -> ARGUMENT -> Node 55834574879
Edge: Node 30064771227 -> AST -> Node 30064771228
Edge: Node 30064771227 -> AST -> Node 55834574879
Edge: Node 30064771227 -> CFG -> Node 68719476847
Edge: Node 30064771227 -> DOMINATE -> Node 68719476847
Edge: Node 30064771227 -> POST_DOMINATE -> Node 55834574879
Edge: Node 30064771227 -> REACHING_DEF -> Node 30064771226
Edge: Node 30064771227 -> REACHING_DEF -> Node 124554051598
Edge: Node 30064771228 -> ARGUMENT -> Node 30064771229
Edge: Node 30064771228 -> ARGUMENT -> Node 68719476846
Edge: Node 30064771228 -> AST -> Node 30064771229
Edge: Node 30064771228 -> AST -> Node 68719476846
Edge: Node 30064771228 -> CFG -> Node 55834574879
Edge: Node 30064771228 -> DOMINATE -> Node 55834574879
Edge: Node 30064771228 -> POST_DOMINATE -> Node 68719476846
Edge: Node 30064771229 -> ARGUMENT -> Node 68719476845
Edge: Node 30064771229 -> ARGUMENT -> Node 55834574878
Edge: Node 30064771229 -> AST -> Node 68719476845
Edge: Node 30064771229 -> AST -> Node 55834574878
Edge: Node 30064771229 -> CFG -> Node 68719476846

The following is an example, and it is Non-vulnerable.
static inline void SetPixelGreenTraits ( Image * image , const PixelTrait traits ) {
 image -> channel_map [ GreenPixelChannel ] . traits = traits ;
 }

Answer (0 or 1):
~~~~

## 50. reveal:test:1803

Arm: B2-flip; phiên: legacy; seed: 42; dataset/split: reveal/test.
SHA-256 prompt: `3e31a29b04abd431f74da3d58b164a9d35b42f4f128c5be2d6c0358a7eaea36a`

~~~~text
You are now an excellent programmer. You are conducting a function vulnerability detection task for C/C++ language.

static void dtap_gcc_term_req ( tvbuff_t * tvb , proto_tree * tree , packet_info * pinfo _U_ , guint32 offset , guint len ) {
 guint32 curr_offset ;
 guint32 consumed ;
 guint curr_len ;
 curr_offset = offset ;
 curr_len = len ;
 ELEM_MAND_V ( GSM_A_PDU_TYPE_DTAP , DE_GCC_CALL_REF , NULL ) ;
 }

In the above code snippet, check for potential security vulnerabilities and answer with a single digit: 1 if Vulnerable, 0 if Non-vulnerable.

The node information of the code snippet is as follows:
Node 25769803781: (BLOCK) '{  guint32 curr_offset ;  guint32 consum...'
Node 30064771076: (CALL) 'curr_offset = offset'
Node 30064771077: (CALL) 'curr_len = len'
Node 30064771078: (CALL) 'ELEM_MAND_V ( GSM_A_PDU_TYPE_DTAP , DE_G...'
Node 68719476754: (IDENTIFIER) 'curr_offset'
Node 68719476755: (IDENTIFIER) 'offset'
Node 68719476756: (IDENTIFIER) 'curr_len'
Node 68719476757: (IDENTIFIER) 'len'
Node 68719476758: (IDENTIFIER) '<unknown> GSM_A_PDU_TYPE_DTAP'
Node 68719476759: (IDENTIFIER) '<unknown> DE_GCC_CALL_REF'
Node 68719476760: (IDENTIFIER) '<unknown> NULL'
Node 94489280516: (LOCAL) 'guint32 curr_offset'
Node 94489280517: (LOCAL) 'guint32 consumed'
Node 94489280518: (LOCAL) 'guint curr_len'
Node 94489280519: (LOCAL) '<unknown> NULL'
Node 94489280520: (LOCAL) '<unknown> DE_GCC_CALL_REF'
Node 94489280521: (LOCAL) '<unknown> GSM_A_PDU_TYPE_DTAP'
Node 107374182405: (METHOD) 'static void dtap_gcc_term_req ( tvbuff_t...'
Node 111669149706: (METHOD_PARAMETER_IN) 'tvbuff_t * tvb'
Node 111669149707: (METHOD_PARAMETER_IN) 'proto_tree * tree'
Node 111669149708: (METHOD_PARAMETER_IN) 'packet_info * pinfo'
Node 111669149709: (METHOD_PARAMETER_IN) 'guint32 offset'
Node 111669149710: (METHOD_PARAMETER_IN) 'guint len'
Node 115964117002: (METHOD_PARAMETER_OUT) 'tvbuff_t * tvb'
Node 115964117003: (METHOD_PARAMETER_OUT) 'proto_tree * tree'
Node 115964117004: (METHOD_PARAMETER_OUT) 'packet_info * pinfo'
Node 115964117005: (METHOD_PARAMETER_OUT) 'guint32 offset'
Node 115964117006: (METHOD_PARAMETER_OUT) 'guint len'
Node 124554051589: (METHOD_RETURN) 'RET'
Node 128849018882: (MODIFIER) '<empty>'
The edge information of the code snippet is as follows:
Edge: Node 25769803781 -> AST -> Node 94489280516
Edge: Node 25769803781 -> AST -> Node 94489280517
Edge: Node 25769803781 -> AST -> Node 94489280518
Edge: Node 25769803781 -> AST -> Node 30064771076
Edge: Node 25769803781 -> AST -> Node 30064771077
Edge: Node 25769803781 -> AST -> Node 30064771078
Edge: Node 25769803781 -> AST -> Node 94489280519
Edge: Node 25769803781 -> AST -> Node 94489280520
Edge: Node 25769803781 -> AST -> Node 94489280521
Edge: Node 30064771076 -> ARGUMENT -> Node 68719476754
Edge: Node 30064771076 -> ARGUMENT -> Node 68719476755
Edge: Node 30064771076 -> AST -> Node 68719476754
Edge: Node 30064771076 -> AST -> Node 68719476755
Edge: Node 30064771076 -> CFG -> Node 68719476756
Edge: Node 30064771076 -> DOMINATE -> Node 68719476756
Edge: Node 30064771076 -> POST_DOMINATE -> Node 68719476755
Edge: Node 30064771076 -> REACHING_DEF -> Node 124554051589
Edge: Node 30064771077 -> ARGUMENT -> Node 68719476756
Edge: Node 30064771077 -> ARGUMENT -> Node 68719476757
Edge: Node 30064771077 -> AST -> Node 68719476756
Edge: Node 30064771077 -> AST -> Node 68719476757

The following is an example, and it is Vulnerable.
static void dtap_gcc_term ( tvbuff_t * tvb , proto_tree * tree , packet_info * pinfo _U_ , guint32 offset , guint len ) {
 guint32 curr_offset ;
 guint32 consumed ;
 guint curr_len ;
 curr_offset = offset ;
 curr_len = len ;
 ELEM_MAND_LV ( GSM_A_PDU_TYPE_DTAP , DE_GCC_CAUSE , NULL ) ;
 }

Answer (0 or 1):
~~~~

## 51. reveal:validation:2053

Arm: B2-rand; phiên: frozen; seed: 43; dataset/split: reveal/validation.
SHA-256 prompt: `4d6623bdd951ec6a0f0df8c7745d856343f2baf5186e12ed92c59190f9469ca7`

~~~~text
You are now an excellent programmer. You are conducting a function vulnerability detection task for C/C++ language.

TEST_F ( OmniboxViewViewsTest , Emphasis ) {
 constexpr struct {
 const char * input ;
 bool expected_base_text_emphasized ;
 Range expected_emphasis_range ;
 Range expected_scheme_range ;
 }
 test_cases [ ] = {
 {
 "data:text/html,Hello%20World" , false , Range ( 0 , 4 ) , Range ( 0 , 4 ) }
 , {
 "http://www.example.com/path/file.htm" , false , Range ( 7 , 22 ) , Range ( 0 , 4 ) }
 , {
 "https://www.example.com/path/file.htm" , false , Range ( 8 , 23 ) , Range ( 0 , 5 ) }
 , {
 "chrome-extension://ldfbacdbackkjhclmhnjabngnppnkagl" , false , Range : : InvalidRange ( ) , Range ( 0 , 16 ) }
 , {
 "nosuchscheme://opaque/string" , true , Range : : InvalidRange ( ) , Range ( 0 , 12 ) }
 , {
 "nosuchscheme:opaquestring" , true , Range : : InvalidRange ( ) , Range ( 0 , 12 ) }
 , {
 "host.com/path/file" , false , Range ( 0 , 8 ) , Range : : InvalidRange ( ) }
 , {
 "This is plain text" , true , Range : : InvalidRange ( ) , Range : : InvalidRange ( ) }
 , }
 ;
 for ( const auto & test_case : test_cases ) {
 SCOPED_TRACE ( test_case . input ) ;
 SetAndEmphasizeText ( test_case . input , false ) ;
 EXPECT_EQ ( TestingOmniboxView : : to_base_text_emphasis ( test_case . expected_base_text_emphasized ) , omnibox_view ( ) -> base_text_emphasis ( ) ) ;
 EXPECT_EQ ( test_case . expected_emphasis_range , omnibox_view ( ) -> emphasis_range ( ) ) ;
 EXPECT_FALSE ( omnibox_view ( ) -> scheme_range ( ) . IsValid ( ) ) ;
 if ( test_case . expected_scheme_range . IsValid ( ) ) {
 SetAndEmphasizeText ( test_case . input , true ) ;
 EXPECT_EQ ( TestingOmniboxView : : to_base_text_emphasis ( test_case . expected_base_text_emphasized ) , omnibox_view ( ) -> base_text_emphasis ( ) ) ;
 EXPECT_EQ ( test_case . expected_emphasis_range , omnibox_view ( ) -> emphasis_range ( ) ) ;
 EXPECT_EQ ( test_case . expected_scheme_range , omnibox_view ( ) -> scheme_range ( ) ) ;
 }
 }
 }

In the above code snippet, check for potential security vulnerabilities and answer with a single digit: 1 if Vulnerable, 0 if Non-vulnerable.

The node information of the code snippet is as follows:
Node 25769803792: (BLOCK) '{  constexpr struct {  const char * inpu...'
Node 68719476774: (IDENTIFIER) '<unknown> constexpr'
Node 94489280535: (LOCAL) '<unknown> constexpr'
Node 107374182406: (METHOD) 'TEST_F ( OmniboxViewViewsTest , Emphasis...'
Node 111669149703: (METHOD_PARAMETER_IN) 'OmniboxViewViewsTest'
Node 111669149704: (METHOD_PARAMETER_IN) 'Emphasis'
Node 115964116999: (METHOD_PARAMETER_OUT) 'OmniboxViewViewsTest'
Node 115964117000: (METHOD_PARAMETER_OUT) 'Emphasis'
Node 124554051590: (METHOD_RETURN) 'RET'
The edge information of the code snippet is as follows:
Edge: Node 25769803792 -> AST -> Node 68719476774
Edge: Node 25769803792 -> AST -> Node 94489280535
Edge: Node 68719476774 -> CFG -> Node 124554051590
Edge: Node 68719476774 -> DOMINATE -> Node 124554051590
Edge: Node 68719476774 -> POST_DOMINATE -> Node 107374182406
Edge: Node 68719476774 -> REF -> Node 94489280535
Edge: Node 107374182406 -> AST -> Node 111669149703
Edge: Node 107374182406 -> AST -> Node 111669149704
Edge: Node 107374182406 -> AST -> Node 25769803792
Edge: Node 107374182406 -> AST -> Node 124554051590
Edge: Node 107374182406 -> AST -> Node 115964116999
Edge: Node 107374182406 -> AST -> Node 115964117000
Edge: Node 107374182406 -> CFG -> Node 68719476774
Edge: Node 107374182406 -> CONTAINS -> Node 25769803792
Edge: Node 107374182406 -> CONTAINS -> Node 68719476774
Edge: Node 107374182406 -> DOMINATE -> Node 68719476774
Edge: Node 107374182406 -> REACHING_DEF -> Node 68719476774
Edge: Node 107374182406 -> REACHING_DEF -> Node 111669149703
Edge: Node 107374182406 -> REACHING_DEF -> Node 111669149704
Edge: Node 111669149703 -> PARAMETER_LINK -> Node 115964116999
Edge: Node 111669149703 -> REACHING_DEF -> Node 115964116999
Edge: Node 111669149703 -> REACHING_DEF -> Node 115964116999
Edge: Node 111669149703 -> REACHING_DEF -> Node 124554051590
Edge: Node 111669149704 -> PARAMETER_LINK -> Node 115964117000
Edge: Node 111669149704 -> REACHING_DEF -> Node 115964117000
Edge: Node 111669149704 -> REACHING_DEF -> Node 115964117000
Edge: Node 111669149704 -> REACHING_DEF -> Node 124554051590
Edge: Node 124554051590 -> POST_DOMINATE -> Node 68719476774

The following is an example, and it is Non-vulnerable.
static void initial_reordering ( const hb_ot_shape_plan_t * plan , hb_font_t * font , hb_buffer_t * buffer ) {
 insert_dotted_circles ( plan , font , buffer ) ;
 foreach_syllable ( buffer , start , end ) initial_reordering_syllable ( plan , font -> face , buffer , start , end ) ;
 }

Answer (0 or 1):
~~~~

## 52. reveal:test:987

Arm: B2-flip; phiên: frozen; seed: 42; dataset/split: reveal/test.
SHA-256 prompt: `76f2ad26b1d36d6875ddfddfa9e1ed384c46ce793c87d12f958e693737f207da`

~~~~text
You are now an excellent programmer. You are conducting a function vulnerability detection task for C/C++ language.

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
Node 25769803824: (BLOCK) '<empty>'
Node 107374182420: (METHOD) 'static ossl_inline STACK_OF ( t1 )'
Node 111669149724: (METHOD_PARAMETER_IN) 't1'
Node 115964117020: (METHOD_PARAMETER_OUT) 't1'
Node 124554051604: (METHOD_RETURN) 'RET'
Node 128849018887: (MODIFIER) '<empty>'
The edge information of the code snippet is as follows:
Edge: Node 107374182420 -> AST -> Node 111669149724
Edge: Node 107374182420 -> AST -> Node 25769803824
Edge: Node 107374182420 -> AST -> Node 128849018887
Edge: Node 107374182420 -> AST -> Node 124554051604
Edge: Node 107374182420 -> AST -> Node 115964117020
Edge: Node 107374182420 -> CFG -> Node 124554051604
Edge: Node 107374182420 -> CONTAINS -> Node 25769803824
Edge: Node 107374182420 -> DOMINATE -> Node 124554051604
Edge: Node 107374182420 -> REACHING_DEF -> Node 111669149724
Edge: Node 111669149724 -> PARAMETER_LINK -> Node 115964117020
Edge: Node 111669149724 -> REACHING_DEF -> Node 115964117020
Edge: Node 111669149724 -> REACHING_DEF -> Node 124554051604
Edge: Node 124554051604 -> POST_DOMINATE -> Node 107374182420

The following is an example, and it is Vulnerable.
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
 sadMxN ( 64 , 64 )

Answer (0 or 1):
~~~~

## 53. reveal:validation:286

Arm: B2-rand; phiên: frozen; seed: 43; dataset/split: reveal/validation.
SHA-256 prompt: `8c022dba8e4a88c1397fa081caac86d4de2fa5e4bb799ddb13e1f7de26185648`

~~~~text
You are now an excellent programmer. You are conducting a function vulnerability detection task for C/C++ language.

IN_PROC_BROWSER_TEST_F ( ExtensionMessageBubbleViewBrowserTest , TestDevModeBubbleIsntShownTwice ) {
 TestDevModeBubbleIsntShownTwice ( ) ;
 }

In the above code snippet, check for potential security vulnerabilities and answer with a single digit: 1 if Vulnerable, 0 if Non-vulnerable.

The node information of the code snippet is as follows:
Node 25769803816: (BLOCK) '{ TestDevModeBubbleIsntShownTwice ( ) ; ...'
Node 30064771292: (CALL) 'TestDevModeBubbleIsntShownTwice ( )'
Node 107374182411: (METHOD) 'IN_PROC_BROWSER_TEST_F ( ExtensionMessag...'
Node 111669149709: (METHOD_PARAMETER_IN) 'ExtensionMessageBubbleViewBrowserTest'
Node 111669149710: (METHOD_PARAMETER_IN) 'TestDevModeBubbleIsntShownTwice'
Node 115964117005: (METHOD_PARAMETER_OUT) 'ExtensionMessageBubbleViewBrowserTest'
Node 115964117006: (METHOD_PARAMETER_OUT) 'TestDevModeBubbleIsntShownTwice'
Node 124554051595: (METHOD_RETURN) 'RET'
The edge information of the code snippet is as follows:
Edge: Node 25769803816 -> AST -> Node 30064771292
Edge: Node 30064771292 -> CFG -> Node 124554051595
Edge: Node 30064771292 -> DOMINATE -> Node 124554051595
Edge: Node 30064771292 -> POST_DOMINATE -> Node 107374182411
Edge: Node 30064771292 -> REACHING_DEF -> Node 124554051595
Edge: Node 107374182411 -> AST -> Node 111669149709
Edge: Node 107374182411 -> AST -> Node 111669149710
Edge: Node 107374182411 -> AST -> Node 25769803816
Edge: Node 107374182411 -> AST -> Node 124554051595
Edge: Node 107374182411 -> AST -> Node 115964117005
Edge: Node 107374182411 -> AST -> Node 115964117006
Edge: Node 107374182411 -> CFG -> Node 30064771292
Edge: Node 107374182411 -> CONTAINS -> Node 25769803816
Edge: Node 107374182411 -> CONTAINS -> Node 30064771292
Edge: Node 107374182411 -> DOMINATE -> Node 30064771292
Edge: Node 107374182411 -> REACHING_DEF -> Node 111669149709
Edge: Node 107374182411 -> REACHING_DEF -> Node 111669149710
Edge: Node 107374182411 -> REACHING_DEF -> Node 30064771292
Edge: Node 111669149709 -> PARAMETER_LINK -> Node 115964117005
Edge: Node 111669149709 -> REACHING_DEF -> Node 115964117005
Edge: Node 111669149709 -> REACHING_DEF -> Node 115964117005
Edge: Node 111669149709 -> REACHING_DEF -> Node 124554051595
Edge: Node 111669149710 -> PARAMETER_LINK -> Node 115964117006
Edge: Node 111669149710 -> REACHING_DEF -> Node 115964117006
Edge: Node 111669149710 -> REACHING_DEF -> Node 115964117006
Edge: Node 111669149710 -> REACHING_DEF -> Node 124554051595
Edge: Node 124554051595 -> POST_DOMINATE -> Node 30064771292

The following is an example, and it is Non-vulnerable.
void PNGAPI png_set_sRGB_gAMA_and_cHRM ( png_structp png_ptr , png_infop info_ptr , int intent ) {
 # ifdef PNG_gAMA_SUPPORTED # ifdef PNG_FLOATING_POINT_SUPPORTED float file_gamma ;
 # endif # ifdef PNG_FIXED_POINT_SUPPORTED png_fixed_point int_file_gamma ;
 # endif # endif # ifdef PNG_cHRM_SUPPORTED # ifdef PNG_FLOATING_POINT_SUPPORTED float white_x , white_y , red_x , red_y , green_x , green_y , blue_x , blue_y ;
 # endif # ifdef PNG_FIXED_POINT_SUPPORTED png_fixed_point int_white_x , int_white_y , int_red_x , int_red_y , int_green_x , int_green_y , int_blue_x , int_blue_y ;
 # endif # endif png_debug1 ( 1 , "in %s storage function" , "sRGB_gAMA_and_cHRM" ) ;
 if ( png_ptr == NULL || info_ptr == NULL ) return ;
 png_set_sRGB ( png_ptr , info_ptr , intent ) ;
 # ifdef PNG_gAMA_SUPPORTED # ifdef PNG_FLOATING_POINT_SUPPORTED file_gamma = ( float ) .45455 ;
 png_set_gAMA ( png_ptr , info_ptr , file_gamma ) ;
 # endif # ifdef PNG_FIXED_POINT_SUPPORTED int_file_gamma = 45455L ;
 png_set_gAMA_fixed ( png_ptr , info_ptr , int_file_gamma ) ;
 # endif # endif # ifdef PNG_cHRM_SUPPORTED # ifdef PNG_FIXED_POINT_SUPPORTED int_white_x = 31270L ;
 int_white_y = 32900L ;
 int_red_x = 64000L ;
 int_red_y = 33000L ;
 int_green_x = 30000L ;
 int_green_y = 60000L ;
 int_blue_x = 15000L ;
 int_blue_y = 6000L ;
 png_set_cHRM_fixed ( png_ptr , info_ptr , int_white_x , int_white_y , int_red_x , int_red_y , int_green_x , int_green_y , int_blue_x , int_blue_y ) ;
 # endif # ifdef PNG_FLOATING_POINT_SUPPORTED white_x = ( float ) .3127 ;
 white_y = ( float ) .3290 ;
 red_x = ( float ) .64 ;
 red_y = ( float ) .33 ;
 green_x = ( float ) .30 ;
 green_y = ( float ) .60 ;
 blue_x = ( float ) .15 ;
 blue_y = ( float ) .06 ;
 png_set_cHRM ( png_ptr , info_ptr , white_x , white_y , red_x , red_y , green_x , green_y , blue_x , blue_y ) ;
 # endif # endif }

Answer (0 or 1):
~~~~

## 54. reveal:validation:547

Arm: B2-rand; phiên: frozen; seed: 42; dataset/split: reveal/validation.
SHA-256 prompt: `0f8301b6e379deb40beced30ccc469ac147661e045b372b5a61f8575aedaac05`

~~~~text
You are now an excellent programmer. You are conducting a function vulnerability detection task for C/C++ language.

TEST_F ( TemplateURLTest , ExtractSearchTermsFromURLPath ) {
 TemplateURLData data ;
 data . SetURL ( "http://term-in-path.com/begin/{
searchTerms}
/end" ) ;
 TemplateURL url ( data ) ;
 base : : string16 result ;
 EXPECT_TRUE ( url . ExtractSearchTermsFromURL ( GURL ( "http://term-in-path.com/begin/something/end" ) , search_terms_data_ , & result ) ) ;
 EXPECT_EQ ( ASCIIToUTF16 ( "something" ) , result ) ;
 EXPECT_TRUE ( url . ExtractSearchTermsFromURL ( GURL ( "http://term-in-path.com/begin/a%20b%20c/end" ) , search_terms_data_ , & result ) ) ;
 EXPECT_EQ ( ASCIIToUTF16 ( "a b c" ) , result ) ;
 EXPECT_TRUE ( url . ExtractSearchTermsFromURL ( GURL ( "http://term-in-path.com/begin/1+2+3/end" ) , search_terms_data_ , & result ) ) ;
 EXPECT_EQ ( ASCIIToUTF16 ( "1+2+3" ) , result ) ;
 EXPECT_FALSE ( url . ExtractSearchTermsFromURL ( GURL ( "http://term-in-path.com/about" ) , search_terms_data_ , & result ) ) ;
 EXPECT_EQ ( base : : string16 ( ) , result ) ;
 EXPECT_FALSE ( url . ExtractSearchTermsFromURL ( GURL ( "http://term-in-path.com/begin" ) , search_terms_data_ , & result ) ) ;
 EXPECT_EQ ( base : : string16 ( ) , result ) ;
 EXPECT_FALSE ( url . ExtractSearchTermsFromURL ( GURL ( "http://term-in-path.com/end" ) , search_terms_data_ , & result ) ) ;
 EXPECT_EQ ( base : : string16 ( ) , result ) ;
 }

In the above code snippet, check for potential security vulnerabilities and answer with a single digit: 1 if Vulnerable, 0 if Non-vulnerable.

The node information of the code snippet is as follows:
Node 25769803806: (BLOCK) '{  TemplateURLData data ;  data . SetURL...'
Node 94489280538: (LOCAL) 'TemplateURLData data'
Node 107374182414: (METHOD) 'TEST_F ( TemplateURLTest , ExtractSearch...'
Node 111669149717: (METHOD_PARAMETER_IN) 'TemplateURLTest'
Node 111669149718: (METHOD_PARAMETER_IN) 'ExtractSearchTermsFromURLPath'
Node 115964117013: (METHOD_PARAMETER_OUT) 'TemplateURLTest'
Node 115964117014: (METHOD_PARAMETER_OUT) 'ExtractSearchTermsFromURLPath'
Node 124554051598: (METHOD_RETURN) 'RET'
The edge information of the code snippet is as follows:
Edge: Node 25769803806 -> AST -> Node 94489280538
Edge: Node 107374182414 -> AST -> Node 111669149717
Edge: Node 107374182414 -> AST -> Node 111669149718
Edge: Node 107374182414 -> AST -> Node 25769803806
Edge: Node 107374182414 -> AST -> Node 124554051598
Edge: Node 107374182414 -> AST -> Node 115964117013
Edge: Node 107374182414 -> AST -> Node 115964117014
Edge: Node 107374182414 -> CFG -> Node 124554051598
Edge: Node 107374182414 -> CONTAINS -> Node 25769803806
Edge: Node 107374182414 -> DOMINATE -> Node 124554051598
Edge: Node 107374182414 -> REACHING_DEF -> Node 111669149718
Edge: Node 107374182414 -> REACHING_DEF -> Node 111669149717
Edge: Node 111669149717 -> PARAMETER_LINK -> Node 115964117013
Edge: Node 111669149717 -> REACHING_DEF -> Node 115964117013
Edge: Node 111669149717 -> REACHING_DEF -> Node 124554051598
Edge: Node 111669149718 -> PARAMETER_LINK -> Node 115964117014
Edge: Node 111669149718 -> REACHING_DEF -> Node 115964117014
Edge: Node 111669149718 -> REACHING_DEF -> Node 124554051598
Edge: Node 124554051598 -> POST_DOMINATE -> Node 107374182414

The following is an example, and it is Non-vulnerable.
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

Answer (0 or 1):
~~~~

## 55. reveal:validation:1933

Arm: B2; phiên: legacy; seed: 42; dataset/split: reveal/validation.
SHA-256 prompt: `29cf40e46da4495fc3b2bf659ba2e24afb4acf7b14937d4422ed844e1b6cacef`

~~~~text
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
~~~~

## 56. reveal:test:447

Arm: B2; phiên: legacy; seed: 42; dataset/split: reveal/test.
SHA-256 prompt: `250ca188fbfa700e18e01ea804445a5ce8343de3246260268365f9a348f55b53`

~~~~text
You are now an excellent programmer. You are conducting a function vulnerability detection task for C/C++ language.

static const char * flat_escape_value_str ( AVBPrint * dst , const char * src ) {
 const char * p ;
 for ( p = src ;
 * p ;
 p ++ ) {
 switch ( * p ) {
 case '\n' : av_bprintf ( dst , "%s" , "\\n" ) ;
 break ;
 case '\r' : av_bprintf ( dst , "%s" , "\\r" ) ;
 break ;
 case '\\' : av_bprintf ( dst , "%s" , "\\\\" ) ;
 break ;
 case '"' : av_bprintf ( dst , "%s" , "\\\"" ) ;
 break ;
 case '`' : av_bprintf ( dst , "%s" , "\\`" ) ;
 break ;
 case '$' : av_bprintf ( dst , "%s" , "\\$" ) ;
 break ;
 default : av_bprint_chars ( dst , * p , 1 ) ;
 break ;
 }
 }
 return dst -> str ;
 }

In the above code snippet, check for potential security vulnerabilities and answer with a single digit: 1 if Vulnerable, 0 if Non-vulnerable.

The node information of the code snippet is as follows:
Node 25769803871: (BLOCK) '{  const char * p ;  for ( p = src ;  * ...'
Node 25769803872: (BLOCK) '{  switch ( * p ) {  case '\n' : av_bpri...'
Node 25769803873: (BLOCK) '{  case '\n' : av_bprintf ( dst , "%s" ,...'
Node 30064771987: (CALL) 'p = src'
Node 30064771988: (CALL) '* p'
Node 30064771989: (CALL) 'p ++'
Node 30064771990: (CALL) '* p'
Node 30064771991: (CALL) 'av_bprintf ( dst , "%s" , "\\n" )'
Node 30064771992: (CALL) 'av_bprintf ( dst , "%s" , "\\r" )'
Node 30064771993: (CALL) 'av_bprintf ( dst , "%s" , "\\\\" )'
Node 30064771994: (CALL) 'av_bprintf ( dst , "%s" , "\\\"" )'
Node 30064771995: (CALL) 'av_bprintf ( dst , "%s" , "\\`" )'
Node 30064771996: (CALL) 'av_bprintf ( dst , "%s" , "\\$" )'
Node 30064771997: (CALL) 'av_bprint_chars ( dst , * p , 1 )'
Node 30064771998: (CALL) '* p'
Node 30064771999: (CALL) 'dst -> str'
Node 47244640351: (CONTROL_STRUCTURE) 'for (p = src ;* p;p ++)'
Node 47244640352: (CONTROL_STRUCTURE) 'switch ( * p ) {  case '\n' : av_bprintf...'
Node 47244640353: (CONTROL_STRUCTURE) 'break ;'
Node 47244640354: (CONTROL_STRUCTURE) 'break ;'
Node 47244640355: (CONTROL_STRUCTURE) 'break ;'
Node 47244640356: (CONTROL_STRUCTURE) 'break ;'
Node 47244640357: (CONTROL_STRUCTURE) 'break ;'
Node 47244640358: (CONTROL_STRUCTURE) 'break ;'
Node 47244640359: (CONTROL_STRUCTURE) 'break ;'
Node 55834575014: (FIELD_IDENTIFIER) 'str'
Node 68719477585: (IDENTIFIER) 'p'
Node 68719477586: (IDENTIFIER) 'src'
Node 68719477587: (IDENTIFIER) 'p'
Node 68719477588: (IDENTIFIER) 'p'
Node 68719477589: (IDENTIFIER) 'p'
Node 68719477590: (IDENTIFIER) 'dst'
Node 68719477591: (IDENTIFIER) 'dst'
Node 68719477592: (IDENTIFIER) 'dst'
Node 68719477593: (IDENTIFIER) 'dst'
Node 68719477594: (IDENTIFIER) 'dst'
Node 68719477595: (IDENTIFIER) 'dst'
Node 68719477596: (IDENTIFIER) 'dst'
Node 68719477597: (IDENTIFIER) 'p'
Node 68719477598: (IDENTIFIER) 'dst'
The edge information of the code snippet is as follows:
Edge: Node 25769803871 -> AST -> Node 47244640351
Edge: Node 25769803872 -> AST -> Node 47244640352
Edge: Node 25769803873 -> AST -> Node 30064771991
Edge: Node 25769803873 -> AST -> Node 47244640353
Edge: Node 25769803873 -> AST -> Node 30064771992
Edge: Node 25769803873 -> AST -> Node 47244640354
Edge: Node 25769803873 -> AST -> Node 30064771993
Edge: Node 25769803873 -> AST -> Node 47244640355
Edge: Node 25769803873 -> AST -> Node 30064771994
Edge: Node 25769803873 -> AST -> Node 47244640356
Edge: Node 25769803873 -> AST -> Node 30064771995
Edge: Node 25769803873 -> AST -> Node 47244640357
Edge: Node 25769803873 -> AST -> Node 30064771996
Edge: Node 25769803873 -> AST -> Node 47244640358
Edge: Node 25769803873 -> AST -> Node 30064771997

The following is an example, and it is Non-vulnerable.
static const char * c_escape_str ( AVBPrint * dst , const char * src , const char sep , void * log_ctx ) {
 const char * p ;
 for ( p = src ;
 * p ;
 p ++ ) {
 switch ( * p ) {
 case '\b' : av_bprintf ( dst , "%s" , "\\b" ) ;
 break ;
 case '\f' : av_bprintf ( dst , "%s" , "\\f" ) ;
 break ;
 case '\n' : av_bprintf ( dst , "%s" , "\\n" ) ;
 break ;
 case '\r' : av_bprintf ( dst , "%s" , "\\r" ) ;
 break ;
 case '\\' : av_bprintf ( dst , "%s" , "\\\\" ) ;
 break ;
 default : if ( * p == sep ) av_bprint_chars ( dst , '\\' , 1 ) ;
 av_bprint_chars ( dst , * p , 1 ) ;
 }
 }
 return dst -> str ;
 }

Answer (0 or 1):
~~~~

## 57. reveal:validation:1081

Arm: B2; phiên: frozen; seed: 42; dataset/split: reveal/validation.
SHA-256 prompt: `8f8d25eedaf8d3656342e7feecad66a4d7a56ce78d2daf28e3712a416d0b702a`

~~~~text
You are now an excellent programmer. You are conducting a function vulnerability detection task for C/C++ language.

static int dissect_h245_MaxRedundancy ( tvbuff_t * tvb _U_ , int offset _U_ , asn1_ctx_t * actx _U_ , proto_tree * tree _U_ , int hf_index _U_ ) {
 offset = dissect_per_constrained_integer ( tvb , offset , actx , tree , hf_index , 1U , NO_BOUND , NULL , FALSE ) ;
 return offset ;
 }

In the above code snippet, check for potential security vulnerabilities and answer with a single digit: 1 if Vulnerable, 0 if Non-vulnerable.

The node information of the code snippet is as follows:
Node 25769803785: (BLOCK) '{  offset = dissect_per_constrained_inte...'
Node 30064771112: (CALL) 'offset = dissect_per_constrained_integer...'
Node 30064771113: (CALL) 'dissect_per_constrained_integer ( tvb , ...'
Node 68719476777: (IDENTIFIER) 'offset'
Node 68719476778: (IDENTIFIER) 'tvb'
Node 68719476779: (IDENTIFIER) 'offset'
Node 68719476780: (IDENTIFIER) 'actx'
Node 68719476781: (IDENTIFIER) 'tree'
Node 68719476782: (IDENTIFIER) 'hf_index'
Node 68719476783: (IDENTIFIER) '<unknown> NO_BOUND'
Node 68719476784: (IDENTIFIER) '<unknown> NULL'
Node 68719476785: (IDENTIFIER) '<unknown> FALSE'
Node 68719476786: (IDENTIFIER) 'offset'
Node 90194313232: (LITERAL) '1U'
Node 94489280522: (LOCAL) '<unknown> FALSE'
Node 94489280523: (LOCAL) '<unknown> NULL'
Node 94489280524: (LOCAL) '<unknown> NO_BOUND'
Node 107374182408: (METHOD) 'static int dissect_h245_MaxRedundancy ( ...'
Node 111669149705: (METHOD_PARAMETER_IN) 'tvbuff_t * tvb'
Node 111669149706: (METHOD_PARAMETER_IN) 'int offset'
Node 111669149707: (METHOD_PARAMETER_IN) 'asn1_ctx_t * actx'
Node 111669149708: (METHOD_PARAMETER_IN) 'proto_tree * tree'
Node 111669149709: (METHOD_PARAMETER_IN) 'int hf_index'
Node 115964117001: (METHOD_PARAMETER_OUT) 'tvbuff_t * tvb'
Node 115964117002: (METHOD_PARAMETER_OUT) 'int offset'
Node 115964117003: (METHOD_PARAMETER_OUT) 'asn1_ctx_t * actx'
Node 115964117004: (METHOD_PARAMETER_OUT) 'proto_tree * tree'
Node 115964117005: (METHOD_PARAMETER_OUT) 'int hf_index'
Node 124554051592: (METHOD_RETURN) 'RET'
Node 128849018882: (MODIFIER) '<empty>'
Node 141733920769: (RETURN) 'return offset ;'
The edge information of the code snippet is as follows:
Edge: Node 25769803785 -> AST -> Node 30064771112
Edge: Node 25769803785 -> AST -> Node 141733920769
Edge: Node 25769803785 -> AST -> Node 94489280522
Edge: Node 25769803785 -> AST -> Node 94489280523
Edge: Node 25769803785 -> AST -> Node 94489280524
Edge: Node 30064771112 -> ARGUMENT -> Node 68719476777
Edge: Node 30064771112 -> ARGUMENT -> Node 30064771113
Edge: Node 30064771112 -> AST -> Node 68719476777
Edge: Node 30064771112 -> AST -> Node 30064771113
Edge: Node 30064771112 -> CFG -> Node 68719476786
Edge: Node 30064771112 -> DOMINATE -> Node 68719476786
Edge: Node 30064771112 -> POST_DOMINATE -> Node 30064771113
Edge: Node 30064771112 -> REACHING_DEF -> Node 124554051592
Edge: Node 30064771113 -> ARGUMENT -> Node 68719476778
Edge: Node 30064771113 -> ARGUMENT -> Node 68719476779
Edge: Node 30064771113 -> ARGUMENT -> Node 68719476780
Edge: Node 30064771113 -> ARGUMENT -> Node 68719476781
Edge: Node 30064771113 -> ARGUMENT -> Node 68719476782
Edge: Node 30064771113 -> ARGUMENT -> Node 90194313232
Edge: Node 30064771113 -> ARGUMENT -> Node 68719476783
Edge: Node 30064771113 -> ARGUMENT -> Node 68719476784
Edge: Node 30064771113 -> ARGUMENT -> Node 68719476785

The following is an example, and it is Non-vulnerable.
static int dissect_h245_McuNumber ( tvbuff_t * tvb _U_ , int offset _U_ , asn1_ctx_t * actx _U_ , proto_tree * tree _U_ , int hf_index _U_ ) {
 offset = dissect_per_constrained_integer ( tvb , offset , actx , tree , hf_index , 0U , 192U , NULL , FALSE ) ;
 return offset ;
 }

Answer (0 or 1):
~~~~

## 58. reveal:validation:730

Arm: B2-rand; phiên: frozen; seed: 44; dataset/split: reveal/validation.
SHA-256 prompt: `d4d38a59bf179ec838791f974b3cf39363266b635e706c355ab0486d7549dcb2`

~~~~text
You are now an excellent programmer. You are conducting a function vulnerability detection task for C/C++ language.

static int dissect_nlm3_shareres ( tvbuff_t * tvb , packet_info * pinfo , proto_tree * tree , void * data _U_ ) {
 return dissect_nlm_shareres ( tvb , 0 , pinfo , tree , 3 ) ;
 }

In the above code snippet, check for potential security vulnerabilities and answer with a single digit: 1 if Vulnerable, 0 if Non-vulnerable.

The node information of the code snippet is as follows:
Node 25769803779: (BLOCK) '{ return dissect_nlm_shareres ( tvb , 0 ...'
Node 30064771073: (CALL) 'dissect_nlm_shareres ( tvb , 0 , pinfo ,...'
Node 68719476738: (IDENTIFIER) 'tvb'
Node 68719476739: (IDENTIFIER) 'pinfo'
Node 68719476740: (IDENTIFIER) 'tree'
Node 90194313216: (LITERAL) '0'
Node 90194313217: (LITERAL) '3'
Node 107374182403: (METHOD) 'static int dissect_nlm3_shareres ( tvbuf...'
Node 111669149697: (METHOD_PARAMETER_IN) 'tvbuff_t * tvb'
Node 111669149698: (METHOD_PARAMETER_IN) 'packet_info * pinfo'
Node 111669149699: (METHOD_PARAMETER_IN) 'proto_tree * tree'
Node 111669149700: (METHOD_PARAMETER_IN) 'void * data'
Node 115964116993: (METHOD_PARAMETER_OUT) 'tvbuff_t * tvb'
Node 115964116994: (METHOD_PARAMETER_OUT) 'packet_info * pinfo'
Node 115964116995: (METHOD_PARAMETER_OUT) 'proto_tree * tree'
Node 115964116996: (METHOD_PARAMETER_OUT) 'void * data'
Node 124554051587: (METHOD_RETURN) 'RET'
Node 128849018881: (MODIFIER) '<empty>'
Node 141733920768: (RETURN) 'return dissect_nlm_shareres ( tvb , 0 , ...'
The edge information of the code snippet is as follows:
Edge: Node 25769803779 -> AST -> Node 141733920768
Edge: Node 30064771073 -> ARGUMENT -> Node 68719476738
Edge: Node 30064771073 -> ARGUMENT -> Node 90194313216
Edge: Node 30064771073 -> ARGUMENT -> Node 68719476739
Edge: Node 30064771073 -> ARGUMENT -> Node 68719476740
Edge: Node 30064771073 -> ARGUMENT -> Node 90194313217
Edge: Node 30064771073 -> AST -> Node 68719476738
Edge: Node 30064771073 -> AST -> Node 90194313216
Edge: Node 30064771073 -> AST -> Node 68719476739
Edge: Node 30064771073 -> AST -> Node 68719476740
Edge: Node 30064771073 -> AST -> Node 90194313217
Edge: Node 30064771073 -> CFG -> Node 141733920768
Edge: Node 30064771073 -> DOMINATE -> Node 141733920768
Edge: Node 30064771073 -> POST_DOMINATE -> Node 90194313217
Edge: Node 30064771073 -> REACHING_DEF -> Node 141733920768
Edge: Node 30064771073 -> REACHING_DEF -> Node 124554051587
Edge: Node 68719476738 -> CFG -> Node 90194313216
Edge: Node 68719476738 -> DOMINATE -> Node 90194313216
Edge: Node 68719476738 -> POST_DOMINATE -> Node 107374182403
Edge: Node 68719476738 -> REACHING_DEF -> Node 115964116993
Edge: Node 68719476738 -> REACHING_DEF -> Node 68719476739
Edge: Node 68719476738 -> REACHING_DEF -> Node 68719476740
Edge: Node 68719476738 -> REACHING_DEF -> Node 30064771073
Edge: Node 68719476738 -> REACHING_DEF -> Node 124554051587
Edge: Node 68719476738 -> REF -> Node 111669149697
Edge: Node 68719476739 -> CFG -> Node 68719476740
Edge: Node 68719476739 -> DOMINATE -> Node 68719476740
Edge: Node 68719476739 -> POST_DOMINATE -> Node 90194313216
Edge: Node 68719476739 -> REACHING_DEF -> Node 68719476738

The following is an example, and it is Non-vulnerable.
void jas_image_delcmpt ( jas_image_t * image , int cmptno ) {
 if ( cmptno >= image -> numcmpts_ ) {
 return ;
 }
 jas_image_cmpt_destroy ( image -> cmpts_ [ cmptno ] ) ;
 if ( cmptno < image -> numcmpts_ ) {
 memmove ( & image -> cmpts_ [ cmptno ] , & image -> cmpts_ [ cmptno + 1 ] , ( image -> numcmpts_ - 1 - cmptno ) * sizeof ( jas_image_cmpt_t * ) ) ;
 }
 -- image -> numcmpts_ ;
 jas_image_setbbox ( image ) ;
 }

Answer (0 or 1):
~~~~

## 59. reveal:validation:466

Arm: B2-rand; phiên: frozen; seed: 44; dataset/split: reveal/validation.
SHA-256 prompt: `3cbab39ecf25c0aa91a89918c96776439e11a072cc71412f98db406fcfba72a0`

~~~~text
You are now an excellent programmer. You are conducting a function vulnerability detection task for C/C++ language.

static void init_bit_trees ( ) {
 init_bit_tree ( cat1 , 1 ) ;
 init_bit_tree ( cat2 , 2 ) ;
 init_bit_tree ( cat3 , 3 ) ;
 init_bit_tree ( cat4 , 4 ) ;
 init_bit_tree ( cat5 , 5 ) ;
 init_bit_tree ( cat6 , 14 ) ;
 }

In the above code snippet, check for potential security vulnerabilities and answer with a single digit: 1 if Vulnerable, 0 if Non-vulnerable.

The node information of the code snippet is as follows:
Node 25769803820: (BLOCK) '{  init_bit_tree ( cat1 , 1 ) ;  init_bi...'
Node 30064771293: (CALL) 'init_bit_tree ( cat1 , 1 )'
Node 30064771294: (CALL) 'init_bit_tree ( cat2 , 2 )'
Node 30064771295: (CALL) 'init_bit_tree ( cat3 , 3 )'
Node 30064771296: (CALL) 'init_bit_tree ( cat4 , 4 )'
Node 30064771297: (CALL) 'init_bit_tree ( cat5 , 5 )'
Node 30064771298: (CALL) 'init_bit_tree ( cat6 , 14 )'
Node 68719476957: (IDENTIFIER) '<unknown> cat1'
Node 68719476958: (IDENTIFIER) '<unknown> cat2'
Node 68719476959: (IDENTIFIER) '<unknown> cat3'
Node 68719476960: (IDENTIFIER) '<unknown> cat4'
Node 68719476961: (IDENTIFIER) '<unknown> cat5'
Node 68719476962: (IDENTIFIER) '<unknown> cat6'
Node 90194313298: (LITERAL) '1'
Node 90194313299: (LITERAL) '2'
Node 90194313300: (LITERAL) '3'
Node 90194313301: (LITERAL) '4'
Node 90194313302: (LITERAL) '5'
Node 90194313303: (LITERAL) '14'
Node 94489280557: (LOCAL) '<unknown> cat6'
Node 94489280558: (LOCAL) '<unknown> cat5'
Node 94489280559: (LOCAL) '<unknown> cat4'
Node 94489280560: (LOCAL) '<unknown> cat3'
Node 94489280561: (LOCAL) '<unknown> cat2'
Node 94489280562: (LOCAL) '<unknown> cat1'
Node 107374182412: (METHOD) 'static void init_bit_trees ( ) {  init_b...'
Node 124554051596: (METHOD_RETURN) 'RET'
Node 128849018884: (MODIFIER) '<empty>'
The edge information of the code snippet is as follows:
Edge: Node 25769803820 -> AST -> Node 30064771293
Edge: Node 25769803820 -> AST -> Node 30064771294
Edge: Node 25769803820 -> AST -> Node 30064771295
Edge: Node 25769803820 -> AST -> Node 30064771296
Edge: Node 25769803820 -> AST -> Node 30064771297
Edge: Node 25769803820 -> AST -> Node 30064771298
Edge: Node 25769803820 -> AST -> Node 94489280557
Edge: Node 25769803820 -> AST -> Node 94489280558
Edge: Node 25769803820 -> AST -> Node 94489280559
Edge: Node 25769803820 -> AST -> Node 94489280560
Edge: Node 25769803820 -> AST -> Node 94489280561
Edge: Node 25769803820 -> AST -> Node 94489280562
Edge: Node 30064771293 -> ARGUMENT -> Node 68719476957
Edge: Node 30064771293 -> ARGUMENT -> Node 90194313298
Edge: Node 30064771293 -> AST -> Node 68719476957
Edge: Node 30064771293 -> AST -> Node 90194313298
Edge: Node 30064771293 -> CFG -> Node 68719476958
Edge: Node 30064771293 -> DOMINATE -> Node 68719476958
Edge: Node 30064771293 -> POST_DOMINATE -> Node 90194313298
Edge: Node 30064771293 -> REACHING_DEF -> Node 124554051596
Edge: Node 30064771294 -> ARGUMENT -> Node 68719476958
Edge: Node 30064771294 -> ARGUMENT -> Node 90194313299
Edge: Node 30064771294 -> AST -> Node 68719476958
Edge: Node 30064771294 -> AST -> Node 90194313299

The following is an example, and it is Non-vulnerable.
static int fetch_token ( netdissect_options * ndo , const u_char * pptr , u_int idx , u_int len , u_char * tbuf , size_t tbuflen ) {
 size_t toklen = 0 ;
 for ( ;
 idx < len ;
 idx ++ ) {
 if ( ! ND_TTEST ( * ( pptr + idx ) ) ) {
 return ( 0 ) ;
 }
 if ( ! isascii ( * ( pptr + idx ) ) ) {
 return ( 0 ) ;
 }
 if ( isspace ( * ( pptr + idx ) ) ) {
 break ;
 }
 if ( ! isprint ( * ( pptr + idx ) ) ) {
 return ( 0 ) ;
 }
 if ( toklen + 2 > tbuflen ) {
 return ( 0 ) ;
 }
 tbuf [ toklen ] = * ( pptr + idx ) ;
 toklen ++ ;
 }
 if ( toklen == 0 ) {
 return ( 0 ) ;
 }
 tbuf [ toklen ] = '\0' ;
 for ( ;
 idx < len ;
 idx ++ ) {
 if ( ! ND_TTEST ( * ( pptr + idx ) ) ) {
 break ;
 }
 if ( * ( pptr + idx ) == '\r' || * ( pptr + idx ) == '\n' ) {
 break ;
 }
 if ( ! isascii ( * ( pptr + idx ) ) || ! isprint ( * ( pptr + idx ) ) ) {
 break ;
 }
 if ( ! isspace ( * ( pptr + idx ) ) ) {
 break ;
 }
 }
 return ( idx ) ;
 }

Answer (0 or 1):
~~~~

## 60. reveal:test:258

Arm: B2-rand; phiên: frozen; seed: 42; dataset/split: reveal/test.
SHA-256 prompt: `9cb369501d9550a1bdb2f5dfba6fda6128f0a09e6be527067783da3c0831b6da`

~~~~text
You are now an excellent programmer. You are conducting a function vulnerability detection task for C/C++ language.

static void qemuMonitorJSONHandleIOError ( qemuMonitorPtr mon , virJSONValuePtr data ) {
 const char * device ;
 const char * action ;
 const char * reason ;
 int actionID ;
 if ( ( action = virJSONValueObjectGetString ( data , "action" ) ) == NULL ) {
 VIR_WARN ( "Missing action in disk io error event" ) ;
 action = "ignore" ;
 }
 if ( ( device = virJSONValueObjectGetString ( data , "device" ) ) == NULL ) {
 VIR_WARN ( "missing device in disk io error event" ) ;
 }
 # if 0 if ( ( reason = virJSONValueObjectGetString ( data , "reason" ) ) == NULL ) {
 VIR_WARN ( "missing reason in disk io error event" ) ;
 reason = "" ;
 }
 # else reason = "" ;
 # endif if ( ( actionID = qemuMonitorIOErrorActionTypeFromString ( action ) ) < 0 ) {
 VIR_WARN ( "unknown disk io error action '%s'" , action ) ;
 actionID = VIR_DOMAIN_EVENT_IO_ERROR_NONE ;
 }
 qemuMonitorEmitIOError ( mon , device , actionID , reason ) ;
 }

In the above code snippet, check for potential security vulnerabilities and answer with a single digit: 1 if Vulnerable, 0 if Non-vulnerable.

The node information of the code snippet is as follows:
Node 25769803842: (BLOCK) '{  const char * device ;  const char * a...'
Node 25769803843: (BLOCK) '{  VIR_WARN ( "Missing action in disk io...'
Node 25769803844: (BLOCK) '{ VIR_WARN ( "missing device in disk io ...'
Node 25769803853: (BLOCK) '<empty>'
Node 30064771372: (CALL) '( action = virJSONValueObjectGetString (...'
Node 30064771373: (CALL) 'action = virJSONValueObjectGetString ( d...'
Node 30064771374: (CALL) 'virJSONValueObjectGetString ( data , "ac...'
Node 30064771375: (CALL) 'VIR_WARN ( "Missing action in disk io er...'
Node 30064771376: (CALL) 'action = "ignore"'
Node 30064771377: (CALL) '( device = virJSONValueObjectGetString (...'
Node 30064771378: (CALL) 'device = virJSONValueObjectGetString ( d...'
Node 30064771379: (CALL) 'virJSONValueObjectGetString ( data , "de...'
Node 30064771380: (CALL) 'VIR_WARN ( "missing device in disk io er...'
Node 30064771381: (CALL) 'VIR_WARN ( "unknown disk io error action...'
Node 30064771382: (CALL) 'actionID = VIR_DOMAIN_EVENT_IO_ERROR_NON...'
Node 47244640294: (CONTROL_STRUCTURE) 'if ( ( action = virJSONValueObjectGetStr...'
Node 47244640295: (CONTROL_STRUCTURE) 'if ( ( device = virJSONValueObjectGetStr...'
Node 68719477001: (IDENTIFIER) 'action'
Node 68719477002: (IDENTIFIER) 'data'
Node 68719477003: (IDENTIFIER) '<unknown> NULL'
Node 68719477004: (IDENTIFIER) 'action'
Node 68719477005: (IDENTIFIER) 'device'
Node 68719477006: (IDENTIFIER) 'data'
Node 68719477007: (IDENTIFIER) '<unknown> NULL'
Node 68719477008: (IDENTIFIER) 'action'
Node 68719477009: (IDENTIFIER) 'actionID'
Node 68719477010: (IDENTIFIER) '<unknown> VIR_DOMAIN_EVENT_IO_ERROR_NONE'
Node 90194313288: (LITERAL) '"action"'
Node 90194313289: (LITERAL) '"Missing action in disk io error event"'
Node 90194313290: (LITERAL) '"ignore"'
Node 90194313291: (LITERAL) '"device"'
Node 90194313292: (LITERAL) '"missing device in disk io error event"'
Node 90194313293: (LITERAL) '"unknown disk io error action '%s'"'
Node 94489280577: (LOCAL) 'const char * device'
Node 94489280578: (LOCAL) 'const char * action'
Node 94489280579: (LOCAL) 'const char * reason'
Node 94489280580: (LOCAL) 'int actionID'
Node 94489280581: (LOCAL) '<unknown> VIR_DOMAIN_EVENT_IO_ERROR_NONE'
Node 94489280582: (LOCAL) '<unknown> NULL'
Node 107374182424: (METHOD) 'static void qemuMonitorJSONHandleIOError...'
The edge information of the code snippet is as follows:
Edge: Node 25769803842 -> AST -> Node 94489280577
Edge: Node 25769803842 -> AST -> Node 94489280578
Edge: Node 25769803842 -> AST -> Node 94489280579
Edge: Node 25769803842 -> AST -> Node 94489280580
Edge: Node 25769803842 -> AST -> Node 47244640294
Edge: Node 25769803842 -> AST -> Node 47244640295
Edge: Node 25769803842 -> AST -> Node 30064771381
Edge: Node 25769803842 -> AST -> Node 30064771382
Edge: Node 25769803842 -> AST -> Node 94489280581
Edge: Node 25769803842 -> AST -> Node 94489280582
Edge: Node 25769803843 -> AST -> Node 30064771375
Edge: Node 25769803843 -> AST -> Node 30064771376
Edge: Node 25769803844 -> AST -> Node 30064771380
Edge: Node 30064771372 -> ARGUMENT -> Node 30064771373

The following is an example, and it is Non-vulnerable.
static void dissect_zcl_scenes_remove_all_get_scene_membership ( tvbuff_t * tvb , proto_tree * tree , guint * offset ) {
 proto_tree_add_item ( tree , hf_zbee_zcl_scenes_group_id , tvb , * offset , 2 , ENC_LITTLE_ENDIAN ) ;
 * offset += 2 ;
 }

Answer (0 or 1):
~~~~

