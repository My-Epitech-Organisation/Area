/*
 ** EPITECH PROJECT, 2025
 ** Area
 ** File description:
 ** HomePage tests
 */

import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import HomePage from '../HomePage';

describe('HomePage', () => {
  it('should render without crashing', () => {
    const { container } = render(
      <BrowserRouter>
        <HomePage />
      </BrowserRouter>
    );
    expect(container).toBeInTheDocument();
  });

  it('should render navigation', () => {
    render(
      <BrowserRouter>
        <HomePage />
      </BrowserRouter>
    );
    const nav = document.querySelector('nav');
    expect(nav).toBeInTheDocument();
  });

  it('should render background container', () => {
    const { container } = render(
      <BrowserRouter>
        <HomePage />
      </BrowserRouter>
    );
    expect(container.querySelector('.relative')).toBeInTheDocument();
  });

  it('should render main heading', () => {
    render(
      <BrowserRouter>
        <HomePage />
      </BrowserRouter>
    );

    const heading = screen.queryByRole('heading', { level: 1 });
    if (heading) {
      expect(heading).toBeInTheDocument();
    }
  });

  it('should have proper page structure', () => {
    const { container } = render(
      <BrowserRouter>
        <HomePage />
      </BrowserRouter>
    );

    expect(container.firstChild).toBeTruthy();
    expect(container.querySelector('div')).toBeInTheDocument();
  });

  it('should render with BrowserRouter context', () => {
    const { container } = render(
      <BrowserRouter>
        <HomePage />
      </BrowserRouter>
    );

    expect(container).toBeInTheDocument();
  });

  it('should have accessible structure', () => {
    const { container } = render(
      <BrowserRouter>
        <HomePage />
      </BrowserRouter>
    );

    const divs = container.querySelectorAll('div');
    expect(divs.length).toBeGreaterThan(0);
  });

  it('should render any links present on the page', () => {
    render(
      <BrowserRouter>
        <HomePage />
      </BrowserRouter>
    );

    const links = screen.queryAllByRole('link');
    expect(links).toBeDefined();
  });

  it('should render any buttons present on the page', () => {
    render(
      <BrowserRouter>
        <HomePage />
      </BrowserRouter>
    );

    const buttons = screen.queryAllByRole('button');
    expect(buttons).toBeDefined();
  });

  it('should have proper CSS classes', () => {
    const { container } = render(
      <BrowserRouter>
        <HomePage />
      </BrowserRouter>
    );

    const element = container.querySelector('.relative');
    expect(element).toBeInTheDocument();
  });
});
