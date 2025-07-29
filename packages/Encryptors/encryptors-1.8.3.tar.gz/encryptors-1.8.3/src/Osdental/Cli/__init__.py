import os
import subprocess
import platform
import click
from Osdental.Shared.Logger import logger
from Osdental.Shared.Enums.Message import Message
from Osdental.Shared.Utils.CaseConverter import CaseConverter

SRC_PATH = 'src'
APP_PATH = os.path.join(SRC_PATH, 'Application')
DOMAIN_PATH = os.path.join(SRC_PATH, 'Domain')
INFRA_PATH = os.path.join(SRC_PATH, 'Infrastructure')
GRAPHQL_PATH = os.path.join(INFRA_PATH, 'Graphql')
SCHEMAS_PATH = os.path.join(GRAPHQL_PATH, 'Schemas')

@click.group()
def cli():
    """Comandos personalizados para gestionar el proyecto."""
    pass

@cli.command()
def clean():
    """Borrar todos los __pycache__."""
    if platform.system() == 'Windows':
        subprocess.run('for /d /r . %d in (__pycache__) do @if exist "%d" rd /s/q "%d"', shell=True)
    else:
        subprocess.run("find . -name '__pycache__' -type d -exec rm -rf {} +", shell=True)

    logger.info(Message.PYCACHE_CLEANUP_SUCCESS_MSG)


