# DS8001 Project Proposal: Permutation-Based Approximate kNN Search for Mixed-Type Hospital Encounters

Jared Smouter and Amarnadh Nalla | Project path: **Empirical Analysis** | Group of two

(Source text of the one-page PDF built by `build_proposal.py`.)

## 1. Problem and question

Exact k-nearest-neighbor (kNN) search computes a distance to all N indexed objects. We study, as a purely algorithmic question (no clinical claim), how permutation-based approximate indexes trade recall for fewer distance computations under a mixed-type distance.

**Principal question:** at matched recall@10, does the truncated MI-File (Amato and Savino, 2008) need fewer distance computations per query than the truncated permutation scan (TPS; Chávez et al., 2008), and how does this change with N?
**Secondary:** how do the pivot count n, permutation length L and re-ranking budget c affect recall@10 and cost?

## 2. Methods and scope

**Essential (implemented by us):**
1. Brute-force exact kNN (ground truth; ties by encounter id).
2. TPS: each object stores the ranks of its L nearest pivots (rank L+1 otherwise); a query scores all objects by Spearman footrule over the n pivots, keeps the best c and re-ranks them with the true distance.
3. MI-File: per-pivot posting lists of (object, rank) with the same score and re-ranking, touching only objects that share a retained pivot.
4. Random pivots.

**Optional extensions (only if time permits):** farthest-first pivots; scikit-learn BallTree as a library baseline (not counted as our implementation); extra grid values.

Complexity: build O(Nn) distances, storage O(NL), query n pivot distances plus c re-ranking distances.

**Distance.** Six feature groups (age, utilization, admission/discharge, ICD-9 diagnosis chapters, labs, medications) with equal weight 1/6:

d(x,y) = (1/6) Σ_g (1/|g|) Σ_{f∈g} d_f(x_f, y_f) ∈ [0,1],

so each group is normalized by its feature count. Numeric/ordinal: d_f = |x_f − y_f| / (max_f − min_f), range fit on the index and queries clipped to it. Nominal: d_f = 1[x_f ≠ y_f]. **Missing values** are never omitted pairwise: diagnoses, specialty, payer and labs get an explicit UNKNOWN/NOT_MEASURED category (two unknowns match; unknown vs. known mismatches); numerics use the index median. This is a weighted L1 metric, checked on sampled triples.

## 3. Data

**Diabetes 130-US Hospitals (1999–2008)** (Strack et al., 2014; UCI): 101,766 encounters, 71,518 patients. We exclude IDs, `readmitted`, race, gender and `weight`. Patients are split 90/5/5 into index/validation/test (fixed seed), so no patient is in both index and queries; scales and medians are fit on the index only.

## 4. Experiments, definitions and decision rules (fixed before running)

Nested N = 10k, 50k, full index; 300 validation and 300 test queries; n ∈ {32, 64}, L ∈ {8, 16, 32}, c/N ∈ {0.5%, 1%, 5%}; 3 seeds.

- **Query cost** = true-distance evaluations per query = n + c (machine-independent). Postings read, build distances, index size, median latency and peak memory are secondary.
- **Operating point:** on validation, take each method's Pareto frontier (recall@10 vs. query cost) and select the lowest-cost setting with mean recall@10 ≥ τ for each τ ∈ {0.80, 0.90}; if a method cannot reach τ, that τ is reported as not reached for it (its highest-recall setting is still reported); ties go to smaller index size. Settings are then frozen and run once on test.
- **Principal comparison** (MI-File vs. TPS), at each N: (a) matched recall: cost at the selected points; (b) matched budget: recall@10 at equal n, L, c.
- **"Beats"** = lower mean query cost at the same τ (or higher recall at equal c), with the 95% patient-level bootstrap CI of the paired per-query difference excluding 0; otherwise we report a tie.
- We also report MI-File zero-overlap misses.

## 5. Validation and plan

Python 3.11+ (NumPy, pandas; scikit-learn only for the optional baseline), fixed seeds, pytest tests: metric axioms, TPS and MI-File equal brute force when c = N, no patient in two partitions. Already implemented: loader, patient-grouped split, encoder, brute-force oracle, metric tests. Plan: pivots and TPS (mid-Nov), MI-File (late Nov), experiments, analysis and report (by Dec 7); optional extensions only after the essential comparison is complete. **Threat:** one dataset and one distance; recall is w.r.t. our metric, not clinical similarity.

## References

- Amato, G., and Savino, P. (2008). Approximate similarity search in metric spaces using inverted files. In *Proc. 3rd International Conference on Scalable Information Systems (InfoScale)*.
- Chávez, E., Figueroa, K., and Navarro, G. (2008). Effective proximity retrieval by ordering permutations. *IEEE Transactions on Pattern Analysis and Machine Intelligence*, 30(9), 1647–1658.
- Mohamed, H., and Marchand-Maillet, S. (2015). Scalable indexing for big data processing. In *Big Data: Algorithms, Analytics, and Applications*. Chapman and Hall/CRC.
- Strack, B., DeShazo, J. P., Gennings, C., Olmo, J. L., Ventura, S., Cios, K. J., and Clore, J. N. (2014). Impact of HbA1c measurement on hospital readmission rates: analysis of 70,000 clinical database patient records. *BioMed Research International*, 2014, Article 781670. Data: UCI Machine Learning Repository, doi:10.24432/C5230J.
