#!/bin/bash

if [ -z "$1" ]; then
  echo "Usage: ./new-post.sh my-post-slug"
  exit 1
fi

SLUG="$1"
DATE=$(date +%Y-%m-%d)

if [ -f "posts/$SLUG.md" ]; then
  echo "Post '$SLUG' already exists"
  exit 1
fi

cat > "posts/$SLUG.md" << EOF
---
title: $SLUG
date: $DATE
---

Write your post here.
EOF

echo "Created: posts/$SLUG.md"
echo "Run 'npm run build' when done"
