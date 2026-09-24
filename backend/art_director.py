from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel

from styles import StyleProfile
from visual_planner import ContentPlan


load_dotenv()

client = OpenAI()


# ---------------------------------------------------------
# Temporary styled-plan model
# ---------------------------------------------------------

class StyledScenePlan(BaseModel):
    """
    TEMPORARY art-direction output.

    This model is intentionally broad and lightweight.

    We have not yet finished studying the Google Calendar reference
    illustrations, so we do not want to prematurely define a detailed
    Google-specific scene-plan schema.

    ContentPlan decides WHAT should be communicated.

    StyledScenePlan provides a temporary description of HOW the content
    should be visually staged.
    """

    style_id: str

    visual_idea: str

    subject: str
    setting: str
    action: str

    selected_objects: list[str]
    accent_detail: str | None

    art_direction: str
    human_direction: str

    content_constraints: list[str]


# ---------------------------------------------------------
# Helpers
# ---------------------------------------------------------

def format_principles(principles: list[str]) -> str:
    """
    Format style-profile principles for inclusion in a prompt.
    """

    if not principles:
        return "- No additional principles specified."

    return "\n".join(
        f"- {principle}"
        for principle in principles
    )


def style_profile_is_empty(style_profile: StyleProfile) -> bool:
    """
    Return True when a style profile contains no actual
    art-direction principles.
    """

    principle_groups = [
        style_profile.composition_principles,
        style_profile.scale_principles,
        style_profile.cropping_principles,
        style_profile.perspective_principles,
        style_profile.human_principles,
        style_profile.scene_density_principles,
        style_profile.color_principles,
        style_profile.shape_principles,
        style_profile.rendering_principles,
    ]

    return all(
        len(group) == 0
        for group in principle_groups
    )


# ---------------------------------------------------------
# Temporary art director
# ---------------------------------------------------------

