from django.db import models

class PredictionHistory(models.Model):
    """
    Model Database untuk mencatat seluruh riwayat simulasi dan prediksi
    performa film yang dilakukan oleh pengguna pada sistem CineMetrics AI.
    """
    # 1. Parameter Input Produksi Film
    runtime = models.IntegerField(
        verbose_name="Durasi (Menit)", 
        help_text="Durasi penayangan film dalam menit (30 - 240 menit)"
    )
    votes = models.IntegerField(
        verbose_name="Resonansi Votes", 
        help_text="Estimasi akumulasi suara / ulasan penonton di IMDb"
    )
    budget = models.FloatField(
        verbose_name="Anggaran Produksi (USD)", 
        help_text="Estimasi anggaran biaya produksi film dalam satuan USD"
    )
    year = models.IntegerField(
        verbose_name="Tahun Rilis", 
        help_text="Tahun penayangan perdana film di bioskop"
    )

    # 2. Hasil Estimasi Model Machine Learning
    kualitas = models.CharField(
        max_length=50, 
        verbose_name="Prediksi Kualitas",
        choices=[
            ('Kurang', 'Kurang (< 6.0)'),
            ('Bagus', 'Bagus (6.0 - 6.9)'),
            ('Sangat Bagus', 'Sangat Bagus (>= 7.0)'),
        ],
        help_text="Hasil klasifikasi tier mutu film dari model Decision Tree"
    )
    skor_imdb = models.FloatField(
        verbose_name="Estimasi Skor IMDb", 
        help_text="Estimasi skor rating kontinu (skala 1.0 - 10.0) dari model Linear Regression"
    )

    # 3. Distribusi Probabilitas Keyakinan Kelas (Decision Tree)
    prob_kurang = models.FloatField(
        default=0.0, 
        verbose_name="Probabilitas Kurang (%)",
        help_text="Tingkat keyakinan model terhadap kelas Kurang"
    )
    prob_bagus = models.FloatField(
        default=0.0, 
        verbose_name="Probabilitas Bagus (%)",
        help_text="Tingkat keyakinan model terhadap kelas Bagus"
    )
    prob_sangat_bagus = models.FloatField(
        default=0.0, 
        verbose_name="Probabilitas Sangat Bagus (%)",
        help_text="Tingkat keyakinan model terhadap kelas Sangat Bagus"
    )

    # 4. Indeks Kelayakan Pasar & Rekomendasi
    market_score = models.IntegerField(
        default=50,
        verbose_name="Indeks Pasar (0-100)",
        help_text="Skor kelayakan komersial pasar film (0 - 100)"
    )
    insight = models.TextField(
        blank=True, 
        null=True, 
        verbose_name="Catatan Analisis AI",
        help_text="Rekomendasi strategis dan catatan kritis produser yang digenerasi oleh AI"
    )

    # 5. Metadata Timestamp
    created_at = models.DateTimeField(
        auto_now_add=True, 
        verbose_name="Waktu Simulasi",
        help_text="Waktu ketika simulasi prediksi ini dijalankan"
    )

    class Meta:
        verbose_name = "Riwayat Prediksi"
        verbose_name_plural = "Riwayat Prediksi Film"
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.created_at.strftime('%Y-%m-%d %H:%M')}] {self.kualitas} (★ {self.skor_imdb:.1f}) — {self.runtime}m | {self.votes:,} votes"
