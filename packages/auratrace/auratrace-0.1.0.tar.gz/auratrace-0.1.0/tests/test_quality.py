"""
Tests for the AuraTrace quality engine.
"""

import pytest
import pandas as pd
import numpy as np
from auratrace.core.quality import QualityEngine, QualityRule, QualityIssue


class TestQualityEngine:
    """Test cases for the QualityEngine class."""
    
    def test_quality_engine_initialization(self):
        """Test quality engine initialization."""
        engine = QualityEngine()
        assert len(engine.rules) == 0
        assert len(engine.issues) == 0
        assert len(engine.built_in_rules) > 0
    
    def test_add_rule(self):
        """Test adding a quality rule."""
        engine = QualityEngine()
        rule = QualityRule(
            name="test_rule",
            description="Test rule",
            rule_type="null_check",
            column="test_column",
            parameters={"max_null_percentage": 50.0},
            severity="warning"
        )
        
        engine.add_rule(rule)
        assert len(engine.rules) == 1
        assert engine.rules[0].name == "test_rule"
    
    def test_load_rules_from_yaml(self, tmp_path):
        """Test loading rules from YAML file."""
        import yaml
        
        # Create a temporary YAML file
        rules_data = {
            'rules': [
                {
                    'name': 'null_check',
                    'description': 'Check for null values',
                    'type': 'null_check',
                    'parameters': {'max_null_percentage': 50.0},
                    'severity': 'warning'
                },
                {
                    'name': 'uniqueness_check',
                    'description': 'Check for unique values',
                    'type': 'uniqueness_check',
                    'column': 'id',
                    'severity': 'error'
                }
            ]
        }
        
        yaml_file = tmp_path / "test_rules.yml"
        with open(yaml_file, 'w') as f:
            yaml.dump(rules_data, f)
        
        engine = QualityEngine()
        engine.load_rules_from_yaml(str(yaml_file))
        
        assert len(engine.rules) == 2
        assert engine.rules[0].name == "null_check"
        assert engine.rules[1].name == "uniqueness_check"
    
    def test_check_dataframe_empty(self):
        """Test checking empty dataframe."""
        engine = QualityEngine()
        df = pd.DataFrame()
        
        issues = engine.check_dataframe(df)
        assert len(issues) == 0
    
    def test_null_check(self):
        """Test null value checking."""
        engine = QualityEngine()
        
        # Add a null check rule
        rule = QualityRule(
            name="null_check",
            description="Check for null values",
            rule_type="null_check",
            parameters={"max_null_percentage": 50.0},
            severity="warning"
        )
        engine.add_rule(rule)
        
        # Create dataframe with nulls
        df = pd.DataFrame({
            'A': [1, 2, None, 4, 5],
            'B': [None, None, None, None, None],  # 100% nulls
            'C': [1, 2, 3, 4, 5]  # No nulls
        })
        
        issues = engine.check_dataframe(df)
        
        # Should detect high null percentage in column B
        assert len(issues) > 0
        null_issues = [i for i in issues if i.issue_type == 'null_check']
        assert len(null_issues) > 0
        
        # Check that column B is flagged
        b_issues = [i for i in null_issues if 'B' in i.affected_columns]
        assert len(b_issues) > 0
    
    def test_range_check(self):
        """Test range value checking."""
        engine = QualityEngine()
        
        # Add a range check rule
        rule = QualityRule(
            name="range_check",
            description="Check value range",
            rule_type="range_check",
            column="age",
            parameters={"min_value": 0, "max_value": 120},
            severity="warning"
        )
        engine.add_rule(rule)
        
        # Create dataframe with out-of-range values
        df = pd.DataFrame({
            'age': [25, 30, -5, 150, 50],  # -5 and 150 are out of range
            'name': ['Alice', 'Bob', 'Charlie', 'David', 'Eve']
        })
        
        issues = engine.check_dataframe(df)
        
        # Should detect out-of-range values
        range_issues = [i for i in issues if i.issue_type == 'range_check']
        assert len(range_issues) > 0
    
    def test_uniqueness_check(self):
        """Test uniqueness checking."""
        engine = QualityEngine()
        
        # Add a uniqueness check rule
        rule = QualityRule(
            name="uniqueness_check",
            description="Check for unique values",
            rule_type="uniqueness_check",
            column="id",
            severity="error"
        )
        engine.add_rule(rule)
        
        # Create dataframe with duplicates
        df = pd.DataFrame({
            'id': [1, 2, 1, 3, 2],  # Duplicates: 1 and 2
            'name': ['Alice', 'Bob', 'Charlie', 'David', 'Eve']
        })
        
        issues = engine.check_dataframe(df)
        
        # Should detect duplicate values
        uniqueness_issues = [i for i in issues if i.issue_type == 'uniqueness_check']
        assert len(uniqueness_issues) > 0
    
    def test_format_check(self):
        """Test format checking."""
        engine = QualityEngine()
        
        # Add a format check rule
        rule = QualityRule(
            name="email_format_check",
            description="Check email format",
            rule_type="format_check",
            column="email",
            parameters={"pattern": r'^[^@]+@[^@]+\.[^@]+$'},
            severity="error"
        )
        engine.add_rule(rule)
        
        # Create dataframe with invalid emails
        df = pd.DataFrame({
            'email': [
                'valid@example.com',
                'invalid-email',
                'another@domain.org',
                'no-at-sign.com'
            ]
        })
        
        issues = engine.check_dataframe(df)
        
        # Should detect invalid email formats
        format_issues = [i for i in issues if i.issue_type == 'format_check']
        assert len(format_issues) > 0
    
    def test_completeness_check(self):
        """Test completeness checking."""
        engine = QualityEngine()
        
        # Add a completeness check rule
        rule = QualityRule(
            name="completeness_check",
            description="Check for required columns",
            rule_type="completeness_check",
            parameters={"required_columns": ["id", "name", "email"]},
            severity="error"
        )
        engine.add_rule(rule)
        
        # Create dataframe missing required columns
        df = pd.DataFrame({
            'id': [1, 2, 3],
            'name': ['Alice', 'Bob', 'Charlie']
            # Missing 'email' column
        })
        
        issues = engine.check_dataframe(df)
        
        # Should detect missing columns
        completeness_issues = [i for i in issues if i.issue_type == 'completeness_check']
        assert len(completeness_issues) > 0
    
    def test_custom_rule(self):
        """Test custom quality rule."""
        engine = QualityEngine()
        
        def custom_check(df, rule):
            issues = []
            if 'custom_column' in df.columns:
                if df['custom_column'].sum() > 100:
                    issues.append(QualityIssue(
                        rule_name=rule.name,
                        issue_type='custom_check',
                        description='Sum exceeds threshold',
                        severity=rule.severity,
                        affected_rows=len(df),
                        affected_columns=['custom_column'],
                        details={'sum': df['custom_column'].sum()},
                        timestamp=pd.Timestamp.now().timestamp()
                    ))
            return issues
        
        # Add a custom rule
        rule = QualityRule(
            name="custom_sum_check",
            description="Check sum of custom column",
            rule_type="custom",
            custom_function=custom_check,
            severity="warning"
        )
        engine.add_rule(rule)
        
        # Create dataframe that triggers the custom rule
        df = pd.DataFrame({
            'custom_column': [50, 60, 70]  # Sum = 180 > 100
        })
        
        issues = engine.check_dataframe(df)
        
        # Should detect the custom issue
        custom_issues = [i for i in issues if i.issue_type == 'custom_check']
        assert len(custom_issues) > 0
    
    def test_rule_execution_error(self):
        """Test handling of rule execution errors."""
        engine = QualityEngine()
        
        def failing_check(df, rule):
            raise ValueError("Simulated error")
        
        # Add a rule that will fail
        rule = QualityRule(
            name="failing_rule",
            description="A rule that fails",
            rule_type="custom",
            custom_function=failing_check,
            severity="error"
        )
        engine.add_rule(rule)
        
        df = pd.DataFrame({'A': [1, 2, 3]})
        issues = engine.check_dataframe(df)
        
        # Should create an issue for the rule failure
        error_issues = [i for i in issues if i.issue_type == 'rule_execution_error']
        assert len(error_issues) > 0
    
    def test_get_quality_summary(self):
        """Test quality summary generation."""
        engine = QualityEngine()
        
        # Add some rules and check a dataframe
        rule1 = QualityRule(
            name="null_check",
            description="Check for null values",
            rule_type="null_check",
            parameters={"max_null_percentage": 50.0},
            severity="warning"
        )
        rule2 = QualityRule(
            name="uniqueness_check",
            description="Check for unique values",
            rule_type="uniqueness_check",
            column="id",
            severity="error"
        )
        
        engine.add_rule(rule1)
        engine.add_rule(rule2)
        
        # Create dataframe that will trigger issues
        df = pd.DataFrame({
            'id': [1, 2, 1, 3],  # Duplicate
            'value': [1, 2, None, 4]  # Some nulls
        })
        
        engine.check_dataframe(df)
        summary = engine.get_quality_summary()
        
        assert 'total_issues' in summary
        assert 'issues_by_severity' in summary
        assert 'issues_by_type' in summary
        assert 'overall_status' in summary
        assert summary['total_issues'] > 0
    
    def test_export_issues(self):
        """Test exporting issues in different formats."""
        engine = QualityEngine()
        
        # Create some issues
        issue1 = QualityIssue(
            rule_name="test_rule",
            issue_type="null_check",
            description="Test issue",
            severity="warning",
            affected_rows=10,
            affected_columns=["test_column"],
            details={"null_count": 5},
            timestamp=1234567890.0
        )
        
        engine.issues = [issue1]
        
        # Test JSON export
        json_export = engine.export_issues('json')
        assert isinstance(json_export, str)
        assert 'test_rule' in json_export
        
        # Test YAML export
        yaml_export = engine.export_issues('yaml')
        assert isinstance(yaml_export, str)
        assert 'test_rule' in yaml_export
        
        # Test CSV export
        csv_export = engine.export_issues('csv')
        assert isinstance(csv_export, str)
        assert 'test_rule' in csv_export


