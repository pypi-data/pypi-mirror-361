import xml.etree.ElementTree as ET
from pathlib import Path
import threading
import hashlib
from functools import lru_cache
from typing import Dict, Any, Optional, List
import logging
from .versionning import check_version
import importlib
import subprocess
import sys
import re

logger = logging.getLogger(__name__)

class ConfigManager:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._init()
        return cls._instance

    def _init(self):
        self._configs = {}
        self._lock = threading.RLock()
        self._project_root = None
        self._file_hashes = {}
        self._modules_metadata = {}

    def set_project_root(self, path: Path):
        """Définit la racine du projet"""
        with self._lock:
            self._project_root = path.resolve()

    def load_all(self):
        """Charge toutes les configurations"""
        if self._project_root is None:
            logger.error("Project root not set, call set_project_root() first")
            return

        # Global
        global_config = self._project_root / 'config.xml'
        if global_config.exists():
            self._load_config('global', global_config)

        # Modules
        modules_dir = self._project_root / 'modules'
        if modules_dir.exists():
            for module_path in modules_dir.iterdir():
                if module_path.is_dir():
                    config_file = module_path / 'config.xml'
                    if config_file.exists():
                        if self._validate_module_structure(config_file):
                            self._load_config(module_path.name, config_file)
                            self._load_module_metadata(module_path.name, config_file)
                            self._check_module_requirements(module_path.name)
                            self._install_module_plugins(module_path.name)
                        else:
                            logger.warning(f"Module {module_path.name} has invalid structure and will be ignored")

        # Install global plugins after modules are loaded
        self._install_global_plugins()

    def _validate_module_structure(self, config_file: Path) -> bool:
        """Valide la structure minimale du module"""
        try:
            tree = ET.parse(config_file)
            root = tree.getroot()
            
            # Vérification des métadonnées minimales
            metadatas = root.find('metadatas')
            if metadatas is None:
                return False
                
            required_fields = ['id', 'name', 'version']
            for field in required_fields:
                if metadatas.find(field) is None:
                    return False
                    
            return True
        except ET.ParseError:
            return False

    def _load_module_metadata(self, module_name: str, config_file: Path):
        """Charge les métadonnées du module"""
        try:
            tree = ET.parse(config_file)
            root = tree.getroot()
            metadatas = root.find('metadatas')
            
            if metadatas is None:
                return
                
            metadata = {
                'id': metadatas.findtext('id', '').strip(),
                'name': metadatas.findtext('name', '').strip(),
                'description': metadatas.findtext('description', '').strip(),
                'version': metadatas.findtext('version', '').strip(),
                'authors': [],
                'requirements': [],
                'plugins': []
            }
            
            # Auteurs
            authors = metadatas.find('authors')
            if authors is not None:
                for author in authors.findall('author'):
                    metadata['authors'].append({
                        'name': author.findtext('name', '').strip(),
                        'email': author.findtext('email', '').strip(),
                        'position': author.findtext('position', '').strip(),
                        'company': author.findtext('company', '').strip()
                    })
            
            # Requirements
            requirements = metadatas.find('requirements')
            if requirements is not None:
                for req in requirements.findall('requirement'):
                    metadata['requirements'].append({
                        'id': req.findtext('id', '').strip(),
                        'version': req.findtext('version', '').strip()
                    })
            
            # Plugins
            plugins = metadatas.find('plugins')
            if plugins is not None:
                for plugin in plugins.findall('plugin'):
                    metadata['plugins'].append({
                        'id': plugin.findtext('id', '').strip(),
                        'version': plugin.findtext('version', '').strip()
                    })
            
            self._modules_metadata[module_name] = metadata
            
        except Exception as e:
            logger.error(f"Failed to load metadata for module {module_name}: {e}")

    def _check_module_requirements(self, module_name: str):
        """Vérifie les dépendances entre modules"""
        if module_name not in self._modules_metadata:
            return
            
        requirements = self._modules_metadata[module_name].get('requirements', [])
        loaded_module_ids = {meta['id']: name for name, meta in self._modules_metadata.items()}
        
        for req in requirements:
            req_id = req['id']
            req_version = req.get('version', '')
            
            # Vérifie d'abord dans les modules chargés
            if req_id in loaded_module_ids:
                mod_meta = self._modules_metadata[loaded_module_ids[req_id]]
                if req_version and not check_version(mod_meta['version'], req_version):
                    logger.error(
                        f"Module {module_name} requires {req_id} version {req_version} "
                        f"but found {mod_meta['version']}"
                    )
                continue
                
            # Vérifie dans les fichiers de modules non encore chargés
            modules_dir = self._project_root / 'modules'
            if modules_dir.exists():
                for mod_dir in modules_dir.iterdir():
                    if mod_dir.is_dir():
                        config_file = mod_dir / 'config.xml'
                        if config_file.exists():
                            try:
                                tree = ET.parse(config_file)
                                root = tree.getroot()
                                if root.find('metadatas/id') is not None:
                                    mod_id = root.findtext('metadatas/id').strip()
                                    if mod_id == req_id:
                                        # Charge le module manquant
                                        self._load_config(mod_dir.name, config_file)
                                        self._load_module_metadata(mod_dir.name, config_file)
                                        loaded_module_ids[req_id] = mod_dir.name
                                        break
                            except ET.ParseError:
                                continue
            
            # Si toujours pas trouvé
            if req_id not in loaded_module_ids:
                logger.error(f"Required module {req_id} not found for {module_name}")
                # Option 1: Lever une exception (comportement actuel)
                # raise ValueError(f"Required module {req_id} not found for {module_name}")
                
                # Option 2: Continuer avec un warning (plus permissif)
                logger.warning(f"Module {module_name} will load without required module {req_id}")

    def get_module_id_map(self) -> Dict[str, str]:
        """Retourne un mapping des IDs vers les noms de dossiers"""
        with self._lock:
            return {
                meta['id']: name 
                for name, meta in self._modules_metadata.items()
                if 'id' in meta
            }

    def _install_global_plugins(self):
        """Installe les plugins globaux"""
        if 'global' not in self._configs or '_hash' not in self._configs['global']:
            return
            
        plugins = self._configs['global'].get('metadatas', {}).get('plugins', [])
        if not plugins:
            return
            
        for plugin in plugins:
            self._install_plugin(plugin)

    def _install_module_plugins(self, module_name: str):
        """Installe les plugins d'un module"""
        if module_name not in self._modules_metadata:
            return
            
        plugins = self._modules_metadata[module_name].get('plugins', [])
        for plugin in plugins:
            self._install_plugin(plugin)

    def _install_plugin(self, plugin: Dict[str, str]):
        """Installe un plugin Python"""
        plugin_id = plugin.get('id', '')
        if not plugin_id:
            return
            
        version_spec = plugin.get('version', '')
        
        try:
            # Vérifie si le plugin est déjà installé
            installed_version = importlib.metadata.version(plugin_id)
            
            if version_spec and not check_version(installed_version, version_spec):
                raise ValueError(
                    f"Plugin {plugin_id} version {installed_version} "
                    f"does not match requirement {version_spec}"
                )
                
            logger.info(f"Plugin {plugin_id} (version {installed_version}) already installed")
            return
        except importlib.metadata.PackageNotFoundError:
            pass
            
        # Installation du plugin
        package_spec = plugin_id
        if version_spec:
            package_spec += version_spec if version_spec.startswith(('==', '>=', '<=', '>', '<', '!=')) else f"=={version_spec}"
        
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package_spec])
            logger.info(f"Successfully installed plugin {package_spec}")
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to install plugin {package_spec}: {e}")
            raise

    def _load_config(self, name: str, path: Path):
        """Charge une configuration XML"""
        path = path.resolve()
        file_hash = self._file_hash(path)
        try:
            tree = ET.parse(path)
            config = self._xml_to_dict(tree.getroot())
            config['_hash'] = file_hash

            with self._lock:
                self._configs[name] = config

        except ET.ParseError as e:
            logger.error(f"XML parsing error in config {path}: {e}")
        except Exception as e:
            logger.error(f"Failed to load config {path}: {e}")

    def _file_hash(self, path: Path) -> str:
        """Calcule le hash d'un fichier"""
        path = path.resolve()
        if path not in self._file_hashes:
            try:
                with open(path, 'rb') as f:
                    self._file_hashes[path] = hashlib.md5(f.read()).hexdigest()
            except IOError as e:
                logger.error(f"Could not read file {path}: {e}")
                return ""
        return self._file_hashes[path]

    def _xml_to_dict(self, element) -> Dict[str, Any]:
        """Convertit XML en dict"""
        result = {**element.attrib}
        for child in element:
            child_data = self._xml_to_dict(child)
            if child.tag in result:
                if isinstance(result[child.tag], list):
                    result[child.tag].append(child_data)
                else:
                    result[child.tag] = [result[child.tag], child_data]
            else:
                result[child.tag] = child_data or child.text
        return result

    @lru_cache(maxsize=1024)
    def get(self, module: str, key: str, default: Any = None) -> Any:
        """Récupère une valeur avec cache"""
        with self._lock:
            keys = key.split('.')
            try:
                value = self._configs.get(module, {})
                for k in keys:
                    value = value[k]
                return value
            except (KeyError, TypeError):
                return default

    def get_project_root(self) -> Path:
        """Retourne la racine du projet"""
        with self._lock:
            return self._project_root

    def get_modules_metadata(self) -> Dict[str, Dict]:
        """Retourne les métadonnées de tous les modules"""
        with self._lock:
            return self._modules_metadata.copy()

    def get_files_from_directory(
        self, 
        directory_name: str, 
        module: str = None, 
        file_filter: str = None
    ) -> Dict[str, List[Path]]:
        """
        Récupère les fichiers d'un répertoire spécifique dans le projet
        
        Args:
            directory_name: Nom du répertoire ('public', 'pages', etc.)
            module: Nom du module (None pour global)
            file_filter: Regex pour filtrer les fichiers
            
        Returns:
            Dictionnaire des chemins des fichiers trouvés
        """
        result = {}
        with self._lock:
            if module is None:
                # Global directory
                dir_path = self._project_root / directory_name
                if dir_path.exists() and dir_path.is_dir():
                    files = self._filter_files(dir_path, file_filter)
                    if files:
                        result['global'] = files
            else:
                # Module directory
                if module in self._modules_metadata:
                    dir_path = self._project_root / 'modules' / module / directory_name
                    if dir_path.exists() and dir_path.is_dir():
                        files = self._filter_files(dir_path, file_filter)
                        if files:
                            result[module] = files
            
            return result

    def _filter_files(self, directory: Path, pattern: str = None) -> List[Path]:
        """Filtre les fichiers selon un motif regex"""
        files = []
        for item in directory.rglob('*'):
            if item.is_file():
                if pattern is None or re.match(pattern, item.name):
                    files.append(item)
        return files

    def get_config_params(
        self, 
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
            
        Returns:
            Dictionnaire des paramètres trouvés
        """
        with self._lock:
            config = self._configs.get('global' if module is None else module, {})
            keys = param_path.split('.')
            
            try:
                value = config
                for k in keys:
                    value = value[k]
                
                if key_filter is None:
                    return value
                
                if isinstance(value, dict):
                    return {
                        k: v for k, v in value.items() 
                        if re.match(key_filter, k)
                    }
                elif isinstance(value, list):
                    return [
                        item for item in value 
                        if isinstance(item, dict) and 
                        any(re.match(key_filter, k) for k in item.keys())
                    ]
                return value
                
            except (KeyError, TypeError):
                return {}