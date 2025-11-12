# Hybrid Search for Resume Generation

## Overview

The Resume Generator uses Weaviate's hybrid search to retrieve the most relevant work experiences for resume generation. Hybrid search combines semantic similarity (vector search) with keyword matching (BM25) to provide optimal retrieval results.

## How It Works

### 1. Search Query Construction

The system builds a search query from job requirements:
- Required skills
- Role description
- Key responsibilities

### 2. Hybrid Search Execution

The query is executed against two collections:
- **WorkLog Collection**: User-created work log entries
- **Chunk Collection**: Document chunks from uploaded files

Both semantic and keyword search are performed simultaneously, with results combined using Weaviate's RELATIVE_SCORE fusion.

### 3. Advanced Ranking Algorithm

Retrieved experiences are re-ranked using a multi-factor algorithm:

| Factor | Weight | Description |
|--------|--------|-------------|
| Base Score | 1.0 | Hybrid search relevance score |
| Skill Match | 0.3 | Bonus for matching required skills |
| Recency | 0.2 | Boost for more recent experiences |
| Content Quality | 0.1 | Preference for detailed content |

**Final Score Formula:**
```
final_score = (base_score × 1.0) + (skill_bonus × 0.3) + (recency_boost × 0.2) + (quality_score × 0.1)
```

## Configuration Parameters

### Alpha Parameter

Controls the balance between semantic and keyword search:

| Value | Type | Best For |
|-------|------|----------|
| 0.0 | Pure Semantic | Conceptual matches, related experiences |
| 0.3 | Semantic-Heavy | Finding similar but not exact matches |
| **0.5** | **Balanced** | **Recommended default for most cases** |
| 0.7 | Keyword-Heavy | Exact skill and term matches |
| 1.0 | Pure Keyword | Specific technical terms |

**Recommendation:** Start with 0.5 and adjust based on results:
- If results are too broad → increase alpha (more keyword-focused)
- If missing relevant experiences → decrease alpha (more semantic)

### Date Range Filtering

Filter experiences to focus on recent work:

```python
date_range_days: int | None = None
```

- `None`: Search all experiences (default)
- `90`: Last 3 months
- `180`: Last 6 months
- `365`: Last year
- `730`: Last 2 years

**Use Case:** When applying for roles requiring current technology experience.

### Recency Boost

Apply time-based scoring boost:

```python
boost_recent: bool = True
```

**Recency Boost Scale:**
- Last 30 days: 1.0 (full boost)
- Last 90 days: 0.8
- Last 180 days: 0.6
- Last 365 days: 0.4
- Older: 0.2

**Recommendation:** Keep enabled (True) unless you want to emphasize older experiences equally.

### Result Limit

Maximum number of experiences to retrieve:

```python
limit: int = 20
```

- Default: 20 experiences
- Minimum: 5 (too few may miss relevant content)
- Maximum: 50 (too many may dilute relevance)

## API Usage

### Generate Resume with Custom Search Parameters

```bash
POST /api/resumes/generate
```

**Request Body:**
```json
{
  "credentials": {
    "deployment": "Local",
    "url": "http://localhost:8080",
    "key": ""
  },
  "job_description": "Senior Python Developer with 5+ years experience...",
  "target_role": "Senior Python Developer",
  "format": "markdown",
  "alpha": 0.5,
  "date_range_days": 365,
  "boost_recent": true,
  "limit": 20
}
```

### Regenerate Resume with Updated Parameters

```bash
POST /api/resumes/{resume_id}/regenerate
```

**Request Body:**
```json
{
  "credentials": {
    "deployment": "Local",
    "url": "http://localhost:8080",
    "key": ""
  },
  "resume_id": "uuid-here",
  "alpha": 0.7,
  "date_range_days": 180,
  "boost_recent": true,
  "limit": 25
}
```

## Tuning Guide

### Scenario 1: Not Finding Relevant Experiences

**Problem:** Resume lacks relevant content despite having matching work logs.

