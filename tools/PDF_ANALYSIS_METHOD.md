# PDF Analysis Method

This document describes the reusable method for analyzing PDF reports, including layout, charts, and text content.

## Prerequisites

```bash
# Install required packages
pip install pdf2image
brew install poppler  # macOS
# or: apt-get install poppler-utils  # Linux
```

## Step 1: Convert PDF to Images

Use the `pdf_to_images.py` script to convert PDF pages to PNG images:

```bash
python tools/pdf_to_images.py <pdf_file> [output_dir] [dpi]
```

Example:
```bash
python tools/pdf_to_images.py reports/2025Q4/OpenRail-Metrics-2025Q4.pdf reports/2025Q4/images 150
```

This creates one PNG image per page at the specified DPI (default: 150).

## Step 2: Analyze Images

The images can then be viewed and analyzed to extract:
- Layout and design elements
- Text content and formatting
- Chart types and styling
- Color schemes and branding
- Section structure

## Step 3: Document Findings

Create structured notes about:
- Report sections and their purpose
- Text content (introductions, descriptions, etc.)
- Visual elements (logos, colors, fonts)
- Chart specifications

## Example: 2025Q4 Report Analysis

### Cover Page (Page 1)
- OpenRail logo (train wheel icon)
- Title: "Quarterly Metrics Report"
- Quarter: "Q4 2025"
- Scope: September - November
- Issue date: Dec 23, 2025
- Prepared by: Igor Zubiaurre
- Bitergia logo (owl)
- Design: Beige/cream background with orange dot pattern on right side

### Table of Contents (Page 2)
- Title: "The State of OpenRail"
- Sections:
  1. Spotlight Metric of the Quarter
  2. OpenRail-Wide Project Statistics
  3. Project Overview Pages
     - Stage 2 - Qualified: OSRD
     - Stage 1 - Onboarded: RCM OSS, DAC Mig, Netzgrafik-Editor, Liblrs
  - Appendices: Methodology, Bitergia and OpenRail

### Section 1: Spotlight Metric (Page 3)
- Title: "Cross-company collaboration is already happening"
- Narrative text explaining the metric
- Donut chart showing organization distribution
- Colors: Teal (SNCF) and Brown (SBB CFF FFS)

### Section 2: OpenRail-Wide Statistics (Page 4)
- Summary statistics for the quarter (Sep-Nov)
- Activity trend: Horizontal stacked bar chart by project
- Color-coded by commit volume ranges
- Code-committing organizations list with note about freelancers

## Tips for Future Analysis

1. **Use consistent DPI**: 150 DPI is good for screen viewing, 300 DPI for print quality
2. **Batch process**: Convert all pages at once for efficiency
3. **Organize output**: Use descriptive directory names (e.g., `{report_name}_images`)
4. **Document immediately**: Take notes while viewing to capture details
5. **Compare versions**: Keep images from different quarters to track evolution

## Automation Potential

This method can be automated further:
- OCR for text extraction (tesseract)
- Chart detection and classification
- Color palette extraction
- Layout analysis
- Diff comparison between reports
