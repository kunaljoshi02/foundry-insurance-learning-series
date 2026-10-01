"""Utilities that model a verified hosted-agent orchestration limitation.

This module deliberately teaches one real Microsoft Foundry behavior observed in a live build:
an A2A call to a hosted agent can return HTTP 200 while the JSON-RPC body contains an
``error`` envelope whose data.code is ``HostedAgentNotSupported``. In that case, the caller must
inspect the JSON-RPC payload, treat the transport as unsuccessful, and fall back to the hosted
Responses protocol in a controlled way.
"""
from __future__ import annotations

from dataclasses import dataclass
import json
from typing import Any, Callable
from urllib import error, request
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit
import uuid

JsonDict = dict[str, Any]
Transport = Callable[[str, JsonDict, dict[str, str]], JsonDict]
FallbackCallable = Callable[[str, JsonDict], JsonDict]


@dataclass(frozen=True)
class A2ASuccess:
    """Represents a successful JSON-RPC response from the A2A protocol."""

    request_id: str
    result: JsonDict
    assistant_text: str | None = None


@dataclass(frozen=True)
class InvocationOutcome:
    """Summarizes whether orchestration completed over A2A or via fallback."""

    protocol: str
    used_fallback: bool
    request_id: str | None
    result: JsonDict
    assistant_text: str | None = None


@dataclass(frozen=True)
class HostedAgentNotSupportedError(RuntimeError):
    """Typed signal used to trigger the hosted Responses fallback path."""

    request_id: str | None
    response_json: JsonDict
    message: str

    def __str__(self) -> str:
        return self.message


@dataclass(frozen=True)
class A2AProtocolError(RuntimeError):
    """Raised for non-fallback JSON-RPC errors or malformed success envelopes."""

    request_id: str | None
    response_json: JsonDict
    message: str

    def __str__(self) -> str:
        return self.message


def _extract_text_candidates(payload: object) -> list[str]:
    if not isinstance(payload, list):
        return []

    texts: list[str] = []
    for part in payload:
        if not isinstance(part, dict):
            continue
        kind = part.get("kind") or part.get("type")
        if kind in {"text", "output_text"} and isinstance(part.get("text"), str):
            texts.append(part["text"])
    return texts


def extract_a2a_text(result: JsonDict) -> str | None:
    """Best-effort text extraction from several common A2A success shapes."""

    artifacts = result.get("artifacts")
    if isinstance(artifacts, list):
        texts: list[str] = []
        for artifact in artifacts:
            if isinstance(artifact, dict):
                texts.extend(_extract_text_candidates(artifact.get("parts")))
        if texts:
            return "\n".join(texts)

    texts = _extract_text_candidates(result.get("parts"))
    if texts:
        return "\n".join(texts)

    status = result.get("status")
    if isinstance(status, dict):
        message = status.get("message")
        if isinstance(message, dict):
            texts = _extract_text_candidates(message.get("parts"))
            if texts:
                return "\n".join(texts)

    return None


def build_a2a_request(fnol: JsonDict) -> JsonDict:
    """Create the blocking JSON-RPC envelope used by the triage orchestrator."""

    request_id = str(uuid.uuid4())
    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "method": "message/send",
        "params": {
            "message": {
                "role": "user",
                "kind": "message",
                "messageId": str(uuid.uuid4()),
                "parts": [
                    {
                        "kind": "text",
                        "text": json.dumps(fnol, ensure_ascii=False, sort_keys=True),
                    }
                ],
            },
            "configuration": {"blocking": True},
        },
    }


def is_hosted_agent_not_supported(response_json: JsonDict) -> bool:
    """Return True only when the JSON-RPC envelope indicates the hosted-agent A2A limitation."""

    if not isinstance(response_json, dict):
        return False

    error_payload = response_json.get("error")
    if not isinstance(error_payload, dict):
        return False

    data = error_payload.get("data")
    indicators: list[str] = []

    if isinstance(error_payload.get("code"), str):
        indicators.append(error_payload["code"])
    if isinstance(error_payload.get("message"), str):
        indicators.append(error_payload["message"])

    if isinstance(data, dict):
        for key in ("code", "detail", "message"):
            value = data.get(key)
            if isinstance(value, str):
                indicators.append(value)

    return any("HostedAgentNotSupported" in value for value in indicators)


