"""Supported desktop chat applications and their stable macOS identities.

The capture and Accessibility layers both need to identify the same client.  Keeping
the small set of bundle IDs and display names here prevents a window captured from one
application being filled into another when WeChat and Feishu are open together.
"""

from __future__ import annotations

from dataclasses import dataclass

import userconfig


@dataclass(frozen=True)
class ChatApp:
    """One supported macOS chat client and the identifiers exposed by macOS."""

    key: str
    label: str
    owner_names: tuple[str, ...]
    bundle_ids: tuple[str, ...]
    window_title_hints: tuple[str, ...]


# Bundle IDs are authoritative when available; owner names make source and regional
# desktop builds work too.  Lark is the international Feishu desktop client.
WECHAT = ChatApp(
    key="wechat",
    label="微信",
    owner_names=("微信", "WeChat"),
    bundle_ids=("com.tencent.xinWeChat",),
    window_title_hints=("微信", "WeChat"),
)
FEISHU = ChatApp(
    key="feishu",
    label="飞书",
    owner_names=("飞书", "Feishu", "Lark"),
    bundle_ids=("com.electron.lark", "com.bytedance.feishu"),
    window_title_hints=("飞书", "Feishu", "Lark"),
)
CHAT_APPS: tuple[ChatApp, ...] = (WECHAT, FEISHU)
_ALIASES = {"lark": "feishu", "feishu": "feishu", "wechat": "wechat", "微信": "wechat", "飞书": "feishu"}


def app_for_key(key: str | None) -> ChatApp | None:
    """Return one supported client, accepting the documented aliases."""
    normalized = _ALIASES.get((key or "").strip().lower(), (key or "").strip().lower())
    return next((app for app in CHAT_APPS if app.key == normalized), None)


def configured_apps() -> tuple[ChatApp, ...]:
    """Resolve ``JEV_CHAT_APP``; invalid values safely keep automatic detection enabled."""
    raw = userconfig.get("JEV_CHAT_APP").strip().lower()
    if raw and raw != "auto":
        app = app_for_key(raw)
        if app is not None:
            return (app,)
    return CHAT_APPS


def app_for_owner(owner: str, allowed: tuple[ChatApp, ...] | None = None) -> ChatApp | None:
    """Map a Quartz window-owner name to a selected supported client."""
    return next((app for app in (allowed or CHAT_APPS) if owner in app.owner_names), None)


def label_for_key(key: str | None) -> str:
    """Return a user-facing client label without leaking an internal bundle ID."""
    app = app_for_key(key)
    return app.label if app is not None else "聊天应用"
