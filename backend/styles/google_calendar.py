from . import StyleProfile


GOOGLE_CALENDAR_STYLE = StyleProfile(
    id="google_calendar",
    name="Google Calendar",
    description=(
        "A playful, simplified, low-realism graphic illustration language "
        "derived from the studied Google Calendar reference corpus. The style "
        "uses clear graphic organization, selective simplification, flat color, "
        "flexible scale, compressed or stylized space, and economical detail. "
        "These principles define stable visual grammar; scene-specific choices "
        "such as the exact composition, viewpoint, crop, depth strategy, scale "
        "relationship, environment treatment, and representation concept remain "
        "the responsibility of the Art Director."
    ),

    # ---------------------------------------------------------
    # Composition
    # ---------------------------------------------------------

    composition_principles=[
        (
            "Prioritize immediate semantic readability over literal "
            "reconstruction of the full real-world event."
        ),
        (
            "Build the illustration from a limited number of clear graphic "
            "masses rather than many equally important details."
        ),
        (
            "Establish either a deliberate visual hierarchy or a deliberate "
            "distributed rhythm. Do not force every scene to contain one "
            "dominant central object when recognition is naturally distributed "
            "across several elements."
        ),
        (
            "Use negative space deliberately so important content remains easy "
            "to read and the composition does not feel unnecessarily crowded."
        ),
        (
            "Negative space may participate actively in balance, isolation, "
            "directional flow, or emphasis rather than functioning merely as "
            "unused background."
        ),
        (
            "Asymmetric balance is allowed and often useful. Visual balance "
            "does not require centered, mirrored, or evenly distributed "
            "placement."
        ),
        (
            "Favor a designed graphic arrangement over an exhaustive inventory "
            "of everything that might exist in the real-world scene."
        ),
    ],

    # ---------------------------------------------------------
    # Scale
    # ---------------------------------------------------------

    scale_principles=[
        (
            "Naturalistic scale is not mandatory. Relative scale may be "
            "adjusted when doing so improves recognition, hierarchy, framing, "
            "spatial clarity, or visual interest."
        ),
        (
            "Scale may remain naturalistic or may derive from semantic "
            "exaggeration, framing, perspective, visual equivalence, or "
            "deliberate compositional variation."
        ),
        (
            "Normally unequal objects may receive similar visual prominence "
            "when distributed recognition, rhythm, or conceptual grouping "
            "benefits from it."
        ),
        (
            "An important object may become unusually large when its prominence "
            "is part of a coherent visual idea rather than an arbitrary stylistic "
            "effect."
        ),
        (
            "Do not exaggerate or distort scale merely because the style permits "
            "it. Scale changes should support the chosen presentation concept."
        ),
    ],

    # ---------------------------------------------------------
    # Cropping
    # ---------------------------------------------------------

    cropping_principles=[
        (
            "Objects, people, and environmental forms may continue beyond the "
            "frame when cropping strengthens composition, hierarchy, motion, "
            "or the sense of a larger surrounding scene."
        ),
        (
            "Strong or very strong cropping is acceptable when a partial "
            "person, object, or interaction communicates the concept more "
            "efficiently than showing the complete form."
        ),
        (
            "A crop may deliberately isolate the most diagnostic region of a "
            "subject or interaction rather than treating complete visibility as "
            "a default requirement."
        ),
        (
            "Cropping should preserve the diagnostic parts required for "
            "recognition and should not obscure the relationship that makes the "
            "scene understandable."
        ),
        (
            "Edge continuation should feel intentional. Forms crossing the "
            "frame should contribute to composition, scale, movement, or "
            "context rather than appear accidentally cut off."
        ),
    ],

    # ---------------------------------------------------------
    # Space and depth
    # ---------------------------------------------------------

    spatial_principles=[
        (
            "Favor visually simplified space. A scene may be near-flat, "
            "shallow, layered, or perspective-driven according to what best "
            "supports the concept; realistic three-dimensional reconstruction "
            "is not required."
        ),
        (
            "Depth may be communicated through overlap, occlusion, relative "
            "scale, placement, foreground-background ordering, and selective "
            "recession rather than through complete realistic spatial modeling."
        ),
        (
            "Compressed or nonliteral spatial relationships are acceptable "
            "when they improve recognition, hierarchy, or graphic organization."
        ),
        (
            "Objects may share a simplified baseline, occupy a shallow "
            "conceptual field, or overlap in ways that function graphically "
            "rather than physically."
        ),
        (
            "Use only as much spatial complexity as the scene needs. Do not add "
            "extra depth, planes, or environmental content merely to make the "
            "illustration feel more three-dimensional."
        ),
    ],

    # ---------------------------------------------------------
    # Perspective
    # ---------------------------------------------------------

    perspective_principles=[
        (
            "Perspective may be absent, minimal, functionally simplified, or "
            "strongly stylized depending on the scene."
        ),
        (
            "When perspective is used, preserve clear directional geometry and "
            "near-far relationships without requiring photorealistic camera or "
            "architectural accuracy."
        ),
        (
            "Perspective may work together with relative scale, cropping, and "
            "foreground-background placement as part of a larger graphic idea."
        ),
        (
            "Do not introduce perspective merely to create realism when a flat "
            "or shallow graphic organization communicates the concept more "
            "effectively."
        ),
    ],

    # ---------------------------------------------------------
    # Environment
    # ---------------------------------------------------------

    environment_principles=[
        (
            "Environmental context may be omitted, abstracted, reduced to a "
            "small diagnostic fragment, simplified into a few recognizable cues, "
            "or made prominent when the environment itself carries meaning."
        ),
        (
            "Do not reconstruct a complete literal location when a smaller "
            "amount of contextual information communicates the setting clearly."
        ),
        (
            "Backgrounds may function as quiet areas of flat or restrained color "
            "rather than fully described physical spaces."
        ),
        (
            "A partial environmental element, such as a shelf, surface, lane, "
            "wall, or architectural fragment, may be sufficient to establish "
            "context."
        ),
        (
            "When the environment is semantically important, it may become a "
            "major graphic structure of the composition rather than merely "
            "background scenery."
        ),
        (
            "Environmental detail should remain subordinate when recognition is "
            "carried primarily by a person, object, or interaction."
        ),
    ],

    # ---------------------------------------------------------
    # Humans
    # ---------------------------------------------------------

    human_principles=[
        (
            "Human figures should remain simplified and graphic rather than "
            "anatomically or materially realistic."
        ),
        (
            "Faces should remain highly simplified, but visible facial features"
            "should not be omitted indiscriminately. When aface is shown from the front"
            "or the side where the eyes and mouth would naturally be visible, include such"
            "features as small, simple graphic marks."
        ),
        (
            "Full-body depiction is not required. People may appear as complete "
            "figures, cropped figures, partial bodies, torsos, hands, arms, or "
            "other diagnostic body regions when that is sufficient for the "
            "scene."
        ),
        (
            "Preserve readable silhouettes, gestures, poses, and human-object "
            "contacts even when anatomy is strongly simplified."
        ),
        (
            "Human staging should communicate the important action or "
            "relationship economically rather than displaying more of the body "
            "than the scene requires."
        ),
        (
            "Anonymous figures may have concrete and naturally varied visible "
            "traits. Do not make them featureless, mannequin-like, or "
            "artificially identical merely because their identities are "
            "unspecified."
        ),
        (
            "For identified people, preserve known information and do not "
            "invent unknown identity-specific characteristics as factual visual "
            "claims."
        ),
    ],

    # ---------------------------------------------------------
    # Motion
    # ---------------------------------------------------------

    motion_principles=[
        (
            "Communicate movement primarily through pose, gesture, body lean, "
            "object orientation, overlap, scatter, repetition, directional "
            "forms, and spatial relationships."
        ),
        (
            "The arrangement of surrounding objects may communicate the result "
            "or force of an action even when the moving subject itself is "
            "visually simple."
        ),
        (
            "Motion lines or other explicit graphic motion cues may be used when "
            "they improve clarity, but they are not required for movement to read."
        ),
        (
            "Avoid realistic motion blur as the default method for communicating "
            "movement."
        ),
        (
            "Do not artificially add movement to a scene whose visual idea is "
            "naturally static."
        ),
    ],

    # ---------------------------------------------------------
    # Scene density and detail distribution
    # ---------------------------------------------------------

    scene_density_principles=[
        (
            "Include only elements that contribute to recognition, useful "
            "context, atmosphere, interaction, or compositional balance."
        ),
        (
            "Avoid filling empty space with semantically unnecessary objects."
        ),
        (
            "Supporting context should generally remain visually quieter than "
            "the primary recognition structure."
        ),
        (
            "Detail may be strongly concentrated in recognition-critical "
            "regions while large supporting areas remain intentionally sparse."
        ),
        (
            "Tertiary objects and environmental forms may be simplified more "
            "aggressively than primary semantic content."
        ),
        (
            "Sparse scenes and more distributed compositions are both valid. "
            "Density should remain deliberate rather than becoming either "
            "accidentally empty or uniformly cluttered."
        ),
        (
            "Overall, the scene must not be too full or visually complex."
        )
    ],

    # ---------------------------------------------------------
    # Color
    # ---------------------------------------------------------

    color_principles=[
        (
            "Favor clean areas of solid color over gradients, realistic material "
            "variation, or continuous tonal modeling."
            "Avoid excessive tonal variation within a single form when a simpler "
            "flat treatment communicates its structure clearly."
        ),
        (
            "Use color primarily to separate major forms, establish grouping, "
            "support hierarchy, and reinforce the graphic organization of the "
            "scene."
        ),
        (
            "Color may be stylized or nonliteral. Physical material colors do "
            "not need to be reproduced realistically when a cleaner graphic "
            "palette improves the illustration."
        ),
        (
            "Large quiet background fields may use restrained color while focal "
            "content receives stronger contrast or saturation."
        ),
        (
            "Repeated or related colors may visually connect separate objects "
            "and help unify a distributed composition."
        ),
        (
            "Use a coherent color palette with a small number of dominant color "
            "families. Additional colors may appear for natural variation and detail."
        ),
        (
            "Be explorative with the color palettes, and explore different atmospheric"
            "background color."
        )
    ],

    # ---------------------------------------------------------
    # Shape language
    # ---------------------------------------------------------

    shape_principles=[
        (
            "Construct subjects from simplified geometric and organic shapes "
            "while retaining the diagnostic features required for recognition."
        ),
        (
            "Favor large, readable silhouettes and clear shape relationships "
            "before introducing small internal details."
        ),
        (
            "Simplification should remove unnecessary detail without erasing the "
            "characteristic structure that makes an object, action, or "
            "interaction recognizable."
        ),
        (
            "Important contacts and overlaps between forms should remain visually "
            "clear even when those forms are highly simplified."
        ),
        (
            "Tertiary forms may use greater geometric simplification than "
            "recognition-critical subjects."
        ),
    ],

    # ---------------------------------------------------------
    # Decorative and nonliteral elements
    # ---------------------------------------------------------

    decorative_principles=[
        (
            "Decorative, symbolic, or abstract forms may support rhythm, "
            "atmosphere, movement, semantic association, or compositional "
            "balance."
        ),
        (
            "Decorative elements should remain subordinate to the primary "
            "recognition structure and should not compete with the scene's main "
            "visual idea."
        ),
        (
            "Nonliteral graphic elements may be used when they strengthen the "
            "existing concept without introducing a new unsupported semantic "
            "claim or storyline."
        ),
        (
            "Decorative abstraction may participate in the composition as a "
            "graphic device rather than needing to correspond to a literal "
            "physical object."
        ),
    ],

    # ---------------------------------------------------------
    # Rendering
    # ---------------------------------------------------------

    rendering_principles=[
        (
            "Use a flat graphic illustration treatment with low material realism."
        ),
        (
            "Avoid photorealistic lighting, continuous realistic shading, heavy "
            "texture, glossy materials, and detailed material simulation."
        ),
        (
            "Use little or no realistic cast-shadow modeling. Simple local "
            "grounding or graphic shadow shapes may be used when structurally "
            "helpful, but avoid a physically realistic shadow system."
        ),
        (
            "Avoid gradients unless an exceptional visual or semantic need "
            "clearly justifies one."
        ),
        (
            "Keep texture minimal and subordinate to shape, color, hierarchy, "
            "and semantic readability."
        ),
        (
            "Allocate the most diagnostic specificity to semantically important "
            "content and simplify supporting forms."
        ),
        (
            "Treat the illustration as a designed graphic scene rather than a "
            "miniature realistic photograph."
        ),
        (
            "Overall, the scene may not be dense or too complex."
        ),
    ],
)