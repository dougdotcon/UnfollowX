#!/usr/bin/env python3
"""
Sistema completo de unfollow do Twitter/X usando apenas Selenium
Não requer API do Twitter - funciona apenas com navegador
"""

import os
import time
import logging
import json
import csv
from datetime import datetime
from typing import Set, Dict, List
from twitter_selenium import TwitterSeleniumScraper
from twitter_unfollow import ImmunityAnalyzer

class TwitterSeleniumUnfollower:
    def __init__(self, openrouter_api_key: str, headless: bool = False, browser: str = "chrome"):
        """
        Inicializa o sistema de unfollow usando apenas Selenium
        
        Args:
            openrouter_api_key: Chave da API do OpenRouter para análise de IA
            headless: Se True, executa navegador sem interface
            browser: "chrome" ou "brave"
        """
        self.openrouter_api_key = openrouter_api_key
        self.headless = headless
        self.browser = browser
        self.state_file = 'selenium_unfollow_state.json'
        self.running = False
        
        # Configurar logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('twitter_selenium_only.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        # Inicializar componentes
        self.scraper = None
        self.immunity_analyzer = ImmunityAnalyzer(openrouter_api_key)
        
    def initialize_scraper(self) -> bool:
        """
        Inicializa e configura o scraper Selenium
        """
        try:
            self.logger.info("🔧 Inicializando scraper Selenium...")
            self.scraper = TwitterSeleniumScraper(
                headless=self.headless,
                use_existing_profile=True,
                browser=self.browser
            )
            
            if not self.scraper.setup_driver():
                self.logger.error("❌ Falha ao configurar driver")
                return False
            
            if not self.scraper.check_login_status():
                self.logger.error("❌ Não foi possível verificar login no Twitter")
                return False
            
            self.logger.info(f"✅ Scraper inicializado. Logado como: @{self.scraper.username}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao inicializar scraper: {e}")
            return False
    
    def collect_data(self, max_following: int = 5000, max_followers: int = 5000) -> tuple:
        """
        Coleta listas de following e followers usando Selenium
        
        Returns:
            Tuple (following_set, followers_set) com usernames
        """
        if not self.scraper:
            raise Exception("Scraper não inicializado")
        
        self.logger.info("📋 Coletando dados via Selenium...")
        
        # Coletar following
        self.logger.info("📤 Coletando lista de following...")
        following_data = self.scraper.get_following_users(max_users=max_following)
        following_usernames = {user['username'] for user in following_data}
        
        # Coletar followers  
        self.logger.info("📥 Coletando lista de followers...")
        followers_data = self.scraper.get_followers_users(max_users=max_followers)
        followers_usernames = {user['username'] for user in followers_data}
        
        self.logger.info(f"📊 Coletados: {len(following_usernames)} following, {len(followers_usernames)} followers")
        
        return following_usernames, followers_usernames
    
    def find_non_followers(self, following: Set[str], followers: Set[str]) -> Set[str]:
        """
        Encontra usuários que você segue mas que não te seguem de volta
        """
        non_followers = following - followers
        self.logger.info(f"🎯 Encontrados {len(non_followers)} usuários que não te seguem de volta")
        return non_followers
    
    def extract_user_profile_data(self, username: str) -> Dict[str, str]:
        """
        Extrai dados completos do perfil de um usuário
        """
        profile_data = {
            'username': username,
            'display_name': '',
            'bio': '',
            'location': '',
            'verified': False,
            'followers_count': '',
            'following_count': ''
        }

        try:
            profile_url = f"https://x.com/{username}"
            self.scraper.driver.get(profile_url)
            time.sleep(3)  # Tempo maior para carregar completamente

            # Aguardar carregamento da página
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            from selenium.webdriver.common.by import By

            wait = WebDriverWait(self.scraper.driver, 10)

            # Extrair nome de exibição
            try:
                display_name_selectors = [
                    '//div[@data-testid="UserName"]//span[1]',
                    '//h1[@role="heading"]//span[1]',
                    '//div[contains(@class, "css-1dbjc4n")]//span[contains(@class, "css-901oao")]'
                ]
                for selector in display_name_selectors:
                    try:
                        element = wait.until(EC.presence_of_element_located((By.XPATH, selector)))
                        profile_data['display_name'] = element.text.strip()
                        break
                    except:
                        continue
            except:
                pass

            # Extrair bio com múltiplos seletores
            try:
                bio_selectors = [
                    '//div[@data-testid="UserDescription"]',
                    '//div[contains(@class, "css-901oao") and contains(@class, "r-18jsvk2")]',
                    '//div[@role="presentation"]//span[contains(@class, "css-901oao")]'
                ]
                for selector in bio_selectors:
                    try:
                        bio_element = self.scraper.driver.find_element(By.XPATH, selector)
                        if bio_element and bio_element.text.strip():
                            profile_data['bio'] = bio_element.text.strip()
                            break
                    except:
                        continue
            except:
                pass

            # Extrair localização
            try:
                location_selectors = [
                    '//span[@data-testid="UserLocation"]',
                    '//div[contains(@class, "css-1dbjc4n")]//span[contains(text(), "📍")]/../span[2]'
                ]
                for selector in location_selectors:
                    try:
                        location_element = self.scraper.driver.find_element(By.XPATH, selector)
                        if location_element and location_element.text.strip():
                            profile_data['location'] = location_element.text.strip()
                            break
                    except:
                        continue
            except:
                pass

            # Verificar se é verificado
            try:
                verified_selectors = [
                    '//svg[@aria-label="Verified account"]',
                    '//div[@data-testid="icon-verified"]'
                ]
                for selector in verified_selectors:
                    try:
                        self.scraper.driver.find_element(By.XPATH, selector)
                        profile_data['verified'] = True
                        break
                    except:
                        continue
            except:
                pass

            self.logger.debug(f"✅ Dados extraídos para @{username}: bio={len(profile_data['bio'])} chars")

        except Exception as e:
            self.logger.warning(f"⚠️ Erro ao extrair dados de @{username}: {e}")

        return profile_data

    def analyze_users_with_ai(self, usernames: Set[str], batch_size: int = 50, save_progress: bool = True) -> List[Dict]:
        """
        Analisa usuários com IA para determinar imunidade
        Otimizado para grandes volumes com salvamento de progresso
        """
        self.logger.info(f"🤖 Analisando {len(usernames)} usuários com IA...")
        self.logger.info(f"📊 Processamento em lotes de {batch_size} usuários")

        analyzed_users = []
        usernames_list = list(usernames)

        # Verificar se existe progresso salvo
        progress_file = 'analysis_progress.json'
        start_index = 0

        if save_progress and os.path.exists(progress_file):
            try:
                import json
                with open(progress_file, 'r') as f:
                    progress = json.load(f)
                    start_index = progress.get('last_processed', 0)
                    analyzed_users = progress.get('analyzed_users', [])
                self.logger.info(f"📂 Retomando análise do usuário {start_index + 1}")
            except:
                pass

        for i in range(start_index, len(usernames_list)):
            username = usernames_list[i]
            self.logger.info(f"🔍 Analisando {i+1}/{len(usernames_list)}: @{username}")

            try:
                # Extrair dados do perfil
                profile_data = self.extract_user_profile_data(username)

                # Analisar com IA
                analysis = self.immunity_analyzer.analyze_user_immunity(
                    username=username,
                    display_name=profile_data['display_name'] or username,
                    description=profile_data['bio'],
                    location=profile_data['location']
                )

                user_data = {
                    'username': username,
                    'display_name': profile_data['display_name'],
                    'bio': profile_data['bio'],
                    'location': profile_data['location'],
                    'verified': profile_data['verified'],
                    'category': analysis['category'],
                    'immunity_status': analysis['immunity_status'],
                    'confidence': analysis['confidence'],
                    'reasoning': analysis.get('reasoning', '')
                }
                
                analyzed_users.append(user_data)

                # Salvar progresso a cada lote
                if save_progress and (i + 1) % batch_size == 0:
                    self.save_analysis_progress(analyzed_users, i + 1, progress_file)
                    self.logger.info(f"💾 Progresso salvo: {i + 1}/{len(usernames_list)} usuários processados")

                # Delay entre análises (mais longo para grandes volumes)
                time.sleep(2)

            except Exception as e:
                self.logger.warning(f"⚠️ Erro ao analisar @{username}: {e}")
                # Adicionar com dados mínimos
                analyzed_users.append({
                    'username': username,
                    'display_name': '',
                    'bio': '',
                    'location': '',
                    'verified': False,
                    'category': 'UNKNOWN',
                    'immunity_status': 'not_immune',
                    'confidence': 0.5,
                    'reasoning': 'Erro na análise'
                })

                # Salvar progresso mesmo em caso de erro
                if save_progress and (i + 1) % batch_size == 0:
                    self.save_analysis_progress(analyzed_users, i + 1, progress_file)

        # Salvar progresso final
        if save_progress:
            self.save_analysis_progress(analyzed_users, len(usernames_list), progress_file)
            # Remover arquivo de progresso após conclusão
            try:
                os.remove(progress_file)
            except:
                pass

        self.logger.info(f"✅ Análise concluída: {len(analyzed_users)} usuários processados")
        return analyzed_users

    def save_analysis_progress(self, analyzed_users: List[Dict], last_processed: int, filename: str):
        """
        Salva progresso da análise
        """
        try:
            import json
            progress_data = {
                'last_processed': last_processed,
                'analyzed_users': analyzed_users,
                'timestamp': datetime.now().isoformat()
            }
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(progress_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.logger.error(f"❌ Erro ao salvar progresso: {e}")
    
    def save_analysis_to_csv(self, analyzed_users: List[Dict]) -> str:
        """
        Salva análise em arquivo CSV
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"selenium_analysis_{timestamp}.csv"
        
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['username', 'bio', 'location', 'category', 'immunity_status', 'confidence', 'reasoning']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                for user in analyzed_users:
                    writer.writerow(user)
            
            self.logger.info(f"💾 Análise salva em: {filename}")
            return filename
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao salvar CSV: {e}")
            return ""
    
    def filter_immune_users(self, analyzed_users: List[Dict]) -> List[str]:
        """
        Filtra usuários que não são imunes (podem receber unfollow)
        """
        non_immune = []
        immune_count = 0
        
        for user in analyzed_users:
            if user['immunity_status'] == 'immune':
                immune_count += 1
                self.logger.info(f"🛡️ IMUNE: @{user['username']} - {user['category']} (confiança: {user['confidence']:.2f})")
            else:
                non_immune.append(user['username'])
        
        self.logger.info(f"🛡️ {immune_count} usuários protegidos por imunidade")
        self.logger.info(f"🎯 {len(non_immune)} usuários elegíveis para unfollow")
        
        return non_immune
    
    def execute_unfollows(self, usernames: List[str], max_unfollows: int = 20, delay_between: float = 5.0) -> Dict:
        """
        Executa unfollows usando Selenium
        """
        if not usernames:
            self.logger.info("📭 Nenhum usuário para dar unfollow")
            return {'success': [], 'failed': [], 'total_processed': 0}
        
        # Limitar quantidade
        users_to_unfollow = usernames[:max_unfollows]
        
        self.logger.info(f"⚡ Executando unfollows: {len(users_to_unfollow)} usuários")
        
        results = self.scraper.unfollow_users_batch(
            usernames=users_to_unfollow,
            delay_between=delay_between,
            max_per_session=max_unfollows
        )
        
        return results
    
    def save_state(self, state_data: Dict):
        """
        Salva estado atual do processo
        """
        try:
            with open(self.state_file, 'w') as f:
                json.dump(state_data, f, indent=2, default=str)
            self.logger.info(f"💾 Estado salvo em {self.state_file}")
        except Exception as e:
            self.logger.error(f"❌ Erro ao salvar estado: {e}")
    
    def load_state(self) -> Dict:
        """
        Carrega estado salvo
        """
        try:
            if os.path.exists(self.state_file):
                with open(self.state_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            self.logger.error(f"❌ Erro ao carregar estado: {e}")
        return {}
    
    def run_full_process(self, max_following: int = 5000, max_followers: int = 5000,
                        max_unfollows: int = 20, delay_between: float = 5.0) -> Dict:
        """
        Executa o processo completo de unfollow

        Args:
            max_following: Máximo de following para coletar
            max_followers: Máximo de followers para coletar
            max_unfollows: Máximo de unfollows por execução
            delay_between: Delay entre unfollows (segundos)

        Returns:
            Dicionário com resultados da execução
        """
        results = {
            'success': False,
            'message': '',
            'stats': {},
            'csv_file': '',
            'unfollow_results': {}
        }

        try:
            self.logger.info("🚀 INICIANDO PROCESSO COMPLETO SELENIUM-ONLY")
            self.logger.info("="*60)

            # 1. Inicializar scraper
            if not self.initialize_scraper():
                results['message'] = "Falha ao inicializar scraper"
                return results

            # 2. Coletar dados
            self.logger.info("📋 ETAPA 1/5: Coletando dados...")
            following, followers = self.collect_data(max_following, max_followers)

            if not following:
                results['message'] = "Nenhum dado de following coletado"
                return results

            # 3. Encontrar não-seguidores
            self.logger.info("🎯 ETAPA 2/5: Identificando não-seguidores...")
            non_followers = self.find_non_followers(following, followers)

            if not non_followers:
                results['message'] = "Todos os usuários te seguem de volta!"
                results['success'] = True
                return results

            # 4. Analisar com IA
            self.logger.info("🤖 ETAPA 3/5: Analisando com IA...")
            analyzed_users = self.analyze_users_with_ai(non_followers)

            # 5. Salvar análise
            self.logger.info("💾 ETAPA 4/5: Salvando análise...")
            csv_file = self.save_analysis_to_csv(analyzed_users)
            results['csv_file'] = csv_file

            # 6. Filtrar usuários imunes
            eligible_users = self.filter_immune_users(analyzed_users)

            if not eligible_users:
                results['message'] = "Todos os não-seguidores são imunes!"
                results['success'] = True
                return results

            # 7. Executar unfollows
            self.logger.info("⚡ ETAPA 5/5: Executando unfollows...")
            unfollow_results = self.execute_unfollows(
                eligible_users,
                max_unfollows=max_unfollows,
                delay_between=delay_between
            )

            # 8. Salvar estado
            state_data = {
                'timestamp': datetime.now().isoformat(),
                'following_count': len(following),
                'followers_count': len(followers),
                'non_followers_count': len(non_followers),
                'analyzed_count': len(analyzed_users),
                'eligible_count': len(eligible_users),
                'unfollow_results': unfollow_results,
                'csv_file': csv_file
            }
            self.save_state(state_data)

            # Resultados finais
            results.update({
                'success': True,
                'message': 'Processo concluído com sucesso',
                'stats': state_data,
                'unfollow_results': unfollow_results
            })

            self.logger.info("🎉 PROCESSO CONCLUÍDO!")
            self.logger.info(f"📊 Estatísticas finais:")
            self.logger.info(f"   Following: {len(following)}")
            self.logger.info(f"   Followers: {len(followers)}")
            self.logger.info(f"   Não-seguidores: {len(non_followers)}")
            self.logger.info(f"   Analisados: {len(analyzed_users)}")
            self.logger.info(f"   Elegíveis: {len(eligible_users)}")
            self.logger.info(f"   Unfollows realizados: {unfollow_results['success_count']}")

            return results

        except Exception as e:
            self.logger.error(f"❌ Erro no processo: {e}")
            results['message'] = f"Erro: {e}"
            return results

        finally:
            self.cleanup()

    def cleanup(self):
        """
        Limpa recursos
        """
        if self.scraper:
            self.scraper.close()
            self.logger.info("🔒 Recursos liberados")
