#! /usr/bin/env python
# -*- coding: utf-8 -*-


# OpenFisca -- A versatile microsimulation software
# By: OpenFisca Team <contact@openfisca.fr>
#
# Copyright (C) 2011, 2012, 2013, 2014, 2015 OpenFisca Team
# https://github.com/openfisca
#
# This file is part of OpenFisca.
#
# OpenFisca is free software; you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# OpenFisca is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


from __future__ import division

import os

from openfisca_core import conv, scenarios
from openfisca_core.tools import assert_near
from openfisca_france.tests.base import tax_benefit_system
import yaml


def check(name, period_str, test):
    scenario = test['scenario']
    scenario.suggest()
    simulation = scenario.new_simulation(debug = True)
    output_variables = test.get(u'output_variables')
    if output_variables is not None:
        for variable_name, expected_value in output_variables.iteritems():
            assert_near(simulation.calculate(variable_name, accept_other_period = True), expected_value,
                error_margin = 0.005, message = u'{}: '.format(variable_name))


def test():
    dir_path = os.path.join(os.path.dirname(__file__), 'formulas')
    for filename in sorted(os.listdir(dir_path)):
        if not filename.endswith('.yaml'):
            continue
        filename_core = os.path.splitext(filename)[0]
        with open(os.path.join(dir_path, filename)) as yaml_file:
            test = yaml.load(yaml_file)
            tests, error = conv.pipe(
                conv.make_item_to_singleton(),
                conv.uniform_sequence(
                    scenarios.make_json_or_python_to_test(tax_benefit_system),
                    drop_none_items = True,
                    ),
                )(test)
            if error is not None:
                embedding_error = conv.embed_error(tests, u'errors', error)
                assert embedding_error is None, embedding_error
                conv.check((tests, error))  # Generate an error.

            for test in tests:
                if test.get(u'ignore', False):
                    continue
                yield check, test.get('name') or filename_core, unicode(test['scenario'].period), test


if __name__ == "__main__":
    import argparse
    import logging
    import sys

    parser = argparse.ArgumentParser(description = __doc__)
    parser.add_argument('-n', '--name', default = None, help = "partial name of tests to execute")
    parser.add_argument('-v', '--verbose', action = 'store_true', default = False, help = "increase output verbosity")
    args = parser.parse_args()
    logging.basicConfig(level = logging.DEBUG if args.verbose else logging.WARNING, stream = sys.stdout)

    for test_index, (function, name, period_str, test) in enumerate(test(), 1):
        if args.name is not None and args.name not in name:
            continue
        print("=" * 120)
        print("Test {}: {} - {}".format(test_index, name.encode('utf-8'), period_str))
        print("=" * 120)
        function(name, period_str, test)