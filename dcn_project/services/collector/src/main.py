"""
Data Collection Service for DCN (Data Collection Node)
Collects metrics and counters from various storage systems and data sources
"""

import asyncio
import logging
import time
from typing import Dict, List, Any
from datetime import datetime
from confluent_kafka import Producer
import json
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MetricCollector:
    """Base class for all metric collectors"""
    
    def __init__(self, name: str, config: Dict[str, Any]):
        self.name = name
        self.config = config
        self.poll_interval = config.get('poll_interval', 60)
        self.timeout = config.get('timeout', 30)
        self.enabled = config.get('enabled', True)
        
    async def collect(self) -> List[Dict[str, Any]]:
        """Override this method in subclasses"""
        raise NotImplementedError
    
    def format_metric(self, name: str, value: float, labels: Dict[str, str], 
                     timestamp: int = None) -> Dict[str, Any]:
        """Format metric in standard structure"""
        return {
            'name': name,
            'value': value,
            'labels': labels,
            'timestamp': timestamp or int(time.time() * 1000),
            'collector': self.name
        }


class ONTAPCollector(MetricCollector):
    """Collects metrics from NetApp ONTAP systems"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__('ontap', config)
        self.api_endpoint = config.get('api_endpoint')
        self.username = config.get('username')
        self.password = config.get('password')
        self.clusters = config.get('clusters', [])
        
    async def collect(self) -> List[Dict[str, Any]]:
        """Collect ONTAP performance metrics"""
        metrics = []
        
        try:
            logger.info(f"Collecting ONTAP metrics from {len(self.clusters)} clusters")
            
            for cluster in self.clusters:
                cluster_name = cluster.get('name')
                logger.debug(f"Collecting from cluster: {cluster_name}")
                
                # Collect IOPS metrics
                iops_metrics = await self._collect_iops(cluster_name)
                metrics.extend(iops_metrics)
                
                # Collect latency metrics
                latency_metrics = await self._collect_latency(cluster_name)
                metrics.extend(latency_metrics)
                
                # Collect throughput metrics
                throughput_metrics = await self._collect_throughput(cluster_name)
                metrics.extend(throughput_metrics)
                
                # Collect capacity metrics
                capacity_metrics = await self._collect_capacity(cluster_name)
                metrics.extend(capacity_metrics)
                
            logger.info(f"Collected {len(metrics)} ONTAP metrics")
            return metrics
            
        except Exception as e:
            logger.error(f"Error collecting ONTAP metrics: {e}")
            return []
    
    async def _collect_iops(self, cluster_name: str) -> List[Dict[str, Any]]:
        """Collect IOPS metrics"""
        # Simulated ONTAP API call - replace with actual API integration
        await asyncio.sleep(0.1)  # Simulate API call
        
        metrics = []
        nodes = ['node-01', 'node-02', 'node-03']
        
        for node in nodes:
            # Read IOPS
            metrics.append(self.format_metric(
                name='dcn_storage_iops_total',
                value=1500.0,
                labels={
                    'cluster': cluster_name,
                    'node': node,
                    'type': 'read'
                }
            ))
            
            # Write IOPS
            metrics.append(self.format_metric(
                name='dcn_storage_iops_total',
                value=800.0,
                labels={
                    'cluster': cluster_name,
                    'node': node,
                    'type': 'write'
                }
            ))
            
        return metrics
    
    async def _collect_latency(self, cluster_name: str) -> List[Dict[str, Any]]:
        """Collect latency metrics"""
        await asyncio.sleep(0.1)
        
        metrics = []
        nodes = ['node-01', 'node-02', 'node-03']
        
        for node in nodes:
            metrics.append(self.format_metric(
                name='dcn_storage_latency_milliseconds',
                value=2.5,
                labels={
                    'cluster': cluster_name,
                    'node': node,
                    'operation': 'read'
                }
            ))
            
            metrics.append(self.format_metric(
                name='dcn_storage_latency_milliseconds',
                value=3.2,
                labels={
                    'cluster': cluster_name,
                    'node': node,
                    'operation': 'write'
                }
            ))
            
        return metrics
    
    async def _collect_throughput(self, cluster_name: str) -> List[Dict[str, Any]]:
        """Collect throughput metrics"""
        await asyncio.sleep(0.1)
        
        metrics = []
        nodes = ['node-01', 'node-02', 'node-03']
        
        for node in nodes:
            metrics.append(self.format_metric(
                name='dcn_storage_throughput_bytes_per_second',
                value=104857600.0,  # 100 MB/s
                labels={
                    'cluster': cluster_name,
                    'node': node
                }
            ))
            
        return metrics
    
    async def _collect_capacity(self, cluster_name: str) -> List[Dict[str, Any]]:
        """Collect capacity metrics"""
        await asyncio.sleep(0.1)
        
        metrics = []
        aggregates = ['aggr1', 'aggr2', 'aggr3']
        
        for aggregate in aggregates:
            # Total capacity
            metrics.append(self.format_metric(
                name='dcn_storage_capacity_bytes',
                value=10995116277760.0,  # 10 TB
                labels={
                    'cluster': cluster_name,
                    'aggregate': aggregate,
                    'type': 'total'
                }
            ))
            
            # Used capacity
            metrics.append(self.format_metric(
                name='dcn_storage_capacity_bytes',
                value=5497558138880.0,  # 5 TB
                labels={
                    'cluster': cluster_name,
                    'aggregate': aggregate,
                    'type': 'used'
                }
            ))
            
        return metrics


class StorageGRIDCollector(MetricCollector):
    """Collects metrics from NetApp StorageGRID systems"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__('storagegrid', config)
        self.api_endpoint = config.get('api_endpoint')
        self.grids = config.get('grids', [])
        
    async def collect(self) -> List[Dict[str, Any]]:
        """Collect StorageGRID metrics"""
        metrics = []
        
        try:
            logger.info(f"Collecting StorageGRID metrics from {len(self.grids)} grids")
            
            for grid in self.grids:
                grid_name = grid.get('name')
                
                # S3 operation metrics
                s3_metrics = await self._collect_s3_metrics(grid_name)
                metrics.extend(s3_metrics)
                
                # Storage capacity
                capacity_metrics = await self._collect_grid_capacity(grid_name)
                metrics.extend(capacity_metrics)
                
            logger.info(f"Collected {len(metrics)} StorageGRID metrics")
            return metrics
            
        except Exception as e:
            logger.error(f"Error collecting StorageGRID metrics: {e}")
            return []
    
    async def _collect_s3_metrics(self, grid_name: str) -> List[Dict[str, Any]]:
        """Collect S3 operation metrics"""
        await asyncio.sleep(0.1)
        
        metrics = []
        operations = ['GET', 'PUT', 'DELETE', 'LIST']
        
        for operation in operations:
            metrics.append(self.format_metric(
                name='dcn_storagegrid_s3_operations_total',
                value=15000.0,
                labels={
                    'grid': grid_name,
                    'operation': operation
                }
            ))
            
        return metrics
    
    async def _collect_grid_capacity(self, grid_name: str) -> List[Dict[str, Any]]:
        """Collect grid capacity metrics"""
        await asyncio.sleep(0.1)
        
        return [
            self.format_metric(
                name='dcn_storagegrid_capacity_bytes',
                value=549755813888000.0,  # 500 TB
                labels={'grid': grid_name, 'type': 'total'}
            ),
            self.format_metric(
                name='dcn_storagegrid_capacity_bytes',
                value=274877906944000.0,  # 250 TB
                labels={'grid': grid_name, 'type': 'used'}
            )
        ]


