from django.contrib import admin
from .models import PredictionHistory

@admin.register(PredictionHistory)
class PredictionHistoryAdmin(admin.ModelAdmin):
    """Konfigurasi tampilan Django Admin untuk riwayat prediksi film."""
    list_display = (
        'created_at', 
        'kualitas', 
        'skor_imdb', 
        'market_score', 
        'runtime', 
        'formatted_votes', 
        'formatted_budget', 
        'year'
    )
    list_filter = ('kualitas', 'year', 'created_at')
    search_fields = ('kualitas', 'insight')
    readonly_fields = ('created_at',)
    list_per_page = 25

    def formatted_votes(self, obj):
        return f"{obj.votes:,}"
    formatted_votes.short_description = "Votes"

    def formatted_budget(self, obj):
        return f"${obj.budget:,.0f}"
    formatted_budget.short_description = "Anggaran"
