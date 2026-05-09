from django.contrib.auth import authenticate, login as auth_login
from django.utils import timezone
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
import random

from .serializers import (
    UserSerializer, TestListSerializer, TestDetailSerializer,
    TestPublicSerializer, TestSubmitSerializer, ResultSerializer
)
from .models import CustomUser, Test, Question, Answer, Result, UserAnswer


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


# ─── АУТЕНТИФИКАЦИЯ ────────────────────────────────────────────────────────────

@api_view(['POST'])
@authentication_classes([])
@permission_classes([])
def register(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        return Response({
            'success': True,
            'message': 'Регистрация прошла успешно!',
            'user_id': user.id,
            'username': user.username,
            'role': user.role,
        }, status=status.HTTP_201_CREATED)
    return Response({
        'success': False,
        'error': 'Ошибка регистрации',
        'details': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@authentication_classes([])
@permission_classes([])
def login(request):
    username = request.data.get('username')
    password = request.data.get('password')

    if not username or not password:
        return Response({
            'success': False,
            'error': 'Введите логин и пароль'
        }, status=status.HTTP_400_BAD_REQUEST)

    user = authenticate(username=username, password=password)

    if user is not None:
        tokens = get_tokens_for_user(user)
        return Response({
            'success': True,
            'message': 'Авторизация успешна',
            'user_id': user.id,
            'username': user.username,
            'role': user.role,
            'access': tokens['access'],
            'refresh': tokens['refresh'],
        }, status=status.HTTP_200_OK)

    return Response({
        'success': False,
        'error': 'Неверный логин или пароль'
    }, status=status.HTTP_401_UNAUTHORIZED)


# ─── ТЕСТЫ ─────────────────────────────────────────────────────────────────────

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def test_list(request):
    """Список тестов. Студент видит только опубликованные, препод — свои."""
    user = request.user
    if user.role == 'student':
        tests = Test.objects.filter(is_published=True)
    elif user.role == 'teacher':
        tests = Test.objects.filter(created_by=user)
    else:  # admin
        tests = Test.objects.all()

    serializer = TestListSerializer(tests, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def test_detail(request, test_id):
    """Детали теста. Студент получает версию без правильных ответов."""
    try:
        test = Test.objects.get(id=test_id)
    except Test.DoesNotExist:
        return Response({'error': 'Тест не найден'}, status=status.HTTP_404_NOT_FOUND)

    user = request.user
    if user.role == 'student':
        if not test.is_published:
            return Response({'error': 'Тест недоступен'}, status=status.HTTP_403_FORBIDDEN)
        serializer = TestPublicSerializer(test)
    else:
        serializer = TestDetailSerializer(test)

    return Response(serializer.data)


# ─── ПРОХОЖДЕНИЕ ТЕСТА ─────────────────────────────────────────────────────────

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def test_start(request, test_id):
    """Начать тест — создаёт запись Result и возвращает вопросы."""
    try:
        test = Test.objects.get(id=test_id, is_published=True)
    except Test.DoesNotExist:
        return Response({'error': 'Тест не найден'}, status=status.HTTP_404_NOT_FOUND)

    user = request.user

    # Проверка количества попыток
    attempts_used = Result.objects.filter(
        user=user, test=test, is_completed=True
    ).count()

    if test.attempts_allowed > 0 and attempts_used >= test.attempts_allowed:
        return Response({
            'error': f'Исчерпано количество попыток ({test.attempts_allowed})'
        }, status=status.HTTP_403_FORBIDDEN)

    # Создаём Result
    result = Result.objects.create(
        user=user,
        test=test,
        max_score=sum(q.points for q in test.questions.all())
    )

    # Получаем вопросы
    questions = list(test.questions.all())
    if test.shuffle_questions:
        random.shuffle(questions)

    serializer = TestPublicSerializer(test)
    data = serializer.data

    # Перемешиваем ответы если нужно
    questions_data = []
    for q in questions:
        answers = list(q.answers.all())
        if test.shuffle_answers:
            random.shuffle(answers)
        questions_data.append({
            'id': q.id,
            'text': q.text,
            'question_type': q.question_type,
            'points': q.points,
            'answers': [{'id': a.id, 'text': a.text} for a in answers]
        })

    return Response({
        'result_id': result.id,
        'test_id': test.id,
        'title': test.title,
        'time_limit': test.time_limit,
        'questions': questions_data,
    }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def test_submit(request):
    """Отправить ответы и получить результат."""
    serializer = TestSubmitSerializer(data=request.data)
    if not serializer.is_valid():
        return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    result_id = serializer.validated_data['result_id']
    answers_data = serializer.validated_data['answers']
    tab_switches = serializer.validated_data.get('tab_switches', 0)
    try:
        result = Result.objects.get(id=result_id, user=request.user, is_completed=False)
    except Result.DoesNotExist:
        return Response({'error': 'Результат не найден'}, status=status.HTTP_404_NOT_FOUND)

    total_score = 0

    for answer_data in answers_data:
        try:
            question = Question.objects.get(id=answer_data['question_id'])
        except Question.DoesNotExist:
            continue

        user_answer = UserAnswer.objects.create(
            result=result,
            question=question,
            text_answer=answer_data.get('text_answer', '')
        )

        selected_ids = answer_data.get('selected_answer_ids', [])
        if selected_ids:
            selected = Answer.objects.filter(id__in=selected_ids)
            user_answer.selected_answers.set(selected)

        # Автопроверка для закрытых вопросов
        if question.question_type in ('single', 'multiple'):
            correct_ids = set(
                question.answers.filter(is_correct=True).values_list('id', flat=True)
            )
            if set(selected_ids) == correct_ids:
                user_answer.is_correct = True
                total_score += question.points
            else:
                user_answer.is_correct = False
        else:
            # Открытый вопрос — на ручную проверку
            user_answer.is_correct = None

        user_answer.save()

    result.score = total_score
    result.finished_at = timezone.now()
    result.is_completed = True
    result.tab_switches = tab_switches
    result.save()

    return Response({
        'success': True,
        'result_id': result.id,
        'score': result.score,
        'max_score': result.max_score,
        'grade': result.grade(),
        'percent': round((result.score / result.max_score * 100) if result.max_score > 0 else 0, 1),
    }, status=status.HTTP_200_OK)


# ─── РЕЗУЛЬТАТЫ ────────────────────────────────────────────────────────────────

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def results(request):
    """Студент видит свои результаты, препод — результаты по своим тестам."""
    user = request.user
    if user.role == 'student':
        qs = Result.objects.filter(user=user, is_completed=True).select_related('test', 'user')
    elif user.role == 'teacher':
        qs = Result.objects.filter(
            test__created_by=user, is_completed=True
        ).select_related('test', 'user')
    else:
        qs = Result.objects.filter(is_completed=True).select_related('test', 'user')

    serializer = ResultSerializer(qs, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def result_detail(request, result_id):
    """Детали результата — список вопросов и ответов студента."""
    try:
        result = Result.objects.select_related('test', 'user').get(id=result_id)
    except Result.DoesNotExist:
        return Response({'error': 'Результат не найден'}, status=status.HTTP_404_NOT_FOUND)

    # Препод может видеть только результаты своих тестов
    if request.user.role == 'teacher' and result.test.created_by != request.user:
        return Response({'error': 'Нет доступа'}, status=status.HTTP_403_FORBIDDEN)
    # Студент — только свои
    if request.user.role == 'student' and result.user != request.user:
        return Response({'error': 'Нет доступа'}, status=status.HTTP_403_FORBIDDEN)

    user_answers_data = []
    for ua in result.user_answers.select_related('question').prefetch_related('selected_answers', 'question__answers'):
        user_answers_data.append({
            'id': ua.id,
            'question_id': ua.question.id,
            'question_text': ua.question.text,
            'question_type': ua.question.question_type,
            'points': ua.question.points,
            'all_answers': [
                {'id': a.id, 'text': a.text, 'is_correct': a.is_correct}
                for a in ua.question.answers.all()
            ],
            'selected_answer_ids': list(ua.selected_answers.values_list('id', flat=True)),
            'text_answer': ua.text_answer,
            'is_correct': ua.is_correct,
        })

    return Response({
        'id': result.id,
        'username': result.user.username,
        'test_title': result.test.title,
        'score': result.score,
        'max_score': result.max_score,
        'grade': result.grade(),
        'finished_at': result.finished_at,
        'answers': user_answers_data,
    })