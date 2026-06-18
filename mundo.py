"""
Modulo responsavel por ler e escrever o estado do mundo em arquivo de texto.

O mundo e representado como uma matriz numpy de strings (dtype '<U1'),
15x15, onde cada posicao contem um caractere representando o estado
daquela celula.

Estados possiveis:
    '+' -> Pessoa saudavel
    '^' -> Pessoa infectada
    '#' -> Area de quarentena
    '?' -> Espaco publico livre
    '~' -> Pessoa imune / vacinada
    'H' -> Hospital de campanha
"""

import numpy as np

TAMANHO = 15
ESTADOS_VALIDOS = {"+", "^", "#", "?", "~", "H"}


def ler_mundo(caminho):
    """
    Le o arquivo de texto contendo a matriz 15x15 e retorna uma matriz
    numpy de caracteres.

    Cada linha do arquivo deve conter 15 caracteres separados por espaco.
    """
    linhas_lidas = []

    with open(caminho, "r", encoding="utf-8") as arquivo:
        for numero_linha, linha in enumerate(arquivo, start=1):
            linha = linha.strip()
            if not linha:
                continue

            celulas = linha.split(" ")

            if len(celulas) != TAMANHO:
                raise ValueError(
                    f"Linha {numero_linha} do arquivo possui {len(celulas)} "
                    f"celulas, mas eram esperadas {TAMANHO}."
                )

            for celula in celulas:
                if celula not in ESTADOS_VALIDOS:
                    raise ValueError(
                        f"Estado invalido '{celula}' encontrado na linha "
                        f"{numero_linha} do arquivo."
                    )

            linhas_lidas.append(celulas)

    if len(linhas_lidas) != TAMANHO:
        raise ValueError(
            f"O arquivo possui {len(linhas_lidas)} linhas, mas eram "
            f"esperadas {TAMANHO}."
        )

    return np.array(linhas_lidas, dtype="<U1")


def salvar_mundo(matriz, caminho):
    """
    Salva a matriz do mundo em um arquivo de texto, no mesmo formato
    de entrada (15 linhas, 15 caracteres por linha, separados por espaco).
    """
    with open(caminho, "w", encoding="utf-8") as arquivo:
        for linha in matriz:
            arquivo.write(" ".join(linha))
            arquivo.write("\n")


def exibir_mundo(matriz, turno=None, creditos=None):
    """
    Imprime o estado atual da matriz no terminal, de forma legivel,
    com cabecalho opcional mostrando turno e creditos disponiveis.
    """
    print()
    if turno is not None:
        cabecalho = f"[ TURNO {turno} ]"
        if creditos is not None:
            cabecalho += f" - Creditos Disponiveis: {creditos}"
        print(cabecalho)

    # Cabecalho de colunas
    indices_colunas = "   " + " ".join(f"{i:2}" for i in range(TAMANHO))
    print(indices_colunas)

    for indice_linha, linha in enumerate(matriz):
        celulas_formatadas = " ".join(f"{celula:2}" for celula in linha)
        print(f"{indice_linha:2} {celulas_formatadas}")

    print()
    print("Legenda: + Saudavel | ^ Infectado | # Quarentena | ? Espaco livre | ~ Imune | H Hospital")
    print()


def criar_mundo_vazio():
    """Cria uma matriz 15x15 inteiramente preenchida com espaco publico livre."""
    return np.full((TAMANHO, TAMANHO), "?", dtype="<U1")
