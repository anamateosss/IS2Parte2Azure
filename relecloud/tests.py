from django.test import TestCase, override_settings
from django.urls import reverse
from django.core import mail
from .models import Destination, Cruise, InfoRequest

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
