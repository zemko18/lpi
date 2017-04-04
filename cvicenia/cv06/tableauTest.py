#!/bin/env python3

import traceback
import time
import itertools

"""
    Testovaci program pre TableauBuilder
"""


""" Nastavte na True ak chcete aby testy zastali na prvej chybe. """
stopOnError = False

""" Nastavte na True, ak chcete vidiet vystup aj pri PASSED testoch. """
showAll = False

from builder import TableauBuilder
from tableau import Tableau, Node, ALPHA, BETA, SignedFormula, T, F
from formula import Formula, Variable, Negation, Conjunction, Disjunction, Implication, Equivalence

def printException():
    print('ERROR: Exception raised:\n%s\n%s\n%s' % (
        '-'*20,
        traceback.format_exc(),
        '-'*20)
    )

def now():
    try:
       return time.perf_counter() # >=3.3
    except AttributeError:
       return time.time() # this is not monotonic!

class FailedTestException(BaseException):
    pass

class BadTableauException(BaseException):
    pass

class Tester(object):
    def __init__(self):
        self.tested = 0
        self.passed = 0
        self.case = 0
        self.closed = 0
        self.size = 0
        self.time = 0

    def compare(self, result, expected, msg):
        self.tested += 1
        if result == expected:
            self.passed += 1
            return True
        else:
            print("Failed: %s:" %  msg)
            print("    got %s  expected %s" % (repr(result), repr(expected)))
            print("")
            return False

    def status(self):
        print("TESTED %d" % (self.tested,))
        print("PASSED %d" % (self.passed,))
        print("SUM(closed) %d" % (self.closed,))
        print("SUM(time) %f" % (self.time,))
        print("SUM(size) %d" % (self.size,))
        if self.tested == self.passed:
            print("OK")
        else:
            print("ERROR")

    def closedToString(self, closed):
        return "CLOSED" if closed else "OPEN"

    def typeToString(self, fType):
        if fType == ALPHA:
            return "ALPHA"
        if fType == BETA:
            return "BETA"
        return str(fType)

    def testSignedForm(self, f, expTypeT, expSfsT):
        self.case += 1
        self.tested += 1
        print("CASE %d: %s" % (self.case, f.toString()))
        sfsT = frozenset()
        sfsF = frozenset()
        try:
            start = now()
            typeT = f.getType(True)
            typeF = f.getType(False)
            sfTs = f.signedSubf(True)
            sfFs = f.signedSubf(False)
            duration = now() - start
            for sfs in (sfTs, sfFs):
                for sf in sfs:
                    if not isinstance(sf, SignedFormula):
                        raise TypeError("Signed subformula must be an instance of SignedFormula")
            sfsT = frozenset(sf.toString() for sf in sfTs)
            sfsF = frozenset(sf.toString() for sf in sfFs)
        except KeyboardInterrupt:
            raise KeyboardInterrupt()
        except:
            printException()
            if stopOnError:
                raise FailedTestException()
            return

        expSfsF = frozenset(sf.neg().toString() for sf in expSfsT)
        expSfsT = frozenset(sf.toString() for sf in expSfsT)
        sameT = expSfsT == sfsT
        sameF = expSfsF == sfsF
        okTypeT = len(expSfsT) <= 1 or expTypeT == typeT
        okTypeF = len(expSfsF) <= 1 or (ALPHA if expTypeT == BETA else BETA) == typeF

        self.time += duration

        if sameT and sameF and okTypeT and okTypeF:
            self.passed += 1
            print('PASSED:  time: %12.9f' % (duration,))
        else:
            print('FAILED:')
            fstrT = T(f).toString()
            fstrF = F(f).toString()
            if not okTypeT:
                print( 'Unexpected type of %r: %s\n' %
                        (fstrT, self.typeToString(typeT)) )
            if not okTypeF:
                print( 'Unexpected type of %r: %s\n' %
                        (fstrF, self.typeToString(typeF)) )
            if not sameT:
                print( 'Wrong subformulas of %r:\n%s\n' %
                        (fstrT, '\n'.join(sfsT)) )
            if not sameF:
                print( 'Wrong subformulas of %r:\n%s\n' %
                        (fstrF, '\n'.join(sfsF)) )
            if stopOnError:
                raise FailedTestException()
        print('')

    def testTableauStructure(self, node, ancestors, strSfs):
        strSf = node.sf.toString()
        if node.source == None:
            if strSf not in strSfs:
                raise BadTableauException(
                    'Node (%d) has no source node and its formula not initial.' %
                    (node.number,)
                    )
        elif node.source not in ancestors:
            raise BadTableauException(
                'Node (%d) has source (%d) which is not one of its ancestors.' %
                (node.number, node.source.number,)
                )
        else:
            src = node.source
            parent = ancestors[-1]
            strSourceSubfs = [ sf.toString() for sf in src.sf.subf() ]
            if strSf not in strSourceSubfs:
                raise BadTableauException(
                    'Node (%d) does not contain a subformula of (%d).' %
                    ( node.number, src.number )
                    )
            if (src.sf.getType() == ALPHA and
                len(parent.children) != 1):
                raise BadTableauException(
                    'Node (%d) is a result of ALPHA rule for (%d) -- must have no siblings.' %
                    ( node.number, src.number )
                    )
            if (src.sf.getType() == BETA and
                len(parent.children) != len(strSourceSubfs)):
                raise BadTableauException(
                    'Node (%d) should have %d siblings -- results of BETA rule for (%d).' %
                    ( node.number, len(strSourceSubfs)-1, src.number )
                    )
        ancestors.append(node)
        for child in node.children:
            self.testTableauStructure(child, ancestors, strSfs)

        if node.closed:
            # this is a 'closing' node
            if not isinstance(node.closedFrom, Node):
                raise BadTableauException(
                    'Close pair reference for closed node (%d) is not a node' % node.number
                )
            if not node.closedFrom in ancestors:
                raise BadTableauException(
                    'Close pair (%d) is not an ancestor of the closed node (%d).' %
                    (node.closedFrom.number, node.number)
                )
            if node.sf.sign != (not node.closedFrom.sf.sign):
                raise BadTableauException(
                    'Close pair formula signs are wrong (%d, %d)'
                    % (node.number, node.closedFrom.number)
                )
            if node.sf.f.toString() != node.closedFrom.sf.f.toString():
                raise BadTableauException(
                    'Close pair formulas do not match (%d, %d)'
                    % (node.number, node.closedFrom.number)
                )

        if not node.isClosed() and node.children == []:
            # open branch should be complete
            branchSet = frozenset(nd.sf.toString() for nd in ancestors)
            for nd in ancestors:
                t = nd.sf.getType()
                if t == ALPHA:
                    for sf in nd.sf.subf():
                        if not( sf.toString() in branchSet):
                                raise BadTableauException(
                                    ('Branch (ending at %d) is open but not complete'
                                    + ' -- %d (ALPHA) is missing subformula %s') %
                                    ( node.number, nd.number, sf.toString() )
                                )
                elif t == BETA:
                    haveOne = False
                    for sf in nd.sf.subf():
                        if sf.toString() in branchSet:
                            haveOne = True
                            break
                    if not haveOne:
                        raise BadTableauException(
                                    ('Branch (ending at %d) is open but not complete'
                                    + ' -- %d (BETA) is missing a subformula') %
                                    ( node.number, nd.number ))

        ancestors.pop()

    def testTableau(self, expect_closed, sfs):
        self.case += 1
        self.tested += 1
        strSfs = [sf.toString() for sf in sfs]
        print("CASE %d: %s" %
                (self.case,
                 '; '.join(strSfs)))
        tableau = Node(False, Variable(""))
        try:
            start = now()
            tableau = TableauBuilder().build(sfs)
            duration = now() - start
        except KeyboardInterrupt:
            raise KeyboardInterrupt()
        except:
            printException()
            if stopOnError:
                raise FailedTestException()
            return

        if not isinstance(tableau, Tableau):
            print('FAILED: not a tableau.Tableau: %s' % type(tableau))
            print()
            return

        if not isinstance(tableau.root, Node):
            print('FAILED: not a tableau.Node: %s' % type(tableau))
            print()
            return

        closed = tableau.isClosed()
        badStructure = False
        try:
            self.testTableauStructure(tableau.root, [], strSfs)
        except BadTableauException as err:
            badStructure = str(err)
        except:
            printException()
            if stopOnError:
                raise FailedTestException()
            return

        size = tableau.size()

        self.time += duration
        self.size += size

        if closed:
            self.closed += 1

        passed =  closed == expect_closed and not badStructure
        if passed:
            self.passed += 1
            print('PASSED:  time: %12.9f   tableau size: %3d   %s' %
                    (duration, size, self.closedToString(closed)))
        else:
            print('FAILED: ')

        if not passed or showAll:
            print('=====TABLEAU=====\n%s\n%s' %
                    (tableau.toString(), '='*13))

        if not passed:
            if closed != expect_closed:
                print('Tableau is %s, but should be %s' %
                        (self.closedToString(closed), self.closedToString(expect_closed)))
            if badStructure:
                print(badStructure)
            if stopOnError:
                raise FailedTestException()
        print('')


