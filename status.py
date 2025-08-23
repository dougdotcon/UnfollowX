#!/usr/bin/env python3
"""
Script para verificar o status do sistema de unfollow automático
"""

import json
import os
import pandas as pd
from datetime import datetime

def load_state():
    """Carrega o estado atual do sistema"""
    state_file = 'unfollow_state.json'
    if os.path.exists(state_file):
        try:
            with open(state_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ Erro ao carregar estado: {e}")
    return None

def analyze_csv(csv_filename):
    """Analisa o arquivo CSV e retorna estatísticas"""
    try:
        df = pd.read_csv(csv_filename)
        
        total = len(df)
        immune = len(df[df['immunity_status'] == 'immune'])
        not_immune = len(df[df['immunity_status'] == 'not_immune'])
        errors = len(df[df['immunity_status'] == 'analysis_error'])
        
        # Estatísticas por categoria
        categories = df['category'].value_counts().to_dict()
        
        return {
            'total': total,
            'immune': immune,
            'not_immune': not_immune,
            'errors': errors,
            'immunity_rate': (immune / total * 100) if total > 0 else 0,
            'categories': categories
        }
    except Exception as e:
        print(f"❌ Erro ao analisar CSV: {e}")
        return None

def show_detailed_status():
    """Mostra status detalhado do sistema"""
    state = load_state()
    
    if not state:
        print("❌ Nenhum estado encontrado. Execute o script principal primeiro.")
        return
    
    print(f"\n{'='*70}")
    print(f"📊 STATUS DETALHADO DO SISTEMA DE UNFOLLOW")
    print(f"{'='*70}")
    
    # Informações básicas
    total = state.get('total_to_process', 0)
    processed = state.get('processed_count', 0)
    remaining = total - processed
    
    print(f"📈 PROGRESSO GERAL:")
    print(f"   • Total para processar: {total}")
    print(f"   • Já processados: {processed}")
    print(f"   • Restantes: {remaining}")
    
    if total > 0:
        progress = (processed / total) * 100
        print(f"   • Progresso: {progress:.1f}%")
        
        # Estimativa de tempo
        if remaining > 0:
            hours_remaining = remaining / 60  # 20 unfollows a cada 20 min = 60 por hora
            print(f"   • Tempo estimado restante: {hours_remaining:.1f} horas")
    
    print(f"\n⏰ TIMESTAMPS:")
    print(f"   • Última execução: {state.get('last_run', 'Nunca')}")
    print(f"   • Última atualização: {state.get('last_update', 'Nunca')}")
    
    # Informações do CSV
    csv_file = state.get('csv_filename')
    if csv_file and os.path.exists(csv_file):
        print(f"\n📄 ANÁLISE CSV:")
        print(f"   • Arquivo: {csv_file}")
        print(f"   • Modo de filtro: {state.get('filter_mode', 'N/A')}")
        
        csv_stats = analyze_csv(csv_file)
        if csv_stats:
            print(f"   • Total analisados: {csv_stats['total']}")
            print(f"   • Usuários imunes: {csv_stats['immune']}")
            print(f"   • Taxa de imunidade: {csv_stats['immunity_rate']:.1f}%")
            
            print(f"\n🏷️ CATEGORIAS PRINCIPAIS:")
            for category, count in list(csv_stats['categories'].items())[:5]:
                print(f"   • {category}: {count}")
    
    # Próximos usuários
    if remaining > 0:
        non_followers = state.get('non_followers', [])
        if non_followers and processed < len(non_followers):
            next_batch = non_followers[processed:processed+5]
            print(f"\n📋 PRÓXIMOS 5 USUÁRIOS:")
            for i, user_id in enumerate(next_batch, 1):
                print(f"   {i}. ID: {user_id}")
    
    print(f"{'='*70}")

def main():
    show_detailed_status()

if __name__ == "__main__":
    main()
