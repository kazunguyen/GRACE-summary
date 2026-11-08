   1 /* Copyright (C) 2001-2012 Artifex Software, Inc.
   2    All Rights Reserved.
   3 
   4    This software is provided AS-IS with no warranty, either express or
   5    implied.
   6 
   7    This software is distributed under license and may not be copied,
   8    modified or distributed except as expressly authorized under the terms
   9    of the license contained in the file LICENSE in this distribution.
  10 
  11    Refer to licensing information at http://www.artifex.com or contact
  12    Artifex Software, Inc.,  7 Mt. Lassen Drive - Suite A-134, San Rafael,
  13    CA  94903, U.S.A., +1(415)492-9861, for further information.
  14 */
  15 
  16 /*
  17     jbig2dec
  18 */
  19 
  20 #ifdef HAVE_CONFIG_H
  21 #include "config.h"
  22 #endif
  23 #include "os_types.h"
  24 
  25 #include <stdio.h>
  26 #include <stdlib.h>
  27 #include <stdarg.h>
  28 #include <string.h>
  29 
  30 #include "jbig2.h"
  31 #include "jbig2_priv.h"
  32 
  33 static void *
  34 jbig2_default_alloc(Jbig2Allocator *allocator, size_t size)
  35 {
  36     return malloc(size);
  37 }
  38 
  39 static void
  40 jbig2_default_free(Jbig2Allocator *allocator, void *p)
  41 {
  42     free(p);
  43 }
  44 
  45 static void *
  46 jbig2_default_realloc(Jbig2Allocator *allocator, void *p, size_t size)
  47 {
  48     return realloc(p, size);
  49 }
  50 
  51 static Jbig2Allocator jbig2_default_allocator = {
  52     jbig2_default_alloc,
  53     jbig2_default_free,
  54     jbig2_default_realloc
  55 };
  56 
  57 void *
  58 jbig2_alloc(Jbig2Allocator *allocator, size_t size, size_t num)
  59 {
  60     /* check for integer multiplication overflow */
  61     if (num > 0 && size >= (size_t) - 0x100 / num)
  62         return NULL;
  63     return allocator->alloc(allocator, size * num);
  64 }
  65 
  66 /* jbig2_free and jbig2_realloc moved to the bottom of this file */
  67 
  68 static int
  69 jbig2_default_error(void *data, const char *msg, Jbig2Severity severity, int32_t seg_idx)
  70 {
  71     /* report only fatal errors by default */
  72     if (severity == JBIG2_SEVERITY_FATAL) {
  73         fprintf(stderr, "jbig2 decoder FATAL ERROR: %s", msg);
  74         if (seg_idx != -1)
  75             fprintf(stderr, " (segment 0x%02x)", seg_idx);
  76         fprintf(stderr, "\n");
  77         fflush(stderr);
  78     }
  79 
  80     return 0;
  81 }
  82 
  83 int
  84 jbig2_error(Jbig2Ctx *ctx, Jbig2Severity severity, int32_t segment_number, const char *fmt, ...)
  85 {
  86     char buf[1024];
  87     va_list ap;
  88     int n;
  89     int code;
  90 
  91     va_start(ap, fmt);
  92     n = vsnprintf(buf, sizeof(buf), fmt, ap);
  93     va_end(ap);
  94     if (n < 0 || n == sizeof(buf))
  95         strncpy(buf, "jbig2_error: error in generating error string", sizeof(buf));
  96     code = ctx->error_callback(ctx->error_callback_data, buf, severity, segment_number);
  97     if (severity == JBIG2_SEVERITY_FATAL)
  98         code = -1;
  99     return code;
 100 }
 101 
 102 Jbig2Ctx *
 103 jbig2_ctx_new(Jbig2Allocator *allocator, Jbig2Options options, Jbig2GlobalCtx *global_ctx, Jbig2ErrorCallback error_callback, void *error_callback_data)
 104 {
 105     Jbig2Ctx *result;
 106 
 107     if (allocator == NULL)
 108         allocator = &jbig2_default_allocator;
 109     if (error_callback == NULL)
 110         error_callback = &jbig2_default_error;
 111 
 112     result = (Jbig2Ctx *) jbig2_alloc(allocator, sizeof(Jbig2Ctx), 1);
 113     if (result == NULL) {
 114         error_callback(error_callback_data, "initial context allocation failed!", JBIG2_SEVERITY_FATAL, -1);
 115         return result;
 116     }
 117 
 118     result->allocator = allocator;
 119     result->options = options;
 120     result->global_ctx = (const Jbig2Ctx *)global_ctx;
 121     result->error_callback = error_callback;
 122     result->error_callback_data = error_callback_data;
 123 
 124     result->state = (options & JBIG2_OPTIONS_EMBEDDED) ? JBIG2_FILE_SEQUENTIAL_HEADER : JBIG2_FILE_HEADER;
 125 
 126     result->buf = NULL;
 127 
 128     result->n_segments = 0;
 129     result->n_segments_max = 16;
 130     result->segments = jbig2_new(result, Jbig2Segment *, result->n_segments_max);
 131     if (result->segments == NULL) {
 132         error_callback(error_callback_data, "initial segments allocation failed!", JBIG2_SEVERITY_FATAL, -1);
 133         jbig2_free(allocator, result);
 134         return result;
 135     }
 136     result->segment_index = 0;
 137 
 138     result->current_page = 0;
 139     result->max_page_index = 4;
 140     result->pages = jbig2_new(result, Jbig2Page, result->max_page_index);
 141     if (result->pages == NULL) {
 142         error_callback(error_callback_data, "initial pages allocation failed!", JBIG2_SEVERITY_FATAL, -1);
 143         jbig2_free(allocator, result->segments);
 144         jbig2_free(allocator, result);
 145         return result;
 146     }
 147     {
 148         int index;
 149 
 150         for (index = 0; index < result->max_page_index; index++) {
 151             result->pages[index].state = JBIG2_PAGE_FREE;
 152             result->pages[index].number = 0;
 153             result->pages[index].image = NULL;
 154         }
 155     }
 156 
 157     return result;
 158 }
 159 
 160 #define get_uint16(bptr)\
 161   (((bptr)[0] << 8) | (bptr)[1])
 162 #define get_int16(bptr)\
 163   (((int)get_uint16(bptr) ^ 0x8000) - 0x8000)
 164 
 165 int16_t
 166 jbig2_get_int16(const byte *bptr)
 167 {
 168     return get_int16(bptr);
 169 }
 170 
 171 uint16_t
 172 jbig2_get_uint16(const byte *bptr)
 173 {
 174     return get_uint16(bptr);
 175 }
 176 
 177 int32_t
 178 jbig2_get_int32(const byte *bptr)
 179 {
 180     return ((int32_t) get_int16(bptr) << 16) | get_uint16(bptr + 2);
 181 }
 182 
 183 uint32_t
 184 jbig2_get_uint32(const byte *bptr)
 185 {
 186     return ((uint32_t) get_uint16(bptr) << 16) | get_uint16(bptr + 2);
 187 }
 188 
 189 /**
 190  * jbig2_data_in: submit data for decoding
 191  * @ctx: The jbig2dec decoder context
 192  * @data: a pointer to the data buffer
 193  * @size: the size of the data buffer in bytes
 194  *
 195  * Copies the specified data into internal storage and attempts
 196  * to (continue to) parse it as part of a jbig2 data stream.
 197  *
 198  * Return code: 0 on success
 199  *             -1 if there is a parsing error, or whatever
 200  *                the error handling callback returns
 201  **/
 202 int
 203 jbig2_data_in(Jbig2Ctx *ctx, const unsigned char *data, size_t size)
 204 {
 205     const size_t initial_buf_size = 1024;
 206 
 207     if (ctx->buf == NULL) {
 208         size_t buf_size = initial_buf_size;
 209 
 210         do
 211             buf_size <<= 1;
 212         while (buf_size < size);
 213         ctx->buf = jbig2_new(ctx, byte, buf_size);
 214         if (ctx->buf == NULL) {
 215             return jbig2_error(ctx, JBIG2_SEVERITY_FATAL, -1, "failed to allocate ctx->buf in jbig2_data_in");
 216         }
 217         ctx->buf_size = buf_size;
 218         ctx->buf_rd_ix = 0;
 219         ctx->buf_wr_ix = 0;
 220     } else if (ctx->buf_wr_ix + size > ctx->buf_size) {
 221         if (ctx->buf_rd_ix <= (ctx->buf_size >> 1) && ctx->buf_wr_ix - ctx->buf_rd_ix + size <= ctx->buf_size) {
 222             memmove(ctx->buf, ctx->buf + ctx->buf_rd_ix, ctx->buf_wr_ix - ctx->buf_rd_ix);
 223         } else {
 224             byte *buf;
 225             size_t buf_size = initial_buf_size;
 226 
 227             do
 228                 buf_size <<= 1;
 229             while (buf_size < ctx->buf_wr_ix - ctx->buf_rd_ix + size);
 230             buf = jbig2_new(ctx, byte, buf_size);
 231             if (buf == NULL) {
 232                 return jbig2_error(ctx, JBIG2_SEVERITY_FATAL, -1, "failed to allocate buf in jbig2_data_in");
 233             }
 234             memcpy(buf, ctx->buf + ctx->buf_rd_ix, ctx->buf_wr_ix - ctx->buf_rd_ix);
 235             jbig2_free(ctx->allocator, ctx->buf);
 236             ctx->buf = buf;
 237             ctx->buf_size = buf_size;
 238         }
 239         ctx->buf_wr_ix -= ctx->buf_rd_ix;
 240         ctx->buf_rd_ix = 0;
 241     }
 242     memcpy(ctx->buf + ctx->buf_wr_ix, data, size);
 243     ctx->buf_wr_ix += size;
 244 
 245     /* data has now been added to buffer */
 246 
 247     for (;;) {
 248         const byte jbig2_id_string[8] = { 0x97, 0x4a, 0x42, 0x32, 0x0d, 0x0a, 0x1a, 0x0a };
 249         Jbig2Segment *segment;
 250         size_t header_size;
 251         int code;
 252 
 253         switch (ctx->state) {
 254         case JBIG2_FILE_HEADER:
 255             /* D.4.1 */
 256             if (ctx->buf_wr_ix - ctx->buf_rd_ix < 9)
 257                 return 0;
 258             if (memcmp(ctx->buf + ctx->buf_rd_ix, jbig2_id_string, 8))
 259                 return jbig2_error(ctx, JBIG2_SEVERITY_FATAL, -1, "Not a JBIG2 file header");
 260             /* D.4.2 */
 261             ctx->file_header_flags = ctx->buf[ctx->buf_rd_ix + 8];
 262             if (ctx->file_header_flags & 0xFC) {
 263                 jbig2_error(ctx, JBIG2_SEVERITY_WARNING, -1, "reserved bits (2-7) of file header flags are not zero (0x%02x)", ctx->file_header_flags);
 264             }
 265             /* D.4.3 */
 266             if (!(ctx->file_header_flags & 2)) {        /* number of pages is known */
 267                 if (ctx->buf_wr_ix - ctx->buf_rd_ix < 13)
 268                     return 0;
 269                 ctx->n_pages = jbig2_get_uint32(ctx->buf + ctx->buf_rd_ix + 9);
 270                 ctx->buf_rd_ix += 13;
 271                 if (ctx->n_pages == 1)
 272                     jbig2_error(ctx, JBIG2_SEVERITY_INFO, -1, "file header indicates a single page document");
 273                 else
 274                     jbig2_error(ctx, JBIG2_SEVERITY_INFO, -1, "file header indicates a %d page document", ctx->n_pages);
 275             } else {            /* number of pages not known */
 276 
 277                 ctx->n_pages = 0;
 278                 ctx->buf_rd_ix += 9;
 279             }
 280             /* determine the file organization based on the flags - D.4.2 again */
 281             if (ctx->file_header_flags & 1) {
 282                 ctx->state = JBIG2_FILE_SEQUENTIAL_HEADER;
 283                 jbig2_error(ctx, JBIG2_SEVERITY_DEBUG, -1, "file header indicates sequential organization");
 284             } else {
 285                 ctx->state = JBIG2_FILE_RANDOM_HEADERS;
 286                 jbig2_error(ctx, JBIG2_SEVERITY_DEBUG, -1, "file header indicates random-access organization");
 287 
 288             }
 289             break;
 290         case JBIG2_FILE_SEQUENTIAL_HEADER:
 291         case JBIG2_FILE_RANDOM_HEADERS:
 292             segment = jbig2_parse_segment_header(ctx, ctx->buf + ctx->buf_rd_ix, ctx->buf_wr_ix - ctx->buf_rd_ix, &header_size);
 293             if (segment == NULL)
 294                 return 0;       /* need more data */
 295             ctx->buf_rd_ix += header_size;
 296 
 297             if (ctx->n_segments == ctx->n_segments_max)
 298                 ctx->segments = jbig2_renew(ctx, ctx->segments, Jbig2Segment *, (ctx->n_segments_max <<= 2));
 299 
 300             ctx->segments[ctx->n_segments++] = segment;
 301             if (ctx->state == JBIG2_FILE_RANDOM_HEADERS) {
 302                 if ((segment->flags & 63) == 51)        /* end of file */
 303                     ctx->state = JBIG2_FILE_RANDOM_BODIES;
 304             } else              /* JBIG2_FILE_SEQUENTIAL_HEADER */
 305                 ctx->state = JBIG2_FILE_SEQUENTIAL_BODY;
 306             break;
 307         case JBIG2_FILE_SEQUENTIAL_BODY:
 308         case JBIG2_FILE_RANDOM_BODIES:
 309             segment = ctx->segments[ctx->segment_index];
 310             if (segment->data_length > ctx->buf_wr_ix - ctx->buf_rd_ix)
 311                 return 0;       /* need more data */
 312             code = jbig2_parse_segment(ctx, segment, ctx->buf + ctx->buf_rd_ix);
 313             ctx->buf_rd_ix += segment->data_length;
 314             ctx->segment_index++;
 315             if (ctx->state == JBIG2_FILE_RANDOM_BODIES) {
 316                 if (ctx->segment_index == ctx->n_segments)
 317                     ctx->state = JBIG2_FILE_EOF;
 318             } else {            /* JBIG2_FILE_SEQUENCIAL_BODY */
 319 
 320                 ctx->state = JBIG2_FILE_SEQUENTIAL_HEADER;
 321             }
 322             if (code < 0) {
 323                 ctx->state = JBIG2_FILE_EOF;
 324                 return code;
 325             }
 326             break;
 327         case JBIG2_FILE_EOF:
 328             if (ctx->buf_rd_ix == ctx->buf_wr_ix)
 329                 return 0;
 330             return jbig2_error(ctx, JBIG2_SEVERITY_WARNING, -1, "Garbage beyond end of file");
 331         }
 332     }
 333 }
 334 
 335 void
 336 jbig2_ctx_free(Jbig2Ctx *ctx)
 337 {
 338     Jbig2Allocator *ca = ctx->allocator;
 339     int i;
 340 
 341     jbig2_free(ca, ctx->buf);
 342     if (ctx->segments != NULL) {
 343         for (i = 0; i < ctx->n_segments; i++)
 344             jbig2_free_segment(ctx, ctx->segments[i]);
 345         jbig2_free(ca, ctx->segments);
 346     }
 347 
 348     if (ctx->pages != NULL) {
 349         for (i = 0; i <= ctx->current_page; i++)
 350             if (ctx->pages[i].image != NULL)
 351                 jbig2_image_release(ctx, ctx->pages[i].image);
 352         jbig2_free(ca, ctx->pages);
 353     }
 354 
 355     jbig2_free(ca, ctx);
 356 }
 357 
 358 Jbig2GlobalCtx *
 359 jbig2_make_global_ctx(Jbig2Ctx *ctx)
 360 {
 361     return (Jbig2GlobalCtx *) ctx;
 362 }
 363 
 364 void
 365 jbig2_global_ctx_free(Jbig2GlobalCtx *global_ctx)
 366 {
 367     jbig2_ctx_free((Jbig2Ctx *) global_ctx);
 368 }
 369 
 370 /* I'm not committed to keeping the word stream interface. It's handy
 371    when you think you may be streaming your input, but if you're not
 372    (as is currently the case), it just adds complexity.
 373 */
 374 
 375 typedef struct {
 376     Jbig2WordStream super;
 377     const byte *data;
 378     size_t size;
 379 } Jbig2WordStreamBuf;
 380 
 381 static int
 382 jbig2_word_stream_buf_get_next_word(Jbig2WordStream *self, int offset, uint32_t *word)
 383 {
 384     Jbig2WordStreamBuf *z = (Jbig2WordStreamBuf *) self;
 385     const byte *data = z->data;
 386     uint32_t result;
 387 
 388     if (offset + 4 < z->size)
 389         result = (data[offset] << 24) | (data[offset + 1] << 16) | (data[offset + 2] << 8) | data[offset + 3];
 390     else if (offset > z->size)
 391         return -1;
 392     else {
 393         int i;
 394 
 395         result = 0;
 396         for (i = 0; i < z->size - offset; i++)
 397             result |= data[offset + i] << ((3 - i) << 3);
 398     }
 399     *word = result;
 400     return 0;
 401 }
 402 
 403 Jbig2WordStream *
 404 jbig2_word_stream_buf_new(Jbig2Ctx *ctx, const byte *data, size_t size)
 405 {
 406     Jbig2WordStreamBuf *result = jbig2_new(ctx, Jbig2WordStreamBuf, 1);
 407 
 408     if (result == NULL) {
 409         jbig2_error(ctx, JBIG2_SEVERITY_FATAL, -1, "failed to allocate Jbig2WordStreamBuf in jbig2_word_stream_buf_new");
 410         return NULL;
 411     }
 412 
 413     result->super.get_next_word = jbig2_word_stream_buf_get_next_word;
 414     result->data = data;
 415     result->size = size;
 416 
 417     return &result->super;
 418 }
 419 
 420 void
 421 jbig2_word_stream_buf_free(Jbig2Ctx *ctx, Jbig2WordStream *ws)
 422 {
 423     jbig2_free(ctx->allocator, ws);
 424 }
 425 
 426 /* When Memento is in use, the ->free and ->realloc calls get
 427  * turned into ->Memento_free and ->Memento_realloc, which is
 428  * obviously problematic. Undefine free and realloc here to
 429  * avoid this. */
 430 #ifdef MEMENTO
 431 #undef free
 432 #undef realloc
 433 #endif
 434 
 435 void
 436 jbig2_free(Jbig2Allocator *allocator, void *p)
 437 {
 438     allocator->free(allocator, p);
 439 }
 440 
 441 void *
 442 jbig2_realloc(Jbig2Allocator *allocator, void *p, size_t size, size_t num)
 443 {
 444     /* check for integer multiplication overflow */
 445     if (num > 0 && size >= (size_t) - 0x100 / num)
 446         return NULL;
 447     return allocator->realloc(allocator, p, size * num);
 448 }
