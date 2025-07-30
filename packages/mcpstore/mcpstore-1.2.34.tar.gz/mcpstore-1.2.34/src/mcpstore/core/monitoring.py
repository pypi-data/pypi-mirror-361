"""
MCPStore 监控和统计模块
提供性能监控、工具使用统计、告警管理等功能
"""

import asyncio
import time
import psutil
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from pathlib import Path
import aiohttp
import logging

logger = logging.getLogger(__name__)

@dataclass
class PerformanceMetrics:
    """性能指标数据类"""
    api_response_time: float  # API平均响应时间(ms)
    active_connections: int   # 活跃连接数
    today_api_calls: int     # 今日API调用数
    memory_usage: float      # 内存使用率(%)
    cpu_usage: float         # CPU使用率(%)
    uptime: float           # 运行时间(秒)

@dataclass
class ToolUsageStats:
    """工具使用统计数据类"""
    tool_name: str
    service_name: str
    execution_count: int
    last_executed: Optional[str]
    average_response_time: float
    success_rate: float

@dataclass
class AlertInfo:
    """告警信息数据类"""
    alert_id: str
    type: str  # 'warning', 'error', 'info'
    title: str
    message: str
    timestamp: str
    service_name: Optional[str] = None
    resolved: bool = False

@dataclass
class NetworkEndpoint:
    """网络端点监控数据类"""
    endpoint_name: str
    url: str
    status: str  # 'healthy', 'warning', 'error'
    response_time: float
    last_checked: str
    uptime_percentage: float

@dataclass
class SystemResourceInfo:
    """系统资源信息数据类"""
    server_uptime: str
    memory_total: int
    memory_used: int
    memory_percentage: float
    disk_usage_percentage: float
    network_traffic_in: int
    network_traffic_out: int

