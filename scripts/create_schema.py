#\!/usr/bin/env python3
"""
Create or update Weaviate schema for AI_v1 class.

Usage:
    python scripts/create_schema.py [--force] [--weaviate-url URL]

Options:
    --force           Delete existing class and recreate (WARNING: deletes all data)
    --weaviate-url    Weaviate instance URL (default: http://localhost:8080)
"""

import json
import sys
import argparse
from pathlib import Path
import weaviate
from weaviate.classes.config import Configure


def load_schema(schema_path: Path) -> dict:
    """Load schema JSON from file."""
    with open(schema_path, 'r') as f:
        return json.load(f)


def class_exists(client: weaviate.WeaviateClient, class_name: str) -> bool:
    """Check if a class already exists in Weaviate."""
    try:
        schema = client.schema.get()
        return any(c['class'] == class_name for c in schema.get('classes', []))
    except Exception as e:
        print(f"Error checking class existence: {e}")
        return False


def create_class(client: weaviate.WeaviateClient, schema: dict, force: bool = False):
    """Create or update the AI_v1 class."""
    class_name = schema['class']
    
    if class_exists(client, class_name):
        if force:
            print(f"⚠️  Class '{class_name}' exists. Deleting (--force mode)...")
            try:
                client.schema.delete_class(class_name)
                print(f"✅ Deleted class '{class_name}'")
            except Exception as e:
                print(f"❌ Error deleting class: {e}")
                sys.exit(1)
        else:
            print(f"ℹ️  Class '{class_name}' already exists. Use --force to recreate.")
            print("   (WARNING: --force will delete all existing data)")
            sys.exit(0)
    
    # Create the class
    print(f"Creating class '{class_name}'...")
    try:
        client.schema.create_class(schema)
        print(f"✅ Successfully created class '{class_name}'")
        
        # Verify creation
        if class_exists(client, class_name):
            print(f"✅ Verified: Class '{class_name}' is now in schema")
            
            # Display schema summary
            print("\n📋 Schema Summary:")
            print(f"   Class: {class_name}")
            print(f"   Description: {schema.get('description', 'N/A')}")
            print(f"   Vectorizer: {schema.get('vectorizer', 'N/A')}")
            print(f"   Properties: {len(schema.get('properties', []))}")
            print("\n   Properties:")
            for prop in schema.get('properties', []):
                print(f"     - {prop['name']} ({', '.join(prop['dataType'])}): {prop.get('description', '')}")
        else:
            print(f"⚠️  Warning: Class creation succeeded but verification failed")
            
    except Exception as e:
        print(f"❌ Error creating class: {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description='Create or update Weaviate schema for AI_v1 class'
    )
    parser.add_argument(
        '--force',
        action='store_true',
        help='Delete existing class and recreate (WARNING: deletes all data)'
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
        print(f"   Make sure Weaviate is running at {args.weaviate_url}")
        sys.exit(1)
    
    try:
        # Create or update class
        create_class(client, schema, force=args.force)
    finally:
        client.close()
        print("\n🔌 Disconnected from Weaviate")


if __name__ == '__main__':
    main()
