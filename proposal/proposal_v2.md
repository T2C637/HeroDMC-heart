# DS8001 Project Proposal: Permutation-Based Approximate kNN Search for Mixed-Type Hospital Encounters

Jared Smouter and Amarnadh Nalla | Project path: **Empirical Analysis** | Group of two

(Source text of the one-page PDF built by `build_proposal.py`.)

## 1. Problem and questions

Exact k-nearest-neighbor (kNN) search computes a distance to all N indexed encounters. We study, as a purely algorithmic question (no clinical claim), how permutation-based approximate indexes trade recall against distance computations, index size and build cost under a mixed-type distance. The dataset is widely used for readmission prediction; our contribution is an algorithmic study of approximate similarity search on it.

- **RQ1.** How do the number of pivots n, the retained permutation length L and the re-ranking budget c affect recall@10 and query cost, and how do these costs scale with N?
- **RQ2.** At matched L and c, when does a truncated MI-File beat a truncated permutation scan, and how does random versus farthest-first pivot selection change this?

## 2. Methods

Implemented by us:

1. **Brute-force exact kNN** (ground truth, ties broken by encounter id).
2. **Truncated permutation scan (TPS):** each object stores the ranks of its L nearest pivots (rank L+1 otherwise); the query scores all objects by the Spearman footrule over the n pivots, keeps the best c and re-ranks them with the true distance (exact only within the candidate set).
3. **Truncated MI-File** (Amato and Savino, 2008): per-pivot posting lists of (object, rank), same score and re-ranking, so only objects sharing a retained pivot are touched.
4. Random versus farthest-first pivot selection.

Library baseline (not counted as ours): scikit-learn **BallTree**, Manhattan metric, on an exact weighted-L1 encoding of the distance, validated against brute force.

Complexity: build O(Nn) distances plus ranking; storage O(NL); query n pivot distances plus candidate scoring plus c re-ranking distances.

**Distance:** six equal-weight feature groups (age, utilization, admission/discharge, ICD-9 diagnosis chapters, labs, medications); numeric = scale-normalized absolute difference, nominal = 0/1 mismatch, missing = fixed state or median plus indicator (no pairwise omission). With fixed scales and weights this is a metric, verified (identity, triangle inequality) on sampled triples.

## 3. Data

Diabetes 130-US Hospitals (1999-2008; Strack et al., 2014; UCI, CC BY 4.0): 101,766 encounters, 71,518 patients. Excluded: IDs, `readmitted`, race, gender, `weight`. Patients are split 90/5/5 into index/validation/test with a fixed seed; scales and medians are fit on the index partition only.

## 4. Experiments and metrics

- Nested N = 10k, 50k, full index partition; 300 validation and 300 test queries (one encounter per patient).
- Grid: n in {32, 64}, L in {8, 16, 32} (L <= n), c/N in {0.5%, 1%, 5%}, random and farthest-first pivots, 3 seeds.
- Pareto-optimal settings chosen on validation, frozen, evaluated on test once.
- Metrics: recall@10; distance computations, entries scored, postings read per query; index size; build distances; median latency and peak memory (single-threaded).
- Patient-level bootstrap 95% CIs, paired per-query differences, seed variability reported separately from query variability.

Work split: J. Smouter - preprocessing, metric, brute force, BallTree; A. Nalla - TPS, MI-File, pivots; experiments, statistics and report are joint.

## References

- Amato, G., and Savino, P. (2008). Approximate similarity search in metric spaces using inverted files. *Proc. 3rd InfoScale*.
- Mohamed, H., and Marchand-Maillet, S. (2015). Scalable indexing for big data processing. In *Big Data: Algorithms, Analytics, and Applications*. Chapman and Hall/CRC.
- Strack, B., et al. (2014). Impact of HbA1c measurement on hospital readmission rates. *BioMed Research International*, 2014, 781670. Data: UCI ML Repository, doi:10.24432/C5230J.
