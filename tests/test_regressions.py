"""Isolated regressions: real PySwitchbot/voluptuous, stubbed HA framework.

Run: python -m pytest tests
These do not replace HA integration or hardware tests.
"""
import asyncio
import importlib
import json
from pathlib import Path
import sys
from types import ModuleType, SimpleNamespace
from unittest.mock import AsyncMock

from bleak.backends.device import BLEDevice
from bleak.backends.scanner import AdvertisementData
import pytest
import switchbot

ROOT = Path(__file__).resolve().parents[1]


def module(name):
    obj = ModuleType(name)
    sys.modules[name] = obj
    return obj


class Abort(Exception):
    pass


class ConfigFlow:
    def __init_subclass__(cls, **kwargs):
        pass

    async def async_set_unique_id(self, value):
        self.unique_id = value

    def _abort_if_unique_id_configured(self):
        if self.unique_id in self.hass.ids:
            raise Abort('already_configured')

    def _async_current_ids(self, **kwargs):
        return self.hass.ids

    def async_show_form(self, **kwargs):
        return dict(type='form', **kwargs)

    def async_show_menu(self, **kwargs):
        return dict(type='menu', **kwargs)

    def async_abort(self, **kwargs):
        return dict(type='abort', **kwargs)

    def async_create_entry(self, **kwargs):
        return dict(type='create_entry', **kwargs)


module('homeassistant')
components = module('homeassistant.components')
bt = module('homeassistant.components.bluetooth')
components.bluetooth = bt
bt.BluetoothServiceInfoBleak = SimpleNamespace
entries = module('homeassistant.config_entries')
entries.ConfigFlow = ConfigFlow
entries.ConfigFlowResult = dict
entries.ConfigEntry = SimpleNamespace
const = module('homeassistant.const')
const.CONF_PASSWORD = 'password'
module('homeassistant.core').HomeAssistant = SimpleNamespace
module('homeassistant.exceptions').HomeAssistantError = RuntimeError
module('homeassistant.helpers')
update = module('homeassistant.helpers.update_coordinator')


class Coordinator:
    def __class_getitem__(cls, value):
        return cls

    def __init__(self, hass, *args, **kwargs):
        self.hass = hass
        self.data = None


update.DataUpdateCoordinator = Coordinator
update.UpdateFailed = RuntimeError
package = module('custom_components')
package.__path__ = [str(ROOT/'custom_components')]
package = module('custom_components.switchbot_bluetooth_extended')
package.__path__ = [str(ROOT/'custom_components/switchbot_bluetooth_extended')]
flowmod = importlib.import_module(package.__name__ + '.config_flow')
coordmod = importlib.import_module(package.__name__ + '.coordinator')
ADDRESS = 'EC:6F:03:C6:38:19'


def info(payload=b'H\x90\xd9', connectable=True, address=ADDRESS, source='esphome-proxy'):
    dev = BLEDevice(address, 'WoHand', {'source': source})
    adv = AdvertisementData('WoHand', {}, {'00000d00-0000-1000-8000-00805f9b34fb': payload} if payload else {}, [], None, -60, ())
    return SimpleNamespace(address=address, device=dev, advertisement=adv, connectable=connectable, source=source)


@pytest.fixture
def env(monkeypatch):
    h = SimpleNamespace(ids=set(), cache={True: [], False: []}, routes={})
    monkeypatch.setattr(bt, 'async_request_active_scan', AsyncMock(), raising=False)
    monkeypatch.setattr(bt, 'async_discovered_service_info', lambda hass, connectable: hass.cache[connectable], raising=False)
    monkeypatch.setattr(bt, 'async_ble_device_from_address', lambda hass, address, connectable: hass.routes.get(address.upper()), raising=False)
    monkeypatch.setattr(bt, 'async_last_service_info', lambda hass, address, connectable: next((i for i in hass.cache[connectable] if i.address.upper()==address.upper()), None), raising=False)
    f = flowmod.SwitchBotExtendedConfigFlow()
    f.hass = h
    f.context = {}
    return h, f


def run(coro):
    return asyncio.run(coro)


def register(h, adv, route=True):
    h.cache[False].append(adv)
    if adv.connectable:
        h.cache[True].append(adv)
    if route:
        h.routes[adv.address.upper()] = adv.device


@pytest.mark.parametrize('source', ['esphome-proxy', 'local'])
def test_discovery_routes(env, source):
    h, f = env
    adv = info(source=source)
    register(h, adv)
    result = run(f.async_step_select_device())
    assert result['step_id'] == 'select_device'
    assert result['data_schema']({'address': ADDRESS}) == {'address': ADDRESS}
    bt.async_request_active_scan.assert_awaited_once_with(h)
    assert run(f.async_step_select_device({'address': ADDRESS}))['step_id'] == 'confirm'
    assert run(f.async_step_confirm({}))['data'] == {'address': ADDRESS, 'name': 'Bot 3819'}
    assert f.unique_id == 'ec6f03c63819'


def test_passive_advertisement_other_connectable_route(env):
    h, f = env
    adv = info(connectable=False)
    register(h, adv)
    assert run(f.async_step_bluetooth(adv))['step_id'] == 'confirm'
    assert run(f.async_step_select_device())['step_id'] == 'select_device'


def test_passive_only_rejected(env):
    h, f = env
    adv = info(connectable=False)
    register(h, adv, route=False)
    assert run(f.async_step_bluetooth(adv))['reason'] == 'not_connectable'
    assert run(f.async_step_select_device())['step_id'] == 'manual'
    assert run(f.async_step_manual({'address': ADDRESS}))['errors']['base'] == 'not_connectable'


