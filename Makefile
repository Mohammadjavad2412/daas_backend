run_app:
	python3 manage.py makemigrations users
	python3 manage.py makemigrations config
	python3 manage.py migrate users
	python3 manage.py migrate config
	python3 manage.py runserver 0.0.0.0:8000
	
run:
	python3 manage.py run_app