import base64
import json
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel


load_dotenv()

client = OpenAI()


# ---------------------------------------------------------
# Data models
# ---------------------------------------------------------

class ConceptRequest(BaseModel):
    name: str
    type: str
    description: str | None = None


class ConceptContext(BaseModel):
    core_concept: str
    known_details: list[str]
    general_associations: list[str]
    open_choices: list[str]
    protected_unknowns: list[str]


class ScenePlan(BaseModel):
    visual_idea: str
    representation: str

    subject: str
    setting: str
    action: str

    important_objects: list[str]
    accent_detail: str | None

    avoid: list[str]


class ReferenceSelection(BaseModel):
    concepts: list[str]


# ---------------------------------------------------------
# Google Calendar visual references
# ---------------------------------------------------------

REFERENCE_ROOT = Path(__file__).parent / "references"
REFERENCE_DIR = REFERENCE_ROOT / "rendered"
REFERENCE_CATALOG_PATH = REFERENCE_ROOT / "references.json"


def load_visual_references() -> list[tuple[str, str]]:
    """
    Load and validate the Google Calendar visual reference catalog.

    Each catalog entry has the form:

        {
            "concept": "Tennis",
            "file": "img_tennis.png"
        }

    The rest of the planner uses (concept, filename) tuples.
    """

    with REFERENCE_CATALOG_PATH.open(
        "r",
        encoding="utf-8",
    ) as file:
        catalog = json.load(file)

    references = []

    for entry in catalog:
        concept = entry["concept"]
        filename = entry["file"]

        image_path = REFERENCE_DIR / filename

        if not image_path.exists():
            raise FileNotFoundError(
                f"Reference catalog contains '{concept}', "
                f"but its rendered image does not exist: "
                f"{image_path}"
            )

        references.append(
            (concept, filename)
        )

    return references


VISUAL_REFERENCES = load_visual_references()


# ---------------------------------------------------------
# Image helper
# ---------------------------------------------------------

def image_to_data_url(path: Path) -> str:
    """
    Convert a local PNG image into a base64 data URL
    that can be sent to the OpenAI API.
    """

    image_bytes = path.read_bytes()
    encoded = base64.b64encode(image_bytes).decode("utf-8")

    return f"data:image/png;base64,{encoded}"


# ---------------------------------------------------------
# Concept interpreter
# ---------------------------------------------------------

