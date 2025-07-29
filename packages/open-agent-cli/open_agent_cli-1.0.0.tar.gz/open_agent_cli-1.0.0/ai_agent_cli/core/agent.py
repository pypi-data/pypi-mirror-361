"""
Agente principal que integra todos os componentes
"""
from typing import List, Dict, Optional
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.prompt import Confirm

from .config import ConfigManager
from .file_manager import FileManager
from .shell_runner import ShellRunner
from .prompt_engine import PromptEngine
from .ai_provider import AIProviderFactory


class AIAgent:
    """Agente principal de IA"""
    
    def __init__(self):
        self.console = Console()
        self.config_manager = ConfigManager()
        self.file_manager = FileManager()
        self.shell_runner = ShellRunner()
        self.prompt_engine = PromptEngine()
        self.ai_provider = None
        
        # Inicializa o provedor se configurado
        if self.config_manager.is_configured():
            self._initialize_provider()
    
    def _initialize_provider(self):
        """Inicializa o provedor de IA"""
        try:
            config = self.config_manager.get_model_config()
            
            if not config.api_key:
                self.console.print("[red]❌ API Key não configurada. Use 'open-agent config' para configurar.[/red]")
                self.ai_provider = None
                return
                
            self.ai_provider = AIProviderFactory.create_provider(
                provider=config.provider,
                api_key=config.api_key,
                model=config.model,
                temperature=config.temperature
            )
            
            provider_name = config.provider.upper()
            self.console.print(f"[green]✅ Provedor {provider_name} inicializado com sucesso![/green]")
        except Exception as e:
            self.console.print(f"[red]❌ Erro ao inicializar provedor: {e}[/red]")
            self.ai_provider = None
    
    def is_ready(self) -> bool:
        """Verifica se o agente está pronto para uso"""
        if not self.config_manager.is_configured():
            self.console.print("[red]❌ Agente não configurado. Use 'open-agent config' para configurar.[/red]")
            return False
        
        if self.ai_provider is None:
            self._initialize_provider()
            if self.ai_provider is None:
                return False
        
        return True
    
    def process_request(self, user_request: str, safe_mode: bool = True) -> bool:
        """Processa uma requisição do usuário"""
        
        if not self.is_ready():
            return False
        
        try:
            # Obtém contexto do projeto
            file_context = self.file_manager.get_file_context()
            system_info = self.shell_runner.get_system_info()
            
            # Monta o prompt
            prompt = self.prompt_engine.build_context_prompt(
                user_request, file_context, system_info
            )
            
            self.console.print("[blue]🤖 Processando sua requisição...[/blue]")
            
            # Gera resposta da IA
            if self.ai_provider is None:
                self.console.print("[red]❌ Provedor de IA não inicializado[/red]")
                return False
                
            response = self.ai_provider.generate_content(prompt)
            
            if not response:
                self.console.print("[red]❌ Não foi possível gerar uma resposta.[/red]")
                return False
            
            # Parseia as ações
            actions = self.prompt_engine.parse_ai_response(response)
            
            if not actions:
                # Se não conseguiu parsear ações, mostra a resposta completa
                self.console.print(Panel(
                    Text(response, style="blue"),
                    title="🤖 Resposta da IA",
                    border_style="blue"
                ))
                return True
            
            # Executa as ações
            return self._execute_actions(actions, safe_mode)
            
        except Exception as e:
            self.console.print(f"[red]❌ Erro ao processar requisição: {e}[/red]")
            return False
    
    def _execute_actions(self, actions: List[Dict], safe_mode: bool = True) -> bool:
        """Executa as ações parseadas da resposta da IA"""
        
        success_count = 0
        
        for i, action in enumerate(actions, 1):
            action_type = action.get('type', '').lower()
            
            self.console.print(f"\n[blue]📋 Executando ação {i}/{len(actions)}: {action_type}[/blue]")
            
            if action_type == 'create_file':
                success = self._handle_create_file(action, safe_mode)
            elif action_type == 'modify_file':
                success = self._handle_modify_file(action, safe_mode)
            elif action_type == 'run_command':
                success = self._handle_run_command(action)
            elif action_type == 'suggest':
                success = self._handle_suggest(action)
            else:
                self.console.print(f"[yellow]⚠️ Ação desconhecida: {action_type}[/yellow]")
                success = False
            
            if success:
                success_count += 1
        
        self.console.print(f"\n[green]✅ {success_count}/{len(actions)} ações executadas com sucesso![/green]")
        return success_count > 0
    
    def _handle_create_file(self, action: Dict, safe_mode: bool) -> bool:
        """Manipula criação de arquivo"""
        target = action.get('target', '')
        content = action.get('content', '')
        
        if not target:
            self.console.print("[red]❌ Caminho do arquivo não especificado[/red]")
            return False
        
        if not content:
            self.console.print("[red]❌ Conteúdo do arquivo não especificado[/red]")
            return False
        
        # Verifica se arquivo existe
        if self.file_manager.file_exists(target):
            if safe_mode:
                if not Confirm.ask(f"Arquivo {target} já existe. Sobrescrever?"):
                    self.console.print("[yellow]⚠️ Operação cancelada pelo usuário[/yellow]")
                    return False
        
        return self.file_manager.write_file(target, content, overwrite=True)
    
    def _handle_modify_file(self, action: Dict, safe_mode: bool) -> bool:
        """Manipula modificação de arquivo"""
        target = action.get('target', '')
        content = action.get('content', '')
        
        if not target:
            self.console.print("[red]❌ Caminho do arquivo não especificado[/red]")
            return False
        
        if not self.file_manager.file_exists(target):
            self.console.print(f"[red]❌ Arquivo {target} não existe[/red]")
            return False
        
        if safe_mode:
            if not Confirm.ask(f"Modificar arquivo {target}?"):
                self.console.print("[yellow]⚠️ Operação cancelada pelo usuário[/yellow]")
                return False
        
        return self.file_manager.write_file(target, content, overwrite=True)
    
    def _handle_run_command(self, action: Dict) -> bool:
        """Manipula execução de comando"""
        command = action.get('command', '')
        description = action.get('description', '')
        
        if not command:
            self.console.print("[red]❌ Comando não especificado[/red]")
            return False
        
        if description:
            self.console.print(f"[blue]📝 {description}[/blue]")
        
        # O comando já é corrigido automaticamente no ShellRunner
        return self.shell_runner.run_command_interactive(command)
    
    def _handle_suggest(self, action: Dict) -> bool:
        """Manipula sugestões"""
        content = action.get('content', '')
        
        if not content:
            self.console.print("[red]❌ Conteúdo da sugestão não especificado[/red]")
            return False
        
        panel = Panel(
            Text(content, style="yellow"),
            title="💡 Sugestão da IA",
            border_style="yellow"
        )
        self.console.print(panel)
        return True
    
    def analyze_file(self, file_path: str, user_request: str) -> bool:
        """Analisa um arquivo específico"""
        
        if not self.is_ready():
            return False
        
        try:
            if not self.file_manager.file_exists(file_path):
                self.console.print(f"[red]❌ Arquivo {file_path} não existe[/red]")
                return False
            
            file_content = self.file_manager.read_file(file_path)
            if file_content is None:
                self.console.print(f"[red]❌ Não foi possível ler o arquivo {file_path}[/red]")
                return False
                
            prompt = self.prompt_engine.build_file_analysis_prompt(
                file_path, file_content, user_request
            )
            
            self.console.print("[blue]🤖 Analisando arquivo...[/blue]")
            
            if self.ai_provider is None:
                self.console.print("[red]❌ Provedor de IA não inicializado[/red]")
                return False
                
            response = self.ai_provider.generate_content(prompt)
            
            if not response:
                self.console.print("[red]❌ Não foi possível gerar uma análise.[/red]")
                return False
            
            panel = Panel(
                Text(response, style="green"),
                title=f"📋 Análise de {file_path}",
                border_style="green"
            )
            self.console.print(panel)
            return True
            
        except Exception as e:
            self.console.print(f"[red]❌ Erro ao analisar arquivo: {e}[/red]")
            return False
    
    def setup_project(self, project_type: str, user_request: str) -> bool:
        """Configura um projeto específico"""
        
        if not self.is_ready():
            return False
        
        try:
            system_info = self.shell_runner.get_system_info()
            prompt = self.prompt_engine.build_project_setup_prompt(
                project_type, user_request, system_info
            )
            
            self.console.print(f"[blue]🤖 Configurando projeto {project_type}...[/blue]")
            
            if self.ai_provider is None:
                self.console.print("[red]❌ Provedor de IA não inicializado[/red]")
                return False
                
            response = self.ai_provider.generate_content(prompt)
            
            if not response:
                self.console.print("[red]❌ Não foi possível configurar o projeto.[/red]")
                return False
            
            actions = self.prompt_engine.parse_ai_response(response)
            
            if not actions:
                self.console.print(Panel(
                    Text(response, style="blue"),
                    title="🤖 Configuração do Projeto",
                    border_style="blue"
                ))
                return True
            
            return self._execute_actions(actions, safe_mode=True)
            
        except Exception as e:
            self.console.print(f"[red]❌ Erro ao configurar projeto: {e}[/red]")
            return False
    
    def suggest_improvements(self, user_request: str) -> bool:
        """Sugere melhorias para o projeto"""
        
        if not self.is_ready():
            return False
        
        try:
            file_context = self.file_manager.get_file_context()
            prompt = self.prompt_engine.build_improvement_prompt(
                file_context, user_request
            )
            
            self.console.print("[blue]🤖 Analisando melhorias...[/blue]")
            
            if self.ai_provider is None:
                self.console.print("[red]❌ Provedor de IA não inicializado[/red]")
                return False
                
            response = self.ai_provider.generate_content(prompt)
            
            if not response:
                self.console.print("[red]❌ Não foi possível gerar sugestões.[/red]")
                return False
            
            panel = Panel(
                Text(response, style="yellow"),
                title="💡 Sugestões de Melhoria",
                border_style="yellow"
            )
            self.console.print(panel)
            return True
            
        except Exception as e:
            self.console.print(f"[red]❌ Erro ao gerar sugestões: {e}[/red]")
            return False
    
    def configure_deployment(self, deployment_target: str, user_request: str) -> bool:
        """Configura deploy para uma plataforma específica"""
        
        if not self.is_ready():
            return False
        
        try:
            file_context = self.file_manager.get_file_context()
            prompt = self.prompt_engine.build_deployment_prompt(
                file_context, deployment_target, user_request
            )
            
            self.console.print(f"[blue]🤖 Configurando deploy para {deployment_target}...[/blue]")
            
            if self.ai_provider is None:
                self.console.print("[red]❌ Provedor de IA não inicializado[/red]")
                return False
                
            response = self.ai_provider.generate_content(prompt)
            
            if not response:
                self.console.print("[red]❌ Não foi possível configurar o deploy.[/red]")
                return False
            
            actions = self.prompt_engine.parse_ai_response(response)
            
            if not actions:
                self.console.print(Panel(
                    Text(response, style="blue"),
                    title="🤖 Configuração de Deploy",
                    border_style="blue"
                ))
                return True
            
            return self._execute_actions(actions, safe_mode=True)
            
        except Exception as e:
            self.console.print(f"[red]❌ Erro ao configurar deploy: {e}[/red]")
            return False 