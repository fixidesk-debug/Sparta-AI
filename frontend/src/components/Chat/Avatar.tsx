import React from 'react';
import styled from 'styled-components';
import { motion } from 'framer-motion';

interface AvatarProps {
  src: string;
  alt: string;
  isOnline: boolean;
}

const AvatarWrapper = styled(motion.div)`
  position: relative;
  width: 40px;
  height: 40px;
`;

const Img = styled.img`
  width: 100%;
  height: 100%;
  border-radius: 50%;
  object-fit: cover;
  border: 2px solid var(--glass-border);
`;

const StatusIndicator = styled(motion.div)<{ $isOnline: boolean }>`
  position: absolute;
  bottom: 0;
  right: 0;
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background-color: ${props => (props.$isOnline ? '#22c55e' : '#64748b')};
  border: 2px solid var(--bg-primary);
`;

export const Avatar: React.FC<AvatarProps> = ({ src, alt, isOnline }) => {
  return (
    <AvatarWrapper>
      <Img src={src} alt={alt} />
      <StatusIndicator
        $isOnline={isOnline}
        initial={{ scale: 0 }}
        animate={{ scale: 1 }}
        transition={{ type: 'spring', stiffness: 500, damping: 30 }}
      />
    </AvatarWrapper>
  );
};
