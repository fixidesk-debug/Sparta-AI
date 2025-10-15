import React, { useState } from 'react';
import styled from 'styled-components';

const GridContainer = styled.div`
  background: rgba(255, 255, 255, 0.06);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  overflow: hidden;
`;

const Table = styled.table`
  width: 100%;
  border-collapse: collapse;
`;

const Thead = styled.thead`
  background: rgba(255, 255, 255, 0.05);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
`;

const Th = styled.th`
  padding: 16px;
  text-align: left;
  font-size: 13px;
  color: #cbd5e1;
  font-weight: 600;
  cursor: pointer;
  user-select: none;
  
  &:hover { color: #f8fafc; }
`;

const Tr = styled.tr`
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  transition: background 150ms;
  
  &:hover { background: rgba(255, 255, 255, 0.05); }
  &:nth-child(even) { background: rgba(255, 255, 255, 0.02); }
`;

const Td = styled.td`
  padding: 16px;
  font-size: 14px;
  color: #f8fafc;
`;

const StatusBadge = styled.span<{ $status: string }>`
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  background: ${p => {
    if (p.$status === 'active') return 'rgba(16, 185, 129, 0.2)';
    if (p.$status === 'pending') return 'rgba(251, 191, 36, 0.2)';
    return 'rgba(239, 68, 68, 0.2)';
  }};
  color: ${p => {
    if (p.$status === 'active') return '#10b981';
    if (p.$status === 'pending') return '#fbbf24';
    return '#ef4444';
  }};
`;

interface DataRow {
  id: string;
  name: string;
  status: string;
  value: number;
}

export const DataGrid: React.FC = () => {
  const [data] = useState<DataRow[]>([
    { id: '1', name: 'Analysis A', status: 'active', value: 1250 },
    { id: '2', name: 'Analysis B', status: 'pending', value: 890 },
    { id: '3', name: 'Analysis C', status: 'active', value: 2100 }
  ]);

  return (
    <GridContainer>
      <Table>
        <Thead>
          <tr>
            <Th>Name ↕</Th>
            <Th>Status ↕</Th>
            <Th>Value ↕</Th>
          </tr>
        </Thead>
        <tbody>
          {data.map(row => (
            <Tr key={row.id}>
              <Td>{row.name}</Td>
              <Td><StatusBadge $status={row.status}>{row.status}</StatusBadge></Td>
              <Td>{row.value.toLocaleString()}</Td>
            </Tr>
          ))}
        </tbody>
      </Table>
    </GridContainer>
  );
};
