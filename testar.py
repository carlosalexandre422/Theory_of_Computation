
import os

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
    transicoes = []
    for linha in linhas:
        if linha.startswith("transicoes"):
            continue
        elif not linha.startswith(("alfabeto:", "estados:", "inicial:", "finais:")):
            transicao = linha.strip().split(",")
            if len(transicao) != 3:
                return False, "Formato de transição inválido."
            origem, destino, simbolo = transicao
            if (origem, simbolo) in transicoes:
                return False, "O AFD não é determinístico."
            transicoes.append((origem, simbolo))

    # Verifica se as transições abrangem todos os símbolos do alfabeto
    alfabeto = [simbolo.strip() for simbolo in linhas if simbolo.startswith("alfabeto:")][0].split(":")[1].split(",")
    transicoes = set()
    for linha in linhas:
        if linha.startswith("transicoes"):
            continue
        elif not linha.startswith(("alfabeto:", "estados:", "inicial:", "finais:")):
            partes = linha.strip().split(",")
            if len(partes) != 3:
                return False, "Transição inválida: cada transição deve conter origem, destino e símbolo separados por vírgula."
            origem, destino, simbolo = partes
            transicoes.add((origem, simbolo))
    
    simbolos_transicoes = set(simbolo for _, simbolo in transicoes)
    if set(alfabeto) != simbolos_transicoes:
        return False, "As transições não abrangem todos os símbolos do alfabeto."

    for estado in set(origem for origem, _ in transicoes):
        if len(set(simbolo for origem, simbolo in transicoes if origem == estado)) != len(alfabeto):
            return False, f"As transições do estado {estado} não abrangem todos os símbolos do alfabeto."

    return True, "Arquivo de entrada válido para um AFD."

def ler_afd(arquivo):
    afd = {}

    with open(arquivo, 'r') as f:
        for linha in f:
            linha = linha.strip()
            if linha.startswith("alfabeto:"):
                afd["alfabeto"] = linha.split(":")[1].split(",")
            elif linha.startswith("estados:"):
                afd["estados"] = linha.split(":")[1].split(",")
            elif linha.startswith("inicial:"):
                afd["inicial"] = linha.split(":")[1].strip()  # Corrigido para atribuir o estado inicial corretamente
            elif linha.startswith("finais:"):
                afd["finais"] = linha.split(":")[1].split(",")
            elif linha.startswith("transicoes"):
                afd["transicoes"] = []
            elif linha.strip():  # Verifica se a linha não está em branco
                # Trata múltiplas transições na mesma linha
                partes = linha.split()
                for parte in partes[1:]:
                    origem, destino, simbolo = parte.strip().split(",")
                    afd["transicoes"].append((origem, destino, simbolo))

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
    print(afd)
else:
    print(mensagem)
