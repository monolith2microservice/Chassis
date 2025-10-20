## Repository link: 
https://github.com/monolith2microservice/Chassis

## A list of functionalities moved to the repository and what they do.

| Functionality | Description |
|---------------|-------------|
| `get_session()` | Provides an asynchronous database session for use with FastAPI dependencies. Ensures proper opening and closing of sessions. |
| `BaseModel` | Base class for all ORM models. Provides a convenient `as_dict()` method to convert ORM objects to dictionaries. |
| `get_list(db, model)` | Retrieve all rows of a given SQLAlchemy model from the database asynchronously. |
| `get_list_statement_result(db, stmt)` | Executes a custom SQLAlchemy statement and returns all results as a list. |
| `get_element_statement_result(db, stmt)` | Executes a custom SQLAlchemy statement and returns a single result. |
| `get_element_by_id(db, model, element_id)` | Retrieves a single database object by its primary key. |
| `delete_element_by_id(db, model, element_id)` | Deletes an object by ID if it exists and commits the transaction. |
| `raise_and_log_error(status_code, message)` | Logs an error message and raises a FastAPI HTTPException with the given status code. |
| `EventPublisher` | Connects to RabbitMQ and publishes JSON events to a given exchange. Includes automatic reconnection attempts. |
| `setup_logging()` | Configures standardized logging format and level based on `settings.LOG_LEVEL`. |
| `router` | Provides a FastAPI router with a default health-check endpoint at `/health`. |
| `EventSuscriber` | Connects to RabbitMQ and reads |

---

## 2. A table that explains which microservices have used which functionality

| Functionality | Machine Service | Notes |
|---------------|----------------|-------|
| `get_session()` | ✅ | Used to manage database sessions in all services. |
| `BaseModel` | ✅ | Base class for ORM models in Machine and future microservices. |
| `get_list` | ✅ | Used to fetch pieces from DB in Machine Service. |
| `get_list_statement_result` | ✅ | Internal helper for custom DB queries. |
| `get_element_statement_result` | ✅ | Internal helper for single object queries. |
| `get_element_by_id` | ✅ | Used for fetching single pieces by ID. |
| `delete_element_by_id` | ✅ | Used for removing pieces or other records. |
| `raise_and_log_error` | ✅ | Standardized error handling for API endpoints. |
| `EventPublisher` | ✅ | Publishes piece-related events to RabbitMQ |
| `setup_logging` | ✅ | Standardizes logging across services. |
| `router` | ✅ | Provides a health check endpoint; can be extended in other services. |
| `EventSuscriber` | ✅ | Connects to RabbitMQ and reads|
---




