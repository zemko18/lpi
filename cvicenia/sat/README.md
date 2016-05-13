Súťaž o najrýchlejší SAT solver
===============================

**Súťaž končí v nedeľu 20.5. 23:59:59. Riešenia po tomto termíne už nebudú
akceptované.**

Cieľom je naprogramovať čo najrýchlejší SAT solver.

Technické požiadavky sú rovnaké ako
v [cvičení 8](../cv08#technické-detaily-riešenia), najmä:
- commandline program, ktorý dostane dva argumenty: meno vstupného a výstupného súboru;
- vstupný súbor vo formáte DIMACS (s korektnou hlavičkou, môže obsahovať komentáre),
  max. 2048 premenných;
- výstupný súbor obsahuje na prvom riadku reťazec `SAT` alebo `UNSAT`, v prvom
  prípade obsahuje druhý riadok čísla s absolútnymi hodnotami 1, 2, … až
  najväčšia premenná, **ukončené nulou**.

## Odovzdávanie

Riešenie odovzdávajte do vetvy, ktorej názov začína na `sat` (napríklad do
vetvy `sat`, ktorú už v repozitároch máte vytvorenú) do adresára `sat`
dodržiavajúc názvy súborov podľa
[cvičenia 8](../cv08#technické-detaily-riešenia)
(t.j. `satsolver.py`, `satsolver.cpp`, `SatSolver.java`; kód môžete rozdeliť
aj do viacerých súborov, ale musí byť skompilovateľný / spustiteľný pomocou
uvedených príkazov). **Nezabudnite vytvoriť pull request.**

Môžete odovzdať viacero riešení (napríklad s rôznymi optimalizáciami) do
rôznych vetiev (začínajúcich na `sat`), vo výsledkoch sa ukážu všetky
a hodnotiť vás budeme podľa najlepšie umiestneného z nich. V každej vetve
nahrávajte súbory normálne do **adresára `sat`** a nezabudnite pre každú
vytvoriť pull request. Rôzne riešenia môžu byť v rôznych jazykoch.  Môžete
napríklad odovzdať 4 rôzne riešenia do vetiev `sat`, `sat2`,
`sat-optimalizacia1` a `satRandom` (a na každú z nich vytvoriť pull
request), kde prvé tri budú mať v adresári `sat` súbor `satsolver.py`
a posledné v adresári `sat` súbory `satsolver.cpp` a `satsolver.h`.

V rámci jednej vetvy bude hodnotená naposledy odovzdaná verzia (commit). Ak
chcete aktualizovať riešenie vo vetve, ktorej ste už vytvorili pull request,
stačí do nej iba nahrať novú verziu riešenia (nový commit). Toto riešenie
bude potom pretestované s touto najnovšou verziou.

Odovzdávanie riešení v iných jazykoch ako python, C++ a Java konzultujte s cvičiacimi.

## Hodnotenie

SAT solvery budú vyhodnotené formou súťaže a budú usporiadané nasledovne:

1. Pre každú dvojicu (<var>solver</var>, <var>vstup</var>) bude vypočítané, koľko solverov
   vyriešilo daný <var>vstup</var> rýchlejšie. Ak <var>solver</var> nerieši <var>vstup</var> korektne, tak
   všetky solvery, ktoré ho riešia korektne sú považované, že ho vyriešili
   rýchlejšie.
1. Pre každý solver sa vypočíta súčet cez všetky vstupy, koľko solverov bolo
   rýchlejších.
1. Solvery sa usporiadajú podľa súčtu z bodu 2.
1. Poradie študentov sa určí podľa umiestnenia ich najlepšieho solvera.
1. Študent na <var>i</var>-tom mieste získa max(0, 6 − <var>i</var>) bodov. Prvé miesto je najvyššie.

Riešenia budú hodnotené priebežne podľa časových možností ;) a výsledky
budú zverejňované niekde tu.

**Súťaž končí v nedeľu 20.5. 23:59:59. Riešenia po tomto termíne už nebudú
akceptované.** Finálne výsledky a body budú zverejnené v krátkej dobe po tomto
termíne.

Riešenia budú kompilované a vyhodnocované na linuxe (Gentoo 64bit,
python aspoň 3.3, g++ aspoň 4.8.3).
Počítač, na ktorom sa bude vyhodnocovať, bude mať minimálne 2, pravdepodobne
4 jadrá.
Používajte ale iba veci, ktoré sú vo vašom jazyku štandardizované.
Nepoužívajte žiaden kód závislý na operačnom systéme, prípadne vašom
vývojovom prostredí.
