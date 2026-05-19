import os

## pegar o caminho do arquivo atual e depois navegar para o arquivo de dados
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

usuarios = os.path.join(BASE_DIR, "..", "data", "usuarios.csv")

def cadastrar_usuario(email, senha):
    id_novo =1

    with open(usuarios, "r") as f:
        linhas = f.readlines()

        ids = []

        for linha in linhas[1:]:
            dados = linha.strip().split(",")

            if dados[0]:
                ids.append(int(dados[0]))

        if ids:
            id_novo = max(ids) + 1
    with open(usuarios, "a") as f:
        f.write(f"{id_novo},{email},{senha}\n")