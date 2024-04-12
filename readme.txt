Steps to run the project:

1. Install Python 3.8 or later

2. Install Python Django 

3. Install Postgres Database 
	If you want to use Postgres database, You need to update database credentials in settings.py. 
	By default system will sqlligt database.

4. Open Folder Power-DataMate project in VS Code

5. Activate the Virtual Environment -- Linux
	Source /venv/bin/activate

6. Make Migrations using below command 
	python manage.py makemigrations

7. Migrate the changes to database
	python manage.py migrate 

8. Run Server 
	python manage.py runserver

9. Open the below URL 
	http://127.0.0.1:8000/bms

10. Login -- System will redirect you on login page
	http://127.0.0.1:8000/bms/login 
	Enter your Username & Password 
	Click on Login Button, You will be enter in Home Page. 
