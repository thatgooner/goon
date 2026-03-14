# Hermes memory behavioral teardown

## neden bu ikinci pass lazim
ilk pass `Hermes iyi ama flat ve 6/10` diyordu.
dogru ama eksik.

asıl olay sadece memory dosyalari degil.
Hermes memory bir davranis sistemi:
- ne zaman save etmeye calisiyor
- ne zaman promptu donduruyor
- ne zaman transcript'i ayiriyor
- compression olunca neyi koruyor
- search/recall'i nasil ucuz tutuyor

Purr icin calmamiz gereken sey de tam bu lane.
`feature list` degil, `behavior loop`.

---

## Hermes'in gizli iyi tarafi: memory bir loop olarak tasarlanmis

### 1. frozen prompt snapshot
Hermes memory'yi session artifact gibi ele aliyor.

olan sey:
- system prompt bir kere build ediliyor
- memory disk'e yazilsa bile ayni session icinde prompt degismiyor
- session devam ederken SQLite'daki ayni stored prompt geri yukleniyor

neden guclu:
- prompt cache bozulmuyor
- davranis drift etmiyor
- `memory update oldu diye her tur prompt rebuild` deliligi olmuyor

Purr icin sonuc:
- hot pack de session/window bazli snapshot olmali
- ama canonical truth snapshot olmamali
- truth ledger'da, session behavior pack'te yasamali

### 2. live write / frozen read ayrimi
Hermes iki state tutuyor:
- live memory entries: diskte guncel
- frozen system snapshot: prompta giden

bu ayrim baya kritik.
agent save edebiliyor ama promptu aninda oynatmiyor.

neden iyi:
- durability var
- cache stability var

neden Purr icin yetmez:
- user sana bir sey duzelttiginde ayni sessionda hissedilmemesi product failure olur

Purr move:
- `frozen session pack + live retrieval override`
- yani tum promptu rebuild etme
- ama turn-level retrieval layer, yeni kritik correction'i canlı pack'e sokabilsin

### 3. memory nudge loop'u
Hermes `memory kullan belki` diye sadece tool vermiyor.
turn sayisi gecince user mesajina yumusak bir sistem notu ekliyor.
`bir sey save etmeyi dusun` diye.
ve counter ancak memory tool gercekten kullanilinca sifirlaniyor.

neden iyi:
- persistence'i pasif umuda birakmiyor
- model behaviorunu hafifce raya sokuyor

Purr icin calmamiz gereken sey:
- memory extraction/event loop should be operationalized
- sadece `model isterse save eder` kafasi olmaz

ama birebir kopyalama yok:
- Purr'da bunu chat icine not duserek yapmak gerekmeyebilir
- server-side event workers / classifier / extractor daha dogru

### 4. pre-compression salvage pass
Hermes'in en temiz hareketlerinden biri bu.
compression oncesi modele tek ekstra tur veriyor:
- `session compress olacak`
- `worth remembering ne varsa save et`
- sadece memory tool acik
- sonra flush artifact'larini history'den siliyor

neden cok iyi:
- modelin kafasinda kalmis ama write edilmemis seyleri kaybetmeden once kurtariyor
- summary'e kurban gitmeden once durable memory'e cekiyor

Purr icin direkt calmali:
- transcript summarize / archive / session cut / notification re-entry oncesi
- `memory salvage step` zorunlu olmali

### 5. compression = overwrite degil, lineage split
Hermes compression yapinca eski session'u ezmiyor.
- eski session kapanıyor
- yeni continuation session aciliyor
- parent_session_id ile zincirleniyor

sonra session_search child session'lari root'a resolve ediyor.

neden iyi:
- audit bozulmuyor
- transcript kaybolmuyor
- compression sonrasi da onceki rich history aranabilir kaliyor

Purr icin bu baya degerli:
- long relationship history tek duz transcript olmamali
- session/episode lineage tutulmali
- ama user-facing memory hala tek Purr gibi hissettirmeli

### 6. compression structural integrity koruyor
cogu sistem summary yaparken tool-call yapisini bozuyor.
Hermes burada dikkatli:
- tool_call / tool_result gruplarini boundary'de bolmemeye calisiyor
- orphan tool result'lari temizliyor
- eksik result icin stub ekliyor
- API bozulmasin diye message yapisini onariyor

neden onemli:
- memory/recall sistemleri sadece semantik degil operasyonel olarak da ayakta kalmali

Purr dersi:
- background cognition / hidden tools varsa
- archive/compression/summarization pipeline message-graph integrity'yi bozmayacak

### 7. retrieval = search sonra summarize
Hermes past recall'da tum transcript'i prompta yigmak yerine:
- FTS5 ile candidate buluyor
- uygun session'lari secip
- ucuz modelle summarize ediyor
- ana modele focused recap veriyor

neden iyi:
- long-tail memory hot prompta tasinmiyor
- ucuz
- kullanisli

ama limiti var:
- lexical first
- summary second
- structured truth yok

Purr icin ders:
- `search -> pack -> cite` mantigi olmali
- raw dump degil
- ama sadece summarization'a guvenmek de yetmez

### 8. memory ve context prompt-injection surface sayiliyor
Hermes memory content'i ve context file'lari scan ediyor:
- invisible unicode
- prompt injection kaliplari
- secret exfil pattern'lari

neden iyi:
- memory future prompt material
- yani bildigin attack surface

