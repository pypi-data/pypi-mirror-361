# SPDX-FileCopyrightText: 2024 Dalibo
#
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

from collections.abc import Coroutine, Iterator
from functools import singledispatch
from typing import TypedDict

from pgtoolkit.hba import HBA, HBAComment, HBARecord
from pgtoolkit.hba import parse as parse_hba

from . import deps, hookimpl, postgresql, ui, util
from .manager import InstanceManager
from .models import PostgreSQLInstance, interface

logger = util.get_logger(__name__)


def serialize(record: interface.HbaRecord) -> dict[str, str]:
    """Serialize interface.HbaRecord to a dict from which a
    pgtoolkit.HBARecord instance can be constructed.
    """
    dumped = record.model_dump(exclude_none=True)
    dumped.update(**dumped.pop("connection", {"type": "local"}))
    dumped["conntype"] = dumped.pop("type")
    return dumped


@deps.use
def get(instance: PostgreSQLInstance, *, manager: InstanceManager = deps.Auto) -> HBA:
    hba = manager.pg_hba_config(instance)
    return parse_hba(hba)


@deps.use
async def save(
    instance: PostgreSQLInstance,
    hba: HBA,
    *,
    reload_on_change: bool = False,
    manager: InstanceManager = deps.Auto,
) -> None:
    cur_hba = get(instance)
    if cur_hba == hba:
        return
    manager.configure_pg_hba(instance, hba=[str(r) for r in hba])
    if await postgresql.is_running(instance) and ui.confirm(
        "PostgreSQL needs to be reloaded; reload now?", reload_on_change
    ):
        await manager.reload_postgresql(instance)


async def add(instance: PostgreSQLInstance, record: interface.HbaRecord) -> None:
    hba = get(instance)
    hba.lines.append(HBARecord(**serialize(record)))
    await save(instance, hba)
    logger.info("entry added to HBA configuration")


async def remove(instance: PostgreSQLInstance, record: interface.HbaRecord) -> None:
    hba = get(instance)
    if hba.remove(filter=None, **serialize(record)):
        await save(instance, hba)
        logger.info("entry removed from HBA configuration")
    else:
        logger.error("entry not found in HBA configuration")


@hookimpl
async def role_change(
    role: interface.BaseRole, instance: PostgreSQLInstance
) -> tuple[bool, bool]:
    """Create / Update / Remove entries in HBA configuration for the given role"""
    return await _role_change(role, instance)


async def _role_change(
    role: interface.BaseRole, instance: PostgreSQLInstance
) -> tuple[bool, bool]:
    return await _async_func_role_change(role, instance)


@singledispatch
def _async_func_role_change(
    role: interface.BaseRole, instance: PostgreSQLInstance
) -> Coroutine[None, None, tuple[bool, bool]]:
    raise NotImplementedError


@_async_func_role_change.register
def _(
    role: interface.RoleDropped, instance: PostgreSQLInstance
) -> Coroutine[None, None, tuple[bool, bool]]:
    async def async_role_change() -> tuple[bool, bool]:
        hba = get(instance)
        if hba.remove(user=role.name):
            logger.info("removing entries from HBA configuration")
            await save(instance, hba)
            return (True, True)
        return False, False

    return async_role_change()


@_async_func_role_change.register
def _(
    role: interface.Role, instance: PostgreSQLInstance
) -> Coroutine[None, None, tuple[bool, bool]]:
    async def async_role_change() -> tuple[bool, bool]:
        hba = get(instance)
        changed = False
        records: list[HBAComment | HBARecord] = []

        for entry in role.hba_records:
            record = interface.HbaRecord(
                **entry.model_dump(exclude={"state"}), user=role.name
            )
            serialized = serialize(record)
            if entry.state == "present":
                records.append(HBARecord(**serialized))
            elif entry.state == "absent":
                changed = hba.remove(filter=None, **serialized) or changed

        if records:
            changed = hba.merge(HBA(records)) or changed

        if changed:
            logger.info("HBA configuration updated")
            await save(instance, hba)

        return changed, changed

    return async_role_change()


def records(
    instance: PostgreSQLInstance, name: str
) -> Iterator[interface.HbaRecordForRole]:
    """Yield HBA records matching named role on instance."""
    hba = get(instance)
    lines = [line for line in hba if line.matches(user=name)]
    for line in lines:
        record = line.as_dict()
        r = {
            "database": record["database"],
            "method": record["method"],
        }
        if line.conntype != "local":
            r["connection"] = {
                "type": record["conntype"],
                "address": record["address"],
                "netmask": record["netmask"] if "netmask" in record else None,
            }
        yield interface.HbaRecordForRole(**r)


class RoleInspect(TypedDict):
    hba_records: list[interface.HbaRecordForRole]


@hookimpl
def role_inspect(instance: PostgreSQLInstance, name: str) -> RoleInspect:
    return {"hba_records": list(records(instance, name))}
