from typing import Optional, List, Dict, Tuple
from icons.lucide import get_lucide_svg

def render_logo(size: int = 70) -> str:
    """Generate high-fidelity branded logo with custom PNG/SVG icon for DevCore AI."""
    import os
    import re
    import base64
    import streamlit as st
    from theme import LIGHT_THEME, DARK_THEME
    theme_name = st.session_state.get("theme", "light")
    colors = LIGHT_THEME if theme_name == "light" else DARK_THEME
    
    primary = colors["primary_color"]
    text = colors["text_color"]
    
    logo_png_path = os.path.join(os.path.dirname(__file__), "..", "assets", "logo.png")
    logo_svg_path = os.path.join(os.path.dirname(__file__), "..", "assets", "logo.svg")
    
    logo_html = ""
    if os.path.exists(logo_png_path):
        try:
            with open(logo_png_path, "rb") as f:
                encoded_png = base64.b64encode(f.read()).decode("utf-8")
            if theme_name == "dark":
                logo_style = f"height: {size}px; width: auto; max-width: 220px; object-fit: contain; flex-shrink: 0; filter: invert(0.92) hue-rotate(185deg) drop-shadow(0 0 12px rgba(99, 102, 241, 0.7));"
            else:
                logo_style = f"height: {size}px; width: auto; max-width: 220px; object-fit: contain; flex-shrink: 0; filter: drop-shadow(0 2px 8px rgba(0, 0, 0, 0.15));"
            logo_html = f'<img src="data:image/png;base64,{encoded_png}" alt="Logo" style="{logo_style}" />'
        except Exception:
            logo_html = ""




            
    if not logo_html and os.path.exists(logo_svg_path):
        try:
            with open(logo_svg_path, "r", encoding="utf-8") as f:
                raw_svg = f.read().strip()
            if theme_name == "dark":
                raw_svg = re.sub(r'fill="#000000"', 'fill="#F8FAFC"', raw_svg)
                raw_svg = re.sub(r'fill="black"', 'fill="#F8FAFC"', raw_svg)
            else:
                raw_svg = re.sub(r'fill="#000000"', 'fill="#0F172A"', raw_svg)
                
            scaled_svg = re.sub(r'width="\d+"', f'width="{size}"', raw_svg, count=1)
            scaled_svg = re.sub(r'height="\d+"', f'height="{size}"', scaled_svg, count=1)
            logo_html = f'<div style="width: {size}px; height: {size}px; display: inline-flex; align-items: center; justify-content: center; flex-shrink: 0; filter: drop-shadow(0 2px 8px rgba(99, 102, 241, 0.4));">{scaled_svg}</div>'
        except Exception:
            logo_html = ""

    if not logo_html:
        logo_html = f'<span style="font-size: 1.8rem; margin-right: 4px;">⚡</span>'
    
    return f"""
    <div style="display: inline-flex; align-items: center; gap: 14px; cursor: pointer; user-select: none; padding: 4px 0;">
        {logo_html}
        <span style="font-family: 'Space Grotesk', sans-serif; font-weight: 800; font-size: 1.6rem; 
                     letter-spacing: -0.04em; margin-left: 6px; white-space: nowrap;
                     background: linear-gradient(135deg, {text}, {primary}); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">DevCore AI</span>
    </div>
    """




def saas_card(
    title: str,
    content: str,
    badge_text: Optional[str] = None,
    badge_type: str = "primary",
    accent_color: Optional[str] = None
) -> str:
    """Generate SaaS-styled container card with optional category badges."""
    accent_style = f"border-top: 6px solid {accent_color};" if accent_color else ""
    badge_html = f'<span class="saas-badge saas-badge-{badge_type}" style="float: right; margin-top: -4px;">{badge_text}</span>' if badge_text else ""
    
    return f"""
    <div class="saas-card" style="{accent_style}">
        {badge_html}
        <h3 style="margin-top: 0; margin-bottom: 12px; font-size: 1.25rem; color: var(--text-color); font-family: 'Space Grotesk', sans-serif; font-weight: 700;">{title}</h3>
        <div style="color: var(--text-secondary); font-size: 0.95rem; line-height: 1.6; margin-bottom: 0;">{content}</div>
    </div>
    """

