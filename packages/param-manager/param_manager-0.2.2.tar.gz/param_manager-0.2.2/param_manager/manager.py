import threading
import logging
import os
import time
from datetime import datetime, timedelta
from typing import Any, Dict, Optional
import sys
import requests
from requests.exceptions import Timeout, ConnectionError
from tinydb import TinyDB
from dotenv import load_dotenv, find_dotenv
from Crypto.Hash import SHA256
from Crypto.Protocol.KDF import PBKDF2
import os
from Crypto.Cipher import AES

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger('ParamManager')


class ParamManager:
    """
    Gerenciador de parâmetros que implementa o padrão Singleton.

    Esta classe permite recuperar parâmetros de uma API, com sistema de cache
    e fallback para armazenamento local usando TinyDB quando a API está indisponível.
    """

    # Atributo de classe para armazenar a instância única (padrão Singleton)
    __instance = None

    def __new__(cls, *args, **kwargs):
        """
        Implementa o padrão Singleton, garantindo uma única instância da classe.
        """
        if cls.__instance is None:
            cls.__instance = super(ParamManager, cls).__new__(cls)
            logger.info('Nova instância do ParamManager criada')
        return cls.__instance

    def __init__(
        self,
        api_url: str | None = None,
        cache_duration: int = 3600,
        timeout: int = 5,
        local_db_path: str | None = None,
    ):
        """
        Inicializa a instância com configurações.
        """

        # Evita reinicialização se já foi inicializado
        if hasattr(self, '_initialized') and self._initialized:
            return

        # Carrega variáveis do .env
        load_dotenv()

        # Lê variáveis do ambiente, com fallback para os parâmetros passados
        self._api_base_url = api_url or os.getenv(
            'API_URL', 'http://djuv6cons85820:8084'
        )
        self._cache_duration = int(os.getenv('CACHE_DURATION', cache_duration))
        self._timeout = int(os.getenv('TIMEOUT', timeout))
        self._lock = threading.Lock()

    def __init__(
        self,
        api_url: str | None = None,
        cache_duration: int = 3600,
        timeout: int = 5,
        local_db_path: str | None = None,
    ):
        # Evita reinicialização
        if hasattr(self, '_initialized') and self._initialized:
            return

        # Procura e carrega .env do diretório correto
        # Detecta se está rodando como executável PyInstaller
        if getattr(sys, 'frozen', False):
            base_dir = (
                sys._MEIPASS
            )  # Diretório temporário onde PyInstaller extrai os arquivos
            dotenv_path = os.path.join(base_dir, '.env')
        else:
            base_dir = None
            dotenv_path = find_dotenv()

        load_dotenv(dotenv_path=dotenv_path)

        self._api_base_url = api_url or os.getenv(
            'API_URL', 'http://djuv6cons85820:8084'
        )
        self._cache_duration = int(os.getenv('CACHE_DURATION', cache_duration))
        self._timeout = int(os.getenv('TIMEOUT', timeout))
        self._lock = threading.Lock()

        env_db_path = os.getenv('LOCAL_DB_PATH')
        if local_db_path and os.path.exists(local_db_path):
            current_dir = local_db_path
        elif base_dir:
            current_dir = base_dir
        elif env_db_path and os.path.exists(env_db_path):
            current_dir = env_db_path
        else:
            current_dir = (
                os.path.dirname(dotenv_path)
                if dotenv_path
                else os.path.dirname(os.path.abspath(__file__))
            )

        db_dir = os.path.join(current_dir, '.param_manager')
        os.makedirs(db_dir, exist_ok=True)

        self._db_path = os.path.join(db_dir, 'params_db.json')
        self._db = TinyDB(self._db_path)

        self._cache = {}
        self._cache_timestamp = {}
        self._param_cache = {}
        self._param_cache_timestamp = {}
        self._api_error_timestamp = {}

        self._initialized = True
        logger.info(f'ParamManager inicializado com API: {self._api_base_url}')

    @staticmethod
    def get_instance(
        api_url: str = None, cache_duration: int = 3600, timeout: int = 5
    ) -> 'ParamManager':
        """
        Método estático para obter a instância única.

        Args:
            api_url: URL base da API de parâmetros.
            cache_duration: Duração do cache em segundos.
            timeout: Tempo limite para requisições à API em segundos.

        Returns:
            A instância única de ParamManager.
        """
        if ParamManager.__instance is None:
            ParamManager(api_url, cache_duration, timeout)
        return ParamManager.__instance

    def get_all_params(self, app_name: str) -> Dict[str, Any]:
        logger.info(f'Solicitando todos os parâmetros para o app: {app_name}')

        def _descriptografar_param(value: dict) -> str | None:
            try:
                if not all(
                    k in value for k in ['salt', 'master_key', 'crypto_data']
                ):
                    return None

                segredo_base = os.getenv('CHAVE_CUSTODIA_APP')
                if not segredo_base:
                    logger.error(
                        '🔐 CHAVE_CUSTODIA_APP não está definida no ambiente.'
                    )
                    return None

                salt = bytes.fromhex(value['salt'])
                chave_custodia = PBKDF2(
                    segredo_base.encode(),
                    salt,
                    dkLen=32,
                    count=100_000,
                    hmac_hash_module=SHA256,
                )

                cm_iv = bytes.fromhex(value['master_key']['iv'])
                cm_tag = bytes.fromhex(value['master_key']['tag'])
                cm_data = bytes.fromhex(value['master_key']['dado'])
                cipher_cm = AES.new(chave_custodia, AES.MODE_GCM, cm_iv)
                chave_mestra = cipher_cm.decrypt_and_verify(cm_data, cm_tag)

                pw_iv = bytes.fromhex(value['crypto_data']['iv'])
                pw_tag = bytes.fromhex(value['crypto_data']['tag'])
                pw_data = bytes.fromhex(value['crypto_data']['dado'])
                cipher_pw = AES.new(chave_mestra, AES.MODE_GCM, pw_iv)
                senha = cipher_pw.decrypt_and_verify(pw_data, pw_tag)

                return senha.decode()
            except Exception as e:
                logger.error(
                    f'Erro ao descriptografar parâmetro secreto: {str(e)}'
                )
                return None

        def _processar_parametros(params: dict) -> dict:
            for nome, p in params.items():
                if p.get('type') == 'secret':
                    raw = p.get('value')
                    if isinstance(raw, dict):
                        p['value'] = _descriptografar_param(raw)
            return params

        # Verifica cache
        if self._is_cache_valid(app_name):
            logger.info(f'Usando cache para o app: {app_name}')
            return _processar_parametros(self._cache[app_name])

        # Verifica erro de API anterior
        if self._is_api_error_cached(app_name):
            logger.warning(
                f'API para {app_name} está em cooldown. Usando dados locais ou cache.'
            )
            return _processar_parametros(self._get_from_local_db(app_name))

        try:
            params = self._fetch_from_api(app_name)
            return _processar_parametros(params)
        except (Timeout, ConnectionError) as e:
            logger.error(f'Erro de conexão/timeout: {str(e)}')
            self._api_error_timestamp[app_name] = time.time()
            return _processar_parametros(
                self._handle_api_error(app_name, None, e)
            )
        except Exception as e:
            logger.error(f'Erro inesperado ao buscar da API: {str(e)}')
            return _processar_parametros(
                self._handle_api_error(app_name, None, e)
            )

    def get_param(self, app_name: str, param_name: str) -> Any:
        """
        Recupera um parâmetro específico de um app.

        Args:
            app_name: Nome do aplicativo.
            param_name: Nome do parâmetro.

        Returns:
            Valor do parâmetro (descriptografado, se for tipo password), ou None.
        """

        logger.info(
            f'Solicitando parâmetro {param_name} para o app: {app_name}'
        )
        param_cache_key = f'{app_name}:{param_name}'

        def _descriptografar_password(value: dict) -> str | None:
            try:
                if not all(
                    k in value for k in ['salt', 'master_key', 'crypto_data']
                ):
                    return None

                segredo_base = os.getenv('CHAVE_CUSTODIA_APP')
                if not segredo_base:
                    logger.error(
                        '🔐 CHAVE_CUSTODIA_APP não está definida no ambiente.'
                    )
                    return None

                salt = bytes.fromhex(value['salt'])
                chave_custodia = PBKDF2(
                    segredo_base.encode(),
                    salt,
                    dkLen=32,
                    count=100_000,
                    hmac_hash_module=SHA256,
                )

                # Descriptografa chave mestra
                cm_iv = bytes.fromhex(value['master_key']['iv'])
                cm_tag = bytes.fromhex(value['master_key']['tag'])
                cm_data = bytes.fromhex(value['master_key']['dado'])
                cipher_cm = AES.new(chave_custodia, AES.MODE_GCM, cm_iv)
                chave_mestra = cipher_cm.decrypt_and_verify(cm_data, cm_tag)

                # Descriptografa senha
                pw_iv = bytes.fromhex(value['crypto_data']['iv'])
                pw_tag = bytes.fromhex(value['crypto_data']['tag'])
                pw_data = bytes.fromhex(value['crypto_data']['dado'])
                cipher_pw = AES.new(chave_mestra, AES.MODE_GCM, pw_iv)
                senha = cipher_pw.decrypt_and_verify(pw_data, pw_tag)

                return senha.decode()
            except Exception as e:
                logger.error(
                    f'Falha na descriptografia do parâmetro {param_name}: {str(e)}'
                )
                return None

        def _extract_value(param_value: dict) -> Any:
            raw = param_value.get('value')
            if isinstance(raw, dict):
                decrypted = _descriptografar_password(raw)
                return decrypted if decrypted is not None else raw
            return raw

        # Verifica cache específico
        if self._is_param_cache_valid(app_name, param_name):
            logger.info(
                f'Usando cache específico para o parâmetro: {param_name} do app: {app_name}'
            )
            return _extract_value(self._param_cache[param_cache_key])

        # Verifica cache global
        if self._is_cache_valid(app_name):
            logger.info(
                f'Usando cache global do app para o parâmetro: {param_name}'
            )
            params = self._cache[app_name]
            param_value = params.get(param_name)
            if param_value is not None:
                self._param_cache[param_cache_key] = param_value
                self._param_cache_timestamp[param_cache_key] = time.time()
                return _extract_value(param_value)

        # Verifica erro anterior
        if self._is_api_error_cached(app_name):
            logger.warning(
                f'API para {app_name} está em cooldown. Usando dados locais.'
            )
            params = self._get_from_local_db(app_name, param_name)
            return (
                _extract_value(params.get(param_name, dict()))
                if params
                else None
            )

        # Tenta buscar da API
        try:
            param_value = self._fetch_param_from_api(app_name, param_name)
            if not isinstance(param_value, dict):
                param_value = dict()
            return _extract_value(param_value)
        except (Timeout, ConnectionError) as e:
            logger.error(
                f'Erro de conexão/timeout ao buscar parâmetro da API: {str(e)}'
            )
            self._api_error_timestamp[app_name] = time.time()
            params = self._handle_api_error(app_name, param_name, e)
            return (
                _extract_value(params.get(param_name, dict()))
                if params
                else None
            )
        except Exception as e:
            logger.error(
                f'Erro inesperado ao buscar parâmetro da API: {str(e)}'
            )
            params = self._handle_api_error(app_name, param_name, e)
            return (
                _extract_value(params.get(param_name, dict()))
                if params
                else None
            )

    def _fetch_from_api(
        self, app_name: str, param_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Faz requisição à API para buscar todos os parâmetros de um app.

        Args:
            app_name: Nome do aplicativo.
            param_name: Nome do parâmetro específico (opcional, mantido para compatibilidade).

        Returns:
            Dicionário com os parâmetros.

        Raises:
            Exception: Se ocorrer erro na requisição.
        """
        # Constrói URL apropriada para todos os parâmetros
        url = f'{self._api_base_url}/parameters/apps/{app_name}/params/'

        logger.info(f'Buscando todos os parâmetros da API: {url}')

        # Faz requisição HTTP
        response = requests.get(url, timeout=self._timeout, verify=False)

        # Verifica se a requisição foi bem-sucedida
        if response.status_code != 200:
            raise Exception(f'API retornou status code {response.status_code}')

        # Processa resposta
        data = response.json()

        # Extrai parâmetros da resposta
        params = data.get('params', {})
        print(len(params))

        # Atualiza cache e timestamp
        self._cache[app_name] = params
        self._cache_timestamp[app_name] = time.time()

        # Salva dados localmente
        self._save_to_local_db(app_name, params)

        # Limpa o timestamp de erro da API se a requisição foi bem-sucedida
        if app_name in self._api_error_timestamp:
            del self._api_error_timestamp[app_name]

        return params

    def _fetch_param_from_api(self, app_name: str, param_name: str) -> Any:
        """
        Faz requisição à API para buscar um parâmetro específico.

        Args:
            app_name: Nome do aplicativo.
            param_name: Nome do parâmetro específico.

        Returns:
            Valor do parâmetro ou None se não encontrado.

        Raises:
            Exception: Se ocorrer erro na requisição.
        """
        # Constrói URL apropriada para o parâmetro específico
        url = f'{self._api_base_url}/parameters/apps/{app_name}/params/{param_name}'

        logger.info(f'Buscando parâmetro específico da API: {url}')

        # Faz requisição HTTP
        response = requests.get(url, timeout=self._timeout, verify=False)

        # Verifica se a requisição foi bem-sucedida
        if response.status_code != 200:
            raise Exception(f'API retornou status code {response.status_code}')

        # Processa resposta
        data = response.json()

        # Extrai parâmetro da resposta
        param_value = data.get('param')

        # Chave para o cache específico do parâmetro
        param_cache_key = f'{app_name}:{param_name}'

        # Atualiza o cache específico do parâmetro
        self._param_cache[param_cache_key] = param_value
        self._param_cache_timestamp[param_cache_key] = time.time()

        # Também atualiza o cache global se existir
        if app_name in self._cache:
            self._cache[app_name][param_name] = param_value
            self._cache_timestamp[app_name] = time.time()
        else:
            self._cache[app_name] = {param_name: param_value}

        # Salva dados localmente
        self._save_to_local_db(app_name, self._cache[app_name])

        # Limpa o timestamp de erro da API se a requisição foi bem-sucedida
        if app_name in self._api_error_timestamp:
            del self._api_error_timestamp[app_name]

        return param_value

    def _is_cache_valid(self, app_name: str) -> bool:
        """
        Verifica se o cache global para um app é válido.

        Args:
            app_name: Nome do aplicativo.

        Returns:
            True se o cache for válido, False caso contrário.
        """
        # Verifica se existe cache para o app
        if (
            app_name not in self._cache
            or app_name not in self._cache_timestamp
        ):
            return False

        # Verifica se o timestamp é recente (menos de cache_duration segundos)
        current_time = time.time()
        cache_time = self._cache_timestamp[app_name]

        return (current_time - cache_time) < self._cache_duration

    def _is_param_cache_valid(self, app_name: str, param_name: str) -> bool:
        """
        Verifica se o cache específico para um parâmetro é válido.

        Args:
            app_name: Nome do aplicativo.
            param_name: Nome do parâmetro.

        Returns:
            True se o cache for válido, False caso contrário.
        """
        # Chave para o cache específico do parâmetro
        param_cache_key = f'{app_name}:{param_name}'

        # Verifica se existe cache específico para o parâmetro
        if (
            param_cache_key not in self._param_cache
            or param_cache_key not in self._param_cache_timestamp
        ):
            return False

        # Verifica se o timestamp é recente (menos de cache_duration segundos)
        current_time = time.time()
        cache_time = self._param_cache_timestamp[param_cache_key]

        return (current_time - cache_time) < self._cache_duration

    def _is_api_error_cached(self, app_name: str) -> bool:
        """
        Verifica se houve um erro de API recente para o app e se o cooldown ainda está ativo.

        Args:
            app_name: Nome do aplicativo.

        Returns:
            True se o erro de API estiver em cooldown, False caso contrário.
        """
        if app_name not in self._api_error_timestamp:
            return False

        current_time = time.time()
        error_time = self._api_error_timestamp[app_name]

        # O erro é considerado "em cache" (cooldown) se o tempo desde o erro for menor que a duração do cache
        return (current_time - error_time) < self._cache_duration

    def _save_to_local_db(self, app_name: str, params: Dict[str, Any]) -> None:
        """
        Salva parâmetros no banco local.

        Args:
            app_name: Nome do aplicativo.
            params: Dicionário com os parâmetros.
        """
        # Define a tabela para o app

        logger.info(f'Salvando parâmetros localmente para o app: {app_name}')

        with self._lock:  # Aguarda a liberação do lock de outras threads
            table = self._db.table(app_name)

            # Limpa a tabela antes de inserir novos dados
            table.truncate()

            # Insere os parâmetros
            table.insert({'timestamp': time.time(), 'params': params})

    def _get_from_local_db(
        self, app_name: str, param_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Recupera dados do banco local.

        Args:
            app_name: Nome do aplicativo.
            param_name: Nome do parâmetro específico (opcional).

        Returns:
            Dicionário com os parâmetros ou vazio se não encontrado.
        """
        logger.info(f'Buscando parâmetros localmente para o app: {app_name}')

        # Define a tabela para o app
        table = self._db.table(app_name)

        # Busca o registro mais recente
        records = table.all()

        if not records:
            logger.warning(
                f'Nenhum registro local encontrado para o app: {app_name}'
            )
            return {}

        # Ordena por timestamp (mais recente primeiro)
        records.sort(key=lambda x: x.get('timestamp', 0), reverse=True)

        # Obtém os parâmetros do registro mais recente
        params = records[0].get('params', {})

        # Filtra por param_name se especificado
        if param_name:
            if param_name in params:
                return {param_name: params[param_name]}
            return {}

        return params

    def _handle_api_error(
        self, app_name: str, param_name: Optional[str], error: Exception
    ) -> Dict[str, Any]:
        """
        Trata erros de API.

        Args:
            app_name: Nome do aplicativo.
            param_name: Nome do parâmetro específico (opcional).
            error: Exceção ocorrida.

        Returns:
            Dados locais se disponíveis ou dicionário vazio.
        """
        logger.error(f'Erro ao acessar API para {app_name}: {str(error)}')
        logger.info(f'Tentando usar dados locais para {app_name}')

        # Busca dados locais
        return self._get_from_local_db(app_name, param_name)

    def clear_cache(
        self, app_name: Optional[str] = None, param_name: Optional[str] = None
    ) -> None:
        """
        Limpa o cache para um app específico, um parâmetro específico ou para todos os apps.

        Args:
            app_name: Nome do aplicativo (opcional).
            param_name: Nome do parâmetro (opcional).
        """
        if app_name and param_name:
            # Limpa o cache específico do parâmetro
            param_cache_key = f'{app_name}:{param_name}'
            if param_cache_key in self._param_cache:
                del self._param_cache[param_cache_key]
            if param_cache_key in self._param_cache_timestamp:
                del self._param_cache_timestamp[param_cache_key]
            logger.info(
                f'Cache limpo para o parâmetro {param_name} do app: {app_name}'
            )
        elif app_name:
            # Limpa o cache do app
            if app_name in self._cache:
                del self._cache[app_name]
            if app_name in self._cache_timestamp:
                del self._cache_timestamp[app_name]
            if app_name in self._api_error_timestamp:
                del self._api_error_timestamp[app_name]

            # Limpa também todos os caches específicos relacionados ao app
            param_cache_keys = [
                k
                for k in self._param_cache.keys()
                if k.startswith(f'{app_name}:')
            ]
            for key in param_cache_keys:
                if key in self._param_cache:
                    del self._param_cache[key]
                if key in self._param_cache_timestamp:
                    del self._param_cache_timestamp[key]

            logger.info(f'Cache limpo para o app: {app_name}')
        else:
            # Limpa todos os caches
            self._cache = {}
            self._cache_timestamp = {}
            self._param_cache = {}
            self._param_cache_timestamp = {}
            self._api_error_timestamp = {}
            logger.info('Cache limpo para todos os apps e parâmetros')

    def get_cache_info(self) -> Dict[str, Any]:
        """
        Retorna informações sobre o cache atual.

        Returns:
            Dicionário com informações do cache.
        """
        info = {
            'apps_cached': list(self._cache.keys()),
            'cache_timestamps': {},
            'cache_valid': {},
            'params_cached': [],
            'param_cache_timestamps': {},
            'param_cache_valid': {},
            'api_error_timestamps': {},
        }

        # Informações sobre o cache global
        for app_name, timestamp in self._cache_timestamp.items():
            dt = datetime.fromtimestamp(timestamp)
            expires_at = dt + timedelta(seconds=self._cache_duration)
            is_valid = self._is_cache_valid(app_name)

            info['cache_timestamps'][app_name] = {
                'cached_at': dt.isoformat(),
                'expires_at': expires_at.isoformat(),
                'seconds_remaining': int(
                    timestamp + self._cache_duration - time.time()
                )
                if is_valid
                else 0,
            }
            info['cache_valid'][app_name] = is_valid

        # Informações sobre o cache específico de parâmetros
        for param_key, timestamp in self._param_cache_timestamp.items():
            info['params_cached'].append(param_key)

            dt = datetime.fromtimestamp(timestamp)
            expires_at = dt + timedelta(seconds=self._cache_duration)

            # Extrai app_name e param_name da chave
            app_name, param_name = param_key.split(':', 1)
            is_valid = self._is_param_cache_valid(app_name, param_name)

            info['param_cache_timestamps'][param_key] = {
                'cached_at': dt.isoformat(),
                'expires_at': expires_at.isoformat(),
                'seconds_remaining': int(
                    timestamp + self._cache_duration - time.time()
                )
                if is_valid
                else 0,
            }
            info['param_cache_valid'][param_key] = is_valid

        # Informações sobre os timestamps de erro da API
        for app_name, timestamp in self._api_error_timestamp.items():
            dt = datetime.fromtimestamp(timestamp)
            cooldown_ends_at = dt + timedelta(seconds=self._cache_duration)
            is_cooldown_active = self._is_api_error_cached(app_name)

            info['api_error_timestamps'][app_name] = {
                'error_at': dt.isoformat(),
                'cooldown_ends_at': cooldown_ends_at.isoformat(),
                'cooldown_remaining_seconds': int(
                    cooldown_ends_at - datetime.fromtimestamp(time.time())
                ).total_seconds()
                if is_cooldown_active
                else 0,
            }

        return info
