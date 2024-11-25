from django.urls import path, include
from django.contrib import admin
from rest_framework.routers import DefaultRouter
from quiz_app import views
from rest_framework_simplejwt.views import TokenObtainPairView , TokenRefreshView , TokenVerifyView

router = DefaultRouter()

urlpatterns = [

    path('', include(router.urls), ),
    path('admin/',admin.site.urls, ),

    path('gettoken/', TokenObtainPairView.as_view(), name='token_obtain_pair', ),
    path('refreshtoken/', TokenRefreshView.as_view(), name='token_refresh', ),
    path('verifytoken/', TokenVerifyView.as_view(), name='token_verify', ),
    
    path('api/quiz/<int:pk>/', views.QuizDetailView.as_view(), name='quiz-detail', ),
    path('api/quiz/<int:quiz_id>/attempt/', views.QuizAttemptListView.as_view(), name='quiz-attempt', ),
    path('api/quiz/create/', views.QuizCreateView.as_view(), name='quiz-create', ),

]
