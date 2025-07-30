# Typer CLI Architecture Pattern

## Overview

This codebase implements a hierarchical CLI architecture using Typer with persistent configuration management. The pattern enables complex multi-service command structures with shared configuration, defaults management, and interactive setup workflows.

## Core Components

### 1. Configuration Management with Pydantic

**Config Structure:**
```python
# utils/api_client_config_utils.py
from pydantic import BaseModel
from pathlib import Path
import json

class ApiClientConfig(BaseModel):
    # Global defaults
    default_env: Optional[Environment] = None
    
    # Service-specific defaults
    fi_services_default_partner_id: Optional[str] = None
    dtc_services_default_session_id: Optional[str] = None
    
    # Complex nested configs
    local_service_ports: LocalServicePorts = LocalServicePorts()
    
    # Sensitive data
    admin_role_name: Optional[str] = None
    admin_credential: Optional[str] = None

def load_api_client_config() -> ApiClientConfig:
    """Load configuration with automatic creation of missing files."""
    config_path = Path.home() / ".config" / "api_client_cli" / "config.json"
    config_path.parent.mkdir(parents=True, exist_ok=True)
    
    if config_path.exists():
        with open(config_path, 'r') as f:
            data = json.load(f)
        return ApiClientConfig(**data)
    else:
        config = ApiClientConfig()
        save_api_client_config(config)
        return config

def save_api_client_config(config: ApiClientConfig):
    """Save configuration with proper file permissions."""
    config_path = Path.home() / ".config" / "api_client_cli" / "config.json"
    with open(config_path, 'w') as f:
        json.dump(config.model_dump(), f, indent=2)
```

### 2. Hierarchical CLI Structure

**Main CLI Entry Point:**
```python
# universal_api_client/cli.py
import typer
from typing_extensions import Annotated

app = typer.Typer(
    name="apic",
    help="Universal API Client for multiple services",
    no_args_is_help=True
)

# Global options available to all subcommands
@app.callback()
def main(
    env: Annotated[Optional[Environment], typer.Option("--env", "-e", help="Environment")] = None,
    verbose: Annotated[bool, typer.Option("--verbose", "-v", help="Verbose output")] = False,
):
    """Global configuration and options."""
    if env:
        # Store in context for subcommands
        ctx = typer.get_current_context()
        ctx.ensure_object(dict)
        ctx.obj["env"] = env
        ctx.obj["verbose"] = verbose

# Add subcommand groups
from .fi_services_cli import fi_services_app
from .dtc_services_cli import dtc_services_app

app.add_typer(fi_services_app, name="fi-services")
app.add_typer(dtc_services_app, name="dtc-services")
```

**Service-Level CLI:**
```python
# universal_api_client/fi_services_cli.py
fi_services_app = typer.Typer(
    name="fi-services",
    help="FiServices API operations",
    no_args_is_help=True
)

@fi_services_app.callback()
def fi_services_main(
    partner_id: Annotated[Optional[str], typer.Option("--partner-id", "-p")] = None,
    private: Annotated[bool, typer.Option("--private", help="Use private network")] = False,
):
    """FiServices-specific options."""
    ctx = typer.get_current_context()
    ctx.ensure_object(dict)
    ctx.obj["partner_id"] = partner_id
    ctx.obj["private"] = private

# Nested subcommands
from .fi_services_admin_cli import admin_app
fi_services_app.add_typer(admin_app, name="admin")
```

### 3. Configuration Management Commands

**Default Management Pattern:**
```python
@app.command("set-default-env")
def set_default_env(env: Environment):
    """Set the default environment for all operations."""
    config = load_api_client_config()
    config.default_env = env
    save_api_client_config(config)
    typer.echo(f"Default environment set to: {env.value}")

@app.command("show-defaults")
def show_defaults():
    """Show current default configurations."""
    config = load_api_client_config()
    
    table = Table(title="Current Defaults")
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="green")
    
    table.add_row("Environment", config.default_env.value if config.default_env else "Not set")
    table.add_row("FI Services Partner ID", config.fi_services_default_partner_id or "Not set")
    
    console.print(table)

@app.command("clear-defaults")
def clear_defaults():
    """Clear all default configurations."""
    if typer.confirm("Are you sure you want to clear all defaults?"):
        config = ApiClientConfig()  # Reset to defaults
        save_api_client_config(config)
        typer.echo("All defaults cleared.")
```

