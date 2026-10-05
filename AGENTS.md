# AGENTS.md – Pravidla a metodika práce AI asistenta

Tento dokument slouží jako závazný soubor pravidel, architektonických mantinelů a provozní metodiky pro AI agenta v rámci repozitáře semestrálního projektu **Rezervace v ordinaci** (PPRO, ZS 2026/2027).

---

## 1. O projektu (stručné shrnutí)

Projekt řeší informační systém pro soukromou lékařskou praxi (Varianta A – Rezervace v ordinaci). Systém nahrazuje papírový diář, zamezuje kolizím termínů, eviduje ordinační doby lékařů, pacienty, návštěvy a výkony pro pojišťovny.

* **Detailní technická dokumentace a zadání:** Viz kompletní dokument [README.md](file:///u:/PPRO/README.md).
* *Pravidlo:* Informace ze zadání se do tohoto dokumentu neduplikují; veškeré doménové a technické specifikace se udržují a rozvíjejí v [README.md](file:///u:/PPRO/README.md).

---

## 2. Závazná pravidla spolupráce s vývojářem

### 2.1 Proaktivní kladení dotazů a ujasňování (Inquiring First)
* **Zákaz tichého domýšlení:** Pokud je v zadání cokoliv nejednoznačného, neúplného nebo otevřeného k interpretaci (např. workflow, chování na hraně, UX detaily, výchozí hodnoty), AI agent **musí proaktivně položit sadu konkrétních ujasňujících otázek**.
* **Strukturované dotazy:** Otázky mají nabízet konkrétní varianty, scénáře a jejich dopady, aby vývojář mohl snadno a rychle rozhodnout.
* Otázky se kladou **před zahájením práce**, nikoliv po napsání kódu.

### 2.2 Zákaz samostatných zásadních architektonických rozhodnutí
* **Striktní zákaz svévolných rozhodnutí:** AI agent nesmí provést žádné klíčové architektonické ani technologické rozhodnutí samostatně (volba konkrétního programovacího jazyka/frameworku, ORM, schéma databáze, autorizační model, transakční strategie, struktura modulů atd.).
* **Předložení alternativ:** Vždy nejprve předloží strukturovaný přehled možností (výhody, nevýhody, pracnost, dopad na projekt a podmínky PPRO) a **vyčká na výslovné potvrzení vývojáře**.

### 2.3 Schvalování postupů vývojářem
* **Plánování před akcí:** Před zahájením jakéhokoliv nového funkčního celku, refaktoringu nebo zakládání komponent musí AI agent předložit jasný a strukturovaný plán kroků.
* **Čekání na souhlas:** Implementace začíná až po schválení navrženého postupu vývojářem.

### 2.4 Zaznamenávání architektonických rozhodnutí
* Všechna věcná rozhodnutí (zejména řešení otevřených bodů ze zadání nebo reakce na změny požadavků) se průběžně zapisují a aktualizují v sekci **5. Deník rozhodnutí** v souboru [README.md](file:///u:/PPRO/README.md).
* Každý záznam musí obsahovat: co bylo rozhodnuto, jak a proč (odůvodnění).

---

## 3. Technické a architektonické hranice projektu

1. **Třívrstvá architektura:**
   * Striktně jednosměrný tok závislostí: Prezentace (UI/API) → Aplikace/Doména (Use Cases, Services) → Data/Infrastruktura (Repositories, DB).
   * Žádné přímé volání databáze z prezentační vrstvy. Doménové entity nevystavovat přímo do UI (využívat DTO / View Modely).
2. **Databáze a migrace:**
   * Relační databáze provozovaná výhradně v Dockeru.
   * Schéma musí být řízeno verzovanými migracemi, nikoliv ad-hoc zásahy.
3. **Příkaz pro spuštění:**
   * Celý projekt (aplikace i databáze) musí být kdykoliv spustitelný jediným příkazem:
     ```bash
     docker compose up
     ```
4. **Syntetická data:**
   * Přísný zákaz používání reálných osobních údajů (žádná reálná rodná čísla, jména ani kontakty). Všechna seed data musí být generovaná/fiktivní.
5. **Bezpečnost a tajemství:**
   * Do repozitáře nikdy nepatří hesla, privátní klíče ani API tokeny. Využívat konfigurační šablony (např. `.env.example`).

---

## 4. Inženýrské best practices a čistota kódu

### 4.1 Doménová integrita a transakce
* **Invarianty u rezervací:** Zákaz překrývání termínů a dodržení ordinačních hodin musí být garantováno na úrovni byznys logiky i databáze (např. unikátní indexy, transakční zámky).
* **Auditovatelnost historie:** Zdravotnická historie pacienta se fyzicky nemaže; používá se soft delete nebo stavový mechanismus.

### 4.2 Testování
* Žádný kód se nepovažuje za dokončený bez adekvátních automatizovaných testů.
* Primární zaměření na testy doménové logiky:
  * Detekce kolizí v rezervacích (hraniční časy, stejný lékař, jiný lékař).
  * Validace ordinačních hodin.
  * Správnost kalkulace měsíčních výkazů a bodů.

### 4.3 Git workflow a čistota kódu
* Atomické, srozumitelně popsané commity v konvenci Conventional Commits (`feat:`, `fix:`, `docs:`, `test:`, `refactor:`).
* Žádný zbytečný dead code, testovací skripty ani dočasné soubory v commitnutém stromu.
* Před commitem vždy zkontrolovat git diff a konzistenci formátování.
