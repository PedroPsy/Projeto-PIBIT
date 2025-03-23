import pdfplumber
import pandas as pd
import sqlite3
import re

# Função para extrair dados do PDF
def extrair_dados_pdf(pdf_path):
    dados = []
    
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                linhas = text.split("\n")
                
                for linha in linhas:
                    match = re.search(r"(\d{4}\.\d)\s+([\w\sÀ-ÿ]+)\s+\d+\s+(\w+)\s+([\d.-]+)?\s+\w+", linha)
                    if match:
                        ano_semestre = match.group(1)
                        disciplina = match.group(2).strip()
                        situacao = match.group(3)
                        nota = float(match.group(4)) if match.group(4) else None
                        dados.append((ano_semestre, disciplina, situacao, nota))

    return dados

# Salvar em CSV
def salvar_csv(dados, nome_arquivo="dados_historico.csv"):
    df = pd.DataFrame(dados, columns=["Ano/Semestre", "Disciplina", "Situação", "Nota"])
    df.to_csv(nome_arquivo, index=False, encoding="utf-8")
    print(f"Dados salvos em {nome_arquivo}")

# Salvar no banco de dados SQLite
def salvar_bd(dados, nome_bd="historico.db"):
    conn = sqlite3.connect(nome_bd)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS historico (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ano_semestre TEXT,
            disciplina TEXT,
            situacao TEXT,
            nota REAL
        )
    """)
    
    cursor.executemany("INSERT INTO historico (ano_semestre, disciplina, situacao, nota) VALUES (?, ?, ?, ?)", dados)
    
    conn.commit()
    conn.close()
    print(f"Dados armazenados em {nome_bd}")

# Função para análises
def analise_dados(nome_bd="historico.db"):
    conn = sqlite3.connect(nome_bd)
    df = pd.read_sql("SELECT * FROM historico", conn)
    conn.close()
    
    print("\nDisciplinas com mais reprovações:")
    print(df[df["Situação"] == "REPROVADO"]["Disciplina"].value_counts().head())

    print("\nDisciplinas com mais trancamentos:")
    print(df[df["Situação"] == "TRANCADO"]["Disciplina"].value_counts().head())

    print("\nNota média por disciplina:")
    print(df.groupby("Disciplina")["Nota"].mean().dropna())

# Execução
pdf_path = "historico_20220063005.pdf"
dados_extraidos = extrair_dados_pdf(pdf_path)
salvar_csv(dados_extraidos)
salvar_bd(dados_extraidos)
analise_dados()
