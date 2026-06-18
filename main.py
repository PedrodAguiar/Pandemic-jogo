"""
Arquivo principal do jogo "Pandemia: Contagio e Quarentena".

Fluxo de cada rodada:
    1. Exibe o estado atual da matriz.
    2. Sorteia e exibe a noticia do dia, ajustando a letalidade do virus.
    3. Verifica se o acumulo de noticias ruins gera uma quarentena automatica.
    4. Exibe o menu e aguarda a acao do jogador.
    5. Calcula a evolucao simultanea de todas as celulas.
    6. Verifica condicoes de vitoria ou derrota antecipada.
    7. Avanca o contador de rodadas.

Ao final (por limite de rodadas ou por vitoria/derrota), salva o
estado final em mundo_final.txt.
"""

import numpy as np

from mundo import ler_mundo, salvar_mundo, exibir_mundo, TAMANHO
from regras import calcular_proxima_geracao
from eventos import sortear_noticia_do_dia, verificar_e_criar_quarentena_automatica
from menu import processar_acao_jogador, CREDITOS_INICIAIS

CAMINHO_MUNDO_INICIAL = "mundo.txt"
CAMINHO_MUNDO_FINAL = "mundo_final.txt"

NUMERO_MINIMO_DE_RODADAS = 10
FATOR_LETALIDADE_INICIAL = 0.20


def criar_estado_inicial(matriz):
    """
    Monta o dicionario de estado do jogo a partir da matriz lida do
    arquivo, inicializando os contadores auxiliares.
    """
    matriz_inicial = matriz.copy()
    matriz_inicial[matriz_inicial == "#"] = "?"

    return {
        "matriz": matriz_inicial,
        "dias_infectado": np.zeros((TAMANHO, TAMANHO), dtype=int),
        "turnos_quarentena": np.zeros((TAMANHO, TAMANHO), dtype=int),
        "estado_anterior_quarentena": np.full((TAMANHO, TAMANHO), "?", dtype="<U1"),
        "fator_letalidade": FATOR_LETALIDADE_INICIAL,
        "noticias_ruins_seguidas": 0,
    }


def verificar_fim_de_jogo(matriz):
    """
    Verifica se alguma condicao de vitoria ou derrota antecipada foi
    atingida.

    Retorna uma tupla (jogo_terminou, mensagem) onde jogo_terminou e um
    booleano e mensagem descreve o resultado (ou None se o jogo deve
    continuar).
    """
    total_infectados = np.sum(matriz == "^")
    total_saudaveis = np.sum(matriz == "+")

    if total_infectados == 0:
        return True, "VITORIA! Nao ha mais nenhuma pessoa infectada no mundo."

    if total_saudaveis == 0:
        return True, "DERROTA! Nao restou nenhuma pessoa saudavel no mundo."

    return False, None


def executar_jogo():
    print("=" * 60)
    print("  PANDEMIA: CONTAGIO E QUARENTENA")
    print("=" * 60)

    matriz_inicial = ler_mundo(CAMINHO_MUNDO_INICIAL)
    estado_jogo = criar_estado_inicial(matriz_inicial)
    creditos = CREDITOS_INICIAIS

    rodada_atual = 1
    mensagem_final = None

    while True:
        exibir_mundo(estado_jogo["matriz"], turno=rodada_atual, creditos=creditos)

        texto_noticia = sortear_noticia_do_dia(estado_jogo)
        print(f"Noticia do dia: {texto_noticia}")
        print(f"Fator de letalidade atual do virus: {estado_jogo['fator_letalidade']:.2f}")

        mensagem_quarentena_automatica = verificar_e_criar_quarentena_automatica(estado_jogo)
        if mensagem_quarentena_automatica:
            print(mensagem_quarentena_automatica)

        creditos = processar_acao_jogador(estado_jogo, creditos)

        estado_jogo, eventos_da_rodada = calcular_proxima_geracao(estado_jogo)

        if eventos_da_rodada:
            print("\nEventos desta rodada:")
            for evento in eventos_da_rodada:
                print(f"  - {evento}")

        condicao_atingida, mensagem_condicao = verificar_fim_de_jogo(estado_jogo["matriz"])

        # So permite o fim antecipado do jogo apos o minimo de rodadas
        if condicao_atingida and rodada_atual < NUMERO_MINIMO_DE_RODADAS:
            print(f"\n(Condicao de fim de jogo atingida, mas o minimo de "
                  f"{NUMERO_MINIMO_DE_RODADAS} rodadas ainda nao foi alcancado. "
                  f"O jogo continua.)")
            condicao_atingida = False

        rodada_atual += 1

        if condicao_atingida:
            mensagem_final = mensagem_condicao
            break

        if rodada_atual > NUMERO_MINIMO_DE_RODADAS:
            break

    print("\n" + "=" * 60)
    if mensagem_final:
        print(mensagem_final)
    else:
        print(f"Fim de jogo: limite de {NUMERO_MINIMO_DE_RODADAS} rodadas atingido.")
    print("=" * 60)

    exibir_mundo(estado_jogo["matriz"], turno=rodada_atual)
    salvar_mundo(estado_jogo["matriz"], CAMINHO_MUNDO_FINAL)
    print(f"Estado final salvo em '{CAMINHO_MUNDO_FINAL}'.")


if __name__ == "__main__":
    executar_jogo()
