#!/bin/bash
set -e

# Parse input arguments
README_PATH=${1:-"README.md"}
REPOSITORY_PATH=${2:-"."}
FAIL_THRESHOLD=${3:-"60"}
OUTPUT_FORMAT=${4:-"markdown"}
CUSTOM_WEIGHTS=${5:-""}
GITHUB_TOKEN=${6:-"$GITHUB_TOKEN"}
INCLUDE_CODE_ANALYSIS=${7:-"true"}
COMMENT_ON_PR=${8:-"false"}

echo "::group::README Quality Analysis"
echo "README Path: $README_PATH"
echo "Repository Path: $REPOSITORY_PATH"
echo "Fail Threshold: $FAIL_THRESHOLD"
echo "Output Format: $OUTPUT_FORMAT"
echo "Include Code Analysis: $INCLUDE_CODE_ANALYSIS"

# Check if README file exists
if [ ! -f "$README_PATH" ]; then
    echo "::error::README file not found: $README_PATH"
    exit 1
fi

# Prepare analysis command
ANALYSIS_CMD="readme-analyzer"

# Add repository path if code analysis is enabled
if [ "$INCLUDE_CODE_ANALYSIS" = "true" ]; then
    ANALYSIS_CMD="$ANALYSIS_CMD $README_PATH --repository $REPOSITORY_PATH"
else
    ANALYSIS_CMD="$ANALYSIS_CMD $README_PATH --no-code"
fi

# Add custom weights if provided
if [ -n "$CUSTOM_WEIGHTS" ] && [ "$CUSTOM_WEIGHTS" != "null" ]; then
    # Parse JSON weights and convert to CLI format
    WEIGHTS=$(echo "$CUSTOM_WEIGHTS" | python3 -c "
import json, sys
data = json.loads(sys.stdin.read())
weights = [
    str(data.get('readability', 0.25)),
    str(data.get('structural', 0.30)),
    str(data.get('complexity', 0.20)),
    str(data.get('consistency', 0.25))
]
print(','.join(weights))
")
    ANALYSIS_CMD="$ANALYSIS_CMD --weights $WEIGHTS"
fi

# Set output format
ANALYSIS_CMD="$ANALYSIS_CMD --format json --output /tmp/analysis.json"

# Set GitHub token if provided
if [ -n "$GITHUB_TOKEN" ]; then
    export GITHUB_TOKEN="$GITHUB_TOKEN"
fi

echo "Running analysis command: $ANALYSIS_CMD"
echo "::endgroup::"

# Run the analysis
eval $ANALYSIS_CMD

# Check if analysis was successful
if [ $? -ne 0 ]; then
    echo "::error::README analysis failed"
    exit 1
fi

if [ ! -f "/tmp/analysis.json" ]; then
    echo "::error::Analysis results not found"
    exit 1
fi

echo "::group::Processing Results"

# Extract key metrics using Python
python3 << 'EOF'
import json
import os
import sys

# Load analysis results
with open('/tmp/analysis.json', 'r') as f:
    analysis = json.load(f)

# Extract quality metrics
quality = analysis['quality']
overall_score = quality['overall_score']
grade = quality['grade_level']
readability_score = quality['readability_score']
structural_score = quality['structural_score']
complexity_score = quality['complexity_score']
consistency_score = quality['consistency_score']

# Check if passed threshold
fail_threshold = float(os.environ.get('FAIL_THRESHOLD', '60'))
passed = overall_score >= fail_threshold

# Set GitHub Actions outputs
print(f"::set-output name=quality-score::{overall_score:.1f}")
print(f"::set-output name=grade::{grade}")
print(f"::set-output name=passed::{str(passed).lower()}")
print(f"::set-output name=readability-score::{readability_score:.1f}")
print(f"::set-output name=structural-score::{structural_score:.1f}")
print(f"::set-output name=complexity-score::{complexity_score:.1f}")
print(f"::set-output name=consistency-score::{consistency_score:.1f}")
print(f"::set-output name=report-file::/tmp/analysis.json")

# Print summary
print(f"\n📊 README Quality Analysis Results")
print(f"{'='*50}")
print(f"Overall Score: {overall_score:.1f}/100 ({grade})")
print(f"Threshold: {fail_threshold}")
print(f"Status: {'✅ PASSED' if passed else '❌ FAILED'}")
print(f"\nDimension Scores:")
print(f"  📖 Readability: {readability_score:.1f}")
print(f"  🏗️  Structure:   {structural_score:.1f}")
print(f"  🔧 Complexity:  {complexity_score:.1f}")
print(f"  🔗 Consistency: {consistency_score:.1f}")

# Generate markdown report if requested
output_format = os.environ.get('OUTPUT_FORMAT', 'markdown')
if output_format == 'markdown':
    markdown_report = f"""## 📊 README Quality Analysis

**Overall Score:** {overall_score:.1f}/100 ({grade})

### Dimension Scores
| Dimension | Score | Status |
|-----------|-------|--------|
| 📖 Readability | {readability_score:.1f}/100 | {'✅' if readability_score >= 70 else '⚠️' if readability_score >= 50 else '❌'} |
| 🏗️ Structure | {structural_score:.1f}/100 | {'✅' if structural_score >= 70 else '⚠️' if structural_score >= 50 else '❌'} |
| 🔧 Complexity | {complexity_score:.1f}/100 | {'✅' if complexity_score >= 70 else '⚠️' if complexity_score >= 50 else '❌'} |
| 🔗 Consistency | {consistency_score:.1f}/100 | {'✅' if consistency_score >= 70 else '⚠️' if consistency_score >= 50 else '❌'} |

### Key Metrics
- **Word Count:** {analysis['readability']['word_count']}
- **Readability Level:** {analysis['readability']['readability_consensus']}
- **Sections:** {analysis['structure']['section_count']}
- **Completeness:** {analysis['structure']['completeness_score']:.1f}%

### Recommendations
"""
    
    # Add top recommendations
    for i, rec in enumerate(quality.get('recommendations', [])[:5], 1):
        markdown_report += f"{i}. {rec}\n"
    
    # Write markdown report
    with open('/tmp/readme_quality_report.md', 'w') as f:
        f.write(markdown_report)
    
    print(f"\n📝 Markdown report saved to: /tmp/readme_quality_report.md")

# Exit with appropriate code
if not passed:
    print(f"\n❌ Quality check failed: {overall_score:.1f} < {fail_threshold}")
    sys.exit(1)
else:
    print(f"\n✅ Quality check passed: {overall_score:.1f} >= {fail_threshold}")
    sys.exit(0)

EOF

echo "::endgroup::"

# Handle PR commenting if enabled
if [ "$COMMENT_ON_PR" = "true" ] && [ -n "$GITHUB_TOKEN" ] && [ -f "/tmp/readme_quality_report.md" ]; then
    echo "::group::Posting PR Comment"
    
    # Check if this is a PR
    if [ -n "$GITHUB_EVENT_NAME" ] && [ "$GITHUB_EVENT_NAME" = "pull_request" ]; then
        # Post comment using GitHub CLI or API
        if command -v gh &> /dev/null; then
            gh pr comment --body-file /tmp/readme_quality_report.md
        else
            echo "::warning::GitHub CLI not available, skipping PR comment"
        fi
    else
        echo "::notice::Not a pull request, skipping comment"
    fi
    
    echo "::endgroup::"
fi

echo "README Quality Analysis completed successfully!"