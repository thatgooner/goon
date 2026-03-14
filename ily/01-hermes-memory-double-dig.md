# Hermes memory — double deep dig

## quick verdict
Hermes memory kotu degil.
ama consumer-grade purr memory icin anca 6/10.

gucu:
- layered
- ucuz
- durable
- disciplined

zayifligi:
- fazla flat
- fazla global
- contradiction/state/confidence zayif
- rich relationship memory icin yetersiz

## Hermes neyi dogru yapiyor

### 1. layered memory mantigi
Hermes'te 3 ana lane var:
- kucuk hot memory (`MEMORY.md`, `USER.md`)
- full transcript history (`state.db`)
- gerekince recall (`session_search`)

bu cok dogru.
raw history ile usable memory ayni sey degil.

### 2. frozen snapshot
memory promptu session basinda yukleniyor ve sabit kaliyor.
mid-session memory disk'e yaziliyor ama prompt hemen degismiyor.

neden iyi:
- prompt cache bozulmuyor
- maliyet kontrolu iyi
- her turn prompt tekrardan rebuild olmuyor

bunu purr'a kesin calmaliyiz.

### 3. bounded memory
char limit var.
memory'yi prompt coplugune cevirmiyor.

neden iyi:
- butce belli
- kaliteyi zorla yukari cekiyor
- her seyi hot layera atma deliligini kesiyor

### 4. transcript store ayri
transcript baska, curated memory baska.

neden iyi:
- her seyi promptta tutmaya calismiyor
- uzun vade recall on-demand geliyor

### 5. proactive memory capture denemesi
Hermes, compression/reset oncesi memory flush yapmaya calisiyor.

neden iyi:
- context kaybolmadan once son kez `bunu save et` deme sansi veriyor

## Hermes niye 6/10'da kaliyor

### 1. same-session memory stale kaliyor
memory yazilsa bile ayni sessionda hot prompt aninda guncellenmiyor.

sonuc:
- kullanici `bunu duzelttim` der
- sistem onu kaydetse bile hemen hissedilmeyebilir

### 2. flat note mantigi
memory entry'ler duz text blok gibi.

eksik olan seyler:
- state
- confidence
- salience
- evidence refs
- last confirmed
- stale / rejected / candidate mantigi

### 3. contradiction handling zayif
`kisa cevap ver`
sonra
`aciklama istersem uzun anlat`

gibi durumlarda structured supersede mantigi yok.

### 4. global mindset
tek agent/single-user lane icin okay.
product icin zayif.
1 human = 1 purr modelinde per-user / per-purr namespace lazim.

### 5. recall daha cok lexical
FTS5 iyi ama semantic degil.
paraphrase / fuzzy emotional recall icin yetmez.

### 6. rich relationship memory yok
Hermes assistant continuity yapiyor.
Purr ise:
- inside jokes
- emotional patterns
- recurring wounds
- relationship dynamics
- next move prediction
isteyecek.

## Hermes'ten neyi calmaliyiz
- layered memory philosophy
- frozen hot-memory snapshot
- bounded prompt pack
- transcript store ayri tutma
- proactive flush / capture moments
- memory security scanning

## Hermes'ten neyi birebir almamaliyiz
- flat MEMORY.md / USER.md ana sistem olsun fikri
- no-state/no-confidence memory
- pure lexical recall
- global namespace
- substring ile memory edit etme ana model olsun fikri

## purr icin sonuc
Purr'un yolu `bigger MEMORY.md` degil.

Dogru yol:
- structured ledger
- compact hot pack
- transcript/raw store
- recall/ranking layer
- correction + verification loop
- candidate / confirmed / rejected / stale lifecycle
