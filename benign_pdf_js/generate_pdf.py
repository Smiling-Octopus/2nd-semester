import io
import sys
import argparse
from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from pypdf import PdfReader, PdfWriter
from pypdf.generic import DictionaryObject, NameObject, ArrayObject, TextStringObject, NumberObject, BooleanObject, RectangleObject


def create_base_pdf(output_path: Path, title: str, warning_text: str):
    from reportlab.lib.colors import black, white
    c = canvas.Canvas(str(output_path), pagesize=A4)
    width, height = A4
    margin = 20 * mm

    # Draw Title
    c.setFont("Helvetica-Bold", 16)
    c.drawString(margin, height - margin, title)

    # Determine expected state based on title
    if "Control" in title:
        expected_state = "NOT_RUN"
    else:
        expected_state = "JS_EXECUTED"

    # Draw warning text and instructions
    c.setFont("Helvetica", 10)
    y_pos = height - margin - 20 * mm
    c.drawString(margin, y_pos, warning_text)

    y_pos -= 10 * mm
    c.drawString(margin, y_pos, "Harmless compatibility test")
    y_pos -= 5 * mm
    c.drawString(margin, y_pos, "No network, file, or program access")
    y_pos -= 5 * mm
    c.drawString(margin, y_pos, "Real viewer result NOT TESTED")
    y_pos -= 5 * mm
    c.drawString(margin, y_pos, "Record full build from About dialog")

    y_pos -= 10 * mm
    c.drawString(margin, y_pos, f"State control expected: {expected_state}")

    # Define fields
    fields = [
        ("test_status", "NOT_RUN"),
        ("viewer_type", "UNKNOWN"),
        ("viewer_version", "UNKNOWN"),
        ("viewer_variation", "UNKNOWN")
    ]

    field_width = 160 * mm
    field_height = 9 * mm
    label_height = 5 * mm
    spacing = 15 * mm

    current_y = y_pos - 10 * mm

    for name, value in fields:
        # Draw Label
        c.setFont("Helvetica", 10)
        c.drawString(margin, current_y, name)

        # Draw Field
        field_y = current_y - field_height - 2 * mm
        c.acroForm.textfield(
            name=name,
            value=value,
            fieldFlags="readOnly",
            borderColor=black,
            fillColor=white,
            textColor=black,
            fontName="Helvetica",
            fontSize=10,
            x=margin,
            y=field_y,
            width=field_width,
            height=field_height
        )

        current_y = field_y - spacing

    c.showPage()
    c.save()


def add_js_to_pdf(input_path: Path, output_path: Path, js_script: str):
    """Add JavaScript to an existing PDF using pypdf."""
    reader = PdfReader(str(input_path))
    writer = PdfWriter(clone_from=reader)

    # Add JavaScript
    writer.add_js(js_script)

    with open(str(output_path), "wb") as f:
        writer.write(f)


def main():
    parser = argparse.ArgumentParser(description="Generate benign PDFs for JavaScript compatibility testing.")
    parser.add_argument("output_dir", type=str, help="Existing output directory")
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    if not output_dir.is_dir():
        print(f"Error: {output_dir} is not an existing directory.", file=sys.stderr)
        sys.exit(1)

    # Define the JavaScript script
    js_script = """(function() {
    try {
        var statusField = this.getField("test_status");
        if (statusField) {
            statusField.value = "JS_EXECUTED";
        }
    } catch (e) {}

    try {
        var typeField = this.getField("viewer_type");
        if (typeField) {
            if (typeof app !== "undefined" && app.viewerType !== undefined) {
                typeField.value = String(app.viewerType);
            } else {
                typeField.value = "UNKNOWN";
            }
        }
    } catch (e) {
        var typeField = this.getField("viewer_type");
        if (typeField) {
            typeField.value = "UNKNOWN";
        }
    }

    try {
        var versionField = this.getField("viewer_version");
        if (versionField) {
            if (typeof app !== "undefined" && app.viewerVersion !== undefined) {
                versionField.value = String(app.viewerVersion);
            } else {
                versionField.value = "UNKNOWN";
            }
        }
    } catch (e) {
        var versionField = this.getField("viewer_version");
        if (versionField) {
            versionField.value = "UNKNOWN";
        }
    }

    try {
        var variationField = this.getField("viewer_variation");
        if (variationField) {
            if (typeof app !== "undefined" && app.viewerVariation !== undefined) {
                variationField.value = String(app.viewerVariation);
            } else {
                variationField.value = "UNKNOWN";
            }
        }
    } catch (e) {
        var variationField = this.getField("viewer_variation");
        if (variationField) {
            variationField.value = "UNKNOWN";
        }
    }
}).call(this);"""

    warning_text = "Harmless compatibility test, no network/files/programs, real viewer result NOT verified yet."

    # Create control PDF (no JS)
    control_path = output_dir / "control_no_js.pdf"
    create_base_pdf(control_path, "Control PDF - No JavaScript", warning_text)

    # Create benign JS test PDF
    benign_js_path = output_dir / "benign_js_test.pdf"
    temp_path = output_dir / "temp_benign.pdf"
    create_base_pdf(temp_path, "Benign JS Test PDF", warning_text)
    add_js_to_pdf(temp_path, benign_js_path, js_script)
    temp_path.unlink()

    # Save the JavaScript script
    js_path = output_dir / "test.js"
    with open(str(js_path), "w") as f:
        f.write(js_script)

    print(f"Generated files in {output_dir}:")
    print(f"  - {control_path.name}: Control PDF without JavaScript. Expected test_status=NOT_RUN.")
    print(f"  - {benign_js_path.name}: Benign PDF with JavaScript. Expected test_status=JS_EXECUTED.")
    print(f"  - {js_path.name}: Embedded JavaScript script.")
    print("")
    print("Expected behavior:")
    print("  - control_no_js.pdf: test_status remains NOT_RUN (no JS executed).")
    print("  - benign_js_test.pdf: test_status becomes JS_EXECUTED (JS executed).")
    print("  - viewer_type, viewer_version, viewer_variation: Populated from app object if available, else UNKNOWN.")
    print("  - Record full version from About dialog for verification.")
    print("  - Only the script reads viewer metadata; no identity data is collected.")


if __name__ == "__main__":
    main()
