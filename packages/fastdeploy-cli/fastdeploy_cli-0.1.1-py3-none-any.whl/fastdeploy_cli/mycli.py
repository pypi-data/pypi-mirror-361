#!/usr/bin/env python3

"""
fastdeploy.mycli
~~~~~~~~~~~~~~~~

Entrypoint for the Fast-Deploy CLI (mycli).
"""

import click
import logging
import json
import os
import re
import subprocess
import shutil
import platform
import glob

# Setup basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[
                        logging.FileHandler("fast-deploy.log"),
                        logging.StreamHandler()
                    ])

def check_package_installation(package_name):
    """Check if a Python package is installed."""
    try:
        # Try to import the package to see if it's installed
        result = subprocess.run(
            ["python", "-c", f"import {package_name}"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        click.echo(f"{package_name} is installed.")

    except subprocess.CalledProcessError:
        click.echo(f"{package_name} is not installed or not functioning correctly.")
        exit(1)
    except FileNotFoundError:
        click.echo(f"{package_name} not found. Please ensure it's installed.")
        exit(1)


# check_package_installation("numpy")


def check_aws_configuration():
    """Check for AWS CLI v2 installation and configuration."""
    try:
        # Check if AWS CLI v2 is installed by running 'aws --version'
        result = subprocess.run(["aws", "--version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        # Ensure it's AWS CLI v2
        if "aws-cli/2" in result.stdout:
            click.echo("AWS CLI v2 is installed.")
        else:
            click.echo("AWS CLI v2 is not installed. Please install AWS CLI version 2.")
            exit(1)

    except subprocess.CalledProcessError:
        click.echo("AWS CLI is not functioning correctly.")
        exit(1)
    except FileNotFoundError:
        click.echo("AWS CLI not found. Please install AWS CLI v2.")
        exit(1)

    # Proceed to check for configuration files
    aws_config_file = os.path.expanduser('~/.aws/config')
    aws_credentials_file = os.path.expanduser('~/.aws/credentials')

    if not os.path.exists(aws_config_file) or not os.path.exists(aws_credentials_file):
        click.echo("AWS CLI is not configured on this system.")
        if click.confirm("Do you want to configure AWS CLI now?"):
            try:
                subprocess.run(["aws", "configure"], check=True)
            except subprocess.CalledProcessError:
                click.echo("Failed to run 'aws configure'. Please ensure AWS CLI v2 is installed.")
        else:
            click.echo("AWS CLI configuration is required to deploy. Exiting.")
            exit(1)
    else:
        click.echo("AWS CLI is already configured.")


def check_docker_configuration():
    """Check for Docker configuration and verify Docker daemon is running."""
    docker_config_file = os.path.expanduser('~/.docker/config.json')

    if not os.path.exists(docker_config_file):
        click.echo("Docker is not configured on this system.")
        # Prompt for Docker installation or configuration
    else:
        click.echo(
            "Docker configuration found. Verifying Docker daemon is running...")
        try:
            subprocess.run(["docker", "version"], check=True,
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            click.echo("Docker is running and accessible.")
        except subprocess.CalledProcessError as e:
            click.echo(
                "Docker daemon is not running. Please ensure Docker is installed and running.")
            exit(1)
        except FileNotFoundError:
            click.echo("Docker is not installed. Please install Docker.")
            exit(1)


def check_nixpacks_installation():
    """Check if Nixpacks is installed and prompt the user to install if not found."""
    try:
        subprocess.run(["nixpacks", "--version"], check=True,
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        click.echo("Nixpacks is installed.")
    except subprocess.CalledProcessError:
        click.echo("Nixpacks is not installed or not functioning correctly.")
        if click.confirm("Do you want to install Nixpacks now?"):
            try:
                subprocess.run(
                    ["curl", "-sSL", "https://nixpacks.com/install.sh", "|", "bash"], check=True)
                click.echo("Nixpacks installed successfully.")
            except subprocess.CalledProcessError as e:
                click.echo(
                    "Failed to install Nixpacks. Please try installing it manually.")
        else:
            click.echo("Nixpacks installation is required. Exiting.")
            exit(1)
    except FileNotFoundError:
        click.echo("Nixpacks command not found. Please install Nixpacks.")
        if click.confirm("Do you want to install Nixpacks now?"):
            try:
                subprocess.run(
                    ["curl", "-sSL", "https://nixpacks.com/install.sh", "|", "bash"], check=True)
                click.echo("Nixpacks installed successfully.")
            except subprocess.CalledProcessError as e:
                click.echo(
                    "Failed to install Nixpacks. Please try installing it manually.")
        else:
            click.echo("Nixpacks installation is required. Exiting.")
            exit(1)


def check_aws_copilot_installation():
    """Check if AWS Copilot CLI is installed and prompt the user to install if not found."""
    try:
        subprocess.run(["copilot", "--version"], check=True,
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        click.echo("AWS Copilot CLI is installed.")
    except subprocess.CalledProcessError:
        click.echo(
            "AWS Copilot CLI is not installed or not functioning correctly.")
        if click.confirm("Do you want to install AWS Copilot CLI now?"):
            install_aws_copilot()
    except FileNotFoundError:
        click.echo(
            "AWS Copilot CLI command not found. Please install AWS Copilot CLI.")
        if click.confirm("Do you want to install AWS Copilot CLI now?"):
            install_aws_copilot()


def install_aws_copilot():
    """Install AWS Copilot CLI based on the user's operating system and architecture."""
    system = platform.system()
    arch = platform.machine()

    try:
        if system == "Darwin":
            click.echo("Installing AWS Copilot CLI for MacOS...")
            subprocess.run(
                ["curl", "-Lo", "copilot", "https://github.com/aws/copilot-cli/releases/latest/download/copilot-darwin"], check=True)
        elif system == "Linux":
            if arch == "x86_64":
                click.echo(
                    "Installing AWS Copilot CLI for Linux x86 (64-bit)...")
                subprocess.run(
                    ["curl", "-Lo", "copilot", "https://github.com/aws/copilot-cli/releases/latest/download/copilot-linux"], check=True)
            elif arch == "aarch64":
                click.echo("Installing AWS Copilot CLI for Linux (ARM)...")
                subprocess.run(
                    ["curl", "-Lo", "copilot", "https://github.com/aws/copilot-cli/releases/latest/download/copilot-linux-arm64"], check=True)
        elif system == "Windows":
            click.echo("Installing AWS Copilot CLI for Windows...")
            subprocess.run(
                ["powershell", "Invoke-WebRequest -OutFile 'C:\\Program Files\\copilot.exe' https://github.com/aws/copilot-cli/releases/latest/download/copilot-windows.exe"], check=True)
        else:
            click.echo(
                "Unsupported operating system. Please install AWS Copilot CLI manually.")
            return

        subprocess.run(["chmod", "+x", "copilot"], check=True)
        if system != "Windows":
            subprocess.run(
                ["sudo", "mv", "copilot", "/usr/local/bin/copilot"], check=True)
        click.echo("AWS Copilot CLI installed successfully.")
    except subprocess.CalledProcessError as e:
        click.echo(
            "Failed to install AWS Copilot CLI. Please try installing it manually.")


def find_config_file():
    """Search for the configuration file ending in '_fd_config.json'."""
    config_files = glob.glob('*_fd_config.json')
    if config_files:
        # Extract the project name by removing the '_fd_config.json' part
        project_name = config_files[0].rsplit('_fd_config.json', 1)[0]
        return project_name
    return None


@click.group()
def cli():
    """Demo CLI for webapp deployment"""
    pass


@click.command()
def init():
    """Initialize a new project configuration"""
    check_aws_configuration()
    check_docker_configuration()
    check_nixpacks_installation()
    check_aws_copilot_installation()
    project_name = click.prompt("Please enter your project name", type=str)

    # Sanitize project name by replacing spaces, slashes, and backslashes
    sanitized_project_name = re.sub(r'[ /\\]', '_', project_name)
    config_filename = f"{sanitized_project_name}_fd_config.json"

    # Check if configuration already exists to handle overwrite
    if os.path.exists(config_filename):
        if not click.confirm(f"Configuration '{config_filename}' already exists. Do you want to overwrite it?"):
            click.echo("Initialization cancelled. No changes made.")
            return

    # Service type options
    service_types = [
        "Request-Driven Web Service", "Load Balanced Web Service",
        "Backend Service", "Worker Service", "Static Site", "Scheduled Job"
    ]
    click.echo("Choose a service type from the following options:")
    for idx, service_type in enumerate(service_types, 1):
        click.echo(f"{idx}. {service_type}")
    service_type_idx = click.prompt("Enter the number for your service type",
                                    type=click.IntRange(1, len(service_types)), default=2)
    service_type = service_types[service_type_idx - 1]

    service_name = click.prompt(
        "Please enter your service name", type=str, default="my-service")
    env_name = click.prompt(
        "Please enter your environment name", type=str, default="prod")
    dockerfile_path = click.prompt(
        "Please enter the path to your Dockerfile", type=str, default="./Dockerfile")
    service_port = click.prompt(
        "Please enter the port your service listens on", type=int, default=80)

    # Construct configuration
    config = {
        "project_name": sanitized_project_name,
        "service_type": service_type,
        "service_name": service_name,
        "environment_name": env_name,
        "dockerfile_path": dockerfile_path,
        "service_port": service_port
    }

    # Save the configuration to a file
    with open(config_filename, 'w') as config_file:
        json.dump(config, config_file, indent=4)

    logging.info(
        f"Project '{sanitized_project_name}' initialized with new configuration. Previous configuration was overwritten if existed.")
    click.echo(
        f"Project '{sanitized_project_name}' initialized and configuration saved.")


@click.command()
def build():
    """Build a Docker image using Nixpacks"""
    project_path = os.getcwd()  # Assuming we are building in the current directory
    default_project_name = find_config_file()

    if default_project_name:
        project_name = click.prompt(
            "Please enter your project name", type=str, default=default_project_name)
    else:
        project_name = click.prompt("Please enter your project name", type=str)

    config_filename = f"{project_name}_fd_config.json"

    if not os.path.exists(config_filename):
        click.echo(
            "Configuration file not found. Please run the init command first.")
        return

    with open(config_filename, 'r') as config_file:
        config = json.load(config_file)

    image_name = click.prompt(
        "Please enter your image name", type=str, default=f"{default_project_name}_v1.0")

    logging.info("Preparing Nixpacks build environment...")
    click.echo("Preparing Nixpacks build environment...")

    try:
        # Generate .nixpacks directory with Dockerfile at the project root
        subprocess.run(["nixpacks", "build", ".", "-o", "."], check=True)
    except subprocess.CalledProcessError as e:
        # Capture the error output for the error message
        error_message = e.stderr or e.stdout
        logging.error(
            f"Error preparing the build environment: {error_message}")
        click.echo(f"Error preparing the build environment: {error_message}")
        return

    # Define the expected path for the Dockerfile after Nixpacks build
    dockerfile_path = os.path.join(project_path, ".nixpacks", "Dockerfile")

    # Check if the Dockerfile exists in the .nixpacks directory
    if not os.path.isfile(dockerfile_path):
        logging.error("Dockerfile not found in the .nixpacks directory")
        click.echo("Dockerfile not found in the .nixpacks directory")
        return

    # Move the Dockerfile to the project root
    dockerfile_destination = os.path.join(project_path, "Dockerfile")
    os.rename(dockerfile_path, dockerfile_destination)
    logging.info(f"Moved Dockerfile to {dockerfile_destination}")
    click.echo(f"Moved Dockerfile to {dockerfile_destination}")

    logging.info("Building Docker image with Nixpacks...")
    click.echo("Building Docker image with Nixpacks...")

    try:
        # Build with image name using the Dockerfile now in the project root
        build_with_name_result = subprocess.run(
            ["nixpacks", "build", f"--name={image_name}", project_path], capture_output=True, text=True, check=True)
        modified_build_with_name_output = build_with_name_result.stdout.replace(
            "docker run -it", "docker run -p PORT:PORT -it")
        click.echo(modified_build_with_name_output)

    except subprocess.CalledProcessError as e:
        error_message = e.stderr  # Capture the standard error output for the error message
        logging.error(f"Error during the build process: {error_message}")
        click.echo(f"Error during the build process: {error_message}")
        return


@click.command()
def deploy():
    """Deploy the project using AWS Copilot."""
    default_project_name = find_config_file()

    if default_project_name:
        project_name = click.prompt(
            "Please enter your project name to load its configuration", type=str, default=default_project_name)
    else:
        project_name = click.prompt(
            "Please enter your project name to load its configuration", type=str)

    config_filename = f"{project_name}_fd_config.json"

    if not os.path.exists(config_filename):
        click.echo(
            "Configuration file not found. Please run the init command first.")
        return

    # Load configuration
    with open(config_filename, 'r') as config_file:
        config = json.load(config_file)

    # Create a shell script from the configuration
    script_content = f"""#!/bin/bash
    copilot init \\
        --app "{config['project_name']}" \\
        --name "{config['service_name']}" \\
        --type "{config['service_type']}" \\
        --dockerfile "{config['dockerfile_path']}" \\
        --env "{config['environment_name']}" \\
        --port {config['service_port']} \\
        --deploy
    """

    script_path = os.path.join(os.getcwd(), 'deploy_script.sh')
    with open(script_path, 'w') as script_file:
        script_file.write(script_content)

    # Make the script executable
    os.chmod(script_path, 0o755)

    click.echo("\nStarting the deployment process...")

    # Execute the script
    try:
        subprocess.run(script_path, check=True)
        click.echo("Deployment successful!")
    except subprocess.CalledProcessError as e:
        click.echo("Error during deployment:")
        logging.error(f"Deployment error: {e}")
        if e.stderr:
            click.echo(e.stderr)
        if e.stdout:
            click.echo(e.stdout)

    # Clean up the script
    os.remove(script_path)


@click.command()
@click.option('-f', '--force', is_flag=True, help='Force delete all files and directories even if no config file is found.')
def purge(force):
    """Delete the entire application and all related resources using AWS Copilot."""
    default_project_name = find_config_file()

    if default_project_name:
        project_name = click.prompt(
            "Please enter the project name to delete", type=str, default=default_project_name)
    else:
        project_name = click.prompt(
            "Please enter the project name to delete", type=str)

    config_filename = f"{project_name}_fd_config.json"
    nix_directory = ".nixpacks"
    docker_filename = "Dockerfile"
    copilot_directory = "copilot"

    if not force:
        if not os.path.exists(config_filename):
            click.echo(
                "Configuration file not found. Please check the project name and try again.")
            return

    if force or click.confirm(f"Are you sure you want to delete the application '{project_name}' and all its resources? This action cannot be undone."):
        if not force:
            # Load configuration
            with open(config_filename, 'r') as config_file:
                config = json.load(config_file)

            # Create a shell script to delete the application
            script_content = f"""#!/bin/bash
            copilot app delete --name "{config['project_name']}" --yes
            """

            script_path = os.path.join(os.getcwd(), 'delete_script.sh')
            with open(script_path, 'w') as script_file:
                script_file.write(script_content)

            # Make the script executable
            os.chmod(script_path, 0o755)

            click.echo("\nStarting the application deletion process...")
            try:
                # Execute the script
                subprocess.run(script_path, check=True)
                click.echo("Application successfully deleted.")
                logging.info(
                    f"Application '{config['project_name']}' successfully deleted.")
            except subprocess.CalledProcessError as e:
                click.echo("Error during application deletion:")
                logging.error(f"Deletion error: {e}")
                click.echo(str(e))
            finally:
                # Clean up the script
                os.remove(script_path)

        # Remove directories and files safely
        if os.path.exists(nix_directory):
            shutil.rmtree(nix_directory)
        if os.path.exists(copilot_directory):
            shutil.rmtree(copilot_directory)
        if os.path.exists(docker_filename):
            os.remove(docker_filename)
        if os.path.exists(config_filename):
            os.remove(config_filename)
            logging.info(f"Removed configuration file: {config_filename}")
    else:
        click.echo("Application deletion cancelled.")


# Add commands to the CLI group
cli.add_command(init)
cli.add_command(build)
cli.add_command(deploy)
cli.add_command(purge)

if __name__ == '__main__':
    cli()
