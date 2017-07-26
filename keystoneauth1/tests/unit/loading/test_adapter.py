# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from oslo_config import cfg
from oslo_config import fixture as config

from keystoneauth1 import loading
from keystoneauth1.tests.unit.loading import utils


class ConfLoadingTests(utils.TestCase):

    GROUP = 'adaptergroup'

    def setUp(self):
        super(ConfLoadingTests, self).setUp()

        self.conf_fx = self.useFixture(config.Config())
        loading.register_adapter_conf_options(self.conf_fx.conf, self.GROUP)

    def test_load(self):
        self.conf_fx.config(
            service_type='type', service_name='name',
            valid_interfaces='internal',
            region_name='region', endpoint_override='endpoint',
            version='2.0', group=self.GROUP)
        adap = loading.load_adapter_from_conf_options(
            self.conf_fx.conf, self.GROUP, session='session', auth='auth')
        self.assertEqual('type', adap.service_type)
        self.assertEqual('name', adap.service_name)
        self.assertEqual(['internal'], adap.interface)
        self.assertEqual('region', adap.region_name)
        self.assertEqual('endpoint', adap.endpoint_override)
        self.assertEqual('session', adap.session)
        self.assertEqual('auth', adap.auth)
        self.assertEqual('2.0', adap.version)
        self.assertIsNone(adap.min_version)
        self.assertIsNone(adap.max_version)

    def test_load_valid_interfaces_list(self):
        self.conf_fx.config(
            service_type='type', service_name='name',
            valid_interfaces=['internal', 'public'],
            region_name='region', endpoint_override='endpoint',
            version='2.0', group=self.GROUP)
        adap = loading.load_adapter_from_conf_options(
            self.conf_fx.conf, self.GROUP, session='session', auth='auth')
        self.assertEqual('type', adap.service_type)
        self.assertEqual('name', adap.service_name)
        self.assertEqual(['internal', 'public'], adap.interface)
        self.assertEqual('region', adap.region_name)
        self.assertEqual('endpoint', adap.endpoint_override)
        self.assertEqual('session', adap.session)
        self.assertEqual('auth', adap.auth)
        self.assertEqual('2.0', adap.version)
        self.assertIsNone(adap.min_version)
        self.assertIsNone(adap.max_version)

    def test_load_valid_interfaces_comma_list(self):
        self.conf_fx.config(
            service_type='type', service_name='name',
            valid_interfaces='internal,public',
            region_name='region', endpoint_override='endpoint',
            version='2.0', group=self.GROUP)
        adap = loading.load_adapter_from_conf_options(
            self.conf_fx.conf, self.GROUP, session='session', auth='auth')
        self.assertEqual('type', adap.service_type)
        self.assertEqual('name', adap.service_name)
        self.assertEqual(['internal', 'public'], adap.interface)
        self.assertEqual('region', adap.region_name)
        self.assertEqual('endpoint', adap.endpoint_override)
        self.assertEqual('session', adap.session)
        self.assertEqual('auth', adap.auth)
        self.assertEqual('2.0', adap.version)
        self.assertIsNone(adap.min_version)
        self.assertIsNone(adap.max_version)

    def test_load_old_interface(self):
        self.conf_fx.config(
            service_type='type', service_name='name',
            interface='internal',
            region_name='region', endpoint_override='endpoint',
            version='2.0', group=self.GROUP)
        adap = loading.load_adapter_from_conf_options(
            self.conf_fx.conf, self.GROUP, session='session', auth='auth')
        self.assertEqual('type', adap.service_type)
        self.assertEqual('name', adap.service_name)
        self.assertEqual('internal', adap.interface)
        self.assertEqual('region', adap.region_name)
        self.assertEqual('endpoint', adap.endpoint_override)
        self.assertEqual('session', adap.session)
        self.assertEqual('auth', adap.auth)
        self.assertEqual('2.0', adap.version)
        self.assertIsNone(adap.min_version)
        self.assertIsNone(adap.max_version)

    def test_load_bad_valid_interfaces_value(self):
        self.conf_fx.config(
            service_type='type', service_name='name',
            valid_interfaces='bad',
            region_name='region', endpoint_override='endpoint',
            version='2.0', group=self.GROUP)
        self.assertRaises(
            TypeError,
            loading.load_adapter_from_conf_options,
            self.conf_fx.conf, self.GROUP, session='session', auth='auth')

    def test_load_version_range(self):
        self.conf_fx.config(
            service_type='type', service_name='name',
            valid_interfaces='internal',
            region_name='region', endpoint_override='endpoint',
            min_version='2.0', max_version='3.0', group=self.GROUP)
        adap = loading.load_adapter_from_conf_options(
            self.conf_fx.conf, self.GROUP, session='session', auth='auth')
        self.assertEqual('type', adap.service_type)
        self.assertEqual('name', adap.service_name)
        self.assertEqual(['internal'], adap.interface)
        self.assertEqual('region', adap.region_name)
        self.assertEqual('endpoint', adap.endpoint_override)
        self.assertEqual('session', adap.session)
        self.assertEqual('auth', adap.auth)
        self.assertIsNone(adap.version)
        self.assertEqual('2.0', adap.min_version)
        self.assertEqual('3.0', adap.max_version)

    def test_interface_conflict(self):
        self.conf_fx.config(
            service_type='type', service_name='name', interface='iface',
            valid_interfaces='internal,public',
            region_name='region', endpoint_override='endpoint',
            group=self.GROUP)

        self.assertRaises(
            TypeError,
            loading.load_adapter_from_conf_options,
            self.conf_fx.conf, self.GROUP, session='session', auth='auth')

    def test_load_bad_version(self):
        self.conf_fx.config(
            service_type='type', service_name='name',
            valid_interfaces='iface',
            region_name='region', endpoint_override='endpoint',
            version='2.0', min_version='2.0', max_version='3.0',
            group=self.GROUP)

        self.assertRaises(
            TypeError,
            loading.load_adapter_from_conf_options,
            self.conf_fx.conf, self.GROUP, session='session', auth='auth')

    def test_get_conf_options(self):
        opts = loading.get_adapter_conf_options()
        for opt in opts:
            if opt.name != 'valid-interfaces':
                self.assertIsInstance(opt, cfg.StrOpt)
            else:
                self.assertIsInstance(opt, cfg.ListOpt)
        self.assertEqual({'service-type', 'service-name',
                          'interface', 'valid-interfaces',
                          'region-name', 'endpoint-override', 'version',
                          'min-version', 'max-version'},
                         {opt.name for opt in opts})

    def test_get_conf_options_undeprecated(self):
        opts = loading.get_adapter_conf_options(include_deprecated=False)
        for opt in opts:
            if opt.name != 'valid-interfaces':
                self.assertIsInstance(opt, cfg.StrOpt)
            else:
                self.assertIsInstance(opt, cfg.ListOpt)
        self.assertEqual({'service-type', 'service-name', 'valid-interfaces',
                          'region-name', 'endpoint-override', 'version',
                          'min-version', 'max-version'},
                         {opt.name for opt in opts})
