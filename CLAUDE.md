# Claude Code Instructions for TikTok Scraper Project

## Project Overview

This is a comprehensive TikTok data analysis and scraping toolkit consisting of three main components:

1. **tiktok_toolkit** - Python-based TikTok scraper with GUI interface
2. **tiktok_ugc_chart** - Vue.js frontend for data visualization and analysis
3. **tiktok_ugc_scraper** - Command-line Python scraper for UGC data collection

## Project Structure

```
tiktok_scraper/
├── tiktok_toolkit/          # Python GUI scraper
│   ├── tiktok.py           # Main application with Tkinter GUI
│   ├── requirements.txt    # Python dependencies
│   ├── config.json        # Configuration (target_time)
│   └── run_tiktok.bat     # Windows batch file
├── tiktok_ugc_chart/       # Vue.js dashboard
│   ├── src/
│   │   ├── App.vue        # Main application component
│   │   ├── components/    # Vue components
│   │   ├── types/         # TypeScript type definitions
│   │   └── utils/         # Utility functions
│   ├── package.json       # Node.js dependencies and scripts
│   └── vite.config.ts     # Vite configuration
└── tiktok_ugc_scraper/     # Command-line scraper
    ├── src/
    │   ├── main.py        # Entry point with process/retry modes
    │   ├── config.py      # Configuration management
    │   └── modules/       # Scraper modules
    ├── requirements.txt   # Python dependencies
    └── config.json       # Configuration file
```

## Technology Stack

### Python Components (tiktok_toolkit & tiktok_ugc_scraper)
- **Language**: Python 3.x
- **Web Scraping**: Selenium WebDriver with Chrome
- **Data Processing**: pandas, openpyxl
- **GUI**: Tkinter (toolkit only)
- **Packaging**: PyInstaller for standalone executables

### Vue.js Component (tiktok_ugc_chart)
- **Framework**: Vue 3 with Composition API
- **Language**: TypeScript
- **UI Framework**: Vuetify 3
- **Charting**: Chart.js with vue-chartjs
- **Build Tool**: Vite
- **Package Manager**: npm

## Development Guidelines

### Code Style and Conventions
- **Python**: Follow PEP 8 conventions
- **Vue/TypeScript**: Use ESLint and Prettier for consistency
- **File naming**: Use snake_case for Python, kebab-case for Vue components
- **Comments**: Write Japanese comments for business logic (existing pattern)

### Dependencies Management
- **Python**: Use `requirements.txt` for exact version pinning
- **Node.js**: Use `package.json` with semantic versioning
- Always check existing dependencies before adding new ones

### Configuration Management
- Python components use `config.json` files for configuration
- Vue component uses environment variables and configuration objects
- Never commit sensitive data like API keys or personal file paths

## Component-Specific Instructions

### tiktok_toolkit
- GUI-based scraper using Selenium with Chrome WebDriver
- Processes Excel files with song data
- Uses threading for concurrent processing
- Includes image handling and screenshot capabilities
- **Setup**: `python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt`
- **Run**: `python3 tiktok.py`
- **Build**: `pyinstaller --onefile tiktok.py`

### tiktok_ugc_scraper
- Command-line scraper with process and retry modes
- Modular architecture with separate modules for different concerns
- Excel-based data input/output with UGC and difference tracking
- **Setup**: Same as tiktok_toolkit
- **Run**: `python3 src/main.py process` or `python3 src/main.py retry`
- **Build**: Uses PyInstaller with module data inclusion

### tiktok_ugc_chart
- Vue 3 application with TypeScript
- Vuetify UI framework for material design
- Chart.js integration for data visualization
- Excel file processing and export functionality
- **Setup**: `npm install`
- **Dev**: `npm run dev`
- **Build**: `npm run build`
- **Lint**: `npm run lint`
- **Type Check**: `npm run type-check`

## Testing and Quality Assurance

### Linting and Type Checking
- **Python**: No explicit linting configured (consider adding flake8/black)
- **Vue.js**: ESLint configured with Vue and TypeScript support
- **Type Checking**: `npm run type-check` for Vue component

### Testing Strategy
- No formal test suites currently implemented
- Manual testing required for Selenium-based scraping
- Consider adding unit tests for utility functions

## Security Considerations

### Web Scraping Ethics
- Respect robots.txt and rate limiting
- Use appropriate delays between requests
- Handle anti-bot measures responsibly

### Data Privacy
- Excel files may contain sensitive song/artist data
- Log files should not contain personal information
- Configuration files with paths should be gitignored

## Deployment and Distribution

### Python Applications
- Use PyInstaller to create standalone executables
- Include all necessary data files and modules
- Test executables on target operating systems

### Vue.js Application
- Build static files with `npm run build`
- Serve from web server or host as static site
- Consider CDN for better performance

## Common Tasks

### Adding New Features
1. Identify which component needs modification
2. Follow existing patterns and conventions
3. Update relevant configuration files
4. Test across all supported environments
5. Update documentation if necessary

### Debugging Issues
1. Check log files (app.log for Python components)
2. Use browser developer tools for Vue component
3. Verify Selenium WebDriver compatibility
4. Check Excel file format compatibility

### Performance Optimization
- **Python**: Use threading/multiprocessing for concurrent operations
- **Vue.js**: Implement lazy loading and component caching
- **Scraping**: Optimize wait times and element selection strategies

## Environment Setup

### Prerequisites
- Python 3.x with pip
- Node.js with npm
- Chrome browser (for Selenium)
- Excel-compatible spreadsheet application

### First-time Setup
1. Clone repository
2. Set up Python virtual environments for each Python component
3. Install dependencies using requirements.txt and package.json
4. Configure Chrome WebDriver (handled by webdriver_manager)
5. Update config.json files with appropriate paths

## Maintenance Notes

- Selenium scripts may break with TikTok UI changes
- WebDriver versions need periodic updates
- Vue.js and npm dependencies should be kept current for security
- Excel file formats should remain compatible with openpyxl

## GitHub Integration

The project uses GitHub Actions with Claude Code integration:
- Trigger phrase: `@claude`
- Supports issue comments and PR reviews
- Automated responses for code assistance and analysis
- Uses LiteLLM proxy for API access

When working with this codebase, always consider the multi-language, multi-framework nature and test changes across all affected components.