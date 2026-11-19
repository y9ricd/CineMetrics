from django import forms

class MoviePredictionForm(forms.Form):
    runtime = forms.IntegerField(
        label="Durasi Film (Menit)",
        min_value=30,
        max_value=400,
        initial=120,
        widget=forms.NumberInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Contoh: 120',
            'min': '30',
            'max': '400'
        }),
        help_text="Rentang wajar: 30 - 400 menit (Rata-rata dataset: ~107 menit)."
    )

    votes = forms.IntegerField(
        label="Jumlah Vote Pengguna (IMDb)",
        min_value=100,
        max_value=5000000,
        initial=150000,
        widget=forms.NumberInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Contoh: 150000',
            'min': '100',
            'max': '5000000'
        }),
        help_text="Total akumulasi ulasan/vote audiens (Rata-rata dataset: ~115.000 vote)."
    )

    budget = forms.FloatField(
        label="Anggaran Produksi (USD $)",
        min_value=10000,
        max_value=1000000000,
        initial=35000000,
        widget=forms.NumberInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Contoh: 35000000',
            'min': '10000',
            'max': '1000000000'
        }),
        help_text="Biaya pembuatan film dalam USD (Contoh: 35.000.000 untuk film medium budget)."
    )

    year = forms.IntegerField(
        label="Tahun Rilis",
        min_value=1970,
        max_value=2030,
        initial=2021,
        widget=forms.NumberInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Contoh: 2021',
            'min': '1970',
            'max': '2030'
        }),
        help_text="Tahun perilisan film di bioskop/platform streaming (1970 - 2030)."
    )

    def clean_runtime(self):
        runtime = self.cleaned_data.get('runtime')
        if runtime is not None and runtime <= 0:
            raise forms.ValidationError("Durasi film harus lebih besar dari 0 menit.")
        return runtime

    def clean_budget(self):
        budget = self.cleaned_data.get('budget')
        if budget is not None and budget <= 0:
            raise forms.ValidationError("Anggaran film harus berupa angka positif.")
        return budget
