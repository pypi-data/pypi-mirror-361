"""
Gerenciamento de arquivos e diretórios
"""
import os
import shutil
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from rich.console import Console
from rich.tree import Tree
import autopep8


class FileManager:
    """Gerenciador de arquivos para o Open Agent CLI"""
    
    def __init__(self, base_path: Optional[Path] = None):
        self.base_path = base_path or Path.cwd()
        self.console = Console()
    
    def get_project_structure(self, max_depth: int = 3) -> str:
        """Retorna a estrutura do projeto como string"""
        tree = Tree(f"📁 {self.base_path.name}")
        self._build_tree(self.base_path, tree, 0, max_depth)
        
        # Captura a saída do tree
        with self.console.capture() as capture:
            self.console.print(tree)
        
        return capture.get()
    
    def _build_tree(self, path: Path, tree: Tree, depth: int, max_depth: int) -> None:
        """Constrói a árvore de diretórios recursivamente"""
        if depth >= max_depth:
            return
        
        try:
            items = sorted(path.iterdir(), key=lambda x: (x.is_file(), x.name.lower()))
            
            for item in items:
                if item.is_dir():
                    if not item.name.startswith('.') and item.name not in ['__pycache__', 'node_modules', '.git']:
                        branch = tree.add(f"📁 {item.name}")
                        self._build_tree(item, branch, depth + 1, max_depth)
                else:
                    if not item.name.startswith('.'):
                        icon = self._get_file_icon(item.name)
                        tree.add(f"{icon} {item.name}")
        except PermissionError:
            tree.add("🔒 [red]Acesso negado[/red]")
    
    def _get_file_icon(self, filename: str) -> str:
        """Retorna o ícone apropriado para o tipo de arquivo"""
        ext = Path(filename).suffix.lower()
        
        icons = {
            '.py': '🐍',
            '.js': '📜',
            '.ts': '📜',
            '.jsx': '⚛️',
            '.tsx': '⚛️',
            '.html': '🌐',
            '.css': '🎨',
            '.json': '📋',
            '.md': '📝',
            '.txt': '📄',
            '.yml': '⚙️',
            '.yaml': '⚙️',
            '.toml': '⚙️',
            '.ini': '⚙️',
            '.cfg': '⚙️',
            '.env': '🔧',
            '.gitignore': '🚫',
            '.dockerfile': '🐳',
            '.dockerignore': '🐳',
            '.sql': '🗄️',
            '.xml': '📄',
            '.csv': '📊',
            '.log': '📋',
        }
        
        return icons.get(ext, '📄')
    
    def read_file(self, file_path: str) -> Optional[str]:
        """Lê o conteúdo de um arquivo"""
        try:
            full_path = self.base_path / file_path
            if full_path.exists() and full_path.is_file():
                with open(full_path, 'r', encoding='utf-8') as f:
                    return f.read()
            else:
                return None
        except Exception as e:
            self.console.print(f"[red]Erro ao ler arquivo {file_path}: {e}[/red]")
            return None
    
    def write_file(self, file_path: str, content: str, overwrite: bool = False) -> bool:
        """Escreve conteúdo em um arquivo"""
        try:
            full_path = self.base_path / file_path

            # Verifica se o arquivo existe e não deve ser sobrescrito
            if full_path.exists() and not overwrite:
                self.console.print(f"[yellow]Arquivo {file_path} já existe. Use --overwrite para sobrescrever.[/yellow]")
                return False

            # Cria o diretório pai se não existir
            full_path.parent.mkdir(parents=True, exist_ok=True)

            # Pós-processamento universal para diferentes linguagens
            language = self._detect_language(str(full_path))
            
            # Remove blocos de markdown (linhas com apenas ```)
            content = '\n'.join([line for line in content.splitlines() if line.strip() != '```'])
            
            # Aplica indentação específica para a linguagem
            content = self._universal_indent(content, language)
            
            # Para Python, aplica autopep8 adicional se disponível
            if language == 'python':
                try:
                    content = autopep8.fix_code(content, options={'aggressive': 1})
                except Exception as e:
                    # Se autopep8 falhar, mantém a indentação já aplicada
                    pass

            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)

            self.console.print(f"[green]✅ Arquivo {file_path} criado/modificado com sucesso![green]")
            return True
            
        except Exception as e:
            self.console.print(f"[red]Erro ao escrever arquivo {file_path}: {e}[/red]")
            return False
    
    def create_directory(self, dir_path: str) -> bool:
        """Cria um diretório"""
        try:
            full_path = self.base_path / dir_path
            full_path.mkdir(parents=True, exist_ok=True)
            self.console.print(f"[green]✅ Diretório {dir_path} criado com sucesso![/green]")
            return True
        except Exception as e:
            self.console.print(f"[red]Erro ao criar diretório {dir_path}: {e}[/red]")
            return False
    
    def file_exists(self, file_path: str) -> bool:
        """Verifica se um arquivo existe"""
        return (self.base_path / file_path).exists()
    
    def get_file_info(self, file_path: str) -> Optional[Dict]:
        """Retorna informações sobre um arquivo"""
        try:
            full_path = self.base_path / file_path
            if full_path.exists():
                stat = full_path.stat()
                return {
                    'name': full_path.name,
                    'size': stat.st_size,
                    'modified': stat.st_mtime,
                    'is_file': full_path.is_file(),
                    'is_dir': full_path.is_dir(),
                }
            return None
        except Exception:
            return None
    
    def get_file_size(self, file_path: str) -> int:
        """Retorna o tamanho de um arquivo em bytes"""
        try:
            full_path = self.base_path / file_path
            if full_path.exists() and full_path.is_file():
                return full_path.stat().st_size
            return 0
        except Exception:
            return 0
    
    def list_files(self, pattern: str = "**/*") -> List[str]:
        """Lista arquivos que correspondem ao padrão (recursivo por padrão)"""
        try:
            files = []
            for file_path in self.base_path.glob(pattern):
                if file_path.is_file() and not file_path.name.startswith('.'):
                    files.append(str(file_path.relative_to(self.base_path)))
            return sorted(files)
        except Exception:
            return []
    
    def get_relevant_files(self, extensions: Optional[List[str]] = None) -> List[str]:
        """Retorna arquivos relevantes para análise"""
        if extensions is None:
            extensions = ['.py', '.js', '.ts', '.jsx', '.tsx', '.html', '.css', '.json', '.md', '.yml', '.yaml']
        
        relevant_files = []
        for ext in extensions:
            relevant_files.extend(self.list_files(f"**/*{ext}"))
        
        return relevant_files
    
    def get_file_context(self, max_files: int = 10) -> str:
        """Retorna contexto dos arquivos mais relevantes"""
        relevant_files = self.get_relevant_files()
        
        if not relevant_files:
            return "Nenhum arquivo relevante encontrado no projeto."
        
        context = "📁 Estrutura do projeto:\n"
        context += self.get_project_structure()
        context += "\n\n📄 Arquivos relevantes:\n"
        
        for i, file_path in enumerate(relevant_files[:max_files]):
            content = self.read_file(file_path)
            if content:
                # Limita o conteúdo para não sobrecarregar o contexto
                preview = content[:500] + "..." if len(content) > 500 else content
                context += f"\n--- {file_path} ---\n{preview}\n"
        
        if len(relevant_files) > max_files:
            context += f"\n... e mais {len(relevant_files) - max_files} arquivos."
        
        return context 

    def _basic_python_indent(self, code: str) -> str:
        """Pré-processa código Python sem indentação mínima"""
        lines = code.splitlines()
        result = []
        indent_level = 0
        in_function = False
        
        for line in lines:
            stripped = line.strip()
            
            # Se é uma definição de função ou classe, reseta o nível
            if stripped.startswith(("def ", "class ")):
                result.append(stripped)
                in_function = True
                indent_level = 1
                continue
            
            # Se é uma linha vazia, mantém
            if not stripped:
                result.append("")
                continue
            
            # Se estamos dentro de uma função, indenta
            if in_function and stripped:
                # Se a linha começa com return, break, continue, etc., pode ser o fim da função
                if stripped.startswith(("return", "break", "continue", "pass", "raise", "yield")):
                    result.append("    " * indent_level + stripped)
                    # Se não há mais código após, pode ser fim da função
                    continue
                
                # Se é um if, for, while, try, etc., aumenta indentação
                if stripped.startswith(("if ", "for ", "while ", "try:", "except", "finally", "with ", "else:", "elif ")):
                    result.append("    " * indent_level + stripped)
                    indent_level += 1
                    continue
                
                # Se é um else, elif, except, etc., diminui indentação
                if stripped.startswith(("else:", "elif ", "except", "finally")):
                    indent_level = max(0, indent_level - 1)
                    result.append("    " * indent_level + stripped)
                    indent_level += 1
                    continue
                
                # Linha normal dentro da função
                result.append("    " * indent_level + stripped)
            else:
                # Linha fora de função
                result.append(stripped)
        
        return "\n".join(result) 

    def _detect_language(self, file_path: str) -> str:
        """Detecta a linguagem baseada na extensão do arquivo"""
        ext = Path(file_path).suffix.lower()
        language_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.jsx': 'javascript',
            '.tsx': 'typescript',
            '.html': 'html',
            '.htm': 'html',
            '.css': 'css',
            '.scss': 'scss',
            '.sass': 'sass',
            '.json': 'json',
            '.xml': 'xml',
            '.yaml': 'yaml',
            '.yml': 'yaml',
            '.toml': 'toml',
            '.ini': 'ini',
            '.cfg': 'ini',
            '.conf': 'ini',
            '.sh': 'bash',
            '.bash': 'bash',
            '.zsh': 'bash',
            '.fish': 'bash',
            '.ps1': 'powershell',
            '.bat': 'batch',
            '.cmd': 'batch',
            '.java': 'java',
            '.c': 'c',
            '.cpp': 'cpp',
            '.cc': 'cpp',
            '.cxx': 'cpp',
            '.h': 'c',
            '.hpp': 'cpp',
            '.cs': 'csharp',
            '.php': 'php',
            '.rb': 'ruby',
            '.go': 'go',
            '.rs': 'rust',
            '.swift': 'swift',
            '.kt': 'kotlin',
            '.scala': 'scala',
            '.r': 'r',
            '.m': 'matlab',
            '.pl': 'perl',
            '.lua': 'lua',
            '.sql': 'sql',
            '.vue': 'vue',
            '.svelte': 'svelte',
        }
        return language_map.get(ext, 'text')

    def _get_indent_size(self, language: str) -> int:
        """Retorna o tamanho da indentação para cada linguagem"""
        indent_map = {
            'python': 4,
            'javascript': 2,
            'typescript': 2,
            'html': 2,
            'css': 2,
            'scss': 2,
            'sass': 2,
            'json': 2,
            'xml': 2,
            'yaml': 2,
            'toml': 2,
            'ini': 2,
            'bash': 2,
            'powershell': 4,
            'batch': 4,
            'java': 4,
            'c': 4,
            'cpp': 4,
            'csharp': 4,
            'php': 4,
            'ruby': 2,
            'go': 4,
            'rust': 4,
            'swift': 4,
            'kotlin': 4,
            'scala': 2,
            'r': 2,
            'matlab': 4,
            'perl': 4,
            'lua': 2,
            'sql': 2,
            'vue': 2,
            'svelte': 2,
        }
        return indent_map.get(language, 4)

    def _universal_indent(self, code: str, language: str) -> str:
        """Aplica indentação universal baseada na linguagem detectada"""
        if language == 'python':
            return self._basic_python_indent(code)
        elif language in ['javascript', 'typescript']:
            return self._js_indent(code)
        elif language == 'html':
            return self._html_indent(code)
        elif language == 'css':
            return self._css_indent(code)
        elif language == 'bash':
            return self._bash_indent(code)
        else:
            # Para outras linguagens, usa indentação básica
            return self._basic_indent(code, self._get_indent_size(language))

    def _js_indent(self, code: str) -> str:
        """Indentação específica para JavaScript/TypeScript"""
        lines = code.splitlines()
        result = []
        indent_level = 0
        indent_size = 2
        
        for line in lines:
            stripped = line.strip()
            
            # Se é uma definição de função, classe, etc.
            if stripped.startswith(("function ", "class ", "const ", "let ", "var ", "export ", "import ")):
                result.append("  " * indent_level + stripped)
                indent_level += 1
                continue
            
            # Se é um bloco de controle
            if stripped.startswith(("if ", "for ", "while ", "try", "catch", "finally", "switch ")):
                result.append("  " * indent_level + stripped)
                indent_level += 1
                continue
            
            # Se é um else, else if, etc.
            if stripped.startswith(("else", "catch", "finally")):
                indent_level = max(0, indent_level - 1)
                result.append("  " * indent_level + stripped)
                indent_level += 1
                continue
            
            # Se é um return, break, continue
            if stripped.startswith(("return", "break", "continue")):
                result.append("  " * indent_level + stripped)
                continue
            
            # Se é um fechamento de bloco
            if stripped == "}" or stripped.startswith("}"):
                indent_level = max(0, indent_level - 1)
                result.append("  " * indent_level + stripped)
                continue
            
            # Se é uma abertura de bloco
            if stripped.endswith("{"):
                result.append("  " * indent_level + stripped)
                indent_level += 1
                continue
            
            # Linha normal
            if stripped:
                result.append("  " * indent_level + stripped)
            else:
                result.append("")
        
        return "\n".join(result)

    def _html_indent(self, code: str) -> str:
        """Indentação específica para HTML"""
        lines = code.splitlines()
        result = []
        indent_level = 0
        indent_size = 2
        
        for line in lines:
            stripped = line.strip()
            
            # Se é uma tag de fechamento
            if stripped.startswith("</"):
                indent_level = max(0, indent_level - 1)
                result.append("  " * indent_level + stripped)
                continue
            
            # Se é uma tag de abertura
            if stripped.startswith("<") and not stripped.startswith("</") and not stripped.endswith("/>"):
                result.append("  " * indent_level + stripped)
                indent_level += 1
                continue
            
            # Se é uma tag auto-fechada
            if stripped.startswith("<") and stripped.endswith("/>"):
                result.append("  " * indent_level + stripped)
                continue
            
            # Linha normal
            if stripped:
                result.append("  " * indent_level + stripped)
            else:
                result.append("")
        
        return "\n".join(result)

    def _css_indent(self, code: str) -> str:
        """Indentação específica para CSS"""
        lines = code.splitlines()
        result = []
        indent_level = 0
        indent_size = 2
        
        for line in lines:
            stripped = line.strip()
            
            # Se é um seletor
            if stripped.endswith("{"):
                result.append("  " * indent_level + stripped)
                indent_level += 1
                continue
            
            # Se é um fechamento de bloco
            if stripped == "}":
                indent_level = max(0, indent_level - 1)
                result.append("  " * indent_level + stripped)
                continue
            
            # Linha normal
            if stripped:
                result.append("  " * indent_level + stripped)
            else:
                result.append("")
        
        return "\n".join(result)

    def _bash_indent(self, code: str) -> str:
        """Indentação específica para Bash/Shell"""
        lines = code.splitlines()
        result = []
        indent_level = 0
        indent_size = 2
        
        for line in lines:
            stripped = line.strip()
            
            # Se é um if, for, while, case, etc.
            if stripped.startswith(("if ", "for ", "while ", "case ", "select ")):
                result.append("  " * indent_level + stripped)
                indent_level += 1
                continue
            
            # Se é um else, elif, esac, done, fi
            if stripped.startswith(("else", "elif", "esac", "done", "fi")):
                indent_level = max(0, indent_level - 1)
                result.append("  " * indent_level + stripped)
                continue
            
            # Linha normal
            if stripped:
                result.append("  " * indent_level + stripped)
            else:
                result.append("")
        
        return "\n".join(result)

    def _basic_indent(self, code: str, indent_size: int) -> str:
        """Indentação básica para outras linguagens"""
        lines = code.splitlines()
        result = []
        indent_level = 0
        indent_char = " " * indent_size
        
        for line in lines:
            stripped = line.strip()
            
            # Se é uma definição de função, classe, etc.
            if stripped.startswith(("def ", "class ", "function ", "public ", "private ", "protected ")):
                result.append(stripped)
                indent_level += 1
                continue
            
            # Se é um bloco de controle
            if stripped.startswith(("if ", "for ", "while ", "try", "catch", "switch ")):
                result.append(indent_char * indent_level + stripped)
                indent_level += 1
                continue
            
            # Se é um else, else if, etc.
            if stripped.startswith(("else", "catch", "finally")):
                indent_level = max(0, indent_level - 1)
                result.append(indent_char * indent_level + stripped)
                indent_level += 1
                continue
            
            # Linha normal
            if stripped:
                result.append(indent_char * indent_level + stripped)
            else:
                result.append("")
        
        return "\n".join(result) 