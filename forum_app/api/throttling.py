from rest_framework.throttling import UserRateThrottle


class QuestionThrottle(UserRateThrottle):
    scope = 'question'
    
    def allow_request(self, request, view):
        
        if request.method == "GET":
            return True
        
        return super().allow_request(request, view)