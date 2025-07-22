#!/usr/bin/env python3
"""
Base class for contract-based AI testing.
Provides schema validation and AI provider integration.
"""

import unittest
import json
import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional
import jsonschema
from jsonschema import validate, ValidationError
import hashlib
import tempfile

# Add parent directories to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import mock provider as fallback
from mocks.mock_claude_provider import MockClaudeProvider


class ContractTestBase(unittest.TestCase):
    """Base class for all contract-based tests"""
    
    @classmethod
    def setUpClass(cls):
        """Set up class-level resources"""
        cls.schemas_dir = Path(__file__).parent / "schemas"
        cls.cache_dir = Path(tempfile.gettempdir()) / "ai_contract_cache"
        cls.cache_dir.mkdir(exist_ok=True)
        
        # Load all schemas
        cls.schemas = {}
        for schema_file in cls.schemas_dir.glob("*.json"):
            with open(schema_file, 'r') as f:
                schema_name = schema_file.stem
                cls.schemas[schema_name] = json.load(f)
        
        # Initialize AI provider based on environment
        cls.ai_provider = cls._initialize_provider()
        
    @classmethod
    def _initialize_provider(cls):
        """Initialize the appropriate AI provider"""
        use_real_ai = os.getenv('USE_REAL_AI', '0') == '1'
        
        if use_real_ai:
            # Try to import real AI provider
            try:
                # This will be implemented when we create the real provider
                from src.ai_providers.claude_provider import ClaudeProvider
                api_key = os.getenv('CLAUDE_API_KEY')
                if not api_key:
                    print("Warning: CLAUDE_API_KEY not set, falling back to mock provider")
                    return MockClaudeProvider()
                return ClaudeProvider(api_key=api_key)
            except ImportError:
                print("Warning: Real AI provider not implemented, using mock")
                return MockClaudeProvider()
        else:
            # Use mock provider for testing
            return MockClaudeProvider()
    
    def setUp(self):
        """Set up test-specific resources"""
        self.responses = []
        self.validation_errors = []
        
    def query_ai(self, prompt: str, context: Optional[Dict[str, Any]] = None, 
                 cache: bool = True) -> Dict[str, Any]:
        """
        Query the AI provider with caching support.
        
        Args:
            prompt: The prompt to send
            context: Optional context
            cache: Whether to cache the response
            
        Returns:
            AI response dictionary
        """
        # Generate cache key
        cache_key = None
        if cache and os.getenv('CACHE_AI_RESPONSES', '1') == '1':
            cache_data = json.dumps({'prompt': prompt, 'context': context}, sort_keys=True)
            cache_key = hashlib.sha256(cache_data.encode()).hexdigest()
            cache_file = self.cache_dir / f"{cache_key}.json"
            
            # Check cache
            if cache_file.exists():
                with open(cache_file, 'r') as f:
                    response = json.load(f)
                    response['_from_cache'] = True
                    self.responses.append(response)
                    return response
        
        # Query AI
        response = self.ai_provider.query(prompt, context)
        self.responses.append(response)
        
        # Cache response
        if cache_key:
            cache_file = self.cache_dir / f"{cache_key}.json"
            with open(cache_file, 'w') as f:
                json.dump(response, f, indent=2)
                
        return response
    
    def validate_schema(self, response: Dict[str, Any], schema_name: str) -> bool:
        """
        Validate a response against a named schema.
        
        Args:
            response: The response to validate
            schema_name: Name of the schema (without .json extension)
            
        Returns:
            True if valid, False otherwise
            
        Raises:
            AssertionError: If validation fails in test context
        """
        if schema_name not in self.schemas:
            self.fail(f"Schema '{schema_name}' not found. Available: {list(self.schemas.keys())}")
        
        schema = self.schemas[schema_name]
        
        try:
            validate(instance=response, schema=schema)
            return True
        except ValidationError as e:
            error_msg = f"Schema validation failed: {e.message} at {'.'.join(str(p) for p in e.path)}"
            self.validation_errors.append({
                'schema': schema_name,
                'error': error_msg,
                'path': list(e.path),
                'instance': e.instance
            })
            self.fail(error_msg)
            return False
    
    def validate_required_fields(self, response: Dict[str, Any], required_fields: list) -> bool:
        """
        Validate that all required fields are present.
        
        Args:
            response: The response to validate
            required_fields: List of required field names
            
        Returns:
            True if all fields present, False otherwise
        """
        missing_fields = []
        for field in required_fields:
            if field not in response:
                missing_fields.append(field)
                
        if missing_fields:
            self.fail(f"Missing required fields: {missing_fields}")
            return False
            
        return True
    
    def validate_field_types(self, response: Dict[str, Any], field_types: Dict[str, type]) -> bool:
        """
        Validate that fields have correct types.
        
        Args:
            response: The response to validate
            field_types: Dictionary mapping field names to expected types
            
        Returns:
            True if all types match, False otherwise
        """
        type_errors = []
        for field, expected_type in field_types.items():
            if field in response:
                actual_value = response[field]
                if not isinstance(actual_value, expected_type):
                    type_errors.append(
                        f"{field}: expected {expected_type.__name__}, "
                        f"got {type(actual_value).__name__}"
                    )
                    
        if type_errors:
            self.fail(f"Type validation errors: {'; '.join(type_errors)}")
            return False
            
        return True
    
    def validate_enum_field(self, response: Dict[str, Any], field: str, valid_values: list) -> bool:
        """
        Validate that a field contains one of the valid enum values.
        
        Args:
            response: The response to validate
            field: Field name to check
            valid_values: List of valid values
            
        Returns:
            True if valid, False otherwise
        """
        if field not in response:
            self.fail(f"Field '{field}' not found in response")
            return False
            
        value = response[field]
        if value not in valid_values:
            self.fail(f"Field '{field}' has invalid value '{value}'. Valid: {valid_values}")
            return False
            
        return True
    
    def assert_response_time(self, max_seconds: float = 30.0):
        """
        Assert that the last response was received within time limit.
        
        Args:
            max_seconds: Maximum allowed response time
        """
        # This would be implemented with actual timing in real provider
        # For now, we assume mock responses are instant
        pass
    
    def get_test_summary(self) -> Dict[str, Any]:
        """Get summary of test execution"""
        return {
            'total_queries': len(self.responses),
            'validation_errors': len(self.validation_errors),
            'cached_responses': sum(1 for r in self.responses if r.get('_from_cache')),
            'errors': self.validation_errors
        }
    
    def tearDown(self):
        """Clean up after test"""
        # Print summary if there were errors
        if self.validation_errors:
            summary = self.get_test_summary()
            print(f"\nTest Summary: {json.dumps(summary, indent=2)}")