from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)
from quiz_app import views

router = DefaultRouter()

urlpatterns = [

    path('admin/', admin.site.urls),

    path('auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/token/verify/', TokenVerifyView.as_view(), name='token_verify'),

    path('api/', include(router.urls)), 

    path('api/quiz/<int:pk>/', views.QuizDetailView.as_view(), name='quiz-detail'),
    path('api/quiz/<int:quiz_id>/attempt/', views.QuizAttemptListView.as_view(), name='quiz-attempt-list'),
    
    path('api/quiz/create/', views.QuizCreateView.as_view(), name='quiz-create'),
    
    path('api/quiz/attempt/', views.QuizAttemptCRUDView.as_view(), name='quiz-attempt-create'), 
    path('api/quiz/attempt/<int:attempt_id>/', views.QuizAttemptCRUDView.as_view(), name='quiz-attempt-crud'),  

]
