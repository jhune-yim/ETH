#!/usr/bin/env python3
"""Finite checks accompanying
"From Exact Counting to Circuit Lower Bounds" (draft 7).

Twenty-three checks compare exact Python integers or fractions.Fraction
values. The final check (zero_error_bound) is a numerical sanity check of
the confidence-limit formula and uses floating point with tolerance 1e-12.
Random instances come from the random module with a fixed seed. These
checks detect transcription and sign errors in small instances. They do
not prove any universal statement and do not test the announced SAT
algorithm itself.

Run:  python3 finite_checks.py        (standard library only)
"""

from fractions import Fraction
from itertools import product, combinations
from math import comb
import random

random.seed(20261028)
RESULTS = []


def check(name, ok):
    RESULTS.append((name, bool(ok)))
    print(("PASS " if ok else "FAIL ") + name)


# ---------------------------------------------------------------- CNF utils
# A literal is (variable index, negated?). A clause is a tuple of literals.

def lit_val(lit, x):
    v, neg = lit
    return 1 - x[v] if neg else x[v]


def satisfies(cnf, x):
    return all(any(lit_val(l, x) for l in c) for c in cnf)


def count(cnf, n, fixed=None):
    fixed = fixed or {}
    total = 0
    for x in product((0, 1), repeat=n):
        if all(x[i] == b for i, b in fixed.items()) and satisfies(cnf, x):
            total += 1
    return total


def random_cnf(n, m, k):
    cnf = []
    for _ in range(m):
        vs = random.sample(range(n), random.randint(1, k))
        cnf.append(tuple((v, random.random() < 0.5) for v in vs))
    return cnf


# ------------------------------------------- 1. gate and cycle encodings

def gate_encoding_unique():
    ok = True
    for table in product((0, 1), repeat=4):          # all 16 binary gates
        g = lambda u, v: table[2 * u + v]
        # forbid every inconsistent triple (u, v, z) with z != g(u, v)
        cl = []
        for u, v in product((0, 1), repeat=2):
            z = 1 - g(u, v)
            cl.append(((0, u == 1), (1, v == 1), (2, z == 1)))
        for u, v in product((0, 1), repeat=2):
            ext = [z for z in (0, 1) if satisfies(cl, (u, v, z))]
            ok &= ext == [g(u, v)]
    return ok


def or_gate_three_clauses():
    cl = [((0, True), (2, False)), ((1, True), (2, False)),
          ((0, False), (1, False), (2, True))]
    return all([z for z in (0, 1) if satisfies(cl, (u, v, z))] == [u | v]
               for u, v in product((0, 1), repeat=2))


def implication_cycle():
    ok = True
    for s in range(2, 7):
        cl = [((i, True), ((i + 1) % s, False)) for i in range(s)]
        sols = [x for x in product((0, 1), repeat=s) if satisfies(cl, x)]
        ok &= sorted(sols) == [(0,) * s, (1,) * s]
    return ok


def clause_polynomial_example():
    # (x1 or not x2) and (x2 or x3)
    tot = 0
    for x1, x2, x3 in product((0, 1), repeat=3):
        tot += (1 - (1 - x1) * x2) * (1 - (1 - x2) * (1 - x3))
    return tot == 4


# --------------------------------------------- 2. graph encodings

def graph_encodings():
    ok = True
    for _ in range(25):
        v = random.randint(1, 6)
        edges = [e for e in combinations(range(v), 2) if random.random() < 0.45]
        # independent sets
        cnf = [((a, True), (b, True)) for a, b in edges]
        direct = sum(1 for S in product((0, 1), repeat=v)
                     if all(not (S[a] and S[b]) for a, b in edges))
        ok &= count(cnf, v) == direct
        # proper 3-colourings, variable x_{u,c} = 3u + c
        a = 3
        cnf = []
        for u in range(v):
            cnf.append(tuple((a * u + c, False) for c in range(a)))
            for c1, c2 in combinations(range(a), 2):
                cnf.append(((a * u + c1, True), (a * u + c2, True)))
        for (p, q) in edges:
            for c in range(a):
                cnf.append(((a * p + c, True), (a * q + c, True)))
        direct = sum(1 for col in product(range(a), repeat=v)
                     if all(col[p] != col[q] for p, q in edges))
        ok &= count(cnf, a * v) == direct
    return ok


