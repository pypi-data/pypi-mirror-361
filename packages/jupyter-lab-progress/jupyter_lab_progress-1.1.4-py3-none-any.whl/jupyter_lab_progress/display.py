from IPython.display import display, HTML, Markdown
from typing import Optional, Dict, Any
import json
import re

def _format_message(message: str) -> str:
    """Format a message for HTML display, handling line breaks and basic formatting."""
    # Convert newlines to HTML line breaks
    formatted = message.replace('\n', '<br>')
    
    # Convert numbered lists (1. item, 2. item, etc.)
    formatted = re.sub(r'^(\d+\.\s)', r'<br>&nbsp;&nbsp;\1', formatted, flags=re.MULTILINE)
    
    # Convert bullet points (- item or * item)
    formatted = re.sub(r'^([-*]\s)', r'<br>&nbsp;&nbsp;•&nbsp;', formatted, flags=re.MULTILINE)
    
    # Clean up any leading <br> tags
    formatted = re.sub(r'^<br>', '', formatted)
    
    return formatted

def show_info(message: str, title: Optional[str] = None):
    """Display an information message with blue styling."""
    title_html = f"<strong>{title}</strong><br>" if title else ""
    formatted_message = _format_message(message)
    display(HTML(f"""
    <div style='background-color: #e7f3ff; border-left: 6px solid #2196F3; 
                padding: 10px; margin: 10px 0; border-radius: 5px;'>
        <span style='font-size: 16px; margin-right: 8px;'>ℹ️</span>
        {title_html}{formatted_message}
    </div>
    """))

def show_warning(message: str, title: Optional[str] = None):
    """Display a warning message with yellow styling."""
    title_html = f"<strong>{title}</strong><br>" if title else ""
    formatted_message = _format_message(message)
    display(HTML(f"""
    <div style='background-color: #fff3cd; border-left: 6px solid #ffecb5; 
                padding: 10px; margin: 10px 0; border-radius: 5px;'>
        <span style='font-size: 16px; margin-right: 8px;'>⚠️</span>
        {title_html}{formatted_message}
    </div>
    """))

def show_error(message: str, title: Optional[str] = None):
    """Display an error message with red styling."""
    title_html = f"<strong>{title}</strong><br>" if title else ""
    formatted_message = _format_message(message)
    display(HTML(f"""
    <div style='background-color: #ffebee; border-left: 6px solid #f44336; 
                padding: 10px; margin: 10px 0; border-radius: 5px;'>
        <span style='font-size: 16px; margin-right: 8px;'>❌</span>
        {title_html}{formatted_message}
    </div>
    """))

def show_success(message: str, title: Optional[str] = None):
    """Display a success message with green styling."""
    title_html = f"<strong>{title}</strong><br>" if title else ""
    formatted_message = _format_message(message)
    display(HTML(f"""
    <div style='background-color: #e8f5e9; border-left: 6px solid #4CAF50; 
                padding: 10px; margin: 10px 0; border-radius: 5px;'>
        <span style='font-size: 16px; margin-right: 8px;'>✅</span>
        {title_html}{formatted_message}
    </div>
    """))

def show_code(code: str, language: str = "python", title: Optional[str] = None):
    """Display code with syntax highlighting."""
    title_html = f"<h4 style='margin-bottom: 10px;'>{title}</h4>" if title else ""
    display(HTML(f"""
    {title_html}
    <pre style='background-color: #f5f5f5; padding: 15px; border-radius: 5px; 
                overflow-x: auto; border: 1px solid #ddd;'>
        <code class='language-{language}'>{code}</code>
    </pre>
    """))

def show_hint(hint: str, title: str = "Hint"):
    """Display a collapsible hint."""
    import uuid
    hint_id = str(uuid.uuid4())
    display(HTML(f"""
    <details style='background-color: #f0f7ff; padding: 10px; margin: 10px 0; 
                     border-radius: 5px; border: 1px solid #90caf9;'>
        <summary style='cursor: pointer; font-weight: bold; color: #1976d2;'>
            💡 {title} (click to expand)
        </summary>
        <div style='margin-top: 10px; padding-left: 20px;'>{hint}</div>
    </details>
    """))

def show_progress_bar(current: int, total: int, label: str = "", 
                     color: str = "#4CAF50"):
    """Display a progress bar."""
    percentage = (current / total) * 100 if total > 0 else 0
    display(HTML(f"""
    <div style='margin: 10px 0;'>
        {f"<div style='margin-bottom: 5px;'>{label}</div>" if label else ""}
        <div style='background-color: #e0e0e0; border-radius: 10px; height: 25px;'>
            <div style='background-color: {color}; height: 100%; border-radius: 10px; 
                        width: {percentage}%; transition: width 0.3s ease;
                        display: flex; align-items: center; padding-left: 10px;'>
                <span style='color: white; font-size: 12px; font-weight: bold;'>
                    {current}/{total} ({percentage:.0f}%)
                </span>
            </div>
        </div>
    </div>
    """))

