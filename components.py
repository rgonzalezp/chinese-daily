from fasthtml.common import Div, Textarea, Span, Form, Input, Br # Import necessary components

def MarkdownEditor(initial_markdown: str, 
                   render_url: str, 
                   preview_target_id: str, 
                   editor_name: str = "notes", 
                   rows: int = 15, 
                   is_editable: bool = True,
                   initial_preview_html: str = ""):
    """
    Generates a two-pane markdown editor with live preview.

    Args:
        initial_markdown: The starting markdown text for the editor.
        render_url: The URL endpoint to POST markdown to for rendering the preview.
        preview_target_id: The ID of the element where the rendered preview should be placed.
        editor_name: The 'name' attribute for the textarea input.
        rows: The number of rows for the textarea.
        is_editable: Whether the textarea should be enabled.
        initial_preview_html: The pre-rendered HTML for the initial preview pane state.
    """
    unique_spinner_id = f"spinner-{preview_target_id}" # Make spinner ID unique if multiple editors exist

    return Div( # Container for editor and preview
        # Editor Pane
        Div(
            Textarea(initial_markdown, name=editor_name, rows=rows,
                     disabled=not is_editable,
                     # HTMX attributes for live preview
                     hx_post=render_url,
                     hx_trigger="keyup changed delay:500ms",
                     hx_target=f"#{preview_target_id}",
                     hx_indicator=f"#{unique_spinner_id}" # Point to unique spinner
                    ),
            cls="notes-editor-pane" # Class for editor div
        ),
        # Preview Pane
        Div(
            # Optional: Spinner placeholder
            Span(id=unique_spinner_id, cls="htmx-indicator", content=" Loading preview..."),
            # Initial rendered content (rendered by the caller)
            initial_preview_html if isinstance(initial_preview_html, str) else initial_preview_html,
            id=preview_target_id, # The target ID for preview updates
            cls="notes-preview-pane tasks-display-readonly" # Re-use styling
        ),
        cls="editor-preview-container" # Class for the flex container
    ) 