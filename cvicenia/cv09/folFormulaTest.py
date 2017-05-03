#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import unittest
from folSemantics import Structure, Valuation
import folFormula as ff

def eq(self, other):
    return self.equals(other)

try:
    # hasattr(..., '__eq__') would find the one from object ;(
    if '__eq__' not in ff.Term.__dict__:
        print('inserted __eq__ stub for Term')
        ff.Term.__eq__ = eq
    if '__eq__' not in ff.Formula.__dict__:
        print('inserted __eq__ stub for Formula')
        ff.Formula.__eq__ = eq
except AttributeError:
    # catch so that Term tests can run even while there's no Formula impl yet etc...
    # will fail somewhere inside tests when Term / Formula is actually used
    pass

class Test1Term(unittest.TestCase):
    def test0Var(self):
        n = 'xxx'
        v = ff.Variable(n)

        self.assertIsInstance(v, ff.Term)
        self.assertEqual(v.name(), n)
        self.assertListEqual(v.subts(), [])
        self.assertEqual(v.toString(), n)
        self.assertSetEqual(v.variables(), frozenset([n]))
        self.assertSetEqual(v.constants(), frozenset([]))
        self.assertSetEqual(v.functions(), frozenset([]))

    def test1Const(self):
        n = 'ccc'
        c = ff.Constant(n)

        self.assertIsInstance(c, ff.Term)
        self.assertEqual(c.name(), n)
        self.assertListEqual(c.subts(), [])
        self.assertEqual(c.toString(), n)
        self.assertSetEqual(c.variables(), frozenset([]))
        self.assertSetEqual(c.constants(), frozenset([n]))
        self.assertSetEqual(c.functions(), frozenset([]))

    def testFunc1(self):
        cn, fn = 'ccc', 'fff'
        c = ff.Constant(cn)
        f = ff.Function(fn, [c])

        self.assertIsInstance(f, ff.Term)
        self.assertEqual(f.name(), fn)
        self.assertListEqual(f.subts(), [c])
        self.assertEqual(f.toString(), '%s(%s)' % (fn, cn))
        self.assertSetEqual(f.variables(), frozenset([]))
        self.assertSetEqual(f.constants(), frozenset([cn]))
        self.assertSetEqual(f.functions(), frozenset([fn]))

    def testFunc2(self):
        cn, vn, fn, gn = 'ccc', 'xx', 'fff', 'ggg'
        c, v = ff.Constant(cn), ff.Variable(vn)
        g = ff.Function(gn, [c])
        f = ff.Function(fn, [g, v])

        self.assertIsInstance(f, ff.Term)
        self.assertEqual(f.name(), fn)
        self.assertListEqual(f.subts(), [g, v])
        self.assertEqual(f.toString(), '%s(%s(%s),%s)' % (fn, gn, cn, vn))
        self.assertSetEqual(f.variables(), frozenset([vn]))
        self.assertSetEqual(f.constants(), frozenset([cn]))
        self.assertSetEqual(f.functions(), frozenset([fn,gn]))

    def testEquals(self):
        V, C, F = ff.Variable, ff.Constant, ff.Function

        self.assertEqual(V('xxx'), V('xxx'))
        self.assertEqual(C('xxx'), C('xxx'))
        self.assertEqual(F('fff'), F('fff'))
        self.assertEqual(F('fff', [V('xxx')]), F('fff', [V('xxx')]))
        self.assertEqual(F('fff', [C('ccc')]), F('fff', [C('ccc')]))
        self.assertEqual(
            F('f', [F('g', [V('x'), C('c')]), C('c')]),
            F('f', [F('g', [V('x'), C('c')]), C('c')])
        )

        self.assertNotEqual(V('xxx'), C('xxx'))
        self.assertNotEqual(C('ccc'), V('vvv'))
        self.assertNotEqual(F('fff'), F('fff', [V('x')]))
        self.assertNotEqual(F('fff', [V('x')]), F('fff'))
        self.assertNotEqual(F('fff'), F('fff', [C('c')]))
        self.assertNotEqual(F('fff', [C('c')]), F('fff'))

        self.assertNotEqual(F('fff', [F('ggg', [C('c')])]), F('fff', [F('ggg'), C('c')]))


    def testSubstitute(self):
        V, C, F = ff.Variable, ff.Constant, ff.Function

        self.assertEqual(
            V('x').substitute('x', C('a')),
            C('a')
        )
        self.assertEqual(
            V('y').substitute('x', C('a')),
            V('y')
        )

        self.assertEqual(
            C('a').substitute('x', V('x')),
            C('a')
        )

        self.assertEqual(
            C('a').substitute('a', C('b')),
            C('a')
        )

        self.assertEqual(
            F('f', [V('y')]).substitute('y', F('g', [C('c')])),
            F('f', [F('g', [C('c')])])
        )

        self.assertEqual(
            F('f', [V('y')]).substitute('f', C('c')),
            F('f', [V('y')])
        )

        self.assertEqual(
            F('f', [V('x'), V('y')]).substitute('x', C('a')),
            F('f', [C('a'), V('y')])
        )

        self.assertEqual(
            F('f', [V('x'), V('x')]).substitute('x', C('a')),
            F('f', [C('a'), C('a')])
        )

        self.assertEqual(
            F('f', [V('x'), V('x')]).substitute('x', V('x')),
            F('f', [V('x'), V('x')])
        )
        self.assertEqual(
            F('f', [V('x'), V('x')]).substitute('x', F('f', [V('x'), V('y')])),
            F('f', [F('f', [V('x'), V('y')]), F('f', [V('x'), V('y')])])
        )

    def testEval(self):
        V, C, F = ff.Variable, ff.Constant, ff.Function
        a,b,c,d,e,mm,x = 1,2,3,4,5,6,7
        bffint = { a: b, b: a, c: d, d: c, e: x, mm: x, x: x}
        m = Structure(
            domain = [a,b,c,d,e,mm,x],
            iC = { 'Anicka': a, 'Betka': b, 'Cecilka': c, 'Edo':e },
            iP = {
                'dievca': frozenset([(a,), (b,), (c,), (d,)]),
                'ma_rada': frozenset([
                 (a, b), (a, c),
                 (b, a), (b, d), (b, mm),
                 (c, a), (c, b), (c, c), (c, d), (c, e), (c, mm),
                 (d, c), (d, e),
                 (e, b),
                 (mm, mm), (mm,x),
                ])
            },
            iF = { 'bff': lambda x: bffint[x] },
        )

        e1 = Valuation({'x': a, 'y': d })
        self.assertEqual(C('Anicka').eval(m, e1), a)
        self.assertEqual(F('bff', [C('Cecilka')]).eval(m, e1), d)
        self.assertEqual(F('bff', [F('bff', [C('Betka')])]).eval(m, e1), b)
        self.assertEqual(V('x').eval(m, e1), a)
        self.assertEqual(F('bff', [V('y')]).eval(m, e1), c)
        self.assertEqual(F('bff', [F('bff', [V('x')])]).eval(m, e1), a)

        e2 = Valuation({'x': mm, 'y': c })
        self.assertEqual(C('Anicka').eval(m, e2), a)
        self.assertEqual(F('bff', [C('Cecilka')]).eval(m, e2), d)
        self.assertEqual(F('bff', [F('bff', [C('Betka')])]).eval(m, e2), b)
        self.assertEqual(V('x').eval(m, e2), mm)
        self.assertEqual(F('bff', [V('y')]).eval(m, e2), d)
        self.assertEqual(F('bff', [F('bff', [V('x')])]).eval(m, e2), x)


