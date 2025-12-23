from django.shortcuts import render
from django.urls import reverse_lazy
from . import models
from django.views import generic
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Count, Avg
from django.conf import settings
from django.core.mail import send_mail



# Create your views here.
def index(request):
    return render(request, 'index.html')

def about(request):
    return render(request, 'about.html')

def destinations(request):
    all_destinations = (
        models.Destination.objects
        .annotate(
            review_count=Count('reviews'),
            avg_rating=Avg('reviews__rating')
        )
        .order_by('-review_count', '-avg_rating')
    )

    return render(request, 'destinations.html', {
        'destinations': all_destinations
    })


class DestinationDetailView(generic.DetailView):
    template_name = 'destination_detail.html'
    model = models.Destination
    context_object_name = 'destination'

class CruiseDetailView(generic.DetailView):
    template_name = 'cruise_detail.html'
    model = models.Cruise
    context_object_name = 'cruise'

class InfoRequestCreate(SuccessMessageMixin, generic.CreateView):
    template_name = 'info_request_create.html'
    model = models.InfoRequest
    fields = ['name', 'email', 'cruise', 'notes']
    success_url = reverse_lazy('index')
    success_message = 'Thank you, %(name)s! We will email you when we have more information about %(cruise)s!'

    def form_valid(self, form):
        response = super().form_valid(form)

        # Enviar el correo usando la instancia guardada
        info_request = form.instance
        send_mail(
            subject=f'Solicitud de información recibida: {info_request.cruise}',
            message=(
                f'Hola {info_request.name},\n\n'
                f'Hemos recibido tu solicitud para obtener más información sobre el crucero "{info_request.cruise}". '
                f'Nos pondremos en contacto contigo pronto.\n\n'
                f'Mensaje adicional: {info_request.notes}'
            ),
            from_email='relecloudgdv@gmail.com',
            recipient_list=[info_request.email],
            fail_silently=False,
        )
        return response
