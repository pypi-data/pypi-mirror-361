# Community Metrics Tracking

The uubed project automatically tracks community engagement and project health metrics across all repositories. This provides transparency and helps us understand how the project is growing and where we need to focus our efforts.

## 📊 What We Track

### Repository Health
- **Stars & Forks**: Community interest and adoption
- **Contributors**: Active developer community size
- **Commit Activity**: Development velocity and consistency
- **Issue Management**: Response time and resolution rate
- **Pull Request Flow**: Code review efficiency

### Engagement Metrics
- **Recent Activity**: Commits, issues, PRs in the last 30 days
- **Community Growth**: New contributors and their contributions
- **Release Cadence**: Frequency and quality of releases
- **Documentation Usage**: Views and engagement with docs

### Project Quality Indicators
- **Code Health**: Open vs closed issues ratio
- **Maintenance**: Time since last release/commit
- **Community Support**: Issue response times
- **Development Momentum**: Consistent activity patterns

## 🎯 Health Score Calculation

Each repository gets a community health score (0-100) based on:

- **Recent Activity (30 points)**: Commits in the last 30 days
- **Community Engagement (25 points)**: Contributors and issue resolution
- **Project Popularity (20 points)**: Stars and community interest
- **Code Quality (15 points)**: Issue management and PR activity
- **Release Management (10 points)**: Regular releases and maintenance

### Score Interpretation
- **🟢 75-100**: Healthy, active project with good community engagement
- **🟡 50-74**: Stable project with moderate activity
- **🔴 0-49**: Needs attention - low activity or engagement issues

## 📅 Collection Schedule

- **Daily Collection**: Basic metrics collected every day at 6 AM UTC
- **Weekly Aggregation**: Comprehensive analysis and trending
- **Monthly Reports**: Detailed community health reports
- **Manual Triggers**: Available for immediate analysis

## 📈 Metrics Dashboard

The community metrics feed into our [Project Dashboard](./DASHBOARD.md), providing:

- **Real-time Health Status**: Current score for each repository
- **Activity Trends**: Visual representation of development velocity
- **Community Growth**: Tracking stars, forks, and contributors over time
- **Issue Management**: Open/closed ratio and response times

## 🔍 How to Access Metrics

### Latest Snapshot
The most recent metrics are automatically updated in `community_metrics_latest.json` and used by the project dashboard.

### Historical Data
- **GitHub Actions Artifacts**: Detailed JSON and CSV files for each collection
- **Retention**: 90 days of historical data available
- **Format**: Both machine-readable (JSON/CSV) and human-readable (Markdown reports)

### Manual Collection
You can trigger metrics collection manually:
1. Go to the [Actions tab](../../actions/workflows/community-metrics.yml)
2. Click "Run workflow"
3. Results will be available as artifacts

## 📋 Current Repositories

| Repository | Focus | Language | Status |
|------------|-------|----------|---------|
| [uubed](https://github.com/twardoch/uubed) | Project coordination | Markdown/Python | ![Tracking](https://img.shields.io/badge/tracking-active-green) |
| [uubed-rs](https://github.com/twardoch/uubed-rs) | High-performance core | Rust | ![Tracking](https://img.shields.io/badge/tracking-active-green) |
| [uubed-py](https://github.com/twardoch/uubed-py) | Python bindings | Python | ![Tracking](https://img.shields.io/badge/tracking-active-green) |
| [uubed-docs](https://github.com/twardoch/uubed-docs) | Documentation | Markdown | ![Tracking](https://img.shields.io/badge/tracking-active-green) |

## 🎯 Using Metrics for Decision Making

### For Maintainers
- **Resource Allocation**: Focus on repositories with declining health scores
- **Community Engagement**: Identify opportunities for increased interaction
- **Release Planning**: Track readiness based on activity and issue resolution
- **Feature Prioritization**: Use community feedback and engagement patterns

### For Contributors
- **Contribution Opportunities**: See which repositories need attention
- **Community Health**: Understand project stability and activity levels
- **Impact Tracking**: See how contributions affect project health
- **Recognition**: Contributors are highlighted in metrics reports

### For Users
- **Project Stability**: Health scores indicate maintenance and support levels
- **Community Support**: Activity levels suggest how quickly issues are addressed
- **Future Planning**: Release cadence helps with upgrade planning
- **Trust Indicators**: Consistent metrics show reliable project management

## 🔧 Technical Implementation

### Data Collection
```yaml
# Automated via GitHub Actions
schedule:
  - cron: '0 6 * * *'  # Daily at 6 AM UTC

permissions:
  contents: read
  actions: read
```

### Metrics Storage
- **Format**: JSON for machine processing, CSV for analysis, Markdown for reports
- **Location**: GitHub Actions artifacts with 90-day retention
- **Access**: Public via GitHub API and dashboard integration

### Privacy Considerations
- **Public Data Only**: All metrics use publicly available GitHub API data
- **No Personal Information**: Individual contributor data is aggregated
- **Transparent Collection**: Open source collection scripts and methodology

## 📞 Questions or Feedback

- **GitHub Issues**: [Report issues or suggest improvements](../../issues)
- **GitHub Discussions**: [Ask questions about metrics](../../discussions)
- **Documentation**: [Contribute to metrics documentation](../../pulls)

## 🤝 Contributing to Metrics

Help us improve community metrics tracking:

1. **Suggest New Metrics**: What else should we track?
2. **Improve Calculations**: Better algorithms for health scores?
3. **Visualization**: Ideas for better dashboard presentation?
4. **Analysis**: Help interpret trends and patterns?

### Current Improvement Ideas
- [ ] Contributor diversity metrics
- [ ] Code quality indicators (test coverage, etc.)
- [ ] Documentation coverage metrics
- [ ] Performance regression tracking
- [ ] Cross-repository dependency health

---

*Community metrics help us build a healthier, more sustainable open source project. Your engagement and feedback make these metrics meaningful!*