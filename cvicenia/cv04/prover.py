#!/usr/bin/env python3

import os
import sys
sys.path[0:0] = [os.path.join(sys.path[0], '../examples/sat')]
import sat

import cnf
from formula import Formula, Variable, Negation, Conjunction, Disjunction, Implication, Equivalence

def prove(theory, consequence):
    """ Dokaze, ci z theory (zoznam formul) vyplyva formula consequence. """
    # mali by sme skontrolovat, ci teoria sama o sebe dava zmysel
    # ale ak by aj bola nekonzistentna, tak z nej logicky vyplyva
    # vsetko, takze to tu kontrolovat nebudeme

    f = Conjunction([
            Conjunction(theory),
            Negation(consequence)
        ])
    c = f.toCnf()

    varMap = cnf.VariableMap()
    varMap.extend(c)

    fn = "problem_cnf.txt"
    of = open(fn, "w")
    c.writeToFile(of, varMap)
    of.close()

    solver = sat.SatSolver()
    ok, sol = solver.solve(fn, "problem_out.txt")
    if ok:
        print("!!! {}   NEVYPLYVA Z   {} lebo:".format(
            consequence.toString(),
            ', '.join([x.toString() for x in theory])))
        print("  {}".format(repr(sol)))
        revMap = varMap.reverse()
        print("  {}".format(repr([str(cnf.Literal.fromInt(i,varMap)) for i in sol])))
    else:
        print("{}   VYPLYVA Z   {}".format(
            consequence.toString(),
            ', '.join([x.toString() for x in theory])))


Not = Negation
Var = Variable
And = Conjunction
Or = Disjunction
Impl = Implication


prove(
    [
        Impl(Var('dazdnik'), Not(Var('prsi'))),
        Impl(
            Var('mokraCesta'),
            Or( [ Var('prsi'), Var('umyvacieAuto') ] ),
        ),
        Impl(Var('umyvacieAuto'), Not(Var('vikend'))),
    ],
    Impl(
        And( [ Var('dazdnik'), Var('mokraCesta') ] ),
        Not(Var('vikend')),
    )
)


party = [
    Impl(Var('kim'), Not(Var('sarah'))),
    Impl(Var('jim'), Var('kim')),
    Impl(Var('sarah'), Var('jim')),
    Or([Var('kim'), Var('jim'), Var('sarah')]),
]

prove(
    party,
    Var('sarah')
)

prove(
    party,
    Var('kim')
)

# vim: set sw=4 ts=4 sts=4 et :