# ------------------------------------- 3. self-reduction and sampling

def sampling_probabilities():
    # Check the probability identity directly; the call budget is proved in the text.
    ok = True
    for _ in range(20):
        n = 5
        cnf = random_cnf(n, random.randint(1, 8), 3)
        total = count(cnf, n)
        for x in product((0, 1), repeat=n):
            if not satisfies(cnf, x):
                continue
            prob, fixed = Fraction(1), {}
            for i in range(n):
                Z = count(cnf, n, fixed)
                fixed[i] = x[i]
                Zb = count(cnf, n, fixed)
                prob *= Fraction(Zb, Z)
            ok &= prob == Fraction(1, total)
    return ok


def canonical_witness_prefix_search():
    ok = True
    for _ in range(30):
        n = 6
        cnf = random_cnf(n, random.randint(1, 12), 3)
        sols = [x for x in product((0, 1), repeat=n) if satisfies(cnf, x)]
        if not sols:
            continue
        fixed = {}
        for i in range(n):
            fixed[i] = 0
            if count(cnf, n, fixed) == 0:
                fixed[i] = 1
        ok &= tuple(fixed[i] for i in range(n)) == min(sols)
    return ok


# ----------------------------------------------- 4. fiber factorization

def fiber_factorization():
    ok = True
    for _ in range(10):
        sizes = [2, 2, 3]
        n = sum(sizes)
        groups, start = [], 0
        for s in sizes:
            groups.append(list(range(start, start + s)))
            start += s
        Cs = [[[random.randint(-1, 1) for _ in g] for _ in range(1)] for g in groups]
        table = {}

        def A(gi, u, y):
            key = (gi, u, y)
            if key not in table:
                table[key] = Fraction(random.randint(-3, 3), random.randint(1, 3))
            return table[key]

        def meas(gi, u):
            return tuple(sum(c * b for c, b in zip(row, u)) for row in Cs[gi])

        lhs = Fraction(0)
        for x in product((0, 1), repeat=n):
            parts = [tuple(x[i] for i in g) for g in groups]
            y = tuple(meas(gi, parts[gi]) for gi in range(len(groups)))
            term = Fraction(1)
            for gi in range(len(groups)):
                term *= A(gi, parts[gi], y)
            lhs += term
        ranges = [sorted({meas(gi, u) for u in product((0, 1), repeat=len(g))})
                  for gi, g in enumerate(groups)]
        rhs = Fraction(0)
        for y in product(*ranges):
            term = Fraction(1)
            for gi, g in enumerate(groups):
                term *= sum((A(gi, u, y) for u in product((0, 1), repeat=len(g))
                             if meas(gi, u) == y[gi]), Fraction(0))
            rhs += term
        ok &= lhs == rhs
    return ok


# ---------------------------------------- 5. truncated polynomials in z

def pmul(a, b, q):
    out = [Fraction(0)] * (q + 1)
    for i, ai in enumerate(a):
        if ai == 0:
            continue
        for j, bj in enumerate(b):
            if i + j <= q:
                out[i + j] += ai * bj
    return out


def padd(a, b):
    return [x + y for x, y in zip(a, b)]


def pscale(a, c):
    return [c * x for x in a]


