import React from 'react';

const About = () => {
  return (
    <div className="container mx-auto px-4 py-12">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl md:text-4xl font-bold mb-8 text-center">About NovaCart</h1>
        
        <div className="prose prose-lg max-w-none mb-12">
          <p>
            NovaCart is a modern e-commerce platform designed to provide a seamless shopping experience for tech products and lifestyle items.
            Our mission is to connect customers with high-quality products through an intuitive and responsive interface.
          </p>
        </div>
        
        {/* Developer Profile Section */}
        <div className="bg-slate-50 rounded-xl p-8 shadow-lg mb-12">
          <h2 className="text-2xl font-bold mb-6 text-center">Meet the Developer</h2>
          
          <div className="flex flex-col md:flex-row items-center gap-8">
            <div className="w-48 h-48 rounded-full overflow-hidden bg-gradient-to-r from-primary-500 to-blue-500 flex items-center justify-center text-white text-4xl font-bold">
              SM
            </div>
            
            <div className="flex-1">
              <h3 className="text-2xl font-bold text-primary-700 mb-2">Sina Mohammadhosseinzadeh</h3>
              <p className="text-lg text-gray-600 mb-4">Full Stack Developer</p>
              
              <div className="prose prose-md max-w-none">
                <p>
                  Sina is a passionate developer with expertise in modern web technologies. 
                  His skills include React, Node.js, TypeScript, and database management.
                </p>
                <p>
                  With a keen eye for detail and a commitment to creating exceptional user experiences,
                  Sina developed NovaCart as a showcase of best practices in e-commerce development.
                </p>
              </div>
              
              <div className="mt-6 flex gap-4">
                <a href="https://github.com/" target="_blank" rel="noopener noreferrer" className="bg-slate-800 text-white px-4 py-2 rounded-md hover:bg-slate-700 transition-colors">
                  <i className="fab fa-github mr-2"></i> GitHub
                </a>
                <a href="https://linkedin.com/" target="_blank" rel="noopener noreferrer" className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 transition-colors">
                  <i className="fab fa-linkedin mr-2"></i> LinkedIn
                </a>
              </div>
            </div>
          </div>
        </div>
        
        <div className="prose prose-lg max-w-none">
          <h2>Our Technology Stack</h2>
          <p>
            NovaCart is built using cutting-edge technologies to ensure performance, security, and scalability:
          </p>
          <ul>
            <li><strong>Frontend:</strong> React, TypeScript, TailwindCSS</li>
            <li><strong>Backend:</strong> Node.js, Express</li>
            <li><strong>Database:</strong> PostgreSQL with Drizzle ORM</li>
            <li><strong>Authentication:</strong> JWT</li>
            <li><strong>Payment Processing:</strong> Stripe</li>
          </ul>
          
          <h2>Our Vision</h2>
          <p>
            We aim to revolutionize online shopping by combining beautiful design with powerful functionality.
            NovaCart represents the future of e-commerce - fast, responsive, and user-friendly.
          </p>
        </div>
      </div>
    </div>
  );
};

export default About; 