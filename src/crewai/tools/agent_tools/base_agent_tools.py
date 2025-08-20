from typing import Optional, Union

from pydantic import Field

from crewai.agents.agent_builder.base_agent import BaseAgent
from crewai.task import Task
from crewai.tools.base_tool import BaseTool
from crewai.utilities import I18N


class BaseAgentTool(BaseTool):
    """Base class for agent-related tools"""

    agents: list[BaseAgent] = Field(description="List of available agents")
    i18n: I18N = Field(
        default_factory=I18N, description="Internationalization settings"
    )

    def _get_coworker(self, coworker: Optional[str], **kwargs) -> Optional[str]:
        coworker = coworker or kwargs.get("co_worker") or kwargs.get("coworker")
        if coworker:
            is_list = coworker.startswith("[") and coworker.endswith("]")
            if is_list:
                coworker = coworker[1:-1].split(",")[0]
        return coworker

    def _execute(
        self, agent_name: Union[str, None], task: str, context: Union[str, None]
    ) -> str:
        try:
            if agent_name is None:
                agent_name = ""

            # Normalize agent name for matching (handle malformed JSON and whitespace)
            normalized_agent_name = agent_name.casefold().replace('"', "").replace("\n", "")
            
            # Find first matching agent by role
            matching_agents = [
                agent for agent in self.agents 
                if agent.role.casefold().replace("\n", "") == normalized_agent_name
            ]
        except Exception as _:
            return self.i18n.errors("agent_tool_unexisting_coworker").format(
                coworkers="\n".join(
                    [f"- {agent.role.casefold()}" for agent in self.agents]
                )
            )

        if not matching_agents:
            return self.i18n.errors("agent_tool_unexisting_coworker").format(
                coworkers="\n".join(
                    [f"- {agent.role.casefold()}" for agent in self.agents]
                )
            )

        agent = matching_agents[0]
        task_with_assigned_agent = Task(  # type: ignore # Incompatible types in assignment (expression has type "Task", variable has type "str")
            description=task,
            agent=agent,
            expected_output=agent.i18n.slice("manager_request"),
            i18n=agent.i18n,
        )
        return agent.execute_task(task_with_assigned_agent, context)