**Solution:**
1. Decrease alpha to 0.3 (more semantic search)
2. Increase limit to 30
3. Remove date_range_days filter
4. Check that work logs contain relevant keywords

### Scenario 2: Too Many Irrelevant Results

**Problem:** Resume includes unrelated experiences.

**Solution:**
1. Increase alpha to 0.7 (more keyword matching)
2. Add date_range_days filter (e.g., 365)
3. Ensure job description has clear required skills
4. Decrease limit to 15

### Scenario 3: Emphasizing Recent Experience

**Problem:** Need to highlight current skills and recent work.

**Solution:**
1. Set date_range_days to 180 or 365
2. Keep boost_recent as True
3. Use alpha 0.5 for balanced search
4. Ensure recent work logs are detailed

### Scenario 4: Highlighting Specific Skills

**Problem:** Need exact matches for technical requirements.

**Solution:**
1. Increase alpha to 0.8 (keyword-heavy)
2. Ensure required skills are clearly listed in job description
3. Tag work logs with extracted_skills
4. Use moderate limit (20-25)

## Ranking Details

### Skill Match Bonus

Calculated as: `matches / total_required_skills`

- Checks both content text and extracted_skills field
- Case-insensitive matching
- Normalized to 0-1 range

**Example:**
- Required skills: ["Python", "Django", "PostgreSQL", "Docker", "AWS"]
- Experience mentions: ["Python", "Django", "AWS"]
- Skill bonus: 3/5 = 0.6

### Content Quality Score

Based on word count:
- < 50 words: Scaled linearly (0.0 to 1.0)
- 50-500 words: Full score (1.0)
- > 500 words: Gradually penalized

**Rationale:** Detailed experiences (100-500 words) provide better context than very short or extremely long entries.

## Best Practices

1. **Start with Defaults:** Use alpha=0.5, boost_recent=True, limit=20
2. **Iterate:** Generate resume, review results, adjust parameters
3. **Document Quality:** Write detailed work logs (100-300 words)
4. **Skill Tagging:** Ensure work logs have extracted_skills populated
5. **Recent Updates:** Keep work logs current for best results
6. **Job Description:** Provide clear, detailed job descriptions with explicit skill requirements

## Performance Considerations

- **Hybrid Search:** Slightly slower than pure vector search but significantly more accurate
- **Ranking:** Minimal overhead (~10ms for 50 experiences)
- **Date Filtering:** Improves performance by reducing search space
- **Optimal Limit:** 20-30 experiences balances quality and speed

## Troubleshooting

### No Results Returned

**Possible Causes:**
1. No work logs or documents ingested
2. Date filter too restrictive
3. Job description doesn't match any content

**Solutions:**
- Check that collections exist and have data
- Remove or expand date_range_days
- Verify embeddings are generated

### Low Relevance Scores

**Possible Causes:**
1. Alpha parameter not optimal
2. Work logs lack detail
3. Skill mismatch

**Solutions:**
- Adjust alpha parameter
- Add more detailed work logs
- Ensure job description is clear

### Slow Performance

**Possible Causes:**
1. Large collections (>10,000 documents)
2. High limit value
3. Complex filters

**Solutions:**
- Use date_range_days to reduce search space
- Decrease limit to 15-20
- Optimize Weaviate index settings

## Future Enhancements

Potential improvements to the hybrid search system:

1. **Dynamic Alpha Tuning:** Automatically adjust alpha based on result quality
2. **User Feedback Loop:** Learn from user selections to improve ranking
3. **Skill Weighting:** Allow different weights for different skills
4. **Context Windows:** Consider surrounding context in chunks
5. **Multi-Stage Retrieval:** Initial broad search followed by refined ranking

## References

- [Weaviate Hybrid Search Documentation](https://weaviate.io/developers/weaviate/search/hybrid)
- [BM25 Algorithm](https://en.wikipedia.org/wiki/Okapi_BM25)
- [Vector Search Fundamentals](https://weaviate.io/developers/weaviate/concepts/vector-index)
