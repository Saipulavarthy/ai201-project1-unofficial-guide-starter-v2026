# The Unofficial Guide

<!-- Replace this line with your name and which corpus you picked. -->

> **This file is your submission.** Fill it in as you go — most sections get
> written during the milestone that produces them, not at the end.
>
> How the starter works, and every command you'll need, is in `RUNNING.md`.
> Leave that file alone.
>
> **Paste everything as text.** No screenshots, no video. A typed table gets
> full credit; a picture of the same table gets none.
>
> Delete these instruction blocks as you replace them. The `<!-- -->` comments
> are notes to you and don't show up when the page renders — you can leave them
> or remove them.

---

# Unit 1

## What This Does

This is a retrieval-augmented question-answering system built on the campus_life corpus — 88 short posts (1–3 paragraphs each) covering dining halls, housing, courses, and campus administration. Ask it a question like "what are wait times like at Kestrel Commons" or "which floors in Aldridge Hall are quiet," and it retrieves the most relevant post, checks that it's actually close enough to be useful, and answers using only that content — naming its source. Questions outside the corpus (like sports trivia or general how-tos) get refused rather than guessed at.

## Chunking Strategy

**Chunk size:** Whole document (no fixed character limit)
**Overlap:** None

campus_life is made up of short posts, 1–3 paragraphs each, where the useful 
information is usually spread across the whole post rather than sitting in one 
isolated sentence. The starter's 800-character fixed-size chunker barely 
touched this corpus — 88 documents came out as 88 chunks, since almost nothing 
reaches 800 characters — which was itself the first sign that a character-count 
strategy wasn't the right fit here.

