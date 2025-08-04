"""
================================================================================
F3.4: HPC TRAINING LAUNCHER (AWS SPOT + RAY)
================================================================================

🎯 **AMAÇ:** AWS Spot instances üzerinde Ray cluster ile large-scale training
📋 **KAPSAM:** 50M hands, parallel Optuna sweeps, cost optimization
🔧 **ENTEGRASYON:** Docker + AWS + Ray seamless integration

================================================================================
"""

import boto3
import ray
import optuna
import subprocess
import time
import logging
import json
import os
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
import yaml

@dataclass
class HPCConfig:
    """Configuration for HPC training setup."""
    # AWS Configuration
    aws_region: str = "us-east-1"
    instance_type: str = "c5.2xlarge"  # 8 vCPU, 16 GB RAM
    spot_price: Optional[float] = None  # Auto-detect
    min_instances: int = 2
    max_instances: int = 8
    
    # Ray Configuration
    ray_head_port: int = 6379
    ray_dashboard_port: int = 8265
    ray_object_store_memory: int = 4000000000  # 4GB
    
    # Training Configuration
    total_timesteps: int = 50000000  # 50M hands
    n_trials: int = 50
    n_workers: int = 4
    study_name: str = "hpc_blackjack_optimization"
    
    # Cost Management
    max_hours: int = 24
    budget_limit: float = 100.0  # USD
    
    def to_dict(self) -> Dict:
        return {
            "aws_region": self.aws_region,
            "instance_type": self.instance_type,
            "spot_price": self.spot_price,
            "min_instances": self.min_instances,
            "max_instances": self.max_instances,
            "ray_head_port": self.ray_head_port,
            "ray_dashboard_port": self.ray_dashboard_port,
            "ray_object_store_memory": self.ray_object_store_memory,
            "total_timesteps": self.total_timesteps,
            "n_trials": self.n_trials,
            "n_workers": self.n_workers,
            "study_name": self.study_name,
            "max_hours": self.max_hours,
            "budget_limit": self.budget_limit
        }

