from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views, web_views

urlpatterns = [
    # API — аутентификация
    path('api/register/', views.register, name='register'),
    path('api/login/', views.login, name='login'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # API — тесты (submit ОБЯЗАТЕЛЬНО перед <int:test_id>)
    path('api/tests/submit/', views.test_submit, name='test_submit'),
    path('api/tests/', views.test_list, name='test_list'),
    path('api/tests/<int:test_id>/', views.test_detail, name='test_detail'),
    path('api/tests/<int:test_id>/start/', views.test_start, name='test_start'),

    # API — результаты
    path('api/results/', views.results, name='results'),
    path('api/results/<int:result_id>/', views.result_detail, name='result_detail'),

    # Веб — преподаватель
    path('web/login/', web_views.web_login, name='web_login'),
    path('web/logout/', web_views.web_logout, name='web_logout'),
    path('web/dashboard/', web_views.dashboard, name='dashboard'),
    path('web/tests/', web_views.test_list, name='web_test_list'),
    path('web/tests/create/', web_views.test_create, name='web_test_create'),
    path('web/tests/<int:test_id>/edit/', web_views.test_edit, name='web_test_edit'),
    path('web/tests/<int:test_id>/toggle/', web_views.test_toggle, name='web_test_toggle'),
    path('web/tests/<int:test_id>/delete/', web_views.test_delete, name='web_test_delete'),
    path('web/results/', web_views.results, name='web_results'),
    path('web/results/review/<int:result_id>/', web_views.result_review, name='web_result_review'),
    path('web/register/', web_views.web_register, name='web_register'),
    path('web/tests/<int:test_id>/stats/', web_views.test_statistics, name='web_test_stats'),
    path('web/results/export/', web_views.results_export, name='web_results_export'),
]