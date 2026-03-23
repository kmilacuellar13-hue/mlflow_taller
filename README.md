# MLflow Taller: Penguin Classification

Este repositorio contiene la solución al taller de MLflow, desplegando un entorno completo para experimentación y despliegue usando Docker Compose.

## Arquitectura del Servicio

- **MLflow DB (PostgreSQL):** Almacenamiento dedicado para los metadatos de MLflow.
- **Data DB (PostgreSQL):** Almacenamiento dedicado para los datos crudos y procesados, independiente de MLflow.
- **MinIO:** Almacenamiento de artefactos S3 en el bucket `mlflows3`.
- **MLflow:** Servidor para el registro y tracking de experimentos.
- **JupyterLab:** Entorno para el entrenamiento de modelos, configurado para conectar con bases de datos y MLflow.
- **FastAPI:** Servicio de API para realizar inferencia obteniendo el modelo más reciente registrado en MLflow.

## Instrucciones de Ejecución

1. Asegúrese de tener Docker y Docker Compose instalados.
2. Construya y levante los servicios:
   ```bash
   docker-compose up --build -d
   ```
3. Abra JupyterLab en http://localhost:8888. Cuando se le solicite un **Password or Token**, ingrese `mlflowtaller` para iniciar sesión. Luego, navegue a `jupyter/data_setup.ipynb` para cargar los datos a la base de datos `data_db`.
4. Ejecute el notebook `jupyter/train.ipynb` para realizar el preprocesamiento, entrenar el modelo, y registrar las múltiples ejecuciones (27 iteraciones) a través de Grid Search usando MLflow.
5. Ingrese a MLflow en http://localhost:5000 para revisar los experimentos registrados y verificar que el modelo "PenguinModel" esté visible en Model Registry.
6. La API en http://localhost:8000 estará ya ejecutándose y cargará el modelo desde MLflow (reinicie el contenedor de la API si se levantó antes de registrar el modelo):
   ```bash
   docker-compose restart api
   ```
7. Pruebe la inferencia mediante peticiones POST a `http://localhost:8000/predict`. Para probar esto de manera más interactiva sin usar código ni Postman, ingrese a **http://localhost:8000/docs** desde su navegador, haga click en el botón `POST /predict`, pulse "Try it out" y envíe sus datos en formato JSON preconfigurado.

## Modelo Utilizado e Iteraciones (Grid Search)

Se implementó un pipeline en `scikit-learn` utilizando `RandomForestClassifier`. Los datos fueron extraidos de una base de datos PostgreSQL (`data_db`) donde posteriormente también se guardó una versión estructurada (`processed_penguins`).

El Grid Search se configuró explorando el siguiente espacio de hyperparámetros:

- `n_estimators`: [50, 100, 200]
- `max_depth`: [Ninguno, 5, 10]
- `min_samples_split`: [2, 5, 10]

Esto genera un total de **27 iteraciones**, asegurando el requisito establecido (múltiples ejecuciones, al menos 20 iteraciones con variaciones de hiperparámetros). Todas estas ejecuciones son automáticamente detectadas y guardadas por la función `mlflow.autolog()`, logrando que hiperparámetros, métricas (incluyendo accuracy, recall) y los propios artefactos de los sub-modelos se almacenen en MLflow y MinIO respectivamente. El mejor modelo evaluado durante el CV es el que termina siendo registrado de forma explícita en el "Model Registry" bajo el nombre **PenguinModel**.

Finalmente, el servicio FastAPI sirve el modelo utilizando la función de inferencia estándar del objeto estandarizado `pyfunc`, permitiendo interacciones API-to-Model en tiempo real.
