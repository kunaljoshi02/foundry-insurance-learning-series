# Lab - Extend the evaluator and safety rules

In this lab, learners make one small routing-data change and one small trust/safety logic change, then confirm the scorecard or test results change as expected.

## Goal

Add:

1. **one new evaluation case** to the triage dataset
2. **one new safety rule** to the rule-based safety helpers
3. rerun the verifier and unit tests

## Starting point

Assume the learner already has:

- this module folder on disk
- Python available locally
- no live Azure connectivity requirement

## Part 1 - Add a new evaluation case

Open [`eval/triage-eval-dataset.json`](eval/triage-eval-dataset.json) and add one new case that includes all required fields:

- `id`
- `test_case_description`
- `input.fnol_narrative`
- `expected.route`
- `tags`

### Suggested example

Create a new FNOL narrative that should clearly route to `manual-review`, such as a multi-party liability dispute or a case with missing police documentation.

### Checkpoint

Re-run:

```powershell
python .\src\evaluator.py --output .\artifacts\scorecard.json
```

Confirm that:

- the case count increased by one
- the new case appears in the scorecard output
- the route result matches your expectation, or clearly shows a failure you can explain

## Part 2 - Add one new safety rule

Open [`src/safety_checks.py`](src/safety_checks.py) and extend one of the rule sets.

Choose one path:

- add a new **protected-class** phrase pattern
- add a new **fraud-signal** keyword or phrase
- strengthen the **citation** detector with another acceptable citation shape

### Suggested example

Add a new fraud phrase such as `synthetic invoice` or `duplicate repair bill`, then add a matching unit test.

## Part 3 - Update tests

Open [`tests/test_safety_checks.py`](tests/test_safety_checks.py) and add a test that proves your new rule works.

Re-run tests:

```powershell
python -m unittest discover -s .\tests -v
```

## Part 4 - Re-run the verification gate

Run:

```powershell
.\verify.ps1 -Threshold 0.85
```

Interpret what changed:

- if the new evaluation case passes, the pass rate may stay similar or improve
- if it fails, the harness should make the failure obvious
- if your safety rule works, the related unit test should now pass because of the new detection logic

## Done-when checklist

- [ ] I added one new evaluation case with `test_case_description`.
- [ ] I kept the route label aligned with the shared schema.
- [ ] I added or updated one safety rule.
- [ ] I added a unit test that proves the new rule works.
- [ ] I re-ran the evaluator and reviewed the scorecard.
- [ ] I re-ran the tests and saw them pass.
- [ ] I can explain whether my change was about routing accuracy, safety, or both.

## Reflection

After this lab, ask:

1. Which is cheaper to fix: the prompt, the routing logic, or the tool contract?
2. Which safety rules should always block release, and which should only warn?
3. What extra cases would you add before trusting a live adjudication workflow?
