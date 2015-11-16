# Licensed to the StackStorm, Inc ('StackStorm') under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import mock

from st2common.services import action as action_service
from st2tests.fixturesloader import FixturesLoader
from tests.base import APIControllerWithRBACTestCase
from tests.unit.controllers.v1.test_alias_execution import DummyActionExecution

FIXTURES_PACK = 'aliases'

TEST_MODELS = {
    'aliases': ['alias1.yaml', 'alias2.yaml'],
    'actions': ['action1.yaml'],
    'runners': ['runner1.yaml']
}

TEST_LOAD_MODELS = {
    'aliases': ['alias3.yaml']
}

__all__ = [
    'AliasExecutionWithRBACTestCase'
]


class AliasExecutionWithRBACTestCase(APIControllerWithRBACTestCase):

    def setUp(self):
        super(AliasExecutionWithRBACTestCase, self).setUp()

        self.models = FixturesLoader().save_fixtures_to_db(fixtures_pack=FIXTURES_PACK,
                                                          fixtures_dict=TEST_MODELS)
        self.alias1 = self.models['aliases']['alias1.yaml']
        self.alias2 = self.models['aliases']['alias2.yaml']

    @mock.patch.object(action_service, 'request',
                       return_value=(None, DummyActionExecution(id_=1)))
    def test_live_action_context_user_is_set_to_authenticated_user(self, request):
        # Verify that the user inside the context of live action is set to authenticated user
        # which hit the endpoint. This is important for RBAC and many other things.
        user_db = self.users['admin']
        self.use_user(user_db)

        command = 'Lorem ipsum value1 dolor sit "value2, value3" amet.'
        post_resp = self._do_post(alias_execution=self.alias2, command=command)
        self.assertEqual(post_resp.status_int, 200)

        live_action_db = request.call_args[0][0]
        self.assertEquals(live_action_db.context['user'], 'admin')

    def _do_post(self, alias_execution, command, expect_errors=False):
        execution = {'name': alias_execution.name,
                     'format': alias_execution.formats[0],
                     'command': command,
                     'user': 'stanley',
                     'source_channel': 'test',
                     'notification_route': 'test'}
        return self.app.post_json('/v1/aliasexecution', execution,
                                  expect_errors=expect_errors)
