import importlib
import inspect
from pathlib import Path
from typing import Any, Callable, Dict, Optional, Union, List
import logging
import asyncio
import threading
from .config_manager import ConfigManager

logger = logging.getLogger(__name__)

class FeatureManager:
    _instance = None
    _lock = threading.Lock()
    _features_cache: Dict[str, Dict[str, Callable]] = {
        'global': {},
        'modules': {}
    }

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._init()
        return cls._instance

    def _init(self):
        self._project_root = None
        self._config = ConfigManager()

    def set_project_root(self, path: Union[str, Path]):
        """Définit la racine du projet"""
        self._project_root = Path(path).resolve()

    async def execute(
        self,
        feature_path: str,
        module: Optional[str] = None,
        *args,
        **kwargs
    ) -> Any:
        """Exécute une fonctionnalité"""
        try:
            feature = self._get_feature(feature_path, module)
            
            if asyncio.iscoroutinefunction(feature):
                return await feature(*args, **kwargs)
            return feature(*args, **kwargs)
            
        except ImportError as e:
            logger.error(f"Feature import error: {e}")
            raise FeatureNotFound(f"Feature '{feature_path}' not found") from e
        except Exception as e:
            logger.error(f"Feature execution error: {e}")
            raise FeatureError(f"Error executing feature '{feature_path}': {str(e)}") from e

    async def execute_many(
        self,
        features: List[Dict[str, Any]],
        fail_fast: bool = False
    ) -> Dict[str, Any]:
        """Exécute plusieurs fonctionnalités en parallèle"""
        tasks = []
        feature_refs = []  # Pour garder la correspondance
        
        for feature_spec in features:
            try:
                feature = self._get_feature(
                    feature_spec['feature_path'],
                    feature_spec.get('module')
                )
                
                args = feature_spec.get('args', [])
                kwargs = feature_spec.get('kwargs', {})
                
                if asyncio.iscoroutinefunction(feature):
                    task = feature(*args, **kwargs)
                else:
                    # Convertit les fonctions sync en coroutines
                    task = asyncio.get_event_loop().run_in_executor(
                        None, 
                        lambda: feature(*args, **kwargs)
                    )
                
                tasks.append(task)
                feature_refs.append(feature_spec['feature_path'])
                
            except Exception as e:
                if fail_fast:
                    raise FeatureError(f"Failed to prepare feature {feature_spec['feature_path']}: {str(e)}") from e
                logger.error(f"Feature preparation error: {e}")
                continue
        
        results = {}
        errors = {}
        
        # Exécute toutes les tâches en parallèle
        completed = await asyncio.gather(*tasks, return_exceptions=True)
        
        for feature_path, result in zip(feature_refs, completed):
            if isinstance(result, Exception):
                errors[feature_path] = str(result)
                logger.error(f"Feature {feature_path} failed: {result}")
            else:
                results[feature_path] = result
        
        return {
            'results': results,
            'errors': errors
        }

    async def execute_many_sync(
        self,
        features: List[Dict[str, Any]],
        fail_fast: bool = False
    ) -> Dict[str, Any]:
        """Version synchrone de execute_many"""
        results = {}
        errors = {}
        
        for feature_spec in features:
            try:
                result = await self.execute(
                    feature_spec['feature_path'],
                    feature_spec.get('module'),
                    *feature_spec.get('args', []),
                    **feature_spec.get('kwargs', {})
                )
                results[feature_spec['feature_path']] = result
            except Exception as e:
                if fail_fast:
                    raise
                errors[feature_spec['feature_path']] = str(e)
                logger.error(f"Feature {feature_spec['feature_path']} failed: {e}")
        
        return {
            'results': results,
            'errors': errors
        }

    def _get_feature(self, feature_path: str, module: Optional[str] = None) -> Callable:
        """Récupère une fonctionnalité depuis le cache ou la charge"""
        # Vérifie que le module est valide
        if module and module not in self._config.get_modules_metadata():
            raise FeatureNotFound(f"Module {module} is not valid or not loaded")
            
        context = 'global' if module is None else f'modules.{module}'
        cache_key = f"{context}.{feature_path}"
        
        # Vérifie le cache
        cached_feature = self._features_cache['global' if module is None else 'modules'].get(cache_key)
        if cached_feature:
            return cached_feature
        
        # Charge la fonctionnalité
        feature = self._load_feature(feature_path, module)
        
        # Met en cache
        if module:
            self._features_cache['modules'][cache_key] = feature
        else:
            self._features_cache['global'][cache_key] = feature
            
        return feature

    def _load_feature(self, feature_path: str, module: Optional[str]) -> Callable:
        """Charge dynamiquement une fonctionnalité"""
        parts = feature_path.split('.')
        if len(parts) < 2:
            raise FeatureNotFound(f"Invalid feature path format: {feature_path}")
        
        # Construction du chemin d'import
        if module:
            # Fonctionnalité de module: "auth.createData"
            filename, *func_parts = parts
            import_path = f"modules.{module}.features.{filename}"
            feature_file = self._project_root / "modules" / module / "features" / f"{filename}.py"
        else:
            # Fonctionnalité globale: "utils.helpers.cleanData"
            *path_parts, filename = parts[:-1]
            func_name = parts[-1]
            import_path = "features." + ".".join(path_parts + [filename]) if path_parts else f"features.{filename}"
            feature_file = self._project_root / "features" / "/".join(path_parts) / f"{filename}.py"
        
        # Vérifie l'existence du fichier
        if not feature_file.exists():
            raise FeatureNotFound(f"Feature file not found: {feature_file}")
        
        # Import dynamique
        try:
            feature_module = importlib.import_module(import_path)
            func_name = parts[-1]
            
            if not hasattr(feature_module, func_name):
                raise FeatureNotFound(f"Function '{func_name}' not found in {import_path}")
                
            return getattr(feature_module, func_name)
            
        except ImportError as e:
            logger.error(f"Failed to import feature module {import_path}: {e}")
            raise FeatureNotFound(f"Could not load feature '{feature_path}'") from e

    def list_all_features(self) -> Dict[str, Dict[str, List[str]]]:
        """Liste toutes les fonctionnalités disponibles"""
        features = {'global': {}, 'modules': {}}
        
        # Fonctionnalités globales
        global_features_dir = self._project_root / "features"
        if global_features_dir.exists():
            features['global'] = self._scan_features_dir(global_features_dir, "features")
        
        # Fonctionnalités des modules (seulement ceux valides)
        modules_metadata = self._config.get_modules_metadata()
        modules_dir = self._project_root / "modules"
        if modules_dir.exists():
            for module_name in modules_metadata.keys():
                features_dir = modules_dir / module_name / "features"
                if features_dir.exists():
                    features['modules'][module_name] = self._scan_features_dir(
                        features_dir, 
                        f"modules.{module_name}.features"
                    )
        
        return features

    def list_features(self, module: str = None) -> Dict[str, list]:
        """Liste toutes les fonctionnalités disponibles d'un module"""
        if module is None:
            res = {}
            global_features_dir = self._project_root / "features"
            if global_features_dir.exists():
                res = self._scan_features_dir(global_features_dir, "features")
            return res

        # Vérifie que le module est valide
        if module not in self._config.get_modules_metadata():
            return {}
            
        features_dir = self._project_root / "modules" / module / "features"
        if not features_dir.exists():
            return {}
            
        features = {}
        for feature_file in features_dir.glob('*.py'):
            if feature_file.name.startswith('_'):
                continue
                
            module_name = feature_file.stem
            module_path = f"modules.{module}.features.{module_name}"
            
            try:
                feature_module = importlib.import_module(module_path)
                module_features = [
                    name for name, obj in inspect.getmembers(feature_module)
                    if inspect.isfunction(obj) or inspect.iscoroutinefunction(obj)
                ]
                features[module_name] = module_features
            except ImportError:
                continue
                
        return features

    def _scan_features_dir(self, directory: Path, base_import: str) -> Dict[str, List[str]]:
        """Scan un répertoire de fonctionnalités"""
        features = {}
        
        for feature_file in directory.glob('**/*.py'):
            if feature_file.name.startswith('_'):
                continue
                
            # Construit le chemin d'import
            rel_path = feature_file.relative_to(directory).with_suffix('')
            module_path = f"{base_import}.{'.'.join(rel_path.parts)}"
            
            try:
                feature_module = importlib.import_module(module_path)
                module_features = [
                    name for name, obj in inspect.getmembers(feature_module)
                    if inspect.isfunction(obj) or inspect.iscoroutinefunction(obj)
                ]
                
                if module_features:
                    features[module_path[len(base_import)+1:]] = module_features
            except ImportError:
                continue
                
        return features

class FeatureNotFound(Exception):
    """Exception levée quand une fonctionnalité n'est pas trouvée"""
    pass

class FeatureError(Exception):
    """Exception levée quand une erreur survient lors de l'exécution"""
    pass