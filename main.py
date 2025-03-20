import numpy as np
import random
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes
import hashlib
import json
from time import time


class Block:
    def __init__(self , index , timestamp , data , previous_hash , nonce=0):
        self.index=index # Posição do bloco na cadeia
        self.timestamp=timestamp  # Momento de criação do bloco
        self.data=data # Dados
        self.previoushash=previous_hash # Hash do bloco anterior
        self.nonce=nonce # Número para prova de trabalho (Proof-of-Work)
        self.hash=self.compute_hash() # Hash atual do bloco

    def compute_hash(self):
        """
        Calcula o hash do bloco convertendo seus atributos para uma string JSON e aplicando SHA-256
        """
        block_string = json.dumps(self.__dict__ , sort_keys=True)
        return hashlib.sha256(block_string.encode()).hexdigest()

class Blockchain:
    def __init__(self , dificulty=2):
        self.chain=[]
        self.dificulty=dificulty
        self.create_genesis_block()
    
    def create_genesis_block(self):
         """
        Cria o bloco gênesis (primeiro bloco da cadeia).
        """
         genesis_block = Block(0 , time() , "Bloco Gênesis" , "0" )
         self.chain.append(genesis_block)

    def get_last_block(self):
        return self.chain[-1]
    
    def proof_of_work(self , block):
        """
        Executa o algoritmo de prova de trabalho.
        """
        block.nonce = 0
        computed_hash = block.compute_hash()
        while not computed_hash.startswith('0'*self.dificulty):
            block.nonce += 1
            computed_hash = block.compute_hash()
        return computed_hash
    
    def add_block(self , block):
        """
        Adiciona um novo bloco à cadeia depois de executar a prova de trabalho.
        """
        block.previous_hash = self.get_last_block().hash
        block.hash = self.proof_of_work(block)
        self.chain.append(block)




def fill_pings(path):
    """
        Preenche a matriz 'path' com valores aleatórios e simétricos com a diagonal zerada
    """
    n=10    # Tamanho da matriz
    path = np.random.randint(1,101, size=(n,n))  # Números entre esse intervalo
    for i in range(n):
        for j in range(i+1, n):
            path[j, i] = path[i, j]  # Torna a matriz simétrica
    np.fill_diagonal(path,0)
    return path , n

def find_shortest_way(path , message):
    """
        Encontra o menor caminho. Atualizando os pings com uma variação de 30% a cada vez que avança um passo
    """
    current_node = 0
    visited_nodes = [False]*len(path)
    crypted_message = [None]*len(path)
    visited_nodes[current_node] = True
    way = [current_node]
    total_cost = 0
    crypted_message[current_node]=message
    for _ in range(len(path)-1):
        lower = float('inf')
        next_row = -1
        for index,cost in enumerate(path[current_node]):
            if not visited_nodes[index] and cost < lower:
                lower = cost
                next_row=index
        total_cost+=lower
        crypted_message[next_row]=crypted_message[current_node]
        crypted_message[current_node]=None
        current_node=next_row
        visited_nodes[current_node] = True
        way.append(current_node)
        if current_node == len(path)-1:
            return total_cost, way
        for index,cost in enumerate(path[current_node]):
            variation = random.uniform(-0.3,0.3)
            cost= cost * (1+variation)
            path[current_node][index]=cost
    return total_cost, way

def generate_keys():
    #Gera a chave privada
    private_key = rsa.generate_private_key(
        public_exponent=65537, #Valor padrão para RSA
        key_size=2048 #Tamanho da chave
    )
    public_key = private_key.public_key() #Extrai a chave pública
    return public_key, private_key

def encrypt_message(message, public_key):
    message_encoded = message.encode() #Converte string para bytes
    crypted_message = public_key.encrypt(
        message_encoded,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return(crypted_message)

def decrypt_message(crypted_message, private_key):
    #Usa a chave privada para descriptografar
    decrypted_message = private_key.decrypt( 
    crypted_message,
    padding.OAEP(
        mgf=padding.MGF1(algorithm=hashes.SHA256()),
        algorithm=hashes.SHA256(),
        label=None
    )
)
    return decrypted_message




path = []
message = input("Digite a mensagem: ")
public_key , private_key = generate_keys()
message = encrypt_message(message , public_key)
path, n = fill_pings(path)
final_cost, final_way = find_shortest_way(path , message)
print(f"O custo final foi de: {final_cost} e este foi o caminho percorrido: {final_way}")
if final_way[-1] == n-1:
    message = decrypt_message(message, private_key)
    print(message.decode())
else:
    print("Error")

















