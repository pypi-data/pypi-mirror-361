"""
Data quality engine for detecting issues and validating data.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass
import yaml
import re

from ..utils.schema import capture_schema, detect_schema_drift


@dataclass
class QualityRule:
    """A data quality rule definition."""
    
    name: str
    description: str
    rule_type: str  # 'null_check', 'range_check', 'uniqueness', 'format_check', 'custom'
    column: Optional[str] = None
    parameters: Dict[str, Any] = None
    custom_function: Optional[Callable] = None
    severity: str = 'warning'  # 'info', 'warning', 'error'
    
    def __post_init__(self):
        if self.parameters is None:
            self.parameters = {}


@dataclass
class QualityIssue:
    """A detected data quality issue."""
    
    rule_name: str
    issue_type: str
    description: str
    severity: str
    affected_rows: int
    affected_columns: List[str]
    details: Dict[str, Any]
    timestamp: float


class QualityEngine:
    """
    Data quality engine for detecting issues and validating data.
    
    This class provides comprehensive data quality checking capabilities
    including built-in rules and custom validation functions.
    """
    
    def __init__(self):
        self.rules: List[QualityRule] = []
        self.issues: List[QualityIssue] = []
        self.built_in_rules = self._initialize_built_in_rules()
        
    def _initialize_built_in_rules(self) -> Dict[str, Callable]:
        """Initialize built-in quality check functions."""
        return {
            'null_check': self._check_nulls,
            'range_check': self._check_range,
            'uniqueness_check': self._check_uniqueness,
            'format_check': self._check_format,
            'completeness_check': self._check_completeness,
            'consistency_check': self._check_consistency,
            'freshness_check': self._check_freshness
        }
    
    def add_rule(self, rule: QualityRule) -> None:
        """
        Add a quality rule to the engine.
        
        Args:
            rule: QualityRule object to add.
        """
        self.rules.append(rule)
    
    def load_rules_from_yaml(self, yaml_file: str) -> None:
        """
        Load quality rules from a YAML file.
        
        Args:
            yaml_file: Path to the YAML file containing rules.
        """
        try:
            with open(yaml_file, 'r') as f:
                rules_data = yaml.safe_load(f)
            
            for rule_data in rules_data.get('rules', []):
                rule = QualityRule(
                    name=rule_data['name'],
                    description=rule_data.get('description', ''),
                    rule_type=rule_data['type'],
                    column=rule_data.get('column'),
                    parameters=rule_data.get('parameters', {}),
                    severity=rule_data.get('severity', 'warning')
                )
                self.add_rule(rule)
                
        except Exception as e:
            raise ValueError(f"Error loading rules from {yaml_file}: {e}")
    
    def check_dataframe(self, df: pd.DataFrame) -> List[QualityIssue]:
        """
        Check a dataframe against all quality rules.
        
        Args:
            df: Pandas DataFrame to check.
            
        Returns:
            List of detected quality issues.
        """
        self.issues.clear()
        
        for rule in self.rules:
            try:
                if rule.rule_type in self.built_in_rules:
                    check_function = self.built_in_rules[rule.rule_type]
                    issues = check_function(df, rule)
                    self.issues.extend(issues)
                elif rule.custom_function:
                    issues = rule.custom_function(df, rule)
                    self.issues.extend(issues)
            except Exception as e:
                # Create an issue for the rule failure itself
                issue = QualityIssue(
                    rule_name=rule.name,
                    issue_type='rule_execution_error',
                    description=f"Rule execution failed: {str(e)}",
                    severity='error',
                    affected_rows=0,
                    affected_columns=[rule.column] if rule.column else [],
                    details={'error': str(e)},
                    timestamp=pd.Timestamp.now().timestamp()
                )
                self.issues.append(issue)
        
        return self.issues
    
    def _check_nulls(self, df: pd.DataFrame, rule: QualityRule) -> List[QualityIssue]:
        """Check for null values in specified columns."""
        issues = []
        
        if rule.column:
            columns = [rule.column]
        else:
            columns = df.columns
        
        max_null_percentage = rule.parameters.get('max_null_percentage', 50.0)
        
        for col in columns:
            if col in df.columns:
                null_count = df[col].isnull().sum()
                null_percentage = (null_count / len(df)) * 100
                
                if null_percentage >= max_null_percentage:
                    issue = QualityIssue(
                        rule_name=rule.name,
                        issue_type='null_check',
                        description=f"Column '{col}' has {null_percentage:.1f}% null values (max: {max_null_percentage}%)",
                        severity=rule.severity,
                        affected_rows=null_count,
                        affected_columns=[col],
                        details={
                            'null_count': null_count,
                            'null_percentage': null_percentage,
                            'max_allowed': max_null_percentage
                        },
                        timestamp=pd.Timestamp.now().timestamp()
                    )
                    issues.append(issue)
        
        return issues
    
    def _check_range(self, df: pd.DataFrame, rule: QualityRule) -> List[QualityIssue]:
        """Check for values within specified ranges."""
        issues = []
        
        if not rule.column or rule.column not in df.columns:
            return issues
        
        min_value = rule.parameters.get('min_value')
        max_value = rule.parameters.get('max_value')
        
        if min_value is not None:
            below_min = df[rule.column] < min_value
            if below_min.any():
                issue = QualityIssue(
                    rule_name=rule.name,
                    issue_type='range_check',
                    description=f"Column '{rule.column}' has values below minimum {min_value}",
                    severity=rule.severity,
                    affected_rows=below_min.sum(),
                    affected_columns=[rule.column],
                    details={
                        'min_value': min_value,
                        'violating_count': below_min.sum()
                    },
                    timestamp=pd.Timestamp.now().timestamp()
                )
                issues.append(issue)
        
        if max_value is not None:
            above_max = df[rule.column] > max_value
            if above_max.any():
                issue = QualityIssue(
                    rule_name=rule.name,
                    issue_type='range_check',
                    description=f"Column '{rule.column}' has values above maximum {max_value}",
                    severity=rule.severity,
                    affected_rows=above_max.sum(),
                    affected_columns=[rule.column],
                    details={
                        'max_value': max_value,
                        'violating_count': above_max.sum()
                    },
                    timestamp=pd.Timestamp.now().timestamp()
                )
                issues.append(issue)
        
        return issues
    
    def _check_uniqueness(self, df: pd.DataFrame, rule: QualityRule) -> List[QualityIssue]:
        """Check for uniqueness constraints."""
        issues = []
        
        if not rule.column or rule.column not in df.columns:
            return issues
        
        duplicate_count = df[rule.column].duplicated().sum()
        
        if duplicate_count > 0:
            issue = QualityIssue(
                rule_name=rule.name,
                issue_type='uniqueness_check',
                description=f"Column '{rule.column}' has {duplicate_count} duplicate values",
                severity=rule.severity,
                affected_rows=duplicate_count,
                affected_columns=[rule.column],
                details={
                    'duplicate_count': duplicate_count,
                    'total_rows': len(df)
                },
                timestamp=pd.Timestamp.now().timestamp()
            )
            issues.append(issue)
        
        return issues
    
    def _check_format(self, df: pd.DataFrame, rule: QualityRule) -> List[QualityIssue]:
        """Check for format compliance."""
        issues = []
        
        if not rule.column or rule.column not in df.columns:
            return issues
        
        pattern = rule.parameters.get('pattern')
        if not pattern:
            return issues
        
        try:
            regex = re.compile(pattern)
            invalid_mask = ~df[rule.column].astype(str).str.match(regex, na=False)
            invalid_count = invalid_mask.sum()
            
            if invalid_count > 0:
                issue = QualityIssue(
                    rule_name=rule.name,
                    issue_type='format_check',
                    description=f"Column '{rule.column}' has {invalid_count} values not matching pattern '{pattern}'",
                    severity=rule.severity,
                    affected_rows=invalid_count,
                    affected_columns=[rule.column],
                    details={
                        'pattern': pattern,
                        'invalid_count': invalid_count
                    },
                    timestamp=pd.Timestamp.now().timestamp()
                )
                issues.append(issue)
        except Exception as e:
            issue = QualityIssue(
                rule_name=rule.name,
                issue_type='format_check_error',
                description=f"Error checking format for column '{rule.column}': {str(e)}",
                severity='error',
                affected_rows=0,
                affected_columns=[rule.column],
                details={'error': str(e)},
                timestamp=pd.Timestamp.now().timestamp()
            )
            issues.append(issue)
        
        return issues
    
    def _check_completeness(self, df: pd.DataFrame, rule: QualityRule) -> List[QualityIssue]:
        """Check for data completeness."""
        issues = []
        
        required_columns = rule.parameters.get('required_columns', [])
        if not required_columns:
            return issues
        
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            issue = QualityIssue(
                rule_name=rule.name,
                issue_type='completeness_check',
                description=f"Missing required columns: {missing_columns}",
                severity=rule.severity,
                affected_rows=len(df),
                affected_columns=missing_columns,
                details={
                    'missing_columns': missing_columns,
                    'required_columns': required_columns
                },
                timestamp=pd.Timestamp.now().timestamp()
            )
            issues.append(issue)
        
        return issues
    
    def _check_consistency(self, df: pd.DataFrame, rule: QualityRule) -> List[QualityIssue]:
        """Check for data consistency."""
        issues = []
        
        # This is a placeholder for more complex consistency checks
        # Could include cross-column validations, business rule checks, etc.
        
        return issues
    
    def _check_freshness(self, df: pd.DataFrame, rule: QualityRule) -> List[QualityIssue]:
        """Check for data freshness."""
        issues = []
        
        # This would typically check if data is within expected time ranges
        # Implementation depends on specific use case
        
        return issues
    
    def get_quality_summary(self) -> Dict[str, Any]:
        """
        Get a summary of quality check results.
        
        Returns:
            Dictionary containing quality summary.
        """
        if not self.issues:
            return {
                'total_issues': 0,
                'issues_by_severity': {},
                'issues_by_type': {},
                'overall_status': 'pass'
            }
        
        issues_by_severity = {}
        issues_by_type = {}
        
        for issue in self.issues:
            # Count by severity
            issues_by_severity[issue.severity] = issues_by_severity.get(issue.severity, 0) + 1
            
            # Count by type
            issues_by_type[issue.issue_type] = issues_by_type.get(issue.issue_type, 0) + 1
        
        # Determine overall status
        if any(issue.severity == 'error' for issue in self.issues):
            overall_status = 'fail'
        elif any(issue.severity == 'warning' for issue in self.issues):
            overall_status = 'warning'
        else:
            overall_status = 'pass'
        
        return {
            'total_issues': len(self.issues),
            'issues_by_severity': issues_by_severity,
            'issues_by_type': issues_by_type,
            'overall_status': overall_status,
            'affected_rows_total': sum(issue.affected_rows for issue in self.issues)
        }
    
    def export_issues(self, format: str = 'json') -> str:
        """
        Export quality issues in various formats.
        
        Args:
            format: Export format ('json', 'yaml', 'csv').
            
        Returns:
            String representation of the issues.
        """
        if format == 'json':
            import json
            return json.dumps([issue.__dict__ for issue in self.issues], indent=2)
        elif format == 'yaml':
            return yaml.dump([issue.__dict__ for issue in self.issues], default_flow_style=False)
        elif format == 'csv':
            import io
            import csv
            
            output = io.StringIO()
            if self.issues:
                writer = csv.DictWriter(output, fieldnames=self.issues[0].__dict__.keys())
                writer.writeheader()
                for issue in self.issues:
                    writer.writerow(issue.__dict__)
            return output.getvalue()
        else:
            raise ValueError(f"Unsupported format: {format}") 