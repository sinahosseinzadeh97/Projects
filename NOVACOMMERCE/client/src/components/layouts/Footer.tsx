import { Link } from 'wouter';
import { useQuery } from '@tanstack/react-query';

const Footer = () => {
  // Get categories for footer links
  const { data: categories } = useQuery({
    queryKey: ['/api/categories'],
  });

  return (
    <footer className="bg-gray-800 text-white pt-12 pb-6">
      <div className="container mx-auto px-4">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8 mb-8">
          <div>
            <h3 className="text-lg font-bold mb-4">NovaCart</h3>
            <p className="text-gray-400 mb-4">Your one-stop shop for all things tech and modern lifestyle.</p>
            <div className="flex space-x-4">
              <a href="#" className="text-gray-400 hover:text-white transition duration-200">
                <i className="fab fa-facebook-f"></i>
              </a>
              <a href="#" className="text-gray-400 hover:text-white transition duration-200">
                <i className="fab fa-twitter"></i>
              </a>
              <a href="#" className="text-gray-400 hover:text-white transition duration-200">
                <i className="fab fa-instagram"></i>
              </a>
              <a href="#" className="text-gray-400 hover:text-white transition duration-200">
                <i className="fab fa-pinterest-p"></i>
              </a>
            </div>
          </div>
          
          <div>
            <h3 className="text-lg font-bold mb-4">Shop</h3>
            <ul className="space-y-2">
              <li>
                <Link href="/products" className="text-gray-400 hover:text-white transition duration-200">
                  All Products
                </Link>
              </li>
              <li>
                <Link href="/products?featured=true" className="text-gray-400 hover:text-white transition duration-200">
                  Featured
                </Link>
              </li>
              <li>
                <Link href="/products?new=true" className="text-gray-400 hover:text-white transition duration-200">
                  New Arrivals
                </Link>
              </li>
              <li>
                <Link href="/products?discount=true" className="text-gray-400 hover:text-white transition duration-200">
                  Discounted
                </Link>
              </li>
            </ul>
          </div>
          
          <div>
            <h3 className="text-lg font-bold mb-4">Customer Care</h3>
            <ul className="space-y-2">
              <li>
                <Link href="/account" className="text-gray-400 hover:text-white transition duration-200">
                  My Account
                </Link>
              </li>
              <li>
                <Link href="/account?tab=orders" className="text-gray-400 hover:text-white transition duration-200">
                  Track Order
                </Link>
              </li>
              <li>
                <Link href="#" className="text-gray-400 hover:text-white transition duration-200">
                  Returns & Exchanges
                </Link>
              </li>
              <li>
                <Link href="#" className="text-gray-400 hover:text-white transition duration-200">
                  Help Center
                </Link>
              </li>
            </ul>
          </div>
          
          <div>
            <h3 className="text-lg font-bold mb-4">Contact Us</h3>
            <ul className="space-y-2">
              <li className="flex items-start">
                <i className="fas fa-map-marker-alt mt-1 mr-2 text-gray-400"></i>
                <span className="text-gray-400">1234 Market St, Suite 1000<br/>San Francisco, CA 94103</span>
              </li>
              <li className="flex items-center">
                <i className="fas fa-phone-alt mr-2 text-gray-400"></i>
                <a href="tel:+1-555-123-4567" className="text-gray-400 hover:text-white transition duration-200">+1 (555) 123-4567</a>
              </li>
              <li className="flex items-center">
                <i className="fas fa-envelope mr-2 text-gray-400"></i>
                <a href="mailto:support@novacart.com" className="text-gray-400 hover:text-white transition duration-200">support@novacart.com</a>
              </li>
            </ul>
          </div>
        </div>
        
        <div className="border-t border-gray-700 pt-6">
          <div className="flex flex-col md:flex-row justify-between items-center">
            <p className="text-gray-400 text-sm mb-4 md:mb-0">
              &copy; {new Date().getFullYear()} NovaCart. All rights reserved. 
              <span className="block md:inline mt-1 md:mt-0 md:ml-2">
                Developed by <span className="text-primary-400 font-semibold">Sina Mohammadhosseinzadeh</span>
              </span>
            </p>
            <div className="flex items-center">
              <Link href="#" className="text-gray-400 hover:text-white text-sm mx-3 transition duration-200">Privacy Policy</Link>
              <Link href="#" className="text-gray-400 hover:text-white text-sm mx-3 transition duration-200">Terms of Service</Link>
              <Link href="#" className="text-gray-400 hover:text-white text-sm mx-3 transition duration-200">Shipping Info</Link>
            </div>
            <div className="flex items-center mt-4 md:mt-0">
              <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/visa/visa-original.svg" alt="Visa" className="h-8 w-auto mx-1" />
              <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/mastercard/mastercard-original.svg" alt="Mastercard" className="h-8 w-auto mx-1" />
              <img src="https://cdn.jsdelivr.net/npm/simple-icons@v5/icons/paypal.svg" alt="PayPal" className="h-8 w-auto mx-1 bg-white p-1 rounded" />
              <img src="https://cdn.jsdelivr.net/npm/simple-icons@v5/icons/applepay.svg" alt="Apple Pay" className="h-8 w-auto mx-1 bg-white p-1 rounded" />
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
