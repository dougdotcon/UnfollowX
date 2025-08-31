#!/usr/bin/env python3
"""
Sistema Híbrido de Unfollow do Twitter/X
Integra extensão Chrome com análise de IA Python
"""

import os
import time
import json
import csv
import logging
import requests
from datetime import datetime
from typing import Set, Dict, List, Optional
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from immunity_analyzer import ImmunityAnalyzer

class TwitterHybridUnfollower:
    def __init__(self, openrouter_api_key: str, headless: bool = False):
        """
        Sistema híbrido que usa extensão Chrome + análise Python
        
        Args:
            openrouter_api_key: Chave da API do OpenRouter para análise de IA
            headless: Se True, executa navegador sem interface
        """
        self.openrouter_api_key = openrouter_api_key
        self.headless = headless
        self.state_file = 'hybrid_unfollow_state.json'
        self.extension_path = os.path.join(os.getcwd(), 'twitter-mass-unfollow', 'build')
        
        # Configurar logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('twitter_hybrid_unfollow.log', encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        # Inicializar componentes
        self.driver = None
        self.immunity_analyzer = ImmunityAnalyzer(openrouter_api_key)
        
    def setup_chrome_with_extension(self) -> webdriver.Chrome:
        """
        Configura Chrome com a extensão de mass unfollow
        """
        try:
            self.logger.info("🔧 Configurando Chrome com extensão...")
            
            # Verificar se extensão existe
            if not os.path.exists(self.extension_path):
                # Construir extensão se não existir
                self.build_extension()
            
            chrome_options = ChromeOptions()
            
            if not self.headless:
                chrome_options.add_argument("--disable-blink-features=AutomationControlled")
                chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
                chrome_options.add_experimental_option('useAutomationExtension', False)
            else:
                chrome_options.add_argument("--headless")
            
            # Carregar extensão
            chrome_options.add_argument(f"--load-extension={self.extension_path}")
            chrome_options.add_argument("--disable-web-security")
            chrome_options.add_argument("--allow-running-insecure-content")
            
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # Configurações anti-detecção
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            self.logger.info("✅ Chrome configurado com sucesso")
            return driver
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao configurar Chrome: {e}")
            raise
    
    def build_extension(self):
        """
        Constrói a extensão se necessário
        """
        self.logger.info("🔨 Construindo extensão...")
        extension_dir = os.path.join(os.getcwd(), 'twitter-mass-unfollow')
        
        if os.path.exists(extension_dir):
            import subprocess
            try:
                # Tentar construir com bun
                result = subprocess.run(['bun', 'run', 'build'], 
                                      cwd=extension_dir, 
                                      capture_output=True, 
                                      text=True)
                if result.returncode == 0:
                    self.logger.info("✅ Extensão construída com bun")
                    return
            except FileNotFoundError:
                pass
            
            try:
                # Fallback para npm
                result = subprocess.run(['npm', 'run', 'build'], 
                                      cwd=extension_dir, 
                                      capture_output=True, 
                                      text=True)
                if result.returncode == 0:
                    self.logger.info("✅ Extensão construída com npm")
                    return
            except FileNotFoundError:
                pass
        
        # Se chegou aqui, criar estrutura mínima
        self.create_minimal_extension()
    
    def create_minimal_extension(self):
        """
        Cria uma versão mínima da extensão baseada no código analisado
        """
        self.logger.info("🔧 Criando extensão mínima...")
        
        build_dir = os.path.join(os.getcwd(), 'twitter-mass-unfollow', 'build')
        os.makedirs(build_dir, exist_ok=True)
        
        # Manifest
        manifest = {
            "name": "Twitter Hybrid Unfollow",
            "description": "Sistema híbrido de unfollow com análise de IA",
            "version": "1.0.0",
            "manifest_version": 3,
            "permissions": ["storage", "scripting", "activeTab"],
            "content_scripts": [
                {
                    "matches": ["https://*.x.com/*/following", "https://*.twitter.com/*/following"],
                    "js": ["contentScript.js"]
                }
            ],
            "background": {
                "service_worker": "background.js"
            }
        }
        
        with open(os.path.join(build_dir, 'manifest.json'), 'w') as f:
            json.dump(manifest, f, indent=2)
        
        # Content Script simplificado
        content_script = '''
// Sistema híbrido de unfollow
let unfollowedUsers = [];
let analysisData = [];

const getFollowingButtons = () => {
    return Array.from(document.querySelectorAll('button[data-testid$="-unfollow"]'));
};

const getUsername = (followingBtn) => {
    return followingBtn.getAttribute('aria-label')?.toLowerCase().replace(/.*@/, '') || '';
};

const getUserData = (followingBtn) => {
    const container = followingBtn.closest('[data-testid="cellInnerDiv"]');
    if (!container) return null;
    
    const username = getUsername(followingBtn);
    const nameElement = container.querySelector('[dir="ltr"] span');
    const bioElement = container.querySelector('[data-testid="UserDescription"]');
    const locationElement = container.querySelector('[data-testid="UserLocation"]');
    
    return {
        username: username,
        display_name: nameElement?.textContent || '',
        bio: bioElement?.textContent || '',
        location: locationElement?.textContent || '',
        follows_you: !!container.querySelector('[data-testid="userFollowIndicator"]')
    };
};

const collectUserData = () => {
    const buttons = getFollowingButtons();
    const data = [];
    
    buttons.forEach(button => {
        const userData = getUserData(button);
        if (userData && !userData.follows_you) {
            data.push(userData);
        }
    });
    
    return data;
};

// Expor funções para o Python
window.twitterHybrid = {
    collectUserData: collectUserData,
    getFollowingButtons: getFollowingButtons,
    unfollowedUsers: unfollowedUsers
};

console.log('Twitter Hybrid Extension carregada');
'''
        
        with open(os.path.join(build_dir, 'contentScript.js'), 'w') as f:
            f.write(content_script)
        
        # Background script vazio
        with open(os.path.join(build_dir, 'background.js'), 'w') as f:
            f.write('// Background script para Twitter Hybrid Unfollow\nconsole.log("Background script carregado");')
        
        self.logger.info("✅ Extensão mínima criada")
    
    def navigate_to_following_page(self, username: Optional[str] = None):
        """
        Navega para a página de following
        """
        if username:
            url = f"https://x.com/{username}/following"
        else:
            url = "https://x.com/following"
        
        self.logger.info(f"🌐 Navegando para: {url}")
        self.driver.get(url)
        
        # Aguardar carregamento
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid$="-unfollow"]'))
            )
            self.logger.info("✅ Página carregada")
            return True
        except Exception as e:
            self.logger.error(f"❌ Erro ao carregar página: {e}")
            return False
    
    def collect_non_followers_data(self, max_users: int = 1000) -> List[Dict]:
        """
        Coleta dados dos usuários que não seguem de volta
        """
        self.logger.info(f"📊 Coletando dados de até {max_users} não-seguidores...")
        
        all_data = []
        last_height = 0
        no_new_data_count = 0
        
        while len(all_data) < max_users and no_new_data_count < 3:
            try:
                # Executar script de coleta
                new_data = self.driver.execute_script("return window.twitterHybrid?.collectUserData() || [];")
                
                # Adicionar novos dados
                for user_data in new_data:
                    if not any(u['username'] == user_data['username'] for u in all_data):
                        all_data.append(user_data)
                        
                        if len(all_data) >= max_users:
                            break
                
                # Scroll para carregar mais
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
                
                # Verificar se há novos dados
                current_height = self.driver.execute_script("return document.body.scrollHeight")
                if current_height == last_height:
                    no_new_data_count += 1
                else:
                    no_new_data_count = 0
                    
                last_height = current_height
                
                self.logger.info(f"📈 Coletados: {len(all_data)} usuários")
                
            except Exception as e:
                self.logger.error(f"❌ Erro na coleta: {e}")
                break
        
        self.logger.info(f"✅ Coleta concluída: {len(all_data)} usuários")
        return all_data
    
    def analyze_users_with_ai(self, users_data: List[Dict]) -> List[Dict]:
        """
        Analisa usuários com IA para determinar imunidade
        """
        self.logger.info(f"🤖 Analisando {len(users_data)} usuários com IA...")
        
        analyzed_users = []
        
        for i, user_data in enumerate(users_data):
            try:
                # Análise de imunidade
                immunity_result = self.immunity_analyzer.analyze_user_immunity(
                    username=user_data['username'],
                    display_name=user_data['display_name'],
                    description=user_data['bio'],
                    location=user_data['location']
                )
                
                # Combinar dados
                analyzed_user = {
                    **user_data,
                    'category': immunity_result['category'],
                    'immunity_status': immunity_result['immunity_status'],
                    'confidence': immunity_result['confidence'],
                    'reasoning': immunity_result['reasoning']
                }
                
                analyzed_users.append(analyzed_user)
                
                if (i + 1) % 10 == 0:
                    self.logger.info(f"🤖 Analisados: {i + 1}/{len(users_data)}")
                
                # Rate limiting
                time.sleep(0.5)
                
            except Exception as e:
                self.logger.error(f"❌ Erro na análise de @{user_data['username']}: {e}")
                
                # Adicionar com status de erro
                analyzed_user = {
                    **user_data,
                    'category': 'ERROR',
                    'immunity_status': 'immune',  # Conservador
                    'confidence': 0.0,
                    'reasoning': f'Erro na análise: {str(e)}'
                }
                analyzed_users.append(analyzed_user)
        
        self.logger.info(f"✅ Análise concluída: {len(analyzed_users)} usuários")
        return analyzed_users
    
    def save_analysis_to_csv(self, analyzed_users: List[Dict]) -> str:
        """
        Salva análise em CSV
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"hybrid_analysis_{timestamp}.csv"
        
        self.logger.info(f"💾 Salvando análise em: {filename}")
        
        fieldnames = [
            'username', 'display_name', 'bio', 'location', 'follows_you',
            'category', 'immunity_status', 'confidence', 'reasoning'
        ]
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(analyzed_users)
        
        self.logger.info(f"✅ CSV salvo: {filename}")
        return filename
    
    def get_eligible_for_unfollow(self, analyzed_users: List[Dict]) -> List[Dict]:
        """
        Filtra usuários elegíveis para unfollow (não imunes)
        """
        eligible = [
            user for user in analyzed_users 
            if user['immunity_status'] == 'not_immune'
        ]
        
        self.logger.info(f"🎯 Usuários elegíveis para unfollow: {len(eligible)}")
        return eligible
    
    def perform_unfollows(self, eligible_users: List[Dict], max_unfollows: int = 20) -> Dict:
        """
        Realiza unfollows dos usuários elegíveis
        """
        self.logger.info(f"⚡ Iniciando unfollows (máximo: {max_unfollows})...")
        
        unfollows_to_perform = eligible_users[:max_unfollows]
        results = {
            'attempted': 0,
            'successful': 0,
            'failed': 0,
            'details': []
        }
        
        for user in unfollows_to_perform:
            try:
                username = user['username']
                self.logger.info(f"⚡ Unfollowing @{username}...")
                
                # Procurar botão de unfollow para este usuário
                buttons = self.driver.find_elements(By.CSS_SELECTOR, '[data-testid$="-unfollow"]')
                
                user_button = None
                for button in buttons:
                    if username in button.get_attribute('aria-label', '').lower():
                        user_button = button
                        break
                
                if user_button:
                    # Clicar no unfollow
                    user_button.click()
                    time.sleep(1)
                    
                    # Confirmar unfollow
                    confirm_button = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-testid="confirmationSheetConfirm"]'))
                    )
                    confirm_button.click()
                    
                    results['successful'] += 1
                    results['details'].append({
                        'username': username,
                        'status': 'success',
                        'category': user['category']
                    })
                    
                    self.logger.info(f"✅ @{username} unfollowed")
                    
                else:
                    results['failed'] += 1
                    results['details'].append({
                        'username': username,
                        'status': 'button_not_found',
                        'category': user['category']
                    })
                    
                    self.logger.warning(f"⚠️ Botão não encontrado para @{username}")
                
                results['attempted'] += 1
                
                # Delay entre unfollows
                time.sleep(3)
                
            except Exception as e:
                results['failed'] += 1
                results['details'].append({
                    'username': user['username'],
                    'status': 'error',
                    'error': str(e),
                    'category': user['category']
                })
                
                self.logger.error(f"❌ Erro ao unfollow @{user['username']}: {e}")
        
        self.logger.info(f"✅ Unfollows concluídos: {results['successful']}/{results['attempted']}")
        return results
    
    def run_full_process(self, max_users: int = 1000, max_unfollows: int = 20) -> Dict:
        """
        Executa o processo completo
        """
        try:
            self.logger.info("🚀 Iniciando processo híbrido completo...")
            
            # Inicializar driver
            self.driver = self.setup_chrome_with_extension()
            
            # Navegar para página de following
            if not self.navigate_to_following_page():
                return {'success': False, 'message': 'Falha ao navegar para página de following'}
            
            # Aguardar usuário fazer login se necessário
            input("\n⚠️ Certifique-se de estar logado no X/Twitter e pressione ENTER para continuar...")
            
            # Coletar dados
            users_data = self.collect_non_followers_data(max_users)
            if not users_data:
                return {'success': False, 'message': 'Nenhum usuário coletado'}
            
            # Analisar com IA
            analyzed_users = self.analyze_users_with_ai(users_data)
            
            # Salvar CSV
            csv_file = self.save_analysis_to_csv(analyzed_users)
            
            # Filtrar elegíveis
            eligible_users = self.get_eligible_for_unfollow(analyzed_users)
            
            # Realizar unfollows
            unfollow_results = None
            if eligible_users and max_unfollows > 0:
                unfollow_results = self.perform_unfollows(eligible_users, max_unfollows)
            
            # Preparar resultados
            results = {
                'success': True,
                'csv_file': csv_file,
                'stats': {
                    'total_collected': len(users_data),
                    'total_analyzed': len(analyzed_users),
                    'eligible_count': len(eligible_users),
                    'immune_count': len([u for u in analyzed_users if u['immunity_status'] == 'immune']),
                    'unfollow_results': unfollow_results
                }
            }
            
            self.logger.info("✅ Processo híbrido concluído com sucesso!")
            return results
            
        except Exception as e:
            self.logger.error(f"❌ Erro no processo: {e}")
            return {'success': False, 'message': str(e)}
            
        finally:
            if self.driver:
                self.driver.quit()


def main():
    """
    Função principal para teste
    """
    from dotenv import load_dotenv
    load_dotenv()
    
    openrouter_key = os.getenv('OPENROUTER_API_KEY')
    if not openrouter_key:
        print("❌ OPENROUTER_API_KEY não encontrada no .env")
        return
    
    print("🚀 Sistema Híbrido de Unfollow Twitter/X")
    print("=" * 50)
    print("📱 Usa extensão Chrome + análise de IA Python")
    print("🛡️ Sistema de imunidade para proteger devs/pesquisadores")
    print("=" * 50)
    
    unfollower = TwitterHybridUnfollower(
        openrouter_api_key=openrouter_key,
        headless=False
    )
    
    results = unfollower.run_full_process(
        max_users=100,  # Teste com poucos usuários
        max_unfollows=5  # Teste com poucos unfollows
    )
    
    if results['success']:
        print("\n✅ Processo concluído!")
        print(f"📊 Estatísticas: {results['stats']}")
        if results.get('csv_file'):
            print(f"💾 Análise salva em: {results['csv_file']}")
    else:
        print(f"\n❌ Erro: {results['message']}")


if __name__ == "__main__":
    main()