Splitting further, whether by a fixed size or by paragraph, risked cutting a 
claim away from its reasoning (for example, separating "3 and 4 are quiet 
floors" from the sentence explaining why) for no real benefit, since each post 
is already about one topic. So `split_documents` in `chunker.py` treats each 
document as exactly one chunk: no cutting, no overlap needed since there's 
nothing to stitch back together.

## Sample Chunks

<!-- Five chunks, pasted as text. Label each one and name the file it came from
     AND the function that produced it — the grader checks your code against
     what you claim here.

     `python app.py chunks -n 5` prints all three for you. Copy them straight
     across.

     Milestone 3. -->

**Chunk 1** — source: `admin_add_drop_deadline.txt#0`

> On the add/drop deadline
>
> You can add a course through the end of the second week. Dropping is a longer window — through the end of week six — but a drop after week two shows as a W on your transcript. Nothing anywhere on the registrar's site says this plainly, and students find out from each other.


**Chunk 2** — source: `course_biol_160.txt#0`

> BIOL 160 Cell Biology
>
> I lived here my sophomore year. Format is lecture three times a week with a weekly lab. Assessment: four unit tests and a cumulative final. Not curved.
>
> Expect 9 to 11 hours a week, the heaviest first-year course by reputation.
>
> The one piece of advice: the unit tests come fast, roughly every three weeks; falling behind once is very hard to recover from.


**Chunk 3** — source: `course_hist_118_workload.txt#0`

> Workload for HIST 118 Modern World History
>
> People keep asking so: a lot of reading, about 120 pages a week, but no problem sets. That's real time, not optimistic time.
>
> It's front-loaded — the first month is heavier than the rest, partly because you're learning the format.

**Chunk 4** — source: `dining_pellew_dining_hall_followup.txt#0`

> Re: Pellew Dining Hall
>
> Adding to what people have said about Pellew Dining Hall. The wait figure of 12 to 18 minutes at peak matches what I've seen. If you're trying to eat between classes, go before 11:45 and it's a different building entirely.
>
> Also worth saying: the furthest hall from anywhere, next to the athletics centre. Nobody tells you this at orientation.

**Chunk 5** — source: `housing_innisfree_hall.txt#0`

> Innisfree Hall — what it's actually like
>
> Transferred in last year, so take this with a grain of salt. Built 1991, renovated 2022. Rooms are doubles arranged as pairs sharing one bathroom between two rooms.
>
> The good: the shared-bathroom-between-two-rooms arrangement is the best compromise on campus.
>
> The bad: no air conditioning, which matters for the first three weeks of September.
>
> Laundry costs $1.75 wash, $1.75 dry, app-based. On noise: moderate; the building is L-shaped and the short wing is much quieter.

## Sample Answer

<!-- One complete question and answer, pasted as text, with the source line
     visible. Milestone 4. -->

**Question:**
What are wait times like at Kestrel Commons around lunch?

**Answer:**
```
Based on the documents, wait times at Kestrel Commons are 20 to 25 minutes between 12:15 and 1:00, and under 5 minutes before 11:45 (dining_kestrel_commons.txt).

Sources retrieved: dining_halden_hall_followup.txt, dining_kestrel_commons.txt, dining_kestrel_commons_followup.txt, dining_north_kitchen_followup.txt, dining_the_ridgeway_cafe_followup.txt

```

**My relevance cutoff:**

0.6 (unchanged from the starter default)

<!-- The number you set in config.py, and how you got there.

     You ran five questions your corpus covers and the five in OUT_OF_SCOPE
     that it clearly doesn't, and wrote down the best distance for each. What
     did those two groups look like? Where was the gap? Put the actual numbers
     here — the table below wants all ten rows.

     Milestone 4. -->

I ran my 5 real questions and the 5 OUT_OF_SCOPE questions and recorded the best 
distance for each. In-corpus distances ranged from 0.183 to 0.461; out-of-scope 
distances ranged from 0.825 to 0.934 — a wide, clean gap with no overlap. The 
default cutoff of 0.6 sits almost exactly in the middle of that gap, giving 
comfortable margin on both sides, so I kept it rather than moving it.

| Question | In corpus? | Best distance |
|---|---|---|
| What are wait times like at Kestrel Commons around lunch? | Yes | 0.183 |
| What time does Kestrel Commons close on weekends? | Yes | 0.407 |
| Which floors in Aldridge Hall are quiet floors? | Yes | 0.356 |
| How late is the library open during term? | Yes | 0.461 |
| Do dining dollars roll over from spring to the following fall? | Yes | 0.210 |
| What is the capital of Mongolia? | No | 0.825 |
| How do I change the oil in a diesel engine? | No | 0.934 |
| Who won the 1994 World Cup? | No | 0.886 |
| What is the recommended dosage of ibuprofen for a headache? | No | 0.844 |
| How do I write a for loop in Rust? | No | 0.896 |

## How I Used AI

**1.** For Milestone 3, I asked Claude to help me implement my chunking strategy. I already knew I wanted "one document, one chunk" rather than a character-count split, since campus_life posts are short and usually about one topic. I gave that instinct to my VS Code AI assistant with a prompt describing the exact behavior I wanted. It implemented `split_documents` correctly, but also flagged something I hadn't considered: a document that's only whitespace would now produce an empty chunk, whereas the original `fallback_split` would have silently skipped it. I decided to leave it as-is since campus_life doesn't have any blank files, but it was a good catch I wouldn't have thought to check for myself.

**2.** For Milestone 2's acceptance criteria, I initially asked Claude to just write criteria #4 and #5 for me. It refused, since the assignment is explicit that AI shouldn't write these — the reasoning has to be defensible as your own. Instead, it asked me two direct questions: which of my chunk-length numbers (178 shortest, 317 average, 549 longest) looked wrong to me, and which of my five test questions worried me most. I said the 317-character average looked like an awkward middle ground, and that the Aldridge Hall floors question worried me because "3 and 4" could show up in an answer without actually coming from the right source. Claude then helped me turn those two answers into properly worded criteria, but the judgment calls were mine.

<!-- ── Stretch features ─────────────────────────────────────────────────────
     Doing one? Say so here BEFORE you start. A feature this README never
     claims earns nothing.
     ───────────────────────────────────────────────────────────────────────── -->

---

# Unit 2

<!-- These sections get ADDED to what's already above. Don't delete or rewrite
     unit 1 — the point is that someone can see what you said before you knew
     how it went. -->

## Run Log — Before

<!-- Your five criteria, three runs each. `python run_eval.py --label before`
     runs the questions, puts the OUT_OF_SCOPE ones through the gate, and
     writes it all into results/ for you. Targets come from criteria.md; the
     verdict column is your call.

     Criterion 3 is measured in one deterministic pass rather than three, so
     the same number goes in all three run columns. That's correct, not lazy.

     Milestone 1. -->

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. Retrieved chunk contains the answer | 4 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 2. Every answer names a source | 5 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 3. Gate stops out-of-corpus questions | 4 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 4. No chunk falls between 200-300 characters | 0 chunks | 39/88 | 39/88 | 39/88 | MISSED |
| 5. Aldridge Hall answer cites housing_aldridge_hall_noise.txt | Cited in all 3 | Cited | Cited | Cited | MET |

<!-- Underneath, paste the REAL output for each criterion from one of your
     runs — the actual text your system produced, not a description of it.
     Name the file and function that produced it. -->

## Verdicts

<!-- MET or MISSED for each of the five, against the target you wrote last
     unit — not a new one. Plus a sentence on how you decided. That sentence
     matters most where it was close.

     If your target said 4 of 5 and your runs came out 4, 3, 4, that's a MISS.
     The target has to hold, not show up occasionally.

     Milestone 2. -->

| # | Criterion | Verdict | How I decided |
|---|---|---|---|
| 1 | Retrieved chunk contains the answer (4 of 5) | MET | All 5 of my 5 questions had the correct answer in the retrieved chunks, across all 3 runs — well above the 4/5 target. |
| 2 | Every answer names a source (5 of 5) | MET | All 5 questions named at least one correct source file in every run, with no exceptions across all 3 passes. |
| 3 | Gate stops out-of-corpus questions (4 of 5) | MET | All 5 out-of-scope questions were refused by the gate, with distances (0.825–0.934) clearly above the 0.6 cutoff and well separated from my in-corpus distances (0.183–0.461). |
| 4 | No chunk falls between 200–300 characters | MISSED | I counted chunk lengths directly and found 39 of 88 chunks (44%) fall in that range — not a close miss, a clear one. Housing and admin posts in particular cluster in this length. |
| 5 | Aldridge Hall answer cites housing_aldridge_hall_noise.txt | MET | In all 3 runs, the answer cited housing_aldridge_hall_noise.txt alongside housing_aldridge_hall.txt. I judged this as meeting the target since the correct noise file was present and correctly cited every time, even though a second file came along with it. |

## Diagnoses

Stage: chunking (specifically, the interaction between the "one chunk per 
document" decision and the natural length distribution of the corpus).

Mechanism: since split_documents makes each document exactly one chunk, chunk 
length is just document length. The corpus turns out to contain two distinct 
kinds of posts: broad narrative posts covering a topic from several angles 
(300-549 characters, e.g. housing_innisfree_hall.txt), and narrow single-fact 
posts — course workloads, exam formats, laundry costs, noise policies, and 
short admin notices — that only need one or two sentences to say their one 
thing. Those narrow posts consistently land in the 200-300 character range, 
which is exactly the zone criterion 4 predicted would be empty.

The criterion assumed chunk lengths would cluster at the extremes (short 
fragments vs. long context-rich passages) and be sparse in the middle. That 
assumption didn't hold — the middle is where nearly half the corpus (39 of 88 
documents) actually lives, because a lot of real campus_life posts are 
genuinely short, single-topic notes rather than fragments of something longer.

This isn't a defect in the chunker or a broken pipeline — every chunk, even 
the 200-300 character ones, reads as a complete thought (see Sample Chunks). 
The problem is with the target I set in criterion 4, not with retrieval or 
generation: criteria 1, 2, 3, and 5 all passed cleanly using these same chunks.

<!-- For each miss: which stage caused it, and how. The stage alone isn't
     enough — you need the mechanism.

     Not a diagnosis: "Question 3 didn't work."
     A diagnosis:     "Question 3 asks about laundry costs. The answer is in
                       one sentence that got split across two chunks, so
                       neither chunk on its own contains it."

     The five stages: loading → chunking → embedding → retrieval → generation.

     Look for a pattern. If three misses all ask about numbers, that's one
     problem, not three.

     Missed nothing? Say so, then say honestly whether your targets were set
     low, and which one you'd tighten and to what.

     Milestone 3. -->

## The Improvement

**What I changed:** Modified `split_documents` in `chunker.py` to merge related companion documents into single chunks, instead of treating every 
document as its own chunk. Course files (a course's main post + its exams 
post + its workload post), dining files (a hall's main post + its followup), 
and housing files (a hall's main post + its noise post + its laundry post) 
are now combined into one chunk each. The merged chunk's `source` field lists 
every original filename joined with "+", so citations still show exactly 
which files contributed. Documents with no companion (admin_* files, 
health_center.txt, money_jobs.txt, etc.) are untouched — still one chunk per 
document, same as before.

**Why I picked it:** My diagnosis for criterion 4 traced the 200-300 
character pileup to narrow, single-fact companion posts — course exam/workload 
notes, dining followups, and housing noise/laundry notes — that were too thin 
to stand alone as chunks. Merging each of these with its base post directly 
targets that mechanism: the merged chunk is naturally longer, since it now 
holds several related facts instead of one, which should pull chunks out of 
the 200-300 range without changing anything about documents that were never 
part of the problem.

<!-- Connect it to a specific diagnosis above in one sentence. If you can't,
     you picked a fix because it sounded impressive. -->

### Run Log — After

<!-- Same format, same five criteria, three runs each.
     `python run_eval.py --label after` -->

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. Retrieved chunk contains the answer | 4 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 2. Every answer names a source | 5 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 3. Gate stops out-of-corpus questions | 4 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 4. No chunk falls between 200-300 characters | 0 chunks | 14/49 | 14/49 | 14/49 | MISSED (improved from 39/88) |
| 5. Aldridge Hall answer cites housing_aldridge_hall_noise.txt | Cited in all 3 | Cited | Cited | Cited | MET |

**Did it help?**

Yes, substantially, though not completely. Merging course, dining, and housing 
companion files cut criterion 4's failure count from 39/88 chunks (44%) to 
14/49 chunks (29%) — nearly two-thirds of the original violations disappeared, 
and every one of the remaining 14 is now a standalone admin_* file or 
advising_registration.txt, none of which had a companion to merge with. 
Criteria 1, 2, 3, and 5 all held steady with no regressions — the merge didn't 
break anything that was already working, including the Aldridge Hall source 
citation, which was the main risk with this change. The one tradeoff: 
distances shifted up slightly across the board (e.g. Aldridge Hall went from 
0.356 to 0.495) since merged chunks are longer and less tightly focused, but 
every question still passed comfortably under the 0.6 cutoff.

<!-- Say plainly whether it did, and how you know. If it made things worse,
     say that — a change that backfired, honestly reported, earns full credit
     and is more interesting than one that worked. What matters is that you can
     tell.

     Milestone 4. -->

## What's Still Broken

<!-- For each criterion still missed after your fix: what you'd do about it,
     and why you stopped where you did.

     "I ran out of time" is fine if it's true. Pretending nothing is left is
     not.

     Milestone 5. -->

## What I'd Do Differently

<!-- Knowing what you know now — which of your five criteria would you write
     differently, and why?

     Milestone 5. -->
