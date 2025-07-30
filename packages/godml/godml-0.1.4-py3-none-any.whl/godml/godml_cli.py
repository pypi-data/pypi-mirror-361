# Copyright (c) 2024 Arturo Gutierrez Rubio Rojas
# Licensed under the MIT License

import os
import typer
import shutil
from pathlib import Path
from godml.core.parser import load_pipeline
from godml.core.executors import get_executor
from godml.utils.logger import get_logger

logger = get_logger()

app = typer.Typer()

@app.command()
def run(file: str = typer.Option(..., "--file", "-f", help="Ruta al archivo YAML")):
    """
    Ejecuta un pipeline GODML desde un archivo YAML.
    """
    try:
        pipeline = load_pipeline(file)
        executor = get_executor(pipeline.provider)
        executor.validate(pipeline)
        result = executor.run(pipeline)
        
        if result is False:
            logger.error("❌ Entrenamiento fallido")
            raise typer.Exit(1)
            
    except Exception as e:
        logger.error(f"❌ Error: {str(e)}")
        raise typer.Exit(1)

@app.command()
def init(project_name: str):
    """
    Inicializa un nuevo proyecto GODML.
    """
    logger.info(f"🚀 Inicializando proyecto GODML: {project_name}")
 
    
    # Crear estructura de directorios
    project_path = Path(project_name)
    project_path.mkdir(exist_ok=True)
    
    # Crear subdirectorios
    (project_path / "data").mkdir(exist_ok=True)
    (project_path / "outputs").mkdir(exist_ok=True)
    (project_path / "models").mkdir(exist_ok=True)
    
    # Crear godml.yml template
    godml_template = f"""name: {project_name}
version: 1.0.0
provider: mlflow

dataset:
  uri: ./data/your_dataset.csv
  hash: auto

model:
  type: xgboost
  hyperparameters:
    max_depth: 5
    eta: 0.3
    objective: binary:logistic
    eval_metric: auc

metrics:
- name: auc
  threshold: 0.85
- name: accuracy
  threshold: 0.80

governance:
  owner: your-team@company.com
  tags:
  - project: {project_name}
  - environment: development

deploy:
  realtime: false
  batch_output: ./outputs/predictions.csv
"""
    
    # Escribir archivos
    with open(project_path / "godml.yml", "w") as f:
        f.write(godml_template)
    
    with open(project_path / "README.md", "w", encoding="utf-8") as f: 
        f.write(f"""name: {project_name}
**Proyecto GODML - Machine Learning con Gobernanza**

[![GODML](https://img.shields.io/badge/Powered%20by-GODML-blue.svg)](https://pypi.org/project/godml/)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> Proyecto de Machine Learning generado automáticamente con **GODML Framework** - Governed, Observable & Declarative ML

---
            
🎯 ¿Qué es este proyecto?
Este proyecto fue generado con GODML , un framework que unifica:

Gobernanza : Trazabilidad y metadatos automáticos

Observabilidad : Tracking completo con MLflow

Declarativo : Configuración simple en YAML

📁 Estructura del Proyecto
                
{project_name}/
├── godml.yml              # 🎯 Configuración principal del pipeline
├── data/                  # 📊 Datasets
│   └── your_dataset.csv   # ← Coloca aquí tus datos
├── outputs/               # 📈 Predicciones y resultados
│   └── predictions.csv    # Salida del modelo
├── models/                # 🤖 Modelos entrenados
│   ├── production/        # Modelos en producción
│   ├── staging/           # Modelos en testing
│   └── experiments/       # Modelos experimentales
├── mlruns/                # 📋 Experimentos MLflow (auto-generado)
├── requirements.txt       # 📦 Dependencias del proyecto
└── README.md             # 📖 Esta documentación


⚙️ Configuración del Pipeline
El archivo godml.yml contiene toda la configuración:

Dataset

dataset:
  uri: ./data/your_dataset.csv  # ← Cambia por tu archivo
  hash: auto                    # Hash automático para trazabilidad

Modelo

model:
  type: xgboost                 # Algoritmo a usar
  hyperparameters:              # Parámetros del modelo
    max_depth: 5
    eta: 0.3
    objective: binary:logistic

Métricas de Calidad

metrics:
- name: auc
  threshold: 0.85              # Umbral mínimo de calidad
- name: accuracy
  threshold: 0.80

Gobernanza

governance:
  owner: your-team@company.com  # ← Cambia por tu email
  tags:
  - project: {project_name}
  - environment: development    # development/staging/production

🔧 Modelos Disponibles
Algoritmo	Tipo	Comando
xgboost	Gradient Boosting	Por defecto
random_forest	Ensemble	Cambiar en model.type
lightgbm	Gradient Boosting	Cambiar en model.type

📊 Métricas Soportadas

auc - Area Under Curve

accuracy - Precisión

precision - Precisión por clase

recall - Recall por clase

f1 - F1 Score

🎯 Flujo de Trabajo
1. Preparar Datos

# Coloca tu dataset en data/
cp mi_dataset.csv data/your_dataset.csv

2. Configurar Pipeline

# Edita godml.yml según tus necesidades
vim godml.yml

3. Entrenar Modelo

# Ejecuta el pipeline completo
godml run -f godml.yml

4. Revisar Resultados

# Ver experimentos en MLflow
mlflow ui

# Ver predicciones
cat outputs/predictions.csv

🏛️ Gobernanza y Trazabilidad
GODML automáticamente registra:

✅ Hash del dataset para trazabilidad

✅ Metadatos del modelo (parámetros, métricas)

✅ Información de gobernanza (owner, tags)

✅ Timestamp y versión de cada experimento

✅ Linaje completo del pipeline

🚀 Próximos Pasos
Agregar tus datos: Coloca tu dataset en data/

Personalizar configuración: Edita godml.yml

Entrenar modelo: Ejecuta godml run -f godml.yml

Monitorear: Revisa resultados en MLflow UI

Iterar: Ajusta parámetros y vuelve a entrenar

📚 Recursos Útiles
📦 GODML en PyPI

📖 Documentación GODML

🎯 Configuración YAML

🏛️ Guía de Gobernanza

🤝 Soporte
¿Necesitas ayuda?

🐛 Reportar Issues

💬 Discusiones

📧 Contacto

📄 Licencia
Este proyecto está bajo la licencia MIT. Ver LICENSE para más detalles.

Generado con ❤️ por GODML Framework v0.1.2
Governed, Observable & Declarative Machine Learning
""")
    
    with open(project_path / "requirements.txt", "w") as f:
        f.write("godml>=0.1.0\npandas>=1.3.0\nscikit-learn>=1.0.0\nxgboost>=1.5.0\nmlflow>=2.0.0")

    logger.info(f"✅ Proyecto {project_name} creado exitosamente!")
    logger.info(f"📁 Ubicación: {project_path.absolute()}")
    logger.info("📋 Próximos pasos:")
    logger.info(f"   cd {project_name}")
    logger.info("   pip install -r requirements.txt")
    logger.info("   godml run -f godml.yml")

def main():
    """Función principal para el CLI"""
    app()

if __name__ == "__main__":
    main()
