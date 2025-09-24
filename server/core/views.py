import time
from django.http import JsonResponse, HttpResponse
from django.conf import settings


def healthz(request):
	return HttpResponse("ok")


def about_json(request):
	data = {
		"client": {"host": getattr(settings, "CLIENT_HOST", "localhost:8081")},
		"server": {
			"current_time": int(time.time()),
			"services": [],
		},
	}
	return JsonResponse(data)
