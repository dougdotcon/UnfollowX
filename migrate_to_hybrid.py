#!/usr/bin/env python3
"""
Script de migração do sistema Selenium para o Sistema Híbrido
Facilita a transição e preserva dados existentes
"""

import os
import json
import shutil
from datetime import datetime
from pathlib import Path

def backup_existing_data():
    """
    Faz backup dos dados existentes do sistema Selenium
    """
    print("🔄 Fazendo backup dos dados existentes...")
    
    backup_dir = f"backup_selenium_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    os.makedirs(backup_dir, exist_ok=True)
    
    files_to_backup = [
        'selenium_unfollow_state.json',
        'twitter_selenium_only.log',
        'twitter_selenium_auto.log',
        'analysis_progress.json'
    ]
    
    csv_files = list(Path('.').glob('selenium_analysis_*.csv'))
    
    backed_up = []
    
    for file_path in files_to_backup:
        if os.path.exists(file_path):
            shutil.copy2(file_path, backup_dir)
            backed_up.append(file_path)
    
    for csv_file in csv_files:
        shutil.copy2(csv_file, backup_dir)
        backed_up.append(str(csv_file))
    
    if backed_up:
        print(f"✅ Backup criado em: {backup_dir}")
        print(f"📁 Arquivos salvos: {len(backed_up)}")
        for file in backed_up:
            print(f"   - {file}")
    else:
        print("ℹ️ Nenhum arquivo de dados antigo encontrado")
    
    return backup_dir

def check_hybrid_dependencies():
    """
    Verifica se as dependências do sistema híbrido estão instaladas
    """
    print("\n🔍 Verificando dependências do sistema híbrido...")
    
    try:
        import selenium
        print("✅ Selenium instalado")
    except ImportError:
        print("❌ Selenium não encontrado")
        return False
    
    try:
        from webdriver_manager.chrome import ChromeDriverManager
        print("✅ WebDriver Manager instalado")
    except ImportError:
        print("❌ WebDriver Manager não encontrado")
        return False
    
    try:
        import openai
        print("✅ OpenAI instalado")
    except ImportError:
        print("❌ OpenAI não encontrado")
        return False
    
    try:
        from dotenv import load_dotenv
        print("✅ Python-dotenv instalado")
    except ImportError:
        print("❌ Python-dotenv não encontrado")
        return False
    
    return True

def check_openrouter_config():
    """
    Verifica se a configuração do OpenRouter está presente
    """
    print("\n🔑 Verificando configuração OpenRouter...")
    
    from dotenv import load_dotenv
    load_dotenv()
    
    openrouter_key = os.getenv('OPENROUTER_API_KEY')
    
    if openrouter_key:
        print("✅ OPENROUTER_API_KEY encontrada no .env")
        return True
    else:
        print("❌ OPENROUTER_API_KEY não encontrada")
        print("💡 Adicione sua chave no arquivo .env:")
        print("   OPENROUTER_API_KEY=sua_chave_aqui")
        return False