def glass_card(title: str, content: str) -> str:
    """Generate premium glassmorphism dark-styled highlight container card."""
    return f"""
    <div class="glass-card">
        <h3 style="margin-top: 0; margin-bottom: 12px; color: #FFFFFF; font-size: 1.25rem; font-family: 'Space Grotesk', sans-serif; font-weight: 700;">{title}</h3>
        <div style="color: #CBD5E1; font-size: 0.95rem; line-height: 1.6; margin-bottom: 0;">{content}</div>
    </div>
    """

def metric_card(label: str, value: str, subtitle: Optional[str] = None, icon_name: Optional[str] = None) -> str:
    """Generate SaaS dashboard metric visualization widget."""
    icon_html = get_lucide_svg(icon_name, size=20, color="var(--primary-color)") if icon_name else ""
    sub_html = f'<div style="font-size: 0.8rem; color: var(--text-secondary); margin-top: 8px; font-weight: 600; letter-spacing: 0.01em;">{subtitle}</div>' if subtitle else ""
    
    return f"""
    <div class="saas-card" style="padding: 20px; margin-bottom: 0; display: flex; flex-direction: column; justify-content: space-between; height: 100%;">
        <div>
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                <span style="font-size: 0.8rem; font-weight: 700; text-transform: uppercase; color: var(--text-secondary); letter-spacing: 0.06em;">{label}</span>
                <div style="background-color: var(--hover-bg); padding: 6px; border-radius: 8px; border: 2px solid var(--border-color); display: flex; align-items: center; justify-content: center;">
                    {icon_html}
                </div>
            </div>
            <div style="font-size: 1.9rem; font-weight: 800; color: var(--text-color); line-height: 1.1; font-family: 'Space Grotesk', sans-serif;">{value}</div>
        </div>
        {sub_html}
    </div>
    """

def agent_status_card(role_name: str, status: str, execution_time: Optional[float] = None, active: bool = False) -> str:
    """Generate agent member status card with hover animation properties."""
    border_style = "border-color: var(--primary-color); box-shadow: 6px 6px 0px 0px var(--primary-color);" if active else ""
    pulse_style = "animation: pulse 1.8s infinite;" if status == "running" else ""
    
    status_badge_type = "success" if status == "completed" else ("primary" if status == "running" else "secondary")
    status_label = "Thinking" if status == "running" else status.capitalize()
    
    exec_html = f'<div style="font-size: 0.8rem; color: var(--text-secondary); margin-top: 8px; font-weight: 600; font-family: \'Space Grotesk\', sans-serif;">Duration: {execution_time}s</div>' if execution_time else ""
    
    return f"""
    <div class="saas-card" style="padding: 16px; margin-bottom: 12px; {border_style} {pulse_style}">
        <div style="display: flex; align-items: center; justify-content: space-between;">
            <span style="font-weight: 800; font-size: 1rem; color: var(--text-color); font-family: 'Space Grotesk', sans-serif;">{role_name}</span>
            <span class="saas-badge saas-badge-{status_badge_type}" style="font-size: 0.65rem; padding: 2px 8px; border-radius: 4px;">{status_label}</span>
        </div>
        {exec_html}
    </div>
    """

def timeline_widget(events: List[Tuple[str, str, str, bool]]) -> str:
    """Generate professional vertical activity timeline."""
    items_html = ""
    for title, desc, time_lbl, active in events:
        active_class = "active" if active else ""
        items_html += f"""
        <div class="timeline-item">
            <div class="timeline-badge {active_class}"></div>
            <div style="font-size: 0.8rem; color: var(--text-secondary); font-weight: 600; font-family: 'Space Grotesk', sans-serif;">{time_lbl}</div>
            <strong style="font-size: 1.05rem; color: var(--text-color); display: block; margin-top: 3px; font-family: 'Space Grotesk', sans-serif;">{title}</strong>
            <p style="font-size: 0.9rem; color: var(--text-secondary); margin: 6px 0 20px 0; line-height: 1.5;">{desc}</p>
        </div>
        """
        
    return f"""
    <div class="timeline-container">
        {items_html}
    </div>
    """

