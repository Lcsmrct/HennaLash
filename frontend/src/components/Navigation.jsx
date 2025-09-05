import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { User, LogOut } from 'lucide-react';
import { mockData } from '../mock';

const Navigation = () => {
  const location = useLocation();

  const getIcon = (iconName) => {
    switch (iconName) {
      case 'user':
        return <User className="w-4 h-4" />;
      case 'log-out':
        return <LogOut className="w-4 h-4" />;
      default:
        return null;
    }
  };

  return (
    <nav className="bg-white/95 backdrop-blur-sm shadow-sm fixed top-0 left-0 right-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <Link to="/" className="flex-shrink-0">
            <h1 className="text-2xl font-bold text-orange-600">Henné Artisanal</h1>
          </Link>

          {/* Navigation Links */}
          <div className="hidden md:block">
            <div className="ml-10 flex items-baseline space-x-8">
              {mockData.navigation.map((item, index) => {
                const isActive = location.pathname === item.href;
                
                return (
                  <Link
                    key={index}
                    to={item.href}
                    className={`flex items-center gap-1 px-3 py-2 text-sm font-medium transition-colors duration-200 ${
                      isActive
                        ? 'text-orange-600 border-b-2 border-orange-600'
                        : 'text-gray-700 hover:text-orange-600 hover:border-b-2 hover:border-orange-300'
                    }`}
                  >
                    {item.icon && getIcon(item.icon)}
                    {item.label}
                  </Link>
                );
              })}
            </div>
          </div>

          {/* Mobile menu button */}
          <div className="md:hidden">
            <button className="bg-gray-100 p-2 rounded-md text-gray-600 hover:text-orange-600 hover:bg-gray-200 transition-colors">
              <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            </button>
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navigation;