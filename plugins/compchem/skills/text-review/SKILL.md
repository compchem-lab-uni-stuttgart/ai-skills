---
name: text-review
description: Review a scientific text file (paper, thesis chapter, SI, abstract, proposal, response to reviewers; LaTeX, Markdown or plain text) and write every proposed change to a Markdown file, ordered from top to bottom and tagged by category (AI-sounding, unclear, language, spelling and grammar, correctness, consistency, chemistry conventions, repetition, citations, LaTeX), with three suggestions per point, the first one recommended, and unverifiable points marked as queries. Runs all categories by default, or only those the user names. The reviewed file is changed only afterwards, when the user picks suggestions to apply. Use this whenever the user asks to review, proofread, check, polish, copy-edit or improve the language of such a text or a section of it ("check my English", "Korrektur lesen", "is this paragraph clear?"), or to apply points from such a review, even if they don't say "review".
argument-hint: <file> [line range or section] [categories] [options]
---

# Text review

Review the text given in the arguments and write all findings to a Markdown file. **Never edit the reviewed file during the review**; the user decides what to apply. Only the points the user picks afterwards are applied (see *Applying suggestions*).

## Input

- `$ARGUMENTS`: the file to review, optionally followed by a line range (e.g. `120-160`) or a section name, the categories and the options (see below), in any order and wording.
- If no file is given, ask which one.
- Read the whole file (or the given part) with line numbers. Skip commented-out lines (`%` in LaTeX) and obvious notes or todo lists, and say in the header that they were skipped.
- For checks of consistency and correctness, also read the rest of the document where needed: the main file with the macros, the other sections, the SI, and the `.bib` file.

### Categories

- The user can choose all categories, one, or a subset, by name, tag or number from the list in *What to look for* (e.g. "only spelling and LaTeX", "Error, Citation", "everything except ideas"). Map their words to the closest category ("grammar" → Error, "style" → Language, "units" → Convention). If the choice is unclear, ask.
- **If no category is given, run all categories.**
- Report only points in the chosen categories. If a sentence also has problems in other categories, leave those out. Parts of `## Whole text` that belong to a category (e.g. the count of "this" under Language) are written only if that category is chosen.

### Options

- **Spelling variety.** Default: the variety (British or American English) that the text already uses for most words. Flag every word that deviates from it as Consistency. The user can set British or American English instead, or name the target journal. With a journal, follow its current author guidelines for spelling and other style rules: look them up, or ask the user if you cannot, and do not state a journal's rules from memory. British spelling with -ize (Oxford spelling) is British as well: flag -ise against -ize only when both occur in the text. For a text in another language (e.g. German), review it by the rules of that language and write the review in that language, unless the user asks otherwise.
- **Keep the author's voice.** Off by default, because the text may have been drafted with Claude: suggestion 1 may then rewrite a sentence completely if that gives the best version. When the user asks for it (e.g. "keep my style", "minimal changes", "light edit"): flag only sentences with a real problem, do not rewrite correct sentences to match your own taste, keep the author's words, terms and sentence structure in the suggestions where possible, and make suggestion 1 the smallest change that fixes the problem.

### Long texts

If the text is longer than one section or about 150 lines, review it in parts:
- Split it at section, subsection or paragraph boundaries into parts of one section or at most about 100–150 lines.
- Before starting, tell the user in one line that the text will be reviewed in N parts.
- Review each part completely against all chosen categories and append its points to the review file before starting the next part, so that later parts get the same care as the first. Number the points continuously across the parts.
- After the last part, go once through the whole text for `## Whole text` (consistency and repetition across sections, order of paragraphs, the count of "this"), then do the final check.

## What to look for

Report **every** point you find in the chosen categories, not a fixed number per category. Go through the text sentence by sentence and check each sentence against all chosen categories below.

1. **AI-sounding sentences**: "not X, but Y" contrasts, "X balances A against B", stock phrases ("proof-of-concept", "plays a crucial role", "a wide range of", "it is worth noting"), generic summarising or closing sentences, empty hedges ("usually, but not always"), signposting ("as described below", "itself"), lists of three for rhythm (e.g. "fast, flexible and efficient"). Also:
   - sentences that open with "Thus," "Therefore," "In addition," or "Moreover," where no logical link is needed;
   - textbook explanations of basics that the intended readers already know;
   - the words "essential", "crucial", "robust", "powerful";
   - each equation introduced with "as shown in Eq.", where "Eq. X gives …" or simply the equation would do.
