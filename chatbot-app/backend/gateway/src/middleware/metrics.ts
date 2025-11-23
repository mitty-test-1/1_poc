import { Request, Response, NextFunction } from 'express';

// Mock metrics implementation since prom-client is not available
interface MetricData {
  labels: Record<string, string>;
  value: number;
}

interface HistogramData {
  observe: (labels: Record<string, string>, value: number) => void;
}

interface CounterData {
  inc: (labels: Record<string, string>) => void;
}

interface GaugeData {
  inc: (labels: Record<string, string>) => void;
  set: (labels: Record<string, string>, value: number) => void;
  get: () => MetricData[];
}

class MockRegistry {
  private metricsData: Map<string, any> = new Map();
  private contentType = 'text/plain; version=0.0.4; charset=utf-8';

  registerMetric(metric: any) {
    this.metricsData.set(metric.name, metric);
  }

  async getMetrics(): Promise<string> {
    // Return mock metrics data
    return `# HELP http_request_duration_ms Duration of HTTP requests in ms
# TYPE http_request_duration_ms histogram
http_request_duration_ms_bucket{le="50"} 0
http_request_duration_ms_bucket{le="100"} 0
http_request_duration_ms_bucket{le="200"} 0
http_request_duration_ms_bucket{le="300"} 0
http_request_duration_ms_bucket{le="400"} 0
http_request_duration_ms_bucket{le="500"} 0
http_request_duration_ms_bucket{le="1000"} 0
http_request_duration_ms_bucket{le="2000"} 0
http_request_duration_ms_bucket{le="+Inf"} 0
http_request_duration_ms_sum 0
http_request_duration_ms_count 0

# HELP http_requests_total Total number of HTTP requests
# TYPE http_requests_total counter
http_requests_total 0

# HELP active_users Number of active users
# TYPE active_users gauge
active_users 0

# HELP chat_messages_total Total number of chat messages
# TYPE chat_messages_total counter
chat_messages_total 0

# HELP ai_processing_duration_ms Duration of AI processing in ms
# TYPE ai_processing_duration_ms histogram
ai_processing_duration_ms_bucket{le="50"} 0
ai_processing_duration_ms_bucket{le="100"} 0
ai_processing_duration_ms_bucket{le="200"} 0
ai_processing_duration_ms_bucket{le="300"} 0
ai_processing_duration_ms_bucket{le="400"} 0
ai_processing_duration_ms_bucket{le="500"} 0
ai_processing_duration_ms_bucket{le="1000"} 0
ai_processing_duration_ms_bucket{le="2000"} 0
ai_processing_duration_ms_bucket{le="+Inf"} 0
ai_processing_duration_ms_sum 0
ai_processing_duration_ms_count 0

# HELP ai_accuracy AI model accuracy
# TYPE ai_accuracy gauge
ai_accuracy 0

# HELP errors_total Total number of errors
# TYPE errors_total counter
errors_total 0`;
  }

  resetMetrics() {
    this.metricsData.clear();
  }
}

const register = new MockRegistry();

// Mock metric implementations
const httpRequestDurationMicroseconds: HistogramData = {
  observe: (labels, value) => {
    console.log(`HTTP Duration: ${value}ms for ${JSON.stringify(labels)}`);
  }
};

const httpRequestTotal: CounterData = {
  inc: (labels) => {
    console.log(`HTTP Request: ${JSON.stringify(labels)}`);
  }
};

const activeUsers: GaugeData = {
  inc: (labels) => {
    console.log(`Active User: ${JSON.stringify(labels)}`);
  },
  set: (labels, value) => {
    console.log(`Active User Set: ${value} for ${JSON.stringify(labels)}`);
  },
  get: () => []
};

const chatMessages: CounterData = {
  inc: (labels) => {
    console.log(`Chat Message: ${JSON.stringify(labels)}`);
  }
};

const aiProcessingDuration: HistogramData = {
  observe: (labels, value) => {
    console.log(`AI Processing: ${value}ms for ${JSON.stringify(labels)}`);
  }
};

