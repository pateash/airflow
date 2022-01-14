#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
from typing import Dict, Optional, Callable

from github import GithubException

from airflow import AirflowException
from airflow.models import BaseOperator
from airflow.providers.github.hooks.github import GithubHook


class GithubOperator(BaseOperator):
    """
    GithubOperator to interact and perform action on Github API.
    This operator is designed to use Github Python SDK: https://github.com/PyGithub/PyGithub

    :param github_conn_id: reference to a pre-defined Github Connection
    :type github_conn_id: str
    :param github_method: method name from Github Python SDK to be called
    :type github_method: str
    :param github_method_args: required method parameters for the github_method. (templated)
    :type github_method_args: dict
    :param result_processor: function to further process the response from Github
    :type result_processor: function
    """

    template_fields = ("github_method_args",)

    def __init__(
        self,
        *,
        github_method: str,
        github_conn_id: str = 'github_default',
        github_method_args: Optional[dict] = None,
        result_processor: Optional[Callable] = None,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.github_conn_id = github_conn_id
        self.method_name = github_method
        self.github_method_args = github_method_args
        self.result_processor = result_processor

    def execute(self, context: Dict) -> Any:
        try:
            # Default method execution is on the top level Github client
            hook = GithubHook(github_conn_id=self.github_conn_id)
            resource = hook.client

            github_result = getattr(resource, self.method_name)(**self.github_method_args)
            if self.result_processor:
                return self.result_processor(context, github_result)

            return github_result

        except GithubException as github_error:
            raise AirflowException(f"Failed to execute GithubOperator, error: {str(github_error)}")
        except Exception as e:
            raise AirflowException(f"Github operator error: {str(e)}")
