graph = {
    'A': ['B', 'C'],
    'B': ['D', 'E'],
    'C': ['F'],
    'D': [],
    'E': ['F'],
    'F': []
}


def dfs(graph, node, destination, visited=None, path=None):
    if visited is None:
        visited = set()
    if path is None:
        path = []
        
    visited.add(node)
    path.append(node)
    
    if node == destination:
        return path
    
    for neighbor in graph[node]:
        if neighbor not in visited:
            result_path = dfs(graph, neighbor, destination, visited, path)
if result_path:  
                return result_path
    

root = 'A'
destination = 'F'

path = dfs(graph, root, destination)

if path:
    print(f"Path found: {' -> '.join(path)}")
else:
    print("No path found.")