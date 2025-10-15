/**
 * Analysis Results Dashboard Example
 * Demonstrates usage of all analysis card components
 */

import React from 'react';
import styled from 'styled-components';
import {
  AnalysisCard,
  MetricCard,
  ProgressBar,
  StatusIndicator,
  StatisticalResult,
  ComparisonCard,
} from './AnalysisCards';
import {
  TimelineCard,
  DistributionCard,
  CorrelationCard,
  TrendCard,
  CategoryCard,
  AlertCard,
} from './SpecializedCards';

export const AnalysisDashboardExample: React.FC = () => {
  // Example data
  const sampleData = {
    metrics: [
      { label: 'Total Records', value: '12,543', trend: 'up' as const, trendValue: '+8.3%', icon: '📊' },
      { label: 'Accuracy', value: '94.2%', trend: 'up' as const, trendValue: '+2.1%', icon: '🎯' },
      { label: 'Processing Time', value: '2.4s', trend: 'down' as const, trendValue: '-15%', icon: '⚡' },
      { label: 'Error Rate', value: '0.03%', trend: 'down' as const, trendValue: '-0.5%', icon: '✓' },
    ],
    timeline: {
      milestones: [
        { label: 'Data Collection', date: '2025-01-15', completed: true, description: 'Gathered 10K samples' },
        { label: 'Data Cleaning', date: '2025-01-20', completed: true, description: 'Removed duplicates and outliers' },
        { label: 'Feature Engineering', date: '2025-01-25', completed: true, description: 'Created 15 new features' },
        { label: 'Model Training', date: '2025-02-01', completed: false, description: 'Training XGBoost classifier' },
        { label: 'Model Evaluation', date: '2025-02-05', completed: false, description: 'Cross-validation testing' },
      ],
    },
    distribution: {
      data: Array.from({ length: 100 }, () => Math.random() * 100 + 50),
      stats: { mean: 75.3, median: 72.1, stdDev: 12.5, min: 48.2, max: 98.7 },
    },
    correlation: {
      data: Array.from({ length: 30 }, () => ({
        x: Math.random() * 100,
        y: Math.random() * 100,
      })),
      coefficient: 0.847,
      pValue: 0.0023,
    },
    categories: [
      { label: 'Category A', value: 3456, percentage: 45.2, color: '#3b82f6' },
      { label: 'Category B', value: 2134, percentage: 27.9, color: '#8b5cf6' },
      { label: 'Category C', value: 1342, percentage: 17.5, color: '#10b981' },
      { label: 'Category D', value: 721, percentage: 9.4, color: '#f59e0b' },
    ],
  };

  return (
    <DashboardContainer>
      <DashboardTitle>Analysis Results Dashboard</DashboardTitle>
      <DashboardSubtitle>Comprehensive overview of your data analysis</DashboardSubtitle>

      {/* Alert Section */}
      <Section>
        <AlertCard
          type="info"
          title="Analysis Complete"
          message="Your statistical analysis has been completed successfully. Review the results below."
          actions={[
            { label: 'Download Report', onClick: () => console.log('Download'), primary: true },
            { label: 'Share', onClick: () => console.log('Share') },
          ]}
        />
      </Section>

      {/* Metrics Grid */}
      <Section>
        <SectionTitle>Key Metrics</SectionTitle>
        <MetricsGrid>
          {sampleData.metrics.map((metric, index) => (
            <MetricCard key={index} {...metric} size="medium" />
          ))}
        </MetricsGrid>
      </Section>

      {/* Main Analysis Cards */}
      <Section>
        <SectionTitle>Detailed Analysis</SectionTitle>
        <CardsGrid>
          {/* Statistical Result Card */}
          <AnalysisCard
            title="T-Test Results"
            subtitle="Comparing treatment vs control groups"
            icon="📈"
            variant="default"
          >
            <StatisticalResult
              metric="Mean Difference"
              value={5.234}
              pValue={0.0012}
              confidenceInterval={[3.12, 7.35]}
              effectSize={0.82}
              significance="high"
            />
            <Separator />
            <ProgressBar
              label="Statistical Power"
              value={87}
              color="#10b981"
              variant="gradient"
            />
          </AnalysisCard>

          {/* Comparison Card */}
          <AnalysisCard
            title="Group Comparison"
            subtitle="Treatment effectiveness analysis"
            icon="⚖️"
            variant="success"
          >
            <ComparisonCard
              leftMetric={{ label: 'Treatment Group', value: '92.4%', subtitle: 'Success rate' }}
              rightMetric={{ label: 'Control Group', value: '78.1%', subtitle: 'Success rate' }}
              comparison="better"
              comparisonText="14.3% improvement"
            />
          </AnalysisCard>

          {/* Distribution Card */}
          <DistributionCard
            title="Data Distribution"
            data={sampleData.distribution.data}
            stats={sampleData.distribution.stats}
          />

          {/* Correlation Card */}
          <CorrelationCard
            title="Variable Correlation"
            xLabel="Feature X"
            yLabel="Feature Y"
            coefficient={sampleData.correlation.coefficient}
            pValue={sampleData.correlation.pValue}
            data={sampleData.correlation.data}
          />

          {/* Trend Card */}
          <TrendCard
            title="Monthly Users"
            value={12543}
            change={8.3}
            direction="up"
            sparklineData={[85, 92, 78, 95, 88, 102, 98, 110, 105, 118, 125, 132]}
            period="Last 12 months"
          />

          {/* Category Card */}
          <CategoryCard
            title="Distribution by Category"
            categories={sampleData.categories}
            total={7653}
          />

          {/* Timeline Card */}
          <TimelineCard title="Project Timeline" milestones={sampleData.timeline.milestones} />

          {/* Status Indicators */}
          <AnalysisCard
            title="System Status"
            subtitle="Current operational status"
            icon="🔄"
            variant="default"
          >
            <StatusList>
              <StatusIndicator
                status="success"
                label="Data Pipeline"
                description="All systems operational"
              />
              <StatusIndicator
                status="warning"
                label="Model Training"
                description="High memory usage detected"
              />
              <StatusIndicator
                status="info"
                label="API Integration"
                description="Rate limit at 75% capacity"
              />
            </StatusList>
          </AnalysisCard>
        </CardsGrid>
      </Section>

      {/* Interactive Example */}
      <Section>
        <SectionTitle>Interactive Results</SectionTitle>
        <AnalysisCard
          title="Model Performance"
          subtitle="Click to select for detailed analysis"
          icon="🎯"
          variant="default"
          selected={false}
          onSelect={() => console.log('Selected')}
          actions={[
            { label: 'View Details', onClick: () => console.log('Details'), icon: '📊' },
            { label: 'Export', onClick: () => console.log('Export'), icon: '💾' },
            { label: 'Compare', onClick: () => console.log('Compare'), icon: '⚖️' },
          ]}
        >
          <MetricsRow>
            <MetricCard label="Precision" value="0.94" size="small" color="#10b981" />
            <MetricCard label="Recall" value="0.91" size="small" color="#3b82f6" />
            <MetricCard label="F1-Score" value="0.93" size="small" color="#8b5cf6" />
          </MetricsRow>
          <Separator />
          <ProgressBar label="Model Confidence" value={93} color="#3b82f6" showPercentage />
          <ProgressBar label="Training Progress" value={67} color="#8b5cf6" showPercentage />
        </AnalysisCard>
      </Section>

      {/* Loading State Example */}
      <Section>
        <SectionTitle>Loading State Example</SectionTitle>
        <AnalysisCard
          title="Processing Data"
          subtitle="Please wait while we analyze your data"
          icon="⏳"
          variant="default"
          loading={true}
        >
          <div>Content will appear once loading is complete</div>
        </AnalysisCard>
      </Section>

      {/* Error State Example */}
      <Section>
        <AlertCard
          type="error"
          title="Analysis Failed"
          message="Unable to complete the analysis due to insufficient data. Please upload more samples."
          actions={[
            { label: 'Retry', onClick: () => console.log('Retry'), primary: true },
            { label: 'Upload Data', onClick: () => console.log('Upload') },
          ]}
          dismissible={true}
          onDismiss={() => console.log('Dismissed')}
        />
      </Section>
    </DashboardContainer>
  );
};

