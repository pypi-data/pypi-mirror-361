"""
Provedores de IA para o Open Agent CLI
"""
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
import openai
import google.generativeai as genai
from rich.console import Console


class AIProvider(ABC):
    """Classe abstrata para provedores de IA"""
    
    def __init__(self, api_key: str, model: str, temperature: float = 0.1):
        self.api_key = api_key
        self.model = model
        self.temperature = temperature
        self.console = Console()
    
    @abstractmethod
    def generate_content(self, prompt: str) -> str:
        """Gera conteúdo usando o provedor de IA"""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Verifica se o provedor está disponível"""
        pass


class OpenAIProvider(AIProvider):
    """Provedor OpenAI"""
    
    def __init__(self, api_key: str, model: str = "gpt-4o-mini", temperature: float = 0.1):
        super().__init__(api_key, model, temperature)
        self.client = openai.OpenAI(api_key=api_key)
    
    def generate_content(self, prompt: str) -> str:
        """Gera conteúdo usando OpenAI"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Você é um assistente especializado em desenvolvimento de software e Clean Code."},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.temperature,
                max_tokens=4000
            )
            return response.choices[0].message.content or ""
        except Exception as e:
            self.console.print(f"[red]❌ Erro ao gerar conteúdo com OpenAI: {e}[/red]")
            return ""
    
    def is_available(self) -> bool:
        """Verifica se a OpenAI está disponível"""
        try:
            # Testa com uma requisição simples
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": "test"}],
                max_tokens=5
            )
            return True
        except Exception:
            return False


class GoogleProvider(AIProvider):
    """Provedor Google (Gemini)"""
    
    def __init__(self, api_key: str, model: str = "gemini-1.5-flash", temperature: float = 0.1):
        super().__init__(api_key, model, temperature)
        # Some linters may not recognize these attributes, but they are valid in google-generativeai >=0.3.0
        getattr(genai, "configure")(api_key=api_key)
        self.model = getattr(genai, "GenerativeModel")(model)
    
    def generate_content(self, prompt: str) -> str:
        """Gera conteúdo usando Google Gemini"""
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            self.console.print(f"[red]❌ Erro ao gerar conteúdo com Google: {e}[/red]")
            return ""
    
    def is_available(self) -> bool:
        """Verifica se o Google Gemini está disponível"""
        try:
            # Testa com uma requisição simples
            response = self.model.generate_content("test")
            return True
        except Exception:
            return False


class AIProviderFactory:
    """Factory para criar provedores de IA"""
    
    @staticmethod
    def create_provider(provider: str, api_key: str, model: str, temperature: float = 0.1) -> AIProvider:
        """Cria um provedor de IA baseado no tipo"""
        
        if provider.lower() == "openai":
            return OpenAIProvider(api_key, model, temperature)
        elif provider.lower() == "google":
            return GoogleProvider(api_key, model, temperature)
        else:
            raise ValueError(f"Provedor não suportado: {provider}")
    
    @staticmethod
    def get_available_models(provider: str) -> Dict[str, str]:
        """Retorna os modelos disponíveis para cada provedor"""
        
        if provider.lower() == "openai":
            return {
                "gpt-4o-mini": "GPT-4o Mini - Rápido e econômico para código",
                "gpt-4o": "GPT-4o - Mais avançado, mas mais caro",
                "gpt-3.5-turbo": "GPT-3.5 Turbo - Econômico e rápido",
                "gpt-4-turbo": "GPT-4 Turbo - Alta qualidade"
            }
        elif provider.lower() == "google":
            return {
                "gemini-1.5-flash": "Gemini 1.5 Flash - Rápido e econômico",
                "gemini-1.5-pro": "Gemini 1.5 Pro - Mais avançado",
                "gemini-pro": "Gemini Pro - Versão estável"
            }
        else:
            return {} 