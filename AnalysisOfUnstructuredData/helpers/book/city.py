from typing import Tuple


class CityEntry:

    def __init__(self, name: str, latitude: float, longitude: float, population: int):
        self.name = name
        self.latitude = latitude
        self.longitude = longitude
        self.population = population

    @property
    def position(self) -> Tuple[float, float]:
        return self.latitude, self.longitude

    @position.setter
    def position(self, set_val: Tuple[float, float]):
        self.latitude, self.longitude = set_val

    @property
    def html_popup(self):
        return f"""
        <center>
            <h4>
                {self.name}
            </h4>
            <br>
            <i>
                {self.latitude:.2f}, {self.longitude:.2f}
            </i>
            <br>
            {self.population}
        </center>"""

    def __repr__(self):
        return f'<{self.name}: {self.latitude}, {self.longitude}>'
