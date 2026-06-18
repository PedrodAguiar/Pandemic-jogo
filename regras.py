"""
Modulo responsavel pelas regras de evolucao do mundo: contagem de
vizinhos (respeitando os limites da matriz) e calculo da proxima
geracao de forma simultanea.
"""

import numpy as np

from mundo import TAMANHO

# Deslocamentos para as 8 posicoes vizinhas (linha, coluna)
DESLOCAMENTOS_VIZINHANCA = [
    (-1, -1), (-1, 0), (-1, 1),
    (0, -1),           (0, 1),
    (1, -1),  (1, 0),  (1, 1),
]

# Limite minimo de vizinhos infectados para que uma pessoa saudavel
# seja contaminada
LIMITE_VIZINHOS_PARA_INFECCAO = 2

# Quantidade de turnos que uma pessoa permanece infectada antes do
# teste de cura/morte
DIAS_PARA_TESTE_SOBREVIVENCIA = 5

# Quantidade de turnos que uma area de quarentena permanece ativa
DURACAO_AREA_QUARENTENA = 3

SIMBOLO_QUARENTENA = "#"
SIMBOLO_HOSPITAL = "H"

RAIO_ATENDIMENTO_HOSPITAL = 2
CAPACIDADE_ATENDIMENTO_HOSPITAL = 3
LIMITE_SOBRECARGA_HOSPITAL = 7


def posicoes_vizinhas(linha, coluna):
    """
    Retorna a lista de posicoes (linha, coluna) vizinhas validas
    (dentro dos limites 0 a 14) para a celula informada.

    Posicoes fora da matriz nao sao retornadas, ja que sao consideradas
    permanentemente vazias e nao contam como vizinhos ativos.
    """
    vizinhos = []

    for deslocamento_linha, deslocamento_coluna in DESLOCAMENTOS_VIZINHANCA:
        nova_linha = linha + deslocamento_linha
        nova_coluna = coluna + deslocamento_coluna

        dentro_dos_limites = (
            0 <= nova_linha < TAMANHO and 0 <= nova_coluna < TAMANHO
        )

        if dentro_dos_limites:
            vizinhos.append((nova_linha, nova_coluna))

    return vizinhos


def posicoes_area_quarentena(linha, coluna):
    """Retorna a celula central e as posicoes vizinhas validas da area 3x3."""
    return [(linha, coluna)] + posicoes_vizinhas(linha, coluna)


def posicoes_em_raio(linha, coluna, raio):
    """Retorna posicoes validas em um raio quadrado ao redor da celula."""
    posicoes = []

    for deslocamento_linha in range(-raio, raio + 1):
        for deslocamento_coluna in range(-raio, raio + 1):
            if deslocamento_linha == 0 and deslocamento_coluna == 0:
                continue

            nova_linha = linha + deslocamento_linha
            nova_coluna = coluna + deslocamento_coluna

            if 0 <= nova_linha < TAMANHO and 0 <= nova_coluna < TAMANHO:
                posicoes.append((nova_linha, nova_coluna))

    return posicoes


def garantir_estado_quarentena(estado_jogo):
    """
    Garante que o estado possui as matrizes auxiliares da quarentena.

    Estados antigos que ainda possuem '#' mas nao possuem historico sao
    tratados como pessoas saudaveis em quarentena, evitando que a area
    vire espaco vazio por falta de informacao.
    """
    matriz = estado_jogo["matriz"]

    if (
        "turnos_quarentena" not in estado_jogo
        or getattr(estado_jogo["turnos_quarentena"], "shape", None) != matriz.shape
    ):
        estado_jogo["turnos_quarentena"] = np.zeros((TAMANHO, TAMANHO), dtype=int)

    if (
        "estado_anterior_quarentena" not in estado_jogo
        or getattr(estado_jogo["estado_anterior_quarentena"], "shape", None)
        != matriz.shape
    ):
        estado_anterior = np.full((TAMANHO, TAMANHO), "?", dtype="<U1")
        estado_anterior[matriz == SIMBOLO_QUARENTENA] = "+"
        estado_jogo["estado_anterior_quarentena"] = estado_anterior


