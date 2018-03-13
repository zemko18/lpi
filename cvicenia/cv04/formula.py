import cnf

from typing import List, Mapping
Valuation = Mapping[str, bool]

class Formula(object):
    def __init__(self, subs : List['Formula']= []) -> None:
        self.m_subf = subs # type: List[Formula]
    def subf(self) -> List['Formula']:
        return self.m_subf
    def isSatisfied(self, v : Mapping[str,bool]) -> bool:
        return False
    def toString(self) -> str:
        return "INVALID"
    def __str__(self) -> str:
        return self.toString()
    def __repr__(self) -> str:
        return self.__class__.__name__ + '(' + ','.join([ repr(f) for f in self.subf()]) + ')'

    def toCnf(self) -> cnf.Cnf:
        """ Vrati reprezentaciu formuly v CNF tvare. """
        # TODO
        return cnf.Cnf()

class Variable(Formula):
    def __init__(self, name : str) -> None:
        Formula.__init__(self)
        self._name = name
    def name(self) -> str:
        return self._name
    def isSatisfied(self, v : Mapping[str, bool]) -> bool:
        return v[self.name()]
    def toString(self) -> str:
        return self.name()
    def __repr__(self) -> str:
        return "Variable(%r)" % (self.name(),)

class Negation(Formula):
    def __init__(self, orig : Formula) -> None:
        Formula.__init__(self, [orig])
    def originalFormula(self) -> Formula:
        return self.subf()[0]
    def isSatisfied(self, v : Valuation) -> bool:
        return not self.originalFormula().isSatisfied(v)
    def toString(self) -> str:
        return "-%s" % (self.originalFormula().toString())

class Disjunction(Formula):
    def __init__(self, subs : List[Formula]) -> None:
        Formula.__init__(self, subs)
    def isSatisfied(self, v : Valuation) -> bool:
        return any(f.isSatisfied(v) for f in self.subf())
    def toString(self) -> str:
        return '(' + '|'.join(f.toString() for f in self.subf()) + ')'

class Conjunction(Formula):
    def __init__(self, subs : List[Formula]) -> None:
        Formula.__init__(self, subs)
    def isSatisfied(self, v : Valuation) -> bool:
        return all(f.isSatisfied(v) for f in self.subf())
    def toString(self) -> str:
        return '(' + '&'.join(f.toString() for f in self.subf()) + ')'

class BinaryFormula(Formula):
    connective = ''
    def __init__(self, left : Formula, right : Formula) -> None:
        Formula.__init__(self, [left, right])
    def leftSide(self) -> Formula:
        return self.subf()[0]
    def rightSide(self) -> Formula:
        return self.subf()[1]
    def toString(self) -> str:
        return '(%s%s%s)' % (self.leftSide().toString(), self.connective, self.rightSide().toString())

class Implication(BinaryFormula):
    connective = '->'
    def isSatisfied(self, v : Valuation) -> bool:
        return (not self.leftSide().isSatisfied(v)) or self.rightSide().isSatisfied(v)

class Equivalence(BinaryFormula):
    connective = '<->'
    def isSatisfied(self, v : Valuation) -> bool:
        return self.leftSide().isSatisfied(v) == self.rightSide().isSatisfied(v)

# vim: set sw=4 ts=4 sts=4 et :
