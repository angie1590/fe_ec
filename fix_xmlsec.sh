#!/bin/bash

# Activar entorno virtual de Poetry
VENV_PATH=$(poetry env info --path)
source "$VENV_PATH/bin/activate"

# Configurar las rutas de las bibliotecas instaladas con Homebrew
export LDFLAGS="-L$(brew --prefix libxml2)/lib -L$(brew --prefix libxmlsec1)/lib"
export CFLAGS="-I$(brew --prefix libxml2)/include -I$(brew --prefix libxmlsec1)/include"
export PKG_CONFIG_PATH="$(brew --prefix libxml2)/lib/pkgconfig:$(brew --prefix libxmlsec1)/lib/pkgconfig"

# Reinstalar xmlsec desde fuente para garantizar compatibilidad
pip uninstall -y xmlsec
pip install --no-binary=:all: xmlsec

# Validar que todo funcione
python -c "import xmlsec; import lxml; print('✅ Todo bien con xmlsec y lxml')"