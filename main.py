import hashlib
import json
import time
import os
import random
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding

# Classe Blockchain
class Blockchain:
    def __init__(self):
        self.chain = []
        self.current_transactions = []
        self.new_block(previous_hash='1', proof=100)

    def new_block(self, proof, previous_hash=None):
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time.time(),
            'transactions': self.current_transactions,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1]) if self.chain else '1',
        }
        self.current_transactions = []
        self.chain.append(block)
        return block

    def new_transaction(self, sender, recipient, amount):
        self.current_transactions.append({
            'sender': sender,
            'recipient': recipient,
            'amount': amount,
        })
        return self.last_block['index'] + 1

    @staticmethod
    def hash(block):
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    @property
    def last_block(self):
        return self.chain[-1]

# Classe Node
class Node:
    def __init__(self, id, blockchain):
        self.id = id
        self.dist = float('inf')  # Inicializa a distância como infinita
        self.predecessor = None
        self.neighbors = []  # Lista de vizinhos
        self.blockchain = blockchain  # Blockchain associada ao nó
        self.private_key = os.urandom(32)  # Gerar chave privada aleatória (32 bytes)
        self.public_key = self.private_key  # Chave pública (para simplicidade, usamos a mesma chave privada)

    def add_neighbor(self, neighbor, distance):
        self.neighbors.append((neighbor, distance))

    def send_message(self, recipient, message, total_nodes):
        """Envia uma mensagem, registra no blockchain de todos os nós e considera o tamanho da rede."""
        print(f"No {self.id} enviando mensagem para o No {recipient.id}: {message}")
        
        # Criptografar a mensagem usando a chave do destinatário
        encrypted_message = encrypt_message(recipient.public_key, message)
        
        # Registra a transação no blockchain do remetente
        self.blockchain.new_transaction(self.id, recipient.id, encrypted_message)
        
        # Registra a transação também nos outros nós
        for node in nodes:
            if node != self:  # Não registra no próprio nó
                node.blockchain.new_transaction(self.id, recipient.id, encrypted_message)
        
        # Considera o total de nós para o envio da mensagem, e simula a propagação
        print(f"Tamanho da rede: {total_nodes} nos.")
        
        # Envia a mensagem criptografada para o destinatário
        recipient.receive_message(self.id, encrypted_message)

    def receive_message(self, sender_id, encrypted_message):
        """Recebe uma mensagem criptografada e registra no blockchain."""
        print(f"No {self.id} recebeu mensagem de {sender_id}.")
        try:
            # Usa sua própria chave para descriptografar
            decrypted_message = decrypt_message(self.private_key, encrypted_message)
            print(f"Mensagem de {sender_id}: {decrypted_message}")
        except Exception as e:
            print("Erro ao remover o padding. A mensagem pode estar corrompida.")
        self.blockchain.new_transaction(sender_id, self.id, encrypted_message)

    def get_next_node(self):
        """Retorna o próximo nó para enviar a mensagem, baseado no predecessor."""
        return self.predecessor if self.predecessor else self

# Função Bellman-Ford
def bellman_ford(nodes, start_node):
    start_node.dist = 0
    
    # Realiza as atualizações das distâncias
    for _ in range(len(nodes) - 1):
        for node in nodes:
            for neighbor, distance in node.neighbors:
                if node.dist + distance < neighbor.dist:
                    neighbor.dist = node.dist + distance
                    neighbor.predecessor = node
    
    # Verifica a existência de ciclos negativos
    for node in nodes:
        for neighbor, distance in node.neighbors:
            if node.dist + distance < neighbor.dist:
                print("Ciclo negativo detectado!")
                return None

    return nodes

# Função para ler o grafo a partir de um arquivo
def read_graph_from_file(filename):
    nodes = []
    with open(filename, 'r') as file:
        lines = file.readlines()
        n = len(lines)
        
        # Cria os nós com uma nova instância de blockchain associada a cada um
        for i in range(n):
            blockchain = Blockchain()  # Cada nó agora tem sua própria instância de blockchain
            nodes.append(Node(i, blockchain))
        
        # Preenche as distâncias entre os nós
        for i in range(n):
            distances = list(map(int, lines[i].split()))
            for j in range(n):
                if i != j:
                    nodes[i].add_neighbor(nodes[j], distances[j])

    return nodes

