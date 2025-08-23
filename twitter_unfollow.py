#!/usr/bin/env python3
"""
Script para dar unfollow em perfis que não te seguem de volta no Twitter/X
Usa a API v2 do Twitter/X
"""

import tweepy
import time
import json
from typing import List, Set, Dict
import logging
import schedule
import threading
from datetime import datetime, timedelta
import os
from openai import OpenAI
import re
import pandas as pd
import csv
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('twitter_unfollow.log'),
        logging.StreamHandler()
    ]
)

class ImmunityAnalyzer:
    def __init__(self, openrouter_api_key: str):
        """
        Inicializa o analisador de imunidade usando OpenRouter
        """
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=openrouter_api_key,
        )
        self.immunity_cache = {}  # Cache para evitar análises repetidas

    def analyze_profile(self, user_data: dict) -> dict:
        """
        Analisa um perfil de usuário de forma detalhada

        Returns:
            dict: {
                'is_immune': bool,
                'category': str,
                'confidence': float,
                'reason': str,
                'keywords_found': list
            }
        """
        user_id = user_data.get('id')
        username = user_data.get('username', 'unknown')
        name = user_data.get('name', '')
        bio = user_data.get('description', '')
        location = user_data.get('location', '')
        followers_count = user_data.get('followers_count', 0)

        # Verificar cache primeiro
        cache_key = f"{user_id}_{hash(bio)}"
        if cache_key in self.immunity_cache:
            return self.immunity_cache[cache_key]

        # Se não tem bio, análise básica
        if not bio or len(bio.strip()) < 10:
            result = {
                'is_immune': False,
                'category': 'no_bio',
                'confidence': 0.9,
                'reason': "Bio muito curta ou inexistente",
                'keywords_found': []
            }
            self.immunity_cache[cache_key] = result
            return result

        try:
            # Prompt melhorado para análise detalhada
            prompt = f"""
Analise o perfil do usuário do Twitter/X e forneça uma análise detalhada.

DADOS DO USUÁRIO:
- Nome: {name}
- Username: @{username}
- Bio: {bio}
- Localização: {location}
- Seguidores: {followers_count}

CATEGORIAS DE ANÁLISE:
1. DEVELOPER - Desenvolvedor de software/programador
2. AI_RESEARCHER - Pesquisador de IA/ML/Data Science
3. ACADEMIC - Professor/estudante de universidades renomadas
4. TECH_EXECUTIVE - CEO/Founder de startups tech
5. ENGINEER - Engenheiro em grandes empresas tech
6. SCIENTIST - Cientista/pesquisador acadêmico
7. STUDENT_TECH - Estudante de tecnologia/ciência
8. CONTENT_CREATOR - Criador de conteúdo tech
9. OTHER - Outras profissões

INSTRUÇÕES:
Responda EXATAMENTE no formato JSON:
{{
  "category": "CATEGORIA",
  "is_immune": true/false,
  "confidence": 0.0-1.0,
  "reason": "explicação detalhada",
  "keywords": ["palavra1", "palavra2"]
}}

CRITÉRIOS DE IMUNIDADE:
- DEVELOPER, AI_RESEARCHER, ACADEMIC, TECH_EXECUTIVE, ENGINEER, SCIENTIST, STUDENT_TECH: IMUNE
- CONTENT_CREATOR: IMUNE se foco em tech
- OTHER: NÃO IMUNE

Seja rigoroso na análise. Confidence alto (>0.8) apenas se muito claro.

RESPOSTA JSON:"""

            completion = self.client.chat.completions.create(
                extra_headers={
                    "HTTP-Referer": "https://github.com/unf_twitter",
                    "X-Title": "Twitter Unfollow Bot",
                },
                model="qwen/qwen-2.5-coder-32b-instruct",
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=200,
                temperature=0.1
            )

            response = completion.choices[0].message.content.strip()

            # Tentar parsear JSON
            try:
                import json
                # Extrair JSON da resposta
                json_start = response.find('{')
                json_end = response.rfind('}') + 1
                if json_start != -1 and json_end != -1:
                    json_str = response[json_start:json_end]
                    analysis = json.loads(json_str)

                    result = {
                        'is_immune': analysis.get('is_immune', False),
                        'category': analysis.get('category', 'OTHER'),
                        'confidence': analysis.get('confidence', 0.5),
                        'reason': analysis.get('reason', 'Análise automática'),
                        'keywords_found': analysis.get('keywords', [])
                    }
                else:
                    raise ValueError("JSON não encontrado na resposta")

            except (json.JSONDecodeError, ValueError, KeyError) as e:
                # Fallback para análise simples
                logging.warning(f"Erro ao parsear JSON para @{username}: {e}")

                # Análise básica por palavras-chave
                bio_lower = bio.lower()
                tech_keywords = [
                    'developer', 'engineer', 'programmer', 'software', 'ai', 'ml',
                    'data science', 'phd', 'researcher', 'professor', 'mit', 'stanford',
                    'google', 'microsoft', 'meta', 'apple', 'openai', 'ceo', 'founder'
                ]

                found_keywords = [kw for kw in tech_keywords if kw in bio_lower]
                is_immune = len(found_keywords) >= 2 or any(kw in bio_lower for kw in ['engineer', 'developer', 'researcher', 'phd'])

                result = {
                    'is_immune': is_immune,
                    'category': 'TECH_RELATED' if is_immune else 'OTHER',
                    'confidence': 0.6 if found_keywords else 0.3,
                    'reason': f"Análise por palavras-chave: {', '.join(found_keywords)}" if found_keywords else "Nenhuma palavra-chave tech encontrada",
                    'keywords_found': found_keywords
                }

            # Salvar no cache
            self.immunity_cache[cache_key] = result

            logging.info(f"Análise para @{username}: {result['category']} - {'IMUNE' if result['is_immune'] else 'NÃO_IMUNE'} (conf: {result['confidence']:.2f})")

            return result

        except Exception as e:
            logging.error(f"Erro na análise para @{username}: {e}")
            result = {
                'is_immune': False,
                'category': 'ERROR',
                'confidence': 0.0,
                'reason': f"Erro na análise: {e}",
                'keywords_found': []
            }
            return result

    def is_immune(self, user_data: dict) -> tuple[bool, str]:
        """
        Método de compatibilidade que usa a nova análise detalhada
        """
        analysis = self.analyze_profile(user_data)
        return analysis['is_immune'], analysis['reason']

