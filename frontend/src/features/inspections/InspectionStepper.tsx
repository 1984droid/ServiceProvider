/**
 * InspectionStepper
 *
 * Visual step navigation component for inspection execution
 * Shows list of steps with current step highlighted
 * Allows clicking to jump between steps
 */

import { useState } from 'react';

interface Step {
  step_id: string;
  type: string;
  title: string;
  description?: string;
}

interface InspectionStepperProps {
  steps: Step[];
  currentStepIndex: number;
  onStepClick: (index: number) => void;
  completedSteps?: Set<number>;
  disabled?: boolean;
}

export function InspectionStepper({
  steps,
  currentStepIndex,
  onStepClick,
  completedSteps = new Set(),
  disabled = false,
}: InspectionStepperProps) {
  const [collapsed, setCollapsed] = useState(false);

  // Get icon for step type
  const getStepIcon = (stepType: string) => {
    const type = stepType.toUpperCase();
    switch (type) {
      case 'SETUP':
        return (
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
          </svg>
        );
      case 'VISUAL_INSPECTION':
        return (
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
          </svg>
        );
      case 'FUNCTION_TEST':
        return (
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        );
      case 'MEASUREMENT':
        return (
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 21a4 4 0 01-4-4V5a2 2 0 012-2h4a2 2 0 012 2v12a4 4 0 01-4 4zm0 0h12a2 2 0 002-2v-4a2 2 0 00-2-2h-2.343M11 7.343l1.657-1.657a2 2 0 012.828 0l2.829 2.829a2 2 0 010 2.828l-8.486 8.485M7 17h.01" />
          </svg>
        );
      case 'DEFECT_CAPTURE':
        return (
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
        );
      default:
        return (
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
        );
    }
  };

  // Get colors for step status
  const getStepColors = (index: number) => {
    const isCurrent = index === currentStepIndex;
    const isCompleted = completedSteps.has(index);

    if (isCurrent) {
      return {
        bg: '#dbeafe',
        border: '#7ed321',
        text: '#111827',
        icon: '#7ed321',
      };
    } else if (isCompleted) {
      return {
        bg: '#dcfce7',
        border: '#10b981',
        text: '#166534',
        icon: '#10b981',
      };
    } else {
      return {
        bg: 'white',
        border: '#e5e7eb',
        text: '#6b7280',
        icon: '#9ca3af',
      };
    }
  };

  return (
    <div className="border-r h-full flex flex-col" style={{ borderColor: '#e5e7eb', width: collapsed ? '48px' : '240px', transition: 'width 0.2s' }}>
      {/* Header with collapse button */}
      <div className="flex-shrink-0 px-2 py-1 border-b flex items-center justify-between" style={{ borderColor: '#e5e7eb' }}>
        {!collapsed && (
          <span className="text-xs font-medium" style={{ color: '#6b7280' }}>
            {currentStepIndex + 1}/{steps.length}
          </span>
        )}
        <button
          onClick={() => setCollapsed(!collapsed)}
          className="flex-shrink-0 p-1 rounded hover:bg-gray-100 transition-colors"
          style={{ color: '#6b7280' }}
        >
          <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            {collapsed ? (
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
            ) : (
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            )}
          </svg>
        </button>
      </div>

      {/* Steps list */}
      <div className="flex-1 overflow-y-auto">
        {steps.map((step, index) => {
          const colors = getStepColors(index);
          const isCurrent = index === currentStepIndex;
          const isClickable = !disabled;

          return (
            <button
              key={step.step_id}
              onClick={() => isClickable && onStepClick(index)}
              disabled={!isClickable}
              className="w-full text-left p-2 border-b transition-all"
              style={{
                borderColor: '#e5e7eb',
                backgroundColor: colors.bg,
                borderLeft: isCurrent ? `3px solid ${colors.border}` : '3px solid transparent',
                cursor: isClickable ? 'pointer' : 'default',
              }}
            >
              {collapsed ? (
                // Collapsed view - just step number
                <div className="flex items-center justify-center">
                  <div
                    className="w-6 h-6 rounded-full flex items-center justify-center text-xs font-semibold"
                    style={{
                      backgroundColor: isCurrent ? colors.icon : 'transparent',
                      border: `2px solid ${colors.icon}`,
                      color: isCurrent ? 'white' : colors.icon,
                    }}
                  >
                    {completedSteps.has(index) ? (
                      <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                      </svg>
                    ) : (
                      index + 1
                    )}
                  </div>
                </div>
              ) : (
                // Expanded view
                <div className="flex items-start gap-2">
                  {/* Step Number Circle */}
                  <div
                    className="flex-shrink-0 w-6 h-6 rounded-full flex items-center justify-center text-xs font-semibold"
                    style={{
                      backgroundColor: isCurrent ? colors.icon : 'transparent',
                      border: `2px solid ${colors.icon}`,
                      color: isCurrent ? 'white' : colors.icon,
                    }}
                  >
                    {completedSteps.has(index) ? (
                      <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                      </svg>
                    ) : (
                      index + 1
                    )}
                  </div>

                  {/* Step Info */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-1.5 mb-0.5">
                      <div style={{ color: colors.icon }}>
                        {getStepIcon(step.type)}
                      </div>
                      <span className="text-xs font-medium uppercase tracking-wide truncate" style={{ color: colors.text }}>
                        {step.type.replace(/_/g, ' ')}
                      </span>
                    </div>
                    <h4
                      className="text-xs font-medium leading-tight truncate"
                      style={{ color: colors.text }}
                    >
                      {step.title}
                    </h4>
                  </div>
                </div>
              )}
            </button>
          );
        })}
      </div>
    </div>
  );
}
