"""
Modulo responsavel pelos eventos aleatorios do jogo: a "noticia do dia"
que altera o fator de letalidade do virus, e a criacao automatica de
areas de quarentena quando noticias ruins se acumulam.
"""

import numpy as np

from mundo import TAMANHO
from regras import criar_area_quarentena

LIMITE_NOTICIAS_RUINS_SEGUIDAS = 3

# Ajuste aplicado ao fator de letalidade a cada tipo de noticia
AJUSTE_LETALIDADE_NOTICIA_BOA = -0.10
AJUSTE_LETALIDADE_NOTICIA_NEUTRA = 0.0
AJUSTE_LETALIDADE_NOTICIA_RUIM = 0.15

LETALIDADE_MINIMA = 0.05
LETALIDADE_MAXIMA = 0.90

NOTICIAS_BOAS = [
    "Um novo lote de testes rapidos foi distribuido a populacao.",
    "Pesquisadores anunciam avanco promissor em tratamento.",
    "Campanha de higienizacao reduz a circulacao do virus.",
]

NOTICIAS_NEUTRAS = [
    "Autoridades pedem calma e mantem o monitoramento da situacao.",
    "Nenhuma mudanca significativa foi registrada hoje.",
    "Especialistas continuam analisando os dados da semana.",
]

NOTICIAS_RUINS = [
    "Uma nova variante mais agressiva do virus foi identificada.",
    "Hospitais relatam aumento brusco na demanda por leitos.",
    "Aglomeracoes nao autorizadas aceleram o contagio na regiao.",
]


def sortear_noticia_do_dia(estado_jogo):
    """
    Sorteia a noticia do dia (boa, neutra ou ruim), ajusta o fator de
    letalidade do virus e atualiza o contador de noticias ruins
    seguidas dentro do estado_jogo.

    Retorna o texto da noticia sorteada.
    """
    categorias = ["boa", "neutra", "ruim"]
    categoria_sorteada = np.random.choice(categorias)

    if categoria_sorteada == "boa":
        texto_noticia = np.random.choice(NOTICIAS_BOAS)
        ajuste = AJUSTE_LETALIDADE_NOTICIA_BOA
        estado_jogo["noticias_ruins_seguidas"] = 0

    elif categoria_sorteada == "neutra":
        texto_noticia = np.random.choice(NOTICIAS_NEUTRAS)
        ajuste = AJUSTE_LETALIDADE_NOTICIA_NEUTRA
        estado_jogo["noticias_ruins_seguidas"] = 0

    else:
        texto_noticia = np.random.choice(NOTICIAS_RUINS)
        ajuste = AJUSTE_LETALIDADE_NOTICIA_RUIM
        estado_jogo["noticias_ruins_seguidas"] += 1

    nova_letalidade = estado_jogo["fator_letalidade"] + ajuste
    nova_letalidade = max(LETALIDADE_MINIMA, min(LETALIDADE_MAXIMA, nova_letalidade))
    estado_jogo["fator_letalidade"] = nova_letalidade

    return f"[{categoria_sorteada.upper()}] {texto_noticia}"


def verificar_e_criar_quarentena_automatica(estado_jogo):
    """
    Verifica se o numero de noticias ruins seguidas atingiu o limite.
    Caso tenha atingido, cria uma area de quarentena automaticamente
    na celula de espaco publico livre ('?') mais proxima de algum
    infectado ('^'), e zera o contador de noticias ruins.

    Retorna uma mensagem descrevendo o evento, ou None caso nenhuma
    area tenha sido criada.
    """
    if estado_jogo["noticias_ruins_seguidas"] < LIMITE_NOTICIAS_RUINS_SEGUIDAS:
        return None

    posicao_escolhida = _encontrar_espaco_livre_mais_proximo_de_infectado(
        estado_jogo["matriz"]
    )

    if posicao_escolhida is None:
        # Nao ha espaco livre disponivel: nao e possivel criar a area
        estado_jogo["noticias_ruins_seguidas"] = 0
        return None

    linha, coluna = posicao_escolhida
    total_celulas = criar_area_quarentena(estado_jogo, linha, coluna)
    estado_jogo["noticias_ruins_seguidas"] = 0

    return (
        f"O acumulo de noticias ruins forcou a criacao automatica de uma area "
        f"de quarentena em torno de ({linha},{coluna}), isolando {total_celulas} celulas."
    )


def _encontrar_espaco_livre_mais_proximo_de_infectado(matriz):
    """
    Procura, em toda a matriz, a celula com estado '?' que esteja mais
    proxima (distancia Euclidiana) de alguma celula infectada ('^').

    Retorna a posicao (linha, coluna) escolhida, ou None caso nao
    existam celulas livres ou infectadas suficientes.
    """
    posicoes_infectadas = list(zip(*np.where(matriz == "^")))
    posicoes_livres = list(zip(*np.where(matriz == "?")))

    if not posicoes_infectadas or not posicoes_livres:
        return None

    melhor_posicao = None
    menor_distancia = None

    for linha_livre, coluna_livre in posicoes_livres:
        for linha_infectada, coluna_infectada in posicoes_infectadas:
            distancia = (
                (linha_livre - linha_infectada) ** 2
                + (coluna_livre - coluna_infectada) ** 2
            ) ** 0.5

            if menor_distancia is None or distancia < menor_distancia:
                menor_distancia = distancia
                melhor_posicao = (linha_livre, coluna_livre)

    return melhor_posicao
