"""
DCN API Service - REST API for Data Collection Node
Provides REST endpoints for querying collected metrics and counters
"""

from fastapi import FastAPI, HTTPException, Query, Depends
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import asyncpg
import redis.asyncio as aioredis
import json
import os
import logging
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from starlette.responses import Response

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Prometheus metrics
REQUEST_COUNT = Counter('dcn_api_requests_total', 'Total API requests', ['method', 'endpoint', 'status'])
REQUEST_LATENCY = Histogram('dcn_api_request_duration_seconds', 'API request latency', ['endpoint'])

# Create FastAPI app
app = FastAPI(
    title="DCN API Service",
    description="Data Collection Node REST API for metrics and counters",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Pydantic models
class MetricQuery(BaseModel):
    """Model for metric query requests"""
    metric_name: str = Field(..., description="Name of the metric")
    start_time: datetime = Field(..., description="Start time for query")
    end_time: datetime = Field(..., description="End time for query")
    labels: Optional[Dict[str, str]] = Field(None, description="Label filters")
    aggregation: Optional[str] = Field("avg", description="Aggregation function (avg, sum, min, max)")
    interval: Optional[str] = Field("5m", description="Aggregation interval")


class MetricResponse(BaseModel):
    """Model for metric query response"""
    metric_name: str
    data_points: List[Dict[str, Any]]
    labels: Dict[str, str]
    aggregation: str
    interval: str


class CounterInfo(BaseModel):
    """Model for counter information"""
    name: str
    description: str
    labels: List[str]
    type: str  # gauge, counter, histogram
    unit: Optional[str] = None


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    timestamp: datetime
    version: str
    services: Dict[str, str]


class DataSourceInfo(BaseModel):
    """Data source information"""
    name: str
    type: str
    status: str
    last_collection: Optional[datetime]
    metrics_count: int


# Database connection pool
db_pool = None
redis_client = None


async def get_db_pool():
    """Get database connection pool"""
    global db_pool
    if db_pool is None:
        db_url = os.getenv('DATABASE_URL', 'postgresql://dcn:dcnpass@timescaledb:5432/dcn')
        db_pool = await asyncpg.create_pool(db_url, min_size=5, max_size=20)
    return db_pool


async def get_redis_client():
    """Get Redis client"""
    global redis_client
    if redis_client is None:
        redis_url = os.getenv('REDIS_URL', 'redis://redis:6379')
        redis_client = await aioredis.from_url(redis_url, decode_responses=True)
    return redis_client


@app.on_event("startup")
async def startup_event():
    """Initialize connections on startup"""
    logger.info("Starting DCN API Service")
    await get_db_pool()
    await get_redis_client()
    logger.info("Database and Redis connections established")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down DCN API Service")
    if db_pool:
        await db_pool.close()
    if redis_client:
        await redis_client.close()


@app.get("/", tags=["General"])
async def root():
    """Root endpoint"""
    return {
        "service": "DCN API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Health check endpoint for Kubernetes liveness probe"""
    try:
        # Check database connection
        pool = await get_db_pool()
        async with pool.acquire() as conn:
            await conn.fetchval('SELECT 1')
        db_status = "healthy"
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        db_status = "unhealthy"
    
    try:
        # Check Redis connection
        redis = await get_redis_client()
        await redis.ping()
        redis_status = "healthy"
    except Exception as e:
        logger.error(f"Redis health check failed: {e}")
        redis_status = "unhealthy"
    
    overall_status = "healthy" if db_status == "healthy" and redis_status == "healthy" else "degraded"
    
    return HealthResponse(
        status=overall_status,
        timestamp=datetime.utcnow(),
        version="1.0.0",
        services={
            "database": db_status,
            "redis": redis_status
        }
    )


@app.get("/ready", tags=["Health"])
async def readiness_check():
    """Readiness check endpoint for Kubernetes readiness probe"""
    try:
        pool = await get_db_pool()
        async with pool.acquire() as conn:
            await conn.fetchval('SELECT 1')
        return {"status": "ready"}
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        raise HTTPException(status_code=503, detail="Service not ready")


@app.get("/metrics", tags=["Metrics"])
async def metrics():
    """Prometheus metrics endpoint"""
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.get("/api/v1/counters", response_model=List[CounterInfo], tags=["Counters"])
async def list_counters():
    """List all available counter types"""
    try:
        # Check cache first
        redis = await get_redis_client()
        cached = await redis.get("counters:list")
        
        if cached:
            return json.loads(cached)
        
        # Query from database
        pool = await get_db_pool()
        async with pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT DISTINCT 
                    name,
                    description,
                    labels,
                    type,
                    unit
                FROM metric_metadata
                ORDER BY name
            """)
        
        counters = [
            CounterInfo(
                name=row['name'],
                description=row['description'] or '',
                labels=row['labels'] or [],
                type=row['type'] or 'gauge',
                unit=row['unit']
            )
            for row in rows
        ]
        
        # Cache for 5 minutes
        await redis.setex("counters:list", 300, json.dumps([c.dict() for c in counters]))
        
        REQUEST_COUNT.labels(method='GET', endpoint='/api/v1/counters', status='200').inc()
        return counters
        
    except Exception as e:
        logger.error(f"Error listing counters: {e}")
        REQUEST_COUNT.labels(method='GET', endpoint='/api/v1/counters', status='500').inc()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/counters/{counter_name}", tags=["Counters"])
async def get_counter_data(
    counter_name: str,
    start_time: Optional[datetime] = Query(None, description="Start time (ISO format)"),
    end_time: Optional[datetime] = Query(None, description="End time (ISO format)"),
    labels: Optional[str] = Query(None, description="Label filters (JSON)"),
    limit: int = Query(1000, le=10000, description="Max results")
):
    """Get data for a specific counter"""
    try:
        # Default time range: last hour
        if not end_time:
            end_time = datetime.utcnow()
        if not start_time:
            start_time = end_time - timedelta(hours=1)
        
        # Parse labels
        label_filters = json.loads(labels) if labels else {}
        
        # Build query
        pool = await get_db_pool()
        async with pool.acquire() as conn:
            query = """
                SELECT 
                    timestamp,
                    value,
                    labels
                FROM metrics
                WHERE name = $1
                  AND timestamp >= $2
                  AND timestamp <= $3
            """
            params = [counter_name, start_time, end_time]
            
            # Add label filters
            if label_filters:
                for key, value in label_filters.items():
                    query += f" AND labels->>'{ key}' = ${len(params) + 1}"
                    params.append(value)
            
            query += f" ORDER BY timestamp DESC LIMIT ${len(params) + 1}"
            params.append(limit)
            
            rows = await conn.fetch(query, *params)
        
        data_points = [
            {
                "timestamp": row['timestamp'].isoformat(),
                "value": float(row['value']),
                "labels": row['labels']
            }
            for row in rows
        ]
        
        REQUEST_COUNT.labels(method='GET', endpoint=f'/api/v1/counters/{counter_name}', status='200').inc()
        
        return {
            "counter_name": counter_name,
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "data_points": data_points,
            "count": len(data_points)
        }
        
    except Exception as e:
        logger.error(f"Error getting counter data: {e}")
        REQUEST_COUNT.labels(method='GET', endpoint=f'/api/v1/counters/{counter_name}', status='500').inc()
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/query", response_model=MetricResponse, tags=["Query"])
async def query_metrics(query: MetricQuery):
    """Query metrics with aggregation"""
    try:
        with REQUEST_LATENCY.labels(endpoint='/api/v1/query').time():
            pool = await get_db_pool()
            async with pool.acquire() as conn:
                # Build aggregation query
                agg_func = query.aggregation.upper()
                if agg_func not in ['AVG', 'SUM', 'MIN', 'MAX', 'COUNT']:
                    raise ValueError(f"Invalid aggregation function: {agg_func}")
                
                sql_query = f"""
                    SELECT 
                        time_bucket('{query.interval}', timestamp) AS bucket,
                        {agg_func}(value) AS aggregated_value,
                        labels
                    FROM metrics
                    WHERE name = $1
                      AND timestamp >= $2
                      AND timestamp <= $3
                """
                params = [query.metric_name, query.start_time, query.end_time]
                
                # Add label filters
                if query.labels:
                    for key, value in query.labels.items():
                        sql_query += f" AND labels->>'{ key}' = ${len(params) + 1}"
                        params.append(value)
                
                sql_query += " GROUP BY bucket, labels ORDER BY bucket DESC"
                
                rows = await conn.fetch(sql_query, *params)
            
            data_points = [
                {
                    "timestamp": row['bucket'].isoformat(),
                    "value": float(row['aggregated_value']),
                    "labels": row['labels']
                }
                for row in rows
            ]
            
            REQUEST_COUNT.labels(method='POST', endpoint='/api/v1/query', status='200').inc()
            
            return MetricResponse(
                metric_name=query.metric_name,
                data_points=data_points,
                labels=query.labels or {},
                aggregation=query.aggregation,
                interval=query.interval
            )
            
    except Exception as e:
        logger.error(f"Error querying metrics: {e}")
        REQUEST_COUNT.labels(method='POST', endpoint='/api/v1/query', status='500').inc()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/sources", response_model=List[DataSourceInfo], tags=["Data Sources"])
async def list_data_sources():
    """List all configured data sources"""
    try:
        pool = await get_db_pool()
        async with pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT 
                    name,
                    type,
                    status,
                    last_collection,
                    metrics_count
                FROM data_sources
                ORDER BY name
            """)
        
        sources = [
            DataSourceInfo(
                name=row['name'],
                type=row['type'],
                status=row['status'],
                last_collection=row['last_collection'],
                metrics_count=row['metrics_count'] or 0
            )
            for row in rows
        ]
        
        REQUEST_COUNT.labels(method='GET', endpoint='/api/v1/sources', status='200').inc()
        return sources
        
    except Exception as e:
        logger.error(f"Error listing data sources: {e}")
        REQUEST_COUNT.labels(method='GET', endpoint='/api/v1/sources', status='500').inc()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/export/{format}", tags=["Export"])
async def export_data(
    format: str,
    counter_name: str = Query(..., description="Counter name to export"),
    start_time: datetime = Query(..., description="Start time"),
    end_time: datetime = Query(..., description="End time")
):
    """Export data in specified format (json, csv, prometheus)"""
    try:
        if format not in ['json', 'csv', 'prometheus']:
            raise HTTPException(status_code=400, detail=f"Unsupported format: {format}")
        
        # Get data
        pool = await get_db_pool()
        async with pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT timestamp, value, labels
                FROM metrics
                WHERE name = $1
                  AND timestamp >= $2
                  AND timestamp <= $3
                ORDER BY timestamp
            """, counter_name, start_time, end_time)
        
        if format == 'json':
            data = [
                {
                    "timestamp": row['timestamp'].isoformat(),
                    "value": float(row['value']),
                    "labels": row['labels']
                }
                for row in rows
            ]
            return JSONResponse(content=data)
        
        elif format == 'csv':
            # Convert to CSV format
            csv_lines = ["timestamp,value,labels\n"]
            for row in rows:
                labels_str = json.dumps(row['labels'])
                csv_lines.append(f"{row['timestamp'].isoformat()},{row['value']},\"{labels_str}\"\n")
            
            return Response(content=''.join(csv_lines), media_type='text/csv')
        
        elif format == 'prometheus':
            # Convert to Prometheus format
            prom_lines = []
            for row in rows:
                labels_str = ','.join([f'{k}="{v}"' for k, v in row['labels'].items()])
                prom_lines.append(f"{counter_name}{{{labels_str}}} {row['value']} {int(row['timestamp'].timestamp() * 1000)}\n")
            
            return Response(content=''.join(prom_lines), media_type='text/plain')
        
        REQUEST_COUNT.labels(method='GET', endpoint=f'/api/v1/export/{format}', status='200').inc()
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exporting data: {e}")
        REQUEST_COUNT.labels(method='GET', endpoint=f'/api/v1/export/{format}', status='500').inc()
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == '__main__':
    import uvicorn
    port = int(os.getenv('API_PORT', '8080'))
    uvicorn.run(app, host='0.0.0.0', port=port)