2. **Unclear sentences**: ambiguous "which/this/it", dangling modifiers, missing definitions or units, sentences that need re-reading, overloaded sentences, terms used before they are defined.
3. **Nicer language**: choppy or clumsy wording, weak openings, nominal style, word order, transitions between sentences and paragraphs. Also:
   - **too many "this"/"these"**: count them in the reviewed text. Flag every "This"/"These" that opens a sentence without a noun ("This shows …") and every "this" whose referent must be guessed; suggest naming the noun or joining the sentences. Even with a noun ("this mechanism"), more than one or two per paragraph is too many, so flag the ones that can go (often "the" or the noun alone works). Give the total count and the paragraphs with the most occurrences in `## Whole text`.
4. **Spelling and grammar errors**: typos, articles, agreement, tense switches, punctuation (also too many semicolons or colons), parallel structure, hyphenation (compound adjectives).
5. **Correctness**: statements that do not follow from the data or the cited source, overclaims, wrong or inconsistent numbers, equations and their descriptions (check symbols, signs, indices, and recompute simple numbers such as unit conversions). If a statement depends on data, results or sources you cannot see, tag the point Query (see *Queries*) instead of calling it wrong.
6. **Consistency**: terms (e.g. "dataset" vs "data set"), notation and symbols, abbreviations defined once and used afterwards, capitalisation, spelling variety (see *Options*), consistency with the other sections and the SI.
7. **Conventions of chemistry and computational chemistry**:
   - numbers and units: a (non-breaking) space between number and unit (e.g. `\qty{}` from siunitx, or `~`), one unit and one unit format per quantity throughout (not kcal mol⁻¹ next to kJ/mol), decimal places that match the precision of the data, an en dash for ranges, × for multiplication, a minus sign instead of a hyphen;
   - symbols: variables and constants in italics (*k*, *T*, Δ*G*); units, element symbols, chemical formulas and descriptive subscripts upright (e.g. `k_\mathrm{cat}`); one symbol per quantity; each symbol defined at its first use;
   - chemistry: chemical formulas with correct sub- and superscripts and charges (e.g. `\ce{}` from mhchem), consistent compound numbering;
   - computational details: notation of method, dispersion correction and basis set (e.g. B3LYP-D3(BJ)/def2-TZVP, with `//` between single-point and optimisation level), software named with version and citation, all settings needed to reproduce the calculations;
   - figures, tables and equations: each one (and each SI item) cited in the text, figures and tables cited in numerical order, panel labels in the text matching the figure, captions that define every symbol, abbreviation, colour and error bar.
8. **Repetition and length**: sentences or facts repeated within the text or from other sections, sentences that can be deleted without loss.
9. **Citations**: claims that need a citation, citations that do not support the sentence they follow (cite only what a source says; judge this only against a source you can actually read, such as a PDF or text the user provides, otherwise tag the point Query), citation placement relative to punctuation, consistency of the citation style.
10. **LaTeX and formatting**: broken or wrong references and labels, spaces before citation commands (e.g. `\cite`, `\autocite`) where the citation style sets them as superscripts, macros followed by a space without `{}`, missing commas or full stops after displayed equations, bracket sizes, math vs text mode, figure and table captions.
11. **Further ideas**: structure and order of paragraphs, missing information a reader needs, figures or tables that would help, anything else worth changing.

**Queries.** If you suspect a problem but cannot verify it (a source you cannot read, data or results that are not in the files, an intention you cannot tell from the text), add the tag Query to the point in its category. Write the Problem line as a question to the author (e.g. "Does ref. 12 report this yield, or only ref. 13?") and start each suggestion with the case it covers (e.g. "If ref. 12 does not report it: …"). Never present a Query as an error, and never call a citation wrong without having read the source.