class GenericCollector(MetricCollector):
    """Generic collector for custom metrics sources"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__('generic', config)
        self.sources = config.get('sources', [])
        
    async def collect(self) -> List[Dict[str, Any]]:
        """Collect metrics from generic sources"""
        metrics = []
        
        try:
            for source in self.sources:
                source_name = source.get('name')
                source_type = source.get('type')
                
                logger.debug(f"Collecting from {source_type} source: {source_name}")
                
                # Add source-specific collection logic here
                source_metrics = await self._collect_from_source(source)
                metrics.extend(source_metrics)
                
            return metrics
            
        except Exception as e:
            logger.error(f"Error collecting generic metrics: {e}")
            return []
    
    async def _collect_from_source(self, source: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Collect from individual source"""
        await asyncio.sleep(0.1)
        
        return [
            self.format_metric(
                name=f"dcn_{source.get('name')}_metric",
                value=100.0,
                labels={'source': source.get('name')}
            )
        ]


class KafkaProducerManager:
    """Manages Kafka producer for sending metrics"""
    
    def __init__(self, bootstrap_servers: str):
        self.bootstrap_servers = bootstrap_servers
        self.producer = Producer({
            'bootstrap.servers': bootstrap_servers,
            'client.id': 'dcn-collector',
            'compression.type': 'gzip',
            'linger.ms': 100,  # Batch messages for 100ms
            'batch.size': 16384  # 16KB batches
        })
        logger.info(f"Kafka producer initialized: {bootstrap_servers}")
        
    def send_metrics(self, topic: str, metrics: List[Dict[str, Any]]):
        """Send metrics to Kafka topic"""
        try:
            for metric in metrics:
                self.producer.produce(
                    topic,
                    key=metric['name'].encode('utf-8'),
                    value=json.dumps(metric).encode('utf-8'),
                    callback=self._delivery_callback
                )
            
            # Wait for outstanding messages
            self.producer.flush(timeout=10)
            logger.debug(f"Sent {len(metrics)} metrics to topic {topic}")
            
        except Exception as e:
            logger.error(f"Error sending metrics to Kafka: {e}")
    
    def _delivery_callback(self, err, msg):
        """Callback for message delivery"""
        if err:
            logger.error(f"Message delivery failed: {err}")
        else:
            logger.debug(f"Message delivered to {msg.topic()} [{msg.partition()}]")


