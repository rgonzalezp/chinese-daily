import mistune
from mistune.renderers.html import HTMLRenderer

# Custom Renderer - Inject index into checkbox
class ClickableTaskRendererIndexed(HTMLRenderer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._task_counter = -1

    def checkbox_input(self, checked=False, **attrs):
        self._task_counter += 1 # Increment counter *per checkbox rendered*
        # Inject data-idx directly into the input tag
        # NOTE: We removed the hx-* attributes from here, they are added later with BS4
        return f'<input class="task-list-item-checkbox" type="checkbox" data-idx="{self._task_counter}" {"checked" if checked else ""}>'
        # Added back standard classes for consistency

    # No need to override list_item if index is on the input

# Create markdown instance with plugin AND custom renderer (v3 style)
# Use the specific class name here
markdown_parser = mistune.create_markdown(
    escape=False,
    plugins=['task_lists'], # Ensure plugin is enabled
    renderer=ClickableTaskRendererIndexed() 
)

def md_to_html(md_text: str) -> str:
    """Converts Markdown text to HTML using the configured parser."""
    # Reset counter for each new render call by creating a fresh renderer instance? 
    # Or assume mistune handles renderer state isolation per call.
    # For safety, let's re-instantiate parser components if state needs reset.
    # Simpler: Let's assume the parser is stateless enough for now.
    # We might need to reset _task_counter if renderer instance is reused inappropriately.
    
    # Ensure the renderer counter is reset if the global instance is problematic
    # A better approach might be to instantiate the parser within the function if needed.
    # For now, relying on the global instance and hoping its state management is sufficient.
    
    # If counter issues arise, recreate parser here:
    # parser = mistune.create_markdown(escape=False, plugins=['task_lists'], renderer=ClickableTaskRendererIndexed()) 
    
    return markdown_parser(md_text) 