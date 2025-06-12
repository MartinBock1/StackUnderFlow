from rest_framework.throttling import UserRateThrottle


class QuestionThrottle(UserRateThrottle):
    scope = 'question'