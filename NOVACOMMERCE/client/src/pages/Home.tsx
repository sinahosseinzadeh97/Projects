import { useEffect } from 'react';
import { Link } from 'wouter';
import { useQuery } from '@tanstack/react-query';
import ProductCard from '@/components/ui/ProductCard';
import CategoryCard from '@/components/ui/CategoryCard';
import ReviewCard from '@/components/ui/ReviewCard';
import Newsletter from '@/components/ui/Newsletter';
import SpecialOffer from '@/components/ui/SpecialOffer';

const Home = () => {
  // Set up future date for special offer countdown
  const targetDate = new Date();
  targetDate.setDate(targetDate.getDate() + 3); // 3 days from now

  // Fetch categories
  const { data: categories } = useQuery({
    queryKey: ['/api/categories'],
  });

  // Fetch featured products
  const { data: featuredProducts } = useQuery({
    queryKey: ['/api/products/featured'],
  });

  // Fetch new products
  const { data: newProducts } = useQuery({
    queryKey: ['/api/products/new'],
  });

  // Mock reviews since we don't have a reviews endpoint for the homepage
  const reviews = [
    {
      id: 1,
      rating: 5,
      comment: "The SmartWatch Series 5 exceeded my expectations. The battery life is impressive, and the health tracking features are incredibly accurate. Definitely worth the investment!",
      userName: "Sarah J.",
      userImage: "https://randomuser.me/api/portraits/women/43.jpg",
      verified: true
    },
    {
      id: 2,
      rating: 5,
      comment: "Fast shipping and excellent customer service. The wireless earbuds have amazing sound quality and the noise cancellation feature works perfectly for my daily commute.",
      userName: "Michael T.",
      userImage: "https://randomuser.me/api/portraits/men/32.jpg",
      verified: true
    },
    {
      id: 3,
      rating: 4,
      comment: "I've been using the Smart Home Camera for a few weeks now and it's been a game-changer for my home security. The app interface is intuitive and the motion detection alerts work well.",
      userName: "Jennifer K.",
      userImage: "https://randomuser.me/api/portraits/women/26.jpg",
      verified: true
    }
  ];

  // Default special offer product
  const specialOfferProduct = {
    id: 2,
    name: "SmartWatch Series 5",
    slug: "smartwatch-series-5",
    description: "Get our bestselling SmartWatch Series 5 at 25% off. Limited time offer with free premium band included.",
    imageUrl: "https://images.unsplash.com/photo-1546868871-7041f2a55e12"
  };

  return (
    <>
      {/* Hero Banner */}
      <section className="bg-gradient-to-r from-primary-700 to-primary-500 text-white">
        <div className="container mx-auto px-4 py-12 md:py-24">
          <div className="flex flex-col md:flex-row items-center">
            <div className="md:w-1/2 mb-8 md:mb-0">
              <h1 className="text-3xl md:text-4xl lg:text-5xl font-bold mb-4">Summer Sale is On!</h1>
              <p className="text-lg mb-6">Get up to 50% off on our latest collection. Limited time offer.</p>
              <Link href="/products" className="inline-block bg-white text-primary-600 font-medium px-6 py-3 rounded-lg hover:bg-gray-100 transition duration-200">Shop Now</Link>
            </div>
            <div className="md:w-1/2">
              <img 
                src="https://images.unsplash.com/photo-1607082350899-7e105aa886ae?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80" 
                alt="Summer Sale Collection" 
                className="rounded-lg shadow-lg w-full h-auto" 
              />
            </div>
          </div>
        </div>
      </section>

      {/* Featured Categories */}
      <section className="py-12 bg-white">
        <div className="container mx-auto px-4">
          <h2 className="text-2xl font-bold mb-8 text-center">Shop by Category</h2>
          
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 md:gap-6">
            {categories?.map(category => (
              <CategoryCard key={category.id} category={category} />
            ))}
          </div>
        </div>
      </section>

      {/* Featured Products */}
      <section className="py-12 bg-gray-50">
        <div className="container mx-auto px-4">
          <div className="flex justify-between items-center mb-8">
            <h2 className="text-2xl font-bold">Featured Products</h2>
            <Link href="/products?featured=true" className="text-primary-600 hover:text-primary-700 font-medium">View All</Link>
          </div>
          
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4 md:gap-6">
            {featuredProducts?.map(product => (
              <ProductCard key={product.id} product={product} />
            ))}
          </div>
        </div>
      </section>

      {/* Special Offer Banner */}
      <SpecialOffer product={specialOfferProduct} targetDate={targetDate} />

      {/* New Arrivals */}
      <section className="py-12 bg-white">
        <div className="container mx-auto px-4">
          <div className="flex justify-between items-center mb-8">
            <h2 className="text-2xl font-bold">New Arrivals</h2>
            <Link href="/products?new=true" className="text-primary-600 hover:text-primary-700 font-medium">View All</Link>
          </div>
          
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4 md:gap-6">
            {newProducts?.map(product => (
              <ProductCard key={product.id} product={product} />
            ))}
          </div>
        </div>
      </section>

      {/* Customer Reviews */}
      <section className="py-12 bg-gray-50">
        <div className="container mx-auto px-4">
          <h2 className="text-2xl font-bold mb-8 text-center">What Our Customers Say</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {reviews.map(review => (
              <ReviewCard key={review.id} review={review} />
            ))}
          </div>
        </div>
      </section>

      {/* Newsletter */}
      <Newsletter />
    </>
  );
};

export default Home;
