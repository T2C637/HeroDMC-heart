"""Build the one-page DS8001 project proposal PDF with ReportLab."""
from pathlib import Path

from pypdf import PdfReader
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

OUT = Path(__file__).parent / "DS8001 project proposal Smouter Nalla.pdf"

body = ParagraphStyle("body", fontName="Times-Roman", fontSize=9.4, leading=10.6,
                      alignment=TA_JUSTIFY, spaceAfter=3)
title = ParagraphStyle("title", parent=body, fontName="Times-Bold", fontSize=12,
                       leading=13.5, alignment=1, spaceAfter=1)
sub = ParagraphStyle("sub", parent=body, alignment=1, spaceAfter=4)
ref = ParagraphStyle("ref", parent=body, fontSize=8.2, leading=9.1, leftIndent=11,
                     firstLineIndent=-11, spaceAfter=1)
story = [
    Paragraph("DS8001 Project Proposal: Permutation-Based Approximate kNN Search "
              "for Mixed-Type Hospital Encounters", title),
    Paragraph("Jared Smouter and Amarnadh Nalla &nbsp;|&nbsp; Project path: "
              "<b>Empirical Analysis</b> &nbsp;|&nbsp; Group of two", sub),
    Paragraph("<b>1. Problem and questions.</b> Exact k-nearest-neighbor (kNN) "
              "search compares a query with all N indexed encounters. Using "
              "hospital encounters only as a mixed-type retrieval benchmark "
              "(no clinical claim), we ask: at matched recall@10, does a "
              "truncated MI-File reduce query latency and work relative to a "
              "truncated permutation scan (TPS), and how does the trade-off "
              "change with N? We also measure sensitivity to pivot count n, "
              "retained rank length L and reranking cap c.", body),
    Paragraph("<b>2. Methods and scope.</b> We implement exact brute-force "
              "kNN as ground truth, TPS, and a truncated MI-File. Both "
              "approximate methods use the same random pivots; each ranks "
              "pivots by distance (ties by pivot ID), retains its top L, and "
              "assigns absent pivots rank L+1. Both use Spearman-footrule "
              "candidate scores and true-distance reranking. TPS scores all N "
              "signatures; MI-File "
              "accumulates scores from posting lists for the query's retained "
              "pivots, so only objects sharing a retained pivot can enter its "
              "candidate set. A scikit-learn BallTree is an exact library "
              "control on a weighted-L1 embedding of the same distance; we "
              "will verify it against brute force, including boundary ties. "
              "Build uses O(Nn) pivot-distance evaluations plus ranking and "
              "stores O(NL) ranks. TPS query scoring is O(Nn); MI-File work "
              "depends on postings read and candidates. Each uses n query-pivot "
              "distances and reranks at most c candidates.", body),
    Paragraph("<b>Distance.</b> Six feature groups (age, utilization, "
              "admission/discharge, ICD-9 chapters, labs, medications) have "
              "equal total weight; features share their group's weight. "
              "Numeric/ordinal values use absolute differences after fixed "
              "index-fitted range scaling, without clipping; zero-range "
              "features are dropped. Nominal values use 0/1 mismatch. The "
              "selected numeric columns are complete in this dataset; "
              "categorical missing/unknown values and lab NOT_MEASURED are "
              "explicit fixed states, never pairwise-omitted. Thus the fixed "
              "weighted sum is a metric on the encoded feature states and has "
              "an exact weighted-L1 embedding for the BallTree. Out-of-index "
              "values retain their scaled differences.", body),
    Paragraph("<b>3. Data and leakage control.</b> Diabetes 130-US Hospitals "
              "(1999-2008): 101,766 encounters, 71,518 patients (Strack et al., "
              "2014; UCI). Patient groups are split 90/5/5 into index, "
              "validation and test with a fixed seed; one query per patient "
              "is sampled. Scales and category vocabulary are fitted using "
              "index patients only; unseen categories map to OTHER. ICD-9 "
              "chapters use a fixed published grouping. Exclude "
              "encounter/patient IDs, readmitted, race, gender "
              "and weight.", body),
    Paragraph("<b>4. Experiments and decision rules.</b> Nested index sizes "
              "N=10k, 50k and the full index; 500 validation and 500 test "
              "queries; five pivot seeds; n in {32, 64}, L in {8, 16, 32}, "
              "c/N in {0.5%, 1%, 5%}. On validation, select Pareto configurations "
              "for recall@10 versus median latency; freeze the lowest-latency "
              "settings meeting recall targets 0.80 and 0.90 before test. "
              "Compare test latency and report distinct true-distance calls "
              "(reusing query-pivot distances), TPS signatures scored, MI-File postings/"
              "candidates, index bytes, build cost and peak memory separately. "
              "Report MI-File zero-overlap misses: true top-10 neighbors excluded "
              "before reranking. "
              "Also compare recall at matched true-distance-call budgets. Run "
              "single-threaded, warmed, repeated query batches on the same "
              "machine. Break candidate-score and exact-distance ties by "
              "encounter ID; "
              "report strict and boundary-tie-aware recall@10. Paired "
              "patient-level bootstrap intervals quantify query uncertainty; "
              "show results for each pivot seed to expose seed variability. "
              "An unreached recall target is reported as such, not extrapolated.", body),
    Paragraph("<b>5. Validation and scope.</b> We will test patient separation, "
              "metric properties, deterministic ties, and exact agreement of "
              "the L1 embedding and BallTree with brute force on sampled cases. "
              "The contribution is a controlled empirical comparison, not a "
              "new index. One dataset and one declared distance limit "
              "generalization; conclusions concern algorithmic retrieval, not "
              "clinical similarity. Python 3.11+; fixed seeds and experiment "
              "settings will be documented for reproduction.", body),
    Spacer(1, 1),
    Paragraph("<b>References</b>", body),
    Paragraph("Amato, G., &amp; Savino, P. (2008). Approximate similarity search "
              "in metric spaces using inverted files. <i>Proc. InfoScale</i>.", ref),
    Paragraph("Chávez, E., Figueroa, K., &amp; Navarro, G. (2008). Effective "
              "proximity retrieval by ordering permutations. <i>IEEE TPAMI, "
              "30</i>(9), 1647-1658.", ref),
    Paragraph("Pedregosa, F. et al. (2011). Scikit-learn: Machine learning in "
              "Python. <i>JMLR, 12</i>, 2825-2830.", ref),
    Paragraph("Strack, B. et al. (2014). Impact of HbA1c measurement on "
              "hospital readmission rates. <i>BioMed Research International</i>, "
              "2014, 781670. UCI dataset, doi:10.24432/C5230J.", ref),
]

doc = SimpleDocTemplate(str(OUT), pagesize=letter, leftMargin=0.68 * inch,
                        rightMargin=0.68 * inch, topMargin=0.45 * inch,
                        bottomMargin=0.42 * inch,
                        title="DS8001 Project Proposal")
doc.build(story)
pages = len(PdfReader(str(OUT)).pages)
print("pages:", pages)
if pages != 1:
    raise SystemExit("Proposal must fit on one page.")
