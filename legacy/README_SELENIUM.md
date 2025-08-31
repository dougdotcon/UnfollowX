# Twitter Unfollow Automático com Selenium

## 🚀 Solução para Limitações da API

Este script usa Selenium para contornar as limitações da API gratuita do Twitter/X, permitindo coletar listas de followers/following diretamente do navegador.

## 📋 Pré-requisitos

1. **Dependências Python:**
   ```bash
   pip install selenium webdriver-manager>=3.5.0
   ```

2. **Credenciais necessárias:**
   - **Para login no Twitter:** Email/username e senha
   - **Para API (unfollow):** Chaves da API do Twitter (mesmo com limitações)
   - **Para IA:** Chave da OpenRouter

## 🔧 Configuração

1. **Configure o arquivo .env:**
   ```env
   # API do Twitter (necessária para unfollow, mesmo com limitações)
   TWITTER_API_KEY=sua_api_key
   TWITTER_API_SECRET=sua_api_secret
   TWITTER_ACCESS_TOKEN=seu_access_token
   TWITTER_ACCESS_TOKEN_SECRET=seu_access_token_secret
   
   # OpenRouter para análise de IA
   OPENROUTER_API_KEY=sua_openrouter_key
   ```

2. **Faça login no Twitter/X no seu navegador:**
   - Abra Chrome ou Brave
   - Acesse https://x.com e faça login
   - Mantenha o navegador aberto

## 🚀 Como usar

### Teste rápido (Recomendado primeiro)
```bash
python test_selenium_simple.py
```

### Modo Selenium Completo
```bash
python twitter_unfollow_selenium.py
```

O script irá:
1. 🌐 Usar seu navegador já logado (Chrome/Brave)
2. 📋 Coletar listas de following/followers via scraping
3. 🤖 Analisar perfis com IA
4. 🛡️ Aplicar filtros de imunidade
5. ⚡ Executar unfollow automático via API

### Vantagens do Selenium:
- ✅ Contorna limitações da API gratuita
- ✅ Coleta dados diretamente do site
- ✅ Não requer upgrade da API
- ✅ Funciona com contas gratuitas
- ✅ Usa seu navegador já logado (sem precisar inserir credenciais)
- ✅ Suporta Chrome e Brave

### Limitações:
- ⏳ Mais lento que a API
- 🖥️ Requer navegador (Chrome/Brave)
- 🔐 Precisa estar logado no navegador

## 🛡️ Segurança

- O script usa delays entre ações para evitar detecção
- Credenciais de login não são salvas
- Dados coletados são salvos localmente em CSV
- Rate limiting automático

## 📊 Arquivos gerados

- `following_selenium.csv` - Lista de quem você segue
- `followers_selenium.csv` - Lista de seus seguidores
- `non_followers_analysis_YYYYMMDD_HHMMSS.csv` - Análise completa
- `twitter_unfollow_selenium.log` - Log detalhado

## 🔧 Troubleshooting

### Erro de login:
- Verifique email/username e senha
- Desative 2FA temporariamente
- Use email em vez de username

### Navegador não abre:
- Instale/atualize o Chrome
- Execute: `pip install --upgrade webdriver-manager`

### Coleta lenta:
- Normal para listas grandes
- Ajuste `max_collect` no código se necessário

## ⚙️ Configurações avançadas

No arquivo `twitter_unfollow_selenium.py`, você pode ajustar:

```python
# Modo headless (sem interface gráfica)
scraper = TwitterSeleniumScraper(headless=True)

# Limite de coleta
max_collect = 1000  # Ajuste conforme necessário
```

## 🆘 Suporte

Se encontrar problemas:
1. Verifique o arquivo de log
2. Teste com modo headless=False para debug visual
3. Verifique se todas as dependências estão instaladas
