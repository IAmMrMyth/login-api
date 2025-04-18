# login-api

This project is a Django-based login API service that provides user management functionalities including authentication, profile management, and integration with the Kavenegar SMS service for messaging capabilities.


## Notes:
- To use OTP, put your API_KEY in `django_kavenegar/common.py` (variable: `API_KEY`)
- Redis is required for this project
- Redis configuration is currently hard-coded - modify it directly in the code if needed

1. Clone the repository.
2. Install the required Python packages:
   ```
   pip install -r requirement.txt
   ```
3. Apply database migrations:
   ```
   python manage.py migrate
   ```
4. Run the development server:
   ```
   python manage.py runserver
   ```

## API Documentation

The API documentation is available via Swagger UI at the following URL after running the server:

```
http://localhost:8000/docs/
```

This provides an interactive interface to explore and test the API endpoints.
