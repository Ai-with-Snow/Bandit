# Sidebar Dark Theme Implementation

## Final State (Verified Working)
The sidebar has been fully converted to a dark professional theme matching the reference.

## Key Design Elements
- **Background**: `#1a1a1a` (dark charcoal)
- **Text colors**: `text-white` for primary, `text-gray-400`/`text-gray-500` for secondary
- **Icon colors**: `#888` for primary icons, `#666` for secondary (ellipsis)
- **Active state**: `bg-white/10` highlight
- **Border color**: `border-white/10` for subtle separation
- **Purple accent**: `bg-purple-600` for Save button, profile avatar

## Structure
1. **Header**: "New chat" button + close (X) button
2. **Projects Section**: Collapsible with chevron, shows folder items
3. **Today/Yesterday Sections**: Collapsible time-grouped chat history
4. **Footer**: User profile (Goddexx Snow, Pro Plan) + settings icon

## Collapsible Functionality
- Projects: `showProjects` state with `setShowProjects(!showProjects)`
- Time groups: `expandedTimeGroups` Set with add/delete toggle

## Modal
- Dark background: `#2a2a2a`
- White text, gray placeholders
- Purple "Save" button

## Files Modified
- `bandit-mobile/src/components/Sidebar.tsx` - Complete dark theme conversion

## Verified Functionality
- [x] Dark background applied
- [x] New chat button works
- [x] Close button works  
- [x] Projects section collapses
- [x] Today/Yesterday sections collapse
- [x] Ellipsis menus appear on same row
- [x] New project modal opens with dark theme
- [x] User profile displayed at bottom
