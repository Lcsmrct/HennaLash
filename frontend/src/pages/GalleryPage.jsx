import React, { useState } from 'react';
import { ArrowLeft, Heart, Eye } from 'lucide-react';
import { Link } from 'react-router-dom';
import Navigation from '../components/Navigation';
import { Card, CardContent } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Dialog, DialogContent, DialogTrigger } from '../components/ui/dialog';

const GalleryPage = () => {
  const [selectedCategory, setSelectedCategory] = useState('Tous');

  const galleryImages = [
    {
      id: 1,
      url: "https://i.ibb.co/CpjCdZ8B/Capture-d-cran-2025-08-31-143559.png",
      title: "Design Floral Élégant",
      category: "Traditionnel",
      description: "Création raffinée avec motifs floraux délicats et détails précis",
      likes: 125
    },
    {
      id: 2,
      url: "https://i.ibb.co/q3WdDscn/IMG-6647.jpg",
      title: "Art Henné Main Complète",
      category: "Traditionnel",
      description: "Motifs traditionnels complexes couvrant toute la main",
      likes: 198
    },
    {
      id: 3,
      url: "https://i.ibb.co/Myx1Nftm/IMG-6648.jpg",
      title: "Henné Géométrique",
      category: "Moderne",
      description: "Design moderne aux lignes géométriques épurées",
      likes: 143
    },
    {
      id: 4,
      url: "https://i.ibb.co/4rVfCDW/IMG-6649.jpg",
      title: "Création Artistique Détaillée",
      category: "Mariée",
      description: "Œuvre d'art complexe parfaite pour occasions spéciales",
      likes: 267
    },
    {
      id: 5,
      url: "https://i.ibb.co/GfDt5V0M/IMG-6650.jpg",
      title: "Henné Raffiné et Délicat",
      category: "Simple",
      description: "Design épuré alliant simplicité et élégance",
      likes: 156
    }
  ];

  const categories = ['Tous', 'Traditionnel', 'Mariée', 'Moderne', 'Simple'];

  const filteredImages = selectedCategory === 'Tous' 
    ? galleryImages 
    : galleryImages.filter(img => img.category === selectedCategory);

  return (
    <div className="min-h-screen bg-gradient-to-b from-orange-50 to-white">
      <Navigation />
      
      <div className="pt-20 pb-16">
        <div className="max-w-7xl mx-auto px-6 py-16">
          {/* Header */}
          <div className="flex items-center gap-4 mb-8">
            <Link 
              to="/" 
              className="flex items-center gap-2 text-orange-600 hover:text-orange-700 transition-colors"
            >
              <ArrowLeft className="w-5 h-5" />
              Retour à l'accueil
            </Link>
          </div>

          {/* Title */}
          <div className="text-center mb-16">
            <h1 className="text-4xl md:text-5xl font-bold text-gray-900 mb-6">
              Notre Galerie
            </h1>
            <p className="text-lg text-gray-600 max-w-3xl mx-auto leading-relaxed">
              Découvrez nos créations uniques au henné, des designs traditionnels aux créations modernes. 
              Chaque œuvre reflète notre passion pour cet art ancestral.
            </p>
          </div>

          {/* Category Filters */}
          <div className="flex flex-wrap justify-center gap-4 mb-12">
            {categories.map((category) => (
              <button
                key={category}
                onClick={() => setSelectedCategory(category)}
                className={`px-6 py-2 rounded-full font-medium transition-all duration-300 ${
                  selectedCategory === category
                    ? 'bg-orange-600 text-white transform scale-105'
                    : 'bg-white text-gray-700 hover:bg-orange-100 hover:text-orange-600 shadow-md'
                }`}
              >
                {category}
              </button>
            ))}
          </div>

          {/* Gallery Grid - Design Pro et Épuré */}
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {filteredImages.map((image) => (
              <div key={image.id} className="group relative overflow-hidden rounded-2xl bg-white shadow-lg hover:shadow-xl transition-all duration-500">
                <div className="aspect-[4/5] relative overflow-hidden">
                  <img
                    src={image.url}
                    alt={image.title}
                    className="w-full h-full object-cover transition-all duration-700 group-hover:scale-105"
                  />
                  
                  {/* Overlay Épuré */}
                  <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-all duration-500">
                    <div className="absolute bottom-6 left-6 right-6">
                      <h3 className="text-white text-xl font-semibold mb-2">
                        {image.title}
                      </h3>
                      <p className="text-white/90 text-sm mb-3">
                        {image.description}
                      </p>
                      <div className="flex items-center justify-between">
                        <Badge className="bg-orange-600 text-white text-xs px-3 py-1">
                          {image.category}
                        </Badge>
                        <Dialog>
                          <DialogTrigger asChild>
                            <button className="bg-white/20 backdrop-blur-sm text-white p-2 rounded-full hover:bg-white/30 transition-colors">
                              <Eye className="w-4 h-4" />
                            </button>
                          </DialogTrigger>
                          <DialogContent className="max-w-3xl p-0 overflow-hidden">
                            <div className="relative">
                              <img
                                src={image.url}
                                alt={image.title}
                                className="w-full h-auto"
                              />
                              <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/80 to-transparent p-6">
                                <h3 className="text-white text-2xl font-bold mb-2">
                                  {image.title}
                                </h3>
                                <p className="text-white/90 mb-3">
                                  {image.description}
                                </p>
                                <div className="flex items-center gap-4">
                                  <Badge className="bg-orange-600 text-white">
                                    {image.category}
                                  </Badge>
                                  <div className="flex items-center gap-1 text-white/80">
                                    <Heart className="w-4 h-4" />
                                    <span className="text-sm">{image.likes} j'aime</span>
                                  </div>
                                </div>
                              </div>
                            </div>
                          </DialogContent>
                        </Dialog>
                      </div>
                    </div>
                  </div>

                  {/* Badge Catégorie Discret */}
                  <div className="absolute top-4 right-4">
                    <Badge className="bg-white/90 text-gray-800 text-xs backdrop-blur-sm">
                      {image.category}
                    </Badge>
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* CTA Section */}
          <div className="text-center mt-16 bg-white rounded-2xl shadow-lg p-12">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">
              Vous aimez nos créations ?
            </h2>
            <p className="text-lg text-gray-600 mb-8 max-w-2xl mx-auto">
              Réservez votre séance dès maintenant pour obtenir votre propre création unique au henné 100% naturel.
            </p>
            <Link
              to="/reserver"
              className="inline-flex items-center gap-2 bg-orange-600 text-white px-8 py-4 rounded-lg font-semibold hover:bg-orange-700 transition-all duration-300 transform hover:scale-105 shadow-lg"
            >
              Réserver ma Séance
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
};

export default GalleryPage;