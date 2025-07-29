# AWS EC2 Instance Pricing Tool

A Python CLI tool to fetch and compare **AWS EC2 hourly on-demand pricing** and the latest **AMI IDs** across all available AWS regions.  
Supports Linux distributions (Ubuntu, Amazon Linux, RHEL, SUSE) and Windows instances.

💡 Ideal for DevOps engineers, cloud architects, and infrastructure teams looking to optimize EC2 costs or automate cloud image selection.

> 🔖 This tool focuses on **on-demand EC2 pricing**, making it perfect for dynamic or short-term workloads where flexibility matters.
## Requirements

- **Python 3.7+**  
  The script is compatible with Python 3.7 and above.

- **AWS Credentials Configured**  
  The tool uses `boto3` to interact with AWS APIs. Make sure your AWS CLI or environment variables are configured with appropriate credentials and permissions to access EC2 and Pricing APIs.
  * Note: you don't have to have a default region set in your environment

- **Python Dependencies**  
  Install required Python packages using pip:

  ```bash
  pip install boto3 rich
  ```
  Or
  ```bash
  pip install -r requirements.txt
## Installation

```bash
git clone https://github.com/spithash/AWS-EC2-Instance-Pricing-Tool.git
cd AWS-EC2-Instance-Pricing-Tool
pip install -r requirements.txt
```
## Usage

Run the tool from the command line by specifying the EC2 instance type, operating system, and optionally the distro:

```bash
python ec2-price-checker.py <instance_type> --os <linux|windows> [--distro <distro_name>]
```
### Examples

Fetch pricing and AMI info for a Linux Ubuntu t2.micro instance:

```bash
python3 ec2-price-checker.py t2.micro --os linux --distro ubuntu
```
Fetch pricing and AMI info for a Windows t3.medium instance (Microsoft publisher):
```bash
python3 ec2-price-checker.py t3.medium --os windows --distro microsoft
```
Fetch pricing and AMI info for a Linux instance across all distros (no distro specified):
```bash
python3 ec2-price-checker.py t2.micro --os linux
```

