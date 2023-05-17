from django.http import JsonResponse

from .models import Presentation

from common.json import ModelEncoder

from django.views.decorators.http import require_http_methods

import json

from events.api_views import Conference

from events.api_views import ConferenceListEncoder
import pika


@require_http_methods(["GET", "POST"])
def api_list_presentations(request, conference_id):
    """
    Lists the presentation titles and the link to the
    presentation for the specified conference id.

    Returns a dictionary with a single key "presentations"
    which is a list of presentation titles and URLS. Each
    entry in the list is a dictionary that contains the
    title of the presentation, the name of its status, and
    the link to the presentation's information.

    {
        "presentations": [
            {
                "title": presentation's title,
                "status": presentation's status name
                "href": URL to the presentation,
            },
            ...
        ]
    }
    """
    if request.method == "GET":
        presentations = [
            {
                "title": p.title,
                "status": p.status.name,
                "href": p.get_api_url(),
            }
            for p in Presentation.objects.filter(conference=conference_id)
        ]
        return JsonResponse({"presentations": presentations})
    else:
        content = json.loads(request.body)
        try:
            conference = Conference.objects.get(id=conference_id)
            content["conference"] = conference
        except Conference.DoesNotExist:
            return JsonResponse(
                {"message": "Invalid conference id"}, status=400
            )
        presentation = Presentation.create(**content)
        return JsonResponse(presentation, PresentationDetailEncoder, False)


class PresentationDetailEncoder(ModelEncoder):
    model = Presentation
    properties = [
        "presenter_name",
        "company_name",
        "presenter_email",
        "title",
        "synopsis",
        "conference",
    ]
    encoders = {
        "conference": ConferenceListEncoder(),
    }

    def get_extra_data(self, o):
        return {"status": o.status.name}


@require_http_methods(["PUT", "DELETE", "GET"])
def api_show_presentation(request, id):
    """
    Returns the details for the Presentation model specified
    by the id parameter.

    This should return a dictionary with the presenter's name,
    their company name, the presenter's email, the title of
    the presentation, the synopsis of the presentation, when
    the presentation record was created, its status name, and
    a dictionary that has the conference name and its URL

    {
        "presenter_name": the name of the presenter,
        "company_name": the name of the presenter's company,
        "presenter_email": the email address of the presenter,
        "title": the title of the presentation,
        "synopsis": the synopsis for the presentation,
        "created": the date/time when the record was created,
        "status": the name of the status for the presentation,
        "conference": {
            "name": the name of the conference,
            "href": the URL to the conference,
        }
    }
    """
    if request.method == "GET":
        presentation = Presentation.objects.get(id=id)

        return JsonResponse(presentation, PresentationDetailEncoder, False)
    elif request.method == "DELETE":
        count, _ = Presentation.objects.filter(id=id).delete()
        return JsonResponse({"deleted": count > 0})
    else:
        content = json.loads(request.body)
        # try:
        #     if "conference" in content:
        #         conference = Conference.objects.get(content["conference"])
        #         content["conference"] = conference
        # except Conference.DoesNotExist:
        #     return JsonResponse(
        #         {"message": "No conference exists"}, status=400
        #     )
        Presentation.objects.filter(id=id).update(**content)
        presentation = Presentation.objects.get(id=id)
        return JsonResponse(presentation, PresentationDetailEncoder, False)

# @require_http_methods(['PUT'])
# def api_approve_presentation(request, id):
#     presentation = Presentation.objects.get(id=id)
#     d = {"presenter_name": presentation.presenter_name,
#          "presenter_email": presentation.presenter_email,
#          "title": presentation.title}
#     parameters = pika.ConnectionParameters(host='rabbitmq')

#     connection = pika.BlockingConnection(parameters)

#     channel = connection.channel()

#     channel.queue_declare(queue='presentation_approvals')

#     content = json.dumps(d)

#     channel.basic_publish(exchange='', routing_key='presentation_approvals', body=content)
#     presentation.approve()
#     connection.close()
#     return JsonResponse(
#         presentation,
#         encoder = PresentationDetailEncoder,
#         safe = False,
#     )

# @require_http_methods(["PUT"])
# def api_reject_presentation(request, id):
#     presentation = Presentation.objects.get(id=id)

#     parameters = pika.ConnectionParameters(host='rabbitmq')

#     connection = pika.BlockingConnection(parameters)

#     channel = connection.channel()

#     channel.queue_declare(queue='presentation_rejections')

#     d = {"presenter_name": presentation.presenter_name,
#          "presenter_email": presentation.presenter_email,
#          "title": presentation.title}

#     content = json.dumps(d)

#     channel.basic_publish(exchange='', routing_key='presentation_rejections', body=content)
#     presentation.reject()
#     connection.close()
#     return JsonResponse(
#         presentation,
#         PresentationDetailEncoder,
#         False
#     )

@require_http_methods(["PUT"])
def api_approve_presentation(request, id):
    presentation = Presentation.objects.get(id=id)
    presentation.approve()
    new_dict = {
        "presenter_name": presentation.presenter_name,
        "presenter_email": presentation.presenter_email,
        "title": presentation.title,
    }
    message = json.dumps(new_dict)

    parameters = pika.ConnectionParameters(host="rabbitmq")
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()
    channel.queue_declare(queue="presentation_approvals")
    channel.basic_publish(
        exchange="",
        routing_key="presentation_approvals",
        body=message
    )
    connection.close()
    return JsonResponse(
        presentation,
        encoder=PresentationDetailEncoder,
        safe=False,)



@require_http_methods(["PUT"])
def api_reject_presentation(request, id):
    presentation = Presentation.objects.get(id=id)
    presentation.reject()
    new_dict = {
        "presenter_name": presentation.presenter_name,
        "presenter_email": presentation.presenter_email,
        "title": presentation.title,
    }
    message = json.dumps(new_dict)

    parameters = pika.ConnectionParameters(host="rabbitmq")
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()
    channel.queue_declare(queue="presentation_rejections")
    channel.basic_publish(
        exchange="",
        routing_key="presentation_rejections",
        body=message
    )
    presentation = Presentation.objects.get(id=id)
    presentation.reject()
    return JsonResponse(
        presentation,
        encoder=PresentationDetailEncoder,
        safe=False,
    )
