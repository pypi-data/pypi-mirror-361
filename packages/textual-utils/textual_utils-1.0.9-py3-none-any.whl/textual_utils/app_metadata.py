from dataclasses import dataclass


@dataclass(frozen=True)
class AppMetadata:
    name: str
    version: str
    codename: str
    author: str
    email: str
