from django import forms

class PortfolioForm(forms.Form):
    name = forms.CharField(label="Your Name", max_length=100, required=True)
    email = forms.EmailField(label="Your Email", required=True)
    phone = forms.CharField(
        label="Your Phone Number", 
        max_length=15, 
        required=True, 
        widget=forms.TextInput(attrs={'placeholder': 'e.g., +1234567890'})
    )
    stocks = forms.CharField(
        label="Stock Details (Format: STOCK_SYMBOL:SHARES, separated by commas)", 
        widget=forms.TextInput(attrs={'placeholder': 'e.g., AAPL:10, GOOGL:5'})
    )