"""
Configuration management for AUGR with multi-project support.
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional


class AugrConfig:
    """Configuration manager for AUGR with multi-project support"""
    
    def __init__(self):
        self.config_dir = Path.home() / ".augr"
        self.projects_dir = self.config_dir / "projects"
        self.global_config_file = self.config_dir / "global.json"
        
    def ensure_config_dir(self):
        """Ensure the configuration directory structure exists"""
        self.config_dir.mkdir(exist_ok=True)
        self.projects_dir.mkdir(exist_ok=True)
        
        # Set secure permissions
        os.chmod(self.config_dir, 0o700)
        os.chmod(self.projects_dir, 0o700)
    
    def get_global_config(self) -> Dict:
        """Get global configuration (default project, etc.)"""
        if not self.global_config_file.exists():
            return {}
        
        try:
            with open(self.global_config_file, 'r') as f:
                return json.load(f)
        except Exception:
            return {}
    
    def save_global_config(self, config: Dict):
        """Save global configuration"""
        self.ensure_config_dir()
        
        with open(self.global_config_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        # Set secure permissions
        os.chmod(self.global_config_file, 0o600)
    
    def list_projects(self) -> List[str]:
        """List all available project names"""
        if not self.projects_dir.exists():
            return []
        
        projects = []
        for config_file in self.projects_dir.glob("*.json"):
            projects.append(config_file.stem)
        
        return sorted(projects)
    
    def project_exists(self, project_name: str) -> bool:
        """Check if a project configuration exists"""
        project_file = self.projects_dir / f"{project_name}.json"
        return project_file.exists()
    
    def get_project_config(self, project_name: str) -> Optional[Dict]:
        """Get configuration for a specific project"""
        project_file = self.projects_dir / f"{project_name}.json"
        
        if not project_file.exists():
            return None
        
        try:
            with open(project_file, 'r') as f:
                return json.load(f)
        except Exception:
            return None
    
    def save_project_config(self, project_name: str, config: Dict):
        """Save configuration for a specific project"""
        self.ensure_config_dir()
        
        project_file = self.projects_dir / f"{project_name}.json"
        
        with open(project_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        # Set secure permissions
        os.chmod(project_file, 0o600)
    
    def delete_project(self, project_name: str) -> bool:
        """Delete a project configuration"""
        project_file = self.projects_dir / f"{project_name}.json"
        
        if project_file.exists():
            try:
                project_file.unlink()
                return True
            except Exception:
                return False
        
        return False
    
    def get_default_project(self) -> Optional[str]:
        """Get the default project name"""
        global_config = self.get_global_config()
        return global_config.get("default_project")
    
    def set_default_project(self, project_name: str):
        """Set the default project"""
        global_config = self.get_global_config()
        global_config["default_project"] = project_name
        self.save_global_config(global_config)


def get_project_api_key(project_name: str) -> str:
    """
    Get the Braintrust API key for a specific project.
    
    Priority:
    1. Environment variable BRAINTRUST_API_KEY
    2. Project configuration file
    3. Interactive setup
    
    Args:
        project_name: Name of the project
        
    Returns:
        API key string
        
    Raises:
        Exception: If no API key can be obtained
    """
    # Check environment variable first
    env_key = os.getenv("BRAINTRUST_API_KEY")
    if env_key:
        return env_key
    
    config = AugrConfig()
    
    # Check project config
    project_config = config.get_project_config(project_name)
    if project_config and project_config.get("braintrust_api_key"):
        return project_config["braintrust_api_key"]
    
    # Interactive setup
    print(f"\n🔧 Setting up project '{project_name}'")
    print("=" * 50)
    print("To use AUGR, you need a Braintrust API key.")
    print("Get your API key at: https://www.braintrust.dev/app/settings/api-keys")
    print()
    
    api_key = input("Enter your Braintrust API key: ").strip()
    
    if not api_key:
        raise Exception("API key is required to use AUGR")
    
    # Save the configuration
    project_config = {"braintrust_api_key": api_key}
    config.save_project_config(project_name, project_config)
    
    print(f"✅ Configuration saved for project '{project_name}'")
    return api_key


def select_or_create_project(create_new: bool = False, new_project_name: str = None) -> str:
    """
    Select an existing project or create a new one.
    
    Args:
        create_new: If True, create a new project
        new_project_name: Name for the new project (if create_new is True)
        
    Returns:
        Selected project name
    """
    config = AugrConfig()
    existing_projects = config.list_projects()
    
    if create_new:
        if not new_project_name:
            new_project_name = input("Enter new project name: ").strip()
        
        if not new_project_name:
            raise Exception("Project name is required")
        
        if config.project_exists(new_project_name):
            raise Exception(f"Project '{new_project_name}' already exists")
        
        return new_project_name
    
    # If no projects exist, prompt for new project name
    if not existing_projects:
        print("🏗️  No projects found.")
        new_name = input("Enter name for your first project: ").strip()
        
        if not new_name:
            print("Project name cannot be empty. Using 'default'...")
            return "default"
        
        return new_name
    
    # If only one project exists, use it
    if len(existing_projects) == 1:
        project_name = existing_projects[0]
        print(f"📂 Using project: {project_name}")
        return project_name
    
    # Multiple projects - let user choose
    print(f"\nFound {len(existing_projects)} projects:")
    for i, project in enumerate(existing_projects, 1):
        marker = " (default)" if project == config.get_default_project() else ""
        print(f"  {i}. {project}{marker}")
    
    print(f"  {len(existing_projects) + 1}. Create new project")
    
    while True:
        try:
            choice = input(f"\nSelect project [1-{len(existing_projects) + 1}]: ").strip()
            
            if not choice:
                continue
                
            choice_num = int(choice)
            
            if 1 <= choice_num <= len(existing_projects):
                selected_project = existing_projects[choice_num - 1]
                
                # Ask if this should be the default
                set_default = input(f"Set '{selected_project}' as default? [y/N]: ").strip().lower()
                if set_default in ['y', 'yes']:
                    config.set_default_project(selected_project)
                
                return selected_project
            
            elif choice_num == len(existing_projects) + 1:
                new_name = input("Enter new project name: ").strip()
                if not new_name:
                    print("Project name is required")
                    continue
                
                if config.project_exists(new_name):
                    print(f"Project '{new_name}' already exists")
                    continue
                
                return new_name
            
            else:
                print("Invalid choice")
                
        except ValueError:
            print("Please enter a number")
        except KeyboardInterrupt:
            raise Exception("Setup cancelled by user")


def cleanup_all_configs():
    """Remove all AUGR configuration files"""
    config = AugrConfig()
    
    if config.config_dir.exists():
        import shutil
        shutil.rmtree(config.config_dir)
        return True
    
    return False 