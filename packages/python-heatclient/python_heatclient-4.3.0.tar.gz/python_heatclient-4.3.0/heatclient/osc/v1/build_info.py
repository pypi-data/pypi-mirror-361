#   Licensed under the Apache License, Version 2.0 (the "License"); you may
#   not use this file except in compliance with the License. You may obtain
#   a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#   WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#   License for the specific language governing permissions and limitations
#   under the License.
#

"""Orchestration v1 build info action implementations"""

import logging

from osc_lib.command import command
from osc_lib import utils

from heatclient.osc.v1 import common


class BuildInfo(command.ShowOne):
    """Retrieve build information."""

    log = logging.getLogger(__name__ + ".BuildInfo")

    def get_parser(self, prog_name):
        parser = super(BuildInfo, self).get_parser(prog_name)
        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)

        heat_client = self.app.client_manager.orchestration
        result = heat_client.build_info.build_info()

        formatters = {
            'api': common.JsonColumn,
            'engine': common.JsonColumn,
        }
        columns = sorted(list(result.keys()))
        return columns, utils.get_dict_properties(result, columns,
                                                  formatters=formatters)
