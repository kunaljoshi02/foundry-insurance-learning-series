# Operate checklist — Foundry Insurance Learning Series

Use this checklist as the **capstone operating routine** for the full curriculum. The goal is not just “can I deploy it?” but “can I verify, govern, and explain it safely?”

## Always-on operator habits

- Tag course-owned assets with `course=foundry-insurance-learning-series`
- Add `owner=<team-or-alias>` and, where helpful, `module=<module-folder>`
- Prefer read-only verification before any live change
- Keep preview boundaries documented and visible to instructors/learners
- Review APIM, model, Search, and monitoring costs before extended demos

## Module-by-module healthy state checks

| Module | What healthy looks like | Verify script |
| --- | --- | --- |
| 01 — Foundations + first prompt agent | The shared foundation exists, the prompt agent can be inspected, and the configured chat deployment name resolves correctly for the learning environment. | `modules\01-foundations-first-agent\verify.ps1` |
| 02 — Tools, Skills & toolbox | The shared toolbox and its Skills are present, versioned correctly, and attached to the target agent. | `modules\02-tools-skills-toolbox\verify.ps1` |
| 03 — Search grounding / Foundry IQ | The Search index exists, contains documents, the project connection is valid, and the grounding tool is attached to the advisor agent. | `modules\03-search-grounding-foundry-iq\verify.ps1` |
| 04 — Hosted agents + orchestration | Hosted agents are present, named as expected, and the orchestration path can be inspected without mutating resources. | `modules\04-hosted-agents-orchestration\verify.ps1` |
| 05 — Managed Memory + privacy | The Memory store exists, is attached to the intended agent, and user-scoped behavior is verified through the module’s read-only checks. | `modules\05-managed-memory-privacy\verify.ps1` |
| 06 — Identity, RBAC, auth & OBO | Least-privilege assignments, OBO prerequisites, and identity wiring are validated without performing privileged mutations. | `modules\06-identity-rbac-auth-obo\verify.ps1` |
| 07 — Observability, evaluation, trust & safety | Telemetry, evaluation assets, and safety/guardrail configuration can be reviewed and explained as healthy for the chosen demo path. | `modules\07-observability-evaluation-trust-safety\verify.ps1` |
| 08 — APIM + networking + operate capstone | The local deployment-probe mock returns the required ARM-shaped resource, unit tests pass, and the enterprise overlay remains disabled unless explicitly enabled. | `modules\08-apim-networking-capstone\verify.ps1` |

## Suggested capstone verification order

1. Run each module’s `verify.ps1` from its own folder.
2. Record pass/fail plus any notes about configuration gaps or preview limits.
3. Run Session 08’s consolidated command:

   ```powershell
   .\verify.ps1 -RunAllModuleVerifications
   ```

4. Review the status table and decide:
   - safe for classroom delivery,
   - safe for operator dry-run only,
   - or blocked pending environment fixes.

## Cost-hygiene reminders

- APIM token-limit policies are not only governance controls; they are also **cost controls**
- Keep demo Search, monitoring, and model SKUs right-sized
- Shut down or remove temporary enterprise-overlay assets after review
- Reconfirm ownership tags before cleanup to avoid touching unrelated resources

## Enterprise overlay reminder

The private-networking overlay in Module 08 is:

- **optional**
- **explicitly gated**
- **disabled by default**
- and intentionally **separate** from the public foundation used by Modules 01-07
