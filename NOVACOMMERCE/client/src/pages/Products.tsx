import { useState, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useLocation } from 'wouter';
import ProductCard from '@/components/ui/ProductCard';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Slider } from "@/components/ui/slider";
import { Checkbox } from "@/components/ui/checkbox";
import { Label } from "@/components/ui/label";

const Products = () => {
  const [location] = useLocation();
  const [searchParams, setSearchParams] = useState(new URLSearchParams(window.location.search));
  const [, navigate] = useLocation();
  
  // State for filters
  const [categoryId, setCategoryId] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [priceRange, setPriceRange] = useState([0, 1000]);
  const [sortBy, setSortBy] = useState('');
  const [inStock, setInStock] = useState(false);
  const [onSale, setOnSale] = useState(false);
  const [featured, setFeatured] = useState(false);
  const [newArrival, setNewArrival] = useState(false);

  // Extract category ID from URL if it exists
  useEffect(() => {
    const path = location.split('/');
    if (path[1] === 'products' && path[2] === 'category' && path[3]) {
      const id = path[3];
      console.log(`Setting categoryId to ${id} from URL path: ${location}`);
      setCategoryId(id);
    } else {
      setCategoryId(null);
    }

    // Parse query parameters
    const params = new URLSearchParams(window.location.search);
    setSearchQuery(params.get('search') || '');
    setSortBy(params.get('sort') || '');
    setFeatured(params.get('featured') === 'true');
    setNewArrival(params.get('new') === 'true');
    setOnSale(params.get('sale') === 'true');
    setInStock(params.get('inStock') === 'true');
    
    const minPrice = params.get('minPrice');
    const maxPrice = params.get('maxPrice');
    if (minPrice && maxPrice) {
      setPriceRange([parseInt(minPrice), parseInt(maxPrice)]);
    }
    
    setSearchParams(params);
  }, [location]);

  // Fetch all products (we'll filter client-side for this demo)
  const { data: products, isLoading, isError, error } = useQuery({
    queryKey: categoryId 
      ? [`/api/categories/${categoryId}/products`]
      : ['/api/products'],
  });

  // Log query status
  useEffect(() => {
    console.log("Query status:", { isLoading, isError, categoryId, error });
  }, [isLoading, isError, categoryId, error]);

  // Debug products data
  useEffect(() => {
    if (products) {
      console.log("Loaded products:", products);
      // Print out all unique categoryIds
      const uniqueCategories = [...new Set(products.map((p: any) => p.categoryId))];
      console.log("Available category IDs in products:", uniqueCategories);
    }
  }, [products]);

  // Fetch categories for filter
  const { data: categories } = useQuery({
    queryKey: ['/api/categories'],
  });

  // Debug categories data
  useEffect(() => {
    if (categories) {
      console.log("Loaded categories:", categories);
    }
  }, [categories]);

  // Apply filters
  const filteredProducts = products?.filter((product: any) => {
    console.log('Filtering product:', product);
    
    // Skip category filter when we're already fetching by category
    if (categoryId && !location.includes(`/products/category/${categoryId}`)) {
      const categoryIdNum = parseInt(categoryId);
      const productCategoryId = product.categoryId;
      console.log(`Comparing category IDs: ${categoryIdNum} (filter) vs ${productCategoryId} (product)`);
      if (categoryIdNum !== productCategoryId) {
        return false;
      }
    }
    
    // Search query
    if (searchQuery && !product.name.toLowerCase().includes(searchQuery.toLowerCase()) && 
        !product.description?.toLowerCase().includes(searchQuery.toLowerCase())) {
      return false;
    }
    
    // Price range
    if (product.price < priceRange[0] || product.price > priceRange[1]) {
      return false;
    }
    
    // In stock
    if (inStock && product.stock <= 0) {
      return false;
    }
    
    // On sale
    if (onSale && (!product.compareAtPrice || product.compareAtPrice <= product.price)) {
      return false;
    }
    
    // Featured
    if (featured && !product.isFeatured) {
      return false;
    }
    
    // New arrival
    if (newArrival && !product.isNew) {
      return false;
    }
    
    return true;
  });

  // Sort products
  const sortedProducts = [...(filteredProducts || [])].sort((a, b) => {
    switch (sortBy) {
      case 'price_asc':
        return a.price - b.price;
      case 'price_desc':
        return b.price - a.price;
      case 'name_asc':
        return a.name.localeCompare(b.name);
      case 'name_desc':
        return b.name.localeCompare(a.name);
      case 'rating_desc':
        return b.rating - a.rating;
      default:
        return 0;
    }
  });

  // Apply filters and update URL
  const applyFilters = () => {
    const params = new URLSearchParams();
    
    if (searchQuery) params.set('search', searchQuery);
    if (sortBy) params.set('sort', sortBy);
    if (inStock) params.set('inStock', 'true');
    if (onSale) params.set('sale', 'true');
    if (featured) params.set('featured', 'true');
    if (newArrival) params.set('new', 'true');
    if (priceRange[0] > 0) params.set('minPrice', priceRange[0].toString());
    if (priceRange[1] < 1000) params.set('maxPrice', priceRange[1].toString());
    
    const path = categoryId ? `/products/category/${categoryId}` : '/products';
    navigate(`${path}?${params.toString()}`);
  };

  // Reset filters
  const resetFilters = () => {
    setSearchQuery('');
    setPriceRange([0, 1000]);
    setSortBy('');
    setInStock(false);
    setOnSale(false);
    setFeatured(false);
    setNewArrival(false);
    
    const path = categoryId ? `/products/category/${categoryId}` : '/products';
    navigate(path);
  };

  // Get category name
  const categoryName = categoryId && categories 
    ? categories.find((c: any) => c.id === parseInt(categoryId))?.name 
    : null;

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-2xl md:text-3xl font-bold mb-6">
        {categoryName ? `${categoryName} Products` : 'All Products'}
      </h1>
      
      <div className="flex flex-col md:flex-row gap-6">
        {/* Filters - Sidebar */}
        <div className="md:w-1/4">
          <Card>
            <CardHeader>
              <CardTitle>Filters</CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* Search */}
              <div>
                <Label htmlFor="search">Search</Label>
                <div className="relative mt-1">
                  <Input
                    id="search"
                    type="text"
                    placeholder="Search products..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                  />
                </div>
              </div>
              
              {/* Categories */}
              <div>
                <Label>Category</Label>
                <Select 
                  value={categoryId || 'all'} 
                  onValueChange={(value) => setCategoryId(value === 'all' ? null : value)}
                >
                  <SelectTrigger className="mt-1">
                    <SelectValue placeholder="All Categories" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Categories</SelectItem>
                    {categories?.map((category: any) => (
                      <SelectItem key={category.id} value={category.id.toString()}>
                        {category.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              
              {/* Price Range */}
              <div>
                <Label>Price Range: ${priceRange[0]} - ${priceRange[1]}</Label>
                <Slider
                  className="mt-2"
                  defaultValue={[0, 1000]}
                  min={0}
                  max={1000}
                  step={10}
                  value={priceRange}
                  onValueChange={setPriceRange}
                />
              </div>
              
              {/* Checkboxes */}
              <div className="space-y-3">
                <div className="flex items-center space-x-2">
                  <Checkbox 
                    id="inStock" 
                    checked={inStock} 
                    onCheckedChange={(checked) => setInStock(checked as boolean)} 
                  />
                  <Label htmlFor="inStock">In Stock</Label>
                </div>
                
                <div className="flex items-center space-x-2">
                  <Checkbox 
                    id="onSale" 
                    checked={onSale} 
                    onCheckedChange={(checked) => setOnSale(checked as boolean)} 
                  />
                  <Label htmlFor="onSale">On Sale</Label>
                </div>
                
                <div className="flex items-center space-x-2">
                  <Checkbox 
                    id="featured" 
                    checked={featured} 
                    onCheckedChange={(checked) => setFeatured(checked as boolean)} 
                  />
                  <Label htmlFor="featured">Featured</Label>
                </div>
                
                <div className="flex items-center space-x-2">
                  <Checkbox 
                    id="newArrival" 
                    checked={newArrival} 
                    onCheckedChange={(checked) => setNewArrival(checked as boolean)} 
                  />
                  <Label htmlFor="newArrival">New Arrivals</Label>
                </div>
              </div>
              
              <div className="pt-4 space-y-2">
                <Button onClick={applyFilters} className="w-full">Apply Filters</Button>
                <Button variant="outline" onClick={resetFilters} className="w-full">Reset Filters</Button>
              </div>
            </CardContent>
          </Card>
        </div>
        
        {/* Product Grid */}
        <div className="md:w-3/4">
          <div className="mb-6 flex justify-between items-center">
            <p className="text-gray-500">
              {sortedProducts ? `Showing ${sortedProducts.length} products` : 'Loading products...'}
            </p>
            
            <div className="flex items-center">
              <label className="mr-2 text-sm text-gray-600">Sort By:</label>
              <Select value={sortBy || 'default'} onValueChange={(value) => setSortBy(value === 'default' ? '' : value)}>
                <SelectTrigger className="w-[180px]">
                  <SelectValue placeholder="Default" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="default">Default</SelectItem>
                  <SelectItem value="price_asc">Price: Low to High</SelectItem>
                  <SelectItem value="price_desc">Price: High to Low</SelectItem>
                  <SelectItem value="name_asc">Name: A to Z</SelectItem>
                  <SelectItem value="name_desc">Name: Z to A</SelectItem>
                  <SelectItem value="rating_desc">Highest Rated</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
          
          {isLoading ? (
            <div className="flex justify-center items-center h-64">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
            </div>
          ) : sortedProducts?.length ? (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 md:gap-6">
              {sortedProducts.map(product => (
                <ProductCard key={product.id} product={product} />
              ))}
            </div>
          ) : (
            <div className="text-center py-12 bg-gray-50 rounded-lg">
              <h3 className="text-lg font-medium mb-2">No Products Found</h3>
              <p className="text-gray-500">Try changing your filter criteria</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Products;
