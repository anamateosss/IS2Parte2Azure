from django.shortcuts import render
from django.urls import reverse_lazy
from . import models
from django.views import generic
from django.contrib.messages.views import SuccessMessageMixin
from django.conf import settings
from django.core.mail import send_mail
import logging

logger = logging.getLogger(__name__)

# Página principal
def index(request):
    return render(request, 'index.html')

# Página "About"
def about(request):
    return render(request, 'about.html')

# Página de destinos (sin reviews, lista simple con imagen)
def destinations(request):
    all_destinations = models.Destination.objects.all().order_by('name')
    return render(request, 'destinations.html', {'destinations': all_destinations})

# Detalle de un destino
class DestinationDetailView(generic.DetailView):
    template_name = 'destination_detail.html'
    model = models.Destination
    context_object_name = 'destination'

# Detalle de un crucero
class CruiseDetailView(generic.DetailView):
    template_name = 'cruise_detail.html'
    model = models.Cruise
    context_object_name = 'cruise'

# Formulario de solicitud (mantiene envío de email)
class InfoRequestCreate(SuccessMessageMixin, generic.CreateView):
    template_name = 'info_request_create.html'
    model = models.InfoRequest
    fields = ['name', 'email', 'cruise', 'notes']
    success_url = reverse_lazy('index')
    success_message = 'Thank you, %(name)s! We will email you when we have more information about %(cruise)s!'

    def form_valid(self, form):
        response = super().form_valid(form)

        info_request = form.instance

        try:
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
        except Exception as e:
            logger.exception("Fallo enviando email")
            raise  

        return response
