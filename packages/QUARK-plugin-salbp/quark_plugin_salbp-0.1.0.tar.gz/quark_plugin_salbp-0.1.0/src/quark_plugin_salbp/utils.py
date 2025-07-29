# --- PARSING HELPER FUNCTIONS ---
# Parser for Assembly Line Balancing Benchmark Datasets by Otto et al. (2013)
# URL: https://assembly-line-balancing.de/

from quark_plugin_salbp.salbp_instance import Task, TaskId


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
