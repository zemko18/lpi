class Literal(object):
    """ Reprezentacia literalu (premenna alebo negovana premenna) v CNF formule. """
    def __init__(self, name):
        """ Vytvori novy, kladny (nenegovany) literal pre premennu name. """
        self.name = name
        self.neg = False

    @staticmethod
    def Not(name):
        """ Vytvory novy, negovany literal pre premennu name. """
        lit = Literal(name)
        lit.neg = True
        return lit

    @staticmethod
    def fromInt(i, varMap):
        """ Vytvori novy literal podla ciselneho kodu a mapovania. """
        if isinstance(varMap, VariableMap):
            lit = Literal(varMap.reverse()[abs(i)])
        else:
            lit = Literal(varMap[abs(i)])
        if i < 0:
            lit.neg = True
        return lit

    def __neg__(self):
        """ Vrati novy literal, ktory je negaciou tohoto.

        Toto je specialna metoda, ktoru python zavola, ked
        na nejaky objekt pouzijeme operator -, t.j.:
        l1 = Literal('a')
        l2 = -l1  # l2 je teraz negaciou l1
        """
        lit = Literal(self.name)
        lit.neg = not self.neg
        return lit

    def toString(self):
        """ Vrati textovu reprezentaciu tohoto literalu. """
        if self.neg:
            return "-" + self.name
        else:
            return self.name

    def __str__(self):
        return self.toString()

    def __repr__(self):
        return self.__class__.__name__ + '(' + self.toString() + ')'


    def isSatisfied(self, v):
        """ Urci, ci je tento literal splneny ohodnotenim v. """
        return bool(self.neg) ^ bool(v[self.name])

    def writeToFile(self, outFile, varMap):
        """ Zapise literal do suboru outFile s pouzitim mapovania premennych varMap. """
        if self.neg:
            outFile.write('-%d' % varMap[self.name])
        else:
            outFile.write('%d' % varMap[self.name])

class VariableMap(dict):
    """ Mapovanie mien premennych na cisla.

    Premennym vzdy priraduje suvisly usek cisel 1..n.
    """

    def __init__(self, *args, **kwargs):
        dict.__init__(self, *args, **kwargs)
        self._varNumMax = 0

    def __missing__(self, key):
        self._varNumMax += 1
        self[key] = self._varNumMax
        return self._varNumMax

    def reverse(self):
        """ Vrati reverzne mapovanie ako jednoduchy slovnik z cisel na mena premennych. """
        rev = {}
        for k,v in self.items():
            rev[v] = k
        return rev

    def extend(self, what):
        """ Rozsiri tuto mapu o premenne v danej cnf / klauze / literale. """
        if isinstance(what, str):
            self[what]
        if isinstance(what, Literal):
            self[what.name]
        elif isinstance(what, list): # Cnf and Clause are list-s
            for x in what:
                self.extend(x)

    def writeToFile(self, outFile, prefix=''):
        """ Zapise mapu do suboru outFile.

        Jedna premenna na jeden riadok (t.j. nefunguje na premenne
        s koncom riadku v nazve).

        Volitelny retazec prefix sa prida pred kazdy riadok
        (napriklad 'c ' vyrobi komentare pre dimacs cnf format).
        """
        outFile.write('%s%d\n' % (prefix, self._varNumMax))
        rev = self.reverse()
        for i in range(self._varNumMax):
            outFile.write('%s%s\n' % (prefix, rev[i+1]))

    @staticmethod
    def readFromFile(inFile, prefix=''):
        """ Nacita novu mapu zo suboru inFile a vrati ju.

        Ak je uvedeny volitelny retazec prefix, tento sa odstrani
        zo zaciatku kazdeho riadku (napriklad 'c ' ak je mapa ulozena
        ako komentar v dimacs cnf formate).
        """
        def removePrefix(s):
            """Remove a prefix from string if present."""
            return s[len(prefix):] if s.startswith(prefix) else s

        varMap = VariableMap([])
        n = int(removePrefix(inFile.readline()))
        for i in range(n):
            varMap[removePrefix(inFile.readline().rstrip('\n'))]
        return varMap



