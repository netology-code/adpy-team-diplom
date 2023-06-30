from dataclasses import dataclass


@dataclass
class ClientUser:
    user_id: int
    age: int
    gender: int
    city: str
    state: int

