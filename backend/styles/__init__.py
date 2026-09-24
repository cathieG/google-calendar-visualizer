from pydantic import BaseModel


class StyleProfile(BaseModel):
    id: str
    name: str

    description: str

    composition_principles: list[str]
    scale_principles: list[str]
    cropping_principles: list[str]
    perspective_principles: list[str]
    human_principles: list[str]
    scene_density_principles: list[str]
    color_principles: list[str]
    shape_principles: list[str]
    rendering_principles: list[str]


def get_style_profile(style_id: str) -> StyleProfile:
    from .generic import GENERIC_STYLE
    from .google_calendar import GOOGLE_CALENDAR_STYLE

    styles = {
        GENERIC_STYLE.id: GENERIC_STYLE,
        GOOGLE_CALENDAR_STYLE.id: GOOGLE_CALENDAR_STYLE,
    }

    if style_id not in styles:
        raise ValueError(
            f"Unknown style '{style_id}'. "
            f"Available styles: {', '.join(styles)}"
        )

    return styles[style_id]