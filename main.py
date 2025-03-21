import numpy as np
import random
import hashlib
import json
from time import time
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes

class Block:
    def __init__(self, index, timestamp, data, previous_hash, nonce=0):
        self.index = index                # Posição do bloco na cadeia
        self.timestamp = timestamp        # Momento de criação do bloco
        self.data = data                  # Dados (ex.: informações do nó e custo)
        self.previous_hash = previous_hash  # Hash do bloco anterior
        self.nonce = nonce                # Número para prova de trabalho (Proof-of-Work)
        self.hash = self.compute_hash()   # Hash atual do bloco

    def compute_hash(self):
        """
        Calcula o hash do bloco convertendo seus atributos para string JSON,
        garantindo que tipos não serializáveis (como numpy.int32) sejam convertidos.
        """
        block_string = json.dumps(self.__dict__, sort_keys=True,
                                  default=lambda o: int(o) if isinstance(o, (np.int32, np.int64)) else o)
        return hashlib.sha256(block_string.encode()).hexdigest()


class Blockchain:
    def __init__(self, difficulty=2):
        self.chain = []
        self.difficulty = difficulty
        self.create_genesis_block()

    def create_genesis_block(self):
        """
        Cria o bloco gênesis (primeiro bloco da cadeia).
        """
        genesis_block = Block(0, time(), "Bloco Gênesis", "0")
        self.chain.append(genesis_block)

    def get_last_block(self):
        return self.chain[-1]

    def proof_of_work(self, block):
        """
        Executa o algoritmo de prova de trabalho.
        """
        block.nonce = 0
        computed_hash = block.compute_hash()
        while not computed_hash.startswith('0' * self.difficulty):
            block.nonce += 1
            computed_hash = block.compute_hash()
        return computed_hash

    def add_block(self, block):
        """
        Adiciona um novo bloco à cadeia depois de executar a prova de trabalho.
        """
        block.previous_hash = self.get_last_block().hash
        block.hash = self.proof_of_work(block)
        self.chain.append(block)

def fill_pings(path):
    """
    Preenche a matriz path com valores aleatórios e simétricos com a diagonal zerada.
    """
    n = 10  # Tamanho da matriz
    path = np.random.randint(1, 101, size=(n, n))  # Números entre 1 e 100
    for i in range(n):
        for j in range(i + 1, n):
            path[j, i] = path[i, j]  # Torna a matriz simétrica
    np.fill_diagonal(path, 0)
    return path, n

def find_shortest_way(path, message, blockchain):
    """
    Encontra o menor caminho (de 0 até n-1) atualizando os pings com variação de 30%.
    Propaga a mensagem criptografada de nó em nó.
    Em cada passo, registra um bloco no blockchain com os dados do nó e custo.
    Retorna o custo total, o caminho percorrido e a mensagem que chegou ao destino.
    """
    current_node = 0
    visited_nodes = [False] * len(path)
    crypted_message = [None] * len(path)
    visited_nodes[current_node] = True
    way = [current_node]
    total_cost = 0
    crypted_message[current_node] = message  # Armazena a mensagem no nó inicial

    # Registra o bloco do nó inicial
    data = {"nó": current_node, "custo": 0, "ação": "início", "mensagem": "criptografada"}
    blockchain.add_block(Block(index=len(blockchain.chain), timestamp=time(), data=data, previous_hash=""))

    for _ in range(len(path) - 1):
        lower = float('inf')
        next_row = -1
        for index, cost in enumerate(path[current_node]):
            if not visited_nodes[index] and cost < lower:
                lower = cost
                next_row = index
        total_cost += lower

        # Propaga a mensagem para o próximo nó
        crypted_message[next_row] = crypted_message[current_node]
        crypted_message[current_node] = None  # Limpa o nó anterior

        # Registra um bloco com as informações do nó atual
        data = {"nó": next_row, "custo": int(lower), "ação": "avançou", "mensagem": "criptografada"}
        blockchain.add_block(Block(index=len(blockchain.chain), timestamp=time(), data=data, previous_hash=""))

        current_node = next_row
        visited_nodes[current_node] = True
        way.append(current_node)

        if current_node == len(path) - 1:
            # Registra o bloco final
            data = {"nó": current_node, "custo": 0, "ação": "destino", "mensagem": "criptografada"}
            blockchain.add_block(Block(index=len(blockchain.chain), timestamp=time(), data=data, previous_hash=""))
            return total_cost, way, crypted_message[current_node]

        # Atualiza os pings com variação de ±30%
        for index, cost in enumerate(path[current_node]):
            variation = random.uniform(-0.3, 0.3)
            cost = cost * (1 + variation)
            path[current_node][index] = cost

    return total_cost, way, crypted_message[current_node]

def generate_keys():
    """
    Gera o par de chaves RSA.
    """
    private_key = rsa.generate_private_key(
        public_exponent=65537,  # Valor padrão para RSA
        key_size=2048           # Tamanho da chave
    )
    public_key = private_key.public_key()  # Extrai a chave pública
    return public_key, private_key

def encrypt_message(message, public_key):
    """
    Criptografa a mensagem usando a chave pública.
    """
    message_encoded = message.encode()  # Converte a string para bytes
    crypted_message = public_key.encrypt(
        message_encoded,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return crypted_message

def decrypt_message(crypted_message, private_key):
    """
    Descriptografa a mensagem usando a chave privada.
    """
    decrypted_message = private_key.decrypt(
        crypted_message,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return decrypted_message


if __name__ == '__main__':
    message_input = input("Digite a mensagem: ")
    # Gera as chaves
    public_key, private_key = generate_keys()
    # Criptografa a mensagem com a chave pública
    encrypted_message = encrypt_message(message_input, public_key)
    # Preenche a matriz de pings
    path, n = fill_pings([])
    # Cria o blockchain para registrar cada etapa do roteamento
    blockchain = Blockchain(difficulty=2)
    # Encontra a rota e propaga a mensagem criptografada,
    # registrando cada etapa no blockchain
    final_cost, final_way, final_encrypted_message = find_shortest_way(path, encrypted_message, blockchain)

    # Exibe o conteúdo do blockchain (cada bloco)
    print("\n--- Blockchain ---")
    for block in blockchain.chain:
        print(f"Índice: {block.index}")
        print(f"Timestamp: {block.timestamp}")
        print(f"Dados: {block.data}")
        print(f"Hash Anterior: {block.previous_hash}")
        print(f"Nonce: {block.nonce}")
        print(f"Hash: {block.hash}\n")

    print(f"O custo final foi de: {final_cost} e este foi o caminho percorrido: {final_way}")
    
    # No destino, descriptografa a mensagem usando a chave privada
    if final_way[-1] == n - 1 and final_encrypted_message is not None:
        decrypted_message = decrypt_message(final_encrypted_message, private_key)
        print("Mensagem descriptografada:", decrypted_message.decode())
    else:
        print("Erro: A mensagem não chegou ao destino corretamente!")