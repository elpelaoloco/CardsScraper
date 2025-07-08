## 📁 Estructura del Proyecto

```
CardsScraper/
├── configs/                   # Archivos JSON de configuración
│   └── scrapers_config.json
├── data/                      # (opcional) Carpeta para guardar resultados
├── logs/                      # Logs de ejecución
├── reports/                   # Resultados de scraping o tests
│   └── test_report.txt
├── screenshots/               # Capturas de fallos o páginas
├── src/
│   ├── core/                  # Lógica general del scraper (base, manager, factory)
│   └── scrapers/              # Scrapers específicos por tienda
├── tests/
│   ├── unit/                  # Tests unitarios por tienda y core
│   ├── utils/                 # utilidades para testeo (base y runner)
│   └── run_all_tests.py       # Ejecuta todos los tests
├── config_scraper.py          # Módulo para carga manual de configuración
├── main.py                    # Punto de entrada principal del scraper
└── README.md
```

---

## 🧰 Requisitos

- Python 3.11+
- Google Chrome + chromedriver
- Entorno virtual (`.venv` recomendado)


---

## ⚙️ Uso

### Scraping

```bash
python main.py
```

Esto inicia todos los scrapers definidos en `scrapers_config.json`.

### Testing

```bash
python tests/run_all_tests.py
```

Esto genera un reporte detallado en `test_report.txt` con resultados por test, agrupados por módulo y tienda.

---

## 🧪 Testing Avanzado

### Tests por Tienda
- Los tests específicos para cada tienda aseguran:
  - Que los `selectors` estén definidos correctamente
  - Que las URLs configuradas sean válidas
  - Que los productos estén visibles y accesibles
- Los errores se agrupan y reportan al final del archivo de reporte para facilitar el debug

### Tests de ScraperManager
El archivo `tests/unit/test_scraper_manager.py` contiene 20 tests que verifican:

**Inicialización y Configuración:**
- `test_init_with_json_config`: Inicialización con archivo JSON
- `test_init_with_yaml_config`: Inicialización con archivo YAML  
- `test_load_config_file_not_found`: Manejo de archivos inexistentes
- `test_load_config_invalid_format`: Manejo de formatos no soportados
- `test_load_config_invalid_json`: Manejo de JSON inválido
- `test_load_config_scraper_creation_failure`: Manejo de errores en creación de scrapers
- `test_load_config_no_scrapers_section`: Configuración sin sección scrapers

**Funcionalidad Principal:**
- `test_get_game_from_category`: Mapeo de categorías a juegos (magic, yugioh, pokemon)
- `test_run_scraper_success`: Ejecución exitosa de scraper individual
- `test_run_scraper_not_found`: Manejo de scrapers inexistentes
- `test_run_all_scrapers`: Ejecución de todos los scrapers
- `test_run_all_scrapers_empty_config`: Manejo de configuración vacía

**Gestión de Resultados y Reportes:**
- `test_save_results_per_category`: Guardado de resultados por categoría
- `test_get_report`: Obtención de reportes
- `test_make_report`: Generación de reportes finales
- `test_scraper_lifecycle`: Ciclo completo de scraping

**Integración y Manejo de Errores:**
- `test_integration_with_scraper_factory`: Integración con ScraperFactory
- `test_logger_integration`: Integración con sistema de logging
- `test_error_handling_during_scraper_run`: Manejo de errores durante ejecución
- `test_config_access_after_loading`: Acceso a configuración tras carga

**MockScraper:** Implementación de prueba que extiende BaseScraper para testing, implementando todos los métodos abstractos necesarios.

---

## 🛠️ Agregar una Nueva Tienda

1. Crear un archivo en `src/scrapers/` basado en los existentes
2. Agregar su entrada en `scrapers_config.json` con `selectors` específicos
3. Agregar su entrada en el archivo `src/core/scraper_factory.py` para que se ejecute
4. Crear un `test_<tienda>.py` dentro de `tests/unit/` y heredar de `BaseScraperTest`
5. Correr `python tests/run_all_tests.py` para verificar

---
