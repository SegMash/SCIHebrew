# Hebrew Translation Review — Examples & Pitfalls

Concrete examples drawn from `output_kq1/messages.json`. Use them to calibrate
what counts as "awkward" and what passes.

## Issue categories with real examples

### 1. Cultural / religious mismatch
The Hebrew word carries cultural baggage that doesn't fit the English source.

| # | EN | Current HE | Why it's wrong | Better |
|---|----|------------|---------------|--------|
| 499 | `fairy godmother` | `פיה סנדקית` | `סנדקית` is the Jewish role of a baby's godmother at a brit/baptism. Nobody in Hebrew calls a fairy that. | `פיה טובה` (already used in #249, #251, #252) or `פיה שומרת` |

Other typical traps: "Sabbath", "godfather", "communion", "pilgrim" — anything
that maps to a specific religious institution.

### 2. Wrong word choice for the visual / context
The dictionary translation is technically a synonym but doesn't fit what is
being described.

| # | EN | Current HE | Why it's wrong | Better |
|---|----|------------|---------------|--------|
| 879 | `In this large cavern, there is a slimy dead dragon.` | `במערה הגדולה הזו, יש דרקון מת ורירי.` | `רירי` describes a snail or jellyfish, not a corpse. Dragons aren't naturally slimy; here the dragon is *covered in slime* from rotting. | `דרקון מת ומכוסה ריר` or `דרקון מת ודביק` |
| 1028 | `there's a dark opening leading into the mountain itself.` | `יש פתח כהה המוביל אל תוך ההר עצמו.` | `כהה` means "dark in color" (dark blue, dark hair). For an ominous opening into a mountain the meaning is atmospheric/sinister — `אפל`. The same file uses `אפלה` correctly in #11468 (`באפלת המערה`). | `יש פתח אפל המוביל אל תוך ההר עצמו.` |
| 1552 | `the troubled realm of Daventry` | `בממלכה המוטרדת של דבנטרי` | `מוטרד` ("bothered/preoccupied") applies to **people**, not to a place or institution. A kingdom doesn't get bothered — it suffers, is afflicted, or is in distress. Also, inserting an adjective between a noun and its `של`-modifier (`ממלכה ... של דבנטרי`) is heavy syntax. | `בממלכת דבנטרי השרויה בצרה` (direct smikhut + adjective phrase). Other valid choices: `הסובלת`, `הדוויה`, `השסועה`. |

**"Troubled / afflicted place" cheat sheet** — when EN applies emotional adjectives
to a *place or institution* (`troubled realm`, `weary city`, `restless land`),
don't use the adjective form normally reserved for people. Translate to a
state-of-being phrase:
- `שרוי בצרה` / `שרויה בצרה` — beset by trouble (default for "troubled")
- `סובל` / `סובלת` — suffering
- `דווי` / `דוויה` — ailing (literary)
- `שסוע` / `שסועה` — torn (suggests internal strife)
- ❌ `מוטרד` / `מוטרדת` — only for people who are *worried/preoccupied*

**Hebrew "dark" cheat sheet** — pick the right word:
- `חשוך` / `חושך` — actual physical lack of light (a dark cave, "it's dark in here"). Default for `dark` describing rooms, caves, wells, nights.
- `כהה` — dark in color (dark hair, dark fabric, dark blue). Only for visual color, never atmosphere.
- `אפל` / `אפלה` — gloomy, ominous, sinister. Right for fantasy `dark` describing portals, omens, evil, mysterious openings, foreboding places.
- `אופל` — noun form ("the gloom"), used like `באופל הלילה`.

### 3. Redundancy / pleonasm
Two Hebrew words back-to-back that mean the same thing.

| # | EN | Current HE | Why it's wrong | Better |
|---|----|------------|---------------|--------|
| 56 | `dwarf` | `גמד ננס` | `גמד` already means dwarf; `ננס` means midget. Together it reads like "dwarfish midget". | `גמד` |

### 4. Grammar / missing verb / agreement
The Hebrew is malformed or doesn't agree in gender/number.

