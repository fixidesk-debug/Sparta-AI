import React from 'react';
import styled from 'styled-components';
import { Sidebar } from './layout/Sidebar';
import { TopBar } from './layout/TopBar';
import { RightPanel } from './layout/RightPanel';
import { DataGrid } from './widgets/DataGrid';
import { SkeletonLoader } from './widgets/SkeletonLoader';

const LayoutContainer = styled.div`
  display: flex;
  min-height: 100vh;
  background: linear-gradient(135deg, #0a0e27 0%, #1a1f3a 100%);
`;

const MainContent = styled.main`
  flex: 1;
  margin-left: 280px;
  margin-right: 320px;
  margin-top: 64px;
  padding: 24px;
`;

const Grid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 24px;
  margin-bottom: 24px;
`;

const Card = styled.div`
  background: rgba(255, 255, 255, 0.06);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
  transition: all 250ms;
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
  }
`;

const CardTitle = styled.h3`
  margin: 0 0 16px 0;
  font-size: 18px;
  color: #f8fafc;
  font-weight: 600;
`;

const StatValue = styled.div`
  font-size: 32px;
  color: #2563eb;
  font-weight: 700;
  margin-bottom: 8px;
`;

const StatLabel = styled.div`
  font-size: 14px;
  color: #cbd5e1;
`;

const FAB = styled.button`
  position: fixed;
  bottom: 32px;
  right: 352px;
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background: linear-gradient(135deg, #2563eb, #3b82f6);
  border: none;
  color: white;
  font-size: 24px;
  cursor: pointer;
  box-shadow: 0 8px 24px rgba(37, 99, 235, 0.4);
  transition: all 200ms;
  
  &:hover {
    transform: scale(1.1);
    box-shadow: 0 12px 32px rgba(37, 99, 235, 0.6);
  }
`;

export const DashboardLayout: React.FC = () => (
  <LayoutContainer>
    <Sidebar />
    <TopBar />
    
    <MainContent>
      <h1 style={{ color: '#f8fafc', marginBottom: '24px', fontSize: '32px' }}>
        Dashboard
      </h1>
      
      <Grid>
        <Card>
          <CardTitle>Total Analyses</CardTitle>
          <StatValue>1,247</StatValue>
          <StatLabel>↑ 12% from last month</StatLabel>
        </Card>
        
        <Card>
          <CardTitle>Active Users</CardTitle>
          <StatValue>89</StatValue>
          <StatLabel>↑ 5% from last week</StatLabel>
        </Card>
        
        <Card>
          <CardTitle>Data Processed</CardTitle>
          <StatValue>2.4 TB</StatValue>
          <StatLabel>↑ 18% from last month</StatLabel>
        </Card>
      </Grid>

      <div style={{ marginBottom: '24px' }}>
        <h2 style={{ color: '#f8fafc', marginBottom: '16px', fontSize: '20px' }}>
          Recent Activity
        </h2>
        <DataGrid />
      </div>

      <div>
        <h2 style={{ color: '#f8fafc', marginBottom: '16px', fontSize: '20px' }}>
          Loading States
        </h2>
        <SkeletonLoader />
      </div>
    </MainContent>

    <RightPanel />
    <FAB>+</FAB>
  </LayoutContainer>
);
