"""Classify whether a Microsoft Entra auth context can satisfy OBO requirements.

The verified rule taught in this module is intentionally narrow:

- OBO succeeds only when the caller is an interactive signed-in human user,
- a delegated user token is available to exchange,
- and the principal type is `User`.

Anything else should be predicted as a failure before attempting a live tool call.
"""
from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class AuthContext:
    """Minimal facts needed to predict whether OBO can work."""

    is_interactive: bool
    has_user_token: bool
    principal_type: str


def predict_obo_outcome(context: AuthContext) -> tuple[bool, str]:
    """Return whether OBO should succeed for the supplied auth context.

    OBO is expected to work only for an interactive, signed-in user with a delegated user token.
    """

    principal_type = context.principal_type.strip().lower()

    if principal_type != "user":
        return (
            False,
            "OBO requires a user principal. Application or service-principal identities do not "
            "carry the interactive delegated user token required for an on-behalf-of exchange.",
        )

    if not context.is_interactive:
        return (
            False,
            "OBO requires an interactive signed-in user context. A background or headless call "
            "cannot satisfy the delegated-user requirement by itself.",
        )

    if not context.has_user_token:
        return (
            False,
            "OBO requires a delegated user token. Without a user token to exchange, the "
            "downstream connection should fail with a signed-in-user-required style error.",
        )

    return (
        True,
        "OBO can proceed because the caller is an interactive signed-in user and a delegated "
        "user token is available for exchange.",
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Predict whether an auth context will satisfy OBO.")
    parser.add_argument("--interactive", action="store_true", help="Set when the caller is an interactive signed-in user.")
    parser.add_argument("--has-user-token", action="store_true", help="Set when a delegated user token is available.")
    parser.add_argument(
        "--principal-type",
        default="User",
        help="Principal type to classify (for example: User, ServicePrincipal, Group).",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    context = AuthContext(
        is_interactive=args.interactive,
        has_user_token=args.has_user_token,
        principal_type=args.principal_type,
    )
    will_succeed, reason = predict_obo_outcome(context)
    print(
        json.dumps(
            {
                "context": asdict(context),
                "will_succeed": will_succeed,
                "reason": reason,
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
