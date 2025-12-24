from django.test import TestCase, override_settings
from django.urls import reverse
from django.core import mail
from .models import Destination, Cruise, InfoRequest
from django.contrib.auth import get_user_model
from django.conf import settings
from .models import Purchase, DestinationReview, CruiseReview

# Usamos override_settings para que durante los tests NO intente enviar
# correos reales a Gmail, sino que los guarde en memoria para comprobarlos.
@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class InfoRequestTests(TestCase):
    def setUp(self):
        # Creamos datos de prueba necesarios (Destino y Crucero)
        self.dest = Destination.objects.create(
            name="Destino Test",
            description="Descripción test",
        )
        self.cruise = Cruise.objects.create(
            name="Crucero de Prueba",
            description="Descripción crucero",
        )
        self.cruise.destinations.add(self.dest)

    def test_form_valid_sends_email(self):
        # 1. Preparamos la URL y los datos del formulario
        url = reverse('info_request')
        data = {
            'name': 'Estudiante',
            'email': 'alumno@test.com',
            'cruise': self.cruise.id,
            'notes': 'Duda sobre el precio'
        }

        # 2. Hacemos el POST (enviamos el formulario)
        response = self.client.post(url, data)

        # 3. Verificaciones
        
        # A) Comprobar que se ha creado el objeto InfoRequest en la BBDD
        self.assertEqual(InfoRequest.objects.count(), 1)
        
        # B) Comprobar que se ha redirigido (Status 302)
        self.assertEqual(response.status_code, 302) 

        # C) Comprobar el envío de correo
        # mail.outbox es el buzón de salida en memoria de los tests
        self.assertEqual(len(mail.outbox), 1)
        
        # D) Comprobar el contenido EXACTO del correo 
        email_enviado = mail.outbox[0]
        
        self.assertIn('Solicitud de información recibida', email_enviado.subject)
        
        self.assertEqual(email_enviado.from_email, 'relecloudgdv@gmail.com')
        
        self.assertEqual(email_enviado.to, ['alumno@test.com'])
        
        # Verificamos parte del cuerpo del mensaje
        self.assertIn('Hola Estudiante', email_enviado.body)
        self.assertIn('Crucero de Prueba', email_enviado.body)

    def test_invalid_form_does_not_send_email(self):
        url = reverse('info_request')
        data = {
            'name': 'Estudiante',
            'email': '',  # inválido
            'cruise': self.cruise.id,
            'notes': 'Duda'
        }

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, 200)  # re-render form
        self.assertEqual(InfoRequest.objects.count(), 0)
        self.assertEqual(len(mail.outbox), 0)

class ReviewPT3Tests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="u1", password="pass12345")

        self.dest = Destination.objects.create(
            name="Destino PT3",
            description="Desc destino",
        )
        self.cruise = Cruise.objects.create(
            name="Crucero PT3",
            description="Desc crucero",
        )
        self.cruise.destinations.add(self.dest)

    def test_anonymous_cannot_access_destination_review_create(self):
        url = reverse("destination_review_create", args=[self.dest.id])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 302)
        self.assertIn(settings.LOGIN_URL, resp["Location"])

    def test_logged_user_without_purchase_cannot_create_destination_review(self):
        self.client.login(username="u1", password="pass12345")
        url = reverse("destination_review_create", args=[self.dest.id])

        resp = self.client.post(url, {"rating": 5, "comment": "Genial"})
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(DestinationReview.objects.count(), 0)

    def test_logged_user_with_purchase_can_create_destination_review(self):
        Purchase.objects.create(user=self.user, destination=self.dest)
        self.client.login(username="u1", password="pass12345")
        url = reverse("destination_review_create", args=[self.dest.id])

        resp = self.client.post(url, {"rating": 4, "comment": "Bien"})
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(DestinationReview.objects.count(), 1)

    def test_logged_user_without_purchase_cannot_create_cruise_review(self):
        self.client.login(username="u1", password="pass12345")
        url = reverse("cruise_review_create", args=[self.cruise.id])

        resp = self.client.post(url, {"rating": 5, "comment": "Top"})
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(CruiseReview.objects.count(), 0)

    def test_logged_user_with_purchase_can_create_cruise_review(self):
        Purchase.objects.create(user=self.user, cruise=self.cruise)
        self.client.login(username="u1", password="pass12345")
        url = reverse("cruise_review_create", args=[self.cruise.id])

        resp = self.client.post(url, {"rating": 3, "comment": "Ok"})
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(CruiseReview.objects.count(), 1)
