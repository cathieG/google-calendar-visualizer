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


class ContentPlan(BaseModel):
    """
    Style-independent description of WHAT should be depicted.

    This model intentionally does not contain composition, color,
    camera, rendering-style, or other style-specific decisions.
    """

    visual_idea: str
    representation: str

    subject: str
    setting: str
    action: str

    candidate_objects: list[str]
    accent_detail: str | None

    content_constraints: list[str]


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
# Generic content planner
# ---------------------------------------------------------

def plan_concept_image(request: ConceptRequest) -> ContentPlan:
    """
    Interpret the concept and create one selective,
    style-independent content plan for the requested calendar concept.

    This function decides WHAT should be depicted.

    It deliberately does not decide HOW a particular visual style
    should compose, stage, color, or render the content.
    """

    # Stage 1:
    # Interpret the real-world meaning of the specific concept.
    concept_context = interpret_concept(request)

    # Stage 2:
    # Use the interpreted concept context to create a
    # style-independent content plan.
    #
    # The planner should decide WHAT should be depicted,
    # but not HOW a particular visual style should stage it.
    response = client.responses.parse(
        model="gpt-5.6-luna",
        input=[
            {
                "role": "system",
                "content": """
You are the generic content planner for a calendar illustration system.

Your job is to decide WHAT should be depicted.

You are NOT the art director and NOT the renderer.

A later style-specific art-direction layer will decide HOW the selected
content should be composed, scaled, framed, cropped, colored, and
rendered.

Your output should therefore remain style-independent.

--------------------------------------------------
CORE PLANNING PRINCIPLE
--------------------------------------------------

The concept interpreter provides many known details, general
associations, open choices, and protected unknowns.

Treat that information as a pool of possibilities.

Do not attempt to include everything associated with the real-world
event.

Choose ONE strong visual interpretation from several plausible
possibilities.

The plan should identify the smallest set of semantic elements needed
to make the concept clear and meaningful.

Before producing your answer, consider several plausible content
approaches internally.

Then choose only ONE.

Do not return the alternatives.

--------------------------------------------------
RECOGNIZABILITY
--------------------------------------------------

The chosen content should make the underlying concept recognizable
without relying on the event title or written text.

A clever, symbolic, or metaphorical idea is useful, but only when the
underlying concept remains understandable.

Prefer clear semantic cues over an inventive idea that becomes
ambiguous without explanation.

A surprising secondary detail may enrich a clear idea.

It must not replace the clear idea.

--------------------------------------------------
REPRESENTATION STRATEGIES
--------------------------------------------------

Choose the strategy according to which kind of visual content does
most of the work in making the concept recognizable.

- human_action_scene:
  A human action, pose, or partial human presence is the main cue.

  Use this when the concept would become substantially less recognizable
  if the person or action were removed.

  The person does not need to be shown fully when hands, arms, posture, or
  a simple human figure is enough.

- object_focus:
  One distinctive object, or a small arrangement of objects, carries
  most of the concept's recognizability.

  Use this when the concept itself is object or focused and when 
  people or a detailed environment add little useful
  semantic information.

- environment_focus:
  A recognizable place, setting, or environment carries most of the
  concept.

  People and objects may appear, but they are semantically secondary.

- social_interaction_scene:
  An interaction between multiple people is central to recognizing the
  event.

  Use this only when the event itself supports that interaction.

- atmosphere_symbolic_scene:
  A small set of atmospheric, seasonal, celebratory, or symbolic
  elements carries the concept without requiring a specific human
  action or detailed physical environment.

These strategies describe the PRIMARY carrier of recognition.

A content plan may include secondary elements associated with other
strategies.

Choose the strategy based on what the viewer relies on most to
recognize the concept.

--------------------------------------------------
CONTENT ECONOMY
--------------------------------------------------

Do not reconstruct the whole real-world event.

Prefer a focused visual idea.

Include only people, objects, actions, or setting information that
materially help communicate the chosen concept.

A specific event can have many valid representations.
Your task is to select one of them.

The candidate_objects field should contain a small pool of objects that are
semantically useful to the chosen visual interpretation.

These are candidate resources for hte later art-direction layer, not a checklist
of objects that must all appear.

Do not make decisions here about how many objects should dominate the
frame, how large they should appear, or where they should be placed.

Those are art-direction decisions.

--------------------------------------------------
SPECIFICITY
--------------------------------------------------

Preserve details that distinguish the requested concept from a more
generic version when those details can be communicated without
overloading the plan.

For example:
- a 70th birthday should not become a generic birthday,
- an anniversary dinner should not become an ordinary dinner,
- the first day of kindergarten should not become generic school.

Specificity does not require representing every detail.

Choose enough content to preserve what is meaningful about this
particular concept.

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

Use them only when they support the chosen visual idea.

OPEN CHOICES are legitimate areas of creative freedom.

You may choose one plausible option when it helps create a clearer
content idea. You do not need to exercise every open choice.

PROTECTED UNKNOWNS are boundaries.

Do not turn a protected unknown into a factual claim in the content
plan.

This is especially important for identified or named people.

These restrictions apply to claims about identifiable people.

They do not prohibit anonymous, unspecified human figures from having
ordinary and varied appearances.

For example, if a concept naturally calls for a group of anonymous
people, those figures may differ in:
- skin tone,
- hair color,
- hair texture or hairstyle,
- gender presentation,
- ordinary clothing,
- facial features,
- body proportions.

Such variation is allowed because those figures are not being presented
as specific known individuals.

Do not treat unspecified identity as a requirement for visually neutral,
featureless, or identical people.

However, if the ContentPlan refers to a specific named or otherwise
identified person, do not infer or assert that person's:
- gender,
- age,
- race or ethnicity,
- skin tone,
- facial appearance,
- hair color or hairstyle,
- body type,
- clothing style,
- occupation,
- relationship to another participant,

unless that information is actually provided.

The key distinction is:

- anonymous person: ordinary visual variation is allowed,
- identified person: preserve known traits and do not invent unknown
  identity-specific traits.

A participant who is semantically part of the event does not
automatically have to appear in the planned content.

--------------------------------------------------
RELATIONSHIP UNCERTAINTY
--------------------------------------------------

When the relationship between participants is a protected unknown, do
not choose content that requires a specific unsupported relationship
to make sense.

Avoid content ideas that inherently depend on:
- physical contact,
- coordinated intimate behavior,
- one person guiding another person's body or hands,
- body language that implies romance, family, caretaking, mentorship,
  or another specific relationship,

unless that interaction is directly supported by the event.

Do not solve relationship uncertainty merely by hiding faces.

The underlying action itself must avoid implying an unsupported
relationship.

If the activity can be recognized using:
- one anonymous participant,
- partial human presence,
- objects,
- tools,
- or the environment,

consider those alternatives.

A participant may be semantically important to the event without
needing to be visually represented.

--------------------------------------------------
CREATIVE ACCENT DETAIL
--------------------------------------------------

You may optionally introduce ONE small incidental content detail.

Its purpose is to make the visual idea feel observed, specific,
charming, playful, or pleasantly surprising.

The accent detail should:
- be plausible in the real-world situation,
- remain secondary to the main concept,
- require no unsupported personal information,
- add personality without adding a new storyline.

Do NOT force an accent detail into every plan.

If there is no genuinely useful detail, set accent_detail to null.

Do not make the accent detail:
- a joke that distracts from the concept,
- a new major character,
- a separate event,
- written text or signage,
- an unsupported fact about a real person,
- a substitute for a recognizable main idea.

The accent_detail field describes WHAT the incidental detail is.

Do not specify where it appears, how large it is, what color it is,
or how it should be rendered.

--------------------------------------------------
CONTENT PLAN FIELDS
--------------------------------------------------

visual_idea:
A concise description of the ONE semantic visual concept you selected.

Explain what the illustration should communicate through depicted
content rather than merely repeating the event title.

Do not include composition, camera, color, or rendering instructions.

representation:
The broad content representation strategy.

Use one of:
- human_action_scene
- object_focus
- environment_focus
- social_interaction_scene
- atmosphere_symbolic_scene

subject:
The primary semantic subject of the idea.

Describe WHAT the subject is, not where it should be positioned or how
large it should appear.

setting:
Only the setting information that is semantically useful to the idea.

Use an empty string when no particular setting is needed.

Do not specify background layout, depth, camera angle, or composition.

action:
An action that is semantically important to the idea.

Use an empty string when no action is needed.

Do not include staging, pose, camera, or drawing instructions.

candidate_objects:
A small pool of physical objects that could help communicate the chosen idea.

These should be objects that are the most expected when thinking of the idea
in real life. 

A later art-direction layer will use this pool as a reference and may select all,
some, or none of these objects depending on how the chosen style expresses the visual idea,
your job is to provide the objects as candidates.

Do not specify their scale, placement, color, or rendering treatment.

accent_detail:
At most one optional secondary content detail.

Use null when none improves the idea.

content_constraints:
A short list of semantic boundaries that the downstream art director
and renderer must preserve.

Use this field for content-level constraints such as:
- do not turn a specific event into a more generic one,
- do not introduce an unsupported participant role,

Do NOT use content_constraints for style or composition rules such as:
- use a sparse composition,
- make an object large or small,
- crop a figure,
- use a particular camera angle,
- use flat colors,
- avoid dramatic perspective,
- use a particular illustration technique.

Those decisions belong to the style-specific art-direction layer.

Choose content that already respects all known details and protected
unknowns.

--------------------------------------------------
STYLE-INDEPENDENT BOUNDARY
--------------------------------------------------

Do NOT decide:
- composition,
- layout,
- visual hierarchy,
- object scale,
- human-to-object scale,
- framing,
- cropping,
- camera angle,
- perspective,
- negative space,
- color palette,
- lighting,
- shading,
- texture,
- shape language,
- illustration technique,
- realism level,
- final rendering style.

Do not imitate or assume any particular product's existing illustration
language.

A later art-direction layer will make those decisions according to the
selected style.

--------------------------------------------------
FINAL GOAL
--------------------------------------------------

The goal is NOT:

"What does this kind of event usually contain?"

The goal is:

"What is one clear, recognizable, meaningful set of content to depict
for THIS event?"

Choose deliberately.

Be selective.

Preserve the meaning of the specific event.

Focus only on WHAT should be depicted.

Leave HOW it should be visually staged to the art-direction layer.
""".strip(),
            },
            {
                "role": "user",
                "content": f"""
Create ONE style-independent content plan for a new calendar
illustration.

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

Treat the general associations as a menu of possibilities rather than
a checklist.

Use the open choices as legitimate creative freedom. You may choose
one plausible option when it improves the content idea, but you do not
need to use every open choice.

Respect the protected unknowns as hard semantic boundaries.

Consider multiple plausible content interpretations internally, then
choose ONE.

Do not attempt to represent the whole event.

Prefer the smallest strong content idea that still communicates what
makes this particular concept meaningful.

Make sure the core concept remains recognizable without written text.

When participant identities or relationships are protected unknowns,
do not choose content that turns those unknowns into factual claims.

You may include one subtle, original incidental detail if it naturally
improves the content idea.

Otherwise set accent_detail to null.

Do not make composition, scale, framing, color, perspective, or
rendering-style decisions. Those belong to the later art-direction
layer.
""".strip(),
            },
        ],
        text_format=ContentPlan,
    )

    content_plan = response.output_parsed

    print(
        f"Generated content plan for {request.name}:"
    )
    print(
        content_plan.model_dump_json(indent=2)
    )

    return content_plan
