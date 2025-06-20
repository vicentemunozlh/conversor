# Conversión de monedas

Utilizando Python y el framework FastAPI, se creó una Rest API que simula la conversión entre las monedas CLP, PEN o COP utilizando cryptomonedas de la API pública de Buda.

Se llevan a cabo conversiones utilizando la cryptomoneda como intercambio que otorga el mejor rate.


## Supuestos:
- Solo se reciben currencies en mayúscula.
- No se considera el minimum_order_amount.
- No se espera que exista un mercado directo CLP-PEN, CLP-COP u otra de las combinaciones de posibles monedas de origen y destino (CLP, PEN o COP)
- Se espera como máximo 1 intermediario.

## Requisitos Previos
- Python 3.9 o superior
- pip (gestor de paquetes de Python)

## Instalación y Ejecución Local

1. **Crear y activar un entorno virtual**:
   ```bash
   python -m venv .venv
   # or python3 -m venv .venv
   source .venv/bin/activate
   ```

2. **Instalar dependencias**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Ejecutar la aplicación**:
   ```bash
   fastapi dev app/main.py
   ```

La aplicación estará disponible en `http://localhost:8000`

## Documentación de la API
Una vez que la aplicación esté en ejecución, puedes acceder a:
- Documentación Swagger UI: `http://localhost:8000/docs`
- Documentación ReDoc: `http://localhost:8000/redoc`

## Ejecutar Tests
Para ejecutar los tests del proyecto, asegúrate de que estás en el entorno virtual y que todas las dependencias están instaladas:

1. **Verificar que estás en el entorno virtual**:
   ```bash
   # Deberías ver (.venv) al inicio de tu línea de comandos
   # Si no lo ves, activa el entorno virtual:
   source .venv/bin/activate
   ```

2. **Ejecutar los tests**:
   ```bash
   pytest -v
   ```

## Ejecución con Docker

**NOTICE** La REST API estará expuesta en http://0.0.0.0:8000 para probar su uso facilmente. Podrás entrar a `http://localhost:8000/docs` para probar la API desde los docs. 

### Requisitos
- Docker

### Pasos para ejecutar con Docker

1. **Construir y ejecutar con Docker**:
     ```bash
   # Construir la imagen
   docker build -t conversor .

   # Ejecutar el contenedor
   docker run --name conversor-api -p 8000:8000 conversor
   ```

2. **Ejecutar los tests**:
   ```bash
   docker run conversor pytest -v
   ```

La REST API estará disponible en `http://localhost:8000`