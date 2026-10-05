# Rezervace v ordinaci (PPRO – Varianta A)

Semestrální projekt pro předmět **Pokročilé programování (PPRO)**, FIM UHK, ZS 2026/2027.

---

## 1. Kontext a zadavatel

* **Klient:** MUDr. Jana Hrubá, Ordinace Na Vyhlídce.
* **Provoz ordinace:** Soukromá praxe, tři lékaři na částečné úvazky a recepční (paní Věra).
* **Klientská základna:** Přibližně 900 pacientů, z toho polovina dochází pravidelně.

### Současný stav a problémy
* Aktuálně se používá **papírový diář na recepci**, kam se záznamy píší tužkou.
* Pacienti volají telefonem a recepční hledá volné termíny zdlouhavým listováním diářem.
* Při nemoci lékaře je nutné ručně dohledávat a obvolávat celý seznam dotčených pacientů.
* Na konci každého měsíce recepční ručně přepisuje vykázané výkony do tabulky pro zdravotní pojišťovny (zabírá celý podvečer).
* Za poslední rok došlo minimálně dvakrát k trapné chybě – na tentýž čas přišli do čekárny dva objednaní pacienti.

---

## 2. Specifikace požadavků

### 2.1 Co klient chce (Funkční požadavky)
1. **Evidence pacientů:**
   * Údaje: Jméno, příjmení, rok narození, telefonní číslo, identifikátor pojištěnce (číslo pojištěnce / rodné číslo), kód zdravotní pojišťovny.
   * Rychlé vyhledávání podle **příjmení** nebo **telefonního čísla** (klíčové při příchozím telefonátu).
2. **Lékaři a ordinační hodiny:**
   * Každý lékař má vlastní specifické ordinační dny a časové bloky.
   * Jeden z lékařů ordinuje v úterý odpoledne na jiné adrese – v tomto čase systém nesmí umožnit objednání do této ordinace.
3. **Rezervace na konkrétní termín u konkrétního lékaře:**
   * Rezervaci zakládá recepce.
   * Ke každé rezervaci se eviduje textová poznámka s důvodem návštěvy.
4. **Záznam o uskutečněné návštěvě:**
   * Při příchodu a ošetření pacienta se evidují provedené zdravotní výkony.
   * Výkony se vybírají ze spravovaného číselníku výkonů (kód výkonu, název, bodové ohodnocení).
   * V rámci jedné návštěvy může proběhnout více různých výkonů; tentýž výkon se může opakovat i u více pacientů/návštěv.
   * U výkonu lze evidovat počet vykázaných jednotek (např. 3 aplikace).
5. **Zrušení rezervace a sledování nespolehlivých pacientů:**
   * Zrušení termínu na žádost pacienta (telefonát).
   * Přehled/statistika pacientů, kteří termíny ruší opakovaně či nedorazí (např. „paní Krátká nepřišla letos pětkrát“).
6. **Přehled volných termínů (nejfrekventovanější funkce):**
   * Týdenní přehled kalendáře pro vybraného lékaře s okamžitou vizualizací volných a obsazených slotů.
7. **Měsíční výkaz pro pojišťovnu:**
   * Generování měsíčního souhrnu za zvoleného lékaře a měsíc: seznam provedených výkonů a celkový součet bodů pro pojišťovny.

---

### 2.2 Na čem klient trvá (Obchodní pravidla – striktně vynucená systémem)
* **Kolidující rezervace jsou zakázány:** Dvě rezervace na stejný čas u stejného lékaře nesmí jít založit za žádných okolností (ani omylem, ani ručním zásahem).
* **Dodržení ordinačních hodin:** Rezervaci nelze vytvořit mimo platné ordinační hodiny daného lékaře.
* **Integrita návštěv:** Výkon nelze přiřadit k návštěvě/termínu, který se ještě neuskutečnil.
* **Nevratnost historie (zákaz mazání):** Historie ošetření a záznamů pacienta se nesmí fyzicky smazat z databáze (z důvodu právní a lékařské doložitelnosti zákroků).

---

### 2.3 Co klient prohodil mimochodem (Ergonomie, UX a budoucí rozšíření)
* **Jednoduchost pro recepční:** Systém musí být maximálně přívětivý pro paní Věru, která s počítačem příliš nekamarádí (čisté UI, velká tlačítka, minimum kroků).
* **Okamžitá odezva:** Při zvonícím telefonu nesmí recepční čekat na načítání – vyhledávání pacientů a zobrazení volných slotů musí být bleskové.
* **Tabletové zobrazení:** Přívětivé zobrazení na tabletu je vítané pro budoucí nahlížení lékařů v ordinaci, ale pro první etapu nespěchá.
* **Samoobslužné objednávání pacientů přes web:** Klient o něm uvažuje s obavami; v první verzi je primární správa přes recepci, ale doménový model by neměl online rezervacím v budoucnu bránit.

---

### 2.4 Co klient nemá dořešené (Otevřené body)
1. **Délka jednoho termínu:** Zda má být diář členěn do pevné časové mřížky (např. sloty po 15 minutách), nebo má mít rezervace individuální délku dle typu zákroku.
2. **Kdo zakládá rezervaci:** Výhradně recepce vs. možnost budoucího online objednání pacienty z domova.
3. **Životní cyklus zrušené rezervace:** Požadavek na uvolnění termínu v diáři vs. zachování záznamu pro statistiku častých rušení.
4. **Jednoznačná identifikace pacienta:** Prevence duplicit v evidenci (problém typu „paní Nováková je v diáři třikrát“).
5. **Postup při nemoci lékaře:** Zda má systém termíny hromadně zrušit, automaticky přesunout na jiného lékaře, nebo pouze označit k ručnímu přeobjednání recepcí.

