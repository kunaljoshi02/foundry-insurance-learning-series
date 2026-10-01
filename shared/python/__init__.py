"""Shared helpers for the Foundry Insurance Learning Series modules.

These utilities are intentionally dependency-light (stdlib + azure-identity/azure-ai-projects
where noted) so each module can import what it needs without a heavy shared package install.
Nothing here performs network calls at import time.
"""
