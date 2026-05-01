from rest_framework import generics, mixins, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Todo
from .serializers import TodoSerializer, UserSerializer
from django.contrib.auth.models import User

# ============ ЧАСТЬ 1: РАЗБИРАЕМ GENERICS НА ПРАКТИКЕ ============

"""
🎓 GenericAPIView - это "основа", которая предоставляет:
   - queryset (набор данных)
   - serializer_class (как преобразовывать данные)
   - методы get_object(), get_queryset() и т.д.

🎓 Mixins - это "кирпичики" с конкретными действиями:
   - CreateModelMixin → метод create() для POST
   - ListModelMixin    → метод list() для GET (список)
   - RetrieveModelMixin→ метод retrieve() для GET (один объект)
   - UpdateModelMixin  → метод update() для PUT/PATCH
   - DestroyModelMixin → метод destroy() для DELETE
"""

# ПРИМЕР 1: Ручная сборка из Mixins + GenericAPIView
# Почему так? Когда нужно ТОЛЬКО создавать и получать список, без обновления/удаления
class TodoListCreateManual(mixins.ListModelMixin,      # Кирпичик для списка
                            mixins.CreateModelMixin,    # Кирпичик для создания
                            generics.GenericAPIView):   # Основа
    
    queryset = Todo.objects.all()
    serializer_class = TodoSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # 🔑 Фильтруем задачи только текущего пользователя
        return self.queryset.filter(user=self.request.user)
    
    # 📍 Вручную привязываем HTTP методы к нашим миксинам
    def get(self, request, *args, **kwargs):
        # list() - это метод из ListModelMixin
        return self.list(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        # create() - это метод из CreateModelMixin
        # Переопределяем, чтобы автоматически подставить пользователя
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)  # 🎯 Подставляем авторизованного пользователя
        return Response(serializer.data, status=status.HTTP_201_CREATED)


# ПРИМЕР 2: Готовая Generic View (проще и короче!)
# Почему так? Это ДЛЯ 90% СЛУЧАЕВ - стандартный CRUD
class TodoListCreate(generics.ListCreateAPIView):
    """
    ListCreateAPIView = GenericAPIView + ListModelMixin + CreateModelMixin
    ✅ Уже готовые GET и POST методы!
    ✅ Автоматическая пагинация
    ✅ Автоматическая фильтрация
    """
    serializer_class = TodoSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # Переопределяем, чтобы показывать только задачи пользователя
        return Todo.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        # perform_create - специальный хук для создания объекта
        serializer.save(user=self.request.user)


# ПРИМЕР 3: Работа с отдельным объектом (UPDATE/DELETE)
class TodoDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    RetrieveUpdateDestroyAPIView = GenericAPIView + 
                                   RetrieveModelMixin + 
                                   UpdateModelMixin + 
                                   DestroyModelMixin
    ✅ GET /todos/1/     - получить задачу
    ✅ PUT /todos/1/     - полностью обновить
    ✅ PATCH /todos/1/   - частично обновить  
    ✅ DELETE /todos/1/  - удалить
    """
    serializer_class = TodoSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # Пользователь может работать ТОЛЬКО со своими задачами
        return Todo.objects.filter(user=self.request.user)


# ============ ЧАСТЬ 2: MIXINS ДЛЯ НЕСТАНДАРТНЫХ СЦЕНАРИЕВ ============

# ПРИМЕР 4: Сборка своей уникальной комбинации
# Нам нужен ТОЛЬКО список и обновление, но БЕЗ создания и удаления
class TodoListUpdateOnly(mixins.ListModelMixin,      # Только список
                          mixins.UpdateModelMixin,    # Только обновление
                          generics.GenericAPIView):
    """
    ❌ Нет create (POST)
    ❌ Нет destroy (DELETE)
    ✅ GET /todos/ - список
    ✅ PUT /todos/<id>/ - обновление конкретной задачи
    """
    queryset = Todo.objects.all()
    serializer_class = TodoSerializer
    permission_classes = [IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
    
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)


# ПРИМЕР 5: Кастомный миксин для архивации (создаем СВОЙ кирпичик!)
class ArchiveModelMixin:
    """
    🏗️ Создаем свой миксин для нестандартного действия!
    Теперь его можно переиспользовать в любых вьюхах
    """
    def archive(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.completed = True
        instance.save()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class TodoArchiveView(ArchiveModelMixin,           # Наш кастомный миксин 🎨
                      generics.GenericAPIView):
    """
    Теперь у нас есть эндпоинт для архивации задачи!
    POST /todos/archive/1/
    """
    queryset = Todo.objects.all()
    serializer_class = TodoSerializer
    permission_classes = [IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        return self.archive(request, *args, **kwargs)


# ============ ЧАСТЬ 3: АУТЕНТИФИКАЦИЯ С SIMPLEJWT ============

# ПРИМЕР 6: Кастомизация JWT (добавляем данные пользователя)
class CustomTokenObtainPairView(TokenObtainPairView):
    """
    📌 SimpleJWT использует те же принципы, что и DRF!
    TokenObtainPairView - это Generic View, который внутри себя использует:
    - GenericAPIView как основу
    - Свой внутренний сериализатор (TokenObtainPairSerializer)
    
    Мы просто переопределяем сериализатор, чтобы добавить данные пользователя
    """
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        
        # Добавляем данные пользователя в ответ к токенам
        if response.status_code == 200:
            user = User.objects.get(username=request.data.get('username'))
            response.data['user_id'] = user.id
            response.data['username'] = user.username
            response.data['email'] = user.email
        
        return response


# ПРИМЕР 7: Регистрация с автоматическим созданием токенов
class RegisterView(APIView):
    """
    APIView - полный контроль, но больше кода.
    Здесь нет миксинов, так как логика нестандартная
    """
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Создаем JWT токены для нового пользователя
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'user': serializer.data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, status=status.HTTP_201_CREATED)


# ПРИМЕР 8: Профиль пользователя с использованим mixins
class UserTodoStatsView(mixins.RetrieveModelMixin,
                         generics.GenericAPIView):
    """
    Статистика: сколько задач у пользователя
    Используем только один миксин - RetrieveModelMixin
    """
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        user = request.user
        total_todos = Todo.objects.filter(user=user).count()
        completed_todos = Todo.objects.filter(user=user, completed=True).count()
        
        return Response({
            'username': user.username,
            'total_tasks': total_todos,
            'completed_tasks': completed_todos,
            'completion_rate': f"{(completed_todos/total_todos*100):.1f}%" if total_todos > 0 else "0%"
        })
