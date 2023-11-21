run_app:
	python3 manage.py makemigrations config
	python3 manage.py makemigrations users
	python3 manage.py migrate config
	python3 manage.py migrate users
	uvicorn daas.asgi:application --host 0.0.0.0 --port 8000
	
run:
	python3 manage.py run_app

initial_configs:
	python3 manage.py initial_configs
	