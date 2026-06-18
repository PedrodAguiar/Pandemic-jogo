"""
Script auxiliar para gerar um arquivo mundo.txt de exemplo, com uma
distribuicao aleatoria (mas controlada) de estados, para fins de teste
do jogo.

Uso:
    python gerar_mundo_inicial.py
"""

import numpy as np

from mundo import TAMANHO, salvar_mundo

# Proporcoes aproximadas de cada estado no mundo inicial
PROPORCOES = {
    "+": 0.66,   # pessoas saudaveis
    "^": 0.10,   # pessoas infectadas
    "?": 0.20,   # espacos publicos livres
    "~": 0.02,   # pessoas imunes
    "H": 0.02,   # hospitais de campanha
}


def gerar_mundo_aleatorio(semente=42):
    """Gera uma matriz 15x15 com estados distribuidos conforme PROPORCOES."""
    np.random.seed(semente)

    estados = list(PROPORCOES.keys())
    pesos = list(PROPORCOES.values())

    matriz = np.random.choice(estados, size=(TAMANHO, TAMANHO), p=pesos)
    return matriz.astype("<U1")


if __name__ == "__main__":
    matriz_gerada = gerar_mundo_aleatorio()
    salvar_mundo(matriz_gerada, "mundo.txt")
    print("Arquivo 'mundo.txt' gerado com sucesso.")