def art_direct_scene(
    content_plan: ContentPlan,
    style_profile: StyleProfile,
) -> StyledScenePlan:
    """
    TEMPORARY art-direction layer.

    For now, this function is primarily intended to support the generic
    style.

    Google Calendar art direction should not be considered implemented
    until we have systematically studied the reference illustrations and
    designed an appropriate Google-specific planning structure.
    """

    # -----------------------------------------------------
    # Guard against accidentally treating the unfinished
    # Google Calendar profile as a real implementation.
    # -----------------------------------------------------

    if (
        style_profile.id == "google_calendar"
        and style_profile_is_empty(style_profile)
    ):
        raise ValueError(
            "Google Calendar art direction is not implemented yet. "
            "The reference illustrations still need to be studied "
            "before defining the Google-specific art-direction rules."
        )

    candidate_objects = "\n".join(
        f"- {item}"
        for item in content_plan.candidate_objects
    )

    if not candidate_objects:
        candidate_objects = "- None suggested."

    content_constraints = "\n".join(
        f"- {item}"
        for item in content_plan.content_constraints
    )

    if not content_constraints:
        content_constraints = "- No additional semantic constraints."

    response = client.responses.parse(
        model="gpt-5.6-luna",
        input=[
            {
                "role": "system",
                "content": """
You are a temporary art-direction layer for a calendar illustration
system.

A previous Content Planner has already decided WHAT the illustration
should communicate.

Your job is to make a small number of reasonable decisions about HOW
that content should be visually staged.

This is deliberately a lightweight art-direction step.

Do not attempt to invent a complex style system.

--------------------------------------------------
SEMANTIC BOUNDARY
--------------------------------------------------

Preserve the meaning of the ContentPlan.

You may simplify how the idea is visually expressed, but do not:

- change the event into a different event,
- contradict the approved visual idea,
- violate content_constraints,
- invent unsupported relationships,
- turn unknown characteristics of an identified person into factual
  visual claims.

content_constraints are hard semantic boundaries.

--------------------------------------------------
OBJECT SELECTION
--------------------------------------------------

candidate_objects are possible semantic resources.

They are not mandatory.

Select only the objects that materially help the final visual idea.

selected_objects should normally come from candidate_objects.

Do not add new semantically important objects merely because they are
commonly associated with the event.

--------------------------------------------------
PEOPLE
--------------------------------------------------

Distinguish between identified people and anonymous people.

For an identified person:
- preserve known characteristics,
- do not invent unknown identity-specific characteristics as facts.

For anonymous people:
- natural human variation is allowed,
- figures may vary in skin tone,
- hair color,
- hair texture or hairstyle,
- gender presentation,
- ordinary clothing,
- facial appearance,
- and body proportions.

Anonymous people should not become featureless, mannequin-like, or
artificially identical simply because their identities are unspecified.

Do not use appearance to imply unsupported roles, relationships, or
stereotypes.

--------------------------------------------------
ART DIRECTION
--------------------------------------------------

Use the art_direction field to describe the overall visual staging.

It may discuss things such as:
- composition,
- emphasis,
- relative scale,
- framing,
- cropping,
- perspective,
- scene density,
- color treatment,
- shape treatment,
- rendering treatment.

Do not feel obligated to mention every category.

Only describe decisions that materially help this particular scene.

For the generic style, use reasonable default illustration judgment.

Do not imitate Google Calendar or any other specific product unless
the supplied StyleProfile explicitly contains those principles.

--------------------------------------------------
HUMAN DIRECTION
--------------------------------------------------

Use human_direction specifically for how people should be depicted.

If no people are needed, say so.

If people are anonymous, allow natural variation.

If an identified person's appearance is unknown, do not invent a
specific appearance and present it as that person.

--------------------------------------------------
ACCENT DETAIL
--------------------------------------------------

The ContentPlan may contain one optional accent detail.

You may keep it or omit it.

Do not invent a major new secondary storyline.

--------------------------------------------------
FINAL GOAL
--------------------------------------------------

Produce one concise temporary StyledScenePlan.

Preserve WHAT the event means.

Make only the visual decisions needed to make the plan renderable.
""".strip(),
            },
            {
                "role": "user",
                "content": f"""
Create a temporary styled scene plan.

--------------------------------------------------
CONTENT PLAN
--------------------------------------------------

Visual idea:
{content_plan.visual_idea}

Suggested representation:
{content_plan.representation}

Subject:
{content_plan.subject}

Setting:
{content_plan.setting or "No particular setting required."}

Action:
{content_plan.action or "No particular action required."}

Candidate objects:
{candidate_objects}

Accent detail:
{content_plan.accent_detail or "None"}

Hard content constraints:
{content_constraints}

--------------------------------------------------
STYLE PROFILE
--------------------------------------------------

Style ID:
{style_profile.id}

Style name:
{style_profile.name}

Description:
{style_profile.description}

Composition principles:
{format_principles(style_profile.composition_principles)}

Scale principles:
{format_principles(style_profile.scale_principles)}

Cropping principles:
{format_principles(style_profile.cropping_principles)}

Perspective principles:
{format_principles(style_profile.perspective_principles)}

Human principles:
{format_principles(style_profile.human_principles)}

Scene-density principles:
{format_principles(style_profile.scene_density_principles)}

Color principles:
{format_principles(style_profile.color_principles)}

Shape principles:
{format_principles(style_profile.shape_principles)}

Rendering principles:
{format_principles(style_profile.rendering_principles)}

--------------------------------------------------

Keep the art direction concise.

Do not invent a detailed style grammar when the StyleProfile does not
provide one.
""".strip(),
            },
        ],
        text_format=StyledScenePlan,
    )

    styled_scene_plan = response.output_parsed

    # -----------------------------------------------------
    # Restore semantic invariants explicitly.
    # -----------------------------------------------------

    styled_scene_plan = styled_scene_plan.model_copy(
        update={
            "style_id": style_profile.id,
            "visual_idea": content_plan.visual_idea,
            "content_constraints": content_plan.content_constraints,
        }
    )

    # The art director may omit an accent detail, but it should
    # not invent one when the ContentPlan had none.
    if content_plan.accent_detail is None:
        styled_scene_plan = styled_scene_plan.model_copy(
            update={
                "accent_detail": None,
            }
        )

    print(
        f"Generated temporary {style_profile.id} styled scene plan:"
    )
    print(
        styled_scene_plan.model_dump_json(indent=2)
    )

    return styled_scene_plan