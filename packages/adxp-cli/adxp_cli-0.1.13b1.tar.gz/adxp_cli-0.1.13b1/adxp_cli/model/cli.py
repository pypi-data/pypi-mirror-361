import click
from .provider import (
    create_provider,
    list_providers,
    get_provider,
    update_provider,
    delete_provider,
)
from .endpoint import (
    create_endpoint,
    list_endpoints,
    get_endpoint,
    delete_endpoint,
)
from .version import (
    list_versions,
    get_model_version,
    get_version,
    delete_model_version,
    update_model_version,
    promote_version,
)
from .model import (
    create_model,
    update_model,
    list_models,
    get_model,
    delete_model,
    recover_model,
    upload_model_file,
    list_model_types,
    list_model_tags,
    add_tags_to_model,
    remove_tags_from_model,
    add_languages_to_model,
    remove_languages_from_model,
    add_tasks_to_model,
    remove_tasks_from_model,
)
from .custom_runtime import (
    create_custom_runtime,
    get_custom_runtime_by_model,
    delete_custom_runtime_by_model,
    upload_custom_code_file,
)

@click.group()
def model():
    """Model command group."""
    pass

@model.group()
def provider():
    """Model Provider command group."""
    pass

@provider.command()
@click.option('--name', prompt=True, help='Provider name')
@click.option('--logo', prompt=True, help='Provider logo')
@click.option('--description', default='', help='Provider description')
def create(name, logo, description):
    """Create a model provider."""
    data = {'name': name, 'logo': logo, 'description': description}
    create_provider(data)

@provider.command()
@click.option('--page', default=1, help='Page number')
@click.option('--size', default=10, help='Page size')
@click.option('--sort', default=None, help='Sort by')
@click.option('--filter', default=None, help='Filter')
@click.option('--search', default=None, help='Search keyword')
def list(page, size, sort, filter, search):
    """List model providers."""
    list_providers(page, size, sort, filter, search)

@provider.command()
@click.argument('provider_id')
def get(provider_id):
    """Get a specific model provider."""
    get_provider(provider_id)

@provider.command()
@click.argument('provider_id')
@click.option('--name', default=None, help='Provider name')
@click.option('--logo', default=None, help='Provider logo')
@click.option('--description', default=None, help='Provider description')
def update(provider_id, name, logo, description):
    """Update a specific model provider."""
    data = {}
    if name is not None:
        data['name'] = name
    if logo is not None:
        data['logo'] = logo
    if description is not None:
        data['description'] = description
    update_provider(provider_id, data)

@provider.command()
@click.argument('provider_id')
def delete(provider_id):
    """Delete a specific model provider."""
    delete_provider(provider_id)

@model.group()
def endpoint():
    """Model Endpoint command group."""
    pass

@endpoint.command()
@click.argument('model_id')
@click.option('--url', prompt=True, help='Endpoint URL')
@click.option('--identifier', prompt=True, help='Endpoint identifier')
@click.option('--key', prompt=True, help='Endpoint key')
@click.option('--description', default='', help='Endpoint description')
def create(model_id, url, identifier, key, description):
    """Create a model endpoint."""
    data = {'url': url, 'identifier': identifier, 'key': key, 'description': description}
    create_endpoint(model_id, data)

@endpoint.command()
@click.argument('model_id')
@click.option('--page', default=1, help='Page number')
@click.option('--size', default=10, help='Page size')
@click.option('--sort', default=None, help='Sort by')
@click.option('--filter', default=None, help='Filter')
@click.option('--search', default=None, help='Search keyword')
def list(model_id, page, size, sort, filter, search):
    """List model endpoints for a specific model."""
    list_endpoints(model_id, page, size, sort, filter, search)

@endpoint.command()
@click.argument('model_id')
@click.argument('endpoint_id')
def get(model_id, endpoint_id):
    """Get a specific model endpoint."""
    get_endpoint(model_id, endpoint_id)

@endpoint.command()
@click.argument('model_id')
@click.argument('endpoint_id')
def delete(model_id, endpoint_id):
    """Delete a specific model endpoint."""
    delete_endpoint(model_id, endpoint_id)

@model.group()
def version():
    """Model Version command group."""
    pass

@version.command()
@click.argument('model_id')
@click.option('--page', default=1, help='Page number')
@click.option('--size', default=10, help='Page size')
@click.option('--sort', default=None, help='Sort by')
@click.option('--filter', default=None, help='Filter')
@click.option('--search', default=None, help='Search keyword')
@click.option('--ids', default=None, help='Comma-separated version IDs')
def list(model_id, page, size, sort, filter, search, ids):
    """List versions for a specific model."""
    list_versions(model_id, page, size, sort, filter, search, ids)

@version.command()
@click.argument('model_id')
@click.argument('version_id')
def get(model_id, version_id):
    """Get a specific version of a model."""
    get_model_version(model_id, version_id)

@version.command('get-by-version')
@click.argument('version_id')
def get_by_version(version_id):
    """Get a specific version by version_id only."""
    get_version(version_id)

@version.command()
@click.argument('model_id')
@click.argument('version_id')
def delete(model_id, version_id):
    """Delete a specific version of a model."""
    delete_model_version(model_id, version_id)

@version.command()
@click.argument('model_id')
@click.argument('version_id')
@click.option('--display-name', default=None, help='Display name')
@click.option('--description', default=None, help='Description')
def update(model_id, version_id, display_name, description):
    """Update a specific version of a model."""
    data = {}
    if display_name is not None:
        data['display_name'] = display_name
    if description is not None:
        data['description'] = description
    update_model_version(model_id, version_id, data)

