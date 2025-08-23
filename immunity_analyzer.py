#!/usr/bin/env python3
"""
Analisador de Imunidade usando IA para proteger desenvolvedores, pesquisadores e profissionais de tech
"""

import logging
from openai import OpenAI
from typing import Dict

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
        
        # Configurar logging
        self.logger = logging.getLogger(__name__)

    def analyze_user_immunity(self, username: str, display_name: str, description: str, location: str = "") -> Dict:
        """
        Analisa se um usuário deve ser imune ao unfollow baseado em seu perfil
        
        Args:
            username: Nome de usuário (@username)
            display_name: Nome de exibição
            description: Bio/descrição do perfil
            location: Localização (opcional)
            
        Returns:
            Dict com category, immunity_status, confidence, reasoning
        """
        # Verificar cache primeiro
        cache_key = f"{username}:{description[:50]}"
        if cache_key in self.immunity_cache:
            return self.immunity_cache[cache_key]
        
        try:
            # Prompt para análise de imunidade
            prompt = f"""
Analise este perfil do Twitter/X e determine se a pessoa deve ser IMUNE ao unfollow automático.

PERFIL:
- Username: @{username}
- Nome: {display_name}
- Bio: {description}
- Localização: {location}

CRITÉRIOS DE IMUNIDADE (pessoas que devem ser PROTEGIDAS):

1. DESENVOLVEDORES/ENGENHEIROS:
   - Software engineers, developers, programmers
   - Frontend, backend, fullstack developers
   - DevOps, SRE, platform engineers
   - Mobile developers (iOS, Android)
   - Game developers

2. PESQUISADORES IA/ML/DATA:
   - Data scientists, ML engineers
   - AI researchers, PhD em CS/AI
   - Research scientists
   - Professores de CS/AI/ML

3. ACADÊMICOS:
   - Professores universitários (CS, Engineering, Math)
   - Estudantes de PhD/Mestrado em áreas técnicas
   - Pesquisadores acadêmicos

4. TECH WORKERS:
   - Funcionários de empresas tech (Google, Meta, Apple, Microsoft, etc.)
   - Startups tech, unicórnios
   - VCs focados em tech

5. TECH LEADERS:
   - CTOs, VPs of Engineering
   - Tech founders, CEOs de startups tech
   - Tech influencers reconhecidos

RESPONDA EM JSON:
{
  "category": "ENGINEER|RESEARCHER|ACADEMIC|TECH_WORKER|TECH_LEADER|OTHER",
  "immunity_status": "immune|not_immune", 
  "confidence": 0.0-1.0,
  "reasoning": "explicação breve"
}

Seja CONSERVADOR - em caso de dúvida, marque como IMUNE.
"""

            response = self.client.chat.completions.create(
                model="anthropic/claude-3.5-sonnet",
                messages=[
                    {"role": "system", "content": "Você é um especialista em análise de perfis tech. Seja conservador e proteja desenvolvedores, pesquisadores e profissionais de tecnologia."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=200,
                temperature=0.1
            )
            
            # Extrair resposta
            content = response.choices[0].message.content.strip()
            
            # Tentar parsear JSON
            import json
            try:
                result = json.loads(content)
            except:
                # Fallback se JSON inválido
                result = {
                    "category": "OTHER",
                    "immunity_status": "not_immune",
                    "confidence": 0.5,
                    "reasoning": "Erro no parsing da resposta da IA"
                }
            
            # Validar campos obrigatórios
            if not all(key in result for key in ["category", "immunity_status", "confidence"]):
                result = {
                    "category": "OTHER",
                    "immunity_status": "not_immune", 
                    "confidence": 0.5,
                    "reasoning": "Resposta incompleta da IA"
                }
            
            # Garantir que confidence está no range correto
            result["confidence"] = max(0.0, min(1.0, float(result.get("confidence", 0.5))))
            
            # Cache do resultado
            self.immunity_cache[cache_key] = result
            
            return result
            
        except Exception as e:
            self.logger.error(f"Erro na análise de IA para @{username}: {e}")
            
            # Fallback conservador em caso de erro
            fallback_result = {
                "category": "UNKNOWN",
                "immunity_status": "immune",  # Conservador: proteger em caso de erro
                "confidence": 0.3,
                "reasoning": f"Erro na análise: {str(e)}"
            }
            
            return fallback_result

    def is_tech_keyword_present(self, text: str) -> bool:
        """
        Verifica se há palavras-chave técnicas no texto (fallback simples)
        """
        if not text:
            return False
            
        text_lower = text.lower()
        
        tech_keywords = [
            # Programming
            'developer', 'engineer', 'programmer', 'coding', 'software',
            'frontend', 'backend', 'fullstack', 'devops', 'sre',
            
            # Languages/Tech
            'python', 'javascript', 'java', 'react', 'node', 'aws',
            'kubernetes', 'docker', 'tensorflow', 'pytorch',
            
            # Roles
            'cto', 'vp engineering', 'tech lead', 'senior engineer',
            'staff engineer', 'principal engineer',
            
            # AI/ML
            'machine learning', 'artificial intelligence', 'data scientist',
            'ml engineer', 'ai researcher', 'deep learning',
            
            # Academic
            'phd', 'professor', 'researcher', 'university', 'stanford',
            'mit', 'berkeley', 'carnegie mellon',
            
            # Companies
            'google', 'microsoft', 'apple', 'meta', 'amazon', 'netflix',
            'uber', 'airbnb', 'stripe', 'openai', 'anthropic'
        ]
        
        return any(keyword in text_lower for keyword in tech_keywords)

    def analyze_simple_immunity(self, username: str, display_name: str, description: str) -> Dict:
        """
        Análise simples baseada em palavras-chave (fallback quando IA não funciona)
        """
        full_text = f"{display_name} {description}".lower()
        
        if self.is_tech_keyword_present(full_text):
            return {
                "category": "TECH_RELATED",
                "immunity_status": "immune",
                "confidence": 0.7,
                "reasoning": "Palavras-chave técnicas detectadas"
            }
        else:
            return {
                "category": "OTHER", 
                "immunity_status": "not_immune",
                "confidence": 0.6,
                "reasoning": "Nenhuma palavra-chave técnica detectada"
            }

    def clear_cache(self):
        """
        Limpa o cache de análises
        """
        self.immunity_cache.clear()
        self.logger.info("Cache de análises limpo")

    def get_cache_stats(self) -> Dict:
        """
        Retorna estatísticas do cache
        """
        return {
            "cache_size": len(self.immunity_cache),
            "cached_users": list(self.immunity_cache.keys())
        }