| # | EN | Current HE | Why it's wrong | Better |
|---|----|------------|---------------|--------|
| 2 | `Looks like you had a bad fall this spring.` | `נראה שאחרי נפילה רעה באביב הזה.` | `שאחרי` ("that after") is dangling — there's no main verb. The translator probably meant "had". | `נראה שעברת נפילה רעה באביב הזה.` |
| 882 | `The dragon's still got it.` | `הדרקון עדיין מחזיק בזה.` | `מחזיק בזה` is wooden literal. The "it" refers to the magic mirror (`מראה`, feminine), so even keeping the verb it should be `בה`. | `המראה עדיין אצל הדרקון` |

#### Logical connectors — `אבל`, `על אף ש`, `מאחר ש`

English connectors don't always map 1-to-1 to Hebrew. The AI translator
tends to use `אבל ↔ but` and `על אף ש ↔ despite` mechanically, even when
the underlying logic doesn't fit. Watch for these:

- **`אבל`** introduces a **contrast** — a *positive* clause leading to a
  *negative* outcome (or vice versa). When both clauses are negative (or
  both positive), use `ו` instead.
  - ❌ `אתה נראה ליצורים מסוכנים, אבל הטבעת נעלמה.` (both bad → use `ו`)
  - ✅ `אתה רץ מהר, אבל לא הספקת.` (positive expectation + negative outcome)
- **`על אף ש`** ("despite") is **concessive** — the second clause happens
  *contrary* to the first. Don't use for causal links.
  - ❌ `על אף שהתיש אוהב את הגזר, אכילתו מסוכנת.` (this is causal, not concessive)
  - ✅ `מאחר שהתיש אוהב את הגזר, אכילתו מסוכנת.` (because → causal)
- **`מאחר ש` / `הואיל ש` / `כיוון ש`** — causal ("because"). Use when the
  English is `seeing how`, `given that`, `since (causal)`.

If the English is `but`, `however`, `yet`: check whether the Hebrew clauses
are genuinely contrastive before using `אבל`. If they're a sequence of
negative outcomes, prefer `ו` or `ובנוסף`.

#### One ו-החיבור per sentence + comma pairing

When a sentence chains 3+ clauses, don't string two `ו` connectors
together. Use **one** `ו` and break the rest with commas. Pairing rule:

- A clause that **starts with `ו`** → **no** comma before it.
- A clause **without `ו`** → **comma** before it.

| ❌ Two ו's | ✅ One ו, comma where the other ו was |
|------------|----------------------------------------|
| `הכישוף פג ואתה שוב נראה ליצורים מסוכנים, והטבעת נעלמה.` | `הכישוף פג, אתה שוב נראה ליצורים מסוכנים והטבעת נעלמה.` |
| `הוא פתח את הדלת ונכנס לחדר, ובדק את הארון.` | `הוא פתח את הדלת, נכנס לחדר ובדק את הארון.` |

Detection cue: search a single translation for the substring ` ו` (space +
ו) appearing **twice or more** in clause-initial position — that's
usually a smell. Also `, ו` (comma + space + ו) is a flag: combined with
another ו earlier in the sentence, restructure.

### 5. Literal / English syntax leaking through
Word-for-word translation that no native Hebrew speaker would say.

| # | EN | Current HE | Why it's wrong | Better |
|---|----|------------|---------------|--------|
| 498 | `The forest is slowly encroaching on the castle grounds; there are tall, ancient trees everywhere you look.` | `היער פולש לאט לאט לשטח הטירה; ישנם עצים גבוהים ועתיקים בכל מקום שאתה מסתכל.` | `בכל מקום שאתה מסתכל` is a calque of "everywhere you look". | `לכל עבר נראים עצים גבוהים ועתיקים` |
| 1211 | `You are standing in a cavern, with a wooden door directly across from you.` | `אתה עומד במערה, עם דלת עץ ישירות מולך.` | "Too much hassle" translation — every English word translated even when redundant. `ישירות` duplicates the directness already in `מולך`, and `עם דלת עץ` calques the English comitative ("with a wooden door"). | `אתה עומד במערה, ודלת עץ ניצבת מולך.` |

