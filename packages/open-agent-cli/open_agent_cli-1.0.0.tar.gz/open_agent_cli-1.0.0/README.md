# 🤖 Open Agent CLI

Um agente de inteligência artificial via linha de comando que cria projetos estruturados e código limpo seguindo as melhores práticas de **Clean Code** e **Clean Architecture** usando OpenAI ou Google Generative AI.

## ✨ Funcionalidades

- **Clean Code & Clean Architecture**: Cria projetos seguindo as melhores práticas
- **Indentação correta**: Gera código com indentação consistente e legível (4 espaços Python, 2 JS/TS)
- **Detecção automática de Python3**: Corrige comandos automaticamente para usar python3/pip3
- **Múltiplos provedores**: Suporte a OpenAI e Google Gemini
- **Configuração flexível**: Ajuste modelo, provedor, temperatura e tokens facilmente
- **Estrutura organizada**: Separa responsabilidades em pastas bem definidas
- **Configuração simples**: Configure sua chave da API com um comando
- **Comandos em linguagem natural**: Descreva o que você quer fazer em português
- **Manipulação segura de arquivos**: Criação, leitura e modificação de arquivos
- **Execução segura de comandos**: Comandos shell executados com segurança
- **Análise inteligente**: Entenda a estrutura e sugira melhorias
- **Setup de projetos**: Crie projetos completos com um comando
- **Configuração de deploy**: Configure deploy para diferentes plataformas

## 🚀 Instalação

### Método Rápido (Recomendado)

```bash
# Clone o repositório
git clone <repository>
cd open-agent-cli

# Instale o projeto
pip install -e .

# Configure o agente
open-agent config
```

### Instalação Manual

#### Via pip (recomendado)

```bash
# Instalação global
pip install open-agent-cli

# Ou com pip3
pip3 install open-agent-cli

# Em ambiente virtual
python -m pip install open-agent-cli
```

#### Via pipx (Isolado)

```bash
pipx install open-agent-cli
```

## 🔧 Configuração

### Configuração Rápida

```bash
# Configuração interativa (recomendado)
open-agent config

# Ou configure diretamente
open-agent config --provider openai --api-key SUA_CHAVE --model gpt-4o-mini
```

### Opções de Configuração

```bash
# Ver configuração atual
open-agent config --show

# Listar modelos disponíveis
open-agent config --list-models

# Atualizar apenas o modelo
open-agent config --model gpt-4o-mini

# Atualizar temperatura (0.0-2.0)
open-agent config --temperature 0.1

# Atualizar max tokens
open-agent config --max-tokens 8000

# Trocar provedor
open-agent config --provider google --model gemini-1.5-flash
```

### Provedores e Modelos

#### OpenAI (Recomendado)
- **gpt-4o-mini**: Rápido e econômico para código
- **gpt-4o**: Mais avançado, mas mais caro
- **gpt-3.5-turbo**: Econômico e rápido
- **gpt-4-turbo**: Alta qualidade

#### Google Gemini
- **gemini-1.5-flash**: Rápido e econômico
- **gemini-1.5-pro**: Mais avançado
- **gemini-pro**: Versão estável

## 📖 Como Usar

### Comandos Básicos

#### Executar instruções em linguagem natural

```bash
# Criar um projeto React com Vite
open-agent run "Crie um projeto React com Vite e Tailwind CSS"

# Adicionar uma rota ao FastAPI
open-agent run "Adicione uma rota /users ao meu app FastAPI que retorna um JSON"

# Configurar Docker
open-agent run "Configure Docker para este projeto Python"

# Otimizar código
open-agent run "Otimize o código deste projeto para melhor performance"
```

#### Setup de projetos específicos

```bash
# Criar projeto React
open-agent run --type react "Crie um projeto React moderno com TypeScript"

# Criar projeto Python
open-agent run --type python "Crie um projeto Python com FastAPI e SQLAlchemy"

# Criar projeto Node.js
open-agent run --type node "Crie um projeto Node.js com Express e MongoDB"
```

### Comandos de Análise

#### Listar arquivos do projeto

```bash
# Listar todos os arquivos
open-agent list-files

# Listar arquivos Python
open-agent list-files --pattern "*.py"

# Listar com conteúdo
open-agent list-files --content
```

#### Analisar arquivo específico

```bash
# Analisar arquivo Python
open-agent analyze main.py "Analise este arquivo e sugira melhorias"

# Analisar com instrução específica
open-agent analyze app.py --instruction "Adicione validação de entrada e tratamento de erros"
```

#### Sugerir melhorias

```bash
# Sugestões gerais
open-agent suggest "Como posso melhorar a performance deste projeto?"

# Sugestões específicas
open-agent suggest "Adicione testes unitários e documentação"
```

### Comandos de Deploy

#### Configurar deploy

```bash
# Deploy com Docker
open-agent deploy docker "Configure deploy com Docker e docker-compose"

# Deploy no Heroku
open-agent deploy heroku "Configure deploy no Heroku"

# Deploy em VPS
open-agent deploy vps "Configure deploy em VPS com Nginx e systemd"
```

### Comandos de Sistema

#### Verificar status

```bash
# Status do agente
open-agent status

# Mostrar configuração
open-agent config --show

# Versão
open-agent version
```

## 🛡️ Modo Seguro

O agente opera em modo seguro por padrão, que:

- ✅ Pergunta antes de sobrescrever arquivos existentes
- ✅ Bloqueia comandos perigosos (rm, sudo, etc.)
- ✅ Mostra o que será executado antes de executar
- ✅ Permite cancelar operações

## 💰 Custos Estimados

### OpenAI GPT-4o-mini (Recomendado)
- **Input**: $0.15 por 1M tokens
- **Output**: $0.60 por 1M tokens
- **Projeto típico**: ~$0.01-0.05

### OpenAI GPT-3.5-turbo (Econômico)
- **Input**: $0.50 por 1M tokens
- **Output**: $1.50 por 1M tokens
- **Projeto típico**: ~$0.02-0.10

## 🎯 Exemplos de Uso

### Criar API Python com Flask

```bash
open-agent run "Crie uma API Python com Flask que seja um CRUD completo com dados mockados"
```

### Criar projeto React moderno

```bash
open-agent run "Crie um projeto React com TypeScript, Vite, Tailwind CSS e estrutura bem organizada"
```

### Melhorar código existente

```bash
open-agent analyze app.py "Refatore este código seguindo Clean Code e adicione validações"
```

## 📚 Documentação

- [Guia de Uso Detalhado](USAGE_GUIDE.md)
- [Guia de Migração para OpenAI](MIGRATION_TO_OPENAI.md)
- [Guia de Instalação](INSTALLATION_GUIDE.md)

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

## 🆘 Suporte

Se você encontrar algum problema ou tiver dúvidas:

1. Verifique a [documentação](USAGE_GUIDE.md)
2. Use `open-agent status` para verificar a configuração
3. Use `open-agent config --show` para ver as configurações atuais
4. Abra uma issue no GitHub

---

**Desenvolvido com ❤️ para facilitar o desenvolvimento de software** 