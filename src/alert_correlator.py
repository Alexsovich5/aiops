"""
Alert Correlator

Correlates related alerts to reduce noise and identify
root cause patterns.
"""

import logging
from datetime import datetime, timedelta
from collections import defaultdict

logger = logging.getLogger('alert_correlator')


class AlertCorrelator:
    """Correlates and deduplicates alerts."""

    def __init__(self, config=None):
        self.window_minutes = config.get('correlation_window', 5) if config else 5
        self.alert_buffer = defaultdict(list)
        self.correlation_rules = self._load_rules()

    def process_alert(self, alert):
        """Process an incoming alert and correlate."""
        source = alert.get('source', '')
        now = datetime.utcnow()

        # Clean old alerts from buffer
        self._cleanup_buffer(now)

        # Check for duplicates
        if self._is_duplicate(alert):
            logger.debug("Duplicate alert suppressed: %s", alert.get('message'))
            return None

        # Add to buffer
        self.alert_buffer[source].append({**alert, '_timestamp': now})

        # Check correlation rules
        correlated = self._correlate(alert)
        if correlated:
            return {
                'type': 'correlated_incident',
                'root_cause': correlated['root_cause'],
                'related_alerts': correlated['alerts'],
                'severity': max(a.get('severity', 0) for a in correlated['alerts']),
                'timestamp': now.isoformat()
            }

        return alert

    def _is_duplicate(self, alert):
        """Check if alert is a duplicate within the window."""
        source = alert.get('source', '')
        message = alert.get('message', '')
        for existing in self.alert_buffer.get(source, []):
            if existing.get('message') == message:
                return True
        return False

    def _correlate(self, alert):
        """Apply correlation rules."""
        for rule in self.correlation_rules:
            matching = self._match_rule(rule, alert)
            if matching:
                return matching
        return None

    def _match_rule(self, rule, trigger_alert):
        """Check if a correlation rule matches current state."""
        pattern = rule['pattern']
        required_count = pattern.get('min_alerts', 2)

        matching_alerts = []
        for source, alerts in self.alert_buffer.items():
            for alert in alerts:
                if self._alert_matches_pattern(alert, pattern):
                    matching_alerts.append(alert)

        if len(matching_alerts) >= required_count:
            return {
                'root_cause': rule['root_cause'],
                'alerts': matching_alerts
            }
        return None

    def _alert_matches_pattern(self, alert, pattern):
        """Check if an alert matches a pattern."""
        for key, value in pattern.get('match', {}).items():
            if alert.get(key) != value:
                return False
        return True

    def _cleanup_buffer(self, now):
        """Remove expired alerts from buffer."""
        cutoff = now - timedelta(minutes=self.window_minutes)
        for source in list(self.alert_buffer.keys()):
            self.alert_buffer[source] = [
                a for a in self.alert_buffer[source]
                if a['_timestamp'] > cutoff
            ]

    def _load_rules(self):
        """Load correlation rules."""
        return [
            {
                'name': 'network_cascade',
                'pattern': {'match': {'type': 'network'}, 'min_alerts': 3},
                'root_cause': 'Network infrastructure issue'
            },
            {
                'name': 'disk_pressure',
                'pattern': {'match': {'type': 'storage'}, 'min_alerts': 2},
                'root_cause': 'Storage capacity issue'
            }
        ]
