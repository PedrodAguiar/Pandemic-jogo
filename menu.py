"""
Modulo responsavel pelo menu de acoes do jogador. A cada rodada, o
jogador pode gastar creditos para intervir no mundo: criar uma area de
quarentena, vacinar uma pessoa, fazer uma campanha de
conscientizacao, ou simplesmente passar o turno.
"""

from mundo import TAMANHO
from regras import criar_area_quarentena

CREDITOS_INICIAIS = 500

CUSTO_QUARENTENA = 100
CUSTO_VACINA = 80
CUSTO_CAMPANHA = 150
CUSTO_PASSAR_TURNO = 0

REDUCAO_NOTICIAS_RUINS_CAMPANHA = 2


def exibir_menu(creditos):
    """Exibe as opcoes de acao disponiveis para o jogador."""
    print("Escolha sua acao:")
    print(f"  1. Criar Area de Quarentena (Custo: {CUSTO_QUARENTENA})")
    print(f"  2. Vacinar Pessoa (Custo: {CUSTO_VACINA})")
    print(f"  3. Campanha de Conscientizacao (Custo: {CUSTO_CAMPANHA})")
    print(f"  4. Passar Turno sem fazer nada (Custo: {CUSTO_PASSAR_TURNO})")
    print(f"Creditos disponiveis: {creditos}")


def solicitar_posicao(mensagem):
    """
    Solicita ao usuario uma posicao (linha, coluna) dentro dos limites
    da matriz, validando a entrada.
    """
    while True:
        entrada = input(f"{mensagem} (formato: linha,coluna): ").strip()

        partes = entrada.split(",")
        if len(partes) != 2:
            print("Formato invalido. Use o formato linha,coluna, por exemplo: 3,7")
            continue

        try:
            linha = int(partes[0].strip())
            coluna = int(partes[1].strip())
        except ValueError:
            print("Linha e coluna devem ser numeros inteiros.")
            continue

        if not (0 <= linha < TAMANHO and 0 <= coluna < TAMANHO):
            print(f"Posicao fora dos limites. Use valores entre 0 e {TAMANHO - 1}.")
            continue

        return linha, coluna


def processar_acao_jogador(estado_jogo, creditos):
    """
    Exibe o menu, le a escolha do jogador e aplica a acao escolhida
    sobre o estado do jogo, descontando os creditos correspondentes.

    Retorna o saldo de creditos atualizado.
    """
    while True:
        exibir_menu(creditos)
        escolha = input("Digite o numero da acao desejada: ").strip()

        if escolha == "1":
            creditos_atualizados, acao_realizada = _criar_area_quarentena(
                estado_jogo, creditos
            )
        elif escolha == "2":
            creditos_atualizados, acao_realizada = _vacinar_pessoa(
                estado_jogo, creditos
            )
        elif escolha == "3":
            creditos_atualizados, acao_realizada = _aplicar_campanha(
                estado_jogo, creditos
            )
        elif escolha == "4":
            print("Voce optou por passar o turno.")
            return creditos
        else:
            print("Opcao invalida. Escolha uma acao valida.")
            continue

        if acao_realizada:
            return creditos_atualizados

        print("A acao nao foi realizada. Escolha outra acao ou passe o turno.")


def _criar_area_quarentena(estado_jogo, creditos):
    if creditos < CUSTO_QUARENTENA:
        print("Creditos insuficientes para criar uma area de quarentena.")
        return creditos, False

    linha, coluna = solicitar_posicao("Centro da area de quarentena?")
    total_celulas = criar_area_quarentena(estado_jogo, linha, coluna)
    print(
        f"Area de quarentena criada em torno de ({linha},{coluna}), "
        f"isolando {total_celulas} celulas."
    )

    return creditos - CUSTO_QUARENTENA, True


def _vacinar_pessoa(estado_jogo, creditos):
    if creditos < CUSTO_VACINA:
        print("Creditos insuficientes para vacinar uma pessoa.")
        return creditos, False

    linha, coluna = solicitar_posicao("Quem vacinar?")
    matriz = estado_jogo["matriz"]

    if matriz[linha, coluna] != "+":
        print("Só e possivel vacinar uma pessoa saudavel.")
        return creditos, False

    matriz[linha, coluna] = "~"
    print(f"Pessoa em ({linha},{coluna}) foi vacinada e agora esta imune.")

    return creditos - CUSTO_VACINA, True


def _aplicar_campanha(estado_jogo, creditos):
    if creditos < CUSTO_CAMPANHA:
        print("Creditos insuficientes para realizar a campanha de conscientizacao.")
        return creditos, False

    estado_jogo["noticias_ruins_seguidas"] = max(
        0, estado_jogo["noticias_ruins_seguidas"] - REDUCAO_NOTICIAS_RUINS_CAMPANHA
    )
    print("Campanha de conscientizacao realizada. O impacto das noticias ruins foi reduzido.")

    return creditos - CUSTO_CAMPANHA, True
