# 🚇 MCP Traffic - Tokyo Traffic Data Collection System

[![Deploy Jekyll site to Pages](https://github.com/Tatsuru-Kikuchi/MCP-traffic/actions/workflows/main.yml/badge.svg)](https://github.com/Tatsuru-Kikuchi/MCP-traffic/actions/workflows/main.yml)
[![GitHub Pages](https://github.com/Tatsuru-Kikuchi/MCP-traffic/actions/workflows/jekyll-gh-pages.yml/badge.svg)](https://github.com/Tatsuru-Kikuchi/MCP-traffic/actions/workflows/jekyll-gh-pages.yml)
![GitHub stars](https://img.shields.io/github/stars/Tatsuru-Kikuchi/MCP-traffic)
![GitHub forks](https://img.shields.io/github/forks/Tatsuru-Kikuchi/MCP-traffic)

> **Real-time Tokyo transportation data collection and visualization system using ODPT API**

---

## 🎯 **Live Dashboard & Demo**

<div align="center">

### 📊 **[🔴 LIVE Tokyo Traffic Dashboard](https://tatsuru-kikuchi.github.io/MCP-traffic/dashboard.html)**
**Interactive real-time visualization of Tokyo's transportation network**

[![Dashboard Preview](https://img.shields.io/badge/🚀_Launch_Dashboard-Live_Demo-blue?style=for-the-badge&logo=dashboard&logoColor=white)](https://tatsuru-kikuchi.github.io/MCP-traffic/dashboard.html)
[![User Guide](https://img.shields.io/badge/📖_User_Guide-Documentation-green?style=for-the-badge&logo=book&logoColor=white)](https://tatsuru-kikuchi.github.io/MCP-traffic/dashboard-help.html)
[![Project Website](https://img.shields.io/badge/🌐_Project_Website-Visit-purple?style=for-the-badge&logo=github&logoColor=white)](https://tatsuru-kikuchi.github.io/MCP-traffic/)

</div>

### ✨ **Dashboard Features**
- 🗺️ **Interactive Tokyo Station Map** with real-time markers
- 📈 **Live Charts & Metrics** showing passenger flow and performance
- 🚂 **Real-time Train Tracking** with delay status
- 🚌 **Bus Route Monitoring** with live positions
- 📱 **Mobile Responsive** design for all devices
- ⚡ **Auto-refresh** with 30-second data updates

### 📊 **Current System Status**
```
🔴 LIVE: Tokyo Transportation Monitor
├── Daily Passengers: 2.15M across 5 major stations
├── System Performance: 94.2% punctuality rate
├── Average Delay: 1.0 minutes
└── Active Alerts: 0 service disruptions
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8+ 
- Git
- Ruby 3.1+ (for Jekyll documentation)

### Installation

```bash
# Clone the repository
git clone https://github.com/Tatsuru-Kikuchi/MCP-traffic.git
cd MCP-traffic

# Set up Python environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt

# Set up Jekyll for documentation
bundle install

# Configure the system
cp config/api_config.example.json config/api_config.json
# Edit config/api_config.json with your ODPT API settings
```

### Running the System

```bash
# Test the installation
python src/collectors/traffic_collector.py --catalog-only

# Run a single data collection
python scripts/collect_all_data.py

# Start continuous scheduled collection
python scripts/schedule_collection.py

# Serve documentation locally
bundle exec jekyll serve
```

## 📊 What is MCP Traffic?

A comprehensive **Tokyo traffic data collection and analysis system** that leverages the ODPT (Open Data Platform for Transportation) API to gather, process, and monitor real-time transportation data across Tokyo's extensive public transit network.

MCP Traffic (Model Control Protocol for Traffic) is an automated system designed for:

- **🔄 Real-time Data Collection**: Continuous gathering of Tokyo transportation data
- **⚡ Data Processing**: Automated cleaning, validation, and transformation
- **📈 Analysis & Monitoring**: Traffic pattern analysis and system health monitoring  
- **🗄️ Data Management**: Organized storage with automatic archiving
- **📚 Documentation**: Comprehensive guides and API documentation

## 🏗️ System Architecture

### Data Flow
```
ODPT API → Data Collectors → Data Processors → Storage → Analysis
    ↓              ↓              ↓            ↓         ↓
Raw Data → Validation → Transformation → Archive → Insights
```

### Directory Structure
```
MCP-traffic/
├── src/                    # Source code
│   ├── collectors/         # Data collection modules
│   └── processors/         # Data processing utilities
├── data/                   # Data storage
│   ├── raw/               # Original API responses
│   ├── processed/         # Cleaned data
│   └── archives/          # Historical data
├── scripts/               # Automation scripts
├── config/                # Configuration files
├── monitoring/            # Health checks and alerts
├── logs/                  # System logs
├── docs/                  # Documentation
└── .github/workflows/     # CI/CD workflows
```

## 🔧 Configuration

### API Configuration
Edit `config/api_config.json`:
```json
{
  "odpt_api": {
    "base_url": "https://ckan.odpt.org/api/3/action/",
    "api_key": "your-api-key",
    "rate_limit": 100,
    "timeout": 30
  },
  "collection": {
    "schedule_interval": 300,
    "data_types": ["train", "bus", "station"],
    "regions": ["tokyo"]
  },
  "storage": {
    "format": "json",
    "compression": true,
    "retention_days": 365
  }
}
```

### Jekyll Configuration
The documentation site is configured in `_config.yml` with:
- GitHub Pages deployment
- SEO optimization
- Responsive design
- Multi-language support

## 📈 Data Collection Features

### Supported Data Types
- **🚆 Train Data**: Real-time positions, delays, service status
- **🚌 Bus Data**: Vehicle locations, route information, schedules
- **🏢 Station Data**: Facility information, accessibility features
- **🗺️ Route Data**: Network topology, connections, fare information
- **📊 Operational Data**: Service disruptions, maintenance schedules

### Collection Strategies
- **Scheduled Collection**: Automated data gathering at configurable intervals
- **On-demand Collection**: Manual collection for specific data types
- **Error Recovery**: Robust retry mechanisms with exponential backoff
- **Rate Limiting**: Compliance with API usage policies

## 🖥️ Deployment Options

### Local Development
```bash
# Standard Python development setup
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python scripts/collect_all_data.py
```

### Docker Deployment
```bash
# Build and run with Docker Compose
docker-compose up -d

# Monitor logs
docker-compose logs -f mcp-traffic
```

### Server Deployment
```bash
# Install as systemd service
sudo cp deployment/mcp-traffic.service /etc/systemd/system/
sudo systemctl enable mcp-traffic
sudo systemctl start mcp-traffic
```

### Cloud Deployment
- **AWS**: EC2 + S3 + CloudWatch
- **Google Cloud**: Compute Engine + Cloud Storage
- **Azure**: Virtual Machines + Blob Storage

See the [Deployment Guide](docs/DEPLOYMENT.md) for detailed instructions.

## 📊 Monitoring & Health Checks

### System Monitoring
- **API Connectivity**: Continuous monitoring of ODPT API availability
- **Data Quality**: Validation and completeness checks
- **Storage Usage**: Disk space monitoring with alerts
- **Performance Metrics**: Response times and throughput tracking

### Health Check Commands
```bash
# System health overview
python monitoring/health_check.py

# Detailed performance metrics
python monitoring/performance_monitor.py

# Data quality report
python monitoring/data_quality_check.py
```

### Alerting
- Email notifications for system failures
- Slack integration for real-time alerts
- Custom webhook support for external monitoring

## 🔍 Data Analysis Tools

### Built-in Analytics
- Traffic pattern analysis
- Peak hour identification
- Service reliability metrics
- Historical trend analysis

### Integration Options
- **Jupyter Notebooks**: Interactive data exploration
- **Pandas/NumPy**: Statistical analysis
- **Matplotlib/Plotly**: Data visualization
- **Apache Spark**: Large-scale data processing

## 📚 Documentation & Links

### 🎯 **Main Dashboard Links**
- **[📊 Live Dashboard](https://tatsuru-kikuchi.github.io/MCP-traffic/dashboard.html)** - Interactive Tokyo traffic visualization
- **[📖 Dashboard User Guide](https://tatsuru-kikuchi.github.io/MCP-traffic/dashboard-help.html)** - Complete tutorial and help
- **[🌐 Project Website](https://tatsuru-kikuchi.github.io/MCP-traffic/)** - Main documentation site

### 📋 **Technical Documentation**
- **[Deployment Guide](docs/DEPLOYMENT.md)**: Complete deployment instructions
- **[API Documentation](docs/api.md)**: API reference and examples  
- **[Configuration Guide](docs/configuration.md)**: System configuration options
- **[Troubleshooting](docs/troubleshooting.md)**: Common issues and solutions

## 🔐 Security & Privacy

### Data Privacy
- **No Personal Data**: Only collects aggregate transportation data
- **Anonymized Data**: All data is inherently anonymous
- **Compliance**: Adheres to data protection regulations

### Security Features
- API key encryption
- Secure configuration management
- Network security best practices
- Regular security updates

## 🤝 Contributing

We welcome contributions! Here's how to get started:

### Development Setup
```bash
# Fork and clone the repository
git clone https://github.com/YOUR-USERNAME/MCP-traffic.git
cd MCP-traffic

# Create development branch
git checkout -b feature/your-feature-name

# Set up development environment
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Run tests
python -m pytest tests/
```

### Contribution Guidelines
1. **Code Style**: Follow PEP 8 for Python, use meaningful variable names
2. **Testing**: Add tests for new functionality
3. **Documentation**: Update documentation for changes
4. **Commits**: Use clear, descriptive commit messages

### Types of Contributions
- 🐛 **Bug Fixes**: Report and fix issues
- ✨ **Features**: New functionality and improvements
- 📚 **Documentation**: Improve guides and examples
- 🧪 **Testing**: Enhance test coverage
- 🔧 **DevOps**: Improve deployment and CI/CD

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

### Getting Help
1. **Documentation**: Check the [docs/](docs/) directory
2. **Issues**: Search [existing issues](https://github.com/Tatsuru-Kikuchi/MCP-traffic/issues)
3. **Discussions**: Join [GitHub Discussions](https://github.com/Tatsuru-Kikuchi/MCP-traffic/discussions)
4. **Dashboard Help**: Read the [User Guide](https://tatsuru-kikuchi.github.io/MCP-traffic/dashboard-help.html)

### Reporting Issues
When reporting issues, please include:
- Operating system and Python version
- Error messages and stack traces
- Steps to reproduce the issue
- Configuration (without sensitive data)

## 🏆 Acknowledgments

### Data Sources
- **[ODPT (Open Data Platform for Transportation)](https://odpt.org/)**: Primary data source
- **Tokyo Metropolitan Government**: Open data initiatives
- **Transportation Operators**: Real-time operational data

### Technology Stack
- **Python**: Core programming language
- **Jekyll**: Documentation site generator
- **GitHub Actions**: CI/CD and deployment
- **Docker**: Containerization
- **Chart.js**: Interactive data visualization
- **Leaflet**: Interactive mapping

### Community
Special thanks to all contributors who have helped improve this project through code, documentation, testing, and feedback.

---

<div align="center">

## 🎯 **Ready to Explore Tokyo's Transportation System?**

[![Launch Dashboard](https://img.shields.io/badge/🚀_Launch_Dashboard-Click_Here-blue?style=for-the-badge&logo=dashboard&logoColor=white)](https://tatsuru-kikuchi.github.io/MCP-traffic/dashboard.html)
[![Read Guide](https://img.shields.io/badge/📖_Read_User_Guide-Get_Started-green?style=for-the-badge&logo=book&logoColor=white)](https://tatsuru-kikuchi.github.io/MCP-traffic/dashboard-help.html)

**[🔴 LIVE Demo Available Now!](https://tatsuru-kikuchi.github.io/MCP-traffic/dashboard.html)**

---

![GitHub issues](https://img.shields.io/github/issues/Tatsuru-Kikuchi/MCP-traffic)
![GitHub pull requests](https://img.shields.io/github/issues-pr/Tatsuru-Kikuchi/MCP-traffic)
![Last commit](https://img.shields.io/github/last-commit/Tatsuru-Kikuchi/MCP-traffic)

</div>

**For more information, visit the [project website](https://tatsuru-kikuchi.github.io/MCP-traffic/) or check out the [live dashboard](https://tatsuru-kikuchi.github.io/MCP-traffic/dashboard.html)!**