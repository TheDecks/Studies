from typing import Set


class Publisher:

    _name_cred: str
    _surnames: Set[str]
    _ID: int = 0

    def __init__(self, name_credential: str, surname: str, is_other: bool = False):
        self.name = name_credential
        self.surname = surname
        self.publishing_power = 0
        self.is_other = is_other
        Publisher._ID += 1
        self.id = Publisher._ID

    @property
    def name(self):
        return self._name_cred

    @name.setter
    def name(self, set_val: str):
        self._name_cred = set_val.strip().upper()[:1]

    @property
    def surname(self):
        return self._surnames

    @surname.setter
    def surname(self, set_val: str):
        self._surnames = set(map(lambda x: x.strip().capitalize(), set_val.split('-')))

    def check_person(self, person: str) -> bool:
        try:
            credential, surnames = person.split('.')
            credential = credential.strip().upper()[:1]
            surnames = set(map(lambda x: x.strip().capitalize(), surnames.split('-')))

            if credential == self.name and surnames.intersection(self.surname):
                self._surnames |= surnames
                return True
        except ValueError:
            pass
        return False

    def __eq__(self, other: 'Publisher'):
        return self.id == other.id

    def __hash__(self):
        return hash(self.id)