class Test2Formula(unittest.TestCase):
    def testPredicate(self):
        V, C, F = ff.Variable, ff.Constant, ff.Function
        P, A, E = ff.Predicate, ff.ForAll, ff.Exists

        cn, pn = 'ccc', 'Ppp'
        c = C(cn)
        p = P(pn, [c])

        self.assertIsInstance(p, ff.Formula)
        self.assertEqual(p.name(), pn)
        self.assertListEqual(p.subfs(), [])
        self.assertListEqual(p.subts(), [c])
        self.assertEqual(p.toString(), '%s(%s)' % (pn, cn))
        self.assertSetEqual(p.variables(), frozenset([]))
        self.assertSetEqual(p.constants(), frozenset([cn]))
        self.assertSetEqual(p.functions(), frozenset([]))
        self.assertSetEqual(p.predicates(), frozenset([pn]))

    def testEquals(self):
        V, C, F = ff.Variable, ff.Constant, ff.Function
        P, A, E = ff.Predicate, ff.ForAll, ff.Exists
        Not, And, Or, Impl, Eq = ff.Negation, ff.Conjunction, ff.Disjunction, ff.Implication, ff.Equivalence

        self.assertEqual(P('p', [V('x')]), P('p', [V('x')]))
        self.assertEqual(P('p', [C('c'), V('x')]), P('p', [C('c'), V('x')]))
        self.assertEqual(Not(P('p', [V('x')])), Not(P('p', [V('x')])))
        self.assertEqual(
            And([P('p', [V('x')]), P('q', [C('c')])]),
            And([P('p', [V('x')]), P('q', [C('c')])])
        )
        self.assertEqual(
            Or([P('p', [V('x')]), P('q', [C('c')])]),
            Or([P('p', [V('x')]), P('q', [C('c')])])
        )
        self.assertEqual(
            Impl(P('p', [V('x')]), P('q', [C('c')])),
            Impl(P('p', [V('x')]), P('q', [C('c')]))
        )
        self.assertEqual(
            Eq(P('p', [V('x')]), P('q', [C('c')])),
            Eq(P('p', [V('x')]), P('q', [C('c')]))
        )
        self.assertEqual(
            A('x', P('p', [V('x')])),
            A('x', P('p', [V('x')])),
        )
        self.assertEqual(
            E('x', P('p', [V('x')])),
            E('x', P('p', [V('x')])),
        )

        self.assertNotEqual(P('p', [V('x')]), P('p', [V('y')]))
        self.assertNotEqual(P('p', [V('x')]), P('q', [V('x')]))
        self.assertNotEqual(P('p', [V('x')]), P('p', [C('c')]))
        self.assertNotEqual(Not(P('p', [V('x')])), P('p', [V('x')]))
        self.assertNotEqual(
            And([P('p', [V('x')]), P('q', [C('c')])]),
            And([P('q', [C('c')]), P('p', [V('x')])])
        )
        self.assertNotEqual(
            And([P('p', [V('x')]), P('q', [C('c')])]),
            Or( [P('p', [V('x')]), P('q', [C('c')])])
        )
        self.assertNotEqual(
            A('x', P('p', [V('x')])),
            E('x', P('p', [V('x')])),
        )
        self.assertNotEqual(
            A('x', P('p', [V('x')])),
            A('y', P('p', [V('x')])),
        )
        self.assertNotEqual(
            A('x', P('p', [V('x')])),
            A('x', P('p', [V('y')])),
        )
        self.assertNotEqual(
            E('x', P('p', [V('x')])),
            E('y', P('p', [V('x')])),
        )
        self.assertNotEqual(
            E('x', P('p', [V('x')])),
            E('x', P('p', [V('y')])),
        )





    def testCollections(self):
        V, C, F = ff.Variable, ff.Constant, ff.Function
        P, A, E = ff.Predicate, ff.ForAll, ff.Exists
        Not, And, Or, Impl, Eq = ff.Negation, ff.Conjunction, ff.Disjunction, ff.Implication, ff.Equivalence

        an, bn, cn = 'aaa', 'bb', 'cccc'
        xn, yn = 'xxx', 'y'
        fn, gn = 'fff', 'gg'
        pn, qn = 'Ppp', 'Qq'

        f = Eq(
            Impl(
                Not(And([
                    P(pn, [V(xn)]),
                    P(qn, [C(an), C(bn)]),
                ])),
                Or([
                    P(qn, [F(fn, [C(cn), F(gn, [V(yn)])]), V(xn)]),
                    P(pn, [F(gn, [C(an)])])
                ])
            ),
            Not(P(qn, [C(cn), F(gn, [V(yn)])]))
        )

        self.assertSetEqual(f.variables(), frozenset([xn, yn]))
        self.assertSetEqual(f.constants(), frozenset([an, bn, cn]))
        self.assertSetEqual(f.functions(), frozenset([fn, gn]))
        self.assertSetEqual(f.predicates(), frozenset([pn, qn]))

    def testToString(self):
        V, C, F = ff.Variable, ff.Constant, ff.Function
        P, A, E = ff.Predicate, ff.ForAll, ff.Exists
        Negation, Conjunction, Disjunction, Implication, Equivalence = \
            ff.Negation, ff.Conjunction, ff.Disjunction, ff.Implication, ff.Equivalence

        formulas = [
            (
                Negation(P('p', [F('f', [V('x'), C('c')])])), '-p(f(x,c))',
            ),

            (
                Conjunction( [ P('p', [F('f', [V('x'), C('c')])]), P('p', [F('f', [C('c'), V('x')])]) ] ),
                '(p(f(x,c))&p(f(c,x)))',
            ),
            (
                Disjunction( [ P('p', [F('f', [V('x'), C('c')])]), P('p', [F('f', [C('c'), V('x')])]) ] ),
                '(p(f(x,c))|p(f(c,x)))',
            ),
            (
                Implication( P('p', [F('f', [V('x'), C('c')])]), P('p', [F('f', [C('c'), V('x')])]) ),
                '(p(f(x,c))->p(f(c,x)))',
            ),
            (
                Equivalence( P('p', [F('f', [V('x'), C('c')])]), P('p', [F('f', [C('c'), V('x')])]) ),
                '(p(f(x,c))<->p(f(c,x)))',
            ),
            (
                Disjunction([
                    Negation(Implication(P('p', [F('f', [V('x'), C('c')])]),P('p', [F('f', [C('c'), V('x')])]))),
                    Negation(Implication(P('p', [F('f', [C('c'), V('x')])]),P('p', [F('f', [V('x'), C('c')])])))
                ]),
                '(-(p(f(x,c))->p(f(c,x)))|-(p(f(c,x))->p(f(x,c))))',
            ),
            (
                Conjunction([
                    Implication(P('p', [F('f', [V('x'), C('c')])]),P('p', [F('f', [C('c'), V('x')])])),
                    Implication(Negation(P('p', [F('f', [V('x'), C('c')])])), P('q', [V('z')]))
                ]),
                '((p(f(x,c))->p(f(c,x)))&(-p(f(x,c))->q(z)))',
            ),
            (
                Equivalence(
                    Conjunction([
                        P('p', [F('f', [V('x'), C('c')])]),
                        Negation(P('p', [F('f', [C('c'), V('x')])]))
                    ]),
                    Disjunction([
                        P('p', [F('f', [V('x'), C('c')])]),
                        Implication(
                            P('p', [F('f', [C('c'), V('x')])]),
                            P('p', [F('f', [V('x'), C('c')])])
                        )
                    ])
                ),
                '((p(f(x,c))&-p(f(c,x)))<->(p(f(x,c))|(p(f(c,x))->p(f(x,c)))))',
            ),
        ]
        for f, s in formulas:
            with self.subTest(formula=s):
                self.assertEqual(f.toString(), s)

    def testIsSatisfied(self):
        V, C, F = ff.Variable, ff.Constant, ff.Function
        P, A, E = ff.Predicate, ff.ForAll, ff.Exists
        Not, And, Or, Impl, Eq = ff.Negation, ff.Conjunction, ff.Disjunction, ff.Implication, ff.Equivalence

        a,b,c,d,e,mm,x = 1,2,3,4,5,6,7
        bffint = { a: b, b: a, c: d, d: c, e: x, mm: x, x: x}
        m = Structure(
            domain = [a,b,c,d,e,mm,x],
            iC = { 'Anicka': a, 'Betka': b, 'Cecilka': c, 'Edo':e },
            iP = {
                'dievca': frozenset([(a,), (b,), (c,), (d,)]),
                'ma_rada': frozenset([
                 (a, b), (a, c),
                 (b, a), (b, d), (b, mm),
                 (c, a), (c, b), (c, c), (c, d), (c, e), (c, mm),
                 (d, c), (d, e),
                 (e, b),
                 (mm, mm), (mm,x),
                ])
            },
            iF = { 'bff': lambda x: bffint[x] },
        )

        Anicka = C('Anicka')
        Betka = C('Betka')
        Cecilka = C('Cecilka')
        Edo = C('Edo')
        vx = V('x')
        vy = V('y')
        def bff(x): return F('bff', [x])
        def dievca(x): return P('dievca', [x])
        def ma_rada(x, y): return P('ma_rada', [x,y])

        e1 = Valuation({'x': b, 'y': c })

        def checkIsSat(sat, f, s):
            msg = '%s is%s satisfied, when it should%s be' % (s, " not" if sat else "", "" if sat else " not")
            self.assertEqual(f.isSatisfied(m, e1), sat, msg = msg)

        checkIsSat( True, dievca(Anicka), 'dievca(Anicka)')
        checkIsSat(False, dievca(Edo), 'dievca(Edo)')
        checkIsSat( True, dievca(vx), 'dievca(x)')
        checkIsSat( True, ma_rada(Anicka, Betka), 'ma_rada(Anicka,Betka)')

        checkIsSat(False, Not(dievca(Anicka)), '-dievca(Anicka)')
        checkIsSat( True, Not(dievca(Edo)), '-dievca(Edo)')

        checkIsSat( True, And([dievca(Anicka), ma_rada(Anicka, Betka), ma_rada(Anicka, Cecilka)]),
                '(dievca(Anicka)&ma_rada(Anicka,Betka)&ma_rada(Anicka,Cecilka))')
        checkIsSat(False, And([dievca(Anicka), ma_rada(Anicka, Betka), ma_rada(Anicka, Edo)]),
                '(dievca(Anicka)&ma_rada(Anicka,Betka)&ma_rada(Anicka,Edo))')

        checkIsSat(True, Or([dievca(Anicka), ma_rada(Anicka, Betka), ma_rada(Anicka, Edo)]),
                '(dievca(Anicka)|ma_rada(Anicka,Betka)|ma_rada(Anicka,Edo))')
        checkIsSat(False, Or([dievca(Edo), ma_rada(Anicka, Edo)]),
                '(dievca(Edo)|ma_rada(Anicka,Edo))')

        checkIsSat( True, Impl(ma_rada(Anicka, Edo), dievca(Edo)), '(ma_rada(Anicka,Edo)->dievca(Edo))')
        checkIsSat( True, Impl(dievca(Anicka), dievca(Betka)), '(dievca(Anicka)->dievca(Betka))')
        checkIsSat(False, Impl(dievca(Anicka), dievca(Edo)), '(dievca(Anicka)->dievca(Edo))')

        checkIsSat( True, Eq(dievca(Anicka), dievca(Betka)), '(dievca(Anicka)<->dievca(Betka))')
        checkIsSat(False, Eq(dievca(Anicka), dievca(Edo)), '(dievca(Anicka)<->dievca(Edo))')

        checkIsSat(False, ma_rada(Anicka, Edo), 'ma_rada(Anicka,Edo)')
        checkIsSat( True, And([ma_rada(Anicka, vx), dievca(vx)]), '(ma_rada(Anicka,x)&dievca(x))')
        checkIsSat(False, A('x', ma_rada(vy, vx)), '∀x ma_rada(y,x)')
        checkIsSat( True, E('y', And([ma_rada(Betka, vy), Not(dievca(vy))])), '∃y (ma_rada(Betka,y)&-dievca(y))')
        checkIsSat( True, A('x', Impl(dievca(vx), ma_rada(vx, bff(vx)))), '∀x (dievca(x)->ma_rada(x,bff(x)))')
        checkIsSat( True, A('x', Impl(dievca(vx), E('y', ma_rada(vx, vy)))), '∀x (dievca(x)->∃y ma_rada(x,y))')
        checkIsSat(False, E('x', And([dievca(vx), A('y', Not(ma_rada(vx, vy)))])), '∃x (dievca(x)&∀y -ma_rada(x,y))')

    def testFreeVariables(self):
        V, C, F = ff.Variable, ff.Constant, ff.Function
        P, A, E = ff.Predicate, ff.ForAll, ff.Exists
        Not, And, Or, Impl, Eq = ff.Negation, ff.Conjunction, ff.Disjunction, ff.Implication, ff.Equivalence

        xn, yn, zn = 'x', 'y', 'z'

        def p(*args): return P('p', list(args))
        def f(*args): return F('f', list(args))
        c = C('c')

        self.assertSetEqual(p(C('c')).freeVariables(), frozenset())
        self.assertSetEqual(p(V(xn)).freeVariables(), frozenset([xn]))
        self.assertSetEqual(p(V(xn), f(V(zn), C('c'))).freeVariables(), frozenset([xn, zn]))

        self.assertSetEqual(A('x', p(V(xn), V(yn), V(zn))).freeVariables(), frozenset([yn, zn]))
        self.assertSetEqual(
            Not(A('x', p(V(xn), V(yn), V(zn)))).freeVariables(), frozenset([yn, zn])
        )
        self.assertSetEqual(
            And([A('x', p(V(xn), V(yn), V(zn))), p(V(yn)), p(c)]).freeVariables(), frozenset([yn, zn])
        )
        self.assertSetEqual(
            Or([A('x', p(V(xn), V(yn), V(zn))), p(V(yn)), p(c)]).freeVariables(), frozenset([yn, zn])
        )
        self.assertSetEqual(
            Impl(A('x', p(V(xn), V(yn), V(zn))), p(V(yn))).freeVariables(), frozenset([yn, zn])
        )
        self.assertSetEqual(
            Eq(A('x', p(V(xn), V(yn), V(zn))), p(V(yn))).freeVariables(), frozenset([yn, zn])
        )

        self.assertSetEqual(E('x', p(V(xn), V(yn), V(zn))).freeVariables(), frozenset([yn, zn]))
        self.assertSetEqual(
            Not(E('x', p(V(xn), V(yn), V(zn)))).freeVariables(), frozenset([yn, zn])
        )
        self.assertSetEqual(
            And([E('x', p(V(xn), V(yn), V(zn))), p(V(yn)), p(c)]).freeVariables(), frozenset([yn, zn])
        )
        self.assertSetEqual(
            Or([E('x', p(V(xn), V(yn), V(zn))), p(V(yn)), p(c)]).freeVariables(), frozenset([yn, zn])
        )
        self.assertSetEqual(
            Impl(E('x', p(V(xn), V(yn), V(zn))), p(V(yn))).freeVariables(), frozenset([yn, zn])
        )
        self.assertSetEqual(
            Eq(E('x', p(V(xn), V(yn), V(zn))), p(V(yn))).freeVariables(), frozenset([yn, zn])
        )

        self.assertSetEqual(A('x', E('y', p(V(xn),V(yn),V(zn)))).freeVariables(), frozenset([zn]))
        self.assertSetEqual(E('x', A('y', p(V(xn),V(yn),V(zn)))).freeVariables(), frozenset([zn]))


    def testSubstitute(self):
        V, C, F = ff.Variable, ff.Constant, ff.Function
        P, A, E = ff.Predicate, ff.ForAll, ff.Exists
        Not, And, Or, Impl, Eq = ff.Negation, ff.Conjunction, ff.Disjunction, ff.Implication, ff.Equivalence

        def p(*args): return P('p', list(args))
        def f(*args): return F('f', list(args))
        c = C('c')
        x, y, z = V('x'), V('y'), V('z')

        self.assertEqual(
            p(f(x,y)).substitute('x', c),
            p(f(c,y))
        )
        self.assertEqual(
            Not(p(x,y)).substitute('x', c),
            Not(p(c,y))
        )
        self.assertEqual(
            And([p(x), p(y), p(z), p(f(x))]).substitute('x', c),
            And([p(c), p(y), p(z), p(f(c))])
        )
        self.assertEqual(
            Or([p(x), p(y), p(z), p(f(x))]).substitute('x', c),
            Or([p(c), p(y), p(z), p(f(c))])
        )
        self.assertEqual(
            Impl(p(x), p(f(x,y))).substitute('x', c),
            Impl(p(c), p(f(c,y)))
        )
        self.assertEqual(
            Eq(p(x), p(f(x,y))).substitute('x', c),
            Eq(p(c), p(f(c,y)))
        )
        self.assertEqual(
            A('x', Impl(p(x), p(y))).substitute('x', c),
            A('x', Impl(p(x), p(y)))
        )
        self.assertEqual(
            A('x', Impl(p(x), p(y))).substitute('y', c),
            A('x', Impl(p(x), p(c)))
        )
        self.assertEqual(
            E('x', Impl(p(x), p(y))).substitute('x', c),
            E('x', Impl(p(x), p(y)))
        )
        self.assertEqual(
            E('x', Impl(p(x), p(y))).substitute('y', c),
            E('x', Impl(p(x), p(c)))
        )
        self.assertEqual(
            A('x', Impl(p(y), E('y', p(y,x)))).substitute('y', c),
            A('x', Impl(p(c), E('y', p(y,x))))
        )
        self.assertEqual(
            E('x', Impl(p(y), A('y', p(y,x)))).substitute('y', c),
            E('x', Impl(p(c), A('y', p(y,x))))
        )

        self.assertEqual(
            And([p(x,y), E('x', p(x,y))]).substitute('x', c),
            And([p(c,y), E('x', p(x,y))])
        )

if __name__ == '__main__':
    unittest.main()

# vim: set sw=4 ts=4 sts=4 et:
