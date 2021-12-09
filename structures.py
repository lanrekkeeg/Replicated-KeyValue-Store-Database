from dataclasses import dataclass

@dataclass
class Point:
    x: float
    y: float
    z: float = 0.0

P = Point(1.5,2.5)
print(P)