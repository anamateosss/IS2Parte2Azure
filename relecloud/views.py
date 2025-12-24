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
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Avg

logger = logging.getLogger(__name__)

# Página principal
def index(request):
    return render(request, 'index.html')

# Página "About"
def about(request):
    return render(request, 'about.html')

# Página de destinos 
def destinations(request):
    all_destinations = (
        models.Destination.objects
        .annotate(
            review_count=Count('reviews', distinct=True),
            avg_rating=Avg('reviews__rating'),
        )
        .order_by('-review_count', '-avg_rating', 'name')
    )
    return render(request, 'destinations.html', {'destinations': all_destinations})

@login_required
def purchase_destination(request, pk):
    dest = get_object_or_404(models.Destination, pk=pk)
    models.Purchase.objects.get_or_create(user=request.user, destination=dest)
    messages.success(request, f"Compra registrada para {dest.name}.")
    return redirect("destination_detail", pk=pk)


@login_required
def purchase_cruise(request, pk):
    cruise = get_object_or_404(models.Cruise, pk=pk)
    models.Purchase.objects.get_or_create(user=request.user, cruise=cruise)
    messages.success(request, f"Compra registrada para {cruise.name}.")
    return redirect("cruise_detail", pk=pk)

# Detalle de un destino
class DestinationDetailView(generic.DetailView):
    template_name = 'destination_detail.html'
    model = models.Destination
    context_object_name = 'destination'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        dest = self.object

        reviews_qs = dest.reviews.select_related("user").order_by("-created_at")
        context["reviews"] = reviews_qs
        context["avg_rating"] = reviews_qs.aggregate(avg=Avg("rating"))["avg"] or 0

        if self.request.user.is_authenticated:
            context["has_purchased"] = models.Purchase.objects.filter(
                user=self.request.user, destination=dest
            ).exists()
            context["already_reviewed"] = models.DestinationReview.objects.filter(
                user=self.request.user, destination=dest
            ).exists()
        else:
            context["has_purchased"] = False
            context["already_reviewed"] = False

        context["can_review"] = context["has_purchased"] and (not context["already_reviewed"])
        return context

# Detalle de un crucero
class CruiseDetailView(generic.DetailView):
    template_name = 'cruise_detail.html'
    model = models.Cruise
    context_object_name = 'cruise'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cruise = self.object

        reviews_qs = cruise.reviews.select_related("user").order_by("-created_at")
        context["reviews"] = reviews_qs
        context["avg_rating"] = reviews_qs.aggregate(avg=Avg("rating"))["avg"] or 0

        if self.request.user.is_authenticated:
            context["has_purchased"] = models.Purchase.objects.filter(
                user=self.request.user, cruise=cruise
            ).exists()
            context["already_reviewed"] = models.CruiseReview.objects.filter(
                user=self.request.user, cruise=cruise
            ).exists()
        else:
            context["has_purchased"] = False
            context["already_reviewed"] = False

        context["can_review"] = context["has_purchased"] and (not context["already_reviewed"])
        return context

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
        if not request.user.is_authenticated:
            return super().dispatch(request, *args, **kwargs)

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
        if not request.user.is_authenticated:
            return super().dispatch(request, *args, **kwargs)

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
