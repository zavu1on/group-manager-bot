from dataclasses import dataclass


@dataclass
class CreateBirthdayDTO:
    name: str
    group_id: int
    date: str


@dataclass
class BirthdayDTO:
    id: int
    name: str
    group_id: int
    date: str
