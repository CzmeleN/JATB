from .genome import Genome

def edge_creates_cycle(genome: Genome, edge: tuple[int, int]) -> bool:
    in_node, out_node = edge
    G_inverted: dict[int, list[int]] = {}
    for c in genome.connection_by_innovation_id.values():
        G_inverted.setdefault(c.in_node, []).append(c.out_node)
        
    stack, seen = [out_node], {out_node}
    while stack:
        node = stack.pop() 
        if node == in_node:
            return True 
        
        for child in G_inverted.get(node, []):
            if child not in seen:
                seen.add(child)
                stack.append(child)
                
    return False