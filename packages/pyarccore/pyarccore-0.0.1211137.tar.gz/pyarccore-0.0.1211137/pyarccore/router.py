from fastapi import APIRouter, Request
from pathlib import Path
import importlib
import inspect
import sys
from typing import Dict, Any, Union
import logging
from .config_manager import ConfigManager

logger = logging.getLogger(__name__)

class ArcCmsRouter:
    @staticmethod
    def _get_route_params(module: Any) -> Dict[str, Any]:
        """Extrait les paramètres de la fonction handler"""
        handler = None
        if hasattr(module, 'get'):
            handler = module.get
        elif hasattr(module, 'default'):
            handler = module.default
        
        if not handler:
            return {}
        
        sig = inspect.signature(handler)
        return {
            name: param.default if param.default != inspect.Parameter.empty else ...
            for name, param in sig.parameters.items()
            if name not in ['request', 'self']
        }

    @staticmethod
    def _get_route_path(filepath: Path, base_path: Path) -> str:
        """Convertit le chemin du fichier en route"""
        try:
            relative_path = filepath.resolve().relative_to(base_path.resolve()).with_suffix('')
        except ValueError as e:
            logger.error(f"Path error: {e}")
            raise

        parts = []
        for part in relative_path.parts:
            if part == 'index':
                continue
            if part.startswith('_'):
                continue
            # Gestion spéciale pour les fichiers paramétrés
            if part.startswith('[') and part.endswith(']') and filepath.suffix == '.py':
                part = f"{{{part[1:-1]}}}"
            parts.append(part)
        
        return '/' + '/'.join(parts)

    @staticmethod
    def _get_base_url(config_data: dict) -> str:
        """Extrait le base-url de la configuration"""
        try:
            routing = config_data.get('routing', {})
            base_url = routing.get('base-url', '').strip()
            if base_url and not base_url.startswith('/'):
                base_url = f'/{base_url}'
            return base_url
        except Exception:
            return ''

    @classmethod
    def register_routes(cls, router: APIRouter, base_path: Union[Path, str]):
        """Enregistre toutes les routes"""
        if isinstance(base_path, str):
            base_path = Path(base_path)
        base_path = base_path.resolve()

        config = ConfigManager()
        modules_metadata = config.get_modules_metadata()
        
        # Base URL global
        global_config = config._configs.get('global', {})
        global_base_url = cls._get_base_url(global_config)

        # Ajout temporaire au PYTHONPATH
        parent_dir = str(base_path.parent)
        original_sys_path = sys.path.copy()
        if parent_dir not in sys.path:
            sys.path.insert(0, parent_dir)

        try:
            # Routes globales
            for filepath in base_path.glob('**/*.py'):
                if filepath.name.startswith(('_', '.')):
                    continue

                try:
                    route_path = cls._get_route_path(filepath, base_path)
                    full_path = f"{global_base_url}{route_path}" if global_base_url else route_path
                    cls._register_route(router, base_path, filepath, full_path)
                except Exception as e:
                    logger.error(f"Error loading route {filepath}: {e}")

            # Routes des modules (seulement ceux valides)
            modules_dir = base_path / 'modules'
            if modules_dir.exists():
                for module_name in modules_metadata.keys():
                    module_config = config._configs.get(module_name, {})
                    module_base_url = cls._get_base_url(module_config)
                    
                    module_path = modules_dir / module_name
                    for filepath in module_path.glob('**/*.py'):
                        if filepath.name.startswith(('_', '.')):
                            continue

                        try:
                            route_path = cls._get_route_path(filepath, base_path)
                            # Construction du chemin complet selon les règles spécifiées
                            full_path = cls._build_module_route_path(
                                global_base_url,
                                module_name,
                                module_base_url,
                                route_path
                            )
                            cls._register_route(router, base_path, filepath, full_path)
                        except Exception as e:
                            logger.error(f"Error loading route {filepath}: {e}")

        finally:
            sys.path = original_sys_path

    @classmethod
    def _build_module_route_path(
        cls,
        global_base_url: str,
        module_name: str,
        module_base_url: str,
        route_path: str
    ) -> str:
        """Construit le chemin complet selon les règles spécifiées"""
        parts = []
        
        # 1. Si base-url global existe, on l'ajoute
        if global_base_url:
            parts.append(global_base_url)
            
            # 2. Si base-url module existe, on l'ajoute (remplace le nom du module)
            if module_base_url:
                parts.append(module_base_url)
            else:
                # Sinon on ajoute le nom du module
                parts.append(f"/{module_name}")
        else:
            # Pas de base-url global, on utilise seulement le module si défini
            if module_base_url:
                parts.append(module_base_url)
        
        # 3. Ajouter le chemin de la route
        parts.append(route_path)
        
        # Joindre les parties et nettoyer les doubles slashes
        full_path = ''.join(parts).replace('//', '/')
        
        # S'assurer que le chemin commence par un slash
        if not full_path.startswith('/'):
            full_path = f'/{full_path}'
        
        return full_path

    @classmethod
    def _register_route(cls, router: APIRouter, base_path: Path, filepath: Path, route_path: str):
        """Enregistre une route individuelle"""
        module_path = '.'.join(filepath.relative_to(base_path.parent).with_suffix('').parts)

        module = importlib.import_module(module_path)
        
        # Enregistrement des méthodes HTTP
        for method in ['get', 'post', 'put', 'delete', 'patch']:
            if hasattr(module, method):
                handler = getattr(module, method)
                getattr(router, method)(
                    route_path,
                    **({'response_model': handler.__annotations__.get('return')} 
                    if hasattr(handler, '__annotations__') else {})
                )(handler)
        
        # Fallback pour default
        if hasattr(module, 'default') and not any(hasattr(module, m) for m in ['get', 'post', 'put', 'delete', 'patch']):
            handler = module.default
            router.get(route_path)(handler)

        logger.info(f"Route registered: {route_path} -> {module_path}")