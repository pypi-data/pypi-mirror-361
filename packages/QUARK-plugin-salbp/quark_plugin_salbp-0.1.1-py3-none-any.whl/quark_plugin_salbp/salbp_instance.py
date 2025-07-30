from __future__ import annotations

import itertools
from dataclasses import dataclass, field
from pathlib import Path
from typing import NamedTuple

import networkx as nx

# --- TYPINGS ---
TaskId = int
StationId = int


class Task(NamedTuple):
    """
    A Task for an Assembly Line Balancing Problem.

    Attributes:
        id: ID of this task
        time: Time that is needed to complete this task
    """

    id: TaskId
    time: int


TaskAssignment = dict[StationId, list[Task]]


@dataclass
class SALBPInstance:
    """
    An instance of the Simple Assembly Line Balancing Problem, version 1 (SALBP-1).

    Attributes:
        cycle_time: Time that is available for a station
        tasks: Tasks in this problem
        preceding_tasks: Known tasks' precedence relations
    """

    cycle_time: int
    tasks: frozenset[Task]
    preceding_tasks: frozenset[tuple[Task, Task]] = field(default_factory=frozenset)

    @property
    def number_of_tasks(self) -> int:
        """
        Return number of tasks.

        :return: The total number of tasks
        """
        return len(self.tasks)

    def get_task(self, task_id: TaskId) -> Task:
        """
        Get task for given task_id.

        :param task_id: The ID of the task to retrieve
        :return: The corresponding Task object
        """
        return next(task for task in self.tasks if task.id == task_id)

    @classmethod
    def create_salbp_from_file(cls, file_path: Path) -> SALBPInstance:
        """
        Read data from a file and create an SALBP-1 instance.

        :param file_path: Path to the `.alb` file
        :return: An instance of SALBP-1 created from the input file
        """
        file_content = cls.read_data(file_path)
        token_to_index = cls.get_indices(
            file_content, list(TOKEN_PARSER_DISPATCHER.keys())
        )
        content = cls.split_lines_to_areas(file_content, token_to_index)
        content_parsed = {}
        for (
            k,
            v,
        ) in content.items():
            if parser := TOKEN_PARSER_DISPATCHER.get(k):
                content_parsed[k] = [parser(vii) for vii in v]

        return cls.salbp_factory(
            tasks=content_parsed["<task times>"],
            precedence_relations=cls.convert_preceding_task_ids_to_tasks(
                content_parsed["<task times>"], content_parsed["<precedence relations>"]
            ),
            cycle_time=content_parsed["<cycle time>"][0],
        )

    @staticmethod
    def read_data(file_path: Path) -> list[str]:
        """
        Read scenario files in .alb format.

        :param file_path: Path to `.alb` file
        :return: List of lines given in data
        """
        with open(file=str(file_path), mode="r", encoding="utf-8") as alb_file:
            return list(
                filter(
                    lambda s: s != "",
                    list(map(lambda s: s.strip(), alb_file.readlines())),
                )
            )

    @staticmethod
    def get_indices(lines: list[str], keywords: list[str]) -> dict[str, int]:
        """
        Find the positions of the keywords in the list.

        :param lines: List of lines
        :param keywords: Keywords to look for
        :return: Dictionary with keyword and their position in lines
        """
        return {keyword: lines.index(keyword) for keyword in keywords}

    @staticmethod
    def split_lines_to_areas(
        lines: list[str], token_indices: dict[str, int]
    ) -> dict[str, list[str]]:
        """
        Group the list into keywords and their corresponding values.

        Each group is introduced by a keyword and ends when another keyword follows.

        :param lines: List of lines
        :param token_indices: Keywords and their position in lines
        :return: Dictionary with keyword and corresponding values
        """
        token_and_range = zip(
            token_indices.keys(), itertools.pairwise(token_indices.values())
        )
        return {t: lines[start + 1 : stop] for t, (start, stop) in token_and_range}

    @staticmethod
    def convert_preceding_task_ids_to_tasks(
        tasks: list[Task], preceding_task_ids: list[tuple[TaskId, TaskId]]
    ) -> list[tuple[Task, Task]]:
        """
        Convert a list of preceding task IDs into a list of preceding tasks.

        :param tasks: List of Task objects
        :param preceding_task_ids: List of tuples representing task precedence constraints
        :return: List of tuples representing task precedence constraints with Task objects
        """
        return [
            (
                next(task for task in tasks if task.id == i),
                next(task for task in tasks if task.id == j),
            )
            for i, j in preceding_task_ids
        ]

    # --- FACTORY FUNCTION ---
    @staticmethod
    def salbp_factory(
        tasks: list[Task],
        precedence_relations: list[tuple[Task, Task]],
        cycle_time: int,
    ) -> SALBPInstance:
        """
        Create an SALBP-1 instance given a list of tasks and their precedence relations.
        Do validity checking on the input data and raise a ValueError if the data is invalid.

        :param tasks: The tasks to be assigned to stations
        :param precedence_relations: The tasks' precedence relations
        :param cycle_time: The cycle time of a station (the same for every station)
        :return: An instance of the SALBP-1
        """
        if len(tasks) == 0:
            raise ValueError(
                "No tasks registered! Trivial instance (no stations needed)."
            )

        task_ids: list[TaskId] = [task.id for task in tasks]
        if not len(task_ids) == len(set(task_ids)):
            raise ValueError(f"Some tasks have the same taskId ({tasks})")

        if not all(x >= 0 for x in [task.time for task in tasks]):
            raise ValueError(f"Some tasks have a negative task time ({tasks})")

        if not all(task.time <= cycle_time for task in tasks):
            raise ValueError(f"Cycle time ({cycle_time}) is too short for some tasks!.")

        task_set = frozenset(tasks)
        if not all(
            t1 in task_set and t2 in task_set for (t1, t2) in precedence_relations
        ):
            raise ValueError(
                f"Preceding tasks ({precedence_relations}) do not match registered tasks ({tasks})."
            )

        precedence_graph = nx.DiGraph(precedence_relations)
        if not nx.is_directed_acyclic_graph(precedence_graph):
            raise ValueError("Precedence graph contains cycles!")

        return SALBPInstance(
            cycle_time=cycle_time,
            tasks=task_set,
            preceding_tasks=frozenset(precedence_relations),
        )


