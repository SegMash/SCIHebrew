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
