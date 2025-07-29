"""
Execução segura de comandos shell
"""
import subprocess
import shlex
import platform
import os
from typing import List, Dict, Optional, Tuple
from rich.console import Console
from rich.panel import Panel
from rich.text import Text


class ShellRunner:
    """Executor seguro de comandos shell"""
    
    def __init__(self):
        self.console = Console()
        self.system = platform.system().lower()
        self.dangerous_commands = {
            'rm', 'del', 'format', 'dd', 'mkfs', 'fdisk',
            'shutdown', 'reboot', 'halt', 'poweroff',
            'sudo', 'su', 'chmod', 'chown', 'chgrp',
            'kill', 'killall', 'pkill', 'xkill',
            'iptables', 'ufw', 'firewall-cmd'
        }
    
    def is_dangerous_command(self, command: str) -> bool:
        """Verifica se um comando é perigoso"""
        cmd_parts = shlex.split(command.lower())
        if not cmd_parts:
            return False
        
        base_cmd = cmd_parts[0]
        return base_cmd in self.dangerous_commands
    
    def run_command(self, command: str, cwd: Optional[str] = None, 
                   capture_output: bool = True, timeout: int = 300) -> Dict:
        """Executa um comando shell de forma segura"""
        
        # Verifica se é um comando perigoso
        if self.is_dangerous_command(command):
            return {
                'success': False,
                'error': f'Comando perigoso detectado: {command}',
                'output': '',
                'return_code': -1
            }
        
        # Corrige comandos Python automaticamente
        fixed_command = self.fix_python_commands(command)
        
        try:
            # Executa o comando
            result = subprocess.run(
                fixed_command,
                shell=True,
                cwd=cwd,
                capture_output=capture_output,
                text=True,
                timeout=timeout,
                encoding='utf-8'
            )
            
            return {
                'success': result.returncode == 0,
                'output': result.stdout,
                'error': result.stderr,
                'return_code': result.returncode,
                'command': fixed_command
            }
            
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'error': f'Comando excedeu o timeout de {timeout} segundos',
                'output': '',
                'return_code': -1
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Erro ao executar comando: {str(e)}',
                'output': '',
                'return_code': -1
            }
    
    def run_command_interactive(self, command: str, cwd: Optional[str] = None) -> bool:
        """Executa um comando de forma interativa (mostra saída em tempo real)"""
        
        if self.is_dangerous_command(command):
            self.console.print(f"[red]❌ Comando perigoso detectado: {command}[/red]")
            return False
        
        try:
            self.console.print(f"[blue]🔄 Executando: {command}[/blue]")
            
            process = subprocess.Popen(
                command,
                shell=True,
                cwd=cwd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            # Mostra a saída em tempo real
            if process.stdout is not None:
                for line in process.stdout:
                    self.console.print(line.rstrip())
            
            process.wait()
            success = process.returncode == 0
            
            if success:
                self.console.print(f"[green]✅ Comando executado com sucesso![/green]")
            else:
                self.console.print(f"[red]❌ Comando falhou com código {process.returncode}[/red]")
            
            return success
            
        except Exception as e:
            self.console.print(f"[red]❌ Erro ao executar comando: {str(e)}[/red]")
            return False
    
    def run_multiple_commands(self, commands: List[str], cwd: Optional[str] = None) -> List[Dict]:
        """Executa múltiplos comandos em sequência"""
        results = []
        
        for i, command in enumerate(commands, 1):
            self.console.print(f"\n[blue]📋 Comando {i}/{len(commands)}: {command}[/blue]")
            
            result = self.run_command(command, cwd)
            results.append(result)
            
            if not result['success']:
                self.console.print(f"[red]❌ Comando falhou: {result['error']}[/red]")
                # Para de executar se um comando falhar
                break
            else:
                self.console.print(f"[green]✅ Comando {i} executado com sucesso![/green]")
        
        return results
    
    def check_command_exists(self, command: str) -> bool:
        """Verifica se um comando existe no sistema"""
        try:
            if self.system == "windows":
                # No Windows, usa 'where' em vez de 'which'
                result = subprocess.run(
                    f"where {command}",
                    shell=True,
                    capture_output=True,
                    text=True
                )
            else:
                # No Linux/macOS, usa 'which'
                result = subprocess.run(
                    f"which {command}",
                    shell=True,
                    capture_output=True,
                    text=True
                )
            return result.returncode == 0
        except Exception:
            return False
    
    def get_python_command(self) -> str:
        """Detecta automaticamente o comando Python correto para o sistema"""
        # Primeiro tenta python3 (comum em sistemas Linux/macOS modernos)
        if self.check_command_exists("python3"):
            return "python3"
        
        # Depois tenta python (Windows ou sistemas mais antigos)
        if self.check_command_exists("python"):
            return "python"
        
        # Fallback para python3
        return "python3"
    
    def fix_python_commands(self, command: str) -> str:
        """Corrige comandos Python para usar o comando correto detectado e adapta para diferentes shells"""
        import re
        
        # Sempre corrige para python3 se disponível, independente se python também existe
        if self.check_command_exists("python3"):
            # Substitui python por python3 usando regex para capturar word boundaries
            command = re.sub(r'\bpython\b', 'python3', command)
            
            # Corrige comandos pip também
            command = re.sub(r'\bpip\b', 'pip3', command)
        
        # Detecta e adapta para diferentes shells
        shell_adaptations = {
            'source': '.',  # source não funciona em sh/ash
            '&&': '&&',     # && funciona em bash, zsh, fish
            '||': '||',     # || funciona em bash, zsh, fish
        }
        
        # Corrige comandos de ativação de ambiente virtual
        # Substitui 'source venv/bin/activate' por '. venv/bin/activate'
        command = re.sub(r'\bsource\s+([^\s]+/bin/activate)', r'. \1', command)
        
        # Para comandos complexos com operadores, garante compatibilidade
        if any(op in command for op in ['&&', '||', ';']):
            # Detecta o shell disponível e adapta o comando
            if self.check_command_exists("bash"):
                # Bash é mais compatível com operadores complexos
                if not command.startswith('bash -c'):
                    command = f'bash -c "{command}"'
            elif self.check_command_exists("sh"):
                # Para sh/ash, simplifica comandos complexos
                command = self._simplify_for_sh(command)
            else:
                # Fallback para shell padrão
                pass
        
        return command
    
    def _simplify_for_sh(self, command: str) -> str:
        """Simplifica comandos complexos para compatibilidade com sh/ash"""
        import re
        
        # Quebra comandos com && em comandos separados
        if '&&' in command:
            parts = command.split('&&')
            # Executa cada parte separadamente
            return '; '.join([f'({part.strip()})' for part in parts])
        
        # Remove operadores complexos que podem não funcionar em sh
        command = re.sub(r'\|\|', ';', command)  # Substitui || por ;
        
        return command
    
    def get_system_info(self) -> Dict:
        """Retorna informações do sistema de forma compatível"""
        info = {}
        
        # Sistema operacional
        try:
            if self.system == "windows":
                # No Windows, usa 'ver' ou platform
                result = subprocess.run("ver", shell=True, capture_output=True, text=True)
                info['os'] = result.stdout.strip() if result.returncode == 0 else platform.system()
            else:
                # No Linux/macOS, usa 'uname'
                result = subprocess.run("uname -s", shell=True, capture_output=True, text=True)
                info['os'] = result.stdout.strip() if result.returncode == 0 else platform.system()
        except Exception:
            info['os'] = platform.system()
        
        # Detectar versão do Python disponível
        python_cmd = self.get_python_command()
        try:
            result = subprocess.run(f"{python_cmd} --version", shell=True, capture_output=True, text=True)
            info['python'] = result.stdout.strip() if result.returncode == 0 else f"Python {platform.python_version()}"
            info['python_command'] = python_cmd
        except Exception:
            info['python'] = f"Python {platform.python_version()}"
            info['python_command'] = python_cmd
        
        # Node.js (se disponível)
        if self.check_command_exists("node"):
            try:
                result = subprocess.run("node --version", shell=True, capture_output=True, text=True)
                info['node'] = result.stdout.strip() if result.returncode == 0 else "Available"
            except Exception:
                info['node'] = "Available"
        else:
            info['node'] = "Not installed"
        
        # Git (se disponível)
        if self.check_command_exists("git"):
            try:
                result = subprocess.run("git --version", shell=True, capture_output=True, text=True)
                info['git'] = result.stdout.strip() if result.returncode == 0 else "Available"
            except Exception:
                info['git'] = "Available"
        else:
            info['git'] = "Not installed"
        
        return info
    
    def display_command_result(self, result: Dict) -> None:
        """Exibe o resultado de um comando de forma formatada"""
        if result['success']:
            if result['output']:
                panel = Panel(
                    Text(result['output'], style="green"),
                    title="✅ Comando executado com sucesso",
                    border_style="green"
                )
                self.console.print(panel)
        else:
            error_text = f"Comando: {result.get('command', 'N/A')}\nErro: {result['error']}"
            panel = Panel(
                Text(error_text, style="red"),
                title="❌ Comando falhou",
                border_style="red"
            )
            self.console.print(panel) 