t = Tester()

Not = Negation
Var = Variable
Impl = Implication
Eq = Equivalence

def And(*args):
    if len(args)==1 and type(args[0]) is list:
        return Conjunction(args[0])
    return Conjunction(args)
def Or(*args):
    if len(args)==1 and type(args[0]) is list:
        return Disjunction(args[0])
    return Disjunction(args)

a = Var('a')
b = Var('b')
c = Var('c')
d = Var('d')


correctRules = False
try:
    t.testSignedForm( a, None, [] )

    t.testSignedForm( Not(a), None, [ F(a) ])

    t.testSignedForm( And([a, b]),
                      ALPHA,
                      [ T(a), T(b) ]
                    )

    t.testSignedForm( Or([a, b]),
                      BETA,
                      [ T(a), T(b) ]
                    )

    t.testSignedForm( And([a, b, c, d]),
                      ALPHA,
                      [ T(a), T(b), T(c), T(d) ]
                    )

    t.testSignedForm( Or([a, b, c, d]),
                      BETA,
                      [ T(a), T(b), T(c), T(d) ]
                    )

    t.testSignedForm( Or([a, Not(b), And(c, d) ]),
                      BETA,
                      [ T(a), T(Not(b)), T(And([c, d])) ]
                    )

    t.testSignedForm( Impl(a, b),
                      BETA,
                      [ F(a), T(b) ]
                    )

    t.testSignedForm( Equivalence(a, b),
                      ALPHA,
                      [ T(Impl(a,b)), T(Impl(b,a)) ]
                    )

    correctRules = t.tested == t.passed

    t.testTableau(True, [ F(Implication(a, a)) ])

    t.testTableau(True, [ F(Implication(Var('a'), Var('a'))) ])

    t.testTableau(True, [ F(Or(a, Not(a))) ])

    t.testTableau(True, [ T(a), F(a) ])

    t.testTableau(True, [ T(a), F(a), T(a) ])

    t.testTableau(True, [ T(a), F(a), T(b) ])

    t.testTableau(False, [ T(Or(a,b)), F(a) ])

    t.testTableau(True, [ T(And(a,b)), F(a) ])

    demorgan1 = Equivalence( Not( And([ a, b ]) ), Or([ Not(a), Not(b) ]) )
    t.testTableau(True, [ F(demorgan1) ])

    demorgan2 = Equivalence( Not( Or([ a, b ]) ), And([ Not(a), Not(b) ]) )
    t.testTableau(True, [ F(demorgan2) ])

    demorgan3 = Equivalence( Not( Or([ a, b, c ]) ),
                             And([ Not(a), Not(b), Not(c) ]) )
    t.testTableau(True, [ F(demorgan3) ])

    contraposition = Equivalence( Impl(a, b), Impl( Not(b), Not(a) ) )
    t.testTableau(True, [ F(contraposition) ])

    impl_impl_distrib = Impl( Impl(a, Impl(b, c)),
                              Impl( Impl(a, b), Impl(a, c) ) )
    t.testTableau(True, [ F(impl_impl_distrib) ])

    impl_or = Equivalence( Impl(a, b), Or([ Not(a), b ]) )
    t.testTableau(True, [ F(impl_or) ])

    impl_and = Equivalence( Impl(a, b), Not( And([ a, Not(b) ]) ) )
    t.testTableau(True, [ F(impl_and) ])

    or_and_distrib = Equivalence( Or([ a, And([ b, c ]) ]),
                                  And([ Or([ a, b ]), Or([ a, c ]) ]) )
    t.testTableau(True, [ F(or_and_distrib) ])

    bad_demorgan1 = Equivalence( Not( And([ a, b ]) ), Or([ a, b ]) )
    t.testTableau(False, [ F(bad_demorgan1) ])

    bad_demorgan2 = Equivalence( Not( Or([ a, b ]) ), Or([ Not(a), Not(b) ]) )
    t.testTableau(False, [ F(bad_demorgan2) ])

    bad_demorgan3 = Equivalence( Not( Or([ a, b, c ]) ),
                             And([ Not(a), b, Not(c) ]) )
    t.testTableau(False, [ F(bad_demorgan3) ])

    bad_contraposition = Equivalence( Impl(a, b), Impl( b, a ) )
    t.testTableau(False, [ F(bad_contraposition) ])

    bad_impl_impl_distrib = Impl( Impl(a, Impl(b, c)),
                              Impl( Impl(b, a), Impl(c, a) ) )
    t.testTableau(False, [ F(bad_impl_impl_distrib) ])

    bad_impl_and = Equivalence( Impl(a, b), Not( And([ Not(a), b ]) ) )
    t.testTableau(False, [ F(bad_impl_and) ])

    bad_or_and_distrib = Equivalence( Or([ a, And([ b, c ]) ]),
                                  Or([ And([ a, b ]), And([ a, c ]) ]) )
    t.testTableau(False, [ F(bad_or_and_distrib) ])

    # Keď Katka nakreslí obrazok, je na ňom bud mačka alebo pes. Obrázok mačky
    # Katkin pes vždy hneď roztrhá. Ak jej pes roztrhá obrazok, Katka je
    # smutná. Dokážte, že ak Katka nakreslila obrázok a je šťastná, tak na jej
    # obrázku je pes.
    ax1 = Implication(
            Var('obrazok'),
            And([
                Or([Var('macka'),Var('pes')]),
                Or([Not(Var('macka')),Not(Var('pes'))]),
            ]),
        )
    ax2 = Implication(Var('macka'), Var('roztrha'))
    ax3 = Implication(Var('roztrha'), Var('smutna'))
    conclusion = Implication(
                    And( [ Var('obrazok'), Not(Var('smutna')) ] ),
                    Var('pes'),
                )

    cax1 = Conjunction([ ax1, ax2, ax3 ])
    t.testTableau(True, [ T(Conjunction([cax1, Not(conclusion)])) ])
    t.testTableau(True, [ F(Implication(cax1, conclusion)) ])
    t.testTableau(True, [ T(cax1), F(conclusion) ])
    t.testTableau(True, [ T(ax1), T(ax2), T(ax3), F(conclusion) ])
    t.testTableau(False, [ T(cax1) ])
    t.testTableau(False, [ F(conclusion) ])

    # Bez práce nie sú koláče. Ak niekto nemá ani koláče, ani chleba, tak bude
    # hladný. Na chlieb treba múku. Dokážte, že ak niekto nemá múku a je
    # najedený (nie je hladný), tak pracoval.
    ax1 = Implication(Var('kolace'), Var('praca'))

    ax2 = Implication(
            And([Not(Var('kolace')),Not(Var('chlieb'))]),
            Var('hlad')
        )
    ax3 = Implication(Var('chlieb'), Var('muka'))

    conclusion = Implication(
                    And( [ Not(Var('muka')), Not(Var('hlad')) ] ),
                    Var('praca'),
                )

    cax1 = Conjunction([ ax1, ax2, ax3 ])
    t.testTableau(True, [ T(Conjunction([cax1, Not(conclusion)])) ])
    t.testTableau(True, [ F(Implication(cax1, conclusion)) ])
    t.testTableau(True, [ T(cax1), F(conclusion) ])
    t.testTableau(True, [ T(ax1), T(ax2), T(ax3), F(conclusion) ])
    t.testTableau(False, [ T(cax1) ])
    t.testTableau(False, [ F(conclusion) ])

    print("END")

except FailedTestException:
    print("Stopped on first failed test!")
finally:
    if not correctRules:
        print()
        print("WARNING:")
        print("getType and signedSub implementations are not correct.")
        print("Any PASSED tableaux can be false positives!")
        print()
    t.status()

# vim: set sw=4 ts=4 sts=4 et :
