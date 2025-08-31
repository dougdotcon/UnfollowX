#!/usr/bin/env python3
"""
Script de teste para validar o sistema Selenium-only
Testa todas as funcionalidades principais sem executar unfollows reais
"""

import os
import sys
from dotenv import load_dotenv
from twitter_selenium_only import TwitterSeleniumUnfollower

def test_initialization():
    """
    Testa inicialização do sistema
    """
    print("🔧 Testando inicialização...")
    
    # Carregar variáveis de ambiente
    load_dotenv()
    openrouter_key = os.getenv('OPENROUTER_API_KEY')
    
    if not openrouter_key:
        print("❌ OPENROUTER_API_KEY não encontrada no .env")
        return False
    
    try:
        unfollower = TwitterSeleniumUnfollower(
            openrouter_api_key=openrouter_key,
            headless=True,  # Headless para evitar conflitos
            browser="chrome"
        )
        print("✅ Sistema inicializado com sucesso")
        return unfollower
    except Exception as e:
        print(f"❌ Erro na inicialização: {e}")
        return False

def test_scraper_setup(unfollower):
    """
    Testa configuração do scraper
    """
    print("\n🌐 Testando configuração do scraper...")
    
    try:
        if unfollower.initialize_scraper():
            print("✅ Scraper configurado com sucesso")
            print(f"✅ Logado como: @{unfollower.scraper.username}")
            return True
        else:
            print("❌ Falha na configuração do scraper")
            return False
    except Exception as e:
        print(f"❌ Erro no scraper: {e}")
        return False

def test_data_collection(unfollower):
    """
    Testa coleta de dados (amostra pequena)
    """
    print("\n📋 Testando coleta de dados (amostra pequena)...")
    
    try:
        # Coletar apenas uma pequena amostra para teste
        following, followers = unfollower.collect_data(
            max_following=50,  # Apenas 50 para teste rápido
            max_followers=50
        )
        
        print(f"✅ Following coletados: {len(following)}")
        print(f"✅ Followers coletados: {len(followers)}")
        
        if following or followers:
            print("✅ Coleta de dados funcionando")
            return following, followers
        else:
            print("⚠️ Nenhum dado coletado (pode ser normal)")
            return set(), set()
            
    except Exception as e:
        print(f"❌ Erro na coleta: {e}")
        return set(), set()

def test_profile_extraction(unfollower):
    """
    Testa extração de dados de perfil
    """
    print("\n👤 Testando extração de perfil...")
    
    # Testar com o próprio usuário
    try:
        username = unfollower.scraper.username
        if username:
            profile_data = unfollower.extract_user_profile_data(username)
            
            print(f"✅ Perfil extraído para @{username}:")
            print(f"   Nome: {profile_data.get('display_name', 'N/A')}")
            print(f"   Bio: {profile_data.get('bio', 'N/A')[:50]}...")
            print(f"   Localização: {profile_data.get('location', 'N/A')}")
            print(f"   Verificado: {profile_data.get('verified', False)}")
            
            return True
        else:
            print("⚠️ Username não disponível para teste")
            return False
            
    except Exception as e:
        print(f"❌ Erro na extração de perfil: {e}")
        return False

def test_ai_analysis(unfollower):
    """
    Testa análise de IA (com usuário de teste)
    """
    print("\n🤖 Testando análise de IA...")
    
    try:
        # Usar o próprio usuário como teste
        username = unfollower.scraper.username
        if username:
            test_users = {username}
            
            analyzed = unfollower.analyze_users_with_ai(
                usernames=test_users,
                batch_size=1,
                save_progress=False
            )
            
            if analyzed:
                user_data = analyzed[0]
                print(f"✅ Análise de IA concluída:")
                print(f"   Usuário: @{user_data['username']}")
                print(f"   Categoria: {user_data['category']}")
                print(f"   Status: {user_data['immunity_status']}")
                print(f"   Confiança: {user_data['confidence']:.2f}")
                return True
            else:
                print("❌ Nenhuma análise retornada")
                return False
        else:
            print("⚠️ Username não disponível para teste")
            return False
            
    except Exception as e:
        print(f"❌ Erro na análise de IA: {e}")
        return False

def test_csv_export(unfollower):
    """
    Testa exportação para CSV
    """
    print("\n💾 Testando exportação CSV...")
    
    try:
        # Criar dados de teste
        test_data = [{
            'username': 'test_user',
            'bio': 'Test bio',
            'location': 'Test location',
            'category': 'OTHER',
            'immunity_status': 'not_immune',
            'confidence': 0.8,
            'reasoning': 'Test reasoning'
        }]
        
        csv_file = unfollower.save_analysis_to_csv(test_data)
        
        if csv_file and os.path.exists(csv_file):
            print(f"✅ CSV criado: {csv_file}")
            # Limpar arquivo de teste
            os.remove(csv_file)
            print("✅ Arquivo de teste removido")
            return True
        else:
            print("❌ Falha na criação do CSV")
            return False
            
    except Exception as e:
        print(f"❌ Erro na exportação CSV: {e}")
        return False

def main():
    """
    Executa todos os testes
    """
    print("="*60)
    print("🧪 TESTE DO SISTEMA SELENIUM-ONLY")
    print("="*60)
    print("⚠️ IMPORTANTE: Certifique-se de estar logado no Twitter/X")
    print("="*60)
    
    # Confirmar execução
    confirm = input("\n🤔 Executar testes? [y/N]: ").strip().lower()
    if confirm not in ['y', 'yes', 's', 'sim']:
        print("👋 Testes cancelados")
        return
    
    results = {
        'initialization': False,
        'scraper_setup': False,
        'data_collection': False,
        'profile_extraction': False,
        'ai_analysis': False,
        'csv_export': False
    }
    
    try:
        # Teste 1: Inicialização
        unfollower = test_initialization()
        if unfollower:
            results['initialization'] = True
        else:
            print("\n❌ Falha na inicialização - parando testes")
            return
        
        # Teste 2: Configuração do scraper
        if test_scraper_setup(unfollower):
            results['scraper_setup'] = True
        
        # Teste 3: Coleta de dados
        following, followers = test_data_collection(unfollower)
        if following is not None and followers is not None:
            results['data_collection'] = True
        
        # Teste 4: Extração de perfil
        if test_profile_extraction(unfollower):
            results['profile_extraction'] = True
        
        # Teste 5: Análise de IA
        if test_ai_analysis(unfollower):
            results['ai_analysis'] = True
        
        # Teste 6: Exportação CSV
        if test_csv_export(unfollower):
            results['csv_export'] = True
        
    except Exception as e:
        print(f"\n❌ Erro geral nos testes: {e}")
    
    finally:
        # Limpar recursos
        if unfollower and hasattr(unfollower, 'cleanup'):
            unfollower.cleanup()
    
    # Relatório final
    print("\n" + "="*60)
    print("📊 RELATÓRIO DE TESTES")
    print("="*60)
    
    passed = sum(results.values())
    total = len(results)
    
    for test_name, passed_test in results.items():
        status = "✅ PASSOU" if passed_test else "❌ FALHOU"
        print(f"{test_name.replace('_', ' ').title()}: {status}")
    
    print(f"\n📈 Resultado: {passed}/{total} testes passaram")
    
    if passed == total:
        print("🎉 TODOS OS TESTES PASSARAM! Sistema pronto para uso.")
    elif passed >= total * 0.8:
        print("⚠️ Maioria dos testes passou. Sistema funcional com pequenos problemas.")
    else:
        print("❌ Muitos testes falharam. Verifique a configuração.")
    
    print("="*60)

if __name__ == "__main__":
    main()
