#!/usr/bin/env python3
"""
Core node monitoring functionality
"""

import time
import psutil
from typing import Dict, List, Optional, NamedTuple, Tuple
from .ros2_utils import is_ros2_available, get_ros2_nodes_with_pids, check_ros2_environment
from .gpu_monitor import GPUMonitor
from .node_registry import get_registered_nodes, get_registered_node_info


class NodeInfo(NamedTuple):
    """Information about a monitored process/node"""
    name: str
    pid: int
    cpu_percent: float
    ram_mb: float
    gpu_memory_mb: int
    gpu_utilization: float
    gpu_device_id: int
    start_time: float  # Unix timestamp


class NodeMonitor:
    """Monitor registered processes and their resource usage (supports both ROS2 nodes and generic processes)"""
    
    def __init__(self, refresh_interval: float = 5.0):
        self.refresh_interval = refresh_interval
        self.last_refresh = 0.0
        self.processes: Dict[str, psutil.Process] = {}
        self.cores = psutil.cpu_count()
        self.gpu_monitor = GPUMonitor()
        
        # Check ROS2 availability
        self.ros2_available = is_ros2_available()
    
    def cleanup(self):
        """Cleanup resources"""
        pass
        
    def is_ros2_available(self) -> bool:
        """Check if ROS2 is available"""
        return self.ros2_available
    
    def is_gpu_available(self) -> bool:
        """Check if GPU monitoring is available"""
        return self.gpu_monitor.is_available()
    
    def get_gpu_count(self) -> int:
        """Get number of available GPUs"""
        return self.gpu_monitor.get_gpu_count()
    
    def update_nodes(self) -> bool:
        """
        Update the list of monitored nodes and processes
        
        Returns:
            True if nodes were updated, False otherwise
        """
        current_time = time.time()
        
        if current_time - self.last_refresh < self.refresh_interval:
            return False
            
        try:
            # Get all processes to monitor (ROS2 nodes + registered processes)
            all_processes = self._get_all_processes_to_monitor()
            
            # Update processes based on discovered nodes
            current_names = [name for name, pid in all_processes]
            self._remove_dead_nodes(current_names)
            self._add_new_nodes_with_pids(all_processes)
            
            self.last_refresh = current_time
            return True
            
        except Exception:
            return False
    
    def _get_all_processes_to_monitor(self) -> List[Tuple[str, int]]:
        """Get all processes to monitor (primarily from registry, optionally including ROS2 nodes)"""
        all_processes = []
        
        # Primary source: registered processes
        try:
            registered_nodes = get_registered_nodes()
            all_processes.extend(registered_nodes)
        except Exception:
            pass
        
        # Secondary source: ROS2 nodes (if available and not already in registry)
        if self.ros2_available:
            try:
                ros2_nodes = get_ros2_nodes_with_pids()
                # Only add ROS2 nodes that aren't already registered
                registered_names = {name for name, pid in all_processes}
                for name, pid in ros2_nodes:
                    if name not in registered_names:
                        all_processes.append((name, pid))
            except Exception:
                pass
            
        return all_processes
    
    def _remove_dead_nodes(self, current_nodes: List[str]):
        """Remove processes for nodes that no longer exist"""
        nodes_to_remove = [node for node in self.processes if node not in current_nodes]
        for node in nodes_to_remove:
            del self.processes[node]
    
    def _add_new_nodes_with_pids(self, nodes_with_pids: List[Tuple[str, int]]):
        """Add new nodes to monitoring using pre-discovered PIDs"""
        for node, pid in nodes_with_pids:
            if node not in self.processes:
                try:
                    proc = psutil.Process(pid)
                    # Initialize CPU measurement
                    proc.cpu_percent()
                    self.processes[node] = proc
                except psutil.NoSuchProcess:
                    pass
    
    def cleanup_dead_processes(self):
        """Remove processes that are no longer running"""
        nodes_to_remove = []
        for node, process in self.processes.items():
            try:
                if not process.is_running():
                    nodes_to_remove.append(node)
            except psutil.NoSuchProcess:
                nodes_to_remove.append(node)
        
        for node in nodes_to_remove:
            del self.processes[node]
    
    def get_node_info_list(self) -> List[NodeInfo]:
        """
        Get information for all monitored nodes
        
        Returns:
            List of NodeInfo objects
        """
        node_infos = []
        
        for node_name, process in self.processes.items():
            try:
                # Get CPU usage (normalized by number of cores)
                raw_cpu = process.cpu_percent()
                cpu_pct = raw_cpu / self.cores if self.cores > 0 else raw_cpu
                
                # Get RAM memory usage in MB
                memory_info = process.memory_info()
                ram_mb = memory_info.rss / (1024 * 1024)  # Resident Set Size in MB
                
                # Get process start time - prefer registry registration time
                start_time = self._get_process_start_time(node_name, process)
                
                # Get GPU usage
                gpu_mem, gpu_util, gpu_id = self.gpu_monitor.get_gpu_usage(process.pid)
                
                node_info = NodeInfo(
                    name=node_name,
                    pid=process.pid,
                    cpu_percent=cpu_pct,
                    ram_mb=ram_mb,
                    gpu_memory_mb=gpu_mem,
                    gpu_utilization=gpu_util,
                    gpu_device_id=gpu_id,
                    start_time=start_time
                )
                
                node_infos.append(node_info)
                
            except psutil.NoSuchProcess:
                # Process died, will be cleaned up in next update
                continue
            except Exception:
                # Skip this process if we can't get info
                continue
        
        return node_infos
    
    def _get_process_start_time(self, node_name: str, process: psutil.Process) -> float:
        """Get process start time, preferring registry registration time"""
        try:
            # First try to get registration time from registry
            registry_info = get_registered_node_info(node_name)
            if registry_info and 'registration_time' in registry_info:
                return registry_info['registration_time']
        except Exception:
            pass
        
        # Fall back to psutil create_time
        try:
            return process.create_time()
        except Exception:
            # If all else fails, use current time
            return time.time()
    
    def get_nodes_count(self) -> int:
        """Get number of monitored nodes"""
        return len(self.processes)
    
    def force_refresh(self):
        """Force refresh of node list on next update"""
        self.last_refresh = 0.0
    
    def shutdown(self):
        """Clean shutdown of monitoring"""
        self.processes.clear()
        self.gpu_monitor.shutdown()
    
    def get_system_info(self) -> Dict[str, str]:
        """Get system information"""
        info = {
            'CPU Cores': str(self.cores),
            'GPU Count': str(self.get_gpu_count()),
            'Monitored Nodes': str(self.get_nodes_count()),
        }
        
        # Add ROS2 environment info if available
        try:
            ros2_env = check_ros2_environment()
            info.update(ros2_env)
        except Exception:
            # If ROS2 environment check fails, just skip it
            info['ROS2 Available'] = str(self.ros2_available)
        
        return info
