# SPDX-FileCopyrightText: 2021 Dalibo
#
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

from collections.abc import Iterator, Sequence
from functools import singledispatch
from pathlib import Path
from typing import Annotated, Any, Literal, NoReturn

import pgtoolkit.conf
from pydantic import Field

from .. import exceptions, hookimpl, postgresql, systemd, types, util
from ..models import Instance, PostgreSQLInstance, interface
from ..settings import Settings
from ..system import svc
from . import impl, models
from .impl import available as available
from .impl import get_settings as get_settings
from .models import build
from .models import interface as i
from .models import system as s

logger = util.get_logger(__name__)


def register_if(settings: Settings) -> bool:
    return available(settings) is not None


@hookimpl
def system_lookup(instance: PostgreSQLInstance) -> s.Service | None:
    settings = get_settings(instance._settings)
    if p := models.patroni(instance.qualname, settings):
        return models.service(instance.qualname, p, settings)
    return None


@hookimpl
def instance_model() -> types.ComponentModel:
    return types.ComponentModel(
        i.Service.__service__,
        (
            Annotated[
                i.Service | None,
                Field(
                    description="Configuration for the Patroni service, if enabled in site settings"
                ),
            ],
            None,
        ),
    )


@hookimpl
async def standby_model(instance: PostgreSQLInstance) -> NoReturn | None:
    if system_lookup(instance) is None:
        return None
    raise ValueError("standby not supported with Patroni")


@hookimpl
async def get(instance: Instance, running: bool) -> i.Service | None:
    settings = get_settings(instance._settings)
    if (patroni := models.patroni(instance.qualname, settings)) is None:
        return None
    if running:
        cluster_members = await impl.cluster_members(patroni)
    else:
        cluster_members = []
    is_paused = await impl.is_paused(patroni)
    return i.Service(
        cluster=patroni.scope,
        node=patroni.name,
        postgresql={
            "connect_host": types.address_host(patroni.postgresql.connect_address)
        },
        restapi=patroni.restapi,
        cluster_members=cluster_members,
        is_paused=is_paused,
    )


SYSTEMD_SERVICE_NAME = "pglift-patroni@.service"


@hookimpl
def systemd_units() -> list[str]:
    return [SYSTEMD_SERVICE_NAME]


@hookimpl
def systemd_unit_templates(settings: Settings) -> Iterator[tuple[str, str]]:
    s = get_settings(settings)
    configpath = str(s.configpath).replace("{name}", "%i")
    yield (
        SYSTEMD_SERVICE_NAME,
        systemd.template(SYSTEMD_SERVICE_NAME).format(
            executeas=systemd.executeas(settings),
            configpath=configpath,
            execpath=s.execpath,
        ),
    )


@hookimpl
def systemd_tmpfilesd_managed_dir(settings: Settings) -> Iterator[tuple[str, Path]]:
    s = get_settings(settings)
    yield "patroni", s.pid_file.parent


@singledispatch
def is_managed(instance: PostgreSQLInstance | interface.Instance) -> bool:
    """Determine if patroni manages or should manage an instance."""
    raise NotImplementedError


@is_managed.register
def _(instance: PostgreSQLInstance) -> bool:
    s = get_settings(instance._settings)
    return models.patroni(instance.qualname, s) is not None


@is_managed.register
def _(instance: interface.Instance) -> bool:
    try:
        instance.service(i.Service)
        return True
    except ValueError:
        return False


async def init_postgresql(
    manifest: interface.Instance, instance: PostgreSQLInstance
) -> None:
    """Initialize PostgreSQL database cluster through Patroni by configuring
    Patroni, then starting it (as the only way to get the actual instance
    created).
    """
    settings = get_settings(instance._settings)
    service_manifest = manifest.service(i.Service)

    # Upon upgrade, we call plain 'initdb', so we should not get there. On the
    # other hand, Patroni service configuration is done through
    # configure_postgresql() hook implementation below.
    assert manifest.upgrading_from is None

    configuration = postgresql.configuration(manifest, instance._settings)
    patroni = impl.setup(
        instance, manifest, service_manifest, settings, configuration, validate=True
    )
    service = models.service(instance.qualname, patroni, settings)
    await impl.init(instance, patroni, service)


async def configure_postgresql(
    configuration: pgtoolkit.conf.Configuration,
    instance: PostgreSQLInstance,
    manifest: interface.Instance,
) -> types.ConfigChanges | None:
    """Build and validate Patroni configuration, and return changes to PostgreSQL configuration."""
    settings = get_settings(instance._settings)
    service_manifest = manifest.service(i.Service)

    if manifest.creating and not manifest.upgrading_from:
        return {}

    if manifest.upgrading_from:
        actual = models.patroni(manifest.upgrading_from.qualname, settings)
        assert actual is not None  # Expected since we're not "creating" the service.
        patroni = impl.upgrade(
            instance,
            manifest,
            actual,
            service_manifest.postgresql,
            settings,
            configuration,
        )
    else:
        if actual := models.patroni(instance.qualname, settings):
            # Instance "alter".
            patroni = impl.update(
                actual, instance.qualname, service_manifest, settings, configuration
            )

        else:
            # Instance is a standalone being converted as a member of a Patroni cluster.
            # First stop PostgreSQL.
            await postgresql.stop_postgresql(instance, mode="fast", wait=True)
            # Then setup Patroni as for a new instance.
            patroni = impl.setup(
                instance,
                manifest,
                service_manifest,
                settings,
                configuration,
                validate=True,
            )
            # And finally, restart PostgreSQL through Patroni.
            await start_postgresql(instance, wait=True, foreground=False)
            # As there is no "changes", return an empty dict to avoid
            # restarting again.
            return {}

    changes = impl.postgresql_changes(
        actual.postgresql if actual else None, patroni.postgresql
    )
    if actual and patroni != actual:
        # We need to reload Patroni if its configuration changed, even if this
        # does not concern PostgreSQL parameters.
        if await impl.check_api_status(actual, logger=None):
            await impl.reload(actual)
        else:
            logger.warning("not reloading Patroni REST API as it's not running")
    return changes


