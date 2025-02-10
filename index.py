import re
import PyPDF2
import pandas as pd

# Defina o caminho do arquivo PDF de entrada
pdf_path = 'entrada.pdf'

# Função para extrair texto de todas as páginas do PDF
def extrair_texto_pdf(caminho_pdf):
    texto_completo = ""
    with open(caminho_pdf, 'rb') as arquivo:
        leitor = PyPDF2.PdfReader(arquivo)
        for pagina in leitor.pages:
            texto = pagina.extract_text()
            if texto:
                texto_completo += texto + "\n"
    return texto_completo

# Função para extrair os dados (aluno, matrícula e média) de cada linha do texto
def extrair_dados(texto):
    dados = []
    
    # Expressão regular para capturar os campos
    # Esta regex busca padrões como:
    # "Aluno: <nome> Matrícula: <numero> Média: <valor>"
    # Pode-se editar para buscar separadamente cada disciplina 
    padrao = r"Aluno:\s*(?P<aluno>.*?)\s*Matr[ií]cula:\s*(?P<matricula>\S+)\s*M[eé]dia:\s*(?P<media>\S+)"
    
    # Para cada linha do texto, tentar encontrar o padrão
    for linha in texto.splitlines():
        correspondencia = re.search(padrao, linha, re.IGNORECASE)
        if correspondencia:
            aluno = correspondencia.group("aluno").strip()
            matricula = correspondencia.group("matricula").strip()
            media = correspondencia.group("media").strip()
            dados.append({
                "aluno": aluno,
                "matricula": matricula,
                "media": media
            })
    return dados

# Extração do texto do PDF
texto_extraido = extrair_texto_pdf(pdf_path)

# Extração dos dados do texto
lista_dados = extrair_dados(texto_extraido)

# Criação do DataFrame com as colunas desejadas
df = pd.DataFrame(lista_dados, columns=["aluno", "matricula", "media"])

# Salva o DataFrame em um arquivo Excel
df.to_excel("saida.xlsx", index=False)

print("Planilha Excel criada com sucesso!")
