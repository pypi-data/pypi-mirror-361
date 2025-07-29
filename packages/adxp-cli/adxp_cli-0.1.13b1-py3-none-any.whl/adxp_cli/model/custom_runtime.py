from adxp_cli.auth.service import get_credential
from adxp_sdk.auth.credentials import Credentials
from adxp_sdk.models.hub import AXModelHub
import click

# ModelHub 인스턴스 생성 함수

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

def create_custom_runtime(runtime_data: dict):
    try:
        hub = get_model_hub()
        result = hub.create_custom_runtime(runtime_data)
        click.secho("✅ Custom runtime created successfully", fg="green")
        click.echo(result)
    except Exception as e:
        error_msg = str(e)
        if "401" in error_msg or "Unauthorized" in error_msg:
            raise click.ClickException(
                "🔐 401 Unauthorized : Please login again. \n Run Either One of the Following Commands \n 1. adxp-cli auth login \n 2. adxp-cli auth refresh"
            )
        click.secho(f"❌ Failed to create custom runtime: {e}", fg="red")

def get_custom_runtime_by_model(model_id: str):
    try:
        hub = get_model_hub()
        result = hub.get_custom_runtime_by_model(model_id)
        click.secho("✅ Custom runtime retrieved", fg="green")
        click.echo(result)
    except Exception as e:
        error_msg = str(e)
        if "401" in error_msg or "Unauthorized" in error_msg:
            raise click.ClickException(
                "🔐 401 Unauthorized : Please login again. \n Run Either One of the Following Commands \n 1. adxp-cli auth login \n 2. adxp-cli auth refresh"
            )
        click.secho(f"❌ Failed to get custom runtime: {e}", fg="red")

def delete_custom_runtime_by_model(model_id: str):
    try:
        hub = get_model_hub()
        hub.delete_custom_runtime_by_model(model_id)
        click.secho("✅ Custom runtime deleted successfully", fg="green")
    except Exception as e:
        error_msg = str(e)
        if "401" in error_msg or "Unauthorized" in error_msg:
            raise click.ClickException(
                "🔐 401 Unauthorized : Please login again. \n Run Either One of the Following Commands \n 1. adxp-cli auth login \n 2. adxp-cli auth refresh"
            )
        click.secho(f"❌ Failed to delete custom runtime: {e}", fg="red")

def upload_custom_code_file(file_path: str):
    try:
        hub = get_model_hub()
        result = hub.upload_custom_code_file(file_path)
        click.secho("✅ Custom code file uploaded successfully", fg="green")
        click.echo(result)
    except Exception as e:
        error_msg = str(e)
        if "401" in error_msg or "Unauthorized" in error_msg:
            raise click.ClickException(
                "🔐 401 Unauthorized : Please login again. \n Run Either One of the Following Commands \n 1. adxp-cli auth login \n 2. adxp-cli auth refresh"
            )
        click.secho(f"❌ Failed to upload custom code file: {e}", fg="red") 