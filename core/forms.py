from django import forms

class UsernameForm(forms.Form):
    """Form for entering a Chess.com username"""
    username = forms.CharField(
        label="Chess.com username",
        max_length=30,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter Chess.com username...',
            'autocomplete': 'off'
        }),
        help_text="Enter a valid Chess.com username to analyze their games."
    )
    
    def clean_username(self):
        """Clean and normalize the username"""
        username = self.cleaned_data['username']
        return username.strip().lower() 