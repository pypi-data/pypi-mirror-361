"""A module for the task capabilities of the Fabricatio library."""

from abc import ABC
from typing import Mapping, Optional, Unpack

from fabricatio_core import Task
from fabricatio_core.capabilities.propose import Propose
from fabricatio_core.capabilities.usages import UseLLM
from fabricatio_core.journal import logger
from fabricatio_core.models.generic import WithBriefing
from fabricatio_core.models.kwargs_types import ChooseKwargs, ValidateKwargs
from fabricatio_core.rust import TEMPLATE_MANAGER

from fabricatio_capabilities.config import capabilities_config


class ProposeTask(Propose, ABC):
    """A class that proposes a task based on a prompt."""

    async def propose_task[T](
        self,
        prompt: str,
        **kwargs: Unpack[ValidateKwargs[Task[T]]],
    ) -> Optional[Task[T]]:
        """Asynchronously proposes a task based on a given prompt and parameters.

        Parameters:
            prompt: The prompt text for proposing a task, which is a string that must be provided.
            **kwargs: The keyword arguments for the LLM (Large Language Model) usage.

        Returns:
            A Task object based on the proposal result.
        """
        if not prompt:
            logger.error(err := "Prompt must be provided.")
            raise ValueError(err)

        return await self.propose(Task, prompt, **kwargs)


class DispatchTask(UseLLM, ABC):
    """A class that dispatches a task based on a task object."""

    async def dispatch_task[T, R: WithBriefing](
        self,
        task: Task[T],
        candidates: Mapping[str, R],
        **kwargs: Unpack[ChooseKwargs[R]],
    ) -> Optional[T]:
        """Asynchronously dispatches a task to an appropriate delegate based on candidate selection.

        This method uses a template to render instructions for selecting the most suitable candidate,
        then delegates the task to that selected candidate by resolving its namespace.

        Parameters:
            task: The task object to be dispatched. It must support delegation.
            candidates: A mapping of identifiers to WithBriefing instances representing available delegates.
                        Each key is a unique identifier and the corresponding value contains briefing details.
            **kwargs: Keyword arguments unpacked from ChooseKwargs, typically used for LLM configuration.

        Returns:
            The result of the delegated task execution, which is of generic type T.

        Raises:
            ValueError: If no valid target is picked or if delegation fails.
            KeyError: If the selected target does not exist in the reverse mapping.
        """
        inst = TEMPLATE_MANAGER.render_template(
            capabilities_config.dispatch_task_template,
            {"task": task.briefing, "candidates": [wb.name for wb in candidates.values()]},
        )

        rev_mapping = {wb.name: ns for (ns, wb) in candidates.items()}

        target = await self.apick(inst, list(candidates.values()), **kwargs)

        target_namespace = rev_mapping[target.name]
        return await task.delegate(target_namespace)
