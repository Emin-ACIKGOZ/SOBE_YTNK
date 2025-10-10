'use client';

import { useContext } from 'react';
import { AppContext } from '@/context/app-context';

export function useApp() {
  const context = useContext(AppContext);
  if (context === undefined) {
    throw new Error('useApp, bir AppProvider içinde kullanılmalıdır.');
  }
  return context;
}
