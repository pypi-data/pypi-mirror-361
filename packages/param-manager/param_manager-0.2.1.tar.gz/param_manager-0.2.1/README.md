# Biblioteca ParamManager

## Descrição
Biblioteca Python orientada a objetos que implementa o padrão Singleton para interagir com a API de parâmetros. A biblioteca oferece funcionalidades de cache, armazenamento local com TinyDB e fallback automático em caso de indisponibilidade da API.

## Funcionalidades

- **Padrão Singleton**: Garante que exista apenas uma instância da classe de acesso à API
- **Cache**: Armazena resultados em memória por até 1 hora para reduzir chamadas à API
- **Armazenamento Local**: Usa TinyDB para persistir dados localmente
- **Fallback Automático**: Utiliza dados locais quando a API está indisponível
- **Recuperação de Parâmetros**: Permite buscar todos os parâmetros de um app ou um parâmetro específico

## Instalação

```bash
pip install param-manager
```

## Uso Básico

```python
from param_manager import ParamManager

# Obter a instância do gerenciador
param_manager = ParamManager.get_instance()

# Recuperar todos os parâmetros de um app
params = param_manager.get_all_params('nome_do_app')

# Recuperar um parâmetro específico
param = param_manager.get_param('nome_do_app', 'NOME_PARAMETRO')

# Limpar o cache para um app específico
param_manager.clear_cache('nome_do_app')

# Obter informações sobre o cache atual
cache_info = param_manager.get_cache_info()
```

## Configuração Avançada

```python
# Configurar com URL de API personalizada, duração de cache e timeout
param_manager = ParamManager.get_instance(
    api_url="http://minha-api.exemplo.com",
    cache_duration=1800,  # 30 minutos
    timeout=10  # 10 segundos
)
```

## Comportamento de Fallback

Quando a API está indisponível, a biblioteca automaticamente:
1. Tenta acessar a API
2. Em caso de falha, busca dados do armazenamento local
3. Retorna os dados mais recentes disponíveis localmente

## Estrutura de Arquivos

- `param_manager.py`: Implementação principal da biblioteca
- `test_param_manager.py`: Testes unitários para validar o funcionamento
- `README.md`: Documentação da biblioteca
- `requirements.txt`: Dependências necessárias

## Dependências

- Python 3.6+
- requests
- tinydb
