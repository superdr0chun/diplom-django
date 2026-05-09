from rest_framework import serializers
from .models import CustomUser, Test, Question, Answer, Result, UserAnswer


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})

    class Meta:
        model = CustomUser
        fields = ('id', 'username', 'email', 'password', 'role')

    def create(self, validated_data):
        user = CustomUser.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            role=validated_data.get('role', 'student')
        )
        return user


class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ('id', 'text', 'is_correct')


class AnswerPublicSerializer(serializers.ModelSerializer):
    """Для студентов — без is_correct"""
    class Meta:
        model = Answer
        fields = ('id', 'text')


class QuestionSerializer(serializers.ModelSerializer):
    answers = AnswerSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = ('id', 'text', 'question_type', 'points', 'order', 'answers')


class QuestionPublicSerializer(serializers.ModelSerializer):
    """Для студентов — ответы без is_correct"""
    answers = AnswerPublicSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = ('id', 'text', 'question_type', 'points', 'order', 'answers')


class TestListSerializer(serializers.ModelSerializer):
    """Краткая инфа для списка тестов"""
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    questions_count = serializers.IntegerField(source='questions.count', read_only=True)

    class Meta:
        model = Test
        fields = ('id', 'title', 'description', 'subject', 'time_limit',
                  'attempts_allowed', 'created_by_username', 'questions_count', 'is_published')


class TestDetailSerializer(serializers.ModelSerializer):
    """Полная инфа с вопросами — для преподавателя"""
    questions = QuestionSerializer(many=True, read_only=True)
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)

    class Meta:
        model = Test
        fields = ('id', 'title', 'description', 'subject', 'time_limit', 'attempts_allowed',
                  'shuffle_questions', 'shuffle_answers', 'created_by_username',
                  'questions', 'is_published', 'created_at')


class TestPublicSerializer(serializers.ModelSerializer):
    """Для студентов — вопросы без правильных ответов"""
    questions = QuestionPublicSerializer(many=True, read_only=True)

    class Meta:
        model = Test
        fields = ('id', 'title', 'description', 'subject', 'time_limit',
                  'attempts_allowed', 'shuffle_questions', 'shuffle_answers', 'questions')


class UserAnswerSubmitSerializer(serializers.Serializer):
    question_id = serializers.IntegerField()
    selected_answer_ids = serializers.ListField(
        child=serializers.IntegerField(), required=False, default=list
    )
    text_answer = serializers.CharField(required=False, allow_blank=True, default='')


class TestSubmitSerializer(serializers.Serializer):
    result_id = serializers.IntegerField()
    answers = UserAnswerSubmitSerializer(many=True)
    tab_switches = serializers.IntegerField(required=False, default=0)

class ResultSerializer(serializers.ModelSerializer):
    test_title = serializers.CharField(source='test.title', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    grade = serializers.SerializerMethodField()

    class Meta:
        model = Result
        fields = ('id', 'username', 'test_title', 'score', 'max_score',
                  'grade', 'started_at', 'finished_at', 'is_completed', 'tab_switches')

    def get_grade(self, obj):
        return obj.grade()