export interface Product {
  id: number;
  user_id: number;
  name: string;
  url: string;
  image: string | null;
  current_price: number;
  target_price: number;
  last_checked: string;
  created_at: string;
  is_available: boolean;
  unavailable_since: string | null;
  check_frequency: 6 | 12 | 24;
}

export interface ProductCreate {
  url: string;
  target_price: number;
  check_frequency?: 6 | 12 | 24;
}

export interface ProductUpdate {
  name?: string;
  target_price?: number;
  check_frequency?: 6 | 12 | 24;
}

export interface PaginationMetadata {
  page: number;
  page_size: number;
  total_items: number;
  total_pages: number;
  has_next: boolean;
  has_previous: boolean;
}

export interface PaginatedProducts {
  items: Product[];
  metadata: PaginationMetadata;
}

// Price history interface for tracking product price changes over time
export interface PriceHistory {
  id: number;
  product_id: number;
  price: number;
  recorded_at: string;
}

// Price statistics interface for displaying aggregated price data
export interface PriceStats {
  current_price: number;
  lowest_price: number;
  highest_price: number;
  average_price: number;
  price_change_percentage: number | null;
  total_records: number;
}

export type SortBy = 'name' | 'current_price' | 'target_price' | 'created_at' | 'last_checked';
export type SortOrder = 'asc' | 'desc';

export interface ProductFilters {
  page?: number;
  page_size?: number;
  search?: string;
  sort_by?: SortBy;
  order?: SortOrder;
}
