import numpy as np
import random
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes


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
    return path    

def find_shortest_way(path):
    """
        Encontra o menor caminho. Atualizando os pings com uma variação de 30% a cada vez que avança um passo
    """
    current_node = 0
    visited_nodes = [False]*len(path)
    visited_nodes[current_node] = True
    way = [current_node]
    total_cost = 0
    for _ in range(len(path)-1):
        lower = float('inf')
        next_row = -1
        for index,cost in enumerate(path[current_node]):
            if not visited_nodes[index] and cost < lower:
                lower = cost
                next_row=index
        total_cost+=lower
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



# path = []
# path = fill_pings(path)
# print(path)
# final_cost, final_way = find_shortest_way(path)
# print(f"O custo final foi de: {final_cost} e este foi o caminho percorrido: {final_way}")



