def criar_area_quarentena(estado_jogo, linha, coluna):
    """
    Cria ou renova uma area de quarentena na celula escolhida e em seus
    vizinhos. O estado anterior de cada celula e guardado para restauracao.
    """
    garantir_estado_quarentena(estado_jogo)

    matriz = estado_jogo["matriz"]
    turnos_quarentena = estado_jogo["turnos_quarentena"]
    estado_anterior = estado_jogo["estado_anterior_quarentena"]
    dias_infectado = estado_jogo["dias_infectado"]

    posicoes_afetadas = posicoes_area_quarentena(linha, coluna)

    for area_linha, area_coluna in posicoes_afetadas:
        if matriz[area_linha, area_coluna] != SIMBOLO_QUARENTENA:
            estado_anterior[area_linha, area_coluna] = matriz[area_linha, area_coluna]

        matriz[area_linha, area_coluna] = SIMBOLO_QUARENTENA
        turnos_quarentena[area_linha, area_coluna] = 0
        dias_infectado[area_linha, area_coluna] = 0

    return len(posicoes_afetadas)


def contar_vizinhos_por_estado(matriz, linha, coluna, estado):
    """
    Conta quantos vizinhos de uma celula possuem um determinado estado,
    respeitando os limites da matriz.
    """
    contador = 0

    for vizinho_linha, vizinho_coluna in posicoes_vizinhas(linha, coluna):
        if matriz[vizinho_linha, vizinho_coluna] == estado:
            contador += 1

    return contador


def celula_protegida_por_quarentena(matriz, linha, coluna):
    """
    Verifica se uma celula saudavel esta protegida por uma area de
    quarentena adjacente (pelo menos um vizinho '#').
    """
    return contar_vizinhos_por_estado(matriz, linha, coluna, SIMBOLO_QUARENTENA) > 0


def celula_protegida_por_hospital(matriz, linha, coluna):
    """Verifica se a celula esta dentro da cobertura de um hospital."""
    for vizinho_linha, vizinho_coluna in posicoes_em_raio(
        linha, coluna, RAIO_ATENDIMENTO_HOSPITAL
    ):
        if matriz[vizinho_linha, vizinho_coluna] == SIMBOLO_HOSPITAL:
            return True

    return False


