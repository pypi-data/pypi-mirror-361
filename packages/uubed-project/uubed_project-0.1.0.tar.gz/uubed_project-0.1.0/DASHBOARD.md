# uubed Project Dashboard

[![Project Health](https://img.shields.io/badge/project%20health-monitoring-blue)](https://twardoch.github.io/uubed/)

## Overview

This dashboard provides real-time visibility into the health and activity across all uubed repositories. It automatically updates every 6 hours with the latest metrics from GitHub.

## 🔗 Quick Links

- **[Live Dashboard](https://twardoch.github.io/uubed/)** - Interactive project status dashboard
- **[Main Repository](https://github.com/twardoch/uubed)** - Project coordination and documentation
- **[Rust Implementation](https://github.com/twardoch/uubed-rs)** - High-performance core
- **[Python Package](https://github.com/twardoch/uubed-py)** - Python bindings and API
- **[Documentation](https://github.com/twardoch/uubed-docs)** - Comprehensive docs and book

## 📊 What's Tracked

The dashboard monitors key metrics across all repositories:

### Repository Health
- **Activity Status**: Recent commits and development activity
- **CI/CD Status**: Build and test pipeline health
- **Release Status**: Latest releases and version currency
- **Issue Management**: Open issues and pull request status

### Development Metrics
- **Commit Activity**: Commits in the last 30 days
- **Community Engagement**: Stars, forks, and contributor activity
- **Code Quality**: Test coverage and build success rates
- **Release Cadence**: Frequency and timing of releases

### Project Coordination
- **Cross-Repository Sync**: Version alignment and dependency updates
- **Documentation Coverage**: API docs and user guide completeness
- **Performance Tracking**: Benchmark results and regression detection

## 🎯 Health Indicators

The dashboard uses color-coded indicators to show repository health:

- **🟢 Green (Good)**: Active development, passing CI, recent releases
- **🟡 Yellow (Warning)**: Some issues but manageable (stale branches, minor failures)
- **🔴 Red (Attention Needed)**: Critical issues requiring immediate attention

## 📈 Key Performance Indicators

### Project-Wide KPIs
- **Overall Health Score**: Percentage of repositories in good health
- **Development Velocity**: Total commits across all repositories
- **Community Growth**: Combined stars and forks across repositories
- **Release Frequency**: Number of releases in the last quarter

### Repository-Specific KPIs
- **Code Freshness**: Days since last commit
- **CI Reliability**: Percentage of successful builds
- **Issue Resolution**: Average time to close issues
- **Documentation Coverage**: Percentage of API documented

## 🔄 Update Schedule

The dashboard automatically updates on the following schedule:

- **Every 6 hours**: Comprehensive metrics collection
- **On every push to main**: Immediate health check updates
- **Manual trigger**: Available via GitHub Actions workflow dispatch

## 📋 Repository Status Summary

| Repository | Purpose | Language | Status |
|------------|---------|----------|---------|
| [uubed](https://github.com/twardoch/uubed) | Project coordination | Markdown | ![Status](https://img.shields.io/badge/status-active-brightgreen) |
| [uubed-rs](https://github.com/twardoch/uubed-rs) | High-performance core | Rust | ![Status](https://img.shields.io/badge/status-active-brightgreen) |
| [uubed-py](https://github.com/twardoch/uubed-py) | Python bindings | Python | ![Status](https://img.shields.io/badge/status-active-brightgreen) |
| [uubed-docs](https://github.com/twardoch/uubed-docs) | Documentation | Markdown | ![Status](https://img.shields.io/badge/status-active-brightgreen) |

## 🛠️ Dashboard Features

### Interactive Elements
- **Repository Cards**: Click to navigate to GitHub repositories
- **Workflow Links**: Direct access to CI/CD pipeline results
- **Issue Tracking**: Quick view of open issues and pull requests
- **Release Timeline**: Visual history of recent releases

### Mobile Responsive
- **Responsive Design**: Works on desktop, tablet, and mobile devices
- **Touch-Friendly**: Optimized for touch navigation
- **Fast Loading**: Minimal dependencies for quick access

### Data Export
- **JSON API**: Raw metrics data available for external tools
- **Badge Generation**: Status badges for README files
- **Historical Data**: Trend analysis over time (future feature)

## 🔧 Technical Implementation

The dashboard is built using:

- **GitHub Actions**: Automated metrics collection every 6 hours
- **GitHub API**: Real-time repository data and workflow status
- **GitHub Pages**: Static hosting for the dashboard interface
- **Responsive HTML/CSS**: Clean, accessible interface design

### Data Collection Process
1. **Metrics Gathering**: GitHub Actions workflow collects data from all repositories
2. **Data Processing**: Metrics are processed and health scores calculated
3. **Dashboard Generation**: HTML dashboard is generated with current data
4. **Deployment**: Updated dashboard is deployed to GitHub Pages

## 🤝 Contributing

To improve the dashboard:

1. **Suggest Metrics**: Open an issue to request new tracking metrics
2. **Report Issues**: Submit bugs or interface improvements
3. **Contribute Code**: Submit PRs for dashboard enhancements
4. **Documentation**: Help improve this documentation

## 📞 Support

For dashboard-related questions:

- **GitHub Issues**: [Report problems or suggestions](https://github.com/twardoch/uubed/issues)
- **GitHub Discussions**: [Ask questions or share feedback](https://github.com/twardoch/uubed/discussions)

---

**Note**: The dashboard provides a high-level overview of project health. For detailed information about specific repositories, please visit the individual repository pages linked above.