"""Builds the one-page DS8001 project proposal PDF with ReportLab."""
from pathlib import Path

from pypdf import PdfReader
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

OUT = Path(__file__).parent / "DS8001 project proposal Smouter Nalla.pdf"

body = ParagraphStyle("body", fontName="Times-Roman", fontSize=10, leading=11.8,
                      alignment=TA_JUSTIFY, spaceAfter=3.5)
title = ParagraphStyle("title", parent=body, fontName="Times-Bold", fontSize=12.5,
                       leading=14.5, alignment=1, spaceAfter=1)
sub = ParagraphStyle("sub", parent=body, alignment=1, spaceAfter=5)
ref = ParagraphStyle("ref", parent=body, fontSize=9, leading=10.4, leftIndent=12,
                     firstLineIndent=-12, spaceAfter=1.5)
code = "<font name='Courier'>{}</font>".format

story = [
    Paragraph("DS8001 Project Proposal: Permutation-Based Approximate kNN Search "
              "for Mixed-Type Hospital Encounters", title),
    Paragraph("Jared Smouter and Amarnadh Nalla &nbsp;|&nbsp; Project path: "
              "<b>Empirical Analysis</b> &nbsp;|&nbsp; Group of two", sub),

    Paragraph("<b>1. Problem and question.</b> Exact k-nearest-neighbor (kNN) "
              "search computes a distance to all N indexed objects. We study, as "
              "a purely algorithmic question (no clinical claim), how "
              "permutation-based approximate indexes trade recall for fewer "
              "distance computations under a mixed-type distance. "
              "<b>Principal question:</b> at matched recall@10, does the "
              "truncated MI-File (Amato and Savino, 2008) need fewer distance "
              "computations per query than the truncated permutation scan "
              "(TPS; Ch&aacute;vez et al., 2008), and how does this change with "
              "N? <b>Secondary:</b> how do the pivot count n, permutation "
              "length L and re-ranking budget c affect recall@10 and cost?", body),

    Paragraph("<b>2. Methods and scope.</b> <b>Essential (implemented by us):</b> "
              "(i) <b>brute-force exact kNN</b> (ground truth; ties by encounter "
              "id); (ii) <b>TPS</b>: each object stores the ranks of its L "
              "nearest pivots (rank L+1 otherwise); a query scores all objects "
              "by Spearman footrule over the n pivots, keeps the best c and "
              "re-ranks them with the true distance; (iii) <b>MI-File</b>: "
              "per-pivot posting lists of (object, rank) with the same score and "
              "re-ranking, touching only objects that share a retained pivot; "
              "random pivots. <b>Optional extensions (if time permits):</b> "
              "farthest-first pivots; scikit-learn <b>BallTree</b> as a library "
              "baseline (not counted as our implementation); extra grid values. "
              "Complexity: build O(Nn) distances, storage O(NL), query n pivot "
              "distances plus c re-ranking distances.", body),

    Paragraph("<b>Distance.</b> Six feature groups G (age, utilization, "
              "admission/discharge, ICD-9 diagnosis chapters, labs, medications) "
              "with equal weight 1/6. For objects x, y: <br/>"
                            "&nbsp;&nbsp;&nbsp;&nbsp;d(x,y) = (1/6) &Sigma;<sub>g</sub> (1/|g|) &Sigma;<sub>f&isin;g</sub> "
              "d<sub>f</sub>(x<sub>f</sub>, y<sub>f</sub>)               &isin; [0,1], <br/>so each "
              "group is normalized by its feature count. Numeric/ordinal: "
              "d<sub>f</sub> = |x<sub>f</sub> &minus; y<sub>f</sub>| / "
              "(max<sub>f</sub> &minus; min<sub>f</sub>), range fit on the index "
              "and queries clipped to it. Nominal: d<sub>f</sub> = 1[x<sub>f</sub> "
              "&ne; y<sub>f</sub>]. <b>Missing values</b> are never omitted "
              "pairwise: diagnoses, specialty, payer and labs get an explicit "
              "UNKNOWN/NOT_MEASURED category (so two unknowns match, unknown vs. "
              "known mismatches); numerics use the index median. This is a "
              "weighted L1 metric, checked on sampled triples.", body),

    Paragraph("<b>3. Data.</b> <b>Diabetes 130-US Hospitals (1999&ndash;2008)</b> "
              "(Strack et al., 2014; UCI): 101,766 encounters, 71,518 patients. "
              "We exclude IDs, " + code("readmitted") + ", race, gender and "
              + code("weight") + ". Patients are split 90/5/5 into "
              "index/validation/test (fixed seed), so no patient is in both "
              "index and queries; scales and medians are fit on the index only.",
              body),

    Paragraph("<b>4. Experiments, definitions and decision rules (fixed before "
              "running).</b> Nested N = 10k, 50k, full index; 300 validation and "
              "300 test queries; n &isin; {32, 64}, L &isin; {8, 16, 32}, c/N "
              "&isin; {0.5%, 1%, 5%}; 3 seeds. <b>Query cost</b> = true-distance "
              "evaluations per query = n + c (machine-independent); postings "
              "read, build distances, index size, median latency and peak memory "
              "are secondary. <b>Operating point:</b> on validation, take each "
              "method's Pareto frontier (recall@10 vs. query cost) and select "
              "              the lowest-cost setting with mean recall@10 &ge; &tau; for each "
                            "&tau; &isin; {0.80, 0.90}; if a method cannot reach &tau;, that "
                            "&tau; is reported as not reached for it (its highest-recall "
                            "setting is still reported); ties go to "
                            "smaller index size. Settings are then frozen and run once on "
                            "test. <b>Principal comparison</b> (MI-File vs. TPS), at each N: "
                            "(a) matched recall: cost at the selected points; (b) matched "
                            "budget: recall@10 at equal n, L, c. <b>&ldquo;Beats&rdquo;</b> = "
                            "lower mean query cost at the same &tau; (or higher recall at "
                            "equal c), with the 95% patient-level bootstrap CI of the paired "
              "per-query difference excluding 0; otherwise we report a tie. We "
              "also report MI-File zero-overlap misses.", body),

    Paragraph("<b>5. Validation and plan.</b> Python 3.11+ (NumPy, pandas; "
              "scikit-learn only for the optional baseline), fixed seeds, pytest "
              "tests: metric axioms, TPS and MI-File equal brute force when c = "
              "N, no patient in two partitions. Already implemented: loader, "
              "patient-grouped split, encoder, brute-force oracle, metric tests. "
              "Plan: pivots and TPS (mid-Nov), MI-File (late Nov), experiments, "
              "analysis and report (by Dec 7); optional extensions only after the "
              "essential comparison is complete. <b>Threat:</b> one dataset and "
              "one distance; recall is w.r.t. our metric, not clinical "
              "similarity.", body),

    Spacer(1, 2),
    Paragraph("<b>References</b>", body),
    Paragraph("Amato, G., and Savino, P. (2008). Approximate similarity search in "
              "metric spaces using inverted files. In <i>Proc. 3rd International "
              "Conference on Scalable Information Systems (InfoScale)</i>.", ref),
    Paragraph("Chávez, E., Figueroa, K., and Navarro, G. (2008). Effective "
              "proximity retrieval by ordering permutations. <i>IEEE "
              "Transactions on Pattern Analysis and Machine Intelligence</i>, "
              "30(9), 1647&ndash;1658.", ref),
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
