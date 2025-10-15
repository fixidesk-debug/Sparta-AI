import React from 'react';
import styled from 'styled-components';

const Panel = styled.aside`
  width: 320px;
  height: 100vh;
  background: rgba(10, 14, 39, 0.6);
  backdrop-filter: blur(12px);
  border-left: 1px solid rgba(255, 255, 255, 0.1);
  position: fixed;
  right: 0;
  top: 0;
  padding: 80px 16px 16px;
  overflow-y: auto;
`;

const Card = styled.div`
  background: rgba(255, 255, 255, 0.06);
  backdrop-filter: blur(8px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  padding: 16px;
  margin-bottom: 16px;
`;

const CardTitle = styled.h3`
  margin: 0 0 12px 0;
  font-size: 14px;
  color: #f8fafc;
  font-weight: 600;
`;

const ActivityItem = styled.div`
  display: flex;
  gap: 12px;
  padding: 8px 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  
  &:last-child { border-bottom: none; }
`;

const ActivityAvatar = styled.div`
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: linear-gradient(135deg, #2563eb, #3b82f6);
  flex-shrink: 0;
`;

const ActivityContent = styled.div`
  flex: 1;
  
  p {
    margin: 0;
    font-size: 13px;
    color: #cbd5e1;
    line-height: 1.4;
  }
  
  span {
    font-size: 11px;
    color: #64748b;
  }
`;

const MetricRow = styled.div`
  display: flex;
  justify-content: space-between;
  padding: 8px 0;
  font-size: 13px;
  
  span:first-child { color: #cbd5e1; }
  span:last-child { color: #f8fafc; font-weight: 500; }
`;

export const RightPanel: React.FC = () => (
  <Panel>
    <Card>
      <CardTitle>Team Activity</CardTitle>
      <ActivityItem>
        <ActivityAvatar />
        <ActivityContent>
          <p>Sarah analyzed sales data</p>
          <span>2 minutes ago</span>
        </ActivityContent>
      </ActivityItem>
      <ActivityItem>
        <ActivityAvatar />
        <ActivityContent>
          <p>Mike shared a dashboard</p>
          <span>15 minutes ago</span>
        </ActivityContent>
      </ActivityItem>
    </Card>

    <Card>
      <CardTitle>Current Analysis</CardTitle>
      <MetricRow>
        <span>Model</span>
        <span>GPT-4</span>
      </MetricRow>
      <MetricRow>
        <span>Tokens Used</span>
        <span>1,247</span>
      </MetricRow>
      <MetricRow>
        <span>Response Time</span>
        <span>1.2s</span>
      </MetricRow>
    </Card>

    <Card>
      <CardTitle>Data Sources</CardTitle>
      <MetricRow>
        <span>🟢 PostgreSQL</span>
        <span>Connected</span>
      </MetricRow>
      <MetricRow>
        <span>🟡 MongoDB</span>
        <span>Syncing</span>
      </MetricRow>
    </Card>
  </Panel>
);
