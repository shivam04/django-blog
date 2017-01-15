from django import forms

class CommentForm(forms.Form):
	content_type = forms.CharField(widget=forms.HiddenInput)
	object_id = forms.IntegerField(widget=forms.HiddenInput)
	#parent_id = forms.IntegerField(widget=forms.HiddenInput, required=False)
	conent = forms.CharField(label='',widget=forms.Textarea)