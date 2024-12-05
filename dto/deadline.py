from dataclasses import dataclass


@dataclass
class CreateDeadlineDTO:
    task_name: str
    group_id: int
    date: str


@dataclass
class DeadlineDTO:
    id: int
    task_name: str
    group_id: int
    date: str
