#\!/usr/bin/env python3
"""
Validate Weaviate schema against the JSON definition.

Usage:
    python scripts/validate_schema.py [--weaviate-url URL]
"""

import json
import sys
import argparse
from pathlib import Path
import weaviate


def load_schema(schema_path: Path) -> dict:
    """Load schema JSON from file."""
    with open(schema_path, 'r') as f:
        return json.load(f)


def validate_schema(client: weaviate.WeaviateClient, expected_schema: dict):
    """Validate that the deployed schema matches the expected schema."""
    class_name = expected_schema['class']
    
    print(f"🔍 Validating schema for class '{class_name}'...")
    
    try:
        deployed_schema = client.schema.get()
        deployed_classes = {c['class']: c for c in deployed_schema.get('classes', [])}
        
        if class_name not in deployed_classes:
            print(f"❌ Class '{class_name}' not found in Weaviate")
            return False
        
        deployed_class = deployed_classes[class_name]
        
        # Validate properties
        expected_props = {p['name']: p for p in expected_schema.get('properties', [])}
        deployed_props = {p['name']: p for p in deployed_class.get('properties', [])}
        
        print(f"\n📋 Property Validation:")
        all_valid = True
        
        # Check for missing properties
        missing = set(expected_props.keys()) - set(deployed_props.keys())
        if missing:
            print(f"  ❌ Missing properties: {', '.join(missing)}")
            all_valid = False
        
        # Check for extra properties
        extra = set(deployed_props.keys()) - set(expected_props.keys())
        if extra:
            print(f"  ⚠️  Extra properties (not in schema file): {', '.join(extra)}")
        
        # Validate each property
        for prop_name, expected_prop in expected_props.items():
            if prop_name not in deployed_props:
                continue
            
            deployed_prop = deployed_props[prop_name]
            
            # Check data type
            if deployed_prop.get('dataType') \!= expected_prop.get('dataType'):
                print(f"  ❌ {prop_name}: dataType mismatch")
                print(f"     Expected: {expected_prop.get('dataType')}")
                print(f"     Deployed: {deployed_prop.get('dataType')}")
                all_valid = False
            else:
                print(f"  ✅ {prop_name}: OK")
        
        # Validate vectorizer
        print(f"\n🔧 Vectorizer Validation:")
        expected_vectorizer = expected_schema.get('vectorizer')
        deployed_vectorizer = deployed_class.get('vectorizer')
        
        if deployed_vectorizer == expected_vectorizer:
            print(f"  ✅ Vectorizer: {deployed_vectorizer}")
        else:
            print(f"  ❌ Vectorizer mismatch")
            print(f"     Expected: {expected_vectorizer}")
            print(f"     Deployed: {deployed_vectorizer}")
            all_valid = False
        
        if all_valid:
            print(f"\n✅ Schema validation passed for '{class_name}'")
        else:
            print(f"\n❌ Schema validation failed for '{class_name}'")
        
        return all_valid
        
    except Exception as e:
        print(f"❌ Error validating schema: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description='Validate Weaviate schema against JSON definition'
    )
    parser.add_argument(
        '--weaviate-url',
        default='http://localhost:8080',
        help='Weaviate instance URL (default: http://localhost:8080)'
    )
    
    args = parser.parse_args()
    
    # Load schema
    schema_path = Path(__file__).parent.parent / 'schema' / 'ai_v1_schema.json'
    if not schema_path.exists():
        print(f"❌ Schema file not found: {schema_path}")
        sys.exit(1)
    
    print(f"📄 Loading schema from: {schema_path}")
    schema = load_schema(schema_path)
    
    # Connect to Weaviate
    print(f"🔌 Connecting to Weaviate at: {args.weaviate_url}")
    try:
        client = weaviate.connect_to_local(host=args.weaviate_url.replace('http://', '').replace(':8080', ''))
        print("✅ Connected to Weaviate")
    except Exception as e:
        print(f"❌ Failed to connect to Weaviate: {e}")
        sys.exit(1)
    
    try:
        # Validate schema
        valid = validate_schema(client, schema)
        sys.exit(0 if valid else 1)
    finally:
        client.close()
        print("\n🔌 Disconnected from Weaviate")


if __name__ == '__main__':
    main()
