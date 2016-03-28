import cnf

class Formula(object):
    def __init__(self, subs = []):
        self.m_subf = subs
    def subf(self):
        return self.m_subf
    def isSatisfied(self, v):
        return False
    def toString(self):
        return "INVALID"
    def __str__(self):
        return self.toString()
    def __repr__(self):
        return self.__class__.__name__ + '(' + ','.join([ repr(f) for f in self.subf()]) + ')'

    def toCnf(self):
        """ Vrati reprezentaciu formuly v CNF tvare. """
        # TODO
        return cnf.Cnf()

class Variable(Formula):
    def __init__(self, name):
        Formula.__init__(self)
        self._name = name
    def name(self):
        return self._name
    def isSatisfied(self, v):
        return v[self.name()]
    def toString(self):
        return self.name()
    def __repr__(self):
        return "Variable(%r)" % (self.name(),)

class Negation(Formula):
    def __init__(self, orig):
        Formula.__init__(self, [orig])
    def originalFormula(self):
        return self.subf()[0]
    def isSatisfied(self, v):
        return not self.originalFormula().isSatisfied(v)
    def toString(self):
        return "-%s" % (self.originalFormula().toString())

class Disjunction(Formula):
    def __init__(self, subs):
        Formula.__init__(self, subs)
    def isSatisfied(self, v):
        return any(f.isSatisfied(v) for f in self.subf())
    def toString(self):
        return '(' + '|'.join(f.toString() for f in self.subf()) + ')'

class Conjunction(Formula):
    def __init__(self, subs):
        Formula.__init__(self, subs)
    def isSatisfied(self, v):
        return all(f.isSatisfied(v) for f in self.subf())
    def toString(self):
        return '(' + '&'.join(f.toString() for f in self.subf()) + ')'

class BinaryFormula(Formula):
    connective = ''
    def __init__(self, left, right, connective = ''):
        Formula.__init__(self, [left, right])
    def leftSide(self):
        return self.subf()[0]
    def rightSide(self):
        return self.subf()[1]
    def toString(self):
        return '(%s%s%s)' % (self.leftSide().toString(), self.connective, self.rightSide().toString())

class Implication(BinaryFormula):
    connective = '->'
    def isSatisfied(self, v):
        return (not self.leftSide().isSatisfied(v)) or self.rightSide().isSatisfied(v)

class Equivalence(BinaryFormula):
    connective = '<->'
    def isSatisfied(self, v):
        return self.leftSide().isSatisfied(v) == self.rightSide().isSatisfied(v)

# vim: set sw=4 ts=4 sts=4 et :