def horizontal_pipeline_widget(active_role: Optional[str] = None) -> str:
    """Generate a premium horizontal animated workflow pipeline matching active agent state."""
    roles = [
        ("ceo", "CEO"),
        ("business_analyst", "Analyst"),
        ("project_manager", "PM"),
        ("architect", "Arch"),
        ("ui_ux", "UI/UX"),
        ("frontend", "FE"),
        ("backend", "BE"),
        ("database", "DB"),
        ("security", "Sec"),
        ("devops", "DevOps"),
        ("qa", "QA"),
        ("documentation", "Docs"),
        ("reviewer", "Review")
    ]
    
    active_idx = -1
    if active_role:
        active_role_clean = active_role.lower().strip()
        for idx, (r, _) in enumerate(roles):
            if r == active_role_clean:
                active_idx = idx
                break
                
    nodes_html = ""
    for idx, (r, label) in enumerate(roles):
        if idx < active_idx:
            state_class = "saas-badge saas-badge-success"
            border_override = "border-color: var(--success-color); background-color: rgba(16, 185, 129, 0.1);"
        elif idx == active_idx:
            state_class = "saas-badge saas-badge-primary"
            border_override = "border-color: var(--primary-color); background-color: rgba(79, 70, 229, 0.1); box-shadow: 0 0 12px rgba(79, 70, 229, 0.35); animation: pulse 1.5s infinite;"
        else:
            state_class = "saas-badge saas-badge-secondary"
            border_override = "border-color: var(--border-color); background-color: var(--card-bg); opacity: 0.65;"
            
        nodes_html += f"""
        <div style="display: flex; align-items: center; gap: 4px;">
            <span class="{state_class}" style="padding: 6px 12px; border-radius: 8px; font-size: 0.75rem; {border_override}">{label}</span>
        </div>
        """
        
        if idx < len(roles) - 1:
            arrow_color = "var(--primary-color)" if idx == active_idx else ("var(--success-color)" if idx < active_idx else "var(--border-color)")
            nodes_html += f"""
            <span style="color: {arrow_color}; font-weight: 800; font-size: 1.1rem; margin: 0 4px;">&rarr;</span>
            """
            
    return f"""
    <div class="saas-card" style="padding: 20px; overflow-x: auto; margin-bottom: 24px; border-color: var(--primary-color); box-shadow: var(--shadow-soft);">
        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 16px;">
            <span style="font-size: 0.8rem; font-weight: 700; text-transform: uppercase; color: var(--text-secondary); letter-spacing: 0.06em;">Workforce Pipeline Progression</span>
            <span class="saas-badge saas-badge-primary" style="font-size: 0.7rem; padding: 3px 10px;">Active Planning Session</span>
        </div>
        <div style="display: flex; align-items: center; gap: 4px; min-width: 900px; padding: 6px 0;">
            {nodes_html}
        </div>
    </div>
    """