@cli.command(name='start-app')
@click.argument('app')
def start_app(app: str):
    """Crear un servicio con estructura hexagonal y CRUD básico."""
    app = CaseConverter.snake_to_pascal(app)
    name_method = CaseConverter.case_to_snake(app)

    data = 'data: Dict[str,str]'
    token = 'token: AuthToken'
    api_type_response = 'Response!'
    
    directories = [
        os.path.join(SRC_PATH),
        os.path.join(APP_PATH, 'UseCases'),
        os.path.join(APP_PATH, 'Interfaces'),
        os.path.join(DOMAIN_PATH, 'Interfaces'),
        os.path.join(GRAPHQL_PATH, 'Resolvers'),
        os.path.join(SCHEMAS_PATH),
        os.path.join(SCHEMAS_PATH, app, 'Queries'),
        os.path.join(SCHEMAS_PATH, app, 'Mutations'),
        os.path.join(INFRA_PATH, 'Repositories', app)
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)

    # Contenidos CRUD
    use_case_interface_content = f'{app}UseCaseInterface'
    use_case_interface_content = f'''
    from abc import ABC, abstractmethod
    from typing import Dict
    from Osdental.Models.Token import AuthToken

    class {use_case_interface_content}(ABC):
    
        @abstractmethod
        def get_all_{name_method}(self, {token}, {data}) -> str: ...

        @abstractmethod
        def get_{name_method}_by_id(self, {token}, {data}) -> str: ...

        @abstractmethod
        def create_{name_method}(self, {token}, {data}) -> str: ...

        @abstractmethod
        def update_{name_method}(self, {token}, {data}) -> str: ...

        @abstractmethod
        def delete_{name_method}(self, {token}, {data}) -> str: ...
    '''


    use_case_content = f'''
    from typing import Dict
    from Osdental.Decorators.DecryptedData import process_encrypted_data
    from Osdental.Models.Token import AuthToken
    ..Interfaces.{app} import {use_case_interface_content}

    class {app}UseCase({use_case_interface_content}):
        
        @process_encrypted_data()
        def get_all_{name_method}(self, {token}, {data}) -> str: pass

        @process_encrypted_data()        
        def get_{name_method}_by_id(self, {token}, {data}) -> str: pass
            
        @process_encrypted_data()    
        def create_{name_method}(self, {token}, {data}) -> str: pass

        @process_encrypted_data()
        def update_{name_method}(self, {token}, {data}) -> str: pass

        @process_encrypted_data()
        def delete_{name_method}(self, {token}, {data}) -> str: pass
    '''


    repository_interface_name = f'{app}RepositoryInterface'
    repository_interface_content = f'''
    from abc import ABC, abstractmethod
    from typing import List, Dict

    class {repository_interface_name}(ABC):

        @staticmethod
        @abstractmethod
        def get_all_{name_method}(self, {data}) -> List[Dict[str,str]]: ...

        @staticmethod
        @abstractmethod
        def get_{name_method}_by_id(self, id: str) -> Dict[str,str]: ...

        @staticmethod
        @abstractmethod
        def create_{name_method}(self, {data}) -> str: ...

        @staticmethod
        @abstractmethod
        def update_{name_method}(self, id: str, {data}) -> str: ...

        @staticmethod
        @abstractmethod
        def delete_{name_method}(self, id: str) -> str: ...
    '''


    repository_content = f'''
    from typing import List, Dict
    from src.Domain.Interfaces.{app} import {repository_interface_name}

    class {app}Repository({repository_interface_name}):
        
        @staticmethod
        def get_all_{name_method}(self, {data}) -> List[Dict[str,str]]: pass
        
        @staticmethod
        def get_{name_method}_by_id(self, id: str) -> Dict[str,str]: pass

        @staticmethod    
        def create_{name_method}(self, {data}) -> str: pass

        @staticmethod                
        def update_{name_method}(self, id: str, {data}) -> str:pass
            
        @staticmethod    
        def delete_{name_method}(self, id: str) -> str: pass
    '''


    query_graphql = f'''type Query {{
        getAll{app}(data: String!): {api_type_response}
        get{app}ById(data: String!): {api_type_response}
    }}
    '''

    mutation_graphql = f'''type Mutation {{
        create{app}(data: String!): {api_type_response}
        update{app}(data: String!): {api_type_response}
        delete{app}(data: String!): {api_type_response}
    }}
    '''

    resolver_content_init = f'''
    {name_method}_query_resolvers = {{}}
    {name_method}_mutation_resolvers = {{}}
    '''

    resolver_content = f'''
    from Osdental.Decorators.AuditLog import handle_audit_and_exception

    class {app}Resolver:
        
        @staticmethod
        @handle_audit_and_exception
        def resolve_get_all_{name_method}(self, _, info, data): pass

        @staticmethod
        @handle_audit_and_exception
        def resolve_get_{name_method}_by_id(self, _, info, data): pass

        @staticmethod
        @handle_audit_and_exception
        def resolve_create_{name_method}(self, _, info, data): pass

        @staticmethod
        @handle_audit_and_exception
        def resolve_update_{name_method}(self, _, info, data): pass

        @staticmethod
        @handle_audit_and_exception
        def resolve_delete_{name_method}(self, _, info, data): pass
    '''


    response_content = '''
        type Response {
            status: String
            message: String
            data: String
        }
    '''

    repository_init_content = ''
    

    files = {
        os.path.join(APP_PATH, 'UseCases', f'{app}UseCase.py'): use_case_content,
        os.path.join(APP_PATH, 'Interfaces', f'{app}UseCaseInterface.py'): use_case_interface_content,
        os.path.join(DOMAIN_PATH, 'Interfaces', f'{app}RepositoryInterface.py'): repository_interface_content,
        os.path.join(GRAPHQL_PATH, 'Resolvers', '__init__.py'): resolver_content_init,
        os.path.join(GRAPHQL_PATH, 'Resolvers', f'{app}Resolver.py'): resolver_content,
        os.path.join(SCHEMAS_PATH, app, 'Queries', 'Query.graphql'): query_graphql,
        os.path.join(SCHEMAS_PATH, app, 'Mutations', 'Mutation.graphql'): mutation_graphql,
        os.path.join(SCHEMAS_PATH, 'Response.graphql'): response_content,
        os.path.join(INFRA_PATH, 'Repositories', app, '__init__.py'): repository_init_content,
        os.path.join(INFRA_PATH, 'Repositories', app, f'{app}Repository.py'): repository_content
    }

    for file_path, content in files.items():
        if not os.path.exists(file_path):
            with open(file_path, 'w') as f:
                f.write(content)

    logger.info(Message.HEXAGONAL_SERVICE_CREATED_MSG)

@cli.command()
@click.argument('port')
def start(port:int):
    """Levantar el servidor FastAPI."""
    try:
        subprocess.run(['uvicorn', 'app:app', '--port', str(port), '--reload'], check=True)
    except subprocess.CalledProcessError as e:
        logger.error(f'{Message.SERVER_NETWORK_ACCESS_ERROR_MSG}: {e}')


@cli.command()
@click.argument('port')
def serve(port:int):
    """Levantar el servidor FastAPI accesible desde cualquier máquina."""
    try:
        # Levanta el servidor en el puerto n accesible desde cualquier IP
        subprocess.run(['uvicorn', 'app:app', '--host', '0.0.0.0', '--port', str(port), '--reload'], check=True)
    except subprocess.CalledProcessError as e:
        logger.error(f'{Message.SERVER_NETWORK_ACCESS_ERROR_MSG}: {e}')


if __name__ == "__main__":
    cli()
