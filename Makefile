run_app:
	python3 manage.py makemigrations users
	python3 manage.py makemigrations config
	python3 manage.py migrate users
	python3 manage.py migrate config
	uvicorn daas.asgi:application --host 0.0.0.0 --port 8001
	
run:
	python3 manage.py run_app
	