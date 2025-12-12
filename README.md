# Download de Imagens do ENEM

Script Python para baixar todas as imagens das questões do ENEM do site Curso Objetivo.

## Instalação

1. Instale as dependências necessárias:

```bash
pip install -r requirements.txt
```

## Uso

Execute o script:

```bash
python baixar_imagens_enem.py
```

O script irá:
1. Criar uma pasta chamada `imagens_enem_2025_1dia`
2. Baixar todas as imagens .gif encontradas na página
3. Salvar as imagens na pasta criada

## Funcionamento

O script utiliza dois métodos para encontrar e baixar as imagens:

1. **Método 1**: Faz scraping da página HTML para encontrar todas as referências a imagens .gif
2. **Método 2**: Tenta baixar imagens seguindo o padrão conhecido (001a.gif, 001b.gif, etc.)

As imagens serão salvas com seus nomes originais (ex: `017a.gif`, `017b.gif`, etc.)