These writing rules apply to every suggestion, unless the user's own instructions (e.g. in CLAUDE.md) say otherwise: concise, no repetition, explicit, and cite only what a source says. Suggestions must not introduce new claims. Suggestions avoid semicolons (use a comma construction or two sentences), use colons sparingly (a single colon, e.g. before a list, is fine, but not several close together) and do not add "this/these" without need.

## Output file

Write the review to `reviews/<basename>_review_<YYYY-MM-DD>.md` in the same folder as the reviewed file (create `reviews/` if needed; add `_2`, `_3` … if the name exists, never overwrite).

The points are **ordered by line number from top to bottom**, not grouped by category, so that the user can go through the text once and apply all changes in one pass. The category is a tag on each point. Use this structure:

```markdown
# Review of <file>

Line numbers refer to `<path>` (state <date>). <What was skipped.>
Categories: <all, or the chosen ones>. Spelling: <British or American English, and whether taken from the text, set by the user or from the journal>. <Keep the author's voice, if chosen.>
The points follow the text from top to bottom. For each point: the category, the original, what is wrong or weak, and three suggestions. Suggestion 1 is always the recommended one.

| Category | Tag | Points |
|---|---|---|
| Spelling and grammar | Error | ... |
| ... | ... | ... |
| Not verified (any category) | Query | ... |

---

## <Section or subsection heading of the reviewed text>

### 1. l. 13 · Error, Unclear · <short title>
> <original sentence, verbatim, wrong parts in **bold**>

Problem: <one or two sentences; one per category if there are several>.
1. <recommended suggestion, changes marked: **new or changed words** in bold, ~~deleted words~~ struck through>
2. <alternative, marked the same way>
3. <alternative, marked the same way>

Example (original: "Since the functional reproduces the CCSD(T) reaction energies well, it was therefore used for all further calculations.\cite{…}"):
1. ~~Since the~~ **The** functional reproduces the CCSD(T) reaction energies well**.** **It** was ~~therefore~~ used for all further calculations.\cite{…}

### 2. l. 22 · AI-sounding · <short title>
...

### 3. l. 31 · Citation, Query · <short title>
> <original sentence, verbatim>

Problem: <question to the author>
1. If <case>: <suggestion, marked as above>
2. If <other case>: <suggestion, marked as above>
```

The table lists only the chosen categories, plus the Query row.

Rules for the points:
- Tags: AI-sounding, Unclear, Language, Error (spelling and grammar), Correctness, Consistency, Convention, Repetition, Citation, LaTeX, Idea, and Query (added to a point of any category, see *Queries*).
- Number the points consecutively through the whole file (1, 2, 3, …), so that the user can refer to them.
- Insert a `##` heading whenever the reviewed text starts a new section, subsection or figure caption, so that the user knows where they are.
- Order the points by line number. Within one line, follow the order in the sentence. Points that concern the whole text (e.g. a term used inconsistently throughout, or the order of paragraphs) go into a final section `## Whole text`.
- **One point per sentence:** if a sentence has several problems, combine them into one point with all tags (e.g. `Error, Unclear`), one problem line per category, and suggestions that fix all of them at once. Do not list the same sentence twice.
- If a point concerns several sentences or a whole paragraph, quote the first words and give the line range (e.g. l. 42–46).
- Quote the original verbatim, keeping LaTeX, so that it can be found with search.
- Suggestion 1 is the one you recommend, i.e., the version you would put in the paper, even if it changes more than the alternatives. With the option *keep the author's voice*, suggestion 1 is the smallest change that fixes the problem. Suggestions 2 and 3 are genuine alternatives (e.g., a smaller change, a different structure, or deleting the sentence).
- For **errors** (Error, and wrong parts in Correctness, Consistency, Citation, LaTeX): mark the wrong part in the quote with `**bold**`, and give the recommended corrected sentence as suggestion 1.
- For a pure error with only one correct form (a typo, a broken reference), give only the correction, without alternatives.
- Suggestions are complete sentences in the same markup as the file. Where deleting is best, "Delete the sentence." is a valid suggestion.
- **Mark the changes in every suggestion** against the current text, so that the user sees at a glance what each suggestion changes:
  - new or changed words in `**bold**`, unchanged words plain;
  - deleted words as `~~strikethrough~~`, but only where a deletion is not already visible from a bold replacement (e.g. a deleted "so far" or "as well");
  - changed punctuation in bold too (e.g. `well**.**`), since a new full stop or a removed comma is easy to miss.
  - Write suggestions as plain Markdown text, never in backticks or code blocks: code formatting highlights the whole sentence and hides the bold marks. Escape Markdown characters in LaTeX (`\*`, `\_`, and every single LaTeX tilde as `\~`, e.g. `Fig.\~2`, since GitHub Markdown renders text between two single tildes as struck through) and put math with `_` or `*` in backticks, so that the text renders correctly.
  - Unchanged citations may be shortened to the command with `{…}` (e.g. `\cite{…}`), so that the changes stand out. Changed or new citations are written in full.
  - If a suggestion rewrites most of a sentence, do not bold all of it. Write it plain and add "(rewritten)" after it.