def taylor_recovery():
    """Lemma (Taylor recovery by inclusion-exclusion) on random instances."""
    ok = True
    for _ in range(12):
        n, q = 4, random.randint(1, 3)
        clauses = []
        for _ in range(random.randint(1, 3)):
            occ = []
            for _ in range(random.randint(1, 3)):
                base = [Fraction(random.randint(-2, 2), random.randint(1, 2)) for _ in range(n)]
                shift = [[Fraction(random.randint(-2, 2)) for _ in range(n)]
                         for _ in range(q)]                 # coefficients of z^1..z^q
                occ.append((base, shift))
            clauses.append(occ)

        def G(x, X):
            res = [Fraction(1)] + [Fraction(0)] * q
            for occ in clauses:
                prod_ = [Fraction(1)] + [Fraction(0)] * q
                for base, shift in occ:
                    y = [sum(b * xi for b, xi in zip(base, x))] + \
                        [sum(s * Xi for s, Xi in zip(shift[i], X)) for i in range(q)]
                    one_minus = [1 - y[0]] + [-c for c in y[1:]]
                    prod_ = pmul(prod_, one_minus, q)
                phi = [1 - prod_[0]] + [-c for c in prod_[1:]]
                res = pmul(res, phi, q)
            return res

        lhs = [Fraction(0)] * (q + 1)
        for x in product((0, 1), repeat=n):
            lhs = padd(lhs, G(x, x))
        rhs = [Fraction(0)] * (q + 1)
        for size in range(q + 1):
            for E in combinations(range(n), size):
                for usize in range(size + 1):
                    for U in combinations(E, usize):
                        ind = [1 if i in U else 0 for i in range(n)]
                        sign = (-1) ** (size - usize)
                        for x in product((0, 1), repeat=n):
                            if all(x[i] == 1 for i in E):
                                rhs = padd(rhs, pscale(G(x, ind), sign))
        ok &= lhs == rhs
    return ok


# --------------------------------------------- 6. exact linear algebra

def rank(rows):
    M = [list(r) for r in rows]
    rk, col = 0, 0
    ncols = len(M[0]) if M else 0
    while rk < len(M) and col < ncols:
        piv = next((i for i in range(rk, len(M)) if M[i][col] != 0), None)
        if piv is None:
            col += 1
            continue
        M[rk], M[piv] = M[piv], M[rk]
        for i in range(len(M)):
            if i != rk and M[i][col] != 0:
                f = M[i][col] / M[rk][col]
                M[i] = [a - f * b for a, b in zip(M[i], M[rk])]
        rk += 1
        col += 1
    return rk


def solve_least(rows, rhs):
    """Solve an overdetermined consistent system exactly; return solution or None."""
    M = [list(r) + [b] for r, b in zip(rows, rhs)]
    ncols = len(rows[0])
    rk, col, pivcols = 0, 0, []
    while rk < len(M) and col < ncols:
        piv = next((i for i in range(rk, len(M)) if M[i][col] != 0), None)
        if piv is None:
            col += 1
            continue
        M[rk], M[piv] = M[piv], M[rk]
        p = M[rk][col]
        M[rk] = [a / p for a in M[rk]]
        for i in range(len(M)):
            if i != rk and M[i][col] != 0:
                f = M[i][col]
                M[i] = [a - f * b for a, b in zip(M[i], M[rk])]
        pivcols.append(col)
        rk += 1
        col += 1
    if rk < ncols or any(all(a == 0 for a in r[:-1]) and r[-1] != 0 for r in M):
        return None
    sol = [Fraction(0)] * ncols
    for i, c in enumerate(pivcols):
        sol[c] = M[i][-1]
    return sol


def hermite_recovery():
    ok = True
    for _ in range(15):
        d = random.randint(1, 9)
        Q = random.randint(1, 4)
        J = d // Q + 1                                      # QJ > d
        H = [Fraction(random.randint(-5, 5), random.randint(1, 4)) for _ in range(d + 1)]
        rows, rhs = [], []
        for t in range(1, Q + 1):
            for i in range(J):
                rows.append([Fraction(comb(k, i)) * t ** (k - i) if k >= i else Fraction(0)
                             for k in range(d + 1)])
                rhs.append(sum(H[k] * comb(k, i) * t ** (k - i) for k in range(i, d + 1)))
        ok &= solve_least(rows, rhs) == H
    return ok


