# Skill Creator - Meta Skill for Creating New Skills

## Purpose
Guide for creating effective, well-structured skills that can be used by the Librarian Agent.

## What is a Skill?

A skill is a markdown document that provides:
1. **Domain expertise** - Specialized knowledge in a specific area
2. **Best practices** - Guidelines and recommendations
3. **Code examples** - Practical implementation samples
4. **Reference material** - Quick lookup information

## Skill File Structure

```
skills/
├── public/           # Core skills available to all users
│   └── skill-name/
│       ├── SKILL.md  # Main skill document
│       └── assets/   # Optional supporting files
└── examples/         # Example/template skills
    └── skill-name/
        └── SKILL.md
```

## SKILL.md Template

```markdown
# [Skill Name] - [Brief Description]

## Purpose
[1-2 sentences explaining what this skill helps with]

## Capabilities
- [Capability 1]
- [Capability 2]
- [Capability 3]

## Best Practices

### [Category 1]
1. [Practice 1]
2. [Practice 2]
3. [Practice 3]

### [Category 2]
- [Guideline 1]
- [Guideline 2]

## Code Examples

### [Example Title]

\`\`\`[language]
[Code example with comments]
\`\`\`

### [Another Example]

\`\`\`[language]
[Code example]
\`\`\`

## Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| [Problem 1] | [Fix 1] |
| [Problem 2] | [Fix 2] |

## Quick Reference

[Tables, cheat sheets, or quick lookup information]

## Dependencies

\`\`\`bash
[Installation commands]
\`\`\`

## References
- [Link to documentation]
- [Link to tutorials]
```

## Writing Effective Skills

### 1. Focus on Actionable Content
- Provide practical examples, not just theory
- Include copy-paste ready code
- Show common use cases

### 2. Structure for Scanability
- Use clear headings (H2, H3)
- Keep paragraphs short
- Use lists for multiple items
- Include tables for comparisons

### 3. Include Edge Cases
- Document common pitfalls
- Provide troubleshooting tips
- Show error handling

### 4. Keep It Current
- Include version information
- Note deprecated features
- Update when APIs change

### 5. Optimize for AI Retrieval
- Use consistent terminology
- Include synonyms in descriptions
- Add relevant keywords naturally

## Skill Categories

| Category | Purpose | Examples |
|----------|---------|----------|
| **Document** | File format manipulation | docx, pptx, xlsx, pdf |
| **Design** | UI/UX and visual design | frontend-design, theme-factory |
| **Integration** | External service connections | github, slack, database |
| **Language** | Programming language guides | python, javascript, sql |
| **Framework** | Framework-specific guidance | react, fastapi, django |
| **Process** | Workflow and methodology | testing, deployment, code-review |

## Skill Detection Keywords

Skills are detected based on keywords in user queries. Include common terms:

```python
# Good - includes multiple related terms
"Keywords: excel, xlsx, spreadsheet, workbook, cells, formulas"

# Also good - natural language variations
"For creating and editing Excel files, spreadsheets, and workbooks"
```

## Example: Creating a Database Skill

```markdown
# Database Skill - SQL & NoSQL Expert

## Purpose
Guide for designing, querying, and optimizing databases.

## Capabilities
- Write efficient SQL queries
- Design normalized schemas
- Implement indexes properly
- Handle migrations safely
- Work with ORMs

## Best Practices

### Schema Design
1. Start with 3NF, denormalize for performance
2. Use appropriate data types
3. Add constraints (NOT NULL, UNIQUE, FK)
4. Plan for scale from the start

### Query Optimization
- Use EXPLAIN ANALYZE
- Index columns in WHERE clauses
- Avoid SELECT *
- Use connection pooling

## Code Examples

### PostgreSQL - Basic Query

\`\`\`sql
SELECT
    u.name,
    COUNT(o.id) as order_count,
    SUM(o.total) as total_spent
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
WHERE u.created_at > '2024-01-01'
GROUP BY u.id
HAVING COUNT(o.id) > 5
ORDER BY total_spent DESC
LIMIT 10;
\`\`\`

### Python - SQLAlchemy ORM

\`\`\`python
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True)

engine = create_engine('postgresql://user:pass@localhost/db')
Session = sessionmaker(bind=engine)
\`\`\`

## Common Issues

| Issue | Solution |
|-------|----------|
| N+1 queries | Use eager loading (joinedload) |
| Slow queries | Add appropriate indexes |
| Deadlocks | Consistent lock ordering |
| Connection exhaustion | Use connection pooling |

## Dependencies

\`\`\`bash
pip install sqlalchemy psycopg2-binary alembic
\`\`\`

## References
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
```

## Validating Skills

Before publishing, verify:

- [ ] Clear purpose statement
- [ ] At least 3 code examples
- [ ] Best practices section
- [ ] Common issues documented
- [ ] Dependencies listed
- [ ] References included
- [ ] Proper markdown formatting
- [ ] No sensitive information
