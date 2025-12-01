import time
from django.utils.deprecation import MiddlewareMixin
from core.monitoring import log_kpi

class PerformanceMiddleware(MiddlewareMixin):
    def process_request(self, request):
        request.start_time = time.time()

    def process_response(self, request, response):
        duration = time.time() - getattr(request, 'start_time', time.time())
        response['X-Process-Time'] = f"{duration:.3f}s"
        print(f"Requête {request.path} traitée en {duration:.3f}s")
        return response
    
    def process_response(self, request, response):
        duration = time.time() - getattr(request, 'start_time', time.time())
        response['X-Process-Time'] = f"{duration:.3f}s"
        log_kpi(request, response)
        return response