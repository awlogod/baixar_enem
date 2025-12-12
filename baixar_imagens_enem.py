
"""
Script para baixar todas as imagens das questões do ENEM do site Curso Objetivo.
Organiza as imagens por ano, tipo (normal/2ª aplicação) e dia (Dia 1, Dia 2).
"""

import os
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time
from pathlib import Path
from collections import defaultdict


HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
    'Referer': 'https://www.curso-objetivo.br/',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
}

HEADERS_IMAGEM = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
    'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
    'Referer': 'https://www.curso-objetivo.br/',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Sec-Fetch-Dest': 'image',
    'Sec-Fetch-Mode': 'no-cors',
    'Sec-Fetch-Site': 'same-origin'
}

URL_PAGINA_PRINCIPAL = "https://www.curso-objetivo.br/vestibular/resolucao-comentada/enem.aspx"

def criar_pasta(pasta):
    """Cria a pasta se ela não existir."""
    if not os.path.exists(pasta):
        os.makedirs(pasta)
        return True
    return False

def eh_imagem_valida(conteudo):
    """Verifica se o conteúdo baixado é realmente uma imagem."""
    
    if conteudo.startswith(b'<!DOCTYPE') or conteudo.startswith(b'<html') or conteudo.startswith(b'<HTML'):
        return False
    
    if conteudo.startswith(b'GIF87a') or conteudo.startswith(b'GIF89a'):
        return True
    
    
    if conteudo.startswith(b'\x89PNG\r\n\x1a\n'):
        return True
    
    
    if conteudo.startswith(b'\xff\xd8\xff'):
        return True
    
    return False

def baixar_imagem(url, caminho_local, referer=None):
    """Baixa uma imagem da URL e salva localmente."""
    try:
        headers = HEADERS_IMAGEM.copy()
        if referer:
            headers['Referer'] = referer
        
        response = requests.get(url, headers=headers, timeout=30, stream=True)
        response.raise_for_status()
        
        conteudo = response.content
        
        
        if not eh_imagem_valida(conteudo):
            return False
        
        with open(caminho_local, 'wb') as f:
            f.write(conteudo)
        
        return True
    except Exception as e:
        return False

