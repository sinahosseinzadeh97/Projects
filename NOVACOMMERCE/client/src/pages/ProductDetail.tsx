import { useState, useEffect } from 'react';
import { useParams, Link } from 'wouter';
import { useQuery } from '@tanstack/react-query';
import { useCart } from '@/lib/cartStore';
import { useAuth } from '@/lib/auth';
import { apiRequest } from '@/lib/queryClient';
import { useToast } from '@/hooks/use-toast';
import ProductCard from '@/components/ui/ProductCard';
import {
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from "@/components/ui/tabs";
import { Button } from '@/components/ui/button';

const ProductDetail = () => {
  const { slug } = useParams();
  const { addToCart } = useCart();
  const { isAuthenticated } = useAuth();
  const { toast } = useToast();
  const [quantity, setQuantity] = useState(1);
  const [isWishlisted, setIsWishlisted] = useState(false);
  const [activeImage, setActiveImage] = useState(0);

  // Fetch product details
  const { data: product, isLoading } = useQuery({
    queryKey: [`/api/products/slug/${slug}`],
  });

  // Fetch related products based on category
  const { data: relatedProducts } = useQuery({
    queryKey: ['/api/products'],
    enabled: !!product,
    select: (data) => data.filter(p => 
      p.categoryId === product.categoryId && p.id !== product.id
    ).slice(0, 4),
  });

  // Fetch product reviews
  const { data: reviews } = useQuery({
    queryKey: [`/api/products/${product?.id}/reviews`],
    enabled: !!product?.id,
  });

  // Check if user has product in wishlist
  useEffect(() => {
    if (isAuthenticated && product) {
      const checkWishlist = async () => {
        try {
          const response = await apiRequest('GET', '/api/wishlist');
          const wishlist = await response.json();
          const isInWishlist = wishlist.some((item: any) => item.productId === product.id);
          setIsWishlisted(isInWishlist);
        } catch (error) {
          console.error('Error checking wishlist:', error);
        }
      };
      
      checkWishlist();
    }
  }, [isAuthenticated, product]);

  const handleAddToCart = () => {
    if (product) {
      addToCart(product.id, quantity);
    }
  };

  const handleAddToWishlist = async () => {
    if (!product) return;
    
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

  // Generate product image array (using main image and placeholders)
  const productImages = product 
    ? [
        product.imageUrl || 'https://via.placeholder.com/600x600?text=No+Image',
        'https://via.placeholder.com/600x600?text=Product+View+2',
        'https://via.placeholder.com/600x600?text=Product+View+3',
        'https://via.placeholder.com/600x600?text=Product+View+4'
      ]
    : [];

  if (isLoading) {
    return (
      <div className="container mx-auto px-4 py-10">
        <div className="flex justify-center items-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
        </div>
      </div>
    );
  }

  if (!product) {
    return (
      <div className="container mx-auto px-4 py-10">
        <div className="text-center py-12 bg-gray-50 rounded-lg">
          <h2 className="text-2xl font-bold mb-2">Product Not Found</h2>
          <p className="text-gray-500 mb-6">The product you're looking for doesn't exist or has been removed.</p>
          <Button asChild>
            <Link href="/products">Browse Products</Link>
          </Button>
        </div>
      </div>
    );
  }

  // Render star rating
  const renderStars = (rating: number) => {
    const stars = [];
    const roundedRating = Math.round(rating * 2) / 2; // Round to nearest 0.5
    
    for (let i = 1; i <= 5; i++) {
      if (i <= roundedRating) {
        stars.push(<i key={i} className="fas fa-star"></i>);
      } else if (i - 0.5 === roundedRating) {
        stars.push(<i key={i} className="fas fa-star-half-alt"></i>);
      } else {
        stars.push(<i key={i} className="far fa-star"></i>);
      }
    }
    
    return stars;
  };

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Breadcrumb */}
      <div className="mb-6 text-sm text-gray-500">
        <Link href="/" className="hover:text-primary-600">Home</Link> / 
        <Link href="/products" className="mx-2 hover:text-primary-600">Products</Link> / 
        <Link href={`/products/category/${product.categoryId}`} className="mx-2 hover:text-primary-600">
          {product.category.name}
        </Link> / 
        <span className="ml-2 text-gray-700">{product.name}</span>
      </div>
      
      {/* Product info */}
      <div className="flex flex-col md:flex-row -mx-4">
        {/* Product images */}
        <div className="md:w-1/2 px-4 mb-6 md:mb-0">
          <div className="relative mb-4 bg-gray-100 rounded-lg overflow-hidden">
            <img 
              src={productImages[activeImage]} 
              alt={product.name}
              className="w-full h-auto object-contain aspect-square"
            />
            {product.isNew && (
              <div className="absolute top-4 left-4 bg-green-500 text-white text-xs px-2 py-1 rounded">New</div>
            )}
            {product.compareAtPrice && product.compareAtPrice > product.price && (
              <div className="absolute top-4 left-4 bg-amber-500 text-white text-xs px-2 py-1 rounded">Sale</div>
            )}
          </div>
          
          {/* Thumbnail images */}
          <div className="grid grid-cols-4 gap-2">
            {productImages.map((img, index) => (
              <button 
                key={index}
                className={`border rounded-md overflow-hidden ${activeImage === index ? 'border-primary-500 ring-2 ring-primary-200' : 'border-gray-200'}`}
                onClick={() => setActiveImage(index)}
              >
                <img src={img} alt={`${product.name} thumbnail ${index + 1}`} className="w-full h-auto aspect-square object-cover" />
              </button>
            ))}
          </div>
        </div>
        
        {/* Product details */}
        <div className="md:w-1/2 px-4">
          <h1 className="text-2xl md:text-3xl font-bold mb-2">{product.name}</h1>
          
          <div className="flex items-center mb-4">
            <div className="flex text-amber-500 mr-2">
              {renderStars(product.rating)}
            </div>
            <span className="text-gray-500 text-sm">({product.reviewCount} reviews)</span>
          </div>
          
          <div className="mb-6">
            <div className="flex items-center">
              <span className="text-2xl font-bold">${product.price.toFixed(2)}</span>
              {product.compareAtPrice && product.compareAtPrice > product.price && (
                <>
                  <span className="text-gray-500 text-lg line-through ml-2">${product.compareAtPrice.toFixed(2)}</span>
                  <span className="ml-2 bg-amber-100 text-amber-800 text-xs font-medium px-2 py-0.5 rounded">
                    {Math.round((1 - product.price / product.compareAtPrice) * 100)}% OFF
                  </span>
                </>
              )}
            </div>
            
            <p className={`mt-1 ${product.stock > 0 ? 'text-green-600' : 'text-red-600'}`}>
              {product.stock > 0 ? (
                <>{product.stock > 10 ? 'In Stock' : `Only ${product.stock} left`} <i className="fas fa-check-circle"></i></>
              ) : (
                <>Out of Stock <i className="fas fa-times-circle"></i></>
              )}
            </p>
          </div>
          
          <div className="mb-6">
            <p className="text-gray-700">{product.description}</p>
          </div>
          
          {product.stock > 0 && (
            <div className="mb-6">
              <div className="flex items-center mb-4">
                <label htmlFor="quantity" className="mr-4 font-medium">Quantity:</label>
                <div className="flex items-center border border-gray-300 rounded-md">
                  <button 
                    className="px-3 py-1 text-gray-600 hover:bg-gray-100"
                    onClick={() => setQuantity(prev => Math.max(1, prev - 1))}
                  >
                    <i className="fas fa-minus"></i>
                  </button>
                  <input 
                    type="number" 
                    id="quantity"
                    className="w-12 border-0 text-center" 
                    value={quantity} 
                    min="1" 
                    max={product.stock}
                    onChange={(e) => setQuantity(parseInt(e.target.value) || 1)}
                  />
                  <button 
                    className="px-3 py-1 text-gray-600 hover:bg-gray-100"
                    onClick={() => setQuantity(prev => Math.min(product.stock, prev + 1))}
                  >
                    <i className="fas fa-plus"></i>
                  </button>
                </div>
              </div>
              
              <div className="flex flex-col sm:flex-row gap-2">
                <Button 
                  onClick={handleAddToCart}
                  className="flex-1 py-3" size="lg"
                >
                  <i className="fas fa-shopping-cart mr-2"></i> Add to Cart
                </Button>
                <Button 
                  variant="outline" 
                  onClick={handleAddToWishlist}
                  className={`py-3 ${isWishlisted ? 'text-primary-600' : ''}`}
                >
                  <i className={`${isWishlisted ? 'fas' : 'far'} fa-heart mr-2`}></i>
                  {isWishlisted ? 'Wishlisted' : 'Add to Wishlist'}
                </Button>
              </div>
            </div>
          )}
          
          <div className="border-t border-gray-200 pt-6">
            <div className="grid grid-cols-2 gap-6">
              <div className="flex items-center">
                <div className="rounded-full bg-gray-100 p-2 mr-3">
                  <i className="fas fa-truck text-primary-600"></i>
                </div>
                <span className="text-sm">Free shipping on orders over $50</span>
              </div>
              <div className="flex items-center">
                <div className="rounded-full bg-gray-100 p-2 mr-3">
                  <i className="fas fa-undo text-primary-600"></i>
                </div>
                <span className="text-sm">30-day easy returns</span>
              </div>
              <div className="flex items-center">
                <div className="rounded-full bg-gray-100 p-2 mr-3">
                  <i className="fas fa-shield-alt text-primary-600"></i>
                </div>
                <span className="text-sm">2-year warranty</span>
              </div>
              <div className="flex items-center">
                <div className="rounded-full bg-gray-100 p-2 mr-3">
                  <i className="fas fa-lock text-primary-600"></i>
                </div>
                <span className="text-sm">Secure payment</span>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      {/* Product tabs */}
      <div className="my-12">
        <Tabs defaultValue="description">
          <TabsList className="w-full border-b">
            <TabsTrigger value="description">Description</TabsTrigger>
            <TabsTrigger value="specifications">Specifications</TabsTrigger>
            <TabsTrigger value="reviews">Reviews ({product.reviewCount})</TabsTrigger>
          </TabsList>
          <TabsContent value="description" className="py-6">
            <div className="prose max-w-none">
              <p>{product.description}</p>
              <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nullam in vestibulum tortor, vitae venenatis lectus. Praesent gravida dapibus neque sit amet molestie. Morbi blandit eu dolor a luctus. Vestibulum sollicitudin elit ac nunc scelerisque rhoncus. Nulla felis sapien, condimentum ut imperdiet vel, aliquet id ante. In vitae odio et est sollicitudin sollicitudin vitae sit amet ligula.</p>
            </div>
          </TabsContent>
          <TabsContent value="specifications" className="py-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <h3 className="font-medium mb-2">Technical Specifications</h3>
                <table className="w-full text-sm">
                  <tbody>
                    <tr className="border-b">
                      <td className="py-2 text-gray-500">Brand</td>
                      <td className="py-2 font-medium">NovaCart</td>
                    </tr>
                    <tr className="border-b">
                      <td className="py-2 text-gray-500">Model</td>
                      <td className="py-2 font-medium">{product.name}</td>
                    </tr>
                    <tr className="border-b">
                      <td className="py-2 text-gray-500">Category</td>
                      <td className="py-2 font-medium">{product.category.name}</td>
                    </tr>
                    <tr className="border-b">
                      <td className="py-2 text-gray-500">Warranty</td>
                      <td className="py-2 font-medium">2 Years</td>
                    </tr>
                  </tbody>
                </table>
              </div>
              <div>
                <h3 className="font-medium mb-2">Features</h3>
                <ul className="list-disc list-inside text-sm space-y-1">
                  <li>High-quality materials</li>
                  <li>Durable construction</li>
                  <li>Modern design</li>
                  <li>Energy efficient</li>
                  <li>Easy to use</li>
                </ul>
              </div>
            </div>
          </TabsContent>
          <TabsContent value="reviews" className="py-6">
            <div className="mb-8">
              <h3 className="font-medium mb-4 text-lg">Customer Reviews</h3>
              
              <div className="flex items-center mb-4">
                <div className="flex text-amber-500 text-3xl mr-4">
                  {renderStars(product.rating)}
                </div>
                <div>
                  <p className="font-medium text-xl">{product.rating.toFixed(1)} out of 5</p>
                  <p className="text-gray-500">{product.reviewCount} global ratings</p>
                </div>
              </div>
              
              {reviews && reviews.length > 0 ? (
                <div className="space-y-6">
                  {reviews.map((review: any) => (
                    <div key={review.id} className="border-b pb-6">
                      <div className="flex items-center mb-2">
                        <div className="flex text-amber-500 mr-2">
                          {renderStars(review.rating)}
                        </div>
                        <span className="font-medium">{review.userId}</span>
                      </div>
                      <p className="text-gray-700">{review.comment}</p>
                      <p className="text-gray-500 text-sm mt-1">
                        {new Date(review.createdAt).toLocaleDateString()}
                      </p>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-gray-500">No reviews yet. Be the first to review this product!</p>
              )}
              
              {isAuthenticated ? (
                <div className="mt-8">
                  <Button asChild>
                    <Link href={`/account?reviewProduct=${product.id}`}>Write a Review</Link>
                  </Button>
                </div>
              ) : (
                <div className="mt-8">
                  <p className="text-gray-500 mb-2">Please sign in to write a review</p>
                  <Button asChild>
                    <Link href="/login">Sign In</Link>
                  </Button>
                </div>
              )}
            </div>
          </TabsContent>
        </Tabs>
      </div>
      
      {/* Related products */}
      {relatedProducts && relatedProducts.length > 0 && (
        <div className="my-12">
          <h2 className="text-2xl font-bold mb-6">Related Products</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 md:gap-6">
            {relatedProducts.map(relatedProduct => (
              <ProductCard key={relatedProduct.id} product={relatedProduct} />
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default ProductDetail;