def interpret_concept(
    request: ConceptRequest,
) -> ConceptContext:
    """
    Interpret what a calendar concept means in the real world
    before making any visual-design decisions.

    The interpreter separates:
    - details supported by the event itself,
    - general real-world associations,
    - unspecified details the planner may safely choose,
    - protected information the planner must not invent.
    """

    response = client.responses.parse(
        model="gpt-5.6-luna",
        input=[
            {
                "role": "system",
                "content": """
You are a concept interpreter for a calendar illustration system.

Your job is to understand what a specific calendar event or concept
means in the real world.

Do NOT design an illustration.

Separate your interpretation into four kinds of information:

1. KNOWN DETAILS

These are details that are directly stated by the event or can be
reliably inferred from its meaning.

Examples:
- "70th Birthday Party" specifies a 70th birthday celebration.
- "Pottery with Canaan" specifies pottery and indicates that a person
  named Canaan is associated with the activity.
- "Sarah's Retirement Party" specifies a retirement celebration
  associated with Sarah.

Do not treat demographic characteristics, appearance, relationships,
or other personal attributes as known unless they are actually
provided.

A person's name alone does not establish their gender, age, race,
appearance, occupation, or relationship to another participant.

2. GENERAL ASSOCIATIONS

These are things commonly associated with this kind of real-world
event, activity, place, or occasion.

They are possibilities, not facts about this particular event.

For example:
- pottery commonly involves clay,
- pottery may involve a pottery wheel or hand-building,
- birthday celebrations commonly involve cake and candles,
- retirement parties may involve congratulations, gifts, coworkers,
  food, or decorations.

Only include associations that are genuinely useful for understanding
the concept.

3. OPEN CHOICES

These are relevant details that the event does not specify, but that
a later visual planner may safely choose among when creating one
plausible visual interpretation.

Open choices are areas of legitimate creative freedom.

For example:
- a study session may be represented with a notebook or a laptop,
- pottery may be represented with wheel-throwing or hand-building,
- camping may be represented with one conventional type of temporary
  shelter when the exact shelter is not specified.

Do not make the final visual choice yourself. Identify where the
later planner has safe freedom to choose.

4. PROTECTED UNKNOWNS

These are relevant details that the event does not provide and that
the visual planner must not invent or visually imply as facts.

Pay particular attention to protected information about named people
and relationships.

For example, if an event says "Pottery with Canaan", Canaan's
appearance, gender, age, and relationship to the other participant
remain protected unless additional information is provided.

If an event says "Sarah's Retirement Party", do not infer Sarah's
age, race, appearance, occupation, or the identities of the guests.

The distinction is important: ordinary unspecified visual choices may
belong in open_choices, while identity, relationship, and other
meaningful unsupported facts belong in protected_unknowns.

Pay close attention to details that distinguish a specific concept
from a generic one.

Do not collapse:
- "70th Birthday Party" into merely "Birthday Party",
- "Anniversary Dinner" into merely "Dinner",
- "First Day of Kindergarten" into merely "School".

Do not make decisions about:
- what the final illustration should contain,
- composition,
- layout,
- illustration style,
- colors,
- camera angle,
- rendering technique.

Your job is real-world interpretation, not visual design.
""".strip(),
            },
            {
                "role": "user",
                "content": f"""
Calendar concept: {request.name}
Concept type: {request.type}
Additional description: {request.description or "None provided"}

Interpret this specific concept.

Clearly distinguish:
- what is known,
- what is merely a general association,
- what is unspecified but safe for the visual planner to choose,
- what must remain protected from unsupported invention.

Preserve the details that distinguish this concept from a more
generic version.
""".strip(),
            },
        ],
        text_format=ConceptContext,
    )

    concept_context = response.output_parsed

    print(
        f"Interpreted concept for {request.name}:"
    )
    print(
        concept_context.model_dump_json(indent=2)
    )

    return concept_context


# ---------------------------------------------------------
# Reference selector
# ---------------------------------------------------------

def select_visual_references(
    request: ConceptRequest,
    context: ConceptContext,
) -> list[tuple[str, str]]:
    """
    Choose a small subset of Google Calendar reference illustrations
    that will be useful for planning the new concept.
    """

    available_concepts = [
        concept_name
        for concept_name, _ in VISUAL_REFERENCES
    ]

    response = client.responses.parse(
        model="gpt-5.6-luna",
        input=[
            {
                "role": "system",
                "content": """
You select visual design references for a calendar illustration planner.

You will receive:
1. a new calendar concept,
2. its interpreted real-world context,
3. a list of available reference concepts.

Choose exactly 3 references that would be most useful when deciding
how the new concept should be visually represented.

Do not simply choose the three concepts that are most semantically
similar.

Choose references that together help the visual planner compare
different possible representation strategies.

Prefer a useful combination of:
- semantic relevance,
- analogous activities or events,
- contrasting ways a concept might be represented.

Known details describe this particular event.

General associations describe possibilities, not facts. Do not treat
them as requirements.

Open choices describe unspecified details the visual planner may
safely choose among.

Protected unknowns describe information that must not be assumed.

Return only concepts from the supplied list.
""".strip(),
            },
            {
                "role": "user",
                "content": f"""
New concept: {request.name}
Concept type: {request.type}
Description: {request.description or "None provided"}

Interpreted core concept:
{context.core_concept}

Known details:
{chr(10).join(f"- {item}" for item in context.known_details)}

General associations:
{chr(10).join(f"- {item}" for item in context.general_associations)}

Open choices:
{chr(10).join(f"- {item}" for item in context.open_choices)}

Protected unknowns:
{chr(10).join(f"- {item}" for item in context.protected_unknowns)}

Available reference concepts:
{", ".join(available_concepts)}
""".strip(),
            },
        ],
        text_format=ReferenceSelection,
    )

    selected_names = response.output_parsed.concepts

    selected_references = [
        (concept_name, filename)
        for concept_name, filename in VISUAL_REFERENCES
        if concept_name in selected_names
    ]

    print(
        f"Selected visual references for {request.name}: "
        f"{[name for name, _ in selected_references]}"
    )

    return selected_references


