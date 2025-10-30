/*
 ** EPITECH PROJECT, 2025
 ** Area
 ** File description:
 ** App component tests
 */

import { describe, it, expect } from 'vitest';
import { render } from '@testing-library/react';
import App from '../App';

describe('App', () => {
  it('should render without crashing', () => {
    render(<App />);
    expect(document.querySelector('nav')).toBeInTheDocument();
  });

  it('should render Navbar component', () => {
    render(<App />);
    const nav = document.querySelector('nav');
    expect(nav).toBeInTheDocument();
  });

  it('should render router', () => {
    const { container } = render(<App />);
    expect(container.firstChild).toBeInTheDocument();
  });
});
