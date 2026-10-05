"""Read Omarchy color data as data, retaining a dark, contrast-checked palette."""
from pathlib import Path
import re
import tomllib

FALLBACK = {"background": "#0f0508", "dark_background": "#0a0305", "lighter_background": "#1d0a0f",
            "accent": "#c5003c", "light_foreground": "#e4356a", "bright_foreground": "#ff4d70",
            "yellow": "#f3e600", "cyan": "#55ead4", "muted": "#880425"}


def rgb(color):
    return tuple(int(color[i:i+2], 16) / 255 for i in (1, 3, 5))


def luminance(color):
    values = [v / 12.92 if v <= .04045 else ((v + .055) / 1.055) ** 2.4 for v in rgb(color)]
    return sum(a * b for a, b in zip(values, (.2126, .7152, .0722)))


def contrast(a, b):
    l1, l2 = sorted((luminance(a), luminance(b)), reverse=True)
    return (l1 + .05) / (l2 + .05)


def read_palette(root=None):
    home = Path(root) if root else Path.home()
    path = home / ".local/state/omarchy/current/theme/colors.toml"
    palette = dict(FALLBACK)
    name = "Netrunner fallback"
    try:
        data = tomllib.loads(path.read_text())
        if data.get("mode") == "dark":
            for key in palette:
                value = data.get(key, "")
                if isinstance(value, str) and re.fullmatch(r"#[0-9a-fA-F]{6}", value):
                    palette[key] = value
            name = (home / ".local/state/omarchy/current/theme.name").read_text().strip().title()
    except (OSError, ValueError):
        pass
    if max(luminance(palette[k]) for k in ("background", "lighter_background")) > .18:
        palette, name = dict(FALLBACK), "Netrunner fallback"
    # A theme's low-contrast foreground is suitable for linework, not small data labels.
    palette["text"] = "#f3dce3"
    palette["secondary"] = "#c796a6"
    for key in ("text", "secondary", "light_foreground", "bright_foreground"):
        if min(contrast(palette[key], palette[bg]) for bg in ("background", "lighter_background")) < 4.5:
            palette[key] = "#fff0f5"
    palette["button_text"] = "#fff6f9" if contrast("#fff6f9", palette["accent"]) >= 4.5 else "#060102"
    return name, palette


def stylesheet(p):
    return f"""
    window, .background {{ background: {p['background']}; color: {p['text']}; }}
    * {{ font-family: 'Inter', 'Adwaita Sans', sans-serif; font-size: 13px; }}
    .page {{ padding: 22px; }}
    .eyebrow {{ color: {p['light_foreground']}; font-family: monospace; font-size: 10px; letter-spacing: 2px; }}
    .title {{ font-size: 27px; font-weight: 800; letter-spacing: 1px; }}
    .subtitle, .muted {{ color: {p['secondary']}; }}
    .small {{ font-size: 11px; }}
    .mono {{ font-family: monospace; }}
    .status {{ color: {p['light_foreground']}; font-family: monospace; font-size: 11px; }}
    .card {{ background: {p['lighter_background']}; border: 1px solid alpha({p['accent']}, .45); border-radius: 5px; padding: 16px; }}
    .metric {{ font-size: 32px; font-weight: 700; color: {p['bright_foreground']}; font-family: monospace; }}
    .metric-title {{ color: {p['secondary']}; font-size: 10px; letter-spacing: 1px; }}
    .section-title {{ font-size: 15px; font-weight: 700; }}
    .rule {{ min-height: 1px; background: alpha({p['accent']}, .55); }}
    button {{ background: {p['lighter_background']}; color: {p['text']}; border: 1px solid alpha({p['accent']}, .65); border-radius: 4px; padding: 8px 14px; box-shadow: none; }}
    button:hover {{ background: alpha({p['accent']}, .22); }}
    button:focus-visible, entry:focus-within {{ outline: 2px solid {p['bright_foreground']}; outline-offset: 2px; }}
    button.primary {{ background: {p['accent']}; color: {p['button_text']}; font-weight: 700; }}
    button:disabled {{ opacity: .45; }}
    entry, spinbutton, dropdown {{ background: {p['dark_background']}; color: {p['text']}; border: 1px solid alpha({p['accent']}, .40); border-radius: 3px; padding: 3px; }}
    entry {{ min-height: 28px; padding-left: 9px; }}
    popover contents, listview, listbox, row, dialog {{ background: {p['lighter_background']}; color: {p['text']}; }}
    row:selected {{ background: alpha({p['accent']}, .25); }}
    textview, textview text {{ background: {p['dark_background']}; color: {p['text']}; font-family: monospace; font-size: 11px; }}
    headerbar {{ background: {p['background']}; color: {p['text']}; box-shadow: none; min-height: 30px; }}
    headerbar button {{ min-width: 20px; min-height: 20px; padding: 3px; border-color: transparent; }}
    .badge {{ color: {p['light_foreground']}; border: 1px solid alpha({p['accent']}, .5); padding: 5px 8px; border-radius: 3px; font-size: 10px; }}
    .notice {{ color: {p['secondary']}; padding: 10px 12px; border-left: 2px solid {p['accent']}; background: {p['dark_background']}; }}
    """
