from . import StyleProfile


GENERIC_STYLE = StyleProfile(
    id="generic",
    name="Generic",
    description=(
        "A neutral default illustration style with minimal imposed "
        "art-direction. Preserve the content plan and allow the renderer "
        "to make reasonable visual decisions."
    ),

    composition_principles=[],
    scale_principles=[],
    cropping_principles=[],
    perspective_principles=[],
    human_principles=[],
    scene_density_principles=[],
    color_principles=[],
    shape_principles=[],
    rendering_principles=[],
)