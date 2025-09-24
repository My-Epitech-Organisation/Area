import time
import uuid
from django.http import JsonResponse, HttpResponse, HttpResponseNotAllowed, Http404
from django.conf import settings


def healthz(request):
	return HttpResponse("ok")


def about_json(request):
	services = [
		{
			"name": "github",
			"actions": [
				{"name": "new_issue", "description": "Triggered when a new issue is created"},
				{"name": "new_pr", "description": "Triggered when a pull request is opened"},
			],
			"reactions": [
				{"name": "create_comment", "description": "Post a comment on an issue or PR"},
				{"name": "add_label", "description": "Add a label to an issue"},
			],
		},
		{
			"name": "timer",
			"actions": [
				{"name": "every_minute", "description": "Tick every minute"},
				{"name": "every_hour", "description": "Tick every hour"},
			],
			"reactions": [
				{"name": "send_email", "description": "Send an email notification"},
				{"name": "log_message", "description": "Write a log entry"},
			],
		},
	]

	data = {
		"client": {"host": getattr(settings, "CLIENT_HOST", "localhost:8081")},
		"server": {
			"current_time": int(time.time()),
			"services": services,
		},
	}
	return JsonResponse(data)


# --- Fake AREAs API (static, no persistence) ---

FAKE_AREAS = [
	{
		"id": "11111111-1111-1111-1111-111111111111",
		"name": "Notify on new GitHub issue",
		"service": "github",
		"action": "new_issue",
		"reactions": ["create_comment"],
	},
	{
		"id": "22222222-2222-2222-2222-222222222222",
		"name": "Hourly log",
		"service": "timer",
		"action": "every_hour",
		"reactions": ["log_message"],
	},
]


def areas_list(request):
	if request.method != "GET":
		return HttpResponseNotAllowed(["GET"])
	return JsonResponse(FAKE_AREAS, safe=False)


def area_detail(request, area_id: uuid.UUID):
	if request.method != "GET":
		return HttpResponseNotAllowed(["GET"])
	s = str(area_id)
	for a in FAKE_AREAS:
		if a["id"] == s:
			return JsonResponse(a)
	raise Http404("Area not found")


def area_simulate(request, area_id: uuid.UUID):
	if request.method != "POST":
		return HttpResponseNotAllowed(["POST"])
	s = str(area_id)
	area = next((a for a in FAKE_AREAS if a["id"] == s), None)
	if not area:
		raise Http404("Area not found")
	result = {
		"status": "ok",
		"message": f"Simulated: action '{area['action']}' would trigger reactions {area['reactions']}",
		"area": area,
		"at": int(time.time()),
	}
	return JsonResponse(result)