**"Too much hassle" pattern** — when EN packs an adverb + preposition + noun
phrase, the AI tends to translate every word even though Hebrew expresses
the same idea with one verb. Watch for and simplify:

| EN pattern | Wooden Hebrew | Natural Hebrew |
|------------|---------------|----------------|
| `directly across from you` | `ישירות מולך` | `מולך` (or add a verb: `ניצבת מולך`) |
| `with a <noun> directly across from you` | `עם <noun> ישירות מולך` | `ו<noun> ניצבת מולך` (verb + connector beats comitative `עם`) |
| `everywhere you look` | `בכל מקום שאתה מסתכל` | `לכל עבר` |
| `you seem unable to <verb>` | `אתה נראה חסר יכולת ל<verb>` | `אינך מצליח ל<verb>` |

Default move: **drop redundant adverbs that are already implied by the
verb/preposition**, and **add a verb** when the noun phrase is doing the
work of a clause in English.

#### Don't chase vivid English imagery into labored Hebrew

When English uses a striking metaphor or dynamic phrasing, the AI translator
sometimes preserves it word-for-word and ends up with Hebrew that's
technically faithful but reads stiff or unnatural. **A plain Hebrew
sentence that captures the same idea is usually better than an over-vivid
calque.**

| EN | Over-translated HE | Plain natural HE |
|----|--------------------|------------------|
| `The deep well dissolves quickly into darkness` | `הבאר העמוקה נבלעת במהירות בחושך` (literally "the deep well is swallowed quickly by darkness" — labored) | `הבאר עמוקה וחשוכה מאד` (the well is deep and very dark) |

Default move: if your "improved" translation needs you to justify it
("preserves the dynamic image of …"), reconsider — Hebrew often expresses
the same atmosphere with fewer words and a flatter structure. Save the
vivid moves for places where Hebrew has its own equivalent flair (e.g.
biblical-register `נבלעת בחשכה` only when the surrounding text earns it).

**English loanwords** — the AI sometimes uses transliterated English words
where Hebrew has a perfectly good native term, and the loanword breaks the
medieval-fantasy register. Replace:

| Loanword | Hebrew | Notes |
|----------|--------|-------|
| `סיטואציה` | `מצב` | Always replaceable |
| `אפקט` | `השפעה` / `תוצאה` | Always replaceable in fantasy register |
| `מיסטי` | `מסתורי` | Or just drop — often redundant with `כישוף` |
| `אינטרסנטי` | `בעל אינטרס` / `נוגע` | |
| `בלוק` (of wood/stone) | `גוש` | |
| `מייפל` (the tree) | `אדר` | |
| `אובססיה` | `התעניינות עזה` / `מרתק` (verbal recasting) | Clinical loanword; breaks register |
| `אלגנטי` | `מהודר` / `מעודן` | Replaceable in fantasy register |
| `פיזי` | `גופני` | Replaceable; `גופני` reads more native |

**Loanwords to leave alone** — these are fully naturalized in modern
Hebrew and replacing them adds no value (and can sound stilted):

| Loanword | Don't replace with | Why |
|----------|-------------------|-----|
| `ספציפי` | `מסוים` / `מיוחד` | Native speakers use it freely; a `מסוים`-only purge sounds like a translator over-correcting |
| `פאזל` (jigsaw) | — | Keep when it actually means a jigsaw |

Rule of thumb: if there's an everyday Hebrew word a 12-year-old would
recognize *and* the loanword sounds out of place in chivalric/fantasy
register, replace it. If the loanword is so common in modern Hebrew that
replacing it would itself sound forced, leave it.

#### Creature names — pin one Hebrew term per English creature

KQ-style games have several "small magical humanoid" creatures that
English distinguishes but the AI translator tends to merge into a single
Hebrew word (usually `גמד`). Don't merge — each English creature gets its
own dedicated Hebrew term, and they must stay distinct because the same
game often features more than one of them.

