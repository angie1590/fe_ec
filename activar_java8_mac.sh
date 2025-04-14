#!/bin/bash

set -e

echo "🔧 Instalando jenv y Java 8 (Temurin)..."

# Detectar shell
SHELL_RC="$HOME/.zshrc"
if [[ "$SHELL" == *"bash"* ]]; then
  SHELL_RC="$HOME/.bashrc"
fi

# 1. Instalar jenv si no está instalado
if ! command -v jenv &> /dev/null; then
  echo "📦 Instalando jenv..."
  brew install jenv
else
  echo "✅ jenv ya está instalado."
fi

# 2. Instalar Temurin 8 si no existe
if [ ! -d "/Library/Java/JavaVirtualMachines/temurin-8.jdk" ]; then
  echo "📦 Instalando Temurin Java 8..."
  brew install --cask temurin@8
else
  echo "✅ Temurin Java 8 ya está instalado."
fi

# 3. Registrar Java 8 en jenv
JDK_PATH="/Library/Java/JavaVirtualMachines/temurin-8.jdk/Contents/Home"
mkdir -p ~/.jenv/versions
if ! jenv versions | grep -q "1.8"; then
  echo "➕ Registrando Java 8 en jenv..."
  jenv add "$JDK_PATH"
else
  echo "✅ Java 8 ya está registrado en jenv."
fi

# 4. Configurar como global
echo "🌍 Configurando Java 8 como versión global..."
jenv global 1.8

# 5. Asegurar configuración en el shell
if ! grep -q 'jenv init -' "$SHELL_RC"; then
  echo "🔧 Configurando jenv en $SHELL_RC..."
  echo '' >> "$SHELL_RC"
  echo 'export PATH="$HOME/.jenv/bin:$PATH"' >> "$SHELL_RC"
  echo 'eval "$(jenv init -)"' >> "$SHELL_RC"
fi

# 6. Recargar configuración del shell
echo "🔄 Recargando $SHELL_RC..."
source "$SHELL_RC"

# 7. Verificar versión
echo "🧪 Versión activa de Java:"
java -version

echo "✅ Instalación y configuración completa de Java 8 con jenv."
