# Capability map

Maps each curriculum objective to the module(s) that deliver it and the concrete assets a learner
or presenter can point to.

| Objective | Module(s) | Key assets |
| --- | --- | --- |
| Understand Foundry account/project/model concepts | 1 | `modules/01-foundations-first-agent/README.md`, `slides.md` |
| Create and test a first prompt agent in the portal | 1 | `demo-runbook.md`, `src/create_prompt_agent.py` |
| Use built-in tools (Code Interpreter) | 2 | `src/toolbox.yaml`, `demo-runbook.md` |
| Author and version reusable Skills | 2 | `src/skills/*/SKILL.md` |
| Compose a toolbox shared across agents | 2 | `src/toolbox.yaml`, `src/provision_toolbox.py` |
| Ground answers in a real document corpus with citations | 3 | `shared/test-data/policy-wordings.json`, `src/build_search_index.py` |
| Understand Foundry IQ / retrieval-augmented grounding patterns | 3 | `README.md` architecture section |
| Build hosted (Agent Framework) agents | 4 | `src/triage_agent/`, `src/adjudicator_stub/` |
| Orchestrate multi-agent calls over A2A | 4 | `src/triage_agent/a2a_client.py`, `orchestrator.py` |
| Detect and handle `HostedAgentNotSupported` (HTTP 200 + JSON-RPC error) | 4 | `tests/test_a2a_fallback.py` |
| Implement a controlled Responses-API fallback | 4 | `src/triage_agent/a2a_client.py` (`invoke_with_fallback`) |
| Enable managed Memory and recall preferences across conversations | 5 | `src/provision_memory.py`, `demo-runbook.md` |
| Respect per-identity memory scope and privacy/erasure | 5 | `src/privacy_tools.py`, `docs/privacy-notes.md` |
| Apply least-privilege RBAC to Foundry resources | 6 | `shared/bicep/rbac-assignment.bicep`, `infra/rbac.bicep` |
| Configure an isolated OBO (user-delegated) toolbox | 6 | `src/provision_obo_toolbox.py` |
| Predict OBO success/failure by auth context | 6 | `src/auth_context.py`, `tests/test_auth_context.py` |
| Integrate OpenTelemetry tracing at authoring time | 7 | `src/otel_setup.py` |
| Build and run an offline evaluation harness | 7 | `src/evaluator.py`, `eval/triage-eval-dataset.json` |
| Apply trust & safety rule-based checks | 7 | `src/safety_checks.py` |
| Front a Foundry model connection with APIM (BYOM) | 8 | `infra/apim/foundry-api-policy.xml` |
| Understand the deployment-metadata probe contract | 8 | `infra/apim/get-deployment-operation-policy.xml`, `src/mock_deployment_probe_server.py` |
| Operate/manage the whole curriculum (tagging, verify-all) | 8 | `verify.ps1 -RunAllModuleVerifications`, `docs/operate-checklist.md` |
| (Optional, gated) Private networking / VNet injection overlay | 8 | `infra/enterprise-overlay/private-networking.bicep` |

## Cross-cutting assets

| Concern | Asset |
| --- | --- |
| No-secrets policy | `SECURITY.md`, `shared/python/secret_scan.py` |
| Module file contract | `CONTRIBUTING.md` |
| Config schema | `shared/schema/module-config.schema.json` |
| Evaluation case schema | `shared/schema/eval-case.schema.json` |
| Offline validation entrypoint | `tests/run-all-validation.ps1` |
| Known limitations (verified, time-bound) | `docs/known-limitations.md` |