class HPCClusterManager:
    """
    Manages HPC cluster for large-scale blackjack AI training.
    
    Handles AWS Spot instance provisioning, Ray cluster setup,
    and cost-optimized training execution.
    """
    
    def __init__(self, config: HPCConfig):
        self.config = config
        self.ec2_client = boto3.client('ec2', region_name=config.aws_region)
        self.ec2_resource = boto3.resource('ec2', region_name=config.aws_region)
        
        # Cluster state
        self.head_instance = None
        self.worker_instances = []
        self.cluster_start_time = None
        
        # Logging
        self.logger = logging.getLogger("HPCClusterManager")
        self.logger.setLevel(logging.INFO)
        
        # Setup logging
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
    
    def get_spot_price(self) -> float:
        """Get current spot price for the instance type."""
        try:
            response = self.ec2_client.describe_spot_price_history(
                InstanceTypes=[self.config.instance_type],
                ProductDescription='Linux/UNIX',
                StartTime=datetime.now() - timedelta(hours=1),
                MaxResults=1
            )
            
            if response['SpotPriceHistory']:
                return float(response['SpotPriceHistory'][0]['SpotPrice'])
            else:
                # Fallback to on-demand price estimate
                return 0.17  # Approximate c5.2xlarge price
                
        except Exception as e:
            self.logger.warning(f"Could not get spot price: {e}")
            return 0.17
    
    def create_security_group(self) -> str:
        """Create security group for Ray cluster."""
        try:
            # Check if security group already exists
            response = self.ec2_client.describe_security_groups(
                GroupNames=['blackjack-ray-cluster']
            )
            return response['SecurityGroups'][0]['GroupId']
        except:
            pass
        
        # Create new security group
        response = self.ec2_client.create_security_group(
            GroupName='blackjack-ray-cluster',
            Description='Security group for Blackjack AI Ray cluster'
        )
        security_group_id = response['GroupId']
        
        # Add rules for Ray
        self.ec2_client.authorize_security_group_ingress(
            GroupId=security_group_id,
            IpPermissions=[
                {
                    'IpProtocol': 'tcp',
                    'FromPort': 22,
                    'ToPort': 22,
                    'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
                },
                {
                    'IpProtocol': 'tcp',
                    'FromPort': self.config.ray_head_port,
                    'ToPort': self.config.ray_head_port,
                    'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
                },
                {
                    'IpProtocol': 'tcp',
                    'FromPort': self.config.ray_dashboard_port,
                    'ToPort': self.config.ray_dashboard_port,
                    'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
                }
            ]
        )
        
        return security_group_id
    
    def launch_head_instance(self) -> str:
        """Launch Ray head instance."""
        self.logger.info("Launching Ray head instance...")
        
        # Get spot price if not specified
        if self.config.spot_price is None:
            self.config.spot_price = self.get_spot_price()
        
        security_group_id = self.create_security_group()
        
        # User data script for head instance
        user_data = f"""#!/bin/bash
# Install Docker
yum update -y
yum install -y docker git
systemctl start docker
systemctl enable docker

# Install Docker Compose
curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Clone repository (replace with your repo)
git clone https://github.com/your-repo/blackjack-ai.git /app
cd /app

# Start Ray head
docker-compose up -d ray-head

# Wait for Ray to be ready
sleep 30

# Start training
docker-compose up training-controller
"""
        
        # Launch spot instance
        response = self.ec2_client.run_instances(
            ImageId='ami-0c02fb55956c7d316',  # Amazon Linux 2
            MinCount=1,
            MaxCount=1,
            InstanceType=self.config.instance_type,
            KeyName='your-key-pair',  # Replace with your key pair
            SecurityGroupIds=[security_group_id],
            UserData=user_data,
            InstanceMarketOptions={
                'MarketType': 'spot',
                'SpotOptions': {
                    'MaxPrice': str(self.config.spot_price),
                    'SpotInstanceType': 'one-time',
                    'InstanceInterruptionBehavior': 'terminate'
                }
            },
            TagSpecifications=[
                {
                    'ResourceType': 'instance',
                    'Tags': [
                        {'Key': 'Name', 'Value': 'blackjack-ray-head'},
                        {'Key': 'Project', 'Value': 'blackjack-ai'},
                        {'Key': 'Role', 'Value': 'ray-head'}
                    ]
                }
            ]
        )
        
        instance_id = response['Instances'][0]['InstanceId']
        self.head_instance = instance_id
        
        self.logger.info(f"Launched head instance: {instance_id}")
        
        # Wait for instance to be running
        waiter = self.ec2_client.get_waiter('instance_running')
        waiter.wait(InstanceIds=[instance_id])
        
        # Get public IP
        response = self.ec2_client.describe_instances(InstanceIds=[instance_id])
        public_ip = response['Reservations'][0]['Instances'][0]['PublicIpAddress']
        
        self.logger.info(f"Head instance ready at: {public_ip}")
        return public_ip
    
    def launch_worker_instances(self, head_ip: str, count: int) -> List[str]:
        """Launch Ray worker instances."""
        self.logger.info(f"Launching {count} worker instances...")
        
        security_group_id = self.create_security_group()
        worker_ips = []
        
        # User data script for worker instances
        user_data = f"""#!/bin/bash
# Install Docker
yum update -y
yum install -y docker git
systemctl start docker
systemctl enable docker

# Install Docker Compose
curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Clone repository
git clone https://github.com/your-repo/blackjack-ai.git /app
cd /app

# Start Ray worker
docker-compose up -d ray-worker-1
"""
        
        for i in range(count):
            response = self.ec2_client.run_instances(
                ImageId='ami-0c02fb55956c7d316',
                MinCount=1,
                MaxCount=1,
                InstanceType=self.config.instance_type,
                KeyName='your-key-pair',
                SecurityGroupIds=[security_group_id],
                UserData=user_data,
                InstanceMarketOptions={
                    'MarketType': 'spot',
                    'SpotOptions': {
                        'MaxPrice': str(self.config.spot_price),
                        'SpotInstanceType': 'one-time',
                        'InstanceInterruptionBehavior': 'terminate'
                    }
                },
                TagSpecifications=[
                    {
                        'ResourceType': 'instance',
                        'Tags': [
                            {'Key': 'Name', 'Value': f'blackjack-ray-worker-{i+1}'},
                            {'Key': 'Project', 'Value': 'blackjack-ai'},
                            {'Key': 'Role', 'Value': 'ray-worker'}
                        ]
                    }
                ]
            )
            
            instance_id = response['Instances'][0]['InstanceId']
            self.worker_instances.append(instance_id)
            
            # Wait for instance to be running
            waiter = self.ec2_client.get_waiter('instance_running')
            waiter.wait(InstanceIds=[instance_id])
            
            # Get public IP
            response = self.ec2_client.describe_instances(InstanceIds=[instance_id])
            public_ip = response['Reservations'][0]['Instances'][0]['PublicIpAddress']
            worker_ips.append(public_ip)
            
            self.logger.info(f"Launched worker {i+1}: {instance_id} at {public_ip}")
        
        return worker_ips
    
    def start_cluster(self) -> Dict[str, str]:
        """Start the complete HPC cluster."""
        self.logger.info("Starting HPC cluster...")
        self.cluster_start_time = datetime.now()
        
        # Launch head instance
        head_ip = self.launch_head_instance()
        
        # Launch worker instances
        worker_ips = self.launch_worker_instances(head_ip, self.config.min_instances)
        
        cluster_info = {
            'head_ip': head_ip,
            'worker_ips': worker_ips,
            'head_instance_id': self.head_instance,
            'worker_instance_ids': self.worker_instances,
            'start_time': self.cluster_start_time.isoformat(),
            'ray_dashboard': f"http://{head_ip}:{self.config.ray_dashboard_port}"
        }
        
        self.logger.info(f"Cluster started successfully!")
        self.logger.info(f"Ray Dashboard: {cluster_info['ray_dashboard']}")
        
        return cluster_info
    
    def monitor_cluster(self, cluster_info: Dict[str, str]):
        """Monitor cluster health and training progress."""
        self.logger.info("Starting cluster monitoring...")
        
        start_time = datetime.fromisoformat(cluster_info['start_time'])
        max_duration = timedelta(hours=self.config.max_hours)
        
        while True:
            current_time = datetime.now()
            elapsed = current_time - start_time
            
            # Check time limit
            if elapsed > max_duration:
                self.logger.info("Maximum time limit reached, stopping cluster...")
                break
            
            # Check instance status
            all_instances = [cluster_info['head_instance_id']] + cluster_info['worker_instance_ids']
            
            try:
                response = self.ec2_client.describe_instances(InstanceIds=all_instances)
                
                running_count = 0
                for reservation in response['Reservations']:
                    for instance in reservation['Instances']:
                        if instance['State']['Name'] == 'running':
                            running_count += 1
                
                self.logger.info(f"Cluster status: {running_count}/{len(all_instances)} instances running")
                
                if running_count < len(all_instances):
                    self.logger.warning("Some instances are not running!")
                
            except Exception as e:
                self.logger.error(f"Error monitoring cluster: {e}")
            
            # Wait before next check
            time.sleep(60)  # Check every minute
    
    def stop_cluster(self, cluster_info: Dict[str, str]):
        """Stop the HPC cluster and terminate instances."""
        self.logger.info("Stopping HPC cluster...")
        
        all_instances = [cluster_info['head_instance_id']] + cluster_info['worker_instance_ids']
        
        try:
            self.ec2_client.terminate_instances(InstanceIds=all_instances)
            self.logger.info("All instances terminated")
        except Exception as e:
            self.logger.error(f"Error terminating instances: {e}")
    
    def estimate_cost(self) -> float:
        """Estimate total cost for the training session."""
        # Get spot price
        spot_price = self.get_spot_price()
        
        # Calculate instance hours
        total_instances = 1 + self.config.min_instances  # head + workers
        total_hours = self.config.max_hours
        
        # Estimate cost
        estimated_cost = spot_price * total_instances * total_hours
        
        self.logger.info(f"Estimated cost: ${estimated_cost:.2f}")
        return estimated_cost

