Cvičenie 8
==========

**Riešenie odovzdávajte podľa
[pokynov na konci tohoto zadania](#technické-detaily-riešenia)
do stredy 2.5. 23:59:59.**

Súbory potrebné pre toto cvičenie si môžete stiahnuť ako jeden zip
[`cv08.zip`](https://github.com/FMFI-UK-1-AIN-412/lpi/archive/cv08.zip).

SAT solver (4b)
----------

Naprogramujte SAT solver, ktorý zisťuje, či je vstupná formula (v konjunktívnej
normálnej forme) splniteľná.

Na prednáške bola základná kostra DPLL metódy, ktorej hlavnou ideou je
propagácia klauzúl s iba jednou premennou (_jednotková klauzula_, <i lang="en">unit clause</i>). Tá ale hovorí o veciach
ako *vymazávanie literálov* z klauzúl a *vymazávanie klauzúl*, čo sú veci, ktoré nie
je také ľahké efektívne (či už časovo alebo pamäťovo) implementovať, hlavne ak
počas <i lang="en">backtrack</i>ovania treba zmazané literály resp. klauzuly správne naspäť
obnovovať.

Ukážeme si preto jednoduchú modifikáciu DPLL metódy, ktorá výrazne zjednodušuje
„menežment“ literálov, klauzúl a dátových štruktúr.

## Sledované literály (<i lang="en">watched literals</i>)

Základným problémom pri DPLL metóde je vedieť povedať, či už klauzula obsahuje
nejaký literál ohodnotený `true` (a teda je už _splnená_), ak nie, tak či obsahuje
práve jeden neohodnotený literál (a teda je _jednotková_), alebo či už sú všetky literály
`false` (a teda je _nesplnená_ a treba <i lang="en">backtrack</i>ovať).

Namiesto mazania / obnovovania literálov a klauzúl budeme v každej klauzule _sledovať_ (označíme si)
dva jej literály (<i lang="en">watched literals</i>), pričom budeme požadovať (pokiaľ je to možné), aby každý z nich
- buď ešte nemal priradenú hodnotu,
- alebo mal priradenú hodnotu `true`.

Ak nejaký literál počas prehľadávania nastavíme na `true`, tak očividne nemusíme
nič meniť. Ak ho nastavíme na `false` (lebo sme napríklad jeho komplement (negáciu) nastavili
na `true`), tak pre každú klauzulu, v ktorej je sledovaný, musíme nájsť nový
literál, ktorý spĺňa horeuvedené podmienky. Môžu nastať nasledovné možnosti:
- našli sme iný literál, ktorý je buď nenastavený, alebo je `true`, odteraz
  sledujeme ten,
- nenašli sme už literál, ktorý by spĺňal naše podmienky (všetky ostatné sú
 `false`):
    - ak druhý sledovaný literál bol `true`, tak to nevadí (klauzula je aj tak splnená),
    - ale ak bol druhý literál _nenastavený_, tak nám práve vznikla jednotková klauzula, a mali by sme ho
      nastaviť na `true`.
    - podľa toho, ako presne implementujeme propagáciu, sa nám môže stať, že sa
      dostaneme do momentu, že aj druhý sledovaný literál sa práve stal `false`,
      v tom prípade sme práve našli nesplnenú klauzulu a musíme <i lang="en">backtrack</i>ovať.

Bonus navyše: ak <i lang="en">backtrack</i>ujeme (meníme nejaký `true` alebo `false` literál naspäť
na nenastavený), tak nemusíme vôbec nič robiť (so sledovanými literálmi v klauzulách;
samotný literál / premennú samozrejme musíme korektne „odnastaviť“).

Dosť podrobný pseudokód riešenia:

```
solve:
  readInput() # nacita clauses, vyrobi (nenastavene) vars
  if not initWatchedLiterals():
    return false
  if not unitPropagate():
    return false
  return dpll()

dpll:
  if all vars are assigned:
    return true
  branchLit = chooseBranchLiteral()

  for lit in branchLit and -branchLit: # backtracking
    setLiteral(lit)
    unitPropagate()
    dpll()
    unsetLiterals()

initWatchedLiterals:  # returns false if it finds a conflict / UNSAT
  for each clause c:
    if c is empty:
      return false
    if len(c) == 1:
      c.w1 = c.w2 = c[0] # watch the same lit
      append c[0] to unitLiterals
    else:
      c.w1 = c[0], c.w2 = another lit from c different then c[0]
  return true

unitPropagate:  # returns false if it finds a conflict / UNSAT
  while unitLiterals not empty:
    take lit from unitLiterals
    if not setLiteral(lit):
      return false
  return true

setLiteral(lit):  # returns false if it finds a conflict / UNSAT
  set lit to true (-lit to false)
  for each clause c in which -lit is watched:
    let c.w1 be -lit, c.w2 be the other watched literal
    if can't find new watched literal for c.w1 (instead of -lit) in c:
      if c.w2 is set to to false:
        return false  # all are false in this clause
      if c.w2 is unset:
        # c.w2 is the last unset, no true literals -> unit propagate on c.w2
        add c.w2 to unitLiterals
      # else other is set to true, this is a satisfied clause, leave it be
  return true

unsetLiterals():
  for lit in literals that have been set on this recursion level
    unsetLiteral(lit)

unsetLiteral(lit):
  set lit and -lit to unset
  nothing else to do...
```
V tomto pseudokóde sa samozrejme neriešia implementačné „drobnosti“ ako reprezentovať
literály a premenné, ako si pamätať, ktoré literály sú sledované (watched) v klauzule
a v ktorých klauzulách je sledovaný daný literál, ako vedieť, ktoré premenné / literály
odnastaviť atď.

## Technické detaily riešenia

Riešenie odovzdajte do vetvy `cv08` v adresári `cvicenia/cv08`.
Odovzdávajte (modifikujte) súbor `satsolver.py`, resp. `satsolver.cpp`, `SatSolver.java`.
Program [`satTest.py`](satTest.py) otestuje váš solver na rôznych vstupoch
(z adresára `testData`). Testovač by mal automaticky detegovať Python / C++ / Java
riešenia prítomné v adresári.

Vaším riešením má byť konzolový program (žiadne GUI), ktorý dostane dva
argumenty: meno vstupného a výstupného súboru. Vstupný súbor bude v DIMACS
formáte s korektnou hlavičkou (môže obsahovať komentáre).

Do výstupného súboru váš program zapíše na prvý riadok buď `SAT` alebo `UNSAT`,
podľa toho, či je formula splniteľná. Ak je formula splniteľná, tak na druhý
riadok zapíše model (spĺňajúce ohodnotenie): medzerami oddelené čísla s
absolútnymi hodnotami 1, 2, … až najväčšia premenná. Kladné číslo znamená, že
premenná je nastavená na `true` a záporné, že je nastavená na `false`.
V predpripravenom `satsolver.py` už je implementované korektné načítavanie a zápis riešenia.

Za korektný beh programu sa považuje iba keď váš program skončí s návratovou hodnotou 0,
nenulová hodnota sa považuje za chybu (Runtime Error). Toto je dôležité hlavne v C++
(`return 0;` na konci `main`), ak Python korektne skončí, tak by mal vrátiť 0.

Môžete predpokladať, že počet premenných bude do 2048.

### Python
Python má limit na počet rekurzívnych volaní funkcií (maximálna hĺbka <i lang="en">stack</i>-u).
Štandardne je to 1000 vo väčšine implementácií.  Keďže naša DPLL metóda je
rekurzívna, môžete ho ľahko dosiahnuť. Dá sa zväčšiť príkazom
[sys.setrecursionlimit](https://docs.python.org/3.3/library/sys.html#sys.setrecursionlimit).

### C++
Odovzdávajte program `satsolver.cpp`, ktorý musí byť skompilovateľný príkazom
`g++ -Wall --std=c++11 -o satsolver *.cpp`.

### Java
Odovzdávajte program `SatSolver.java`, ktorý implementuje triedu `SatSolver` s
`main` metódou. Kód musí byť skompilovateľný príkazom
`javac SatSolver.java`.

Odovzdávanie riešení v iných jazykoch konzultujte s cvičiacimi.
