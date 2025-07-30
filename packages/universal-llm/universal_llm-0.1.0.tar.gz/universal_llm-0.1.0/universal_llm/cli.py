import typer
from typing_extensions import Annotated
from typing import Optional
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt
from .config import Provider, load_config, save_config
from .registry import get_client
from .settings import Settings

app = typer.Typer(
    name="universal-llm",
    help="Universal LLM client - chat with any provider",
    no_args_is_help=True
)

console = Console()


@app.command("ask")
def ask_question(
    question: Annotated[str, typer.Argument(help="Question to ask the LLM")],
    provider: Annotated[Optional[Provider], typer.Option("--provider", "-p", help="Override provider")] = None,
    model: Annotated[Optional[str], typer.Option("--model", "-m", help="Override model")] = None,
    temperature: Annotated[Optional[float], typer.Option("--temperature", "-t", help="Override temperature")] = None,
):
    """Ask a question and get a response from the LLM."""
    config = load_config()
    
    # Determine provider
    active_provider = provider or config.current_provider
    if not active_provider:
        console.print("[red]No provider set. Use 'universal-llm set-provider' to configure.[/red]")
        raise typer.Exit(1)
    
    # Get provider config
    provider_config = config.providers[active_provider]
    if not provider_config.api_key and active_provider != Provider.OLLAMA:
        console.print(f"[red]No API key set for {active_provider.value}. Use 'universal-llm set-key' to configure.[/red]")
        raise typer.Exit(1)
    
    # Build settings
    settings = Settings(
        provider=active_provider.value,
        model=model or provider_config.model,
        api_key=provider_config.api_key,
        base_url=provider_config.base_url,
        temperature=temperature or config.default_temperature,
        timeout=config.default_timeout
    )
    
    try:
        client = get_client(settings)
        with console.status(f"[bold green]Asking {active_provider.value}..."):
            response = client.ask(question)
        
        console.print(f"\n[bold cyan]{active_provider.value.title()}:[/bold cyan] {response}")
        
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@app.command("chat")
def interactive_chat(
    provider: Annotated[Optional[Provider], typer.Option("--provider", "-p", help="Override provider")] = None,
    model: Annotated[Optional[str], typer.Option("--model", "-m", help="Override model")] = None,
):
    """Start an interactive chat session."""
    config = load_config()
    
    # Determine provider
    active_provider = provider or config.current_provider
    if not active_provider:
        console.print("[red]No provider set. Use 'universal-llm set-provider' to configure.[/red]")
        raise typer.Exit(1)
    
    # Get provider config
    provider_config = config.providers[active_provider]
    if not provider_config.api_key and active_provider != Provider.OLLAMA:
        console.print(f"[red]No API key set for {active_provider.value}. Use 'universal-llm set-key' to configure.[/red]")
        raise typer.Exit(1)
    
    # Build settings
    settings = Settings(
        provider=active_provider.value,
        model=model or provider_config.model,
        api_key=provider_config.api_key,
        base_url=provider_config.base_url,
        temperature=config.default_temperature,
        timeout=config.default_timeout
    )
    
    try:
        client = get_client(settings)
        console.print(f"[bold green]Starting chat with {active_provider.value} ({settings.model})[/bold green]")
        console.print("[dim]Type 'quit' to exit[/dim]\n")
        
        conversation = []
        
        while True:
            question = Prompt.ask("[bold blue]You")
            if question.lower() in ['quit', 'exit', 'q']:
                break
            
            conversation.append({"role": "user", "content": question})
            
            with console.status(f"[bold green]{active_provider.value.title()} is thinking..."):
                response = client.chat_sync(conversation)
            
            console.print(f"[bold cyan]{active_provider.value.title()}:[/bold cyan] {response}\n")
            conversation.append({"role": "assistant", "content": response})
            
    except KeyboardInterrupt:
        console.print("\n[yellow]Chat session ended.[/yellow]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@app.command("set-provider")
def set_provider(provider: Provider):
    """Set the current active provider."""
    config = load_config()
    config.current_provider = provider
    save_config(config)
    console.print(f"[green]Current provider set to: {provider.value}[/green]")


@app.command("set-key")
def set_api_key(
    provider: Annotated[Optional[Provider], typer.Option("--provider", "-p", help="Provider to set key for")] = None,
):
    """Set API key for a provider."""
    config = load_config()
    
    # Use current provider if none specified
    target_provider = provider or config.current_provider
    if not target_provider:
        console.print("[red]No provider specified and no current provider set.[/red]")
        raise typer.Exit(1)
    
    if target_provider == Provider.OLLAMA:
        console.print("[yellow]Ollama doesn't require an API key.[/yellow]")
        return
    
    api_key = typer.prompt(f"Enter API key for {target_provider.value}", hide_input=True)
    
    config.providers[target_provider].api_key = api_key
    save_config(config)
    console.print(f"[green]API key set for {target_provider.value}[/green]")


@app.command("set-model")
def set_model(
    model: Annotated[str, typer.Argument(help="Model name to set")],
    provider: Annotated[Optional[Provider], typer.Option("--provider", "-p", help="Provider to set model for")] = None,
):
    """Set default model for a provider."""
    config = load_config()
    
    # Use current provider if none specified
    target_provider = provider or config.current_provider
    if not target_provider:
        console.print("[red]No provider specified and no current provider set.[/red]")
        raise typer.Exit(1)
    
    config.providers[target_provider].model = model
    save_config(config)
    console.print(f"[green]Default model for {target_provider.value} set to: {model}[/green]")


@app.command("show-config")
def show_config():
    """Show current configuration."""
    config = load_config()
    
    table = Table(title="Universal LLM Configuration")
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="green")
    
    table.add_row("Current Provider", config.current_provider.value if config.current_provider else "Not set")
    table.add_row("Default Temperature", str(config.default_temperature))
    table.add_row("Default Timeout", f"{config.default_timeout}s")
    
    console.print(table)
    console.print()
    
    # Provider details
    providers_table = Table(title="Provider Configurations")
    providers_table.add_column("Provider", style="cyan")
    providers_table.add_column("Model", style="green")
    providers_table.add_column("API Key", style="yellow")
    providers_table.add_column("Base URL", style="magenta")
    
    for provider, provider_config in config.providers.items():
        api_key_status = "Set" if provider_config.api_key else "Not set"
        if provider == Provider.OLLAMA:
            api_key_status = "N/A"
        
        providers_table.add_row(
            provider.value,
            provider_config.model or "Not set",
            api_key_status,
            provider_config.base_url or "Default"
        )
    
    console.print(providers_table)


