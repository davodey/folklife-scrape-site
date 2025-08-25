# Importance Filtering System for Layout Viewer

## Overview

This document describes the new importance filtering system implemented in the Festival Layouts Viewer. The system automatically calculates importance levels for each layout cluster and provides interactive filtering capabilities.

## Features Implemented

### 1. Automatic Importance Scoring

Each layout cluster is automatically assigned an importance level based on multiple factors:

- **Cluster Size (60% weight)**: Larger clusters (more screenshots) get higher importance
- **Layout Consistency (40% weight)**: Clusters with more similar screenshots get higher importance
- **Site Priority**: Festival layouts get a 20% boost over Folklife layouts

### 2. Importance Levels

- **🔴 HIGH**: Importance score ≥ 0.8
  - Large clusters with consistent layouts
  - Critical layouts that appear frequently across the site
  
- **🟠 MEDIUM**: Importance score 0.5 - 0.79
  - Medium-sized clusters with moderate consistency
  - Important but not critical layouts
  
- **⚫ LOW**: Importance score < 0.5
  - Small clusters or inconsistent layouts
  - Less critical layouts

### 3. Visual Indicators

- **Importance Labels**: Color-coded badges on each cluster card
- **Filter Buttons**: Interactive buttons to filter by importance level
- **Count Display**: Shows how many layouts are currently visible
- **Responsive Design**: Works on both desktop and mobile devices

## How It Works

### Importance Calculation

```python
def calculate_cluster_importance(cluster_size, avg_distance, site_type):
    # Base importance from cluster size (more screenshots = more important)
    size_score = min(cluster_size / 20.0, 1.0)  # Normalize to 0-1, cap at 20+ screenshots
    
    # Distance score (closer to canonical = more important)
    distance_score = 1.0 - min(avg_distance, 1.0)
    
    # Site-specific importance (festival might be more important than folklife)
    site_multiplier = 1.2 if site_type == 'festival' else 1.0
    
    # Combined importance score (0-1)
    importance = (size_score * 0.6 + distance_score * 0.4) * site_multiplier
    
    # Convert to importance level
    if importance >= 0.8:
        return 'high', importance
    elif importance >= 0.5:
        return 'medium', importance
    else:
        return 'low', importance
```

### Filtering Logic

The system provides four filter options:

1. **All Layouts**: Shows all clusters regardless of importance
2. **High Priority**: Shows only high-importance layouts
3. **Medium Priority**: Shows only medium-importance layouts  
4. **Low Priority**: Shows only low-importance layouts

## User Interface

### Filter Bar

Located below the header, the filter bar includes:

- Clear labeling: "Filter by Importance:"
- Four filter buttons with emoji indicators
- Live count display showing current results
- Responsive design that stacks on mobile

### Cluster Cards

Each cluster card now displays:

- **Importance Label**: Color-coded badge in top-right corner
- **Data Attributes**: `data-importance` attribute for JavaScript filtering
- **Enhanced Styling**: Hover effects and visual hierarchy

### Interactive Features

- **Real-time Filtering**: Instant results when clicking filter buttons
- **Active State**: Visual feedback for selected filter
- **Count Updates**: Dynamic display of visible layout count
- **Smooth Transitions**: CSS animations for better UX

## Technical Implementation

### CSS Classes

- `.importance-filter`: Main filter container
- `.filter-btn`: Individual filter buttons
- `.filter-btn.active`: Active filter state
- `.importance-label`: Importance badges on cards
- `.importance-label.high/medium/low`: Color variants
- `.cluster-card.hidden`: Hidden cards during filtering

### JavaScript Functions

```javascript
function filterByImportance(importance) {
    const cards = document.querySelectorAll('.cluster-card');
    const filterBtns = document.querySelectorAll('.filter-btn');
    let visibleCount = 0;
    
    // Update active filter button
    filterBtns.forEach(btn => {
        btn.classList.remove('active');
        if (btn.dataset.filter === importance) {
            btn.classList.add('active');
        }
    });
    
    // Filter cards
    cards.forEach(card => {
        if (importance === 'all' || card.dataset.importance === importance) {
            card.classList.remove('hidden');
            visibleCount++;
        } else {
            card.classList.add('hidden');
        }
    });
    
    // Update count display
    const countElement = document.getElementById('filterCount');
    if (importance === 'all') {
        countElement.textContent = `Showing all ${cards.length} layouts`;
    } else {
        countElement.textContent = `Showing ${visibleCount} ${importance} priority layouts`;
    }
}
```

### Data Attributes

Each cluster card includes:

```html
<div class="cluster-card" data-importance="high">
    <div class="importance-label high">HIGH</div>
    <!-- card content -->
</div>
```

## Benefits

### For Users

1. **Quick Prioritization**: Easily identify most important layouts
2. **Focused Review**: Filter to specific importance levels
3. **Better Understanding**: Visual cues for layout significance
4. **Improved Workflow**: Streamlined review process

### For Developers

1. **Data-Driven Decisions**: Objective importance scoring
2. **Scalable System**: Easy to adjust scoring algorithms
3. **Maintainable Code**: Clean separation of concerns
4. **Extensible Design**: Easy to add new filter criteria

## Future Enhancements

### Potential Improvements

1. **Custom Scoring**: Allow users to adjust importance weights
2. **Advanced Filters**: Combine importance with other criteria (year, page type, etc.)
3. **Export Options**: Filter and export specific importance levels
4. **Analytics**: Track which layouts are most frequently viewed
5. **Machine Learning**: Improve scoring based on user behavior

### Additional Filter Criteria

- **Year-based filtering**: Focus on specific time periods
- **Page type filtering**: Filter by homepage, blog, schedule, etc.
- **Size-based filtering**: Filter by cluster size ranges
- **Distance-based filtering**: Filter by layout consistency

## Usage Examples

### Scenario 1: High-Priority Review
1. Click "🔴 High Priority" filter
2. Review only the most critical layouts
3. Focus on layouts that appear most frequently

### Scenario 2: Quality Assessment
1. Click "⚫ Low Priority" filter
2. Identify layouts that might need attention
3. Look for inconsistent or problematic designs

### Scenario 3: Comprehensive Analysis
1. Use "All Layouts" to see everything
2. Toggle between importance levels as needed
3. Compare high vs. low priority layouts

## Conclusion

The importance filtering system provides a powerful way to prioritize and organize layout analysis. By automatically scoring layouts based on objective criteria and providing intuitive filtering tools, users can focus their attention on the most critical layouts while maintaining access to the complete dataset.

The system is designed to be:
- **Intuitive**: Easy to understand and use
- **Efficient**: Fast filtering and responsive interface
- **Flexible**: Multiple filtering options and extensible design
- **Informative**: Clear visual indicators and helpful feedback

This enhancement significantly improves the usability of the Layout Viewer for website redesign projects, making it easier to identify and prioritize the most important layout patterns.
