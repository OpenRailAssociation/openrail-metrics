"""PDF generation."""

import subprocess
from pathlib import Path


def generate_pdf(markdown_path: Path, output_path: Path):
    """Generate PDF from Markdown using Pandoc."""
    # Change to output directory so relative image paths work
    working_dir = markdown_path.parent

    # Find stylesheet (in project root)
    stylesheet = Path(__file__).parent.parent.parent / 'assets' / 'style.css'

    cmd = [
        'pandoc',
        markdown_path.name,
        '-o', output_path.name,
        '--pdf-engine=weasyprint',
    ]

    # Add stylesheet if it exists
    if stylesheet.exists():
        cmd.extend(['--css', str(stylesheet)])

    subprocess.run(cmd, cwd=working_dir, check=True)
