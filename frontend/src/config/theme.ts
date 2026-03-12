/**
 * Theme Configuration
 *
 * Central configuration for theme management.
 * Use this to programmatically switch between themes at runtime.
 */

export type Theme = 'default' | 'dark';

export const THEMES: Record<Theme, { name: string; cssFile: string }> = {
  default: {
    name: 'Default',
    cssFile: '/src/styles/themes/default.css',
  },
  dark: {
    name: 'Dark',
    cssFile: '/src/styles/themes/dark.css',
  },
};

export const DEFAULT_THEME: Theme = 'default';

/**
 * Load a theme by importing its CSS file
 */
export async function loadTheme(theme: Theme): Promise<void> {
  const themeConfig = THEMES[theme];
  if (!themeConfig) {
    console.error(`Theme "${theme}" not found`);
    return;
  }

  // In a real implementation, you would dynamically load the CSS file
  // For now, we'll rely on the @import in index.css
  // But this function can be used to switch themes at runtime
  console.log(`Loading theme: ${themeConfig.name}`);
}

/**
 * Get the current theme from localStorage
 */
export function getCurrentTheme(): Theme {
  const stored = localStorage.getItem('theme');
  return (stored as Theme) || DEFAULT_THEME;
}

/**
 * Save the current theme to localStorage
 */
export function saveTheme(theme: Theme): void {
  localStorage.setItem('theme', theme);
}
