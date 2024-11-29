<p >
    <img width="100%" src="https://github.com/user-attachments/assets/7b177163-3f7e-48f7-a95e-e90149dc7852"> 
</p>

# Proyecto individual módulo Back End

## Aplicación eCommerce sin pasarela de pagos

## Características
La aplicación expone la API principal del eCommerce que interactúa con una base de datos no-relacional.

- **API RESTful**: Proporciona endpoints para realizar operaciones CRUD de productos, usuarios y órdenes de compra.
- **MongoDB Atlas**: Utiliza MongoDB como base de datos y Pymongo para interactuar con la aplicación.
- **Validación de Datos**: Usa Pydantic para validación y gestión de datos.
- **Documentación Automática**: Genera automáticamente documentación interactiva con Swagger UI.
- **Autenticación y Autorización**: Utiliza tokens JWT para manejo de sesión, verifiación de identidad e interacción con endpoints en base a roles.
- **Email transaccional**: Utiliza FastAPI-MAIL para envío automático de notificaciónes de compra, token de verificación para nuevos usuarios y cambio de contraseña.
- **Gestion de dependencias**: Utiliza Poetry como gestor de dependencias y entorno virtual predeterminado.

## Requisitos
- Python 3.12
- MongoDB (de preferencia MongoDB Atlas remoto para permitir funcionalidad de índice de búsqueda)
- Dependencias del proyecto (ver `requirements.txt`)

## Intalación
1. Clonar repositorio

```bash
git clone https://github.com/andresbonelli/proyecto-final-backend
```
2. Navegar a directorio raíz

```bash
cd proyecto_final_backend
```
3. Instalar dependencias

```bash
poetry install
```
4. Crear archivo `.env` y poblar las variables de entorno necesarias (ver `.env.example`)

```bash
touch '.env'
```
```bash
echo '.env' >> .gitignore
```
6. (opcional) Generar un usuario administrador general (ver ejemplo en `scripts/ADMIN_USER_CONF.example`) 
```bash
cd scripts && touch '.ADMIN_USER_CONF'
```
(añadir al archivo las variables de 'USERNAME', 'EMAIL' y 'PASSWORD' personalizadas)
```bash
python -m scripts.create_super_user
```
```bash
echo '.ADMIN_USER_CONF' >> .gitignore
```
8. Ejecutar modo de desarrollo.
   
```bash
fastapi dev
```
> Navegar a la documentación expuesta en [http://localhost:8000/docs](http://localhost:8000/docs)

## Despliegue demo: https://vocal-nelie-andresbonelli-1d085aa1.koyeb.app/docs#/

