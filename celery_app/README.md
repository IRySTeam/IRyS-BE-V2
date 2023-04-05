## Environment Variables
### Celery Docker
| Variable | Description | Default |
| --- | --- | --- |
| `CELERY_BROKER_URL` | The URL of the broker to use. | `redis://redis:6379/0` |
| `CELERY_RESULT_BACKEND` | The URL of the result backend to use. | `redis://redis:6379/0` |
Note:
1. The value of `CELERY_BROKER_URL` and `CELERY_RESULT_BACKEND` should be the same as the value of redis configuration in the `docker-compose.yml` file.