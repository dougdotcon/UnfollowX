# Twitter/X Unfollow Bot com IA - SELENIUM ONLY

Bot automático inteligente para dar unfollow em usuários que não te seguem de volta no Twitter/X, com análise de IA para proteger desenvolvedores, pesquisadores e profissionais de tech.

**🆕 NOVA VERSÃO: Funciona apenas com Selenium - NÃO requer API do Twitter!**

## 🚀 Características Principais

- 🌐 **Selenium Only** - Funciona apenas com navegador (Chrome/Brave)
- 🚫 **Sem API** - Não requer credenciais da API do Twitter
- 🤖 **Análise de IA** - OpenRouter para categorizar perfis
- 🛡️ **Sistema de Imunidade** - Protege devs, pesquisadores, acadêmicos
- 📊 **Análise em CSV** - Dados organizados e auditáveis com bio completa
- ⏰ **Execução Automática** - 20 unfollows a cada 20 minutos
- 💾 **Progresso Salvo** - Pode ser pausado e retomado
- 🔄 **Filtros Inteligentes** - Múltiplos critérios de filtragem
- 📈 **Suporte a Grandes Volumes** - Otimizado para milhares de usuários

## 🎯 Fluxo Automático

1. **🌐 Coleta via Selenium** - Extrai listas de following/followers do navegador
2. **📋 Extração de Bio** - Coleta bio, localização e dados completos de cada perfil
3. **🤖 Análise de IA** - IA analisa cada perfil para determinar imunidade
4. **💾 CSV Completo** - Salva análise detalhada em formato CSV
5. **🛡️ Filtros** - Remove usuários imunes automaticamente
6. **⚡ Unfollow Selenium** - Executa unfollows via navegador

## 📦 Instalação

```bash
# Instalar dependências
pip install -r requirements.txt --force-reinstall
```

## ⚙️ Configuração

### 1. Pré-requisitos

- **Navegador**: Chrome ou Brave instalado
- **Login**: Estar logado no Twitter/X no navegador
- **OpenRouter**: Chave da API para análise de IA

### 2. Configurar Variáveis de Ambiente

```bash
# Copiar arquivo de exemplo
cp .env.example .env

# Editar com suas credenciais
nano .env  # ou use seu editor preferido
```

### 3. Preencher Credenciais no .env

```bash
# APENAS OpenRouter é necessário (sem API do Twitter!)
OPENROUTER_API_KEY=sua_openrouter_key_aqui

# Configurações opcionais
BROWSER=chrome
HEADLESS=false
MAX_FOLLOWING=5000
MAX_FOLLOWERS=5000
```

### 4. Obter Credencial

- **OpenRouter API**: [openrouter.ai](https://openrouter.ai/) (ÚNICO requisito)

## 🚀 Uso Rápido

### Execução Automática (Recomendado)
```bash
python twitter_unfollow_auto.py
```

### Execução Única Completa
```bash
python main_selenium_only.py
```

### Teste Rápido
```bash
python test_selenium_simple.py
```

### Verificar Status
```bash
python status.py
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

- `selenium_analysis_YYYYMMDD_HHMMSS.csv` - Análise completa com IA e bio
- `selenium_unfollow_state.json` - Estado e progresso do sistema
- `twitter_selenium_auto.log` - Logs detalhados
- `analysis_progress.json` - Progresso da análise (temporário)

## 📈 Exemplo de CSV Gerado

| username | bio | location | category | immunity_status | confidence | reasoning |
|----------|-----|----------|----------|----------------|------------|-----------|
| johndoe | Software Engineer at Google | San Francisco | ENGINEER | immune | 0.95 | Tech professional |
| janedoe | Marketing Manager | New York | OTHER | not_immune | 0.80 | Non-tech profile |

## 🔧 Vantagens do Selenium

- ✅ **Sem limitações de API** - Funciona com conta gratuita
- ✅ **Bio completa** - Extrai descrição, localização, verificação
- ✅ **Grandes volumes** - Suporta milhares de usuários (suas 5.268 pessoas)
- ✅ **Progresso salvo** - Retoma de onde parou em caso de interrupção
- ✅ **Análise detalhada** - Dados completos para melhor categorização

## ⚠️ Segurança

- ✅ Rate limiting automático entre ações
- ✅ Delays inteligentes para evitar detecção
- ✅ Salva progresso para recuperação
- ✅ Sistema de lotes para grandes volumes
- ✅ Logs detalhados para auditoria
- ✅ Usa navegador já logado (sem credenciais expostas)

## 📋 Requisitos

- Python 3.8+
- Chrome ou Brave instalado
- Estar logado no Twitter/X no navegador
- Chave API do OpenRouter
- Dependências: `selenium`, `webdriver-manager`, `pandas`, `openai`, `schedule`, `python-dotenv`

## 🔒 Segurança das Credenciais

- ✅ Apenas OpenRouter API necessária (armazenada em `.env`)
- ✅ Sem credenciais do Twitter expostas
- ✅ Usa navegador já logado (sessão existente)
- ✅ Arquivo `.env.example` como template
- ✅ `.gitignore` protege dados sensíveis

## 🆘 Troubleshooting

### Navegador não abre:
- Instale/atualize Chrome ou Brave
- Execute: `pip install --upgrade webdriver-manager`

### Coleta lenta:
- Normal para grandes listas (suas 5.268 pessoas)
- Sistema otimizado com progresso salvo
- Pode ser pausado e retomado

### Erro de login:
- Certifique-se de estar logado no Twitter/X
- Use o navegador padrão configurado

## ⚖️ Aviso Legal

Use responsavelmente e respeite os termos de serviço do Twitter/X. O sistema foi projetado para ser conservador e proteger usuários relevantes. Funciona apenas com navegador, sem violar limitações de API.
