Cvičenie 6
==========

**Riešenie odovzdávajte podľa
[pokynov na konci tohoto zadania](#technické-detaily-riešenia)
do piatku 6.4. 23:59:59.**


Súbory potrebné pre toto cvičenie si môžete stiahnuť ako jeden zip
[`cv06.zip`](https://github.com/FMFI-UK-1-AIN-412/lpi/archive/cv06.zip).

Tablo (4b)
------------------

Implementujte _tablový algoritmus_,
teda algoritmus na konštrukciu úplného tabla
pre konečnú množinu označených formúl.

Vaše riešenie sa má skladať z dvoch častí:

1. Do tried na reprezentáciu formúl z cvičenia 3 doimplementujte
   metódy `signedSubf` a `getType`, ktoré reprezentujú informácie
   o tablových pravidlách pre jednotlivé typy formúl.
2. Implementujte triedu `TableauBuilder` obsahujúcu metódu `build`,
   ktorá dostane zoznam označených formúl a vytvorí pre ne úplné (alebo
   uzavreté) tablo.

### Bonus

Nižšie popisovaný jednoduchý algoritmus nie je ideálny vzhľadom na dobu behu
a veľkosť výsledného tabla. Ak implementujete zaujímavé optimalizácie
(výber formúl na rozpísanie), môžete získať bonusové body.
Pozor: algoritmus, ktorý vyrobí trochu menšie tablo, ale trvá mu to oveľa
dlhšie, nie je nutne lepší.

V pull requeste presne popíšte vaše optimalizácie a ideálne tiež uveďte
porovnanie s naivným (nižšie uvedeným) algoritmom vzhľadom na dobu behu
a veľkosť tabla.


### Označené formuly a tablové pravidlá

Označené formuly reprezentujeme triedou `SignedFormula` z modulu
[`tableau.py`](tableau.py). Pri ich vyrábaní môžete použiť buď konštruktor,
ktorý očakáva znamienko (`True` alebo `False`) a formulu, alebo pomocné statické
metódy `T` a `F`, ktoré očakávajú iba formulu. Na vytvorenie opačnej formuly
voči danej označenej formule môžete použiť metódu `neg`
alebo unárny operátor `-`:

```python
from tableau import SignedFormula, T, F

f = Conjunction([Variable('a'), Variable('b')])

tf = SignedFormula(True, f)  # T (a∧b)
tf = T(f)                    # to isté

ff = SignedFormula(False, f) # F (a∧b)
ff = F(f)                    # to isté
ff = tf.neg()                # to isté
ff = -tf                     # to isté
```

Metóda `getType(sign)` vráti akého typu (&alpha; alebo &beta;) by dotyčná
formula bola, ak by bola označená značkou `sign` (negácia a premenná sú vždy
typu &alpha;).

Metóda `signedSubf` vráti „podformuly“ označenej formuly,
t.j. &alpha;<sub>1</sub> a &alpha;<sub>2</sub>, ak by bola typu &alpha;,
a &beta;<sub>1</sub> a &beta;<sub>2</sub>, ak by bola typu &beta;.

Pamätajte, že konjukcia a disjunkcia môžu mať viacero podformúl, takže
tablové pravidlá v skutočnosti vyzerajú nasledovne:

```
  T A1 ∧ A2 ∧ A3 ∧ ... ∧ An           F A1 ∧ A2 ∧ A3 ∧ ... ∧ An
 ───────────────────────────      ──────┬──────┬──────┬─────┬──────
           T A1                    F A1 │ F A2 │ F A3 │ ... │ F An
           T A2
           T A3
           ...
           T An
```
Ekvivalencia je konjunkcia dvoch implikácií ((<var>A</var> ↔︎ <var>B</var>) je
skratkou za ((<var>A</var> → <var>B</var>) ∧ (<var>B</var> → <var>A</var>)),
takže pravidlá pre ňu vyzerajú podobne ako pre konjunkciu, len podformuly majú
trošku zložitejší tvar:

```
 T A↔︎B             F A↔︎B
───────       ───────┬───────
 T A→B         F A→B │ F B→A
 T B→A
```

### Tablo

Tablo, ktoré vytvorí metóda `TableauBuilder::build`, bude reprezentované ako
strom vytvorený z objektov `tableau.Node` definovaných v knižnici
[`tableau.py`](tableau.py). Ukážková implementácia v [`builder.py`](builder.py)
iba vytvorí prázdne tablo a následne doň popridáva „vstupné“ formuly.

Pri vytváraní ďalších uzlov tabla potom treba vždy ako druhý parameter  (`source`) konštruktora
`Node` uviesť referenciu na uzol s formulou, z ktorej vznikla formula nového uzla.

Keď pridáme uzol s formulou, ktorá uzatvára vetvu, treba ho navyše „označiť“ volaním metódy
`close`, ktorá má ako parameter referenciu na uzol, ktorého formula má
opačné znamienko ako formula nového uzla.

Jednoduchý príklad na vygenerovanie uzavretého tabla a výsledné tablo:

```python
tab = tableau.Tableau()
root = tableau.Node( tableau.F( Implication( Variable('a'), Variable('a') ) ) )
tab.append(None, root) # Pridávame prvý vrchol - koreň

node1 = tableau.Node( tableau.T( Variable('a') ), source = root)
tab.append(root, node1) # Pridávame node1 pod root

node2 = tableau.Node( tableau.F( Variable('a') ), source = root)
tab.append(node1, node2) # Pridávame node2 pod node1
node2.close(node1)  # node2 je opačný k node1, takže sme zavreli tablo

print(tab)
```

```
(1) F (a->a)
============
(2) T a (1) 
(3) F a (1) 
  * [3,2]   
```

### Algoritmus

Najjednoduchší algoritmus na vytvorenie tabla je v skratke:

1. Rozpísať všetky formuly typu &alpha;.
2. Ak už žiadna formula typu &alpha; nie je, rozpísať *nejakú* formulu
   typu &beta;.
3. Opakovať, kým tablo nie je uzavreté a máme nerozpísané formuly.

_Pozor:_ formula môže byť rozpísaná v nejakej vetve, ale ešte nerozpísaná
v inej vetve.

Nasledujúci pseudokód podrobnejšie popisuje jednu možnú implementáciu tohto algoritmu:

```
build(zoznam vstupných formúl):
  vytvor tablo zo zoznamu vstupných formúl 
  ak je už uzavreté:
    označ ho ako uzavreté a skonči
  alfy  := zoznam uzlov tabla s alfa formulami
  bety  := zoznam uzlov tabla s beta formulami
  vetva := štruktúra obsahujúca všetky vstupné formuly
    # tip: oplatí sa použiť spracujNovýUzol
  expanduj(posledný uzol tabla, alfy, bety, vetva)

expanduj(uzol, alfy, bety, vetva):
  kým alfy nie sú prázdne:
    vyber z álf nejaký uzol s formulou f
    pre každú sf z označených podformúl f:
      vytvor nový uzol obsahujúci sf a pripoj ho pod uzol
      ak spracujNovýUzol(nový uzol, alfy, bety, vetva) uzavrelo vetvu:
        skonči
      uzol := nový uzol

  ak bety nie sú prázdne:
    vyber z biet nejaký uzol s formulou f
    pre každú sf z označených podformúl f:
      vytvor nový uzol so sf a pripoj ho pod uzol
      nové alfy, bety a vetva := kópie álf, biet a vetvy (pre túto novú vetvu)
      ak spracujNovýUzol(nový uzol, nové alfy, nové bety, nová vetva) neuzavrelo vetvu:
        expanduj(nový uzol, nové alfy, nové bety, nová vetva)
  ináč:
    rozpísali sme všetky alfy a bety, nepodarilo sa zavrieť vetvu
    (takže máme úplnú otvorenú vetvu)
    s tablom/vetvou ale nemusíme nič robiť

spracujNovýUzol(uzol, alfy, bety, vetva):
  pridaj uzol do álf alebo biet podľa toho, aká formula v ňom je
  pridaj formulu do vetvy
  ak je vo vetve opačná formula:
    označ uzol (aktuálnu vetvu) ako uzatvorený
  vráť, či sa vetva uzavrela
```

Pri implementácii pozor na „jazykové“ problémy: python nemá rád, keď iterujete
cez zoznam, ktorý zároveň meníte (pridávate / odoberáte prvky); ujasnite si,
kedy potrebujete novú kópiu zoznamu / štruktúry a kedy chcete meniť tú pôvodnú
atď.

Tiež pozor na to, že v metóde `expanduj` sa alfy pridávajú „nad seba“ a bety
„vedľa seba“.

## Technické detaily riešenia

Riešenie odovzdajte do vetvy `cv06` v adresári `cvicenia/cv06`.  Odovzdávajte
(modifikujte) súbory `formula.py` a `builder.py`.  Program
[`tableauTest.py`](tableauTest.py) musí korektne zbehnúť s vašou knižnicou.

Odovzdávanie riešení v iných jazykoch konzultujte s cvičiacimi.
