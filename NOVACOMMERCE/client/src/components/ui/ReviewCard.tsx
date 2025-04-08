interface ReviewCardProps {
  review: {
    id: number;
    rating: number;
    comment: string;
    userName: string;
    userImage?: string;
    verified?: boolean;
  };
}

const ReviewCard = ({ review }: ReviewCardProps) => {
  // Render star rating
  const renderStars = () => {
    const stars = [];
    
    for (let i = 1; i <= 5; i++) {
      if (i <= review.rating) {
        stars.push(<i key={i} className="fas fa-star"></i>);
      } else {
        stars.push(<i key={i} className="far fa-star"></i>);
      }
    }
    
    return stars;
  };

  return (
    <div className="bg-white p-6 rounded-lg shadow">
      <div className="flex text-amber-500 mb-3">
        {renderStars()}
      </div>
      <p className="text-gray-600 mb-4">{review.comment}</p>
      <div className="flex items-center">
        <div className="w-10 h-10 rounded-full bg-gray-300 mr-3 overflow-hidden">
          {review.userImage ? (
            <img 
              src={review.userImage} 
              alt={review.userName} 
              className="w-full h-full object-cover" 
            />
          ) : (
            <div className="w-full h-full flex items-center justify-center bg-primary-100 text-primary-700 font-medium">
              {review.userName.charAt(0).toUpperCase()}
            </div>
          )}
        </div>
        <div>
          <h4 className="font-medium">{review.userName}</h4>
          {review.verified && <p className="text-gray-500 text-sm">Verified Buyer</p>}
        </div>
      </div>
    </div>
  );
};

export default ReviewCard;
