from adxp_cli.auth.service import get_credential
from adxp_sdk.auth.credentials import Credentials
from adxp_sdk.models.hub import AXModelHub
import click

# Create AXModelHub instance with credentials
def get_model_hub():
    headers, config = get_credential()
    # Use headers directly if token is available (avoids password authentication)
    if hasattr(config, 'token') and config.token:
        return AXModelHub(headers=headers, base_url=config.base_url)
    else:
        # Fallback to credentials-based authentication
        credentials = Credentials(
            username=config.username,
            password="",  # Only token is needed
            project=config.client_id,
            base_url=config.base_url
        )
        return AXModelHub(credentials)

# [모델 관련]
def create_model(model_data: dict):
    """Create a new model"""
    try:
        hub = get_model_hub()
        result = hub.create_model(model_data)
        click.secho("✅ Model created successfully", fg="green")
        click.echo(result)
    except Exception as e:
        error_msg = str(e)
        if "401" in error_msg or "Unauthorized" in error_msg:
            raise click.ClickException(
                "🔐 401 Unauthorized : Please login again. \n Run Either One of the Following Commands \n 1. adxp-cli auth login \n 2. adxp-cli auth refresh"
            )
        click.secho(f"❌ Failed to create model: {e}", fg="red")

def update_model(model_id: str, model_data: dict):
    """Update a model"""
    try:
        hub = get_model_hub()
        result = hub.update_model(model_id, model_data)
        click.secho("✅ Model updated successfully", fg="green")
        click.echo(result)
    except Exception as e:
        error_msg = str(e)
        if "401" in error_msg or "Unauthorized" in error_msg:
            raise click.ClickException(
                "🔐 401 Unauthorized : Please login again. \n Run Either One of the Following Commands \n 1. adxp-cli auth login \n 2. adxp-cli auth refresh"
            )
        click.secho(f"❌ Failed to update model: {e}", fg="red")

def list_models(page=1, size=10, sort=None, filter=None, search=None, ids=None):
    """List all models"""
    try:
        hub = get_model_hub()
        result = hub.get_models(page=page, size=size, sort=sort, filter=filter, search=search, ids=ids)
        click.secho("✅ Models listed", fg="green")
        click.echo(result)
    except Exception as e:
        error_msg = str(e)
        if "401" in error_msg or "Unauthorized" in error_msg:
            raise click.ClickException(
                "🔐 401 Unauthorized : Please login again. \n Run Either One of the Following Commands \n 1. adxp-cli auth login \n 2. adxp-cli auth refresh"
            )
        click.secho(f"❌ Failed to list models: {e}", fg="red")

def get_model(model_id: str):
    """Get a model by ID"""
    try:
        hub = get_model_hub()
        result = hub.get_model_by_id(model_id)
        click.secho("✅ Model retrieved", fg="green")
        click.echo(result)
    except Exception as e:
        error_msg = str(e)
        if "401" in error_msg or "Unauthorized" in error_msg:
            raise click.ClickException(
                "🔐 401 Unauthorized : Please login again. \n Run Either One of the Following Commands \n 1. adxp-cli auth login \n 2. adxp-cli auth refresh"
            )
        click.secho(f"❌ Failed to get model: {e}", fg="red")

def delete_model(model_id: str):
    """Delete a model by ID"""
    try:
        hub = get_model_hub()
        result = hub.delete_model(model_id)
        click.secho("✅ Model deleted successfully", fg="green")
        click.echo(result)
    except Exception as e:
        error_msg = str(e)
        if "401" in error_msg or "Unauthorized" in error_msg:
            raise click.ClickException(
                "🔐 401 Unauthorized : Please login again. \n Run Either One of the Following Commands \n 1. adxp-cli auth login \n 2. adxp-cli auth refresh"
            )
        click.secho(f"❌ Failed to delete model: {e}", fg="red")

def recover_model(model_id: str):
    """Recover a deleted model by ID"""
    try:
        hub = get_model_hub()
        result = hub.recover_model(model_id)
        click.secho("✅ Model recovered successfully", fg="green")
        click.echo(result)
    except Exception as e:
        error_msg = str(e)
        if "401" in error_msg or "Unauthorized" in error_msg:
            raise click.ClickException(
                "🔐 401 Unauthorized : Please login again. \n Run Either One of the Following Commands \n 1. adxp-cli auth login \n 2. adxp-cli auth refresh"
            )
        click.secho(f"❌ Failed to recover model: {e}", fg="red")

def upload_model_file(file_path: str):
    """Upload a local LLM model file"""
    try:
        hub = get_model_hub()
        result = hub.upload_model_file(file_path)
        click.secho("✅ Model file uploaded successfully", fg="green")
        click.echo(result)
    except Exception as e:
        error_msg = str(e)
        if "401" in error_msg or "Unauthorized" in error_msg:
            raise click.ClickException(
                "🔐 401 Unauthorized : Please login again. \n Run Either One of the Following Commands \n 1. adxp-cli auth login \n 2. adxp-cli auth refresh"
            )
        click.secho(f"❌ Failed to upload model file: {e}", fg="red")

