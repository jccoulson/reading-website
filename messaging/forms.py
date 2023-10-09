from django import forms
from messaging.models import Message

class MessageForm(forms.ModelForm):
    recipient = forms.CharField(widget=forms.TextInput(attrs={'size': '80'}))
    content = forms.CharField(widget=forms.Textarea(attrs={'rows': '10', 'cols': '80'}))

    class Meta():
        model = Message
        fields = ['recipient', 'content']