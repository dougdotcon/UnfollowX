#!/usr/bin/env python3
"""
Automação do Twitter/X usando Selenium para contornar limitações da API
"""

import time
import logging
from typing import Set, Dict
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager

class TwitterSeleniumScraper:
    def __init__(self, headless: bool = False, use_existing_profile: bool = True, browser: str = "chrome"):
        """
        Inicializa o scraper do Twitter usando Selenium

        Args:
            headless: Se True, executa o navegador em modo headless (sem interface)
            use_existing_profile: Se True, usa o perfil existente do navegador (já logado)
            browser: "chrome" ou "brave"
        """
        self.driver = None
        self.headless = headless
        self.use_existing_profile = use_existing_profile
        self.browser = browser.lower()
        self.logged_in = False
        self.username = None

        # Configurar logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
    def setup_driver(self):
        """
        Configura e inicializa o driver do Chrome ou Brave
        """
        try:
            # Configurações do navegador
            if self.browser == "brave":
                from selenium.webdriver.chrome.options import Options as BraveOptions
                options = BraveOptions()
                # Caminho típico do Brave no Windows
                brave_path = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
                options.binary_location = brave_path
            else:
                options = Options()

            if self.headless:
                options.add_argument("--headless")

            # Se usar perfil existente, configurar
            if self.use_existing_profile:
                import os

                if self.browser == "brave":
                    # Caminho do perfil do Brave
                    profile_path = os.path.expanduser(r"~\AppData\Local\BraveSoftware\Brave-Browser\User Data")
                    options.add_argument(f"--user-data-dir={profile_path}")
                    options.add_argument("--profile-directory=Default")
                else:
                    # Caminho do perfil do Chrome
                    profile_path = os.path.expanduser(r"~\AppData\Local\Google\Chrome\User Data")
                    options.add_argument(f"--user-data-dir={profile_path}")
                    options.add_argument("--profile-directory=Default")

                self.logger.info(f"🔧 Usando perfil existente: {profile_path}")

            # Configurações para melhor performance e estabilidade
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-gpu")
            options.add_argument("--window-size=1920,1080")
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)

            # Desabilitar notificações e popups
            prefs = {
                "profile.default_content_setting_values.notifications": 2,
                "profile.default_content_settings.popups": 0,
            }
            options.add_experimental_option("prefs", prefs)

            # Usar webdriver-manager para baixar automaticamente o driver
            if self.browser == "brave":
                # Para Brave, usar ChromeDriver (compatível)
                service = Service(ChromeDriverManager().install())
            else:
                service = Service(ChromeDriverManager().install())

            # Criar driver
            self.driver = webdriver.Chrome(service=service, options=options)
            self.driver.implicitly_wait(10)

            # Remover propriedades que indicam automação
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

            browser_name = "Brave" if self.browser == "brave" else "Chrome"
            self.logger.info(f"✅ Driver do {browser_name} configurado com sucesso")
            return True

        except Exception as e:
            self.logger.error(f"❌ Erro ao configurar driver: {e}")
            self.logger.error("💡 Dicas:")
            if self.browser == "brave":
                self.logger.error("   - Verifique se o Brave está instalado no caminho padrão")
                self.logger.error("   - Tente usar browser='chrome' se o Brave não funcionar")
            else:
                self.logger.error("   - Verifique se o Chrome está instalado")
                self.logger.error("   - Feche todas as instâncias do Chrome antes de executar")
            return False
    
    def check_login_status(self) -> bool:
        """
        Verifica se já está logado no Twitter/X e obtém o username

        Returns:
            True se já estiver logado
        """
        try:
            self.logger.info("� Verificando status de login...")

            # Navegar para o Twitter
            self.driver.get("https://x.com/home")
            time.sleep(5)

            # Verificar se está na página home (indicativo de login)
            if "home" in self.driver.current_url:
                self.logger.info("✅ Já está logado!")

                # Tentar obter o username do perfil
                try:
                    # Clicar no menu do perfil para obter username
                    profile_button = WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-testid="SideNav_AccountSwitcher_Button"]'))
                    )
                    profile_button.click()
                    time.sleep(2)

                    # Extrair username do menu
                    username_element = self.driver.find_element(By.CSS_SELECTOR, '[data-testid="UserName"] span')
                    self.username = username_element.text.replace('@', '')

                    # Fechar menu clicando fora
                    self.driver.find_element(By.TAG_NAME, 'body').click()

                    self.logged_in = True
                    self.logger.info(f"👤 Usuário logado: @{self.username}")
                    return True

                except Exception as e:
                    self.logger.warning(f"Não foi possível obter username: {e}")
                    # Mesmo assim, considerar como logado
                    self.logged_in = True
                    self.username = "unknown"
                    return True
            else:
                self.logger.error("❌ Não está logado - faça login manualmente no navegador")
                self.logger.error("💡 Abra o Twitter/X no seu navegador e faça login antes de executar o script")
                return False

        except Exception as e:
            self.logger.error(f"❌ Erro ao verificar login: {e}")
            return False
    
    def get_following_count(self) -> int:
        """
        Obtém o número total de usuários que você segue
        """
        try:
            # Navegar para o perfil
            self.driver.get(f"https://x.com/{self.username}")
            time.sleep(3)
            
            # Encontrar elemento com contagem de following
            following_element = self.driver.find_element(
                By.XPATH, '//a[contains(@href, "/following")]//span[contains(@class, "css-1jxf684")]'
            )
            
            following_text = following_element.text
            # Extrair número (pode estar em formato como "1,234" ou "1.2K")
            following_count = self._parse_count(following_text)
            
            self.logger.info(f"📊 Você segue {following_count} usuários")
            return following_count
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao obter contagem de following: {e}")
            return 0
    
    def get_followers_count(self) -> int:
        """
        Obtém o número total de seguidores
        """
        try:
            # Navegar para o perfil se não estiver lá
            if not self.driver.current_url.endswith(f"/{self.username}"):
                self.driver.get(f"https://x.com/{self.username}")
                time.sleep(3)
            
            # Encontrar elemento com contagem de followers
            followers_element = self.driver.find_element(
                By.XPATH, '//a[contains(@href, "/verified_followers") or contains(@href, "/followers")]//span[contains(@class, "css-1jxf684")]'
            )
            
            followers_text = followers_element.text
            followers_count = self._parse_count(followers_text)
            
            self.logger.info(f"📊 Você tem {followers_count} seguidores")
            return followers_count
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao obter contagem de followers: {e}")
            return 0
    
    def _parse_count(self, count_text: str) -> int:
        """
        Converte texto de contagem (ex: "1.2K", "1,234") para número inteiro
        """
        try:
            count_text = count_text.replace(",", "").replace(".", "")
            
            if "K" in count_text:
                return int(float(count_text.replace("K", "")) * 1000)
            elif "M" in count_text:
                return int(float(count_text.replace("M", "")) * 1000000)
            else:
                return int(count_text)
                
        except:
            return 0
    
    def get_following_list(self, max_users: int = 6000) -> Set[Dict]:
        """
        Obtém lista de usuários que você segue

        Args:
            max_users: Número máximo de usuários para coletar

        Returns:
            Set com dicionários contendo user_id, username, display_name
        """
        following_users = set()

        try:
            self.logger.info(f"📋 Coletando lista de usuários que você segue (máx: {max_users})...")

            # Navegar para página de following
            self.driver.get(f"https://x.com/{self.username}/following")
            time.sleep(5)

            # Scroll e coleta de usuários
            last_height = self.driver.execute_script("return document.body.scrollHeight")
            collected_count = 0

            while collected_count < max_users:
                # Encontrar todos os elementos de usuário na página atual
                user_elements = self.driver.find_elements(
                    By.CSS_SELECTOR,
                    '[data-testid="UserCell"]'
                )

                for element in user_elements:
                    if collected_count >= max_users:
                        break

                    try:
                        # Extrair informações do usuário
                        user_info = self._extract_user_info(element)
                        if user_info and user_info not in following_users:
                            following_users.add(user_info)
                            collected_count += 1

                            if collected_count % 50 == 0:
                                self.logger.info(f"   Coletados {collected_count} usuários...")

                    except Exception as e:
                        self.logger.debug(f"Erro ao extrair usuário: {e}")
                        continue

                # Scroll para carregar mais usuários
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)

                # Verificar se carregou mais conteúdo
                new_height = self.driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    self.logger.info("📄 Fim da lista alcançado")
                    break
                last_height = new_height

            self.logger.info(f"✅ Coletados {len(following_users)} usuários que você segue")
            return following_users

        except Exception as e:
            self.logger.error(f"❌ Erro ao coletar lista de following: {e}")
            return following_users

    def get_followers_list(self, max_users: int = 1000) -> Set[Dict]:
        """
        Obtém lista de usuários que te seguem

        Args:
            max_users: Número máximo de usuários para coletar

        Returns:
            Set com dicionários contendo user_id, username, display_name
        """
        followers_users = set()

        try:
            self.logger.info(f"📋 Coletando lista de seus seguidores (máx: {max_users})...")

            # Navegar para página de followers
            self.driver.get(f"https://x.com/{self.username}/verified_followers")
            time.sleep(5)

            # Se não conseguir acessar verified_followers, tentar followers normal
            if "verified_followers" not in self.driver.current_url:
                self.driver.get(f"https://x.com/{self.username}/followers")
                time.sleep(5)

            # Scroll e coleta de usuários
            last_height = self.driver.execute_script("return document.body.scrollHeight")
            collected_count = 0

            while collected_count < max_users:
                # Encontrar todos os elementos de usuário na página atual
                user_elements = self.driver.find_elements(
                    By.CSS_SELECTOR,
                    '[data-testid="UserCell"]'
                )

                for element in user_elements:
                    if collected_count >= max_users:
                        break

                    try:
                        # Extrair informações do usuário
                        user_info = self._extract_user_info(element)
                        if user_info and user_info not in followers_users:
                            followers_users.add(user_info)
                            collected_count += 1

                            if collected_count % 50 == 0:
                                self.logger.info(f"   Coletados {collected_count} seguidores...")

                    except Exception as e:
                        self.logger.debug(f"Erro ao extrair seguidor: {e}")
                        continue

                # Scroll para carregar mais usuários
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)

                # Verificar se carregou mais conteúdo
                new_height = self.driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    self.logger.info("📄 Fim da lista alcançado")
                    break
                last_height = new_height

            self.logger.info(f"✅ Coletados {len(followers_users)} seguidores")
            return followers_users

        except Exception as e:
            self.logger.error(f"❌ Erro ao coletar lista de followers: {e}")
            return followers_users

    def _extract_user_info(self, element) -> Dict:
        """
        Extrai informações de um elemento de usuário

        Returns:
            Dicionário com user_id, username, display_name
        """
        try:
            # Extrair username do link do perfil
            profile_link = element.find_element(By.CSS_SELECTOR, 'a[role="link"]')
            href = profile_link.get_attribute('href')
            username = href.split('/')[-1] if href else None

            # Extrair display name
            display_name_element = element.find_element(
                By.CSS_SELECTOR,
                '[data-testid="UserName"] span'
            )
            display_name = display_name_element.text

            # Para user_id, vamos usar o username como identificador único por enquanto
            # (o Twitter não expõe facilmente o user_id numérico via scraping)
            user_id = username

            if username and display_name:
                return {
                    'user_id': user_id,
                    'username': username,
                    'display_name': display_name
                }

        except Exception as e:
            self.logger.debug(f"Erro ao extrair info do usuário: {e}")

        return None

    def save_to_csv(self, users_data: Set[Dict], filename: str):
        """
        Salva dados dos usuários em arquivo CSV
        """
        try:
            import csv

            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['user_id', 'username', 'display_name']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

                writer.writeheader()
                for user in users_data:
                    writer.writerow(user)

            self.logger.info(f"💾 Dados salvos em {filename}")

        except Exception as e:
            self.logger.error(f"❌ Erro ao salvar CSV: {e}")

    def close(self):
        """
        Fecha o navegador
        """
        if self.driver:
            self.driver.quit()
            self.logger.info("🔒 Navegador fechado")