# [모델 타입/태그]
def list_model_types():
    """List all model types"""
    try:
        hub = get_model_hub()
        result = hub.get_model_types()
        click.secho("✅ Model types listed", fg="green")
        click.echo(result)
    except Exception as e:
        error_msg = str(e)
        if "401" in error_msg or "Unauthorized" in error_msg:
            raise click.ClickException(
                "🔐 401 Unauthorized : Please login again. \n Run Either One of the Following Commands \n 1. adxp-cli auth login \n 2. adxp-cli auth refresh"
            )
        click.secho(f"❌ Failed to list model types: {e}", fg="red")

def list_model_tags():
    """List all model tags"""
    try:
        hub = get_model_hub()
        result = hub.get_model_tags()
        click.secho("✅ Model tags listed", fg="green")
        click.echo(result)
    except Exception as e:
        error_msg = str(e)
        if "401" in error_msg or "Unauthorized" in error_msg:
            raise click.ClickException(
                "🔐 401 Unauthorized : Please login again. \n Run Either One of the Following Commands \n 1. adxp-cli auth login \n 2. adxp-cli auth refresh"
            )
        click.secho(f"❌ Failed to list model tags: {e}", fg="red")

# [모델 태그]
def add_tags_to_model(model_id: str, tags: list):
    """Add tags to a specific model"""
    try:
        hub = get_model_hub()
        result = hub.add_tags_to_model(model_id, tags)
        click.secho("✅ Tags added to model", fg="green")
        click.echo(result)
    except Exception as e:
        error_msg = str(e)
        if "401" in error_msg or "Unauthorized" in error_msg:
            raise click.ClickException(
                "🔐 401 Unauthorized : Please login again. \n Run Either One of the Following Commands \n 1. adxp-cli auth login \n 2. adxp-cli auth refresh"
            )
        click.secho(f"❌ Failed to add tags to model: {e}", fg="red")

def remove_tags_from_model(model_id: str, tags: list):
    """Remove tags from a specific model"""
    try:
        hub = get_model_hub()
        result = hub.remove_tags_from_model(model_id, tags)
        click.secho("✅ Tags removed from model", fg="green")
        click.echo(result)
    except Exception as e:
        error_msg = str(e)
        if "401" in error_msg or "Unauthorized" in error_msg:
            raise click.ClickException(
                "🔐 401 Unauthorized : Please login again. \n Run Either One of the Following Commands \n 1. adxp-cli auth login \n 2. adxp-cli auth refresh"
            )
        click.secho(f"❌ Failed to remove tags from model: {e}", fg="red")

# [모델 언어]
def add_languages_to_model(model_id: str, languages: list):
    """Add languages to a specific model"""
    try:
        hub = get_model_hub()
        result = hub.add_languages_to_model(model_id, languages)
        click.secho("✅ Languages added to model", fg="green")
        click.echo(result)
    except Exception as e:
        error_msg = str(e)
        if "401" in error_msg or "Unauthorized" in error_msg:
            raise click.ClickException(
                "🔐 401 Unauthorized : Please login again. \n Run Either One of the Following Commands \n 1. adxp-cli auth login \n 2. adxp-cli auth refresh"
            )
        click.secho(f"❌ Failed to add languages to model: {e}", fg="red")

def remove_languages_from_model(model_id: str, languages: list):
    """Remove languages from a specific model"""
    try:
        hub = get_model_hub()
        result = hub.remove_languages_from_model(model_id, languages)
        click.secho("✅ Languages removed from model", fg="green")
        click.echo(result)
    except Exception as e:
        error_msg = str(e)
        if "401" in error_msg or "Unauthorized" in error_msg:
            raise click.ClickException(
                "🔐 401 Unauthorized : Please login again. \n Run Either One of the Following Commands \n 1. adxp-cli auth login \n 2. adxp-cli auth refresh"
            )
        click.secho(f"❌ Failed to remove languages from model: {e}", fg="red")

# [모델 태스크]
def add_tasks_to_model(model_id: str, tasks: list):
    """Add tasks to a specific model"""
    try:
        hub = get_model_hub()
        result = hub.add_tasks_to_model(model_id, tasks)
        click.secho("✅ Tasks added to model", fg="green")
        click.echo(result)
    except Exception as e:
        error_msg = str(e)
        if "401" in error_msg or "Unauthorized" in error_msg:
            raise click.ClickException(
                "🔐 401 Unauthorized : Please login again. \n Run Either One of the Following Commands \n 1. adxp-cli auth login \n 2. adxp-cli auth refresh"
            )
        click.secho(f"❌ Failed to add tasks to model: {e}", fg="red")

def remove_tasks_from_model(model_id: str, tasks: list):
    """Remove tasks from a specific model"""
    try:
        hub = get_model_hub()
        result = hub.remove_tasks_from_model(model_id, tasks)
        click.secho("✅ Tasks removed from model", fg="green")
        click.echo(result)
    except Exception as e:
        error_msg = str(e)
        if "401" in error_msg or "Unauthorized" in error_msg:
            raise click.ClickException(
                "🔐 401 Unauthorized : Please login again. \n Run Either One of the Following Commands \n 1. adxp-cli auth login \n 2. adxp-cli auth refresh"
            )
        click.secho(f"❌ Failed to remove tasks from model: {e}", fg="red") 