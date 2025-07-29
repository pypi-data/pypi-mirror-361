# Nia Knowledge Agent Integration Rules

## Overview
These rules guide AI assistants in effectively using Nia's knowledge search capabilities for codebase analysis, documentation search, and AI-powered research.

Note: Nia is just "Nia" - not an acronym. It's the name of the knowledge search platform.

## Core Principles

### 1. Repository Management
- **Always check indexed repositories** before searching with `list_repositories`
- **Proactively suggest indexing** when users mention GitHub repositories
- **Monitor indexing status** using `check_repository_status` for ongoing operations
- **Index relevant repositories** discovered during web searches

### 2. Search Strategy Selection

#### Use `nia_web_search` for:
- Finding specific repositories or documentation
- Quick lookups and discovery tasks
- Trending content searches
- Finding similar content to a known URL
- Simple, direct queries

#### Use `nia_deep_research_agent` for:
- Comparative analysis (X vs Y vs Z)
- Evaluating pros and cons
- Complex questions requiring synthesis
- Structured output needs (tables, lists)
- Questions with "best", "which is better", "compare"

### 3. Query Optimization
- **Use natural language queries** - Form complete questions, not just keywords
- **Be specific and detailed** - "How does authentication work in NextAuth.js?" not "auth nextauth"
- **Include context** - Mention specific technologies, frameworks, or use cases
- **Leverage repository context** - Specify repositories when searching indexed codebases

### 4. API Usage Best Practices
- **Handle rate limits gracefully** - Free tier has 25 API request limit
- **Cache results mentally** - Avoid redundant searches in the same conversation
- **Batch operations** - Index multiple related repositories together
- **Monitor status efficiently** - Check status periodically, not continuously

### 5. Result Interpretation
- **Provide actionable next steps** - Always suggest how to use the results
- **Extract indexable content** - Identify repositories and docs from search results
- **Format for readability** - Use markdown formatting for clear presentation
- **Include sources** - Always show where information comes from

### 6. Error Handling
- **Explain API limits clearly** - Help users understand free tier limitations
- **Suggest alternatives** - Provide workarounds when hitting limits
- **Report issues helpfully** - Include enough context for debugging
- **Guide to solutions** - Link to upgrade options when appropriate

## Workflow Patterns

### Pattern 1: New Project Research
1. Use `nia_deep_research_agent` to understand the technology landscape
2. Use `nia_web_search` to find specific implementations
3. Index discovered repositories for detailed analysis
4. Search indexed codebases for implementation details

### Pattern 2: Codebase Understanding
1. Check if repository is already indexed with `list_repositories`
2. If not indexed, use `index_repository` and wait for completion
3. Use `search_codebase` with specific technical questions
4. Include code snippets and file references in responses

### Pattern 3: Documentation Search
1. Index documentation sites with `index_documentation`
   - If no URL patterns specified, default to `["/*"]` for entire site
   - Or ask user: "Which sections should I index? (e.g., /docs/*, /api/*, or /* for everything)"
   - Common patterns: `["/docs/*", "/api/*", "/guide/*", "/reference/*"]`
2. Use URL patterns to focus on relevant sections
3. Search with `search_documentation` for specific topics
4. Combine with code searches for complete understanding

### Pattern 4: Technology Comparison
1. Start with `nia_deep_research_agent` for structured comparison
2. Follow up with `nia_web_search` for specific examples
3. Index key repositories from each option
4. Search codebases to understand implementation differences

## Configuration

### Environment Setup
- **API Key**: Set `NIA_API_KEY` environment variable
- **Never hardcode API keys** in code or configuration files
- **Use .env files** for local development
- **Secure key storage** in production environments

### Project Structure
When initialized, Nia projects should have:
```
.nia/
├── config.json          # Project-specific settings
├── indexed_repos.json   # Track indexed repositories
└── search_history.json  # Cache common queries
```

## Integration Guidelines

### With Version Control
- Add `.nia/cache/` to `.gitignore`
- Commit `.nia/config.json` for team sharing
- Document indexed repositories in README

### With CI/CD
- Set `NIA_API_KEY` as secret environment variable
- Run repository indexing in setup phase
- Cache search results between builds

### With IDEs
- Configure workspace-specific indexed repositories
- Set up quick search shortcuts
- Integrate with code navigation features

## Best Practices Summary

1. **Be Proactive** - Suggest indexing relevant content
2. **Be Efficient** - Use the right tool for each query type  
3. **Be Helpful** - Provide clear next steps and context
4. **Be Smart** - Learn from search results to improve future queries
5. **Be Considerate** - Respect API limits and guide users appropriately

Remember: Nia is designed to make AI-powered code and documentation search accessible. Help users unlock its full potential by following these guidelines.