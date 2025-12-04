from django.test import TestCase, Client
from django.urls import reverse
from chatbot.models import Reading

class APITestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        Reading.objects.bulk_create([
            Reading(sensor='ch4_percent', ts='2025-10-01T08:00:00Z', value=58.2),
            Reading(sensor='ch4_percent', ts='2025-10-01T09:00:00Z', value=59.1),
            Reading(sensor='ch4_percent', ts='2025-10-01T10:00:00Z', value=60.0),
            Reading(sensor='ch4_percent', ts='2025-10-01T11:00:00Z', value=59.4),
            Reading(sensor='ch4_percent', ts='2025-10-01T12:00:00Z', value=58.7),

            Reading(sensor='flow_scfm', ts='2025-10-01T09:00:00Z', value=130.0),
            Reading(sensor='flow_scfm', ts='2025-10-01T10:00:00Z', value=125.5),
            Reading(sensor='flow_scfm', ts='2025-10-01T11:00:00Z', value=140.3),
            Reading(sensor='flow_scfm', ts='2025-10-01T12:00:00Z', value=135.2),

            Reading(sensor='h2s_ppm', ts='2025-10-01T09:00:00Z', value=31),
            Reading(sensor='h2s_ppm', ts='2025-10-01T10:00:00Z', value=35),
            Reading(sensor='h2s_ppm', ts='2025-10-01T11:00:00Z', value=33),
        ])

    def setUp(self):
        self.client = Client()

    def test_schema(self):
        response = self.client.get("/schema/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {
            "columns": ["sensor", "ts", "value"]
        })

    def test_health(self):
        response = self.client.get("/healthz/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})

    def test_reject_non_select(self):
        response = self.client.get(
            "/query/?sql=DROP%20TABLE%20chatbot_reading"
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("Only SELECT allowed", str(response.content))

    def test_flow_values(self):
        sql = """
            SELECT ts, value AS flow_scfm
            FROM chatbot_reading
            WHERE sensor = 'flow_scfm'
            ORDER BY ts;
        """
        response = self.client.get("/query/", {"sql": sql})
        data = response.json()["rows"]

        self.assertEqual(len(data), 4)
        values = [row["flow_scfm"] for row in data]
        self.assertEqual(values, [130.0, 125.5, 140.3, 135.2])

    def test_average_ch4(self):
        sql = """
            SELECT ROUND(AVG(value)::numeric, 2) AS avg_ch4
            FROM chatbot_reading
            WHERE sensor = 'ch4_percent'
            AND ts >= '2025-10-01T00:00:00Z'
            AND ts < '2025-10-02T00:00:00Z';
        """
        response = self.client.get("/query/", {"sql": sql})
        avg = float(response.json()["rows"][0]["avg_ch4"])
        self.assertAlmostEqual(avg, 59.08)
