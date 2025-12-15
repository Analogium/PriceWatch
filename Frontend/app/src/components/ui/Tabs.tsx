import { useState, useRef, ReactNode } from 'react';
import { cn } from '@/utils';

export interface TabItem {
  id: string;
  label: string;
  icon?: string;
  content: ReactNode;
  disabled?: boolean;
}

export interface TabsProps {
  items: TabItem[];
  defaultTab?: string;
  onChange?: (tabId: string) => void;
  variant?: 'underline' | 'pills';
  className?: string;
}

export default function Tabs({
  items,
  defaultTab,
  onChange,
  variant = 'underline',
  className,
}: TabsProps) {
  const [activeTab, setActiveTab] = useState(defaultTab || items[0]?.id);
  const tabRefs = useRef<Map<string, HTMLButtonElement>>(new Map());

  const handleTabChange = (tabId: string) => {
    const tab = items.find((t) => t.id === tabId);
    if (tab?.disabled) return;

    setActiveTab(tabId);
    onChange?.(tabId);
  };

  const handleKeyDown = (e: React.KeyboardEvent, currentIndex: number) => {
    let nextIndex = currentIndex;

    switch (e.key) {
      case 'ArrowLeft':
        e.preventDefault();
        nextIndex = currentIndex - 1;
        if (nextIndex < 0) nextIndex = items.length - 1;
        break;
      case 'ArrowRight':
        e.preventDefault();
        nextIndex = currentIndex + 1;
        if (nextIndex >= items.length) nextIndex = 0;
        break;
      case 'Home':
        e.preventDefault();
        nextIndex = 0;
        break;
      case 'End':
        e.preventDefault();
        nextIndex = items.length - 1;
        break;
      default:
        return;
    }

    // Skip disabled tabs
    while (items[nextIndex]?.disabled && nextIndex !== currentIndex) {
      if (e.key === 'ArrowLeft' || e.key === 'End') {
        nextIndex = nextIndex - 1;
        if (nextIndex < 0) nextIndex = items.length - 1;
      } else {
        nextIndex = nextIndex + 1;
        if (nextIndex >= items.length) nextIndex = 0;
      }
    }

    const nextTab = items[nextIndex];
    if (nextTab && !nextTab.disabled) {
      handleTabChange(nextTab.id);
      tabRefs.current.get(nextTab.id)?.focus();
    }
  };

  const activeContent = items.find((item) => item.id === activeTab)?.content;

  return (
    <div className={cn('w-full', className)}>
      <div
        className={cn(
          'flex items-center gap-1',
          variant === 'underline' && 'border-b border-gray-200 dark:border-gray-800'
        )}
        role="tablist"
        aria-label="Onglets"
      >
        {items.map((item, index) => {
          const isActive = activeTab === item.id;

          return (
            <button
              key={item.id}
              ref={(el) => {
                if (el) tabRefs.current.set(item.id, el);
                else tabRefs.current.delete(item.id);
              }}
              role="tab"
              aria-selected={isActive}
              aria-controls={`tabpanel-${item.id}`}
              id={`tab-${item.id}`}
              tabIndex={isActive ? 0 : -1}
              disabled={item.disabled}
              onClick={() => handleTabChange(item.id)}
              onKeyDown={(e) => handleKeyDown(e, index)}
              className={cn(
                'inline-flex items-center gap-2 px-4 py-2.5 text-sm font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-primary-600 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed',
                variant === 'underline' &&
                  cn(
                    'border-b-2 -mb-px',
                    isActive
                      ? 'border-primary-600 text-primary-600 dark:text-primary-400'
                      : 'border-transparent text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-100 hover:border-gray-300 dark:hover:border-gray-700'
                  ),
                variant === 'pills' &&
                  cn(
                    'rounded-lg',
                    isActive
                      ? 'bg-primary-600 text-white'
                      : 'text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800 hover:text-gray-900 dark:hover:text-gray-100'
                  )
              )}
            >
              {item.icon && (
                <span className="material-symbols-outlined text-base" aria-hidden="true">
                  {item.icon}
                </span>
              )}
              <span>{item.label}</span>
            </button>
          );
        })}
      </div>

      <div className="mt-4">
        {items.map((item) => (
          <div
            key={item.id}
            id={`tabpanel-${item.id}`}
            role="tabpanel"
            aria-labelledby={`tab-${item.id}`}
            hidden={activeTab !== item.id}
            tabIndex={0}
          >
            {activeTab === item.id && activeContent}
          </div>
        ))}
      </div>
    </div>
  );
}
