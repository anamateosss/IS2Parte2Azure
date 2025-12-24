from django import forms
from .models import DestinationReview, CruiseReview

class DestinationReviewForm(forms.ModelForm):
    class Meta:
        model = DestinationReview
        fields = ["rating", "comment"]

class CruiseReviewForm(forms.ModelForm):
    class Meta:
        model = CruiseReview
        fields = ["rating", "comment"]
