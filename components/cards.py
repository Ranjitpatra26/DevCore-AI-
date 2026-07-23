from typing import Optional

def neobrutalist_card(
    title: str,
    content: str,
    accent_color: str = "#6366F1",
    bg_color: str = "var(--card-bg)",
    badge_text: Optional[str] = None,
    badge_type: str = "primary"
) -> str:
    """Generate Neo-Brutalist CSS styled HTML card container dynamically matching Light/Dark themes."""
    badge_html = ""
    if badge_text:
        badge_html = f'<span class="nb-badge nb-badge-{badge_type}" style="float: right; margin-top: -2px;">{badge_text}</span>'
        
    return f"""
    <div class="nb-card" style="border-top: 8px solid {accent_color}; background-color: {bg_color};">
        {badge_html}
        <h3 style="margin-top: 0; margin-bottom: 12px; font-size: 1.35rem; color: var(--text-color); font-family: 'Space Grotesk', sans-serif; font-weight: 700;">{title}</h3>
        <div style="color: var(--text-secondary); line-height: 1.6; font-size: 0.95rem;">{content}</div>
    </div>
    """

def neobrutalist_badge(text: str, badge_type: str = "primary") -> str:
    """Generate inline badge element."""
    return f'<span class="nb-badge nb-badge-{badge_type}">{text}</span>'

def neobrutalist_progress(percentage: int, label: str) -> str:
    """Generate custom visual progress bar component."""
    return f"""
    <div style="margin-bottom: 20px;">
        <div style="display: flex; justify-content: space-between; font-weight: 700; margin-bottom: 8px; font-size: 0.9rem; color: var(--text-color); font-family: 'Space Grotesk', sans-serif;">
            <span>{label}</span>
            <span>{percentage}%</span>
        </div>
        <div class="nb-progress-container">
            <div class="nb-progress-fill" style="width: {percentage}%;"></div>
            <div class="nb-progress-text">{percentage}%</div>
        </div>
    </div>
    """

def neobrutalist_stat(
    title: str,
    value: str,
    subtitle: Optional[str] = None,
    accent: str = "#FBBF24"
) -> str:
    """Generate key metric box with correct text color variables for accessibility."""
    sub_html = f'<div style="font-size: 0.82rem; color: var(--text-secondary); margin-top: 6px; font-weight: 600;">{subtitle}</div>' if subtitle else ""
    return f"""
    <div class="nb-card" style="border-left: 8px solid {accent}; padding: 20px;">
        <div style="font-size: 0.8rem; font-weight: 700; text-transform: uppercase; color: var(--text-secondary); letter-spacing: 0.06em;">{title}</div>
        <div style="font-size: 2.2rem; font-weight: 800; color: var(--text-color); margin-top: 10px; line-height: 1; font-family: 'Space Grotesk', sans-serif;">{value}</div>
        {sub_html}
    </div>
    """

def agent_avatar_card(
    role_name: str,
    status: str,
    execution_time: Optional[float] = None,
    active: bool = False
) -> str:
    """Generate agent member status card for dashboard & workspace views with theme borders and shadows."""
    border_color = "var(--primary-color)" if active else "var(--border-color)"
    shadow_offset = "6px 6px" if active else "4px 4px"
    status_badge_type = "success" if status == "completed" else ("primary" if status == "running" else "secondary")
    status_label = "Active" if status == "running" else status.capitalize()
    
    time_html = f'<div style="font-size: 0.8rem; font-weight: 600; color: var(--text-secondary); margin-top: 6px; font-family: \'Space Grotesk\', sans-serif;">Exec: {execution_time}s</div>' if execution_time else ""
    
    return f"""
    <div class="saas-card" style="border: 3px solid {border_color}; margin-bottom: 16px; padding: 16px;
                box-shadow: {shadow_offset} 0px 0px var(--border-color);
                transform: {'translate(-2px, -2px)' if active else 'none'};">
        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px;">
            <span style="font-weight: 800; font-size: 1.05rem; color: var(--text-color); font-family: 'Space Grotesk', sans-serif;">{role_name}</span>
            <span class="nb-badge nb-badge-{status_badge_type}" style="font-size: 0.7rem; padding: 2px 8px;">{status_label}</span>
        </div>
        {time_html}
    </div>
    """
