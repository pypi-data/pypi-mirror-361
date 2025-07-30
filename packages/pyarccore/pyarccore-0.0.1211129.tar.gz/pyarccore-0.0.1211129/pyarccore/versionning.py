from packaging import version

def check_version(plugin_version, version_spec):
    """Vérifie si la version du plugin correspond à la spécification"""
    try:
        plugin_ver = version.parse(plugin_version)
        version_spec = version_spec.strip()
        
        # Gestion des OU logiques (priorité sur ET)
        if '||' in version_spec:
            or_parts = [p.strip() for p in version_spec.split('||')]
            return any(_process_spec(plugin_ver, part) for part in or_parts)
        
        return _process_spec(plugin_ver, version_spec)
    except:
        return False

def _process_spec(ver, spec):
    """Traite une spécification individuelle (peut contenir des ET)"""
    # Gestion des ET logiques
    if '&&' in spec:
        and_parts = [p.strip() for p in spec.split('&&')]
        return all(_compare(ver, part) for part in and_parts)
    
    # Gestion des intervalles avec virgule
    if ',' in spec:
        low, high = spec.split(',')
        return (_compare(ver, f'>={low.strip()}') and 
                _compare(ver, f'<={high.strip()}'))
    
    # Cas simple (version exacte)
    return _compare(ver, spec)

def _compare(ver, spec):
    """Compare une version avec une spécification individuelle"""
    spec = spec.strip()
    
    # Détection de l'opérateur
    op = ''
    if spec.startswith(('>=', '<=', '==', '!=')):
        op = spec[:2]
    elif spec.startswith(('>', '<')):
        op = spec[0]
    
    # Version exacte si pas d'opérateur
    if not op:
        return ver == version.parse(spec)
    
    spec_ver = version.parse(spec[len(op):].strip())
    
    # Comparaisons
    if op == '>':
        return ver > spec_ver
    elif op == '>=':
        return ver >= spec_ver
    elif op == '<':
        return ver < spec_ver
    elif op == '<=':
        return ver <= spec_ver
    elif op == '==':
        return ver == spec_ver
    elif op == '!=':
        return ver != spec_ver
    
    return False