# Cypher Queries

## Delete All Nodes for a Knowledge ID

### Full deletion

```cypher
MATCH (n {knowledge_id: "<KNOWLEDGE_ID>"})
DETACH DELETE n
RETURN count(*) AS deletedCount
```

### Batched deletion (5000 at a time)

Run repeatedly until `deletedCount` returns 0.

```cypher
MATCH (n {knowledge_id: "<KNOWLEDGE_ID>"})
WITH n LIMIT 5000
DETACH DELETE n
RETURN count(*) AS deletedCount
```

## Count all the files, folders and level batches of all knowledge ids

```
MATCH (fn:FileNode)
WITH fn.knowledge_id AS kid, fn.repo_name AS repo
WITH kid, repo, COUNT(fn) AS total_files
OPTIONAL MATCH (fo:FolderNode {knowledge_id: kid, repo_name: repo})
RETURN kid AS knowledge_id, repo AS repo_name, total_files, COUNT(fo) AS total_folders
ORDER BY total_files DESC

```

## Count all the files, folders and level batches of all knowledge ids

```cypher
MATCH (fn:FileNode)
WITH fn.knowledge_id AS kid, fn.repo_name AS repo, COUNT(fn) AS total_files
OPTIONAL MATCH (fo:FolderNode {knowledge_id: kid, repo_name: repo})
WITH kid, repo, total_files, COUNT(DISTINCT fo) AS total_folders
OPTIONAL MATCH (lb:LevelBatch {knowledge_id: kid, repo_name: repo})
RETURN kid AS knowledge_id, repo AS repo_name, total_files, total_folders, COUNT(DISTINCT lb) AS total_level_batches
ORDER BY total_files DESC
```

## OrgKeyword Relationship Analysis

### Keywords shared across multiple repos (cross-repo keywords)

```cypher
MATCH (k:OrgKeyword)
WHERE k.file_count > 1
WITH k
MATCH (k)-[:APPEARS_IN_FILE]->(f:FileNode)
WITH k.keyword AS keyword, k.semantic_type AS category, k.total_frequency AS freq,
     COLLECT(DISTINCT f.repo_name) AS repos
WHERE SIZE(repos) > 1
RETURN keyword, category, freq, SIZE(repos) AS repo_count, repos
ORDER BY repo_count DESC, freq DESC
```

### Top keywords per category with frequency > 1 across repos

```cypher
MATCH (k:OrgKeyword)
WHERE k.file_count > 1
WITH k
MATCH (k)-[:APPEARS_IN_FILE]->(f:FileNode)
WITH k.semantic_type AS category, k.keyword AS keyword, k.total_frequency AS freq,
     COLLECT(DISTINCT f.repo_name) AS repos
WHERE SIZE(repos) > 1
WITH category, COLLECT({keyword: keyword, freq: freq, repo_count: SIZE(repos), repos: repos}) AS keywords
RETURN category, SIZE(keywords) AS shared_keyword_count,
       keywords[0..10] AS top_keywords
ORDER BY shared_keyword_count DESC
```

### Category-level summary of cross-repo keyword coverage

```cypher
MATCH (k:OrgKeyword)
WHERE k.file_count > 1
WITH k
MATCH (k)-[:APPEARS_IN_FILE]->(f:FileNode)
WITH k.semantic_type AS category, k.keyword AS keyword,
     COLLECT(DISTINCT f.repo_name) AS repos
WITH category, keyword, SIZE(repos) AS repo_count
RETURN category,
       COUNT(keyword) AS total_keywords,
       SUM(CASE WHEN repo_count > 1 THEN 1 ELSE 0 END) AS cross_repo_keywords,
       MAX(repo_count) AS max_repo_spread
ORDER BY cross_repo_keywords DESC
```

### Specific keyword drill-down: which files share a keyword across repos

```cypher
MATCH (k:OrgKeyword {keyword: "<KEYWORD>"})-[r:APPEARS_IN_FILE]->(f:FileNode)
RETURN k.keyword AS keyword, k.semantic_type AS category,
       f.repo_name AS repo, f.relative_path AS file, r.frequency AS frequency
ORDER BY r.frequency DESC
```

### Find related files in other repos by relative path

```cypher
MATCH (source:FileNode {relative_path: "<RELATIVE_PATH>"})
WITH source
MATCH (source)<-[:APPEARS_IN_FILE]-(k:OrgKeyword)-[:APPEARS_IN_FILE]->(related:FileNode)
WHERE related.repo_name <> source.repo_name
RETURN related.repo_name AS repo, related.relative_path AS file,
       COLLECT(k.keyword) AS shared_keywords, COUNT(k) AS keyword_count
ORDER BY keyword_count DESC
```

### Repo-pair affinity: how many keywords are shared between each pair of repos

```cypher
MATCH (k:OrgKeyword)
WHERE k.file_count > 1
WITH k
MATCH (k)-[:APPEARS_IN_FILE]->(f1:FileNode)
MATCH (k)-[:APPEARS_IN_FILE]->(f2:FileNode)
WHERE f1.repo_name < f2.repo_name
RETURN f1.repo_name AS repo_a, f2.repo_name AS repo_b,
       COUNT(DISTINCT k) AS shared_keywords
ORDER BY shared_keywords DESC
```
