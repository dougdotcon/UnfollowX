#!/usr/bin/env python3
"""
Script de configuração inicial para o Twitter Unfollow Bot
"""

import os
import shutil
import subprocess
import sys

def check_python_version():
    """Verifica se a versão do Python é compatível"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ é necessário")
        print(f"   Versão atual: {sys.version}")
        return False
    print(f"✅ Python {sys.version.split()[0]} - OK")
    return True

def install_dependencies():
    """Instala as dependências do requirements.txt"""
    print("\n📦 Instalando dependências...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependências instaladas com sucesso")
        return True
    except subprocess.CalledProcessError:
        print("❌ Erro ao instalar dependências")
        return False

def setup_env_file():
    """Configura o arquivo .env"""
    print("\n⚙️ Configurando arquivo .env...")
    
    if os.path.exists('.env'):
        response = input("📝 Arquivo .env já existe. Sobrescrever? (s/N): ").lower()
        if response not in ['s', 'sim', 'y', 'yes']:
            print("📄 Mantendo arquivo .env existente")
            return True
    
    if not os.path.exists('.env.example'):
        print("❌ Arquivo .env.example não encontrado")
        return False
    
    try:
        shutil.copy('.env.example', '.env')
        print("✅ Arquivo .env criado a partir do .env.example")
        print("\n📝 PRÓXIMO PASSO:")
        print("   1. Edite o arquivo .env com suas credenciais")
        print("   2. Obtenha credenciais em:")
        print("      • Twitter/X: https://developer.twitter.com/")
        print("      • OpenRouter: https://openrouter.ai/")
        return True
    except Exception as e:
        print(f"❌ Erro ao criar .env: {e}")
        return False

def check_env_file():
    """Verifica se o arquivo .env está configurado"""
    print("\n🔍 Verificando configuração...")
    
    if not os.path.exists('.env'):
        print("❌ Arquivo .env não encontrado")
        return False
    
    required_vars = [
        'TWITTER_API_KEY',
        'TWITTER_API_SECRET', 
        'TWITTER_ACCESS_TOKEN',
        'TWITTER_ACCESS_TOKEN_SECRET',
        'OPENROUTER_API_KEY'
    ]
    
    missing_vars = []
    with open('.env', 'r') as f:
        content = f.read()
        for var in required_vars:
            if f"{var}=your_" in content or f"{var}=" not in content:
                missing_vars.append(var)
    
    if missing_vars:
        print(f"⚠️ Variáveis não configuradas: {', '.join(missing_vars)}")
        print("📝 Edite o arquivo .env com suas credenciais reais")
        return False
    
    print("✅ Arquivo .env configurado")
    return True

def main():
    """Função principal de setup"""
    print("🚀 SETUP - Twitter/X Unfollow Bot com IA")
    print("=" * 50)
    
    # Verificar Python
    if not check_python_version():
        return
    
    # Instalar dependências
    if not install_dependencies():
        return
    
    # Configurar .env
    if not setup_env_file():
        return
    
    # Verificar configuração
    env_configured = check_env_file()
    
    print("\n" + "=" * 50)
    print("📋 RESUMO DO SETUP:")
    print("✅ Python - OK")
    print("✅ Dependências - OK")
    print("✅ Arquivo .env - Criado")
    
    if env_configured:
        print("✅ Credenciais - Configuradas")
        print("\n🚀 PRONTO PARA USO!")
        print("   Execute: python twitter_unfollow_auto.py")
    else:
        print("⚠️ Credenciais - Pendentes")
        print("\n📝 PRÓXIMOS PASSOS:")
        print("   1. Edite o arquivo .env")
        print("   2. Execute: python twitter_unfollow_auto.py")
    
    print("=" * 50)

if __name__ == "__main__":
    main()
