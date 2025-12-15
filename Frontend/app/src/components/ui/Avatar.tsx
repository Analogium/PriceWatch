import { useState } from 'react';
import { cn } from '@/utils';

export interface AvatarProps {
  src?: string | null;
  alt?: string;
  fallback?: string;
  size?: 'xs' | 'sm' | 'md' | 'lg' | 'xl' | '2xl';
  variant?: 'circle' | 'square';
  className?: string;
}

const sizeClasses = {
  xs: 'h-6 w-6 text-xs',
  sm: 'h-8 w-8 text-sm',
  md: 'h-10 w-10 text-base',
  lg: 'h-12 w-12 text-lg',
  xl: 'h-16 w-16 text-xl',
  '2xl': 'h-24 w-24 text-3xl',
};

const variantClasses = {
  circle: 'rounded-full',
  square: 'rounded-lg',
};

export default function Avatar({
  src,
  alt = 'Avatar',
  fallback,
  size = 'md',
  variant = 'circle',
  className,
}: AvatarProps) {
  const [imageError, setImageError] = useState(false);

  const shouldShowImage = src && !imageError;
  const shouldShowFallback = !shouldShowImage && fallback;

  return (
    <div
      className={cn(
        'inline-flex items-center justify-center overflow-hidden bg-primary-100 dark:bg-primary-900/50 text-primary-700 dark:text-primary-300 font-medium select-none',
        sizeClasses[size],
        variantClasses[variant],
        className
      )}
      aria-label={alt}
    >
      {shouldShowImage ? (
        <img
          src={src}
          alt={alt}
          className="h-full w-full object-cover"
          onError={() => setImageError(true)}
        />
      ) : shouldShowFallback ? (
        <span className="uppercase">{fallback}</span>
      ) : (
        <span className="material-symbols-outlined" aria-hidden="true">
          person
        </span>
      )}
    </div>
  );
}
