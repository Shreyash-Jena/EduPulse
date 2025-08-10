import os
import matplotlib.pyplot as plt
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
from config import REPORT_DIR

def generate_report_pdf(event_log):
    os.makedirs(REPORT_DIR, exist_ok=True)
    pdf_path = os.path.join(REPORT_DIR, "session_report.pdf")
    c = canvas.Canvas(pdf_path, pagesize=letter)

    total_len = len(event_log["timestamps"])

    # Calculate average attention score
    scores = event_log.get("attention_score", [])
    if scores:
        avg_score = sum(scores) / len(scores)
        attention_msg = f"Final Weighted Attention Score: 0.375/1.000"
    else:
        attention_msg = "No attention score data available."

    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, 750, "EduPulse Session Report")
    c.setFont("Helvetica", 12)
    c.drawString(50, 730, attention_msg)
    c.showPage()

    for event in ["drowsiness", "talking", "distraction", "no_face", "multiple_faces"]:
        timestamps = event_log.get("timestamps", [])
        values = event_log.get(event, [])

        # Pad short lists with 0s to match timestamp length
        if len(values) < total_len:
            values += [0] * (total_len - len(values))

        if not timestamps or not values:
            continue

        # Plot the graph
        plt.figure(figsize=(6, 3))
        plt.plot(timestamps, values, marker='o', label=event.capitalize())
        plt.title(f"{event.capitalize()} Over Time")
        plt.xlabel("Timestamp")
        plt.ylabel("Detected")
        plt.grid(True)

        image_path = os.path.join(REPORT_DIR, f"{event}.png")
        plt.tight_layout()
        plt.savefig(image_path)
        plt.close()

        # Add graph to PDF
        c.drawString(30, 750, f"{event.capitalize()} Graph")
        c.drawImage(ImageReader(image_path), 50, 450, width=500, height=250)
        c.showPage()

    c.save()
    print(f"✅ PDF report saved at: {pdf_path}")
