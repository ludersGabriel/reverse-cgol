# CGOL reverse min solver

This script computes the previous step of an CGOL instance of any size, giving
the least amount of live cells that could have generated that state.
It uses LLS by OscarCunningham to build the clauses for a SAT solver, the
SAT solver used is Kissat.

Input example:
```txt
7 8
0 0 0 0 0 0 0 0
0 1 1 1 1 0 1 0
0 0 0 1 0 0 1 0
0 1 1 1 1 1 1 0
0 0 1 0 0 0 1 0
0 1 1 1 1 0 1 0
0 0 0 0 0 0 0 0
```