def descobrir_anos_e_dias():
    """Descobre todos os anos e dias disponíveis na página principal."""
    try:
        print("Acessando página principal para descobrir anos disponíveis...")
        response = requests.get(URL_PAGINA_PRINCIPAL, headers=HEADERS, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        
        enem_anos = defaultdict(lambda: defaultdict(list))
        
        
        for link in soup.find_all('a', href=True):
            href = link.get('href', '')
            texto = link.get_text(strip=True)
            
            
            match1 = re.search(r'enem(\d{4})_(\d)dia\.aspx', href, re.I)
            if match1:
                ano = match1.group(1)
                dia = match1.group(2)
                enem_anos[ano]['normal'].append(int(dia))
            
            
            match2 = re.search(r'enem(\d{4})_2aplicacao_(\d)dia\.aspx', href, re.I)
            if match2:
                ano = match2.group(1)
                dia = match2.group(2)
                enem_anos[ano]['2a_aplicacao'].append(int(dia))
            
            
            match3 = re.search(r'enem(\d{4})_digital_(\d)dia\.aspx', href, re.I)
            if match3:
                ano = match3.group(1)
                dia = match3.group(2)
                enem_anos[ano]['digital'].append(int(dia))
            
            
            match4 = re.search(r'enem(\d{4})_impressa_(\d)dia\.aspx', href, re.I)
            if match4:
                ano = match4.group(1)
                dia = match4.group(2)
                enem_anos[ano]['impressa'].append(int(dia))
            
            
            match5 = re.search(r'enem(\d{4})_resolucao\.aspx', href, re.I)
            if match5:
                ano = match5.group(1)
                
                enem_anos[ano]['normal'].extend([1, 2])
        
        
        for ano in enem_anos:
            for tipo in enem_anos[ano]:
                enem_anos[ano][tipo] = sorted(set(enem_anos[ano][tipo]))
        
        return dict(enem_anos)
    
    except Exception as e:
        print(f"Erro ao descobrir anos: {e}")
        return {}

def construir_urls(ano, tipo, dia):
    """Constrói as URLs da página e das imagens baseado no ano, tipo e dia."""
    base_url = "https://www.curso-objetivo.br/vestibular/resolucao-comentada/enem/"
    
    
    if tipo == 'normal':
        url_pagina = f"{base_url}enem{ano}_{dia}dia.aspx"
        url_imagens = f"{base_url}{ano}/{dia}dia/"
    elif tipo == '2a_aplicacao':
        url_pagina = f"{base_url}enem{ano}_2aplicacao_{dia}dia.aspx"
        url_imagens = f"{base_url}{ano}/2aplicacao/{dia}dia/"
    elif tipo == 'digital':
        url_pagina = f"{base_url}enem{ano}_digital_{dia}dia.aspx"
        url_imagens = f"{base_url}{ano}/digital/{dia}dia/"
    elif tipo == 'impressa':
        url_pagina = f"{base_url}enem{ano}_impressa_{dia}dia.aspx"
        url_imagens = f"{base_url}{ano}/impressa/{dia}dia/"
    else:
        
        url_pagina = f"{base_url}enem{ano}_resolucao.aspx"
        url_imagens = f"{base_url}{ano}/{dia}dia/"
    
    return url_pagina, url_imagens

def encontrar_imagens_na_pagina(url_pagina, url_base_imagens):
    """Encontra todas as referências a imagens .gif na página."""
    try:
        response = requests.get(url_pagina, headers=HEADERS, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        imagens = set()
        
        
        for img in soup.find_all('img'):
            src = img.get('src', '') or img.get('data-src', '') or img.get('data-lazy-src', '')
            if src and '.gif' in src.lower():
                if src.startswith('http'):
                    url_completa = src
                else:
                    url_completa = urljoin(url_base_imagens, src)
                imagens.add(url_completa)
        
        html_texto = str(soup)
        padroes_gif = re.findall(r'(\d{3}[a-z]\.gif)', html_texto, re.I)
        for padrao in padroes_gif:
            url_completa = urljoin(url_base_imagens, padrao)
            imagens.add(url_completa)
        
        padroes_caminho = re.findall(r'([\w/]+/\d{3}[a-z]\.gif)', html_texto, re.I)
        for padrao in padroes_caminho:
            if padrao.startswith('http'):
                imagens.add(padrao)
            else:
                url_completa = urljoin(url_base_imagens, padrao)
                imagens.add(url_completa)
        
        return list(imagens)
    
    except Exception as e:
        return []

def baixar_imagens_por_padrao(url_base_imagens, pasta_destino, referer, max_questoes=180):
    """Tenta baixar imagens baseado no padrão conhecido."""
    imagens_baixadas = 0
    imagens_nao_encontradas = 0
    
    
    for questao in range(1, max_questoes + 1):
        questao_str = f"{questao:03d}"
        encontrou_alguma = False
        
        for letra in 'abcdefghijklmnopqrstuvwxyz':
            nome_arquivo = f"{questao_str}{letra}.gif"
            url_imagem = urljoin(url_base_imagens, nome_arquivo)
            caminho_local = os.path.join(pasta_destino, nome_arquivo)
            
            
            if os.path.exists(caminho_local):
                try:
                    with open(caminho_local, 'rb') as f:
                        if eh_imagem_valida(f.read()):
                            continue
                except:
                    pass
            
            if baixar_imagem(url_imagem, caminho_local, referer):
                imagens_baixadas += 1
                encontrou_alguma = True
                time.sleep(0.05)  
            else:
                imagens_nao_encontradas += 1
                if imagens_nao_encontradas > 5:
                    break
        
        if encontrou_alguma:
            imagens_nao_encontradas = 0
    
    return imagens_baixadas

def processar_ano_dia(ano, tipo, dia, url_pagina, url_base_imagens):
    """Processa o download de imagens para um ano, tipo e dia específicos."""
    if tipo == 'normal':
        pasta_base = f"ENEM_{ano}"
        nome_exibicao = f"ENEM {ano} - Dia {dia}"
    elif tipo == '2a_aplicacao':
        pasta_base = f"ENEM_{ano}_2a_Aplicacao"
        nome_exibicao = f"ENEM {ano} (2ª Aplicação) - Dia {dia}"
    elif tipo == 'digital':
        pasta_base = f"ENEM_{ano}_Digital"
        nome_exibicao = f"ENEM {ano} (Digital) - Dia {dia}"
    elif tipo == 'impressa':
        pasta_base = f"ENEM_{ano}_Impressa"
        nome_exibicao = f"ENEM {ano} (Impressa) - Dia {dia}"
    else:
        pasta_base = f"ENEM_{ano}"
        nome_exibicao = f"ENEM {ano} - Dia {dia}"
    
    pasta_dia = os.path.join(pasta_base, f"Dia_{dia}")
    criar_pasta(pasta_dia)
    
    print(f"\n  [{nome_exibicao}]")
    
    imagens_encontradas = encontrar_imagens_na_pagina(url_pagina, url_base_imagens)
    imagens_baixadas_html = 0
    
    if imagens_encontradas:
        for url_imagem in imagens_encontradas:
            nome_arquivo = os.path.basename(urlparse(url_imagem).path)
            if not nome_arquivo or not nome_arquivo.endswith('.gif'):
                continue
            
            caminho_local = os.path.join(pasta_dia, nome_arquivo)
            
            if os.path.exists(caminho_local):
                try:
                    with open(caminho_local, 'rb') as f:
                        if eh_imagem_valida(f.read()):
                            continue
                except:
                    pass
            
            if baixar_imagem(url_imagem, caminho_local, url_pagina):
                imagens_baixadas_html += 1
                time.sleep(0.05)
    
    imagens_por_padrao = baixar_imagens_por_padrao(url_base_imagens, pasta_dia, url_pagina)
    
    total_arquivos = 0
    if os.path.exists(pasta_dia):
        total_arquivos = len([f for f in os.listdir(pasta_dia) 
                             if f.endswith('.gif') and os.path.getsize(os.path.join(pasta_dia, f)) > 0])
    
    print(f"    ✓ {total_arquivos} imagens baixadas")
    return total_arquivos

def main():
    """Função principal."""
    print("=" * 70)
    print("Download de Imagens do ENEM - TODOS OS ANOS")
    print("Organização: Ano -> Tipo -> Dia")
    print("=" * 70)
    
    enem_anos = descobrir_anos_e_dias()
    
    if not enem_anos:
        print("✗ Não foi possível descobrir os anos disponíveis.")
        return
    
    print(f"\n✓ Encontrados {len(enem_anos)} anos do ENEM")
    
    anos_ordenados = sorted(enem_anos.keys(), reverse=True)
    
    if '2025' in anos_ordenados:
        anos_ordenados.remove('2025')
        print("ℹ Ano 2025 será pulado (já foi baixado anteriormente)")
    
    total_geral = 0
    total_processados = 0
    
    for ano in anos_ordenados:
        print(f"\n{'='*70}")
        print(f"Processando ENEM {ano}")
        print(f"{'='*70}")
        
        tipos_ordenados = sorted(enem_anos[ano].keys())
        
        for tipo in tipos_ordenados:
            dias = enem_anos[ano][tipo]
            
            for dia in dias:
                url_pagina, url_base_imagens = construir_urls(ano, tipo, dia)
                total_dia = processar_ano_dia(ano, tipo, dia, url_pagina, url_base_imagens)
                total_geral += total_dia
                total_processados += 1
                time.sleep(0.5)  
    
    print("\n" + "=" * 70)
    print("✓ Processo concluído!")
    print(f"✓ Total de provas processadas: {total_processados}")
    print(f"✓ Total geral de imagens baixadas: {total_geral}")
    print("\nEstrutura de pastas criada:")
    
    pastas = [d for d in os.listdir('.') if os.path.isdir(d) and d.startswith('ENEM_')]
    for pasta in sorted(pastas):
        if os.path.isdir(pasta):
            subpastas = [sd for sd in os.listdir(pasta) if os.path.isdir(os.path.join(pasta, sd))]
            for subpasta in sorted(subpastas):
                caminho_completo = os.path.join(pasta, subpasta)
                total = len([f for f in os.listdir(caminho_completo) if f.endswith('.gif')])
                print(f"  - {caminho_completo}/ ({total} imagens)")
    
    print("=" * 70)

if __name__ == "__main__":
    main()
