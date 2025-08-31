#!/usr/bin/env python3
"""
Script principal para sistema híbrido de unfollow
Integra extensão Chrome com análise de IA Python
"""

import os
import sys
from dotenv import load_dotenv
from twitter_hybrid_unfollow import TwitterHybridUnfollower

def get_execution_parameters():
    """
    Obtém parâmetros de execução do usuário
    """
    print("\n⚙️ Configurações de execução:")
    
    # Máximo de usuários para analisar
    while True:
        try:
            max_users = input("👥 Máximo de usuários para analisar [500]: ").strip()
            max_users = int(max_users) if max_users else 500
            if max_users > 0:
                break
            print("❌ Deve ser um número positivo")
        except ValueError:
            print("❌ Digite um número válido")
    
    # Máximo de unfollows por execução
    while True:
        try:
            max_unfollows = input("⚡ Máximo de unfollows por execução [20]: ").strip()
            max_unfollows = int(max_unfollows) if max_unfollows else 20
            if max_unfollows >= 0:
                break
            print("❌ Deve ser um número não-negativo (0 para apenas análise)")
        except ValueError:
            print("❌ Digite um número válido")
    
    # Modo headless
    headless_input = input("🖥️ Executar em modo headless (sem interface)? [n]: ").strip().lower()
    headless = headless_input in ['y', 'yes', 's', 'sim']
    
    return {
        'max_users': max_users,
        'max_unfollows': max_unfollows,
        'headless': headless
    }

def main():
    """
    Função principal
    """
    # Carregar variáveis de ambiente
    load_dotenv()
    
    print("="*70)
    print("🤖 TWITTER/X UNFOLLOW HÍBRIDO - EXTENSÃO + IA")
    print("="*70)
    print("🚀 CARACTERÍSTICAS:")
    print("   ✅ Usa extensão Chrome para coleta e unfollow")
    print("   ✅ Análise de IA para proteger devs/pesquisadores")
    print("   ✅ Identifica não-seguidores automaticamente")
    print("   ✅ Gera CSV completo com análise detalhada")
    print("   ✅ Sistema de imunidade conservador")
    print("="*70)
    
    # Verificar credencial da OpenRouter
    openrouter_key = os.getenv('OPENROUTER_API_KEY')
    if not openrouter_key:
        print("❌ ERRO: OPENROUTER_API_KEY não encontrada no arquivo .env")
        print("💡 Configure sua chave da OpenRouter no arquivo .env:")
        print("   OPENROUTER_API_KEY=sua_chave_aqui")
        return
    
    print("✅ Credencial OpenRouter encontrada")
    
    # Avisos importantes
    print("\n⚠️ IMPORTANTE:")
    print("   1. Certifique-se de estar logado no X/Twitter no Chrome")
    print("   2. A extensão será carregada automaticamente")
    print("   3. O processo coleta dados, analisa com IA e faz unfollows seletivos")
    print("   4. Mantenha o navegador visível durante a execução")
    print("   5. O sistema é CONSERVADOR - protege desenvolvedores e pesquisadores")
    
    # Confirmar continuação
    confirm = input("\n🤔 Deseja continuar? [y/N]: ").strip().lower()
    if confirm not in ['y', 'yes', 's', 'sim']:
        print("👋 Operação cancelada pelo usuário")
        return
    
    try:
        # Obter parâmetros
        params = get_execution_parameters()
        
        print(f"\n📋 CONFIGURAÇÕES:")
        print(f"   👥 Max Usuários: {params['max_users']}")
        print(f"   ⚡ Max Unfollows: {params['max_unfollows']}")
        print(f"   🖥️ Headless: {'Sim' if params['headless'] else 'Não'}")
        
        # Confirmar configurações
        confirm = input("\n✅ Confirmar configurações? [Y/n]: ").strip().lower()
        if confirm in ['n', 'no', 'não']:
            print("👋 Operação cancelada pelo usuário")
            return
        
        # Inicializar sistema híbrido
        print("\n🔧 Inicializando sistema híbrido...")
        unfollower = TwitterHybridUnfollower(
            openrouter_api_key=openrouter_key,
            headless=params['headless']
        )
        
        # Executar processo completo
        print("\n🚀 Iniciando processo híbrido...")
        results = unfollower.run_full_process(
            max_users=params['max_users'],
            max_unfollows=params['max_unfollows']
        )
        
        # Mostrar resultados
        print("\n" + "="*70)
        print("📊 RESULTADOS FINAIS")
        print("="*70)
        
        if results['success']:
            print("✅ Processo concluído com sucesso!")
            
            if 'stats' in results and results['stats']:
                stats = results['stats']
                print(f"📈 Estatísticas:")
                print(f"   👥 Usuários coletados: {stats.get('total_collected', 0)}")
                print(f"   🤖 Analisados pela IA: {stats.get('total_analyzed', 0)}")
                print(f"   🛡️ Protegidos (imunes): {stats.get('immune_count', 0)}")
                print(f"   ✅ Elegíveis para unfollow: {stats.get('eligible_count', 0)}")
                
                if 'unfollow_results' in stats and stats['unfollow_results']:
                    unfollow = stats['unfollow_results']
                    print(f"   ⚡ Unfollows realizados: {unfollow.get('successful', 0)}")
                    print(f"   ❌ Unfollows falharam: {unfollow.get('failed', 0)}")
                    
                    # Mostrar detalhes por categoria
                    if 'details' in unfollow:
                        categories = {}
                        for detail in unfollow['details']:
                            cat = detail.get('category', 'OTHER')
                            if cat not in categories:
                                categories[cat] = {'success': 0, 'failed': 0}
                            
                            if detail['status'] == 'success':
                                categories[cat]['success'] += 1
                            else:
                                categories[cat]['failed'] += 1
                        
                        print(f"   📊 Por categoria:")
                        for cat, counts in categories.items():
                            total = counts['success'] + counts['failed']
                            print(f"      {cat}: {counts['success']}/{total} sucessos")
            
            if results.get('csv_file'):
                print(f"💾 Análise completa salva em: {results['csv_file']}")
                
        else:
            print(f"❌ Processo falhou: {results['message']}")
        
        print("="*70)
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Processo interrompido pelo usuário")
        print("💾 Dados podem ter sido salvos parcialmente")
        
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        print("💾 Verifique os logs para mais detalhes")
        
    finally:
        print("\n👋 Finalizando...")

if __name__ == "__main__":
    main()
