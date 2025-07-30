from pathlib import Path
from typing import override

from quark.core import Core, Data, Failed, Result
from quark.interface_types import Other

from quark_plugin_salbp.salbp_instance import SALBPInstance, Task, TaskAssignment


class SalbpInstanceProvider(Core):
    instance: str = "data/example_instance_n=5.alb"

    @override
    def preprocess(self, data: None) -> Data:
        try:
            salbp = SALBPInstance.create_salbp_from_file(
                file_path=Path(__file__).parent / self.instance
            )
            self.salbp = salbp
        except ValueError as err:
            raise err

        return Data(Other[SALBPInstance](self.salbp))

    @override
    def postprocess(self, data: Other) -> Result:
        solution = data.data
        if solution is None:
            return Failed("No solution found")

        self.task_assignment = solution

        if not (
            not self.has_overloaded_station(self.salbp.cycle_time, self.task_assignment)
            and self.has_unique_assignment_for_every_task(
                self.salbp.tasks, self.task_assignment
            )
            and self.respects_precedences(
                self.salbp.preceding_tasks, self.task_assignment
            )
        ):
            return Failed("Solution invalid")

        if solution is None:
            return Failed("No solution found")
        obj_value = len([s for s in self.task_assignment.values() if len(s) > 0])

        return Data(Other(obj_value))

    # --- VALIDITY CHECKS FOR TASK ASSIGNMENT ---
    @staticmethod
    def has_overloaded_station(
        cycle_time: int, task_assignment: TaskAssignment
    ) -> bool:
        """
        Return if a station in the given task_assignment is overloaded wrt the given cycle time.

        :param cycle_time: The maximum time a station can take
        :param task_assignment: The assignment of tasks to stations
        :return: True if at least one station is overloaded, False otherwise
        """
        return any(
            sum(task.time for task in tasks) > cycle_time
            for tasks in task_assignment.values()
        )

    @staticmethod
    def has_unique_assignment_for_every_task(
        tasks: frozenset[Task], task_assignment: TaskAssignment
    ) -> bool:
        """
        Return if each task is assigned to exactly one station.

        :param tasks: Set of all tasks in the SALBP-1 instance
        :param task_assignment: The assignment of tasks to stations
        :return: True if all tasks are uniquely assigned, False otherwise
        """
        tasks_in_solution = [
            task for tasks in task_assignment.values() for task in tasks
        ]
        number_of_tasks_correct = len(tasks_in_solution) == len(tasks)
        only_unique_tasks = len(set(tasks_in_solution)) == len(tasks_in_solution)
        return number_of_tasks_correct and only_unique_tasks

    @staticmethod
    def respects_precedences(
        preceding_tasks: frozenset[tuple[Task, Task]], task_assignment: TaskAssignment
    ) -> bool:
        """
        Return if the given task_assignment respects the given precedences.

        :param preceding_tasks: Set of precedence constraints between tasks
        :param task_assignment: The assignment of tasks to stations
        :return: True if all precedence constraints are satisfied, False otherwise
        """
        task_to_station_assignment = {
            task: station_id
            for station_id, tasks in task_assignment.items()
            for task in tasks
        }
        for task_1, task_2 in preceding_tasks:
            if task_to_station_assignment[task_1] > task_to_station_assignment[task_2]:
                return False
        return True
