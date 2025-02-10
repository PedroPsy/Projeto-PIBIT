from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

def criar_pdf_exemplo(nome_arquivo):
    # Define o tamanho da página e cria o canvas
    c = canvas.Canvas(nome_arquivo, pagesize=letter)
    width, height = letter
    c.setFont("Helvetica", 12)
    
    # Dados de exemplo (cada linha no formato esperado pelo algoritmo)
    linhas = [
        "Aluno: João da Silva Matrícula: 12345 Média: 8.5",
        "Aluno: Maria Oliveira Matrícula: 54321 Média: 9.0",
        "Aluno: Pedro Santos Matrícula: 98765 Média: 7.5"
    ]
    
    # Posição inicial para escrever as linhas
    y = height - 50
    for linha in linhas:
        c.drawString(50, y, linha)
        y -= 20  # Desloca a posição vertical para a próxima linha
    
    # Salva o PDF
    c.save()

# Gera o PDF de teste
criar_pdf_exemplo("entrada.pdf")
print("PDF de teste 'entrada.pdf' criado com sucesso!")
