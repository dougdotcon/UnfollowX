#!/usr/bin/env python3
"""
Teste simples do Selenium com perfil existente
"""

from twitter_selenium import TwitterSeleniumScraper

def test_browser_connection():
    """
    Testa conexão com navegador usando perfil existente
    """
    print("🧪 TESTE SELENIUM COM PERFIL EXISTENTE")
    print("="*50)
    
    # Escolher navegador
    print("Qual navegador testar?")
    print("1. Chrome")
    print("2. Brave")
    choice = input("Escolha (1 ou 2): ").strip()
    
    browser = "brave" if choice == "2" else "chrome"
    
    try:
        print(f"\n🔧 Configurando {browser.title()}...")
        scraper = TwitterSeleniumScraper(
            headless=False, 
            use_existing_profile=True, 
            browser=browser
        )
        
        if scraper.setup_driver():
            print("✅ Driver configurado!")
            
            print("🔍 Verificando login no Twitter...")
            if scraper.check_login_status():
                print("✅ Login verificado com sucesso!")
                print(f"👤 Usuário: @{scraper.username}")
                
                # Testar contagem básica
                print("\n📊 Testando contagens...")
                following = scraper.get_following_count()
                followers = scraper.get_followers_count()
                
                print(f"   Following: {following}")
                print(f"   Followers: {followers}")
                
                print("\n✅ Teste concluído com sucesso!")
                
            else:
                print("❌ Não está logado no Twitter")
                print("💡 Faça login no Twitter no seu navegador primeiro")
            
            # Aguardar antes de fechar
            input("\nPressione Enter para fechar o navegador...")
            scraper.close()
            
        else:
            print("❌ Erro ao configurar driver")
            
    except Exception as e:
        print(f"❌ Erro no teste: {e}")

if __name__ == "__main__":
    test_browser_connection()
