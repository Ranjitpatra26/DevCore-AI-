from typing import Dict

# DevCore AI - Neo-Brutalist Stationery Design System Tokens

LIGHT_THEME: Dict[str, str] = {
    "bg_color": "#EFE9DB",          # Warm Craft Paper Cream Background
    "bg_gradient": "linear-gradient(180deg, #EFE9DB 0%, #E8E2D3 100%)",
    "card_bg": "#FAF5EB",            # Soft Ivory Card
    "card_border": "#1A2238",        # Heavy Slate Charcoal Border
    "glass_highlight": "rgba(255, 255, 255, 0.9)",
    "border_color": "#1A2238",       # Heavy Neo-Brutalist Outline
    "primary_color": "#6366F1",    # Electric Indigo Accent
    "secondary_color": "#06B6D4",  # Cyan Accent
    "accent_color": "#F59E0B",     # Warm Amber
    "hover_bg": "#EAE3D2",
    "text_color": "#1A2238",       # Bold Black Charcoal Text
    "text_secondary": "#334155",   # Medium Charcoal Text
    "muted_color": "#64748B",
    "success_color": "#10B981",    # Emerald
    "danger_color": "#EF4444",     # Red
    "warning_color": "#F59E0B",
    "shadow_soft": "5px 5px 0px 0px #1A2238",
    "shadow_hover": "9px 9px 0px 0px #6366F1",
    "ai_team_gradient": "linear-gradient(120deg, #F43F5E 0%, #8B5CF6 25%, #06B6D4 50%, #10B981 75%, #F43F5E 100%)",
    "chat_terminal_gradient": "linear-gradient(120deg, #0284C7 0%, #2563EB 25%, #7C3AED 50%, #EC4899 75%, #0284C7 100%)",
}

DARK_THEME: Dict[str, str] = {
    "bg_color": "#0B0F19",          # Deep Midnight Slate Background
    "bg_gradient": "linear-gradient(180deg, #0B0F19 0%, #060912 100%)",
    "card_bg": "#111827",            # Dark Charcoal Card
    "card_border": "#374151",
    "glass_highlight": "rgba(255, 255, 255, 0.1)",
    "border_color": "#374151",
    "primary_color": "#6366F1",
    "secondary_color": "#06B6D4",
    "accent_color": "#F43F5E",
    "hover_bg": "#1E293B",
    "text_color": "#F9FAFB",       # Crisp White Text
    "text_secondary": "#9CA3AF",
    "muted_color": "#6B7280",
    "success_color": "#34D399",
    "danger_color": "#FB7185",
    "warning_color": "#FBBF24",
    "shadow_soft": "5px 5px 0px 0px #000000",
    "shadow_hover": "9px 9px 0px 0px #6366F1",
    "ai_team_gradient": "linear-gradient(120deg, #FF3366 0%, #A855F7 25%, #38BDF8 50%, #34D399 75%, #FF3366 100%)",
    "chat_terminal_gradient": "linear-gradient(120deg, #38BDF8 0%, #60A5FA 25%, #A855F7 50%, #F472B6 75%, #38BDF8 100%)",
}


def get_theme_colors(theme_name: str) -> Dict[str, str]:
    """Return dictionary of theme colors matching light or dark selection."""
    return LIGHT_THEME if theme_name.lower() == "light" else DARK_THEME

def get_theme_tokens(theme_name: str) -> Dict[str, str]:
    """Return dictionary of design tokens for the specified theme."""
    return get_theme_colors(theme_name)
