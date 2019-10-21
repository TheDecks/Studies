from typing import Dict


class Singleton(type):
    """
    Singleton type implementation. Assures that no more than one instance of object is created.
    """

    _instances: Dict[type, 'Singleton'] = {}

    def __call__(cls, *args, **kwargs):

        if cls not in Singleton._instances:
            Singleton._instances[cls] = super().__call__(*args, **kwargs)

        return Singleton._instances[cls]
