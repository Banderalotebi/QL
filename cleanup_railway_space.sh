#!/bin/bash
# Railway Space Cleanup Script
# Safely removes duplicate files from codebase

set -e

REPO_ROOT="/workspaces/QL"
BACKUP_NAME="data_backup_$(date +%Y%m%d_%H%M%S).tar.gz"

echo "🔍 Railway Codebase Cleanup Script"
echo "=================================="
echo ""
echo "📦 Creating backup: $BACKUP_NAME"
cd "$REPO_ROOT"
tar czf "$BACKUP_NAME" data/ || { echo "Backup failed!"; exit 1; }
echo "✅ Backup created: $BACKUP_NAME"
echo ""

# Calculate before
echo "📊 Space BEFORE cleanup:"
du -sh data/ || echo "N/A"
BEFORE=$(du -sh data | awk '{print $1}')
echo "Data folder: $BEFORE"
echo ""

echo "🗑️ Removing duplicate files..."

# Remove duplicate Quran files (marked with (1) or (2))
if [ -d "$REPO_ROOT/data" ]; then
    cd "$REPO_ROOT/data"
    
    # Count files before
    BEFORE_COUNT=$(find . -type f | wc -l)
    
    # Remove duplicates
    echo "  Removing: quran-* (1) and (2) versions..."
    rm -f quran-simple\ \(1\).sql 2>/dev/null || true
    rm -f quran-simple\ \(1\).txt 2>/dev/null || true
    rm -f quran-simple\ \(2\).sql 2>/dev/null || true
    rm -f quran-uthmani\ \(1\).sql 2>/dev/null || true
    rm -f quran-uthmani\ \(2\).sql 2>/dev/null || true
    rm -f quran-uthmani-min\ \(1\).sql 2>/dev/null || true
    rm -f quran-uthmani-min\ \(2\).sql 2>/dev/null || true
    rm -f quran-simple-plain\ \(1\).sql 2>/dev/null || true
    rm -f quran-simple-plain\ \(1\).sql.xml 2>/dev/null || true
    
    echo "  Removing: XML and TXT versions (keeping SQL only)..."
    # Only remove if SQL version exists
    [ -f quran-simple.sql ] && rm -f quran-simple.xml 2>/dev/null || true
    [ -f quran-simple.sql ] && rm -f quran-simple.txt 2>/dev/null || true
    [ -f quran-uthmani.sql ] && rm -f quran-uthmani.xml 2>/dev/null || true
    [ -f quran-uthmani.sql ] && rm -f quran-uthmani.txt 2>/dev/null || true
    [ -f quran-uthmani-min.sql ] && rm -f quran-uthmani-min.xml 2>/dev/null || true
    [ -f quran-uthmani-min.sql ] && rm -f quran-uthmani-min.txt 2>/dev/null || true
    [ -f quran-simple-min.sql ] && rm -f quran-simple-min.xml 2>/dev/null || true
    
    echo "  Removing: raw/ and researches/ directories..."
    rm -rf raw 2>/dev/null || true
    rm -rf researches 2>/dev/null || true
fi

# Remove Python cache
echo "  Removing: Python cache (__pycache__)..."
find "$REPO_ROOT" -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
find "$REPO_ROOT" -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
find "$REPO_ROOT" -type d -name .mypy_cache -exec rm -rf {} + 2>/dev/null || true

# Remove test files if not needed
echo "  Removing: .pyc files..."
find "$REPO_ROOT" -type f -name "*.pyc" -delete 2>/dev/null || true
find "$REPO_ROOT" -type f -name ".DS_Store" -delete 2>/dev/null || true

# Calculate after
echo ""
echo "📊 Space AFTER cleanup:"
du -sh "$REPO_ROOT/data/" || echo "N/A"
AFTER=$(du -sh "$REPO_ROOT/data" | awk '{print $1}')
AFTER_COUNT=$(find "$REPO_ROOT/data" -type f | wc -l)

echo ""
echo "✅ Cleanup complete!"
echo "  Before: ~$BEFORE  ($BEFORE_COUNT files)"
echo "  After:  ~$AFTER   ($AFTER_COUNT files)"
echo ""
echo "📝 Backup available at: $BACKUP_NAME"
echo ""
echo "🚀 Next steps:"
echo "  1. git add -A"
echo "  2. git commit -m 'Cleanup: Remove duplicate data files'"
echo "  3. git push"
echo "  4. Railway will redeploy with optimized codebase"
echo ""
