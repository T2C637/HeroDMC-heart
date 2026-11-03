"""Builds the one-page DS8001 project proposal PDF with ReportLab."""
from pathlib import Path

from pypdf import PdfReader
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

OUT = Path(__file__).parent / "DS8001 project proposal Smouter Nalla.pdf"

body = ParagraphStyle("body", fontName="Times-Roman", fontSize=9.5, leading=11.2,
                      alignment=TA_JUSTIFY, spaceAfter=3.5)
title = ParagraphStyle("title", parent=body, fontName="Times-Bold", fontSize=13,
                       leading=15, alignment=1, spaceAfter=1)
sub = ParagraphStyle("sub", parent=body, alignment=1, spaceAfter=5)
ref = ParagraphStyle("ref", parent=body, fontSize=8.4, leading=9.8, leftIndent=12,
                     firstLineIndent=-12, spaceAfter=1.5)
code = "<font name='Courier'>{}</font>".format

story = [
    Paragraph("DS8001 Project Proposal: Pivot-Based Approximate Similarity Search "
              "for Hospital Encounters", title),
    Paragraph("Jared Smouter and Amarnadh Nalla &nbsp;|&nbsp; Project path: "
              "<b>Empirical Analysis</b> &nbsp;|&nbsp; Group of two", sub),

    Paragraph("<b>1. Problem and questions.</b> Finding the most similar past "
              "hospital encounters supports case-based reasoning, cohort building "
              "and nearest-neighbor (kNN) risk prediction, but exact search "
              "computes a distance to every one of the N encounters. Following "
              "the scalable-indexing material of the course, we study the "
              "algorithmic question: <i>how well can pivot-based approximate "
              "indexes trade search quality against distance computations, index "
              "size and build cost on large, mixed-type clinical data?</i> "
              "(Q1) How do the number of pivots n, the pruned-list length "
              "&ntilde; and the re-ranking budget c affect recall@K, and which "
              "dominates? (Q2) Does the metric permutation table (MPT) improve on "
              "the metric inverted file (MIF) accumulator, especially for small "
              "&ntilde;? (Q3) How do the costs grow with N, and how does the "
              "intrinsic dimensionality of the data limit pruning, compared with "
              "exact tree indexes?", body),

    Paragraph("<b>2. Algorithms and implementation.</b> We will implement "
              "ourselves: (i) <b>exact brute-force</b> K-NN, as ground truth; "
              "(ii) <b>permutation-based indexing</b> (PBI), where each object is "
              "stored as the ordered list of its &ntilde; nearest pivots; "
              "(iii) the <b>metric inverted file</b> (MIF) with its Spearman "
              "footrule accumulator and exact re-ranking of the best c candidates "
              "(Amato and Savino, 2008); and (iv) the <b>MPT</b> scoring "
              "refinement, plus a prefix index (Esuli, 2012) if time permits. We "
              "will also compare random against farthest-first pivot selection. "
              "The report will analyze build cost O(Nn) distances, index size "
              "O(N&ntilde;), and why recall is limited when a query and its true "
              "neighbor share no pivot. Baselines (library code, not counted as "
              "our implementation): scikit-learn KD-tree and ball tree for exact "
              "search, and an inverted-file (IVF) index with k-means centroids "
              "(Jegou et al., 2011) built with scikit-learn.", body),

    Paragraph("<b>3. Data.</b> The <b>Diabetes 130-US Hospitals (1999&ndash;2008)</b> "
              "dataset (Strack et al., 2014; UCI Machine Learning Repository, "
              "CC BY 4.0): 101,766 inpatient encounters, 71,518 patients and 50 "
              "attributes (demographics, stay and utilization counts, ICD-9 "
              "diagnoses, 23 medication fields), with the 3-class label "
              + code("readmitted") + " (NO, &gt;30, &lt;30; &lt;30 is about 11%). "
                            "The dataset is widely used for readmission prediction; our "
                            "contribution is an algorithmic study of approximate similarity "
                            "search on it. Preprocessing: drop IDs and " + code("weight") + " (about 97% "
              "missing), and keep missing lab results as an explicit category. "
              "Because pivot methods only need a metric, we can use a "
              "mixed-type distance (the mean of per-feature distances: "
              "range-normalized absolute difference for numeric and ordinal "
              "attributes, 0/1 mismatch for categorical ones, in the spirit of "
              "Gower, 1971), which is a proper metric. We will also test an "
              "all-numeric one-hot Euclidean encoding. Subsets of "
              "N = 10k, 25k, 50k and 100k provide scaling instances.", body),

    Paragraph("<b>4. Experiments and metrics.</b> On 1,000 held-out queries with "
              "K = 10 and 50 we report recall@K against brute-force ground truth. "
              "Following the lecture, we report machine-independent costs: "
              "distances computed per query, postings read per query, index size "
              "and build distances. Wall-clock query latency and peak memory are "
              "reported too, but only between methods run in the same language on "
              "the same machine. We run a grid over (n, &ntilde;, c) and report "
              "the recall&ndash;cost trade-off curves for each method, then the "
              "scaling with N. Queries come from a patient-grouped split (by "
              + code("patient_nbr") + ") so no patient appears in both the index "
              "and the queries. Pivot selection is random, so each setting is "
              "repeated over 10 seeds and reported as mean &plusmn; standard "
              "deviation. Parameters are tuned on a validation set of patients, "
              "not on the query set. As an optional extension, we test how "
              "approximate neighbors change kNN readmission prediction, using "
              "balanced accuracy and macro-F1.", body),

    Paragraph("<b>5. Deliverables.</b> A Python (3.11+) package with a README and "
              "fixed seeds, and a report connecting the empirical trade-offs to "
              "the theory of pivot-based indexing and the curse of "
              "dimensionality.", body),

    Spacer(1, 2),
    Paragraph("<b>References</b>", body),
    Paragraph("Amato, G., and Savino, P. (2008). Approximate similarity search in "
              "metric spaces using inverted files. In <i>Proc. 3rd International "
              "Conference on Scalable Information Systems (InfoScale)</i>.", ref),
    Paragraph("Esuli, A. (2012). Use of permutation prefixes for efficient and "
              "scalable approximate similarity search. <i>Information Processing "
              "&amp; Management</i>, 48(5), 889&ndash;902.", ref),
    Paragraph("Gower, J. C. (1971). A general coefficient of similarity and some of "
              "its properties. <i>Biometrics</i>, 27(4), 857&ndash;871.", ref),
    Paragraph("Jegou, H., Douze, M., and Schmid, C. (2011). Product quantization "
              "for nearest neighbor search. <i>IEEE Transactions on Pattern "
              "Analysis and Machine Intelligence</i>, 33(1), 117&ndash;128.", ref),
    Paragraph("Mohamed, H., and Marchand-Maillet, S. (2015). Scalable indexing for "
              "big data processing. In <i>Big Data: Algorithms, Analytics, and "
              "Applications</i>. Chapman and Hall/CRC.", ref),
    Paragraph("Strack, B., DeShazo, J. P., Gennings, C., Olmo, J. L., Ventura, S., "
              "Cios, K. J., and Clore, J. N. (2014). Impact of HbA1c measurement "
              "on hospital readmission rates: analysis of 70,000 clinical database "
              "patient records. <i>BioMed Research International</i>, 2014, "
              "Article 781670. Data: UCI Machine Learning Repository, "
              "doi:10.24432/C5230J.", ref),
]

doc = SimpleDocTemplate(str(OUT), pagesize=letter, leftMargin=0.75 * inch,
                        rightMargin=0.75 * inch, topMargin=0.55 * inch,
                        bottomMargin=0.5 * inch,
                        title="DS8001 Project Proposal")
doc.build(story)
print("pages:", len(PdfReader(str(OUT)).pages))
