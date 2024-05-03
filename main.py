import os
import re
from graphviz import Digraph

class MyhillNerodeMinimizer:
    pass

class AFDGraphDrawer:
    @staticmethod
    def desenhar_diagrama_afd(afd, diretorio):
        # Criação do grafo
        graph = Digraph(format='png')
        graph.attr(rankdir='LR')
        graph.node('', shape='none')
        graph.edge('', 'q0')

        # Adiciona estados
        for estado in afd['estados']:
            if isinstance(estado, tuple): 
                estado_str = ','.join(estado)
            else:
                estado_str = estado
            if estado in afd['finais']:
                if estado in afd['inicial']:
                    graph.node(estado_str, shape='doublecircle')
                else:
                    graph.node(estado_str, shape='doublecircle')
            elif estado in afd['inicial']:
                graph.node(estado_str, shape='circle', peripheries='2')
            else:
                graph.node(estado_str, shape='circle')

        # Adiciona transições
        for origem, trans in afd['transicoes'].items():
            for simbolo, destino in trans.items():
                if isinstance(origem, tuple):  
                    origem_str = ','.join(origem)  
                else:
                    origem_str = origem
                if isinstance(destino, tuple): 
                    destino_str = ','.join(destino)  
                else:
                    destino_str = destino
                graph.edge(origem_str, destino_str, label=simbolo)

        # Salva o grafo em um arquivo
        caminho_arquivo = os.path.join(diretorio, 'afd_diagram.png')
        graph.render(filename=caminho_arquivo, cleanup=True, format='png')

        # Exibe o grafo
        graph.view()



def verificar_entrada_afd(arquivo):
    # Verifica se o arquivo existe
    if not os.path.exists(arquivo):
        return False, "O arquivo não existe."

    # Verifica se o arquivo tem extensão .txt
    if not arquivo.endswith('.txt'):
        return False, "O arquivo não é um arquivo de texto (.txt)."

    # Verifica se o arquivo está vazio
    if os.path.getsize(arquivo) == 0:
        return False, "O arquivo está vazio."

    # Verifica se as informações básicas estão presentes
    prefixos_esperados = ["alfabeto:", "estados:", "inicial:", "finais:", "transicoes"]
    with open(arquivo, 'r') as f:
        linhas = f.readlines()
        for prefixo in prefixos_esperados:
            if not any(linha.startswith(prefixo) for linha in linhas):
                return False, f"O arquivo não contém a informação necessária: {prefixo}"

    # estado inicial
    estados_iniciais = [linha.split(":")[1].strip() for linha in linhas if linha.startswith("inicial:")]
    if len(estados_iniciais) != 1:
        return False, "O arquivo não contém exatamente um estado inicial."
    elif len(estados_iniciais[0].split(",")) != 1:  # Verifica se há apenas um estado inicial
        return False, "O arquivo contém mais de um estado inicial."
    elif not estados_iniciais[0]:  # Verifica se não há nenhum estado inicial
        return False, "O arquivo não contém nenhum estado inicial especificado."

    # Verifica se o AFD é determinístico
    transicoes = {}
    for linha in linhas:
        if linha.startswith("transicoes"):
            continue
        elif not linha.startswith(("alfabeto:", "estados:", "inicial:", "finais:")):
            partes = linha.strip().split(",")
            if len(partes) != 3:
                return False, "Transição inválida: cada transição deve conter origem, destino e símbolo separados por vírgula."
            origem, destino, simbolo = partes
            if origem not in transicoes:
                transicoes[origem] = {}
            if simbolo in transicoes[origem]:
                return False, "O AFD não é determinístico."
            transicoes[origem][simbolo] = destino

    # Verifica se as transições abrangem todos os símbolos do alfabeto
    alfabeto = [simbolo.strip() for simbolo in linhas if simbolo.startswith("alfabeto:")][0].split(":")[1].split(",")
    for origem, trans in transicoes.items():
        if set(trans.keys()) != set(alfabeto):
            return False, f"As transições do estado {origem} não abrangem todos os símbolos do alfabeto."

    return True, "Arquivo de entrada válido para um AFD."


def ler_afd(arquivo):
    afd = {
        "transicoes": {}  # Inicializa um dicionário vazio para armazenar as transições
    }

    with open(arquivo, 'r') as f:
        for linha in f:
            linha = linha.strip()
            if linha.startswith("alfabeto:"):
                afd["alfabeto"] = linha.split(":")[1].split(",")
            elif linha.startswith("estados:"):
                afd["estados"] = linha.split(":")[1].split(",")
            elif linha.startswith("inicial:"):
                afd["inicial"] = linha.split(":")[1].strip()
            elif linha.startswith("finais:"):
                afd["finais"] = linha.split(":")[1].split(",")
            elif linha.startswith("transicoes"):
                continue
            elif linha.strip() and "transicoes:" not in linha:
                # Trata transições na mesma linha usando expressão regular
                transicoes = re.findall(r"(\w+),(\w+),(\w+)", linha)
                for transicao in transicoes:
                    origem, destino, simbolo = transicao
                    if origem not in afd["transicoes"]:
                        afd["transicoes"][origem] = {}
                    afd["transicoes"][origem][simbolo] = destino

    return afd


# Diretório do projeto
diretorio_atual = r"C:\Users\carlo\Desktop\Linguagens Formais\projeto"
print("Diretório de trabalho atual:", diretorio_atual)
print("Conteúdo do diretório:")
for item in os.listdir(diretorio_atual):
    print(item)

# Caminho para o arquivo
arquivo = r"C:\Users\carlo\Desktop\Linguagens Formais\projeto\arquivo.txt"

# Verifica se o arquivo de entrada é válido
valido, mensagem = verificar_entrada_afd(arquivo)
if valido:
    print("Caminho do arquivo:", arquivo)
    print(mensagem)
    afd = ler_afd(arquivo)
    print("AFD original:")
    print(afd)



    AFDGraphDrawer.desenhar_diagrama_afd(afd, diretorio_atual)
else:
    print(mensagem)