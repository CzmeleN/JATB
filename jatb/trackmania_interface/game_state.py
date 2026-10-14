class GameState:
    """
        class to represetn all relevant game state informations 
    """
    
    def __init__(self):
        self.__speed: int = 0
        self.__acceleration: int = 0
        self.__obstacle_distances: list[int] = []
    
    def update_speed(self, speed: int): 
        self.__speed: int = speed
        
    def get_speed(self) -> int:
        return self.__speed

    def update_acceleration(self, acceleration: int):
        self.__acceleration: int = acceleration

    def get_acceleration(self) -> int:
        return self.__acceleration
    
    def update_obstacle_distances(self, obstacle_distances: list[int]):
        self.__obstacle_distances: list[int] = obstacle_distances

    def get_obstacle_distances(self) -> list[int]:
        return self.__obstacle_distances
        