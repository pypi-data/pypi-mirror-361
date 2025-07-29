"""
Configuração e gerenciamento de configurações locais
"""
import json
import os
from pathlib import Path
from typing import Optional
from pydantic import BaseModel, Field


class Config(BaseModel):
    """Modelo de configuração do Open Agent CLI"""
    api_key: Optional[str] = Field(None, description="Chave da API (OpenAI ou Google)")
    provider: str = Field("openai", description="Provedor da API (openai ou google)")
    model: str = Field("gpt-4o-mini", description="Modelo a ser usado")
    max_tokens: int = Field(4096, description="Número máximo de tokens")
    temperature: float = Field(0.1, description="Temperatura para geração de código (baixa para código mais consistente)")


class ConfigManager:
    """Gerenciador de configurações do Open Agent CLI"""
    
    def __init__(self):
        self.config_dir = Path.home() / ".openagent"
        self.config_file = self.config_dir / "config.json"
        self._config: Optional[Config] = None
    
    def ensure_config_dir(self) -> None:
        """Garante que o diretório de configuração existe"""
        self.config_dir.mkdir(exist_ok=True)
    
    def load_config(self) -> Config:
        """Carrega a configuração do arquivo"""
        if self._config is not None:
            return self._config
        
        self.ensure_config_dir()
        
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self._config = Config(**data)
            except (json.JSONDecodeError, KeyError):
                self._config = Config(
                    api_key=None,
                    provider="openai",
                    model="gpt-4o-mini",
                    max_tokens=4096,
                    temperature=0.1
                )
        else:
            self._config = Config(
                api_key=None,
                provider="openai",
                model="gpt-4o-mini",
                max_tokens=4096,
                temperature=0.1
            )
        
        return self._config
    
    def save_config(self, config: Config) -> None:
        """Salva a configuração no arquivo"""
        self.ensure_config_dir()
        
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(config.model_dump(), f, indent=2, ensure_ascii=False)
        
        self._config = config
    
    def update_api_key(self, api_key: str) -> None:
        """Atualiza a chave da API"""
        config = self.load_config()
        config.api_key = api_key
        self.save_config(config)
    
    def update_provider(self, provider: str) -> None:
        """Atualiza o provedor da API"""
        config = self.load_config()
        config.provider = provider
        self.save_config(config)
    
    def update_model(self, model: str) -> None:
        """Atualiza o modelo"""
        config = self.load_config()
        config.model = model
        self.save_config(config)
    
    def update_temperature(self, temperature: float) -> None:
        """Atualiza a temperatura"""
        config = self.load_config()
        config.temperature = temperature
        self.save_config(config)
    
    def update_max_tokens(self, max_tokens: int) -> None:
        """Atualiza o número máximo de tokens"""
        config = self.load_config()
        config.max_tokens = max_tokens
        self.save_config(config)
    
    def get_api_key(self) -> Optional[str]:
        """Retorna a chave da API"""
        config = self.load_config()
        return config.api_key
    
    def get_provider(self) -> str:
        """Retorna o provedor da API"""
        config = self.load_config()
        return config.provider
    
    def get_model(self) -> str:
        """Retorna o modelo"""
        config = self.load_config()
        return config.model
    
    def is_configured(self) -> bool:
        """Verifica se o agente está configurado"""
        return self.get_api_key() is not None
    
    def get_model_config(self) -> Config:
        """Retorna a configuração completa do modelo"""
        return self.load_config() 