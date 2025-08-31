#!/usr/bin/env python3
"""
Script otimizado para unfollow automático no Twitter/X - SELENIUM ONLY
Sequência automática: Extrair → Analisar → Filtrar → Unfollow
Não requer API do Twitter - funciona apenas com navegador
"""

import time
import logging
import os
import schedule
from datetime import datetime
from dotenv import load_dotenv
from twitter_selenium_only import TwitterSeleniumUnfollower

# Carregar variáveis de ambiente
load_dotenv()

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('twitter_selenium_auto.log'),
        logging.StreamHandler()
    ]
)

def run_unfollow_cycle():
    """
    Executa um ciclo de unfollow automático usando Selenium
    """
    try:
        logging.info("🔄 Iniciando ciclo de unfollow automático (Selenium)...")

        # Carregar credencial OpenRouter
        openrouter_key = os.getenv('OPENROUTER_API_KEY')
        if not openrouter_key:
            logging.error("❌ OPENROUTER_API_KEY não encontrada")
            return False

        # Inicializar sistema Selenium
        unfollower = TwitterSeleniumUnfollower(
            openrouter_api_key=openrouter_key,
            headless=True,  # Modo headless para execução automática
            browser="chrome"
        )

        # Executar processo com limites para ciclo automático
        results = unfollower.run_full_process(
            max_following=1000,  # Processar em lotes menores
            max_followers=1000,
            max_unfollows=20,    # 20 unfollows por ciclo
            delay_between=3.0    # 3 segundos entre unfollows
        )

        if results['success']:
            logging.info("✅ Ciclo concluído com sucesso")
            if 'unfollow_results' in results.get('stats', {}):
                unfollow_stats = results['stats']['unfollow_results']
                logging.info(f"⚡ Unfollows realizados: {unfollow_stats.get('success_count', 0)}")
            return True
        else:
            logging.error(f"❌ Ciclo falhou: {results['message']}")
            return False

    except Exception as e:
        logging.error(f"❌ Erro no ciclo: {e}")
        return False

def main():
    """
    Executa a sequência automática completa de unfollow usando Selenium
    """
    # Verificar credencial OpenRouter
    openrouter_key = os.getenv('OPENROUTER_API_KEY')
    if not openrouter_key:
        print("❌ ERRO: OPENROUTER_API_KEY não encontrada no arquivo .env")
        print("💡 Configure sua chave da OpenRouter no arquivo .env:")
        print("   OPENROUTER_API_KEY=sua_chave_aqui")
        return

    print(f"\n{'='*70}")
    print(f"🤖 TWITTER/X UNFOLLOW AUTOMÁTICO - SELENIUM ONLY")
    print(f"{'='*70}")
    print("🚀 MODO AUTOMÁTICO:")
    print("   • Executa a cada 20 minutos")
    print("   • 20 unfollows por ciclo")
    print("   • Análise de IA para proteger devs/pesquisadores")
    print("   • Funciona apenas com navegador (sem API)")
    print("   • Pressione Ctrl+C para parar")
    print(f"{'='*70}")

    # Escolher modo
    print("\n🔧 Escolha o modo de execução:")
    print("1. 🔄 Automático (a cada 20 minutos)")
    print("2. 🚀 Execução única completa")

    while True:
        choice = input("\nDigite sua escolha (1-2) [1]: ").strip()
        if choice == "" or choice == "1":
            mode = "automatic"
            break
        elif choice == "2":
            mode = "single"
            break
        else:
            print("❌ Opção inválida. Tente novamente.")

    try:
        if mode == "automatic":
            print("\n⚡ MODO AUTOMÁTICO ATIVADO")
            print("🔄 Executando primeiro ciclo...")

            # Executar primeiro ciclo
            run_unfollow_cycle()

            # Agendar execuções automáticas
            schedule.every(20).minutes.do(run_unfollow_cycle)

            print("\n⏰ Sistema agendado para executar a cada 20 minutos")
            print("🛑 Pressione Ctrl+C para parar")

            while True:
                schedule.run_pending()
                time.sleep(60)  # Verificar a cada minuto

        else:  # single execution
            print("\n🚀 MODO EXECUÇÃO ÚNICA")

            # Inicializar sistema Selenium
            unfollower = TwitterSeleniumUnfollower(
                openrouter_api_key=openrouter_key,
                headless=False,  # Interface visível para execução única
                browser="chrome"
            )

            # Executar processo completo
            results = unfollower.run_full_process(
                max_following=6000,  # Suporte para suas 5.268 pessoas
                max_followers=6000,
                max_unfollows=50,    # Mais unfollows em execução única
                delay_between=3.0
            )

            # Mostrar resultados
            if results['success']:
                print("\n✅ Processo concluído com sucesso!")
                if 'stats' in results:
                    stats = results['stats']
                    print(f"📊 Estatísticas:")
                    print(f"   📤 Following: {stats.get('following_count', 0)}")
                    print(f"   📥 Followers: {stats.get('followers_count', 0)}")
                    print(f"   🎯 Não-seguidores: {stats.get('non_followers_count', 0)}")
                    print(f"   🤖 Analisados: {stats.get('analyzed_count', 0)}")
                    print(f"   ⚡ Unfollows: {stats.get('unfollow_results', {}).get('success_count', 0)}")
                if results.get('csv_file'):
                    print(f"💾 Análise salva em: {results['csv_file']}")
            else:
                print(f"❌ Processo falhou: {results['message']}")

    except KeyboardInterrupt:
        print("\n\n🛑 SISTEMA INTERROMPIDO PELO USUÁRIO")
        print("   O progresso foi salvo automaticamente.")
        print("   Execute novamente para continuar de onde parou.")
    except Exception as e:
        logging.error(f"Erro crítico: {e}")
        print(f"\n❌ ERRO CRÍTICO: {e}")
        print("   Verifique o arquivo de log para mais detalhes.")

if __name__ == "__main__":
    main()
