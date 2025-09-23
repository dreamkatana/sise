#!/usr/bin/env python
"""
WSGI entry point for SISE Flask application
"""

import os
from app import create_app

# Carrega configuração baseada na variável de ambiente
config_name = 'Production' if os.getenv('FLASK_ENV') == 'production' else 'Debug'
app = create_app(config_name)

if __name__ == "__main__":
    app.run()