# Twitter/X Unfollow Bot com IA

Bot automático inteligente para dar unfollow em usuários que não te seguem de volta no Twitter/X, com análise de IA para proteger desenvolvedores, pesquisadores e profissionais de tech.

## 🚀 Características Principais

- ✅ **API v2 do Twitter/X** - Usa a API mais recente
- 🤖 **Análise de IA** - OpenRouter para categorizar perfis
- 🛡️ **Sistema de Imunidade** - Protege devs, pesquisadores, acadêmicos
- 📊 **Análise em CSV** - Dados organizados e auditáveis
- ⏰ **Execução Automática** - 20 unfollows a cada 20 minutos
- 💾 **Progresso Salvo** - Pode ser pausado e retomado
- 🔄 **Filtros Inteligentes** - Múltiplos critérios de filtragem

## 🎯 Fluxo Automático

1. **📋 Extração** - Obtém listas de following/followers
2. **🤖 Análise** - IA analisa cada perfil (bio, localização, etc.)
3. **💾 CSV** - Salva análise completa em formato CSV
4. **🛡️ Filtros** - Remove usuários imunes automaticamente
5. **⚡ Unfollow** - Executa unfollows de forma agendada

## 📦 Instalação

```bash
# Instalar dependências
pip install -r requirements.txt --force-reinstall
```

## ⚙️ Configuração

### 1. Configurar Variáveis de Ambiente

```bash
# Copiar arquivo de exemplo
cp .env.example .env

# Editar com suas credenciais
nano .env  # ou use seu editor preferido
```

### 2. Preencher Credenciais no .env

```bash
# Twitter/X API Credentials
TWITTER_API_KEY=sua_api_key_aqui
TWITTER_API_SECRET=sua_api_secret_aqui
TWITTER_ACCESS_TOKEN=seu_access_token_aqui
TWITTER_ACCESS_TOKEN_SECRET=seu_access_token_secret_aqui

# OpenRouter API Key
OPENROUTER_API_KEY=sua_openrouter_key_aqui
```

### 3. Obter Credenciais

- **Twitter/X API**: [developer.twitter.com](https://developer.twitter.com/)
- **OpenRouter API**: [openrouter.ai](https://openrouter.ai/)

## 🚀 Uso Rápido

### Execução Automática (Recomendado)
```bash
python twitter_unfollow_auto.py
```

### Verificar Status
```bash
python status.py
```

### Modo Avançado (com menu)
```bash
python twitter_unfollow.py
```

## 🛡️ Sistema de Imunidade

A IA protege automaticamente:

- 💻 **Desenvolvedores** - Software engineers, programmers
- 🧠 **Pesquisadores IA/ML** - Data scientists, ML engineers  
- 🎓 **Acadêmicos** - Professores, estudantes de universidades renomadas
- 🏢 **Tech Workers** - Funcionários de Google, Meta, Apple, etc.
- 🚀 **Founders** - CEOs e fundadores de startups tech
- 📊 **Cientistas** - Pesquisadores acadêmicos

## 📊 Arquivos Gerados

- `non_followers_analysis_YYYYMMDD_HHMMSS.csv` - Análise completa com IA
- `unfollow_state.json` - Estado e progresso do sistema
- `twitter_unfollow_auto.log` - Logs detalhados

## 📈 Exemplo de CSV Gerado

| user_id | username | name | description | category | immunity_status | confidence |
|---------|----------|------|-------------|----------|----------------|------------|
| 123456 | johndoe | John Doe | Software Engineer at Google | ENGINEER | immune | 0.95 |
| 789012 | janedoe | Jane Doe | Marketing Manager | OTHER | not_immune | 0.80 |

## 🔧 Modos de Filtragem

- **Normal** - Filtros balanceados (recomendado)
- **Agressivo** - Filtros mais rigorosos (mais conservador)

## ⚠️ Segurança

- ✅ Rate limiting automático
- ✅ Aguarda entre unfollows (3 segundos)
- ✅ Salva progresso para recuperação
- ✅ Sistema de cache para análises
- ✅ Logs detalhados para auditoria

## 📋 Requisitos

- Python 3.8+
- Conta de desenvolvedor Twitter/X
- Chave API do OpenRouter
- Dependências: `tweepy`, `pandas`, `openai`, `schedule`, `python-dotenv`

## 🔒 Segurança das Credenciais

- ✅ Credenciais armazenadas em arquivo `.env` (não versionado)
- ✅ Arquivo `.env.example` como template
- ✅ `.gitignore` protege dados sensíveis
- ✅ Verificação automática de credenciais ao iniciar

## ⚖️ Aviso Legal

Use responsavelmente e respeite os termos de serviço do Twitter/X. O sistema foi projetado para ser conservador e proteger usuários relevantes.
