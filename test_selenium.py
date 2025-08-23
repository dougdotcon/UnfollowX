#!/usr/bin/env python3
"""
Teste básico do Selenium para verificar se está funcionando
"""

from twitter_selenium import TwitterSeleniumScraper
import logging

def test_selenium_setup():
    """
    Testa se o Selenium está configurado corretamente
    """
    print("🧪 TESTE DO SELENIUM")
    print("="*50)
    
    try:
        # Criar scraper
        scraper = TwitterSeleniumScraper(headless=False)
        
        # Testar configuração do driver
        print("🔧 Testando configuração do driver...")
        if scraper.setup_driver():
            print("✅ Driver configurado com sucesso!")
            
            # Testar navegação básica
            print("🌐 Testando navegação...")
            scraper.driver.get("https://x.com")
            
            # Verificar se a página carregou
            if "x.com" in scraper.driver.current_url:
                print("✅ Navegação funcionando!")
                print(f"   URL atual: {scraper.driver.current_url}")
                
                # Aguardar um pouco para ver a página
                import time
                print("⏳ Aguardando 5 segundos para visualização...")
                time.sleep(5)
                
            else:
                print("❌ Erro na navegação")
                
        else:
            print("❌ Erro na configuração do driver")
            
        # Fechar navegador
        scraper.close()
        print("🔒 Navegador fechado")
        
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        logging.error(f"Erro no teste: {e}")

if __name__ == "__main__":
    test_selenium_setup()
