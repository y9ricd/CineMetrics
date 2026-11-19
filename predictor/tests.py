from django.test import TestCase, Client
from django.urls import reverse
from predictor.forms import MoviePredictionForm
from predictor.views import get_ml_assets

class MoviePredictorTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse("predictor:index")

    def test_ml_assets_loading(self):
        """Memastikan model ML dan metadata dapat dimuat tanpa error."""
        clf, reg, meta = get_ml_assets()
        self.assertIsNotNone(clf)
        self.assertIsNotNone(reg)
        self.assertIn("decision_tree", meta)

    def test_form_valid(self):
        """Memastikan input form yang valid diterima."""
        form = MoviePredictionForm(data={
            "runtime": 120,
            "votes": 50000,
            "budget": 20000000,
            "year": 2021
        })
        self.assertTrue(form.is_valid())

    def test_form_invalid_values(self):
        """Memastikan input non-realistis ditolak oleh form validation."""
        # Runtime terlalu kecil / nol
        form_runtime = MoviePredictionForm(data={
            "runtime": 10,
            "votes": 50000,
            "budget": 20000000,
            "year": 2021
        })
        self.assertFalse(form_runtime.is_valid())
        self.assertIn("runtime", form_runtime.errors)

        # Budget terlalu kecil / negatif
        form_budget = MoviePredictionForm(data={
            "runtime": 120,
            "votes": 50000,
            "budget": -100,
            "year": 2021
        })
        self.assertFalse(form_budget.is_valid())
        self.assertIn("budget", form_budget.errors)

    def test_index_view_get(self):
        """Memastikan halaman utama dapat diakses via GET."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "predictor/index.html")
        self.assertIn("form", response.context)
        self.assertIn("meta", response.context)

    def test_index_view_post_prediction(self):
        """Memastikan pengiriman form POST menghasilkan inferensi yang akurat."""
        payload = {
            "runtime": 125,
            "votes": 200000,
            "budget": 50000000,
            "year": 2015
        }
        response = self.client.post(self.url, data=payload)
        self.assertEqual(response.status_code, 200)
        self.assertIn("result", response.context)

        res = response.context["result"]
        self.assertIsNotNone(res)
        self.assertIn(res["kualitas"], ["Kurang", "Bagus", "Sangat Bagus"])
        self.assertGreaterEqual(res["skor_imdb"], 1.0)
        self.assertLessEqual(res["skor_imdb"], 10.0)

    def test_index_view_ajax_prediction(self):
        """Memastikan pengiriman request AJAX POST menghasilkan respons JSON."""
        payload = {
            "runtime": 125,
            "votes": 200000,
            "budget": 50000000,
            "year": 2015
        }
        response = self.client.post(
            self.url,
            data=payload,
            headers={"x-requested-with": "XMLHttpRequest"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers.get("Content-Type"), "application/json")
        data = response.json()
        self.assertTrue(data.get("success"))
        self.assertIn("result", data)
        self.assertIn(data["result"]["kualitas"], ["Kurang", "Bagus", "Sangat Bagus"])

    def test_ai_service_functions(self):
        """Memastikan fungsi ai_service mengembalikan analisis non-kosong dan cerdas."""
        from predictor.ai_service import generate_movie_insight, ask_cinebot
        
        insight = generate_movie_insight(
            runtime=140,
            votes=400000,
            budget=150000000,
            year=2023,
            kualitas="Sangat Bagus",
            skor_imdb=7.8
        )
        self.assertIsInstance(insight, str)
        self.assertGreater(len(insight), 20)

        reply = ask_cinebot("Bagaimana cara kerja model ini?")
        self.assertIsInstance(reply, str)
        self.assertGreater(len(reply), 20)

    def test_prediction_history_creation_and_api(self):
        """Memastikan prediksi tersimpan ke PredictionHistory dan dapat diakses via API."""
        from predictor.models import PredictionHistory
        
        # Bersihkan riwayat sebelum tes
        PredictionHistory.objects.all().delete()

        payload = {
            "runtime": 130,
            "votes": 250000,
            "budget": 60000000,
            "year": 2020
        }
        response = self.client.post(self.url, data=payload)
        self.assertEqual(response.status_code, 200)

        # Cek database tersimpan
        self.assertEqual(PredictionHistory.objects.count(), 1)
        record = PredictionHistory.objects.first()
        self.assertEqual(record.runtime, 130)
        self.assertEqual(record.votes, 250000)
        self.assertIn(record.kualitas, ["Kurang", "Bagus", "Sangat Bagus"])
        self.assertGreaterEqual(record.skor_imdb, 1.0)
        self.assertGreaterEqual(record.market_score, 10)

        # Cek filter duplikasi: kirim parameter persis sama
        self.client.post(self.url, data=payload)
        self.assertEqual(PredictionHistory.objects.count(), 1)

        # Cek API riwayat
        history_url = reverse("predictor:history_api")
        res_history = self.client.get(history_url)
        self.assertEqual(res_history.status_code, 200)
        h_data = res_history.json()
        self.assertTrue(h_data.get("success"))
        self.assertEqual(h_data.get("count"), 1)
        self.assertEqual(h_data["history"][0]["runtime"], 130)

    def test_chat_view_endpoint(self):
        """Memastikan endpoint /api/chat/ merespons pertanyaan chat dengan JSON."""
        chat_url = reverse("predictor:chat")
        payload = {
            "message": "Jelaskan cara kerja Decision Tree",
            "runtime": 120,
            "votes": 100000,
            "budget": 30000000,
            "year": 2022
        }
        response = self.client.post(chat_url, data=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data.get("success"))
        self.assertIn("reply", data)
        self.assertGreater(len(data["reply"]), 20)

    def test_history_api_clear_action(self):
        """Memastikan aksi pembersihan riwayat pada /api/history/ bekerja."""
        from predictor.models import PredictionHistory
        PredictionHistory.objects.create(
            runtime=100, votes=50000, budget=10000000, year=2020,
            kualitas="Bagus", skor_imdb=6.5, prob_kurang=10, prob_bagus=70,
            prob_sangat_bagus=20, market_score=65, insight="Test"
        )
        self.assertEqual(PredictionHistory.objects.count(), 1)

        history_url = reverse("predictor:history_api")
        resp = self.client.post(history_url, data={"action": "clear"})
        self.assertEqual(resp.status_code, 200)
        res_data = resp.json()
        self.assertTrue(res_data.get("success"))
        self.assertEqual(PredictionHistory.objects.count(), 0)

    def test_is_out_of_scope_guardrail(self):
        """Memastikan guardrail topik di luar domain perfilman bekerja dengan baik."""
        from predictor.ai_service import is_out_of_scope, ask_cinebot
        # Topik terlarang
        self.assertTrue(is_out_of_scope("Bagaimana cara membuat nasi goreng lezat?"))
        self.assertTrue(is_out_of_scope("Siapa presiden Indonesia saat ini?"))
        self.assertTrue(is_out_of_scope("Apa obat untuk sakit kepala?"))

        # Topik perfilman yang sah
        self.assertFalse(is_out_of_scope("Bagaimana pengaruh durasi terhadap rating film?"))
        self.assertFalse(is_out_of_scope("Jelaskan pohon keputusan di CineMetrics"))

        # Cinebot merespons penolakan ramah
        reply = ask_cinebot("Bagaimana resep rendang daging?")
        self.assertIn("CineBot", reply)
        self.assertIn("perfilman", reply)

    def test_chat_view_empty_message(self):
        """Memastikan pesan kosong ditolak dengan status 400."""
        chat_url = reverse("predictor:chat")
        resp = self.client.post(chat_url, data={"message": "   "})
        self.assertEqual(resp.status_code, 400)
        data = resp.json()
        self.assertFalse(data.get("success"))

    def test_get_chart_data(self):
        """Memastikan get_chart_data mengembalikan struktur data visualisasi yang valid."""
        from predictor.views import get_chart_data
        chart_data = get_chart_data()
        self.assertIn("kualitas_labels", chart_data)
        self.assertIn("kualitas_counts", chart_data)
        self.assertIn("genre_labels", chart_data)
        self.assertIn("genre_scores", chart_data)
        self.assertIn("importance_labels", chart_data)
        self.assertIn("importance_values", chart_data)
        self.assertEqual(len(chart_data["importance_values"]), 4)