- The recommended full version of a longer passage (e.g. a whole abstract in `## Whole text`) may stay in a code block for copying, without marks.
- If the suggestion for one point changes a sentence that a later point refers to, say so (e.g. "if you take 1, point 7 is no longer needed").

## Final check

Before replying, go through the review file and fix every failure:
- **Quotes**: each quote occurs verbatim in the reviewed file at the given line (search for it with the Markdown escapes undone; for long quotes, search the first words). Correct wrong line numbers.
- **Coverage**: every line of the reviewed text was checked; skipped parts are named in the header.
- **Order and numbering**: points sorted by line and numbered without gaps, no sentence in two points, each `##` heading matching the reviewed text.
- **Categories and options**: only the chosen categories appear; the spelling variety and, if chosen, *keep the author's voice* hold in every suggestion.
- **Suggestions**: suggestion 1 fixes every problem listed for its point; no suggestion adds a claim, number or citation that is not in the text or its source; the bold and struck-through marks match the actual changes; no suggestion is in backticks or a code block.
- **Queries**: every point you could not verify is tagged Query and written as a question, not as an error.
- **Numbers**: every corrected or recomputed number is recomputed once more.
- **Counts**: the table in the header matches the points in the file.

## Reply to the user

After writing the file, reply briefly with:
- the full absolute path of the Markdown file,
- the chosen categories and options,
- a table with the number of points per category and one or two examples each (with point numbers),
- the clear errors (Error points, and Correctness, Convention and LaTeX points without Query) as a short list with point number, line number, wrong part and correction,
- the Query points as a short list with point number and question,
- an offer to apply the suggestions the user chooses, with the format: e.g. "1, 4.2, 7" applies suggestion 1 of point 1, suggestion 2 of point 4 and suggestion 1 of point 7.

## Applying suggestions

When the user picks points from a review:
1. **Read the choice.** A point number alone means suggestion 1 (or the only correction); "4.2" means suggestion 2 of point 4. Ranges and groups work too ("1–10", "all Error points", "all except 12"). A Query point needs the user's answer first; then apply the suggestion for that case. If the choice is unclear, ask.
2. **Find the originals again.** Read the review file and the current reviewed file. Find each original by its verbatim quote, not by its line number, since the file may have changed. If a quote is no longer found (e.g. the user edited the sentence), skip the point and report it.
3. **Check the chosen points against each other.** If two change the same sentence, or one depends on another (see the notes in the points), combine them if they fit; otherwise ask which one to take.
4. **Apply exactly the chosen suggestion**, as plain text without the review markup: bold marks removed, struck-through words deleted, "(rewritten)" removed, Markdown escapes undone (`\_` → `_`, `\~` → `~`, `\*` → `*`), shortened citations (`{…}`) restored to the full original keys. Change nothing else in the file: no other wording, no reformatting or reflowing of lines, same encoding and line endings (CRLF or LF). Problems you notice while applying go into the reply, not into the file.
5. **Mark the points in the review file**: below each point's heading, add `**Applied** (suggestion N, <date>)` or `**Skipped** (<reason>)`. Do not delete points.
6. **Reply** with the applied points and the lines they are on now, the skipped points and why, and further problems you noticed. For a LaTeX file, suggest compiling it to check the result.
