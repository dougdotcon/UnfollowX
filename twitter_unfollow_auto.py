#!/usr/bin/env python3
"""
Script otimizado para unfollow automático no Twitter/X
Sequência automática: Extrair → Analisar → Filtrar → Unfollow
"""

import time
import logging
import os
from dotenv import load_dotenv
from twitter_unfollow import TwitterUnfollower

# Carregar variáveis de ambiente
load_dotenv()

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('twitter_unfollow_auto.log'),
        logging.StreamHandler()
    ]
)

def main():
    """
    Executa a sequência automática completa de unfollow
    """
    # Carregar credenciais das variáveis de ambiente
    API_KEY = os.getenv('TWITTER_API_KEY')
    API_SECRET = os.getenv('TWITTER_API_SECRET')
    ACCESS_TOKEN = os.getenv('TWITTER_ACCESS_TOKEN')
    ACCESS_TOKEN_SECRET = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
    OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')

    # Verificar se todas as credenciais estão presentes
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
        print("💡 Execute: cp .env.example .env")
        print("📝 Depois edite o arquivo .env com suas credenciais")
        return

    try:
        print(f"\n{'='*70}")
        print(f"🤖 TWITTER/X UNFOLLOW AUTOMÁTICO COM IA")
        print(f"{'='*70}")
        print("🚀 SEQUÊNCIA AUTOMÁTICA:")
        print("   1. 📋 Extrair listas (following/followers)")
        print("   2. 🤖 Analisar perfis com IA (OpenRouter)")
        print("   3. 💾 Salvar análise em CSV")
        print("   4. 🛡️ Filtrar usuários imunes (devs, pesquisadores, etc.)")
        print("   5. ⚡ Executar unfollow automático (20 a cada 20 min)")
        print(f"{'='*70}")

        # Inicializar sistema
        print("\n🔧 Inicializando sistema...")
        unfollower = TwitterUnfollower(API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET, OPENROUTER_API_KEY)
        print(f"✅ Autenticado como: @{unfollower.username}")

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
