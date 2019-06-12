from conifer.sources.base_loader import BaseLoader, LoaderMode, LoaderDisallowedAction

import pytest


def ro_loader():
    return BaseLoader(mode=LoaderMode.RO)


def wo_loader():
    return BaseLoader(mode=LoaderMode.WO)


def rw_loader():
    return BaseLoader(mode=LoaderMode.RW)


@pytest.mark.parametrize(
    "loader, mode",
    [
        (ro_loader(), LoaderMode.RO),
        (wo_loader(), LoaderMode.WO),
        (rw_loader(), LoaderMode.RW),
    ],
)
def test_loader_mode_set(loader, mode):
    assert loader.mode == mode


@pytest.mark.parametrize("loader", [(ro_loader()), (rw_loader())])
def test_load_config_allowed(loader):
    with pytest.raises(NotImplementedError):
        loader.load_config({})


@pytest.mark.parametrize("loader", [(wo_loader())])
def test_load_config_disallowed(loader):
    with pytest.raises(LoaderDisallowedAction):
        loader.load_config({})


@pytest.mark.parametrize("loader", [(wo_loader()), (rw_loader())])
def test_set_config_allowed(loader):
    with pytest.raises(NotImplementedError):
        loader.set_config({})


@pytest.mark.parametrize("loader", [(ro_loader())])
def test_set_config_disallowed(loader):
    with pytest.raises(LoaderDisallowedAction):
        loader.set_config({})
