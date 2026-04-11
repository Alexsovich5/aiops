"""
Incident Classifier
IT Operations Specialist - ACORIA (2019)

BERT-based incident classification for automatic categorization
and priority assignment.
"""

import logging
import numpy as np
from models.bert_classifier import BERTClassifier

logger = logging.getLogger('incident_classifier')

CATEGORIES = [
    'network', 'server', 'database', 'application',
    'security', 'storage', 'authentication', 'performance'
]

PRIORITIES = ['P1-Critical', 'P2-High', 'P3-Medium', 'P4-Low']


class IncidentClassifier:
    """Classifies incidents using NLP."""

    def __init__(self, model_path=None):
        self.bert = BERTClassifier(num_classes=len(CATEGORIES))
        if model_path:
            self.bert.load(model_path)
        self.resolution_db = {}

    def classify(self, incident_text):
        """Classify incident and suggest resolution."""
        # Get category prediction
        predictions = self.bert.predict(incident_text)
        category_idx = int(np.argmax(predictions))
        confidence = float(predictions[category_idx])

        # Determine priority based on keywords
        priority = self._assess_priority(incident_text)

        # Find similar past incidents
        suggestions = self._suggest_resolution(incident_text, CATEGORIES[category_idx])

        return {
            'category': CATEGORIES[category_idx],
            'confidence': round(confidence, 3),
            'priority': priority,
            'suggestions': suggestions
        }

    def _assess_priority(self, text):
        """Assess incident priority from text."""
        text_lower = text.lower()
        if any(kw in text_lower for kw in ['outage', 'down', 'critical', 'production']):
            return 'P1-Critical'
        elif any(kw in text_lower for kw in ['degraded', 'slow', 'intermittent']):
            return 'P2-High'
        elif any(kw in text_lower for kw in ['error', 'warning', 'failed']):
            return 'P3-Medium'
        return 'P4-Low'

    def _suggest_resolution(self, text, category):
        """Suggest resolutions based on similar past incidents."""
        # Simplified - would use vector similarity in production
        common_resolutions = {
            'network': ['Check network connectivity', 'Restart network services', 'Verify DNS resolution'],
            'server': ['Check server resources', 'Restart affected service', 'Review system logs'],
            'database': ['Check database connections', 'Review slow queries', 'Verify disk space'],
            'application': ['Restart application', 'Check application logs', 'Verify configuration'],
            'security': ['Review security logs', 'Check firewall rules', 'Scan for vulnerabilities'],
            'storage': ['Check disk usage', 'Verify mount points', 'Review I/O metrics'],
            'authentication': ['Verify credentials', 'Check AD/LDAP connectivity', 'Reset user password'],
            'performance': ['Check CPU/memory usage', 'Review active processes', 'Scale resources']
        }
        return common_resolutions.get(category, ['Investigate further'])

    def train(self, training_data):
        """Train the classifier on historical incidents."""
        texts = [d['text'] for d in training_data]
        labels = [CATEGORIES.index(d['category']) for d in training_data]
        self.bert.train(texts, labels)
        logger.info("Classifier trained on %d incidents", len(texts))
