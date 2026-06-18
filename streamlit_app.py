from pathlib import Path
import html
import importlib

import numpy as np
import streamlit as st

import eventos as eventos_mod
import menu as menu_mod
import mundo as mundo_mod
import regras as regras_mod

eventos_mod = importlib.reload(eventos_mod)
menu_mod = importlib.reload(menu_mod)
mundo_mod = importlib.reload(mundo_mod)
regras_mod = importlib.reload(regras_mod)

from main import (
    NUMERO_MINIMO_DE_RODADAS,
    criar_estado_inicial,
    verificar_fim_de_jogo,
)
from mundo import TAMANHO, ler_mundo, salvar_mundo

CREDITOS_INICIAIS = menu_mod.CREDITOS_INICIAIS
CREDITOS_POR_RODADA = menu_mod.CREDITOS_POR_RODADA
CUSTO_QUARENTENA = menu_mod.CUSTO_QUARENTENA
CUSTO_CAMPANHA = menu_mod.CUSTO_CAMPANHA
CUSTO_HOSPITAL = menu_mod.CUSTO_HOSPITAL
CUSTO_PASSAR_TURNO = menu_mod.CUSTO_PASSAR_TURNO
CUSTO_VACINA = menu_mod.CUSTO_VACINA
REDUCAO_NOTICIAS_RUINS_CAMPANHA = menu_mod.REDUCAO_NOTICIAS_RUINS_CAMPANHA

calcular_proxima_geracao = regras_mod.calcular_proxima_geracao
criar_area_quarentena = regras_mod.criar_area_quarentena
criar_hospital = regras_mod.criar_hospital
garantir_estado_quarentena = regras_mod.garantir_estado_quarentena

mundo_mod.ESTADOS_VALIDOS.add("H")
sortear_noticia_do_dia = eventos_mod.sortear_noticia_do_dia
verificar_e_criar_quarentena_automatica = (
    eventos_mod.verificar_e_criar_quarentena_automatica
)


BASE_DIR = Path(__file__).resolve().parent
CAMINHO_MUNDO_INICIAL = BASE_DIR / "mundo.txt"
CAMINHO_MUNDO_FINAL = BASE_DIR / "mundo_final.txt"

SIMBOLOS = {
    "+": {
        "classe": "saudavel",
        "rotulo": "Saudavel",
        "descricao": "+ Saudavel",
    },
    "^": {
        "classe": "infectado",
        "rotulo": "Infectado",
        "descricao": "^ Infectado",
    },
    "#": {
        "classe": "quarentena",
        "rotulo": "Quarentena",
        "descricao": "# Quarentena",
    },
    "?": {
        "classe": "livre",
        "rotulo": "Espaco livre",
        "descricao": "? Espaco livre",
    },
    "~": {
        "classe": "imune",
        "rotulo": "Imune",
        "descricao": "~ Imune",
    },
    "H": {
        "classe": "hospital",
        "rotulo": "Hospital",
        "descricao": "H Hospital raio 2, cura 1",
    },
}

ACOES = {
    "Criar Area de Quarentena": "quarentena",
    "Vacinar Pessoa": "vacina",
    "Criar Hospital de Campanha": "hospital",
    "Campanha de Conscientizacao": "campanha",
    "Passar Turno sem fazer nada": "passar",
}

VERSAO_ESTADO_STREAMLIT = 4


st.set_page_config(page_title="Pandemic", page_icon="P", layout="wide")


