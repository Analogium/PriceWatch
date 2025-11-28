import type { PaginationMetadata } from '@/types';

interface PaginationProps {
  metadata: PaginationMetadata;
  onPageChange: (page: number) => void;
}

export function Pagination({ metadata, onPageChange }: PaginationProps) {
  const { page, total_pages, has_next, has_previous } = metadata;

  // Générer les numéros de page à afficher
  const getPageNumbers = () => {
    const pages: (number | string)[] = [];
    const maxVisible = 7; // Nombre maximum de pages visibles

    if (total_pages <= maxVisible) {
      // Afficher toutes les pages si peu nombreuses
      for (let i = 1; i <= total_pages; i++) {
        pages.push(i);
      }
    } else {
      // Toujours afficher la première page
      pages.push(1);

      if (page > 3) {
        pages.push('...');
      }

      // Afficher les pages autour de la page actuelle
      const start = Math.max(2, page - 1);
      const end = Math.min(total_pages - 1, page + 1);

      for (let i = start; i <= end; i++) {
        pages.push(i);
      }

      if (page < total_pages - 2) {
        pages.push('...');
      }

      // Toujours afficher la dernière page
      pages.push(total_pages);
    }

    return pages;
  };

  if (total_pages <= 1) {
    return null;
  }

  return (
    <div className="flex items-center justify-between border-t border-gray-200 pt-4">
      {/* Info */}
      <div className="text-sm text-gray-700">
        Page <span className="font-medium">{page}</span> sur{' '}
        <span className="font-medium">{total_pages}</span>
      </div>

      {/* Navigation */}
      <div className="flex items-center gap-1">
        {/* Bouton Précédent */}
        <button
          onClick={() => onPageChange(page - 1)}
          disabled={!has_previous}
          className="px-3 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:bg-white transition-colors"
        >
          <span className="material-symbols-outlined text-gray-700">chevron_left</span>
        </button>

        {/* Numéros de page */}
        <div className="hidden sm:flex gap-1">
          {getPageNumbers().map((pageNum, index) => {
            if (pageNum === '...') {
              return (
                <span key={`ellipsis-${index}`} className="px-3 py-2 text-gray-700">
                  ...
                </span>
              );
            }

            const isActive = pageNum === page;
            return (
              <button
                key={pageNum}
                onClick={() => onPageChange(pageNum as number)}
                className={`px-3 py-2 rounded-lg transition-colors ${
                  isActive
                    ? 'bg-primary-600 text-white font-medium'
                    : 'border border-gray-300 text-gray-700 hover:bg-gray-50'
                }`}
              >
                {pageNum}
              </button>
            );
          })}
        </div>

        {/* Bouton Suivant */}
        <button
          onClick={() => onPageChange(page + 1)}
          disabled={!has_next}
          className="px-3 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:bg-white transition-colors"
        >
          <span className="material-symbols-outlined text-gray-700">chevron_right</span>
        </button>
      </div>
    </div>
  );
}