| English | Hebrew | KQ1 example | Don't translate as |
|---------|--------|-------------|--------------------|
| `elf` | `אלף` | The lake elf who gives Graham the invisibility ring (#406-#426) | `גמד` (collides with the gnome) |
| `gnome` / `dwarf` (the old wrinkled rock-house character) | `גמד` (often `גמד זקן`) | The Rumpelstiltskin-style gnome at the rock house (#1162-1188 area) | `אלף` |
| `leprechaun` | `לפרקון` (single canonical spelling — pick one and stick to it) | The sneaky thief that steals treasures (#1644-1648, #2032-2036 area) | `גמד` (collides with the gnome) or `שדון` mid-stream |
| `fairy godmother` | `הפיה הטובה השומרת עליך` (or `פיה שומרת` / `פיה טובה`) | #248, #251-253 | `פיה סנדקית` (Christian-coded) |

**Detection cue**: when reviewing a batch and you see `גמד` appearing in
the same scene as another `גמד`-distinct creature in EN, check whether
this is the gnome (rock house, carving wood, knows your name riddle) or
something else. Speaker labels (`גמד:` vs `אלף:`) are especially worth a
spot-check — they're easy places for the cast to mis-align with the
narration.

**Why "merge in the wrong direction" matters**: merging the elf into
`גמד` is worse than merging the gnome into `אלף`, because the gnome
character has stronger Hebrew identity (he's `גמד זקן ומקומט` —
"old, wrinkled gnome"). Always defer to the more entrenched name.

#### Modifier attachment doesn't shift in translation

When EN places a modifier on a noun (`this particular elf`,
`a really big rock`, `that very dark cave`), the Hebrew translation must
keep the modifier on the *same* noun — it cannot drift onto a verb or a
different noun. The AI translator sometimes "improves" by re-attaching, and
that silently changes the meaning.

| EN | Wrong attachment (HE) | Correct attachment (HE) |
|----|----------------------|--------------------------|
| `This particular elf doesn't like…` | `הגמד הזה במיוחד אינו אוהב…` (this elf *especially doesn't like*) | `הגמד הספציפי הזה אינו אוהב…` (this *particular* elf doesn't like) |

Default move: if the EN modifier sits between a determiner and a noun
(`this/that/the` + ADJ + N), put the Hebrew adjective in the same slot —
between the article and the head noun (`ה...ה...הזה`), not after the verb.

#### Folktale-specific terminology — defer to the Hebrew tradition

Some EN words have a literal Hebrew lexicographic match AND a different
"received" Hebrew form that's used inside a specific folktale. When
translating story content, the **folktale form wins** even if the literal
match feels more accurate.

| EN | Literal match | Folktale-correct (use this) | Folktale |
|----|---------------|------------------------------|----------|
| `beans` / `magic beans` (Jack-and-the-Beanstalk context) | `שעועית` (beans) | `אפונה` / `אפונת קסם` | The Hebrew "ג'ק וגרגר האפונה" tradition uses **אפונה** (peas), not שעועית (beans). |
| `beanstalk` (the climbable structure) | `שעועית` / `קנוקנת השעועית` / `קנוקנת האפונה` | **`גבעול האפונה`** (masc) | `גבעול` = stalk/stem (the upright structure Jack climbs). `קנוקנת` = tendril (the curling threads pea plants use to grip a support — Jack might use these for grip, but he climbs the stalk itself). |
| `gingerbread house` (Hansel-and-Gretel context) | `בית עוגיות` | `בית עוגת ג'ינג'ר` (or classical `בית עוגת זנגביל`) | Either form is acceptable; pick one and stay consistent within the file. |

Rule of thumb: if the English text is referencing a recognizable fairy
tale (beanstalk, gingerbread house, glass slipper, golden goose, etc.),
look up the Hebrew form *the Hebrew version of the tale uses* before
defaulting to the lexicographic match. Game flavor text is "story" text,
not "encyclopedia" text — folktale resonance matters more than botanical
accuracy.

**Beanstalk gender note**: `גבעול` is masculine, so all agreeing forms
must be masculine: `גבעול אפונה ענקי` (not `ענקית`), `הגבעול נעלם` (not
`נעלמת`), `גבעול אדיר היורד` (not `היורדת`), `הזה` (not `הזו`). Watch
this carefully — the earlier form `קנוקנת` is feminine, so any text that
used to be feminine-agreeing needs flipping.

KQ1 calibration: across messages #598, #643, #1138, #1141, #1143,
#1470, #1471, #1479, #1481, the climbable beanstalk is consistently
`גבעול האפונה` (or indefinite `גבעול אפונה`). Magic beans (the seeds
you plant) remain `אפונה` / `אפונת הקסם` (#1466–#1469). Do not introduce
`שעועית` or `קנוקנת` in this context.

#### Game-world facts override grammar instincts

The agent does not have full knowledge of the game's cast and locations,
so a label that reads as a grammatical mismatch may actually reflect
ground truth. **Before "fixing" speaker labels, character counts, gender
of pronouns referring to specific characters, etc., assume the existing
translation captured something the agent doesn't know.**

| Issue | What looks wrong | Why it's actually right | Fix? |
|-------|------------------|-------------------------|------|
| `CASTLE GUARD:` (EN singular) → `שומרי הטירה:` (HE plural) | EN/HE number mismatch | KQ1's Daventry castle has **2 guards**, so the plural is the collective speaker label (one speaks, both are present). | **No — keep plural.** |
| `the goat… he… his` (EN masc) → `העז… היא… חייה` (HE fem in late game) | EN/HE gender mismatch | Genuine inconsistency: early-game messages use `תיש` (masc), late-game messages use `עז` (fem). User decision required for direction. | **Resolved (KQ1): use `תיש` everywhere.** See note below. |

Default move when you spot a number/gender mismatch with EN: ask the user
about the in-game referent before fixing. The translator may have known
something the source label didn't capture.

##### Goat character canonical form (KQ1)

KQ1 calibration: the goat that follows Graham across the bridge is
referred to as **`תיש`** (he-goat) throughout — matching EN's
`he/his/him`. The earlier-batch usage of `עז` (she-goat) was a 22-message
inconsistency that was swept on user request.

**Do not "fix" `תיש` back to `עז`** even though `עז` is the more common
generic Hebrew word for "goat" — the in-game character is masculine.

The sweep also propagates to all agreeing forms — every verb, possessive,
demonstrative, and pronoun that previously agreed with `העז` (fem) flips
to masculine:

| Fem (was) | Masc (now) |
|-----------|------------|
| `העז משוטטת` | `התיש משוטט` |
| `מחליטה` | `מחליט` |
| `אותה` (her, obj) | `אותו` |
| `ממנה` | `ממנו` |
| `חייה` | `חייו` |
| `פרוותה` | `פרוותו` |
| `לבדה` | `לבדו` |
| `בעצמה` | `בעצמו` |
| `אינה יכולה` | `אינו יכול` |
| `נאבקת… צונחת` | `נאבק… צונח` |
| `עזים אוהבות` (generic pl.) | `תישים אוהבים` |

When the EN says `Goats love carrots!` (a generic plural), Hebrew has
two options: keep `עזים אוהבות` (fem-pl as gender-neutral generic) or
flip to `תישים אוהבים` for in-corpus consistency with the singular
character. **KQ1 chose the latter** (#1387, #1391) so the reader doesn't
parse a gender shift between adjacent sentences.

**Sweep principle:** when a user resolves a number/gender mismatch
(like the goat or castle-guard cases above), do a *full sweep* of the
file using `find_inconsistencies.py` plus a regex search for the old
form — don't leave straggler messages in the abandoned spelling. The
user shouldn't have to point out each instance individually.

#### Castle/architecture vocabulary — prefer the everyday Hebrew word

When EN uses a specialized architectural term (`portcullis`, `bailey`,
`barbican`, `merlon`, `keep`, etc.), the literal Hebrew technical
translation is often unfamiliar. Prefer the simpler, more common Hebrew
word unless the specialized meaning is plot-relevant.

| EN | Technical HE (avoid) | Natural HE (prefer) |
|----|----------------------|----------------------|
| `portcullis` | `שער הגרר` (lit. "drag gate") | `השער` (the gate) |
| `castle gate` | (no technical form) | `שער הטירה` |
| `moat` | `חפיר` | `חפיר` is fine — well-known. |

KQ1 calibration: #1555 `הרימו את שער הגרר!` was simplified to
`הרימו את השער!`. Hebrew readers would parse `שער הגרר` only by
context, while `השער` is unambiguous and natural.

#### Don't preserve EN line breaks that split a Hebrew construct phrase

Sierra games occasionally use `\n` inside speaker labels and short
exclamations to force a poster-style two-line layout (e.g. `CASTLE\nGUARD:`).
This works in English because each line is a standalone word. **In Hebrew
it often breaks a smikhut (construct phrase) where the bound noun has no
independent meaning.**

| EN | Mechanical HE (awkward) | Natural HE (prefer) |
|----|-------------------------|----------------------|
| `CASTLE\nGUARD:` | `שומרי\nהטירה:` (`guards-of` then `the-castle:` — bound noun stranded on its own line) | `שומרי הטירה:\n` (one line; let the dialogue use its own line break) |

Rule: when a Hebrew translation has `\n` inside a smikhut, between a
preposition and its object, or between `את` and its noun, drop the line
break. EN's display intent doesn't survive translation — and forcing it
produces awkward fragments like `שומרי \n הטירה`.

KQ1 calibration: #1555 was changed from
`שומרי\nהטירה:\n"הרימו את\nהשער!"` to
`שומרי הטירה:\n"הרימו את\nהשער!"` — kept the dialogue's internal line
break (`הרימו את \n השער` parallels the EN's `Raise the \n portcullis!`),
but consolidated the speaker label to one line.

### 6. Inconsistent translation of the same term
The same English term is rendered different ways in different messages, with
no in-game reason.

Example: `Cancel` → `ביטול` (#18, noun "cancellation") vs `בטל` (#510,
imperative "cancel!"). Both are legitimate Hebrew, but a UI label should
be one part of speech consistently — usually `ביטול` for buttons.

For fairy godmother, the file has both `פיה סנדקית` (#499) and `פיה טובה`
(#249, #251, #252, #917, #1020) — the standalone term in #499 should match
the rest.

Run `scripts/find_inconsistencies.py` to surface these automatically.

## Translations that DO sound natural (don't flag these)

- #248 `She is your fairy godmother.` → `היא הפיה הטובה השומרת עליך.`
- #884 `You take the Magic Mirror!  Congratulations!` → `מצאת את מראת הקסמים! ברכות!`
- #885 `Dragon's Tongue is considered a delicacy in some parts of the world, but not in Daventry!` → `לשון דרקון נחשבת למעדן בחלקים מסוימים של העולם, אך לא בדבנטרי!`
- #58  `This is a fine silver dagger, with a very sharp edge!` → `זהו פגיון כסף משובח, עם קצה חד מאוד!`

## Things to NOT flag

- **Transliterated proper nouns**: `Daventry → דבנטרי`, `Graham → גרהם`,
  `leprechaun → ליפרקון`. Transliteration is acceptable for names and
  game-specific creatures. Only flag if there's a well-established Hebrew
  equivalent (e.g. `dragon → דרקון`, not `דראגון`).
- **Lost wordplay**: English puns ("a bad fall this spring" = autumn/spring
  pun) usually can't be preserved. Don't flag unless the Hebrew is also
  *grammatically* broken.
- **Style differences you'd write differently**: only flag what a native
  Hebrew speaker would actually find odd, not personal preference.

## Severity rubric

When writing findings, tag each with one severity:

- **high** — broken grammar, wrong word, or actively misleading. Must fix.
- **medium** — awkward but understandable. Should fix.
- **low** — could be polished, but acceptable as-is.
