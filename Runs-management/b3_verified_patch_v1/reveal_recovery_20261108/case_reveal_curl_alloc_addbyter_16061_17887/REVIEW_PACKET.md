# REVEAL — review required, not admitted

Payload SHA-256: `537b1732aa7cc6dbc3821044275e1364568c6a0893999262b9e5f1264a1c71a7`

Candidate: reveal:train:16061 (label1) -> reveal:train:17887 (label0). Both keep_in_bank=true.

Source: curl/curl, lib/mprintf.c, alloc_addbyter, CVE-2016-8618.

Fix: 8732ec40db652c53fa58cd13e2acb8eab6e40874; parent: ee4f76606cfa4ee068bf28edd37c8dae7e8db317.

Read candidate.json, technical_verification.json, ../curl_before.c, ../curl_after.c, ../curl_actual_fix.diff and https://curl.se/docs/CVE-2016-8618.html. The original CSV rows are archived as ../source_-8228664527580018723_{True,False}.c; CSV source_id is a distribution identifier, not commit evidence.

Check function identity, security mechanism and exact C token mapping independently. Formatting/comments differ; do not apply the old Devign empty-line exception. The full patch is applied with exact context and reproduces the upstream after-file.

Use the two template JSON files independently. Fill real decision, criteria, comments and UTC timestamp. They contain no prefilled decisions or signature. Both approvals must bind this exact payload, including mapping. If either reviewer rejects, retain disagreement and do not admit to pool.

## Displayed donor diff

```diff
--- vulnerable
+++ patched
@@ -11,14 +11,15 @@
  infop -> len = 0 ;
  }
  else if ( infop -> len + 1 >= infop -> alloc ) {
- char * newptr ;
- newptr = realloc ( infop -> buffer , infop -> alloc * 2 ) ;
+ char * newptr = NULL ;
+ size_t newsize = infop -> alloc * 2 ;
+ if ( newsize > infop -> alloc ) newptr = realloc ( infop -> buffer , newsize ) ;
  if ( ! newptr ) {
  infop -> fail = 1 ;
  return - 1 ;
  }
  infop -> buffer = newptr ;
- infop -> alloc *= 2 ;
+ infop -> alloc = newsize ;
  }
  infop -> buffer [ infop -> len ] = outc ;
  infop -> len ++ ;

```
