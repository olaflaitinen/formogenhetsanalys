# Accessibility

This document describes accessibility measures in Förmögenhetsanalys.

## Documentation Accessibility

### Language
- Primary language: English
- Swedish translation planned
- Technical terms in English with Swedish equivalents where relevant

### Reading Level
- Technical documentation written for graduate-level researchers
- User guide written for practitioners
- Plain language summaries planned

### Formatting
- Markdown for all documentation
- Headings provide structure
- Code blocks clearly marked
- Tables for data presentation

## Visual Accessibility

### Color Contrast
- Figures use high contrast colors
- Colorblind-friendly palettes (viridis, plasma)
- Patterns used where possible (not just color)

### Figure Accessibility
- Alt text for all figures
- Descriptive captions
- Vector graphics (PDF) for scalability
- PNG for web viewing

### Font Sizes
- Documentation: 16px base font
- Code blocks: 14px monospace
- Figures: Minimum 12px labels

## Code Accessibility

### Type Hints
- All functions have type hints
- Mypy strict mode enforced
- Clear parameter and return types

### Docstrings
- Google-style docstrings
- Parameter descriptions
- Return value descriptions
- Examples for key functions

### Error Messages
- Clear, actionable error messages
- Suggested fixes where possible
- Stack traces for debugging

## Screen Reader Compatibility

### HTML Output
- Semantic HTML structure
- ARIA labels where needed
- Keyboard navigation support
- Screen reader tested (planned)

### PDF/A Output
- Tagged PDF for accessibility
- Reading order preserved
- Alt text for images
- Tables with headers

## Keyboard Accessibility

### CLI
- Full keyboard control
- Help command: `formogenhetsanalys --help`
- Tab completion (planned)

### Documentation Site
- Keyboard navigation
- Skip to content links
- Focus indicators visible

## Internationalization

### Character Encoding
- UTF-8 throughout
- UTF-8 BOM for CSV files (Excel compatibility)
- Proper handling of Swedish characters (å, ä, ö)

### Number Formatting
- Swedish number formats in Swedish documentation
- English number formats in English documentation
- Thousands separators consistent

## Testing Accessibility

### Accessibility Testing
- Automated testing with axe-core (planned)
- Manual keyboard navigation testing
- Screen reader testing planned

### WCAG 2.1 Compliance
- Target: Level AA
- Current: Partial compliance
- Gap analysis ongoing

## Feedback

### Reporting Accessibility Issues
- Use GitHub issue template
- Tag with `accessibility` label
- Include browser and assistive technology

### Continuous Improvement
- Accessibility reviewed in each release
- User feedback incorporated
- Training for contributors