# Função de criptografia
def encrypt_message(key, message):
    # Gerar um IV (vetor de inicialização) aleatório
    iv = os.urandom(16)
    
    # Criar um objeto de cipher com a chave e o IV
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    
    # Aplicar padding à mensagem para garantir que seu tamanho seja múltiplo do bloco de 16 bytes
    padder = padding.PKCS7(128).padder()  # PKCS7 com 128 bits (16 bytes)
    padded_data = padder.update(message.encode()) + padder.finalize()
    
    # Criptografar os dados
    encrypted_message = encryptor.update(padded_data) + encryptor.finalize()
    
    return iv + encrypted_message  # Concatenando o IV com a mensagem criptografada

# Função de descriptografia
def decrypt_message(key, encrypted_message):
    # Separar o IV (primeiros 16 bytes) da mensagem criptografada
    iv = encrypted_message[:16]
    ciphertext = encrypted_message[16:]
    
    # Criar o objeto de cipher para a descriptografia
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    
    # Descriptografar a mensagem
    decrypted_data = decryptor.update(ciphertext) + decryptor.finalize()
    
    # Remover o padding
    unpadder = padding.PKCS7(128).unpadder()  # PKCS7 com 128 bits (16 bytes)
    unpadded_data = unpadder.update(decrypted_data) + unpadder.finalize()
    
    # Converter a mensagem de volta para texto
    return unpadded_data.decode()

# Função para enviar a mensagem do ponto inicial até o ponto final
def send_message_through_path(start_node, end_node, message):
    visited = set()  # Conjunto para armazenar os nós visitados
    current_node = start_node
    while current_node != end_node:
        # Marca o nó atual como visitado
        visited.add(current_node.id)
        
        # Envia a mensagem para um nó vizinho não visitado
        next_node = None
        for neighbor, _ in current_node.neighbors:
            if neighbor.id not in visited:
                next_node = neighbor
                break
        
        if next_node is None:
            print("Noo ha mais nos nao visitados para enviar a mensagem.")
            break
        
        current_node.send_message(next_node, message, len(nodes))
        current_node = next_node

# Função de Algoritmo Genético para otimizar o roteamento
def genetic_algorithm(nodes, generations=100, population_size=50):
    def fitness(path):
        total_distance = 0
        for i in range(len(path) - 1):
            total_distance += get_distance(nodes[path[i]], nodes[path[i+1]])
        return total_distance

    def generate_random_path():
        path = list(range(len(nodes)))
        random.shuffle(path)
        return path

    def crossover(parent1, parent2):
        point = random.randint(1, len(parent1) - 1)
        child = parent1[:point] + parent2[point:]
        return child

    def mutate(path):
        i = random.randint(0, len(path) - 1)
        j = random.randint(0, len(path) - 1)
        path[i], path[j] = path[j], path[i]
        return path

    population = [generate_random_path() for _ in range(population_size)]
    for generation in range(generations):
        population.sort(key=lambda path: fitness(path))
        new_population = population[:2]  # Seleção dos melhores
        while len(new_population) < population_size:
            parent1, parent2 = random.sample(population[:10], 2)
            child = crossover(parent1, parent2)
            child = mutate(child)
            new_population.append(child)
        population = new_population
    return population[0]

# Função para obter a distância entre dois nós (exemplo simples)
def get_distance(node1, node2):
    for neighbor, distance in node1.neighbors:
        if neighbor.id == node2.id:
            return distance
    return float('inf')

# Exemplo de uso
filename = "tsp1_253.txt"
nodes = read_graph_from_file(filename)  # Lê os nós do arquivo

# Escolhe um nó inicial e um nó final
start_node = nodes[0]  # Alterar para o nó inicial desejado
end_node = nodes[9]    # Alterar para o nó final desejado

# Executa o Bellman-Ford
result = bellman_ford(nodes, start_node)

# Exibe os resultados
if result:
    for node in nodes:
        print(f"No {node.id}: Distancia = {node.dist}")

# Envia a mensagem do nó inicial até o nó final
send_message_through_path(start_node, end_node, "Ola,Mundo!")

# Exibe a blockchain de todos os nós
print("\nBlockchain dos nos:")
for node in nodes:
    print(f"\nNo {node.id} - Blockchain: {node.blockchain.chain}")