# ---------------------------------------------------------
# Build multimodal reference message
# ---------------------------------------------------------

def build_visual_reference_content(
    references: list[tuple[str, str]],
):
    """
    Build a multimodal message containing the selected Google Calendar
    reference illustrations.

    Each image is labeled with its concept name, but we deliberately
    do not describe what appears inside it. The planner should infer
    Google's representation decisions from the image itself.
    """

    content = [
        {
            "type": "input_text",
            "text": (
                "Below are reference illustrations used by Google Calendar. "
                "Each image is labeled with the concept it represents. "
                "Study what Google chose to depict for each concept. "
                "Focus on representation decisions: which subjects, objects, "
                "people, actions, environments, or small incidental details "
                "were selected, and especially what Google chose to omit. "
                "Do not copy the rendering style."
            ),
        }
    ]

    for concept_name, filename in references:
        image_path = REFERENCE_DIR / filename

        if not image_path.exists():
            raise FileNotFoundError(
                f"Visual reference image not found: {image_path}"
            )

        content.append(
            {
                "type": "input_text",
                "text": f"Reference concept: {concept_name}",
            }
        )

        content.append(
            {
                "type": "input_image",
                "image_url": image_to_data_url(image_path),
            }
        )

    return content


# ---------------------------------------------------------
# Visual planner
# ---------------------------------------------------------

