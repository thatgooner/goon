# code-worker first run checklist

ilk run'da bunu yap. build'e atlama.

## 1. sync
- `git pull --rebase origin main`

## 2. oku
- `notes/boards/system-board.md`
- `notes/boards/weekly-missions.md`
- `notes/boards/hermes-memory-review.md`
- `notes/boards/purr-alignment-brief.md`
- `notes/boards/coding-agent-task-board.md`
- `ily/README.md`
- `ily/00-project-brief.md`
- `ily/01-hermes-memory-double-dig.md`
- `ily/02-purr-app-memory-architecture.md`
- `ily/03-catnet-markets.md`
- `ily/04-open-questions.md`

## 3. anlaman gerekenler
- Purr = cat skinli assistant degil
- memory = product
- current phase = research-first
- visible tool-call theater yok
- Catnet autonomous olacak
- private-human behavior marketleri yasak lane

## 4. ilk run outputu ne olsun
tek bir cycle log yaz ve su 4 basligi cevapla:
- Hermes'ten neyi calmaliyiz?
- Hermes'ten neyi almamaliyiz?
- Purr'u builder gozuyle bir cumlede nasil tarif edersin?
- first implementation slice ne olmali ve neden?

## 5. yasaklar
- tools/ altinda yeni build yok (simdilik)
- archived Moltbook lane'i revive etmek yok
- hermes/memories'e dokunmak yok
- fake progress yok

## 6. commit
research ise commit prefix:
- `notes:`
veya
- `research:`
