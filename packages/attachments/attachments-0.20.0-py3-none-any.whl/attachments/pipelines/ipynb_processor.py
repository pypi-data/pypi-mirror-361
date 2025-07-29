# This file will contain the logic for processing IPYNB files.
# It will include a matcher, loader, presenter, and processor for IPYNB files.

from attachments.core import Attachment, loader

def ipynb_match(att: Attachment) -> bool:
    """Matches IPYNB files based on their extension."""
    return att.path.lower().endswith(".ipynb")

@loader(match=ipynb_match)
def ipynb_loader(att: Attachment) -> Attachment:
    """Loads and parses an IPYNB file."""
    try:
        import nbformat
    except ImportError:
        raise ImportError(
            "nbformat is required for Jupyter notebook processing.\n"
            "Install with: pip install nbformat"
        )
    
    with open(att.input_source, "r", encoding="utf-8") as f:
        notebook = nbformat.read(f, as_version=4)
    att._obj = notebook
    return att

from attachments.core import presenter

@presenter  
def ipynb_text_presenter(att: Attachment, notebook) -> Attachment:
    """Presents the IPYNB content as text."""
    full_content_blocks = []
    for cell in notebook.cells:
        cell_block_parts = []
        if cell.cell_type == "markdown":
            cell_block_parts.append(cell.source)
        elif cell.cell_type == "code":
            cell_block_parts.append(f"```python\n{cell.source}\n```")
            for output in cell.outputs:
                if output.output_type == "stream":
                    text = output.text
                    if text.endswith("\n"): # Ensure single newline for stream output before closing ```
                        text = text[:-1]
                    cell_block_parts.append(f"Output:\n```\n{text}\n```")
                elif output.output_type == "execute_result":
                    if "text/plain" in output.data:
                        text = output.data['text/plain']
                        if text.endswith("\n"): # Ensure single newline
                            text = text[:-1]
                        cell_block_parts.append(f"Output:\n```\n{text}\n```")
                elif output.output_type == "error":
                    cell_block_parts.append(f"Error:\n```\n{output.ename}: {output.evalue}\n```")

        if cell_block_parts:
            full_content_blocks.append("\n".join(cell_block_parts))

    att.text = "\n\n".join(full_content_blocks)
    return att

from attachments.pipelines import processor
from attachments import load, present

@processor(
    match=ipynb_match,
    description="A processor for IPYNB (Jupyter Notebook) files."
)
def ipynb_to_llm(att: Attachment) -> Attachment:
    """Processes an IPYNB file into an LLM-friendly text format."""
    from attachments import load, present # Explicit import
    return att | load.ipynb_loader | present.ipynb_text_presenter
