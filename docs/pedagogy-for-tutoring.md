# Pedagogy Notes for Agent Tutors

This repo uses compact Pi project resources under `.pi/` for tutoring policy. This file records the research basis so agents can consult it when designing help for a specific topic.

## Practical Principles

- Use formative assessment before explanation when the user's misunderstanding is unclear. Black and Wiliam's formative-assessment work emphasizes using evidence of student understanding to decide next instructional moves.
- Use diagnostic questions when a misconception might otherwise remain hidden. Barton argues for short diagnostic multiple-choice questions whose distractors map to specific misconceptions; a correct answer still deserves a quick reasoning check.
- Prefer worked examples early, then fade support. For a new proof pattern, show one complete model, give a partially completed analogue, then ask the user to finish the next one.
- Make the user retrieve definitions, hypotheses, and theorem statements. Retrieval practice, spacing, and interleaving have stronger long-term learning value than rereading alone.
- Use contrast: example/non-example pairs, near misses, and "which hypothesis fails?" prompts.
- Ask for self-explanation: why a theorem applies, why an operation is closed, why a map is well-defined, or why a counterexample works.
- Support productive struggle, but keep it productive: reduce the problem, give a hint, or switch to a worked example when the user lacks the prerequisite schema.
- Use metacognitive prompts after feedback: "What was the first wrong inference?" and "What cue would help you catch this next time?"

## Adaptation for Abstract Algebra

Most diagnostic-question guidance comes from school mathematics. In this repo, use it as a way to expose conceptual and proof-strategy misconceptions quickly, then return to proof writing, examples, and exercises. A diagnostic MCQ is useful when it changes the next tutoring move; it is not useful as busywork.

## Diagnostic MCQ Pattern

For abstract algebra, a diagnostic MCQ should usually have:

1. one target idea;
2. four plausible answers;
3. distractors tied to likely misconceptions;
4. a request for the user's reason or confidence;
5. follow-up feedback that explains the misconception, not only the right answer.

Good targets include:

- confusing subgroup closure with subset membership;
- confusing the order of an element with the order of a group;
- treating normal subgroups as equivalent to abelian subgroups;
- forgetting well-definedness in quotient or equivalence-class arguments;
- assuming a homomorphism is injective or surjective without proof;
- using a theorem while missing one of its hypotheses.

## Sources

- Craig Barton, "On Formative Assessment in Math: How Diagnostic Questions Can Help", *American Educator* 42(2), 2018: https://www.aft.org/ae/summer2018/barton
- Craig Barton, *How I Wish I'd Taught Maths*, John Catt, 2018: https://shop.maths.scot/products/how-i-wish-id-taught-maths-craig-barton
- Paul Black and Dylan Wiliam, "Inside the Black Box: Raising Standards Through Classroom Assessment", *Phi Delta Kappan*, 1998: https://eric.ed.gov/?id=EJ575146
- Education Endowment Foundation, "Cognitive Science Approaches in the Classroom", evidence review: https://educationendowmentfoundation.org.uk/education-evidence/evidence-reviews/cognitive-science-approaches-in-the-classroom%2B
- Education Endowment Foundation, "Improving Mathematics in Key Stages 2 and 3", guidance report: https://educationendowmentfoundation.org.uk/education-evidence/guidance-reports/maths-ks-2-3
- Mathematical Association of America, *Instructional Practices Guide*, 2017: https://maa.org/resource/instructional-practices-guide/
- National Council of Teachers of Mathematics, *Principles to Actions*, 2014: https://www.nctm.org/store/Products/Principles-to-Actions--Ensuring-Mathematical-Success-for-All/
