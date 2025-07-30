from __future__ import annotations

import operator
from typing import TYPE_CHECKING

from tsbot.exceptions import TSPermissionError

from teamspeak_bot.utils import get

if TYPE_CHECKING:
    from collections.abc import Sequence

    from tsbot import TSBot, TSCtx


def has_group(
    groups: Sequence[str],
    client_groups: Sequence[dict[str, str]],
    *,
    strict: bool = False,
) -> bool:
    op = operator.eq if strict else operator.contains
    return any(op(cg["name"], g) for g in groups for cg in client_groups)


async def check_groups(
    bot: TSBot,
    ctx: TSCtx,
    groups: Sequence[str],
    *,
    strict: bool = False,
) -> bool:
    return has_group(groups, await get.client_server_groups(bot, ctx), strict=strict)


def check_uids(uids: Sequence[str], ctx: TSCtx) -> bool:
    return ctx.get("invokeruid") in uids


def check_uids_and_server_groups(  # noqa: ANN201
    uids: tuple[str, ...] | None,
    server_groups: tuple[str, ...] | None,
    *,
    strict: bool = False,
):
    async def is_allowed_to_run(bot: TSBot, ctx: TSCtx, *a: str | None, **kw: str | None) -> None:
        if uids and check_uids(uids, ctx):
            return

        if server_groups and await check_groups(bot, ctx, server_groups, strict=strict):
            return

        raise TSPermissionError("Client not permitted to run this command")

    return is_allowed_to_run
