"""PDF generation."""

import subprocess
from pathlib import Path


def generate_pdf(markdown_path: Path, output_path: Path):
    """Generate PDF from Markdown using Pandoc."""
    # Change to output directory so relative image paths work
    working_dir = markdown_path.parent
    
    subprocess.run([
        'pandoc',
        markdown_path.name,
        '-o', output_path.name,
        '--pdf-engine=weasyprint',
        '-V', 'geometry:margin=1in'
    ], cwd=working_dir, check=True)
