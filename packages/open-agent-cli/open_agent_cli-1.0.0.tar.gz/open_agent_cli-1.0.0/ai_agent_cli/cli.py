"""
CLI principal do Open Agent
"""
import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from .core.agent import AIAgent
from .core.config import ConfigManager
from .core.ai_provider import AIProviderFactory


@click.group()
@click.version_option(version="1.0.0")
def cli():
    """Open Agent CLI - Assistente de IA para desenvolvimento"""
    pass


@cli.command()
@click.option('--api-key', help='Chave da API')
@click.option('--provider', type=click.Choice(['openai', 'google']), help='Provedor da API')
@click.option('--model', help='Modelo específico a ser usado')
@click.option('--temperature', type=float, help='Temperatura para geração (0.0-2.0)')
@click.option('--max-tokens', type=int, help='Número máximo de tokens')
@click.option('--show', is_flag=True, help='Mostra configuração atual')
@click.option('--list-models', is_flag=True, help='Lista modelos disponíveis')
def config(api_key: str, provider: str, model: str, temperature: float, max_tokens: int, show: bool, list_models: bool):
    """Configura o agente com suas preferências"""
    console = Console()
    config_manager = ConfigManager()
    
    try:
        # Se --show, mostra configuração atual
        if show:
            if config_manager.is_configured():
                config = config_manager.get_model_config()
                
                table = Table(title="Configuração Atual")
                table.add_column("Configuração", style="cyan")
                table.add_column("Valor", style="green")
                
                table.add_row("Provedor", config.provider.upper())
                table.add_row("Modelo", config.model)
                table.add_row("API Key", "✅ Configurada" if config.api_key else "❌ Não configurada")
                table.add_row("Temperatura", str(config.temperature))
                table.add_row("Max Tokens", str(config.max_tokens))
                
                console.print(table)
            else:
                console.print("[red]❌ Agente não configurado[/red]")
            return
        
        # Se --list-models, mostra modelos disponíveis
        if list_models:
            current_provider = config_manager.get_provider() if config_manager.is_configured() else "openai"
            models = AIProviderFactory.get_available_models(current_provider)
            
            table = Table(title=f"Modelos disponíveis para {current_provider.upper()}")
            table.add_column("Modelo", style="cyan")
            table.add_column("Descrição", style="green")
            
            for model_name, description in models.items():
                table.add_row(model_name, description)
            
            console.print(table)
            return
        
        # Atualiza configurações fornecidas
        if api_key:
            config_manager.update_api_key(api_key)
            console.print("[green]✅ API Key atualizada![/green]")
        
        if provider:
            config_manager.update_provider(provider)
            console.print(f"[green]✅ Provedor atualizado para {provider.upper()}![/green]")
        
        if model:
            config_manager.update_model(model)
            console.print(f"[green]✅ Modelo atualizado para {model}![/green]")
        
        if temperature is not None:
            config_manager.update_temperature(temperature)
            console.print(f"[green]✅ Temperatura atualizada para {temperature}![/green]")
        
        if max_tokens:
            config_manager.update_max_tokens(max_tokens)
            console.print(f"[green]✅ Max tokens atualizado para {max_tokens}![/green]")
        
        # Se nenhum parâmetro foi fornecido, configura interativamente
        if not any([api_key, provider, model, temperature is not None, max_tokens, show, list_models]):
            console.print("[blue]🔧 Configuração interativa[/blue]")
            
            # Solicita API Key
            api_key = click.prompt("🔑 Digite sua chave da API", type=str)
            config_manager.update_api_key(api_key)
            
            # Escolhe provedor
            provider = click.prompt(
                "🤖 Escolha o provedor",
                type=click.Choice(['openai', 'google']),
                default='openai'
            )
            config_manager.update_provider(provider)
            
            # Mostra modelos disponíveis
            models = AIProviderFactory.get_available_models(provider)
            console.print(f"\n[blue]Modelos disponíveis para {provider.upper()}:[/blue]")
            for model_name, description in models.items():
                console.print(f"  • {model_name}: {description}")
            
            # Escolhe modelo
            model = click.prompt(
                "🧠 Escolha o modelo",
                type=click.Choice(list(models.keys())),
                default='gpt-4o-mini' if provider == 'openai' else 'gemini-1.5-flash'
            )
            config_manager.update_model(model)
            
            # Configura temperatura
            temperature = click.prompt(
                "🌡️ Temperatura (0.0-2.0, baixa = mais consistente)",
                type=float,
                default=0.1
            )
            config_manager.update_temperature(temperature)
            
            console.print("[green]✅ Configuração salva com sucesso![/green]")
        
    except Exception as e:
        console.print(f"[red]❌ Erro ao configurar: {e}[/red]")


