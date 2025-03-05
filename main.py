import numpy as np 

def nearest_neighbor(matriz):
    num_nodes = len(matriz)
    start_node = 0
    visited = [False] * num_nodes
    path = [start_node]
    visited[start_node] = True
    total_cost = 0
    current_node = start_node
    
    while len(path) < num_nodes:
        nearest_node = None
        min_cost = float('inf')
        
        for neighbor in range(num_nodes):
            if not visited[neighbor] and matriz[current_node][neighbor] < min_cost:
                min_cost = matriz[current_node][neighbor]
                nearest_node = neighbor
        
        if nearest_node is None:
            break  # Evita erro caso não haja vizinhos disponíveis
        
        path.append(nearest_node)
        visited[nearest_node] = True
        total_cost += min_cost
        current_node = nearest_node

    return path, total_cost

# Lendo e convertendo a matriz
with open('tsp1_253.txt', 'r') as f:
    matriz = np.array([list(map(float, linha.split())) for linha in f.readlines()])

path, total_cost = nearest_neighbor(matriz)
print(f"O melhor caminho e: {path} e o custo total e: {total_cost:.2f}")
