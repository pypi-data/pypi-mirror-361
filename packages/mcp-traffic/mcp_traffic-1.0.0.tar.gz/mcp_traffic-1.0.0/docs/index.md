---
layout: page
title: Documentation
permalink: /docs/
---

# MCP Traffic Documentation

Welcome to the MCP Traffic documentation. This section contains comprehensive information about the Tokyo traffic data collection and analysis system.

## Table of Contents

- [Deployment Guide](./DEPLOYMENT.md)
- [Analysis Results](./analysis-results.md)
- [Dashboard](./dashboard.html)

## Overview

MCP Traffic is a comprehensive system for collecting, analyzing, and visualizing Tokyo traffic data using the ODPT (Open Data Platform for Transportation) API.

### Key Features

- **Real-time Data Collection**: Automated collection of traffic data from multiple sources
- **Data Analysis**: Advanced analytics for traffic pattern identification
- **Interactive Dashboard**: Web-based visualization dashboard
- **Historical Analysis**: Long-term trend analysis capabilities

## Quick Start

1. **Setup**: Follow the [Deployment Guide](./DEPLOYMENT.md) for installation instructions
2. **Dashboard**: Access the [Interactive Dashboard](./dashboard.html) for real-time visualizations
3. **Analysis**: Review [Analysis Results](./analysis-results.md) for insights

## System Architecture

The system consists of several components:

- **Data Collection Layer**: Python scripts for API interactions
- **Data Processing**: Analytics and transformation modules
- **Storage Layer**: Data persistence and management
- **Visualization Layer**: Web-based dashboard and reports

## Data Sources

- **ODPT API**: Primary source for Tokyo transportation data
- **Traffic Sensors**: Real-time traffic flow information
- **Public Transportation**: Train and bus schedule data

## Technologies Used

- **Backend**: Python, Flask
- **Frontend**: HTML5, JavaScript, Chart.js
- **Database**: PostgreSQL, Redis (caching)
- **Deployment**: Docker, Docker Compose
- **CI/CD**: GitHub Actions

## Getting Help

- Check the [troubleshooting section](./DEPLOYMENT.md#troubleshooting) in the deployment guide
- Review existing [GitHub Issues](https://github.com/Tatsuru-Kikuchi/MCP-traffic/issues)
- Create a new issue for bugs or feature requests

## Contributing

We welcome contributions! Please see our [Contributing Guidelines](../README.md#contributing) for more information.
