from app import create_app
from flask import url_for

app = create_app('Production')
with app.app_context():
    print('=== TESTE DE URLs ===')
    print('Auth logout URL (relative):', url_for('auth.logout'))
    print('Auth logout URL (external):', url_for('auth.logout', _external=True))
    print('LMS logout_ajax URL:', url_for('lms.logout_ajax'))
    print()
    print('=== CONFIG ===')
    print('APPLICATION_ROOT:', app.config.get('APPLICATION_ROOT'))
    print('SERVER_NAME:', app.config.get('SERVER_NAME'))
    print()
    print('=== ROTAS REGISTRADAS ===')
    for rule in app.url_map.iter_rules():
        if 'logout' in rule.rule:
            print(f'Route: {rule.rule} -> {rule.endpoint}')
    print()
    print('=== BLUEPRINTS ===')
    for blueprint_name, blueprint in app.blueprints.items():
        print(f'Blueprint: {blueprint_name} -> {blueprint.url_prefix}')