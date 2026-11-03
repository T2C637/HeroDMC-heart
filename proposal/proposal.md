# DS8001 Project Proposal: Pivot-Based Approximate Similarity Search for Hospital Encounters

Jared Smouter and Amarnadh Nalla | Project path: **Empirical Analysis** | Group of two

## 1. Problem and questions

Finding the most similar past hospital encounters supports case-based reasoning, cohort building and nearest-neighbor (kNN) risk prediction, but exact search computes a distance to every one of the N encounters. Following the scalable-indexing material of the course, we study the algorithmic question: *how well can pivot-based approximate indexes trade search quality against distance computations, index size and build cost on large, mixed-type clinical data?*

- **Q1.** How do the number of pivots n, the pruned-list length ñ and the re-ranking budget c affect recall@K, and which dominates?
- **Q2.** Does the metric permutation table (MPT) improve on the metric inverted file (MIF) accumulator, especially for small ñ?
- **Q3.** How do the costs grow with N, and how does the intrinsic dimensionality of the data limit pruning, compared with exact tree indexes?

## 2. Algorithms and implementation

We will implement ourselves:

1. **Exact brute-force** K-NN, as ground truth.
2. **Permutation-based indexing** (PBI), where each object is stored as the ordered list of its ñ nearest pivots.
3. The **metric inverted file** (MIF) with its Spearman footrule accumulator and exact re-ranking of the best c candidates (Amato and Savino, 2008).
4. The **MPT** scoring refinement, plus a prefix index (Esuli, 2012) if time permits.

We will also compare random against farthest-first pivot selection. The report will analyze build cost O(Nn) distances, index size O(Nñ), and why recall is limited when a query and its true neighbor share no pivot.

Baselines (library code, not counted as our implementation): scikit-learn KD-tree and ball tree for exact search, and an inverted-file (IVF) index with k-means centroids (Jegou et al., 2011) built with scikit-learn.

## 3. Data

The **Diabetes 130-US Hospitals (1999-2008)** dataset (Strack et al., 2014; UCI Machine Learning Repository, CC BY 4.0): 101,766 inpatient encounters, 71,518 patients and 50 attributes (demographics, stay and utilization counts, ICD-9 diagnoses, 23 medication fields), with the 3-class label `readmitted` (NO, >30, <30; <30 is about 11%).

Preprocessing: drop IDs and `weight` (about 97% missing), and keep missing lab results as an explicit category. Because pivot methods only need a metric, we can use a mixed-type distance (the mean of per-feature distances: range-normalized absolute difference for numeric and ordinal attributes, 0/1 mismatch for categorical ones, in the spirit of Gower, 1971), which is a proper metric. We will also test an all-numeric one-hot Euclidean encoding. Subsets of N = 10k, 25k, 50k and 100k provide scaling instances.

## 4. Experiments and metrics

On 1,000 held-out queries with K = 10 and 50 we report recall@K against brute-force ground truth. Following the lecture, we report machine-independent costs: distances computed per query, postings read per query, index size and build distances. Wall-clock query latency and peak memory are reported too, but only between methods run in the same language on the same machine.

We run a grid over (n, ñ, c) and report the recall-cost trade-off curves for each method, then the scaling with N. Queries come from a patient-grouped split (by `patient_nbr`) so no patient appears in both the index and the queries. Pivot selection is random, so each setting is repeated over 10 seeds and reported as mean ± standard deviation. Parameters are tuned on a validation set of patients, not on the query set.

As an optional extension, we test how approximate neighbors change kNN readmission prediction, using balanced accuracy and macro-F1.

## 5. Deliverables

A Python (3.11+) package with a README and fixed seeds, and a report connecting the empirical trade-offs to the theory of pivot-based indexing and the curse of dimensionality.

## References

- Amato, G., and Savino, P. (2008). Approximate similarity search in metric spaces using inverted files. In *Proc. 3rd International Conference on Scalable Information Systems (InfoScale)*.
- Esuli, A. (2012). Use of permutation prefixes for efficient and scalable approximate similarity search. *Information Processing & Management*, 48(5), 889-902.
- Gower, J. C. (1971). A general coefficient of similarity and some of its properties. *Biometrics*, 27(4), 857-871.
- Jegou, H., Douze, M., and Schmid, C. (2011). Product quantization for nearest neighbor search. *IEEE Transactions on Pattern Analysis and Machine Intelligence*, 33(1), 117-128.
- Mohamed, H., and Marchand-Maillet, S. (2015). Scalable indexing for big data processing. In *Big Data: Algorithms, Analytics, and Applications*. Chapman and Hall/CRC.
- Strack, B., DeShazo, J. P., Gennings, C., Olmo, J. L., Ventura, S., Cios, K. J., and Clore, J. N. (2014). Impact of HbA1c measurement on hospital readmission rates: analysis of 70,000 clinical database patient records. *BioMed Research International*, 2014, Article 781670. Data: UCI Machine Learning Repository, doi:10.24432/C5230J.
