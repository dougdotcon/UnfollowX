# Sistema Selenium Legado

Esta pasta contém o sistema original baseado puramente em Selenium que foi substituído pelo sistema híbrido.

## Arquivos do Sistema Legado:

### Scripts Principais:
- `main_selenium_only.py` - Script principal de execução única
- `twitter_unfollow_auto.py` - Script de execução automática
- `twitter_selenium_only.py` - Módulo principal do sistema
- `twitter_selenium.py` - Módulo base de scraping Selenium

### Scripts de Teste:
- `test_selenium_simple.py` - Teste simples do sistema
- `test_selenium_system.py` - Teste completo do sistema

### Documentação:
- `README_SELENIUM.md` - Documentação original do sistema Selenium

## Status do Sistema Legado

⚠️ **ATENÇÃO:** Este sistema pode não funcionar devido às mudanças recentes do Twitter/X.

### Problemas Conhecidos:
- Seletores CSS podem estar desatualizados
- Rate limiting mais rigoroso do X
- Mudanças na estrutura DOM da página

### Por que foi substituído:
1. **Compatibilidade:** X mudou estrutura, quebrando seletores
2. **Performance:** Sistema híbrido é mais rápido
3. **Confiabilidade:** Extensão Chrome é mais estável
4. **Manutenção:** Código híbrido é mais fácil de manter

## Migração para Sistema Híbrido

Para migrar do sistema legado para o híbrido, execute:

```bash
python migrate_to_hybrid.py
```

Este script irá:
- Fazer backup dos dados existentes
- Migrar configurações compatíveis
- Configurar o novo sistema híbrido

## Uso do Sistema Legado (Não Recomendado)

Se precisar usar o sistema legado por algum motivo:

```bash
# Execução única
python legacy/main_selenium_only.py

# Execução automática
python legacy/twitter_unfollow_auto.py
```

**Recomendação:** Use o sistema híbrido atual que está na raiz do projeto.
