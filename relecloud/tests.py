from django.test import TestCase

# Create your tests here.
def test_destinations_are_ordered_by_popularity(client, django_user_model):
    d1 = Destination.objects.create(
        name="Destino Popular",
        description="Desc"
    )
    d2 = Destination.objects.create(
        name="Destino Menos Popular",
        description="Desc"
    )

    user = django_user_model.objects.create_user(
        username="test",
        password="1234"
    )

    Review.objects.create(destination=d1, user=user, rating=5)
    Review.objects.create(destination=d1, user=user, rating=4)
    Review.objects.create(destination=d2, user=user, rating=5)

    response = client.get("/destinations/")
    destinations = response.context["destinations"]

    assert destinations[0] == d1
