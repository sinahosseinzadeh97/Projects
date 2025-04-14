import { useState } from 'react';
import { Link } from 'wouter';
import { useCart } from '@/lib/cartStore';
import { useAuth } from '@/lib/auth';
import { apiRequest } from '@/lib/queryClient';
import { useToast } from '@/hooks/use-toast';
import { Button } from '@/components/ui/button';

interface ProductCardProps {
  product: {
    id: number;
    name: string;
    slug: string;
    description?: string;
    price: number;
    compareAtPrice?: number | null;
    imageUrl?: string;
    stock: number;
    rating: number;
    reviewCount: number;
    isNew?: boolean;
    isFeatured?: boolean;
  };
}

const ProductCard = ({ product }: ProductCardProps) => {
  const { addToCart } = useCart();
  const { isAuthenticated, user } = useAuth();
  const { toast } = useToast();
  const [isWishlisted, setIsWishlisted] = useState(false);
  
  const handleAddToCart = (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    addToCart(product.id, 1);
  };
  
  const handleAddToWishlist = async (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    
    if (!isAuthenticated) {
      toast({
        title: "Login Required",
        description: "Please login to add items to your wishlist",
        variant: "destructive",
      });
      return;
    }
    
    try {
      if (isWishlisted) {
        await apiRequest('DELETE', `/api/wishlist/${product.id}`);
        setIsWishlisted(false);
        toast({
          title: "Removed from wishlist",
          description: `${product.name} has been removed from your wishlist`,
        });
      } else {
        await apiRequest('POST', '/api/wishlist', { productId: product.id });
        setIsWishlisted(true);
        toast({
          title: "Added to wishlist",
          description: `${product.name} has been added to your wishlist`,
        });
      }
    } catch (error) {
      toast({
        title: "Error",
        description: "Could not update wishlist",
        variant: "destructive",
      });
    }
  };
  
  // Render star rating
  const renderStars = () => {
    const stars = [];
    const rating = Math.round(product.rating * 2) / 2; // Round to nearest 0.5
    
    for (let i = 1; i <= 5; i++) {
      if (i <= rating) {
        stars.push(<i key={i} className="fas fa-star"></i>);
      } else if (i - 0.5 === rating) {
        stars.push(<i key={i} className="fas fa-star-half-alt"></i>);
      } else {
        stars.push(<i key={i} className="far fa-star"></i>);
      }
    }
    
    return stars;
  };
  
  return (
    <div className="bg-white rounded-lg overflow-hidden shadow hover:shadow-md transition duration-300">
      {/* Product Image */}
      <div className="relative">
        <Link href={`/product/${product.slug}`}>
          <img 
            src={product.imageUrl || 'https://via.placeholder.com/400x300?text=No+Image'} 
            alt={product.name} 
            className="w-full h-48 md:h-56 object-cover" 
          />
        </Link>
        <button 
          className={`absolute top-2 right-2 bg-white w-8 h-8 rounded-full flex items-center justify-center ${isWishlisted ? 'text-primary-600' : 'text-gray-400'} hover:text-primary-600 transition duration-200 border border-gray-200`}
          onClick={handleAddToWishlist}
        >
          <i className={isWishlisted ? "fas fa-heart" : "far fa-heart"}></i>
        </button>
        
        {product.isNew && (
          <div className="absolute top-2 left-2 bg-green-500 text-white text-xs px-2 py-1 rounded">New</div>
        )}
        
        {product.compareAtPrice && product.compareAtPrice > product.price && (
          <div className="absolute top-2 left-2 bg-amber-500 text-white text-xs px-2 py-1 rounded">Sale</div>
        )}
      </div>
      
      {/* Product Info */}
      <div className="p-4">
        <Link href={`/product/${product.slug}`}>
          <h3 className="font-medium mb-1 text-sm md:text-base hover:text-primary-600 transition-colors">
            {product.name}
          </h3>
        </Link>
        <p className="text-gray-500 text-xs md:text-sm mb-2 line-clamp-1">{product.description}</p>
        
        <div className="flex items-center mb-2">
          <div className="flex text-amber-500">
            {renderStars()}
          </div>
          <span className="text-xs text-gray-500 ml-1">({product.reviewCount})</span>
        </div>
        
        <div className="flex justify-between items-center">
          <div>
            <span className="font-bold">${product.price.toFixed(2)}</span>
            {product.compareAtPrice && product.compareAtPrice > product.price && (
              <span className="text-gray-500 text-xs line-through ml-1">${product.compareAtPrice.toFixed(2)}</span>
            )}
          </div>
          
          <Button 
            size="sm"
            className="text-xs bg-primary-600 text-white py-1 px-3 rounded-lg hover:bg-primary-700"
            onClick={handleAddToCart}
            disabled={product.stock <= 0}
          >
            {product.stock > 0 ? 'Add to Cart' : 'Out of Stock'}
          </Button>
        </div>
      </div>
    </div>
  );
};

export default ProductCard;
