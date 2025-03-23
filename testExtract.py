import pdfplumber
import re
import pandas as pd
import sqlite3
from scipy.stats import chi2_contingency  # Para análises estatísticas (exemplo)

def extrair_info_estudante(pdf_path):
    """
    Extrai a matrícula e o nome do estudante a partir do cabeçalho do PDF.
    Pressupõe que haja uma linha contendo, no início, 11 dígitos (matrícula)
    seguidos pelo nome do estudante em letras.
    """
    matricula = None
    nome = None
    with pdfplumber.open(pdf_path) as pdf:
        primeira_pagina = pdf.pages[0]
        texto = primeira_pagina.extract_text()
        if texto:
            linhas = texto.split("\n")
            # Procura por uma linha que comece com 11 dígitos seguidos por letras
            for linha in linhas:
                linha = linha.strip()
                match = re.match(r"^(\d{11})([A-ZÀ-Ü\s]+)$", linha, re.IGNORECASE)
                if match:
                    matricula = match.group(1).strip()
                    nome = match.group(2).strip().title()
                    break
    return matricula, nome

def extrair_dados_pdf(pdf_path, matricula, nome):
    """
    Extrai os dados acadêmicos do PDF. Cada linha extraída conterá as informações
    do componente: Ano/Semestre, Disciplina, Situação e Nota.
    Os dados serão vinculados ao estudante (matrícula e nome).
    """
    dados = []
    # Expressão regular para capturar linhas no formato:
    # <Ano.Semestre> <Disciplina> <Turma> <Situação> <Nota (opcional)> ...
    padrao = re.compile(
        r"(\d{4}\.\d)\s+([A-ZÃÉÍÓÚÀÈ\s]+?)\s+\d+\s+(APROVADO|REPROVADO|TRANCADO|MATRICULADO|PENDENTE)\s*([\d.]+)?"
    )
    
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            texto = page.extract_text()
            if texto:
                for linha in texto.split("\n"):
                    match = padrao.search(linha)
                    if match:
                        ano_semestre = match.group(1).strip()
                        disciplina = match.group(2).strip().title()
                        situacao = match.group(3).strip()
                        nota = float(match.group(4)) if match.group(4) is not None else None
                        # Adiciona matrícula e nome a cada registro
                        dados.append((matricula, nome, ano_semestre, disciplina, situacao, nota))
    return dados

def salvar_csv(dados, nome_arquivo="dados_historico.csv"):
    df = pd.DataFrame(dados, columns=["Matricula", "Nome", "Ano/Semestre", "Disciplina", "Situação", "Nota"])
    df.to_csv(nome_arquivo, index=False, encoding="utf-8")
    print(f"Dados salvos no arquivo CSV: {nome_arquivo}")
    return df

def salvar_bd(dados, nome_bd="historico.db"):
    conn = sqlite3.connect(nome_bd)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS historico (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            matricula TEXT,
            nome TEXT,
            ano_semestre TEXT,
            disciplina TEXT,
            situacao TEXT,
            nota REAL
        )
    """)
    
    cursor.executemany("""
        INSERT INTO historico (matricula, nome, ano_semestre, disciplina, situacao, nota)
        VALUES (?, ?, ?, ?, ?, ?)
    """, dados)
    
    conn.commit()
    conn.close()
    print(f"Dados armazenados no banco de dados: {nome_bd}")

def analise_dados(df):
    print("\n--- Análise dos Dados ---\n")
    
    # Disciplinas com mais reprovações
    reprovas = df[df["Situação"] == "REPROVADO"]["Disciplina"].value_counts()
    print("Disciplinas com mais reprovações:")
    print(reprovas if not reprovas.empty else "Nenhuma reprovação registrada", "\n")
    
    # Disciplinas com mais trancamentos
    trancamentos = df[df["Situação"] == "TRANCADO"]["Disciplina"].value_counts()
    print("Disciplinas com mais trancamentos:")
    print(trancamentos if not trancamentos.empty else "Nenhum trancamento registrado", "\n")
    
    # Média das notas por disciplina (apenas onde há nota)
    medias = df.groupby("Disciplina")["Nota"].mean().dropna()
    print("Nota média por disciplina:")
    print(medias, "\n")
    
    # Exemplo de análise estatística (teste Qui-Quadrado) - para associação entre reprovações em duas disciplinas
    # Esse exemplo exige dados de vários alunos; abaixo está ilustrativo.
    # df_estat = pd.DataFrame({
    #     'Disciplina_X': [1, 0, 1, 0, 0],
    #     'Disciplina_Y': [0, 1, 1, 0, 1]
    # })
    # tabela_contingencia = pd.crosstab(df_estat['Disciplina_X'], df_estat['Disciplina_Y'])
    # chi2, p, dof, ex = chi2_contingency(tabela_contingencia)
    # print("Teste Qui-Quadrado:")
    # print("Qui-quadrado:", chi2, "p-valor:", p)
    
def main():
    pdf_path = "historico_20220063005.pdf"
    
    # Extrai informações do estudante (matrícula e nome)
    matricula, nome = extrair_info_estudante(pdf_path)
    if not matricula or not nome:
        print("Não foi possível extrair a matrícula e/ou o nome do estudante. Verifique o formato do PDF.")
        return
    else:
        print(f"Processando histórico do estudante: {nome} (Matrícula: {matricula})")
    
    # Extrai os dados acadêmicos vinculados ao estudante
    dados_extraidos = extrair_dados_pdf(pdf_path, matricula, nome)
    if not dados_extraidos:
        print("Nenhum dado acadêmico foi extraído. Verifique o formato do PDF.")
        return
    
    # Salva os dados em CSV e em um banco de dados SQLite
    df = salvar_csv(dados_extraidos)
    salvar_bd(dados_extraidos)
    
    # Realiza análises
    analise_dados(df)
    
if __name__ == "__main__":
    main()
