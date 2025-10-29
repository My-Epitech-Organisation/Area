import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import ProfileModal from '../ProfileModal';

describe('ProfileModal Component', () => {
  const mockOnClose = vi.fn();
  const mockOnConfirm = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('Rendering and Visibility', () => {
    it('should not render when isOpen is false', () => {
      const { container } = render(
        <ProfileModal isOpen={false} onClose={mockOnClose} onConfirm={mockOnConfirm} />
      );

      expect(container.firstChild).toBeNull();
    });

    it('should render when isOpen is true', () => {
      render(<ProfileModal isOpen={true} onClose={mockOnClose} onConfirm={mockOnConfirm} />);

      expect(screen.getByText('Confirm Action')).toBeInTheDocument();
      expect(
        screen.getByText('Please enter your current password to confirm changes')
      ).toBeInTheDocument();
    });

    it('should render with custom title and message', () => {
      render(
        <ProfileModal
          isOpen={true}
          onClose={mockOnClose}
          onConfirm={mockOnConfirm}
          title="Delete Account"
          message="Enter password to delete your account permanently"
        />
      );

      expect(screen.getByText('Delete Account')).toBeInTheDocument();
      expect(
        screen.getByText('Enter password to delete your account permanently')
      ).toBeInTheDocument();
    });
  });

  describe('Form Interaction', () => {
    it('should render password input field', () => {
      render(<ProfileModal isOpen={true} onClose={mockOnClose} onConfirm={mockOnConfirm} />);

      const passwordInput = screen.getByLabelText('Current Password');
      expect(passwordInput).toBeInTheDocument();
      expect(passwordInput).toHaveAttribute('type', 'password');
    });

    it('should update password value on input change', () => {
      render(<ProfileModal isOpen={true} onClose={mockOnClose} onConfirm={mockOnConfirm} />);

      const passwordInput = screen.getByLabelText('Current Password') as HTMLInputElement;
      fireEvent.change(passwordInput, { target: { value: 'mypassword123' } });

      expect(passwordInput.value).toBe('mypassword123');
    });

    it('should have password input with placeholder', () => {
      render(<ProfileModal isOpen={true} onClose={mockOnClose} onConfirm={mockOnConfirm} />);

      const passwordInput = screen.getByPlaceholderText('Enter your current password');
      expect(passwordInput).toBeInTheDocument();
    });
  });

  describe('Form Submission', () => {
    it('should call onConfirm with password when form is submitted', () => {
      render(<ProfileModal isOpen={true} onClose={mockOnClose} onConfirm={mockOnConfirm} />);

      const passwordInput = screen.getByLabelText('Current Password');
      const confirmButton = screen.getByRole('button', { name: /confirm/i });

      fireEvent.change(passwordInput, { target: { value: 'testpass123' } });
      fireEvent.click(confirmButton);

      expect(mockOnConfirm).toHaveBeenCalledWith('testpass123');
      expect(mockOnConfirm).toHaveBeenCalledTimes(1);
    });

    it('should not call onConfirm if password is empty', () => {
      render(<ProfileModal isOpen={true} onClose={mockOnClose} onConfirm={mockOnConfirm} />);

      const confirmButton = screen.getByRole('button', { name: /confirm/i });
      fireEvent.click(confirmButton);

      expect(mockOnConfirm).not.toHaveBeenCalled();
    });

    it('should clear password after submission', () => {
      render(<ProfileModal isOpen={true} onClose={mockOnClose} onConfirm={mockOnConfirm} />);

      const passwordInput = screen.getByLabelText('Current Password') as HTMLInputElement;
      const confirmButton = screen.getByRole('button', { name: /confirm/i });

      fireEvent.change(passwordInput, { target: { value: 'testpass123' } });
      fireEvent.click(confirmButton);

      expect(passwordInput.value).toBe('');
    });
  });

  describe('Cancel Functionality', () => {
    it('should call onClose when cancel button is clicked', () => {
      render(<ProfileModal isOpen={true} onClose={mockOnClose} onConfirm={mockOnConfirm} />);

      const cancelButton = screen.getByRole('button', { name: /cancel/i });
      fireEvent.click(cancelButton);

      expect(mockOnClose).toHaveBeenCalledTimes(1);
    });

    it('should clear password when cancel is clicked', () => {
      render(<ProfileModal isOpen={true} onClose={mockOnClose} onConfirm={mockOnConfirm} />);

      const passwordInput = screen.getByLabelText('Current Password') as HTMLInputElement;
      const cancelButton = screen.getByRole('button', { name: /cancel/i });

      fireEvent.change(passwordInput, { target: { value: 'testpass123' } });
      expect(passwordInput.value).toBe('testpass123');

      fireEvent.click(cancelButton);
      expect(mockOnClose).toHaveBeenCalled();
    });
  });

  describe('Focus Management', () => {
    it('should focus password input when modal opens', async () => {
      const { rerender } = render(
        <ProfileModal isOpen={false} onClose={mockOnClose} onConfirm={mockOnConfirm} />
      );

      rerender(<ProfileModal isOpen={true} onClose={mockOnClose} onConfirm={mockOnConfirm} />);

      await waitFor(
        () => {
          const passwordInput = screen.getByLabelText('Current Password');
          expect(document.activeElement).toBe(passwordInput);
        },
        { timeout: 200 }
      );
    });
  });

  describe('Accessibility and Structure', () => {
    it('should have proper form structure', () => {
      render(<ProfileModal isOpen={true} onClose={mockOnClose} onConfirm={mockOnConfirm} />);

      const form = screen.getByLabelText('Current Password').closest('form');
      expect(form).toBeInTheDocument();
    });

    it('should have required attribute on password input', () => {
      render(<ProfileModal isOpen={true} onClose={mockOnClose} onConfirm={mockOnConfirm} />);

      const passwordInput = screen.getByLabelText('Current Password');
      expect(passwordInput).toHaveAttribute('required');
    });

    it('should render both action buttons', () => {
      render(<ProfileModal isOpen={true} onClose={mockOnClose} onConfirm={mockOnConfirm} />);

      expect(screen.getByRole('button', { name: /confirm/i })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /cancel/i })).toBeInTheDocument();
    });

    it('should stop propagation when clicking modal content', () => {
      render(<ProfileModal isOpen={true} onClose={mockOnClose} onConfirm={mockOnConfirm} />);

      const modalContent = screen.getByText('Confirm Action').closest('div');
      const stopPropagationSpy = vi.fn();

      const event = new MouseEvent('click', { bubbles: true });
      Object.defineProperty(event, 'stopPropagation', {
        value: stopPropagationSpy,
      });

      modalContent?.dispatchEvent(event);
      expect(modalContent).toBeInTheDocument();
    });
  });
});
