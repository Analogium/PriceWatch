import { Link } from 'react-router';
import { cn } from '@/utils';

export interface BreadcrumbItem {
  label: string;
  href?: string;
  icon?: string;
}

export interface BreadcrumbProps {
  items: BreadcrumbItem[];
  separator?: string;
  className?: string;
}

export default function Breadcrumb({
  items,
  separator = 'chevron_right',
  className,
}: BreadcrumbProps) {
  return (
    <nav aria-label="Fil d'Ariane" className={cn('flex items-center', className)}>
      <ol className="flex items-center gap-2 flex-wrap">
        {items.map((item, index) => {
          const isLast = index === items.length - 1;

          return (
            <li key={index} className="flex items-center gap-2">
              {item.href && !isLast ? (
                <Link
                  to={item.href}
                  className="inline-flex items-center gap-1.5 text-sm text-gray-600 dark:text-gray-400 hover:text-primary-600 dark:hover:text-primary-400 transition-colors"
                >
                  {item.icon && (
                    <span className="material-symbols-outlined text-base" aria-hidden="true">
                      {item.icon}
                    </span>
                  )}
                  <span>{item.label}</span>
                </Link>
              ) : (
                <span
                  className={cn(
                    'inline-flex items-center gap-1.5 text-sm',
                    isLast
                      ? 'text-gray-900 dark:text-gray-100 font-medium'
                      : 'text-gray-600 dark:text-gray-400'
                  )}
                  aria-current={isLast ? 'page' : undefined}
                >
                  {item.icon && (
                    <span className="material-symbols-outlined text-base" aria-hidden="true">
                      {item.icon}
                    </span>
                  )}
                  <span>{item.label}</span>
                </span>
              )}

              {!isLast && (
                <span
                  className="material-symbols-outlined text-gray-400 dark:text-gray-600 text-base"
                  aria-hidden="true"
                >
                  {separator}
                </span>
              )}
            </li>
          );
        })}
      </ol>
    </nav>
  );
}
