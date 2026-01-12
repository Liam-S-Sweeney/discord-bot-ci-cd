# CI/CD Infrastructure for a Discord Bot

This project implements a Discord bot designed to support server coordination through a multi-step user verification workflow and automated role assignment, enabling privacy-aware access control for different user groups.

The system was explicitly designed as a **foundational infrastructure framework** rather than a single-purpose bot. To support continuous development and uninterrupted operation, a full **Continuous Integration / Continuous Deployment (CI/CD)** pipeline was implemented using a cloud-based virtual machine (e2-micro).

The VM automatically checks the shared GitHub repository for updates at regular intervals. When changes are detected, the code is pulled, validated through basic error checks, and deployed without requiring downtime. This enables multiple contributors to collaboratively develop and extend the system while maintaining continuous uptime.

---

## Technical Highlights

- **Python-based modular bot architecture** separating core logic, APIs, and feature extensions  
- **GitHub + Webhooks** to support collaborative development, automated updates, and version control  
- **Secure Shell (SSH)**–based automation for deployment, monitoring, and remote execution on the VM  
- **Cloud-hosted CI/CD workflow** enabling unattended operation and rapid iteration  

---

## Professional Applicability

This project demonstrates applied engineering skills relevant to research labs and production systems:

- Supports collaborative development workflows common in data science and research teams  
- Demonstrates real-world CI/CD principles, automation, and infrastructure reliability  
- Enables long-running, continuously available services suitable for data collection, experimentation, or orchestration tasks  
