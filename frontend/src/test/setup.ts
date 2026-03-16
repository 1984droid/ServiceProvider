/**
 * Vitest Test Setup
 *
 * Global test configuration and mocks
 */

import '@testing-library/jest-dom';
import { expect, afterEach, vi } from 'vitest';
import { cleanup } from '@testing-library/react';

// Cleanup after each test
afterEach(() => {
  cleanup();
});

// Mock window.URL.createObjectURL and revokeObjectURL
global.URL.createObjectURL = vi.fn(() => 'mock-object-url');
global.URL.revokeObjectURL = vi.fn();

// Mock canvas for image compression tests
HTMLCanvasElement.prototype.getContext = vi.fn(() => ({
  drawImage: vi.fn(),
  canvas: {
    toBlob: vi.fn((callback) => {
      const mockBlob = new Blob(['mock-image-data'], { type: 'image/jpeg' });
      callback(mockBlob);
    }),
  },
})) as any;

HTMLCanvasElement.prototype.toBlob = vi.fn(function(this: HTMLCanvasElement, callback) {
  const mockBlob = new Blob(['mock-image-data'], { type: 'image/jpeg' });
  callback(mockBlob);
});
