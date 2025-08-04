#!/usr/bin/env python3
"""
================================================================================
FAZ3.x DOCKER ENVIRONMENT MANAGER
================================================================================

🎯 **AMAÇ:** Docker ortamlarını yönetmek için unified interface
📋 **KAPSAM:** Development, production, HPC cluster management
🔧 **ÖZELLİKLER:** 
   • Environment setup ve teardown
   • Health checking ve monitoring
   • Resource management
   • Log aggregation

================================================================================
"""

import os
import sys
import time
import json
import subprocess
import argparse
from typing import Dict, List, Optional, Any
from pathlib import Path
import docker
import yaml

class DockerManager:
    """Docker ortamlarını yöneten sınıf."""
    
    def __init__(self, project_name: str = "blackjack"):
        self.project_name = project_name
        self.client = docker.from_env()
        self.base_dir = Path(__file__).parent.parent
        
    def start_development_env(self) -> bool:
        """Development ortamını başlatır."""
        print("🚀 Starting Development Environment...")
        
        try:
            # Docker Compose ile development ortamını başlat
            result = subprocess.run([
                "docker-compose", "-f", "docker-compose-dev.yml", "up", "-d"
            ], cwd=self.base_dir, capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ Development environment started successfully!")
                print("📖 Jupyter Lab: http://localhost:8888")
                print("📊 TensorBoard: http://localhost:6006")
                print("📈 Grafana: http://localhost:3000 (admin/admin)")
                return True
            else:
                print(f"❌ Failed to start development environment: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Error starting development environment: {e}")
            return False
    
    def start_production_env(self) -> bool:
        """Production ortamını başlatır."""
        print("🚀 Starting Production Environment...")
        
        try:
            result = subprocess.run([
                "docker-compose", "up", "-d"
            ], cwd=self.base_dir, capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ Production environment started successfully!")
                print("📊 Ray Dashboard: http://localhost:8265")
                return True
            else:
                print(f"❌ Failed to start production environment: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Error starting production environment: {e}")
            return False
    
    def stop_environment(self, env_type: str = "dev") -> bool:
        """Belirtilen ortamı durdurur."""
        print(f"🛑 Stopping {env_type} environment...")
        
        try:
            compose_file = "docker-compose-dev.yml" if env_type == "dev" else "docker-compose.yml"
            result = subprocess.run([
                "docker-compose", "-f", compose_file, "down", "-v"
            ], cwd=self.base_dir, capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"✅ {env_type} environment stopped successfully!")
                return True
            else:
                print(f"❌ Failed to stop {env_type} environment: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Error stopping {env_type} environment: {e}")
            return False
    
    def get_container_status(self) -> Dict[str, Any]:
        """Container durumlarını döndürür."""
        status = {
            "containers": [],
            "total": 0,
            "running": 0,
            "stopped": 0
        }
        
        try:
            containers = self.client.containers.list(all=True, 
                                                   filters={"label": f"com.docker.compose.project={self.project_name}"})
            
            for container in containers:
                container_info = {
                    "name": container.name,
                    "status": container.status,
                    "image": container.image.tags[0] if container.image.tags else "unknown",
                    "ports": container.ports,
                    "created": container.attrs['Created']
                }
                status["containers"].append(container_info)
                
                if container.status == "running":
                    status["running"] += 1
                else:
                    status["stopped"] += 1
            
            status["total"] = len(containers)
            
        except Exception as e:
            print(f"❌ Error getting container status: {e}")
            
        return status
    
    def health_check(self) -> Dict[str, bool]:
        """Sistem sağlık kontrolü yapar."""
        health = {
            "docker_daemon": False,
            "containers_healthy": False,
            "services_accessible": False
        }
        
        try:
            # Docker daemon check
            self.client.ping()
            health["docker_daemon"] = True
            
            # Container health check
            containers = self.client.containers.list(filters={"status": "running"})
            if containers:
                health["containers_healthy"] = True
            
            # Service accessibility check
            import requests
            services_to_check = [
                ("http://localhost:8888", "Jupyter"),
                ("http://localhost:6006", "TensorBoard"),
                ("http://localhost:3000", "Grafana")
            ]
            
            accessible_services = 0
            for url, name in services_to_check:
                try:
                    response = requests.get(url, timeout=5)
                    if response.status_code == 200:
                        accessible_services += 1
                        print(f"✅ {name} is accessible at {url}")
                    else:
                        print(f"⚠️ {name} returned status {response.status_code}")
                except:
                    print(f"❌ {name} is not accessible at {url}")
            
            if accessible_services > 0:
                health["services_accessible"] = True
                
        except Exception as e:
            print(f"❌ Health check error: {e}")
            
        return health
    
    def get_logs(self, service_name: str, lines: int = 100) -> str:
        """Belirtilen servisin loglarını döndürür."""
        try:
            result = subprocess.run([
                "docker-compose", "logs", "--tail", str(lines), service_name
            ], cwd=self.base_dir, capture_output=True, text=True)
            
            return result.stdout if result.returncode == 0 else result.stderr
            
        except Exception as e:
            return f"Error getting logs: {e}"
    
    def clean_resources(self) -> bool:
        """Kullanılmayan Docker kaynaklarını temizler."""
        print("🧹 Cleaning Docker resources...")
        
        try:
            # Remove unused containers
            result = subprocess.run(["docker", "container", "prune", "-f"], 
                                  capture_output=True, text=True)
            print("✅ Cleaned unused containers")
            
            # Remove unused images
            result = subprocess.run(["docker", "image", "prune", "-f"], 
                                  capture_output=True, text=True)
            print("✅ Cleaned unused images")
            
            # Remove unused volumes
            result = subprocess.run(["docker", "volume", "prune", "-f"], 
                                  capture_output=True, text=True)
            print("✅ Cleaned unused volumes")
            
            return True
            
        except Exception as e:
            print(f"❌ Error cleaning resources: {e}")
            return False

def main():
    """Ana fonksiyon."""
    parser = argparse.ArgumentParser(description="Blackjack AI Docker Manager")
    parser.add_argument("command", choices=[
        "start-dev", "start-prod", "stop-dev", "stop-prod", 
        "status", "health", "logs", "clean"
    ], help="Command to execute")
    parser.add_argument("--service", help="Service name for logs command")
    parser.add_argument("--lines", type=int, default=100, help="Number of log lines")
    
    args = parser.parse_args()
    
    manager = DockerManager()
    
    if args.command == "start-dev":
        manager.start_development_env()
    elif args.command == "start-prod":
        manager.start_production_env()
    elif args.command == "stop-dev":
        manager.stop_environment("dev")
    elif args.command == "stop-prod":
        manager.stop_environment("prod")
    elif args.command == "status":
        status = manager.get_container_status()
        print(f"📊 Container Status:")
        print(f"   Total: {status['total']}")
        print(f"   Running: {status['running']}")
        print(f"   Stopped: {status['stopped']}")
        for container in status["containers"]:
            print(f"   - {container['name']}: {container['status']}")
    elif args.command == "health":
        health = manager.health_check()
        print(f"🏥 Health Check Results:")
        for check, result in health.items():
            status = "✅" if result else "❌"
            print(f"   {check}: {status}")
    elif args.command == "logs":
        if not args.service:
            print("❌ Service name required for logs command")
            sys.exit(1)
        logs = manager.get_logs(args.service, args.lines)
        print(logs)
    elif args.command == "clean":
        manager.clean_resources()

if __name__ == "__main__":
    main() 