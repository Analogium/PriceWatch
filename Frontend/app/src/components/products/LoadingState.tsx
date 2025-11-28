export function LoadingState() {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {[1, 2, 3, 4, 5, 6].map((i) => (
        <div
          key={i}
          className="bg-white rounded-lg border border-gray-200 overflow-hidden animate-pulse"
        >
          {/* Image skeleton */}
          <div className="aspect-square bg-gray-200" />

          {/* Content skeleton */}
          <div className="p-4">
            {/* Title */}
            <div className="h-4 bg-gray-200 rounded mb-2" />
            <div className="h-4 bg-gray-200 rounded w-3/4 mb-4" />

            {/* Prices */}
            <div className="space-y-2 mb-4">
              <div className="flex justify-between">
                <div className="h-3 bg-gray-200 rounded w-20" />
                <div className="h-6 bg-gray-200 rounded w-24" />
              </div>
              <div className="flex justify-between">
                <div className="h-3 bg-gray-200 rounded w-20" />
                <div className="h-5 bg-gray-200 rounded w-20" />
              </div>
            </div>

            {/* Info */}
            <div className="space-y-1 mb-4">
              <div className="h-3 bg-gray-200 rounded w-32" />
              <div className="h-3 bg-gray-200 rounded w-40" />
            </div>

            {/* Actions */}
            <div className="flex gap-2">
              <div className="flex-1 h-10 bg-gray-200 rounded-lg" />
              <div className="w-10 h-10 bg-gray-200 rounded-lg" />
              <div className="w-10 h-10 bg-gray-200 rounded-lg" />
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