def test_empty_search_fallback_and_menu(env):
    h, f = env
    assert run(f.async_step_select_device())['step_id'] == 'manual'
    assert run(f.async_step_user())['menu_options'] == ['select_device', 'manual']


@pytest.mark.parametrize('address', [' ec:6f:03:c6:38:19 ', 'ec-6f-03-c6-38-19', 'ec6f03c63819'])
def test_manual_normalization_without_parsed_advertisement(env, address):
    h, f = env
    h.routes[ADDRESS] = info().device
    assert run(f.async_step_manual({'address': address}))['step_id'] == 'confirm'
    assert run(f.async_step_confirm({}))['data']['address'] == ADDRESS


@pytest.mark.parametrize('address', ['', 'nope', 'EC:6F:03:C6:38', 'EC:6F-03:C6:38:19', 'GG:6F:03:C6:38:19'])
def test_invalid_address(env, address):
    h, f = env
    assert run(f.async_step_manual({'address': address}))['errors'] == {'address': 'invalid_address'}
    bt.async_request_active_scan.assert_not_awaited()


def test_duplicate_manual_and_discovery(env):
    h, f = env
    adv = info()
    register(h, adv)
    h.ids.add('ec6f03c63819')
    with pytest.raises(Abort, match='already_configured'):
        run(f.async_step_manual({'address': ADDRESS}))
    with pytest.raises(Abort, match='already_configured'):
        run(f.async_step_bluetooth(adv))
    assert run(f.async_step_select_device())['step_id'] == 'manual'


def test_non_bot_not_offered_and_manual_rejected(env):
    h, f = env
    # Separate address avoids PySwitchbot's per-MAC model cache.
    adv = info(b'c\xd0Y\x00\x11\x04', address='AA:BB:CC:DD:EE:02')
    register(h, adv)
    assert run(f.async_step_select_device())['step_id'] == 'manual'
    assert run(f.async_step_bluetooth(adv))['reason'] == 'not_supported'
    assert run(f.async_step_manual({'address': adv.address}))['errors']['address'] == 'not_supported'


def test_encrypted_bot_password(env):
    h, f = env
    adv = info(b'\xc8\x10\xcf', address='AA:BB:CC:DD:EE:03')
    register(h, adv)
    result = run(f.async_step_bluetooth(adv))
    import voluptuous as vol
    with pytest.raises(vol.Invalid):
        result['data_schema']({})
    assert run(f.async_step_confirm({'password':'secret'}))['data']['password'] == 'secret'


def test_retry_manual_after_proxy_arrives(env):
    h, f = env
    assert run(f.async_step_manual({'address': ADDRESS}))['errors']
    register(h, info())
    assert run(f.async_step_manual({'address': ADDRESS}))['step_id'] == 'confirm'


def test_coordinator_manual_missing_advertisement_and_route_update(env):
    async def scenario():
        h, _ = env
        h.routes[ADDRESS] = info().device
        entry = SimpleNamespace(data={'address': ADDRESS, 'name':'Bot', 'password':'test'}, title='Bot')
        c = coordmod.SwitchBotExtendedCoordinator(h, entry)
        device = c._ensure_device()
        assert isinstance(device, switchbot.Switchbot)
        assert device._device is h.routes[ADDRESS]
        h.routes[ADDRESS] = info(source='replacement-proxy').device
        assert c._ensure_device()._device is h.routes[ADDRESS]
        h.routes.clear()
        with pytest.raises(RuntimeError, match='connectable'):
            c._ensure_device()
    run(scenario())


def test_coordinator_read_with_real_parser(env, monkeypatch):
    async def scenario():
        h, _ = env
        register(h, info())
        c = coordmod.SwitchBotExtendedCoordinator(h, SimpleNamespace(data={'address':ADDRESS}, title='Bot'))
        monkeypatch.setattr(switchbot.Switchbot, 'get_basic_info', AsyncMock(return_value={'holdSeconds':2}))
        result = await c._async_update_data()
        assert result['holdSeconds'] == 2
        assert result['rssi'] == -60
        assert 'battery' in result
    run(scenario())


def test_metadata_translation_keys():
    p=ROOT/'custom_components/switchbot_bluetooth_extended'
    m=json.loads((p/'manifest.json').read_text())
    assert m['domain']=='switchbot_bluetooth_extended' and m['version']=='0.1.1'
    assert m['requirements']==['PySwitchbot==2.7.0'] and m['config_flow'] is True
    def keys(d, prefix=''):
        return {prefix+k for k in d} | set().union(*(keys(v,prefix+k+'.') for k,v in d.items() if isinstance(v,dict)))
    expected=keys(json.loads((p/'strings.json').read_text()))
    for lang in ['en','de']:
        assert keys(json.loads((p/f'translations/{lang}.json').read_text())) == expected


def test_failed_basic_read_does_not_report_success(env, monkeypatch):
    async def scenario():
        h, _ = env
        register(h, info())
        c = coordmod.SwitchBotExtendedCoordinator(h, SimpleNamespace(data={'address': ADDRESS}, title='Bot'))
        monkeypatch.setattr(switchbot.Switchbot, 'get_basic_info', AsyncMock(return_value=None))
        with pytest.raises(RuntimeError, match='no basic settings'):
            await c._async_update_data()
    run(scenario())