def render_neural_network_svg(active_role: Optional[str] = None) -> str:
    """Generate high-fidelity animated SVG network mapping the 13 collaborating AI agents."""
    agents = [
        {"id": "ceo", "label": "CEO", "x": 250, "y": 30},
        {"id": "business_analyst", "label": "Analyst", "x": 80, "y": 110},
        {"id": "project_manager", "label": "PM", "x": 190, "y": 110},
        {"id": "architect", "label": "Architect", "x": 310, "y": 110},
        {"id": "ui_ux", "label": "UI/UX", "x": 420, "y": 110},
        {"id": "frontend", "label": "Frontend", "x": 60, "y": 200},
        {"id": "backend", "label": "Backend", "x": 180, "y": 200},
        {"id": "database", "label": "Database", "x": 320, "y": 200},
        {"id": "security", "label": "Security", "x": 440, "y": 200},
        {"id": "devops", "label": "DevOps", "x": 80, "y": 290},
        {"id": "qa", "label": "QA", "x": 190, "y": 290},
        {"id": "documentation", "label": "Docs", "x": 310, "y": 290},
        {"id": "reviewer", "label": "Reviewer", "x": 420, "y": 290}
    ]
    
    # Establish links between agents to draw connection lines
    links = [
        ("ceo", "business_analyst"), ("ceo", "project_manager"), ("ceo", "architect"), ("ceo", "ui_ux"),
        ("business_analyst", "frontend"), ("project_manager", "frontend"), ("architect", "backend"), ("ui_ux", "frontend"),
        ("frontend", "backend"), ("backend", "database"), ("database", "security"),
        ("database", "devops"), ("security", "qa"), ("devops", "qa"), ("qa", "documentation"),
        ("documentation", "reviewer"), ("reviewer", "ceo")
    ]
    
    # Active index for state evaluation
    active_idx = -1
    if active_role:
        active_role_clean = active_role.lower().strip()
        for idx, a in enumerate(agents):
            if a["id"] == active_role_clean:
                active_idx = idx
                break
                
    # Build connection lines
    lines_svg = ""
    for start_id, end_id in links:
        start_node = next(a for a in agents if a["id"] == start_id)
        end_node = next(a for a in agents if a["id"] == end_id)
        
        # Determine status color of the link
        is_completed = False
        is_active = False
        
        start_idx = next(i for i, a in enumerate(agents) if a["id"] == start_id)
        end_idx = next(i for i, a in enumerate(agents) if a["id"] == end_id)
        
        if active_idx != -1:
            if start_idx < active_idx and end_idx <= active_idx:
                is_completed = True
            elif start_idx == active_idx or end_idx == active_idx:
                is_active = True
                
        stroke_color = "var(--success-color)" if is_completed else ("var(--primary-color)" if is_active else "rgba(148, 163, 184, 0.45)")
        stroke_dash = "5 5" if not is_completed else "none"
        animation_class = 'class="pulse-line"' if is_active else ""
        
        lines_svg += f"""
        <line x1="{start_node['x']}" y1="{start_node['y']}" x2="{end_node['x']}" y2="{end_node['y']}" 
              stroke="{stroke_color}" stroke-width="2.5" stroke-dasharray="{stroke_dash}" {animation_class} />
        """
        
    # Build nodes
    nodes_svg = ""
    for idx, a in enumerate(agents):
        state = "completed" if idx < active_idx else ("running" if idx == active_idx else "pending")
        
        # Color mapping with high contrast in light & dark themes
        if state == "completed":
            node_color = "var(--success-color)"
            border_color = "var(--border-color)"
            text_color = "#FFFFFF"
        elif state == "running":
            node_color = "var(--primary-color)"
            border_color = "var(--border-color)"
            text_color = "#FFFFFF"
        else:
            node_color = "var(--card-bg)"
            border_color = "var(--border-color)"
            text_color = "var(--text-color)"
            
        glow_svg = ""
        if state == "running":
            glow_svg = f'<circle cx="{a["x"]}" cy="{a["y"]}" r="30" fill="none" stroke="var(--primary-color)" stroke-width="3" class="pulse-glow"/>'
            
        nodes_svg += f"""
        <g style="cursor: pointer;">
            {glow_svg}
            <circle cx="{a['x']}" cy="{a['y']}" r="21" fill="{node_color}" stroke="{border_color}" stroke-width="2.5"/>
            <text x="{a['x']}" y="{a['y']}" dy="4" font-family="'Space Grotesk', sans-serif" font-weight="800" font-size="9" fill="{text_color}" text-anchor="middle">{a['label']}</text>
        </g>
        """
        
    return f"""
    <div style="width: 100%; display: flex; align-items: center; justify-content: center; padding: 10px 0;">
        <svg width="100%" height="280" viewBox="0 0 500 330" fill="none" xmlns="http://www.w3.org/2000/svg" style="overflow: visible;">
            <defs>
                <style>
                .pulse-glow {{
                    transform-origin: center;
                    animation: circlePulse 2s infinite ease-in-out;
                }}
                .pulse-line {{
                    stroke-dasharray: 8 8;
                    animation: lineMove 1.5s linear infinite;
                }}
                @keyframes circlePulse {{
                    0% {{ r: 21; opacity: 1; }}
                    100% {{ r: 35; opacity: 0; }}
                }}
                @keyframes lineMove {{
                    from {{ stroke-dashoffset: 16; }}
                    to {{ stroke-dashoffset: 0; }}
                }}
                </style>
            </defs>
            {lines_svg}
            {nodes_svg}
        </svg>
    </div>
    """
