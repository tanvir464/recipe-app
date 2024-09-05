from django.urls import path
from . import views

urlpatterns = [
    path('login_user', views.login_user, name="login"),
    path('logout_user',views.logout_user, name="logout"),
    path('signup/', views.signup_user, name='signup'),
    path('verify_otp/', views.verify_otp, name='verify_otp'),
    path('forgot_password/', views.forgot_password, name='forgot_password'),
    path('verify_reset-otp/', views.verify_reset_otp, name='verify_reset_otp'),
    path('reset_password/', views.reset_password, name='reset_password'),
    path('edit_profile', views.edit_profile, name='edit_profile'),
    path('change_password/', views.change_password, name='change_password'),
    path('myprofile/', views.profile, name='myprofile'),
    path('profile/<str:username>/', views.user_profile, name='user_profile'),
    path('profile/<str:username>/follow/', views.follow_user, name='follow_user'),
    path('user/<str:username>/recipes/', views.user_uploaded_recipes, name='user_uploaded_recipes'),
    path('user/<str:username>/followers/', views.user_followers, name='user_followers'),
    path('user/<str:username>/followings/', views.user_followings, name='user_followings'),
]