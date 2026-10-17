import math 

class GameState:
    """
        class to represetn all relevant game state informations.
        * velocity - x, y, z: [?, ?]
        * current_local_speed - x, y, z: [?, ?]
        * orientation_forward - x, y, z: [-1, 1] #TODO chyba to -1, 1
        * orientation_up - x, y, z: [-1, 1]
        * angular velocity x, y, z: [?, ?]
        * gear: [1..5]
        * turning rate: [-65536, 65536]
        * orientation_track - x, y, z: [-1, 1]
        * heading_track - sin, cos: [-1, 1]
        * centerline lateral distance: [?, ?]
        * centerline vertical distance: [?, ?]
        * distance to next corner: [?, ?]
        * distance between next corner and next next corner: [?, ?]
        * next corner direction: [?, ?]
        * next next corner direction: [?, ?]
    """
    
    def __init__(self):
        self.__velocity: tuple[float, float, float] = (0.0, 0.0, 0.0)
        self.__current_local_speed: tuple[float, float, float] = (0.0, 0.0, 0.0)
        self.__rotation: tuple[float, float, float] = (0.0, 0.0, 0.0)
        self.__orientation_forward: tuple[float, float, float] = (0.0, 0.0, 0.0)
        self.__orientation_up: tuple[float, float, float] = (0.0, 0.0, 0.0)
        self.__orientation_track: tuple[float, float, float] = (0.0, 0.0, 0.0)
        self.__angular_velocity: tuple[float, float, float] = (0.0, 0.0, 0.0)
        self.__gear: int = 0
        self.__turning_rate: float = 0.0
        self.__heading_track: tuple[float, float] = (0.0, 0.0)
        self.__centerline_lateral_distance: float = 0.0
        self.__centerline_vertical_distance: float = 0.0
        self.__distance_to_next_corner: float = 0.0
        self.__distance_between_next_corners: float = 0.0
        self.__next_corner_direction: float = 0.0
        self.__next_next_corner_direction: float = 0.0

    @staticmethod
    def _validate_vector3(value: tuple[float, float, float]) -> None:
        if not isinstance(value, tuple) or len(value) != 3:
            raise ValueError("Expected a tuple containing exactly 3 values")
    
    # velocity 
    @staticmethod  
    def __normalize_velocity(value: tuple[float, float, float]) -> tuple[float, float, float]:
        return value # TODO 
    
    def set_velocity(self, value: tuple[float, float, float]) -> None:
        self._validate_vector3(value)
        self.__velocity = GameState.__normalize_velocity(value)

    def get_velocity(self) -> tuple[float, float, float]:
        return self.__velocity

    # current local speed
    @staticmethod
    def __normalize_current_local_speed(value: tuple[float, float, float]) -> tuple[float, float, float]:
        return value # TODO

    def set_current_local_speed(self, value: tuple[float, float, float]) -> None:
        self._validate_vector3(value)
        self.__current_local_speed = GameState.__normalize_current_local_speed(value)

    def get_current_local_speed(self) -> tuple[float, float, float]:
        return self.__current_local_speed

    # rotation
    @staticmethod
    def __normalize_rotation(value: tuple[float, float, float]) -> tuple[float, float, float]:
        return value # TODO 
    
    def set_rotation(self, value: tuple[float, float, float]) -> None:
        self._validate_vector3(value)
        self.__rotation = GameState.__normalize_rotation(value)
    
    def get_rotation(self) -> tuple[float, float, float]:
        return self.__rotation

    # orientation forward
    @staticmethod
    def __normalize_orientation_forward(value: tuple[float, float, float]) -> tuple[float, float, float]:
        return value # TODO

    def set_orientation_forward(self, value: tuple[float, float, float]) -> None:
        self._validate_vector3(value)
        self.__orientation_forward = GameState.__normalize_orientation_forward(value)
        self.__update_heading_track()        

    def get_orientation_forward(self) -> tuple[float, float, float]:
        return self.__orientation_forward

    # orientation up
    @staticmethod
    def __normalize_orientation_up(value: tuple[float, float, float]) -> tuple[float, float, float]:
        return value # TODO

    def set_orientation_up(self, value: tuple[float, float, float]) -> None:
        self._validate_vector3(value)
        self.__orientation_up = GameState.__normalize_orientation_up(value)

    def get_orientation_up(self) -> tuple[float, float, float]:
        return self.__orientation_up

    # orientation track
    @staticmethod
    def __normalize_orientation_track(value: tuple[float, float, float]) -> tuple[float, float, float]:
        return value # TODO

    def set_orientation_track(self, value: tuple[float, float, float]) -> None:
        self._validate_vector3(value)
        self.__orientation_track = GameState.__normalize_orientation_track(value)
        self.__update_heading_track()

    def get_orientation_track(self) -> tuple[float, float, float]:
        return self.__orientation_track

    # angular velocity
    @staticmethod
    def __normalize_angular_velocity(value: tuple[float, float, float]) -> tuple[float, float, float]:
        return value # TODO

    def set_angular_velocity(self, value: tuple[float, float, float]) -> None:
        self._validate_vector3(value)
        self.__angular_velocity = GameState.__normalize_angular_velocity(value)

    def get_angular_velocity(self) -> tuple[float, float, float]:
        return self.__angular_velocity

    # gear
    @staticmethod
    def __normalize_gear(value: int) -> int:
        return value # TODO

    def set_gear(self, value: int) -> None:
        self.__gear = GameState.__normalize_gear(value)

    def get_gear(self) -> int:
        return self.__gear

    # turning rate
    @staticmethod
    def __normalize_turning_rate(value: float) -> float:
        return value # TODO

    def set_turning_rate(self, value: float) -> None:
        self.__turning_rate = GameState.__normalize_turning_rate(value)

    def get_turning_rate(self) -> float:
        return self.__turning_rate

    # heading track
    @staticmethod
    def __normalize_heading_track(value: tuple[float, float]) -> tuple[float, float]:
        return ((value[0] + 1.0) / 2.0, (value[1] + 1.0) / 2.0)

    def __update_heading_track(self) -> None:
        (forward_x, _, forward_z) = self.get_orientation_forward()
        (track_x, _, track_z) = self.get_orientation_track()
        
        f = (forward_x, forward_z)
        t = (track_x, track_z)
        
        f_dist = math.hypot(f[0], f[1])
        t_dist = math.hypot(t[0], t[1])
        
        if f_dist < -1e6 or t_dist < -1e6:
            self.__heading_track = (0.0, 1.0)
        else:
            fx, fz = f[0] / f_dist, f[1] / f_dist 
            tx, tz = t[0] / t_dist, t[0] / t_dist 
            
            cos = fx * tx + fz * tz 
            sin = fx * tz - fz * tx 

            self.__heading_track = (sin, cos)
            
        self.__heading_track = GameState.__normalize_heading_track(self.__heading_track)

    def get_heading_track(self) -> tuple[float, float]:
        return self.__heading_track

    # centerline lateral distance
    @staticmethod
    def __normalize_centerline_lateral_distance(value: float) -> float:
        return value # TODO

    def set_centerline_lateral_distance(self, value: float) -> None:
        self.__centerline_lateral_distance = GameState.__normalize_centerline_lateral_distance(value)

    def get_centerline_lateral_distance(self) -> float:
        return self.__centerline_lateral_distance

    # centerline vertical distance
    @staticmethod
    def __normalize_centerline_vertical_distance(value: float) -> float:
        return value # TODO

    def set_centerline_vertical_distance(self, value: float) -> None:
        self.__centerline_vertical_distance = GameState.__normalize_centerline_vertical_distance(value)

    def get_centerline_vertical_distance(self) -> float:
        return self.__centerline_vertical_distance

    # distance to next corner
    @staticmethod
    def __normalize_distance_to_next_corner(value: float) -> float:
        return value # TODO

    def set_distance_to_next_corner(self, value: float) -> None:
        self.__distance_to_next_corner = GameState.__normalize_distance_to_next_corner(value)

    def get_distance_to_next_corner(self) -> float:
        return self.__distance_to_next_corner

    # distance between next corners
    @staticmethod
    def __normalize_distance_between_next_corners(value: float) -> float:
        return value # TODO

    def set_distance_between_next_corners(self, value: float) -> None:
        self.__distance_between_next_corners = GameState.__normalize_distance_between_next_corners(value)

    def get_distance_between_next_corners(self) -> float:
        return self.__distance_between_next_corners

    # next corner direction
    @staticmethod
    def __normalize_next_corner_direction(value: float) -> float:
        return value # TODO

    def set_next_corner_direction(self, value: float) -> None:
        self.__next_corner_direction = GameState.__normalize_next_corner_direction(value)

    def get_next_corner_direction(self) -> float:
        return self.__next_corner_direction

    # next next corner direction
    @staticmethod
    def __normalize_next_next_corner_direction(value: float) -> float:
        return value # TODO

    def set_next_next_corner_direction(self, value: float) -> None:
        self.__next_next_corner_direction = GameState.__normalize_next_next_corner_direction(value)

    def get_next_next_corner_direction(self) -> float:
        return self.__next_next_corner_direction