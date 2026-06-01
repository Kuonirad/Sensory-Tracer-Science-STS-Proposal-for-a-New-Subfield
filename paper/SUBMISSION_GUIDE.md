# arXiv Submission Guide — Sensory Tracer Science (STS)

This folder contains a **submission-ready manuscript** for arXiv. It is *not*
auto-submitted: arXiv requires a logged-in human submitter (and, for a first
submission in a category, an endorsement). The steps below take ~10–15 minutes.

> **Important framing:** This paper is written as a **theoretical / in-silico
> framework proposal**. It makes **no wet-lab or clinical validation claims**.
> Keep it that way unless you add real experimental data — overclaiming is the
> fastest route to a desk-reject or a moderation hold on arXiv.

---

## 0. Files

| File | Purpose |
|------|---------|
| `main.tex` | The manuscript source (compiles with pdflatex + bibtex). |
| `references.bib` | Bibliography (copied from `docs/references.bib`). |
| `Makefile` | `make` builds the PDF; `make arxiv` builds the upload tarball. |

## 1. Before you submit — edit these

In `main.tex`:
- **`\author{...}` block** — replace with your real name(s).
- **`\thanks{...}`** — affiliation, email, and **ORCID** (register free at
  <https://orcid.org> if you don't have one).
- Re-read the **Abstract** and **Limitations** so you stand behind every claim.

## 2. Build the PDF locally (optional but recommended)

No LaTeX toolchain was available in the environment that generated this, so the
PDF has **not** been compiled here. To compile:

```bash
cd paper
make            # -> main.pdf   (needs a TeX distribution: TeX Live / MiKTeX)
# or manually:
pdflatex main && bibtex main && pdflatex main && pdflatex main
```

No local TeX? Upload `main.tex` + `references.bib` to **Overleaf** and it compiles
in-browser. arXiv also compiles the source itself, so a local build is only to
preview.

## 3. Pick the arXiv category

STS spans biophysics, information thermodynamics, and ML interpretability.
Recommended primary + cross-list:

- **Primary:** `q-bio.NC` (Neurons and Cognition) — fits the neural-tracer core,
  **or** `physics.bio-ph` (Biological Physics).
- **Cross-list:** `cs.LG` or `cs.AI` (for the reasoning-stack attribution bridge),
  and optionally `cond-mat.stat-mech` (information thermodynamics).

If unsure, `physics.bio-ph` (primary) + `cs.LG` (cross) is a defensible pairing.

## 4. Endorsement (first-time submitters only)

If you have never submitted to the chosen category, arXiv will ask for an
**endorsement** from an established author in that category. Plan for this —
it can take a few days. See <https://arxiv.org/help/endorsement>.

## 5. Submit

1. Create/log in at <https://arxiv.org>.
2. **Start New Submission** → upload the **source tarball** (preferred over PDF):
   ```bash
   make arxiv     # produces arxiv-submission.tar.gz with main.tex + references.bib
   ```
   Upload `arxiv-submission.tar.gz`. arXiv compiles it server-side.
3. Fill in **title**, **authors**, **abstract** (paste from the paper), category,
   and comments (e.g. "Reference implementation: <repo URL>").
4. Add the **MSC/ACM class** and a **DOI/code link** if you mint a Zenodo DOI
   (recommended — see below).
5. Preview the arXiv-generated PDF, then **submit**. There is a moderation/hold
   step; postings go live on the next announcement cycle.

## 6. Recommended companions (optional)

- **Zenodo DOI for the code.** Connect the GitHub repo to Zenodo and cut a
  release → you get a citable DOI. Put it in the README badge (currently a
  placeholder) and in the paper's "Code and Data Availability".
- **Journal route.** arXiv is a preprint server, not a journal. Suitable venues
  for the framework once it has empirical backing include *PLOS Computational
  Biology*, *Physical Review X / PRX Life*, *Journal of Neural Engineering*, or
  *Entropy* (MDPI, information-thermodynamics angle). Most are arXiv-friendly.

## 7. What this repo cannot do for you

- It cannot create an arXiv account, obtain endorsement, or click "submit" —
  those are account-bound human actions.
- It cannot assert experimental validation that hasn't happened.

Everything else — a clean, compilable, accurately-scoped manuscript — is ready.
