# Pandemic

Pandemic e um jogo/simulador de contagio em uma matriz 15x15. O jogador
administra creditos para conter a propagacao de uma doenca usando quarentena,
vacinacao, campanhas de conscientizacao e hospitais de campanha.

O projeto pode ser executado de duas formas:

- Interface web com Streamlit, em `streamlit_app.py`.
- Versao interativa pelo terminal, em `main.py`.

## Como o mundo e representado

O estado inicial fica em `mundo.txt`. Ele deve ter 15 linhas, cada uma com
15 simbolos separados por espaco.

Legenda dos simbolos:

- `+`: pessoa saudavel
- `^`: pessoa infectada
- `#`: area de quarentena
- `?`: espaco publico livre
- `~`: pessoa imune ou vacinada
- `H`: hospital de campanha

Ao fim do jogo, o estado final e salvo em `mundo_final.txt`.

## Como funciona

Cada rodada segue este fluxo:

1. O mapa atual e exibido.
2. Uma noticia do dia e sorteada.
3. A noticia ajusta o fator de letalidade do virus.
4. O jogador escolhe uma acao.
5. O mundo avanca uma geracao de forma simultanea.
6. O jogo verifica condicoes de vitoria, derrota ou limite de rodadas.

O jogo usa 500 creditos iniciais. As acoes disponiveis sao:

- Criar area de quarentena 3x3: custa 100 creditos.
- Vacinar uma pessoa saudavel: custa 80 creditos.
- Fazer campanha de conscientizacao: custa 150 creditos.
- Passar turno: custa 0 creditos.

Regras principais:

- Uma pessoa saudavel e infectada quando tem pelo menos 2 vizinhos infectados
  e nao esta protegida.
- Quarentenas e hospitais podem impedir novas infeccoes.
- Uma pessoa infectada passa por um teste de sobrevivencia apos 5 turnos.
- Se sobreviver, vira imune (`~`); se nao sobreviver, o local vira espaco livre
  (`?`).
- Uma quarentena dura 3 turnos e depois restaura as celulas afetadas.
- Hospitais atendem infectados em raio 2, tratam ate 3 pessoas por rodada e
  podem ser desativados se houver sobrecarga.
- Tres noticias ruins seguidas criam automaticamente uma area de quarentena
  perto de pessoas infectadas.

Por padrao, o jogo usa 10 rodadas como limite/minimo de execucao.

## Como rodar

Abra o PowerShell na pasta do projeto:

```powershell
cd C:\Users\pedro\Documents\files
```

Instale as dependencias:

```powershell
pip install -r requirements.txt
```

Para rodar a interface web:

```powershell
python -m streamlit run streamlit_app.py
```

Depois abra o endereco exibido no terminal. Normalmente sera:

```text
http://localhost:8501
```

Se a porta `8501` estiver ocupada, o Streamlit pode escolher outra porta.

Para rodar a versao de terminal:

```powershell
python main.py
```

## Arquivos principais

- `streamlit_app.py`: interface web do jogo.
- `main.py`: fluxo principal da versao de terminal.
- `mundo.py`: leitura, escrita e exibicao do mapa.
- `regras.py`: regras de contagio, cura, morte, quarentena e hospital.
- `eventos.py`: noticias do dia e quarentena automatica.
- `menu.py`: acoes do jogador na versao de terminal.
- `gerar_mundo_inicial.py`: script auxiliar para recriar um `mundo.txt` de
  exemplo.
- `requirements.txt`: dependencias Python do projeto.

## Gerar um mundo inicial de exemplo

A interface web nao mostra mais a opcao de gerar um novo mundo. Se precisar
recriar manualmente o arquivo `mundo.txt` para testes, rode:

```powershell
python gerar_mundo_inicial.py
```