@cli.command()
def status():
    """Mostra o status atual do agente"""
    console = Console()
    config_manager = ConfigManager()
    
    if config_manager.is_configured():
        config = config_manager.get_model_config()
        
        table = Table(title="Status do Open Agent CLI")
        table.add_column("Configuração", style="cyan")
        table.add_column("Valor", style="green")
        
        table.add_row("Provedor", config.provider.upper())
        table.add_row("Modelo", config.model)
        table.add_row("API Key", "✅ Configurada" if config.api_key else "❌ Não configurada")
        table.add_row("Temperatura", str(config.temperature))
        table.add_row("Max Tokens", str(config.max_tokens))
        
        console.print(table)
        console.print("[green]✅ Agente configurado e pronto para uso![/green]")
    else:
        console.print("[red]❌ Agente não configurado[/red]")
        console.print("[yellow]💡 Use 'open-agent config' para configurar[/yellow]")


@cli.command()
@click.argument('request', nargs=-1)
@click.option('--type', 'project_type', help='Tipo específico de projeto')
@click.option('--safe/--no-safe', default=True, help='Modo seguro (confirma ações)')
def run(request: tuple, project_type: str, safe: bool):
    """Executa uma requisição em linguagem natural"""
    console = Console()
    agent = AIAgent()
    
    if not request:
        console.print("[red]❌ Forneça uma requisição[/red]")
        return
    
    user_request = ' '.join(request)
    
    if project_type:
        success = agent.setup_project(project_type, user_request)
    else:
        success = agent.process_request(user_request, safe_mode=safe)
    
    if not success:
        console.print("[red]❌ Falha ao processar requisição[/red]")


@cli.command()
@click.argument('file_path')
@click.argument('instruction', nargs=-1)
def analyze(file_path: str, instruction: tuple):
    """Analisa um arquivo específico"""
    console = Console()
    agent = AIAgent()
    
    if not instruction:
        user_instruction = "Analise este arquivo e sugira melhorias seguindo Clean Code"
    else:
        user_instruction = ' '.join(instruction)
    
    success = agent.analyze_file(file_path, user_instruction)
    
    if not success:
        console.print("[red]❌ Falha ao analisar arquivo[/red]")


@cli.command()
@click.argument('instruction', nargs=-1)
def suggest(instruction: tuple):
    """Sugere melhorias para o projeto atual"""
    console = Console()
    agent = AIAgent()
    
    if not instruction:
        user_instruction = "Sugira melhorias gerais para este projeto"
    else:
        user_instruction = ' '.join(instruction)
    
    success = agent.suggest_improvements(user_instruction)
    
    if not success:
        console.print("[red]❌ Falha ao gerar sugestões[/red]")


@cli.command()
@click.argument('target')
@click.argument('instruction', nargs=-1)
def deploy(target: str, instruction: tuple):
    """Configura deploy para uma plataforma específica"""
    console = Console()
    agent = AIAgent()
    
    if not instruction:
        user_instruction = f"Configure deploy para {target}"
    else:
        user_instruction = ' '.join(instruction)
    
    success = agent.configure_deployment(target, user_instruction)
    
    if not success:
        console.print("[red]❌ Falha ao configurar deploy[/red]")


@cli.command()
@click.option('--pattern', help='Padrão de arquivos para listar')
@click.option('--content', is_flag=True, help='Mostra conteúdo dos arquivos')
def list_files(pattern: str, content: bool):
    """Lista arquivos do projeto atual"""
    console = Console()
    from .core.file_manager import FileManager
    
    file_manager = FileManager()
    files = file_manager.list_files(pattern)
    
    if not files:
        console.print("[yellow]⚠️ Nenhum arquivo encontrado[/yellow]")
        return
    
    table = Table(title="Arquivos do Projeto")
    table.add_column("Arquivo", style="cyan")
    table.add_column("Tamanho", style="green")
    
    for file_path in files:
        size = file_manager.get_file_size(file_path)
        table.add_row(str(file_path), f"{size} bytes")
    
    console.print(table)
    
    if content:
        console.print("\n[blue]📄 Conteúdo dos arquivos:[/blue]")
        for file_path in files[:5]:  # Limita a 5 arquivos
            file_content = file_manager.read_file(file_path)
            if file_content is not None:
                panel = Panel(
                    Text(file_content[:500] + "..." if len(file_content) > 500 else file_content),
                    title=str(file_path),
                    border_style="blue"
                )
                console.print(panel)


@cli.command()
def version():
    """Mostra a versão do Open Agent CLI"""
    console = Console()
    console.print("[green]Open Agent CLI v1.0.0[/green]")
    console.print("[blue]🤖 Assistente de IA para desenvolvimento[/blue]")


if __name__ == '__main__':
    cli() 