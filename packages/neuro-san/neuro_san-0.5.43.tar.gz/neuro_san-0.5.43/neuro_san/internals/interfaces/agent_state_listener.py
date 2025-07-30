
# Copyright (C) 2023-2025 Cognizant Digital Business, Evolutionary AI.
# All Rights Reserved.
# Issued under the Academic Public License.
#
# You can be released from the terms, and requirements of the Academic Public
# License by purchasing a commercial license.
# Purchase of a commercial license is mandatory for any use of the
# neuro-san SDK Software in commercial settings.
#
# END COPYRIGHT

class AgentStateListener:
    """
    Abstract interface for publishing agent state changes -
    when an agent is being added or removed from the service.
    """

    def agent_added(self, agent_name: str):
        """
        Agent is being added to the service.
        :param agent_name: name of an agent
        """
        raise NotImplementedError

    def agent_modified(self, agent_name: str):
        """
        Existing agent has been modified in service scope.
        :param agent_name: name of an agent
        """
        raise NotImplementedError

    def agent_removed(self, agent_name: str):
        """
        Agent is being removed from the service.
        :param agent_name: name of an agent
        """
        raise NotImplementedError
