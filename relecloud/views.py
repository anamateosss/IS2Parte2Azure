from django.shortcuts import render
from django.urls import reverse_lazy
from . import models
from django.views import generic
from django.contrib.messages.views import SuccessMessageMixin
from django.conf import settings
from django.core.mail import send_mail
import logging
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse
from .forms import DestinationReviewForm, CruiseReviewForm

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

# Formulario de solicitud 
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

class DestinationReviewCreate(LoginRequiredMixin, SuccessMessageMixin, generic.CreateView):
    template_name = "review_form.html"
    model = models.DestinationReview
    form_class = DestinationReviewForm
    success_message = "¡Gracias! Tu opinión se ha guardado."

    def dispatch(self, request, *args, **kwargs):
        self.destination = get_object_or_404(models.Destination, pk=self.kwargs["pk"])
        has_purchased = models.Purchase.objects.filter(
            user=request.user, destination=self.destination
        ).exists()
        if not has_purchased:
            messages.error(request, "Debes haber comprado este destino para opinar.")
            return redirect("destination_detail", pk=self.destination.pk)
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.destination = self.destination
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("destination_detail", kwargs={"pk": self.destination.pk})

class CruiseReviewCreate(LoginRequiredMixin, SuccessMessageMixin, generic.CreateView):
    template_name = "review_form.html"
    model = models.CruiseReview
    form_class = CruiseReviewForm
    success_message = "¡Gracias! Tu opinión se ha guardado."

    def dispatch(self, request, *args, **kwargs):
        self.cruise = get_object_or_404(models.Cruise, pk=self.kwargs["pk"])
        has_purchased = models.Purchase.objects.filter(
            user=request.user, cruise=self.cruise
        ).exists()
        if not has_purchased:
            messages.error(request, "Debes haber comprado este crucero para opinar.")
            return redirect("cruise_detail", pk=self.cruise.pk)
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.cruise = self.cruise
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("cruise_detail", kwargs={"pk": self.cruise.pk})
