import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar, PieChart, Pie, Cell } from 'recharts';
import { Activity, Users, MessageSquare, TrendingUp, AlertTriangle, CheckCircle } from 'lucide-react';

interface AnalyticsData {
  timestamp: string;
  activeUsers: number;
  messagesPerSecond: number;
  responseTime: number;
  aiAccuracy: number;
  errorRate: number;
  throughput: number;
}

interface AlertData {
  id: string;
  type: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  message: string;
  timestamp: string;
  resolved: boolean;
}

interface ServiceMetrics {
  service: string;
  cpu: number;
  memory: number;
  requests: number;
  errors: number;
  responseTime: number;
}

const RealTimeAnalytics: React.FC = () => {
  const [analyticsData, setAnalyticsData] = useState<AnalyticsData[]>([]);
  const [alerts, setAlerts] = useState<AlertData[]>([]);
  const [serviceMetrics, setServiceMetrics] = useState<ServiceMetrics[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const [timeRange, setTimeRange] = useState('1h');
  
  // Mock data for demonstration
  const mockAnalyticsData: AnalyticsData[] = [
    { timestamp: '10:00:00', activeUsers: 45, messagesPerSecond: 12, responseTime: 150, aiAccuracy: 0.92, errorRate: 0.02, throughput: 75 },
    { timestamp: '10:01:00', activeUsers: 52, messagesPerSecond: 15, responseTime: 145, aiAccuracy: 0.93, errorRate: 0.015, throughput: 82 },
    { timestamp: '10:02:00', activeUsers: 48, messagesPerSecond: 13, responseTime: 155, aiAccuracy: 0.91, errorRate: 0.025, throughput: 78 },
    { timestamp: '10:03:00', activeUsers: 55, messagesPerSecond: 18, responseTime: 140, aiAccuracy: 0.94, errorRate: 0.01, throughput: 95 },
    { timestamp: '10:04:00', activeUsers: 60, messagesPerSecond: 20, responseTime: 135, aiAccuracy: 0.95, errorRate: 0.008, throughput: 102 },
    { timestamp: '10:05:00', activeUsers: 58, messagesPerSecond: 17, responseTime: 142, aiAccuracy: 0.93, errorRate: 0.012, throughput: 88 },
  ];
  
  const mockAlerts: AlertData[] = [
    { id: '1', type: 'High Response Time', severity: 'medium', message: 'AI response time exceeded threshold', timestamp: '10:02:30', resolved: false },
    { id: '2', type: 'Low Accuracy', severity: 'high', message: 'AI model accuracy dropped below 90%', timestamp: '10:03:15', resolved: false },
    { id: '3', type: 'Error Spike', severity: 'low', message: 'Increased error rate detected', timestamp: '10:04:45', resolved: true },
  ];
  
  const mockServiceMetrics: ServiceMetrics[] = [
    { service: 'Auth Service', cpu: 25, memory: 40, requests: 1250, errors: 5, responseTime: 120 },
    { service: 'Chat Service', cpu: 45, memory: 60, requests: 3200, errors: 12, responseTime: 95 },
    { service: 'Admin Service', cpu: 15, memory: 30, requests: 850, errors: 2, responseTime: 110 },
    { service: 'Personalization', cpu: 35, memory: 55, requests: 2100, errors: 8, responseTime: 140 },
    { service: 'AI Service', cpu: 65, memory: 75, requests: 4500, errors: 18, responseTime: 150 },
    { service: 'Data Service', cpu: 20, memory: 35, requests: 950, errors: 3, responseTime: 130 },
  ];
  
  useEffect(() => {
    // Simulate real-time data updates
    const interval = setInterval(() => {
      setAnalyticsData(mockAnalyticsData);
      setAlerts(mockAlerts);
      setServiceMetrics(mockServiceMetrics);
      setIsConnected(true);
    }, 5000);
    
    // Initial data load
    setAnalyticsData(mockAnalyticsData);
    setAlerts(mockAlerts);
    setServiceMetrics(mockServiceMetrics);
    setIsConnected(true);
    
    return () => clearInterval(interval);
  }, [timeRange]);
  
  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return 'bg-red-500';
      case 'high': return 'bg-orange-500';
      case 'medium': return 'bg-yellow-500';
      case 'low': return 'bg-blue-500';
      default: return 'bg-gray-500';
    }
  };
  
  const getHealthStatus = (value: number, threshold: number) => {
    if (value < threshold * 0.7) return 'good';
    if (value < threshold) return 'warning';
    return 'critical';
  };
  
  const currentMetrics = analyticsData[analyticsData.length - 1] || mockAnalyticsData[0];
  
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold">Real-Time Analytics</h2>
          <p className="text-gray-600">Monitor system performance and user activity in real-time</p>
        </div>
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2">
            <div className={`w-3 h-3 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`}></div>
            <span className="text-sm">{isConnected ? 'Connected' : 'Disconnected'}</span>
          </div>
          <select 
            value={timeRange} 
            onChange={(e) => setTimeRange(e.target.value)}
            className="px-3 py-2 border rounded-md"
          >
            <option value="5m">Last 5 minutes</option>
            <option value="15m">Last 15 minutes</option>
            <option value="1h">Last hour</option>
            <option value="24h">Last 24 hours</option>
          </select>
        </div>
      </div>
      
      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Active Users</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{currentMetrics.activeUsers}</div>
            <p className="text-xs text-muted-foreground">
              +12% from last hour
            </p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Messages/Second</CardTitle>
            <MessageSquare className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{currentMetrics.messagesPerSecond}</div>
            <p className="text-xs text-muted-foreground">
              +8% from last hour
            </p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Response Time</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{currentMetrics.responseTime}ms</div>
            <p className="text-xs text-muted-foreground">
              -5% from last hour
            </p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">AI Accuracy</CardTitle>
            <CheckCircle className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{(currentMetrics.aiAccuracy * 100).toFixed(1)}%</div>
            <p className="text-xs text-muted-foreground">
              +2% from last hour
            </p>
          </CardContent>
        </Card>
      </div>
      
      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Performance Chart */}
        <Card>
          <CardHeader>
            <CardTitle>Performance Metrics</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={analyticsData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="timestamp" />
                <YAxis />
                <Tooltip />
                <Line type="monotone" dataKey="responseTime" stroke="#8884d8" name="Response Time (ms)" />
                <Line type="monotone" dataKey="aiAccuracy" stroke="#82ca9d" name="AI Accuracy" />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
        
        {/* Throughput Chart */}
        <Card>
          <CardHeader>
            <CardTitle>System Throughput</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={analyticsData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="timestamp" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="messagesPerSecond" fill="#8884d8" name="Messages/Second" />
                <Bar dataKey="throughput" fill="#82ca9d" name="Throughput" />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>
      
      {/* Service Metrics */}
      <Card>
        <CardHeader>
          <CardTitle>Service Health</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {serviceMetrics.map((service) => (
              <div key={service.service} className="flex items-center justify-between p-4 border rounded-lg">
                <div className="flex items-center space-x-4">
                  <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                    <Activity className="h-6 w-6 text-blue-600" />
                  </div>
                  <div>
                    <h3 className="font-semibold">{service.service}</h3>
                    <p className="text-sm text-gray-600">
                      {service.requests.toLocaleString()} requests/min
                    </p>
                  </div>
                </div>
                
                <div className="flex items-center space-x-6">
                  <div className="text-center">
                    <p className="text-sm text-gray-600">CPU</p>
                    <div className="w-20">
                      <Progress value={service.cpu} className="h-2" />
                      <p className="text-xs mt-1">{service.cpu}%</p>
                    </div>
                  </div>
                  
                  <div className="text-center">
                    <p className="text-sm text-gray-600">Memory</p>
                    <div className="w-20">
                      <Progress value={service.memory} className="h-2" />
                      <p className="text-xs mt-1">{service.memory}%</p>
                    </div>
                  </div>
                  
                  <div className="text-center">
                    <p className="text-sm text-gray-600">Response</p>
                    <p className="text-sm font-semibold">{service.responseTime}ms</p>
                  </div>
                  
                  <div className="text-center">
                    <p className="text-sm text-gray-600">Errors</p>
                    <Badge variant={service.errors > 10 ? 'destructive' : 'secondary'}>
                      {service.errors}
                    </Badge>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
      
      {/* Alerts */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <AlertTriangle className="h-5 w-5" />
            <span>System Alerts</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {alerts.map((alert) => (
              <div key={alert.id} className="flex items-center justify-between p-3 border rounded-lg">
                <div className="flex items-center space-x-3">
                  <div className={`w-3 h-3 rounded-full ${getSeverityColor(alert.severity)}`}></div>
                  <div>
                    <h4 className="font-medium">{alert.type}</h4>
                    <p className="text-sm text-gray-600">{alert.message}</p>
                  </div>
                </div>
                
                <div className="flex items-center space-x-3">
                  <span className="text-sm text-gray-500">{alert.timestamp}</span>
                  <Badge variant={alert.resolved ? 'default' : 'destructive'}>
                    {alert.resolved ? 'Resolved' : 'Open'}
                  </Badge>
                  {!alert.resolved && (
                    <Button size="sm" variant="outline">
                      Resolve
                    </Button>
                  )}
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default RealTimeAnalytics;