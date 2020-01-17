from typing import Set


class Person:

    _ID: int = 0

    def __init__(self, identifiers: Set[str]):
        self.identifiers = identifiers
        self.id = Person._ID
        Person._ID += 1
        self.mentions = 1

    @classmethod
    def from_entry(cls, entry: str):
        return cls(set(map(str.strip, entry.split(' '))))

    def is_mentioned(self, entry: str) -> bool:
        entry_identifiers = set(map(str.strip, entry.split(' ')))
        return bool(self.identifiers.intersection(entry_identifiers))

    def update_from_entry(self, entry: str):
        self.identifiers |= set(map(str.strip, entry.split(' ')))

    def __eq__(self, other: 'Person'):
        return self.identifiers == other.identifiers

    def __hash__(self):
        return hash(self.id)

    def __repr__(self):
        return f"Person: {' '.join(self.identifiers)} ({self.id})"
