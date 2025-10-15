import React from 'react';
import styled, { keyframes } from 'styled-components';

const shimmer = keyframes`
  0% { transform: translateX(-100%); }
  100% { transform: translateX(100%); }
`;

const SkeletonBox = styled.div<{ $width?: string; $height?: string }>`
  width: ${p => p.$width || '100%'};
  height: ${p => p.$height || '20px'};
  background: rgba(255, 255, 255, 0.05);
  border-radius: 8px;
  position: relative;
  overflow: hidden;
  
  &::after {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.1), transparent);
    animation: ${shimmer} 2s infinite;
  }
`;

const SkeletonCard = styled.div`
  background: rgba(255, 255, 255, 0.06);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  padding: 24px;
`;

export const SkeletonLoader: React.FC = () => (
  <SkeletonCard>
    <SkeletonBox $width="60%" $height="24px" style={{ marginBottom: '16px' }} />
    <SkeletonBox $height="16px" style={{ marginBottom: '8px' }} />
    <SkeletonBox $width="80%" $height="16px" style={{ marginBottom: '8px' }} />
    <SkeletonBox $width="90%" $height="16px" />
  </SkeletonCard>
);
