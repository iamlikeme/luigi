# -*- coding: utf-8 -*-
#
# Copyright 2018 Vote inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import os

from luigi.configuration import LuigiConfigParser, get_config
from luigi.configuration.cfg_parser import InterpolationMissingEnvvarError

from helpers import LuigiTestCase


class ConfigParserTest(LuigiTestCase):

    environ = {
        "TESTVAR": "1",
    }

    def setUp(self):
        self.environ_backup = {
            os.environ[key] for key in self.environ
            if key in os.environ
        }
        for key, value in self.environ.items():
            os.environ[key] = value
        LuigiConfigParser._instance = None
        super(ConfigParserTest, self).setUp()

    def tearDown(self):
        for key in self.environ:
            os.environ.pop(key)
        for key, value in self.environ_backup:
            os.environ[key] = value

    def test_basic_interpolation(self):
        # Make sure the default ConfigParser behaviour is not broken
        config = get_config()
        config.set("test", "a", "testval")
        config.set("test", "b", "%(a)s")
        config.set("test", "c", "%(a)s%(a)s")

        self.assertEqual(config.get("test", "b"), config.get("test", "a"))
        self.assertEqual(config.get("test", "c"), 2 * config.get("test", "a"))

    def test_env_interpolation(self):
        config = get_config()
        config.set("test", "a", "${TESTVAR}")
        config.set("test", "b", "${TESTVAR} ${TESTVAR}")
        config.set("test", "c", "${TESTVAR} %(a)s")
        config.set("test", "d", "${NONEXISTING}")

        self.assertEqual(config.get("test", "a"), "1")
        self.assertEqual(config.getint("test", "a"), 1)
        self.assertEqual(config.getboolean("test", "a"), True)

        self.assertEqual(config.get("test", "b"), "1 1")

        self.assertEqual(config.get("test", "c"), "1 1")

        with self.assertRaises(InterpolationMissingEnvvarError):
            config.get("test", "d")
