# Fast-Deploy

Fast-Deploy is a CLI tool designed to simplify the process of deploying web applications for beginners and intermediate developers. It streamlines the deployment process by leveraging Docker and Nixpacks, managing AWS configurations, and ensuring that Docker environments are set up correctly. Fast-Deploy aims to demystify the deployment process, allowing developers to focus on building their applications.

## Features

- **AWS CLI Configuration Check:** Ensures AWS CLI is properly configured for deployment.
- **Docker Configuration Verification:** Checks if Docker is installed and running, and configures it if necessary.
- **Simplified Deployment Process:** Utilizes Nixpacks for building Docker images, making the process straightforward and efficient.
- **Port Mapping for Test Runs:** Offers an option to run built Docker images with specified port mapping for immediate testing.

## Getting Started

### Prerequisites

- Docker installed on your system.
- Nixpacks installed on your system.
- AWS CLI installed and configured.
- AWS Copilot installed and configured.
- Python 3 and pip.

### Installation

Clone the Fast-Deploy repository to your local machine:

```bash
git clone https://github.com/ojimba01/fast-deploy.git
cd fast-deploy
```

## Usage

- **Initialize your project:**

This command checks your AWS CLI, Docker, Nixpacks, and AWS Copilot CLI configurations and prompts you to set up a new project configuration, including service type and environment settings.bash
```bash
./mycli.py init
```

- **Build your Docker image with Nixpacks:**

Automates the Docker image creation using Nixpacks, ensuring that the environment is prepped correctly before initiating the build.bash
```bash
./mycli.py build
```

- **Deploy your project:**

Leverages AWS Copilot to deploy your project based on the defined configuration file, handling complex AWS interactions automatically.bash
```bash
./mycli.py deploy
```

- **Purge your project:**

Removes all project components, including Docker and AWS resources, with an option to force deletion even if the configuration file is missing.bash
```bash
./mycli.py purge -f
```Contributing

We welcome contributions from the community. Please fork the repository and submit pull requests with new features or bug fixes

Fast-Deploy is released under the MIT License. See the LICENSE file in the repository for more details.