def calcular_proxima_geracao(estado_jogo):
    """
    Calcula o proximo estado do mundo de forma simultanea: toda a
    avaliacao das regras e feita com base no estado atual (antes de
    qualquer alteracao), e o resultado e escrito em uma nova matriz.

    Recebe e retorna um dicionario "estado_jogo" contendo:
        - "matriz": matriz numpy 15x15 com os estados das celulas
        - "dias_infectado": matriz numpy de inteiros com a contagem de
          dias que cada celula infectada permanece infectada
        - "turnos_quarentena": matriz numpy de inteiros com a contagem de
          turnos que cada area de quarentena permanece ativa
        - "fator_letalidade": float representando o quao perigoso o
          virus esta no momento (afetado pelas noticias do dia)

    Retorna um novo dicionario "estado_jogo" com os valores atualizados
    para a proxima geracao, alem de uma lista de eventos textuais
    ocorridos na rodada (para exibir ao jogador).
    """
    matriz_atual = estado_jogo["matriz"]
    garantir_estado_quarentena(estado_jogo)
    dias_infectado_atual = estado_jogo["dias_infectado"]
    turnos_quarentena_atual = estado_jogo["turnos_quarentena"]
    estado_anterior_quarentena_atual = estado_jogo["estado_anterior_quarentena"]
    fator_letalidade = estado_jogo["fator_letalidade"]

    nova_matriz = matriz_atual.copy()
    novos_dias_infectado = dias_infectado_atual.copy()
    novos_turnos_quarentena = turnos_quarentena_atual.copy()
    novos_estados_anteriores_quarentena = estado_anterior_quarentena_atual.copy()

    eventos_ocorridos = []

    for linha in range(TAMANHO):
        for coluna in range(TAMANHO):
            estado_celula = matriz_atual[linha, coluna]

            if estado_celula == "+":
                _processar_pessoa_saudavel(
                    matriz_atual, linha, coluna,
                    nova_matriz, novos_dias_infectado,
                    eventos_ocorridos,
                )

            elif estado_celula == "^":
                if nova_matriz[linha, coluna] != "^":
                    continue

                _processar_pessoa_infectada(
                    linha, coluna,
                    dias_infectado_atual, novos_dias_infectado,
                    nova_matriz, fator_letalidade,
                    eventos_ocorridos,
                )

            elif estado_celula == SIMBOLO_QUARENTENA:
                _processar_area_quarentena(
                    linha, coluna,
                    turnos_quarentena_atual, novos_turnos_quarentena,
                    estado_anterior_quarentena_atual,
                    novos_estados_anteriores_quarentena,
                    matriz_atual, nova_matriz, novos_dias_infectado,
                    eventos_ocorridos,
                )

            elif estado_celula == SIMBOLO_HOSPITAL:
                _processar_hospital(
                    matriz_atual, linha, coluna,
                    nova_matriz, novos_dias_infectado,
                    dias_infectado_atual, eventos_ocorridos,
                )

            # '?' e '~' nao possuem regra de transicao propria:
            # permanecem como estao (ja copiados em nova_matriz)

    novos_turnos_quarentena[nova_matriz != SIMBOLO_QUARENTENA] = 0

    novo_estado_jogo = {
        "matriz": nova_matriz,
        "dias_infectado": novos_dias_infectado,
        "turnos_quarentena": novos_turnos_quarentena,
        "estado_anterior_quarentena": novos_estados_anteriores_quarentena,
        "fator_letalidade": fator_letalidade,
        "noticias_ruins_seguidas": estado_jogo["noticias_ruins_seguidas"],
    }

    return novo_estado_jogo, eventos_ocorridos


def _processar_pessoa_saudavel(
    matriz_atual, linha, coluna,
    nova_matriz, novos_dias_infectado,
    eventos_ocorridos,
):
    """Aplica as regras de contagio para uma celula saudavel ('+')."""
    vizinhos_infectados = contar_vizinhos_por_estado(
        matriz_atual, linha, coluna, "^"
    )
    protegida_por_quarentena = celula_protegida_por_quarentena(
        matriz_atual, linha, coluna
    )
    protegida_por_hospital = celula_protegida_por_hospital(
        matriz_atual, linha, coluna
    )
    protegida = protegida_por_quarentena or protegida_por_hospital

    if vizinhos_infectados >= LIMITE_VIZINHOS_PARA_INFECCAO and not protegida:
        nova_matriz[linha, coluna] = "^"
        novos_dias_infectado[linha, coluna] = 1
    elif (
        vizinhos_infectados >= LIMITE_VIZINHOS_PARA_INFECCAO
        and protegida_por_hospital
    ):
        eventos_ocorridos.append(
            f"Hospital proximo impediu a infeccao da pessoa em ({linha},{coluna})."
        )
    elif vizinhos_infectados >= LIMITE_VIZINHOS_PARA_INFECCAO and protegida:
        # A quarentena impediu a infeccao desta celula: nao marca falha,
        # a celula permanece saudavel
        pass


def _processar_pessoa_infectada(
    linha, coluna,
    dias_infectado_atual, novos_dias_infectado,
    nova_matriz, fator_letalidade,
    eventos_ocorridos,
):
    """
    Avanca a contagem de dias de uma pessoa infectada e, ao atingir o
    limite de dias, realiza o teste de sobrevivencia (cura ou morte).
    """
    dias_atual = int(dias_infectado_atual[linha, coluna])
    dias_atual += 1

    if dias_atual >= DIAS_PARA_TESTE_SOBREVIVENCIA:
        sobreviveu = _testar_sobrevivencia(fator_letalidade)

        if sobreviveu:
            nova_matriz[linha, coluna] = "~"
            eventos_ocorridos.append(
                f"Pessoa em ({linha},{coluna}) se recuperou e ficou imune."
            )
        else:
            nova_matriz[linha, coluna] = "?"
            eventos_ocorridos.append(
                f"Pessoa em ({linha},{coluna}) nao resistiu a doenca."
            )

        novos_dias_infectado[linha, coluna] = 0
    else:
        novos_dias_infectado[linha, coluna] = dias_atual


