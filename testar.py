import os
import re
from graphviz import Digraph

class MyhillNerodeMinimizer:
    @staticmethod
    def minimize_dfa(dfa):
        """
        Minimiza um DFA usando o algoritmo de Myhill-Nerode.
        """
        def classes_equivalencia(dfa, estados):
            """
            Retorna as classes de equivalência de Nerode para os estados do DFA.
            """
            classes_equiv = {}
            for estado in estados:
                classes_equiv[estado] = {estado}

            for estado in estados:
                for simbolo in dfa['alfabeto']:
                    # Verifica se a transição está definida no DFA
                    if (estado, simbolo) in dfa['transicoes']:
                        prox_estado = dfa['transicoes'][(estado, simbolo)]
                        classes_equiv[estado].add(prox_estado)

            classes_unicas = []
            for conjunto_classe in classes_equiv.values():
                if conjunto_classe not in classes_unicas:
                    classes_unicas.append(conjunto_classe)

            return classes_unicas

        estados = dfa['estados']
        alfabeto = dfa['alfabeto']
        estado_inicial = dfa['inicial']
        estados_aceitacao = dfa['finais']
        transicoes = dfa['transicoes']

        # Define as classes de equivalência iniciais
        classes_equiv = classes_equivalencia(dfa, estados)

        # Refina as classes de equivalência
        while True:
            novas_classes_equiv = {}
            for conjunto_classe in classes_equiv:
                for simbolo in alfabeto:
                    transicoes_para = {}
                    for estado in conjunto_classe:
                        # Verifica se a transição está definida no DFA
                        if (estado, simbolo) in transicoes:
                            prox_estado = transicoes.get((estado, simbolo))
                            if prox_estado:
                                transicoes_para[prox_estado] = True

                    prox_classe = tuple(sorted(transicoes_para.keys()))

                    if prox_classe not in novas_classes_equiv:
                        novas_classes_equiv[prox_classe] = set()
                    novas_classes_equiv[prox_classe].update(conjunto_classe)

            if len(novas_classes_equiv) == len(classes_equiv):
                break
            classes_equiv = list(novas_classes_equiv.keys())

        # Constrói o novo DFA minimizado
        novos_estados = [tuple(sorted(conjunto_classe)) for conjunto_classe in classes_equiv]
        novas_transicoes = {}
        for conjunto_classe in classes_equiv:
            for simbolo in alfabeto:
                transicoes_para = set()
                for estado in conjunto_classe:
                    # Verifica se a transição está definida no DFA
                    if (estado, simbolo) in transicoes:
                        prox_estado = transicoes.get((estado, simbolo))
                        if prox_estado:
                            transicoes_para.add(tuple(sorted(prox_estado)))

                if transicoes_para:
                    novas_transicoes[(tuple(sorted(conjunto_classe)), simbolo)] = transicoes_para.pop()

        novo_estado_inicial = tuple(sorted([estado_inicial]))
        novos_estados_aceitacao = [tuple(sorted(conjunto_classe)) for conjunto_classe in classes_equiv if any(estado in estados_aceitacao for estado in conjunto_classe)]

        dfa_minimizado = {
            'estados': novos_estados,
            'alfabeto': alfabeto,
            'inicial': novo_estado_inicial,
            'finais': novos_estados_aceitacao,
            'transicoes': novas_transicoes
        }

        return dfa_minimizado

    @staticmethod
    def encontrar_estados_alcancaveis(afd):
        estados_alcancaveis = set()
        estados_visitados = set()

        def dfs(estado):
            estados_visitados.add(estado)
            estados_alcancaveis.add(estado)
            if estado in afd['transicoes']:
                for destino in afd['transicoes'][estado].values():
                    if destino not in estados_visitados:
                        dfs(destino)

        dfs(afd['inicial'])
        return estados_alcancaveis

    @staticmethod
    def refinar_particao(afd, particao):
        nova_particao = []
        for grupo in particao:
            if len(grupo) == 1:
                nova_particao.append(grupo)
                continue

            novos_grupos = []
            for estado in grupo:
                particao_atual = None
                for grupo_existente in novos_grupos:
                    representante = grupo_existente[0]
                    if MyhillNerodeMinimizer.sao_inequivalentes(afd, estado, representante, particao):
                        continue
                    particao_atual = grupo_existente
                    break

                if particao_atual is None:
                    novos_grupos.append([estado])
                else:
                    particao_atual.append(estado)

            nova_particao.extend(novos_grupos)

        return nova_particao

    @staticmethod
    def sao_inequivalentes(afd, estado1, estado2, particao):
        for simbolo in afd['alfabeto']:
            destino1 = afd['transicoes'].get(estado1, {}).get(simbolo)
            destino2 = afd['transicoes'].get(estado2, {}).get(simbolo)
            for grupo in particao:
                if destino1 in grupo and destino2 in grupo:
                    break
            else:
                return True
        return False

    @staticmethod
    def construir_automato_minimo(afd, particao, estados_alcancaveis):
        afd_minimo = {
            'alfabeto': afd['alfabeto'],
            'estados': [],
            'inicial': None,
            'finais': [],
            'transicoes': {}
        }

        estado_map = {}
        for i, grupo in enumerate(particao):
            novo_estado = f'q{i}'
            afd_minimo['estados'].append(novo_estado)
            if afd['inicial'] in grupo:
                afd_minimo['inicial'] = novo_estado
            if any(estado in afd['finais'] for estado in grupo):
                afd_minimo['finais'].append(novo_estado)
            for estado in grupo:
                estado_map[estado] = novo_estado

        for estado, transicoes in afd['transicoes'].items():
            if estado not in estados_alcancaveis:
                continue
            estado_minimo = estado_map[estado]
            afd_minimo['transicoes'][estado_minimo] = {}  # Inicializa as transições para o estado mínimo
            for simbolo, destino in transicoes.items():
                destino_minimo = estado_map[destino]
                afd_minimo['transicoes'][estado_minimo][simbolo] = destino_minimo

        return afd_minimo




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
            if isinstance(estado, tuple):  # Verifica se o estado é uma tupla
                estado_str = ','.join(estado)  # Converte a tupla para uma string separada por vírgula
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
                if isinstance(origem, tuple):  # Verifica se a origem é uma tupla
                    origem_str = ','.join(origem)  # Converte a tupla para uma string separada por vírgula
                else:
                    origem_str = origem
                if isinstance(destino, tuple):  # Verifica se o destino é uma tupla
                    destino_str = ','.join(destino)  # Converte a tupla para uma string separada por vírgula
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

    # Minimiza o AFD
    # afd_minimo = MyhillNerodeMinimizer.minimize_dfa(afd)

    # print("\nAFD mínimo:")
    # print(afd_minimo)

    # Desenha o diagrama do AFD mínimo
    AFDGraphDrawer.desenhar_diagrama_afd(afd_minimo, diretorio_atual)

else:
    print(mensagem)