def configure_auth(*args: Any, **kwargs: Any) -> Literal[False]:
    # no-op, since pg_hba.conf and pg_ident.conf are installed
    # through Patroni configuration.
    return False


def pg_hba_config(instance: PostgreSQLInstance) -> list[str]:
    settings = get_settings(instance._settings)
    patroni = build.Patroni.get(instance.qualname, settings)
    return patroni.postgresql.pg_hba


def configure_pg_hba(instance: PostgreSQLInstance, hba: list[str]) -> None:
    settings = get_settings(instance._settings)
    patroni = build.Patroni.get(instance.qualname, settings)
    impl.update_hba(patroni, instance.qualname, settings, hba=hba)


@hookimpl
def postgresql_editable_conf(instance: PostgreSQLInstance) -> str | None:
    settings = get_settings(instance._settings)
    if (patroni := models.patroni(instance.qualname, settings)) is None:
        return None
    conf = pgtoolkit.conf.Configuration()
    with conf.edit() as entries:
        for k, v in patroni.postgresql.parameters.items():
            entries.add(k, v)
    return "".join(conf.lines)


async def start_postgresql(
    instance: PostgreSQLInstance,
    foreground: bool,
    *,
    wait: bool,
    timeout: int = postgresql.WAIT_TIMEOUT,
    run_hooks: bool = True,  # noqa: ARG001
    **runtime_parameters: str,
) -> None:
    """Start PostgreSQL with Patroni."""
    service = system_lookup(instance)
    assert service
    settings = instance._settings
    postgresql.ensure_socket_directory(settings)
    await impl.start(settings, service, foreground=foreground)
    if wait:
        await postgresql.wait_ready(instance, timeout=timeout)


async def stop_postgresql(
    instance: PostgreSQLInstance,
    mode: types.PostgreSQLStopMode,  # noqa: ARG001
    wait: bool,  # noqa: ARG001
    deleting: bool = False,
    run_hooks: bool = True,  # noqa: ARG001
) -> None:
    """Stop PostgreSQL through Patroni.

    If 'deleting', do nothing as this will be handled upon by Patroni
    deconfiguration.
    """
    service = system_lookup(instance)
    assert service
    if not deleting:
        await impl.stop(instance._settings, service)


async def restart_postgresql(
    instance: PostgreSQLInstance,
    mode: types.PostgreSQLStopMode,  # noqa: ARG001
    wait: bool,  # noqa: ARG001
) -> None:
    """Restart PostgreSQL with Patroni."""
    settings = get_settings(instance._settings)
    patroni = build.Patroni.get(instance.qualname, settings)
    await impl.restart(patroni)


async def reload_postgresql(instance: PostgreSQLInstance) -> None:
    settings = get_settings(instance._settings)
    patroni = build.Patroni.get(instance.qualname, settings)
    await impl.reload(patroni)


async def promote_postgresql(
    instance: PostgreSQLInstance,  # noqa: ARG001
) -> None:
    raise exceptions.UnsupportedError(
        "unsupported operation: instance managed by Patroni"
    )


async def demote_postgresql(
    instance: PostgreSQLInstance,  # noqa: ARG001
    source: postgresql.RewindSource,  # noqa: ARG001
    *,
    rewind_opts: Sequence[str] = (),  # noqa: ARG001
) -> None:
    raise exceptions.UnsupportedError(
        "unsupported operation: instance managed by Patroni"
    )


@hookimpl
def postgresql_service_name(instance: PostgreSQLInstance) -> str | None:
    if system_lookup(instance) is None:
        return None
    return "patroni"


@hookimpl
async def instance_status(instance: Instance) -> tuple[types.Status, str] | None:
    try:
        service = instance.service(s.Service)
    except ValueError:
        return None
    return (await svc.status(instance._settings, service), "Patroni API")


@hookimpl
async def instance_upgraded(old: PostgreSQLInstance) -> None:
    if (service := system_lookup(old)) is None:
        return
    await impl.remove_cluster(service)


async def deinit_postgresql(instance: PostgreSQLInstance) -> None:
    """Uninstall Patroni from an instance being dropped."""
    if service := system_lookup(instance):
        await impl.delete(instance._settings, service)
        postgresql.delete_postgresql_data(instance)


@hookimpl
def instance_env(instance: Instance) -> dict[str, str]:
    settings = get_settings(instance._settings)
    if (s := system_lookup(instance.postgresql)) is None:
        return {}
    configpath = impl._configpath(instance.qualname, settings)
    return {
        "PATRONI_NAME": s.node,
        "PATRONI_SCOPE": s.cluster,
        "PATRONICTL_CONFIG_FILE": str(configpath),
    }


@hookimpl
def logrotate_config(settings: Settings) -> str:
    s = get_settings(settings)
    return impl.template("logrotate.conf").format(logpath=s.logpath)