class TestQualityRule:
    """Test cases for QualityRule."""
    
    def test_quality_rule_creation(self):
        """Test QualityRule creation."""
        rule = QualityRule(
            name="test_rule",
            description="Test rule description",
            rule_type="null_check",
            column="test_column",
            parameters={"max_null_percentage": 50.0},
            severity="warning"
        )
        
        assert rule.name == "test_rule"
        assert rule.description == "Test rule description"
        assert rule.rule_type == "null_check"
        assert rule.column == "test_column"
        assert rule.parameters["max_null_percentage"] == 50.0
        assert rule.severity == "warning"
    
    def test_quality_rule_defaults(self):
        """Test QualityRule default values."""
        rule = QualityRule(
            name="test_rule",
            description="Test rule",
            rule_type="null_check"
        )
        
        assert rule.parameters == {}
        assert rule.severity == "warning"
        assert rule.column is None
        assert rule.custom_function is None


class TestQualityIssue:
    """Test cases for QualityIssue."""
    
    def test_quality_issue_creation(self):
        """Test QualityIssue creation."""
        issue = QualityIssue(
            rule_name="test_rule",
            issue_type="null_check",
            description="Test issue description",
            severity="warning",
            affected_rows=10,
            affected_columns=["test_column"],
            details={"null_count": 5},
            timestamp=1234567890.0
        )
        
        assert issue.rule_name == "test_rule"
        assert issue.issue_type == "null_check"
        assert issue.description == "Test issue description"
        assert issue.severity == "warning"
        assert issue.affected_rows == 10
        assert "test_column" in issue.affected_columns
        assert issue.details["null_count"] == 5
        assert issue.timestamp == 1234567890.0


