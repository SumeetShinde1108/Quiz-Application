# Quiz-Application
Welcome to the Quiz Application! This Django-based quiz platform allows users to participate in specefic time. Admins or user can create quizzes, set points for each quiz, and each users can answer questions with instant result updates Django APIs. The application also features user authentication to create quiz via API.

# Features
1.Topic-Based Quizzes: Admins or users can create quizzes on different topics , and any user will be able to participate in a quiz which he not created.

2.Instant Result Update: Users receive instant result updates with the help Django APIs.

3.User Authentication: Secure jwt authentication for a personalized experience.

4.Scoring System: Each question in a quiz is assigned points, providing users with a leaderboard system.

# Installation
To run this project locally for development purposes, follow these steps:

## Project Structure
Quiz-Application/
├── Quiz/
│   ├── __pycache__/
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── ...
├── quiz_app/
│   ├── __pycache__/
│   ├── migrations/
│   │   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── serializers.py
│   ├── tests.py
│   ├── views.py
│   └── ...
├── db.sqlite3
├── manage.py
├── requirements.txt
├── README.md

1. Clone the repository to your local machine:
```shell
git clone https://github.com/SumeetShinde1108/Quiz-Application.git
```

2. Navigate to the project directory:
```shell
cd quiz_app
```

3. Install dependencies:
```shell
pip install -r requirements.txt
```

4. Run migrations:
```shell
python manage.py migrate
```

5. Create a superuser for admin access:
```shell
python manage.py createsuperuser
```

6. To run all tests :
```shell
python manage.py test quiz_app.tests
```

7. Start the development server:
```shell
python manage.py runserver
```