def responses_url_from_a2a_url(a2a_url: str) -> str:
    """Convert an agent's A2A endpoint URL into its hosted Responses endpoint URL."""

    parsed = urlsplit(a2a_url)
    marker = "/endpoint/protocols/a2a"
    if marker not in parsed.path:
        raise ValueError("Expected an A2A endpoint path containing '/endpoint/protocols/a2a'.")

    query = dict(parse_qsl(parsed.query, keep_blank_values=True))
    query["api-version"] = query.get("api-version", "v1")
    return urlunsplit(
        (
            parsed.scheme,
            parsed.netloc,
            parsed.path.replace(marker, "/endpoint/protocols/openai/responses", 1),
            urlencode(query),
            parsed.fragment,
        )
    )


def _default_transport(url: str, payload: JsonDict, headers: dict[str, str]) -> JsonDict:
    """Minimal real transport used only outside tests."""

    request_headers = {"Content-Type": "application/json", **headers}
    http_request = request.Request(
        url=url,
        data=json.dumps(payload).encode("utf-8"),
        headers=request_headers,
        method="POST",
    )
    try:
        with request.urlopen(http_request, timeout=30) as response:
            body = response.read().decode("utf-8")
    except error.HTTPError as exc:
        details = exc.read().decode("utf-8", errors="replace")
        raise A2AProtocolError(
            request_id=str(payload.get("id")),
            response_json={},
            message=f"A2A transport failed with HTTP {exc.code}: {details[:400]}",
        ) from exc

    try:
        return json.loads(body)
    except json.JSONDecodeError as exc:
        raise A2AProtocolError(
            request_id=str(payload.get("id")),
            response_json={},
            message=f"A2A transport returned non-JSON content: {body[:200]}",
        ) from exc


def call_adjudicator_via_a2a(
    a2a_url: str,
    fnol: JsonDict,
    *,
    transport: Transport | None = None,
    headers: dict[str, str] | None = None,
) -> A2ASuccess:
    """POST a blocking JSON-RPC request and validate the body-level success contract."""

    payload = build_a2a_request(fnol)
    response_json = (transport or _default_transport)(a2a_url, payload, headers or {})
    request_id = str(response_json.get("id") or payload["id"])

    if is_hosted_agent_not_supported(response_json):
        raise HostedAgentNotSupportedError(
            request_id=request_id,
            response_json=response_json,
            message=(
                "Hosted agent A2A target is not supported by the service. "
                "Inspect the JSON-RPC envelope and use the hosted Responses fallback."
            ),
        )

    error_payload = response_json.get("error")
    if isinstance(error_payload, dict):
        raise A2AProtocolError(
            request_id=request_id,
            response_json=response_json,
            message=f"A2A call failed with JSON-RPC error: {json.dumps(error_payload, sort_keys=True)}",
        )

    result = response_json.get("result")
    if not isinstance(result, dict):
        raise A2AProtocolError(
            request_id=request_id,
            response_json=response_json,
            message="A2A success envelope did not include a JSON object in 'result'.",
        )

    return A2ASuccess(
        request_id=request_id,
        result=result,
        assistant_text=extract_a2a_text(result),
    )


def invoke_with_fallback(
    a2a_url: str,
    fnol: JsonDict,
    *,
    transport: Transport | None = None,
    fallback_callable: FallbackCallable,
    headers: dict[str, str] | None = None,
) -> InvocationOutcome:
    """Call the adjudicator over A2A, or use the hosted Responses fallback when required."""

    try:
        success = call_adjudicator_via_a2a(
            a2a_url,
            fnol,
            transport=transport,
            headers=headers,
        )
    except HostedAgentNotSupportedError as exc:
        responses_url = responses_url_from_a2a_url(a2a_url)
        fallback_result = fallback_callable(responses_url, fnol)
        return InvocationOutcome(
            protocol="responses",
            used_fallback=True,
            request_id=exc.request_id,
            result=fallback_result,
            assistant_text=None,
        )

    return InvocationOutcome(
        protocol="a2a",
        used_fallback=False,
        request_id=success.request_id,
        result=success.result,
        assistant_text=success.assistant_text,
    )