class Clause(list):
    """ Reprezentacia klauzy (pole literalov). """
    def __init__(self, *args, **kwargs):
        """ Vytvori novu klauzu obsahujucu argumenty konstruktora. """
        list.__init__(self, *args, **kwargs)
        for lit in self:
            if not isinstance(lit, Literal):
                raise TypeError('Clause can contain only Literal-s')

    def toString(self):
        """ Vrati textovu reprezentaciu tejto klauzy (vid zadanie). """
        return ' '.join(lit.toString() for lit in self)

    def __str__(self):
        return self.toString()

    def isSatisfied(self, v):
        """ Urci, ci je tato klauza splnena ohodnotenim v. """
        for lit in self:
            if lit.isSatisfied(v):
                return True
        return False

    def writeToFile(self, oFile, varMap):
        """ Zapise klauzu do suboru outFile v DIMACS formate
            pricom pouzije varMap na zakodovanie premennych na cisla.

        Klauzu zapise na jeden riadok (ukonceny znakom konca riadku).
        """
        for lit in self:
            lit.writeToFile(oFile, varMap)
            oFile.write(' ')
        oFile.write(' 0\n')

    @staticmethod
    def readFromFile(inFile, varMap):
        """ Nacita novu klauzu zo suboru inFile a vrati ju ako vysledok.
        Mozete predpokladat, ze klauza je samostatne na jednom riadku.
        Ak sa z aktualneho riadku na vstupe neda nacitat korektna klauza,
        vyhodi vynimku IOError.
        """
        line = inFile.readline()
        if line is None:
            raise IOError('End of file')

        rVarMap = varMap.reverse()

        cls = Clause()
        ints = [int(x) for x in line.split()]
        if len(ints) < 1 or ints[-1] != 0:
            raise IOError('Bad clause')
        for i in ints[:-1]:
            if i == 0:
                raise IOError('Bad clause (0 inside)')
            elif i < 0:
                cls.append(Literal.Not(rVarMap[abs(i)]))
            else:
                cls.append(Literal(rVarMap[abs(i)]))
        return cls

class Cnf(list):
    """ Reprezentacia Cnf formuly ako pola klauz. """
    def __init__(self, *args, **kwargs):
        """ Vytvori novu Cnf formulu obsahujucu argumenty konstruktora. """
        list.__init__(self, *args, **kwargs)
        for cls in self:
            if not isinstance(cls, Clause):
                raise TypeError('Cnf can contain only Clause-s')

    def toString(self):
        """ Vrati textovu reprezentaciu tejto formuly (vid zadanie). """
        return ''.join([ cls.toString() + '\n' for cls in self])

    def __str__(self):
        return self.toString()

    def isSatisfied(self, v):
        """ Urci, ci je tato formula splnena ohodnotenim v. """
        for cls in self:
            if not cls.isSatisfied(v):
                return False
        return True

    def extendVarMap(self, varMap):
        """ Rozsiri varMap o premenne v tejto formule. """
        for cls in self:
            cls.extendVarMap(varMap)

    def writeToFile(self, oFile, varMap):
        """ Zapise klauzu do suboru outFile v DIMACS formate
            pricom pouzije varMap na zakodovanie premennych na cisla
            a zapise kazdu klauzu na jeden riadok.
        """
        for cls in self:
            cls.writeToFile(oFile, varMap)

    @staticmethod
    def readFromFile(inFile, varMap):
        """ Nacita novu formulu zo suboru inFile a vrati ju ako vysledok.
        Mozete predpokladat, ze kazda klauza je samostatne na jednom riadku.
        """
        cnf = Cnf()
        while True:
            try:
                cls = Clause.readFromFile(inFile, varMap)
            except IOError:
                break
            cnf.append(cls)
        return cnf

# vim: set sw=4 ts=4 sts=4 et :