// Styled Components
const DashboardContainer = styled.div`
  max-width: 1400px;
  margin: 0 auto;
  padding: 32px;
  background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%);
  min-height: 100vh;

  @media (max-width: 768px) {
    padding: 16px;
  }
`;

const DashboardTitle = styled.h1`
  margin: 0 0 8px;
  font-family: 'Inter', sans-serif;
  font-size: 32px;
  font-weight: 700;
  color: #f8fafc;
  background: linear-gradient(135deg, #3b82f6, #8b5cf6);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
`;

const DashboardSubtitle = styled.p`
  margin: 0 0 32px;
  font-family: 'Inter', sans-serif;
  font-size: 16px;
  font-weight: 400;
  color: #94a3b8;
`;

const Section = styled.section`
  margin-bottom: 32px;
`;

const SectionTitle = styled.h2`
  margin: 0 0 16px;
  font-family: 'Inter', sans-serif;
  font-size: 20px;
  font-weight: 600;
  color: #f8fafc;
`;

const MetricsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 16px;

  @media (max-width: 640px) {
    grid-template-columns: 1fr;
  }
`;

const CardsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 24px;

  @media (max-width: 768px) {
    grid-template-columns: 1fr;
  }
`;

const StatusList = styled.div`
  display: flex;
  flex-direction: column;
  gap: 16px;
`;

const MetricsRow = styled.div`
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
  margin-bottom: 16px;

  @media (max-width: 640px) {
    grid-template-columns: 1fr;
  }
`;

const Separator = styled.div`
  height: 1px;
  background: rgba(255, 255, 255, 0.1);
  margin: 16px 0;
`;

export default AnalysisDashboardExample;
