import random
import string
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse
from .forms import EvaluationForm
from .models import WebsiteEvaluation,Post
from .models import *
from django.core.urlresolvers import reverse
from django.utils import formats, timezone
from sets import Set
from .tables import WebsiteEvaluationTable
from django_tables2   import RequestConfig
from django.views.generic.base import TemplateView

# Create your views here.


class SuccessView(TemplateView):
    template_name="success.html"

    def get_context_data(self, **kwargs):
        pass


def survey_view(request):
    #sets the expiry date of a session in future
    request.session.set_expiry(timezone.now() + datetime.timedelta(days=365))
    if request.session._session_key:
        USER_ID = request.session._session_key
    else:
        USER_ID = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(32))

    print(request.session.get_expiry_age())
    if request.method == 'POST':
       form = EvaluationForm(request.POST)
       if form.is_valid():
               p,created = Post.objects.get_or_create(url=request.POST['url'])
               p.save()
               evaluation,created = WebsiteEvaluation.objects.get_or_create(user_id=USER_ID, post_url=p,
                                                    time_constraint = form.cleaned_data['time_constraint'],
                                                    answer_validity = form.cleaned_data['answer_validity'],
                                                    generality_applicability=form.cleaned_data['generality_applicability'],
                                                    location_constraint=form.cleaned_data['location_constraint'],
                                                    degree_knowledge=form.cleaned_data['degree_knowledge'],
                                                    costs_parameters=form.cleaned_data['costs_parameters'],
                                                    info_provider_layman=form.cleaned_data['info_provider_layman'],
                                                    info_provider_operator=form.cleaned_data['info_provider_operator'],
                                                    info_provider_expert=form.cleaned_data['info_provider_expert'],
                                                    mobile_context=form.cleaned_data['mobile_context'],
                                                    spatial_coordinates=form.cleaned_data['spatial_coordinates'],
                                                    ask_questions=form.cleaned_data['ask_questions'],
                                                    suggestions=form.cleaned_data['suggestions'],
                                                    comment=form.cleaned_data['comment'],
                                                    personal_profile=form.cleaned_data['personal_profile'],
                                                    others_information_need=form.cleaned_data['others_information_need'],
                                                    contact_user=form.cleaned_data['contact_user']
                                                    )
               evaluation.save()
               return HttpResponseRedirect(reverse('success_view'))
    else:
        form = EvaluationForm()
    posts = [p for p in Post.objects.all()]
    #posts_evaluated = [p.post_url for p in WebsiteEvaluation.objects.filter(user_id=USER_ID)]
    posts_evaluated = [p.post_url for p in WebsiteEvaluation.objects.all()]
    print posts
    print posts_evaluated
    posts_random = list(Set(posts).difference(Set(posts_evaluated)))
    print(len(posts_random))
    if len(posts_random) == 0:
        return HttpResponseRedirect(reverse('evaluation_complete_view'))
    else:
        url = random.choice(posts_random)
        return render(request, 'survey_form.html', {'form': form, 'url': url})


class StatisticsView(TemplateView):
    template_name = "statistics.html"

    def get_context_data(self, **kwargs):
        objects = set([w.post_url for w in WebsiteEvaluation.objects.all()])
        evaluation_table = WebsiteEvaluationTable(objects)
        RequestConfig(self.request).configure(evaluation_table)
        return {'evaluation_table': evaluation_table}


class EvaluationCompleteView(TemplateView):
    template_name = "evaluation_complete.html"

    def get_context_data(self, **kwargs):
        pass