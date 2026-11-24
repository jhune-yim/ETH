# Release record: draft 7

Manuscript: *From Exact Counting to Circuit Lower Bounds: A Reconstruction of the Announced Refutation of ETH and Its Verification Obligations*.

Release date: 30 October 2026. This is the draft 7 author version.

## Publication files

- `ETH.tex`: self-contained `amsart` source, with the bibliography and TikZ figures embedded. No separate bibliography or image files are required.
- `finite_checks.py`: finite-check suite using only the Python standard library.
- `Release_record.md`: this release record, including the execution identity and full check output.

Filename capitalization is intentional. Keep these three files together.

## File identity

SHA-256 hashes of the frozen manuscript and script:

```text
8f92e24939832217fa307f013a2945728192aaa3a3873ec38371e74d304fbdba  ETH.tex
62051ecb3dda8ecf4f495d76be548869caead8f5bda501c48d3b212c7bf0ce11  finite_checks.py
```

To verify these hashes on macOS:

```sh
shasum -a 256 ETH.tex finite_checks.py
```

## Changes from draft 6

- Handled the greedy-elimination lemma's endpoint `alpha = 1` separately.
- Specified the one-occurrence and two-occurrence tensor cases, the unique-extension property, and the imported tensor theorem's uniformity and vertex-count conditions.
- Corrected the parity proof to use at most `p` powers and made its uniqueness argument explicit.
- Restricted the `3.1N - o(N)` comparison to polynomial-time computable functions and framed the historical circuit lower-bound barrier relative to the announcement.
- Clarified the post-splitting variable count and the positive-parameter assumptions in the illustrative minimization.
- Distinguished the sampling probability check from the analytical oracle-call bound; removed the unused counter from the script without changing the pass criteria.
- Synchronized all publication filenames, advanced the manuscript metadata to draft 7, and put the bibliography entries in alphabetical order.

Draft 6 and its original release record are retained separately as historical files.

## Reproduction

Build the manuscript with a LaTeX installation providing `amsart`, the AMS mathematics packages, TikZ, and the other packages declared in the preamble:

```sh
latexmk -pdf -interaction=nonstopmode -halt-on-error ETH.tex
```

Run the finite checks:

```sh
python3 finite_checks.py
```

The reviewed local build produced 26 pages with no LaTeX warnings, overfull or underfull boxes, missing characters, or unresolved references or citations. All 98 source labels are unique, all 27 bibliography entries are cited, and all PDF fonts are embedded. All pages were inspected in contact sheets; changed passages on pages 3, 19, and 20 were also inspected at full-page size.

## Recorded finite-check execution

- Started: `2026-10-30T05:34:06.486068+09:00`
- Completed: `2026-10-30T05:35:30.209945+09:00`
- Script: `finite_checks.py`
- Script SHA-256: `62051ecb3dda8ecf4f495d76be548869caead8f5bda501c48d3b212c7bf0ce11`
- Python: `3.12.11 (main, Jun  8 2026, 06:58:11) [Clang 17.0.0 (clang-1700.0.13.5)]`
- Platform: `macOS-15.6.1-arm64-arm-64bit`
- Seed: `20261028` (set at import)
- Command: `python3 finite_checks.py`
- Exit status: `0`
- Elapsed wall time: `83.722` seconds (a record of this run, not a performance claim)
- Standard error: empty
- Checks passed: `24/24`

Twenty-three checks compare exact integers or rational numbers. The final confidence-limit check uses floating point with tolerance `1e-12`. Random instances use Python's `random` module; their sequences may differ between Python versions, although the pass criteria are unchanged.

These checks cover finite examples of the interfaces described in the manuscript. They do not prove universal claims, execute the announced SAT algorithm, audit its full implementation, or rebuild its Lean development. The manuscript identifies the imported results and the conditional status of its reconstruction.

## Full output

```text
PASS OR gate: three clauses force z = u or v
PASS all 16 binary gates: unique extension
PASS implication cycles force equal copies
PASS clause-polynomial example has count 4
PASS independent-set and 3-colouring encodings are parsimonious
PASS exact sampler gives probability 1/#F
PASS prefix search returns lexicographically first witness
PASS fiber factorization identity
PASS Taylor recovery by inclusion-exclusion
PASS Hermite recovery with QJ > d
PASS precision counterexample modulo 4
PASS matrix construction r=2, Q=2, I0=[0, 1] (dim 16)
PASS matrix construction r=2, Q=2, I0=[1] (dim 16)
PASS matrix construction r=2, Q=3, I0=[1, 2] (dim 64)
PASS matrix construction r=3, Q=2, I0=[0, 1] (dim 81)
PASS matrix construction r=3, Q=2, I0=[1] (dim 81)
PASS integral parity polynomial and h-expansion
PASS global truncation congruence
PASS support recovery from low-weight inputs
PASS circuit-to-3CNF encoding with clause budget
PASS violation circuit unsatisfiable iff all clauses hold
PASS Hamiltonian position encoding: 2v assignments per cycle
PASS K_v has (v-1)!/2 Hamiltonian cycles
PASS zero-error one-sided bound (numeric sanity only)

24/24 checks passed
```