def migrate_state_data():
    """
    Migra dados de estado do sistema Selenium para o híbrido (se existir)
    """
    print("\n📋 Verificando dados de estado para migração...")
    
    selenium_state_file = 'selenium_unfollow_state.json'
    hybrid_state_file = 'hybrid_unfollow_state.json'
    
    if os.path.exists(selenium_state_file):
        try:
            with open(selenium_state_file, 'r', encoding='utf-8') as f:
                selenium_state = json.load(f)
            
            # Adaptar estrutura para sistema híbrido
            hybrid_state = {
                'migrated_from_selenium': True,
                'migration_date': datetime.now().isoformat(),
                'original_selenium_state': selenium_state,
                'hybrid_state': {
                    'last_execution': None,
                    'total_analyzed': selenium_state.get('analyzed_count', 0),
                    'total_unfollowed': selenium_state.get('total_unfollowed', 0)
                }
            }
            
            with open(hybrid_state_file, 'w', encoding='utf-8') as f:
                json.dump(hybrid_state, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Estado migrado para: {hybrid_state_file}")
            print(f"📊 Dados preservados:")
            print(f"   - Analisados: {selenium_state.get('analyzed_count', 0)}")
            print(f"   - Unfollows: {selenium_state.get('total_unfollowed', 0)}")
            
        except Exception as e:
            print(f"⚠️ Erro na migração do estado: {e}")
            print("ℹ️ O sistema híbrido funcionará normalmente sem os dados antigos")
    else:
        print("ℹ️ Nenhum estado anterior encontrado")

def setup_hybrid_config():
    """
    Configura arquivos de configuração do sistema híbrido
    """
    print("\n⚙️ Configurando sistema híbrido...")
    
    # Verificar se config exemplo existe
    if os.path.exists('config_hybrid_example.env'):
        print("✅ Arquivo de configuração exemplo encontrado")
        
        if not os.path.exists('.env'):
            print("📝 Criando arquivo .env baseado no exemplo...")
            shutil.copy2('config_hybrid_example.env', '.env')
            print("⚠️ IMPORTANTE: Edite o arquivo .env e configure sua OPENROUTER_API_KEY")
        else:
            print("ℹ️ Arquivo .env já existe")
    
    print("✅ Configuração do sistema híbrido concluída")

def test_hybrid_system():
    """
    Testa se o sistema híbrido pode ser inicializado
    """
    print("\n🧪 Testando sistema híbrido...")
    
    try:
        from twitter_hybrid_unfollow import TwitterHybridUnfollower
        from dotenv import load_dotenv
        
        load_dotenv()
        openrouter_key = os.getenv('OPENROUTER_API_KEY')
        
        if not openrouter_key:
            print("❌ Teste falhou: OPENROUTER_API_KEY não configurada")
            return False
        
        # Teste de inicialização (sem executar)
        unfollower = TwitterHybridUnfollower(
            openrouter_api_key=openrouter_key,
            headless=True
        )
        
        print("✅ Sistema híbrido inicializado com sucesso")
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        return False

def main():
    """
    Executa a migração completa
    """
    print("="*70)
    print("🔄 MIGRAÇÃO PARA SISTEMA HÍBRIDO")
    print("="*70)
    print("Este script irá:")
    print("1. Fazer backup dos dados existentes")
    print("2. Verificar dependências")
    print("3. Configurar sistema híbrido")
    print("4. Migrar dados de estado")
    print("5. Testar nova configuração")
    print("="*70)
    
    confirm = input("\nDeseja continuar com a migração? [y/N]: ").strip().lower()
    if confirm not in ['y', 'yes', 's', 'sim']:
        print("👋 Migração cancelada")
        return
    
    # 1. Backup
    backup_dir = backup_existing_data()
    
    # 2. Verificar dependências
    if not check_hybrid_dependencies():
        print("\n❌ Dependências faltando. Execute:")
        print("pip install -r requirements.txt --force-reinstall")
        return
    
    # 3. Verificar OpenRouter
    openrouter_ok = check_openrouter_config()
    
    # 4. Configurar sistema
    setup_hybrid_config()
    
    # 5. Migrar estado
    migrate_state_data()
    
    # 6. Testar sistema
    if openrouter_ok:
        system_ok = test_hybrid_system()
    else:
        system_ok = False
    
    # Resultados finais
    print("\n" + "="*70)
    print("📊 RESULTADOS DA MIGRAÇÃO")
    print("="*70)
    
    if backup_dir:
        print(f"✅ Backup criado: {backup_dir}")
    
    print("✅ Dependências verificadas")
    
    if openrouter_ok and system_ok:
        print("✅ Sistema híbrido configurado e testado")
        print("\n🚀 PRÓXIMOS PASSOS:")
        print("1. Execute o sistema híbrido:")
        print("   python main_hybrid.py")
        print("2. Ou configure execução automática:")
        print("   python twitter_hybrid_auto.py")
    else:
        print("⚠️ Configuração incompleta")
        print("\n🔧 AÇÕES NECESSÁRIAS:")
        if not openrouter_ok:
            print("1. Configure OPENROUTER_API_KEY no arquivo .env")
        print("2. Execute novamente este script após corrigir")
    
    print("\n📚 DOCUMENTAÇÃO:")
    print("- README.md atualizado com instruções do sistema híbrido")
    print("- Seção '🆕 Sistema Híbrido (RECOMENDADO)' no README")
    
    print("="*70)

if __name__ == "__main__":
    main()
