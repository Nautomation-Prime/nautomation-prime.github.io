---
title: Beginner Tutorials
description: Foundation tutorials for Python network automation beginners. Learn Netmiko, TextFSM, and data export with complete line-by-line explanations.
tags:
  - Beginner
  - Tutorials
  - Netmiko
  - TextFSM
  - Excel
---

# Beginner Tutorials

## "Master the Fundamentals — Build Confidence with Simple, Working Scripts"

Welcome to the **Beginner Tutorial Series**! These tutorials are designed for network engineers who are new to Python automation or want to solidify their understanding of core concepts.

Each tutorial provides complete, working code with exhaustive line-by-line explanations. You'll understand exactly what every line does, why it's there, and how to modify it for your own use.

---

## 🎯 What You'll Learn

By completing these beginner tutorials, you'll be able to:

- ✅ Connect to Cisco devices using **Netmiko**
- ✅ Send show commands and retrieve structured data
- ✅ Parse command output using **TextFSM**
- ✅ Export data to Excel spreadsheets
- ✅ Handle basic errors and exceptions
- ✅ Manage credentials securely (without hardcoding passwords)
- ✅ Work with multiple devices using loops

---

## 📚 Tutorial List

### 1. [Send a Show Command and Export to Excel](./netmiko-show-command-to-excel.md)

**The perfect starting point for network automation beginners.**

Learn how to:

- Connect to a Cisco device using Netmiko
- Execute a show command with automatic TextFSM parsing
- Convert the structured data to an Excel spreadsheet using pandas
- Understand every line of code with detailed explanations

**What You'll Build**: A script that collects `show version` output and exports it to Excel.

**Prerequisites**: Basic Python knowledge only.

---

### 2. Coming Soon: Multi-Device Show Command Collection

Extend the first tutorial to collect data from multiple devices using a CSV inventory.

---

### 3. Coming Soon: Basic Configuration Backup

Create a simple script to back up device configurations with timestamps.

---

## 🔧 Setup Requirements

Before starting these tutorials, ensure you have:

### Python Environment
```bash
# Install required libraries
pip install netmiko pandas openpyxl
```

### Test Device Access

You'll need at least one Cisco device (physical or virtual) with:

- SSH enabled
- Reachable IP address
- Valid username and password
- Appropriate privilege level for show commands

### Supported Platforms

These tutorials work with:

- Cisco IOS
- Cisco IOS-XE
- Cisco NX-OS
- Cisco IOS-XR (with minor modifications)

---

## 💡 How to Use These Tutorials

1. **Read the Explanation** — Each tutorial starts with an overview
2. **Review the Code** — Complete, working script with annotations
3. **Understand Each Line** — Detailed line-by-line breakdown
4. **Run It Yourself** — Test on your own devices
5. **Experiment** — Modify the code to learn how it works

---

## 🎓 Learning Path

We recommend working through these tutorials in order:

```mermaid
graph LR
    A[Show Command to Excel] --> B[Multi-Device Collection]
    B --> C[Configuration Backup]
    C --> D[Ready for Intermediate!]
    
    style A fill:#90EE90
    style D fill:#FFD700
```

---

!!! success "After Completing Beginner Tutorials"
    Once you're comfortable with these concepts, move on to [Intermediate Tutorials](../intermediate/index.md) to learn about threading, advanced parsing, and configuration management.

---

## 🆘 Troubleshooting Tips

**Common Issues:**

- **Authentication fails**: Verify SSH is enabled and credentials are correct
- **TextFSM parsing returns empty**: Your device type might not be supported — try `use_textfsm=False` first
- **Module not found**: Run `pip install netmiko pandas openpyxl`
- **Connection timeout**: Check network connectivity and firewall rules

---

## 📖 Additional Resources

- **[Netmiko Documentation](https://github.com/ktbyers/netmiko)** — Official Netmiko guide
- **[TextFSM Templates](https://github.com/networktocode/ntc-templates)** — See all available parsing templates
- **[Pandas Documentation](https://pandas.pydata.org/docs/)** — Learn more about data manipulation

---
