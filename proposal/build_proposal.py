"""Builds the one-page DS8001 project proposal PDF with ReportLab."""
from pathlib import Path

from pypdf import PdfReader
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

OUT = Path(__file__).parent / "DS8001 project proposal Smouter Nalla.pdf"

body = ParagraphStyle("body", fontName="Times-Roman", fontSize=9.3, leading=10.8,
                      alignment=TA_JUSTIFY, spaceAfter=3.5)
title = ParagraphStyle("title", parent=body, fontName="Times-Bold", fontSize=12.5,
                       leading=14.5, alignment=1, spaceAfter=1)
sub = ParagraphStyle("sub", parent=body, alignment=1, spaceAfter=5)
ref = ParagraphStyle("ref", parent=body, fontSize=8.2, leading=9.5, leftIndent=12,
                     firstLineIndent=-12, spaceAfter=1.5)
code = "<font name='Courier'>{}</font>".format

story = [
    Paragraph("DS8001 Project Proposal: Permutation-Based Approximate kNN Search "
              "for Mixed-Type Hospital Encounters", title),
    Paragraph("Jared Smouter and Amarnadh Nalla &nbsp;|&nbsp; Project path: "
              "<b>Empirical Analysis</b> &nbsp;|&nbsp; Group of two", sub),

    Paragraph("<b>1. Problem and questions.</b> Exact k-nearest-neighbor (kNN) "
              "search computes a distance to all N indexed encounters. We study, "
              "as a purely algorithmic question (no clinical claim), how "
              "permutation-based approximate indexes trade recall against "
              "distance computations, index size and build cost under a "
              "mixed-type distance. The dataset is widely used for readmission "
              "prediction; our contribution is an algorithmic study of "
              "approximate similarity search on it. "
              "<b>RQ1.</b> How do the number of pivots n, the retained "
              "permutation length L and the re-ranking budget c affect recall@10 "
              "and query cost, and how do these costs scale with N? "
              "<b>RQ2.</b> At matched L and c, when does a truncated "
              "MI-File beat a truncated permutation scan, and how does random "
              "versus farthest-first pivot selection change this?", body),

    Paragraph("<b>2. Methods.</b> Implemented by us: (i) <b>brute-force exact "
              "kNN</b> (ground truth, ties broken by encounter id); (ii) a "
              "<b>truncated permutation scan</b> (TPS): each object stores the "
              "ranks of its L nearest pivots (rank L+1 otherwise); the query "
              "scores all objects by the Spearman footrule over the n pivots, "
              "keeps the best c and re-ranks them with the true distance "
              "(exact only within the candidate set); (iii) a <b>truncated "
              "MI-File</b> (Amato and Savino, 2008): per-pivot posting lists of "
              "(object, rank), with the same score and re-ranking, so only "
              "objects sharing a retained pivot are touched; (iv) random versus "
              "farthest-first pivot selection. Library baseline (not counted as "
              "ours): scikit-learn <b>BallTree</b> with the Manhattan metric on "
              "an exact weighted-L1 encoding of the distance, validated against "
              "brute force. Complexity analysis: build O(Nn) distances plus "
              "ranking, storage O(NL), query n pivot distances plus candidate "
              "scoring plus c re-ranking distances. "
              "<b>Distance:</b> six equal-weight feature groups (age, "
              "utilization, admission/discharge, ICD-9 diagnosis chapters, labs, "
              "medications); numeric features use scale-normalized absolute "
              "difference, nominal ones 0/1 mismatch, missing values get a "
              "fixed state or median plus indicator (no pairwise omission). With "
              "fixed scales and weights this is a metric, which we verify "
              "(identity, triangle inequality) on sampled triples.", body),

    Paragraph("<b>3. Data.</b> <b>Diabetes 130-US Hospitals (1999&ndash;2008)</b> "
              "(Strack et al., 2014; UCI, CC BY 4.0): 101,766 encounters, 71,518 "
              "patients. We exclude IDs, " + code("readmitted") + ", race, gender "
              "and " + code("weight") + ". Patients are split 90/5/5 into "
              "index/validation/test with a fixed seed, so no patient appears in "
              "both index and queries; scales and medians are fit on the index "
              "partition only.", body),

    Paragraph("<b>4. Experiments and metrics.</b> Nested index sizes N = 10k, "
              "50k and the full index partition; 300 validation and 300 test "
              "queries (one encounter per patient). Grid: n &isin; {32, 64}, "
              "L &isin; {8, 16, 32} (L &le; n), c/N &isin; {0.5%, 1%, 5%}, "
              "random and farthest-first pivots, 3 seeds each. We choose "
              "Pareto-optimal settings on validation, freeze them, and evaluate "
              "on test once. Metrics: recall@10 against brute force; distance "
              "computations, entries scored and postings read per query "
              "(machine-independent); serialized index size; build distances; "
              "median latency and peak memory (single-threaded, same machine). "
              "We report patient-level bootstrap 95% CIs, paired per-query "
              "differences, and seed variability separately from query "
              "variability. Deliverables: a Python 3.11+ package with README and "
              "fixed seeds, and a report relating the trade-offs to theory. "
              "Work split: J. Smouter &ndash; preprocessing, metric, brute force, "
              "BallTree; A. Nalla &ndash; TPS, MI-File, pivots; experiments, "
              "statistics and report are joint.", body),

    Spacer(1, 2),
    Paragraph("<b>References</b>", body),
    Paragraph("Amato, G., and Savino, P. (2008). Approximate similarity search in "
              "metric spaces using inverted files. In <i>Proc. 3rd International "
              "Conference on Scalable Information Systems (InfoScale)</i>.", ref),
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