---

## 3. Společné technické minimum (PPRO)

* **Architektura:** Třívrstvá architektura se striktně jednosměrnými závislostmi:
  * *Prezentační vrstva (UI / API / Web)*
  * *Aplikační / Byznys vrstva (Services, Use Cases)*
  * *Datová vrstva (Repositories, Entity, DB kontext)*
* **Databáze:** Relační databáze běžící v Docker kontejneru se správou schématu pomocí migrací.
* **Doménový model:** Minimálně 5 entit a alespoň jedna vazba M:N.
* **Testování:** Sada unit a integračních testů ověřujících klíčová byznys pravidla (zejména kolize termínů a výkazy).
* **Kontejnerizace:** Spuštění kompletního aplikačního prostředí jediným příkazem:
  ```bash
  docker compose up
  ```
* **Bezpečnost a data:** Výhradně syntetická testovací data (žádná reálná rodná čísla ani osobní údaje), žádná hesla ani citlivé API klíče v repozitáři.

---

## 4. Návrh klíčových entit a vazeb

Předpokládaný model pokrývá minimálně následující entity a vztahy:
1. `Pacient` – osobní a kontaktní údaje, číslo pojištěnce, kód pojišťovny.
2. `Lekar` – jméno, titul, specializace, barva pro kalendář.
3. `OrdinacniDoba` – týdenní šablona ordinačních hodin konkrétního lékaře (den v týdnu, platnost od-do, ordinace/lokace).
4. `Rezervace` – vazba na lékaře, pacienta, datum a čas od-do, stav (Plánováno, Dokončeno, Zrušeno), poznámka.
5. `Navsteva` – záznam o uskutečněném ošetření navázaný na rezervaci, čas příchodu, souhrnná zpráva.
6. `Vykon` – číselník výkonů (kód, název, počet bodů).
7. `NavstevaVykon` (Vazební entita M:N) – propojení návštěvy a vykázaného výkonu včetně počtu aplikací (`pocet`).

---

## 5. Deník rozhodnutí (Rozhodnutí / Decisions Log)

V souladu s metodikou zadání zde evidujeme konkrétní rozhodnutí k otevřeným bodům klienta. Každé rozhodnutí má jasné odůvodnění:

* **[ROZHODNUTÍ-01] Délka termínu a členění diáře:**
  * *Rozhodnutí:* Základní mřížka diáře bude nastavena na fixní 15minutové bloky, přičemž délku rezervace lze při zakládání nastavit jako celistvý násobek tohoto bloku (15, 30, 45, 60 min dle typu výkonu).
  * *Důvod:* Zajišťuje přehlednost kalendáře pro paní Věru bez vzniku drobných nepřehledných mezer a zároveň poskytuje flexibilitu pro delší výkony.
* **[ROZHODNUTÍ-02] Oprávnění k zakládání rezervací:**
  * *Rozhodnutí:* V první etapě bude tvorba rezervací umožněna výhradně personálu recepce (interní rozhraní). Doménová vrstva a API však budou navrženy odděleně, aby bylo možné v budoucnu napojit samoobslužný veřejný portál.
  * *Důvod:* Respektuje obavu klientky ze zmatků v diáři a zaručuje bezchybný start ordinace pod dohledem recepční.
* **[ROZHODNUTÍ-03] Životní cyklus a zachování zrušených rezervací:**
  * *Rozhodnutí:* Zrušená rezervace se neodstraňuje z databáze, nýbrž se přepne do stavu `ZRUŠENA` s evidencí data a důvodu storna. Kalendářový dotaz na volné sloty filtruje pouze aktivní rezervace (slot se v diáři uvolní), zatímco v profilu pacienta a statistikách zůstává historie zrušení plně zachována.
  * *Důvod:* Elegantně řeší zdánlivý rozpor v zadání – termín je okamžitě volný pro dalšího pacienta a klient neztrácí statistiku o nespolehlivých pacientech.
* **[ROZHODNUTÍ-04] Jednoznačná identifikace pacienta a duplicity:**
  * *Rozhodnutí:* Jednoznačným přirozeným identifikátorem pacienta v systému bude kombinace čísla pojištěnce (obvykle RČ) a kódu pojišťovny. Při pokusu o zápis pacienta se stejným číslem systém vyvolá upozornění na existující kartu a nabídne její otevření namísto duplicitního zápisu.
  * *Důvod:* Zabraňuje vzniku vícenásobných karet jedné osoby („paní Nováková třikrát“) a zaručuje správnost vykazování pojišťovnám.
* **[ROZHODNUTÍ-05] Řešení nemoci lékaře:**
  * *Rozhodnutí:* Při nahlášení výpadku lékaře systém umožní označit termíny v daném období stavem `POŽADUJE_PŘEPLÁNOVÁNÍ` a vygeneruje recepční prioritní přehledný pracovní seznam pacientů k obvolání s možností jedním klikem termín přeobjednat či zrušit.
  * *Důvod:* V medicínském prostředí nelze pacienty svévolně automaticky přesouvat k jiným lékařům bez jejich souhlasu; recepční získá nástroj, který jí ušetří čas a zajistí, že na nikoho nezapomene.
