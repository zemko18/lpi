#! /bin/env python3

import os.path
import shutil
import collections
import subprocess
import sys


class SimpleExecutableSolver:
    def __init__(self, executable):
        self.executable = executable
    def compile(self):
        return True
    def cmdline(self):
        return [os.path.abspath(self.executable)]

class PythonSolver:
    def __init__(self, executable):
        self.executable = executable
    def compile(self):
        return True
    def cmdline(self):
        return [sys.executable, self.executable]

class CPPSolver:
    def __init__(self, executable):
        self.executable = executable
    def compile(self):
        #TODO
        return True
    def cmdline(self):
        return [os.path.abspath(self.executable)]

class JavaSolver:
    def __init__(self, cls='SatSolver'):
        self.cls = cls
    def compile(self):
        # TODO
        return True
    def cmdline(self):
        return ['java', '-cp', '.', cls]

import time
def now():
    try:
       return time.perf_counter() # >=3.3
    except AttributeError:
       return time.time() # this is not monotonic!

class SatTester:
    minTestTime = 0.5
    defaultTimeout = 60
    testTimeouts = {
            'normal' : 30,
            'bigger' : 2*60,
            }

    OK = 1
    WA = 2
    BADASS = 3
    TLE = 4
    RE = 5
    NO = 6
    WO = 7
    statusStrings = {
            OK: 'OK',
            WA: 'Wrong answer',
            BADASS: 'Bad assignment',
            TLE: 'TLE',
            RE: 'Runtime error',
            NO: 'No output',
            WO: 'Bad output format',
            }
    TestStat = collections.namedtuple('TestStat', 'test status statusString time count')

    def __init__(self, args):
        import argparse
        parser = argparse.ArgumentParser(description = 'Run tests for SAT solver')
        parser.add_argument('--test', '-t', default = None, help='Run the specified test (file name)')
        parser.add_argument('--bigger', '-b', action='store_true', help='Run larger test cases')
        parser.add_argument('--quiet', '-q', action='store_true', help='Don\'t show solvers stdout/stderr output')
        parser.add_argument('--ignoreRetcode', '-i', action='store_true', help='Ignore return code from solver')
        parser.add_argument('solver', nargs='?', default = None, action='store', help='Path to the solver executable')
        args = parser.parse_args(args[1:])

        self.biggerTests = args.bigger
        self.quiet = args.quiet
        self.ignoreRetcode = args.ignoreRetcode

        self.solverFile = None
        if args.solver is None:
            for f in [ 'satsolver.cpp', 'SatSolver.java', 'satsolver.py' ]:
                if os.path.exists(f):
                    self.solverFile = f
                    break
        else:
            if os.path.exists(args.solver):
                self.solverFile = args.solver
            else:
                print('Solver "%s" does not exist.' % args.solver)

        if self.solverFile is None:
            raise Exception('No solver found!')

        print('Testing %s' % self.solverFile)


        self.solver = self.getSolver()

        if args.test:
            self.tests = [ args.test ]
        else:
            self.tests = self.enumerateTests()

        self.tests = sorted(self.tests, key = os.path.basename)


    def getSolver(self):
        import fnmatch
        if fnmatch.fnmatch(self.solverFile, '*.cpp'):
            return CPPSolver(self.solverFile.replace('.cpp', ''))
        elif fnmatch.fnmatch(self.solverFile, '*.java'):
            return JavaSolver(self.solverFile.replace('.java', ''))
        elif fnmatch.fnmatch(self.solverFile, '*.py'):
            return PythonSolver(self.solverFile)
        else:
            return SimpleExecutableSolver(self.solverFile)

    def enumerateTests(self):
        testFileFolders = [
            'testData/normal/sat', 'testData/normal/unsat',
            ]
        if self.biggerTests:
            testFileFolders.extend([
                'testData/bigger/sat', 'testData/bigger/unsat',
                ])
        import glob
        tests = []

        for folder in testFileFolders:
            tests += glob.glob(folder+'/*.cnf')
        return tests

    def testTimeout(self, test):
        from os.path import basename, dirname
        category = basename(dirname(dirname(test)))
        if category in self.testTimeouts:
            return self.testTimeouts[category]
        else:
            return self.defaultTimeout

    def expectedTestSat(self, test):
        from os.path import basename, dirname
        case = basename(dirname(test))
        if case == 'sat':
            return 'SAT'
        else:
            return 'UNSAT'

    def checkOutput(self, test, oFileName):
        if not os.path.exists(oFileName):
            return self.NO
        with open(oFileName, 'r') as oFile:
            sat = oFile.readline().strip()
            if sat != self.expectedTestSat(test):
                return self.WA
            if sat == 'SAT':
                try:
                    sol = set(int(x) for x in oFile.readline().split())
                    if 0 not in sol:
                        # we don't really check for it to be at the end... 
                        print('Solution is not finished by 0')
                        return self.WO
                    sol.remove(0)
                    with open(test, 'r') as iFile:
                        for line in iFile:
                            line = line.strip()
                            if line[0] in ['c','p']:
                                continue
                            cls=set()
                            ncls=0
                            for x in (int(x) for x in line.split()):
                                if x == 0:
                                    if cls.isdisjoint(sol):
                                        print(
                                            'Clause %d %s not satisfied by solution %s' % (
                                                ncls,
                                                str(sorted(cls,key=abs)),
                                                str(sorted(sol,key=abs))
                                            )
                                        )
                                        return self.BADASS
                                    ncls += 1
                                else:
                                    cls.add(x)

                except:
                    return self.WO
        return self.OK

    def runCommand(self, cmdline, to):
        retcode = -1
        kwargs = {}
        if sys.version_info >= (3,3):
            kwargs['timeout'] = to
            timeoutException = subprocess.TimeoutExpired
        else:
            class FakeExcp(Exception):
                pass
            timeoutException = FakeExcp

        try:
            if self.quiet:
                try:
                    kwargs['stderr'] = subprocess.STDOUT
                    subprocess.check_output(cmdline, **kwargs)
                    retcode = 0
                except subprocess.CalledProcessError as e:
                    retcode = e.returncode
            else:
                retcode = subprocess.call(cmdline, **kwargs)
        except timeoutException:
            return self.TLE

        if retcode != 0 and not self.ignoreRetcode:
            return self.RE
        else:
            return self.OK

    def runTest(self, test):
        print('')
        print('='*62)
        print('{} {:<56s} {}'.format('='*2, test.replace('testData/',''), '='*2))
        shutil.copy2(test, 'test.cnf')

        cmdline = self.solver.cmdline()
        cmdline.extend(['test.cnf', 'output.txt'])

        timeout = self.testTimeout(test)
        tStart = now()
        tEnd = tStart
        count = 0

        while tEnd < tStart + self.minTestTime:
            if os.path.exists('output.txt'):
                os.remove('output.txt')

            status = self.runCommand(cmdline, timeout)

            tEnd = now()
            count += 1

            if status is not self.OK:
                break

        if status is self.OK:
            status = self.checkOutput(test, 'output.txt')

        if status is self.OK:
            self.passed += 1

        avgTime = (tEnd - tStart) / count
        ts =  self.TestStat(test, status, self.statusStrings[status], avgTime, count)
        self.stats.append(ts)
        print('='*2, ' '*56, '='*2)
        print('== {2:18s} time:  {3:15.12f} repeated {4:4d}x =='.format(*ts))
        print('='*62)

    def test(self):
        if not self.solver.compile():
            print('Cannont compile solver!!!')
            return
        self.stats = []
        self.passed = 0
        for test in self.tests:
            self.runTest(test)

        print('\n\n\n')
        print('Passed %d of %d' % (self.passed, len(self.tests)))


if __name__ == "__main__":
    if sys.version_info < (3,3):
        print("WARNING:  python < 3.3 : timeouts / TLE won't work")
    t = SatTester(sys.argv)
    t.test()

# vim: set sw=4 ts=4 sts=4 et :
