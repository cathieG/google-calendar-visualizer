**\*\*# Google Calendar Illustration Study — Annotation Codebook\*\***

**\*\*\\\*\\\*Version:\\\*\\\*\*\*** 0.5 (provisional)  

**\*\*\\\*\\\*Basis:\\\*\\\*\*\*** 15 rich discovery studies: Art, Athletic Jumping, Baby Shower, Basketball, Barbecue, Bowling, Chinese New Year, Cinema, Climbing, Concert, Delivery / Parcel, Doctor, Shopping, Vote, and Wedding.  

**\*\*\\\*\\\*Purpose:\\\*\\\*\*\*** Normalize recurring art-direction decisions across the reference set without replacing the richer discovery records.

**\*\*\\\*\\\*Pilot evidence informing v0.4:\\\*\\\*\*\*** Art, Climbing, Bowling, Valentine’s Day, and Thanksgiving.

**\*\*\\\*\\\*Unseen stress-test evidence informing v0.5:\\\*\\\*\*\*** American Football, Cooking, Camping, and Karate.

**\*\*---\*\***

**\*\*## 1. What this codebook is for\*\***

The discovery JSON files preserve detailed, image-specific observations and hypotheses. This codebook serves a different purpose: it defines a **\*\*\\\*\\\*small, reusable set of annotation dimensions\\\*\\\*\*\*** that can be applied consistently across many illustrations so that recurring patterns can be compared.

The codebook should capture decisions that vary meaningfully from image to image, such as:

\\- how the concept is represented;

\\- what carries recognition;

\\- whether and how people are shown;

\\- how action, event state, and causal logic are encoded;

\\- how much of the environment is retained;

\\- how viewpoint, depth, scale, and cropping are used;

\\- how visual hierarchy and negative space are organized;

\\- how color, shape, detail, repetition, and nonliteral graphic cues are used.

It should **\*\*\\\*\\\*not\\\*\\\*\*\*** attempt to preserve every image-specific observation. Details such as a shopping-cart grid, a doctor badge, film-strip perforations, or the exact contents of a barbecue grill stay in the discovery record unless they support a broader codebook dimension.

**\*\*---\*\***

**\*\*## 2. Annotation principles\*\***

**\*\*### 2.1 Separate observation from interpretation\*\***

Annotations should distinguish three levels:

1\\. **\*\*\\\*\\\*Observable\\\*\\\*\*\*** — what is visibly present in the image.

2\\. **\*\*\\\*\\\*Interpretive\\\*\\\*\*\*** — what visual or semantic function an element appears to serve.

3\\. **\*\*\\\*\\\*Hypothesis\\\*\\\*\*\*** — why the designer may have chosen that solution.

Standardized annotations should primarily encode levels 1 and 2. Level 3 belongs in notes and should carry an explicit confidence level.

**\*\*### 2.2 Code visible attributes, not inferred identity\*\***

For people, record observable visual design choices such as skin color, hair color, hairstyle, clothing, pose, and body construction. Do **\*\*\\\*\\\*not\\\*\\\*\*\*** infer race, ethnicity, nationality, religion, gender identity, or other demographic identity from appearance.

Example:

