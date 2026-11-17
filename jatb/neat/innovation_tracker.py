class InnovationTracker:
    def __init__(self) -> None:
        self._next_innovation_id: int = 0
        self._next_node_id: int = 0
        self._innovation_by_node_pair: dict[tuple[int, int], int] = {}
        self._node_id_by_split_innovation: dict[int, int] = {}

    def new_node_id(self) -> int:
        node_id = self._next_node_id
        self._next_node_id += 1
        return node_id

# innovation methods
    def create_innovation(self, in_node: int, out_node: int) -> int:
        key = (in_node, out_node)
        assert key not in self._innovation_by_node_pair, f"Error: innovation {key} already exists"

        self._innovation_by_node_pair[key] = self._next_innovation_id
        self._next_innovation_id += 1
        return self._innovation_by_node_pair[key]

    def get_innovation(self, in_node: int, out_node: int) -> int:
        key = (in_node, out_node)
        assert key in self._innovation_by_node_pair, f"Error: no innovation for {key}"
        return self._innovation_by_node_pair[key]
    
    def get_or_create_innovation(self, in_node: int, out_node: int) -> int: 
        key = (in_node, out_node)
        if key in self._innovation_by_node_pair:
            return self.get_innovation(*key)
        else:
            return self.create_innovation(*key) 
        
# split methods
    def create_split_node_id(self, split_innovation: int) -> int:
        assert split_innovation not in self._node_id_by_split_innovation, f"Error: connection {split_innovation} was already split"

        self._node_id_by_split_innovation[split_innovation] = self.new_node_id()
        return self._node_id_by_split_innovation[split_innovation]

    def get_split_node_id(self, split_innovation: int) -> int:
        assert split_innovation in self._node_id_by_split_innovation, f"Error: connection {split_innovation} was never split"
        return self._node_id_by_split_innovation[split_innovation]
    
    def get_or_create_split_node_id(self, split_innovation: int) -> int:
        if split_innovation in self._node_id_by_split_innovation:
            return self.get_split_node_id(split_innovation)
        else:
            return self.create_split_node_id(split_innovation)

# saving / loading methods 
    def to_dict(self) -> dict:
        return {
            "next_innovation_id": self._next_innovation_id,
            "next_node_id": self._next_node_id,
            "innovations": [
                [in_node, out_node, innovation]
                for (in_node, out_node), innovation in self._innovation_by_node_pair.items()
            ],
            "split_node_ids": [
                [split_innovation, node_id]
                for split_innovation, node_id in self._node_id_by_split_innovation.items()
            ],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "InnovationTracker":
        tracker = cls()
        tracker._next_innovation_id = data["next_innovation_id"]
        tracker._next_node_id = data["next_node_id"]
        tracker._innovation_by_node_pair = {
            (in_node, out_node): innovation for in_node, out_node, innovation in data["innovations"]
        }
        tracker._node_id_by_split_innovation = {
            split_innovation: node_id for split_innovation, node_id in data["split_node_ids"]
        }
        return tracker