class MonitoringManager:
    """监控管理器"""
    
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.stats_file = data_dir / "monitoring_stats.json"
        self.alerts_file = data_dir / "alerts.json"
        self.tool_usage_file = data_dir / "tool_usage.json"
        
        # 运行时统计
        self.start_time = time.time()
        self.api_call_times = []
        self.api_call_count = 0
        self.active_connections = 0
        
        # 确保数据文件存在
        self._ensure_data_files()
    
    def _ensure_data_files(self):
        """确保数据文件存在"""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        if not self.stats_file.exists():
            self.stats_file.write_text(json.dumps({
                "daily_api_calls": {},
                "tool_usage": {},
                "network_endpoints": []
            }, indent=2))
        
        if not self.alerts_file.exists():
            self.alerts_file.write_text(json.dumps([], indent=2))
        
        if not self.tool_usage_file.exists():
            self.tool_usage_file.write_text(json.dumps({}, indent=2))
    
    def record_api_call(self, response_time: float):
        """记录API调用"""
        self.api_call_count += 1
        self.api_call_times.append(response_time)
        
        # 只保留最近100次调用的响应时间
        if len(self.api_call_times) > 100:
            self.api_call_times = self.api_call_times[-100:]
        
        # 记录今日调用数
        today = datetime.now().strftime("%Y-%m-%d")
        try:
            with open(self.stats_file, 'r') as f:
                stats = json.load(f)
            
            if "daily_api_calls" not in stats:
                stats["daily_api_calls"] = {}
            
            stats["daily_api_calls"][today] = stats["daily_api_calls"].get(today, 0) + 1
            
            with open(self.stats_file, 'w') as f:
                json.dump(stats, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to record API call: {e}")
    
    def record_tool_execution(self, tool_name: str, service_name: str, 
                            response_time: float, success: bool):
        """记录工具执行"""
        try:
            with open(self.tool_usage_file, 'r') as f:
                usage_data = json.load(f)
            
            key = f"{service_name}:{tool_name}"
            if key not in usage_data:
                usage_data[key] = {
                    "tool_name": tool_name,
                    "service_name": service_name,
                    "execution_count": 0,
                    "total_response_time": 0.0,
                    "success_count": 0,
                    "last_executed": None
                }
            
            tool_stats = usage_data[key]
            tool_stats["execution_count"] += 1
            tool_stats["total_response_time"] = float(tool_stats["total_response_time"]) + response_time
            tool_stats["last_executed"] = datetime.now().isoformat()
            
            if success:
                tool_stats["success_count"] += 1
            
            with open(self.tool_usage_file, 'w') as f:
                json.dump(usage_data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Failed to record tool execution: {e}")
    
    def add_alert(self, alert_type: str, title: str, message: str, 
                  service_name: Optional[str] = None) -> str:
        """添加告警"""
        alert_id = f"alert_{int(time.time() * 1000)}"
        alert = AlertInfo(
            alert_id=alert_id,
            type=alert_type,
            title=title,
            message=message,
            timestamp=datetime.now().isoformat(),
            service_name=service_name
        )
        
        try:
            with open(self.alerts_file, 'r') as f:
                alerts = json.load(f)
            
            alerts.append(asdict(alert))
            
            # 只保留最近50个告警
            if len(alerts) > 50:
                alerts = alerts[-50:]
            
            with open(self.alerts_file, 'w') as f:
                json.dump(alerts, f, indent=2)
            
            return alert_id
        except Exception as e:
            logger.error(f"Failed to add alert: {e}")
            return ""
    
    def get_performance_metrics(self) -> PerformanceMetrics:
        """获取性能指标"""
        # API响应时间
        avg_response_time = (
            sum(self.api_call_times) / len(self.api_call_times) 
            if self.api_call_times else 0
        )
        
        # 今日API调用数
        today = datetime.now().strftime("%Y-%m-%d")
        today_calls = 0
        try:
            with open(self.stats_file, 'r') as f:
                stats = json.load(f)
            today_calls = stats.get("daily_api_calls", {}).get(today, 0)
        except:
            pass
        
        # 系统资源
        memory = psutil.virtual_memory()
        cpu_percent = psutil.cpu_percent(interval=0.1)
        uptime = time.time() - self.start_time
        
        return PerformanceMetrics(
            api_response_time=round(avg_response_time, 2),
            active_connections=self.active_connections,
            today_api_calls=today_calls,
            memory_usage=round(memory.percent, 1),
            cpu_usage=round(cpu_percent, 1),
            uptime=round(uptime, 1)
        )
    
    def get_tool_usage_stats(self, limit: int = 10) -> List[ToolUsageStats]:
        """获取工具使用统计"""
        try:
            with open(self.tool_usage_file, 'r') as f:
                usage_data = json.load(f)
            
            stats = []
            for key, data in usage_data.items():
                if data["execution_count"] > 0:
                    avg_response_time = data["total_response_time"] / data["execution_count"]
                    success_rate = data["success_count"] / data["execution_count"] * 100
                    
                    stats.append(ToolUsageStats(
                        tool_name=data["tool_name"],
                        service_name=data["service_name"],
                        execution_count=data["execution_count"],
                        last_executed=data["last_executed"],
                        average_response_time=round(avg_response_time, 2),
                        success_rate=round(success_rate, 1)
                    ))
            
            # 按执行次数排序
            stats.sort(key=lambda x: x.execution_count, reverse=True)
            return stats[:limit]
            
        except Exception as e:
            logger.error(f"Failed to get tool usage stats: {e}")
            return []
    
    def get_alerts(self, unresolved_only: bool = False) -> List[AlertInfo]:
        """获取告警列表"""
        try:
            with open(self.alerts_file, 'r') as f:
                alerts_data = json.load(f)
            
            alerts = [AlertInfo(**alert) for alert in alerts_data]
            
            if unresolved_only:
                alerts = [alert for alert in alerts if not alert.resolved]
            
            # 按时间倒序
            alerts.sort(key=lambda x: x.timestamp, reverse=True)
            return alerts
            
        except Exception as e:
            logger.error(f"Failed to get alerts: {e}")
            return []
    
    def resolve_alert(self, alert_id: str) -> bool:
        """解决告警"""
        try:
            with open(self.alerts_file, 'r') as f:
                alerts_data = json.load(f)
            
            for alert in alerts_data:
                if alert["alert_id"] == alert_id:
                    alert["resolved"] = True
                    break
            
            with open(self.alerts_file, 'w') as f:
                json.dump(alerts_data, f, indent=2)
            
            return True
        except Exception as e:
            logger.error(f"Failed to resolve alert: {e}")
            return False
    
    def clear_all_alerts(self) -> bool:
        """清除所有告警"""
        try:
            with open(self.alerts_file, 'w') as f:
                json.dump([], f, indent=2)
            return True
        except Exception as e:
            logger.error(f"Failed to clear alerts: {e}")
            return False
    
    async def check_network_endpoints(self, endpoints: List[Dict[str, str]]) -> List[NetworkEndpoint]:
        """检查网络端点状态"""
        results = []
        
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=5)) as session:
            for endpoint in endpoints:
                name = endpoint.get("name", "Unknown")
                url = endpoint.get("url", "")
                
                start_time = time.time()
                status = "error"
                response_time = 0
                
                try:
                    async with session.get(url) as response:
                        response_time = (time.time() - start_time) * 1000
                        if response.status == 200:
                            status = "healthy" if response_time < 1000 else "warning"
                        else:
                            status = "warning"
                except:
                    status = "error"
                    response_time = 5000  # 超时
                
                results.append(NetworkEndpoint(
                    endpoint_name=name,
                    url=url,
                    status=status,
                    response_time=round(response_time, 2),
                    last_checked=datetime.now().isoformat(),
                    uptime_percentage=95.0  # 简化实现，实际应该基于历史数据
                ))
        
        return results
    
    def get_system_resource_info(self) -> SystemResourceInfo:
        """获取系统资源信息"""
        # 内存信息
        memory = psutil.virtual_memory()
        
        # 磁盘信息
        disk = psutil.disk_usage('/')
        
        # 网络信息
        net_io = psutil.net_io_counters()
        
        # 运行时间
        uptime_seconds = time.time() - self.start_time
        uptime_str = str(timedelta(seconds=int(uptime_seconds)))
        
        return SystemResourceInfo(
            server_uptime=uptime_str,
            memory_total=memory.total,
            memory_used=memory.used,
            memory_percentage=round(memory.percent, 1),
            disk_usage_percentage=round(disk.percent, 1),
            network_traffic_in=net_io.bytes_recv,
            network_traffic_out=net_io.bytes_sent
        )
    
    def increment_active_connections(self):
        """增加活跃连接数"""
        self.active_connections += 1
    
    def decrement_active_connections(self):
        """减少活跃连接数"""
        self.active_connections = max(0, self.active_connections - 1)
