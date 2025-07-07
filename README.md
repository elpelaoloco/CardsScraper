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

- Los tests específicos para cada tienda aseguran:
  - Que los `selectors` estén definidos correctamente
  - Que las URLs configuradas sean válidas
  - Que los productos estén visibles y accesibles
- Los errores se agrupan y reportan al final del archivo de reporte para facilitar el debug

---

## 🛠️ Agregar una Nueva Tienda

1. Crear un archivo en `src/scrapers/` basado en los existentes
2. Agregar su entrada en `scrapers_config.json` con `selectors` específicos
3. Agregar su entrada en el archivo `src/core/scraper_factory.py` para que se ejecute
4. Crear un `test_<tienda>.py` dentro de `tests/unit/` y heredar de `BaseScraperTest`
5. Correr `python tests/run_all_tests.py` para verificar

---