def create_hpc_config() -> HPCConfig:
    """Create HPC configuration with sensible defaults."""
    return HPCConfig(
        aws_region="us-east-1",
        instance_type="c5.2xlarge",
        min_instances=2,
        max_instances=4,
        total_timesteps=50000000,  # 50M hands
        n_trials=50,
        max_hours=24,
        budget_limit=100.0
    )

def main():
    """Main function to launch HPC training."""
    print("🚀 F3.4: HPC Training Launcher")
    print("=" * 50)
    
    # Create configuration
    config = create_hpc_config()
    
    # Estimate cost
    manager = HPCClusterManager(config)
    estimated_cost = manager.estimate_cost()
    
    if estimated_cost > config.budget_limit:
        print(f"⚠️  Estimated cost (${estimated_cost:.2f}) exceeds budget limit (${config.budget_limit})")
        return
    
    # Start cluster
    cluster_info = manager.start_cluster()
    
    # Save cluster info
    with open('cluster_info.json', 'w') as f:
        json.dump(cluster_info, f, indent=2)
    
    print(f"✅ Cluster started successfully!")
    print(f"📊 Ray Dashboard: {cluster_info['ray_dashboard']}")
    print(f"💰 Estimated cost: ${estimated_cost:.2f}")
    
    try:
        # Monitor cluster
        manager.monitor_cluster(cluster_info)
    except KeyboardInterrupt:
        print("\n🛑 Interrupted by user")
    finally:
        # Stop cluster
        manager.stop_cluster(cluster_info)
        print("✅ Cluster stopped")

if __name__ == "__main__":
    main() 