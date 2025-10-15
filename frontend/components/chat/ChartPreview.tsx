import React, { useState } from 'react';
import styled from 'styled-components';
import { motion, AnimatePresence } from 'framer-motion';
import { ChartData } from './types';

const ChartContainer = styled.div`
  background: rgba(255, 255, 255, 0.06);
  backdrop-filter: blur(12px);
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  padding: 16px;
  cursor: pointer;
  transition: all 250ms;
  
  &:hover {
    background: rgba(255, 255, 255, 0.1);
    transform: scale(1.02);
  }
`;

const ChartTitle = styled.h4`
  margin: 0 0 12px 0;
  font-size: 14px;
  color: #f8fafc;
  font-weight: 600;
`;

const ChartPlaceholder = styled.div`
  height: 200px;
  background: linear-gradient(135deg, rgba(37, 99, 235, 0.1), rgba(59, 130, 246, 0.1));
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #60a5fa;
  font-size: 12px;
`;

const ExpandButton = styled.button`
  margin-top: 8px;
  background: transparent;
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: #cbd5e1;
  padding: 6px 12px;
  border-radius: 6px;
  font-size: 12px;
  cursor: pointer;
  transition: all 150ms;
  
  &:hover {
    background: rgba(255, 255, 255, 0.1);
    border-color: #2563eb;
    color: #f8fafc;
  }
`;

const Modal = styled(motion.div)`
  position: fixed;
  inset: 0;
  background: rgba(10, 14, 39, 0.9);
  backdrop-filter: blur(24px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 32px;
`;

const ModalContent = styled(motion.div)`
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(16px);
  border-radius: 24px;
  border: 1px solid rgba(255, 255, 255, 0.18);
  padding: 32px;
  max-width: 900px;
  width: 100%;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
`;

export const ChartPreview: React.FC<ChartData> = ({ type, title, data }) => {
  const [expanded, setExpanded] = useState(false);

  return (
    <>
      <ChartContainer onClick={() => setExpanded(true)}>
        <ChartTitle>{title}</ChartTitle>
        <ChartPlaceholder>
          📊 {type.toUpperCase()} Chart Preview
        </ChartPlaceholder>
        <ExpandButton onClick={(e) => { e.stopPropagation(); setExpanded(true); }}>
          Expand Chart
        </ExpandButton>
      </ChartContainer>

      <AnimatePresence>
        {expanded && (
          <Modal
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={() => setExpanded(false)}
          >
            <ModalContent
              initial={{ scale: 0.9, y: 20 }}
              animate={{ scale: 1, y: 0 }}
              exit={{ scale: 0.9, y: 20 }}
              onClick={(e) => e.stopPropagation()}
            >
              <ChartTitle>{title}</ChartTitle>
              <ChartPlaceholder style={{ height: '500px' }}>
                Full Size {type.toUpperCase()} Chart
              </ChartPlaceholder>
            </ModalContent>
          </Modal>
        )}
      </AnimatePresence>
    </>
  );
};
