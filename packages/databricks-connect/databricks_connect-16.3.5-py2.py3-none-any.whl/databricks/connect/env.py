#
# DATABRICKS CONFIDENTIAL & PROPRIETARY
# __________________
#
# Copyright 2020-present Databricks, Inc.
# All Rights Reserved.
#
# NOTICE:  All information contained herein is, and remains the property of Databricks, Inc.
# and its suppliers, if any.  The intellectual and technical concepts contained herein are
# proprietary to Databricks, Inc. and its suppliers and may be covered by U.S. and foreign Patents,
# patents in process, and are protected by trade secret and/or copyright law. Dissemination, use,
# or reproduction of this information is strictly forbidden unless prior written permission is
# obtained from Databricks, Inc.
#
# If you view or obtain a copy of this information and believe Databricks, Inc. may not have
# intended it to be made available, please promptly report it to Databricks Legal Department
# @ legal@databricks.com.
#

from typing import Any


class DatabricksEnv:
    """Private Preview. API may incur backwards incompatible changes in future releases.

    Specify the Python environment used while executing user-defined functions.
    """
    def __init__(self):
        # NOTE: Include any new state modifying members in the `_as_hashable` method.
        self._dependencies = []
        raise NotImplementedError("DatabricksEnv is a Private Preview API and is not widely available yet.")

    @property
    def dependencies(self) -> list[str]:
        """Return a copy of environment's dependencies."""
        return self._dependencies.copy()

    def withDependencies(self, dependencies: list[str]) -> 'DatabricksEnv':
        """Add a list of dependencies to the environment.

        Packages are installed in the same order as specified.
        When the same package is specified twice with different versions, the latter wins.

        Currently supported dependency types are:
        1. PyPI packages, specified according to PEP 508,
            e.g. "numpy" or "simplejson==3.19.*".
        2. UC Volumes files, specified as "dbfs:<path>",
            e.g. "dbfs:/Volumes/users/Alice/wheels/my_private_dep.whl" or
            "dbfs:/Volumes/users/Bob/tars/my_private_deps.tar.gz".
        UC Volumes files must be configured as readable by all account users.
        """
        self._dependencies.extend(dependencies)
        return self

    def _as_hashable(self) -> frozenset[tuple[str, Any]]:
        """Return a simple hashable representation of the environment."""
        dict_repr = {"dependencies": tuple(self.dependencies)}
        return frozenset(dict_repr.items())
