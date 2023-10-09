from django import forms
from personalization.models import PersonalInfo

class PersonalInfoForm(forms.ModelForm):
	about_user = forms.CharField(widget=forms.Textarea(attrs={'rows': '9' , 'cols': '80'}))

	class Meta():
		model = PersonalInfo
		fields = ['about_user', 'personal_image']

class FollowForm(forms.Form):
    userName = forms.CharField(max_length=200)
