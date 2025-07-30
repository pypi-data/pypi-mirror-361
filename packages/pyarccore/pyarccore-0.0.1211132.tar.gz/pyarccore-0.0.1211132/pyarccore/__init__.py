from typing import Any, Union, Dict, List, Optional
from fastapi import FastAPI, APIRouter, Request
from fastapi.responses import HTMLResponse
from pathlib import Path
from .internationalisation_manager import InternationalisationManager
from .config_manager import ConfigManager
from .router import ArcCmsRouter
from .page_manager import PageManager
from .feature_manager import FeatureManager
from .request_utils import RequestData, extract_all_request_data, get_specific_data
import logging
import asyncio

logger = logging.getLogger(__name__)

_intl = InternationalisationManager()
_config = ConfigManager()
_router = ArcCmsRouter()
_feature = FeatureManager()
_page = PageManager()

def init_app(app_root: Union[Path, str] = None):
    """Initialise toutes les ressources"""
    if app_root is None:
        app_root = Path(__file__).parent.parent
    if isinstance(app_root, str):
        app_root = Path(app_root)
    
    _intl.set_project_root(app_root.resolve())
    _config.set_project_root(app_root.resolve())
    _feature.set_project_root(app_root)
    _page.set_project_root(app_root.resolve())
    _intl.load_all()
    _config.load_all()
    
def execute_feature(
    feature_path: str,
    module: Optional[str] = None,
    *args,
    **kwargs
) -> Any:
    """Exécute une fonctionnalité"""
    return _feature.execute(feature_path, module, *args, **kwargs)

async def execute_features(
    features: List[Dict[str, Any]],
    fail_fast: bool = False
) -> Dict[str, Any]:
    """Exécute plusieurs fonctionnalités en parallèle"""
    return await _feature.execute_many(features, fail_fast)

def execute_features_sync(
    features: List[Dict[str, Any]],
    fail_fast: bool = False
) -> Dict[str, Any]:
    """Version synchrone de execute_features"""
    return asyncio.run(_feature.execute_many_sync(features, fail_fast))

def list_features(module: str = None) -> Dict[str, list]:
    """Liste toutes les fonctionnalités disponibles d'un module"""
    return _feature.list_features(module)

def list_all_features() -> Dict[str, Dict[str, List[str]]]:
    """Liste toutes les fonctionnalités disponibles"""
    return _feature.list_all_features()

def t(key: str, locale: str = 'fr', module: str = "global", **kwargs) -> str:
    """Récupère une traduction"""
    value = _intl.get(module, key, locale) or key
    return value.format(**kwargs) if kwargs else value

def cfg(key: str, default: Any = None, module: str = "global") -> Any:
    """Récupère une configuration"""
    return _config.get(module, key, default)

def register_routes(router: APIRouter, base_path: Union[Path, str]):
    """Enregistre les routes"""
    if isinstance(base_path, str):
        base_path = Path(base_path)
    _router.register_routes(router, base_path.resolve())

def get_module_id_map() -> Dict[str, str]:
    """Retourne un mapping des IDs vers les noms de dossiers"""
    return _config.get_module_id_map()

async def all_requests(request: Request) -> RequestData:
    return await extract_all_request_data(request = request)

def specific_request(
    request_data: RequestData,
    data_type: str,
    key: Optional[str] = None,
    default: Any = None
) -> Any:
    return get_specific_data(
        request_data = request_data,
        data_type = data_type,
        key = key,
        default = default,
    )

def get_project_root() -> Path:
    """Retourne la racine du projet"""
    return _config.get_project_root()

def get_modules_metadata() -> Dict[str, Dict]:
    """Retourne les métadonnées de tous les modules"""
    return _config.get_modules_metadata()

def get_files_from_directory(
    directory_name: str, 
    module: str = None, 
    file_filter: str = None
) -> Dict[str, List[Path]]:
    """
    Récupère les fichiers d'un répertoire spécifique
    
    Args:
        directory_name: Nom du répertoire ('public', 'pages', etc.)
        module: Nom du module (None pour global)
        file_filter: Regex pour filtrer les fichiers
    """
    return _config.get_files_from_directory(directory_name, module, file_filter)
def get_all_files_from_directory(
    directory_name: str,
    file_filter: str = None,
    include_global: bool = True
) -> Dict[str, List[Path]]:
    """
    Récupère les fichiers d'un répertoire spécifique dans tous les modules
    
    Args:
        directory_name: Nom du répertoire ('public', 'pages', etc.)
        file_filter: Regex pour filtrer les fichiers
        include_global: Inclure les fichiers globaux si True
        
    Returns:
        Dictionnaire avec:
            - clé: nom du module ou 'global'
            - valeur: liste des fichiers trouvés
    """
    return _config.get_all_files_from_directory(
        directory_name=directory_name,
        file_filter=file_filter,
        include_global=include_global,
    )

def get_config_params(
    param_path: str, 
    module: str = None, 
    key_filter: str = None
) -> Dict[str, Any]:
    """
    Récupère des paramètres spécifiques de configuration
    
    Args:
        param_path: Chemin du paramètre ('metadatas.authors')
        module: Nom du module (None pour global)
        key_filter: Regex pour filtrer les clés
    """
    return _config.get_config_params(param_path, module, key_filter)
def get_all_config_params(
    param_path: str,
    key_filter: str = None,
    include_global: bool = True
) -> Dict[str, Dict[str, Any]]:
    """
    Récupère des paramètres spécifiques de configuration pour tous les modules
    
    Args:
        param_path: Chemin du paramètre ('metadatas.authors')
        key_filter: Regex pour filtrer les clés
        include_global: Inclure la configuration globale si True
        
    Returns:
        Dictionnaire avec:
            - clé: nom du module ou 'global'
            - valeur: paramètres trouvés pour ce module
    """
    return _config.get_all_config_params(
        param_path=param_path,
        key_filter=key_filter,
        include_global=include_global,
    )

def get_page(page_path: str, context: str = 'global', **kwargs) -> str:
    """Récupère une page rendue"""
    return _page.get_page(page_path, context, **kwargs)

def list_pages(context: str = None, pattern: str = None) -> Dict[str, List[str]]:
    """Liste toutes les pages disponibles"""
    return _page.list_pages(context, pattern)

def get_layout(layout_name: str, context: str = 'global') -> str:
    """Récupère un layout"""
    return _page.get_layout(layout_name, context)

def list_layouts(context: str = None) -> Dict[str, List[str]]:
    """Liste tous les layouts disponibles"""
    return _page.list_layouts(context)

def mount_static_files(app):
    """Monte les fichiers statiques sur l'application FastAPI"""
    _page.mount_static_files(app)

def render_template(request: Request, template_name: str, context: str = 'global', **kwargs) -> HTMLResponse:
    """
    Rend un template avec le contexte de la requête
    
    Args:
        request: Objet Request de FastAPI
        template_name: Nom du template ('index.html', 'auth/login.html')
        context: 'global' ou nom du module
        **kwargs: Variables supplémentaires pour le template
        
    Returns:
        HTMLResponse
    """
    return _page.render_template(request, template_name, context, **kwargs)

def get_static_url(context: str = 'global') -> str:
    """
    Retourne l'URL de base pour les assets statiques
    
    Args:
        context: 'global' ou nom du module
        
    Returns:
        URL de base pour les assets
    """
    return _page.get_static_url(context)

def list_templates(context: str = None) -> Dict[str, List[str]]:
    """
    Liste tous les templates disponibles
    
    Args:
        context: 'global', nom de module ou None pour tous
        
    Returns:
        Dictionnaire des templates disponibles
    """
    return _page.list_templates(context)