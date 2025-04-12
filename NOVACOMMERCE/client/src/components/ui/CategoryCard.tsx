import { Link } from 'wouter';

interface CategoryCardProps {
  category: {
    id: number;
    name: string;
    slug: string;
    imageUrl?: string;
  };
}

const CategoryCard = ({ category }: CategoryCardProps) => {
  return (
    <Link href={`/products/category/${category.id}`} className="group">
      <div className="bg-gray-100 rounded-lg overflow-hidden transition duration-300 transform hover:scale-105 hover:shadow-md">
        <img 
          src={category.imageUrl || 'https://via.placeholder.com/400x300?text=No+Image'} 
          alt={category.name} 
          className="w-full h-32 md:h-48 object-cover" 
        />
        <div className="p-3 text-center">
          <h3 className="font-medium text-sm md:text-base group-hover:text-primary-600">
            {category.name}
          </h3>
        </div>
      </div>
    </Link>
  );
};

export default CategoryCard;