const aiAccuracy: GaugeData = {
  inc: (labels) => {
    console.log(`AI Accuracy Increment: ${JSON.stringify(labels)}`);
  },
  set: (labels, value) => {
    console.log(`AI Accuracy Set: ${value} for ${JSON.stringify(labels)}`);
  },
  get: () => []
};

const errorRate: CounterData = {
  inc: (labels) => {
    console.log(`Error: ${JSON.stringify(labels)}`);
  }
};

// Middleware to track HTTP metrics
export const metricsMiddleware = (req: Request, res: Response, next: NextFunction) => {
  const start = Date.now();
  const service = req.headers['x-service-name'] || 'unknown';
  
  // Track active users
  activeUsers.inc({ service: req.path.split('/')[2] || 'gateway' });
  
  res.on('finish', () => {
    const duration = Date.now() - start;
    const route = req.route?.path || req.path;
    
    // Record HTTP request metrics
    httpRequestDurationMicroseconds.observe(
      {
        method: req.method,
        route: route,
        status_code: res.statusCode.toString(),
        service: service as string
      },
      duration
    );
    
    httpRequestTotal.inc({
      method: req.method,
      route: route,
      status_code: res.statusCode.toString(),
      service: service as string
    });
    
    // Track errors
    if (res.statusCode >= 400) {
      errorRate.inc({
        service: service as string,
        error_type: res.statusCode >= 500 ? 'server_error' : 'client_error',
        route: route
      });
    }
  });
  
  next();
};

// Middleware to track chat messages
export const chatMetricsMiddleware = (messageType: string) => {
  return (req: Request, res: Response, next: NextFunction) => {
    chatMessages.inc({
      service: 'chat',
      message_type: messageType
    });
    next();
  };
};

// Middleware to track AI processing
export const aiMetricsMiddleware = (component: string, operation: string) => {
  return (req: Request, res: Response, next: NextFunction) => {
    const start = Date.now();
    
    res.on('finish', () => {
      const duration = Date.now() - start;
      aiProcessingDuration.observe(
        {
          service: 'ai',
          component,
          operation
        },
        duration
      );
    });
    
    next();
  };
};

// Middleware to update AI accuracy
export const updateAiAccuracy = (component: string, model: string, accuracy: number) => {
  aiAccuracy.set(
    {
      service: 'ai',
      component,
      model
    },
    accuracy
  );
};

// Metrics endpoint
export const metricsEndpoint = async (req: Request, res: Response) => {
  try {
    res.set('Content-Type', register['contentType']);
    res.end(await register.getMetrics());
  } catch (err) {
    res.status(500).end(err);
  }
};

// Get metrics for specific service
export const getServiceMetrics = async (serviceName: string) => {
  const metrics = await register.getMetrics();
  
  // Parse metrics and filter for specific service
  const lines = metrics.split('\n');
  const serviceMetrics = lines.filter((line: string) => 
    line.startsWith('# HELP') || 
    line.startsWith('# TYPE') || 
    line.includes(`{service="${serviceName}"`)
  );
  
  return serviceMetrics.join('\n');
};

// Get all metrics summary
export const getMetricsSummary = async () => {
  const metrics = await register.getMetrics();
  return metrics;
};

// Reset metrics (for testing)
export const resetMetrics = () => {
  register.resetMetrics();
};

// Get active users count
export const getActiveUsersCount = (service?: string) => {
  const metrics = activeUsers.get();
  if (service) {
    return metrics.find((m: MetricData) => m.labels.service === service)?.value || 0;
  }
  return metrics.reduce((sum: number, metric: MetricData) => sum + metric.value, 0);
};

// Get error rate
export const getErrorRate = (service: string, timeRange: string = '5m') => {
  // This would need to be implemented with proper time series data
  // For now, return a mock value
  return 0.0;
};

export {
  httpRequestDurationMicroseconds,
  httpRequestTotal,
  activeUsers,
  chatMessages,
  aiProcessingDuration,
  aiAccuracy,
  errorRate
};