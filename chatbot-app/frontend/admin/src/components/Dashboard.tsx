import React, { useState, useEffect } from 'react';
import {
  Card,
  Row,
  Col,
  Statistic,
  Typography,
  Button,
  Space,
  Table,
  Tag,
  Progress,
  Alert,
  Spin,
  Tabs
} from '@shared-ui';
import {
  UserOutlined,
  MessageOutlined,
  ClockCircleOutlined,
  CheckCircleOutlined,
  ExclamationCircleOutlined,
  ArrowUpOutlined,
  ArrowDownOutlined,
  LineChartOutlined,
  BarChartOutlined,
  AlertTriangleOutlined
} from '@ant-design/icons';
import RealTimeAnalytics from './RealTimeAnalytics';

interface DashboardStats {
  totalUsers: number;
  activeConversations: number;
  resolvedToday: number;
  avgResponseTime: number;
  satisfactionRate: number;
}

interface RecentConversation {
  id: string;
  user: string;
  subject: string;
  status: 'open' | 'pending' | 'resolved';
  duration: string;
  lastUpdate: string;
}

const Dashboard: React.FC = () => {
  const [stats, setStats] = useState<DashboardStats>({
    totalUsers: 0,
    activeConversations: 0,
    resolvedToday: 0,
    avgResponseTime: 0,
    satisfactionRate: 0
  });
  const [recentConversations, setRecentConversations] = useState<RecentConversation[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Simulate API call to fetch dashboard data
    const fetchDashboardData = async () => {
      setLoading(true);
      
      // Simulate API delay
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      // Mock data
      const mockStats: DashboardStats = {
        totalUsers: 1247,
        activeConversations: 23,
        resolvedToday: 156,
        avgResponseTime: 2.3,
        satisfactionRate: 94.5
      };

      const mockConversations: RecentConversation[] = [
        {
          id: '1',
          user: 'John Doe',
          subject: 'Account setup assistance',
          status: 'open',
          duration: '5m',
          lastUpdate: '2 minutes ago'
        },
        {
          id: '2',
          user: 'Jane Smith',
          subject: 'Billing inquiry',
          status: 'pending',
          duration: '12m',
          lastUpdate: '5 minutes ago'
        },
        {
          id: '3',
          user: 'Bob Johnson',
          subject: 'Technical support',
          status: 'resolved',
          duration: '8m',
          lastUpdate: '15 minutes ago'
        },
        {
          id: '4',
          user: 'Alice Brown',
          subject: 'Feature request',
          status: 'open',
          duration: '3m',
          lastUpdate: '1 minute ago'
        },
        {
          id: '5',
          user: 'Charlie Wilson',
          subject: 'Password reset',
          status: 'pending',
          duration: '7m',
          lastUpdate: '10 minutes ago'
        }
      ];

      setStats(mockStats);
      setRecentConversations(mockConversations);
      setLoading(false);
    };

    fetchDashboardData();
  }, []);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'open': return 'red';
      case 'pending': return 'orange';
      case 'resolved': return 'green';
      default: return 'default';
    }
  };

  const columns = [
    {
      title: 'User',
      dataIndex: 'user',
      key: 'user',
      render: (text: string) => (
        <div className="flex items-center space-x-2">
          <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
            <UserOutlined className="text-blue-600" />
          </div>
          <span className="font-medium">{text}</span>
        </div>
      ),
    },
    {
      title: 'Subject',
      dataIndex: 'subject',
      key: 'subject',
    },
    {
      title: 'Status',
      dataIndex: 'status',
      key: 'status',
      render: (status: string) => (
        <Tag color={getStatusColor(status)}>
          {status.charAt(0).toUpperCase() + status.slice(1)}
        </Tag>
      ),
    },
    {
      title: 'Duration',
      dataIndex: 'duration',
      key: 'duration',
    },
    {
      title: 'Last Update',
      dataIndex: 'lastUpdate',
      key: 'lastUpdate',
    },
    {
      title: 'Action',
      key: 'action',
      render: (record: RecentConversation) => (
        <Space size="middle">
          <Button type="link" size="small">
            View
          </Button>
          <Button type="link" size="small" danger>
            Assign
          </Button>
        </Space>
      ),
    },
  ];

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Spin size="large" />
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <Typography.Title level={2}>Dashboard</Typography.Title>
        <Space>
          <Button type="primary">Export Report</Button>
          <Button>Refresh</Button>
        </Space>
      </div>

      {/* Alert Banner */}
      <Alert
        message="System Performance"
        description="All systems are running normally. Average response time is 2.3 seconds."
        type="success"
        showIcon
        closable
      />

      {/* Main Content Tabs */}
      <Tabs defaultActiveKey="overview" items={[
        {
          key: 'overview',
          label: (
            <span>
              <LineChartOutlined />
              Overview
            </span>
          ),
          children: (
            <>
              {/* Stats Cards */}
              <Row gutter={[16, 16]}>
                <Col xs={24} sm={12} lg={6}>
                  <Card>
                    <Statistic
                      title="Total Users"
                      value={stats.totalUsers}
                      prefix={<UserOutlined />}
                      valueStyle={{ color: '#3f8600' }}
                      suffix={
                        <span className="text-green-600 text-sm">
                          <ArrowUpOutlined /> 12%
                        </span>
                      }
                    />
                  </Card>
                </Col>
                <Col xs={24} sm={12} lg={6}>
                  <Card>
                    <Statistic
                      title="Active Conversations"
                      value={stats.activeConversations}
                      prefix={<MessageOutlined />}
                      valueStyle={{ color: '#cf1322' }}
                      suffix={
                        <span className="text-red-600 text-sm">
                          <ArrowUpOutlined /> 5%
                        </span>
                      }
                    />
                  </Card>
                </Col>
                <Col xs={24} sm={12} lg={6}>
                  <Card>
                    <Statistic
                      title="Resolved Today"
                      value={stats.resolvedToday}
                      prefix={<CheckCircleOutlined />}
                      valueStyle={{ color: '#3f8600' }}
                      suffix={
                        <span className="text-green-600 text-sm">
                          <ArrowUpOutlined /> 8%
                        </span>
                      }
                    />
                  </Card>
                </Col>
                <Col xs={24} sm={12} lg={6}>
                  <Card>
                    <Statistic
                      title="Avg Response Time"
                      value={stats.avgResponseTime}
                      suffix="min"
                      prefix={<ClockCircleOutlined />}
                      valueStyle={{ color: '#1890ff' }}
                      precision={1}
                    />
                  </Card>
                </Col>
              </Row>

              {/* Charts Row */}
              <Row gutter={[16, 16]}>
                <Col xs={24} lg={12}>
                  <Card title="Satisfaction Rate" extra={<Button type="link">View Details</Button>}>
                    <div className="text-center">
                      <Progress type="circle" percent={stats.satisfactionRate} size={120} />
                      <div className="mt-4">
                        <Typography.Text strong>{stats.satisfactionRate}%</Typography.Text>
                        <Typography.Text type="secondary"> Customer Satisfaction</Typography.Text>
                      </div>
                    </div>
                  </Card>
                </Col>
                <Col xs={24} lg={12}>
                  <Card title="Recent Conversations" extra={<Button type="link">View All</Button>}>
                    <Table
                      dataSource={recentConversations}
                      columns={columns}
                      pagination={false}
                      rowKey="id"
                      size="small"
                    />
                  </Card>
                </Col>
              </Row>

              {/* Quick Actions */}
              <Card title="Quick Actions">
                <Row gutter={[16, 16]}>
                  <Col xs={24} sm={12} lg={6}>
                    <Button
                      type="primary"
                      block
                      icon={<MessageOutlined />}
                      href="/conversations"
                    >
                      Manage Conversations
                    </Button>
                  </Col>
                  <Col xs={24} sm={12} lg={6}>
                    <Button
                      type="default"
                      block
                      icon={<UserOutlined />}
                      href="/users"
                    >
                      User Management
                    </Button>
                  </Col>
                  <Col xs={24} sm={12} lg={6}>
                    <Button
                      type="default"
                      block
                      icon={<ExclamationCircleOutlined />}
                      href="/analytics"
                    >
                      View Analytics
                    </Button>
                  </Col>
                  <Col xs={24} sm={12} lg={6}>
                    <Button
                      type="default"
                      block
                      icon={<CheckCircleOutlined />}
                      href="/settings"
                    >
                      System Settings
                    </Button>
                  </Col>
                </Row>
              </Card>
            </>
          )
        },
        {
          key: 'realtime',
          label: (
            <span>
              <BarChartOutlined />
              Real-Time Analytics
            </span>
          ),
          children: <RealTimeAnalytics />
        },
        {
          key: 'alerts',
          label: (
            <span>
              <AlertTriangleOutlined />
              System Alerts
            </span>
          ),
          children: (
            <Card title="Recent System Alerts">
              <div className="text-center py-8 text-gray-500">
                <AlertTriangleOutlined className="text-4xl mb-4" />
                <p>No active alerts at this time</p>
              </div>
            </Card>
          )
        }
      ]} />
    </div>
  );
};

export default Dashboard;