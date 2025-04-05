## Instalación

1. **Clonar el repositorio**:
   ```bash
   git clone https://github.com/tuusuario/task-manager-backend.git
   cd task-manager-backend
   ```

2. **Crear un entorno virtual**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # En Linux/Mac
   venv\Scripts\activate     # En Windows
   ```

3. **Instalar dependencias**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configurar MongoDB**:
   - Si estás usando MongoDB Atlas, obtén la URI de conexión desde tu clúster de MongoDB.
   - Configura la URI de MongoDB en un archivo `.env` o en las variables de entorno:
     ```bash
     MONGO_URI="mongodb+srv://usuario:contraseña@cluster.mongodb.net/db?retryWrites=true&w=majority"
     ```

5. **Subir el código a AWS Lambda**:
   Si estás usando un CI/CD como GitHub Actions, el código se subirá automáticamente. Si lo haces manualmente:

   - Empaqueta tu código en un archivo ZIP:
     ```bash
     zip -r function.zip .
     ```
   
   - Sube el archivo `function.zip` a un bucket de S3 en AWS y luego actualiza la función Lambda.

6. **Configurar AWS API Gateway**:
   - En el **API Gateway**, crea un nuevo API RESTful.
   - Crea un recurso y asigna los métodos HTTP (GET, POST, PUT, DELETE).
   - Asocia cada método a su respectiva función Lambda.

## Endpoints

### `GET /tasks`

Obtiene todas las tareas almacenadas en MongoDB.

**Respuesta**:
- `200 OK`: Lista de tareas.
- `500 Internal Server Error`: Si ocurre un error al obtener las tareas.

### `POST /tasks`

Crea una nueva tarea en MongoDB.

**Cuerpo de la solicitud**:
```json
{
  "title": "Mi nueva tarea",
  "description": "Descripción de la tarea",
  "status": "Pendiente"
}
```

**Respuesta**:
- `201 Created`: Tarea agregada exitosamente.
- `400 Bad Request`: Si la solicitud es inválida.
- `500 Internal Server Error`: Si ocurre un error al agregar la tarea.

### `PUT /tasks`

Actualiza el estado de una tarea existente.

**Cuerpo de la solicitud**:
```json
{
  "_id": "ID_de_la_tarea",
  "status": "Completada"
}
```

**Respuesta**:
- `200 OK`: Tarea actualizada exitosamente.
- `404 Not Found`: Si la tarea no existe.
- `500 Internal Server Error`: Si ocurre un error al actualizar la tarea.

### `DELETE /tasks`

Elimina una tarea por su ID.

**Cuerpo de la solicitud**:
```json
{
  "_id": "ID_de_la_tarea"
}
```

**Respuesta**:
- `200 OK`: Tarea eliminada exitosamente.
- `404 Not Found`: Si la tarea no existe.
- `500 Internal Server Error`: Si ocurre un error al eliminar la tarea.

## Tests

Para realizar pruebas unitarias, puedes ejecutar:

```bash
pytest tests/
```

## Despliegue

Puedes desplegar el backend en AWS Lambda siguiendo estos pasos:

1. Empaquetar el código:
   ```bash
   zip -r function.zip .
   ```

2. Subir el archivo `function.zip` a un bucket de S3.

3. Actualizar la función Lambda en AWS:
   ```bash
   aws lambda update-function-code --function-name task-manager --s3-bucket <bucket-name> --s3-key function.zip
   ```

## Contribuir

1. Haz un fork del repositorio.
2. Crea una rama para tu cambio (`git checkout -b feature/nueva-funcionalidad`).
3. Realiza los cambios y haz commit (`git commit -am 'Agrega nueva funcionalidad'`).
4. Empuja a tu rama (`git push origin feature/nueva-funcionalidad`).
5. Crea un Pull Request.

## Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para más detalles.