def precision_counterexample():
    # 2T and 2 agree at T = 1, 3 modulo 4 but differ at T = 0.
    H1 = lambda T: 2 * T
    H2 = lambda T: 2
    return all((H1(t) - H2(t)) % 4 == 0 for t in (1, 3)) and (H1(0) - H2(0)) % 4 != 0


# ------------------------------------------- 7. the matrix construction

def matmul(A, B):
    n, m, p = len(A), len(B), len(B[0])
    Bt = list(zip(*B))
    return [[sum((A[i][k] * Bt[j][k] for k in range(m) if A[i][k] != 0), Fraction(0))
             for j in range(p)] for i in range(n)]


def identity(D):
    return [[Fraction(int(i == j)) for j in range(D)] for i in range(D)]


def lagrange_coeffs(nodes, values):
    """Coefficients (low to high) of the interpolating polynomial."""
    coeffs = [Fraction(0)] * len(nodes)
    for i, (xi, yi) in enumerate(zip(nodes, values)):
        basis = [Fraction(1)]
        denom = Fraction(1)
        for j, xj in enumerate(nodes):
            if j == i:
                continue
            basis = [Fraction(0)] + basis
            for k in range(len(basis) - 1):
                basis[k] -= xj * basis[k + 1]
            denom *= (xi - xj)
        for k, c in enumerate(basis):
            coeffs[k] += yi * c / denom
    return coeffs


def matrix_construction(r, Q, I0):
    R = len(I0)
    labels = list(product(range(r), repeat=Q))
    B = [(a, d) for a in labels for d in labels]
    idx = {u: i for i, u in enumerate(B)}
    D = len(B)

    def swap(u, s):
        a, d = list(u[0]), list(u[1])
        a[s], d[s] = d[s], a[s]
        return (tuple(a), tuple(d))

    Pis = []
    for s in range(Q):
        P = [[Fraction(0)] * D for _ in range(D)]
        for y in B:
            P[idx[swap(y, s)]][idx[y]] = Fraction(1)
        Pis.append(P)
    I = identity(D)
    V0 = I
    for P in Pis:
        V0 = matmul(V0, P)
    W0 = [[sum((I[i][j] - P[i][j] for P in Pis), Fraction(0)) / 2 for j in range(D)]
          for i in range(D)]
    f = lagrange_coeffs([Fraction(j) for j in I0], [Fraction((-1) ** j) for j in I0])
    fW = [[Fraction(0)] * D for _ in range(D)]
    power = I
    for c in f:
        fW = [[fW[i][j] + c * power[i][j] for j in range(D)] for i in range(D)]
        power = matmul(power, W0)
    M0 = matmul(V0, fW)

    # tensor eigenbasis
    one_pos = []
    for a in range(r):
        one_pos.append(({(a, a): 1}, 0))
    for a, b in combinations(range(r), 2):
        one_pos.append(({(a, b): 1, (b, a): 1}, 0))
        one_pos.append(({(a, b): 1, (b, a): -1}, 1))
    basis = []
    for choice in product(one_pos, repeat=Q):
        vec = [Fraction(0)] * D
        for u in B:
            val = 1
            for s in range(Q):
                val *= choice[s][0].get((u[0][s], u[1][s]), 0)
                if val == 0:
                    break
            vec[idx[u]] = Fraction(val)
        basis.append((vec, sum(c[1] for c in choice)))

    ok = len(basis) == D
    # entries in {0, +1, -1} and l1 norm at most 2^Q
    ok &= all(x in (0, 1, -1) for v, _ in basis for x in v)
    ok &= all(sum(abs(x) for x in v) <= 2 ** Q for v, _ in basis)
    # eigenvalues
    for v, j in basis:
        Mv = [sum((M0[i][k] * v[k] for k in range(D) if v[k] != 0), Fraction(0))
              for i in range(D)]
        fj = sum(c * Fraction(j) ** k for k, c in enumerate(f))
        ok &= Mv == [(-1) ** j * fj * x for x in v]
    CB = [v for v, j in basis if j not in I0]
    # exceptional fraction equals the binomial tail
    pneg = Fraction(r - 1, 2 * r)
    tail = sum(comb(Q, j) * pneg ** j * (1 - pneg) ** (Q - j)
               for j in range(Q + 1) if j not in I0)
    ok &= Fraction(len(CB), D) == tail
    # rank(I - M0) <= rows(C^B)
    IminusM = [[I[i][j] - M0[i][j] for j in range(D)] for i in range(D)]
    rCB = rank(CB) if CB else 0
    ok &= rank(IminusM) <= len(CB) and rCB == len(CB)
    # locality: nonzero M0[u,y] => #{s : a_y(s) != d_u(s)} <= R-1
    for u in B:
        for y in B:
            if M0[idx[u]][idx[y]] != 0:
                mism = sum(1 for s in range(Q) if y[0][s] != u[1][s])
                ok &= mism <= R - 1
    # replacement forms: P_u(0) = delta_u; at t in 1..Q the surviving terms
    # lie in group d_u(t), and delta_u (I - M0) lies in the row space of C^B
    for u in B:
        iu = idx[u]
        row = IminusM[iu]
        if CB:
            ok &= rank(CB + [row]) == rCB
        else:
            ok &= all(x == 0 for x in row)
        for t in range(0, Q + 1):
            Pt = list(row)
            for y in B:
                m = M0[iu][idx[y]]
                if m == 0:
                    continue
                E = [s for s in range(Q) if y[0][s] != u[1][s]]
                phi = Fraction(1)
                for s in E:
                    phi *= 1 - Fraction(t, s + 1)
                if t >= 1 and y[0][t - 1] != u[1][t - 1]:
                    ok &= phi == 0
                Pt[idx[y]] += m * phi
            if t == 0:
                ok &= Pt == I[iu]
    return ok


