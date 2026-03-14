# purr app + memory architecture

## target
memory o kadar iyi olmali ki:
- user'in patternlerini yakalasin
- next move'unu tahmin etsin
- ne zaman roast / ne zaman soru / ne zaman sessiz kalacagini bilsin
- bunu yaparken prompt cost'u patlatmasin

## main layers

### 1. raw layer
- messages
- sessions
- notification events
- app actions
- future tool outputs

ham veri burada.

### 2. ledger layer
Supabase source of truth.

burada structured memory item'lari olacak:
- profile
- preference
- fact
- episode
- relationship
- uncertainty
- open loop
- pattern signal
- next-action candidate

her item'da ideal olarak su alanlar olur:
- id
- owner_id
- purr_id
- kind
- state
- confidence
- salience
- created_at
- updated_at
- last_confirmed_at
- evidence_refs
- supersedes / conflicts_with
- needs_review_at

state'ler:
- candidate
- confirmed
- rejected
- stale

### 3. retrieval layer
butun memory prompta gitmez.
retrieval secerek getirir.

rank sinyalleri:
- relevance
- recency
- confidence
- salience
- unresolved/open loop durumu
- direct contradiction

vector burada yardimci olabilir.
ana sistem degil.

### 4. hot pack layer
LLM'e giden compact memory package.

icerik:
- core identity / tone / hard constraints
- active preferences
- current relationship texture
- unresolved loops
- query'ye en alakali 2-5 episodic item

bu layer bounded olmali.

### 5. background cognition
kullanici gormeden arkada donebilecek isler:
- candidate extraction
- duplicate merge
- confidence update
- stale review scheduling
- next-action prediction refresh
- optional semantic embedding jobs

## turn pipeline
1. user message gelir
2. fast classifier/extractor candidate memory cikarir
3. existing beliefs ile compare edilir
4. ask_now / defer / silent_store / drop karari verilir
5. retrieval current turn icin pack uretir
6. response uretilir
7. arkada consolidation calisabilir

## next-move prediction nasil olur
prediction magic degil.
pattern + open loops + recency.

ornek sinyaller:
- gece 2'de hep ayni topicte donuyorsa
- ayni bahane kalibini kullaniyorsa
- x konu acilinca sonra y soru geliyorsa
- her stresli anda ayni playlist / ayni doomscroll patterni varsa

prediction outputs:
- likely next ask
- likely mood
- likely follow-up topic
- proactive ping opportunity

## tool meselesi

### internal tools
bence evet.
arkada kullaniriz:
- memory extraction
- contradiction resolver
- retrieval packer
- review scheduler
- Catnet heartbeat planner

### user-facing tools
v1'de buyuk ihtimalle hayir.
kullanici `tool` hissetmesin.
ilerde belki:
- memory export
- memory correction UI
- `why do you think that?` style transparency card
ama primary interface tool panel degil chat olmalı.

## cost optimization
- stable system prompt
- small hot pack
- heavy memory work bg'de
- cheap model for extraction/summarization
- stronger model only for response or hard conflict resolution
- event-driven recompute, her turn full recompute degil
- cold storage vs hot package ayrimi

## free credits thought
free usersi memory'den degil throughput'tan kis.

yani:
- memory quality kalsin
- belki stronger model sayisi limitli olsun
- bg ağır işler batchlensin
- proactive messaging rate-limitli olsun

## direct result
Purr icin esas infra:
- great memory ledger
- great retrieval
- great correction loop
- great timing

LLM tek basina yetmez.
memory orchestration quality isi belirler.
