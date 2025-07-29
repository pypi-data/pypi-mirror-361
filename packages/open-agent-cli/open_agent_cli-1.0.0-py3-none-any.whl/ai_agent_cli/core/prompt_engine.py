"""
Engine de prompts para montar prompts contextuais para o Gemini
"""
from typing import List, Dict, Optional
from pathlib import Path


class PromptEngine:
    """Engine para montar prompts contextuais"""
    
    def __init__(self):
        self.system_prompt = self._get_system_prompt()
    
    def _get_system_prompt(self) -> str:
        """Retorna o prompt do sistema"""
        return """Você é um assistente de desenvolvimento de software especializado em criar projetos estruturados e código limpo seguindo as melhores práticas de Clean Code.

CAPACIDADES:
- Criar projetos com arquitetura bem estruturada
- Implementar Clean Code e boas práticas
- Criar e modificar arquivos de código com indentação correta
- Executar comandos de terminal de forma segura
- Analisar e melhorar estrutura de projetos
- Sugerir otimizações e refatorações
- Configurar ferramentas de desenvolvimento

DIRETRIZES DE CÓDIGO LIMPO:
1. SEMPRE use indentação consistente (4 espaços para Python, 2 para JavaScript/TypeScript)
2. NUNCA use ```python``` ou ```javascript``` nos códigos - apenas o código puro
3. Siga princípios SOLID e Clean Architecture
4. Use nomes descritivos para variáveis, funções e classes
5. Mantenha funções pequenas e com responsabilidade única
6. Evite código duplicado (DRY - Don't Repeat Yourself)
7. Use comentários apenas quando necessário
8. Siga convenções de nomenclatura da linguagem
9. Organize imports e dependências adequadamente
10. SEMPRE mantenha espaçamento adequado entre funções e classes

COMANDOS SHELL:
- SEMPRE use 'bash -c "comando"' para comandos complexos com && ou ||
- Use '.' em vez de 'source' para ativar ambientes virtuais
- Para comandos em sequência, use: bash -c "comando1 && comando2 && comando3"
- Exemplo: bash -c "cd projeto && python3 -m venv venv && . venv/bin/activate && pip install -r requirements.txt"

ESTRUTURA DE PROJETOS:
Para projetos full-stack, sempre separe em:
- frontend/ (aplicação frontend)
- backend/ (API e lógica de negócio)
- shared/ (código compartilhado)
- docs/ (documentação)
- scripts/ (scripts de automação)
- tests/ (testes)

Para projetos específicos:
- src/ (código fonte)
- lib/ (bibliotecas)
- config/ (configurações)
- assets/ (recursos estáticos)
- dist/ ou build/ (arquivos compilados)

FORMATO DE RESPOSTA:
Para ações que envolvem criação/modificação de arquivos, responda com:
```
ACTION: create_file|modify_file|run_command
TARGET: caminho/do/arquivo
CONTENT: conteúdo do arquivo com indentação correta (4 espaços para Python, 2 para JS/TS)
```

Para comandos shell:
```
ACTION: run_command
COMMAND: comando a ser executado
DESCRIPTION: explicação do que o comando faz
```

Para sugestões ou análises:
```
ACTION: suggest
CONTENT: sua sugestão ou análise
```

IMPORTANTE: 
- NUNCA use ```python``` ou ```javascript``` nos códigos
- SEMPRE use indentação correta (4 espaços para Python)
- Mantenha espaçamento adequado entre funções e classes
- Use nomes descritivos e significativos

EXEMPLOS DE AÇÕES:
- Criar estrutura de projeto com separação clara de responsabilidades
- Implementar padrões de projeto adequados
- Adicionar validações e tratamento de erros
- Configurar testes unitários e de integração
- Implementar logging e monitoramento
- Configurar CI/CD e deploy
- Documentar APIs e código
- Otimizar performance e segurança

Lembre-se: Sempre crie código limpo, bem estruturado e seguindo as melhores práticas!"""
    
    def build_context_prompt(self, user_request: str, file_context: str, 
                           system_info: Optional[Dict] = None) -> str:
        """Monta o prompt completo com contexto"""
        
        prompt = f"{self.system_prompt}\n\n"
        
        # Adiciona informações do sistema se disponíveis
        if system_info:
            prompt += "INFORMAÇÕES DO SISTEMA:\n"
            for key, value in system_info.items():
                prompt += f"- {key}: {value}\n"
            prompt += "\n"
        
        # Adiciona contexto dos arquivos
        prompt += f"CONTEXTO DO PROJETO:\n{file_context}\n\n"
        
        # Adiciona a requisição do usuário
        prompt += f"REQUISIÇÃO DO USUÁRIO:\n{user_request}\n\n"
        
        prompt += "Por favor, analise o contexto e execute as ações necessárias para atender à requisição do usuário. Se houver múltiplas ações, execute-as em sequência lógica."
        
        return prompt
    
    def build_file_analysis_prompt(self, file_path: str, file_content: str, 
                                 user_request: str) -> str:
        """Monta prompt para análise de arquivo específico"""
        
        prompt = f"{self.system_prompt}\n\n"
        prompt += f"ANÁLISE DE ARQUIVO:\n"
        prompt += f"Arquivo: {file_path}\n"
        prompt += f"Conteúdo:\n{file_content}\n\n"
        prompt += f"REQUISIÇÃO DO USUÁRIO:\n{user_request}\n\n"
        prompt += "Analise o arquivo acima e sugira melhorias seguindo Clean Code:\n"
        prompt += "- Mantenha a funcionalidade existente\n"
        prompt += "- Melhore a legibilidade e estrutura\n"
        prompt += "- Use nomes mais descritivos\n"
        prompt += "- Separe responsabilidades se necessário\n"
        prompt += "- Adicione validações e tratamento de erros\n"
        prompt += "- Mantenha indentação consistente\n"
        prompt += "- Siga convenções da linguagem\n"
        prompt += "- Documente funções complexas\n"
        
        return prompt
    
    def build_project_setup_prompt(self, project_type: str, user_request: str,
                                 system_info: Optional[Dict] = None) -> str:
        """Monta prompt para configuração de projeto"""
        
        prompt = f"{self.system_prompt}\n\n"
        
        if system_info:
            prompt += "INFORMAÇÕES DO SISTEMA:\n"
            for key, value in system_info.items():
                prompt += f"- {key}: {value}\n"
            prompt += "\n"
        
        prompt += f"TIPO DE PROJETO: {project_type}\n"
        prompt += f"REQUISIÇÃO DO USUÁRIO:\n{user_request}\n\n"
        prompt += f"Crie um projeto {project_type} completo seguindo Clean Architecture e Clean Code:\n\n"
        prompt += "ESTRUTURA OBRIGATÓRIA:\n"
        prompt += "- Organize o código em camadas (presentation, business, data)\n"
        prompt += "- Separe responsabilidades claramente\n"
        prompt += "- Use injeção de dependência\n"
        prompt += "- Implemente tratamento de erros robusto\n"
        prompt += "- Adicione validações de entrada\n"
        prompt += "- Configure logging estruturado\n"
        prompt += "- Implemente testes unitários\n"
        prompt += "- Documente APIs e código\n"
        prompt += "- Configure linting e formatação\n"
        prompt += "- Adicione scripts de automação\n"
        prompt += "- Configure ambiente de desenvolvimento\n"
        prompt += "- Implemente CI/CD básico\n\n"
        prompt += "QUALIDADE DO CÓDIGO:\n"
        prompt += "- SEMPRE use indentação correta (4 espaços para Python, 2 para JS/TS)\n"
        prompt += "- NUNCA use ```python``` ou ```javascript``` nos códigos\n"
        prompt += "- Use nomes descritivos e significativos\n"
        prompt += "- Mantenha funções pequenas e focadas\n"
        prompt += "- Evite código duplicado\n"
        prompt += "- Use comentários apenas quando necessário\n"
        prompt += "- Siga convenções da linguagem/framework\n"
        prompt += "- Implemente padrões de projeto adequados\n"
        prompt += "- Mantenha espaçamento adequado entre funções e classes\n"
        
        return prompt
    
    def build_improvement_prompt(self, current_state: str, user_request: str) -> str:
        """Monta prompt para sugestões de melhoria"""
        
        prompt = f"{self.system_prompt}\n\n"
        prompt += f"ESTADO ATUAL DO PROJETO:\n{current_state}\n\n"
        prompt += f"REQUISIÇÃO DE MELHORIA:\n{user_request}\n\n"
        prompt += "Analise o projeto atual e sugira melhorias específicas seguindo Clean Code e Clean Architecture:\n\n"
        prompt += "MELHORIAS DE ARQUITETURA:\n"
        prompt += "- Separação clara de responsabilidades\n"
        prompt += "- Implementação de padrões adequados\n"
        prompt += "- Melhoria na estrutura de diretórios\n"
        prompt += "- Refatoração de código duplicado\n\n"
        prompt += "MELHORIAS DE QUALIDADE:\n"
        prompt += "- Otimizações de performance\n"
        prompt += "- Melhoria na legibilidade\n"
        prompt += "- Adição de validações\n"
        prompt += "- Implementação de testes\n"
        prompt += "- Documentação de código\n\n"
        prompt += "MELHORIAS DE INFRAESTRUTURA:\n"
        prompt += "- Configurações de deploy\n"
        prompt += "- CI/CD e automação\n"
        prompt += "- Monitoramento e logging\n"
        prompt += "- Segurança e boas práticas\n"
        
        return prompt
    
    def build_deployment_prompt(self, project_info: str, deployment_target: str,
                              user_request: str) -> str:
        """Monta prompt para configuração de deploy"""
        
        prompt = f"{self.system_prompt}\n\n"
        prompt += f"INFORMAÇÕES DO PROJETO:\n{project_info}\n\n"
        prompt += f"ALVO DE DEPLOY: {deployment_target}\n"
        prompt += f"REQUISIÇÃO DO USUÁRIO:\n{user_request}\n\n"
        prompt += f"Configure o deploy do projeto para {deployment_target}. Inclua:\n"
        prompt += "- Arquivos de configuração de deploy\n"
        prompt += "- Scripts de build e deploy\n"
        prompt += "- Configurações de ambiente\n"
        prompt += "- Documentação de deploy\n"
        prompt += "- Considerações de segurança\n"
        
        return prompt
    
    def parse_ai_response(self, response: str) -> List[Dict]:
        """Parseia a resposta da IA para extrair ações"""
        actions = []
        lines = response.split('\n')
        
        current_action = {}
        in_content = False
        content_lines = []
        
        for line in lines:
            line = line.strip()
            
            if line.startswith('ACTION:'):
                # Salva ação anterior se existir
                if current_action:
                    if content_lines:
                        current_action['content'] = '\n'.join(content_lines)
                    actions.append(current_action)
                
                # Inicia nova ação
                action_type = line.split(':', 1)[1].strip()
                current_action = {'type': action_type}
                in_content = False
                content_lines = []
                
            elif line.startswith('TARGET:') or line.startswith('COMMAND:') or line.startswith('DESCRIPTION:'):
                key = line.split(':', 1)[0].lower()
                value = line.split(':', 1)[1].strip()
                current_action[key] = value
                in_content = False
                
            elif line.startswith('CONTENT:'):
                in_content = True
                content_lines = []
                
            elif in_content and line:
                content_lines.append(line)
        
        # Adiciona a última ação
        if current_action:
            if content_lines:
                current_action['content'] = '\n'.join(content_lines)
            actions.append(current_action)
        
        return actions 