# ----------------------------- 8. integral parity indicator and truncation

def poly_mul_int(a, b):
    out = [0] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            out[i + j] += x * y
    return out


def parity_poly(p):
    one_minus_pow = [1]
    for _ in range(p):
        one_minus_pow = poly_mul_int(one_minus_pow, [1, -1])
    trunc = [comb(p + j - 1, j) for j in range(p)]
    return poly_mul_int(one_minus_pow, trunc)


def ev(poly, y):
    return sum(c * y ** k for k, c in enumerate(poly))


def h_expansion(P):
    """Write P = sum_j e_j(Y) h(Y)^j with h = Y^2 - Y, deg e_j <= 1."""
    P = list(P)
    es = []
    while any(P):
        # divide by monic h = Y^2 - Y
        qcoef = [0] * max(len(P) - 2, 1)
        rem = list(P)
        for k in range(len(rem) - 1, 1, -1):
            c = rem[k]
            if c:
                qcoef[k - 2] += c
                rem[k] -= c
                rem[k - 1] += c          # subtract c*Y^{k-2}*(Y^2 - Y)
        es.append((rem[0], rem[1] if len(rem) > 1 else 0))
        P = qcoef if len(P) > 2 else [0]
    return es


def parity_lemma():
    ok = True
    for p in range(1, 10):
        P = parity_poly(p)
        while len(P) > 1 and P[-1] == 0:
            P.pop()
        ok &= len(P) - 1 < 2 * p
        ok &= all(ev(P, y) % 2 ** p == (1 if y % 2 == 0 else 0) for y in range(-60, 61))
        es = h_expansion(P)
        ok &= len(es) <= p
        recon = [0]
        hpow = [1]
        for e0, e1 in es:
            term = poly_mul_int([e0, e1], hpow)
            recon = [a + b for a, b in
                     zip(recon + [0] * (len(term) - len(recon)), term + [0] * (len(recon) - len(term)))]
            hpow = poly_mul_int(hpow, [0, -1, 1])
        while len(recon) > 1 and recon[-1] == 0:
            recon.pop()
        ok &= recon == P
    return ok


