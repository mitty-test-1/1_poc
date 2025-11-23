import json
import re
import logging
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

class ValidationType(Enum):
    REQUIRED = "required"
    FORMAT = "format"
    LENGTH = "length"
    RANGE = "range"
    ENUM = "enum"
    CUSTOM = "custom"

@dataclass
class ValidationRule:
    type: ValidationType
    field: str
    value: Any = None
    message: str = ""
    severity: str = "error"  # error, warning

@dataclass
class ValidationResult:
    valid: bool
    errors: List[str]
    warnings: List[str]
    validated_data: Dict[str, Any]

class ValidationService:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.validation_rules = {
            "user": self._get_user_validation_rules(),
            "conversation": self._get_conversation_validation_rules(),
            "message": self._get_message_validation_rules(),
            "analytics": self._get_analytics_validation_rules()
        }
    
    async def validate_data(self, data_type: str, data: Any, rules: Dict[str, Any] = None) -> ValidationResult:
        """Validate data against specified rules"""
        try:
            # Initialize validation result
            result = ValidationResult(
                valid=True,
                errors=[],
                warnings=[],
                validated_data={}
            )
            
            # Get validation rules
            validation_rules = rules or self.validation_rules.get(data_type, [])
            
            # Validate based on data type
            if data_type == "user":
                await self._validate_user_data(data, result, validation_rules)
            elif data_type == "conversation":
                await self._validate_conversation_data(data, result, validation_rules)
            elif data_type == "message":
                await self._validate_message_data(data, result, validation_rules)
            elif data_type == "analytics":
                await self._validate_analytics_data(data, result, validation_rules)
            else:
                raise ValueError(f"Unsupported data type: {data_type}")
            
            # Set validated data
            result.validated_data = data
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error validating data: {e}")
            raise
    
    def _get_user_validation_rules(self) -> List[ValidationRule]:
        """Get validation rules for user data"""
        return [
            ValidationRule(ValidationType.REQUIRED, "id"),
            ValidationRule(ValidationType.REQUIRED, "email"),
            ValidationRule(ValidationType.FORMAT, "email", r"^[^\s@]+@[^\s@]+\.[^\s@]+$", "Invalid email format"),
            ValidationRule(ValidationType.REQUIRED, "name"),
            ValidationRule(ValidationType.LENGTH, "name", min_value=2, max_value=100, message="Name must be between 2 and 100 characters"),
            ValidationRule(ValidationType.REQUIRED, "password_hash"),
            ValidationRule(ValidationType.LENGTH, "password_hash", min_value=60, max_value=60, message="Password hash must be 60 characters"),
            ValidationRule(ValidationType.ENUM, "role", ["user", "admin"], "Role must be either 'user' or 'admin"),
            ValidationRule(ValidationType.FORMAT, "created_at", r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d{3})?Z?$", "Invalid timestamp format"),
        ]
    
    def _get_conversation_validation_rules(self) -> List[ValidationRule]:
        """Get validation rules for conversation data"""
        return [
            ValidationRule(ValidationType.REQUIRED, "id"),
            ValidationRule(ValidationType.REQUIRED, "user_id"),
            ValidationRule(ValidationType.FORMAT, "user_id", r"^[a-f0-9-]{36}$", "Invalid UUID format"),
            ValidationRule(ValidationType.FORMAT, "admin_id", r"^[a-f0-9-]{36}$", "Invalid UUID format", severity="warning"),
            ValidationRule(ValidationType.LENGTH, "title", min_value=0, max_value=255, message="Title must be less than 255 characters"),
            ValidationRule(ValidationType.ENUM, "status", ["active", "pending", "resolved", "closed"], "Invalid status"),
            ValidationRule(ValidationType.FORMAT, "started_at", r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d{3})?Z?$", "Invalid timestamp format"),
            ValidationRule(ValidationType.FORMAT, "ended_at", r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d{3})?Z?$", "Invalid timestamp format", severity="warning"),
        ]
    
    def _get_message_validation_rules(self) -> List[ValidationRule]:
        """Get validation rules for message data"""
        return [
            ValidationRule(ValidationType.REQUIRED, "id"),
            ValidationRule(ValidationType.REQUIRED, "conversation_id"),
            ValidationRule(ValidationType.FORMAT, "conversation_id", r"^[a-f0-9-]{36}$", "Invalid UUID format"),
            ValidationRule(ValidationType.REQUIRED, "sender_id"),
            ValidationRule(ValidationType.FORMAT, "sender_id", r"^[a-f0-9-]{36}$", "Invalid UUID format"),
            ValidationRule(ValidationType.REQUIRED, "content"),
            ValidationRule(ValidationType.LENGTH, "content", min_value=1, max_value=5000, message="Content must be between 1 and 5000 characters"),
            ValidationRule(ValidationType.ENUM, "message_type", ["text", "image", "file", "system"], "Invalid message type"),
            ValidationRule(ValidationType.FORMAT, "created_at", r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d{3})?Z?$", "Invalid timestamp format"),
        ]
    
    def _get_analytics_validation_rules(self) -> List[ValidationRule]:
        """Get validation rules for analytics data"""
        return [
            ValidationRule(ValidationType.REQUIRED, "summary"),
            ValidationRule(ValidationType.REQUIRED, "daily_stats"),
            ValidationRule(ValidationType.CUSTOM, "summary", self._validate_summary_structure, "Invalid summary structure"),
            ValidationRule(ValidationType.CUSTOM, "daily_stats", self._validate_daily_stats_structure, "Invalid daily stats structure"),
            ValidationRule(ValidationType.CUSTOM, "user_analytics", self._validate_user_analytics_structure, "Invalid user analytics structure"),
        ]
    
    async def _validate_user_data(self, data: Union[Dict, List], result: ValidationResult, rules: List[ValidationRule]):
        """Validate user data"""
        if isinstance(data, list):
            for item in data:
                await self._validate_single_user(item, result, rules)
        else:
            await self._validate_single_user(data, result, rules)
    
    async def _validate_single_user(self, user: Dict, result: ValidationResult, rules: List[ValidationRule]):
        """Validate a single user record"""
        for rule in rules:
            try:
                await self._validate_field(user, rule, result)
            except Exception as e:
                self.logger.error(f"Error validating user field {rule.field}: {e}")
                result.errors.append(f"Validation error for field '{rule.field}': {str(e)}")
                result.valid = False
    
    async def _validate_conversation_data(self, data: Union[Dict, List], result: ValidationResult, rules: List[ValidationRule]):
        """Validate conversation data"""
        if isinstance(data, list):
            for item in data:
                await self._validate_single_conversation(item, result, rules)
        else:
            await self._validate_single_conversation(data, result, rules)
    
    async def _validate_single_conversation(self, conversation: Dict, result: ValidationResult, rules: List[ValidationRule]):
        """Validate a single conversation record"""
        for rule in rules:
            try:
                await self._validate_field(conversation, rule, result)
            except Exception as e:
                self.logger.error(f"Error validating conversation field {rule.field}: {e}")
                if rule.severity == "error":
                    result.errors.append(f"Validation error for field '{rule.field}': {str(e)}")
                    result.valid = False
                else:
                    result.warnings.append(f"Validation warning for field '{rule.field}': {str(e)}")
    
    async def _validate_message_data(self, data: Union[Dict, List], result: ValidationResult, rules: List[ValidationRule]):
        """Validate message data"""
        if isinstance(data, list):
            for item in data:
                await self._validate_single_message(item, result, rules)
        else:
            await self._validate_single_message(data, result, rules)
    
    async def _validate_single_message(self, message: Dict, result: ValidationResult, rules: List[ValidationRule]):
        """Validate a single message record"""
        for rule in rules:
            try:
                await self._validate_field(message, rule, result)
            except Exception as e:
                self.logger.error(f"Error validating message field {rule.field}: {e}")
                result.errors.append(f"Validation error for field '{rule.field}': {str(e)}")
                result.valid = False
    
    async def _validate_analytics_data(self, data: Dict, result: ValidationResult, rules: List[ValidationRule]):
        """Validate analytics data"""
        for rule in rules:
            try:
                if rule.type == ValidationType.CUSTOM:
                    if not rule.value(data, result):
                        result.valid = False
                        if rule.message:
                            result.errors.append(rule.message)
                else:
                    await self._validate_field(data, rule, result)
            except Exception as e:
                self.logger.error(f"Error validating analytics field {rule.field}: {e}")
                result.errors.append(f"Validation error for field '{rule.field}': {str(e)}")
                result.valid = False
    
    async def _validate_field(self, data: Dict, rule: ValidationRule, result: ValidationResult):
        """Validate a single field against a rule"""
        field_value = data.get(rule.field)
        
        # Check if field exists
        if rule.type == ValidationType.REQUIRED:
            if field_value is None or field_value == "":
                raise ValueError(rule.message or f"Field '{rule.field}' is required")
        
        # Skip validation if field is None and not required
        if field_value is None:
            return
        
        # Format validation
        if rule.type == ValidationType.FORMAT:
            if not re.match(rule.value, str(field_value)):
                raise ValueError(rule.message or f"Field '{rule.field}' has invalid format")
        
        # Length validation
        if rule.type == ValidationType.LENGTH:
            str_value = str(field_value)
            min_length = getattr(rule.value, 'min_value', None)
            max_length = getattr(rule.value, 'max_value', None)
            
            if min_length and len(str_value) < min_length:
                raise ValueError(rule.message or f"Field '{rule.field}' must be at least {min_length} characters")
            
            if max_length and len(str_value) > max_length:
                raise ValueError(rule.message or f"Field '{rule.field}' must be at most {max_length} characters")
        
        # Range validation
        if rule.type == ValidationType.RANGE:
            min_value = getattr(rule.value, 'min_value', None)
            max_value = getattr(rule.value, 'max_value', None)
            
            if min_value is not None and field_value < min_value:
                raise ValueError(rule.message or f"Field '{rule.field}' must be at least {min_value}")
            
            if max_value is not None and field_value > max_value:
                raise ValueError(rule.message or f"Field '{rule.field}' must be at most {max_value}")
        
        # Enum validation
        if rule.type == ValidationType.ENUM:
            if field_value not in rule.value:
                raise ValueError(rule.message or f"Field '{rule.field}' must be one of: {', '.join(rule.value)}")
    
    def _validate_summary_structure(self, data: Dict, result: ValidationResult) -> bool:
        """Validate analytics summary structure"""
        required_fields = ["total_conversations", "resolved_conversations", "avg_response_time", "satisfaction_rate"]
        
        for field in required_fields:
            if field not in data:
                result.errors.append(f"Missing required field in summary: {field}")
                return False
        
        # Validate data types
        if not isinstance(data["total_conversations"], int):
            result.errors.append("total_conversations must be an integer")
            return False
        
        if not isinstance(data["resolved_conversations"], int):
            result.errors.append("resolved_conversations must be an integer")
            return False
        
        if not isinstance(data["avg_response_time"], (int, float)):
            result.errors.append("avg_response_time must be a number")
            return False
        
        if not isinstance(data["satisfaction_rate"], (int, float)):
            result.errors.append("satisfaction_rate must be a number")
            return False
        
        # Validate ranges
        if data["total_conversations"] < 0:
            result.errors.append("total_conversations must be non-negative")
            return False
        
        if data["resolved_conversations"] < 0:
            result.errors.append("resolved_conversations must be non-negative")
            return False
        
        if data["avg_response_time"] < 0:
            result.errors.append("avg_response_time must be non-negative")
            return False
        
        if not (0 <= data["satisfaction_rate"] <= 5):
            result.errors.append("satisfaction_rate must be between 0 and 5")
            return False
        
        return True
    
    def _validate_daily_stats_structure(self, data: Dict, result: ValidationResult) -> bool:
        """Validate daily stats structure"""
        if not isinstance(data["daily_stats"], list):
            result.errors.append("daily_stats must be a list")
            return False
        
        for stat in data["daily_stats"]:
            if not isinstance(stat, dict):
                result.errors.append("Each daily stat must be an object")
                return False
            
            required_fields = ["date", "conversations", "resolved", "avg_response_time"]
            for field in required_fields:
                if field not in stat:
                    result.errors.append(f"Missing required field in daily stat: {field}")
                    return False
            
            # Validate data types
            if not isinstance(stat["date"], str):
                result.errors.append("date must be a string")
                return False
            
            if not isinstance(stat["conversations"], int):
                result.errors.append("conversations must be an integer")
                return False
            
            if not isinstance(stat["resolved"], int):
                result.errors.append("resolved must be an integer")
                return False
            
            if not isinstance(stat["avg_response_time"], (int, float)):
                result.errors.append("avg_response_time must be a number")
                return False
        
        return True
    
    def _validate_user_analytics_structure(self, data: Dict, result: ValidationResult) -> bool:
        """Validate user analytics structure"""
        if not isinstance(data["user_analytics"], dict):
            result.errors.append("user_analytics must be an object")
            return False
        
        required_fields = ["new_users", "active_users", "returning_users"]
        for field in required_fields:
            if field not in data["user_analytics"]:
                result.errors.append(f"Missing required field in user analytics: {field}")
                return False
        
        # Validate data types
        for field in required_fields:
            if not isinstance(data["user_analytics"][field], int):
                result.errors.append(f"{field} must be an integer")
                return False
        
        # Validate ranges
        for field in required_fields:
            if data["user_analytics"][field] < 0:
                result.errors.append(f"{field} must be non-negative")
                return False
        
        return True
    
    async def validate_import_file(self, file_content: str, file_type: str) -> ValidationResult:
        """Validate imported file content"""
        try:
            result = ValidationResult(
                valid=True,
                errors=[],
                warnings=[],
                validated_data={}
            )
            
            if file_type == "json":
                try:
                    data = json.loads(file_content)
                    result.validated_data = data
                except json.JSONDecodeError as e:
                    result.valid = False
                    result.errors.append(f"Invalid JSON format: {str(e)}")
                    return result
            
            elif file_type == "csv":
                import csv
                import io
                
                try:
                    csv_reader = csv.DictReader(io.StringIO(file_content))
                    data = list(csv_reader)
                    result.validated_data = data
                except Exception as e:
                    result.valid = False
                    result.errors.append(f"Invalid CSV format: {str(e)}")
                    return result
            
            elif file_type == "xlsx":
                # For Excel files, we'd need pandas to validate
                # For now, just return success
                result.validated_data = {"message": "Excel file validation requires pandas"}
            
            else:
                result.valid = False
                result.errors.append(f"Unsupported file type: {file_type}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error validating import file: {e}")
            raise
    
    async def get_validation_rules(self, data_type: str) -> List[Dict[str, Any]]:
        """Get validation rules for a specific data type"""
        try:
            rules = self.validation_rules.get(data_type, [])
            
            # Convert to dictionary format for API response
            rule_dicts = []
            for rule in rules:
                rule_dict = {
                    "field": rule.field,
                    "type": rule.type.value,
                    "severity": rule.severity
                }
                
                if rule.value:
                    if isinstance(rule.value, str):
                        rule_dict["pattern"] = rule.value
                    elif isinstance(rule.value, list):
                        rule_dict["allowed_values"] = rule.value
                    elif hasattr(rule.value, '__dict__'):
                        rule_dict.update(rule.value.__dict__)
                
                if rule.message:
                    rule_dict["message"] = rule.message
                
                rule_dicts.append(rule_dict)
            
            return rule_dicts
            
        except Exception as e:
            self.logger.error(f"Error getting validation rules: {e}")
            raise
    
    async def add_custom_validation_rule(self, data_type: str, rule: ValidationRule):
        """Add a custom validation rule"""
        try:
            if data_type not in self.validation_rules:
                self.validation_rules[data_type] = []
            
            self.validation_rules[data_type].append(rule)
            self.logger.info(f"Added custom validation rule for {data_type}: {rule.field}")
            
        except Exception as e:
            self.logger.error(f"Error adding custom validation rule: {e}")
            raise
    
    async def remove_validation_rule(self, data_type: str, field: str):
        """Remove a validation rule"""
        try:
            if data_type in self.validation_rules:
                self.validation_rules[data_type] = [
                    rule for rule in self.validation_rules[data_type] 
                    if rule.field != field
                ]
                self.logger.info(f"Removed validation rule for {data_type}: {field}")
            
        except Exception as e:
            self.logger.error(f"Error removing validation rule: {e}")
            raise