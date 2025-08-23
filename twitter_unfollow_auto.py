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

        # ETAPA 1: Extrair listas
        print(f"\n📋 ETAPA 1/5: Extraindo listas do Twitter...")
        following = unfollower.get_following()
        followers = unfollower.get_followers()
        non_followers = unfollower.find_non_followers(following, followers)

        print(f"   📊 Estatísticas:")
        print(f"      • Você segue: {len(following)} usuários")
        print(f"      • Te seguem: {len(followers)} usuários")
        print(f"      • Não te seguem de volta: {len(non_followers)} usuários")

        if not non_followers:
            if len(following) == 0 and len(followers) == 0:
                print("\n❌ LIMITAÇÃO DA API DETECTADA!")
                print("   Sua conta Twitter API tem acesso limitado e não pode acessar")
                print("   os endpoints de followers/following.")
                print("\n💡 SOLUÇÕES DISPONÍVEIS:")
                print("   1. 💰 Upgrade para Twitter API Pro ($100/mês)")
                print("   2. 📁 Usar entrada manual de dados:")
                print("      • Exporte suas listas manualmente do Twitter")
                print("      • Salve como CSV com colunas: user_id, username")
                print("      • Use o modo manual do script")
                print("\n📖 INSTRUÇÕES PARA MODO MANUAL:")
                print("   python twitter_unfollow.py --manual")
                print("\n📝 FORMATO DO CSV:")
                print("   Crie dois arquivos CSV:")
                print("   • following.csv - usuários que você segue")
                print("   • followers.csv - usuários que te seguem")
                print("   Formato: user_id,username (uma linha por usuário)")
                return
            else:
                print("\n🎉 RESULTADO: Todos os usuários que você segue também te seguem de volta!")
                print("   Nenhum unfollow necessário. Sistema finalizado.")
                return

        # ETAPA 2-3: Analisar perfis e salvar CSV
        print(f"\n🤖 ETAPA 2-3/5: Analisando {len(non_followers)} perfis com IA...")
        print("   ⏳ Este processo pode demorar alguns minutos...")
        
        csv_filename = unfollower.save_non_followers_to_csv(non_followers)

        if not csv_filename:
            print("❌ ERRO: Falha ao salvar análise em CSV. Abortando processo.")
            return

        print(f"   ✅ Análise salva em: {csv_filename}")

        # ETAPA 4: Filtrar usuários imunes
        print(f"\n🛡️ ETAPA 4/5: Aplicando filtros de imunidade...")
        filter_config = unfollower.create_smart_filter_config(aggressive=False)
        filtered_non_followers = unfollower.load_non_followers_from_csv(csv_filename, filter_config)

        # Salvar estado para sistema automático
        state = unfollower.load_state()
        state['non_followers'] = filtered_non_followers
        state['total_to_process'] = len(filtered_non_followers)
        state['processed_count'] = 0
        state['last_update'] = time.strftime('%Y-%m-%d %H:%M:%S')
        state['csv_filename'] = csv_filename
        state['filter_mode'] = 'normal'
        unfollower.save_state(state)

        print(f"   ✅ Usuários filtrados para unfollow: {len(filtered_non_followers)}")

        if not filtered_non_followers:
            print("\n🛡️ RESULTADO: Todos os usuários são imunes!")
            print("   Nenhum unfollow será realizado. Sistema finalizado.")
            return

        # ETAPA 5: Iniciar sistema automático
        print(f"\n⚡ ETAPA 5/5: Configurando sistema automático...")
        print(f"   📊 Arquivo de análise: {csv_filename}")
        print(f"   ⏰ Frequência: 20 unfollows a cada 20 minutos")
        print(f"   🛑 Para parar: Pressione Ctrl+C")
        print(f"   📈 Progresso será salvo automaticamente")
        
        # Estimativa de tempo
        hours_estimated = len(filtered_non_followers) / 60  # 20 unfollows a cada 20 min = 60 por hora
        print(f"   ⏱️ Tempo estimado total: {hours_estimated:.1f} horas")
        
        print(f"\n{'='*70}")
        print("🚨 ATENÇÃO: O sistema iniciará em 10 segundos...")
        print("   Pressione Ctrl+C agora se quiser cancelar")
        print(f"{'='*70}")

        # Countdown
        for i in range(10, 0, -1):
            print(f"   Iniciando em {i}s...", end='\r')
            time.sleep(1)

        print("\n🚀 INICIANDO SISTEMA AUTOMÁTICO...")
        print(f"{'='*70}")

        # Iniciar sistema automático
        unfollower.start_scheduled_unfollows(use_existing_csv=True)

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