def global_truncation():
    ok = True
    for p in range(1, 8):
        es = h_expansion(parity_poly(p))
        es += [(0, 0)] * (p - len(es))
        for _ in range(60):
            a = random.randint(1, 4)
            ls = [random.randint(-30, 30) for _ in range(a)]
            prod_ = [1] + [0] * (p - 1)
            for l in ls:
                h = l * (l - 1)
                Bi = [(e0 + e1 * l) * h ** j for j, (e0, e1) in enumerate(es[:p])]
                new = [0] * p
                for i, x in enumerate(prod_):
                    for j, y in enumerate(Bi):
                        if i + j < p:
                            new[i + j] += x * y
                prod_ = new
            target = 1
            for l in ls:
                target *= 1 if l % 2 == 0 else 0
            ok &= sum(prod_) % 2 ** p == target
    return ok


# ------------------------------------------- 9. circuit-argument pieces

def support_recovery():
    ok = True
    for _ in range(40):
        qbits, w = 8, 3
        S = random.sample(range(qbits), random.randint(0, w))
        tt = {bits: random.randint(0, 1) for bits in product((0, 1), repeat=len(S))}
        f = lambda x: tt[tuple(x[i] for i in S)]
        relevant = {i for i in range(qbits)
                    if any(f(x) != f(tuple(b ^ (j == i) for j, b in enumerate(x)))
                           for x in product((0, 1), repeat=qbits))}
        low = [x for x in product((0, 1), repeat=qbits) if sum(x) <= w]
        lowset = set(low)
        found = set()
        for x in low:
            for i in range(qbits):
                y = tuple(b ^ (j == i) for j, b in enumerate(x))
                if y in lowset and f(x) != f(y):
                    found.add(i)
        ok &= found == relevant
    return ok


def random_circuit(qin, t):
    gates = []
    for g in range(t):
        nodes = qin + g
        a, b = random.randrange(nodes), random.randrange(nodes)
        table = tuple(random.randint(0, 1) for _ in range(4))
        gates.append((a, b, table))
    return gates


def eval_circuit(gates, qin, x):
    vals = list(x)
    for a, b, table in gates:
        vals.append(table[2 * vals[a] + vals[b]])
    return vals


def circuit_encoding():
    ok = True
    for _ in range(30):
        qin, t = random.randint(1, 5), random.randint(1, 8)
        gates = random_circuit(qin, t)
        cnf = []
        for g, (a, b, table) in enumerate(gates):
            z = qin + g
            for u, v in product((0, 1), repeat=2):
                bad = 1 - table[2 * u + v]
                cnf.append(((a, u == 1), (b, v == 1), (z, bad == 1)))
        cnf.append(((qin + t - 1, False),))
        ok &= len(cnf) <= 4 * t + 1 <= 5 * (qin + t)
        accepted = sum(eval_circuit(gates, qin, x)[-1]
                       for x in product((0, 1), repeat=qin))
        ok &= count(cnf, qin + t) == accepted
    return ok


def violation_circuit():
    ok = True
    for _ in range(200):
        N, qaddr = 3, 4
        nvars = 2 ** N
        decoder = [tuple((random.randrange(nvars), random.random() < 0.5) for _ in range(3))
                   for _ in range(2 ** qaddr)]
        C = [random.randint(0, 1) for _ in range(nvars)]   # guessed truth table
        all_sat = all(any(C[lab] ^ sig for lab, sig in cl) for cl in decoder)
        B = lambda z: all(not (C[lab] ^ sig) for lab, sig in decoder[z])
        ok &= all_sat == (not any(B(z) for z in range(2 ** qaddr)))
    return ok


# ------------------------------------------------- 10. Section 8.3 checks

