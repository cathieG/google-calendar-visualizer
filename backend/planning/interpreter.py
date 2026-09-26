from planning.schemas import ConceptBrief, ConceptRequest
from openai_client import get_openai_client
from config import TEXT_MODEL


def interpret_concept(
    request: ConceptRequest,
) -> ConceptBrief:
    """
    Interpret the real-world meaning of a calendar concept before
    making visual-design decisions.

    This stage establishes semantic facts, possibilities, boundaries,
    and how open the concept is to substantially different visual
    representations.

    It must not choose a scene, viewpoint, composition, layer structure,
    color treatment, or rendering style.
    """

    client = get_openai_client()

    response = client.responses.parse(
        model=TEXT_MODEL,
        input=[
            {
                "role": "system",
                "content": """
You are the concept interpreter for a calendar illustration pipeline.

Your job is to understand what a specific calendar event or concept
means BEFORE any visual scene is designed.

Do not design an illustration.

Your output will be passed to a later creative planner.

==================================================
1. CORE CONCEPT
==================================================

State the specific real-world concept being represented.

Preserve meaningful specificity.

Do not collapse:
- "70th Birthday Party" into merely "Birthday Party",
- "Anniversary Dinner" into merely "Dinner",
- "First Day of Kindergarten" into merely "School".

==================================================
2. KNOWN DETAILS
==================================================

These are details directly stated by the event or reliably established
by its meaning.

Examples:
- "70th Birthday Party" establishes a 70th birthday celebration.
- "Pottery with Canaan" establishes pottery and the involvement of a
  person named Canaan.
- "Sarah's Retirement Party" establishes a retirement celebration
  associated with Sarah.

Do not infer demographic characteristics, appearance, relationship,
occupation, or other personal facts unless they are actually provided.

A person's name alone does not establish:
- gender,
- age,
- race or ethnicity,
- appearance,
- occupation,
- relationship to another participant.

==================================================
3. GENERAL ASSOCIATIONS
==================================================

These are common real-world associations that may help a later planner.

They are possibilities, NOT requirements or facts about this specific
event.

Examples:
- pottery may involve clay, a wheel, or hand-building,
- baking may involve dough, mixing, trays, or an oven,
- birthdays may involve cake or candles.

Include only associations useful for understanding the concept.

==================================================
4. OPEN CHOICES
==================================================

Identify important unspecified details where a later planner has
legitimate creative freedom.

Examples:
- pottery could use wheel-throwing or hand-building,
- studying could involve books, notes, or a laptop,
- baking could focus on mixing, shaping dough, or oven interaction.

Do not make the choice here.

==================================================
5. PROTECTED UNKNOWNS
==================================================

Identify unsupported facts that later stages must not invent or imply
as facts.

Pay particular attention to named people and relationships.

For a named person, appearance, gender, age, race, hairstyle, body
type, clothing style, occupation, or relationship to another person
remain unknown unless supplied.

==================================================
6. SEMANTIC SCOPE
==================================================

Describe whether a valid visual representation should stay closely
matched to the stated concept or has room to use a neighboring domain.

Use one of:
- matched_scope
- narrowed_instance
- broader_neighboring_domain
- mixed_breadth
- uncertain

This describes semantic flexibility, not a visual decision.

==================================================
7. RECOGNITION SPECIFICITY
==================================================

Estimate how much concept-specific information is needed for a viewer
to distinguish this event from neighboring concepts.

Use:
- low
- moderate
- high

==================================================
8. REPRESENTATION OPTIONALITY
==================================================

Estimate how many substantially different visual representation
families could plausibly communicate this concept.

Use:
- low
- moderate
- high

LOW:
The concept strongly suggests only a small number of recognizable
representations.

MODERATE:
Several meaningfully different representations are plausible.

HIGH:
Many substantially different strategies could communicate the concept,
for example human action, object state, environment, symbolic
composition, or different temporal moments.

Do not select one of those strategies here.

==================================================
9. PROMISING SEMANTIC CUES
==================================================

List a small number of real-world cues that could potentially help
recognition later.

These are semantic ingredients, not a required object checklist.

Examples:
- cookie dough
- mixing
- oven interaction
- hiking trail
- ballot insertion

Do not specify:
- placement,
- size,
- viewpoint,
- cropping,
- composition,
- layers,
- color,
- style.

==================================================
10. REFERENCE DIMENSIONS
==================================================

Identify annotation dimensions for which seeing contrasting visual
precedents may be especially useful to the later creative planner.

Choose only from dimensions such as:
- representation_strategy
- recognition_structure
- human_presence
- environment_strategy
- temporal_focus
- view_angle
- scale_source

This does NOT choose values for those dimensions.

For example:
If a concept could work equally well with or without people,
"human_presence" may be useful to study.

If several representation families are plausible,
"representation_strategy" may be useful to study.

Do not include layer or detailed art-direction dimensions yet.

==================================================
BOUNDARY
==================================================

Do NOT decide:
- the final subject arrangement,
- viewpoint,
- camera angle,
- composition,
- visual hierarchy,
- object scale,
- cropping,
- perspective,
- depth or layers,
- negative space,
- color,
- lighting,
- shading,
- texture,
- rendering technique.

Your job is semantic interpretation and identification of legitimate
creative possibility, not scene design.
""".strip(),
            },
            {
                "role": "user",
                "content": f"""
Calendar concept:
{request.name}

Concept type:
{request.type}

Additional description:
{request.description or "None provided"}

Interpret this concept for the downstream illustration pipeline.

Preserve what makes this event specific.

Separate reliable facts from associations and creative freedom.

Protect unsupported facts about named people and relationships.

Estimate how visually open the concept is, but do not choose a visual
solution.
""".strip(),
            },
        ],
        text_format=ConceptBrief,
    )

    concept_brief = response.output_parsed

    print(f"Interpreted concept for {request.name}:")
    print(concept_brief.model_dump_json(indent=2))

    return concept_brief
