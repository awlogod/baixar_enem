#!/bin/bash

echo "=== Monitoramento do Download de Imagens do ENEM ==="
echo ""

while true; do
    # Verifica se o processo ainda está rodando
    if ! ps aux | grep -q "[p]ython3 baixar_imagens_enem.py"; then
        echo ""
        echo "✓ Script finalizado!"
        echo ""
        break
    fi
    
    # Mostra progresso
    clear
    echo "=== Monitoramento do Download de Imagens do ENEM ==="
    echo "Data/Hora: $(date '+%Y-%m-%d %H:%M:%S')"
    echo ""
    echo "Status: Script em execução..."
    echo ""
    
    # Conta pastas criadas
    pastas=$(ls -d ENEM_* 2>/dev/null | wc -l | tr -d ' ')
    echo "Pastas criadas: $pastas"
    
    # Conta total de imagens
    total_imagens=$(find ENEM_* -name "*.gif" 2>/dev/null | wc -l | tr -d ' ')
    echo "Total de imagens baixadas: $total_imagens"
    echo ""
    echo "=== Progresso por Ano ==="
    
    # Lista progresso por pasta
    for dir in ENEM_*/Dia_*; do
        if [ -d "$dir" ]; then
            count=$(ls -1 "$dir"/*.gif 2>/dev/null | wc -l | tr -d ' ')
            echo "$dir: $count imagens"
        fi
    done | sort
    
    echo ""
    echo "Pressione Ctrl+C para parar o monitoramento"
    sleep 30  # Atualiza a cada 30 segundos
done

echo ""
echo "=== RESUMO FINAL ==="
echo "Total de pastas: $(ls -d ENEM_* 2>/dev/null | wc -l | tr -d ' ')"
echo "Total de imagens: $(find ENEM_* -name "*.gif" 2>/dev/null | wc -l | tr -d ' ')"
echo ""
echo "Estrutura de pastas:"
for pasta in ENEM_*; do
    if [ -d "$pasta" ]; then
        echo "  $pasta/"
        for subpasta in "$pasta"/Dia_*; do
            if [ -d "$subpasta" ]; then
                count=$(ls -1 "$subpasta"/*.gif 2>/dev/null | wc -l | tr -d ' ')
                echo "    $(basename "$subpasta"): $count imagens"
            fi
        done
    fi
done

