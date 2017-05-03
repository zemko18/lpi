#!/usr/bin/env python3

class Structure:
    def __init__(self, domain = frozenset(), iC = {}, iF = {}, iP = {}):
        self.domain = frozenset(domain)
        self.iC = iC
        self.iF = iF
        self.iP = iP

class Valuation(dict):
    def set(self, var, value):
        new = Valuation(self)
        new.update({var: value})
        return new

class NotApplicable(Exception):
    pass

# vim: set sw=4 ts=4 sts=4 et:
