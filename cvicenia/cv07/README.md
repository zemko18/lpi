Cvičenie 7
==========

**Riešenie odovzdávajte podľa
[pokynov na konci tohoto zadania](#technické-detaily-riešenia)
do stredy 18.4. 23:59:59.**

Súbory potrebné pre toto cvičenie si môžete stiahnuť ako jeden zip
[`cv07.zip`](https://github.com/FMFI-UK-1-AIN-412/lpi/archive/cv07.zip).

## Kto zabil Agátu (3b)

Someone in Dreadsbury Mansion killed Aunt Agatha. Agatha, the butler, and
Charles live in Dreadsbury Mansion, and are the only ones to live there.
A killer always hates, and is no richer than his victim. Charles hates no one that
Agatha hates. Agatha hates everybody except the butler. The butler hates
everyone not richer than Aunt Agatha. The butler hates everyone whom Agatha
hates. No one hates everyone. Who killed Agatha?

Niekto v Dreadsburskom panstve zabil Agátu. Agáta, komorník a Karol bývajú
v Dreadsburskom panstve a nikto iný okrem nich tam nebýva. Vrah vždy nenávidí
svoje obete a nie je od nich bohatší.
Karol neprechováva nenávisť k nikomu, koho nenávidí Agáta.
Agáta nenávidí každého okrem komorníka.
Komorník nenávidí každého, kto nie je bohatší ako Agáta. Komorník nenávidí
každého, koho nenávidí Agáta. Niet toho, kto by nenávidel všetkých. Kto zabil
Agátu?

Zistite a **dokážte** kto zabil Agátu.

### Formalizácia

Najprv treba jednotlivé tvrdenia zo zadania prepísať do logiky. Napríklad:

    The butler hates everyone whom Agatha hates.

    ∀X ( hates(Agatha,X) → hates(butler,X) )

Toto samozrejme nie je výroková logika, takže budeme potrebovať program, ktorý
vyrobí inštancie pravidiel pre správne doplnené premenné.


### Hľadanie riešenia a dôkaz

Takto sformulovaný problém prerobíme na vstup pre SAT solver. Keď ho
len tak pustíme, nájde nám jedno z možných riešení, v ktorom sa môžeme pozrieť,
kto by mohol byť vrahom. Potrebujeme však ukázať, že to neplatí len náhodou
v tom jednom *modeli* (ohodnotení spĺňajúcom všetky formuly), ale že to naozaj
*vyplýva* z našej *teórie* (množiny formúl), teda platí to vo
všetkých jej modeloch. Takže musíme pridať negáciu toho tvrdenia k teórii. Ak bude
nesplniteľná, tak naše tvrdenie (kto bol vrahom) vyplýva z teórie, teda platí
vo všetkých modeloch našej teórie.

**Pozor**: Je dôležité najskôr (pred pridaním negácie toho, čo chceme dokázať)
naozaj overiť, že naša teória je *splniteľná* (má aspoň nejaký model). Keby sme
niečo pokazili a vyrobili nekonzistentnú (nesplniteľnú) teóriu, tak by z nej
samozrejme vyplývalo všetko, vrátane nášho cieľa (ale aj jeho negácie).

Najlepší spôsob je, keď celú teóriu zapíšete do nejakej funkcie, aby ste ju
(vstup pre SAT solver) mohli ľahko zapísať dvakrát:

1. najskôr samotnú, pustiť SAT solver a overiť, že má nejaké riešenie;
2. prejsť všetkých možných vrahov v tomto riešení (t.j. také `X`, pre ktoré je
   `killed(X,Agatha)` splnené);
3. pre každého možného vraha znovu zapísať teóriu ale aj spolu s negáciou
   dokazovaného tvrdenia a znovu pustiť SAT solver.

### Kódovanie

Podobne ako v predchádzajúcich úlohách potrebujeme zakódovať
(výrokové) premenné na čísla. Máme 3 druhy premenných, zodpovedajúce
binárnym predikátom `killed(X,Y)`, `hates(X,Y)` a `richer(X,Y)`.

Keďže máme 3 binárne predikáty, ktoré majú ako parametre jedného z troch ľudí,
môžeme premenné zakódovať ako číslo v trojkovej sústave <var>R</var><var>X</var><var>Y</var><sub>3</sub> + 1, kde
<var>R</var> je číslo predikátu a <var>X</var> a <var>Y</var> sú čísla osôb od 0 do 2 (teda v desiatkovej
sústave to bude `R*3*3 + X*3 + Y + 1`).

Ak predikát `killed` a Agáta budú mať číslo 0 a keď vymeníte poradie parametrov
v predikáte `killed` (aby vrah bola najnižšia cifra), tak potom prvé
3 premenné (1, 2, 3) budú zodpovedať možnostiam toho, kto zabil Agátu.
(Dobré je vymeniť poradie parametrov len vo
výpočte čísla premennej, nie poradie argumentov vo funkcii ;)

Veľmi pomôže spraviť si pár pomocných funkcií podobne ako
v predchádzajúcich úlohách:

```python
P = 3 # pocet ludi
Agatha = 0
Butler = 1
Charles = 2

def killed(p1, p2):
    # p1 a p2 su vymenene,
    # aby killed(X,Agatha) zodpovedalo 1, 2, 3
    return 0 * P * P + p2 * P + p1 + 1

def hates(p1, p2):
    return 1 * P * P + p1 * P + p2 + 1

def richer(p1, p2):
    return 2 * P * P + p1 * P + p2 + 1
```

Formuly môžeme potom vygenerovať takto (`writeImpl`
je metóda pomocnej triedy `DimacsWriter`, ktorá rovno správne zapíše
implikáciu):
```python
# The butler hates everyone whom Agatha hates.
# ∀X ( hates(Agatha,X) → hates(butler,X) )
for p in range(P):
    w.writeImpl( hates(Agatha, p), hates(Butler, p) )
```

## Technické detaily riešenia

Riešenie odovzdajte do vetvy `cv07` v adresári `cvicenia/cv07`.

Odovzdávajte program (`agatha.py`, `agatha.cpp` alebo `Agatha.java`), ktorý
pomocou SAT solvera dokáže, kto zabil Agátu.

Program by mal najskôr zakódovať iba teóriu a pustiť na ňu SAT solver, aby ste
sa ubezpečili, že vaša teória má model (riešenie) a našli možných vrahov.
Potom by mal pre každého možného vraha znovu zakódovať teóriu spolu s tvrdením,
ktoré chcete dokázať, a znovu zavolať SAT solver (a skontrolovať, či dá
očakávaný výstup). Ak sa podarí dokázať, kto je vrahom, program by mal vypísať
`Vrahom je XXX.`.

Do komentárov v programe napíšte tvrdenia / formuly, ktoré ste
sformalizovali.

Ak chcete v pythone použiť knižnicu z [examples/sat](../../examples/sat), nemusíte
si ju kopírovať do aktuálneho adresára, stačí ak na začiatok svojej knižnice
pridáte:
```python
import os
import sys
sys.path[0:0] = [os.path.join(sys.path[0], '../../examples/sat')]
import sat
```
