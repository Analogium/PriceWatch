import { useState, useEffect, useCallback } from 'react';
import { Link } from 'react-router-dom';
import { productsApi } from '@/api/products';
import {
  ProductCard,
  EmptyState,
  LoadingState,
  SearchBar,
  SortSelect,
  Pagination,
} from '@/components/products';
import type { Product, SortBy, SortOrder, PaginatedProducts } from '@/types';
import { useToast } from '@/hooks/useToast';

export default function Dashboard() {
  const { success, error, info } = useToast();
  const [data, setData] = useState<PaginatedProducts | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [sortBy, setSortBy] = useState<SortBy>('created_at');
  const [order, setOrder] = useState<SortOrder>('desc');
  const [page, setPage] = useState(1);

  const fetchProducts = useCallback(async () => {
    try {
      setIsLoading(true);
      const result = await productsApi.getAll({
        page,
        page_size: 12,
        search: search || undefined,
        sort_by: sortBy,
        order,
      });
      setData(result);
    } catch (err: unknown) {
      const message =
        err && typeof err === 'object' && 'response' in err
          ? (err.response as { data?: { detail?: string } })?.data?.detail
          : undefined;
      error(message || 'Erreur lors du chargement des produits');
    } finally {
      setIsLoading(false);
    }
  }, [page, search, sortBy, order, error]);

  useEffect(() => {
    fetchProducts();
  }, [fetchProducts]);

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

  const handleDelete = async (id: number) => {
    if (!confirm('Êtes-vous sûr de vouloir supprimer ce produit ?')) {
      return;
    }

    try {
      await productsApi.delete(id);
      success('Produit supprimé avec succès');
      fetchProducts(); // Refresh list
    } catch (err: unknown) {
      const message =
        err && typeof err === 'object' && 'response' in err
          ? (err.response as { data?: { detail?: string } })?.data?.detail
          : undefined;
      error(message || 'Erreur lors de la suppression du produit');
    }
  };

  const handleCheckPrice = async (id: number) => {
    try {
      info('Vérification du prix en cours...');
      const updatedProduct = await productsApi.checkPrice(id);

      // Update the product in the list
      if (data) {
        setData({
          ...data,
          items: data.items.map((p) => (p.id === id ? updatedProduct : p)),
        });
      }

      success('Prix vérifié avec succès');
    } catch (err: unknown) {
      const message =
        err && typeof err === 'object' && 'response' in err
          ? (err.response as { data?: { detail?: string } })?.data?.detail
          : undefined;
      error(message || 'Erreur lors de la vérification du prix');
    }
  };

  return (
    <div>
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Mes produits suivis</h1>
        <Link
          to="/products/add"
          className="inline-flex items-center gap-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors font-medium"
        >
          <span className="material-symbols-outlined">add</span>
          Ajouter un produit
        </Link>
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
      {isLoading && !data && <LoadingState />}

      {/* Empty State */}
      {!isLoading && data && data.items.length === 0 && (
        <EmptyState hasSearch={!!search} onClearSearch={handleClearSearch} />
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
    </div>
  );
}
