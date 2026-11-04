# DS8001 Project Proposal: Permutation-Based Approximate kNN Search for Mixed-Type Hospital Encounters

Jared Smouter and Amarnadh Nalla | Project path: **Empirical Analysis** | Group of two

## 1. Problem and questions

Exact k-nearest-neighbor (kNN) search compares a query with all N indexed encounters. Using hospital encounters only as a mixed-type retrieval benchmark (no clinical claim), we ask: at matched recall@10, does a truncated MI-File (Amato & Savino, 2008) reduce query latency and work relative to a truncated permutation scan (TPS; Chávez et al., 2008), and how does the trade-off change with N? We also measure sensitivity to pivot count n, retained rank length L and reranking cap c.

## 2. Methods and scope

We implement exact brute-force kNN as ground truth, TPS, and a truncated MI-File. Both approximate methods use the same random pivots; each ranks pivots by distance (ties by pivot ID), retains its top L, and assigns absent pivots rank L+1, our explicit truncation rule. Both use Spearman-footrule scores over all n pivots and rerank candidates by the true distance. TPS scans all N signatures; MI-File unions the query's L posting lists, scores each distinct candidate, and reranks up to min(c, candidates). Thus only shared-pivot objects can enter its candidate set; matching signatures isolates the effect of this access structure. This comparison builds on the course's metric-inverted-file and permutation-index topics (DS 8001, 2026). A scikit-learn BallTree (Pedregosa et al., 2011) is an exact library control on a weighted-L1 embedding of the same metric; we will check it against brute force, including ties.

Build uses Nn pivot-distance evaluations and O(Nn log n) sorting; storage is O(NL) rank/posting entries. TPS scores in O(Nn); MI-File work is O(P+Un), for P postings read and U distinct candidates, plus n query-pivot and at most c reranking distances.

## Distance

Six feature groups (age, utilization, admission/discharge, ICD-9 chapters, labs, medications) have equal total weight; features share their group's weight. Numeric/ordinal values use absolute differences after fixed index-fitted range scaling, without clipping; zero-range features are dropped. Nominal values use 0/1 mismatch. The selected numeric columns are complete in this dataset; categorical missing/unknown values and lab NOT_MEASURED are explicit fixed states, never pairwise-omitted. Thus the fixed weighted sum is a metric on the encoded feature states and has an exact weighted-L1 embedding for the BallTree. Out-of-index values retain their scaled differences.

## 3. Data and leakage control

Diabetes 130-US Hospitals (1999-2008): 101,766 encounters, 71,518 patients (Strack et al., 2014; UCI). Patient groups are split 90/5/5 into index, validation and test with a fixed seed; one query per patient is sampled. Fit scales and category vocabulary once on the full index partition and freeze them across nested N; unseen categories map to OTHER. ICD-9 chapters use a fixed published grouping. Exclude encounter/patient IDs, `readmitted`, race, gender and `weight`.

## 4. Experiments and decision rules

Nested index sizes N=10k, 50k and the full index; 500 validation and 500 test queries; five fixed pivot seeds; n in {32, 64}, L in {8, 16, 32}, c/N in {0.5%, 1%, 5%}. Tune on validation across the five seeds; freeze the lowest-median-latency settings meeting mean recall targets 0.80 and 0.90 before test, breaking ties by smaller index size then fewer distance calls. On identical test queries, compare TPS/MI-File and exact brute-force/BallTree controls; verify BallTree top-10 against brute force on all test queries, allowing exact-distance ties. Report latency, distinct true-distance calls (reusing query-pivot distances), TPS signatures scored, MI-File postings/candidates, index bytes, build cost and peak memory separately. Report MI-File zero-overlap misses: true top-10 neighbors excluded before reranking. Also compare recall at matched true-distance-call budgets. Run single-threaded on the same machine; warm up and time five batches, report median and p95 query latency, and record hardware/software versions. Break candidate-score and exact-distance ties by encounter ID; report strict recall and recall crediting any neighbor tied at the exact rank-10 distance. Paired patient-level bootstrap intervals quantify query uncertainty; report each pivot seed separately. An unreached recall target is reported as such, not extrapolated.

## 5. Validation and scope

We will test patient separation, metric properties, deterministic ties, and exact agreement of the L1 embedding and BallTree with brute force on sampled cases. The contribution is a controlled empirical comparison, not a new index. One dataset and one declared distance limit generalization; conclusions concern algorithmic retrieval, not clinical similarity. Python 3.11+; code, versions, fixed seeds and experiment settings will be documented for reproduction.

## References

- Amato, G., & Savino, P. (2008). Approximate similarity search in metric spaces using inverted files. In *Proceedings of the 3rd International Conference on Scalable Information Systems*.
- Chávez, E., Figueroa, K., & Navarro, G. (2008). Effective proximity retrieval by ordering permutations. *IEEE Transactions on Pattern Analysis and Machine Intelligence, 30*(9), 1647–1658.
- Pedregosa, F. et al. (2011). Scikit-learn: Machine learning in Python. *Journal of Machine Learning Research, 12*, 2825–2830.
- DS 8001. (2026). *Lecture 8: Scalable Indexing for Big Data Processing* [Course handout].
- Strack, B. et al. (2014). Impact of HbA1c measurement on hospital readmission rates: analysis of 70,000 clinical database patient records. *BioMed Research International, 2014*, 781670. UCI, doi:10.24432/C5230J.
