from . import StyleProfile


GOOGLE_CALENDAR_STYLE = StyleProfile(
    id="google_calendar",
    name="Google Calendar",
    description=(
        "A playful, simplified, low-realism graphic illustration "
        "language derived from the studied Google Calendar reference "
        "corpus. Stable style principles live here; scene-specific "
        "composition, depth, scale, cropping, and representation "
        "choices should be made from the candidate itself and from "
        "relevant visual precedents."
    ),

    composition_principles=[
        (
            "Prioritize immediate semantic readability over literal "
            "reconstruction of the full real-world event."
        ),
        (
            "Build the illustration from a limited number of clear "
            "graphic masses rather than many equally important details."
        ),
        (
            "Use negative space deliberately so the principal semantic "
            "content remains easy to read in a wide, shallow format."
        ),
        (
            "Asymmetric balance is allowed and often useful; visual "
            "balance does not require centered or mirrored placement."
        ),
    ],

    scale_principles=[
        (
            "Naturalistic scale is not mandatory. Relative scale may be "
            "adjusted when it improves recognition, hierarchy, framing, "
            "or narrative clarity."
        ),
        (
            "Do not exaggerate scale merely because the style permits "
            "it; scale changes should serve the already-planned scene."
        ),
    ],

    cropping_principles=[
        (
            "Objects, people, and environmental forms may continue "
            "beyond the frame when cropping strengthens composition or "
            "makes the scene feel larger than the illustration window."
        ),
        (
            "Cropping should preserve the diagnostic parts needed for "
            "recognition."
        ),
    ],

    perspective_principles=[
        (
            "Use simplified spatial construction rather than strict "
            "photorealistic perspective."
        ),
        (
            "Choose or preserve the viewpoint that makes the candidate's "
            "important objects and actions easiest to recognize."
        ),
        (
            "Depth may be communicated through overlap, relative scale, "
            "placement, and simplified spatial layers without requiring "
            "realistic perspective construction."
        ),
    ],

    human_principles=[
        (
            "Human figures should remain simplified and graphic rather "
            "than anatomically or materially realistic."
        ),
        (
            "Faces may use minimal features when facial information is "
            "not semantically important."
        ),
        (
            "Anonymous figures may have concrete, varied visible traits; "
            "do not make them featureless merely because their identity "
            "is unspecified."
        ),
        (
            "For identified people, preserve known information and do "
            "not invent unknown identity-specific traits."
        ),
    ],

    scene_density_principles=[
        (
            "Include only elements that contribute to recognition, "
            "narrative context, atmosphere, or compositional balance."
        ),
        (
            "Avoid filling empty space with semantically unnecessary "
            "objects."
        ),
        (
            "Supporting context should remain visually quieter than the "
            "primary recognition structure."
        ),
    ],

    color_principles=[
        (
            "Favor clean areas of solid color over gradients, realistic "
            "material variation, or continuous tonal modeling."
        ),
        (
            "Use color to separate major forms and support hierarchy "
            "rather than to simulate realistic materials."
        ),
        (
            "When meaningful depth layers exist, deeper or less important "
            "content should generally compete less strongly for attention "
            "than the primary semantic content."
        ),
    ],

    shape_principles=[
        (
            "Construct subjects from simplified geometric and organic "
            "shapes while retaining the diagnostic features necessary "
            "for recognition."
        ),
        (
            "Simplification should remove unnecessary detail, not erase "
            "the characteristic structure that makes an object or action "
            "recognizable."
        ),
    ],

    rendering_principles=[
        (
            "Use a flat graphic illustration treatment with low material "
            "realism."
        ),
        (
            "Avoid photorealistic lighting, realistic cast shadows, "
            "heavy texture, and glossy material rendering."
        ),
        (
            "Avoid gradients unless an exceptional semantic need clearly "
            "justifies one."
        ),
        (
            "Allocate the most diagnostic detail to the most semantically "
            "important content and simplify supporting forms."
        ),
        (
            "Treat the illustration as a designed graphic scene rather "
            "than a miniature realistic photograph."
        ),
    ],
)
