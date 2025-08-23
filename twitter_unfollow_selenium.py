#!/usr/bin/env python3
"""
Script principal para unfollow automático usando Selenium
Contorna limitações da API do Twitter/X
"""

import time
import logging
import os
from dotenv import load_dotenv
from twitter_selenium import TwitterSeleniumScraper
from twitter_unfollow import TwitterUnfollower

# Carregar variáveis de ambiente
load_dotenv()

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('twitter_unfollow_selenium.log'),
        logging.StreamHandler()
    ]
)

def choose_browser():
    """
    Permite ao usuário escolher o navegador
    """
    print("\n🌐 ESCOLHA DO NAVEGADOR")
    print("   Qual navegador você quer usar (deve estar logado no Twitter/X)?")
    print("   1. Chrome (padrão)")
    print("   2. Brave")

    choice = input("   Escolha (1 ou 2): ").strip()

    if choice == "2":
        return "brave"
    else:
        return "chrome"

def main():
    """
    Executa a sequência automática completa usando Selenium
    """
    # Carregar credenciais da API (para unfollow e análise IA)
    API_KEY = os.getenv('TWITTER_API_KEY')
    API_SECRET = os.getenv('TWITTER_API_SECRET')
    ACCESS_TOKEN = os.getenv('TWITTER_ACCESS_TOKEN')
    ACCESS_TOKEN_SECRET = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
    OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')

    # Verificar credenciais da API (necessárias para unfollow)
    required_vars = {
        'TWITTER_API_KEY': API_KEY,
        'TWITTER_API_SECRET': API_SECRET,
        'TWITTER_ACCESS_TOKEN': ACCESS_TOKEN,
        'TWITTER_ACCESS_TOKEN_SECRET': ACCESS_TOKEN_SECRET,
        'OPENROUTER_API_KEY': OPENROUTER_API_KEY
    }

    missing_vars = [var for var, value in required_vars.items() if not value]
    if missing_vars:
        print(f"❌ ERRO: Variáveis de ambiente não encontradas: {', '.join(missing_vars)}")
        print("📝 Crie um arquivo .env baseado no .env.example")
        print("💡 Mesmo usando Selenium, ainda precisamos da API para fazer unfollow")
        return

    try:
        print(f"\n{'='*70}")
        print(f"🤖 TWITTER/X UNFOLLOW AUTOMÁTICO COM SELENIUM + IA")
        print(f"{'='*70}")
        print("🚀 SEQUÊNCIA AUTOMÁTICA:")
        print("   1. 🌐 Coletar listas via Selenium (usa navegador já logado)")
        print("   2. 🤖 Analisar perfis com IA (OpenRouter)")
        print("   3. 💾 Salvar análise em CSV")
        print("   4. 🛡️ Filtrar usuários imunes")
        print("   5. ⚡ Executar unfollow via API")
        print(f"{'='*70}")

        # Escolher navegador
        browser_choice = choose_browser()

        # ETAPA 1: Coletar dados via Selenium
        print(f"\n🌐 ETAPA 1/5: Coletando dados via Selenium...")
        print(f"   📋 IMPORTANTE: Certifique-se de que está logado no Twitter/X no seu {browser_choice.title()}")

        scraper = TwitterSeleniumScraper(
            headless=False,
            use_existing_profile=True,
            browser=browser_choice
        )
        
        if not scraper.setup_driver():
            print("❌ Erro ao configurar navegador")
            return

        print("� Verificando se está logado no Twitter/X...")
        if not scraper.check_login_status():
            print("❌ Não está logado - faça login manualmente no navegador primeiro")
            print("💡 Abra o Twitter/X no seu navegador, faça login e execute o script novamente")
            scraper.close()
            return
        
        print("📊 Obtendo contagens...")
        following_count = scraper.get_following_count()
        followers_count = scraper.get_followers_count()
        
        print(f"   • Você segue: {following_count} usuários")
        print(f"   • Te seguem: {followers_count} usuários")
        
        # Definir limite de coleta baseado no tamanho das listas
        max_collect = min(2000, max(following_count, followers_count))
        
        print(f"\n📋 Coletando listas (máximo {max_collect} usuários cada)...")
        print("   ⏳ Este processo pode demorar alguns minutos...")
        
        # Coletar following
        following_data = scraper.get_following_list(max_users=max_collect)
        scraper.save_to_csv(following_data, 'following_selenium.csv')
        
        # Coletar followers
        followers_data = scraper.get_followers_list(max_users=max_collect)
        scraper.save_to_csv(followers_data, 'followers_selenium.csv')
        
        # Fechar navegador
        scraper.close()
        
        # Converter para formato compatível com o sistema existente
        following_usernames = {user['username'] for user in following_data}
        followers_usernames = {user['username'] for user in followers_data}
        
        # Encontrar quem não te segue de volta
        non_followers = following_usernames - followers_usernames
        
        print(f"\n📊 RESULTADOS DA COLETA:")
        print(f"   • Coletados {len(following_data)} usuários que você segue")
        print(f"   • Coletados {len(followers_data)} seus seguidores")
        print(f"   • {len(non_followers)} não te seguem de volta")
        
        if not non_followers:
            print("\n🎉 RESULTADO: Todos os usuários coletados te seguem de volta!")
            print("   Nenhum unfollow necessário. Sistema finalizado.")
            return
        
        # ETAPA 2-5: Usar sistema existente para análise e unfollow
        print(f"\n🤖 ETAPA 2-5/5: Processando com sistema de IA...")
        
        # Inicializar sistema de unfollow
        unfollower = TwitterUnfollower(API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET, OPENROUTER_API_KEY)
        print(f"✅ Sistema de unfollow autenticado como: @{unfollower.username}")
        
        # Converter usernames para user_ids (necessário para a API)
        print("🔄 Convertendo usernames para user_ids...")
        user_ids = unfollower.get_user_ids_from_usernames(list(non_followers))
        
        if not user_ids:
            print("❌ Erro ao converter usernames para IDs")
            return
        
        print(f"✅ Convertidos {len(user_ids)} usernames para IDs")
        
        # Continuar com o processo normal de análise e unfollow
        csv_filename = unfollower.save_non_followers_to_csv(user_ids)
        
        if not csv_filename:
            print("❌ ERRO: Falha ao salvar análise em CSV")
            return
        
        print(f"✅ Análise salva em: {csv_filename}")
        
        # Aplicar filtros de imunidade
        print(f"\n🛡️ Aplicando filtros de imunidade...")
        filter_config = unfollower.create_smart_filter_config(aggressive=False)
        filtered_non_followers = unfollower.load_non_followers_from_csv(csv_filename, filter_config)
        
        print(f"✅ Usuários filtrados para unfollow: {len(filtered_non_followers)}")
        
        if not filtered_non_followers:
            print("\n🛡️ RESULTADO: Todos os usuários são imunes!")
            print("   Nenhum unfollow será realizado.")
            return
        
        # Salvar estado e iniciar sistema automático
        state = unfollower.load_state()
        state['non_followers'] = filtered_non_followers
        state['total_to_process'] = len(filtered_non_followers)
        state['processed_count'] = 0
        state['last_update'] = time.strftime('%Y-%m-%d %H:%M:%S')
        state['csv_filename'] = csv_filename
        state['filter_mode'] = 'selenium'
        unfollower.save_state(state)
        
        # Estimativa de tempo
        hours_estimated = len(filtered_non_followers) / 60  # 20 unfollows a cada 20 min = 60 por hora
        print(f"\n⚡ SISTEMA AUTOMÁTICO CONFIGURADO:")
        print(f"   📊 Arquivo de análise: {csv_filename}")
        print(f"   ⏰ Frequência: 20 unfollows a cada 20 minutos")
        print(f"   ⏱️ Tempo estimado total: {hours_estimated:.1f} horas")
        print(f"   🛑 Para parar: Pressione Ctrl+C")
        
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