# --- PARSING HELPER FUNCTIONS ---
# Parser for Assembly Line Balancing Benchmark Datasets by Otto et al. (2013)
# URL: https://assembly-line-balancing.de/


def parse_number_of_tasks(number_task: str) -> int:
    """
    Parse the number n of tasks in this problem.

    :param number_task: The number of tasks as a string
    :return: The number of tasks as an integer
    """
    return int(number_task)


def parse_cycle_time(cycle_time: str) -> int:
    """
    Parse the available cycle time for one station.

    :param cycle_time: The cycle time as a string
    :return: The cycle time as an integer
    """
    return int(cycle_time)


def parse_order_strength(order_strength: str) -> float:
    """
    Parse the order strength of the precedence graph.

    :param order_strength: The order strength as a string
    :return: The order strength as a float
    """
    return float(order_strength.replace(",", "."))


def parse_task(task_times: str) -> Task:
    """
    Parse a task and its time requirement.

    :param task_times: A string containing the task ID and time
    :return: A Task instance
    """
    task_id, task_time = task_times.split(" ")
    return Task(int(task_id), int(task_time))


def parse_precedence_relation(relation: str) -> tuple[TaskId, ...]:
    """
    The precedence relations define constraints on the order in which
    tasks are performed. A priority relation of task i to task j means
    that task i must be completed before task j can be started.
    (Task i, Task j).

    :param relation: A string containing task IDs that define precedence constraints
    :return: A tuple of task IDs representing precedence constraints
    """
    return tuple(int(task) for task in relation.split(","))


TOKEN_PARSER_DISPATCHER = {
    "<number of tasks>": parse_number_of_tasks,
    "<cycle time>": parse_cycle_time,
    "<order strength>": parse_order_strength,
    "<task times>": parse_task,
    "<precedence relations>": parse_precedence_relation,
    "<end>": None,
}
