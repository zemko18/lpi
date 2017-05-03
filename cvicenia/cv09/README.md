Cvičenie 09
===========

**Riešenie odovzdávajte podľa
[pokynov na konci tohoto zadania](#technické-detaily-riešenia)
do stredy 9.5. 23:59:59.**

Všetky ukážkové a testovacie súbory k tomuto cvičeniu si môžete stiahnuť
ako jeden zip súbor
[cv09.zip](https://github.com/FMFI-UK-1-AIN-412/lpi/archive/cv09.zip).

## FolFormula (4b)

Vytvorte objektovú hierarchiu na reprezentáciu prvorádových formúl.
Zadefinujte základné triedy `Term` a `Formula` a od nich odvodené pre
jednotlivé typy termov a formúl.

Všetky triedy naprogramujte ako knižnicu podľa
[pokynov na konci tohoto zadania](#technické-detaily-riešenia).

```
Term
 │  constructor(...)
 │  subts() -> Array of Term      // vrati vsetky "priame" podtermy
 │  name() -> String              // vrati nazov termu (i.e. premennej, konst., funkcie)
 │  toString() -> String          // vrati retazcovu reprezentaciu termu
 │  equals(Term other) -> Bool    // vrati true ak je tento term rovnaky ako other
 │  variables() -> Set of String  // vrati mnozinu mien premennych
 │  constants() -> Set of String  // vrati mnozinu mien konstant
 │  functions() -> Set of String  // vrati mnozinu mien funkcii
 │  eval(Structure m, Valuation e) -> m.domain  // vrati hodnotu termu v m pri e
 │  substitute(String var, Term t)              // substituuje term t za vsetky vyskyty
 │                                              // premennej var v tomto terme
 │
 ├─ Variable
 │      constructor(String name)
 │
 ├─ Constant
 │      constructor(String name)
 │
 └─ Function
        constructor(String name, Array of Term subts))

Formula
 │  constructor()
 │  subfs() -> Array of Formula   // vrati vsetky priame podformuly ako pole
 │  toString() -> String          // vrati retazcovu reprezentaciu formuly
 │  equals(Formula other) -> Bool // vrati true ak je tato formula rovnaka ako other
 │  variables() -> Set of String  // vrati mnozinu mien premennych
 │  constants() -> Set of String  // vrati mnozinu mien konstant
 │  functions() -> Set of String  // vrati mnozinu mien funkcii
 │  predicates() -> Set of String // vrati mnozinu mien predikatov
 │  isSatisfied(Structure m, Valuation e) -> Bool  // vrati true, ak je formula
 │                                                 // splnena ohodnotenim v m pri e
 │  freeVariables() -> Set of String   // vrati mnozinu vsetkych volnych premennych
 │                                     // v tejto formule
 │  substitute(String var, Term t)     // substituuje term t za vsetky volne vyskyty
 │                                     // premennej var, vyhodi vynimku ak substitucia
 │                                     // nie je aplikovatelna
 │
 ├─ Predicate
 │      constructor(String name, Array of Term subts)
 │      name() -> String          // vrati meno premennej
 │      subts() -> Array of Term  // vrati termy, ktore su argumentami tohoto predikatu
 │
 ├─ Negation
 │      constructor(Formula originalFormula)
 │      originalFormula() -> Formula // vrati povodnu formulu
 │                                   // (jedinu priamu podformulu)
 │
 ├─ Disjunction
 │      constructor(Array of Formula disjuncts)
 │
 ├─ Conjunction
 │      constructor(Array of Formula conjuncts)
 │
 ├─ BinaryFormula
 │   │  constructor(Formula leftSide, Formula rightSide)
 │   │  Formula leftSide()    // vrati lavu priamu podformulu
 │   │  Formula rightSide()   // vrati pravu priamu podformulu
 │   │
 │   ├─ Implication
 │   │
 │   └─ Equivalence
 │
 └─ QuantifiedFormula
     │  constructor(String qvar, Formula originalFormula)
     │  originalFormula() -> Formula  // vrati povodnu formulu
     │  qvar() -> String              // vrati meno kvantifikovanej premennej
     │
     ├─ ForAll
     │
     └─ Exists
```

Samozrejme použite syntax a základné typy jazyka, ktorý používate (viď
príklady použitia knižnice na konci).

Metóda `toString` vráti reťazcovú reprezentáciu termu / formuly podľa
nasledovných pravidiel:
- `Variable`: reťazec `x`, kde `x` je meno premennej (môže byť
  viacpísmenkové)
- `Constant`: reťazec `c`, kde `c` je meno konštanty (môže byť
  viacpísmenkové)
- `Function`:  reťazec `funcName(T1,T2,T3...)`, kde `funcName` je meno funkcie
  a `T1`, `T2`, `T3`, ... sú  reprezentácie argumentov (termov) funkcie
  (funkcia s nula argumentami ma reprezentáciu `funcName()`).
- `Predicate`:  reťazec `predName(T1,T2,T3...)`, kde `predName` je meno predikátu
  a `T1`, `T2`, `T3`, ... sú  reprezentácie argumentov (termov) predikátu
  (predikát s nula argumentami ma reprezentáciu `predName()`).
- `ForAll`: reťazec `∀x F` kde `x` je meno kvantifikovanej premennej
  a `F` je reprezentácia podformuly.
- `Exists`: reťazec `∃x F` kde `x` je meno kvantifikovanej premennej
  a `F` je reprezentácia podformuly.

Ostatné typy formúl majú rovnakú reprezentáciu ako v [cvičení 3](../cv03/).

Metóda `eval` vráti hodnotu termu v danej štruktúre pri danon ohodnotení premenných.
Ak sa stane, že ohodnotenie neobsahuje nejakú premennú, ktorá sa vyskytne
v terme alebo štruktúra neobsahuje interpretáciu niektorého symbolu, tak môžete
buď vygenerovať chybu / výnimku alebo vrátiť ľubovoľnú hodnotu.
*Poznámka: Pri vyhodnocovaní funkčných symbolov získate zoznam vyhodnotených
podtermov, ktoré budete ale chcieť dosadiť ako argumenty do pythonovskej
funkcie (ktorú získate z  interpretácie funkčného symbolu). V pythone to
našťastie ide použítím `*args`, teda napríklad `value =
m.iF['functionName'](*evaluatedSubTerms)`.*


Metóda `isSatisfied` vráti `True` alebo `False` podľa toho, či je formula splnená
v danej štruktúre pri danom ohodnotení premenných. Ak sa stane, že ohodnotenie
neobsahuje nejakú premennú, ktorá sa vyskytne vo formule alebo štruktúra
neobsahuje interpretáciu niektorého symbolu, tak môžete buď vygenerovať chybu /
výnimku alebo ju považovať za `False`.


Metóda `freeVariables` vráti množinu názvov všetkých voľných premenných vo formule.
Voľné premenné sú také, ktoré nie sú viazané žiadnym kvantifikátorom, t.j. vo formule

```
(P(x,x) -> ∀x∃y(Q(x,z)-> P(z,y)))
```
sú voľné premenné `z` a `x` (ale iba jej prvé dva výskyty mimo `∀x`).

Metóda `substitute` vráti **kópiu** formuly, v ktorej je každý voľný výskyt danej
premennej nahradený **kópiou** daného termu. Napríklad volanie
```python
`substitute('x', Function('f', [ Constant('c'), Variable('x') ]))
```
na predchádzajúcej formule by ju zmenilo na
```
(P(f(c,x),f(c,x)) -> ∀x∃y(Q(x,z)-> P(z,y))).
```

Všimnite si, že ani tretí výskyt `x` (viazaný kvantifikátorom `∀x`), ani „nové“
výskyty `x` už neboli ďalej nesubstituované.

Ak substitúcia nie je aplikovateľná, metóda `substitue` vyhodí výnimku (v pythone
`NotApplicable` z knižnice `folSemantics.py`, viď nižšie).

## Štruktúra a ohodnotenie premenných

Štruktúra je objekt obsahujúci nasledovné atribúty:

- `domain` - množina prvkov domény. Použite vhodnú štruktúru jazyka, ktorý používate.
  Mala by umožňovať iterovať cez všetky prvky a testovať príslušnosť.
- `iC` - interpretácia symbolov konštánt. Mapa z mien premenných na prvky z `domain`.
- `iF` - interpretácia funkčných symbolov. Mapa z mien funkcií na funkcie ktoré
  berú správny počet argumentov a vracajú  hodnotu z `domain`.
- `iP` - interpretácia predikátových symbolov. Mapa z mien predikátov na množinu
  `n`-tíc prvkov z `domain` (kde `n` je arita príslušného symbolu).

*Poznámka: štruktúra štruktúry (pun intended) je navrhnútá tak, aby čo najviac
zodpovedala teórii z prednášky (teda skoro, mala by to byť jedna mapa spolu).
V praxi môže byť praktickejšie (again) použiť iné reprezentácie. Interpretácie
predikátov môžu tiež byť reprezentované ako funkcie (s návratovou hodnotou
bool), čo môže byť pamäťovo efektívnejšie. Naopak, ak štruktúry treba
serializovať / ukladať do súborov a pod., musia byť tiež funkcie reprezentované
ako `n+1`-tice (`(arg1, arg2, ..., vysledok)`). Všimnite si, že ak by sme
navyše brali interpretácie konštánt ako 1-tice z `domain`, tak v tomto prípade budú
všetky interpretácie reprezentované ako `n`-tice z `domain`.*

Ohodnotenie premenných (angl. <i>valuation</i>) je mapa z reťazcov (mien premenných)
na hodnoty z `domain` (pre danú štruktúru).

Na prednáškach ste používali označenie `e(x/v)` pre (nové) ohodnotenie, ktoré je
rovnaké ako `e` ale premennej `x` priraďuje hodnotu `v`. Je dobré si spraviť
podobnú funkciu (napr. s názvom `set`).

### Python

V knižnici [`folSemantics.py`](folSemantics.py) sú zadefinované triedy
`Structure` a `Valuation` a tiež výnimku "NotApplicable". Dajú sa používať
nasledovne:

```python
from folSemantics import Structure, Valuation

# jednotlive cleny mozno dat konstruktoru
m = Structure(domain = [1,2,3], iC = {'c':1}, iP = {'P': frozenset([(1,2), (1,3)])})
# pripadne ich nastavit dodatocne
# (pozor, domain sa interne konvertuje na frozenset, ktora je immutable)
m.iF['f'] = lambda x,y: 1
m.iF['g'] = lambda x: (x+1) % 3 + 1


e = Valuation({'x': 1, 'y': 2, 'z': 3})
e1 = e.set('x', 3)  # e1 == {'x':3, 'y': 2, 'z': 3}

# hodnota termu f(g(c), x) v strukture m pri ohodnoteni e
h = m.iF['f'](     # hodnota f(3, 1)
      m.iF['g'](    # hodnota g(1) -> 3
        m.iC['c']    # interpretacia konstanty c -> 1
      ),
      e['x']         # interpretacia premennej x v ohodnoteni e -> 1
    )

# ci je P(f(g(c),x), z) splnena v strukture m pri ohodnoteni e
isSatisfied = (h, e['z']) in m.iP['P']
```

## Technické detaily riešenia

Riešenie [odovzdajte](../docs/odovzdavanie.md) do vetvy `cv09` v adresári
`cvicenia/cv09`.

Odovzdávanie riešení v iných jazykoch konzultujte s cvičiacimi.

### Python
Odovzdávajte súbor `folFormula.py`.
Program [`folFormulaTest.py`](folFormulaTest.py) musí korektne zbehnúť s vašou knižnicou.
