"""
SOCsentinel — Unit tests for alert generator.
"""

from app.features.alerts.generator import generate_alert, generate_batch, SCENARIOS


class TestAlertGenerator:
    def test_generate_specific_scenario(self):
        alert = generate_alert("brute_force")
        assert alert.alert_id.startswith("ALERT-")
        assert alert.rule_name == "Multiple Failed Login Attempts"
        assert alert.severity.value == "high"
        assert alert.source_ip == "203.0.113.42"

    def test_generate_random(self):
        alert = generate_alert()
        assert alert.alert_id.startswith("ALERT-")
        assert alert.description != ""

    def test_generate_all_scenarios(self):
        for scenario in SCENARIOS:
            alert = generate_alert(scenario)
            assert alert.alert_id.startswith("ALERT-")
            assert alert.metadata.get("scenario") == scenario

    def test_generate_batch(self):
        alerts = generate_batch(5)
        assert len(alerts) == 5
        ids = [a.alert_id for a in alerts]
        assert len(set(ids)) == 5  # All unique

    def test_generate_batch_cycles_scenarios(self):
        alerts = generate_batch(10)
        assert len(alerts) == 10