class CollectorService:
    """Main collector service orchestrator"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.collectors = []
        self.kafka_manager = None
        self.running = False
        
        # Initialize collectors
        self._init_collectors()
        
        # Initialize Kafka
        kafka_servers = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')
        self.kafka_manager = KafkaProducerManager(kafka_servers)
        
    def _init_collectors(self):
        """Initialize all configured collectors"""
        collectors_config = self.config.get('collectors', {})
        
        # ONTAP collector
        if collectors_config.get('ontap', {}).get('enabled', False):
            self.collectors.append(ONTAPCollector(collectors_config['ontap']))
            logger.info("ONTAP collector initialized")
        
        # StorageGRID collector
        if collectors_config.get('storagegrid', {}).get('enabled', False):
            self.collectors.append(StorageGRIDCollector(collectors_config['storagegrid']))
            logger.info("StorageGRID collector initialized")
        
        # Generic collectors
        if collectors_config.get('generic', {}).get('enabled', False):
            self.collectors.append(GenericCollector(collectors_config['generic']))
            logger.info("Generic collector initialized")
            
        logger.info(f"Initialized {len(self.collectors)} collectors")
    
    async def collect_and_send(self):
        """Collect metrics from all collectors and send to Kafka"""
        all_metrics = []
        
        # Collect from all collectors concurrently
        tasks = [collector.collect() for collector in self.collectors if collector.enabled]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Aggregate results
        for result in results:
            if isinstance(result, list):
                all_metrics.extend(result)
            elif isinstance(result, Exception):
                logger.error(f"Collector error: {result}")
        
        # Send to Kafka
        if all_metrics:
            kafka_topic = self.config.get('kafka_topic', 'dcn-metrics')
            self.kafka_manager.send_metrics(kafka_topic, all_metrics)
            logger.info(f"Collected and sent {len(all_metrics)} metrics")
        else:
            logger.warning("No metrics collected")
        
        return len(all_metrics)
    
    async def run(self):
        """Run the collector service"""
        self.running = True
        poll_interval = self.config.get('poll_interval', 60)
        
        logger.info(f"Starting collector service (poll interval: {poll_interval}s)")
        
        while self.running:
            try:
                start_time = time.time()
                
                # Collect and send metrics
                metric_count = await self.collect_and_send()
                
                elapsed = time.time() - start_time
                logger.info(f"Collection cycle completed in {elapsed:.2f}s, "
                          f"collected {metric_count} metrics")
                
                # Sleep until next poll interval
                await asyncio.sleep(max(0, poll_interval - elapsed))
                
            except Exception as e:
                logger.error(f"Error in collection cycle: {e}")
                await asyncio.sleep(10)  # Wait before retry
    
    def stop(self):
        """Stop the collector service"""
        logger.info("Stopping collector service")
        self.running = False


async def main():
    """Main entry point"""
    # Load configuration
    config = {
        'poll_interval': int(os.getenv('COLLECTOR_POLL_INTERVAL', '60')),
        'kafka_topic': os.getenv('KAFKA_TOPIC', 'dcn-metrics'),
        'collectors': {
            'ontap': {
                'enabled': True,
                'api_endpoint': os.getenv('ONTAP_API_ENDPOINT', 'https://ontap-cluster'),
                'username': os.getenv('ONTAP_USERNAME', 'admin'),
                'password': os.getenv('ONTAP_PASSWORD', ''),
                'clusters': [
                    {'name': 'prod-cluster-01'},
                    {'name': 'prod-cluster-02'}
                ],
                'poll_interval': 60
            },
            'storagegrid': {
                'enabled': True,
                'api_endpoint': os.getenv('STORAGEGRID_API_ENDPOINT', 'https://storagegrid'),
                'grids': [
                    {'name': 'grid-01'}
                ],
                'poll_interval': 60
            },
            'generic': {
                'enabled': False,
                'sources': []
            }
        }
    }
    
    # Create and run service
    service = CollectorService(config)
    
    try:
        await service.run()
    except KeyboardInterrupt:
        logger.info("Received interrupt signal")
        service.stop()


if __name__ == '__main__':
    asyncio.run(main())
