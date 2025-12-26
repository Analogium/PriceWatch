import { useState, useCallback, useMemo } from 'react';
import {
  ProductCard,
  EmptyState,
  LoadingState,
  SearchBar,
  SortSelect,
  Pagination,
} from '@/components/products';
import { Button, Modal, Alert, LinkButton } from '@/components/ui';
import type { Product, SortBy, SortOrder } from '@/types';
import { useToast } from '@/contexts/ToastContext';
import { usePriceCheck } from '@/contexts/PriceCheckContext';
import { useProducts, useDeleteProduct, useCheckPrice } from '@/hooks/useProducts';

export default function Dashboard() {
  const { success, error, info } = useToast();
  const { startChecking, finishChecking } = usePriceCheck();
  const [search, setSearch] = useState('');
  const [sortBy, setSortBy] = useState<SortBy>('created_at');
  const [order, setOrder] = useState<SortOrder>('desc');
  const [page, setPage] = useState(1);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [productToDelete, setProductToDelete] = useState<Product | null>(null);

  // Memoize filters to prevent unnecessary re-fetches
  const filters = useMemo(
    () => ({
      page,
      page_size: 12,
      search: search || undefined,
      sort_by: sortBy,
      order,
    }),
    [page, search, sortBy, order]
  );

  // Use React Query hooks
  const { data, isLoading, error: queryError } = useProducts(filters);
  const deleteMutation = useDeleteProduct();
  const checkPriceMutation = useCheckPrice();

  // Show error toast if query fails
  if (queryError) {
    const message =
      queryError && typeof queryError === 'object' && 'response' in queryError
        ? (queryError.response as { data?: { detail?: string } })?.data?.detail
        : undefined;
    error(message || 'Erreur lors du chargement des produits');
  }

  const handleSearchChange = (value: string) => {
    setSearch(value);
    setPage(1); // Reset to first page on search
  };

  const handleSortChange = (newSortBy: SortBy, newOrder: SortOrder) => {
    setSortBy(newSortBy);
    setOrder(newOrder);
    setPage(1); // Reset to first page on sort change
  };

  const handlePageChange = (newPage: number) => {
    setPage(newPage);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleClearSearch = () => {
    setSearch('');
    setPage(1);
  };

  const handleDelete = useCallback(
    (id: number) => {
      // Find the product to delete
      const product = data?.items.find((p) => p.id === id);
      if (!product) return;

      // Show delete confirmation modal
      setProductToDelete(product);
      setShowDeleteModal(true);
    },
    [data]
  );

  const confirmDelete = useCallback(async () => {
    if (!productToDelete) return;

    try {
      // Close modal immediately for better UX
      setShowDeleteModal(false);
      const productId = productToDelete.id;
      setProductToDelete(null);

      // Perform delete with React Query mutation
      await deleteMutation.mutateAsync(productId);
      success('Produit supprimé avec succès');
    } catch (err: unknown) {
      const message =
        err && typeof err === 'object' && 'response' in err
          ? (err.response as { data?: { detail?: string } })?.data?.detail
          : undefined;
      error(message || 'Erreur lors de la suppression du produit');
    }
  }, [productToDelete, deleteMutation, success, error]);

  const cancelDelete = useCallback(() => {
    setShowDeleteModal(false);
    setProductToDelete(null);
  }, []);

  const handleCheckPrice = useCallback(
    async (id: number) => {
      // Find the product to get its full data
      const product = data?.items.find((p) => p.id === id);
      if (!product) return;

      // Start checking and show info toast
      startChecking(product);
      info('Vérification du prix en cours...', undefined, 10000);

      try {
        await checkPriceMutation.mutateAsync(id);
        success('Prix vérifié avec succès');
      } catch (err: unknown) {
        const message =
          err && typeof err === 'object' && 'response' in err
            ? (err.response as { data?: { detail?: string } })?.data?.detail
            : undefined;
        error(message || 'Erreur lors de la vérification du prix');
      } finally {
        finishChecking(id);
      }
    },
    [data, startChecking, finishChecking, checkPriceMutation, success, error, info]
  );

  return (
    <div>
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Mes produits suivis</h1>
        <LinkButton
          to="/products/add"
          variant="primary"
          leftIcon={<span className="material-symbols-outlined">add</span>}
        >
          Ajouter un produit
        </LinkButton>
      </div>

      {/* Filters */}
      {(!isLoading || data) && data && data.metadata.total_items > 0 && (
        <div className="mb-6 flex flex-col sm:flex-row gap-4">
          <div className="flex-1">
            <SearchBar value={search} onChange={handleSearchChange} />
          </div>
          <div>
            <SortSelect sortBy={sortBy} order={order} onSortChange={handleSortChange} />
          </div>
        </div>
      )}

      {/* Loading State */}
      {isLoading && <LoadingState />}

      {/* Empty State */}
      {!isLoading && data && data.items.length === 0 && (
        <>
          {!search && (
            <Alert variant="info" title="Aucun produit suivi" className="mb-6">
              Vous ne suivez aucun produit pour le moment. Commencez par ajouter un produit à
              surveiller en cliquant sur le bouton ci-dessus.
            </Alert>
          )}
          <EmptyState hasSearch={!!search} onClearSearch={handleClearSearch} />
        </>
      )}

      {/* Products Grid */}
      {!isLoading && data && data.items.length > 0 && (
        <>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-6">
            {data.items.map((product: Product) => (
              <ProductCard
                key={product.id}
                product={product}
                onDelete={handleDelete}
                onCheckPrice={handleCheckPrice}
              />
            ))}
          </div>

          {/* Pagination */}
          <Pagination metadata={data.metadata} onPageChange={handlePageChange} />
        </>
      )}

      {/* Delete confirmation modal */}
      <Modal
        isOpen={showDeleteModal}
        onClose={cancelDelete}
        title="Confirmer la suppression"
        size="sm"
      >
        <div className="space-y-4">
          <p className="text-gray-700">
            Êtes-vous sûr de vouloir supprimer ce produit ? Cette action est irréversible.
          </p>

          {productToDelete && (
            <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
              <p className="text-sm font-medium text-gray-900 mb-1">Produit à supprimer :</p>
              <p className="text-sm text-gray-600 line-clamp-2">{productToDelete.name}</p>
            </div>
          )}

          <div className="flex gap-3 justify-end">
            <Button variant="secondary" onClick={cancelDelete} disabled={deleteMutation.isPending}>
              Annuler
            </Button>
            <Button
              variant="danger"
              onClick={confirmDelete}
              isLoading={deleteMutation.isPending}
              leftIcon={<span className="material-symbols-outlined">delete</span>}
            >
              Supprimer
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  );
}
