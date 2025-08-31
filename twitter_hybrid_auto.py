#!/usr/bin/env python3
"""
Script automático para sistema híbrido de unfollow
Executa periodicamente com configurações otimizadas
"""

import time
import logging
import os
import schedule
from datetime import datetime
from dotenv import load_dotenv
from twitter_hybrid_unfollow import TwitterHybridUnfollower

# Carregar variáveis de ambiente
load_dotenv()

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('twitter_hybrid_auto.log'),
        logging.StreamHandler()
    ]
)

def run_hybrid_cycle():
    """
    Executa um ciclo de unfollow híbrido automático
    """
    try:
        logging.info("🔄 Iniciando ciclo híbrido automático...")

        # Carregar credencial OpenRouter
        openrouter_key = os.getenv('OPENROUTER_API_KEY')
        if not openrouter_key:
            logging.error("❌ OPENROUTER_API_KEY não encontrada")
            return False

        # Inicializar sistema híbrido
        unfollower = TwitterHybridUnfollower(
            openrouter_api_key=openrouter_key,
            headless=True  # Modo headless para execução automática
        )

        # Executar processo com limites para ciclo automático
        results = unfollower.run_full_process(
            max_users=200,    # Processar menos usuários por ciclo
            max_unfollows=15  # 15 unfollows por ciclo
        )

        if results['success']:
            logging.info("✅ Ciclo híbrido concluído com sucesso")
            
            if 'stats' in results:
                stats = results['stats']
                logging.info(f"📊 Estatísticas do ciclo:")
                logging.info(f"   👥 Coletados: {stats.get('total_collected', 0)}")
                logging.info(f"   🤖 Analisados: {stats.get('total_analyzed', 0)}")
                logging.info(f"   🛡️ Imunes: {stats.get('immune_count', 0)}")
                logging.info(f"   ✅ Elegíveis: {stats.get('eligible_count', 0)}")
                
                if 'unfollow_results' in stats and stats['unfollow_results']:
                    unfollow_stats = stats['unfollow_results']
                    logging.info(f"   ⚡ Unfollows: {unfollow_stats.get('successful', 0)}")
                    
                    # Log das categorias unfollowed
                    if 'details' in unfollow_stats:
                        categories = {}
                        for detail in unfollow_stats['details']:
                            if detail['status'] == 'success':
                                cat = detail.get('category', 'OTHER')
                                categories[cat] = categories.get(cat, 0) + 1
                        
                        if categories:
                            logging.info(f"   📊 Unfollows por categoria: {categories}")
            
            return True
        else:
            logging.error(f"❌ Ciclo falhou: {results['message']}")
            return False

    except Exception as e:
        logging.error(f"❌ Erro no ciclo híbrido: {e}")
        return False

def main():
    """
    Executa a sequência automática completa híbrida
    """
    # Verificar credencial OpenRouter
    openrouter_key = os.getenv('OPENROUTER_API_KEY')
    if not openrouter_key:
        print("❌ ERRO: OPENROUTER_API_KEY não encontrada no arquivo .env")
        print("💡 Configure sua chave da OpenRouter no arquivo .env:")
        print("   OPENROUTER_API_KEY=sua_chave_aqui")
        return

    print(f"\n{'='*70}")
    print(f"🤖 TWITTER/X UNFOLLOW HÍBRIDO AUTOMÁTICO")
    print(f"{'='*70}")
    print("🚀 MODO AUTOMÁTICO HÍBRIDO:")
    print("   • Executa a cada 25 minutos")
    print("   • 15 unfollows por ciclo")
    print("   • Usa extensão Chrome + análise de IA")
    print("   • Análise de IA para proteger devs/pesquisadores")
    print("   • Identifica não-seguidores automaticamente")
    print("   • Pressione Ctrl+C para parar")
    print(f"{'='*70}")

    # Escolher modo
    print("\n🔧 Escolha o modo de execução:")
    print("1. 🔄 Automático (a cada 25 minutos)")
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
            print("\n⚡ MODO AUTOMÁTICO HÍBRIDO ATIVADO")
            print("🔄 Executando primeiro ciclo...")

            # Executar primeiro ciclo
            success = run_hybrid_cycle()
            if success:
                # Agendar execuções automáticas
                schedule.every(25).minutes.do(run_hybrid_cycle)

                print("\n⏰ Sistema agendado para executar a cada 25 minutos")
                print("🛑 Pressione Ctrl+C para parar")

                while True:
                    schedule.run_pending()
                    time.sleep(60)  # Verificar a cada minuto
            else:
                print("❌ Primeiro ciclo falhou. Verifique os logs.")

        else:  # single execution
            print("\n🚀 MODO EXECUÇÃO ÚNICA HÍBRIDA")

            # Inicializar sistema híbrido
            unfollower = TwitterHybridUnfollower(
                openrouter_api_key=openrouter_key,
                headless=False  # Interface visível para execução única
            )

            # Executar processo completo
            results = unfollower.run_full_process(
                max_users=1000,   # Mais usuários em execução única
                max_unfollows=50  # Mais unfollows em execução única
            )

            # Mostrar resultados
            if results['success']:
                print("\n✅ Processo híbrido concluído com sucesso!")
                
                if 'stats' in results:
                    stats = results['stats']
                    print(f"📊 Estatísticas:")
                    print(f"   👥 Coletados: {stats.get('total_collected', 0)}")
                    print(f"   🤖 Analisados: {stats.get('total_analyzed', 0)}")
                    print(f"   🛡️ Imunes: {stats.get('immune_count', 0)}")
                    print(f"   ✅ Elegíveis: {stats.get('eligible_count', 0)}")
                    
                    if 'unfollow_results' in stats and stats['unfollow_results']:
                        unfollow_stats = stats['unfollow_results']
                        print(f"   ⚡ Unfollows: {unfollow_stats.get('successful', 0)}")
                        print(f"   ❌ Falhas: {unfollow_stats.get('failed', 0)}")
                        
                        # Mostrar estatísticas por categoria
                        if 'details' in unfollow_stats:
                            categories = {}
                            for detail in unfollow_stats['details']:
                                cat = detail.get('category', 'OTHER')
                                status = detail['status']
                                
                                if cat not in categories:
                                    categories[cat] = {'success': 0, 'failed': 0, 'total': 0}
                                
                                categories[cat]['total'] += 1
                                if status == 'success':
                                    categories[cat]['success'] += 1
                                else:
                                    categories[cat]['failed'] += 1
                            
                            print(f"   📊 Por categoria:")
                            for cat, counts in categories.items():
                                success_rate = (counts['success'] / counts['total'] * 100) if counts['total'] > 0 else 0
                                print(f"      {cat}: {counts['success']}/{counts['total']} ({success_rate:.1f}%)")
                
                if results.get('csv_file'):
                    print(f"💾 Análise completa salva em: {results['csv_file']}")
            else:
                print(f"❌ Processo falhou: {results['message']}")

    except KeyboardInterrupt:
        print("\n\n🛑 SISTEMA HÍBRIDO INTERROMPIDO PELO USUÁRIO")
        print("   O progresso foi salvo automaticamente.")
        print("   Execute novamente para continuar de onde parou.")
    except Exception as e:
        logging.error(f"Erro crítico: {e}")
        print(f"\n❌ ERRO CRÍTICO: {e}")
        print("   Verifique o arquivo de log para mais detalhes.")

if __name__ == "__main__":
    main()
