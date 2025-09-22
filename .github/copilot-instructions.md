# SISE Flask - Copilot Instructions

## Architecture Overview

SISE é uma aplicação Flask que integra autenticação via Keycloak com consultas a dados educacionais da UNICAMP. A arquitetura segue o padrão Blueprint com separação clara entre autenticação, cursos e configurações.

### Core Components

- **Authentication**: Keycloak SSO integration via `python-keycloak`
- **Database**: MariaDB com views específicas do sistema EDUCORP (`V_EDUCORP_*`)
- **Configuration**: JSON-based course ordering and admin permissions in `course_config.json`

## Critical Patterns

### Authentication Flow
- All protected routes use `@token_required` decorator from `app.auth`
- User info is stored in Flask's `g.user` after token validation
- Email from token (`g.user.get('email')`) is the primary user identifier

### Database Queries
Models use composite primary keys with `TIPCOL` and `NUMCAD`:
```python
# Example join pattern for course data
query = db.session.query(...).join(
    CursoAperfCol,
    and_(FichaCol.TIPCOL == CursoAperfCol.TIPCOL, FichaCol.NUMCAD == CursoAperfCol.NUMCAD)
)
```

### Configuration Management
- `course_config.json` controls course ordering (`codcua_order`) and admin access (`admin_emails`)
- Use `load_course_config()` and `save_course_config()` helper functions
- Admin routes check email against `admin_emails` list

### API Structure
- Auth endpoints: `/api/auth/login`, `/api/auth/protected`
- Course endpoints: `/api/courses`, `/api/admin/courses`
- All responses use JSON format with consistent error handling

## Development Setup

### Missing Configuration
The `config/config.py` file is gitignored and contains Keycloak credentials:
```python
class Config:
    KEYCLOAK_SERVER_URL = "https://your-keycloak-server"
    KEYCLOAK_CLIENT_ID = "your-client-id"
    KEYCLOAK_REALM = "your-realm"
    KEYCLOAK_CLIENT_SECRET = "your-secret"
```

### Running the Application
```powershell
# Install dependencies
pip install -r requirements.txt

# Start development server
python run.py
```

### Database Models
- `FichaCol`: Employee/student data (primary table)
- `CursoAperf`: Course definitions
- `CursoAperfCol`: Course enrollments
- `FrequenciaTurma`: Attendance records

All models represent database views (`V_EDUCORP_*`) and should not be modified structurally.

## Key Integration Points

- **Email-based authorization**: User's email from Keycloak token determines data access
- **Course filtering**: `codcua_order` in config controls which courses appear and their display order
- **Admin functions**: Course configuration management restricted by email whitelist
- **Complex joins**: Multi-table queries require careful handling of composite keys

## Common Tasks

- Adding new protected routes: Apply `@token_required` decorator and access `g.user`
- Modifying course queries: Follow existing join patterns with `and_()` for composite keys
- Admin features: Check `user_email in config.get('admin_emails', [])`
- Configuration changes: Use JSON file helpers, not direct file operations