### 4. Interactive Configuration

**Interactive Menu Pattern:**
```python
@app.command("configure-localhost")
def configure_localhost():
    """Interactive menu to configure localhost service ports."""
    config = load_api_client_config()
    
    typer.echo("Configure localhost service ports:")
    typer.echo("(Press Enter to keep current value)")
    
    current_ports = config.local_service_ports
    
    # Interactive prompts with current values as defaults
    fi_services_port = typer.prompt(
        f"FI Services port",
        default=current_ports.fi_services,
        type=int
    )
    
    dtc_services_port = typer.prompt(
        f"DTC Services port",
        default=current_ports.dtc_services,
        type=int
    )
    
    # Update config
    config.local_service_ports.fi_services = fi_services_port
    config.local_service_ports.dtc_services = dtc_services_port
    
    save_api_client_config(config)
    typer.echo("Localhost configuration updated!")
```

### 5. Secure Credential Management

**Hidden Input Pattern:**
```python
@app.command("set-credentials")
def set_admin_credentials():
    """Set admin credentials with secure input."""
    config = load_api_client_config()
    
    admin_role_name = typer.prompt("Admin role name")
    admin_credential = typer.prompt("Admin credential", hide_input=True)
    
    config.admin_role_name = admin_role_name
    config.admin_credential = admin_credential
    
    save_api_client_config(config)
    typer.echo("Admin credentials configured successfully!")

@app.command("show-credentials")
def show_admin_credentials():
    """Show admin credentials (masked)."""
    config = load_api_client_config()
    
    if config.admin_role_name:
        typer.echo(f"Admin role: {config.admin_role_name}")
        typer.echo(f"Admin credential: {'*' * len(config.admin_credential) if config.admin_credential else 'Not set'}")
    else:
        typer.echo("No admin credentials configured.")
```

### 6. Context and Override Hierarchy

**Resolution Pattern:**
```python
def resolve_environment(ctx: typer.Context) -> Environment:
    """Resolve environment with proper hierarchy."""
    config = load_api_client_config()
    
    # 1. Command line option (highest priority)
    if ctx.obj and "env" in ctx.obj and ctx.obj["env"]:
        return ctx.obj["env"]
    
    # 2. Service-specific default
    if hasattr(config, 'service_default_env') and config.service_default_env:
        return config.service_default_env
    
    # 3. Global default
    if config.default_env:
        return config.default_env
    
    # 4. Error (no fallback)
    raise typer.BadParameter("Environment not specified and no default set")
```

## Key Patterns

### 1. Configuration File Structure
- **Location:** `~/.config/[tool_name]/config.json`
- **Validation:** Pydantic models with type checking
- **Auto-creation:** Missing files/directories created automatically
- **Permissions:** Secure file permissions for sensitive data

### 2. Command Structure
```
tool [global-options] <service> [service-options] <command> [command-options]
```

### 3. Default Management
- **Set:** `tool set-default-<setting> <value>`
- **Show:** `tool show-defaults`
- **Clear:** `tool clear-defaults`

### 4. Interactive Configuration
- **Menu-driven:** Step through multiple related settings
- **Current value defaults:** Show existing values as defaults
- **Confirmation:** Dangerous operations require confirmation

### 5. Secure Data Handling
- **Hidden input:** `typer.prompt(hide_input=True)`
- **Masked display:** Show asterisks instead of actual values
- **File permissions:** Restrict access to config files

## Implementation Checklist

1. Create Pydantic config model with all necessary fields
2. Implement load/save functions with auto-creation
3. Set up main CLI app with global options callback
4. Create service-level sub-apps with service-specific options
5. Add default management commands (set/show/clear)
6. Implement interactive configuration for complex settings
7. Add secure credential handling with hidden input
8. Create context resolution functions for option hierarchy
9. Set up proper file permissions for config directory
10. Add rich output formatting with tables and colors