@pytest.fixture
def sample_dataframe():
    """Create a sample dataframe for testing."""
    return pd.DataFrame({
        'id': [1, 2, 3, 4, 5],
        'name': ['Alice', 'Bob', 'Charlie', 'David', 'Eve'],
        'age': [25, 30, 35, 40, 45],
        'email': ['alice@example.com', 'bob@example.com', 'charlie@example.com', 'david@example.com', 'eve@example.com'],
        'score': [85, 90, 75, 88, 92]
    })


@pytest.fixture
def quality_engine():
    """Create a fresh quality engine instance."""
    return QualityEngine()


class TestQualityIntegration:
    """Integration tests for the quality engine."""
    
    def test_comprehensive_quality_check(self, quality_engine, sample_dataframe):
        """Test comprehensive quality checking."""
        # Add multiple rules
        rules = [
            QualityRule(
                name="null_check",
                description="Check for null values",
                rule_type="null_check",
                parameters={"max_null_percentage": 50.0},
                severity="warning"
            ),
            QualityRule(
                name="uniqueness_check",
                description="Check for unique IDs",
                rule_type="uniqueness_check",
                column="id",
                severity="error"
            ),
            QualityRule(
                name="range_check",
                description="Check age range",
                rule_type="range_check",
                column="age",
                parameters={"min_value": 0, "max_value": 120},
                severity="warning"
            ),
            QualityRule(
                name="email_format_check",
                description="Check email format",
                rule_type="format_check",
                column="email",
                parameters={"pattern": r'^[^@]+@[^@]+\.[^@]+$'},
                severity="error"
            )
        ]
        
        for rule in rules:
            quality_engine.add_rule(rule)
        
        # Check the dataframe
        issues = quality_engine.check_dataframe(sample_dataframe)
        
        # Should pass all checks (no issues expected)
        assert len(issues) == 0
        
        # Test with problematic data
        problematic_df = pd.DataFrame({
            'id': [1, 2, 1, 3],  # Duplicate
            'name': ['Alice', 'Bob', 'Charlie', 'David'],
            'age': [25, 30, 150, 40],  # Out of range
            'email': ['alice@example.com', 'invalid-email', 'charlie@example.com', 'david@example.com'], 
            'score': [None, 90, None, 88]  # 2/4 nulls = 50%
        })
        
        issues = quality_engine.check_dataframe(problematic_df)
        
        # Should detect multiple issues
        assert len(issues) > 0
        
        # Check for specific issue types
        uniqueness_issues = [i for i in issues if i.issue_type == 'uniqueness_check']
        range_issues = [i for i in issues if i.issue_type == 'range_check']
        format_issues = [i for i in issues if i.issue_type == 'format_check']
        null_issues = [i for i in issues if i.issue_type == 'null_check']
        
        assert len(uniqueness_issues) > 0
        assert len(range_issues) > 0
        assert len(format_issues) > 0
        assert len(null_issues) > 0
    
    def test_quality_summary_integration(self, quality_engine):
        """Test quality summary with real data."""
        # Add rules
        quality_engine.add_rule(QualityRule(
            name="null_check",
            description="Check for null values",
            rule_type="null_check",
            parameters={"max_null_percentage": 50.0},
            severity="warning"
        ))
        
        # Create dataframe with issues
        df = pd.DataFrame({
            'A': [1, 2, None, 4, 5],
            'B': [None, None, None, None, None],  # 100% nulls
            'C': [1, 2, 3, 4, 5]  # No issues
        })
        
        quality_engine.check_dataframe(df)
        summary = quality_engine.get_quality_summary()
        
        assert summary['total_issues'] > 0
        assert 'warning' in summary['issues_by_severity']
        assert 'null_check' in summary['issues_by_type']
        assert summary['overall_status'] in ['pass', 'warning', 'fail']
        assert summary['affected_rows_total'] > 0 