from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path
import os
import threading
from typing import Dict, List, Optional
from fastapi import Request
from fastapi.responses import HTMLResponse
import logging
from .config_manager import ConfigManager

logger = logging.getLogger(__name__)

class PageManager:
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
        self._project_root = None
        self._config = ConfigManager()
        self._templates = None
        self._static_mounts = []
        self._lock = threading.RLock()

    def set_project_root(self, path: Path):
        """Définit la racine du projet"""
        with self._lock:
            self._project_root = path.resolve()
            self._init_templates()
            self._init_static_mounts()

    def _init_templates(self):
        """Initialise les templates Jinja2"""
        template_dirs = []
        
        # Global pages
        global_pages = self._project_root / 'pages'
        if global_pages.exists():
            template_dirs.append(str(global_pages))
        
        # Modules pages
        modules_metadata = self._config.get_modules_metadata()
        modules_dir = self._project_root / 'modules'
        if modules_dir.exists():
            for module_name in modules_metadata.keys():
                module_pages = modules_dir / module_name / 'pages'
                if module_pages.exists():
                    template_dirs.append(str(module_pages))
        
        if template_dirs:
            self._templates = Jinja2Templates(directory=template_dirs)

    def _init_static_mounts(self):
        """Initialise les chemins pour les fichiers statiques"""
        self._static_mounts = []
        
        # Global public
        global_public = self._project_root / 'public'
        if global_public.exists():
            self._static_mounts.append(('/assets', global_public))
        
        # Modules public
        modules_metadata = self._config.get_modules_metadata()
        modules_dir = self._project_root / 'modules'
        if modules_dir.exists():
            for module_name in modules_metadata.keys():
                module_public = modules_dir / module_name / 'public'
                if module_public.exists():
                    self._static_mounts.append((f'/assets/{module_name}', module_public))

    def mount_static_files(self, app):
        """Monte les fichiers statiques sur l'application FastAPI"""
        with self._lock:
            for route, path in self._static_mounts:
                app.mount(route, StaticFiles(directory=path), name=f"static_{path.name}")

    def render_template(self, request: Request, template_name: str, context: str = 'global', **kwargs) -> HTMLResponse:
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
        with self._lock:
            if self._templates is None:
                raise ValueError("Templates not initialized")
                
            # Ajoute les URLs des assets au contexte
            kwargs.update({
                'request': request,
                'static_url': self.get_static_url(context)
            })
            
            try:
                # Essaye d'abord avec le contexte spécifié
                template_path = f"{context}/{template_name}" if context != 'global' else template_name
                return self._templates.TemplateResponse(template_path, kwargs)
            except Exception as e:
                # Fallback global si le template n'est pas trouvé dans le module
                if context != 'global':
                    try:
                        return self._templates.TemplateResponse(template_name, kwargs)
                    except Exception:
                        pass
                logger.error(f"Error rendering template {template_name}: {e}")
                raise

    def get_static_url(self, context: str = 'global') -> str:
        """
        Retourne l'URL de base pour les assets statiques
        
        Args:
            context: 'global' ou nom du module
            
        Returns:
            URL de base pour les assets
        """
        if context == 'global':
            return '/assets'
        return f'/assets/{context}'

    def list_templates(self, context: str = None) -> Dict[str, List[str]]:
        """
        Liste tous les templates disponibles
        
        Args:
            context: 'global', nom de module ou None pour tous
            
        Returns:
            Dictionnaire des templates disponibles
        """
        with self._lock:
            if self._templates is None:
                return {}
                
            result = {}
            template_dirs = self._templates.env.loader.searchpath
            
            for template_dir in template_dirs:
                ctx = 'global'
                if 'modules' in template_dir:
                    ctx = Path(template_dir).parent.name
                
                if context is not None and ctx != context:
                    continue
                    
                templates = []
                for root, _, files in os.walk(template_dir):
                    for file in files:
                        if file.endswith('.html'):
                            rel_path = os.path.relpath(os.path.join(root, file), template_dir)
                            templates.append(rel_path.replace('\\', '/'))
                
                if ctx not in result:
                    result[ctx] = []
                result[ctx].extend(templates)
            
            return result