from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator

# Create your models here.
class Destination(models.Model):
    name = models.CharField(
        unique=True,
        max_length=50,
        null=False,
        blank=False,
    )
    description = models.TextField(
        max_length=2000,
        null=False,
        blank=False
    )
    image_url = models.URLField(
        max_length=300,
        null=True,
        blank=True,
        help_text="URL de la imagen del destino"
    )

    def __str__(self):
        return self.name


class Cruise(models.Model):
    name = models.CharField(
        unique=True,
        max_length=50,
        null=False,
        blank=False,
    )
    description = models.TextField(
        max_length=2000,
        null=False,
        blank=False
    )
    destinations = models.ManyToManyField(
        Destination,
        related_name='cruises'
    )

    def __str__(self):
        return self.name


class InfoRequest(models.Model):
    name = models.CharField(
        max_length=50,
        null=False,
        blank=False,
    )
    email = models.EmailField()
    notes = models.TextField(
        max_length=2000,
        null=False,
        blank=False
    )
    cruise = models.ForeignKey(
        Cruise,
        on_delete=models.PROTECT
    )

    def __str__(self):
        return f"{self.name} - {self.cruise}"

class Purchase(models.Model):
    """
    Compra simulada: un usuario compra un DESTINO o un CRUCERO.
    Exactamente uno de los dos debe estar relleno.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="purchases"
    )
    destination = models.ForeignKey(
        Destination,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="purchases"
    )
    cruise = models.ForeignKey(
        Cruise,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="purchases"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=(
                    (models.Q(destination__isnull=False) & models.Q(cruise__isnull=True)) |
                    (models.Q(destination__isnull=True) & models.Q(cruise__isnull=False))
                ),
                name="purchase_exactly_one_item"
            ),
        ]

    def __str__(self):
        item = self.destination.name if self.destination_id else self.cruise.name
        return f"Purchase({self.user.username} -> {item})"


class DestinationReview(models.Model):
    destination = models.ForeignKey(
        Destination,
        on_delete=models.CASCADE,
        related_name="reviews"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="destination_reviews"
    )
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.TextField(max_length=2000, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["destination", "user"],
                name="uniq_destination_review_per_user"
            )
        ]

    def __str__(self):
        return f"DestinationReview({self.destination} - {self.rating})"


class CruiseReview(models.Model):
    cruise = models.ForeignKey(
        Cruise,
        on_delete=models.CASCADE,
        related_name="reviews"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="cruise_reviews"
    )
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.TextField(max_length=2000, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["cruise", "user"],
                name="uniq_cruise_review_per_user"
            )
        ]

    def __str__(self):
        return f"CruiseReview({self.cruise} - {self.rating})"
