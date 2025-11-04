# Weaviate Schema for AI_v1

## Overview

This directory contains the Weaviate schema definition for the `AI_v1` class, which stores Australian Family Law case law documents with hybrid search support.

## Schema Version

- **Current Version**: 1.0.0
- **Last Updated**: 2025-11-05
- **Weaviate Compatibility**: v1.24+

## Schema File

- `ai_v1_schema.json`: Complete schema definition for the AI_v1 class

## Properties

### Core Metadata

| Property | Type | Description | Indexed | Vectorized |
|----------|------|-------------|---------|------------|
| `case_name` | text | Full case name/title | ✅ | ✅ |
| `citation` | text | Official citation (e.g., [2024] FamCA 123) | ✅ | ❌ |
| `court` | text | Court name | ✅ | ❌ |
| `jurisdiction` | text | Jurisdiction/state (NSW, VIC, etc.) | ✅ | ❌ |
| `decision_date` | date | Date of decision (ISO 8601) | ✅ | ❌ |

### Content

| Property | Type | Description | Indexed | Vectorized |
|----------|------|-------------|---------|------------|
| `data` | text | Main judgment text (paragraph/section) | Search only | ✅ |
| `paragraph_refs` | text[] | Paragraph numbers in this chunk | ❌ | ❌ |

### Source Tracking

| Property | Type | Description | Indexed | Vectorized |
|----------|------|-------------|---------|------------|
| `source_uri` | text | Source URL (e.g., AUSTLII link) | ✅ | ❌ |
| `legal_topics` | text[] | Family law topics/categories | ✅ | ❌ |
| `chunk_index` | int | Index of this chunk (0-based) | ✅ | ❌ |
| `total_chunks` | int | Total chunks for this case | ❌ | ❌ |
| `ingestion_date` | date | When document was ingested | ✅ | ❌ |

## Vectorizer Configuration

- **Vectorizer**: `text2vec-openai`
- **Model**: `text-embedding-3-small`
- **Model Version**: 003
- **Distance Metric**: Cosine

### Vectorized Properties
Only `case_name` and `data` are vectorized for semantic search. Metadata fields are excluded to optimize embedding quality and cost.

## Index Configuration

### Vector Index (HNSW)
- **Max Connections**: 64
- **EF Construction**: 128
- **Dynamic EF**: 100-500 (factor: 8)
- **Distance**: Cosine

### Inverted Index (BM25)
- **b**: 0.75
- **k1**: 1.2
- **Stopwords**: English preset

## Usage

### Create Schema

```bash
# Create schema (will fail if class exists)
python scripts/create_schema.py

# Force recreate (WARNING: deletes all data)
python scripts/create_schema.py --force

# Use custom Weaviate URL
python scripts/create_schema.py --weaviate-url http://production:8080
```

### Validate Schema

```bash
# Validate deployed schema matches definition
python scripts/validate_schema.py

# Validate against custom Weaviate instance
python scripts/validate_schema.py --weaviate-url http://production:8080
```

## Migration Notes

### From Legacy Schema

If migrating from the legacy schema (no explicit properties), you'll need to:

1. **Backup existing data**:
   ```bash
   # Export data (implement export script if needed)
   python scripts/export_data.py --output backup.jsonl
   ```

2. **Recreate schema**:
   ```bash
   python scripts/create_schema.py --force
   ```

3. **Re-ingest data** with new properties:
   ```bash
   python scripts/ingest.py --input backup.jsonl
   ```

### Schema Changes

When updating the schema:

1. Update `ai_v1_schema.json`
2. Increment version in this README
3. Document changes in CHANGELOG.md
4. Test with `validate_schema.py`
5. Plan migration if breaking changes

## Design Decisions

### Why text-embedding-3-small?
- Cost-effective for large document corpus
- Sufficient quality for legal text retrieval
- Can upgrade to `text-embedding-3-large` if needed

### Why separate chunk_index and paragraph_refs?
- `chunk_index`: Sequential position for ordering
- `paragraph_refs`: Legal paragraph citations for display

### Why legal_topics as array?
- Cases often span multiple topics (e.g., parenting + property)
- Enables multi-topic filtering

## Australian Family Law Topics

Common values for `legal_topics`:

- `parenting` - Parenting orders, custody, care arrangements
- `property_settlement` - Property division, financial matters
- `s60CC_factors` - Best interests of the child factors
- `relocation` - Relocation disputes
- `child_support` - Child support matters
- `spousal_maintenance` - Spousal/partner maintenance
- `consent_orders` - Consent order applications
- `contravention` - Contravention applications
- `family_violence` - Family violence matters
- `interim_orders` - Interim/urgent orders

## Compliance

- **Data Privacy**: Ensure case data complies with publication restrictions
- **Licensing**: Verify AUSTLII or source terms of use
- **Disclaimers**: This is for training/education, not legal advice

## Support

For schema issues or questions:
- Check `scripts/validate_schema.py` output
- Review Weaviate logs
- Consult Weaviate documentation: https://weaviate.io/developers/weaviate
