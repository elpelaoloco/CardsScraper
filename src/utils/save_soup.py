import os
import json
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse


def save_soup_to_file(soup, 
                     filename=None,
                     output_dir="saved_html",
                     url=None,
                     prettify=True,
                     save_metadata=True,
                     overwrite=True,
                     debug=False):
    """
    Guarda un objeto BeautifulSoup en un archivo HTML
    
    Args:
        soup (BeautifulSoup): Objeto soup a guardar
        filename (str): Nombre del archivo (opcional, se genera automáticamente)
        output_dir (str): Directorio donde guardar
        url (str): URL original (opcional, para metadata)
        prettify (bool): Si formatear el HTML de manera legible
        save_metadata (bool): Si guardar metadata en archivo JSON
        overwrite (bool): Si sobrescribir archivos existentes
        debug (bool): Mostrar información de debug
        
    Returns:
        dict: Información sobre el archivo guardado
    """
    
    # Crear directorio si no existe
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # Generar nombre de archivo si no se proporciona
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if url:
            parsed_url = urlparse(url)
            domain = parsed_url.netloc.replace('www.', '')
            path = parsed_url.path.strip('/').replace('/', '_') or 'index'
            filename = f"{domain}_{path}_{timestamp}.html"
        else:
            # Usar título de la página si está disponible
            title = soup.title.string if soup.title else "page"
            title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).strip()
            title = title.replace(' ', '_')[:50]  # Limitar longitud
            filename = f"{title}_{timestamp}.html"
    
    # Asegurar extensión .html
    if not filename.endswith('.html'):
        filename += '.html'
    
    filepath = Path(output_dir) / filename
    metadata_path = filepath.with_suffix('.json')
    
    # Verificar si el archivo existe
    if filepath.exists() and not overwrite:
        raise FileExistsError(f"El archivo {filepath} ya existe. Use overwrite=True para sobrescribir.")
    
    if debug:
        print(f"💾 Guardando soup en: {filepath}")
    
    try:
        # Formatear HTML
        if prettify:
            html_content = soup.prettify()
        else:
            html_content = str(soup)
        
        # Guardar archivo HTML
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        file_size = filepath.stat().st_size
        
        # Preparar metadata
        metadata = {
            'filename': filename,
            'save_date': datetime.now().isoformat(),
            'file_size_bytes': file_size,
            'file_size_kb': round(file_size / 1024, 2),
            'content_length': len(html_content),
            'prettified': prettify,
            'status': 'success'
        }
        
        # Agregar información de la página si está disponible
        if soup.title:
            metadata['title'] = soup.title.string
        
        # Meta description
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc:
            metadata['meta_description'] = meta_desc.get('content', '')
        
        # URL original si se proporciona
        if url:
            metadata['original_url'] = url
        
        # Contar algunos elementos
        metadata['stats'] = {
            'links': len(soup.find_all('a')),
            'images': len(soup.find_all('img')),
            'paragraphs': len(soup.find_all('p')),
            'divs': len(soup.find_all('div')),
            'scripts': len(soup.find_all('script')),
            'stylesheets': len(soup.find_all('link', rel='stylesheet'))
        }
        
        # Guardar metadata si se solicita
        if save_metadata:
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        if debug:
            print(f"✅ Archivo guardado exitosamente!")
            print(f"📊 Tamaño: {metadata['file_size_kb']} KB")
            print(f"📝 Título: {metadata.get('title', 'Sin título')}")
            print(f"🔗 Enlaces: {metadata['stats']['links']}")
            print(f"🖼️ Imágenes: {metadata['stats']['images']}")
        
        return metadata
        
    except Exception as e:
        if debug:
            print(f"❌ Error guardando archivo: {e}")
        raise
