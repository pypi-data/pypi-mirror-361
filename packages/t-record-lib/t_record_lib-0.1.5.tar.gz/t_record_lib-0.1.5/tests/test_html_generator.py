from t_record.report.html_generator import generate_enhanced_html
from t_record.models.records_logs import RecordLog


def test_generate_html_includes_content() -> None:
    record_log = RecordLog(record_id="r123", record="{}")
    html = generate_enhanced_html({"r123": record_log})
    assert "r123" in html
    assert "<html>" in html