@app.command("configure")
def interactive_configure():
    """Interactive configuration wizard."""
    config = load_config()
    
    console.print("[bold green]Universal LLM Configuration Wizard[/bold green]")
    console.print("Press Enter to keep current values\n")
    
    # Set provider
    provider_choices = [p.value for p in Provider]
    current_provider = config.current_provider.value if config.current_provider else None
    
    provider_input = Prompt.ask(
        "Choose provider",
        choices=provider_choices,
        default=current_provider
    )
    config.current_provider = Provider(provider_input)
    
    # Configure the selected provider
    provider_config = config.providers[config.current_provider]
    
    console.print(f"\n[bold cyan]Configuring {config.current_provider.value}[/bold cyan]")
    
    # Set model
    current_model = provider_config.model
    new_model = Prompt.ask(
        "Model name",
        default=current_model
    )
    provider_config.model = new_model
    
    # Set API key (if not Ollama)
    if config.current_provider != Provider.OLLAMA:
        has_key = "Yes" if provider_config.api_key else "No"
        set_key = Prompt.ask(
            f"Set API key? (currently: {has_key})",
            choices=["y", "n"],
            default="n"
        )
        
        if set_key.lower() == "y":
            api_key = typer.prompt(f"Enter API key for {config.current_provider.value}", hide_input=True)
            provider_config.api_key = api_key
    
    # Set base URL for custom endpoints
    if config.current_provider in [Provider.OPENAI, Provider.OLLAMA]:
        current_base_url = provider_config.base_url or "Default"
        set_base_url = Prompt.ask(
            f"Set custom base URL? (currently: {current_base_url})",
            choices=["y", "n"],
            default="n"
        )
        
        if set_base_url.lower() == "y":
            base_url = Prompt.ask("Base URL")
            provider_config.base_url = base_url if base_url else None
    
    save_config(config)
    console.print(f"\n[green]Configuration saved! Current provider: {config.current_provider.value}[/green]")


if __name__ == "__main__":
    app()