def ham_cycles(v, edges):
    """Number of undirected Hamiltonian cycles (v >= 3)."""
    E = {frozenset(e) for e in edges}
    from itertools import permutations
    directed = 0
    for perm in permutations(range(1, v)):
        cyc = (0,) + perm
        if all(frozenset((cyc[i], cyc[(i + 1) % v])) in E for i in range(v)):
            directed += 1
    return directed // 2          # each undirected cycle has two directions


def ham_position_encoding():
    """x_{u,i}: vertex u at position i. Each cycle gives 2v assignments."""
    ok = True
    for _ in range(12):
        v = random.randint(3, 5)
        edges = [e for e in combinations(range(v), 2) if random.random() < 0.7]
        E = {frozenset(e) for e in edges}
        var = lambda u, i: u * v + i
        cnf = []
        for u in range(v):                        # each vertex at some position
            cnf.append(tuple((var(u, i), False) for i in range(v)))
            for i, j in combinations(range(v), 2):
                cnf.append(((var(u, i), True), (var(u, j), True)))
        for i in range(v):                        # each position holds one vertex
            cnf.append(tuple((var(u, i), False) for u in range(v)))
            for u, w in combinations(range(v), 2):
                cnf.append(((var(u, i), True), (var(w, i), True)))
        for i in range(v):                        # consecutive positions adjacent
            for u in range(v):
                for w in range(v):
                    if u != w and frozenset((u, w)) not in E:
                        cnf.append(((var(u, i), True), (var(w, (i + 1) % v), True)))
        ok &= count(cnf, v * v) == 2 * v * ham_cycles(v, edges)
    return ok


def complete_graph_cycle_count():
    from math import factorial
    ok = True
    for v in range(3, 8):
        ok &= ham_cycles(v, list(combinations(range(v), 2))) == factorial(v - 1) // 2
    return ok


def zero_error_bound():
    ok = True
    for M in (1, 10, 100):
        for alpha in (Fraction(1, 20), Fraction(1, 100)):
            piU = 1 - float(alpha) ** (1 / M)
            ok &= abs((1 - piU) ** M - float(alpha)) < 1e-12
    return ok


if __name__ == "__main__":
    check("OR gate: three clauses force z = u or v", or_gate_three_clauses())
    check("all 16 binary gates: unique extension", gate_encoding_unique())
    check("implication cycles force equal copies", implication_cycle())
    check("clause-polynomial example has count 4", clause_polynomial_example())
    check("independent-set and 3-colouring encodings are parsimonious", graph_encodings())
    check("exact sampler gives probability 1/#F", sampling_probabilities())
    check("prefix search returns lexicographically first witness", canonical_witness_prefix_search())
    check("fiber factorization identity", fiber_factorization())
    check("Taylor recovery by inclusion-exclusion", taylor_recovery())
    check("Hermite recovery with QJ > d", hermite_recovery())
    check("precision counterexample modulo 4", precision_counterexample())
    for r, Q, I0 in [(2, 2, [0, 1]), (2, 2, [1]), (2, 3, [1, 2]), (3, 2, [0, 1]), (3, 2, [1])]:
        check(f"matrix construction r={r}, Q={Q}, I0={I0} (dim {r ** (2 * Q)})",
              matrix_construction(r, Q, I0))
    check("integral parity polynomial and h-expansion", parity_lemma())
    check("global truncation congruence", global_truncation())
    check("support recovery from low-weight inputs", support_recovery())
    check("circuit-to-3CNF encoding with clause budget", circuit_encoding())
    check("violation circuit unsatisfiable iff all clauses hold", violation_circuit())
    check("Hamiltonian position encoding: 2v assignments per cycle", ham_position_encoding())
    check("K_v has (v-1)!/2 Hamiltonian cycles", complete_graph_cycle_count())
    check("zero-error one-sided bound (numeric sanity only)", zero_error_bound())
    failed = [n for n, ok in RESULTS if not ok]
    print(f"\n{len(RESULTS) - len(failed)}/{len(RESULTS)} checks passed")
    raise SystemExit(1 if failed else 0)