class TwitterUnfollower:
    def __init__(self, api_key: str, api_secret: str, access_token: str, access_token_secret: str, openrouter_api_key: str):
        """
        Inicializa o cliente do Twitter e o analisador de imunidade
        """
        self.api_key = api_key
        self.api_secret = api_secret
        self.access_token = access_token
        self.access_token_secret = access_token_secret
        self.state_file = 'unfollow_state.json'
        self.running = False

        # Inicializar analisador de imunidade
        self.immunity_analyzer = ImmunityAnalyzer(openrouter_api_key)
        
        # Configurar autenticação OAuth 1.0a
        auth = tweepy.OAuth1UserHandler(
            consumer_key=api_key,
            consumer_secret=api_secret,
            access_token=access_token,
            access_token_secret=access_token_secret
        )
        
        # Criar cliente da API v2
        self.client = tweepy.Client(
            consumer_key=api_key,
            consumer_secret=api_secret,
            access_token=access_token,
            access_token_secret=access_token_secret,
            wait_on_rate_limit=True
        )
        
        # Obter informações do usuário autenticado
        try:
            self.me = self.client.get_me()
            self.user_id = self.me.data.id
            self.username = self.me.data.username
            logging.info(f"Autenticado como: @{self.username} (ID: {self.user_id})")
        except Exception as e:
            logging.error(f"Erro na autenticação: {e}")
            raise

    def get_following(self) -> Set[int]:
        """
        Obtém lista de usuários que você segue
        """
        following = set()
        try:
            logging.info("Obtendo lista de usuários que você segue...")
            
            # Usar paginação para obter todos os seguidos
            paginator = tweepy.Paginator(
                self.client.get_following,
                id=self.user_id,
                max_results=1000,
                limit=10  # Limitar a 10 páginas por segurança
            )
            
            for page in paginator:
                if page.data:
                    for user in page.data:
                        following.add(user.id)
                        
            logging.info(f"Você segue {len(following)} usuários")
            return following
            
        except Exception as e:
            logging.error(f"Erro ao obter lista de seguidos: {e}")
            return set()

    def get_followers(self) -> Set[int]:
        """
        Obtém lista de usuários que te seguem
        """
        followers = set()
        try:
            logging.info("Obtendo lista de seus seguidores...")
            
            # Usar paginação para obter todos os seguidores
            paginator = tweepy.Paginator(
                self.client.get_followers,
                id=self.user_id,
                max_results=1000,
                limit=10  # Limitar a 10 páginas por segurança
            )
            
            for page in paginator:
                if page.data:
                    for user in page.data:
                        followers.add(user.id)
                        
            logging.info(f"Você tem {len(followers)} seguidores")
            return followers
            
        except Exception as e:
            logging.error(f"Erro ao obter lista de seguidores: {e}")
            return set()

    def find_non_followers(self, following: Set[int], followers: Set[int]) -> Set[int]:
        """
        Encontra usuários que você segue mas que não te seguem de volta
        """
        non_followers = following - followers
        logging.info(f"Encontrados {len(non_followers)} usuários que não te seguem de volta")
        return non_followers

    def get_user_info(self, user_ids: List[int]) -> dict:
        """
        Obtém informações completas dos usuários (nome, username, bio, localização)
        """
        user_info = {}
        try:
            # Processar em lotes de 100 (limite da API)
            for i in range(0, len(user_ids), 100):
                batch = user_ids[i:i+100]
                users = self.client.get_users(
                    ids=batch,
                    user_fields=['description', 'location', 'verified', 'public_metrics']
                )

                if users.data:
                    for user in users.data:
                        user_info[user.id] = {
                            'id': user.id,
                            'username': user.username,
                            'name': user.name,
                            'description': getattr(user, 'description', ''),
                            'location': getattr(user, 'location', ''),
                            'verified': getattr(user, 'verified', False),
                            'followers_count': getattr(user, 'public_metrics', {}).get('followers_count', 0) if hasattr(user, 'public_metrics') else 0
                        }

                # Aguardar um pouco entre as requisições
                time.sleep(1)

        except Exception as e:
            logging.error(f"Erro ao obter informações dos usuários: {e}")

        return user_info

    def unfollow_user(self, user_id: int) -> bool:
        """
        Para de seguir um usuário específico
        """
        try:
            response = self.client.unfollow_user(target_user_id=user_id)
            if response.data and response.data.get('following') == False:
                return True
            return False
        except Exception as e:
            logging.error(f"Erro ao dar unfollow no usuário {user_id}: {e}")
            return False

    def unfollow_non_followers(self, non_followers: Set[int], dry_run: bool = True, max_unfollows: int = 50):
        """
        Faz unfollow em usuários que não te seguem de volta
        
        Args:
            non_followers: Set de IDs dos usuários para dar unfollow
            dry_run: Se True, apenas simula sem fazer unfollow real
            max_unfollows: Máximo de unfollows por execução (para evitar rate limits)
        """
        if not non_followers:
            logging.info("Nenhum usuário para dar unfollow")
            return

        # Converter para lista e limitar quantidade
        users_to_unfollow = list(non_followers)[:max_unfollows]
        
        # Obter informações dos usuários
        logging.info("Obtendo informações dos usuários...")
        user_info = self.get_user_info(users_to_unfollow)
        
        unfollowed_count = 0
        failed_count = 0
        
        for user_id in users_to_unfollow:
            user_data = user_info.get(user_id, {'username': 'unknown', 'name': 'Unknown'})
            username = user_data['username']
            name = user_data['name']
            
            if dry_run:
                logging.info(f"[DRY RUN] Daria unfollow em: @{username} ({name})")
            else:
                logging.info(f"Dando unfollow em: @{username} ({name})")
                
                if self.unfollow_user(user_id):
                    unfollowed_count += 1
                    logging.info(f"✓ Unfollow realizado com sucesso em @{username}")
                else:
                    failed_count += 1
                    logging.error(f"✗ Falha ao dar unfollow em @{username}")
                
                # Aguardar entre unfollows para evitar rate limit
                time.sleep(2)
        
        if not dry_run:
            logging.info(f"Processo concluído: {unfollowed_count} unfollows realizados, {failed_count} falharam")
        else:
            logging.info(f"[DRY RUN] Seriam realizados {len(users_to_unfollow)} unfollows")

    def save_report(self, following: Set[int], followers: Set[int], non_followers: Set[int]):
        """
        Salva relatório em arquivo JSON
        """
        report = {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'user': f"@{self.username}",
            'stats': {
                'following_count': len(following),
                'followers_count': len(followers),
                'non_followers_count': len(non_followers)
            },
            'non_followers_ids': list(non_followers)
        }
        
        with open('twitter_unfollow_report.json', 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
            
        logging.info("Relatório salvo em 'twitter_unfollow_report.json'")

    def save_non_followers_to_csv(self, non_followers: Set[int]):
        """
        Salva apenas os non_followers em formato CSV com análise de perfil otimizada
        """
        logging.info(f"Analisando {len(non_followers)} non_followers e salvando em CSV...")

        # Obter informações detalhadas apenas dos non_followers
        non_followers_list = list(non_followers)
        user_info = self.get_user_info(non_followers_list)

        # Preparar dados para o CSV (apenas non_followers)
        csv_data = []

        print(f"🤖 Analisando perfis com IA...")
        analyzed_count = 0

        for user_id in non_followers_list:
            user_data = user_info.get(user_id, {
                'id': user_id,
                'username': 'unknown',
                'name': 'Unknown',
                'description': '',
                'location': '',
                'verified': False,
                'followers_count': 0
            })

            analyzed_count += 1
            if analyzed_count % 10 == 0:
                print(f"   Analisados: {analyzed_count}/{len(non_followers_list)}")

            # Todos são non_followers
            relationship = "following_only"

            # Analisar perfil (todos são non_followers)
            try:
                analysis = self.immunity_analyzer.analyze_profile(user_data)
                immunity_status = "immune" if analysis['is_immune'] else "not_immune"
                immunity_reason = analysis['reason']
                category = analysis['category']
                confidence = analysis['confidence']
                keywords_found = analysis['keywords_found']
            except Exception as e:
                immunity_status = "analysis_error"
                immunity_reason = str(e)
                category = "ERROR"
                confidence = 0.0
                keywords_found = []
                logging.error(f"Erro na análise para @{user_data['username']}: {e}")

            csv_data.append({
                'user_id': user_id,
                'username': user_data['username'],
                'name': user_data['name'],
                'description': user_data['description'][:300] if user_data['description'] else '',
                'location': user_data['location'],
                'verified': user_data['verified'],
                'followers_count': user_data['followers_count'],
                'relationship': relationship,
                'immunity_status': immunity_status,
                'immunity_reason': immunity_reason,
                'category': category,
                'confidence': confidence,
                'keywords_found': ', '.join(keywords_found) if keywords_found else '',
                'analysis_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })

        # Salvar em CSV
        csv_filename = f'non_followers_analysis_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'

        try:
            df = pd.DataFrame(csv_data)
            df.to_csv(csv_filename, index=False, encoding='utf-8')

            # Estatísticas
            immune_count = len([row for row in csv_data if row['immunity_status'] == 'immune'])
            not_immune_count = len([row for row in csv_data if row['immunity_status'] == 'not_immune'])
            error_count = len([row for row in csv_data if row['immunity_status'] == 'analysis_error'])

            logging.info(f"Análise completa salva em '{csv_filename}'")
            print(f"\n📊 ESTATÍSTICAS DA ANÁLISE:")
            print(f"Total de non-followers analisados: {len(csv_data)}")
            print(f"Usuários imunes: {immune_count}")
            print(f"Usuários não-imunes: {not_immune_count}")
            print(f"Erros de análise: {error_count}")
            print(f"Taxa de imunidade: {(immune_count/len(csv_data)*100):.1f}%")

            # Estatísticas por categoria
            categories = {}
            for row in csv_data:
                cat = row['category']
                categories[cat] = categories.get(cat, 0) + 1

            print(f"\n📋 CATEGORIAS ENCONTRADAS:")
            for category, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
                print(f"   {category}: {count}")

            return csv_filename

        except Exception as e:
            logging.error(f"Erro ao salvar CSV: {e}")
            return None

    def load_non_followers_from_csv(self, csv_filename: str, filter_config: dict = None) -> List[int]:
        """
        Carrega lista de non_followers filtrada do CSV com critérios avançados

        Args:
            csv_filename: Nome do arquivo CSV
            filter_config: Configuração de filtros {
                'min_confidence': float,
                'exclude_categories': list,
                'min_followers': int,
                'max_followers': int,
                'exclude_verified': bool
            }
        """
        try:
            df = pd.read_csv(csv_filename)

            # Configuração padrão de filtros
            if filter_config is None:
                filter_config = {
                    'min_confidence': 0.5,
                    'exclude_categories': ['DEVELOPER', 'AI_RESEARCHER', 'ACADEMIC', 'TECH_EXECUTIVE', 'ENGINEER', 'SCIENTIST'],
                    'min_followers': 0,
                    'max_followers': float('inf'),
                    'exclude_verified': False
                }

            # Todos os dados já são non_followers
            filtered_df = df.copy()

            # Filtro por status de imunidade
            filtered_df = filtered_df[filtered_df['immunity_status'] == 'not_immune']

            # Filtro por confiança da análise
            if 'confidence' in filtered_df.columns:
                filtered_df = filtered_df[filtered_df['confidence'] >= filter_config.get('min_confidence', 0.5)]

            # Filtro por categoria (excluir categorias específicas)
            exclude_categories = filter_config.get('exclude_categories', [])
            if exclude_categories and 'category' in filtered_df.columns:
                filtered_df = filtered_df[~filtered_df['category'].isin(exclude_categories)]

            # Filtro por número de seguidores
            min_followers = filter_config.get('min_followers', 0)
            max_followers = filter_config.get('max_followers', float('inf'))
            if 'followers_count' in filtered_df.columns:
                filtered_df = filtered_df[
                    (filtered_df['followers_count'] >= min_followers) &
                    (filtered_df['followers_count'] <= max_followers)
                ]

            # Filtro por verificação
            if filter_config.get('exclude_verified', False) and 'verified' in filtered_df.columns:
                filtered_df = filtered_df[filtered_df['verified'] == False]

            user_ids = filtered_df['user_id'].tolist()

            # Log das estatísticas de filtragem
            total_non_followers = len(df)
            filtered_count = len(user_ids)

            logging.info(f"Filtragem aplicada:")
            logging.info(f"  Total non-followers: {total_non_followers}")
            logging.info(f"  Após filtros: {filtered_count}")
            logging.info(f"  Taxa de filtragem: {(1 - filtered_count/total_non_followers)*100:.1f}%")

            # Estatísticas por categoria
            if 'category' in filtered_df.columns:
                category_stats = filtered_df['category'].value_counts()
                logging.info(f"  Categorias restantes: {dict(category_stats)}")

            return user_ids

        except Exception as e:
            logging.error(f"Erro ao carregar CSV: {e}")
            return []

    def create_smart_filter_config(self, aggressive: bool = False) -> dict:
        """
        Cria configuração de filtro inteligente

        Args:
            aggressive: Se True, aplica filtros mais rigorosos
        """
        if aggressive:
            return {
                'min_confidence': 0.7,
                'exclude_categories': [
                    'DEVELOPER', 'AI_RESEARCHER', 'ACADEMIC', 'TECH_EXECUTIVE',
                    'ENGINEER', 'SCIENTIST', 'STUDENT_TECH', 'CONTENT_CREATOR'
                ],
                'min_followers': 0,
                'max_followers': 100000,  # Evitar contas muito grandes
                'exclude_verified': True
            }
        else:
            return {
                'min_confidence': 0.5,
                'exclude_categories': [
                    'DEVELOPER', 'AI_RESEARCHER', 'ACADEMIC', 'TECH_EXECUTIVE',
                    'ENGINEER', 'SCIENTIST'
                ],
                'min_followers': 0,
                'max_followers': float('inf'),
                'exclude_verified': False
            }

    def analyze_csv_data(self, csv_filename: str) -> dict:
        """
        Analisa os dados do CSV e fornece estatísticas detalhadas
        """
        try:
            df = pd.read_csv(csv_filename)

            # Estatísticas gerais
            total_users = len(df)
            non_followers = len(df[df['is_non_follower'] == True])
            immune_users = len(df[df['immunity_status'] == 'immune'])
            not_immune_users = len(df[df['immunity_status'] == 'not_immune'])

            # Estatísticas por categoria
            category_stats = {}
            if 'category' in df.columns:
                category_stats = df['category'].value_counts().to_dict()

            # Estatísticas de confiança
            confidence_stats = {}
            if 'confidence' in df.columns:
                confidence_stats = {
                    'mean': df['confidence'].mean(),
                    'median': df['confidence'].median(),
                    'high_confidence': len(df[df['confidence'] >= 0.8]),
                    'low_confidence': len(df[df['confidence'] < 0.5])
                }

            # Usuários verificados
            verified_count = len(df[df['verified'] == True]) if 'verified' in df.columns else 0

            return {
                'total_users': total_users,
                'non_followers': non_followers,
                'immune_users': immune_users,
                'not_immune_users': not_immune_users,
                'verified_count': verified_count,
                'category_stats': category_stats,
                'confidence_stats': confidence_stats,
                'immunity_rate': (immune_users / non_followers * 100) if non_followers > 0 else 0
            }

        except Exception as e:
            logging.error(f"Erro ao analisar CSV: {e}")
            return {}

    def load_state(self) -> dict:
        """
        Carrega o estado salvo do processo de unfollow
        """
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logging.error(f"Erro ao carregar estado: {e}")

        return {
            'non_followers': [],
            'processed_count': 0,
            'last_run': None,
            'total_to_process': 0
        }

    def save_state(self, state: dict):
        """
        Salva o estado atual do processo
        """
        try:
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(state, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logging.error(f"Erro ao salvar estado: {e}")

    def update_non_followers_list(self, use_csv: bool = True, filter_mode: str = 'normal'):
        """
        Atualiza a lista de não-seguidores com análise de imunidade e salva em CSV

        Args:
            use_csv: Se deve usar análise CSV
            filter_mode: 'normal', 'aggressive', ou 'custom'
        """
        logging.info("Atualizando lista de não-seguidores...")

        following = self.get_following()
        followers = self.get_followers()
        non_followers = self.find_non_followers(following, followers)

        # Salvar dados em CSV com análise de imunidade
        if use_csv:
            print("🔄 Analisando perfis e salvando em CSV...")
            csv_filename = self.save_non_followers_to_csv(non_followers)

            if csv_filename:
                # Criar configuração de filtro baseada no modo
                if filter_mode == 'aggressive':
                    filter_config = self.create_smart_filter_config(aggressive=True)
                    print("🔥 Modo agressivo: Filtros rigorosos aplicados")
                elif filter_mode == 'normal':
                    filter_config = self.create_smart_filter_config(aggressive=False)
                    print("⚖️ Modo normal: Filtros balanceados aplicados")
                else:
                    filter_config = None  # Usar padrão

                # Carregar usuários filtrados do CSV
                filtered_non_followers = self.load_non_followers_from_csv(csv_filename, filter_config)

                # Analisar dados para estatísticas
                analysis = self.analyze_csv_data(csv_filename)

                state = self.load_state()
                state['non_followers'] = filtered_non_followers
                state['total_to_process'] = len(filtered_non_followers)
                state['last_update'] = time.strftime('%Y-%m-%d %H:%M:%S')
                state['csv_filename'] = csv_filename
                state['filter_mode'] = filter_mode
                state['analysis_stats'] = analysis

                self.save_state(state)

                print(f"\n🎯 RESULTADO FINAL:")
                print(f"   Usuários filtrados para unfollow: {len(filtered_non_followers)}")
                print(f"   Arquivo CSV: {csv_filename}")

                logging.info(f"Lista filtrada atualizada: {len(filtered_non_followers)} usuários para dar unfollow")

                return csv_filename

        # Fallback para método original
        state = self.load_state()
        state['non_followers'] = list(non_followers)
        state['total_to_process'] = len(non_followers)
        state['last_update'] = time.strftime('%Y-%m-%d %H:%M:%S')

        self.save_state(state)
        self.save_report(following, followers, non_followers)

        logging.info(f"Lista atualizada: {len(non_followers)} usuários para dar unfollow")
        return None

    def scheduled_unfollow(self):
        """
        Executa unfollow agendado de 10 usuários
        """
        if not self.running:
            return

        logging.info("=== EXECUÇÃO AGENDADA DE UNFOLLOW ===")

        state = self.load_state()
        non_followers = state.get('non_followers', [])
        processed_count = state.get('processed_count', 0)

        if not non_followers:
            logging.info("Lista de não-seguidores vazia. Atualizando...")
            self.update_non_followers_list()
            state = self.load_state()
            non_followers = state.get('non_followers', [])

        if not non_followers:
            logging.info("Nenhum usuário para dar unfollow. Todos te seguem de volta! 🎉")
            return

        # Pegar próximos 20 usuários para unfollow
        batch_size = 20
        start_idx = processed_count
        end_idx = min(start_idx + batch_size, len(non_followers))

        if start_idx >= len(non_followers):
            logging.info("Todos os unfollows foram processados! Atualizando lista...")
            self.update_non_followers_list()
            state = self.load_state()
            state['processed_count'] = 0
            self.save_state(state)
            return

        batch_to_process = non_followers[start_idx:end_idx]

        logging.info(f"Processando lote {start_idx//batch_size + 1}: usuários {start_idx+1} a {end_idx} de {len(non_followers)}")

        # Verificar se temos dados CSV para evitar re-análise
        state = self.load_state()
        has_csv_data = state.get('csv_filename') and os.path.exists(state.get('csv_filename', ''))

        # Executar unfollows (com ou sem análise de imunidade)
        success_count = 0
        immune_count = 0
        user_info = self.get_user_info(batch_to_process)

        for user_id in batch_to_process:
            if not self.running:
                break

            user_data = user_info.get(user_id, {
                'id': user_id,
                'username': 'unknown',
                'name': 'Unknown',
                'description': '',
                'location': ''
            })
            username = user_data['username']
            name = user_data['name']

            # Se temos dados CSV, os usuários já foram filtrados, então não precisamos re-analisar
            if has_csv_data:
                logging.info(f"Dando unfollow em: @{username} ({name}) [Pré-filtrado via CSV]")
                print(f"Dando unfollow em: @{username} [Filtrado]")
            else:
                # Verificar imunidade apenas se não temos dados CSV
                is_immune, reason = self.immunity_analyzer.is_immune(user_data)

                if is_immune:
                    immune_count += 1
                    logging.info(f"🛡️ IMUNE: @{username} ({name}) - {reason}")
                    print(f"🛡️ IMUNE: @{username} - {reason}")

                    # Remover da lista de não-seguidores para não processar novamente
                    if user_id in state.get('non_followers', []):
                        state['non_followers'].remove(user_id)
                        state['total_to_process'] = len(state['non_followers'])
                        self.save_state(state)

                    continue

                logging.info(f"Dando unfollow em: @{username} ({name})")
                print(f"Dando unfollow em: @{username}")

            if self.unfollow_user(user_id):
                success_count += 1
                logging.info(f"✓ Unfollow realizado com sucesso em @{username}")
                print(f"✓ Unfollow realizado: @{username}")
            else:
                logging.error(f"✗ Falha ao dar unfollow em @{username}")
                print(f"✗ Falha no unfollow: @{username}")

            # Aguardar entre unfollows
            time.sleep(3)

        # Atualizar estado
        state['processed_count'] = end_idx
        state['last_run'] = time.strftime('%Y-%m-%d %H:%M:%S')
        self.save_state(state)

        # Recalcular remaining baseado no estado atualizado
        updated_state = self.load_state()
        remaining = len(updated_state.get('non_followers', [])) - updated_state.get('processed_count', 0)

        logging.info(f"Lote concluído: {success_count} unfollows realizados, {immune_count} usuários imunes encontrados")
        logging.info(f"Restam {remaining} usuários para processar")
        print(f"Lote concluído: {success_count} unfollows, {immune_count} imunes")

        if remaining > 0:
            next_run = datetime.now() + timedelta(minutes=20)
            logging.info(f"Próxima execução agendada para: {next_run.strftime('%H:%M:%S')}")

    def start_scheduled_unfollows(self, use_existing_csv: bool = True):
        """
        Inicia o sistema de unfollows agendados

        Args:
            use_existing_csv: Se deve usar CSV existente ou gerar novo
        """
        self.running = True

        # Verificar se existe CSV recente
        state = self.load_state()
        has_recent_csv = (
            use_existing_csv and
            state.get('csv_filename') and
            os.path.exists(state.get('csv_filename', ''))
        )

        if has_recent_csv:
            logging.info("Usando análise CSV existente para unfollows agendados")
            print("📊 Usando análise CSV existente")

            # Mostrar estatísticas da análise existente
            if state.get('analysis_stats'):
                stats = state['analysis_stats']
                print(f"📈 Estatísticas da análise:")
                print(f"   Non-followers analisados: {stats.get('non_followers', 0)}")
                print(f"   Usuários imunes: {stats.get('immune_users', 0)}")
                print(f"   Taxa de imunidade: {stats.get('immunity_rate', 0):.1f}%")
                print(f"   Modo de filtro: {state.get('filter_mode', 'normal')}")
        else:
            # Atualizar lista inicial com CSV
            logging.info("Gerando nova análise CSV para unfollows agendados")
            print("🔄 Gerando nova análise CSV...")
            self.update_non_followers_list(use_csv=True)

        # Agendar execução a cada 20 minutos
        schedule.every(20).minutes.do(self.scheduled_unfollow)

        # Executar primeira vez imediatamente
        self.scheduled_unfollow()

        logging.info("Sistema de unfollows agendados iniciado!")
        logging.info("Executando 20 unfollows a cada 20 minutos...")
        logging.info("Pressione Ctrl+C para parar")

        try:
            while self.running:
                schedule.run_pending()
                time.sleep(60)  # Verificar a cada minuto
        except KeyboardInterrupt:
            logging.info("Parando sistema de unfollows agendados...")
            self.running = False

    def stop_scheduled_unfollows(self):
        """
        Para o sistema de unfollows agendados
        """
        self.running = False
        schedule.clear()
        logging.info("Sistema de unfollows agendados parado")

def show_status(unfollower):
    """
    Mostra o status atual do sistema com informações do CSV
    """
    state = unfollower.load_state()

    print(f"\n{'='*60}")
    print(f"STATUS DO SISTEMA DE UNFOLLOW AUTOMÁTICO")
    print(f"{'='*60}")
    print(f"Total de não-seguidores: {state.get('total_to_process', 0)}")
    print(f"Já processados: {state.get('processed_count', 0)}")
    print(f"Restantes: {state.get('total_to_process', 0) - state.get('processed_count', 0)}")
    print(f"Última execução: {state.get('last_run', 'Nunca')}")
    print(f"Última atualização da lista: {state.get('last_update', 'Nunca')}")

    # Mostrar informações do CSV se disponível
    if state.get('csv_filename'):
        print(f"\n📊 ANÁLISE CSV:")
        print(f"Arquivo CSV: {state.get('csv_filename', 'N/A')}")
        print(f"Modo de filtro: {state.get('filter_mode', 'N/A')}")

        if state.get('analysis_stats'):
            stats = state['analysis_stats']
            print(f"Taxa de imunidade: {stats.get('immunity_rate', 0):.1f}%")
            print(f"Usuários imunes encontrados: {stats.get('immune_users', 0)}")

            if stats.get('category_stats'):
                print(f"\nCategorias principais:")
                for category, count in list(stats['category_stats'].items())[:3]:
                    print(f"  {category}: {count}")

    print(f"{'='*60}")

def main():
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
        return

    try:
        print(f"\n{'='*60}")
        print(f"🤖 TWITTER/X UNFOLLOW AUTOMÁTICO COM IA")
        print(f"{'='*60}")
        print("🔄 SEQUÊNCIA AUTOMÁTICA:")
        print("1. 📋 Extrair listas (following/followers)")
        print("2. 🤖 Analisar perfis com IA")
        print("3. 💾 Salvar dados em CSV")
        print("4. 🛡️ Filtrar usuários imunes")
        print("5. ⚡ Iniciar unfollow automático")
        print(f"{'='*60}")

        # Inicializar o unfollower
        unfollower = TwitterUnfollower(API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET, OPENROUTER_API_KEY)
        print(f"✅ Autenticado como: @{unfollower.username}")

        # ETAPA 1: Extrair listas
        print(f"\n📋 ETAPA 1: Extraindo listas...")
        following = unfollower.get_following()
        followers = unfollower.get_followers()
        non_followers = unfollower.find_non_followers(following, followers)

        print(f"   Você segue: {len(following)} usuários")
        print(f"   Te seguem: {len(followers)} usuários")
        print(f"   Não te seguem de volta: {len(non_followers)} usuários")

        if not non_followers:
            print("\n🎉 Todos os usuários que você segue também te seguem de volta!")
            print("Nenhum unfollow necessário.")
            return

        # ETAPA 2 e 3: Analisar e salvar CSV
        print(f"\n🤖 ETAPA 2-3: Analisando perfis e salvando CSV...")
        csv_filename = unfollower.save_non_followers_to_csv(non_followers)

        if not csv_filename:
            print("❌ Erro ao salvar CSV. Abortando.")
            return

        # ETAPA 4: Filtrar usuários
        print(f"\n🛡️ ETAPA 4: Aplicando filtros inteligentes...")
        filter_config = unfollower.create_smart_filter_config(aggressive=False)
        filtered_non_followers = unfollower.load_non_followers_from_csv(csv_filename, filter_config)

        # Salvar estado
        state = unfollower.load_state()
        state['non_followers'] = filtered_non_followers
        state['total_to_process'] = len(filtered_non_followers)
        state['processed_count'] = 0
        state['last_update'] = time.strftime('%Y-%m-%d %H:%M:%S')
        state['csv_filename'] = csv_filename
        state['filter_mode'] = 'normal'
        unfollower.save_state(state)

        print(f"✅ Lista filtrada: {len(filtered_non_followers)} usuários para unfollow")

        if not filtered_non_followers:
            print("\n🛡️ Todos os usuários são imunes! Nenhum unfollow será realizado.")
            return

        # ETAPA 5: Iniciar unfollow automático
        print(f"\n⚡ ETAPA 5: Iniciando unfollow automático...")
        print(f"📊 Arquivo CSV salvo: {csv_filename}")
        print(f"⏰ Sistema executará 10 unfollows a cada 1 hora")
        print(f"🛑 Pressione Ctrl+C para parar")
        print(f"{'='*60}")

        # Aguardar confirmação
        input("\nPressione ENTER para iniciar o sistema automático...")

        # Iniciar sistema automático
        unfollower.start_scheduled_unfollows(use_existing_csv=True)

    except KeyboardInterrupt:
        print("\n\n🛑 Sistema interrompido pelo usuário")
    except Exception as e:
        logging.error(f"Erro na execução principal: {e}")
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    main()
