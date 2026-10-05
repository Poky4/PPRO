# AGENTS.md – Pravidla a metodika práce AI asistenta

Tento dokument slouží jako závazný soubor pravidel a provozní metodiky pro AI agenta v rámci repozitáře semestrálního projektu **Rezervace v ordinaci** (PPRO, ZS 2026/2027).

---

## 1. O projektu (stručné shrnutí)

Projekt řeší informační systém pro soukromou lékařskou praxi (Varianta A – Rezervace v ordinaci). Systém nahrazuje papírový diář, zamezuje kolizím termínů, eviduje ordinační doby lékařů, pacienty, návštěvy a výkony pro pojišťovny.

* **Detailní technická dokumentace a zadání:** Viz kompletní dokument [README.md](file:///u:/PPRO/README.md).
* *Pravidlo:* Informace ze zadání se do tohoto dokumentu neduplikují; veškeré doménové a technické specifikace se udržují v `README.md`.

---

## 2. Závazná metodika a pravidla spolupráce

### 2.1 Schvalování postupů vývojářem (Klíčové pravidlo)
* **Žádná samovolná exekuce větších kroků:** Před zahájením jakéhokoliv nového funkčního celku, refaktoringu, volby technického stacku nebo zakládání komponent musí AI agent předložit jasný a strukturovaný návrh postupu vývojáři.
* **Čekání na souhlas:** Práce na implementaci začíná až po explicitním odsouhlasení navrženého plánu vývojářem.

### 2.2 Zaznamenávání architektonických rozhodnutí
* Všechna věcná rozhodnutí vzniklá během řešení otevřených bodů nebo specifikace klientky se průběžně zapisují a aktualizují v sekci **5. Deník rozhodnutí** v souboru [README.md](file:///u:/PPRO/README.md).
* Při jakékoliv změně zadání od vyučujícího/klienta se provede aktualizace zápisu s odůvodněním, proč byla změna provedena.

### 2.3 Technické a architektonické hranice
1. **Třívrstvá architektura:** Striktně jednosměrné závislosti (Prezentace → Aplikace/Doména → Data/Infrastruktura). Žádné přímé dotazy z UI do databáze.
2. **Databáze a migrace:** Relační databáze provozovaná v Dockeru, databázové schéma řízené verzovanými migracemi.
3. **Příkaz pro spuštění:** Celý projekt musí být kdykoliv spustitelný příkazem `docker compose up`.
4. **Syntetická data:** Přísný zákaz používání reálných osobních údajů (žádná reálná rodná čísla, jména ani kontakty).
5. **Bezpečnost repozitáře:** V repozitáři se nikdy nesmí objevit hesla, privátní klíče ani API tokeny.

### 2.4 Git workflow a čistota kódu
* Atomické, srozumitelně popsané commity v konvenci Conventional Commits (např. `feat:`, `fix:`, `docs:`, `test:`, `refactor:`).
* Žádný kód se nepovažuje za dokončený bez adekvátních testů ověřujících byznys logiku (překrývání termínů, kalkulace bodů, validace ordinačních hodin).
