import requests
from bs4 import BeautifulSoup, SoupStrainer
import zipfile
import os
from datetime import datetime

def buscar_links_ans(url_alvo):
    """
    Acessa o site da ANS e retorna um dicionário com os links dos Anexos I e II.
    Filtra por tag <a> e classe 'external-link'.
    """
    headers = {
       "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    links_encontrados = {}
    
    try:
        # Acesso ao site
        response = requests.get(url_alvo, headers=headers)
        response.raise_for_status()
        
        # Filtra o html pela tag <a> e classe 'external-link'
        filtro = SoupStrainer("a", attrs={"class": "external-link"})
        soup = BeautifulSoup(response.content, "html.parser", parse_only=filtro)
        
        for link in soup.find_all("a"):
            # Limpeza do texto para evitar erros com o ponto final
            texto = link.get_text().strip().replace(".", "")
            href = link.get('href')
            
            # Identificação dos pdf's 
            if texto == "Anexo I":
                links_encontrados["Anexo_I"] = href
            elif texto == "Anexo II":
                links_encontrados["Anexo_II"] = href
                
        return links_encontrados

    except Exception as e:
        print(f"Erro ao buscar links: {e}")
        return {}

def baixar_e_compactar_anexos(links_dict):
    """
    Recebe um dicionário com os URLs, baixa os PDFs e os compacta em um ZIP.
    """
    if not links_dict:
        print("Aviso: Nenhum link encontrado.")
        return

    # Gera o timestamp no formato: dia_mes_ano_hora_minuto_segundo
    timestamp = datetime.now().strftime("%d-%m-%y_%H%M%S")
    nome_zip = f"Anexos_ANS_{timestamp}.zip"

    # Define o caminho para salvar na mesma pasta do script
    diretorio_script = os.path.dirname(os.path.abspath(__file__))
    caminho_zip = os.path.join(diretorio_script, nome_zip)

    try:
        with zipfile.ZipFile(caminho_zip, 'w') as zip_arq:
            for nome, url in links_dict.items():
                nome_pdf = f"{nome}.pdf"
                print(f"Baixando: {nome_pdf}...")
                
                conteudo_pdf = requests.get(url).content
                
                with open(nome_pdf, "wb") as f:
                    f.write(conteudo_pdf)
                
                zip_arq.write(nome_pdf)
                os.remove(nome_pdf)
        
        print(f"\nSucesso! Arquivo gerado: {nome_zip}")
        print(f"Local: {caminho_zip}")

    except Exception as e:
        print(f"Erro no download/ZIP: {e}")

# --- Execução ---
url_ans = "https://www.gov.br/ans/pt-br/acesso-a-informacao/participacao-da-sociedade/atualizacao-do-rol-de-procedimentos"
baixar_e_compactar_anexos(buscar_links_ans(url_ans))


