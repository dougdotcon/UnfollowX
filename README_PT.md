# UnfollowXBot - Sistema Inteligente Híbrido para Twitter/X

**UnfollowXBot** é um bot automático inteligente projetado para dar unfollow em usuários que não te seguem de volta no Twitter/X. Ele possui um sistema de análise híbrida usando IA (OpenRouter) para proteger desenvolvedores, pesquisadores e profissionais de tecnologia.

**🆕 Versão Híbrida:** Extensão Chrome + Análise de IA Python!

## 🚀 Características Principais

### 🆕 Sistema Híbrido (RECOMENDADO)
- 🌐 **Extensão Chrome** - Funciona perfeitamente com as mudanças atuais da interface do X.
- 🤖 **Análise de IA** - Utiliza OpenRouter para categorizar e analisar perfis.
- 🛡️ **Sistema de Imunidade** - Protege automaticamente devs, pesquisadores e acadêmicos.
- 📊 **Análise em CSV** - Logs de dados organizados e auditáveis com bios completas.
- ⚡ **Identificação Automática** - Detecta não-seguidores automaticamente.
- ⏰ **Execução Automática** - Realiza 15 unfollows a cada 25 minutos (respeitando limites).
- 🚫 **Sem API** - Não requer credenciais da API do Twitter.

### 📜 Sistema Selenium (LEGADO)
- 🌐 **Selenium Apenas** - Funciona estritamente via automação de navegador.
- 💾 **Progresso Salvo** - Pode ser pausado e retomado.
- 🔄 **Filtros Inteligentes** - Múltiplos critérios de filtragem.
- 📈 **Suporte a Grandes Volumes** - Otimizado para milhares de usuários.

## 🎯 Fluxo de Trabalho

### 🆕 Sistema Híbrido:
1. **🌐 Extensão Chrome** - Identifica não-seguidores automaticamente.
2. **📋 Coleta de Dados** - Extrai username, bio e localização dos perfis.
3. **🤖 Análise de IA** - IA analisa perfis para determinar status de imunidade.
4. **💾 CSV Completo** - Salva análise detalhada em formato CSV.
5. **🛡️ Filtros** - Remove usuários imunes automaticamente.
6. **⚡ Unfollow Inteligente** - Executa unfollows seletivos via extensão.

### 📜 Sistema Legado:
1. **🌐 Coleta via Selenium** - Extrai listas de seguindo/seguidores.
2. **📋 Extração de Bio** - Coleta bios, localização e dados completos.
3. **🤖 Análise de IA** - Analisa perfis para imunidade.
4. **💾 Exportação CSV** - Salva dados em CSV.
5. **🛡️ Filtros** - Remove perfis protegidos.
6. **⚡ Unfollow Selenium** - Executa via automação do navegador.

## 📦 Instalação

bash
# Instalar dependências
pip install -r requirements.txt --force-reinstall


## ⚙️ Configuração

### 1. Pré-requisitos

- **Navegador**: Chrome ou Brave instalado.
- **Login**: Estar logado no Twitter/X no navegador.
- **OpenRouter**: Chave de API para análise de IA.

### 2. Configurar Variáveis de Ambiente

bash
# Copiar arquivo de exemplo
cp .env.example .env

# Editar com suas credenciais
nano .env


### 3. Preencher Credenciais no .env

bash
# OpenRouter é o ÚNICO requisito (Sem API do Twitter!)
OPENROUTER_API_KEY=sua_chave_openrouter_aqui

# Configurações opcionais
BROWSER=chrome
HEADLESS=false
MAX_FOLLOWING=5000
MAX_FOLLOWERS=5000


### 4. Obter Credenciais

- **OpenRouter API**: [openrouter.ai](https://openrouter.ai/) (Único requisito)

## 🚀 Uso Rápido

### 🆕 Sistema Híbrido (Recomendado)

#### Execução Automática
bash
python twitter_hybrid_bot.py


#### Configuração da Extensão
1. Abra Chrome/Brave e vá para `chrome://extensions/`
2. Ative o "Modo Desenvolvedor"
3. Clique em "Carregar sem empacotar" e selecione a pasta `extension`.
4. Fixe a extensão na barra de ferramentas.

### 📜 Sistema Selenium (Legado)

#### Dar Unfollow em Não-Seguidores
bash
python bot.py


#### Analisar Usuário via IA (Linha de Comando)
bash
python analyze.py --username @usuario


## 🛡️ Lógica de Proteção

A IA analisa a bio e metadados do usuário em busca de palavras-chave que indiquem que são:
- Desenvolvedores (`dev`, `engineer`, `software`)
- Pesquisadores (`research`, `PhD`, `science`)
- Acadêmicos (`professor`, `universidade`, `academic`)
- Profissionais de Tech (`CTO`, `tech`, `IA`)

Esses perfis são automaticamente marcados como **IMUNES** e excluídos da lista de unfollow.

## ⚠️ Notas Importantes

- **Limites de Taxa**: O bot respeita os limites do X (aprox. 15 unfollows/hora).
- **Segurança**: Use a análise de IA para evitar "queimar pontes" com conexões valiosas.
- **Legalidade**: Este bot cumpre os Termos de Serviço do X ao usar automação de navegador em vez de acesso não autorizado à API.

## 🤝 Contribuindo

Contribuições são bem-vindas! Abra uma issue ou pull request.

## 📜 Licença

Licença MIT. Use com responsabilidade.