def plan_concept_image(request: ConceptRequest) -> ScenePlan:
    """
    Interpret the concept, select useful visual references,
    and create one selective, creative scene plan for the
    requested calendar concept.
    """

    # Stage 1:
    # Interpret the real-world meaning of the specific concept.
    concept_context = interpret_concept(request)

    # Stage 2:
    # Select useful Google Calendar references using that context.
    selected_references = select_visual_references(
        request,
        concept_context,
    )

    # Stage 3:
    # Give the interpretation and selected reference images
    # to the visual planner.
    #
    # The planner is the main creative decision-maker.
    # It should consider multiple possibilities, select one,
    # and deliberately leave most possible context out.
    response = client.responses.parse(
        model="gpt-5.6-luna",
        input=[
            {
                "role": "system",
                "content": """
You are the creative visual planner for small calendar illustrations.

You are the main visual decision-maker in the pipeline.

Your job is NOT to summarize everything that could occur in the
real-world event.

Your job is to choose ONE strong visual interpretation from many
possible interpretations and turn it into a compact design brief.

Think like a thoughtful illustrator or creative director.

--------------------------------------------------
CORE PLANNING PRINCIPLE
--------------------------------------------------

The concept interpreter may provide many known details and many
general associations.

Treat that information as a pool of possibilities.

Do not attempt to include all of it.

A successful calendar illustration usually communicates one clear
idea with very few elements.

The image should feel selected and designed, not comprehensive.

Before producing your answer, consider several plausible visual
approaches internally.

Then choose only ONE.

Do not return the alternatives.

--------------------------------------------------
RECOGNIZABILITY BEFORE CLEVERNESS
--------------------------------------------------

Creativity is secondary to recognizability.

A clever, symbolic, or metaphorical idea is only useful if a viewer
can still understand the underlying concept without relying on the
event title or written text.

Ask whether the chosen image would still communicate the core event
if it were viewed on its own.

Prefer a familiar but elegant visual cue over an inventive idea that
becomes ambiguous without explanation.

A surprising detail may enrich a clear idea.

It must not replace the clear idea.

--------------------------------------------------
REPRESENTATION STRATEGIES
--------------------------------------------------

Possible representation strategies include:

- activity_scene:
  A person, partial person, or simple human action is central to
  recognizing the concept.

- environment_scene:
  A recognizable place or environment carries the idea.

- object_composition:
  A small arrangement of distinctive objects communicates the concept
  more simply than a complete scene.

- character_activity:
  A character performs a simple recognizable action where showing
  the action adds useful meaning.

- atmosphere_scene:
  A small set of environmental or symbolic elements communicates
  a celebration, holiday, season, or mood.

These are strategies, not rigid categories.

Choose whichever best serves the visual idea.

--------------------------------------------------
VISUAL ECONOMY
--------------------------------------------------

Do not reconstruct the whole real-world event.

Prefer:
- one primary visual idea,
- one clear subject,
- roughly 1-3 essential objects,
- sparse setting information,
- little or no secondary activity.

A specific event can have many valid illustrations.
Your task is to select one of them.

The important_objects field contains only objects explicitly approved
to appear in the image.

Do not fill important_objects with everything commonly associated
with the event.

--------------------------------------------------
SPECIFICITY
--------------------------------------------------

Preserve details that distinguish the requested concept from a more
generic version when those details can be communicated simply.

For example:
- a 70th birthday should not become a generic birthday,
- an anniversary dinner should not become an ordinary dinner,
- the first day of kindergarten should not become generic school.

But specificity does not mean comprehensiveness.

Choose the smallest amount of specificity needed to make the visual
idea meaningful.

--------------------------------------------------
KNOWN, ASSOCIATED, OPEN, AND PROTECTED INFORMATION
--------------------------------------------------

The concept interpretation distinguishes between:
- known details,
- general associations,
- open choices,
- protected unknowns.

KNOWN DETAILS may be relied upon.

GENERAL ASSOCIATIONS are possible sources of inspiration.
They are not requirements.

You may use one or two when they support the chosen visual idea.

OPEN CHOICES are legitimate areas of creative freedom.
You may choose one plausible option when it helps create a clearer
or more effective visual idea. You do not need to exercise every
open choice.

PROTECTED UNKNOWNS are boundaries.
Do not invent them or visually imply them as facts.

This is especially important for named people.

Do not infer or invent a named person's:
- gender,
- age,
- race or ethnicity,
- facial features,
- hair,
- body type,
- clothing style,
- occupation,
- relationship to another participant.

More generally, a participant who is known to be part of the event
does not have to be visually represented.

The ScenePlan should depict a participant only when showing that
participant materially improves recognition of the chosen visual idea.

Do not treat the number of known participants as a requirement for
the number of people shown in the image.

For example, an event involving two people may still be best
represented by:
- one anonymous participant performing the activity,
- partial human features such as hands,
- objects associated with the activity,
- or no people at all.

Semantic participation and visual presence are different things.
Choose visual presence based on what makes the illustration clearest,
simplest, and most effective.

If a person's appearance is a protected unknown, prefer a visual idea
that does not require inventing a specific identity.

If people are not necessary, omit them.

If an activity can be communicated without showing all participants,
you do not need to depict all participants mentioned by the event.

--------------------------------------------------
RELATIONSHIP UNCERTAINTY
--------------------------------------------------

When the relationship between participants is a protected unknown,
do not choose a visual idea that requires close interpersonal interaction.

Avoid visual ideas that rely on:
- two people jointly manipulating the same object,
- physical contact between participants,
- coordinated intimate poses,
- one person guiding another person's body or hands,
- body language that implies romance, family, caretaking, mentorship,
  or another specific relationship,

unless that interaction is directly supported by the event.

Do not attempt to solve this problem only by hiding faces.

Hands, body position, proximity, and shared actions can also imply
relationships.

If the activity can be recognized using:
- one anonymous participant,
- partial human features,
- objects,
- tools,
- or the environment,

prefer that simpler representation.

A participant may be semantically important to the event without
needing to be visually represented.

--------------------------------------------------
CREATIVE ACCENT DETAIL
--------------------------------------------------

You may optionally introduce ONE small incidental visual detail.

The purpose of this detail is to make the illustration feel observed,
specific, charming, playful, or pleasantly surprising.

The accent detail should feel like a small real-life observation:
something plausible, secondary, and visually charming that is not
required to identify the concept.

Invent the detail from the specific situation rather than following
a fixed library of examples.

The accent detail should:
- be plausible in the real-world situation,
- be visually simple,
- remain secondary to the main concept,
- require no unsupported personal information,
- add personality without adding a new storyline.

Do NOT force an accent detail into every illustration.

If there is no genuinely useful detail, set accent_detail to null.

Do not make the accent detail:
- a joke that distracts from the concept,
- a new character,
- a major new event,
- text or signage,
- an unsupported fact about a real person,
- a substitute for a recognizable main visual idea.

--------------------------------------------------
USING GOOGLE CALENDAR REFERENCES
--------------------------------------------------

The reference images are examples of how Google Calendar has made
visual representation choices.

Study them for decisions such as:
- what Google made central,
- what Google omitted,
- when objects were enough,
- when human action was useful,
- when a setting carried the idea,
- how sparse or selective the scene was,
- whether a small incidental detail added personality.

Do not simply copy the subject matter of a reference.

Do not assume the most semantically similar reference should dictate
the representation.

Use the references as design evidence, not templates.

--------------------------------------------------
SCENE PLAN FIELDS
--------------------------------------------------

visual_idea:
A concise description of the ONE visual concept you selected.

It should explain the creative idea behind the illustration rather
than merely repeat the event title.

representation:
The broad representation strategy.

subject:
The primary thing the viewer should notice.

setting:
Only the minimal setting information needed to support the idea.
Use an empty string when a specific setting is unnecessary.

action:
An action occurring within the scene.
Use an empty string when no action is needed.

Do not put composition instructions or drawing instructions here.

important_objects:
Usually 1-3 explicitly approved objects.

These are the essential physical objects that belong in the chosen
visual interpretation.

accent_detail:
At most one optional, subtle incidental detail.
Use null when none improves the idea.

avoid:
A short list of predictable mistakes that would weaken or distort
this particular design.

Use this field to protect the concept from issues such as:
- inventing an unknown person's appearance,
- adding unnecessary people,
- implying an unsupported relationship,
- turning a sparse composition into a crowded scene,
- using written words when visual communication would work better,
- adding generic event clutter that dilutes the chosen idea.

The avoid list should be specific to this design rather than an
exhaustive list of every possible rendering mistake.

Important:
The avoid field cannot rescue a fundamentally poor visual idea.

Do not select a scene whose basic composition already creates an
unsupported implication and then merely write that implication into
the avoid list.

The chosen visual idea itself must respect all known details and
protected unknowns.

--------------------------------------------------
FINAL GOAL
--------------------------------------------------

The goal is NOT:

"What does this kind of event usually contain?"

The goal is:

"What is one simple, recognizable, memorable, visually appealing
way to represent THIS event?"

Choose deliberately.

Be selective.

Leave things out.

Be creative only after the core concept is visually clear.

A small clever detail is welcome when it genuinely improves the idea.

Focus only on WHAT should be depicted.

Do not make decisions about illustration style, colors, lighting,
shading, artistic technique, or final rendering.
""".strip(),
            },

            # Selected actual Google Calendar illustrations
            {
                "role": "user",
                "content": build_visual_reference_content(
                    selected_references
                ),
            },

            # New concept and its interpreted context
            {
                "role": "user",
                "content": f"""
Now create ONE visual plan for a new calendar illustration.

Concept name:
{request.name}

Concept type:
{request.type}

Additional description:
{request.description or "None provided"}

Real-world interpretation:

Core concept:
{concept_context.core_concept}

Known details:
{chr(10).join(f"- {item}" for item in concept_context.known_details)}

General associations:
{chr(10).join(f"- {item}" for item in concept_context.general_associations)}

Open choices:
{chr(10).join(f"- {item}" for item in concept_context.open_choices)}

Protected unknowns:
{chr(10).join(f"- {item}" for item in concept_context.protected_unknowns)}

Use the known details as reliable information.

Treat the general associations as a menu of possibilities rather
than a checklist.

Use the open choices as legitimate creative freedom. You may choose
one plausible option when it improves the visual idea, but you do not
need to use every open choice.

Respect the protected unknowns as hard boundaries.

Consider multiple plausible visual interpretations internally,
then choose ONE.

Do not attempt to represent the whole event.

Prefer the smallest, strongest visual idea that still communicates
what makes this particular concept meaningful.

Make sure the core concept remains recognizable without written text.

When participant identities or relationships are protected unknowns,
do not choose an interaction that visually invents those relationships.

You may include one subtle, original, charming incidental detail if
it naturally improves the scene.

Do not reuse an accent detail merely because it appeared in another
example or reference.

Otherwise set accent_detail to null.
""".strip(),
            },
        ],
        text_format=ScenePlan,
    )

    scene_plan = response.output_parsed

    print(
        f"Generated scene plan for {request.name}:"
    )
    print(
        scene_plan.model_dump_json(indent=2)
    )

    return scene_plan