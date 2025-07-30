"""HTML report generator for records logs."""
import base64
import os
from datetime import datetime
from html import escape

from t_utils.const_utils import EMPOWER_RUN_LINK, work_item

from ..models.records_logs import RecordLog
from ..models.status_update import StatusUpdate
from ..models.trace import Trace


current_dir = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(current_dir, "style.txt"), encoding="utf-8") as f:
    style_content = f.read()

with open(os.path.join(current_dir, "script.txt"), encoding="utf-8") as f:
    script_content = f.read()


def _make_safe_id(record_id: str) -> str:
    """Encode the record_id safely for HTML usage (base64, url-safe, no padding)."""
    return base64.urlsafe_b64encode(record_id.encode()).decode().rstrip("=")


def _get_status_name(name: str) -> str:
    """Get the status name, escaping HTML special characters."""
    return name.strip() if name.strip() else "—"


def _get_color(col: str) -> str:
    """Get the color associated with a status."""
    return col if col and col != "transparent" else "#999999"


def _get_status_counts(record_logs: list[RecordLog]) -> dict[str, dict]:
    status_counter = {}
    for record_log in record_logs:
        if record_log.status not in status_counter:
            status_counter[record_log.status] = {"color": record_log.status_color, "count": 0}
        status_counter[record_log.status]["count"] += 1
    return status_counter


def __build_sorted_events(traces: list[Trace], status_updates: list[StatusUpdate]) -> list[tuple]:
    """Merge and sort traces and status_updates by timestamp."""
    events = [(t.timestamp, "trace", t) for t in traces] + [(s.timestamp, "status", s) for s in status_updates]
    return sorted(events, key=lambda x: x[0])


def generate_enhanced_html(records_logs_data: dict[str, RecordLog]) -> str:
    """Generate an enhanced HTML report of the records logs."""
    # Collect status counts
    status_counter = _get_status_counts(list(records_logs_data.values()))
    total_records = sum(s["count"] for s in status_counter.values())
    report_date = datetime.now().strftime("%Y-%m-%d")
    admin_code = work_item.get("metadata", {}).get("process", {}).get("adminCode", "")
    process_name = work_item.get("metadata", {}).get("process", {}).get("name", "")

    full_process_name = f"{admin_code} - {process_name}" if admin_code and process_name else process_name or admin_code
    report_name = f'Records Report for "{full_process_name}"' if full_process_name else "Records Report"

    # Start HTML
    html = (
        f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>{report_name}</title>
    """
        + """<style>"""
        + """\n"""
        + style_content
        + """\n"""
        + """</style>"""
        + """
    <script>
    """
        + script_content
        + f"""
    </script>
    </head>
    <body>
        <div class="header">
            <h1>{report_name}</h1>
            <div class="subtitle">
                Report generated for run on {report_date} <a href="{escape(EMPOWER_RUN_LINK or '')}" target="_blank">
                [run link]</a>
            </div>
            <a href="https://thoughtful.ai" class="thoughtful-logo" target="_blank">Powered by Thoughtful AI</a>
        </div>

        <div class="summary-table">
            <div class="summary-header">Status Summary</div>
            <div class="summary-content">
                <div class="summary-grid">

                    <div class="summary-item summary-total">
                        <div class="summary-count">{total_records}</div>
                        <div class="summary-label">Total Records</div>
                    </div>
    """
    )

    # Add summary blocks for each status
    for status, status_data in status_counter.items():
        html += f"""
        <div class="summary-item" style="border-color: {_get_color(status_data['color'])};">
            <div class="summary-count">{status_data['count']}</div>
            <div class="summary-label">{escape(_get_status_name(status))}</div>
        </div>
        """

    html += """
                </div>
            </div>
        </div>

        <table>
            <thead>
                <tr>
                    <th>Record ID</th>
                    <th>Status</th>
                </tr>
            </thead>
            <tbody>
    """

    # Build table rows
    for record_id, record_log in records_logs_data.items():
        safe_id = _make_safe_id(record_id)
        html += f"""
        <tr onclick="toggleTraces('{safe_id}')">
            <td>{escape(record_id)}</td>
            <td>
                <span class="status-badge" style="background-color: {_get_color(record_log.status_color)};">
                    {escape(_get_status_name(record_log.status))}
                </span>
            </td>
        </tr>
        """

        events = __build_sorted_events(record_log.traces, record_log.status_updates)
        trace_counter = 1

        for i, (timestamp, kind, event) in enumerate(events):
            if kind == "trace":
                header = (
                    f"<strong>Trace {trace_counter}</strong>"
                    f"<span class='timestamp-note'>({timestamp.strftime('%Y-%m-%d %H:%M:%S')})</span>"
                )
                trace_counter += 1

                updates_toggle = ""
                if event.dict_updates:
                    updates_toggle = f"""
                    <br><div class="toggle" id="toggle-update-{safe_id}-{i}" onclick="toggleUpdates('{safe_id}-{i}')">
{len(event.dict_updates)} fields updated</div>
                    <div class="update-details" id="update-{safe_id}-{i}">{'<br>'.join(event.dict_updates)}</div>
                    """

                image_block = ""
                if event.image:
                    image_block = f"""
<br><img src="{event.html_image_path}" class="screenshot-thumb" onclick="openImage('{safe_id}-{i}')" alt="Screenshot">
<img id="fullscreen-{safe_id}-{i}" src="{event.html_image_path}"
class="screenshot-fullscreen" onclick="closeImage('{safe_id}-{i}')">
"""

                html += f"""
<tr class="trace-{safe_id}" style="display:none;">
    <td colspan="2">
        <div class="trace-details">
            {header}
        """

                if event.action:
                    html += f"<div><strong>Action:</strong> {escape(event.action)}</div>"
                if event.reason:
                    html += f"<div><strong>Reason:</strong> {escape(event.reason)}</div>"

                html += (
                    image_block
                    + updates_toggle
                    + f"""
<br>
<div class="toggle" id="toggle-code-{safe_id}-{i}" onclick="toggleCode('{safe_id}-{i}')">
Show technical details
</div>
<div class="code-details" id="code-{safe_id}-{i}">
    <strong>Caller Trace</strong>
    <pre>{escape(event.traceback)}</pre>
</div>
</div>
    </td>
</tr>
"""
                )
            elif kind == "status":
                html += f"""
    <tr class="trace-{safe_id}" style="display:none;">
        <td colspan="2">
            <div class="trace-details">
                <div>
                    <strong>Status Update:</strong>
                    <span class="old-status"
                    style="background-color: {event.old_status_color};">{escape(_get_status_name(event.old_status))}
                    </span>
                    →
                    <span class="new-status"
                    style="background-color: {event.new_status_color};">{escape(_get_status_name(event.new_status))}
                    </span>
                </div>
                <div class="toggle"
                id="toggle-code-{safe_id}-status-{i}" onclick="toggleCode('{safe_id}-status-{i}')">
                Show technical details
                </div>
                <div class="code-details" id="code-{safe_id}-status-{i}">
                    <strong>Caller Trace</strong>
                    <pre>{escape(event.traceback)}</pre>
                </div>
            </div>
        </td>
    </tr>
    """

    # Close HTML
    html += """
            </tbody>
        </table>
    </body>
    </html>
    """

    return html
