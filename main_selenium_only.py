#!/usr/bin/env python3
"""
Script principal para sistema de unfollow usando apenas Selenium
Não requer API do Twitter - funciona apenas com navegador
"""

import os
import sys
from dotenv import load_dotenv
from twitter_selenium_only import TwitterSeleniumUnfollower

def choose_browser():
    """
    Permite ao usuário escolher o navegador
    """
    print("\n🌐 Escolha o navegador:")
    print("1. Chrome (padrão)")
    print("2. Brave")
    
    while True:
        choice = input("\nDigite sua escolha (1-2) [1]: ").strip()
        
        if choice == "" or choice == "1":
            return "chrome"
        elif choice == "2":
            return "brave"
        else:
            print("❌ Opção inválida. Tente novamente.")

def get_execution_parameters():
    """
    Obtém parâmetros de execução do usuário
    """
    print("\n⚙️ Configurações de execução:")
    
    # Máximo de following para coletar
    while True:
        try:
            max_following = input("📤 Máximo de following para coletar [5000]: ").strip()
            max_following = int(max_following) if max_following else 5000
            if max_following > 0:
                break
            print("❌ Deve ser um número positivo")
        except ValueError:
            print("❌ Digite um número válido")
    
    # Máximo de followers para coletar
    while True:
        try:
            max_followers = input("📥 Máximo de followers para coletar [5000]: ").strip()
            max_followers = int(max_followers) if max_followers else 5000
            if max_followers > 0:
                break
            print("❌ Deve ser um número positivo")
        except ValueError:
            print("❌ Digite um número válido")
    
    # Máximo de unfollows por execução
    while True:
        try:
            max_unfollows = input("⚡ Máximo de unfollows por execução [20]: ").strip()
            max_unfollows = int(max_unfollows) if max_unfollows else 20
            if max_unfollows > 0:
                break
            print("❌ Deve ser um número positivo")
        except ValueError:
            print("❌ Digite um número válido")
    
    # Delay entre unfollows
    while True:
        try:
            delay = input("⏳ Delay entre unfollows em segundos [5.0]: ").strip()
            delay = float(delay) if delay else 5.0
            if delay >= 1.0:
                break
            print("❌ Delay deve ser pelo menos 1.0 segundo")
        except ValueError:
            print("❌ Digite um número válido")
    
    # Modo headless
    headless_input = input("🖥️ Executar em modo headless (sem interface)? [n]: ").strip().lower()
    headless = headless_input in ['y', 'yes', 's', 'sim']
    
    return {
        'max_following': max_following,
        'max_followers': max_followers,
        'max_unfollows': max_unfollows,
        'delay_between': delay,
        'headless': headless
    }

def main():
    """
    Função principal
    """
    # Carregar variáveis de ambiente
    load_dotenv()
    
    print("="*70)
    print("🤖 TWITTER/X UNFOLLOW AUTOMÁTICO - SELENIUM ONLY")
    print("="*70)
    print("🚀 CARACTERÍSTICAS:")
    print("   ✅ Não requer API do Twitter")
    print("   ✅ Funciona apenas com navegador")
    print("   ✅ Análise de IA para proteger devs/pesquisadores")
    print("   ✅ Coleta dados via scraping")
    print("   ✅ Unfollow automático via Selenium")
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
    print("   1. Certifique-se de estar logado no Twitter/X no seu navegador")
    print("   2. Feche outras instâncias do navegador antes de continuar")
    print("   3. O processo pode demorar dependendo do tamanho das suas listas")
    print("   4. Mantenha o navegador visível durante a execução (se não for headless)")
    
    # Confirmar continuação
    confirm = input("\n🤔 Deseja continuar? [y/N]: ").strip().lower()
    if confirm not in ['y', 'yes', 's', 'sim']:
        print("👋 Operação cancelada pelo usuário")
        return
    
    try:
        # Escolher navegador
        browser = choose_browser()
        print(f"✅ Navegador selecionado: {browser.title()}")
        
        # Obter parâmetros
        params = get_execution_parameters()
        
        print(f"\n📋 CONFIGURAÇÕES:")
        print(f"   🌐 Navegador: {browser.title()}")
        print(f"   📤 Max Following: {params['max_following']}")
        print(f"   📥 Max Followers: {params['max_followers']}")
        print(f"   ⚡ Max Unfollows: {params['max_unfollows']}")
        print(f"   ⏳ Delay: {params['delay_between']}s")
        print(f"   🖥️ Headless: {'Sim' if params['headless'] else 'Não'}")
        
        # Confirmar configurações
        confirm = input("\n✅ Confirmar configurações? [Y/n]: ").strip().lower()
        if confirm in ['n', 'no', 'não']:
            print("👋 Operação cancelada pelo usuário")
            return
        
        # Inicializar sistema
        print("\n🔧 Inicializando sistema...")
        unfollower = TwitterSeleniumUnfollower(
            openrouter_api_key=openrouter_key,
            headless=params['headless'],
            browser=browser
        )
        
        # Executar processo completo
        print("\n🚀 Iniciando processo...")
        results = unfollower.run_full_process(
            max_following=params['max_following'],
            max_followers=params['max_followers'],
            max_unfollows=params['max_unfollows'],
            delay_between=params['delay_between']
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
                print(f"   📤 Following coletados: {stats.get('following_count', 0)}")
                print(f"   📥 Followers coletados: {stats.get('followers_count', 0)}")
                print(f"   🎯 Não-seguidores: {stats.get('non_followers_count', 0)}")
                print(f"   🤖 Analisados pela IA: {stats.get('analyzed_count', 0)}")
                print(f"   ✅ Elegíveis para unfollow: {stats.get('eligible_count', 0)}")
                
                if 'unfollow_results' in stats:
                    unfollow = stats['unfollow_results']
                    print(f"   ⚡ Unfollows realizados: {unfollow.get('success_count', 0)}")
                    print(f"   ❌ Unfollows falharam: {unfollow.get('failed_count', 0)}")
            
            if results.get('csv_file'):
                print(f"💾 Análise salva em: {results['csv_file']}")
                
        else:
            print(f"❌ Processo falhou: {results['message']}")
        
        print("="*70)
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Processo interrompido pelo usuário")
        print("💾 Estado pode ter sido salvo em selenium_unfollow_state.json")
        
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        print("💾 Verifique os logs para mais detalhes")
        
    finally:
        print("\n👋 Finalizando...")

if __name__ == "__main__":
    main()
