# Quiz-Application
Welcome to the Quiz Application! This Django-based quiz platform allows users to participate in specefic time. Admins or user can create quizzes, set points for each quiz, and each users can answer questions with instant result updates Django APIs. The application also features user authentication to create quiz via API.

# Features
1.Topic-Based Quizzes: Admins or users can create quizzes on different topics , and any user will be able to participate in a quiz which he not created.

2.Instant Result Update: Users receive instant result updates with the help Django APIs.

3.User Authentication: Secure jwt authentication for a personalized experience.

4.Scoring System: Each question in a quiz is assigned points, providing users with a leaderboard system.

# Installation
To run this project locally for development purposes, follow these steps:

1.Clone the repository to your local machine:
git clone https://github.com/rajatrawal/quiz-app-django.git

2.Navigate to the project directory:
cd quiz-app-django

3.Install dependencies:
pip install -r requirements.txt

4.Run migrations:
python manage.py migrate

5.Create a superuser for admin access:
python manage.py createsuperuser

6.Start the development server:
python manage.py runserver

7.Open your web browser and explore the project locally at http://localhost:8000/.

