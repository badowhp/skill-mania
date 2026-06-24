# AI-Slop Text Checks

Use this as a quality gate for reader-facing prose. A tell is an unchosen default, not a banned word or a detector verdict. Keep deliberate voice choices when they fit the author, audience, and register.

This reference is based on JCarterJohnson's `vibecoded-design-tells` research and `unslop-text` skill: https://github.com/JCarterJohnson/vibecoded-design-tells/tree/main/unslop-ai-text. The repo reports a Reddit-mined study of AI-writing complaints and packages those findings as text audit guidance.

## Always-On Pass

Before returning prose, ask:

- Is the register chosen: casual, conversational-professional, expository, or formal?
- Is there a specific speaker, audience, and reason to care?
- Does each paragraph make or advance a claim?
- Does the structure follow the idea instead of an intro, three even points, and recap?
- Does the rhythm vary naturally when read aloud?
- Are any flagged patterns intentional enough to keep?

If prose exists in local files, run `scripts/scan-ai-slop-text.py` first. Then do the structural read manually. A clean scan only means the lexical layer is clean.

## Mechanical Tells

Prioritize fixes in this order:

- Real em dash characters or spaced en dashes used as a default punctuation tic.
- Leftover assistant boilerplate: model disclaimers, cutoff references, refusals, "I cannot help" scaffolding, or meta offers to revise.
- Antithesis cadence: "not just X, it is Y" or "not X, but Y" used to manufacture importance.
- Sycophantic openers: flattery, reflexive agreement, or customer-support warmth before the actual point.
- Bolded lead-in labels, title-case mini-headings, and chat-answer formatting where prose should stand on its own.
- Generic AI diction: `delve`, `tapestry`, `leverage`, `seamless`, `game-changer`, `unleash`, `underscore`, `meticulous`, `elevate`, `harness`, and similar words clustered together.
- Hollow openers: broad "today's world" setup, "let's dive in," and throat-clearing before the point.
- Listicle scaffolding when the material is an argument, not a list.
- Decorative emoji used as headings, bullets, or structure.
- Signposted recap endings such as "in conclusion" when the piece needs a real final point.

Do not over-weight a lone ordinary word. A single `however`, `robust`, `comprehensive`, or `utilize` is usually weak evidence. Density and concentration matter unless the issue is assistant boilerplate or real dash punctuation.

## Structural Tells

These need a human read:

- Uniform sentence rhythm. If every sentence has the same length and shape, vary it.
- Polished emptiness. If a paragraph can be removed without losing meaning, cut or replace it with a claim.
- Yes-man tone. Do not agree, flatter, or soften when the piece needs judgment.
- Over-formality in casual or professional contexts. Use contractions when the chosen register supports them.
- Hedging without a recommendation. State the tradeoff, then take a position when the reader needs one.
- Rule-of-three dependency. Do not force every idea into three points or three parallel phrases.
- Fake specificity: invented citations, vague authorities, fake typos, or casual markers pasted onto otherwise formal prose.

## Over-Correction

Do not replace smooth AI default prose with a different default. Forced lowercase, staccato fragments, fake mistakes, bolted-on slang, profanity for authenticity, and conspicuous dash avoidance all read as costume when they do not belong to the speaker.

The fix is not "sound less AI." The fix is a chosen register, a concrete speaker, a real claim, and sentences that fit the audience.

## Fixing Order

1. Delete assistant residue and any meta-commentary that only belongs in a chat turn.
2. Replace mechanical tells with plain wording.
3. Cut hollow openers and recap endings.
4. Restore the claim and restructure around the idea.
5. Read aloud for cadence and sentence variety.
6. Check that fixes did not erase the author's voice or create forced casualness.

## Audit Output

Lead with the verdict and the highest-impact fix. Then list findings by priority, with file and line when available, and give the smallest useful rewrite. Close with the scanner score if used and the top three changes needed before shipping.
