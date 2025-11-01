/*
 ** EPITECH PROJECT, 2025
 ** Area
 ** File description:
 ** About page tests
 */

import { describe, it, expect } from 'vitest';
import { render } from '@testing-library/react';
import About from '../About';

describe('About', () => {
  it('should render About page', () => {
    render(<About />);

    expect(document.body).toBeInTheDocument();
  });

  it('should render without crashing', () => {
    const { container } = render(<About />);
    expect(container).toBeInTheDocument();
  });
});
