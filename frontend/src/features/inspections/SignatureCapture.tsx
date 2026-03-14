/**
 * SignatureCapture
 *
 * HTML5 Canvas-based signature capture component
 * Allows user to draw signature with mouse/touch
 * Exports signature as base64 PNG data URL
 */

import { useRef, useState, useEffect } from 'react';

interface SignatureCaptureProps {
  onSignatureChange: (signatureData: string | null) => void;
  width?: number;
  height?: number;
}

export function SignatureCapture({
  onSignatureChange,
  width = 500,
  height = 200,
}: SignatureCaptureProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [isDrawing, setIsDrawing] = useState(false);
  const [isEmpty, setIsEmpty] = useState(true);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Set canvas background to white
    ctx.fillStyle = 'white';
    ctx.fillRect(0, 0, width, height);

    // Set drawing style
    ctx.strokeStyle = '#000';
    ctx.lineWidth = 2;
    ctx.lineCap = 'round';
    ctx.lineJoin = 'round';
  }, [width, height]);

  const getCoordinates = (
    e: React.MouseEvent<HTMLCanvasElement> | React.TouchEvent<HTMLCanvasElement>
  ): { x: number; y: number } | null => {
    const canvas = canvasRef.current;
    if (!canvas) return null;

    const rect = canvas.getBoundingClientRect();

    if ('touches' in e) {
      // Touch event
      const touch = e.touches[0];
      return {
        x: touch.clientX - rect.left,
        y: touch.clientY - rect.top,
      };
    } else {
      // Mouse event
      return {
        x: e.clientX - rect.left,
        y: e.clientY - rect.top,
      };
    }
  };

  const startDrawing = (
    e: React.MouseEvent<HTMLCanvasElement> | React.TouchEvent<HTMLCanvasElement>
  ) => {
    e.preventDefault();
    const coords = getCoordinates(e);
    if (!coords) return;

    const ctx = canvasRef.current?.getContext('2d');
    if (!ctx) return;

    setIsDrawing(true);
    ctx.beginPath();
    ctx.moveTo(coords.x, coords.y);
  };

  const draw = (
    e: React.MouseEvent<HTMLCanvasElement> | React.TouchEvent<HTMLCanvasElement>
  ) => {
    e.preventDefault();
    if (!isDrawing) return;

    const coords = getCoordinates(e);
    if (!coords) return;

    const ctx = canvasRef.current?.getContext('2d');
    if (!ctx) return;

    ctx.lineTo(coords.x, coords.y);
    ctx.stroke();

    setIsEmpty(false);
  };

  const stopDrawing = () => {
    if (!isDrawing) return;
    setIsDrawing(false);

    // Export signature as base64 PNG
    const canvas = canvasRef.current;
    if (!canvas) return;

    const signatureData = canvas.toDataURL('image/png');
    onSignatureChange(signatureData);
  };

  const clear = () => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Clear canvas and reset to white background
    ctx.fillStyle = 'white';
    ctx.fillRect(0, 0, width, height);

    setIsEmpty(true);
    setIsDrawing(false);
    onSignatureChange(null);
  };

  return (
    <div className="space-y-3">
      <div className="relative">
        <canvas
          ref={canvasRef}
          width={width}
          height={height}
          onMouseDown={startDrawing}
          onMouseMove={draw}
          onMouseUp={stopDrawing}
          onMouseLeave={stopDrawing}
          onTouchStart={startDrawing}
          onTouchMove={draw}
          onTouchEnd={stopDrawing}
          className="border-2 border-gray-300 rounded-lg cursor-crosshair bg-white touch-none"
          style={{ touchAction: 'none' }}
        />
        {isEmpty && (
          <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
            <p className="text-gray-400 text-sm">
              Sign here with your mouse or finger
            </p>
          </div>
        )}
      </div>
      <div className="flex justify-between items-center">
        <p className="text-xs text-gray-500">
          Draw your signature in the box above
        </p>
        <button
          onClick={clear}
          className="px-3 py-1.5 text-sm text-red-600 hover:bg-red-50 rounded transition-colors"
          disabled={isEmpty}
        >
          Clear
        </button>
      </div>
    </div>
  );
}
