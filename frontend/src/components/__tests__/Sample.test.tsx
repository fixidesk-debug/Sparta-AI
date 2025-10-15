/// <reference types="vitest" />
import React from 'react';
import { render, screen } from '@testing-library/react';
import Sample from '../Sample';

test('renders sample component', () => {
  render(<Sample />);
  const el = screen.getByText(/sample/i);
  expect(el).toBeTruthy();
});