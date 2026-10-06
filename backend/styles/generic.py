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

    spatial_principles=[],
    perspective_principles=[],
    environment_principles=[],

    human_principles=[],
    motion_principles=[],

    scene_density_principles=[],
    color_principles=[],
    shape_principles=[],
    decorative_principles=[],

    rendering_principles=[],
)