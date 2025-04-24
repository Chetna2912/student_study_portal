from django import forms
from . models import *
from django.contrib.auth.forms import UserCreationForm

class NotesForm(forms.ModelForm):
    class Meta:
        model = Notes
        fields = ['title','description']

class DateInput(forms.DateInput):
    input_type = 'date'
        
class HomeworkForm(forms.ModelForm):
    class Meta:
        model = Homework
        widgets = {'due':DateInput()}
        fields = ['subject','title','description','due','is_finished']

class DashboardForm(forms.Form):
    text = forms.CharField(max_length=100, label="Enter Your Search ")
    
class TodoForm(forms.ModelForm):
    class Meta:
        model = Todo
        fields = ['title','is_finished']
    

class ConversionForm(forms.Form):
    MEASUREMENT_CHOICES = [
        ('length', 'Length'),
        ('mass', 'Mass'),
    ]
    measurement = forms.ChoiceField(choices=MEASUREMENT_CHOICES)

class ConversionLengthForm(forms.Form):
    LENGTH_CHOICES = [
        ('yard', 'Yard'),
        ('foot', 'Foot'),
    ]
    input = forms.FloatField()
    measure1 = forms.ChoiceField(choices=LENGTH_CHOICES)
    measure2 = forms.ChoiceField(choices=LENGTH_CHOICES)

class ConversionMassForm(forms.Form):
    MASS_CHOICES = [
        ('pound', 'Pound'),
        ('kilogram', 'Kilogram'),
    ]
    input = forms.FloatField()
    measure1 = forms.ChoiceField(choices=MASS_CHOICES)
    measure2 = forms.ChoiceField(choices=MASS_CHOICES)

class UserRegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username','password1','password2']
        