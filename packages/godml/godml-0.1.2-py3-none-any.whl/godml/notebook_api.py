from godml.core.parser import load_pipeline
from godml.core.executors import get_executor
from godml.core.models import PipelineDefinition

class GodmlNotebook:
    def __init__(self):
        self.pipeline = None
    
    def create_pipeline(self, name: str, model_type: str, hyperparameters: dict, 
                       dataset_path: str, output_path: str = None):
        config = {
            "name": name,
            "version": "1.0.0",
            "provider": "mlflow",
            "dataset": {
                "uri": dataset_path,
                "hash": "auto"
            },
            "model": {
                "type": model_type,
                "hyperparameters": hyperparameters
            },
            "metrics": [
                {"name": "auc", "threshold": 0.8}
            ],
            "governance": {
                "owner": "notebook-user@company.com",
                "tags": [{"source": "jupyter"}]
            },
            "deploy": {
                "realtime": False,
                "batch_output": output_path or f"./outputs/{name}_predictions.csv"
            }
        }
        
        self.pipeline = PipelineDefinition(**config)
        return self.pipeline
    
    def train(self):
        if not self.pipeline:
            raise ValueError("Primero crea un pipeline")
        
        executor = get_executor(self.pipeline.provider)
        executor.run(self.pipeline)
        return "✅ Entrenamiento completado"

def quick_train(model_type: str, hyperparameters: dict, dataset_path: str, name: str = None):
    """Función rápida para entrenar un modelo"""
    godml = GodmlNotebook()
    name = name or f"{model_type}-quick-train"
    
    godml.create_pipeline(
        name=name,
        model_type=model_type,
        hyperparameters=hyperparameters,
        dataset_path=dataset_path
    )
    
    godml.train()
    return "✅ Modelo entrenado exitosamente"

# Agregar al final de notebook_api.py

def train_from_yaml(yaml_path: str = "./godml/godml.yml"):
    """Entrenar usando configuración YAML existente"""
    try:
        # Cargar pipeline desde YAML
        pipeline = load_pipeline(yaml_path)
        
        # Ejecutar
        executor = get_executor(pipeline.provider)
        executor.run(pipeline)
        
        return f"✅ Modelo {pipeline.model.type} entrenado desde {yaml_path}"
    except Exception as e:
        return f"❌ Error: {e}"

def quick_train_yaml(model_type: str, hyperparameters: dict, yaml_path: str = "./godml/godml.yml"):
    """Entrenar modificando el YAML existente"""
    try:
        # Cargar configuración base del YAML
        pipeline = load_pipeline(yaml_path)
        
        print(f"🔄 Cambiando modelo de '{pipeline.model.type}' a '{model_type}'")
        print(f"🔧 Hiperparámetros originales: {pipeline.model.hyperparameters.dict()}")
        
        # Modificar el modelo y hiperparámetros
        pipeline.model.type = model_type
        pipeline.model.hyperparameters = type(pipeline.model.hyperparameters)(**hyperparameters)
        pipeline.name = f"{pipeline.name}-{model_type}"
        
        print(f"🔧 Nuevos hiperparámetros: {hyperparameters}")
        
        # Ejecutar
        executor = get_executor(pipeline.provider)
        executor.run(pipeline)
        
        return f"✅ Modelo {model_type} entrenado con configuración de {yaml_path}"
    except Exception as e:
        return f"❌ Error: {e}"
