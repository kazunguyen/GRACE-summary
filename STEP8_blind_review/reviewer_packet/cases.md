# Gói chấm mù độ liên quan của demo

30 ca. Mở [hướng dẫn chấm](README.md) trước khi điền phiếu. Số dòng bắt đầu lại từ 1 trong mỗi khối mã.

## Danh sách ca

[CA-01](#ca-01) · [CA-02](#ca-02) · [CA-03](#ca-03) · [CA-04](#ca-04) · [CA-05](#ca-05) · [CA-06](#ca-06)
[CA-07](#ca-07) · [CA-08](#ca-08) · [CA-09](#ca-09) · [CA-10](#ca-10) · [CA-11](#ca-11) · [CA-12](#ca-12)
[CA-13](#ca-13) · [CA-14](#ca-14) · [CA-15](#ca-15) · [CA-16](#ca-16) · [CA-17](#ca-17) · [CA-18](#ca-18)
[CA-19](#ca-19) · [CA-20](#ca-20) · [CA-21](#ca-21) · [CA-22](#ca-22) · [CA-23](#ca-23) · [CA-24](#ca-24)
[CA-25](#ca-25) · [CA-26](#ca-26) · [CA-27](#ca-27) · [CA-28](#ca-28) · [CA-29](#ca-29) · [CA-30](#ca-30)

## CA-01

### Target

```text
   1 | unsigned int TSMimeHdrFieldValueUintGet ( TSMBuffer bufp , TSMLoc hdr , TSMLoc field , int idx ) {
   2 |  sdk_assert ( sdk_sanity_check_mbuffer ( bufp ) == TS_SUCCESS ) ;
   3 |  sdk_assert ( ( sdk_sanity_check_mime_hdr_handle ( hdr ) == TS_SUCCESS ) || ( sdk_sanity_check_http_hdr_handle ( hdr ) == TS_SUCCESS ) ) ;
   4 |  sdk_assert ( sdk_sanity_check_field_handle ( field , hdr ) == TS_SUCCESS ) ;
   5 |  int value_len ;
   6 |  const char * value_str = TSMimeFieldValueGet ( bufp , field , idx , & value_len ) ;
   7 |  if ( value_str == nullptr ) {
   8 |  return 0 ;
   9 |  }
  10 |  return mime_parse_uint ( value_str , value_str + value_len ) ;
  11 |  }
```

### Demo A

```text
   1 | static char * wv_csp10_opaque_literal_tag ( tvbuff_t * tvb , guint32 offset , const char * token , guint8 codepage _U_ , guint32 * length ) {
   2 |  guint32 data_len = tvb_get_guintvar ( tvb , offset , length ) ;
   3 |  char * str = NULL ;
   4 |  if ( token && ( ( strcmp ( token , "Code" ) == 0 ) || ( strcmp ( token , "ContentSize" ) == 0 ) || ( strcmp ( token , "MessageCount" ) == 0 ) || ( strcmp ( token , "Validity" ) == 0 ) || ( strcmp ( token , "KeepAliveTime" ) == 0 ) || ( strcmp ( token , "TimeToLive" ) == 0 ) || ( strcmp ( token , "AcceptedContentLength" ) == 0 ) || ( strcmp ( token , "MultiTrans" ) == 0 ) || ( strcmp ( token , "ParserSize" ) == 0 ) || ( strcmp ( token , "ServerPollMin" ) == 0 ) || ( strcmp ( token , "TCPAddress" ) == 0 ) || ( strcmp ( token , "TCPPort" ) == 0 ) || ( strcmp ( token , "UDPPort" ) == 0 ) ) ) {
   5 |  str = wv_integer_from_opaque ( tvb , offset + * length , data_len ) ;
   6 |  }
   7 |  else if ( token && ( strcmp ( token , "DateTime" ) == 0 ) ) {
   8 |  str = wv_datetime_from_opaque ( tvb , offset + * length , data_len ) ;
   9 |  }
  10 |  if ( str == NULL ) {
  11 |  str = wmem_strdup_printf ( wmem_packet_scope ( ) , "(%d bytes of unparsed opaque data)" , data_len ) ;
  12 |  }
  13 |  * length += data_len ;
  14 |  return str ;
  15 |  }
```

### Demo B

```text
   1 | int TSMimeHdrFieldValueIntGet ( TSMBuffer bufp , TSMLoc hdr , TSMLoc field , int idx ) {
   2 |  sdk_assert ( sdk_sanity_check_mbuffer ( bufp ) == TS_SUCCESS ) ;
   3 |  sdk_assert ( ( sdk_sanity_check_mime_hdr_handle ( hdr ) == TS_SUCCESS ) || ( sdk_sanity_check_http_hdr_handle ( hdr ) == TS_SUCCESS ) ) ;
   4 |  sdk_assert ( sdk_sanity_check_field_handle ( field , hdr ) == TS_SUCCESS ) ;
   5 |  int value_len ;
   6 |  const char * value_str = TSMimeFieldValueGet ( bufp , field , idx , & value_len ) ;
   7 |  if ( value_str == nullptr ) {
   8 |  return 0 ;
   9 |  }
  10 |  return mime_parse_int ( value_str , value_str + value_len ) ;
  11 |  }
```

[Về danh sách ca](#danh-sách-ca)

## CA-02

### Target

```text
   1 | static const char * array_value ( const char * * array , char key ) {
   2 |  for ( ;
   3 |  * array ;
   4 |  array += 2 ) if ( * * array == key ) return array [ 1 ] ;
   5 |  return 0 ;
   6 |  }
```

### Demo A

```text
   1 | static Flag decBiStr ( const char * targ , const char * str1 , const char * str2 ) {
   2 |  for ( ;
   3 |  ;
   4 |  targ ++ , str1 ++ , str2 ++ ) {
   5 |  if ( * targ != * str1 && * targ != * str2 ) return 0 ;
   6 |  if ( * targ == '\0' ) break ;
   7 |  }
   8 |  return 1 ;
   9 |  }
```

### Demo B

```text
   1 | err_status_t srtp_protect ( srtp_ctx_t * ctx , void * rtp_hdr , int * pkt_octet_len ) {
   2 |  srtp_hdr_t * hdr = ( srtp_hdr_t * ) rtp_hdr ;
   3 |  uint32_t * enc_start ;
   4 |  uint32_t * auth_start ;
   5 |  unsigned int enc_octet_len = 0 ;
   6 |  xtd_seq_num_t est ;
   7 |  int delta ;
   8 |  uint8_t * auth_tag = NULL ;
   9 |  err_status_t status ;
  10 |  int tag_len ;
  11 |  srtp_stream_ctx_t * stream ;
  12 |  int prefix_len ;
  13 |  debug_print ( mod_srtp , "function srtp_protect" , NULL ) ;
  14 |  status = srtp_validate_rtp_header ( rtp_hdr , pkt_octet_len ) ;
  15 |  if ( status ) return status ;
  16 |  if ( * pkt_octet_len < octets_in_rtp_header ) return err_status_bad_param ;
  17 |  stream = srtp_get_stream ( ctx , hdr -> ssrc ) ;
  18 |  if ( stream == NULL ) {
  19 |  if ( ctx -> stream_template != NULL ) {
  20 |  srtp_stream_ctx_t * new_stream ;
  21 |  status = srtp_stream_clone ( ctx -> stream_template , hdr -> ssrc , & new_stream ) ;
  22 |  if ( status ) return status ;
  23 |  new_stream -> next = ctx -> stream_list ;
  24 |  ctx -> stream_list = new_stream ;
  25 |  new_stream -> direction = dir_srtp_sender ;
  26 |  stream = new_stream ;
  27 |  }
  28 |  else {
  29 |  return err_status_no_ctx ;
  30 |  }
  31 |  }
  32 |  if ( stream -> direction != dir_srtp_sender ) {
  33 |  if ( stream -> direction == dir_unknown ) {
  34 |  stream -> direction = dir_srtp_sender ;
  35 |  }
  36 |  else {
  37 |  srtp_handle_event ( ctx , stream , event_ssrc_collision ) ;
  38 |  }
  39 |  }
  40 |  if ( stream -> rtp_cipher -> algorithm == AES_128_GCM || stream -> rtp_cipher -> algorithm == AES_256_GCM ) {
  41 |  return srtp_protect_aead ( ctx , stream , rtp_hdr , ( unsigned int * ) pkt_octet_len ) ;
  42 |  }
  43 |  switch ( key_limit_update ( stream -> limit ) ) {
  44 |  case key_event_normal : break ;
  45 |  case key_event_soft_limit : srtp_handle_event ( ctx , stream , event_key_soft_limit ) ;
  46 |  break ;
  47 |  case key_event_hard_limit : srtp_handle_event ( ctx , stream , event_key_hard_limit ) ;
  48 |  return err_status_key_expired ;
  49 |  default : break ;
  50 |  }
  51 |  tag_len = auth_get_tag_length ( stream -> rtp_auth ) ;
  52 |  if ( stream -> rtp_services & sec_serv_conf ) {
  53 |  enc_start = ( uint32_t * ) hdr + uint32s_in_rtp_header + hdr -> cc ;
  54 |  if ( hdr -> x == 1 ) {
  55 |  srtp_hdr_xtnd_t * xtn_hdr = ( srtp_hdr_xtnd_t * ) enc_start ;
  56 |  enc_start += ( ntohs ( xtn_hdr -> length ) + 1 ) ;
  57 |  if ( ! ( ( uint8_t * ) enc_start < ( uint8_t * ) hdr + * pkt_octet_len ) ) return err_status_parse_err ;
  58 |  }
  59 |  enc_octet_len = ( unsigned int ) ( * pkt_octet_len - ( ( uint8_t * ) enc_start - ( uint8_t * ) hdr ) ) ;
  60 |  }
  61 |  else {
  62 |  enc_start = NULL ;
  63 |  }
  64 |  if ( stream -> rtp_services & sec_serv_auth ) {
  65 |  auth_start = ( uint32_t * ) hdr ;
  66 |  auth_tag = ( uint8_t * ) hdr + * pkt_octet_len ;
  67 |  }
  68 |  else {
  69 |  auth_start = NULL ;
  70 |  auth_tag = NULL ;
  71 |  }
  72 |  delta = rdbx_estimate_index ( & stream -> rtp_rdbx , & est , ntohs ( hdr -> seq ) ) ;
  73 |  status = rdbx_check ( & stream -> rtp_rdbx , delta ) ;
  74 |  if ( status ) {
  75 |  if ( status != err_status_replay_fail || ! stream -> allow_repeat_tx ) return status ;
  76 |  }
  77 |  else rdbx_add_index ( & stream -> rtp_rdbx , delta ) ;
  78 |  # ifdef NO_64BIT_MATH debug_print2 ( mod_srtp , "estimated packet index: %08x%08x" , high32 ( est ) , low32 ( est ) ) ;
  79 |  # else debug_print ( mod_srtp , "estimated packet index: %016llx" , est ) ;
  80 |  # endif if ( stream -> rtp_cipher -> type -> id == AES_ICM || stream -> rtp_cipher -> type -> id == AES_256_ICM ) {
  81 |  v128_t iv ;
  82 |  iv . v32 [ 0 ] = 0 ;
  83 |  iv . v32 [ 1 ] = hdr -> ssrc ;
  84 |  # ifdef NO_64BIT_MATH iv . v64 [ 1 ] = be64_to_cpu ( make64 ( ( high32 ( est ) << 16 ) | ( low32 ( est ) >> 16 ) , low32 ( est ) << 16 ) ) ;
  85 |  # else iv . v64 [ 1 ] = be64_to_cpu ( est << 16 ) ;
  86 |  # endif status = cipher_set_iv ( stream -> rtp_cipher , & iv , direction_encrypt ) ;
  87 |  }
  88 |  else {
  89 |  v128_t iv ;
  90 |  # ifdef NO_64BIT_MATH iv . v32 [ 0 ] = 0 ;
  91 |  iv . v32 [ 1 ] = 0 ;
  92 |  # else iv . v64 [ 0 ] = 0 ;
  93 |  # endif iv . v64 [ 1 ] = be64_to_cpu ( est ) ;
  94 |  status = cipher_set_iv ( stream -> rtp_cipher , & iv , direction_encrypt ) ;
  95 |  }
  96 |  if ( status ) return err_status_cipher_fail ;
  97 |  # ifdef NO_64BIT_MATH est = be64_to_cpu ( make64 ( ( high32 ( est ) << 16 ) | ( low32 ( est ) >> 16 ) , low32 ( est ) << 16 ) ) ;
  98 |  # else est = be64_to_cpu ( est << 16 ) ;
  99 |  # endif if ( auth_start ) {
 100 |  prefix_len = auth_get_prefix_length ( stream -> rtp_auth ) ;
 101 |  if ( prefix_len ) {
 102 |  status = cipher_output ( stream -> rtp_cipher , auth_tag , prefix_len ) ;
 103 |  if ( status ) return err_status_cipher_fail ;
 104 |  debug_print ( mod_srtp , "keystream prefix: %s" , octet_string_hex_string ( auth_tag , prefix_len ) ) ;
 105 |  }
 106 |  }
 107 |  if ( enc_start ) {
 108 |  status = cipher_encrypt ( stream -> rtp_cipher , ( uint8_t * ) enc_start , & enc_octet_len ) ;
 109 |  if ( status ) return err_status_cipher_fail ;
 110 |  }
 111 |  if ( auth_start ) {
 112 |  status = auth_start ( stream -> rtp_auth ) ;
 113 |  if ( status ) return status ;
 114 |  status = auth_update ( stream -> rtp_auth , ( uint8_t * ) auth_start , * pkt_octet_len ) ;
 115 |  if ( status ) return status ;
 116 |  debug_print ( mod_srtp , "estimated packet index: %016llx" , est ) ;
 117 |  status = auth_compute ( stream -> rtp_auth , ( uint8_t * ) & est , 4 , auth_tag
 118 | /* [TRUNCATED] */
```

[Về danh sách ca](#danh-sách-ca)

## CA-03

### Target

```text
   1 | static inline void RENAME(yuv422ptouyvy)(const uint8_t *ysrc, const uint8_t *usrc, const uint8_t *vsrc, uint8_t *dst,
   2 | 
   3 |                                          long width, long height,
   4 | 
   5 |                                          long lumStride, long chromStride, long dstStride)
   6 | 
   7 | {
   8 | 
   9 |     RENAME(yuvPlanartouyvy)(ysrc, usrc, vsrc, dst, width, height, lumStride, chromStride, dstStride, 1);
  10 | 
  11 | }
```

### Demo A

```text
   1 | static double get_scene_score(AVFilterContext *ctx, AVFrame *crnt, AVFrame *next)
   2 | 
   3 | {
   4 | 
   5 |     FrameRateContext *s = ctx->priv;
   6 | 
   7 |     double ret = 0;
   8 | 
   9 | 
  10 | 
  11 |     ff_dlog(ctx, "get_scene_score()\n");
  12 | 
  13 | 
  14 | 
  15 |     if (crnt->height == next->height &&
  16 | 
  17 |         crnt->width  == next->width) {
  18 | 
  19 |         int64_t sad;
  20 | 
  21 |         double mafd, diff;
  22 | 
  23 | 
  24 | 
  25 |         ff_dlog(ctx, "get_scene_score() process\n");
  26 | 
  27 |         if (s->bitdepth == 8)
  28 | 
  29 |             sad = scene_sad8(s, crnt->data[0], crnt->linesize[0], next->data[0], next->linesize[0], crnt->height);
  30 | 
  31 |         else
  32 | 
  33 |             sad = scene_sad16(s, (const uint16_t*)crnt->data[0], crnt->linesize[0] >> 1, (const uint16_t*)next->data[0], next->linesize[0] >> 1, crnt->height);
  34 | 
  35 | 
  36 | 
  37 |         mafd = (double)sad * 100.0 / (crnt->height * crnt->width) / (1 << s->bitdepth);
  38 | 
  39 |         diff = fabs(mafd - s->prev_mafd);
  40 | 
  41 |         ret  = av_clipf(FFMIN(mafd, diff), 0, 100.0);
  42 | 
  43 |         s->prev_mafd = mafd;
  44 | 
  45 |     }
  46 | 
  47 |     ff_dlog(ctx, "get_scene_score() result is:%f\n", ret);
  48 | 
  49 |     return ret;
  50 | 
  51 | }
```

### Demo B

```text
   1 | static inline void RENAME(yuv422ptoyuy2)(const uint8_t *ysrc, const uint8_t *usrc, const uint8_t *vsrc, uint8_t *dst,
   2 | 
   3 | 	unsigned int width, unsigned int height,
   4 | 
   5 | 	int lumStride, int chromStride, int dstStride)
   6 | 
   7 | {
   8 | 
   9 | 	RENAME(yuvPlanartoyuy2)(ysrc, usrc, vsrc, dst, width, height, lumStride, chromStride, dstStride, 1);
  10 | 
  11 | }
```

[Về danh sách ca](#danh-sách-ca)

## CA-04

### Target

```text
   1 | static int libquvi_read_header(AVFormatContext *s)
   2 | 
   3 | {
   4 | 
   5 |     int i, ret;
   6 | 
   7 |     quvi_t q;
   8 | 
   9 |     quvi_media_t m;
  10 | 
  11 |     QUVIcode rc;
  12 | 
  13 |     LibQuviContext *qc = s->priv_data;
  14 | 
  15 |     char *media_url, *pagetitle;
  16 | 
  17 | 
  18 | 
  19 |     rc = quvi_init(&q);
  20 | 
  21 |     if (rc != QUVI_OK)
  22 | 
  23 |         goto quvi_fail;
  24 | 
  25 | 
  26 | 
  27 |     quvi_setopt(q, QUVIOPT_FORMAT, qc->format);
  28 | 
  29 | 
  30 | 
  31 |     rc = quvi_parse(q, s->filename, &m);
  32 | 
  33 |     if (rc != QUVI_OK)
  34 | 
  35 |         goto quvi_fail;
  36 | 
  37 | 
  38 | 
  39 |     rc = quvi_getprop(m, QUVIPROP_MEDIAURL, &media_url);
  40 | 
  41 |     if (rc != QUVI_OK)
  42 | 
  43 |         goto quvi_fail;
  44 | 
  45 | 
  46 | 
  47 |     av_assert0(!qc->fmtctx->codec_whitelist && !qc->fmtctx->format_whitelist);
  48 | 
  49 |     qc->fmtctx-> codec_whitelist = av_strdup(s->codec_whitelist);
  50 | 
  51 |     qc->fmtctx->format_whitelist = av_strdup(s->format_whitelist);
  52 | 
  53 | 
  54 | 
  55 |     ret = avformat_open_input(&qc->fmtctx, media_url, NULL, NULL);
  56 | 
  57 |     if (ret < 0)
  58 | 
  59 |         goto end;
  60 | 
  61 | 
  62 | 
  63 |     rc = quvi_getprop(m, QUVIPROP_PAGETITLE, &pagetitle);
  64 | 
  65 |     if (rc == QUVI_OK)
  66 | 
  67 |         av_dict_set(&s->metadata, "title", pagetitle, 0);
  68 | 
  69 | 
  70 | 
  71 |     for (i = 0; i < qc->fmtctx->nb_streams; i++) {
  72 | 
  73 |         AVStream *st = avformat_new_stream(s, NULL);
  74 | 
  75 |         AVStream *ist = qc->fmtctx->streams[i];
  76 | 
  77 |         if (!st) {
  78 | 
  79 |             ret = AVERROR(ENOMEM);
  80 | 
  81 |             goto end;
  82 | 
  83 |         }
  84 | 
  85 |         avpriv_set_pts_info(st, ist->pts_wrap_bits, ist->time_base.num, ist->time_base.den);
  86 | 
  87 |         avcodec_copy_context(st->codec, qc->fmtctx->streams[i]->codec);
  88 | 
  89 |     }
  90 | 
  91 | 
  92 | 
  93 |     return 0;
  94 | 
  95 | 
  96 | 
  97 | quvi_fail:
  98 | 
  99 |     av_log(s, AV_LOG_ERROR, "%s\n", quvi_strerror(q, rc));
 100 | 
 101 |     ret = AVERROR_EXTERNAL;
 102 | 
 103 | 
 104 | 
 105 | end:
 106 | 
 107 |     quvi_parse_close(&m);
 108 | 
 109 |     quvi_close(&q);
 110 | 
 111 |     return ret;
 112 | 
 113 | }
```

### Demo A

```text
   1 | static void test_acpi_dsdt_table(test_data *data)
   2 | 
   3 | {
   4 | 
   5 |     AcpiSdtTable dsdt_table;
   6 | 
   7 |     uint32_t addr = le32_to_cpu(data->fadt_table.dsdt);
   8 | 
   9 | 
  10 | 
  11 |     test_dst_table(&dsdt_table, addr);
  12 | 
  13 |     ACPI_ASSERT_CMP(dsdt_table.header.signature, "DSDT");
  14 | 
  15 | 
  16 | 
  17 |     /* Since DSDT isn't in RSDT, add DSDT to ASL test tables list manually */
  18 | 
  19 |     g_array_append_val(data->tables, dsdt_table);
  20 | 
  21 | }
```

### Demo B

```text
   1 | static void get_attachment(AVFormatContext *s, AVIOContext *pb, int length)
   2 | 
   3 | {
   4 | 
   5 |     char mime[1024];
   6 | 
   7 |     char description[1024];
   8 | 
   9 |     unsigned int filesize;
  10 | 
  11 |     AVStream *st;
  12 | 
  13 |     int64_t pos = avio_tell(pb);
  14 | 
  15 | 
  16 | 
  17 |     avio_get_str16le(pb, INT_MAX, mime, sizeof(mime));
  18 | 
  19 |     if (strcmp(mime, "image/jpeg"))
  20 | 
  21 |         goto done;
  22 | 
  23 | 
  24 | 
  25 |     avio_r8(pb);
  26 | 
  27 |     avio_get_str16le(pb, INT_MAX, description, sizeof(description));
  28 | 
  29 |     filesize = avio_rl32(pb);
  30 | 
  31 |     if (!filesize)
  32 | 
  33 |         goto done;
  34 | 
  35 | 
  36 | 
  37 |     st = avformat_new_stream(s, NULL);
  38 | 
  39 |     if (!st)
  40 | 
  41 |         goto done;
  42 | 
  43 |     av_dict_set(&st->metadata, "title", description, 0);
  44 | 
  45 |     st->codec->codec_id   = AV_CODEC_ID_MJPEG;
  46 | 
  47 |     st->codec->codec_type = AVMEDIA_TYPE_ATTACHMENT;
  48 | 
  49 |     st->codec->extradata  = av_mallocz(filesize);
  50 | 
  51 | 
  52 |     if (!st->codec->extradata)
  53 | 
  54 |         goto done;
  55 | 
  56 |     st->codec->extradata_size = filesize;
  57 | 
  58 |     avio_read(pb, st->codec->extradata, filesize);
  59 | 
  60 | done:
  61 | 
  62 |     avio_seek(pb, pos + length, SEEK_SET);
  63 | 
  64 | }
```

[Về danh sách ca](#danh-sách-ca)

## CA-05

### Target

```text
   1 | IN_PROC_BROWSER_TEST_F ( ContentFaviconDriverTest , AssociateIconWithInitialPageIconDespiteReplaceState ) {
   2 |  ASSERT_TRUE ( embedded_test_server ( ) -> Start ( ) ) ;
   3 |  GURL url = embedded_test_server ( ) -> GetURL ( "/favicon/replacestate_with_favicon.html" ) ;
   4 |  GURL replacestate_url = embedded_test_server ( ) -> GetURL ( "/favicon/replacestate_with_favicon_replaced.html" ) ;
   5 |  PendingTaskWaiter waiter ( web_contents ( ) ) ;
   6 |  waiter . AlsoRequireUrl ( replacestate_url ) ;
   7 |  ui_test_utils : : NavigateToURLWithDisposition ( browser ( ) , url , WindowOpenDisposition : : CURRENT_TAB , ui_test_utils : : BROWSER_TEST_NONE ) ;
   8 |  waiter . Wait ( ) ;
   9 |  EXPECT_NE ( nullptr , GetFaviconForPageURL ( url , favicon_base : : IconType : : kFavicon ) . bitmap_data ) ;
  10 |  EXPECT_NE ( nullptr , GetFaviconForPageURL ( replacestate_url , favicon_base : : IconType : : kFavicon ) . bitmap_data ) ;
  11 |  }
```

### Demo A

```text
   1 | static void dissect_coap_opt_hex_string ( tvbuff_t * tvb , proto_item * item , proto_tree * subtree , gint offset , gint opt_length , int hf ) {
   2 |  const guint8 * str ;
   3 |  if ( opt_length == 0 ) str = nullstr ;
   4 |  else str = tvb_bytes_to_str_punct ( wmem_packet_scope ( ) , tvb , offset , opt_length , ' ' ) ;
   5 |  proto_tree_add_item ( subtree , hf , tvb , offset , opt_length , ENC_NA ) ;
   6 |  proto_item_append_text ( item , ": %s" , str ) ;
   7 |  }
```

### Demo B

```text
   1 | IN_PROC_BROWSER_TEST_F ( ContentFaviconDriverTest , AssociateIconWithInitialPageIconDespitePushState ) {
   2 |  ASSERT_TRUE ( embedded_test_server ( ) -> Start ( ) ) ;
   3 |  GURL url = embedded_test_server ( ) -> GetURL ( "/favicon/pushstate_with_favicon.html" ) ;
   4 |  GURL pushstate_url = embedded_test_server ( ) -> GetURL ( "/favicon/pushstate_with_favicon_pushed.html" ) ;
   5 |  PendingTaskWaiter waiter ( web_contents ( ) ) ;
   6 |  waiter . AlsoRequireUrl ( pushstate_url ) ;
   7 |  ui_test_utils : : NavigateToURLWithDisposition ( browser ( ) , url , WindowOpenDisposition : : CURRENT_TAB , ui_test_utils : : BROWSER_TEST_NONE ) ;
   8 |  waiter . Wait ( ) ;
   9 |  EXPECT_NE ( nullptr , GetFaviconForPageURL ( url , favicon_base : : IconType : : kFavicon ) . bitmap_data ) ;
  10 |  EXPECT_NE ( nullptr , GetFaviconForPageURL ( pushstate_url , favicon_base : : IconType : : kFavicon ) . bitmap_data ) ;
  11 |  }
```

[Về danh sách ca](#danh-sách-ca)

## CA-06

### Target

```text
   1 | static void mixer_reset (AC97LinkState *s)
   2 | 
   3 | {
   4 | 
   5 |     uint8_t active[LAST_INDEX];
   6 | 
   7 | 
   8 | 
   9 |     dolog ("mixer_reset\n");
  10 | 
  11 |     memset (s->mixer_data, 0, sizeof (s->mixer_data));
  12 | 
  13 |     memset (active, 0, sizeof (active));
  14 | 
  15 |     mixer_store (s, AC97_Reset                   , 0x0000); /* 6940 */
  16 | 
  17 |     mixer_store (s, AC97_Master_Volume_Mono_Mute , 0x8000);
  18 | 
  19 |     mixer_store (s, AC97_PC_BEEP_Volume_Mute     , 0x0000);
  20 | 
  21 | 
  22 | 
  23 |     mixer_store (s, AC97_Phone_Volume_Mute       , 0x8008);
  24 | 
  25 |     mixer_store (s, AC97_Mic_Volume_Mute         , 0x8008);
  26 | 
  27 |     mixer_store (s, AC97_CD_Volume_Mute          , 0x8808);
  28 | 
  29 |     mixer_store (s, AC97_Aux_Volume_Mute         , 0x8808);
  30 | 
  31 |     mixer_store (s, AC97_Record_Gain_Mic_Mute    , 0x8000);
  32 | 
  33 |     mixer_store (s, AC97_General_Purpose         , 0x0000);
  34 | 
  35 |     mixer_store (s, AC97_3D_Control              , 0x0000);
  36 | 
  37 |     mixer_store (s, AC97_Powerdown_Ctrl_Stat     , 0x000f);
  38 | 
  39 | 
  40 | 
  41 |     /*
  42 | 
  43 |      * Sigmatel 9700 (STAC9700)
  44 | 
  45 |      */
  46 | 
  47 |     mixer_store (s, AC97_Vendor_ID1              , 0x8384);
  48 | 
  49 |     mixer_store (s, AC97_Vendor_ID2              , 0x7600); /* 7608 */
  50 | 
  51 | 
  52 | 
  53 |     mixer_store (s, AC97_Extended_Audio_ID       , 0x0809);
  54 | 
  55 |     mixer_store (s, AC97_Extended_Audio_Ctrl_Stat, 0x0009);
  56 | 
  57 |     mixer_store (s, AC97_PCM_Front_DAC_Rate      , 0xbb80);
  58 | 
  59 |     mixer_store (s, AC97_PCM_Surround_DAC_Rate   , 0xbb80);
  60 | 
  61 |     mixer_store (s, AC97_PCM_LFE_DAC_Rate        , 0xbb80);
  62 | 
  63 |     mixer_store (s, AC97_PCM_LR_ADC_Rate         , 0xbb80);
  64 | 
  65 |     mixer_store (s, AC97_MIC_ADC_Rate            , 0xbb80);
  66 | 
  67 | 
  68 | 
  69 |     record_select (s, 0);
  70 | 
  71 |     set_volume (s, AC97_Master_Volume_Mute, 0x8000);
  72 | 
  73 |     set_volume (s, AC97_PCM_Out_Volume_Mute, 0x8808);
  74 | 
  75 |     set_volume (s, AC97_Line_In_Volume_Mute, 0x8808);
  76 | 
  77 | 
  78 | 
  79 |     reset_voices (s, active);
  80 | 
  81 | }
```

### Demo A

```text
   1 | static int gt64120_pci_init(PCIDevice *d)
   2 | 
   3 | {
   4 | 
   5 |     /* FIXME: Malta specific hw assumptions ahead */
   6 | 
   7 |     pci_config_set_vendor_id(d->config, PCI_VENDOR_ID_MARVELL);
   8 | 
   9 |     pci_config_set_device_id(d->config, PCI_DEVICE_ID_MARVELL_GT6412X);
  10 | 
  11 |     pci_set_word(d->config + PCI_COMMAND, 0);
  12 | 
  13 |     pci_set_word(d->config + PCI_STATUS,
  14 | 
  15 |                  PCI_STATUS_FAST_BACK | PCI_STATUS_DEVSEL_MEDIUM);
  16 | 
  17 |     pci_set_byte(d->config + PCI_CLASS_REVISION, 0x10);
  18 | 
  19 |     pci_config_set_prog_interface(d->config, 0);
  20 | 
  21 |     pci_config_set_class(d->config, PCI_CLASS_BRIDGE_HOST);
  22 | 
  23 |     pci_set_long(d->config + PCI_BASE_ADDRESS_0, 0x00000008);
  24 | 
  25 |     pci_set_long(d->config + PCI_BASE_ADDRESS_1, 0x01000008);
  26 | 
  27 |     pci_set_long(d->config + PCI_BASE_ADDRESS_2, 0x1c000000);
  28 | 
  29 |     pci_set_long(d->config + PCI_BASE_ADDRESS_3, 0x1f000000);
  30 | 
  31 |     pci_set_long(d->config + PCI_BASE_ADDRESS_4, 0x14000000);
  32 | 
  33 |     pci_set_long(d->config + PCI_BASE_ADDRESS_5, 0x14000001);
  34 | 
  35 |     pci_set_byte(d->config + 0x3d, 0x01);
  36 | 
  37 | 
  38 | 
  39 |     return 0;
  40 | 
  41 | }
```

### Demo B

```text
   1 | int cpu_gen_code(CPUState *env, TranslationBlock *tb,
   2 | 
   3 |                  int max_code_size, int *gen_code_size_ptr)
   4 | 
   5 | {
   6 | 
   7 |     uint8_t *gen_code_buf;
   8 | 
   9 |     int gen_code_size;
  10 | 
  11 | 
  12 | 
  13 |     if (gen_intermediate_code(env, tb) < 0)
  14 | 
  15 |         return -1;
  16 | 
  17 |     
  18 | 
  19 |     /* generate machine code */
  20 | 
  21 |     tb->tb_next_offset[0] = 0xffff;
  22 | 
  23 |     tb->tb_next_offset[1] = 0xffff;
  24 | 
  25 |     gen_code_buf = tb->tc_ptr;
  26 | 
  27 | #ifdef USE_DIRECT_JUMP
  28 | 
  29 |     /* the following two entries are optional (only used for string ops) */
  30 | 
  31 |     tb->tb_jmp_offset[2] = 0xffff;
  32 | 
  33 |     tb->tb_jmp_offset[3] = 0xffff;
  34 | 
  35 | #endif
  36 | 
  37 |     dyngen_labels(gen_labels, nb_gen_labels, gen_code_buf, gen_opc_buf);
  38 | 
  39 |     
  40 | 
  41 |     gen_code_size = dyngen_code(gen_code_buf, tb->tb_next_offset,
  42 | 
  43 | #ifdef USE_DIRECT_JUMP
  44 | 
  45 |                                 tb->tb_jmp_offset,
  46 | 
  47 | #else
  48 | 
  49 |                                 NULL,
  50 | 
  51 | #endif
  52 | 
  53 |                                 gen_opc_buf, gen_opparam_buf, gen_labels);
  54 | 
  55 |     *gen_code_size_ptr = gen_code_size;
  56 | 
  57 | #ifdef DEBUG_DISAS
  58 | 
  59 |     if (loglevel & CPU_LOG_TB_OUT_ASM) {
  60 | 
  61 |         fprintf(logfile, "OUT: [size=%d]\n", *gen_code_size_ptr);
  62 | 
  63 |         disas(logfile, tb->tc_ptr, *gen_code_size_ptr);
  64 | 
  65 |         fprintf(logfile, "\n");
  66 | 
  67 |         fflush(logfile);
  68 | 
  69 |     }
  70 | 
  71 | #endif
  72 | 
  73 |     return 0;
  74 | 
  75 | }
```

[Về danh sách ca](#danh-sách-ca)

## CA-07

### Target

```text
   1 | void vp9_idct32x32_34_add_c ( const tran_low_t * input , uint8_t * dest , int stride ) {
   2 |  tran_low_t out [ 32 * 32 ] = {
   3 |  0 }
   4 |  ;
   5 |  tran_low_t * outptr = out ;
   6 |  int i , j ;
   7 |  tran_low_t temp_in [ 32 ] , temp_out [ 32 ] ;
   8 |  for ( i = 0 ;
   9 |  i < 8 ;
  10 |  ++ i ) {
  11 |  idct32 ( input , outptr ) ;
  12 |  input += 32 ;
  13 |  outptr += 32 ;
  14 |  }
  15 |  for ( i = 0 ;
  16 |  i < 32 ;
  17 |  ++ i ) {
  18 |  for ( j = 0 ;
  19 |  j < 32 ;
  20 |  ++ j ) temp_in [ j ] = out [ j * 32 + i ] ;
  21 |  idct32 ( temp_in , temp_out ) ;
  22 |  for ( j = 0 ;
  23 |  j < 32 ;
  24 |  ++ j ) dest [ j * stride + i ] = clip_pixel ( ROUND_POWER_OF_TWO ( temp_out [ j ] , 6 ) + dest [ j * stride + i ] ) ;
  25 |  }
  26 |  }
```

### Demo A

```text
   1 | void vp9_idct32x32_34_add_c ( const int16_t * input , uint8_t * dest , int stride ) {
   2 |  int16_t out [ 32 * 32 ] = {
   3 |  0 }
   4 |  ;
   5 |  int16_t * outptr = out ;
   6 |  int i , j ;
   7 |  int16_t temp_in [ 32 ] , temp_out [ 32 ] ;
   8 |  for ( i = 0 ;
   9 |  i < 8 ;
  10 |  ++ i ) {
  11 |  idct32 ( input , outptr ) ;
  12 |  input += 32 ;
  13 |  outptr += 32 ;
  14 |  }
  15 |  for ( i = 0 ;
  16 |  i < 32 ;
  17 |  ++ i ) {
  18 |  for ( j = 0 ;
  19 |  j < 32 ;
  20 |  ++ j ) temp_in [ j ] = out [ j * 32 + i ] ;
  21 |  idct32 ( temp_in , temp_out ) ;
  22 |  for ( j = 0 ;
  23 |  j < 32 ;
  24 |  ++ j ) dest [ j * stride + i ] = clip_pixel ( ROUND_POWER_OF_TWO ( temp_out [ j ] , 6 ) + dest [ j * stride + i ] ) ;
  25 |  }
  26 |  }
```

### Demo B

```text
   1 | EVP_PKEY * d2i_PUBKEY_fp ( FILE * fp , EVP_PKEY * * a ) {
   2 |  return ASN1_d2i_fp_of ( EVP_PKEY , EVP_PKEY_new , d2i_PUBKEY , fp , a ) ;
   3 |  }
```

[Về danh sách ca](#danh-sách-ca)

## CA-08

### Target

```text
   1 | static void intel_hda_mmio_writeb(void *opaque, target_phys_addr_t addr, uint32_t val)
   2 | 
   3 | {
   4 | 
   5 |     IntelHDAState *d = opaque;
   6 | 
   7 |     const IntelHDAReg *reg = intel_hda_reg_find(d, addr);
   8 | 
   9 | 
  10 | 
  11 |     intel_hda_reg_write(d, reg, val, 0xff);
  12 | 
  13 | }
```

### Demo A

```text
   1 | static void intel_hda_mmio_writew(void *opaque, target_phys_addr_t addr, uint32_t val)
   2 | 
   3 | {
   4 | 
   5 |     IntelHDAState *d = opaque;
   6 | 
   7 |     const IntelHDAReg *reg = intel_hda_reg_find(d, addr);
   8 | 
   9 | 
  10 | 
  11 |     intel_hda_reg_write(d, reg, val, 0xffff);
  12 | 
  13 | }
```

### Demo B

```text
   1 | qemu_irq *arm_gic_init(uint32_t base, qemu_irq parent_irq)
   2 | 
   3 | {
   4 | 
   5 |     gic_state *s;
   6 | 
   7 |     qemu_irq *qi;
   8 | 
   9 |     int iomemtype;
  10 | 
  11 | 
  12 | 
  13 |     s = (gic_state *)qemu_mallocz(sizeof(gic_state));
  14 | 
  15 |     if (!s)
  16 | 
  17 |         return NULL;
  18 | 
  19 |     qi = qemu_allocate_irqs(gic_set_irq, s, GIC_NIRQ);
  20 | 
  21 |     s->parent_irq = parent_irq;
  22 | 
  23 |     if (base != 0xffffffff) {
  24 | 
  25 |         iomemtype = cpu_register_io_memory(0, gic_cpu_readfn,
  26 | 
  27 |                                            gic_cpu_writefn, s);
  28 | 
  29 |         cpu_register_physical_memory(base, 0x00000fff, iomemtype);
  30 | 
  31 |         iomemtype = cpu_register_io_memory(0, gic_dist_readfn,
  32 | 
  33 |                                            gic_dist_writefn, s);
  34 | 
  35 |         cpu_register_physical_memory(base + 0x1000, 0x00000fff, iomemtype);
  36 | 
  37 |         s->base = base;
  38 | 
  39 |     } else {
  40 | 
  41 |         s->base = 0;
  42 | 
  43 |     }
  44 | 
  45 |     gic_reset(s);
  46 | 
  47 |     return qi;
  48 | 
  49 | }
```

[Về danh sách ca](#danh-sách-ca)

## CA-09

### Target

```text
   1 | static void option_date_format ( const char * fmt ) {
   2 |  if ( ! strcmp ( fmt , "raw" ) ) whenspec = WHENSPEC_RAW ;
   3 |  else if ( ! strcmp ( fmt , "rfc2822" ) ) whenspec = WHENSPEC_RFC2822 ;
   4 |  else if ( ! strcmp ( fmt , "now" ) ) whenspec = WHENSPEC_NOW ;
   5 |  else die ( "unknown --date-format argument %s" , fmt ) ;
   6 |  }
```

### Demo A

```text
   1 | static gchar get_priority ( const guint8 * priority ) {
   2 |  static gchar priorities [ ] = "??VDIWEFS" ;
   3 |  if ( * priority >= ( guint8 ) sizeof ( priorities ) ) return '?' ;
   4 |  return priorities [ ( int ) * priority ] ;
   5 |  }
```

### Demo B

```text
   1 | static const char * cmd_cookie_format ( cmd_parms * cmd , void * _dcfg , const char * p1 ) {
   2 |  directory_config * dcfg = ( directory_config * ) _dcfg ;
   3 |  if ( strcmp ( p1 , "0" ) == 0 ) dcfg -> cookie_format = COOKIES_V0 ;
   4 |  else if ( strcmp ( p1 , "1" ) == 0 ) dcfg -> cookie_format = COOKIES_V1 ;
   5 |  else {
   6 |  return apr_psprintf ( cmd -> pool , "ModSecurity: Invalid cookie format: %s" , p1 ) ;
   7 |  }
   8 |  return NULL ;
   9 |  }
```

[Về danh sách ca](#danh-sách-ca)

## CA-10

### Target

```text
   1 | void ppc_translate_init(void)
   2 | 
   3 | {
   4 | 
   5 |     int i;
   6 | 
   7 |     char* p;
   8 | 
   9 |     size_t cpu_reg_names_size;
  10 | 
  11 |     static int done_init = 0;
  12 | 
  13 | 
  14 | 
  15 |     if (done_init)
  16 | 
  17 |         return;
  18 | 
  19 | 
  20 | 
  21 |     cpu_env = tcg_global_reg_new_ptr(TCG_AREG0, "env");
  22 | 
  23 | 
  24 | 
  25 |     p = cpu_reg_names;
  26 | 
  27 |     cpu_reg_names_size = sizeof(cpu_reg_names);
  28 | 
  29 | 
  30 | 
  31 |     for (i = 0; i < 8; i++) {
  32 | 
  33 |         snprintf(p, cpu_reg_names_size, "crf%d", i);
  34 | 
  35 |         cpu_crf[i] = tcg_global_mem_new_i32(TCG_AREG0,
  36 | 
  37 |                                             offsetof(CPUState, crf[i]), p);
  38 | 
  39 |         p += 5;
  40 | 
  41 |         cpu_reg_names_size -= 5;
  42 | 
  43 |     }
  44 | 
  45 | 
  46 | 
  47 |     for (i = 0; i < 32; i++) {
  48 | 
  49 |         snprintf(p, cpu_reg_names_size, "r%d", i);
  50 | 
  51 |         cpu_gpr[i] = tcg_global_mem_new(TCG_AREG0,
  52 | 
  53 |                                         offsetof(CPUState, gpr[i]), p);
  54 | 
  55 |         p += (i < 10) ? 3 : 4;
  56 | 
  57 |         cpu_reg_names_size -= (i < 10) ? 3 : 4;
  58 | 
  59 | #if !defined(TARGET_PPC64)
  60 | 
  61 |         snprintf(p, cpu_reg_names_size, "r%dH", i);
  62 | 
  63 |         cpu_gprh[i] = tcg_global_mem_new_i32(TCG_AREG0,
  64 | 
  65 |                                              offsetof(CPUState, gprh[i]), p);
  66 | 
  67 |         p += (i < 10) ? 4 : 5;
  68 | 
  69 |         cpu_reg_names_size -= (i < 10) ? 4 : 5;
  70 | 
  71 | #endif
  72 | 
  73 | 
  74 | 
  75 |         snprintf(p, cpu_reg_names_size, "fp%d", i);
  76 | 
  77 |         cpu_fpr[i] = tcg_global_mem_new_i64(TCG_AREG0,
  78 | 
  79 |                                             offsetof(CPUState, fpr[i]), p);
  80 | 
  81 |         p += (i < 10) ? 4 : 5;
  82 | 
  83 |         cpu_reg_names_size -= (i < 10) ? 4 : 5;
  84 | 
  85 | 
  86 | 
  87 |         snprintf(p, cpu_reg_names_size, "avr%dH", i);
  88 | 
  89 | #ifdef HOST_WORDS_BIGENDIAN
  90 | 
  91 |         cpu_avrh[i] = tcg_global_mem_new_i64(TCG_AREG0,
  92 | 
  93 |                                              offsetof(CPUState, avr[i].u64[0]), p);
  94 | 
  95 | #else
  96 | 
  97 |         cpu_avrh[i] = tcg_global_mem_new_i64(TCG_AREG0,
  98 | 
  99 |                                              offsetof(CPUState, avr[i].u64[1]), p);
 100 | 
 101 | #endif
 102 | 
 103 |         p += (i < 10) ? 6 : 7;
 104 | 
 105 |         cpu_reg_names_size -= (i < 10) ? 6 : 7;
 106 | 
 107 | 
 108 | 
 109 |         snprintf(p, cpu_reg_names_size, "avr%dL", i);
 110 | 
 111 | #ifdef HOST_WORDS_BIGENDIAN
 112 | 
 113 |         cpu_avrl[i] = tcg_global_mem_new_i64(TCG_AREG0,
 114 | 
 115 |                                              offsetof(CPUState, avr[i].u64[1]), p);
 116 | 
 117 | #else
 118 | 
 119 |         cpu_avrl[i] = tcg_global_mem_new_i64(TCG_AREG0,
 120 | 
 121 |                                              offsetof(CPUState, avr[i].u64[0]), p);
 122 | 
 123 | #endif
 124 | 
 125 |         p += (i < 10) ? 6 : 7;
 126 | 
 127 |         cpu_reg_names_size -= (i < 10) ? 6 : 7;
 128 | 
 129 |     }
 130 | 
 131 | 
 132 | 
 133 |     cpu_nip = tcg_global_mem_new(TCG_AREG0,
 134 | 
 135 |                                  offsetof(CPUState, nip), "nip");
 136 | 
 137 | 
 138 | 
 139 |     cpu_msr = tcg_global_mem_new(TCG_AREG0,
 140 | 
 141 |                                  offsetof(CPUState, msr), "msr");
 142 | 
 143 | 
 144 | 
 145 |     cpu_ctr = tcg_global_mem_new(TCG_AREG0,
 146 | 
 147 |                                  offsetof(CPUState, ctr), "ctr");
 148 | 
 149 | 
 150 | 
 151 |     cpu_lr = tcg_global_mem_new(TCG_AREG0,
 152 | 
 153 |                                 offsetof(CPUState, lr), "lr");
 154 | 
 155 | 
 156 | 
 157 |     cpu_xer = tcg_global_mem_new(TCG_AREG0,
 158 | 
 159 |                                  offsetof(CPUState, xer), "xer");
 160 | 
 161 | 
 162 | 
 163 |     cpu_reserve = tcg_global_mem_new(TCG_AREG0,
 164 | 
 165 |                                      offsetof(CPUState, reserve), "reserve");
 166 | 
 167 | 
 168 | 
 169 |     cpu_fpscr = tcg_global_mem_new_i32(TCG_AREG0,
 170 | 
 171 |                                        offsetof(CPUState, fpscr), "fpscr");
 172 | 
 173 | 
 174 | 
 175 |     cpu_access_type = tcg_global_mem_new_i32(TCG_AREG0,
 176 | 
 177 |                                              offsetof(CPUState, access_type), "access_type");
 178 | 
 179 | 
 180 | 
 181 |     /* register helpers */
 182 | 
 183 | #define GEN_HELPER 2
 184 | 
 185 | #include "helper.h"
 186 | 
 187 | 
 188 | 
 189 |     done_init = 1;
 190 | 
 191 | }
```

### Demo A

```text
   1 | static int mov_write_hdlr_tag(AVIOContext *pb, MOVTrack *track)
   2 | 
   3 | {
   4 | 
   5 |     const char *hdlr, *descr = NULL, *hdlr_type = NULL;
   6 | 
   7 |     int64_t pos = avio_tell(pb);
   8 | 
   9 | 
  10 | 
  11 |     if (!track) { /* no media --> data handler */
  12 | 
  13 | 
  14 | 
  15 | 
  16 | 
  17 |         hdlr = (track->mode == MODE_MOV) ? "mhlr" : "\0\0\0\0";
  18 | 
  19 |         if (track->enc->codec_type == AVMEDIA_TYPE_VIDEO) {
  20 | 
  21 |             hdlr_type = "vide";
  22 | 
  23 |             descr = "VideoHandler";
  24 | 
  25 |         } else if (track->enc->codec_type == AVMEDIA_TYPE_AUDIO) {
  26 | 
  27 |             hdlr_type = "soun";
  28 | 
  29 |             descr = "SoundHandler";
  30 | 
  31 |         } else if (track->enc->codec_type == AVMEDIA_TYPE_SUBTITLE) {
  32 | 
  33 |             if (track->tag == MKTAG('t','x','3','g')) hdlr_type = "sbtl";
  34 | 
  35 |             else                                      hdlr_type = "text";
  36 | 
  37 |             descr = "SubtitleHandler";
  38 | 
  39 |         } else if (track->enc->codec_tag == MKTAG('r','t','p',' ')) {
  40 | 
  41 |             hdlr_type = "hint";
  42 | 
  43 |             descr = "HintHandler";
  44 | 
  45 | 
  46 | 
  47 | 
  48 | 
  49 |         }
  50 | 
  51 |     }
  52 | 
  53 | 
  54 | 
  55 |     avio_wb32(pb, 0); /* size */
  56 | 
  57 |     ffio_wfourcc(pb, "hdlr");
  58 | 
  59 |     avio_wb32(pb, 0); /* Version & flags */
  60 | 
  61 |     avio_write(pb, hdlr, 4); /* handler */
  62 | 
  63 |     ffio_wfourcc(pb, hdlr_type); /* handler type */
  64 | 
  65 |     avio_wb32(pb ,0); /* reserved */
  66 | 
  67 |     avio_wb32(pb ,0); /* reserved */
  68 | 
  69 |     avio_wb32(pb ,0); /* reserved */
  70 | 
  71 |     if (!track || track->mode == MODE_MOV)
  72 | 
  73 |         avio_w8(pb, strlen(descr)); /* pascal string */
  74 | 
  75 |     avio_write(pb, descr, strlen(descr)); /* handler description */
  76 | 
  77 |     if (track && track->mode != MODE_MOV)
  78 | 
  79 |         avio_w8(pb, 0); /* c string */
  80 | 
  81 |     return update_size(pb, pos);
  82 | 
  83 | }
```

### Demo B

```text
   1 | void ppc_translate_init(void)
   2 | {
   3 |     int i;
   4 |     char* p;
   5 |     size_t cpu_reg_names_size;
   6 |     static int done_init = 0;
   7 |     if (done_init)
   8 |         return;
   9 |     cpu_env = tcg_global_reg_new_ptr(TCG_AREG0, "env");
  10 |     p = cpu_reg_names;
  11 |     cpu_reg_names_size = sizeof(cpu_reg_names);
  12 |     for (i = 0; i < 8; i++) {
  13 |         snprintf(p, cpu_reg_names_size, "crf%d", i);
  14 |         cpu_crf[i] = tcg_global_mem_new_i32(TCG_AREG0,
  15 |                                             offsetof(CPUState, crf[i]), p);
  16 |         p += 5;
  17 |         cpu_reg_names_size -= 5;
  18 |     }
  19 |     for (i = 0; i < 32; i++) {
  20 |         snprintf(p, cpu_reg_names_size, "r%d", i);
  21 |         cpu_gpr[i] = tcg_global_mem_new(TCG_AREG0,
  22 |                                         offsetof(CPUState, gpr[i]), p);
  23 |         p += (i < 10) ? 3 : 4;
  24 |         cpu_reg_names_size -= (i < 10) ? 3 : 4;
  25 | #if !defined(TARGET_PPC64)
  26 |         snprintf(p, cpu_reg_names_size, "r%dH", i);
  27 |         cpu_gprh[i] = tcg_global_mem_new_i32(TCG_AREG0,
  28 |                                              offsetof(CPUState, gprh[i]), p);
  29 |         p += (i < 10) ? 4 : 5;
  30 |         cpu_reg_names_size -= (i < 10) ? 4 : 5;
  31 |         snprintf(p, cpu_reg_names_size, "fp%d", i);
  32 |         cpu_fpr[i] = tcg_global_mem_new_i64(TCG_AREG0,
  33 |                                             offsetof(CPUState, fpr[i]), p);
  34 |         p += (i < 10) ? 4 : 5;
  35 |         cpu_reg_names_size -= (i < 10) ? 4 : 5;
  36 |         snprintf(p, cpu_reg_names_size, "avr%dH", i);
  37 | #ifdef HOST_WORDS_BIGENDIAN
  38 |         cpu_avrh[i] = tcg_global_mem_new_i64(TCG_AREG0,
  39 |                                              offsetof(CPUState, avr[i].u64[0]), p);
  40 | #else
  41 |         cpu_avrh[i] = tcg_global_mem_new_i64(TCG_AREG0,
  42 |                                              offsetof(CPUState, avr[i].u64[1]), p);
  43 |         p += (i < 10) ? 6 : 7;
  44 |         cpu_reg_names_size -= (i < 10) ? 6 : 7;
  45 |         snprintf(p, cpu_reg_names_size, "avr%dL", i);
  46 | #ifdef HOST_WORDS_BIGENDIAN
  47 |         cpu_avrl[i] = tcg_global_mem_new_i64(TCG_AREG0,
  48 |                                              offsetof(CPUState, avr[i].u64[1]), p);
  49 | #else
  50 |         cpu_avrl[i] = tcg_global_mem_new_i64(TCG_AREG0,
  51 |                                              offsetof(CPUState, avr[i].u64[0]), p);
  52 |         p += (i < 10) ? 6 : 7;
  53 |         cpu_reg_names_size -= (i < 10) ? 6 : 7;
  54 |     }
  55 |     cpu_nip = tcg_global_mem_new(TCG_AREG0,
  56 |                                  offsetof(CPUState, nip), "nip");
  57 |     cpu_msr = tcg_global_mem_new(TCG_AREG0,
  58 |                                  offsetof(CPUState, msr), "msr");
  59 |     cpu_ctr = tcg_global_mem_new(TCG_AREG0,
  60 |                                  offsetof(CPUState, ctr), "ctr");
  61 |     cpu_lr = tcg_global_mem_new(TCG_AREG0,
  62 |                                 offsetof(CPUState, lr), "lr");
  63 |     cpu_xer = tcg_global_mem_new(TCG_AREG0,
  64 |                                  offsetof(CPUState, xer), "xer");
  65 |     cpu_reserve = tcg_global_mem_new(TCG_AREG0,
  66 |                                      offsetof(CPUState, reserve_addr),
  67 |                                      "reserve_addr");
  68 |     cpu_fpscr = tcg_global_mem_new_i32(TCG_AREG0,
  69 |                                        offsetof(CPUState, fpscr), "fpscr");
  70 |     cpu_access_type = tcg_global_mem_new_i32(TCG_AREG0,
  71 |                                              offsetof(CPUState, access_type), "access_type");
  72 |     /* register helpers */
  73 | #define GEN_HELPER 2
  74 | #include "helper.h"
  75 |     done_init = 1;
  76 | }
```

[Về danh sách ca](#danh-sách-ca)

## CA-11

### Target

```text
   1 | static int dprintf_formatf ( void * data , int ( * stream ) ( int , FILE * ) , const char * format , va_list ap_save ) {
   2 |  const char * digits = lower_digits ;
   3 |  char * f ;
   4 |  int done = 0 ;
   5 |  long param ;
   6 |  long param_num = 0 ;
   7 |  va_stack_t vto [ MAX_PARAMETERS ] ;
   8 |  char * endpos [ MAX_PARAMETERS ] ;
   9 |  char * * end ;
  10 |  char work [ BUFFSIZE ] ;
  11 |  va_stack_t * p ;
  12 |  char * workend = & work [ sizeof ( work ) - 2 ] ;
  13 |  if ( dprintf_Pass1 ( format , vto , endpos , ap_save ) ) return - 1 ;
  14 |  end = & endpos [ 0 ] ;
  15 |  f = ( char * ) format ;
  16 |  while ( * f != '\0' ) {
  17 |  int is_alt ;
  18 |  long width ;
  19 |  long prec ;
  20 |  int is_neg ;
  21 |  long base ;
  22 |  mp_uintmax_t num ;
  23 |  mp_intmax_t signed_num ;
  24 |  char * w ;
  25 |  if ( * f != '%' ) {
  26 |  do {
  27 |  OUTCHAR ( * f ) ;
  28 |  }
  29 |  while ( * ++ f && ( '%' != * f ) ) ;
  30 |  continue ;
  31 |  }
  32 |  ++ f ;
  33 |  if ( * f == '%' ) {
  34 |  ++ f ;
  35 |  OUTCHAR ( '%' ) ;
  36 |  continue ;
  37 |  }
  38 |  param = dprintf_DollarString ( f , & f ) ;
  39 |  if ( ! param ) param = param_num ;
  40 |  else -- param ;
  41 |  param_num ++ ;
  42 |  p = & vto [ param ] ;
  43 |  if ( p -> flags & FLAGS_WIDTHPARAM ) {
  44 |  width = ( long ) vto [ p -> width ] . data . num . as_signed ;
  45 |  param_num ++ ;
  46 |  if ( width < 0 ) {
  47 |  width = - width ;
  48 |  p -> flags |= FLAGS_LEFT ;
  49 |  p -> flags &= ~ FLAGS_PAD_NIL ;
  50 |  }
  51 |  }
  52 |  else width = p -> width ;
  53 |  if ( p -> flags & FLAGS_PRECPARAM ) {
  54 |  prec = ( long ) vto [ p -> precision ] . data . num . as_signed ;
  55 |  param_num ++ ;
  56 |  if ( prec < 0 ) prec = - 1 ;
  57 |  }
  58 |  else if ( p -> flags & FLAGS_PREC ) prec = p -> precision ;
  59 |  else prec = - 1 ;
  60 |  is_alt = ( p -> flags & FLAGS_ALT ) ? 1 : 0 ;
  61 |  switch ( p -> type ) {
  62 |  case FORMAT_INT : num = p -> data . num . as_unsigned ;
  63 |  if ( p -> flags & FLAGS_CHAR ) {
  64 |  if ( ! ( p -> flags & FLAGS_LEFT ) ) while ( -- width > 0 ) OUTCHAR ( ' ' ) ;
  65 |  OUTCHAR ( ( char ) num ) ;
  66 |  if ( p -> flags & FLAGS_LEFT ) while ( -- width > 0 ) OUTCHAR ( ' ' ) ;
  67 |  break ;
  68 |  }
  69 |  if ( p -> flags & FLAGS_OCTAL ) {
  70 |  base = 8 ;
  71 |  goto unsigned_number ;
  72 |  }
  73 |  else if ( p -> flags & FLAGS_HEX ) {
  74 |  digits = ( p -> flags & FLAGS_UPPER ) ? upper_digits : lower_digits ;
  75 |  base = 16 ;
  76 |  goto unsigned_number ;
  77 |  }
  78 |  else if ( p -> flags & FLAGS_UNSIGNED ) {
  79 |  base = 10 ;
  80 |  goto unsigned_number ;
  81 |  }
  82 |  base = 10 ;
  83 |  is_neg = ( p -> data . num . as_signed < ( mp_intmax_t ) 0 ) ? 1 : 0 ;
  84 |  if ( is_neg ) {
  85 |  signed_num = p -> data . num . as_signed + ( mp_intmax_t ) 1 ;
  86 |  signed_num = - signed_num ;
  87 |  num = ( mp_uintmax_t ) signed_num ;
  88 |  num += ( mp_uintmax_t ) 1 ;
  89 |  }
  90 |  goto number ;
  91 |  unsigned_number : is_neg = 0 ;
  92 |  number : if ( prec == - 1 ) prec = 1 ;
  93 |  w = workend ;
  94 |  while ( num > 0 ) {
  95 |  * w -- = digits [ num % base ] ;
  96 |  num /= base ;
  97 |  }
  98 |  width -= ( long ) ( workend - w ) ;
  99 |  prec -= ( long ) ( workend - w ) ;
 100 |  if ( is_alt && base == 8 && prec <= 0 ) {
 101 |  * w -- = '0' ;
 102 |  -- width ;
 103 |  }
 104 |  if ( prec > 0 ) {
 105 |  width -= prec ;
 106 |  while ( prec -- > 0 ) * w -- = '0' ;
 107 |  }
 108 |  if ( is_alt && base == 16 ) width -= 2 ;
 109 |  if ( is_neg || ( p -> flags & FLAGS_SHOWSIGN ) || ( p -> flags & FLAGS_SPACE ) ) -- width ;
 110 |  if ( ! ( p -> flags & FLAGS_LEFT ) && ! ( p -> flags & FLAGS_PAD_NIL ) ) while ( width -- > 0 ) OUTCHAR ( ' ' ) ;
 111 |  if ( is_neg ) OUTCHAR ( '-' ) ;
 112 |  else if ( p -> flags & FLAGS_SHOWSIGN ) OUTCHAR ( '+' ) ;
 113 |  else if ( p -> flags & FLAGS_SPACE ) OUTCHAR ( ' ' ) ;
 114 |  if ( is_alt && base == 16 ) {
 115 |  OUTCHAR ( '0' ) ;
 116 |  if ( p -> flags & FLAGS_UPPER ) OUTCHAR ( 'X' ) ;
 117 |  else OUTCHAR ( 'x' ) ;
 118 |  }
 119 |  if ( ! ( p -> flags & FLAGS_LEFT ) && ( p -> flags & FLAGS_PAD_NIL ) ) while ( width -- > 0 ) OUTCHAR ( '0' ) ;
 120 |  while ( ++ w <= workend ) {
 121 |  OUTCHAR ( * w ) ;
 122 |  }
 123 |  if ( p -> flags & FLAGS_LEFT ) while ( width -- > 0 ) OUTCHAR ( ' ' ) ;
 124 |  break ;
 125 |  case FORMAT_STRING : {
 126 |  static const char null [ ] = "(nil)" ;
 127 |  const char * str ;
 128 |  size_t len ;
 129 |  str = ( char * ) p -> data . str ;
 130 |  if ( str == NULL ) {
 131 |  if ( prec == - 1 || prec >= ( long ) sizeof ( null ) - 1 ) {
 132 |  str = null ;
 133 |  len = sizeof ( null ) - 1 ;
 134 |  p -> flags &= ( ~ FLAGS_ALT ) ;
 135 |  }
 136 |  else {
 137 |  str = "" ;
 138 |  len = 0 ;
 139 |  }
 140 |  }
 141 |  else if ( prec != - 1 ) len = ( size_t ) prec ;
 142 |  else len = strlen ( str ) ;
 143 |  width -= ( len > LONG_MAX ) ? LONG_MAX : ( long ) len ;
 144 |  if ( p -> flags & FLAGS_ALT ) OUTCHAR ( '"' ) ;
 145 |  if ( ! ( p -> flags & FLAGS_LEFT ) ) while ( width -- > 0 ) OUTCHAR ( ' ' ) ;
 146 |  while ( ( len -- > 0 ) && * str ) OUTCHAR ( * str ++ ) ;
 147 |  if ( p -> flags & FLAGS_LEFT ) while ( width -- > 0 ) OUTCHAR ( ' ' ) ;
 148 |  if ( p -> flags & FLAGS_ALT ) OUTCHAR ( '"' ) ;
 149 |  }
 150 |  break ;
 151 |  case FORMAT_PTR : {
 152 |  void * ptr ;
 153 |  ptr = ( void * ) p -> data . ptr ;
 154 |  if ( ptr != NULL ) {
 155 |  base = 16 ;
 156 |  digits = ( p -> flags & FLAGS_UPPER ) ? upper_digits : lower_digits ;
 157 |  is_alt = 1 ;
 158 |  num = ( size_t ) ptr ;
 159 |  is_neg = 0 ;
 160 |  goto number ;
 161 |  }
 162 |  else {
 163 |  static const char strnil [ ] = "(nil)" ;
 164 |  const char * point ;
 165 |  width -= ( long ) ( sizeof ( strnil ) - 1 ) ;
 166 |  if ( p -> flags & FLAGS_LEFT ) while ( width -- > 0 ) OUTCHAR ( ' ' ) ;
 167 |  for ( point = strnil ;
 168 |  * point != '\0' ;
 169 |  ++ point ) OUTCHAR ( * point ) ;
 170 |  if ( ! ( p -> flags & FLAGS_LEFT ) ) while ( width -- > 0 ) OUTCHAR ( ' ' ) ;
 171 |  }
 172 |  }
 173 |  break ;
 174 |  case FORMAT_DOUBLE : {
 175 |  char formatbuf [ 32 ] = "%" ;
 176 |  char * fptr = & formatbuf [ 1 ] ;
 177 |  size_t left = sizeof ( formatbuf ) - strlen ( formatbuf ) ;
 178 |  int len ;
 179 |  width = - 1 ;
 180 |  if ( p -> flags & FLAGS_WIDTH ) width = p -> width ;
 181 |  else if ( p -> flags & FLAGS_WIDTHPARAM ) width = ( long ) vto [ p -> width ] . data . num . as_signed ;
 182 |  prec = - 1 ;
 183 |  if ( p -> flags & FLAGS_PREC ) prec = p -> precision ;
 184 |  else if ( p -> flags & FLAGS_PRECPARAM ) prec = ( long ) vto [ p -> precision ] . data . num . as_signed ;
 185 |  if ( p -> flags & FLAGS_LEFT ) * fptr ++ = '-' ;
 186 |  if ( p -> flags & FLAGS_SHOWSIGN ) * fptr ++ = '+' ;
 187 |  if ( p -> flags & FLAGS_SPACE ) * fptr ++ = ' ' ;
 188 |  if ( p -> flags & FLAGS_ALT ) * fptr ++ = '#' ;
 189 |  * fptr = 0 ;
 190 |  if ( width >= 0 ) {
 191 |  len = curl_msnprintf ( fptr , left , "%ld" , width ) ;
 192 |  fptr += len ;
 193 |  left -= len ;
 194 |  }
 195 |  if ( prec >= 0 ) {
 196 |  len = curl_msnprintf ( fptr , left , ".%ld" , prec ) ;
 197 |  fptr += len ;
 198 |  }
 199 |  if ( p -> flags & FLAGS_LONG ) * fptr ++ = 'l' ;
 200 |  if ( p -> flags & FLAGS_FLOATE ) * fptr ++ = ( char ) ( ( p -> flags & FLAGS_UPPER ) ? 'E' : 'e' ) ;
 201 |  else if ( p -> flags & FLAGS_FLOATG ) * fptr ++ = ( char ) ( ( p -> flags & FLAGS_UPPER ) ? 'G' : 'g' ) ;
 202 |  else * fptr ++ = 'f' ;
 203 |  * fptr = 0 ;
 204 |  ( sprintf ) ( work , formatbuf , p -> data . dnum ) ;
 205 |  for ( fptr = work ;
 206 |  * fptr ;
 207 |  fptr ++ ) OUTCHAR ( * fptr ) ;
 208 |  }
 209 |  break ;
 210 |  case FORMAT_INTPTR : # ifdef HAVE_LONG_LONG_TYPE if ( p -> flags & FLAGS_LONGLONG ) * ( LONG_LONG_TYPE * ) p -> data . ptr = ( LONG_LONG_TYPE ) done ;
 211 |  else # endif if ( p -> flags & FLAGS_LONG ) * ( long * ) p -> data . ptr = ( long ) done ;
 212 |  else if ( ! ( p -> flags & FLAGS_SHORT ) ) * ( int * ) p -> data . ptr = ( int ) done ;
 213 |  else * ( short * ) p -> data . ptr = ( short ) done ;
 214 |  break ;
 215 |  default : break ;
 216 |  }
 217 |  f = * end ++ ;
 218 |  }
 219 |  return done ;
 220 |  }
```

### Demo A

```text
   1 | libc_hidden_proto ( __printf_fp ) extern unsigned int __guess_grouping ( unsigned int intdig_max , const char * grouping , wchar_t sepchar ) ;
   2 |  ssize_t __vstrfmon_l ( char * s , size_t maxsize , __locale_t loc , const char * format , va_list ap ) {
   3 |  struct locale_data * current = loc -> __locales [ LC_MONETARY ] ;
   4 |  _IO_strfile f ;
   5 |  # ifdef _IO_MTSAFE_IO _IO_lock_t lock ;
   6 |  # endif struct printf_info info ;
   7 |  char * dest ;
   8 |  const char * fmt ;
   9 |  dest = s ;
  10 |  fmt = format ;
  11 |  while ( * fmt != '\0' ) {
  12 |  union {
  13 |  double dbl ;
  14 |  __long_double_t ldbl ;
  15 |  }
  16 |  fpnum ;
  17 |  int int_format ;
  18 |  int print_curr_symbol ;
  19 |  int left_prec ;
  20 |  int left_pad ;
  21 |  int right_prec ;
  22 |  int group ;
  23 |  char pad ;
  24 |  int is_long_double ;
  25 |  int p_sign_posn ;
  26 |  int n_sign_posn ;
  27 |  int sign_posn ;
  28 |  int other_sign_posn ;
  29 |  int left ;
  30 |  int is_negative ;
  31 |  int sep_by_space ;
  32 |  int other_sep_by_space ;
  33 |  int cs_precedes ;
  34 |  int other_cs_precedes ;
  35 |  const char * sign_string ;
  36 |  const char * other_sign_string ;
  37 |  int done ;
  38 |  const char * currency_symbol ;
  39 |  size_t currency_symbol_len ;
  40 |  long int width ;
  41 |  char * startp ;
  42 |  const void * ptr ;
  43 |  char space_char ;
  44 |  if ( * fmt != '%' ) {
  45 |  out_char ( * fmt ++ ) ;
  46 |  continue ;
  47 |  }
  48 |  if ( fmt [ 1 ] == '%' ) {
  49 |  out_char ( * ++ fmt ) ;
  50 |  ++ fmt ;
  51 |  continue ;
  52 |  }
  53 |  int_format = 0 ;
  54 |  print_curr_symbol = 1 ;
  55 |  left_prec = - 1 ;
  56 |  right_prec = - 1 ;
  57 |  group = 1 ;
  58 |  pad = ' ' ;
  59 |  is_long_double = 0 ;
  60 |  p_sign_posn = - 1 ;
  61 |  n_sign_posn = - 1 ;
  62 |  width = - 1 ;
  63 |  left = 0 ;
  64 |  while ( 1 ) {
  65 |  switch ( * ++ fmt ) {
  66 |  case '=' : pad = * ++ fmt ;
  67 |  if ( pad == '\0' ) {
  68 |  __set_errno ( EINVAL ) ;
  69 |  return - 1 ;
  70 |  }
  71 |  continue ;
  72 |  case '^' : group = 0 ;
  73 |  continue ;
  74 |  case '+' : if ( n_sign_posn != - 1 ) {
  75 |  __set_errno ( EINVAL ) ;
  76 |  return - 1 ;
  77 |  }
  78 |  p_sign_posn = * _NL_CURRENT ( LC_MONETARY , P_SIGN_POSN ) ;
  79 |  n_sign_posn = * _NL_CURRENT ( LC_MONETARY , N_SIGN_POSN ) ;
  80 |  continue ;
  81 |  case '(' : if ( n_sign_posn != - 1 ) {
  82 |  __set_errno ( EINVAL ) ;
  83 |  return - 1 ;
  84 |  }
  85 |  p_sign_posn = 0 ;
  86 |  n_sign_posn = 0 ;
  87 |  continue ;
  88 |  case '!' : print_curr_symbol = 0 ;
  89 |  continue ;
  90 |  case '-' : left = 1 ;
  91 |  continue ;
  92 |  default : ;
  93 |  }
  94 |  break ;
  95 |  }
  96 |  if ( isdigit ( * fmt ) ) {
  97 |  width = to_digit ( * fmt ) ;
  98 |  while ( isdigit ( * ++ fmt ) ) {
  99 |  int val = to_digit ( * fmt ) ;
 100 |  if ( width > LONG_MAX / 10 || ( width == LONG_MAX && val > LONG_MAX % 10 ) ) {
 101 |  __set_errno ( E2BIG ) ;
 102 |  return - 1 ;
 103 |  }
 104 |  width = width * 10 + val ;
 105 |  }
 106 |  if ( width >= maxsize - ( dest - s ) ) {
 107 |  __set_errno ( E2BIG ) ;
 108 |  return - 1 ;
 109 |  }
 110 |  }
 111 |  if ( * fmt == '#' ) {
 112 |  if ( ! isdigit ( * ++ fmt ) ) {
 113 |  __set_errno ( EINVAL ) ;
 114 |  return - 1 ;
 115 |  }
 116 |  left_prec = to_digit ( * fmt ) ;
 117 |  while ( isdigit ( * ++ fmt ) ) {
 118 |  left_prec *= 10 ;
 119 |  left_prec += to_digit ( * fmt ) ;
 120 |  }
 121 |  }
 122 |  if ( * fmt == '.' ) {
 123 |  if ( ! isdigit ( * ++ fmt ) ) {
 124 |  __set_errno ( EINVAL ) ;
 125 |  return - 1 ;
 126 |  }
 127 |  right_prec = to_digit ( * fmt ) ;
 128 |  while ( isdigit ( * ++ fmt ) ) {
 129 |  right_prec *= 10 ;
 130 |  right_prec += to_digit ( * fmt ) ;
 131 |  }
 132 |  }
 133 |  if ( * fmt == 'L' ) {
 134 |  ++ fmt ;
 135 |  if ( ! __ldbl_is_dbl ) is_long_double = 1 ;
 136 |  }
 137 |  char int_symbol [ 4 ] ;
 138 |  switch ( * fmt ++ ) {
 139 |  case 'i' : {
 140 |  const char * int_curr_symbol ;
 141 |  int_curr_symbol = _NL_CURRENT ( LC_MONETARY , INT_CURR_SYMBOL ) ;
 142 |  strncpy ( int_symbol , int_curr_symbol , 3 ) ;
 143 |  int_symbol [ 3 ] = '\0' ;
 144 |  currency_symbol_len = 3 ;
 145 |  currency_symbol = & int_symbol [ 0 ] ;
 146 |  space_char = int_curr_symbol [ 3 ] ;
 147 |  int_format = 1 ;
 148 |  break ;
 149 |  }
 150 |  case 'n' : currency_symbol = _NL_CURRENT ( LC_MONETARY , CURRENCY_SYMBOL ) ;
 151 |  currency_symbol_len = strlen ( currency_symbol ) ;
 152 |  space_char = ' ' ;
 153 |  int_format = 0 ;
 154 |  break ;
 155 |  default : __set_errno ( EINVAL ) ;
 156 |  return - 1 ;
 157 |  }
 158 |  if ( p_sign_posn == - 1 ) p_sign_posn = * _NL_CURRENT ( LC_MONETARY , int_format ? INT_P_SIGN_POSN : P_SIGN_POSN ) ;
 159 |  if ( n_sign_posn == - 1 ) n_sign_posn = * _NL_CURRENT ( LC_MONETARY , int_format ? INT_N_SIGN_POSN : N_SIGN_POSN ) ;
 160 |  if ( right_prec == - 1 ) {
 161 |  right_prec = * _NL_CURRENT ( LC_MONETARY , int_format ? INT_FRAC_DIGITS : FRAC_DIGITS ) ;
 162 |  if ( right_prec == CHAR_MAX ) right_prec = 2 ;
 163 |  }
 164 |  if ( group && left_prec != - 1 ) left_prec += __guess_grouping ( left_prec , _NL_CURRENT ( LC_MONETARY , MON_GROUPING ) , * _NL_CURRENT ( LC_MONETARY , MON_THOUSANDS_SEP ) ) ;
 165 |  if ( is_long_double == 1 ) {
 166 |  fpnum . ldbl = va_arg ( ap , long double ) ;
 167 |  is_negative = fpnum . ldbl < 0 ;
 168 |  if ( is_negative ) fpnum . ldbl = - fpnum . ldbl ;
 169 |  }
 170 |  else {
 171 |  fpnum . dbl = va_arg ( ap , double ) ;
 172 |  is_negative = fpnum . dbl < 0 ;
 173 |  if ( is_negative ) fpnum . dbl = - fpnum . dbl ;
 174 |  }
 175 |  if ( is_negative ) {
 176 |  sign_string = _NL_CURRENT ( LC_MONETARY , NEGATIVE_SIGN ) ;
 177 |  if ( * sign_string == '\0' ) sign_string = ( const char * ) "-" ;
 178 |  cs_precedes = * _NL_CURRENT ( LC_MONETARY , int_format ? INT_N_CS_PRECEDES : N_CS_PRECEDES ) ;
 179 |  sep_by_space = * _NL_CURRENT ( LC_MONETARY , int_format ? INT_N_SEP_BY_SPACE : N_SEP_BY_SPACE ) ;
 180 |  sign_posn = n_sign_posn ;
 181 |  other_sign_string = _NL_CURRENT ( LC_MONETARY , POSITIVE_SIGN
 182 | /* [TRUNCATED] */
```

### Demo B

```text
   1 | static void sig_complete_word ( GList * * list , WINDOW_REC * window , const char * word , const char * linestart , int * want_space ) {
   2 |  SERVER_REC * server ;
   3 |  CHANNEL_REC * channel ;
   4 |  QUERY_REC * query ;
   5 |  char * prefix ;
   6 |  g_return_if_fail ( list != NULL ) ;
   7 |  g_return_if_fail ( window != NULL ) ;
   8 |  g_return_if_fail ( word != NULL ) ;
   9 |  g_return_if_fail ( linestart != NULL ) ;
  10 |  server = window -> active_server ;
  11 |  if ( server == NULL && servers != NULL ) server = servers -> data ;
  12 |  if ( server != NULL && server_ischannel ( server , word ) ) {
  13 |  * list = completion_get_channels ( window -> active_server , word ) ;
  14 |  if ( * list != NULL ) signal_stop ( ) ;
  15 |  return ;
  16 |  }
  17 |  server = window -> active_server ;
  18 |  if ( server == NULL || ! server -> connected ) return ;
  19 |  if ( * linestart == '\0' && * word == '\0' ) {
  20 |  if ( ! completion_empty_line ) return ;
  21 |  prefix = g_strdup_printf ( "%cmsg" , * cmdchars ) ;
  22 |  * list = completion_msg ( server , NULL , "" , prefix ) ;
  23 |  if ( * list == NULL ) * list = g_list_append ( * list , g_strdup ( prefix ) ) ;
  24 |  g_free ( prefix ) ;
  25 |  signal_stop ( ) ;
  26 |  return ;
  27 |  }
  28 |  channel = CHANNEL ( window -> active ) ;
  29 |  query = QUERY ( window -> active ) ;
  30 |  if ( channel == NULL && query != NULL && g_ascii_strncasecmp ( word , query -> name , strlen ( word ) ) == 0 ) {
  31 |  * list = g_list_append ( * list , g_strdup ( query -> name ) ) ;
  32 |  }
  33 |  else if ( channel != NULL ) {
  34 |  const char * suffix = * linestart != '\0' ? NULL : completion_char ;
  35 |  complete_window_nicks ( list , window , word , suffix ) ;
  36 |  }
  37 |  else if ( window -> level & MSGLEVEL_MSGS ) {
  38 |  * list = g_list_concat ( completion_msg ( server , NULL , word , NULL ) , * list ) ;
  39 |  }
  40 |  if ( * list != NULL ) signal_stop ( ) ;
  41 |  }
```

[Về danh sách ca](#danh-sách-ca)

## CA-12

### Target

```text
   1 | static int output_frame(H264Context *h, AVFrame *dst, AVFrame *src)
   2 | 
   3 | {
   4 | 
   5 |     int i;
   6 | 
   7 |     int ret = av_frame_ref(dst, src);
   8 | 
   9 |     if (ret < 0)
  10 | 
  11 |         return ret;
  12 | 
  13 | 
  14 | 
  15 |     if (!h->sps.crop)
  16 | 
  17 |         return 0;
  18 | 
  19 | 
  20 | 
  21 |     for (i = 0; i < 3; i++) {
  22 | 
  23 |         int hshift = (i > 0) ? h->chroma_x_shift : 0;
  24 | 
  25 |         int vshift = (i > 0) ? h->chroma_y_shift : 0;
  26 | 
  27 |         int off    = ((h->sps.crop_left >> hshift) << h->pixel_shift) +
  28 | 
  29 |             (h->sps.crop_top  >> vshift) * dst->linesize[i];
  30 | 
  31 |         dst->data[i] += off;
  32 | 
  33 |     }
  34 | 
  35 |     return 0;
  36 | 
  37 | }
```

### Demo A

```text
   1 | static float get_band_cost_NONE_mips(struct AACEncContext *s,
   2 | 
   3 |                                      PutBitContext *pb, const float *in,
   4 | 
   5 |                                      const float *scaled, int size, int scale_idx,
   6 | 
   7 |                                      int cb, const float lambda, const float uplim,
   8 | 
   9 |                                      int *bits)
  10 | 
  11 | {
  12 | 
  13 |     av_assert0(0);
  14 | 
  15 |     return 0;
  16 | 
  17 | }
```

### Demo B

```text
   1 | static int output_frame(H264Context *h, AVFrame *dst, Picture *srcp)
   2 | 
   3 | {
   4 | 
   5 |     AVFrame *src = &srcp->f;
   6 | 
   7 |     int i;
   8 | 
   9 |     int ret = av_frame_ref(dst, src);
  10 | 
  11 |     if (ret < 0)
  12 | 
  13 |         return ret;
  14 | 
  15 | 
  16 | 
  17 |     av_dict_set(&dst->metadata, "stereo_mode", ff_h264_sei_stereo_mode(h), 0);
  18 | 
  19 | 
  20 | 
  21 |     if (!srcp->crop)
  22 | 
  23 |         return 0;
  24 | 
  25 | 
  26 | 
  27 |     for (i = 0; i < 3; i++) {
  28 | 
  29 |         int hshift = (i > 0) ? h->chroma_x_shift : 0;
  30 | 
  31 |         int vshift = (i > 0) ? h->chroma_y_shift : 0;
  32 | 
  33 |         int off    = ((srcp->crop_left >> hshift) << h->pixel_shift) +
  34 | 
  35 |                       (srcp->crop_top  >> vshift) * dst->linesize[i];
  36 | 
  37 |         dst->data[i] += off;
  38 | 
  39 |     }
  40 | 
  41 |     return 0;
  42 | 
  43 | }
```

[Về danh sách ca](#danh-sách-ca)

## CA-13

### Target

```text
   1 | uint32_t wm8750_adc_dat(void *opaque)
   2 | 
   3 | {
   4 | 
   5 |     WM8750State *s = (WM8750State *) opaque;
   6 | 
   7 |     uint32_t *data;
   8 | 
   9 | 
  10 | 
  11 |     if (s->idx_in >= sizeof(s->data_in))
  12 | 
  13 |         wm8750_in_load(s);
  14 | 
  15 | 
  16 | 
  17 |     data = (uint32_t *) &s->data_in[s->idx_in];
  18 | 
  19 |     s->req_in -= 4;
  20 | 
  21 |     s->idx_in += 4;
  22 | 
  23 |     return *data;
  24 | 
  25 | }
```

### Demo A

```text
   1 | uint32_t ide_data_readl(void *opaque, uint32_t addr)
   2 | {
   3 |     IDEBus *bus = opaque;
   4 |     IDEState *s = idebus_active_if(bus);
   5 |     uint8_t *p;
   6 |     int ret;
   7 |     /* PIO data access allowed only when DRQ bit is set. The result of a read
   8 |      * during PIO in is indeterminate, return 0 and don't move forward. */
   9 |     if (!(s->status & DRQ_STAT) || !ide_is_pio_out(s)) {
  10 |     p = s->data_ptr;
  11 |     ret = cpu_to_le32(*(uint32_t *)p);
  12 |     p += 4;
  13 |     s->data_ptr = p;
  14 |     if (p >= s->data_end)
  15 |         s->end_transfer_func(s);
  16 |     return ret;
```

### Demo B

```text
   1 | static void enable_device(PIIX4PMState *s, int slot)
   2 | 
   3 | {
   4 | 
   5 |     s->ar.gpe.sts[0] |= PIIX4_PCI_HOTPLUG_STATUS;
   6 | 
   7 |     s->pci0_status.up |= (1 << slot);
   8 | 
   9 | }
```

[Về danh sách ca](#danh-sách-ca)

## CA-14

### Target

```text
   1 | void vp9_fdct16x16_1_c ( const int16_t * input , int16_t * output , int stride ) {
   2 |  int r , c ;
   3 |  int16_t sum = 0 ;
   4 |  for ( r = 0 ;
   5 |  r < 16 ;
   6 |  ++ r ) for ( c = 0 ;
   7 |  c < 16 ;
   8 |  ++ c ) sum += input [ r * stride + c ] ;
   9 |  output [ 0 ] = sum >> 1 ;
  10 |  output [ 1 ] = 0 ;
  11 |  }
```

### Demo A

```text
   1 | static void update_stats ( VP9_COMMON * cm , const MACROBLOCK * x ) {
   2 |  const MACROBLOCKD * const xd = & x -> e_mbd ;
   3 |  const MODE_INFO * const mi = xd -> mi [ 0 ] . src_mi ;
   4 |  const MB_MODE_INFO * const mbmi = & mi -> mbmi ;
   5 |  if ( ! frame_is_intra_only ( cm ) ) {
   6 |  const int seg_ref_active = vp9_segfeature_active ( & cm -> seg , mbmi -> segment_id , SEG_LVL_REF_FRAME ) ;
   7 |  if ( ! seg_ref_active ) {
   8 |  FRAME_COUNTS * const counts = & cm -> counts ;
   9 |  const int inter_block = is_inter_block ( mbmi ) ;
  10 |  counts -> intra_inter [ vp9_get_intra_inter_context ( xd ) ] [ inter_block ] ++ ;
  11 |  if ( inter_block ) {
  12 |  const MV_REFERENCE_FRAME ref0 = mbmi -> ref_frame [ 0 ] ;
  13 |  if ( cm -> reference_mode == REFERENCE_MODE_SELECT ) counts -> comp_inter [ vp9_get_reference_mode_context ( cm , xd ) ] [ has_second_ref ( mbmi ) ] ++ ;
  14 |  if ( has_second_ref ( mbmi ) ) {
  15 |  counts -> comp_ref [ vp9_get_pred_context_comp_ref_p ( cm , xd ) ] [ ref0 == GOLDEN_FRAME ] ++ ;
  16 |  }
  17 |  else {
  18 |  counts -> single_ref [ vp9_get_pred_context_single_ref_p1 ( xd ) ] [ 0 ] [ ref0 != LAST_FRAME ] ++ ;
  19 |  if ( ref0 != LAST_FRAME ) counts -> single_ref [ vp9_get_pred_context_single_ref_p2 ( xd ) ] [ 1 ] [ ref0 != GOLDEN_FRAME ] ++ ;
  20 |  }
  21 |  }
  22 |  }
  23 |  }
  24 |  }
```

### Demo B

```text
   1 | void vp9_fdct32x32_1_c ( const int16_t * input , int16_t * output , int stride ) {
   2 |  int r , c ;
   3 |  int16_t sum = 0 ;
   4 |  for ( r = 0 ;
   5 |  r < 32 ;
   6 |  ++ r ) for ( c = 0 ;
   7 |  c < 32 ;
   8 |  ++ c ) sum += input [ r * stride + c ] ;
   9 |  output [ 0 ] = sum >> 3 ;
  10 |  output [ 1 ] = 0 ;
  11 |  }
```

[Về danh sách ca](#danh-sách-ca)

## CA-15

### Target

```text
   1 | static int option_cmp ( my_option * a , my_option * b ) {
   2 |  const char * sa = a -> name ;
   3 |  const char * sb = b -> name ;
   4 |  for ( ;
   5 |  * sa || * sb ;
   6 |  sa ++ , sb ++ ) {
   7 |  if ( * sa < * sb ) {
   8 |  if ( * sa == '-' && * sb == '_' ) continue ;
   9 |  else return - 1 ;
  10 |  }
  11 |  if ( * sa > * sb ) {
  12 |  if ( * sa == '_' && * sb == '-' ) continue ;
  13 |  else return 1 ;
  14 |  }
  15 |  }
  16 |  DBUG_ASSERT ( a -> name == b -> name ) ;
  17 |  return 0 ;
  18 |  }
```

### Demo A

```text
   1 | static void fill_scaling_lists ( struct dxva_context * ctx , const H264Context * h , DXVA_Qmatrix_H264 * qm ) {
   2 |  unsigned i , j ;
   3 |  memset ( qm , 0 , sizeof ( * qm ) ) ;
   4 |  if ( ctx -> workaround & FF_DXVA2_WORKAROUND_SCALING_LIST_ZIGZAG ) {
   5 |  for ( i = 0 ;
   6 |  i < 6 ;
   7 |  i ++ ) for ( j = 0 ;
   8 |  j < 16 ;
   9 |  j ++ ) qm -> bScalingLists4x4 [ i ] [ j ] = h -> pps . scaling_matrix4 [ i ] [ j ] ;
  10 |  for ( i = 0 ;
  11 |  i < 64 ;
  12 |  i ++ ) {
  13 |  qm -> bScalingLists8x8 [ 0 ] [ i ] = h -> pps . scaling_matrix8 [ 0 ] [ i ] ;
  14 |  qm -> bScalingLists8x8 [ 1 ] [ i ] = h -> pps . scaling_matrix8 [ 3 ] [ i ] ;
  15 |  }
  16 |  }
  17 |  else {
  18 |  for ( i = 0 ;
  19 |  i < 6 ;
  20 |  i ++ ) for ( j = 0 ;
  21 |  j < 16 ;
  22 |  j ++ ) qm -> bScalingLists4x4 [ i ] [ j ] = h -> pps . scaling_matrix4 [ i ] [ zigzag_scan [ j ] ] ;
  23 |  for ( i = 0 ;
  24 |  i < 64 ;
  25 |  i ++ ) {
  26 |  qm -> bScalingLists8x8 [ 0 ] [ i ] = h -> pps . scaling_matrix8 [ 0 ] [ ff_zigzag_direct [ i ] ] ;
  27 |  qm -> bScalingLists8x8 [ 1 ] [ i ] = h -> pps . scaling_matrix8 [ 3 ] [ ff_zigzag_direct [ i ] ] ;
  28 |  }
  29 |  }
  30 |  }
```

### Demo B

```text
   1 | static gboolean purple_menu_cmp ( const char * a , const char * b ) {
   2 |  while ( * a && * b ) {
   3 |  while ( * a == '_' ) {
   4 |  a ++ ;
   5 |  }
   6 |  while ( * b == '_' ) {
   7 |  b ++ ;
   8 |  }
   9 |  if ( g_ascii_tolower ( * a ) != g_ascii_tolower ( * b ) ) {
  10 |  return FALSE ;
  11 |  }
  12 |  a ++ ;
  13 |  b ++ ;
  14 |  }
  15 |  return ( * a == '\0' && * b == '\0' ) ;
  16 |  }
```

[Về danh sách ca](#danh-sách-ca)

## CA-16

### Target

```text
   1 | static void request_finished ( struct request * const req , struct request * * head ) {
   2 |  if ( head ) {
   3 |  if ( req -> next == req ) {
   4 |  * head = NULL ;
   5 |  }
   6 |  else {
   7 |  req -> next -> prev = req -> prev ;
   8 |  req -> prev -> next = req -> next ;
   9 |  if ( * head == req ) * head = req -> next ;
  10 |  }
  11 |  }
  12 |  log ( EVDNS_LOG_DEBUG , "Removing timeout for request %lx" , ( unsigned long ) req ) ;
  13 |  evtimer_del ( & req -> timeout_event ) ;
  14 |  search_request_finished ( req ) ;
  15 |  global_requests_inflight -- ;
  16 |  if ( ! req -> request_appended ) {
  17 |  free ( req -> request ) ;
  18 |  }
  19 |  else {
  20 |  }
  21 |  free ( req ) ;
  22 |  evdns_requests_pump_waiting_queue ( ) ;
  23 |  }
```

### Demo A

```text
   1 | static void evdns_request_timeout_callback ( int fd , short events , void * arg ) {
   2 |  struct request * const req = ( struct request * ) arg ;
   3 |  ( void ) fd ;
   4 |  ( void ) events ;
   5 |  log ( EVDNS_LOG_DEBUG , "Request %lx timed out" , ( unsigned long ) arg ) ;
   6 |  req -> ns -> timedout ++ ;
   7 |  if ( req -> ns -> timedout > global_max_nameserver_timeout ) {
   8 |  req -> ns -> timedout = 0 ;
   9 |  nameserver_failed ( req -> ns , "request timed out." ) ;
  10 |  }
  11 |  ( void ) evtimer_del ( & req -> timeout_event ) ;
  12 |  if ( req -> tx_count >= global_max_retransmits ) {
  13 |  reply_callback ( req , 0 , DNS_ERR_TIMEOUT , NULL ) ;
  14 |  request_finished ( req , & req_head ) ;
  15 |  }
  16 |  else {
  17 |  evdns_request_transmit ( req ) ;
  18 |  }
  19 |  }
```

### Demo B

```text
   1 | static void basic_ec_math_simplified ( void ) {
   2 |  gpg_error_t err ;
   3 |  gcry_ctx_t ctx ;
   4 |  gcry_mpi_point_t G , Q ;
   5 |  gcry_mpi_t d ;
   6 |  gcry_mpi_t x , y , z ;
   7 |  gcry_sexp_t sexp ;
   8 |  wherestr = "basic_ec_math_simplified" ;
   9 |  show ( "checking basic math functions for EC (variant)\n" ) ;
  10 |  d = hex2mpi ( "D4EF27E32F8AD8E2A1C6DDEBB1D235A69E3CEF9BCE90273D" ) ;
  11 |  Q = gcry_mpi_point_new ( 0 ) ;
  12 |  err = gcry_mpi_ec_new ( & ctx , NULL , "NIST P-192" ) ;
  13 |  if ( err ) die ( "gcry_mpi_ec_new failed: %s\n" , gpg_strerror ( err ) ) ;
  14 |  G = gcry_mpi_ec_get_point ( "g" , ctx , 1 ) ;
  15 |  if ( ! G ) die ( "gcry_mpi_ec_get_point(G) failed\n" ) ;
  16 |  gcry_mpi_ec_mul ( Q , d , G , ctx ) ;
  17 |  x = gcry_mpi_new ( 0 ) ;
  18 |  y = gcry_mpi_new ( 0 ) ;
  19 |  z = gcry_mpi_new ( 0 ) ;
  20 |  gcry_mpi_point_get ( x , y , z , Q ) ;
  21 |  if ( cmp_mpihex ( x , "222D9EC717C89D047E0898C9185B033CD11C0A981EE6DC66" ) || cmp_mpihex ( y , "605DE0A82D70D3E0F84A127D0739ED33D657DF0D054BFDE8" ) || cmp_mpihex ( z , "00B06B519071BC536999AC8F2D3934B3C1FC9EACCD0A31F88F" ) ) fail ( "computed public key does not match\n" ) ;
  22 |  if ( debug ) {
  23 |  print_mpi ( "Q.x" , x ) ;
  24 |  print_mpi ( "Q.y" , y ) ;
  25 |  print_mpi ( "Q.z" , z ) ;
  26 |  }
  27 |  if ( gcry_mpi_ec_get_affine ( x , y , Q , ctx ) ) fail ( "failed to get affine coordinates\n" ) ;
  28 |  if ( cmp_mpihex ( x , "008532093BA023F4D55C0424FA3AF9367E05F309DC34CDC3FE" ) || cmp_mpihex ( y , "00C13CA9E617C6C8487BFF6A726E3C4F277913D97117939966" ) ) fail ( "computed affine coordinates of public key do not match\n" ) ;
  29 |  if ( debug ) {
  30 |  print_mpi ( "q.x" , x ) ;
  31 |  print_mpi ( "q.y" , y ) ;
  32 |  }
  33 |  gcry_mpi_release ( z ) ;
  34 |  gcry_mpi_release ( y ) ;
  35 |  gcry_mpi_release ( x ) ;
  36 |  err = gcry_mpi_ec_set_point ( "g" , G , ctx ) ;
  37 |  if ( err ) die ( "gcry_mpi_ec_set_point(G) failed\n" ) ;
  38 |  err = gcry_mpi_ec_set_mpi ( "d" , d , ctx ) ;
  39 |  if ( err ) die ( "gcry_mpi_ec_set_mpi(d) failed\n" ) ;
  40 |  err = gcry_pubkey_get_sexp ( & sexp , 0 , ctx ) ;
  41 |  if ( err ) fail ( "gcry_pubkey_get_sexp(0) failed: %s\n" , gpg_strerror ( err ) ) ;
  42 |  else if ( verbose ) print_sexp ( "Result of gcry_pubkey_get_sexp (0):\n" , sexp ) ;
  43 |  gcry_sexp_release ( sexp ) ;
  44 |  err = gcry_pubkey_get_sexp ( & sexp , GCRY_PK_GET_PUBKEY , ctx ) ;
  45 |  if ( err ) fail ( "gcry_pubkey_get_sexp(GET_PUBKEY) failed: %s\n" , gpg_strerror ( err ) ) ;
  46 |  else if ( verbose ) print_sexp ( "Result of gcry_pubkey_get_sexp (GET_PUBKEY):\n" , sexp ) ;
  47 |  gcry_sexp_release ( sexp ) ;
  48 |  err = gcry_mpi_ec_set_mpi ( "d" , NULL , ctx ) ;
  49 |  if ( err ) die ( "gcry_mpi_ec_set_mpi(d=NULL) failed\n" ) ;
  50 |  err = gcry_pubkey_get_sexp ( & sexp , 0 , ctx ) ;
  51 |  if ( err ) fail ( "gcry_pubkey_get_sexp(0 w/o d) failed: %s\n" , gpg_strerror ( err ) ) ;
  52 |  else if ( verbose ) print_sexp ( "Result of gcry_pubkey_get_sexp (0 w/o d):\n" , sexp ) ;
  53 |  gcry_sexp_release ( sexp ) ;
  54 |  err = gcry_pubkey_get_sexp ( & sexp , GCRY_PK_GET_SECKEY , ctx ) ;
  55 |  if ( gpg_err_code ( err ) != GPG_ERR_NO_SECKEY ) fail ( "gcry_pubkey_get_sexp(GET_SECKEY) returned wrong error: %s\n" , gpg_strerror ( err ) ) ;
  56 |  gcry_sexp_release ( sexp ) ;
  57 |  err = gcry_mpi_ec_set_point ( "q" , NULL , ctx ) ;
  58 |  if ( err ) die ( "gcry_mpi_ec_set_point(q=NULL) failed\n" ) ;
  59 |  err = gcry_pubkey_get_sexp ( & sexp , 0 , ctx ) ;
  60 |  if ( gpg_err_code ( err ) != GPG_ERR_BAD_CRYPT_CTX ) fail ( "gcry_pubkey_get_sexp(0 w/o Q,d) returned wrong error: %s\n" , gpg_strerror ( err ) ) ;
  61 |  gcry_sexp_release ( sexp ) ;
  62 |  gcry_mpi_point_release ( Q ) ;
  63 |  gcry_mpi_release ( d ) ;
  64 |  gcry_mpi_point_release ( G ) ;
  65 |  gcry_ctx_release ( ctx ) ;
  66 |  }
```

[Về danh sách ca](#danh-sách-ca)

## CA-17

### Target

```text
   1 | static bool all_cpu_threads_idle ( void ) {
   2 |  CPUArchState * env ;
   3 |  for ( env = first_cpu ;
   4 |  env != NULL ;
   5 |  env = env -> next_cpu ) {
   6 |  if ( ! cpu_thread_is_idle ( ENV_GET_CPU ( env ) ) ) {
   7 |  return false ;
   8 |  }
   9 |  }
  10 |  return true ;
  11 |  }
```

### Demo A

```text
   1 | void message_search_deinit ( struct message_search_context * * _ctx ) {
   2 |  struct message_search_context * ctx = * _ctx ;
   3 |  * _ctx = NULL ;
   4 |  str_find_deinit ( & ctx -> str_find_ctx ) ;
   5 |  message_decoder_deinit ( & ctx -> decoder ) ;
   6 |  i_free ( ctx ) ;
   7 |  }
```

### Demo B

```text
   1 | static int all_vcpus_paused ( void ) {
   2 |  CPUArchState * penv = first_cpu ;
   3 |  while ( penv ) {
   4 |  CPUState * pcpu = ENV_GET_CPU ( penv ) ;
   5 |  if ( ! pcpu -> stopped ) {
   6 |  return 0 ;
   7 |  }
   8 |  penv = penv -> next_cpu ;
   9 |  }
  10 |  return 1 ;
  11 |  }
```

[Về danh sách ca](#danh-sách-ca)

## CA-18

### Target

```text
   1 | static inline void usb_bt_fifo_out_enqueue(struct USBBtState *s,
   2 | 
   3 |                 struct usb_hci_out_fifo_s *fifo,
   4 | 
   5 |                 void (*send)(struct HCIInfo *, const uint8_t *, int),
   6 | 
   7 |                 int (*complete)(const uint8_t *, int),
   8 | 
   9 |                 const uint8_t *data, int len)
  10 | 
  11 | {
  12 | 
  13 |     if (fifo->len) {
  14 | 
  15 |         memcpy(fifo->data + fifo->len, data, len);
  16 | 
  17 |         fifo->len += len;
  18 | 
  19 |         if (complete(fifo->data, fifo->len)) {
  20 | 
  21 |             send(s->hci, fifo->data, fifo->len);
  22 | 
  23 |             fifo->len = 0;
  24 | 
  25 |         }
  26 | 
  27 |     } else if (complete(data, len))
  28 | 
  29 |         send(s->hci, data, len);
  30 | 
  31 |     else {
  32 | 
  33 |         memcpy(fifo->data, data, len);
  34 | 
  35 |         fifo->len = len;
  36 | 
  37 |     }
  38 | 
  39 | 
  40 | 
  41 |     /* TODO: do we need to loop? */
  42 | 
  43 | }
```

### Demo A

```text
   1 | int av_fifo_generic_write(AVFifoBuffer *f, void *src, int size, int (*func)(void*, void*, int))
   2 | 
   3 | {
   4 | 
   5 |     int total = size;
   6 | 
   7 |     do {
   8 | 
   9 |         int len = FFMIN(f->end - f->wptr, size);
  10 | 
  11 |         if (func) {
  12 | 
  13 |             if (func(src, f->wptr, len) <= 0)
  14 | 
  15 |                 break;
  16 | 
  17 |         } else {
  18 | 
  19 |             memcpy(f->wptr, src, len);
  20 | 
  21 |             src = (uint8_t*)src + len;
  22 | 
  23 |         }
  24 | 
  25 | // Write memory barrier needed for SMP here in theory
  26 | 
  27 |         f->wptr += len;
  28 | 
  29 |         if (f->wptr >= f->end)
  30 | 
  31 |             f->wptr = f->buffer;
  32 | 
  33 |         f->wndx += len;
  34 | 
  35 |         size -= len;
  36 | 
  37 |     } while (size > 0);
  38 | 
  39 |     return total - size;
  40 | 
  41 | }
```

### Demo B

```text
   1 | static inline int svq3_decode_block(GetBitContext *gb, DCTELEM *block,
   2 | 
   3 |                                     int index, const int type)
   4 | 
   5 | {
   6 | 
   7 |     static const uint8_t *const scan_patterns[4] =
   8 | 
   9 |     { luma_dc_zigzag_scan, zigzag_scan, svq3_scan, chroma_dc_scan };
  10 | 
  11 | 
  12 | 
  13 |     int run, level, sign, vlc, limit;
  14 | 
  15 |     const int intra = (3 * type) >> 2;
  16 | 
  17 |     const uint8_t *const scan = scan_patterns[type];
  18 | 
  19 | 
  20 | 
  21 |     for (limit = (16 >> intra); index < 16; index = limit, limit += 8) {
  22 | 
  23 |         for (; (vlc = svq3_get_ue_golomb(gb)) != 0; index++) {
  24 | 
  25 | 
  26 | 
  27 |           if (vlc == INVALID_VLC)
  28 | 
  29 |               return -1;
  30 | 
  31 | 
  32 | 
  33 |           sign = (vlc & 0x1) - 1;
  34 | 
  35 |           vlc  = (vlc + 1) >> 1;
  36 | 
  37 | 
  38 | 
  39 |           if (type == 3) {
  40 | 
  41 |               if (vlc < 3) {
  42 | 
  43 |                   run   = 0;
  44 | 
  45 |                   level = vlc;
  46 | 
  47 |               } else if (vlc < 4) {
  48 | 
  49 |                   run   = 1;
  50 | 
  51 |                   level = 1;
  52 | 
  53 |               } else {
  54 | 
  55 |                   run   = (vlc & 0x3);
  56 | 
  57 |                   level = ((vlc + 9) >> 2) - run;
  58 | 
  59 |               }
  60 | 
  61 |           } else {
  62 | 
  63 |               if (vlc < 16) {
  64 | 
  65 |                   run   = svq3_dct_tables[intra][vlc].run;
  66 | 
  67 |                   level = svq3_dct_tables[intra][vlc].level;
  68 | 
  69 |               } else if (intra) {
  70 | 
  71 |                   run   = (vlc & 0x7);
  72 | 
  73 |                   level = (vlc >> 3) + ((run == 0) ? 8 : ((run < 2) ? 2 : ((run < 5) ? 0 : -1)));
  74 | 
  75 |               } else {
  76 | 
  77 |                   run   = (vlc & 0xF);
  78 | 
  79 |                   level = (vlc >> 4) + ((run == 0) ? 4 : ((run < 3) ? 2 : ((run < 10) ? 1 : 0)));
  80 | 
  81 |               }
  82 | 
  83 |           }
  84 | 
  85 | 
  86 | 
  87 |           if ((index += run) >= limit)
  88 | 
  89 |               return -1;
  90 | 
  91 | 
  92 | 
  93 |           block[scan[index]] = (level ^ sign) - sign;
  94 | 
  95 |         }
  96 | 
  97 | 
  98 | 
  99 |         if (type != 2) {
 100 | 
 101 |             break;
 102 | 
 103 |         }
 104 | 
 105 |     }
 106 | 
 107 | 
 108 | 
 109 |     return 0;
 110 | 
 111 | }
```

[Về danh sách ca](#danh-sách-ca)

## CA-19

### Target

```text
   1 | PPC_OP(srawi)
   2 | 
   3 | {
   4 | 
   5 |     T1 = T0;
   6 | 
   7 |     T0 = (Ts0 >> PARAM(1));
   8 | 
   9 |     if (Ts1 < 0 && (Ts1 & PARAM(2)) != 0) {
  10 | 
  11 |         xer_ca = 1;
  12 | 
  13 |     } else {
  14 | 
  15 |         xer_ca = 0;
  16 | 
  17 |     }
  18 | 
  19 |     RETURN();
  20 | 
  21 | }
```

### Demo A

```text
   1 | PPC_OP(addic)
   2 | 
   3 | {
   4 | 
   5 |     T1 = T0;
   6 | 
   7 |     T0 += PARAM(1);
   8 | 
   9 |     if (T0 < T1) {
  10 | 
  11 |         xer_ca = 1;
  12 | 
  13 |     } else {
  14 | 
  15 |         xer_ca = 0;
  16 | 
  17 |     }
  18 | 
  19 |     RETURN();
  20 | 
  21 | }
```

### Demo B

```text
   1 | static void xics_class_init(ObjectClass *oc, void *data)
   2 | 
   3 | {
   4 | 
   5 |     DeviceClass *dc = DEVICE_CLASS(oc);
   6 | 
   7 | 
   8 | 
   9 |     dc->realize = xics_realize;
  10 | 
  11 |     dc->props = xics_properties;
  12 | 
  13 |     dc->reset = xics_reset;
  14 | 
  15 | }
```

[Về danh sách ca](#danh-sách-ca)

## CA-20

### Target

```text
   1 | static void start_children(FFStream *feed)
   2 | 
   3 | {
   4 | 
   5 |     if (no_launch)
   6 | 
   7 |         return;
   8 | 
   9 | 
  10 | 
  11 |     for (; feed; feed = feed->next) {
  12 | 
  13 |         if (feed->child_argv && !feed->pid) {
  14 | 
  15 |             feed->pid_start = time(0);
  16 | 
  17 | 
  18 | 
  19 |             feed->pid = fork();
  20 | 
  21 | 
  22 | 
  23 |             if (feed->pid < 0) {
  24 | 
  25 |                 http_log("Unable to create children\n");
  26 | 
  27 |                 exit(1);
  28 | 
  29 |             }
  30 | 
  31 |             if (!feed->pid) {
  32 | 
  33 |                 /* In child */
  34 | 
  35 |                 char pathname[1024];
  36 | 
  37 |                 char *slash;
  38 | 
  39 |                 int i;
  40 | 
  41 | 
  42 | 
  43 |                 av_strlcpy(pathname, my_program_name, sizeof(pathname));
  44 | 
  45 | 
  46 | 
  47 |                 slash = strrchr(pathname, '/');
  48 | 
  49 |                 if (!slash)
  50 | 
  51 |                     slash = pathname;
  52 | 
  53 |                 else
  54 | 
  55 |                     slash++;
  56 | 
  57 |                 strcpy(slash, "ffmpeg");
  58 | 
  59 | 
  60 | 
  61 |                 http_log("Launch command line: ");
  62 | 
  63 |                 http_log("%s ", pathname);
  64 | 
  65 |                 for (i = 1; feed->child_argv[i] && feed->child_argv[i][0]; i++)
  66 | 
  67 |                     http_log("%s ", feed->child_argv[i]);
  68 | 
  69 |                 http_log("\n");
  70 | 
  71 | 
  72 | 
  73 |                 for (i = 3; i < 256; i++)
  74 | 
  75 |                     close(i);
  76 | 
  77 | 
  78 | 
  79 |                 if (!ffserver_debug) {
  80 | 
  81 |                     i = open("/dev/null", O_RDWR);
  82 | 
  83 |                     if (i != -1) {
  84 | 
  85 |                         dup2(i, 0);
  86 | 
  87 |                         dup2(i, 1);
  88 | 
  89 |                         dup2(i, 2);
  90 | 
  91 |                         close(i);
  92 | 
  93 |                     }
  94 | 
  95 |                 }
  96 | 
  97 | 
  98 | 
  99 |                 /* This is needed to make relative pathnames work */
 100 | 
 101 |                 chdir(my_program_dir);
 102 | 
 103 | 
 104 | 
 105 |                 signal(SIGPIPE, SIG_DFL);
 106 | 
 107 | 
 108 | 
 109 |                 execvp(pathname, feed->child_argv);
 110 | 
 111 | 
 112 | 
 113 |                 _exit(1);
 114 | 
 115 |             }
 116 | 
 117 |         }
 118 | 
 119 |     }
 120 | 
 121 | }
```

### Demo A

```text
   1 | static rwpipe *rwpipe_open( int argc, char *argv[] )
   2 | 
   3 | {
   4 | 
   5 |     rwpipe *this = av_mallocz( sizeof( rwpipe ) );
   6 | 
   7 | 
   8 | 
   9 |     if ( this != NULL )
  10 | 
  11 |     {
  12 | 
  13 |         int input[ 2 ];
  14 | 
  15 |         int output[ 2 ];
  16 | 
  17 | 
  18 | 
  19 |         pipe( input );
  20 | 
  21 |         pipe( output );
  22 | 
  23 | 
  24 | 
  25 |         this->pid = fork();
  26 | 
  27 | 
  28 | 
  29 |         if ( this->pid == 0 )
  30 | 
  31 |         {
  32 | 
  33 | #define COMMAND_SIZE 10240
  34 | 
  35 |             char *command = av_mallocz( COMMAND_SIZE );
  36 | 
  37 |             int i;
  38 | 
  39 | 
  40 | 
  41 |             strcpy( command, "" );
  42 | 
  43 |             for ( i = 0; i < argc; i ++ )
  44 | 
  45 |             {
  46 | 
  47 |                 av_strlcat( command, argv[ i ], COMMAND_SIZE );
  48 | 
  49 |                 av_strlcat( command, " ", COMMAND_SIZE );
  50 | 
  51 |             }
  52 | 
  53 | 
  54 | 
  55 |             dup2( output[ 0 ], STDIN_FILENO );
  56 | 
  57 |             dup2( input[ 1 ], STDOUT_FILENO );
  58 | 
  59 | 
  60 | 
  61 |             close( input[ 0 ] );
  62 | 
  63 |             close( input[ 1 ] );
  64 | 
  65 |             close( output[ 0 ] );
  66 | 
  67 |             close( output[ 1 ] );
  68 | 
  69 | 
  70 | 
  71 |             execl("/bin/sh", "sh", "-c", command, (char*)NULL );
  72 | 
  73 |             _exit( 255 );
  74 | 
  75 |         }
  76 | 
  77 |         else
  78 | 
  79 |         {
  80 | 
  81 |             close( input[ 1 ] );
  82 | 
  83 |             close( output[ 0 ] );
  84 | 
  85 | 
  86 | 
  87 |             this->reader = fdopen( input[ 0 ], "r" );
  88 | 
  89 |             this->writer = fdopen( output[ 1 ], "w" );
  90 | 
  91 |         }
  92 | 
  93 |     }
  94 | 
  95 | 
  96 | 
  97 |     return this;
  98 | 
  99 | }
```

### Demo B

```text
   1 | static int hls_coding_unit(HEVCContext *s, int x0, int y0, int log2_cb_size)
   2 | 
   3 | {
   4 | 
   5 |     int cb_size          = 1 << log2_cb_size;
   6 | 
   7 |     HEVCLocalContext *lc = &s->HEVClc;
   8 | 
   9 |     int log2_min_cb_size = s->sps->log2_min_cb_size;
  10 | 
  11 |     int length           = cb_size >> log2_min_cb_size;
  12 | 
  13 |     int min_cb_width     = s->sps->min_cb_width;
  14 | 
  15 |     int x_cb             = x0 >> log2_min_cb_size;
  16 | 
  17 |     int y_cb             = y0 >> log2_min_cb_size;
  18 | 
  19 |     int x, y;
  20 | 
  21 | 
  22 | 
  23 |     lc->cu.x                = x0;
  24 | 
  25 |     lc->cu.y                = y0;
  26 | 
  27 |     lc->cu.rqt_root_cbf     = 1;
  28 | 
  29 |     lc->cu.pred_mode        = MODE_INTRA;
  30 | 
  31 |     lc->cu.part_mode        = PART_2Nx2N;
  32 | 
  33 |     lc->cu.intra_split_flag = 0;
  34 | 
  35 |     lc->cu.pcm_flag         = 0;
  36 | 
  37 | 
  38 | 
  39 |     SAMPLE_CTB(s->skip_flag, x_cb, y_cb) = 0;
  40 | 
  41 |     for (x = 0; x < 4; x++)
  42 | 
  43 |         lc->pu.intra_pred_mode[x] = 1;
  44 | 
  45 |     if (s->pps->transquant_bypass_enable_flag) {
  46 | 
  47 |         lc->cu.cu_transquant_bypass_flag = ff_hevc_cu_transquant_bypass_flag_decode(s);
  48 | 
  49 |         if (lc->cu.cu_transquant_bypass_flag)
  50 | 
  51 |             set_deblocking_bypass(s, x0, y0, log2_cb_size);
  52 | 
  53 |     } else
  54 | 
  55 |         lc->cu.cu_transquant_bypass_flag = 0;
  56 | 
  57 | 
  58 | 
  59 |     if (s->sh.slice_type != I_SLICE) {
  60 | 
  61 |         uint8_t skip_flag = ff_hevc_skip_flag_decode(s, x0, y0, x_cb, y_cb);
  62 | 
  63 | 
  64 | 
  65 |         lc->cu.pred_mode = MODE_SKIP;
  66 | 
  67 |         x = y_cb * min_cb_width + x_cb;
  68 | 
  69 |         for (y = 0; y < length; y++) {
  70 | 
  71 |             memset(&s->skip_flag[x], skip_flag, length);
  72 | 
  73 |             x += min_cb_width;
  74 | 
  75 |         }
  76 | 
  77 |         lc->cu.pred_mode = skip_flag ? MODE_SKIP : MODE_INTER;
  78 | 
  79 |     }
  80 | 
  81 | 
  82 | 
  83 |     if (SAMPLE_CTB(s->skip_flag, x_cb, y_cb)) {
  84 | 
  85 |         hls_prediction_unit(s, x0, y0, cb_size, cb_size, log2_cb_size, 0);
  86 | 
  87 |         intra_prediction_unit_default_value(s, x0, y0, log2_cb_size);
  88 | 
  89 | 
  90 | 
  91 |         if (!s->sh.disable_deblocking_filter_flag)
  92 | 
  93 |             ff_hevc_deblocking_boundary_strengths(s, x0, y0, log2_cb_size,
  94 | 
  95 |                                                   lc->slice_or_tiles_up_boundary,
  96 | 
  97 |                                                   lc->slice_or_tiles_left_boundary);
  98 | 
  99 |     } else {
 100 | 
 101 |         if (s->sh.slice_type != I_SLICE)
 102 | 
 103 |             lc->cu.pred_mode = ff_hevc_pred_mode_decode(s);
 104 | 
 105 |         if (lc->cu.pred_mode != MODE_INTRA ||
 106 | 
 107 |             log2_cb_size == s->sps->log2_min_cb_size) {
 108 | 
 109 |             lc->cu.part_mode        = ff_hevc_part_mode_decode(s, log2_cb_size);
 110 | 
 111 |             lc->cu.intra_split_flag = lc->cu.part_mode == PART_NxN &&
 112 | 
 113 |                                       lc->cu.pred_mode == MODE_INTRA;
 114 | 
 115 |         }
 116 | 
 117 | 
 118 | 
 119 |         if (lc->cu.pred_mode == MODE_INTRA) {
 120 | 
 121 |             if (lc->cu.part_mode == PART_2Nx2N && s->sps->pcm_enabled_flag &&
 122 | 
 123 |                 log2_cb_size >= s->sps->pcm.log2_min_pcm_cb_size &&
 124 | 
 125 |                 log2_cb_size <= s->sps->pcm.log2_max_pcm_cb_size) {
 126 | 
 127 |                 lc->cu.pcm_flag = ff_hevc_pcm_flag_decode(s);
 128 | 
 129 |             }
 130 | 
 131 |             if (lc->cu.pcm_flag) {
 132 | 
 133 |                 int ret;
 134 | 
 135 |                 intra_prediction_unit_default_value(s, x0, y0, log2_cb_size);
 136 | 
 137 |                 ret = hls_pcm_sample(s, x0, y0, log2_cb_size);
 138 | 
 139 |                 if (s->sps->pcm.loop_filter_disable_flag)
 140 | 
 141 |                     set_deblocking_bypass(s, x0, y0, log2_cb_size);
 142 | 
 143 | 
 144 | 
 145 |                 if (ret < 0)
 146 | 
 147 |                     return ret;
 148 | 
 149 |             } else {
 150 | 
 151 |                 intra_prediction_unit(s, x0, y0, log2_cb_size);
 152 | 
 153 |             }
 154 | 
 155 |         } else {
 156 | 
 157 |             intra_prediction_unit_default_value(s, x0, y0, log2_cb_size);
 158 | 
 159 |             switch (lc->cu.part_mode) {
 160 | 
 161 |             case PART_2Nx2N:
 162 | 
 163 |                 hls_prediction_unit(s, x0, y0, cb_size, cb_size, log2_cb_size, 0);
 164 | 
 165 |                 break;
 166 | 
 167 |             case PART_2NxN:
 168 | 
 169 |                 hls_prediction_unit(s, x0, y0,               cb_size, cb_size / 2, log2_cb_size, 0);
 170 | 
 171 |                 hls_prediction_unit(s, x0, y0 + cb_size / 2, cb_size, cb_size / 2, log2_cb_size, 1);
 172 | 
 173 |                 break;
 174 | 
 175 |             case PART_Nx2N:
 176 | 
 177 |                 hls_prediction_unit(s, x0,               y0, cb_size / 2, cb_size, log2_cb_size, 0);
 178 | 
 179 |                 hls_prediction_unit(s, x0 + cb_size / 2, y0, cb_size / 2, cb_size, log2_cb_size, 1);
 180 | 
 181 |                 break;
 182 | 
 183 |             case PART_2NxnU:
 184 | 
 185 |                 hls_prediction_unit(s, x0, y0,               cb_size, cb_size     / 4, log2_cb_size, 0);
 186 | 
 187 |                 hls_prediction_unit(s, x0, y0 + cb_size / 4, cb_size, cb_size * 3 / 4, log2_cb_size, 1);
 188 | 
 189 |                 break;
 190 | 
 191 |             case PART_2NxnD:
 192 | 
 193 |                 hls_prediction_unit(s, x0, y0,                   cb_size, cb_size * 3 / 4, log2_cb_size, 0);
 194 | 
 195 |                 hls_prediction_unit(s, x0, y0 + cb_size * 3 / 4, cb_size, cb_size     / 4, log2_cb_size, 1);
 196 | 
 197 |                 break;
 198 | 
 199 |             case PART_nLx2N:
 200 | 
 201 |                 hls_prediction_unit(s, x0,               y0, cb_size     / 4, cb_size, log2_cb_size, 0);
 202 | 
 203 |                 hls_prediction_unit(s, x0 + cb_size / 4, y0, cb_size * 3 / 4, cb_size, log2_cb_size, 1);
 204 | 
 205 |                 break;
 206 | 
 207 |             case PART_nRx2N:
 208 | 
 209 |                 hls_prediction_unit(s, x0,                   y0, cb_size * 3 / 4, cb_size, log2_cb_size, 0);
 210 | 
 211 |                 hls_prediction_unit(s, x0 + cb_size * 3 / 4, y0, cb_size
 212 | /* [TRUNCATED] */
```

[Về danh sách ca](#danh-sách-ca)

## CA-21

### Target

```text
   1 | static void dissect_zcl_appl_evtalt_event_notif ( tvbuff_t * tvb , proto_tree * tree , guint * offset ) {
   2 |  proto_tree_add_item ( tree , hf_zbee_zcl_appl_evtalt_event_hdr , tvb , * offset , 1 , ENC_NA ) ;
   3 |  * offset += 1 ;
   4 |  proto_tree_add_item ( tree , hf_zbee_zcl_appl_evtalt_event_id , tvb , * offset , 1 , ENC_NA ) ;
   5 |  * offset += 1 ;
   6 |  }
```

### Demo A

```text
   1 | int xmlrpc_set_options ( int type , const char * value ) {
   2 |  if ( type == XMLRPC_HTTP_HEADER ) {
   3 |  if ( ! stricmp ( value , XMLRPC_ON ) ) {
   4 |  xmlrpc . httpheader = 1 ;
   5 |  }
   6 |  if ( ! stricmp ( value , XMLRPC_OFF ) ) {
   7 |  xmlrpc . httpheader = 0 ;
   8 |  }
   9 |  }
  10 |  if ( type == XMLRPC_ENCODE ) {
  11 |  if ( value ) {
  12 |  xmlrpc . encode = sstrdup ( value ) ;
  13 |  }
  14 |  }
  15 |  if ( type == XMLRPC_INTTAG ) {
  16 |  if ( ! stricmp ( value , XMLRPC_I4 ) ) {
  17 |  xmlrpc . inttagstart = sstrdup ( "<i4>" ) ;
  18 |  xmlrpc . inttagend = sstrdup ( "</i4>" ) ;
  19 |  }
  20 |  if ( ! stricmp ( value , XMLRPC_INT ) ) {
  21 |  xmlrpc . inttagstart = sstrdup ( "<int>" ) ;
  22 |  xmlrpc . inttagend = sstrdup ( "</int>" ) ;
  23 |  }
  24 |  }
  25 |  return 1 ;
  26 |  }
```

### Demo B

```text
   1 | static void dissect_zcl_sched_energy_phase ( tvbuff_t * tvb , proto_tree * tree , guint * offset ) {
   2 |  proto_tree_add_item ( tree , hf_zbee_zcl_pwr_prof_energy_phase_id , tvb , * offset , 1 , ENC_NA ) ;
   3 |  * offset += 1 ;
   4 |  proto_tree_add_item ( tree , hf_zbee_zcl_pwr_prof_scheduled_time , tvb , * offset , 2 , ENC_LITTLE_ENDIAN ) ;
   5 |  * offset += 2 ;
   6 |  }
```

[Về danh sách ca](#danh-sách-ca)

## CA-22

### Target

```text
   1 | static int allocate_buffers ( ShortenContext * s ) {
   2 |  int i , chan ;
   3 |  int * coeffs ;
   4 |  void * tmp_ptr ;
   5 |  for ( chan = 0 ;
   6 |  chan < s -> channels ;
   7 |  chan ++ ) {
   8 |  if ( FFMAX ( 1 , s -> nmean ) >= UINT_MAX / sizeof ( int32_t ) ) {
   9 |  av_log ( s -> avctx , AV_LOG_ERROR , "nmean too large\n" ) ;
  10 |  return AVERROR_INVALIDDATA ;
  11 |  }
  12 |  if ( s -> blocksize + s -> nwrap >= UINT_MAX / sizeof ( int32_t ) || s -> blocksize + s -> nwrap <= ( unsigned ) s -> nwrap ) {
  13 |  av_log ( s -> avctx , AV_LOG_ERROR , "s->blocksize + s->nwrap too large\n" ) ;
  14 |  return AVERROR_INVALIDDATA ;
  15 |  }
  16 |  tmp_ptr = av_realloc ( s -> offset [ chan ] , sizeof ( int32_t ) * FFMAX ( 1 , s -> nmean ) ) ;
  17 |  if ( ! tmp_ptr ) return AVERROR ( ENOMEM ) ;
  18 |  s -> offset [ chan ] = tmp_ptr ;
  19 |  tmp_ptr = av_realloc ( s -> decoded_base [ chan ] , ( s -> blocksize + s -> nwrap ) * sizeof ( s -> decoded_base [ 0 ] [ 0 ] ) ) ;
  20 |  if ( ! tmp_ptr ) return AVERROR ( ENOMEM ) ;
  21 |  s -> decoded_base [ chan ] = tmp_ptr ;
  22 |  for ( i = 0 ;
  23 |  i < s -> nwrap ;
  24 |  i ++ ) s -> decoded_base [ chan ] [ i ] = 0 ;
  25 |  s -> decoded [ chan ] = s -> decoded_base [ chan ] + s -> nwrap ;
  26 |  }
  27 |  coeffs = av_realloc ( s -> coeffs , s -> nwrap * sizeof ( * s -> coeffs ) ) ;
  28 |  if ( ! coeffs ) return AVERROR ( ENOMEM ) ;
  29 |  s -> coeffs = coeffs ;
  30 |  return 0 ;
  31 |  }
```

### Demo A

```text
   1 | static int decode_subframe_lpc ( FLACContext * s , int32_t * decoded , int pred_order , int bps ) {
   2 |  int i ;
   3 |  int coeff_prec , qlevel ;
   4 |  int coeffs [ 32 ] ;
   5 |  for ( i = 0 ;
   6 |  i < pred_order ;
   7 |  i ++ ) {
   8 |  decoded [ i ] = get_sbits_long ( & s -> gb , bps ) ;
   9 |  }
  10 |  coeff_prec = get_bits ( & s -> gb , 4 ) + 1 ;
  11 |  if ( coeff_prec == 16 ) {
  12 |  av_log ( s -> avctx , AV_LOG_ERROR , "invalid coeff precision\n" ) ;
  13 |  return - 1 ;
  14 |  }
  15 |  qlevel = get_sbits ( & s -> gb , 5 ) ;
  16 |  if ( qlevel < 0 ) {
  17 |  av_log ( s -> avctx , AV_LOG_ERROR , "qlevel %d not supported, maybe buggy stream\n" , qlevel ) ;
  18 |  return - 1 ;
  19 |  }
  20 |  for ( i = 0 ;
  21 |  i < pred_order ;
  22 |  i ++ ) {
  23 |  coeffs [ pred_order - i - 1 ] = get_sbits ( & s -> gb , coeff_prec ) ;
  24 |  }
  25 |  if ( decode_residuals ( s , decoded , pred_order ) < 0 ) return - 1 ;
  26 |  s -> dsp . lpc ( decoded , coeffs , pred_order , qlevel , s -> blocksize ) ;
  27 |  return 0 ;
  28 |  }
```

### Demo B

```text
   1 | static guint32 amf_get_u29 ( tvbuff_t * tvb , int offset , guint * lenp ) {
   2 |  guint len = 0 ;
   3 |  guint8 iByte ;
   4 |  guint32 iValue ;
   5 |  iByte = tvb_get_guint8 ( tvb , offset ) ;
   6 |  iValue = ( iByte & 0x7F ) ;
   7 |  offset ++ ;
   8 |  len ++ ;
   9 |  if ( ! ( iByte & 0x80 ) ) {
  10 |  * lenp = len ;
  11 |  return iValue ;
  12 |  }
  13 |  iByte = tvb_get_guint8 ( tvb , offset ) ;
  14 |  iValue = ( iValue << 7 ) | ( iByte & 0x7F ) ;
  15 |  offset ++ ;
  16 |  len ++ ;
  17 |  if ( ! ( iByte & 0x80 ) ) {
  18 |  * lenp = len ;
  19 |  return iValue ;
  20 |  }
  21 |  iByte = tvb_get_guint8 ( tvb , offset ) ;
  22 |  iValue = ( iValue << 7 ) | ( iByte & 0x7F ) ;
  23 |  offset ++ ;
  24 |  len ++ ;
  25 |  if ( ! ( iByte & 0x80 ) ) {
  26 |  * lenp = len ;
  27 |  return iValue ;
  28 |  }
  29 |  iByte = tvb_get_guint8 ( tvb , offset ) ;
  30 |  iValue = ( iValue << 8 ) | iByte ;
  31 |  len ++ ;
  32 |  * lenp = len ;
  33 |  return iValue ;
  34 |  }
```

[Về danh sách ca](#danh-sách-ca)

## CA-23

### Target

```text
   1 | static int fill_default_ref_list(H264Context *h){
   2 | 
   3 |     MpegEncContext * const s = &h->s;
   4 | 
   5 |     int i;
   6 | 
   7 |     int smallest_poc_greater_than_current = -1;
   8 | 
   9 |     int structure_sel;
  10 | 
  11 |     Picture sorted_short_ref[32];
  12 | 
  13 |     Picture field_entry_list[2][32];
  14 | 
  15 |     Picture *frame_list[2];
  16 | 
  17 | 
  18 | 
  19 |     if (FIELD_PICTURE) {
  20 | 
  21 |         structure_sel = PICT_FRAME;
  22 | 
  23 |         frame_list[0] = field_entry_list[0];
  24 | 
  25 |         frame_list[1] = field_entry_list[1];
  26 | 
  27 |     } else {
  28 | 
  29 |         structure_sel = 0;
  30 | 
  31 |         frame_list[0] = h->default_ref_list[0];
  32 | 
  33 |         frame_list[1] = h->default_ref_list[1];
  34 | 
  35 |     }
  36 | 
  37 | 
  38 | 
  39 |     if(h->slice_type_nos==FF_B_TYPE){
  40 | 
  41 |         int list;
  42 | 
  43 |         int len[2];
  44 | 
  45 |         int short_len[2];
  46 | 
  47 |         int out_i;
  48 | 
  49 |         int limit= INT_MIN;
  50 | 
  51 | 
  52 | 
  53 |         /* sort frame according to POC in B slice */
  54 | 
  55 |         for(out_i=0; out_i<h->short_ref_count; out_i++){
  56 | 
  57 |             int best_i=INT_MIN;
  58 | 
  59 |             int best_poc=INT_MAX;
  60 | 
  61 | 
  62 | 
  63 |             for(i=0; i<h->short_ref_count; i++){
  64 | 
  65 |                 const int poc= h->short_ref[i]->poc;
  66 | 
  67 |                 if(poc > limit && poc < best_poc){
  68 | 
  69 |                     best_poc= poc;
  70 | 
  71 |                     best_i= i;
  72 | 
  73 |                 }
  74 | 
  75 |             }
  76 | 
  77 | 
  78 | 
  79 |             assert(best_i != INT_MIN);
  80 | 
  81 | 
  82 | 
  83 |             limit= best_poc;
  84 | 
  85 |             sorted_short_ref[out_i]= *h->short_ref[best_i];
  86 | 
  87 |             tprintf(h->s.avctx, "sorted poc: %d->%d poc:%d fn:%d\n", best_i, out_i, sorted_short_ref[out_i].poc, sorted_short_ref[out_i].frame_num);
  88 | 
  89 |             if (-1 == smallest_poc_greater_than_current) {
  90 | 
  91 |                 if (h->short_ref[best_i]->poc >= s->current_picture_ptr->poc) {
  92 | 
  93 |                     smallest_poc_greater_than_current = out_i;
  94 | 
  95 |                 }
  96 | 
  97 |             }
  98 | 
  99 |         }
 100 | 
 101 | 
 102 | 
 103 |         tprintf(h->s.avctx, "current poc: %d, smallest_poc_greater_than_current: %d\n", s->current_picture_ptr->poc, smallest_poc_greater_than_current);
 104 | 
 105 | 
 106 | 
 107 |         // find the largest POC
 108 | 
 109 |         for(list=0; list<2; list++){
 110 | 
 111 |             int index = 0;
 112 | 
 113 |             int j= -99;
 114 | 
 115 |             int step= list ? -1 : 1;
 116 | 
 117 | 
 118 | 
 119 |             for(i=0; i<h->short_ref_count && index < h->ref_count[list]; i++, j+=step) {
 120 | 
 121 |                 int sel;
 122 | 
 123 |                 while(j<0 || j>= h->short_ref_count){
 124 | 
 125 |                     if(j != -99 && step == (list ? -1 : 1))
 126 | 
 127 |                         return -1;
 128 | 
 129 |                     step = -step;
 130 | 
 131 |                     j= smallest_poc_greater_than_current + (step>>1);
 132 | 
 133 |                 }
 134 | 
 135 |                 sel = sorted_short_ref[j].reference | structure_sel;
 136 | 
 137 |                 if(sel != PICT_FRAME) continue;
 138 | 
 139 |                 frame_list[list][index  ]= sorted_short_ref[j];
 140 | 
 141 |                 frame_list[list][index++].pic_id= sorted_short_ref[j].frame_num;
 142 | 
 143 |             }
 144 | 
 145 |             short_len[list] = index;
 146 | 
 147 | 
 148 | 
 149 |             for(i = 0; i < 16 && index < h->ref_count[ list ]; i++){
 150 | 
 151 |                 int sel;
 152 | 
 153 |                 if(h->long_ref[i] == NULL) continue;
 154 | 
 155 |                 sel = h->long_ref[i]->reference | structure_sel;
 156 | 
 157 |                 if(sel != PICT_FRAME) continue;
 158 | 
 159 | 
 160 | 
 161 |                 frame_list[ list ][index  ]= *h->long_ref[i];
 162 | 
 163 |                 frame_list[ list ][index++].pic_id= i;
 164 | 
 165 |             }
 166 | 
 167 |             len[list] = index;
 168 | 
 169 |         }
 170 | 
 171 | 
 172 | 
 173 |         for(list=0; list<2; list++){
 174 | 
 175 |             if (FIELD_PICTURE)
 176 | 
 177 |                 len[list] = split_field_ref_list(h->default_ref_list[list],
 178 | 
 179 |                                                  h->ref_count[list],
 180 | 
 181 |                                                  frame_list[list],
 182 | 
 183 |                                                  len[list],
 184 | 
 185 |                                                  s->picture_structure,
 186 | 
 187 |                                                  short_len[list]);
 188 | 
 189 | 
 190 | 
 191 |             // swap the two first elements of L1 when L0 and L1 are identical
 192 | 
 193 |             if(list && len[0] > 1 && len[0] == len[1])
 194 | 
 195 |                 for(i=0; h->default_ref_list[0][i].data[0] == h->default_ref_list[1][i].data[0]; i++)
 196 | 
 197 |                     if(i == len[0]){
 198 | 
 199 |                         FFSWAP(Picture, h->default_ref_list[1][0], h->default_ref_list[1][1]);
 200 | 
 201 |                         break;
 202 | 
 203 |                     }
 204 | 
 205 | 
 206 | 
 207 |             if(len[list] < h->ref_count[ list ])
 208 | 
 209 |                 memset(&h->default_ref_list[list][len[list]], 0, sizeof(Picture)*(h->ref_count[ list ] - len[list]));
 210 | 
 211 |         }
 212 | 
 213 | 
 214 | 
 215 | 
 216 | 
 217 |     }else{
 218 | 
 219 |         int index=0;
 220 | 
 221 |         int short_len;
 222 | 
 223 |         for(i=0; i<h->short_ref_count; i++){
 224 | 
 225 |             int sel;
 226 | 
 227 |             sel = h->short_ref[i]->reference | structure_sel;
 228 | 
 229 |             if(sel != PICT_FRAME) continue;
 230 | 
 231 |             frame_list[0][index  ]= *h->short_ref[i];
 232 | 
 233 |             frame_list[0][index++].pic_id= h->short_ref[i]->frame_num;
 234 | 
 235 |         }
 236 | 
 237 |         short_len = index;
 238 | 
 239 |         for(i = 0; i < 16; i++){
 240 | 
 241 |             int sel;
 242 | 
 243 |             if(h->long_ref[i] == NULL) continue;
 244 | 
 245 |             sel = h->long_ref[i]->reference | structure_sel;
 246 | 
 247 |             if(sel != PICT_FRAME) continue;
 248 | 
 249 |             frame_list[0][index  ]= *h->long_ref[i];
 250 | 
 251 |             frame_list[0][index++].pic_id= i;
 252 | 
 253 |         }
 254 | 
 255 | 
 256 | 
 257 |         if (FIELD_PICTURE)
 258 | 
 259 |             index = split_field_ref_list(h->default_ref_list[0],
 260 | 
 261 |                                          h->ref_count[0], frame_list[0],
 262 | 
 263 |                                          index, s->picture_structure,
 264 | 
 265 |                                          short_len);
 266 | 
 267 | 
 268 | 
 269 |         if(index < h->ref_count[0])
 270 | 
 271 |             memset(&h->default_ref_list[0][index], 0, sizeof(Picture)*(h->ref_count[0] - index));
 272 | 
 273 |     }
 274 | 
 275 | #ifdef TRACE
 276 | 
 277 |     for (i=0; i<h->ref_count[0]; i++) {
 278 | 
 279 |         tprintf(h->s.avctx, "List0: %s fn:%d 0x%p\n", (h->default_ref_list[0][i].long_ref ? "LT" : "ST"), h->default_ref_list[0][i].pic_id, h->default_ref_list[0][i].data[0]);
 280 | 
 281 |     }
 282 | 
 283 |     if(h->slice_type_nos==FF_B_TYPE){
 284 | 
 285 |         for (i=0; i<h->ref_count[1]; i++) {
 286 | 
 287 |             tprintf(h->s.avctx, "List1: %s fn:%d 0x%p\n", (h->default_ref_list[1][i].long_ref ? "LT" : "ST"), h->default_ref_list[1][i].pic_id, h->default_ref_list[1][i].data[0]);
 288 | 
 289 |         }
 290 | 
 291 |     }
 292 | 
 293 | #endif
 294 | 
 295 |     return 0;
 296 | 
 297 | }
```

### Demo A

```text
   1 | static QObject *parse_escape(JSONParserContext *ctxt, QList **tokens, va_list *ap)
   2 | 
   3 | {
   4 | 
   5 |     QObject *token = NULL, *obj;
   6 | 
   7 |     QList *working = qlist_copy(*tokens);
   8 | 
   9 | 
  10 | 
  11 |     if (ap == NULL) {
  12 | 
  13 |         goto out;
  14 | 
  15 |     }
  16 | 
  17 | 
  18 | 
  19 |     token = qlist_pop(working);
  20 | 
  21 |     if (token == NULL) {
  22 | 
  23 |         goto out;
  24 | 
  25 |     }
  26 | 
  27 | 
  28 | 
  29 |     if (token_is_escape(token, "%p")) {
  30 | 
  31 |         obj = va_arg(*ap, QObject *);
  32 | 
  33 |     } else if (token_is_escape(token, "%i")) {
  34 | 
  35 |         obj = QOBJECT(qbool_from_int(va_arg(*ap, int)));
  36 | 
  37 |     } else if (token_is_escape(token, "%d")) {
  38 | 
  39 |         obj = QOBJECT(qint_from_int(va_arg(*ap, int)));
  40 | 
  41 |     } else if (token_is_escape(token, "%ld")) {
  42 | 
  43 |         obj = QOBJECT(qint_from_int(va_arg(*ap, long)));
  44 | 
  45 |     } else if (token_is_escape(token, "%lld") ||
  46 | 
  47 |                token_is_escape(token, "%I64d")) {
  48 | 
  49 |         obj = QOBJECT(qint_from_int(va_arg(*ap, long long)));
  50 | 
  51 |     } else if (token_is_escape(token, "%s")) {
  52 | 
  53 |         obj = QOBJECT(qstring_from_str(va_arg(*ap, const char *)));
  54 | 
  55 |     } else if (token_is_escape(token, "%f")) {
  56 | 
  57 |         obj = QOBJECT(qfloat_from_double(va_arg(*ap, double)));
  58 | 
  59 |     } else {
  60 | 
  61 |         goto out;
  62 | 
  63 |     }
  64 | 
  65 | 
  66 | 
  67 |     qobject_decref(token);
  68 | 
  69 |     QDECREF(*tokens);
  70 | 
  71 |     *tokens = working;
  72 | 
  73 | 
  74 | 
  75 |     return obj;
  76 | 
  77 | 
  78 | 
  79 | out:
  80 | 
  81 |     qobject_decref(token);
  82 | 
  83 |     QDECREF(working);
  84 | 
  85 | 
  86 | 
  87 |     return NULL;
  88 | 
  89 | }
```

### Demo B

```text
   1 | static int fill_default_ref_list(H264Context *h){
   2 | 
   3 |     MpegEncContext * const s = &h->s;
   4 | 
   5 |     int i;
   6 | 
   7 |     int smallest_poc_greater_than_current = -1;
   8 | 
   9 |     Picture sorted_short_ref[32];
  10 | 
  11 |     
  12 | 
  13 |     if(h->slice_type==B_TYPE){
  14 | 
  15 |         int out_i;
  16 | 
  17 |         int limit= -1;
  18 | 
  19 | 
  20 | 
  21 |         /* sort frame according to poc in B slice */
  22 | 
  23 |         for(out_i=0; out_i<h->short_ref_count; out_i++){
  24 | 
  25 |             int best_i=-1;
  26 | 
  27 |             int best_poc=INT_MAX;
  28 | 
  29 | 
  30 | 
  31 |             for(i=0; i<h->short_ref_count; i++){
  32 | 
  33 |                 const int poc= h->short_ref[i]->poc;
  34 | 
  35 |                 if(poc > limit && poc < best_poc){
  36 | 
  37 |                     best_poc= poc;
  38 | 
  39 |                     best_i= i;
  40 | 
  41 |                 }
  42 | 
  43 |             }
  44 | 
  45 |             
  46 | 
  47 |             assert(best_i != -1);
  48 | 
  49 |             
  50 | 
  51 |             limit= best_poc;
  52 | 
  53 |             sorted_short_ref[out_i]= *h->short_ref[best_i];
  54 | 
  55 |             tprintf("sorted poc: %d->%d poc:%d fn:%d\n", best_i, out_i, sorted_short_ref[out_i].poc, sorted_short_ref[out_i].frame_num);
  56 | 
  57 |             if (-1 == smallest_poc_greater_than_current) {
  58 | 
  59 |                 if (h->short_ref[best_i]->poc >= s->current_picture_ptr->poc) {
  60 | 
  61 |                     smallest_poc_greater_than_current = out_i;
  62 | 
  63 |                 }
  64 | 
  65 |             }
  66 | 
  67 |         }
  68 | 
  69 |     }
  70 | 
  71 | 
  72 | 
  73 |     if(s->picture_structure == PICT_FRAME){
  74 | 
  75 |         if(h->slice_type==B_TYPE){
  76 | 
  77 |             int list;
  78 | 
  79 |             tprintf("current poc: %d, smallest_poc_greater_than_current: %d\n", s->current_picture_ptr->poc, smallest_poc_greater_than_current);
  80 | 
  81 | 
  82 | 
  83 |             // find the largest poc
  84 | 
  85 |             for(list=0; list<2; list++){
  86 | 
  87 |                 int index = 0;
  88 | 
  89 |                 int j= -99;
  90 | 
  91 |                 int step= list ? -1 : 1;
  92 | 
  93 | 
  94 | 
  95 |                 for(i=0; i<h->short_ref_count && index < h->ref_count[list]; i++, j+=step) {
  96 | 
  97 |                     while(j<0 || j>= h->short_ref_count){
  98 | 
  99 |                         if(j != -99 && step == (list ? -1 : 1))
 100 | 
 101 |                             return -1;
 102 | 
 103 |                         step = -step;
 104 | 
 105 |                         j= smallest_poc_greater_than_current + (step>>1);
 106 | 
 107 |                     }
 108 | 
 109 |                     if(sorted_short_ref[j].reference != 3) continue;
 110 | 
 111 |                     h->default_ref_list[list][index  ]= sorted_short_ref[j];
 112 | 
 113 |                     h->default_ref_list[list][index++].pic_id= sorted_short_ref[j].frame_num;
 114 | 
 115 |                 }
 116 | 
 117 | 
 118 | 
 119 |                 for(i = 0; i < 16 && index < h->ref_count[ list ]; i++){
 120 | 
 121 |                     if(h->long_ref[i] == NULL) continue;
 122 | 
 123 |                     if(h->long_ref[i]->reference != 3) continue;
 124 | 
 125 | 
 126 | 
 127 |                     h->default_ref_list[ list ][index  ]= *h->long_ref[i];
 128 | 
 129 |                     h->default_ref_list[ list ][index++].pic_id= i;;
 130 | 
 131 |                 }
 132 | 
 133 |                 
 134 | 
 135 |                 if(list && (smallest_poc_greater_than_current<=0 || smallest_poc_greater_than_current>=h->short_ref_count) && (1 < index)){
 136 | 
 137 |                     // swap the two first elements of L1 when
 138 | 
 139 |                     // L0 and L1 are identical
 140 | 
 141 |                     Picture temp= h->default_ref_list[1][0];
 142 | 
 143 |                     h->default_ref_list[1][0] = h->default_ref_list[1][1];
 144 | 
 145 |                     h->default_ref_list[1][1] = temp;
 146 | 
 147 |                 }
 148 | 
 149 | 
 150 | 
 151 |                 if(index < h->ref_count[ list ])
 152 | 
 153 |                     memset(&h->default_ref_list[list][index], 0, sizeof(Picture)*(h->ref_count[ list ] - index));
 154 | 
 155 |             }
 156 | 
 157 |         }else{
 158 | 
 159 |             int index=0;
 160 | 
 161 |             for(i=0; i<h->short_ref_count; i++){
 162 | 
 163 |                 if(h->short_ref[i]->reference != 3) continue; //FIXME refernce field shit
 164 | 
 165 |                 h->default_ref_list[0][index  ]= *h->short_ref[i];
 166 | 
 167 |                 h->default_ref_list[0][index++].pic_id= h->short_ref[i]->frame_num;
 168 | 
 169 |             }
 170 | 
 171 |             for(i = 0; i < 16; i++){
 172 | 
 173 |                 if(h->long_ref[i] == NULL) continue;
 174 | 
 175 |                 if(h->long_ref[i]->reference != 3) continue;
 176 | 
 177 |                 h->default_ref_list[0][index  ]= *h->long_ref[i];
 178 | 
 179 |                 h->default_ref_list[0][index++].pic_id= i;;
 180 | 
 181 |             }
 182 | 
 183 |             if(index < h->ref_count[0])
 184 | 
 185 |                 memset(&h->default_ref_list[0][index], 0, sizeof(Picture)*(h->ref_count[0] - index));
 186 | 
 187 |         }
 188 | 
 189 |     }else{ //FIELD
 190 | 
 191 |         if(h->slice_type==B_TYPE){
 192 | 
 193 |         }else{
 194 | 
 195 |             //FIXME second field balh
 196 | 
 197 |         }
 198 | 
 199 |     }
 200 | 
 201 | #ifdef TRACE
 202 | 
 203 |     for (i=0; i<h->ref_count[0]; i++) {
 204 | 
 205 |         tprintf("List0: %s fn:%d 0x%p\n", (h->default_ref_list[0][i].long_ref ? "LT" : "ST"), h->default_ref_list[0][i].pic_id, h->default_ref_list[0][i].data[0]);
 206 | 
 207 |     }
 208 | 
 209 |     if(h->slice_type==B_TYPE){
 210 | 
 211 |         for (i=0; i<h->ref_count[1]; i++) {
 212 | 
 213 |             tprintf("List1: %s fn:%d 0x%p\n", (h->default_ref_list[1][i].long_ref ? "LT" : "ST"), h->default_ref_list[1][i].pic_id, h->default_ref_list[0][i].data[0]);
 214 | 
 215 |         }
 216 | 
 217 |     }
 218 | 
 219 | #endif
 220 | 
 221 |     return 0;
 222 | 
 223 | }
```

[Về danh sách ca](#danh-sách-ca)

## CA-24

### Target

```text
   1 | void qmp_migrate_set_cache_size(int64_t value, Error **errp)
   2 | 
   3 | {
   4 | 
   5 |     MigrationState *s = migrate_get_current();
   6 | 
   7 | 
   8 | 
   9 |     /* Check for truncation */
  10 | 
  11 |     if (value != (size_t)value) {
  12 | 
  13 |         error_set(errp, QERR_INVALID_PARAMETER_VALUE, "cache size",
  14 | 
  15 |                   "exceeding address space");
  16 | 
  17 |         return;
  18 | 
  19 |     }
  20 | 
  21 | 
  22 | 
  23 |     s->xbzrle_cache_size = xbzrle_cache_resize(value);
  24 | 
  25 | }
```

### Demo A

```text
   1 | inline static void RENAME(hcscale)(SwsContext *c, uint16_t *dst, long dstWidth, uint8_t *src1, uint8_t *src2,
   2 | 
   3 |                                    int srcW, int xInc, int flags, int canMMX2BeUsed, int16_t *hChrFilter,
   4 | 
   5 |                                    int16_t *hChrFilterPos, int hChrFilterSize, void *funnyUVCode,
   6 | 
   7 |                                    int srcFormat, uint8_t *formatConvBuffer, int16_t *mmx2Filter,
   8 | 
   9 |                                    int32_t *mmx2FilterPos, uint8_t *pal)
  10 | 
  11 | {
  12 | 
  13 |     if (srcFormat==PIX_FMT_YUYV422)
  14 | 
  15 |     {
  16 | 
  17 |         RENAME(yuy2ToUV)(formatConvBuffer, formatConvBuffer+VOFW, src1, src2, srcW);
  18 | 
  19 |         src1= formatConvBuffer;
  20 | 
  21 |         src2= formatConvBuffer+VOFW;
  22 | 
  23 |     }
  24 | 
  25 |     else if (srcFormat==PIX_FMT_UYVY422)
  26 | 
  27 |     {
  28 | 
  29 |         RENAME(uyvyToUV)(formatConvBuffer, formatConvBuffer+VOFW, src1, src2, srcW);
  30 | 
  31 |         src1= formatConvBuffer;
  32 | 
  33 |         src2= formatConvBuffer+VOFW;
  34 | 
  35 |     }
  36 | 
  37 |     else if (srcFormat==PIX_FMT_RGB32)
  38 | 
  39 |     {
  40 | 
  41 |         if(c->chrSrcHSubSample)
  42 | 
  43 |             RENAME(bgr32ToUV_half)(formatConvBuffer, formatConvBuffer+VOFW, src1, src2, srcW);
  44 | 
  45 |         else
  46 | 
  47 |             RENAME(bgr32ToUV)(formatConvBuffer, formatConvBuffer+VOFW, src1, src2, srcW);
  48 | 
  49 |         src1= formatConvBuffer;
  50 | 
  51 |         src2= formatConvBuffer+VOFW;
  52 | 
  53 |     }
  54 | 
  55 |     else if (srcFormat==PIX_FMT_RGB32_1)
  56 | 
  57 |     {
  58 | 
  59 |         if(c->chrSrcHSubSample)
  60 | 
  61 |             RENAME(bgr32ToUV_half)(formatConvBuffer, formatConvBuffer+VOFW, src1+ALT32_CORR, src2+ALT32_CORR, srcW);
  62 | 
  63 |         else
  64 | 
  65 |             RENAME(bgr32ToUV)(formatConvBuffer, formatConvBuffer+VOFW, src1+ALT32_CORR, src2+ALT32_CORR, srcW);
  66 | 
  67 |         src1= formatConvBuffer;
  68 | 
  69 |         src2= formatConvBuffer+VOFW;
  70 | 
  71 |     }
  72 | 
  73 |     else if (srcFormat==PIX_FMT_BGR24)
  74 | 
  75 |     {
  76 | 
  77 |         if(c->chrSrcHSubSample)
  78 | 
  79 |             RENAME(bgr24ToUV_half)(formatConvBuffer, formatConvBuffer+VOFW, src1, src2, srcW);
  80 | 
  81 |         else
  82 | 
  83 |             RENAME(bgr24ToUV)(formatConvBuffer, formatConvBuffer+VOFW, src1, src2, srcW);
  84 | 
  85 |         src1= formatConvBuffer;
  86 | 
  87 |         src2= formatConvBuffer+VOFW;
  88 | 
  89 |     }
  90 | 
  91 |     else if (srcFormat==PIX_FMT_BGR565)
  92 | 
  93 |     {
  94 | 
  95 |         if(c->chrSrcHSubSample)
  96 | 
  97 |             RENAME(bgr16ToUV_half)(formatConvBuffer, formatConvBuffer+VOFW, src1, src2, srcW);
  98 | 
  99 |         else
 100 | 
 101 |             RENAME(bgr16ToUV)(formatConvBuffer, formatConvBuffer+VOFW, src1, src2, srcW);
 102 | 
 103 |         src1= formatConvBuffer;
 104 | 
 105 |         src2= formatConvBuffer+VOFW;
 106 | 
 107 |     }
 108 | 
 109 |     else if (srcFormat==PIX_FMT_BGR555)
 110 | 
 111 |     {
 112 | 
 113 |         if(c->chrSrcHSubSample)
 114 | 
 115 |             RENAME(bgr15ToUV_half)(formatConvBuffer, formatConvBuffer+VOFW, src1, src2, srcW);
 116 | 
 117 |         else
 118 | 
 119 |             RENAME(bgr15ToUV)(formatConvBuffer, formatConvBuffer+VOFW, src1, src2, srcW);
 120 | 
 121 |         src1= formatConvBuffer;
 122 | 
 123 |         src2= formatConvBuffer+VOFW;
 124 | 
 125 |     }
 126 | 
 127 |     else if (srcFormat==PIX_FMT_BGR32)
 128 | 
 129 |     {
 130 | 
 131 |         if(c->chrSrcHSubSample)
 132 | 
 133 |             RENAME(rgb32ToUV_half)(formatConvBuffer, formatConvBuffer+VOFW, src1, src2, srcW);
 134 | 
 135 |         else
 136 | 
 137 |             RENAME(rgb32ToUV)(formatConvBuffer, formatConvBuffer+VOFW, src1, src2, srcW);
 138 | 
 139 |         src1= formatConvBuffer;
 140 | 
 141 |         src2= formatConvBuffer+VOFW;
 142 | 
 143 |     }
 144 | 
 145 |     else if (srcFormat==PIX_FMT_BGR32_1)
 146 | 
 147 |     {
 148 | 
 149 |         if(c->chrSrcHSubSample)
 150 | 
 151 |             RENAME(rgb32ToUV_half)(formatConvBuffer, formatConvBuffer+VOFW, src1+ALT32_CORR, src2+ALT32_CORR, srcW);
 152 | 
 153 |         else
 154 | 
 155 |             RENAME(rgb32ToUV)(formatConvBuffer, formatConvBuffer+VOFW, src1+ALT32_CORR, src2+ALT32_CORR, srcW);
 156 | 
 157 |         src1= formatConvBuffer;
 158 | 
 159 |         src2= formatConvBuffer+VOFW;
 160 | 
 161 |     }
 162 | 
 163 |     else if (srcFormat==PIX_FMT_RGB24)
 164 | 
 165 |     {
 166 | 
 167 |         if(c->chrSrcHSubSample)
 168 | 
 169 |             RENAME(rgb24ToUV_half)(formatConvBuffer, formatConvBuffer+VOFW, src1, src2, srcW);
 170 | 
 171 |         else
 172 | 
 173 |             RENAME(rgb24ToUV)(formatConvBuffer, formatConvBuffer+VOFW, src1, src2, srcW);
 174 | 
 175 |         src1= formatConvBuffer;
 176 | 
 177 |         src2= formatConvBuffer+VOFW;
 178 | 
 179 |     }
 180 | 
 181 |     else if (srcFormat==PIX_FMT_RGB565)
 182 | 
 183 |     {
 184 | 
 185 |         if(c->chrSrcHSubSample)
 186 | 
 187 |             RENAME(rgb16ToUV_half)(formatConvBuffer, formatConvBuffer+VOFW, src1, src2, srcW);
 188 | 
 189 |         else
 190 | 
 191 |             RENAME(rgb16ToUV)(formatConvBuffer, formatConvBuffer+VOFW, src1, src2, srcW);
 192 | 
 193 |         src1= formatConvBuffer;
 194 | 
 195 |         src2= formatConvBuffer+VOFW;
 196 | 
 197 |     }
 198 | 
 199 |     else if (srcFormat==PIX_FMT_RGB555)
 200 | 
 201 |     {
 202 | 
 203 |         if(c->chrSrcHSubSample)
 204 | 
 205 |             RENAME(rgb15ToUV_half)(formatConvBuffer, formatConvBuffer+VOFW, src1, src2, srcW);
 206 | 
 207 |         else
 208 | 
 209 |             RENAME(rgb15ToUV)(formatConvBuffer, formatConvBuffer+VOFW, src1, src2, srcW);
 210 | 
 211 |         src1= formatConvBuffer;
 212 | 
 213 |         src2= formatConvBuffer+VOFW;
 214 | 
 215 |     }
 216 | 
 217 |     else if (isGray(srcFormat) || srcFormat==PIX_FMT_MONOBLACK || PIX_FMT_MONOWHITE)
 218 | 
 219 |     {
 220 | 
 221 |         return;
 222 | 
 223 |     }
 224 | 
 225 |     else if (srcFormat==PIX_FMT_RGB8 || srcFormat==PIX_FMT_BGR8 || srcFormat==PIX_FMT_PAL8 || srcFormat==PIX_FMT_BGR4_BYTE  || srcFormat==PIX
 226 | /* [TRUNCATED] */
```

### Demo B

```text
   1 | void qmp_migrate_set_cache_size(int64_t value, Error **errp)
   2 | 
   3 | {
   4 | 
   5 |     MigrationState *s = migrate_get_current();
   6 | 
   7 |     int64_t new_size;
   8 | 
   9 | 
  10 | 
  11 |     /* Check for truncation */
  12 | 
  13 |     if (value != (size_t)value) {
  14 | 
  15 |         error_set(errp, QERR_INVALID_PARAMETER_VALUE, "cache size",
  16 | 
  17 |                   "exceeding address space");
  18 | 
  19 |         return;
  20 | 
  21 |     }
  22 | 
  23 | 
  24 | 
  25 |     /* Cache should not be larger than guest ram size */
  26 | 
  27 |     if (value > ram_bytes_total()) {
  28 | 
  29 |         error_set(errp, QERR_INVALID_PARAMETER_VALUE, "cache size",
  30 | 
  31 |                   "exceeds guest ram size ");
  32 | 
  33 |         return;
  34 | 
  35 |     }
  36 | 
  37 | 
  38 | 
  39 |     new_size = xbzrle_cache_resize(value);
  40 | 
  41 |     if (new_size < 0) {
  42 | 
  43 |         error_set(errp, QERR_INVALID_PARAMETER_VALUE, "cache size",
  44 | 
  45 |                   "is smaller than page size");
  46 | 
  47 |         return;
  48 | 
  49 |     }
  50 | 
  51 | 
  52 | 
  53 |     s->xbzrle_cache_size = new_size;
  54 | 
  55 | }
```

[Về danh sách ca](#danh-sách-ca)

## CA-25

### Target

```text
   1 | IN_PROC_BROWSER_TEST_F ( DownloadsApiTest , DownloadsApiTest ) {
   2 |  ASSERT_TRUE ( RunExtensionTest ( "downloads" ) ) << message_ ;
   3 |  }
```

### Demo A

```text
   1 | IN_PROC_BROWSER_TEST_F ( CrossOriginXHR , FileAccess ) {
   2 |  ASSERT_TRUE ( RunExtensionTest ( "cross_origin_xhr/file_access" ) ) << message_ ;
   3 |  }
```

### Demo B

```text
   1 | static int selinux_secctx_to_secid ( const char * secdata , u32 seclen , u32 * secid ) {
   2 |  return security_context_to_sid ( secdata , seclen , secid , GFP_KERNEL ) ;
   3 |  }
```

[Về danh sách ca](#danh-sách-ca)

## CA-26

### Target

```text
   1 | static void http_connection_test ( int persistent ) {
   2 |  short port = - 1 ;
   3 |  struct evhttp_connection * evcon = NULL ;
   4 |  struct evhttp_request * req = NULL ;
   5 |  test_ok = 0 ;
   6 |  fprintf ( stdout , "Testing Request Connection Pipeline %s: " , persistent ? "(persistent)" : "" ) ;
   7 |  http = http_setup ( & port , NULL ) ;
   8 |  evcon = evhttp_connection_new ( "127.0.0.1" , port ) ;
   9 |  if ( evcon == NULL ) {
  10 |  fprintf ( stdout , "FAILED\n" ) ;
  11 |  exit ( 1 ) ;
  12 |  }
  13 |  req = evhttp_request_new ( http_request_done , NULL ) ;
  14 |  evhttp_add_header ( req -> output_headers , "Host" , "somehost" ) ;
  15 |  if ( evhttp_make_request ( evcon , req , EVHTTP_REQ_GET , "/test" ) == - 1 ) {
  16 |  fprintf ( stdout , "FAILED\n" ) ;
  17 |  exit ( 1 ) ;
  18 |  }
  19 |  event_dispatch ( ) ;
  20 |  if ( test_ok != 1 ) {
  21 |  fprintf ( stdout , "FAILED\n" ) ;
  22 |  exit ( 1 ) ;
  23 |  }
  24 |  test_ok = 0 ;
  25 |  req = evhttp_request_new ( http_request_done , NULL ) ;
  26 |  evhttp_add_header ( req -> output_headers , "Host" , "somehost" ) ;
  27 |  if ( ! persistent ) evhttp_add_header ( req -> output_headers , "Connection" , "close" ) ;
  28 |  if ( evhttp_make_request ( evcon , req , EVHTTP_REQ_GET , "/test" ) == - 1 ) {
  29 |  fprintf ( stdout , "FAILED\n" ) ;
  30 |  exit ( 1 ) ;
  31 |  }
  32 |  event_dispatch ( ) ;
  33 |  test_ok = 0 ;
  34 |  req = evhttp_request_new ( http_request_empty_done , NULL ) ;
  35 |  evhttp_add_header ( req -> output_headers , "Empty" , "itis" ) ;
  36 |  if ( evhttp_make_request ( evcon , req , EVHTTP_REQ_GET , "/test" ) == - 1 ) {
  37 |  fprintf ( stdout , "FAILED\n" ) ;
  38 |  exit ( 1 ) ;
  39 |  }
  40 |  event_dispatch ( ) ;
  41 |  if ( test_ok != 1 ) {
  42 |  fprintf ( stdout , "FAILED\n" ) ;
  43 |  exit ( 1 ) ;
  44 |  }
  45 |  evhttp_connection_free ( evcon ) ;
  46 |  evhttp_free ( http ) ;
  47 |  fprintf ( stdout , "OK\n" ) ;
  48 |  }
```

### Demo A

```text
   1 | static void http_close_detection ( int with_delay ) {
   2 |  short port = - 1 ;
   3 |  struct evhttp_connection * evcon = NULL ;
   4 |  struct evhttp_request * req = NULL ;
   5 |  test_ok = 0 ;
   6 |  fprintf ( stdout , "Testing Connection Close Detection%s: " , with_delay ? " (with delay)" : "" ) ;
   7 |  http = http_setup ( & port , NULL ) ;
   8 |  evhttp_set_timeout ( http , 2 ) ;
   9 |  evcon = evhttp_connection_new ( "127.0.0.1" , port ) ;
  10 |  if ( evcon == NULL ) {
  11 |  fprintf ( stdout , "FAILED\n" ) ;
  12 |  exit ( 1 ) ;
  13 |  }
  14 |  delayed_client = evcon ;
  15 |  req = evhttp_request_new ( close_detect_cb , evcon ) ;
  16 |  evhttp_add_header ( req -> output_headers , "Host" , "somehost" ) ;
  17 |  if ( evhttp_make_request ( evcon , req , EVHTTP_REQ_GET , with_delay ? "/largedelay" : "/test" ) == - 1 ) {
  18 |  fprintf ( stdout , "FAILED\n" ) ;
  19 |  exit ( 1 ) ;
  20 |  }
  21 |  event_dispatch ( ) ;
  22 |  if ( test_ok != 1 ) {
  23 |  fprintf ( stdout , "FAILED\n" ) ;
  24 |  exit ( 1 ) ;
  25 |  }
  26 |  if ( TAILQ_FIRST ( & http -> connections ) != NULL ) {
  27 |  fprintf ( stdout , "FAILED (left connections)\n" ) ;
  28 |  exit ( 1 ) ;
  29 |  }
  30 |  evhttp_connection_free ( evcon ) ;
  31 |  evhttp_free ( http ) ;
  32 |  fprintf ( stdout , "OK\n" ) ;
  33 |  }
```

### Demo B

```text
   1 | float lut_interp_linear_float ( float value , float * table , size_t length ) {
   2 |  int upper , lower ;
   3 |  value = value * ( length - 1 ) ;
   4 |  upper = ceil ( value ) ;
   5 |  lower = floor ( value ) ;
   6 |  value = table [ upper ] * ( 1. - ( upper - value ) ) + table [ lower ] * ( upper - value ) ;
   7 |  return value ;
   8 |  }
```

[Về danh sách ca](#danh-sách-ca)

## CA-27

### Target

```text
   1 | static inline void RENAME(bgr24ToY)(uint8_t *dst, const uint8_t *src, int width, uint32_t *unused)
   2 | 
   3 | {
   4 | 
   5 | #if COMPILE_TEMPLATE_MMX
   6 | 
   7 |     RENAME(bgr24ToY_mmx)(dst, src, width, PIX_FMT_BGR24);
   8 | 
   9 | #else
  10 | 
  11 |     int i;
  12 | 
  13 |     for (i=0; i<width; i++) {
  14 | 
  15 |         int b= src[i*3+0];
  16 | 
  17 |         int g= src[i*3+1];
  18 | 
  19 |         int r= src[i*3+2];
  20 | 
  21 | 
  22 | 
  23 |         dst[i]= ((RY*r + GY*g + BY*b + (33<<(RGB2YUV_SHIFT-1)))>>RGB2YUV_SHIFT);
  24 | 
  25 |     }
  26 | 
  27 | #endif /* COMPILE_TEMPLATE_MMX */
  28 | 
  29 | }
```

### Demo A

```text
   1 | static inline void RENAME(bgr24ToY)(uint8_t *dst, const uint8_t *src, long width, uint32_t *unused)
   2 | 
   3 | {
   4 | 
   5 | #if COMPILE_TEMPLATE_MMX
   6 | 
   7 |     RENAME(bgr24ToY_mmx)(dst, src, width, PIX_FMT_BGR24);
   8 | 
   9 | #else
  10 | 
  11 |     int i;
  12 | 
  13 |     for (i=0; i<width; i++) {
  14 | 
  15 |         int b= src[i*3+0];
  16 | 
  17 |         int g= src[i*3+1];
  18 | 
  19 |         int r= src[i*3+2];
  20 | 
  21 | 
  22 | 
  23 |         dst[i]= ((RY*r + GY*g + BY*b + (33<<(RGB2YUV_SHIFT-1)))>>RGB2YUV_SHIFT);
  24 | 
  25 |     }
  26 | 
  27 | #endif /* COMPILE_TEMPLATE_MMX */
  28 | 
  29 | }
```

### Demo B

```text
   1 | static int mov_read_tkhd(MOVContext *c, AVIOContext *pb, MOVAtom atom)
   2 | 
   3 | {
   4 | 
   5 |     int i;
   6 | 
   7 |     int width;
   8 | 
   9 |     int height;
  10 | 
  11 |     int display_matrix[3][3];
  12 | 
  13 |     AVStream *st;
  14 | 
  15 |     MOVStreamContext *sc;
  16 | 
  17 |     int version;
  18 | 
  19 |     int flags;
  20 | 
  21 | 
  22 | 
  23 |     if (c->fc->nb_streams < 1)
  24 | 
  25 |         return 0;
  26 | 
  27 |     st = c->fc->streams[c->fc->nb_streams-1];
  28 | 
  29 |     sc = st->priv_data;
  30 | 
  31 | 
  32 | 
  33 |     version = avio_r8(pb);
  34 | 
  35 |     flags = avio_rb24(pb);
  36 | 
  37 |     st->disposition |= (flags & MOV_TKHD_FLAG_ENABLED) ? AV_DISPOSITION_DEFAULT : 0;
  38 | 
  39 | 
  40 | 
  41 |     if (version == 1) {
  42 | 
  43 |         avio_rb64(pb);
  44 | 
  45 |         avio_rb64(pb);
  46 | 
  47 |     } else {
  48 | 
  49 |         avio_rb32(pb); /* creation time */
  50 | 
  51 |         avio_rb32(pb); /* modification time */
  52 | 
  53 |     }
  54 | 
  55 |     st->id = (int)avio_rb32(pb); /* track id (NOT 0 !)*/
  56 | 
  57 |     avio_rb32(pb); /* reserved */
  58 | 
  59 | 
  60 | 
  61 |     /* highlevel (considering edits) duration in movie timebase */
  62 | 
  63 |     (version == 1) ? avio_rb64(pb) : avio_rb32(pb);
  64 | 
  65 |     avio_rb32(pb); /* reserved */
  66 | 
  67 |     avio_rb32(pb); /* reserved */
  68 | 
  69 | 
  70 | 
  71 |     avio_rb16(pb); /* layer */
  72 | 
  73 |     avio_rb16(pb); /* alternate group */
  74 | 
  75 |     avio_rb16(pb); /* volume */
  76 | 
  77 |     avio_rb16(pb); /* reserved */
  78 | 
  79 | 
  80 | 
  81 |     //read in the display matrix (outlined in ISO 14496-12, Section 6.2.2)
  82 | 
  83 |     // they're kept in fixed point format through all calculations
  84 | 
  85 |     // save u,v,z to store the whole matrix in the AV_PKT_DATA_DISPLAYMATRIX
  86 | 
  87 |     // side data, but the scale factor is not needed to calculate aspect ratio
  88 | 
  89 |     for (i = 0; i < 3; i++) {
  90 | 
  91 |         display_matrix[i][0] = avio_rb32(pb);   // 16.16 fixed point
  92 | 
  93 |         display_matrix[i][1] = avio_rb32(pb);   // 16.16 fixed point
  94 | 
  95 |         display_matrix[i][2] = avio_rb32(pb);   //  2.30 fixed point
  96 | 
  97 |     }
  98 | 
  99 | 
 100 | 
 101 |     width = avio_rb32(pb);       // 16.16 fixed point track width
 102 | 
 103 |     height = avio_rb32(pb);      // 16.16 fixed point track height
 104 | 
 105 |     sc->width = width >> 16;
 106 | 
 107 |     sc->height = height >> 16;
 108 | 
 109 | 
 110 | 
 111 |     // save the matrix and add rotate metadata when it is not the default
 112 | 
 113 |     // identity
 114 | 
 115 |     if (display_matrix[0][0] != (1 << 16) ||
 116 | 
 117 |         display_matrix[1][1] != (1 << 16) ||
 118 | 
 119 |         display_matrix[2][2] != (1 << 30) ||
 120 | 
 121 |         display_matrix[0][1] || display_matrix[0][2] ||
 122 | 
 123 |         display_matrix[1][0] || display_matrix[1][2] ||
 124 | 
 125 |         display_matrix[2][0] || display_matrix[2][1]) {
 126 | 
 127 |         int i, j;
 128 | 
 129 |         double rotate;
 130 | 
 131 | 
 132 | 
 133 |         av_freep(&sc->display_matrix);
 134 | 
 135 |         sc->display_matrix = av_malloc(sizeof(int32_t) * 9);
 136 | 
 137 |         if (!sc->display_matrix)
 138 | 
 139 |             return AVERROR(ENOMEM);
 140 | 
 141 | 
 142 | 
 143 |         for (i = 0; i < 3; i++)
 144 | 
 145 |             for (j = 0; j < 3; j++)
 146 | 
 147 |                 sc->display_matrix[i * 3 + j] = display_matrix[j][i];
 148 | 
 149 | 
 150 | 
 151 |         rotate = av_display_rotation_get(sc->display_matrix);
 152 | 
 153 |         if (!isnan(rotate)) {
 154 | 
 155 |             char rotate_buf[64];
 156 | 
 157 |             rotate = -rotate;
 158 | 
 159 |             if (rotate < 0) // for backward compatibility
 160 | 
 161 |                 rotate += 360;
 162 | 
 163 |             snprintf(rotate_buf, sizeof(rotate_buf), "%g", rotate);
 164 | 
 165 |             av_dict_set(&st->metadata, "rotate", rotate_buf, 0);
 166 | 
 167 |         }
 168 | 
 169 |     }
 170 | 
 171 | 
 172 | 
 173 |     // transform the display width/height according to the matrix
 174 | 
 175 |     // to keep the same scale, use [width height 1<<16]
 176 | 
 177 |     if (width && height && sc->display_matrix) {
 178 | 
 179 |         double disp_transform[2];
 180 | 
 181 | 
 182 | 
 183 | #define SQR(a) ((a)*(double)(a))
 184 | 
 185 |         for (i = 0; i < 2; i++)
 186 | 
 187 |             disp_transform[i] = sqrt(SQR(display_matrix[i][0]) + SQR(display_matrix[i][1]));
 188 | 
 189 | 
 190 | 
 191 |         if (disp_transform[0] > 0 && disp_transform[1] > 0 &&
 192 | 
 193 |             fabs((disp_transform[0] / disp_transform[1]) - 1.0) > 0.01)
 194 | 
 195 |             st->sample_aspect_ratio = av_d2q(
 196 | 
 197 |                 disp_transform[0] / disp_transform[1],
 198 | 
 199 |                 INT_MAX);
 200 | 
 201 |     }
 202 | 
 203 |     return 0;
 204 | 
 205 | }
```

[Về danh sách ca](#danh-sách-ca)

## CA-28

### Target

```text
   1 | void qemu_file_set_error(QEMUFile *f, int ret)
   2 | 
   3 | {
   4 | 
   5 |     if (f->last_error == 0) {
   6 | 
   7 |         f->last_error = ret;
   8 | 
   9 |     }
  10 | 
  11 | }
```

### Demo A

```text
   1 | static void qemu_file_set_error(QEMUFile *f, int ret)
   2 | 
   3 | {
   4 | 
   5 |     if (f->last_error == 0) {
   6 | 
   7 |         f->last_error = ret;
   8 | 
   9 |     }
  10 | 
  11 | }
```

### Demo B

```text
   1 | void apic_deliver_pic_intr(DeviceState *dev, int level)
   2 | 
   3 | {
   4 | 
   5 |     APICCommonState *s = APIC_COMMON(dev);
   6 | 
   7 | 
   8 | 
   9 |     if (level) {
  10 | 
  11 |         apic_local_deliver(s, APIC_LVT_LINT0);
  12 | 
  13 |     } else {
  14 | 
  15 |         uint32_t lvt = s->lvt[APIC_LVT_LINT0];
  16 | 
  17 | 
  18 | 
  19 |         switch ((lvt >> 8) & 7) {
  20 | 
  21 |         case APIC_DM_FIXED:
  22 | 
  23 |             if (!(lvt & APIC_LVT_LEVEL_TRIGGER))
  24 | 
  25 |                 break;
  26 | 
  27 |             apic_reset_bit(s->irr, lvt & 0xff);
  28 | 
  29 |             /* fall through */
  30 | 
  31 |         case APIC_DM_EXTINT:
  32 | 
  33 |             cpu_reset_interrupt(CPU(s->cpu), CPU_INTERRUPT_HARD);
  34 | 
  35 |             break;
  36 | 
  37 |         }
  38 | 
  39 |     }
  40 | 
  41 | }
```

[Về danh sách ca](#danh-sách-ca)

## CA-29

### Target

```text
   1 | static void dec_calc(DisasContext *dc, uint32_t insn)
   2 | 
   3 | {
   4 | 
   5 |     uint32_t op0, op1, op2;
   6 | 
   7 |     uint32_t ra, rb, rd;
   8 | 
   9 |     op0 = extract32(insn, 0, 4);
  10 | 
  11 |     op1 = extract32(insn, 8, 2);
  12 | 
  13 |     op2 = extract32(insn, 6, 2);
  14 | 
  15 |     ra = extract32(insn, 16, 5);
  16 | 
  17 |     rb = extract32(insn, 11, 5);
  18 | 
  19 |     rd = extract32(insn, 21, 5);
  20 | 
  21 | 
  22 | 
  23 |     switch (op0) {
  24 | 
  25 |     case 0x0000:
  26 | 
  27 |         switch (op1) {
  28 | 
  29 |         case 0x00:    /* l.add */
  30 | 
  31 |             LOG_DIS("l.add r%d, r%d, r%d\n", rd, ra, rb);
  32 | 
  33 |             {
  34 | 
  35 |                 int lab = gen_new_label();
  36 | 
  37 |                 TCGv_i64 ta = tcg_temp_new_i64();
  38 | 
  39 |                 TCGv_i64 tb = tcg_temp_new_i64();
  40 | 
  41 |                 TCGv_i64 td = tcg_temp_local_new_i64();
  42 | 
  43 |                 TCGv_i32 res = tcg_temp_local_new_i32();
  44 | 
  45 |                 TCGv_i32 sr_ove = tcg_temp_local_new_i32();
  46 | 
  47 |                 tcg_gen_extu_i32_i64(ta, cpu_R[ra]);
  48 | 
  49 |                 tcg_gen_extu_i32_i64(tb, cpu_R[rb]);
  50 | 
  51 |                 tcg_gen_add_i64(td, ta, tb);
  52 | 
  53 |                 tcg_gen_trunc_i64_i32(res, td);
  54 | 
  55 |                 tcg_gen_shri_i64(td, td, 31);
  56 | 
  57 |                 tcg_gen_andi_i64(td, td, 0x3);
  58 | 
  59 |                 /* Jump to lab when no overflow.  */
  60 | 
  61 |                 tcg_gen_brcondi_i64(TCG_COND_EQ, td, 0x0, lab);
  62 | 
  63 |                 tcg_gen_brcondi_i64(TCG_COND_EQ, td, 0x3, lab);
  64 | 
  65 |                 tcg_gen_ori_i32(cpu_sr, cpu_sr, (SR_OV | SR_CY));
  66 | 
  67 |                 tcg_gen_andi_i32(sr_ove, cpu_sr, SR_OVE);
  68 | 
  69 |                 tcg_gen_brcondi_i32(TCG_COND_NE, sr_ove, SR_OVE, lab);
  70 | 
  71 |                 gen_exception(dc, EXCP_RANGE);
  72 | 
  73 |                 gen_set_label(lab);
  74 | 
  75 |                 tcg_gen_mov_i32(cpu_R[rd], res);
  76 | 
  77 |                 tcg_temp_free_i64(ta);
  78 | 
  79 |                 tcg_temp_free_i64(tb);
  80 | 
  81 |                 tcg_temp_free_i64(td);
  82 | 
  83 |                 tcg_temp_free_i32(res);
  84 | 
  85 |                 tcg_temp_free_i32(sr_ove);
  86 | 
  87 |             }
  88 | 
  89 |             break;
  90 | 
  91 |         default:
  92 | 
  93 |             gen_illegal_exception(dc);
  94 | 
  95 |             break;
  96 | 
  97 |         }
  98 | 
  99 |         break;
 100 | 
 101 | 
 102 | 
 103 |     case 0x0001:    /* l.addc */
 104 | 
 105 |         switch (op1) {
 106 | 
 107 |         case 0x00:
 108 | 
 109 |             LOG_DIS("l.addc r%d, r%d, r%d\n", rd, ra, rb);
 110 | 
 111 |             {
 112 | 
 113 |                 int lab = gen_new_label();
 114 | 
 115 |                 TCGv_i64 ta = tcg_temp_new_i64();
 116 | 
 117 |                 TCGv_i64 tb = tcg_temp_new_i64();
 118 | 
 119 |                 TCGv_i64 tcy = tcg_temp_local_new_i64();
 120 | 
 121 |                 TCGv_i64 td = tcg_temp_local_new_i64();
 122 | 
 123 |                 TCGv_i32 res = tcg_temp_local_new_i32();
 124 | 
 125 |                 TCGv_i32 sr_cy = tcg_temp_local_new_i32();
 126 | 
 127 |                 TCGv_i32 sr_ove = tcg_temp_local_new_i32();
 128 | 
 129 |                 tcg_gen_extu_i32_i64(ta, cpu_R[ra]);
 130 | 
 131 |                 tcg_gen_extu_i32_i64(tb, cpu_R[rb]);
 132 | 
 133 |                 tcg_gen_andi_i32(sr_cy, cpu_sr, SR_CY);
 134 | 
 135 |                 tcg_gen_extu_i32_i64(tcy, sr_cy);
 136 | 
 137 |                 tcg_gen_shri_i64(tcy, tcy, 10);
 138 | 
 139 |                 tcg_gen_add_i64(td, ta, tb);
 140 | 
 141 |                 tcg_gen_add_i64(td, td, tcy);
 142 | 
 143 |                 tcg_gen_trunc_i64_i32(res, td);
 144 | 
 145 |                 tcg_gen_shri_i64(td, td, 32);
 146 | 
 147 |                 tcg_gen_andi_i64(td, td, 0x3);
 148 | 
 149 |                 /* Jump to lab when no overflow.  */
 150 | 
 151 |                 tcg_gen_brcondi_i64(TCG_COND_EQ, td, 0x0, lab);
 152 | 
 153 |                 tcg_gen_brcondi_i64(TCG_COND_EQ, td, 0x3, lab);
 154 | 
 155 |                 tcg_gen_ori_i32(cpu_sr, cpu_sr, (SR_OV | SR_CY));
 156 | 
 157 |                 tcg_gen_andi_i32(sr_ove, cpu_sr, SR_OVE);
 158 | 
 159 |                 tcg_gen_brcondi_i32(TCG_COND_NE, sr_ove, SR_OVE, lab);
 160 | 
 161 |                 gen_exception(dc, EXCP_RANGE);
 162 | 
 163 |                 gen_set_label(lab);
 164 | 
 165 |                 tcg_gen_mov_i32(cpu_R[rd], res);
 166 | 
 167 |                 tcg_temp_free_i64(ta);
 168 | 
 169 |                 tcg_temp_free_i64(tb);
 170 | 
 171 |                 tcg_temp_free_i64(tcy);
 172 | 
 173 |                 tcg_temp_free_i64(td);
 174 | 
 175 |                 tcg_temp_free_i32(res);
 176 | 
 177 |                 tcg_temp_free_i32(sr_cy);
 178 | 
 179 |                 tcg_temp_free_i32(sr_ove);
 180 | 
 181 |             }
 182 | 
 183 |             break;
 184 | 
 185 |         default:
 186 | 
 187 |             gen_illegal_exception(dc);
 188 | 
 189 |             break;
 190 | 
 191 |         }
 192 | 
 193 |         break;
 194 | 
 195 | 
 196 | 
 197 |     case 0x0002:    /* l.sub */
 198 | 
 199 |         switch (op1) {
 200 | 
 201 |         case 0x00:
 202 | 
 203 |             LOG_DIS("l.sub r%d, r%d, r%d\n", rd, ra, rb);
 204 | 
 205 |             {
 206 | 
 207 |                 int lab = gen_new_label();
 208 | 
 209 |                 TCGv_i64 ta = tcg_temp_new_i64();
 210 | 
 211 |                 TCGv_i64 tb = tcg_temp_new_i64();
 212 | 
 213 |                 TCGv_i64 td = tcg_temp_local_new_i64();
 214 | 
 215 |                 TCGv_i32 res = tcg_temp_local_new_i32();
 216 | 
 217 |                 TCGv_i32 sr_ove = tcg_temp_local_new_i32();
 218 | 
 219 | 
 220 | 
 221 |                 tcg_gen_extu_i32_i64(ta, cpu_R[ra]);
 222 | 
 223 |                 tcg_gen_extu_i32_i64(tb, cpu_R[rb]);
 224 | 
 225 |                 tcg_gen_sub_i64(td, ta, tb);
 226 | 
 227 |                 tcg_gen_trunc_i64_i32(res, td);
 228 | 
 229 |                 tcg_gen_shri_i64(td, td, 31);
 230 | 
 231 |                 tcg_gen_andi_i64(td, td, 0x3);
 232 | 
 233 |                 /* Jump to lab when no overflow.  */
 234 | 
 235 |                 tcg_gen_brcondi_i64(TCG_COND_EQ, td, 0x0, lab);
 236 | 
 237 |                 tcg_gen_brcondi_i64(TCG_COND_EQ, td, 0x3, lab);
 238 | 
 239 |                 tcg_gen_ori_i32(cpu_sr, cpu_sr, (SR_OV | SR_CY));
 240 | 
 241 |                 tcg_gen_andi_i32(sr_ove, cpu_sr, SR_OVE);
 242 | 
 243 |                 tcg_gen_brcondi_i32(TCG_COND_NE, sr_ove, SR_OVE, lab);
 244 | 
 245 |                 gen_exception(dc, EXCP_RANGE);
 246 | 
 247 |                 gen_set_label(lab);
 248 | 
 249 |                 tcg_gen_mov_i32(cpu_R[rd], res);
 250 | 
 251 |                 tcg_temp_free_i64(ta);
 252 | 
 253 |                 tcg_temp_free_i64(tb);
 254 | 
 255 |                 tcg_temp_free_i64(td);
 256 | 
 257 |                 tcg_temp_free_i32(res);
 258 | 
 259 |                 tcg_temp_free_i32(sr_ove);
 260 | 
 261 |             }
 262 | 
 263 |             break;
 264 | 
 265 |         default:
 266 | 
 267 |             gen_illegal_exception(dc);
 268 | 
 269 |             break;
 270 | 
 271 |         }
 272 | 
 273 |         break;
 274 | 
 275 | 
 276 | 
 277 |     case 0x0003:    /* l.and */
 278 | 
 279 |         switch (op1) {
 280 | 
 281 |         case 0x00:
 282 | 
 283 |             LOG_DIS("l.and r%d, r%d, r%d\n", rd, ra, rb);
 284 | 
 285 |             tcg_gen_and_tl(cpu_R[rd], cpu_R[ra], cpu_R[rb]);
 286 | 
 287 |             break;
 288 | 
 289 |         default:
 290 | 
 291 |             gen_illegal_exception(dc);
 292 | 
 293 |             break;
 294 | 
 295 |         }
 296 | 
 297 |         break;
 298 | 
 299 | 
 300 | 
 301 |     case 0x0004:    /* l.or */
 302 | 
 303 |         switch (op1) {
 304 | 
 305 |         case 0x00:
 306 | 
 307 |             LOG_DIS("l.or r%d, r%d, r%d\n", rd, ra, rb);
 308 | 
 309 |             tcg_gen_or_tl(cpu_R[rd], cpu_R[ra], cpu_R[rb]);
 310 | 
 311 |             break;
 312 | 
 313 |         default:
 314 | 
 315 |             gen_illegal_exception(dc);
 316 | 
 317 |             break;
 318 | 
 319 |         }
 320 | 
 321 |         break;
 322 | 
 323 | 
 324 | 
 325 |     case 0x0005:
 326 | 
 327 |         switch (op1) {
 328 | 
 329 |         case 0x00:    /* l.xor */
 330 | 
 331 |             LOG_DIS("l.xor r%d, r%d, r%d\n", rd, ra, rb);
 332 | 
 333 |             tcg_gen_xor_tl(cpu_R[rd], cpu_R[ra], cpu_R[rb]);
 334 | 
 335 |             break;
 336 | 
 337 |         default:
 338 | 
 339 |             gen_illegal_exception(dc);
 340 | 
 341 |             break;
 342 | 
 343 |         }
 344 | 
 345 |         break;
 346 | 
 347 | 
 348 | 
 349 |     case 0x0006:
 350 | 
 351 |         switch (op1) {
 352 | 
 353 |         case 0x03:    /* l.mul */
 354 | 
 355 |             LOG_DIS("l.mul r%d, r%d, r%d\n", rd, ra, rb);
 356 | 
 357 |             if (ra != 0 && rb != 0) {
 358 | 
 359 |                 gen_helper_mul32(cpu_R[rd], cpu_env, cpu_R[ra], cpu_R[rb]);
 360 | 
 361 |             } else {
 362 | 
 363 |                 tcg_gen_movi_tl(cpu_R[rd], 0x0);
 364 | 
 365 |             }
 366 | 
 367 |             break;
 368 | 
 369 |         default:
 370 | 
 371 |             gen_illegal_exception(dc);
 372 | 
 373 |             break;
 374 | 
 375 |         }
 376 | 
 377 |         break;
 378 | 
 379 | 
 380 | 
 381 |     case 0x0009:
 382 | 
 383 |         switch (op1) {
 384 | 
 385 |         case 0x03:    /* l.div */
 386 | 
 387 |             LOG_DIS("l.div r%d, r%d, r%d\n", rd, ra, rb);
 388 | 
 389 |             {
 390 | 
 391 |                 int lab0 = gen_new_label();
 392 | 
 393 |                 int lab1 = gen_new_label();
 394 | 
 395 |                 int lab2 = gen_new_label();
 396 | 
 397 |                 int lab3 = gen_new_label();
 398 | 
 399 |                 TCGv_i32 sr_ove = tcg_temp_local_new_i32();
 400 | 
 401 |                 if (rb == 0) {
 402 | 
 403 |                     tcg_gen_ori_tl(cpu_sr, cpu_sr, (SR_OV | SR_CY));
 404 | 
 405 |                     tcg_gen_andi_tl(sr_ove, cpu_sr, SR_OVE);
 406 | 
 407 |                     tcg_gen_brcondi_tl(TCG_COND_NE, sr_ove, SR_OVE, lab0);
 408 | 
 409 |                     gen_exception(dc, EXCP_RANGE);
 410 | 
 411 |                     gen_set_label(lab0);
 412 | 
 413 |                 } else {
 414 | 
 415 |                     tcg_gen_brcondi_tl(TCG_COND_EQ, cpu_R[rb],
 416 | 
 417 |                                        0x00000000, lab1);
 418 | 
 419 |                     tcg_gen_brcondi_tl(TCG_COND_NE, cpu_R[ra],
 420 | 
 421 |                                        0x80000000, lab2);
 422 | 
 423 |                     tcg_gen_brcondi_tl(TCG_COND_NE, cpu_R[rb],
 424 | 
 425 |                                        0xffffffff, lab2);
 426 | 
 427 |                     gen_set_label(lab1);
 428 | 
 429 |                     tcg_gen_ori_tl(cpu_sr, cpu_sr, (SR_OV | SR_CY));
 430 | 
 431 |                     tcg_gen_andi_tl(sr_ove, cpu_sr, SR_OVE);
 432 | 
 433 |                     tcg_gen_brcondi_tl(TCG_COND_NE, sr_ove, SR_OVE, lab3);
 434 | 
 435 |                     gen_exception(dc, EXCP_RANGE);
 436 | 
 437 |                     gen_set_label(lab2);
 438 | 
 439 |                     tcg_gen_div_tl(cpu_R[rd], cpu_R[ra], cpu_R[rb]);
 440 | 
 441 |                     gen_set_label(lab3);
 442 | 
 443 |                 }
 444 | 
 445 |                 tcg_temp_free_i32(sr_ove);
 446 | 
 447 |             }
 448 | 
 449 |             break;
 450 | 
 451 | 
 452 | 
 453 |         default:
 454 | 
 455 |             gen_illegal_exception(dc);
 456 | 
 457 |             break;
 458 | 
 459 |         }
 460 | 
 461 |         break;
 462 | 
 463 | 
 464 | 
 465 |     case 0x000a:
 466 | 
 467 |         switch (op1) {
 468 | 
 469 |         case 0x03:    /* l.divu */
 470 | 
 471 |             LOG_DIS("l.divu r%d, r%d, r%d\n", rd, ra, rb);
 472 | 
 473 |             {
 474 | 
 475 |                 int lab0 = gen_new_label();
 476 | 
 477 |                 int lab1 = gen_new_label();
 478 | 
 479 |                 int lab2 = gen_new_label();
 480 | 
 481 |                 TCGv_i32 sr_ove = tcg_temp_local_new_i32();
 482 | 
 483 |                 if (rb == 0) {
 484 | 
 485 |                     tcg_gen_ori_tl(cpu_sr, cpu_sr, (SR_OV | SR_CY));
 486 | 
 487 |                     tcg_gen_andi_tl(sr_ove, cpu_sr, SR_OVE);
 488 | 
 489 |                     tcg_gen_brcondi_tl(TCG_COND_NE, sr_ove, SR_OVE, lab0);
 490 | 
 491 |                     gen_exception(dc, EXCP_RANGE);
 492 | 
 493 |                     gen_set_label(lab0);
 494 | 
 495 |                 } else {
 496 | 
 497 |                     tcg_gen_brcondi_tl(TCG_COND_NE, cpu_R[rb],
 498 | 
 499 |                                        0x00000000, lab1);
 500 | 
 501 |                     tcg_gen_ori_tl(cpu_sr, cpu_sr, (SR_OV | SR_CY));
 502 | 
 503 |                     tcg_gen_andi_tl(sr_ove, cpu_sr, SR_OVE);
 504 | 
 505 |                     tcg_gen_brcondi_tl(TCG_COND_NE, sr_ove, SR_OVE, lab2);
 506 | 
 507 |                     gen_exception(dc, EXCP_RANGE);
 508 | 
 509 |                     gen_set_label(lab1);
 510 | 
 511 |                     tcg_gen_divu_tl(cpu_R[rd], cpu_R[ra], cpu_R[rb]);
 512 | 
 513 |                     gen_set_label(lab2);
 514 | 
 515 |                 }
 516 | 
 517 |                 tcg_temp_free_i32(sr_ove);
 518 | 
 519 |             }
 520 | 
 521 |             break;
 522 | 
 523 | 
 524 | 
 525 |         default:
 526 | 
 527 |             gen_illegal_exception(dc);
 528 | 
 529 |             break;
 530 | 
 531 |         }
 532 | 
 533 |         break;
 534 | /* [TRUNCATED TARGET] */
```

### Demo A

```text
   1 | static int print_uint16(DeviceState *dev, Property *prop, char *dest, size_t len)
   2 | 
   3 | {
   4 | 
   5 |     uint16_t *ptr = qdev_get_prop_ptr(dev, prop);
   6 | 
   7 |     return snprintf(dest, len, "%" PRIu16, *ptr);
   8 | 
   9 | }
```

### Demo B

```text
   1 | static void disas_cc(DisasContext *s, uint32_t insn)
   2 | 
   3 | {
   4 | 
   5 |     unsigned int sf, op, y, cond, rn, nzcv, is_imm;
   6 | 
   7 |     int label_continue = -1;
   8 | 
   9 |     TCGv_i64 tcg_tmp, tcg_y, tcg_rn;
  10 | 
  11 | 
  12 | 
  13 |     if (!extract32(insn, 29, 1)) {
  14 | 
  15 |         unallocated_encoding(s);
  16 | 
  17 |         return;
  18 | 
  19 |     }
  20 | 
  21 |     if (insn & (1 << 10 | 1 << 4)) {
  22 | 
  23 |         unallocated_encoding(s);
  24 | 
  25 |         return;
  26 | 
  27 |     }
  28 | 
  29 |     sf = extract32(insn, 31, 1);
  30 | 
  31 |     op = extract32(insn, 30, 1);
  32 | 
  33 |     is_imm = extract32(insn, 11, 1);
  34 | 
  35 |     y = extract32(insn, 16, 5); /* y = rm (reg) or imm5 (imm) */
  36 | 
  37 |     cond = extract32(insn, 12, 4);
  38 | 
  39 |     rn = extract32(insn, 5, 5);
  40 | 
  41 |     nzcv = extract32(insn, 0, 4);
  42 | 
  43 | 
  44 | 
  45 |     if (cond < 0x0e) { /* not always */
  46 | 
  47 |         int label_match = gen_new_label();
  48 | 
  49 |         label_continue = gen_new_label();
  50 | 
  51 |         arm_gen_test_cc(cond, label_match);
  52 | 
  53 |         /* nomatch: */
  54 | 
  55 |         tcg_tmp = tcg_temp_new_i64();
  56 | 
  57 |         tcg_gen_movi_i64(tcg_tmp, nzcv << 28);
  58 | 
  59 |         gen_set_nzcv(tcg_tmp);
  60 | 
  61 |         tcg_temp_free_i64(tcg_tmp);
  62 | 
  63 |         tcg_gen_br(label_continue);
  64 | 
  65 |         gen_set_label(label_match);
  66 | 
  67 |     }
  68 | 
  69 |     /* match, or condition is always */
  70 | 
  71 |     if (is_imm) {
  72 | 
  73 |         tcg_y = new_tmp_a64(s);
  74 | 
  75 |         tcg_gen_movi_i64(tcg_y, y);
  76 | 
  77 |     } else {
  78 | 
  79 |         tcg_y = cpu_reg(s, y);
  80 | 
  81 |     }
  82 | 
  83 |     tcg_rn = cpu_reg(s, rn);
  84 | 
  85 | 
  86 | 
  87 |     tcg_tmp = tcg_temp_new_i64();
  88 | 
  89 |     if (op) {
  90 | 
  91 |         gen_sub_CC(sf, tcg_tmp, tcg_rn, tcg_y);
  92 | 
  93 |     } else {
  94 | 
  95 |         gen_add_CC(sf, tcg_tmp, tcg_rn, tcg_y);
  96 | 
  97 |     }
  98 | 
  99 |     tcg_temp_free_i64(tcg_tmp);
 100 | 
 101 | 
 102 | 
 103 |     if (cond < 0x0e) { /* continue */
 104 | 
 105 |         gen_set_label(label_continue);
 106 | 
 107 |     }
 108 | 
 109 | }
```

[Về danh sách ca](#danh-sách-ca)

## CA-30

### Target

```text
   1 | static void s390_init ( ram_addr_t ram_size , const char * boot_device , const char * kernel_filename , const char * kernel_cmdline , const char * initrd_filename , const char * cpu_model ) {
   2 |  CPUState * env = NULL ;
   3 |  ram_addr_t ram_addr ;
   4 |  ram_addr_t kernel_size = 0 ;
   5 |  ram_addr_t initrd_offset ;
   6 |  ram_addr_t initrd_size = 0 ;
   7 |  int i ;
   8 |  if ( ! kvm_enabled ( ) ) {
   9 |  fprintf ( stderr , "The S390 target only works with KVM enabled\n" ) ;
  10 |  exit ( 1 ) ;
  11 |  }
  12 |  s390_bus = s390_virtio_bus_init ( & ram_size ) ;
  13 |  ram_addr = qemu_ram_alloc ( ram_size ) ;
  14 |  cpu_register_physical_memory ( 0 , ram_size , ram_addr ) ;
  15 |  if ( cpu_model == NULL ) {
  16 |  cpu_model = "host" ;
  17 |  }
  18 |  ipi_states = qemu_malloc ( sizeof ( CPUState * ) * smp_cpus ) ;
  19 |  for ( i = 0 ;
  20 |  i < smp_cpus ;
  21 |  i ++ ) {
  22 |  CPUState * tmp_env ;
  23 |  tmp_env = cpu_init ( cpu_model ) ;
  24 |  if ( ! env ) {
  25 |  env = tmp_env ;
  26 |  }
  27 |  ipi_states [ i ] = tmp_env ;
  28 |  tmp_env -> halted = 1 ;
  29 |  tmp_env -> exception_index = EXCP_HLT ;
  30 |  }
  31 |  env -> halted = 0 ;
  32 |  env -> exception_index = 0 ;
  33 |  if ( kernel_filename ) {
  34 |  kernel_size = load_image ( kernel_filename , qemu_get_ram_ptr ( 0 ) ) ;
  35 |  if ( lduw_phys ( KERN_IMAGE_START ) != 0x0dd0 ) {
  36 |  fprintf ( stderr , "Specified image is not an s390 boot image\n" ) ;
  37 |  exit ( 1 ) ;
  38 |  }
  39 |  cpu_synchronize_state ( env ) ;
  40 |  env -> psw . addr = KERN_IMAGE_START ;
  41 |  env -> psw . mask = 0x0000000180000000ULL ;
  42 |  }
  43 |  if ( initrd_filename ) {
  44 |  initrd_offset = INITRD_START ;
  45 |  while ( kernel_size + 0x100000 > initrd_offset ) {
  46 |  initrd_offset += 0x100000 ;
  47 |  }
  48 |  initrd_size = load_image ( initrd_filename , qemu_get_ram_ptr ( initrd_offset ) ) ;
  49 |  stq_phys ( INITRD_PARM_START , initrd_offset ) ;
  50 |  stq_phys ( INITRD_PARM_SIZE , initrd_size ) ;
  51 |  }
  52 |  if ( kernel_cmdline ) {
  53 |  cpu_physical_memory_rw ( KERN_PARM_AREA , ( uint8_t * ) kernel_cmdline , strlen ( kernel_cmdline ) , 1 ) ;
  54 |  }
  55 |  for ( i = 0 ;
  56 |  i < nb_nics ;
  57 |  i ++ ) {
  58 |  NICInfo * nd = & nd_table [ i ] ;
  59 |  DeviceState * dev ;
  60 |  if ( ! nd -> model ) {
  61 |  nd -> model = qemu_strdup ( "virtio" ) ;
  62 |  }
  63 |  if ( strcmp ( nd -> model , "virtio" ) ) {
  64 |  fprintf ( stderr , "S390 only supports VirtIO nics\n" ) ;
  65 |  exit ( 1 ) ;
  66 |  }
  67 |  dev = qdev_create ( ( BusState * ) s390_bus , "virtio-net-s390" ) ;
  68 |  qdev_set_nic_properties ( dev , nd ) ;
  69 |  qdev_init_nofail ( dev ) ;
  70 |  }
  71 |  for ( i = 0 ;
  72 |  i < MAX_BLK_DEVS ;
  73 |  i ++ ) {
  74 |  DriveInfo * dinfo ;
  75 |  DeviceState * dev ;
  76 |  dinfo = drive_get ( IF_IDE , 0 , i ) ;
  77 |  if ( ! dinfo ) {
  78 |  continue ;
  79 |  }
  80 |  dev = qdev_create ( ( BusState * ) s390_bus , "virtio-blk-s390" ) ;
  81 |  qdev_prop_set_drive ( dev , "drive" , dinfo ) ;
  82 |  qdev_init_nofail ( dev ) ;
  83 |  }
  84 |  }
```

### Demo A

```text
   1 | static int frame_is_boosted ( const VP9_COMP * cpi ) {
   2 |  return frame_is_intra_only ( & cpi -> common ) || cpi -> refresh_alt_ref_frame || ( cpi -> refresh_golden_frame && ! cpi -> rc . is_src_frame_alt_ref ) || vp9_is_upper_layer_key_frame ( cpi ) ;
   3 |  }
```

### Demo B

```text
   1 | static void bamboo_init ( ram_addr_t ram_size , const char * boot_device , const char * kernel_filename , const char * kernel_cmdline , const char * initrd_filename , const char * cpu_model ) {
   2 |  unsigned int pci_irq_nrs [ 4 ] = {
   3 |  28 , 27 , 26 , 25 }
   4 |  ;
   5 |  PCIBus * pcibus ;
   6 |  CPUState * env ;
   7 |  uint64_t elf_entry ;
   8 |  uint64_t elf_lowaddr ;
   9 |  target_phys_addr_t entry = 0 ;
  10 |  target_phys_addr_t loadaddr = 0 ;
  11 |  target_long kernel_size = 0 ;
  12 |  target_ulong initrd_base = 0 ;
  13 |  target_long initrd_size = 0 ;
  14 |  target_ulong dt_base = 0 ;
  15 |  void * fdt ;
  16 |  int i ;
  17 |  env = ppc440ep_init ( & ram_size , & pcibus , pci_irq_nrs , 1 , cpu_model ) ;
  18 |  if ( pcibus ) {
  19 |  for ( i = 0 ;
  20 |  i < nb_nics ;
  21 |  i ++ ) {
  22 |  pci_nic_init_nofail ( & nd_table [ i ] , "e1000" , NULL ) ;
  23 |  }
  24 |  }
  25 |  if ( kernel_filename ) {
  26 |  kernel_size = load_uimage ( kernel_filename , & entry , & loadaddr , NULL ) ;
  27 |  if ( kernel_size < 0 ) {
  28 |  kernel_size = load_elf ( kernel_filename , 0 , & elf_entry , & elf_lowaddr , NULL , 1 , ELF_MACHINE , 0 ) ;
  29 |  entry = elf_entry ;
  30 |  loadaddr = elf_lowaddr ;
  31 |  }
  32 |  if ( kernel_size < 0 ) {
  33 |  fprintf ( stderr , "qemu: could not load kernel '%s'\n" , kernel_filename ) ;
  34 |  exit ( 1 ) ;
  35 |  }
  36 |  }
  37 |  if ( initrd_filename ) {
  38 |  initrd_base = kernel_size + loadaddr ;
  39 |  initrd_size = load_image_targphys ( initrd_filename , initrd_base , ram_size - initrd_base ) ;
  40 |  if ( initrd_size < 0 ) {
  41 |  fprintf ( stderr , "qemu: could not load initial ram disk '%s'\n" , initrd_filename ) ;
  42 |  exit ( 1 ) ;
  43 |  }
  44 |  }
  45 |  if ( kernel_filename ) {
  46 |  if ( initrd_base ) dt_base = initrd_base + initrd_size ;
  47 |  else dt_base = kernel_size + loadaddr ;
  48 |  fdt = bamboo_load_device_tree ( dt_base , ram_size , initrd_base , initrd_size , kernel_cmdline ) ;
  49 |  if ( fdt == NULL ) {
  50 |  fprintf ( stderr , "couldn't load device tree\n" ) ;
  51 |  exit ( 1 ) ;
  52 |  }
  53 |  env -> gpr [ 1 ] = ( 16 << 20 ) - 8 ;
  54 |  env -> gpr [ 3 ] = dt_base ;
  55 |  env -> nip = entry ;
  56 |  }
  57 |  if ( kvm_enabled ( ) ) kvmppc_init ( ) ;
  58 |  }
```

[Về danh sách ca](#danh-sách-ca)
