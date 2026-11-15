class InnovationTracker:
    def __init__(self) -> None:
        self._next_innovation: int = 0
        self._next_node_id: int = 0
        self._innovation_by_node_pair: dict[tuple[int, int], int] = {}
        self._node_id_by_split_innovation: dict[int, int] = {}

    def new_node_id(self) -> int:
        node_id = self._next_node_id
        self._next_node_id += 1
        return node_id

    def create_innovation(self, in_node: int, out_node: int) -> int:
        key = (in_node, out_node)
        assert key not in self._innovation_by_node_pair, f"Error: innovation {key} already exists"

        self._innovation_by_node_pair[key] = self._next_innovation
        self._next_innovation += 1
        return self._innovation_by_node_pair[key]

    def get_innovation(self, in_node: int, out_node: int) -> int:
        key = (in_node, out_node)
        assert key in self._innovation_by_node_pair, f"Error: no innovation for {key}"
        return self._innovation_by_node_pair[key]

    def create_split_node_id(self, split_innovation: int) -> int:
        assert split_innovation not in self._node_id_by_split_innovation, f"Error: connection {split_innovation} was already split"

        self._node_id_by_split_innovation[split_innovation] = self.new_node_id()
        return self._node_id_by_split_innovation[split_innovation]

    def get_split_node_id(self, split_innovation: int) -> int:
        assert split_innovation in self._node_id_by_split_innovation, f"Error: connection {split_innovation} was never split"
        return self._node_id_by_split_innovation[split_innovation]