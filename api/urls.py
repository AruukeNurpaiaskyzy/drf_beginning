from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView, TokenBlacklistView
from . import views 

urlpatterns = [
    path('token/', views.CustomTokenObtainPairView.as_view(), name='token_obtain'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/blacklist/', TokenBlacklistView.as_view(), name='token_blacklist'),
    path('register/', views.RegisterView.as_view(), name='register'),
    
    # 📝 Стандартные CRUD операции с Todo
    path('todos/', views.TodoListCreate.as_view(), name='todo-list'),
    path('todos/<int:pk>/', views.TodoDetail.as_view(), name='todo-detail'),
    
    # 🎨 Нестандартные эндпоинты (для демонстрации миксинов)
    path('todos/manual/', views.TodoListCreateManual.as_view(), name='todo-manual'),
    path('todos/archive/<int:pk>/', views.TodoArchiveView.as_view(), name='todo-archive'),
    path('todos/update-only/', views.TodoListUpdateOnly.as_view(), name='todo-update-only'),
    
    # 📊 Дополнительные эндпоинты
    path('user/stats/', views.UserTodoStatsView.as_view(), name='user-stats'),
]