def aplicar_estilos():
    st.markdown(
        """
        <style>
            [data-testid="stMainBlockContainer"] {
                max-width: 1180px;
                padding: 46px 24px 28px;
            }

            .stApp {
                background:
                    linear-gradient(180deg, rgba(180, 35, 24, 0.08), transparent 260px),
                    #f3f6f2;
            }

            .titulo-principal {
                color: #1b2b24;
                font-size: 38px;
                font-weight: 800;
                letter-spacing: 0;
                margin: 14px 0 4px;
                text-align: center;
                text-transform: uppercase;
            }

            .subtitulo {
                color: #52635a;
                font-size: 16px;
                margin-bottom: 22px;
                text-align: center;
            }

            .painel-info {
                background: #fbfcfa;
                border: 1px solid #cfd8cf;
                border-radius: 8px;
                box-shadow: 0 8px 24px rgba(25, 43, 36, 0.06);
                color: #26352f;
                padding: 12px 14px;
                margin-bottom: 10px;
            }

            .painel-info strong {
                color: #1d2d26;
            }

            .painel-lateral {
                background: #fbfcfa;
                border: 1px solid #cfd8cf;
                border-radius: 8px;
                box-shadow: 0 8px 24px rgba(25, 43, 36, 0.06);
                padding: 12px 14px 8px;
            }

            .painel-lateral h3 {
                color: #1b2b24;
                font-size: 18px;
                letter-spacing: 0;
                margin: 0 0 8px;
            }

            .painel-alertas {
                background: #fff8e6;
                border: 1px solid #e6c46a;
                border-left: 5px solid #b7791f;
                border-radius: 8px;
                color: #4f3510;
                margin: 8px 0 14px;
                min-height: 72px;
                padding: 10px 14px;
            }

            .painel-alertas strong {
                color: #2f2110;
            }

            .painel-tabuleiro {
                background: #fbfcfa;
                border: 1px solid #cfd8cf;
                border-radius: 8px;
                box-shadow: 0 8px 24px rgba(25, 43, 36, 0.06);
                padding: 12px;
            }

            .resumo-grid {
                display: grid;
                gap: 7px;
                grid-template-columns: repeat(2, minmax(0, 1fr));
                margin-bottom: 10px;
            }

            .indicador {
                background: #fbfcfa;
                border: 1px solid #cfd8cf;
                border-radius: 8px;
                color: #26352f;
                padding: 8px 10px;
            }

            .indicador span {
                color: #5d6d64;
                display: block;
                font-size: 12px;
            }

            .indicador strong {
                color: #1b2b24;
                display: block;
                font-size: 20px;
                line-height: 1.1;
            }

            .board-scroll {
                display: flex;
                justify-content: center;
                overflow: hidden;
                padding: 2px 0 10px;
                width: 100%;
            }

            .world-grid {
                --cell-size: clamp(20px, min(3.1vw, 4.9vh), 34px);
                --grid-gap: clamp(2px, 0.35vw, 4px);
                display: grid;
                gap: var(--grid-gap);
                grid-template-columns: var(--cell-size) repeat(15, var(--cell-size));
                max-width: 100%;
            }

            .axis,
            .cell {
                align-items: center;
                border-radius: 5px;
                display: flex;
                font-family: Consolas, "Courier New", monospace;
                font-size: clamp(12px, min(1.7vw, 2.3vh), 17px);
                font-weight: 700;
                height: var(--cell-size);
                justify-content: center;
                width: var(--cell-size);
            }

            .axis {
                color: #66786e;
                font-size: clamp(10px, min(1.2vw, 1.8vh), 13px);
                font-weight: 600;
            }

            .cell {
                border: 1px solid rgba(29, 45, 38, 0.16);
            }

            .saudavel {
                background: #d8f0dc;
                color: #166534;
            }

            .infectado {
                background: #ffdad6;
                color: #b42318;
                box-shadow: inset 0 0 0 1px rgba(180, 35, 24, 0.16);
            }

            .quarentena {
                background: #d7e8e2;
                color: #0f5b4b;
            }

            .livre {
                background: #edf1ed;
                color: #53625a;
            }

            .imune {
                background: #e6ddff;
                color: #5b35a8;
            }

            .hospital {
                background: #ffe8bd;
                color: #9a4b00;
            }

            .legenda {
                display: flex;
                flex-wrap: wrap;
                gap: 6px;
                margin: 4px 0 0;
            }

            .legenda-item {
                align-items: center;
                background: #f7faf7;
                border: 1px solid #d6ded6;
                border-radius: 7px;
                color: #34443d;
                display: inline-flex;
                font-size: 13px;
                gap: 6px;
                padding: 6px 8px;
            }

            .amostra {
                align-items: center;
                border-radius: 5px;
                display: inline-flex;
                font-family: Consolas, "Courier New", monospace;
                font-weight: 700;
                height: 22px;
                justify-content: center;
                width: 22px;
            }

            div[data-testid="stRadio"] label,
            div[data-testid="stNumberInput"] label {
                color: #24362e;
                font-size: 14px;
            }

            div[data-testid="stRadio"] p,
            div[data-testid="stMarkdownContainer"] p {
                color: #2d3d35;
            }

            .stButton > button {
                border-radius: 7px;
                min-height: 40px;
            }

            @media (max-width: 640px) {
                [data-testid="stMainBlockContainer"] {
                    padding: 42px 12px 22px;
                }

                .titulo-principal {
                    font-size: 30px;
                }

                .world-grid {
                    --cell-size: clamp(17px, 5vw, 28px);
                    --grid-gap: 2px;
                }

                .painel-alertas {
                    min-height: 82px;
                }
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def rerun():
    if hasattr(st, "rerun"):
        st.rerun()
    else:
        st.experimental_rerun()


def inicializar_sessao():
    if st.session_state.get("versao_estado") != VERSAO_ESTADO_STREAMLIT:
        st.session_state.clear()
        st.session_state.versao_estado = VERSAO_ESTADO_STREAMLIT

    valores_padrao = {
        "tela": "inicio",
        "estado_jogo": None,
        "creditos": CREDITOS_INICIAIS,
        "rodada": 1,
        "turno_info": None,
        "mensagens_acao": [],
        "eventos_rodada": [],
        "mensagem_continuacao": None,
        "mensagem_final": None,
        "jogo_finalizado": False,
    }

    for chave, valor in valores_padrao.items():
        if chave not in st.session_state:
            st.session_state[chave] = valor


def limpar_jogo():
    st.session_state.estado_jogo = None
    st.session_state.creditos = CREDITOS_INICIAIS
    st.session_state.rodada = 1
    st.session_state.turno_info = None
    st.session_state.mensagens_acao = []
    st.session_state.eventos_rodada = []
    st.session_state.mensagem_continuacao = None
    st.session_state.mensagem_final = None
    st.session_state.jogo_finalizado = False


def iniciar_jogo():
    matriz_inicial = ler_mundo(CAMINHO_MUNDO_INICIAL)
    st.session_state.estado_jogo = criar_estado_inicial(matriz_inicial)
    st.session_state.creditos = CREDITOS_INICIAIS
    st.session_state.rodada = 1
    st.session_state.turno_info = None
    st.session_state.mensagens_acao = []
    st.session_state.eventos_rodada = []
    st.session_state.mensagem_continuacao = None
    st.session_state.mensagem_final = None
    st.session_state.jogo_finalizado = False
    st.session_state.tela = "jogo"


def preparar_turno():
    if st.session_state.jogo_finalizado or st.session_state.turno_info is not None:
        return

    estado_jogo = st.session_state.estado_jogo
    garantir_estado_quarentena(estado_jogo)
    texto_noticia = sortear_noticia_do_dia(estado_jogo)
    mensagem_quarentena = verificar_e_criar_quarentena_automatica(estado_jogo)

    st.session_state.turno_info = {
        "noticia": texto_noticia,
        "mensagem_quarentena": mensagem_quarentena,
        "fator_letalidade": estado_jogo["fator_letalidade"],
    }


def montar_grade_mundo(matriz):
    partes = ['<div class="board-scroll"><div class="world-grid">']
    partes.append("<div></div>")

    for coluna in range(TAMANHO):
        partes.append(f'<div class="axis">{coluna}</div>')

    for indice_linha, linha in enumerate(matriz):
        partes.append(f'<div class="axis">{indice_linha}</div>')

        for celula in linha:
            simbolo = str(celula)
            info = SIMBOLOS[simbolo]
            partes.append(
                '<div class="cell {classe}" title="{titulo}">{simbolo}</div>'.format(
                    classe=info["classe"],
                    titulo=html.escape(info["rotulo"]),
                    simbolo=html.escape(simbolo),
                )
            )

    partes.append("</div></div>")
    return "".join(partes)


def montar_legenda():
    partes = ['<div class="legenda">']

    for simbolo, info in SIMBOLOS.items():
        partes.append(
            (
                '<span class="legenda-item">'
                '<span class="amostra {classe}">{simbolo}</span>'
                "{descricao}"
                "</span>"
            ).format(
                classe=info["classe"],
                simbolo=html.escape(simbolo),
                descricao=html.escape(info["descricao"]),
            )
        )

    partes.append("</div>")
    return "".join(partes)


def montar_resumo_mundo():
    matriz = st.session_state.estado_jogo["matriz"]
    itens = [
        ("Saudaveis", int(np.sum(matriz == "+"))),
        ("Infectados", int(np.sum(matriz == "^"))),
        ("Quarentena", int(np.sum(matriz == "#"))),
        ("Livres", int(np.sum(matriz == "?"))),
        ("Imunes", int(np.sum(matriz == "~"))),
        ("Hospitais", int(np.sum(matriz == "H"))),
    ]
    conteudo = "".join(
        (
            '<div class="indicador">'
            "<span>{rotulo}</span>"
            "<strong>{valor}</strong>"
            "</div>"
        ).format(rotulo=html.escape(rotulo), valor=valor)
        for rotulo, valor in itens
    )
    return f'<div class="resumo-grid">{conteudo}</div>'


def renderizar_inicio():
    st.markdown('<div class="titulo-principal">Pandemic</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="subtitulo">Contagio, quarentena e sobrevivencia em um mundo 15x15.</div>',
        unsafe_allow_html=True,
    )

    coluna_esquerda, coluna_centro, coluna_direita = st.columns([1, 1.2, 1])

    with coluna_centro:
        if st.button("Jogar", use_container_width=True):
            iniciar_jogo()
            rerun()

        if st.button("Sair", use_container_width=True):
            st.session_state.tela = "saida"
            rerun()


def renderizar_saida():
    st.markdown('<div class="titulo-principal">Pandemic</div>', unsafe_allow_html=True)
    st.info("Jogo encerrado. Voce pode fechar esta aba.")

    if st.button("Voltar ao inicio"):
        st.session_state.tela = "inicio"
        rerun()


def renderizar_status_turno():
    st.markdown(
        (
            '<div class="painel-info">'
            "<strong>[ TURNO {rodada} ]</strong><br>"
            "Creditos Disponiveis: {creditos}"
            "</div>"
        ).format(
            rodada=st.session_state.rodada,
            creditos=st.session_state.creditos,
        ),
        unsafe_allow_html=True,
    )

    turno_info = st.session_state.turno_info
    if turno_info:
        st.markdown(
            (
                '<div class="painel-info">'
                "<strong>Noticia do dia</strong><br>"
                "{noticia}<br><br>"
                "<strong>Fator de letalidade:</strong> {fator:.2f}"
                "</div>"
            ).format(
                noticia=html.escape(turno_info["noticia"]),
                fator=turno_info["fator_letalidade"],
            ),
            unsafe_allow_html=True,
        )


def renderizar_alertas_superiores():
    alertas = []

    turno_info = st.session_state.turno_info
    if turno_info and turno_info.get("mensagem_quarentena"):
        alertas.append(turno_info["mensagem_quarentena"])

    alertas.extend(st.session_state.mensagens_acao)
    alertas.extend(st.session_state.eventos_rodada)

    if st.session_state.mensagem_continuacao:
        alertas.append(st.session_state.mensagem_continuacao)

    if st.session_state.mensagem_final:
        alertas.append(st.session_state.mensagem_final)

    if alertas:
        conteudo = "".join(
            f"<div>- {html.escape(str(alerta))}</div>" for alerta in alertas
        )
    else:
        conteudo = "<div>Sem ocorrencias recentes.</div>"

    st.markdown(
        (
            '<div class="painel-alertas">'
            "<strong>Ocorrencias da rodada</strong>"
            "{conteudo}"
            "</div>"
        ).format(conteudo=conteudo),
        unsafe_allow_html=True,
    )


def renderizar_mensagens_rodada():
    if st.session_state.mensagens_acao:
        for mensagem in st.session_state.mensagens_acao:
            st.info(mensagem)

    if st.session_state.eventos_rodada:
        st.markdown("**Eventos desta rodada:**")
        for evento in st.session_state.eventos_rodada:
            st.write(f"- {evento}")

    if st.session_state.mensagem_continuacao:
        st.warning(st.session_state.mensagem_continuacao)


def renderizar_mundo():
    st.markdown(
        (
            '<div class="painel-tabuleiro">'
            "<strong>Mapa de Contagio</strong>"
            "{grade}"
            "{legenda}"
            "</div>"
        ).format(
            grade=montar_grade_mundo(st.session_state.estado_jogo["matriz"]),
            legenda=montar_legenda(),
        ),
        unsafe_allow_html=True,
    )


def renderizar_menu_acoes():
    st.markdown("**Escolha sua acao**")
    st.caption(
        (
            "Quarentena 3x3: {quarentena} | Vacina: {vacina} | "
            "Hospital: {hospital} | Campanha: {campanha} | "
            "Passar: {passar} | +{creditos_rodada} creditos por rodada"
        ).format(
            quarentena=CUSTO_QUARENTENA,
            vacina=CUSTO_VACINA,
            hospital=CUSTO_HOSPITAL,
            campanha=CUSTO_CAMPANHA,
            passar=CUSTO_PASSAR_TURNO,
            creditos_rodada=CREDITOS_POR_RODADA,
        )
    )

    acao_label = st.radio(
        "Acao desejada",
        list(ACOES.keys()),
        label_visibility="collapsed",
    )
    acao = ACOES[acao_label]

    linha = coluna = None
    if acao in ("quarentena", "vacina", "hospital"):
        coluna_linha, coluna_coluna = st.columns(2)
        with coluna_linha:
            linha = st.number_input("Linha", min_value=0, max_value=TAMANHO - 1, step=1)
        with coluna_coluna:
            coluna = st.number_input("Coluna", min_value=0, max_value=TAMANHO - 1, step=1)

    if st.button("Executar acao", type="primary"):
        aplicar_acao(acao, int(linha or 0), int(coluna or 0))
        rerun()


def aplicar_acao(acao, linha, coluna):
    mensagens = []
    estado_jogo = st.session_state.estado_jogo
    garantir_estado_quarentena(estado_jogo)
    matriz = estado_jogo["matriz"]
    creditos = st.session_state.creditos
    acao_realizada = False

    st.session_state.eventos_rodada = []
    st.session_state.mensagem_continuacao = None

    if acao == "quarentena":
        if creditos < CUSTO_QUARENTENA:
            mensagens.append("Creditos insuficientes para criar uma area de quarentena.")
        else:
            total_celulas = criar_area_quarentena(estado_jogo, linha, coluna)
            creditos -= CUSTO_QUARENTENA
            acao_realizada = True
            mensagens.append(
                f"Area de quarentena criada em torno de ({linha},{coluna}), isolando {total_celulas} celulas."
            )

    elif acao == "vacina":
        if creditos < CUSTO_VACINA:
            mensagens.append("Creditos insuficientes para vacinar uma pessoa.")
        elif matriz[linha, coluna] != "+":
            mensagens.append("So e possivel vacinar uma pessoa saudavel.")
        else:
            matriz[linha, coluna] = "~"
            creditos -= CUSTO_VACINA
            acao_realizada = True
            mensagens.append(f"Pessoa em ({linha},{coluna}) foi vacinada e agora esta imune.")

    elif acao == "hospital":
        if creditos < CUSTO_HOSPITAL:
            mensagens.append("Creditos insuficientes para criar um hospital.")
        elif not criar_hospital(estado_jogo, linha, coluna):
            mensagens.append("So e possivel criar hospital em um espaco publico livre.")
        else:
            creditos -= CUSTO_HOSPITAL
            acao_realizada = True
            mensagens.append(f"Hospital de campanha criado em ({linha},{coluna}).")

    elif acao == "campanha":
        if creditos < CUSTO_CAMPANHA:
            mensagens.append(
                "Creditos insuficientes para realizar a campanha de conscientizacao."
            )
        else:
            estado_jogo["noticias_ruins_seguidas"] = max(
                0,
                estado_jogo["noticias_ruins_seguidas"]
                - REDUCAO_NOTICIAS_RUINS_CAMPANHA,
            )
            creditos -= CUSTO_CAMPANHA
            acao_realizada = True
            mensagens.append(
                "Campanha de conscientizacao realizada. O impacto das noticias ruins foi reduzido."
            )

    elif acao == "passar":
        acao_realizada = True
        mensagens.append("Voce optou por passar o turno.")

    st.session_state.creditos = creditos
    st.session_state.mensagens_acao = mensagens

    if acao_realizada:
        avancar_rodada()


def avancar_rodada():
    estado_jogo, eventos_da_rodada = calcular_proxima_geracao(
        st.session_state.estado_jogo
    )
    st.session_state.estado_jogo = estado_jogo
    st.session_state.eventos_rodada = eventos_da_rodada
    st.session_state.creditos += CREDITOS_POR_RODADA
    st.session_state.eventos_rodada.append(
        f"Voce recebeu {CREDITOS_POR_RODADA} creditos pela rodada."
    )
    st.session_state.mensagem_continuacao = None

    condicao_atingida, mensagem_condicao = verificar_fim_de_jogo(
        estado_jogo["matriz"]
    )

    if condicao_atingida and st.session_state.rodada < NUMERO_MINIMO_DE_RODADAS:
        st.session_state.mensagem_continuacao = (
            "Condicao de fim de jogo atingida, mas o minimo de "
            f"{NUMERO_MINIMO_DE_RODADAS} rodadas ainda nao foi alcancado. "
            "O jogo continua."
        )
        condicao_atingida = False

    st.session_state.rodada += 1

    if condicao_atingida:
        finalizar_jogo(mensagem_condicao)
        return

    if st.session_state.rodada > NUMERO_MINIMO_DE_RODADAS:
        finalizar_jogo(
            f"Fim de jogo: limite de {NUMERO_MINIMO_DE_RODADAS} rodadas atingido."
        )
        return

    st.session_state.turno_info = None


def finalizar_jogo(mensagem_final):
    st.session_state.mensagem_final = mensagem_final
    st.session_state.jogo_finalizado = True
    st.session_state.turno_info = None
    salvar_mundo(st.session_state.estado_jogo["matriz"], CAMINHO_MUNDO_FINAL)


def renderizar_jogo():
    if st.session_state.estado_jogo is None:
        iniciar_jogo()

    preparar_turno()

    st.markdown('<div class="titulo-principal">Pandemic</div>', unsafe_allow_html=True)

    renderizar_alertas_superiores()

    if st.session_state.jogo_finalizado:
        st.info(f"Estado final salvo em '{CAMINHO_MUNDO_FINAL.name}'.")

    coluna_menu, coluna_tabuleiro = st.columns([0.35, 0.65], gap="medium")

    with coluna_menu:
        st.markdown("### Central de Controle")
        st.markdown(montar_resumo_mundo(), unsafe_allow_html=True)
        renderizar_status_turno()

        if st.session_state.jogo_finalizado:
            if st.button("Voltar ao inicio", use_container_width=True):
                st.session_state.tela = "inicio"
                limpar_jogo()
                rerun()
        else:
            renderizar_menu_acoes()


    with coluna_tabuleiro:
        renderizar_mundo()

    if st.session_state.jogo_finalizado:
        return


def main():
    aplicar_estilos()
    inicializar_sessao()

    if st.session_state.tela == "inicio":
        renderizar_inicio()
    elif st.session_state.tela == "saida":
        renderizar_saida()
    else:
        renderizar_jogo()


if __name__ == "__main__":
    main()