@version.command()
@click.argument('version_id')
@click.option('--display-name', prompt=True, help='Display name')
@click.option('--description', default='', help='Description')
def promote(version_id, display_name, description):
    """Promote a specific version to a model."""
    data = {'display_name': display_name, 'description': description}
    promote_version(version_id, data)

@model.command()
@click.option('--json', 'json_path', type=click.Path(exists=True), required=True, help='Model creation JSON file path')
def create(json_path):
    """Create a new model (only JSON file input is allowed)."""
    import json
    with open(json_path, 'r') as f:
        data = json.load(f)
    create_model(data)

@model.command()
@click.argument('model_id')
@click.option('--json', 'json_path', type=click.Path(exists=True), required=True, help='Model update JSON file path')
def update(model_id, json_path):
    """Update a model (only JSON file input is allowed)."""
    import json
    with open(json_path, 'r') as f:
        data = json.load(f)
    update_model(model_id, data)

@model.command()
@click.option('--page', default=1, help='Page number')
@click.option('--size', default=10, help='Page size')
@click.option('--sort', default=None, help='Sort by')
@click.option('--filter', default=None, help='Filter')
@click.option('--search', default=None, help='Search keyword')
@click.option('--ids', default=None, help='Comma-separated model IDs')
def list(page, size, sort, filter, search, ids):
    """List all models."""
    list_models(page, size, sort, filter, search, ids)

@model.command()
@click.argument('model_id')
def get(model_id):
    """Get a model by ID."""
    get_model(model_id)

@model.command()
@click.argument('model_id')
def delete(model_id):
    """Delete a model by ID."""
    delete_model(model_id)

@model.command()
@click.argument('model_id')
def recover(model_id):
    """Recover a deleted model by ID."""
    recover_model(model_id)

@model.command()
@click.argument('file_path')
def upload(file_path):
    """Upload a local LLM model file."""
    upload_model_file(file_path)

@model.command('type-list')
def type_list():
    """List all model types."""
    list_model_types()

@model.command('tag-list')
def tag_list():
    """List all model tags."""
    list_model_tags()

@model.command('tag-add')
@click.argument('model_id')
@click.argument('tags', nargs=-1)
def tag_add(model_id, tags):
    """Add tags to a specific model."""
    tag_list = [{'name': tag} for tag in tags]
    add_tags_to_model(model_id, tag_list)

@model.command('tag-remove')
@click.argument('model_id')
@click.argument('tags', nargs=-1)
def tag_remove(model_id, tags):
    """Remove tags from a specific model."""
    tag_list = [{'name': tag} for tag in tags]
    remove_tags_from_model(model_id, tag_list)

@model.command('lang-add')
@click.argument('model_id')
@click.argument('languages', nargs=-1)
def lang_add(model_id, languages):
    """Add languages to a specific model."""
    lang_list = [{'name': lang} for lang in languages]
    add_languages_to_model(model_id, lang_list)

@model.command('lang-remove')
@click.argument('model_id')
@click.argument('languages', nargs=-1)
def lang_remove(model_id, languages):
    """Remove languages from a specific model."""
    lang_list = [{'name': lang} for lang in languages]
    remove_languages_from_model(model_id, lang_list)

@model.command('task-add')
@click.argument('model_id')
@click.argument('tasks', nargs=-1)
def task_add(model_id, tasks):
    """Add tasks to a specific model."""
    task_list = [{'name': task} for task in tasks]
    add_tasks_to_model(model_id, task_list)

@model.command('task-remove')
@click.argument('model_id')
@click.argument('tasks', nargs=-1)
def task_remove(model_id, tasks):
    """Remove tasks from a specific model."""
    task_list = [{'name': task} for task in tasks]
    remove_tasks_from_model(model_id, task_list)

@model.group('custom-runtime')
def custom_runtime():
    """Model Custom Runtime command group."""
    pass

@custom_runtime.command("create")
@click.option("--model-id", required=True, help="모델 ID (UUID)")
@click.option("--image-url", required=True, help="Custom Docker image URL")
@click.option("--use-bash", is_flag=True, default=False, help="Bash 사용 여부")
@click.option("--command", multiple=True, help="실행 커맨드 (여러 개 가능)")
@click.option("--args", multiple=True, help="실행 인자 (여러 개 가능)")
def create(model_id, image_url, use_bash, command, args):
    """Create a custom runtime."""
    runtime_data = {
        "model_id": model_id,
        "image_url": image_url,
        "use_bash": use_bash,
        "command": list(command) if command else None,
        "args": list(args) if args else None
    }
    create_custom_runtime(runtime_data)

@custom_runtime.command("get")
@click.option("--model-id", required=True, help="모델 ID (UUID)")
def get(model_id):
    """Get a custom runtime."""
    get_custom_runtime_by_model(model_id)

@custom_runtime.command("delete")
@click.option("--model-id", required=True, help="모델 ID (UUID)")
def delete(model_id):
    """Delete a custom runtime."""
    delete_custom_runtime_by_model(model_id)

@custom_runtime.command("upload-code")
@click.option("--file-path", required=True, help="업로드할 코드 파일 경로 (zip, tar 등)")
def upload_code(file_path):
    """Upload a custom code file."""
    upload_custom_code_file(file_path)

@click.group()
def cli():
    """AIP Model CLI"""
    pass

cli.add_command(model)

if __name__ == "__main__":
    cli()