Purr icin net kural:
- user-derived summaries
- network-derived content
- Catnet/public text'ten cikan memory candidate'lari
prompta girmeden once sanitize edilmeli

---

## Hermes'in gizli kotu tarafi: bu design Purr'da direkt patlar

### 1. same-session staleness
Hermes bunu bilerek yapiyor.
cache icin.

ama Purr'da su kotu olur:
- user correction verdi
- Purr save etti
- ama hala eski seyi baz aliyor

bu assistant'ta tolere edilebilir.
`beni taniyan varlik` fantazisinde edilmez.

### 2. flat text memory ana truth olamaz
Hermes memory:
- delimiter'li text entry
- substring replace/remove
- no id
- no provenance
- no confidence
- no supersede graph
- no lifecycle

bu formatla Purr sunlari saglam yapamaz:
- identity drift tracking
- conflicting preference resolution
- episodic evidence linking
- pattern confidence
- stale review queue
- prediction justification

### 3. memory persistence hala heuristik
Hermes nudge + flush ile durumu toparliyor.
ama final karar hala buyuk oranda modelin tool call vermesine bagli.
flush da best-effort.

Purr icin bu zayif:
- candidate extraction deterministic-ish olmali
- save failure'lari gorunmez sekilde gecistirilmemeli
- high-value facts icin explicit capture pipeline lazim

### 4. lexical recall Purr depth'i icin yetersiz
FTS5 guzel ama:
- paraphrase
- fuzzy emotional pattern
- latent habit cluster
- `bu yine ayni kacis rutini`
gibi seylerde tek basina yetmez.

Purr lane:
- hybrid recall
  - structured filters first
  - semantic support second
  - transcript evidence third

### 5. current-session recall ile long-term recall ayri ada gibi
Hermes session_search current session'i skip ediyor.
bu Hermes mantiginda okay cunku current context zaten elde.

ama Purr'da:
- current turn memory
- this-week pattern memory
- last-month relationship memory
tek retrieval contract altinda olmalı

### 6. compression summary truth yerine gecme riski tasiyor
Hermes'te summary failure varsa middle turns drop bile olabiliyor.
summary olursa da kaynak yerine o summary kalıyor.

assistant icin okay-ish.
Purr icin risk:
- nuanced relationship details summary sludge'a doner
- wrong abstraction kalici hissedilebilir

Purr move:
- summaries are navigation aids
- not canonical truth
- canonical truth = ledger + evidence refs

---

## calmamiz gerekenler vs redesign etmemiz gerekenler

## direkt calmamiz gerekenler
- frozen session hot-pack mantigi
- pre-compression memory salvage pass
- transcript ile curated memory'nin ayrilmasi
- session lineage / parent-child continuation mantigi
- search -> summarize cost discipline
- reinjected content icin injection scanning
- compression'da structural integrity guard'lari

## redesign etmemiz gerekenler
- flat MEMORY.md / USER.md ana memory modeli
- substring replacement ile mutation
- same-session stale hot memory
- purely lexical search
- memory capture'in model insafina kalmasi
- contradiction'larin text coexistence ile yasamasi
- summaries'in truth yerine gecmesi

---

## Purr icin yeni net architecture consequence

Purr memory stack su sekilde olmalı:

### 1. canonical ledger
Supabase source-of-truth.
structured rows / records:
- memory_id
- owner_id
- purr_id
- kind
- state
- confidence
- salience
- provenance/evidence_refs
- created_at
- updated_at
- last_confirmed_at
- stale_at / needs_review_at
- supersedes / conflicts_with

### 2. session hot pack
session boyunca olabildigince stabil kalan compact pack:
- tone/identity frame
- durable relationship texture
- active preferences
- unresolved loops
- query'ye bagli 2-5 high-value memory

### 3. live turn override lane
session freeze var diye kritik correction'i bekletme.
small turn-level override lane lazim:
- direct contradiction
- fresh explicit correction
- high-value new preference
- safety-sensitive update

bunlar full prompt rebuild yapmadan active response'e girebilmeli.

### 4. salvage / consolidation jobs
background veya boundary job'lari:
- candidate extraction
- contradiction merge
- stale review scheduling
- session-end salvage
- compression-before-write salvage
- proactive timing refresh

### 5. recall contract
tek retrieval contract altinda:
- current session facts
- recent unresolved loops
- long-term structured memory
- semantic recall hits
- transcript evidence

tek sistem, farkli zaman ufuklari.

---

## code-worker icin net implication
build baslamadan once Hermes'ten alinacak ana thesis su:

`memory dosyasi degil, behavior pipeline tasarla.`

ilk build candidate'lar da bu thesis'e hizmet etmeli:
1. structured memory ledger
2. retrieval/context packer
3. contradiction + review loop
4. salvage/extraction worker

`chatbot memory` degil.
`memory operating system`.

---

## kisa verdict
Hermes bize su dersi veriyor:
- promptu stabilize et
- raw history'yi ayri tut
- recall'i on-demand yap
- compression'dan once memory kurtar
- future prompt material'i sanitize et

ama ayni zamanda su hatayi da gosteriyor:
- stale prompt memory
- flat text truth
- heuristic save behavior
- lexical recall ceiling

Purr'un yolu daha buyuk MEMORY.md degil.

Purr'un yolu:
- stable hot pack
- live structured ledger
- evidence-backed recall
- contradiction-aware memory lifecycle
- invisible background cognition
