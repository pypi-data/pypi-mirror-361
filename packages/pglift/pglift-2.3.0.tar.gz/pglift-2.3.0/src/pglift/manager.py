# SPDX-FileCopyrightText: 2025 Dalibo
#
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

from collections.abc import Iterator, Sequence
from contextlib import contextmanager
from contextvars import ContextVar
from typing import Annotated, Protocol

from pgtoolkit import conf as pgconf

from . import patroni, postgresql
from .deps import Dependency
from .models import PostgreSQLInstance, interface
from .settings import Settings
from .types import ConfigChanges, PostgreSQLStopMode


class AbstractInstanceManager(Protocol):
    """Interface for instance manager, define operations for
    instance operation and configuration.
    """

    async def init_postgresql(
        self, manifest: interface.Instance, instance: PostgreSQLInstance
    ) -> None: ...

    async def deinit_postgresql(self, instance: PostgreSQLInstance) -> None: ...

    async def configure_postgresql(
        self,
        configuration: pgconf.Configuration,
        instance: PostgreSQLInstance,
        manifest: interface.Instance,
    ) -> ConfigChanges | None: ...

    def configure_pg_hba(
        self, instance: PostgreSQLInstance, hba: list[str]
    ) -> None: ...

    def pg_hba_config(self, instance: PostgreSQLInstance) -> list[str]: ...

    def configure_auth(
        self, instance: PostgreSQLInstance, manifest: interface.Instance
    ) -> bool: ...

    async def start_postgresql(
        self,
        instance: PostgreSQLInstance,
        foreground: bool,
        *,
        wait: bool,
        timeout: int = ...,
        run_hooks: bool = True,
        **runtime_parameters: str,
    ) -> None: ...

    async def stop_postgresql(
        self,
        instance: PostgreSQLInstance,
        mode: PostgreSQLStopMode,
        wait: bool,
        deleting: bool = False,
        run_hooks: bool = True,
    ) -> None: ...

    async def restart_postgresql(
        self, instance: PostgreSQLInstance, mode: PostgreSQLStopMode, wait: bool
    ) -> None: ...

    async def reload_postgresql(self, instance: PostgreSQLInstance) -> None: ...

    async def promote_postgresql(self, instance: PostgreSQLInstance) -> None: ...

    async def demote_postgresql(
        self,
        instance: PostgreSQLInstance,
        source: postgresql.RewindSource,
        *,
        rewind_opts: Sequence[str] = (),
    ) -> None: ...


VAR = ContextVar[AbstractInstanceManager]("InstanceManager")

InstanceManager = Annotated[AbstractInstanceManager, Dependency(VAR)]


@contextmanager
def use(manager: AbstractInstanceManager) -> Iterator[None]:
    """Alter the contextvar to manager (patroni or postgresql) to use for mananing
    the instances.
    """
    token = VAR.set(manager)
    try:
        yield
    finally:
        VAR.reset(token)


@contextmanager
def from_instance(instance: PostgreSQLInstance) -> Iterator[None]:
    """Alter the ContextVar defining the module (patroni or  postgresql) to
    configure and manage the instance.
    """
    yield from _set_instance_manager(instance, instance._settings)


@contextmanager
def from_manifest(manifest: interface.Instance, settings: Settings) -> Iterator[None]:
    """Alter the ContextVar defining the module (patroni or  postgresql) to
    configure and manage the instance.
    """
    yield from _set_instance_manager(manifest, settings)


def _set_instance_manager(
    instance: PostgreSQLInstance | interface.Instance, settings: Settings
) -> Iterator[None]:
    """Set the instance manager to patroni if Patroni is available (in settings)
    and managing the instance.
    """
    mngr = (
        patroni
        if patroni.available(settings) and patroni.is_managed(instance)
        else postgresql
    )

    with use(mngr):
        yield