\\- Preferred: \\\`skin_color: "medium warm brown"\\\`

\\- Preferred: \\\`hairstyle: "dark hair in a bun"\\\`

\\- Avoid: assigning a racial or ethnic identity from those features.

**\*\*### 2.3 Use broad reusable categories\*\***

Prefer categories that can describe many references. Do not create a new code merely because one illustration contains a distinctive object or motif.

**\*\*### 2.4 Allow multiple codes when the image genuinely combines strategies\*\***

Some fields are explicitly **\*\*\\\*\\\*multi-select\\\*\\\*\*\***. For example, color can simultaneously establish semantic association, visual hierarchy, and participant grouping.

For fields that use a primary strategy, an optional secondary strategy may be recorded when needed.

**\*\*### 2.5 Preserve uncertainty\*\***

Do not force a confident label when the image is ambiguous.

Use:

\\- \\\`null\\\` — the field is not applicable.

\\- \\\`none\\\` — the field is applicable and the feature is visibly absent.

\\- \\\`uncertain\\\` — the field is applicable, but the correct value cannot be determined confidently.

\\- \\\`not_observed\\\` — the feature could exist, but the image does not provide enough visible information to judge it.

**\*\*### 2.6 Confidence\*\***

Interpretive annotations may optionally be marked:

\\- \\\`high\\\` — strongly supported by visible evidence;

\\- \\\`medium\\\` — plausible and reasonably supported;

\\- \\\`low\\\` — tentative interpretation.

Confidence should be used especially for semantic role, environment role, causal structure, and nonliteral graphic cues.

**\*\*### 2.7 Controlled-vocabulary discipline\*\***

When a field has an explicit controlled vocabulary, use the **\*\*\\\*\\\*exact allowed value\\\*\\\*\*\***. Do not invent intermediate or hybrid labels such as \\\`moderate_high\\\`, \\\`low_to_moderate\\\`, \\\`close_symbolic_field\\\`, or \\\`composition_based\\\` simply because they feel descriptively convenient.

If the allowed code is broadly correct but needs nuance, preserve the controlled value and put the nuance in the relevant note or evidence field. Only expand the vocabulary when repeated annotations expose a genuine conceptual gap.

**\*\*### 2.8 Describe visible clothing and accessories with downstream precision\*\***

Open-text appearance fields should be specific enough that a downstream art-direction or generation system would not have to guess what was visibly present. Record distinct visible garment pieces, colors, and activity-specific accessories when they materially affect the figure design.

Examples:

\\- Prefer \\\`light blue football jersey with light yellow football pants\\\` over a generic \\\`football uniform\\\` when both pieces are visible.

\\- Prefer \\\`football helmet with helmet face mask\\\` over \\\`face mask\\\`, which could be misread as a medical or fabric face covering.

\\- Preserve meaningful differences between figures even when they share a uniform system; do not collapse a visible garment into a group-level label if that would erase an observed distinction.

This rule concerns descriptive precision, not finer categorical coding. Do not invent invisible garment details or equipment.

**\*\*---\*\***

**\*\*# 3. Annotation families\*\***

The normalized schema is organized into six families:

1\\. Representation & Recognition

2\\. People & Social Structure

3\\. Event & Semantic Logic

4\\. Environment & Space

5\\. Composition & Visual Hierarchy

6\\. Visual Language

**\*\*---\*\***

**\*\*# 4. Representation & Recognition\*\***

**\*\*## 4.1 \\\`representation_strategy\\\`\*\***

**\*\*\\\*\\\*Question:\\\*\\\*\*\*** What broad visual strategy was chosen to represent the concept?

**\*\*\\\*\\\*Type:\\\*\\\*\*\*** primary controlled value + optional secondary value

**\*\*\\\*\\\*Allowed values:\\\*\\\*\*\***

\\- \\\`human_action_scene\\\` — a person performing an activity is the main representation.

\\- \\\`human_object_interaction\\\` — recognition depends on a person interacting with a diagnostic object.

\\- \\\`multi_person_interaction\\\` — relationships among multiple people are central.

\\- \\\`occupational_figure\\\` — a person is shown primarily as a carrier of professional/role-specific cues rather than as an action performer.

\\- \\\`object_centered_scene\\\` — one or a few diagnostic objects dominate without requiring a person.

\\- \\\`symbolic_object_composition\\\` — symbolic objects collectively evoke the concept rather than depict a literal event.

\\- \\\`iconic_object_collage\\\` — several iconic cues from the concept are assembled into a nonliteral conceptual composition.

\\- \\\`prepared_environment\\\` — a setting or object arrangement implies human activity through an event-ready or in-use state.

\\- \\\`environment_led_scene\\\` — the environment itself is a major carrier of recognition.

\\- \\\`decorative_atmosphere_scene\\\` — atmosphere, repeated decorations, or cultural/festive cues carry most of the concept.

**\*\*\\\*\\\*Operational note:\\\*\\\*\*\*** Choose the broadest strategy that explains why the image works. Use a secondary strategy only when two strategies are genuinely important. The secondary code should describe a distinct representation mechanism, not merely restate the primary code in different words.

**\*\*\\\*\\\*Examples from discovery studies:\\\*\\\*\*\***

\\- Athletic Jumping → primary \\\`human_action_scene\\\`

\\- Art → primary \\\`human_action_scene\\\`; secondary \\\`human_object_interaction\\\`

\\- Climbing → primary \\\`human_action_scene\\\`; secondary \\\`human_object_interaction\\\`

\\- Vote → \\\`human_object_interaction\\\`

\\- Doctor → \\\`occupational_figure\\\`

\\- Barbecue → \\\`prepared_environment\\\`

\\- Cinema → \\\`iconic_object_collage\\\`

\\- Chinese New Year → \\\`decorative_atmosphere_scene\\\`

**\*\*---\*\***

**\*\*## 4.2 \\\`recognition_structure\\\`\*\***

**\*\*\\\*\\\*Question:\\\*\\\*\*\*** How is semantic recognition distributed across the image?

**\*\*\\\*\\\*Type:\\\*\\\*\*\*** controlled value

**\*\*\\\*\\\*Allowed values:\\\*\\\*\*\***

\\- \\\`concentrated\\\` — one compact cue or one tightly integrated diagnostic interaction carries most recognition.

\\- \\\`dominant_anchor_with_support\\\` — one clearly dominant cue carries most recognition while spatially or semantically separable supporting cues materially reinforce or narrow the reading.

\\- \\\`distributed_symbolic\\\` — several symbolic cues jointly carry recognition.

\\- \\\`distributed_functional\\\` — several functionally related objects jointly carry recognition.

\\- \\\`distributed_iconic\\\` — several recognizable icons from the broader concept jointly carry recognition.

\\- \\\`distributed_narrative\\\` — several cues become diagnostic through a small process, sequence, origin-to-destination structure, or other narrative chain.

\\- \\\`relational\\\` — recognition depends substantially on the relationship among multiple people and/or objects rather than on one compact interaction.

\\- \\\`contextual\\\` — recognition depends strongly on setting or surrounding context.

\\- \\\`mixed\\\` — no single structure adequately describes the image.

**\*\*\\\*\\\*Operational distinction:\\\*\\\*\*\***

\\\`concentrated\\\` and \\\`relational\\\` should not be separated merely by counting how many objects participate. A compact interaction can contain several elements and still be concentrated if they function as one diagnostic unit.

For example:

\\- Vote → \\\`concentrated\\\`: hand + ballot + slot + box form one compact voting gesture.

\\- Thanksgiving → \\\`dominant_anchor_with_support\\\`: the turkey is the primary holiday cue while autumn leaves and palette reinforce the reading.

\\- Climbing → \\\`relational\\\`: climber + wall + holds + rope work together across the scene.

\\- Basketball → \\\`relational\\\`: recognition depends on the interaction among several players, ball, and court context.

\\- Delivery / Parcel → \\\`distributed_narrative\\\`: worker, parcels, truck, and houses form a readable delivery sequence.

**\*\*\\\*\\\*Distinction:\\\*\\\*\*\*** This field is about **\*\*\\\*\\\*how recognition is distributed\\\*\\\*\*\***, not merely which objects are shown.

**\*\*---\*\***

**\*\*## 4.3 \\\`recognition_anchor\\\`\*\***

**\*\*\\\*\\\*Question:\\\*\\\*\*\*** What carries the strongest semantic recognition?

**\*\*\\\*\\\*Type:\\\*\\\*\*\*** structured free text

Use:

\\\`\\\`\\\`json

{

  "primary": "hand inserting ballot into ballot-box slot",

  "supporting": [

    "ballot box",

    "folded ballot"

  ]

}

\\\`\\\`\\\`

\\\`primary\\\` should name the strongest cue or the smallest coherent interaction that explains recognition.

\\\`supporting\\\` contains additional cues that materially reinforce the reading. It may be empty.

The primary anchor does **\*\*\\\*\\\*not\\\*\\\*\*\*** have to be one physical object. In a relational or distributed scene, it may be a compact phrase describing the core interaction or cue system.

Examples:

\\- Athletic Jumping → primary: \\\`human jumping pose\\\`

\\- Vote → primary: \\\`hand inserting ballot into ballot-box slot\\\`

\\- Doctor → primary: \\\`stethoscope + coat + badge cluster\\\`

\\- Barbecue → primary: \\\`open grill with food\\\`; supporting: outdoor setting + serving setup

\\- Delivery / Parcel → primary: \\\`worker-parcels-truck delivery chain\\\`; supporting: residential destination

Keep phrases short and concrete.

**\*\*---\*\***

**\*\*## 4.4 \\\`recognition_specificity\\\`\*\***

**\*\*\\\*\\\*Question:\\\*\\\*\*\*** How specifically does the image communicate the exact named concept rather than a broader neighboring concept?

**\*\*\\\*\\\*Type:\\\*\\\*\*\*** controlled ordinal

\\- \\\`low\\\` — mainly communicates a broad domain.

\\- \\\`moderate\\\` — communicates the intended domain clearly but could plausibly map to several neighboring events.

\\- \\\`high\\\` — strongly distinguishes the intended concept.

Use only these three levels. If a case falls between them, choose the closest value and explain the uncertainty in an evidence/confidence note rather than creating a hybrid label.

**\*\*\\\*\\\*Example:\\\*\\\*\*\*** Baby Shower may communicate baby/newborn strongly while being less specific to the shower event itself.

**\*\*---\*\***

**\*\*## 4.5 \\\`semantic_scope\\\`\*\***

**\*\*\\\*\\\*Question:\\\*\\\*\*\*** How does the semantic scope of the depicted solution relate to the named concept?

**\*\*\\\*\\\*Type:\\\*\\\*\*\*** controlled value

\\- \\\`matched_scope\\\` — the depiction remains at roughly the same conceptual scope as the named concept.

\\- \\\`narrowed_instance\\\` — a broad concept is represented through one more specific subtype, activity, or instance.

\\- \\\`broader_neighboring_domain\\\` — the depiction communicates a broader or neighboring domain rather than staying tightly within the named concept.

\\- \\\`mixed_breadth\\\` — the depiction intentionally combines multiple subdomains or aspects of the concept.

\\- \\\`uncertain\\\` — the relationship between the named concept and depicted scope cannot be assigned confidently.

**\*\*\\\*\\\*Examples:\\\*\\\*\*\***

\\- Art → \\\`narrowed_instance\\\` because broad art is represented through painting.

\\- Climbing → \\\`narrowed_instance\\\` because broad climbing is represented through roped indoor climbing.

\\- Bowling → \\\`matched_scope\\\`.

\\- Wedding → potentially \\\`broader_neighboring_domain\\\` because the symbolic cluster can also suggest a broader romantic or celebratory event.

\\- Cinema → \\\`mixed_breadth\\\` because filmmaking and moviegoing cues are combined.

**\*\*\\\*\\\*Distinction from \\\`recognition_specificity\\\`:\\\*\\\*\*\***

\\\`recognition_specificity\\\` asks how strongly the image distinguishes the exact named concept from neighboring concepts.

\\\`semantic_scope\\\` asks whether the **\*\*\\\*\\\*depicted solution itself\\\*\\\*\*\*** is narrower, broader, matched, or semantically mixed relative to the concept label.

**\*\*---\*\***

**\*\*## 4.6 \\\`representation_optionality\\\`\*\***

**\*\*\\\*\\\*Question:\\\*\\\*\*\*** How many substantially different representation strategies appear plausibly available for this concept?

**\*\*\\\*\\\*Type:\\\*\\\*\*\*** interpretive ordinal

\\- \\\`low\\\`

\\- \\\`moderate\\\`

\\- \\\`high\\\`

Use this cautiously. It describes the **\*\*\\\*\\\*design space\\\*\\\*\*\***, not a visible object count. Add an evidence note when coded.

**\*\*---\*\***

**\*\*# 5. People & Social Structure\*\***

If \\\`human_presence = none\\\`, most person-level fields are \\\`null\\\`, and group-level relationship/clothing fields are generally \\\`not_applicable\\\`.

**\*\*## 5.1 \\\`human_presence\\\`\*\***

**\*\*\\\*\\\*Type:\\\*\\\*\*\*** controlled value

\\- \\\`none\\\`

\\- \\\`partial_body\\\`

\\- \\\`single\\\`

\\- \\\`pair\\\`

\\- \\\`group\\\`

**\*\*---\*\***

**\*\*## 5.2 \\\`human_count\\\`\*\***

**\*\*\\\*\\\*Type:\\\*\\\*\*\*** integer, \\\`uncertain\\\`, or \\\`null\\\`

Count the number of **\*\*\\\*\\\*represented human individuals\\\*\\\*\*\***, even when only part of a person is visible.

Examples:

\\- Vote shows one hand and forearm belonging to one represented person → \\\`human_count: 1\\\`.

\\- Barbecue shows no visible human body or body part → \\\`human_count: 0\\\`.

Do not count people who are merely implied by prepared objects, social context, or off-screen narrative.

**\*\*---\*\***

**\*\*## 5.3 \\\`human_role\\\`\*\***

**\*\*\\\*\\\*Question:\\\*\\\*\*\*** What semantic job do the visible people perform?

**\*\*\\\*\\\*Type:\\\*\\\*\*\*** primary controlled value + optional secondary

\\- \\\`primary_action_carrier\\\`

\\- \\\`supporting_action_carrier\\\`

\\- \\\`occupational_carrier\\\`

\\- \\\`relational_carrier\\\`

\\- \\\`contextual_participant\\\`

\\- \\\`collective_participant\\\`

\\- \\\`absent\\\`

At image level, \\\`human_role\\\` summarizes the roles present in the scene. When multiple visible people have meaningfully different roles, also record \\\`semantic_role\\\` inside the relevant per-person records so that the annotation preserves which figure performs which role. Use the same role vocabulary as this section.

Example: in American Football, the foreground ball carrier may be \\\`primary_action_carrier\\\` while a more distant teammate is \\\`supporting_action_carrier\\\`.

**\*\*---\*\***

**\*\*## 5.4 \\\`body_visibility\\\`\*\***

**\*\*\\\*\\\*Type:\\\*\\\*\*\*** controlled value

\\- \\\`full_body\\\`

\\- \\\`upper_body\\\`

\\- \\\`torso\\\`

\\- \\\`head_shoulders\\\`

\\- \\\`limb_only\\\`

\\- \\\`mixed\\\`

**\*\*---\*\***

**\*\*## 5.5 \\\`figure_orientation\\\`\*\***

**\*\*\\\*\\\*Question:\\\*\\\*\*\*** How are visible figures oriented relative to the viewer?

**\*\*\\\*\\\*Type:\\\*\\\*\*\*** controlled value

\\- \\\`front\\\`

\\- \\\`back\\\`

\\- \\\`side\\\`

\\- \\\`three_quarter\\\`

\\- \\\`overhead\\\`

\\- \\\`mixed\\\`

\\- \\\`indeterminate\\\`

This is separate from the overall camera/view angle.

**\*\*---\*\***

**\*\*## 5.6 \\\`face_visibility\\\`\*\***

**\*\*\\\*\\\*Type:\\\*\\\*\*\*** controlled value

\\- \\\`none\\\`

\\- \\\`partial\\\`

\\- \\\`visible\\\`

\\- \\\`mixed\\\`

**\*\*---\*\***

**\*\*## 5.7 \\\`facial_specificity\\\`\*\***

**\*\*\\\*\\\*Question:\\\*\\\*\*\*** How much facial information is actually rendered?

**\*\*\\\*\\\*Type:\\\*\\\*\*\*** controlled ordinal

\\- \\\`none\\\`

\\- \\\`very_low\\\`

\\- \\\`low\\\`

\\- \\\`moderate\\\`

\\- \\\`high\\\`

The value should reflect rendered specificity, not whether the face is merely visible.

**\*\*---\*\***

**\*\*## 5.8 Per-person observable appearance\*\***

When the number of figures is manageable, create a \\\`people\\\` array. Each person may contain:

\\\`\\\`\\\`json

{

  "person_id": "p1",

  "skin_color": "medium warm brown",

  "hair_color": "dark brown",

  "hairstyle": "short curly hair",

  "hair_detail_level": "distinct_silhouette",

  "facial_hair": "none",

  "clothing_description": "yellow basketball uniform",

  "activity_accessories": [],

  "body_visibility": "full_body",

  "figure_orientation": "three_quarter"

}

\\\`\\\`\\\`

**\*\*### \\\`semantic_role\\\`\*\***

Optional per-person controlled value using the same vocabulary as image-level \\\`human_role\\\`. Use it when individual figures play meaningfully different semantic roles and the image-level primary/secondary summary would otherwise lose that mapping. Leave it out when all visible people share essentially the same role.

**\*\*### \\\`skin_color\\\`\*\***

Use a short **\*\*\\\*\\\*visual color description\\\*\\\*\*\***, not demographic identity.

Examples:

\\- \\\`light peach\\\`

\\- \\\`medium peach\\\`

\\- \\\`orange-coral\\\`

\\- \\\`light brown\\\`

\\- \\\`medium warm brown\\\`

\\- \\\`dark brown\\\`

\\- \\\`stylized non-natural color\\\`

\\- \\\`obscured\\\`

Do not infer race or ethnicity.

**\*\*### \\\`hair_color\\\`\*\***

Use visible rendered color:

\\- \\\`black\\\`

\\- \\\`dark brown\\\`

\\- \\\`brown\\\`

\\- \\\`blonde/gold\\\`

\\- \\\`red/auburn\\\`

\\- \\\`gray/white\\\`

\\- \\\`stylized other\\\`

\\- \\\`obscured\\\`

\\- \\\`none_visible\\\`

**\*\*### \\\`hairstyle\\\`\*\***

Short open-vocabulary visual phrase. Examples:

\\- \\\`short straight hair\\\`

\\- \\\`short curly hair\\\`

\\- \\\`rounded curly hair\\\`

\\- \\\`long straight hair\\\`

\\- \\\`long wavy hair\\\`

\\- \\\`ponytail\\\`

\\- \\\`bun\\\`

\\- \\\`high bun\\\`

\\- \\\`low bun\\\`

\\- \\\`braids\\\` only when visually unambiguous

\\- \\\`shaved/bald\\\`

\\- \\\`partially obscured\\\`

**\*\*### \\\`hair_detail_level\\\`\*\***

\\- \\\`none\\\`

\\- \\\`simple_mass\\\`

\\- \\\`distinct_silhouette\\\`

\\- \\\`moderately_detailed\\\`

**\*\*### \\\`facial_hair\\\`\*\***

Use a short open-vocabulary visual phrase for visible facial hair, for example \\\`full beard\\\`, \\\`mustache\\\`, \\\`short beard\\\`, \\\`none\\\`, or \\\`obscured\\\`. Use only when visibly supported. Bowling is a useful example because the beard contributes to anonymous character specificity without making the figure portrait-like.

**\*\*### \\\`activity_accessories\\\`\*\***

Use a short list of person-attached or person-used accessories that materially contribute to the depicted activity or role, for example \\\`climbing harness\\\`, \\\`chalk bag\\\`, \\\`stethoscope\\\`, or \\\`football helmet with helmet face mask\\\`. Describe the accessory specifically enough to avoid semantic ambiguity. Do not duplicate every nearby object; use this field for accessories meaningfully associated with the person.

**\*\*---\*\***

**\*\*## 5.9 \\\`skin_color_variation\\\`\*\***

For multi-person images only.

\\- \\\`not_applicable\\\`

\\- \\\`none\\\`

\\- \\\`low\\\`

\\- \\\`moderate\\\`

\\- \\\`high\\\`

This describes visible rendered variation, not demographic diversity.

**\*\*---\*\***

**\*\*## 5.10 \\\`hair_color_variation\\\`\*\***

\\- \\\`not_applicable\\\`

\\- \\\`none\\\`

\\- \\\`low\\\`

\\- \\\`moderate\\\`

\\- \\\`high\\\`

**\*\*---\*\***

**\*\*## 5.11 \\\`hairstyle_variation\\\`\*\***

\\- \\\`not_applicable\\\`

\\- \\\`none\\\`

\\- \\\`low\\\`

\\- \\\`moderate\\\`

\\- \\\`high\\\`

**\*\*---\*\***

**\*\*## 5.12 \\\`clothing_strategy\\\`\*\***

**\*\*\\\*\\\*Type:\\\*\\\*\*\*** controlled value

\\- \\\`generic\\\`

\\- \\\`activity_specific\\\`

\\- \\\`occupational\\\`

\\- \\\`ceremonial\\\`

\\- \\\`team_uniform\\\`

\\- \\\`coordinated\\\`

\\- \\\`mixed\\\`

**\*\*---\*\***

**\*\*## 5.13 \\\`clothing_variation\\\`\*\***

For multi-person images:

\\- \\\`not_applicable\\\`

\\- \\\`uniform\\\`

\\- \\\`coordinated\\\`

\\- \\\`varied\\\`

\\- \\\`mixed\\\`

**\*\*---\*\***

**\*\*## 5.16 \\\`inter_person_clothing_structure\\\`\*\***

**\*\*\\\*\\\*Question:\\\*\\\*\*\*** When multiple people are present, how are their clothing choices visually related to one another?

**\*\*\\\*\\\*Type:\\\*\\\*\*\*** controlled value

\\- \\\`not_applicable\\\` — fewer than two visible people, or clothing relationships cannot meaningfully be evaluated.

\\- \\\`shared_uniform\\\` — the group wears essentially the same costume or uniform.

\\- \\\`subgroup_uniforms\\\` — internally consistent clothing distinguishes subgroups, teams, sides, or factions.

\\- \\\`coordinated\\\` — clothing is visibly related through palette, form, styling, or costume logic without being identical.

\\- \\\`role_differentiated\\\` — clothing visibly distinguishes functional or social roles.

\\- \\\`individually_varied\\\` — clothing primarily preserves individual differentiation rather than group uniformity.

\\- \\\`mixed\\\` — more than one relationship is substantially important.

Pay particular attention to this field when the semantic center of the scene is relational: competition, cooperation, coordinated performance, team activity, ceremonial group action, or other structured interaction.

Examples:

\\- Basketball → \\\`subgroup_uniforms\\\`.

\\- Graduation → likely \\\`shared_uniform\\\`.

\\- Concert → \\\`individually_varied\\\`.

**\*\*---\*\***

**\*\*## 5.17 \\\`clothing_relationship_function\\\`\*\***

**\*\*\\\*\\\*Question:\\\*\\\*\*\*** What does the clothing relationship communicate about the people?

**\*\*\\\*\\\*Type:\\\*\\\*\*\*** multi-select

\\- \\\`group_unity\\\`

\\- \\\`team_or_side_membership\\\`

\\- \\\`opposition\\\`

\\- \\\`coordinated_performance\\\`

\\- \\\`role_differentiation\\\`

\\- \\\`ceremonial_unity\\\`

\\- \\\`individual_differentiation\\\`

\\- \\\`none_or_unclear\\\`

Examples:

\\- Basketball → \\\`team_or_side_membership\\\` + \\\`opposition\\\`.

\\- A coordinated ballet ensemble may use \\\`group_unity\\\` + \\\`coordinated_performance\\\`.

\\- Graduation may use \\\`ceremonial_unity\\\`.

\\- Concert → \\\`individual_differentiation\\\`, because the performers cooperate while remaining visually distinct.

**\*\*\\\*\\\*Distinction:\\\*\\\*\*\***

\\\`group_relationship_structure\\\` asks **\*\*\\\*\\\*what relationship exists among the people\\\*\\\*\*\***.

\\\`inter_person_clothing_structure\\\` asks **\*\*\\\*\\\*how their clothes are visually related\\\*\\\*\*\***.

\\\`clothing_relationship_function\\\` asks **\*\*\\\*\\\*what that clothing relationship communicates\\\*\\\*\*\***.

**\*\*---\*\***

**\*\*## 5.14 \\\`body_shape_variation\\\`\*\***

For multi-person images:

\\- \\\`not_applicable\\\`

\\- \\\`none\\\`

\\- \\\`low\\\`

\\- \\\`moderate\\\`

\\- \\\`high\\\`

Code only visible silhouette/body-construction variation.

**\*\*---\*\***

**\*\*## 5.15 \\\`pose_variation\\\`\*\***

For multi-person images:

\\- \\\`not_applicable\\\`

\\- \\\`none\\\`

\\- \\\`low\\\`

\\- \\\`moderate\\\`

\\- \\\`high\\\`

**\*\*---\*\***

**\*\*## 5.18 \\\`anonymous_character_specificity\\\`\*\***

**\*\*\\\*\\\*Question:\\\*\\\*\*\*** How much visual individuality do anonymous figures retain while remaining non-portrait-like?

\\- \\\`low\\\`

\\- \\\`moderate\\\`

\\- \\\`high\\\`

\\- \\\`not_applicable\\\`

Possible contributors include hair silhouette, skin color, clothing, pose, and body shape.

**\*\*---\*\***

**\*\*## 5.19 \\\`group_visual_diversity\\\`\*\***

For multi-person images:

\\- \\\`not_applicable\\\`

\\- \\\`low\\\`

\\- \\\`moderate\\\`

\\- \\\`high\\\`

This is a group-level summary of observable differentiation across figures.

**\*\*---\*\***

**\*\*## 5.20 \\\`group_relationship_structure\\\`\*\***

For multi-person images:

\\- \\\`not_applicable\\\`

\\- \\\`cooperative\\\`

\\- \\\`competitive\\\`

\\- \\\`co-present_noninteractive\\\`

\\- \\\`shared_collective_action\\\`

\\- \\\`relational_pair_or_group\\\`

\\- \\\`uncertain\\\`

Examples from the discovery set include competitive play in Basketball and coordinated performance in Concert.

**\*\*---\*\***

**\*\*## 5.21 \\\`human_proportion_stylization\\\`\*\***

**\*\*\\\*\\\*Question:\\\*\\\*\*\*** How strongly are overall human proportions stylized?

\\- \\\`low\\\`

\\- \\\`moderate\\\`

\\- \\\`strong\\\`

\\- \\\`not_applicable\\\`

Use notes for recurring features such as relatively small heads or elongated limbs.

**\*\*---\*\***

**\*\*## 5.22 \\\`human_shape_language\\\`\*\***

**\*\*\\\*\\\*Question:\\\*\\\*\*\*** How are human forms constructed geometrically?

\\- \\\`mostly_geometric\\\`

\\- \\\`mostly_organic\\\`

\\- \\\`mixed_geometric_organic\\\`

\\- \\\`not_applicable\\\`

**\*\*---\*\***

**\*\*## 5.23 \\\`anatomical_responsiveness\\\`\*\***

**\*\*\\\*\\\*Question:\\\*\\\*\*\*** Does the illustration become more anatomically specific where action clarity requires it?

\\- \\\`low\\\`

\\- \\\`moderate\\\`

\\- \\\`high\\\`

\\- \\\`not_applicable\\\`

Examples include more articulated hands in Vote and Basketball or more responsive limb shapes in action-heavy figures.

**\*\*---\*\***

**\*\*## 5.24 \\\`human_detail_allocation\\\`\*\***

**\*\*\\\*\\\*Type:\\\*\\\*\*\*** multi-select

Allowed values:

\\- \\\`face\\\`

\\- \\\`hair\\\`

\\- \\\`hands\\\`

\\- \\\`limbs\\\`

\\- \\\`clothing\\\`

\\- \\\`occupational_accessories\\\`

\\- \\\`action_objects\\\`

\\- \\\`evenly_distributed\\\`

\\- \\\`minimal\\\`

This captures **\*\*\\\*\\\*where\\\*\\\*\*\*** human-related detail is spent.

**\*\*---\*\***

**\*\*# 6. Event & Semantic Logic\*\***

**\*\*## 6.1 \\\`action_structure\\\`\*\***

**\*\*\\\*\\\*Question:\\\*\\\*\*\*** What kind of action relationship is depicted?

**\*\*\\\*\\\*Type:\\\*\\\*\*\*** controlled value

\\- \\\`none\\\`

\\- \\\`single_actor_action\\\`

\\- \\\`human_object_interaction\\\`

\\- \\\`multi_actor_cooperative\\\`

\\- \\\`multi_actor_competitive\\\`

\\- \\\`collective_action\\\`

\\- \\\`object_or_environment_state\\\`

\\- \\\`mixed\\\`

This describes structural relationships, not the precise moment in time.

**\*\*---\*\***

**\*\*## 6.2 \\\`temporal_focus\\\`\*\***

**\*\*\\\*\\\*Question:\\\*\\\*\*\*** What event state or moment does the image choose?

\\- \\\`timeless_or_static\\\`

\\- \\\`prepared_state\\\`

\\- \\\`action_in_progress\\\`

\\- \\\`peak_action_moment\\\`

\\- \\\`aftermath_or_result\\\`

\\- \\\`uncertain\\\`

Definitions:

\\- \\\`prepared_state\\\` — objects or environment are arranged for imminent or ongoing use even if no active person is shown.

\\- \\\`action_in_progress\\\` — an activity is visibly underway without isolating its most critical instant.

\\- \\\`peak_action_moment\\\` — the image selects a particularly diagnostic, high-information instant within an action.

\\- \\\`aftermath_or_result\\\` — the visible state primarily communicates what happened after an action.

Examples:

\\- Barbecue → \\\`prepared_state\\\`.

\\- Shopping → \\\`action_in_progress\\\`.

\\- Bowling → \\\`peak_action_moment\\\`.

**\*\*---\*\***

**\*\*## 6.3 \\\`causal_structure\\\`\*\***

**\*\*\\\*\\\*Question:\\\*\\\*\*\*** Does understanding cause-and-effect among elements contribute to recognition?

\\- \\\`none\\\`

\\- \\\`weak_or_implied\\\`

\\- \\\`clear_single_link\\\`

\\- \\\`multi_step_chain\\\`

Examples include hand → ballot box in Vote and bowler → ball → pins in Bowling.

**\*\*---\*\***

**\*\*## 6.4 \\\`diagnostic_object_state\\\`\*\***

**\*\*\\\*\\\*Question:\\\*\\\*\*\*** Does an object's state carry semantic information beyond its identity?

**\*\*\\\*\\\*Type:\\\*\\\*\*\*** multi-select controlled values + short note

Use:

\\\`\\\`\\\`json

{

  "states": [

    "open_or_revealing_contents",

    "in_use",

    "loaded_or_filled"

  ],

  "note": "The open grill reveals food and active cooking."

}

\\\`\\\`\\\`

**\*\*\\\*\\\*Allowed values:\\\*\\\*\*\***

\\- \\\`neutral\\\`

\\- \\\`prepared\\\`

\\- \\\`in_use\\\`

\\- \\\`loaded_or_filled\\\`

\\- \\\`open_or_revealing_contents\\\`

\\- \\\`impact_or_transformed_state\\\`

Use an empty \\\`states\\\` list when no object state is semantically important.

Do **\*\*\\\*\\\*not\\\*\\\*\*\*** use a generic \\\`mixed\\\` code when several specific states apply; select all applicable states instead.

If an image contains a semantically important state that is not captured by the controlled values, describe it in \\\`note\\\` rather than inventing a one-off categorical label. Promote a new state value only if it recurs across references.

Examples:

\\- Barbecue → \\\`open_or_revealing_contents\\\` + \\\`in_use\\\` + \\\`loaded_or_filled\\\`.

\\- Delivery / Parcel → open cargo and loaded parcel-cart states can both carry information.

\\- Vote → \\\`in_use\\\` because the ballot is actively entering the slot.

\\- Bowling → \\\`impact_or_transformed_state\\\` because the pins are shown during/after impact.

**\*\*---\*\***

**\*\*## 6.5 \\\`motion_encoding\\\`\*\***

**\*\*\\\*\\\*Type:\\\*\\\*\*\*** multi-select

\\- \\\`none\\\`

\\- \\\`body_pose\\\`

\\- \\\`human_object_interaction\\\`

\\- \\\`object_arrangement\\\`

\\- \\\`contact_geometry\\\`

\\- \\\`abstract_action_marks\\\`

\\- \\\`structural_directionality\\\`

Do not treat general diagonal composition as motion unless it actually helps communicate movement/action.

**\*\*---\*\***

**\*\*## 6.6 \\\`implied_human_presence\\\`\*\***

**\*\*\\\*\\\*Question:\\\*\\\*\*\*** Only when **\*\*\\\*\\\*no person is visibly depicted\\\*\\\*\*\***, does the drawn state of the scene nevertheless suggest that people are present, were recently present, or are socially implicated?

**\*\*\\\*\\\*Type:\\\*\\\*\*\*** controlled value

\\- \\\`not_applicable\\\` — one or more people or human body parts are visibly represented.

\\- \\\`none\\\` — no visible people and no meaningful evidence of current/recent human activity or participants.

\\- \\\`indirect\\\` — people or social relationships are conceptually implied, but the scene provides little evidence of active or recent physical use.

\\- \\\`strong\\\` — object states strongly suggest human use, preparation, activity, or an event currently/recently taking place.

**\*\*\\\*\\\*Operational rule:\\\*\\\*\*\*** Only assign \\\`none\\\`, \\\`indirect\\\`, or \\\`strong\\\` when \\\`human_presence = none\\\`.

This field is **\*\*\\\*\\\*not\\\*\\\*\*\*** asking whether the real-world activity normally involves people. It asks what evidence exists **\*\*\\\*\\\*inside the depicted scene\\\*\\\*\*\***.

Examples:

\\- Chinese New Year decorative lantern arrangement → \\\`none\\\`.

\\- Wedding symbolic invitation / paired-glasses composition → \\\`indirect\\\`.

\\- Valentine’s Day letter/envelope/flowers → \\\`indirect\\\`, because the objects imply a sender/recipient relationship without showing active use.

\\- Thanksgiving turkey + autumn leaves → \\\`none\\\`, because the image is a symbolic holiday composition rather than evidence of recent human activity.

\\- Barbecue open grill + cooking food + cups + condiments + prepared table → \\\`strong\\\`.

\\- Vote → \\\`not_applicable\\\`, because a hand and forearm are visibly represented.

A separate future field such as \\\`implied_offscreen_participants\\\` may be introduced only if recurring evidence shows that visible-person scenes systematically imply additional off-screen participants.

**\*\*---\*\***

**\*\*## 6.7 \\\`narrative_structure\\\`\*\***

**\*\*\\\*\\\*Question:\\\*\\\*\*\*** Does the image imply a story, micro-situation, or sequence?

\\- \\\`none\\\`

\\- \\\`micro_situation\\\`

\\- \\\`implied_sequence\\\`

\\- \\\`strong_sequence\\\`

\\- \\\`processional\\\`

This is separate from motion. A scene can imply narrative without depicting speed or movement.

**\*\*---\*\***

**\*\*# 7. Environment & Space\*\***

**\*\*## 7.1 \\\`environment_strategy\\\`\*\***

**\*\*\\\*\\\*Question:\\\*\\\*\*\*** How is the literal setting handled?

\\- \\\`omitted\\\`

\\- \\\`abstract\\\`

\\- \\\`partial_context\\\`

\\- \\\`semantic_environment\\\`

\\- \\\`simplified_literal\\\`

\\- \\\`narrative_environment\\\`

Definitions:

\\- \\\`omitted\\\` — no meaningful literal setting.

\\- \\\`abstract\\\` — background/space is primarily nonliteral graphic structure.

\\- \\\`partial_context\\\` — only selected setting cues are retained.

\\- \\\`semantic_environment\\\` — concept-diagnostic objects effectively construct the world rather than depict a normal setting.

\\- \\\`simplified_literal\\\` — recognizable real setting retained but strongly simplified.

\\- \\\`narrative_environment\\\` — setting contributes to a story or sequence, not merely recognition.

**\*\*\\\*\\\*Operational distinction:\\\*\\\*\*\*** Code the environment only when the illustration actually represents a setting or spatial world. A collection of concept-related objects does **\*\*\\\*\\\*not\\\*\\\*\*\*** become a \\\`semantic_environment\\\` merely because those objects jointly communicate the concept.

\\- Cooking → \\\`omitted\\\`: knife, vegetables, herbs, and cut ingredients are evenly art-directed across a flat graphic field; no kitchen, countertop, cutting board, or other setting is represented.

\\- Art → \\\`semantic_environment\\\`: enlarged canvases, easels, brushes, and painting structures effectively construct the world in which the painter acts.

\\- Camping → \\\`simplified_literal\\\`: trees, mountains, ground, tent, and campfire form a coherent but highly simplified outdoor setting.

Use \\\`abstract\\\` when the space itself contains meaningful nonliteral graphic structure. Use \\\`omitted\\\` when no meaningful setting is depicted, even if diagnostic objects fill much of the frame.

**\*\*---\*\***

**\*\*## 7.2 \\\`environment_role\\\`\*\***

**\*\*\\\*\\\*Question:\\\*\\\*\*\*** What semantic/compositional job does the environment perform?

**\*\*\\\*\\\*Type:\\\*\\\*\*\*** multi-select

\\- \\\`none\\\`

\\- \\\`recognition_anchor\\\`

\\- \\\`recognition_support\\\`

\\- \\\`disambiguation\\\`

\\- \\\`action_support\\\`

\\- \\\`narrative_context\\\`

\\- \\\`mood_or_atmosphere\\\`

\\- \\\`structural_backdrop\\\`

Examples:

\\- Climbing wall → recognition anchor + action support

\\- Bowling lane → recognition support + action support

\\- Barbecue outdoor setting → disambiguation

\\- Delivery neighborhood → narrative context

\\\`recognition_anchor\\\` means the environment itself is one of the major diagnostic carriers of the concept. \\\`recognition_support\\\` means the environment materially reinforces recognition but is not itself a co-primary anchor. \\\`disambiguation\\\` means the environment mainly resolves an otherwise ambiguous action/object reading.

\\\`narrative_context\\\` may include an environment functioning as an origin, destination, or stage in a sequence. Do not create narrower codes such as \\\`narrative_destination\\\` unless that distinction recurs across enough references to justify a universal field.

**\*\*---\*\***

**\*\*## 7.3 \\\`spatial_coherence\\\`\*\***

**\*\*\\\*\\\*Question:\\\*\\\*\*\*** Does the image behave like one plausible physical world or a conceptual arrangement?

\\- \\\`literal_physical_world\\\`

\\- \\\`stylized_physical_world\\\`

\\- \\\`conceptual_collage\\\`

\\- \\\`symbolic_or_diagrammatic_space\\\`

\\- \\\`mixed\\\`

Cinema is a strong conceptual-collage example. Cooking and Karate are useful \\\`symbolic_or_diagrammatic_space\\\` examples: literal objects or people are arranged as an art-directed graphic field or pose lineup rather than as one naturalistic shared moment. Camping is a \\\`stylized_physical_world\\\` example.

**\*\*---\*\***

**\*\*## 7.4 \\\`view_angle\\\`\*\***

**\*\*\\\*\\\*Question:\\\*\\\*\*\*** What is the dominant camera/view direction?

\\- \\\`frontal\\\`

\\- \\\`side\\\`

\\- \\\`three_quarter\\\`

\\- \\\`overhead\\\`

\\- \\\`oblique\\\`

\\- \\\`mixed\\\`

\\- \\\`indeterminate\\\`

Use \\\`viewpoint_note\\\` for unusual task-specific viewpoints.

**\*\*---\*\***

**\*\*## 7.5 \\\`framing_scale\\\`\*\***

\\- \\\`wide\\\`

\\- \\\`medium\\\`

\\- \\\`close_up\\\`

\\- \\\`extreme_close_up\\\`

\\- \\\`mixed\\\`

This captures camera framing, not object scale exaggeration.

**\*\*---\*\***

**\*\*## 7.6 \\\`perspective_strategy\\\`\*\***

\\- \\\`minimal_or_flat\\\`

\\- \\\`layered_without_strong_perspective\\\`

\\- \\\`conventional_perspective\\\`

\\- \\\`perspective_driven_exaggeration\\\`

\\- \\\`mixed\\\`

Bowling is the clearest example of perspective-driven exaggeration in the discovery set.

**\*\*---\*\***

**\*\*## 7.7 \\\`scale_source\\\`\*\***

**\*\*\\\*\\\*Question:\\\*\\\*\*\*** Why do important elements appear at the sizes they do?

\\- \\\`mostly_naturalistic\\\`

\\- \\\`semantic_exaggeration\\\`

\\- \\\`perspective_based\\\`

\\- \\\`framing_based\\\`

\\- \\\`visual_equivalence\\\`

\\- \\\`mixed\\\`

Definitions:

\\- \\\`semantic_exaggeration\\\` — importance drives size beyond physical realism.

\\- \\\`perspective_based\\\` — size contrast primarily follows viewpoint/depth.

\\- \\\`framing_based\\\` — apparent scale comes mainly from close cropping.

\\- \\\`visual_equivalence\\\` — unlike real objects are intentionally normalized toward similar visual prominence.

**\*\*\\\*\\\*Operational note:\\\*\\\*\*\*** Do not introduce a generic \\\`composition_based\\\` value. Ask what specifically produces the scale choice: semantic importance, perspective, framing, visual equivalence, or mostly naturalistic size. Use \\\`mixed\\\` only when more than one of these is materially important.

**\*\*---\*\***

**\*\*## 7.8 \\\`depth_strategy\\\`\*\***

**\*\*\\\*\\\*Question:\\\*\\\*\*\*** How is pictorial depth constructed?

**\*\*\\\*\\\*Type:\\\*\\\*\*\*** primary controlled value + optional secondary

**\*\*\\\*\\\*Allowed values:\\\*\\\*\*\***

\\- \\\`flat\\\` — elements largely occupy one graphic plane with little meaningful near/far separation.

\\- \\\`shallow_overlap\\\` — depth is suggested mainly through overlap or slight separation among elements that remain spatially close.

\\- \\\`layered_depth\\\` — the image establishes distinct foreground, middle, and/or background planes primarily through relative scale, placement, occlusion, or environmental ordering, without requiring strong perspective construction.

\\- \\\`perspective_driven\\\` — viewpoint and perspective create strong recession or near/far scale contrast.

\\- \\\`collage_depth\\\` — overlap and scale create layering among elements that do not form one physically coherent world.

\\- \\\`mixed\\\` — more than one depth strategy is substantially important.

**\*\*\\\*\\\*Operational note:\\\*\\\*\*\*** \\\`depth_strategy\\\` describes **\*\*\\\*\\\*how\\\*\\\*\*\*** the image constructs depth. It does not describe how many spatial planes are present or how far apart those planes feel.

**\*\*\\\*\\\*Examples:\\\*\\\*\*\***

\\- Climbing → likely \\\`shallow_overlap\\\`

\\- Delivery / Parcel → \\\`layered_depth\\\`

\\- Bowling → \\\`perspective_driven\\\`

\\- Cinema → \\\`collage_depth\\\`

**\*\*---\*\***

**\*\*## 7.9 \\\`depth_layer_count\\\`\*\***

**\*\*\\\*\\\*Question:\\\*\\\*\*\*** How many perceptually distinct spatial planes are established?

**\*\*\\\*\\\*Type:\\\*\\\*\*\*** integer, or \\\`uncertain\\\`

A **\*\*\\\*\\\*depth layer\\\*\\\*\*\*** is a perceptually distinct spatial plane containing one or more meaningful elements. Count spatial planes, **\*\*\\\*\\\*not individual overlapping objects\\\*\\\*\*\***.

Elements that appear attached to, resting on, or immediately adjacent to the same surface may belong to the same effective depth layer.

Examples of possible layers include:

\\- foreground action cluster;

\\- middle-ground environmental elements;

\\- distant background or sky field.

**\*\*\\\*\\\*Important:\\\*\\\*\*\*** Layer count measures the **\*\*\\\*\\\*structural segmentation of depth\\\*\\\*\*\***, not the total perceived physical distance in the scene.

Two illustrations may both have two layers while producing very different depth spans.

Because this measure can be subjective, use \\\`uncertain\\\` when layer boundaries are not perceptually stable.

**\*\*---\*\***

**\*\*## 7.10 \\\`depth_span\\\`\*\***

**\*\*\\\*\\\*Question:\\\*\\\*\*\*** How much perceived near-to-far spatial distance does the composition span?

**\*\*\\\*\\\*Type:\\\*\\\*\*\*** controlled ordinal

\\- \\\`minimal\\\` — elements behave almost like a single graphic plane; little meaningful physical separation is perceived.

\\- \\\`shallow\\\` — some near/far separation is visible, but the meaningful elements remain spatially close.

\\- \\\`moderate\\\` — a clear foreground/background relationship is established.

\\- \\\`deep\\\` — the scene implies substantial physical separation between its nearest and farthest meaningful elements.

\\- \\\`very_deep\\\` — strong near/far separation is a dominant compositional effect, often supported by major scale contrast, recession, or perspective.

**\*\*\\\*\\\*Operational note:\\\*\\\*\*\*** Judge \\\`depth_span\\\` from the perceived separation between the nearest and farthest **\*\*\\\*\\\*meaningful semantic elements\\\*\\\*\*\***, considering cues such as:

\\- relative scale difference;

\\- overlap and occlusion;

\\- perspective convergence;

\\- foreground/background placement;

\\- whether elements appear attached to the same surface;

\\- whether a recognizable environmental distance is implied.

Do not estimate literal meters. This is an ordinal abstraction of perceived physical depth.

**\*\*\\\*\\\*Key distinction:\\\*\\\*\*\***

\\- \\\`depth_strategy\\\` = how the illustration creates depth.

\\- \\\`depth_layer_count\\\` = how many spatial planes are established.

\\- \\\`depth_span\\\` = how much perceived physical distance those planes appear to span.

For example, Climbing may use \\\`shallow_overlap\\\` with a shallow span because the climber remains very close to the wall, while Delivery may use \\\`layered_depth\\\` with a deep span because the foreground worker/truck are perceptually separated from the residential background. Bowling may use \\\`perspective_driven\\\` depth with a very deep span.

**\*\*---\*\***

**\*\*## 7.11 \\\`cropping_strength\\\`\*\***

\\- \\\`none\\\`

\\- \\\`light\\\`

\\- \\\`moderate\\\`

\\- \\\`strong\\\`

Code the overall use of frame-edge cropping, not one incidental clipped pixel.

**\*\*---\*\***

**\*\*## 7.12 \\\`edge_continuation\\\`\*\***

**\*\*\\\*\\\*Question:\\\*\\\*\*\*** Do major forms intentionally continue beyond the frame, implying a larger world?

\\- \\\`none\\\`

\\- \\\`limited\\\`

\\- \\\`strong\\\`

**\*\*---\*\***

**\*\*# 8. Composition & Visual Hierarchy\*\***

**\*\*## 8.1 \\\`composition_structure\\\`\*\***

**\*\*\\\*\\\*Type:\\\*\\\*\*\*** short controlled-ish phrase / concise free text

Describe the dominant organization using reusable language where possible, for example:

\\- \\\`asymmetric focal cluster\\\`

\\- \\\`horizontal procession\\\`

\\- \\\`three-zone layout\\\`

\\- \\\`foreground framing\\\`

\\- \\\`central anchor with supporting objects\\\`

\\- \\\`diagonal collage\\\`

\\- \\\`distributed suspended arrangement\\\`

\\- \\\`right-weighted action cluster\\\`

Do not invent a unique poetic label when an existing structural phrase fits.

**\*\*---\*\***

**\*\*## 8.2 \\\`visual_weight_distribution\\\`\*\***

\\- \\\`centered\\\`

\\- \\\`left_weighted\\\`

\\- \\\`right_weighted\\\`

\\- \\\`top_weighted\\\`

\\- \\\`bottom_weighted\\\`

\\- \\\`evenly_distributed\\\`

\\- \\\`multi_clustered\\\`

\\- \\\`asymmetrically_balanced\\\`

\\- \\\`mixed\\\`

Use a short note if the image combines several patterns.

**\*\*---\*\***

**\*\*## 8.3 \\\`salience_structure\\\`\*\***

**\*\*\\\*\\\*Question:\\\*\\\*\*\*** How is semantic/visual importance distributed?

\\- \\\`single_dominant_anchor\\\`

\\- \\\`dominant_anchor_with_support\\\`

\\- \\\`dual_anchor\\\`

\\- \\\`distributed_salience\\\`

\\- \\\`multi_cluster\\\`

\\- \\\`uncertain\\\`

Optionally record:

\\- \\\`primary_salience_anchor\\\`

\\- \\\`secondary_salience_elements\\\`

\\- \\\`large_quiet_elements\\\`

This is particularly useful when a large pale structure provides mass without being the semantic focus.

**\*\*---\*\***

**\*\*## 8.4 \\\`negative_space_strategy\\\`\*\***

\\- \\\`none_or_minimal\\\`

\\- \\\`passive\\\`

\\- \\\`balancing\\\`

\\- \\\`directional_lead_space\\\`

\\- \\\`isolation_or_emphasis\\\`

\\- \\\`mixed\\\`

Definitions:

\\- \\\`passive\\\` — empty space exists but has no strong apparent function.

\\- \\\`balancing\\\` — empty space counterbalances a dense cluster.

\\- \\\`directional_lead_space\\\` — empty space lies in the direction of movement/action.

\\- \\\`isolation_or_emphasis\\\` — empty space isolates a focal element.

**\*\*---\*\***

**\*\*## 8.5 \\\`directional_flow_strength\\\`\*\***

\\- \\\`none\\\`

\\- \\\`weak\\\`

\\- \\\`moderate\\\`

\\- \\\`strong\\\`

Optionally pair with \\\`directional_flow_note\\\`, such as \\\`right-to-left lead space\\\` or \\\`upper-left to lower-right diagonal\\\`.

**\*\*---\*\***

**\*\*## 8.6 \\\`structural_motif\\\`\*\***

Use:

\\\`\\\`\\\`json

{

  "present": true,

  "motif": "toy train"

}

\\\`\\\`\\\`

or \\\`present: false\\\`.

A structural motif is an organizing device for the composition, not merely a repeated detail.

**\*\*---\*\***

**\*\*## 8.7 \\\`repetition_and_rhythm\\\`\*\***

**\*\*\\\*\\\*Question:\\\*\\\*\*\*** How strongly does repetition contribute to the image?

\\- \\\`none\\\`

\\- \\\`low\\\`

\\- \\\`moderate\\\`

\\- \\\`strong\\\`

Optional \\\`repetition_role\\\` may be multi-select:

\\- \\\`structural\\\`

\\- \\\`semantic\\\`

\\- \\\`functional\\\`

\\- \\\`decorative\\\`

Examples include repeated lanterns, train cars, film-strip perforations, and repeated cart-grid structure.

**\*\*---\*\***

**\*\*## 8.8 \\\`scene_density\\\`\*\***

\\- \\\`low\\\`

\\- \\\`moderate\\\`

\\- \\\`high\\\`

Use only these three density levels; put borderline nuance in \\\`density_distribution\\\` or an evidence note rather than creating hybrid values.

Optional \\\`density_distribution\\\`:

\\- \\\`even\\\`

\\- \\\`concentrated\\\`

\\- \\\`multi_clustered\\\`

\\- \\\`full_frame\\\`

**\*\*---\*\***

**\*\*# 9. Visual Language\*\***

**\*\*## 9.1 \\\`color_functions\\\`\*\***

**\*\*\\\*\\\*Type:\\\*\\\*\*\*** multi-select

\\- \\\`semantic_association\\\`

\\- \\\`salience_hierarchy\\\`

\\- \\\`participant_grouping\\\`

\\- \\\`individual_differentiation\\\`

\\- \\\`atmosphere_or_mood\\\`

\\- \\\`foreground_background_separation\\\`

\\- \\\`context_suppression\\\`

\\- \\\`decorative_balance\\\`

Definitions:

\\- \\\`participant_grouping\\\` — color visually binds people or objects into the same team, side, role, or semantic group.

\\- \\\`individual_differentiation\\\` — color helps keep people or semantic actors visually distinct from one another within the same scene.

Examples:

\\- Chinese New Year → strong semantic association through a red-dominant palette.

\\- Basketball → participant grouping through uniform colors.

\\- Concert → individual differentiation through distinct performer color identities.

\\- Delivery / Shopping → background/context can be palette-compressed so focal objects remain salient.

**\*\*---\*\***

**\*\*## 9.2 \\\`shape_language\\\`\*\***

\\- \\\`mostly_geometric\\\`

\\- \\\`mostly_organic\\\`

\\- \\\`mixed_geometric_organic\\\`

Optional note may identify dominant forms such as blocky, rounded, faceted, tapered, or irregular.

**\*\*---\*\***

**\*\*## 9.3 \\\`detail_allocation\\\`\*\***

**\*\*\\\*\\\*Question:\\\*\\\*\*\*** Where is additional visual detail deliberately spent?

**\*\*\\\*\\\*Type:\\\*\\\*\*\*** multi-select

\\- \\\`diagnostic_objects\\\`

\\- \\\`action_critical_elements\\\`

\\- \\\`occupational_cues\\\`

\\- \\\`primary_salience_anchor\\\`

\\- \\\`characteristic_repeated_structure\\\`

\\- \\\`human_identity_cues\\\`

\\- \\\`environmental_context\\\`

\\- \\\`uniform_minimal_detail\\\`

This is image-level. Human-specific detail can additionally be coded in \\\`human_detail_allocation\\\`.

**\*\*---\*\***

**\*\*## 9.4 \\\`characteristic_detail_retention\\\`\*\***

**\*\*\\\*\\\*Question:\\\*\\\*\*\*** To what degree are small or repetitive details preserved because they are essential to object recognition?

\\- \\\`none\\\`

\\- \\\`low\\\`

\\- \\\`moderate\\\`

\\- \\\`strong\\\`

Optional note should name the retained feature, e.g. film perforations, cart grid, reel circles, or functional numerals.

**\*\*---\*\***

**\*\*## 9.5 \\\`nonliteral_graphic_cues\\\`\*\***

**\*\*\\\*\\\*Type:\\\*\\\*\*\*** multi-select

\\- \\\`none\\\`

\\- \\\`informational\\\`

\\- \\\`symbolic\\\`

\\- \\\`atmospheric\\\`

\\- \\\`action_or_energy\\\`

\\- \\\`decorative\\\`

Examples:

\\- Athletic Jumping measurement/tick cue → informational

\\- Concert sound/energy marks → action_or_energy

\\- Cinema light-beam forms → atmospheric

Use only when the cue is meaningfully nonliteral.

**\*\*---\*\***

**\*\*## 9.6 \\\`symbolic_information_integration\\\`\*\***

**\*\*\\\*\\\*Question:\\\*\\\*\*\*** How strongly do symbolic or informational elements contribute to meaning?

\\- \\\`none\\\`

\\- \\\`low\\\`

\\- \\\`moderate\\\`

\\- \\\`strong\\\`

This summarizes semantic importance, whereas \\\`nonliteral_graphic_cues\\\` specifies cue type.

**\*\*---\*\***

**\*\*## 9.7 \\\`decorative_abstraction\\\`\*\***

\\- \\\`none\\\`

\\- \\\`low\\\`

\\- \\\`moderate\\\`

\\- \\\`strong\\\`

Use for nonliteral shapes whose main role is compositional, atmospheric, or decorative rather than literal depiction.

**\*\*---\*\***

**\*\*## 9.8 \\\`text_numeral_symbol_usage\\\`\*\***

**\*\*\\\*\\\*Type:\\\*\\\*\*\*** multi-select

\\- \\\`none\\\`

\\- \\\`functional_numerals\\\`

\\- \\\`object_native_symbols_or_icons\\\`

\\- \\\`readable_text\\\`

\\- \\\`pseudo_text_or_handwriting\\\`

\\\`pseudo_text_or_handwriting\\\` means non-readable marks are visibly designed to function like writing, handwriting, or textual content without conveying actual readable language. This is different from arbitrary decorative squiggles.

Examples:

\\- Valentine’s Day → \\\`pseudo_text_or_handwriting\\\` + \\\`object_native_symbols_or_icons\\\` (heart seal).

\\- Basketball → \\\`functional_numerals\\\`.

\\- Doctor → \\\`object_native_symbols_or_icons\\\` on the badge.

Only code visible marks. Do not infer unreadable shapes as text unless their visual organization clearly functions as text-like content.

**\*\*---\*\***

**\*\*# 10. Fields retained only in discovery records\*\***

The following kinds of observations should generally **\*\*\\\*\\\*not\\\*\\\*\*\*** become universal normalized fields unless repeated evidence later justifies promotion:

\\- shopping-cart-specific structure

\\- groceries/inventory breakdown

\\- badge-specific details

\\- film-strip-specific construction

\\- food-and-serving breakdown

\\- impact-structure details tied to one sport

\\- measurement-device details tied to one activity

\\- semantic bridge for one particular object

\\- relationship-sensitive abstraction hypotheses

These remain useful evidence in the rich discovery JSONs.

**\*\*---\*\***

**\*\*# 11. Likely global style invariants — verify, do not repeatedly code by default\*\***

Across the discovery set, several rendering traits currently show very little variation:

\\- flat color regions;

\\- little or no gradient;

\\- little or no surface texture;

\\- little or no realistic shadowing;

\\- low material realism;

\\- simplified geometric or geometric-organic forms.

Because these properties appear close to corpus-wide constants, they should be tracked as **\*\*\\\*\\\*candidate style principles\\\*\\\*\*\*** rather than repeated in every normalized annotation. If later references violate them meaningfully, the codebook can be revised.

**\*\*---\*\***

**\*\*# 12. Recommended normalized annotation shape\*\***

This is a structural example only; it is **\*\*\\\*\\\*not an annotation of any study image\\\*\\\*\*\***.

\\\`\\\`\\\`json

{

  "reference_id": "...",

  "concept": "...",

  "codebook_version": "0.5",

  "representation": {

    "representation_strategy": {

      "primary": "...",

      "secondary": null

    },

    "recognition_structure": "...",

    "recognition_anchor": {

      "primary": "...",

      "supporting": []

    },

    "recognition_specificity": "...",

    "semantic_scope": "...",

    "representation_optionality": "..."

  },

  "people_and_social": {

    "human_presence": "...",

    "human_count": null,

    "human_role": {

      "primary": "...",

      "secondary": null

    },

    "body_visibility": "...",

    "figure_orientation": "...",

    "face_visibility": "...",

    "facial_specificity": "...",

    "people": [],

    "skin_color_variation": "...",

    "hair_color_variation": "...",

    "hairstyle_variation": "...",

    "clothing_strategy": "...",

    "clothing_variation": "...",

    "inter_person_clothing_structure": "...",

    "clothing_relationship_function": [],

    "body_shape_variation": "...",

    "pose_variation": "...",

    "anonymous_character_specificity": "...",

    "group_visual_diversity": "...",

    "group_relationship_structure": "...",

    "human_proportion_stylization": "...",

    "human_shape_language": "...",

    "anatomical_responsiveness": "...",

    "human_detail_allocation": []

  },

  "event_logic": {

    "action_structure": "...",

    "temporal_focus": "...",

    "causal_structure": "...",

    "diagnostic_object_state": {

      "states": [],

      "note": null

    },

    "motion_encoding": [],

    "implied_human_presence": "...",

    "narrative_structure": "..."

  },

  "environment_and_space": {

    "environment_strategy": "...",

    "environment_role": [],

    "spatial_coherence": "...",

    "view_angle": "...",

    "viewpoint_note": null,

    "framing_scale": "...",

    "perspective_strategy": "...",

    "scale_source": "...",

    "depth_strategy": {

      "primary": "...",

      "secondary": null

    },

    "depth_layer_count": null,

    "depth_span": "...",

    "cropping_strength": "...",

    "edge_continuation": "..."

  },

  "composition": {

    "composition_structure": "...",

    "visual_weight_distribution": "...",

    "salience_structure": "...",

    "primary_salience_anchor": "...",

    "secondary_salience_elements": [],

    "large_quiet_elements": [],

    "negative_space_strategy": "...",

    "directional_flow_strength": "...",

    "directional_flow_note": null,

    "structural_motif": {

      "present": false,

      "motif": null

    },

    "repetition_and_rhythm": "...",

    "repetition_role": [],

    "scene_density": "...",

    "density_distribution": "..."

  },

  "visual_language": {

    "color_functions": [],

    "shape_language": "...",

    "detail_allocation": [],

    "characteristic_detail_retention": "...",

    "characteristic_detail_note": null,

    "nonliteral_graphic_cues": [],

    "symbolic_information_integration": "...",

    "decorative_abstraction": "...",

    "text_numeral_symbol_usage": []

  },

  "evidence_notes": [],

  "confidence_notes": []

}

\\\`\\\`\\\`

**\*\*---\*\***

**\*\*# 13. Revision notes for v0.4\*\***

Version 0.4 incorporates the first annotation-pilot findings from Art, Climbing, Bowling, Valentine’s Day, and Thanksgiving.

Key changes:

\\- clarified secondary representation-strategy use, with Art and Climbing as examples;

\\- added \\\`dominant_anchor_with_support\\\` to \\\`recognition_structure\\\` after the Thanksgiving pilot exposed a pattern not captured cleanly by \\\`concentrated\\\` or distributed codes;

\\- added controlled-vocabulary discipline to prevent ad hoc hybrid values during systematic coding;

\\- added per-person \\\`facial_hair\\\` and \\\`activity_accessories\\\` after Bowling and Climbing exposed these as useful observable character details;

\\- added \\\`recognition_support\\\` to \\\`environment_role\\\`, separating supportive context from a primary recognition anchor or pure disambiguation;

\\- clarified how to handle novel \\\`diagnostic_object_state\\\` observations without proliferating one-off codes;

\\- expanded \\\`implied_human_presence\\\` examples using Valentine’s Day and Thanksgiving;

\\- replaced \\\`abstract_text_like_marks\\\` with the more operational \\\`pseudo_text_or_handwriting\\\` based on the Valentine’s Day pilot;

\\- corrected inconsistencies in the normalized schema for \\\`recognition_anchor\\\`, \\\`diagnostic_object_state\\\`, and clothing-relationship fields.

**\*\*---\*\***

**\*\*# 14. Revision notes for v0.5\*\***

Version 0.5 incorporates the unseen-reference stress test using American Football, Cooking, Camping, and Karate.

Key changes:

\\- added optional per-person \\\`semantic_role\\\` so multi-person scenes can preserve which figure is the primary, supporting, occupational, relational, contextual, or collective carrier;

\\- added an annotation principle requiring precise open-text clothing and accessory descriptions when visible differences matter for downstream art direction or generation;

\\- clarified that activity accessories should be named unambiguously, e.g. \\\`football helmet with helmet face mask\\\` rather than the ambiguous \\\`face mask\\\`;

\\- clarified \\\`environment_strategy\\\`: concept-related objects do not constitute a semantic environment unless they actually construct a setting or world;

\\- added Cooking as a canonical \\\`environment_strategy = omitted\\\` and \\\`spatial_coherence = symbolic_or_diagrammatic_space\\\` example;

\\- added Camping as a canonical \\\`simplified_literal\\\` / \\\`stylized_physical_world\\\` example and Karate as a pose-lineup example of \\\`symbolic_or_diagrammatic_space\\\`;

\\- retained the existing six-family taxonomy and controlled vocabularies because the four unseen references did not expose a new top-level conceptual gap.

**\*\*---\*\***

**\*\*# 15. Pilot and revision protocol\*\***

Before freezing the codebook:

1\\. Annotate a deliberately varied pilot set, beginning with roughly five previously studied references and expanding only as needed to stress-test under-exercised fields.

2\\. Record every point where a value feels forced, ambiguous, redundant, or missing.

3\\. Revise allowed values only when the problem recurs or exposes a real conceptual gap.

4\\. Back-code the remaining discovery references.

5\\. Test the revised codebook on several references that were **\*\*\\\*\\\*not\\\*\\\*\*\*** part of the discovery set.

6\\. Freeze a version only after new references can be represented without frequent schema expansion.

7\\. Keep a held-out validation set for testing whether later principles generalize.

Version 0.5 is the final provisional cleanup after back-coding and four-category unseen stress testing. If review of this revision does not reveal a substantive inconsistency, freeze the schema as \\\`1.0\\\` for systematic coding. After freezing, log later edge cases rather than changing controlled vocabularies casually; revise the version only when a repeated or consequential conceptual gap appears.