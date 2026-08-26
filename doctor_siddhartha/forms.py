from django import forms
from django.forms import inlineformset_factory

from .models import Availability, Prescription, PrescriptionItem


class PrescriptionForm(forms.ModelForm):
    class Meta:
        model = Prescription
        fields = ['diagnosis', 'additional_notes']
        widgets = {
            'diagnosis': forms.Textarea(attrs={'rows': 3, 'class': 'w-full p-md rounded-lg border-outline-variant'}),
            'additional_notes': forms.Textarea(attrs={'rows': 2, 'class': 'w-full p-md rounded-lg border-outline-variant'}),
        }


PrescriptionItemFormSet = inlineformset_factory(
    Prescription, PrescriptionItem,
    fields=['medicine_name', 'dosage', 'frequency', 'duration'],
    extra=1, can_delete=True,
)


class AvailabilityForm(forms.Form):
    days = forms.MultipleChoiceField(choices=Availability.DAY_CHOICES, widget=forms.CheckboxSelectMultiple)
    start_time = forms.TimeField()
    end_time = forms.TimeField()
    slot_duration_minutes = forms.ChoiceField(choices=[(30, '30 Min'), (45, '45 Min'), (60, '60 Min')])