def _processar_hospital(
    matriz_atual, linha, coluna,
    nova_matriz, novos_dias_infectado,
    dias_infectado_atual, eventos_ocorridos,
):
    """
    Hospital de campanha trata infectados em sua area de cobertura. Se
    houver infectados demais em volta, ele fica sobrecarregado e deixa
    de funcionar.
    """
    infectados_vizinhos = [
        (vizinho_linha, vizinho_coluna)
        for vizinho_linha, vizinho_coluna in posicoes_em_raio(
            linha, coluna, RAIO_ATENDIMENTO_HOSPITAL
        )
        if matriz_atual[vizinho_linha, vizinho_coluna] == "^"
    ]

    if len(infectados_vizinhos) >= LIMITE_SOBRECARGA_HOSPITAL:
        nova_matriz[linha, coluna] = "?"
        eventos_ocorridos.append(
            f"Hospital em ({linha},{coluna}) ficou sobrecarregado e foi desativado."
        )
        return

    infectados_vizinhos.sort(
        key=lambda posicao: int(dias_infectado_atual[posicao[0], posicao[1]]),
        reverse=True,
    )

    for paciente_linha, paciente_coluna in infectados_vizinhos[:CAPACIDADE_ATENDIMENTO_HOSPITAL]:
        if nova_matriz[paciente_linha, paciente_coluna] == "+":
            continue

        nova_matriz[paciente_linha, paciente_coluna] = "+"
        novos_dias_infectado[paciente_linha, paciente_coluna] = 0
        eventos_ocorridos.append(
            f"Hospital em ({linha},{coluna}) tratou a pessoa infectada em ({paciente_linha},{paciente_coluna})."
        )


def _testar_sobrevivencia(fator_letalidade):
    """
    Sorteia se uma pessoa infectada sobrevive (vira imune) ou morre,
    com base no fator de letalidade acumulado durante a infeccao.

    fator_letalidade e um valor entre 0.0 (virus fraco) e 1.0
    (virus extremamente letal).
    """
    chance_de_morte = fator_letalidade
    resultado_sorteio = np.random.random()

    sobreviveu = resultado_sorteio >= chance_de_morte
    return sobreviveu


def _processar_area_quarentena(
    linha, coluna,
    turnos_quarentena_atual, novos_turnos_quarentena,
    estado_anterior_quarentena_atual, novos_estados_anteriores_quarentena,
    matriz_atual, nova_matriz, novos_dias_infectado,
    eventos_ocorridos,
):
    """
    Avanca a contagem de turnos de uma area de quarentena. Ao completar
    seu ciclo, humanos voltam saudaveis e espacos vazios voltam vazios.
    """
    turnos_atual = int(turnos_quarentena_atual[linha, coluna]) + 1

    if turnos_atual >= DURACAO_AREA_QUARENTENA:
        estado_original = estado_anterior_quarentena_atual[linha, coluna]
        retorno_celula = _restaurar_estado_pos_quarentena(estado_original)
        nova_matriz[linha, coluna] = retorno_celula
        novos_dias_infectado[linha, coluna] = 0
        novos_turnos_quarentena[linha, coluna] = 0
        novos_estados_anteriores_quarentena[linha, coluna] = "?"

        if retorno_celula == "+":
            eventos_ocorridos.append(
                f"Pessoa em ({linha},{coluna}) saiu da quarentena saudavel."
            )
    else:
        novos_turnos_quarentena[linha, coluna] = turnos_atual


def _restaurar_estado_pos_quarentena(estado_original):
    if estado_original in ("+", "^", "~"):
        return "+"
    if estado_original == SIMBOLO_HOSPITAL:
        return SIMBOLO_HOSPITAL
    return "?"