def show_json(data: Dict[str, Any], title: Optional[str] = None, 
              collapsed: bool = False):
    """Display JSON data in a formatted, collapsible view."""
    import uuid
    json_id = str(uuid.uuid4())
    json_str = json.dumps(data, indent=2)
    
    if collapsed:
        display(HTML(f"""
        <details style='margin: 10px 0;'>
            <summary style='cursor: pointer; font-weight: bold; 
                           background-color: #f5f5f5; padding: 10px; 
                           border-radius: 5px;'>
                {title or 'JSON Data'} (click to expand)
            </summary>
            <pre style='background-color: #f8f8f8; padding: 15px; 
                        border-radius: 5px; overflow-x: auto; 
                        border: 1px solid #ddd; margin-top: 5px;'>
                <code>{json_str}</code>
            </pre>
        </details>
        """))
    else:
        title_html = f"<h4>{title}</h4>" if title else ""
        display(HTML(f"""
        {title_html}
        <pre style='background-color: #f8f8f8; padding: 15px; 
                    border-radius: 5px; overflow-x: auto; 
                    border: 1px solid #ddd; margin: 10px 0;'>
            <code>{json_str}</code>
        </pre>
        """))

def show_table(headers: list, rows: list, title: Optional[str] = None):
    """Display data in a formatted table."""
    title_html = f"<h4>{title}</h4>" if title else ""
    
    header_html = "".join(f"<th style='padding: 10px; text-align: left; background-color: #f5f5f5;'>{h}</th>" 
                         for h in headers)
    
    rows_html = ""
    for i, row in enumerate(rows):
        bg_color = "#ffffff" if i % 2 == 0 else "#f9f9f9"
        row_html = "".join(f"<td style='padding: 10px; border-bottom: 1px solid #ddd;'>{cell}</td>" 
                          for cell in row)
        rows_html += f"<tr style='background-color: {bg_color};'>{row_html}</tr>"
    
    display(HTML(f"""
    {title_html}
    <table style='border-collapse: collapse; width: 100%; margin: 10px 0; 
                  border: 1px solid #ddd;'>
        <thead>
            <tr>{header_html}</tr>
        </thead>
        <tbody>
            {rows_html}
        </tbody>
    </table>
    """))

def show_checklist(items: Dict[str, bool], title: str = "Checklist"):
    """Display a checklist with checked/unchecked items."""
    items_html = ""
    for item, checked in items.items():
        icon = "✅" if checked else "⬜"
        style = "color: #4CAF50;" if checked else "color: #666;"
        items_html += f"<li style='{style} list-style: none; margin: 5px 0;'>{icon} {item}</li>"
    
    display(HTML(f"""
    <div style='background-color: #f9f9f9; padding: 15px; 
                border-radius: 5px; margin: 10px 0;'>
        <h4 style='margin-top: 0;'>{title}</h4>
        <ul style='padding-left: 0; margin-bottom: 0;'>
            {items_html}
        </ul>
    </div>
    """))

def show_tabs(tabs: Dict[str, str], default_tab: Optional[str] = None):
    """Display content in tabs."""
    import uuid
    tab_id = str(uuid.uuid4())
    
    if not default_tab:
        default_tab = list(tabs.keys())[0]
    
    tab_buttons = ""
    tab_contents = ""
    
    for i, (tab_name, content) in enumerate(tabs.items()):
        active = tab_name == default_tab
        button_style = """
            padding: 10px 20px; 
            background-color: {bg}; 
            border: 1px solid #ddd; 
            border-bottom: none; 
            cursor: pointer;
            border-radius: 5px 5px 0 0;
            margin-right: 5px;
        """.format(bg="#fff" if active else "#f5f5f5")
        
        content_style = f"""
            padding: 20px; 
            background-color: #fff; 
            border: 1px solid #ddd;
            border-radius: 0 5px 5px 5px;
            display: {'block' if active else 'none'};
        """
        
        tab_buttons += f"""
            <button id="tab-btn-{tab_id}-{i}" 
                    onclick="showTab('{tab_id}', {i})"
                    style="{button_style}">
                {tab_name}
            </button>
        """
        
        tab_contents += f"""
            <div id="tab-content-{tab_id}-{i}" style="{content_style}">
                {content}
            </div>
        """
    
    display(HTML(f"""
    <div style='margin: 10px 0;'>
        <div style='margin-bottom: -1px;'>
            {tab_buttons}
        </div>
        <div>
            {tab_contents}
        </div>
    </div>
    <script>
    function showTab(tabId, index) {{
        // Hide all tabs
        var contents = document.querySelectorAll('[id^="tab-content-' + tabId + '"]');
        var buttons = document.querySelectorAll('[id^="tab-btn-' + tabId + '"]');
        
        for (var i = 0; i < contents.length; i++) {{
            contents[i].style.display = 'none';
            buttons[i].style.backgroundColor = '#f5f5f5';
        }}
        
        // Show selected tab
        document.getElementById('tab-content-' + tabId + '-' + index).style.display = 'block';
        document.getElementById('tab-btn-' + tabId + '-' + index).style.backgroundColor = '#fff';
    }}
    </script>
    """))

def clear():
    """Clear the output area."""
    from IPython.display import clear_output
    clear_output(wait=True)