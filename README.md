# Government Scheme Eligibility Matching with Justified Decisions
SIH26092 · Group G8 · Section K3P25LH

A rule-based advisor: applicant profile in, eligible schemes with a reason for every
decision out. Built to match the PPT and report section by section.

## Run it
```bash
pip install -r requirements.txt
python -m pytest -q tests                  # 12 tests
streamlit run app.py                       # advisor + single-scheme baseline
python -m eligibility.generate_profiles --n 120 --out data/profiles.csv
```

## Validate (the numbers in the slides come from this step)
1. Generate profiles (above). They are unlabelled.
2. Label every profile–scheme case by hand from the guideline clause, as the report
   describes (section 5.3). Fill `data/ground_truth_TEMPLATE.csv`, save as
   `data/ground_truth.csv`. Use `decisive_conditions` to list the condition ids that
   decided each case (for example `c1;c3`). The validator refuses blank labels.
3. Run:
```bash
python -m eligibility.validation --profiles data/profiles.csv --truth data/ground_truth.csv --out results/
```
This writes `metrics.json` (engine accuracy, undetermined share, baseline accuracy,
explanation completeness, eligible per profile, per-scheme table), `decisions.csv`
and `mismatches.csv`. Put only these numbers in the final slides and report.

Do not label ground truth with the engine's own output. That makes the validation circular.

## Mapping to the PPT and report
| Slide / report item | Where in code |
|---|---|
| Profile: age, income, location, category, gender, enterprise (slide 4) | `eligibility/normalize.py` `FIELD_TYPES` |
| Rule store, separate from code, source-clause refs (slide 5, 8) | `rules/schemes.json` (edit without touching code) |
| Four condition types: numeric, categorical, boolean, date (slide 6) | `engine.check_value`, `validate_rules` |
| Controlled vocabulary, normalisation (report 5.4) | `normalize._to_category`, `vocabulary.aliases` |
| No imputation; missing → undetermined (slide 6, report 5.4) | `normalize_profile`, `engine.evaluate_condition` |
| ELIGIBLE / NOT ELIGIBLE / UNDETERMINED logic (slide 7, report 4.3) | `engine.evaluate_scheme` |
| Condition met / not met / cannot be assessed (slide 7) | `ConditionResult.outcome` |
| Condition-level explanation with source clause (slide 8) | `engine._explain`, `_line` |
| Missing fields listed for undetermined schemes (slide 8) | `SchemeResult.missing_fields` |
| Identical inputs → identical outputs (slide 5) | sorted scheme ids; `test_same_input_gives_identical_output` |
| Single-scheme yes/no checklist baseline (slide 8, report 6.3) | `eligibility/baseline.py` |
| Accuracy on committed decisions only (report 6.2) | `validation.run_validation` |
| Explanation completeness (slide 9, report 6.2) | `validation._explanation_complete` |
| Streamlit advisor, grouped results, expandable reasons (slide 8) | `app.py` |

## What is and is not included
- **Included:** the full engine, baseline, validation harness, advisor UI, synthetic
  profile generator, and tests for the logic that matters (boundaries, missing values,
  precedence, determinism, rule validation).
- **Not included: real scheme rules.** `rules/schemes.json` has three PLACEHOLDER
  schemes, labelled as such. Replace them with clauses verified from the official
  guidelines. The report's 15 schemes and 8 states must be encoded by your group.
- **Not included: ground-truth labels.** The 96.4%, 81.2% and 98.7% figures cannot be
  reproduced from this code alone. They are reproducible only by running the
  validation on your group's hand-labelled cases. If your run gives different numbers,
  use your numbers.

## Open questions to settle before submission
1. **Mandatory vs conditional.** Report 4.3 says eligibility needs all mandatory
   conditions met *and* no applicable conditional rule unmet, but it says a mandatory
   failure is decisive. This code treats every condition as mandatory. If conditional
   clauses should behave differently (for example, apply only when a related field is
   true), add an `applies_if` field and handle it in `evaluate_scheme`.
2. **Explanation completeness.** This code lists every condition in every
   explanation, so completeness mostly tests whether the decisive lines are rendered
   correctly. Be ready to say that in the report.

## Inconsistencies found in the PPT and report (fix before 30 Nov)
1. **Accuracy does not reproduce from the group table.** Report Table 4 gives group
   accuracies of 99.0% (612), 96.8% (538) and 92.2% (592). Weighted together, that is
   about 1,672 of 1,742, or **96.0%**, not 1,679 (96.4%). Recheck the group counts or
   the 96.4% figure.
2. **Undetermined rate.** The abstract says 3.1%. Section 8.1, Table 3 and slide 9 say
   58 of 1,800, which is **3.2%**.
3. **Component count.** Section 4.1 says "four components", but Table 1 and slide 5 list five.
4. **Reference numbering.** Section 3.4 cites [3] for benefit take-up research, but
   reference [3] is the Python documentation (the take-up paper is [8]). Section 3.4
   cites [4] for Doshi-Velez and Kim, but [4] is pandas (theirs is [9]). References
   [5]–[7] are never cited in the text, and [8]–[9] are never cited by number.
5. **Section numbering.** Section 5 goes 5.4 → 5.6 with no 5.5.
6. **Mandatory/conditional.** Section 4.3 uses this distinction and section 4.4 does
   not, so the algorithm and the decision rule do not match. See open question 1.
7. **Slide 9 vs report 8.1.** Both say 63 mismatches, consistent. But slide 9 says
   "1,679 matched ground truth" and the report calls the 1,742 committed decisions
   "engine decisions". Make the denominator wording identical everywhere.

## Data and ethics
Profiles are synthetic and contain no personal identifiers. The advisor stores nothing
between sessions (report 5.6). Results are advisory, not a legal determination.
