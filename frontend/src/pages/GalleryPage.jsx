import React from 'react';
import { ArrowLeft, Heart, Eye } from 'lucide-react';
import { Link } from 'react-router-dom';
import Navigation from '../components/Navigation';
import { Badge } from '../components/ui/badge';
import { Dialog, DialogContent, DialogTrigger } from '../components/ui/dialog';

const GalleryPage = () => {
  const galleryImages = [
    {
      id: 1,
      url: "https://i.ibb.co/CpjCdZ8B/Capture-d-cran-2025-08-31-143559.png",
      title: "Bouquet Henné & Fleurs",
      category: "Mariée",
      description: "Création artistique mêlant henné traditionnel et arrangement floral",
      likes: 245
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
      title: "Henné Géométrique Moderne",
      category: "Moderne",
      description: "Design contemporain aux lignes géométriques épurées",
      likes: 143
    },
    {
      id: 4,
      url: "https://i.ibb.co/4rVfCDW/IMG-6649.jpg",
      title: "Création Artistique Détaillée",
      category: "Traditionnel",
      description: "Œuvre d'art complexe avec motifs fins et précis",
      likes: 267
    },
    {
      id: 5,
      url: "https://i.ibb.co/GfDt5V0/IMG-6650.jpg",
      title: "Henné Raffiné et Délicat",
      category: "Simple",
      description: "Design épuré alliant simplicité et élégance",
      likes: 156
    }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-b from-orange-50 to-white">
      <Navigation />
      
      <div className="pt-20 pb-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 py-8 sm:py-16">
          {/* Header */}
          <div className="flex items-center gap-4 mb-6 sm:mb-8">
            <Link 
              to="/" 
              className="flex items-center gap-2 text-orange-600 hover:text-orange-700 transition-colors"
            >
              <ArrowLeft className="w-4 h-4 sm:w-5 sm:h-5" />
              <span className="text-sm sm:text-base">Retour à l'accueil</span>
            </Link>
          </div>

          {/* Title - Design Épuré */}
          <div className="text-center mb-12 sm:mb-20">
            <h1 className="text-4xl sm:text-5xl md:text-6xl font-light text-gray-900 mb-6 sm:mb-8 tracking-tight">
              Galerie
            </h1>
            <div className="w-16 sm:w-24 h-1 bg-orange-600 mx-auto mb-6 sm:mb-8"></div>
            <p className="text-lg sm:text-xl text-gray-600 max-w-2xl mx-auto leading-relaxed font-light px-4">
              Découvrez l'art du henné à travers nos créations authentiques
            </p>
          </div>

          {/* Gallery Grid - Design Pro et Épuré - Suppression des filtres de catégories */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6 sm:gap-8">
            {galleryImages.map((image) => (
              <div key={image.id} className="group relative overflow-hidden rounded-2xl bg-white shadow-lg hover:shadow-xl transition-all duration-500">
                <div className="aspect-[4/5] relative overflow-hidden">
                  <img
                    src={image.url}
                    alt={image.title}
                    className="w-full h-full object-cover transition-all duration-700 group-hover:scale-105"
                  />
                  
                  {/* Overlay Épuré */}
                  <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-all duration-500">
                    <div className="absolute bottom-4 sm:bottom-6 left-4 sm:left-6 right-4 sm:right-6">
                      <h3 className="text-white text-lg sm:text-xl font-semibold mb-2">
                        {image.title}
                      </h3>
                      <p className="text-white/90 text-sm mb-3 line-clamp-2">
                        {image.description}
                      </p>
                      <div className="flex items-center justify-between">
                        <Badge className="bg-orange-600 text-white text-xs px-2 sm:px-3 py-1">
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
                              <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/80 to-transparent p-4 sm:p-6">
                                <h3 className="text-white text-xl sm:text-2xl font-bold mb-2">
                                  {image.title}
                                </h3>
                                <p className="text-white/90 mb-3 text-sm sm:text-base">
                                  {image.description}
                                </p>
                                <div className="flex items-center gap-4">
                                  <Badge className="bg-orange-600 text-white text-xs">
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
                  <div className="absolute top-3 sm:top-4 right-3 sm:right-4">
                    <Badge className="bg-white/90 text-gray-800 text-xs backdrop-blur-sm">
                      {image.category}
                    </Badge>
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* CTA Section - Design Épuré */}
          <div className="text-center mt-16 sm:mt-20 py-12 sm:py-16 border-t border-gray-100">
            <h2 className="text-3xl sm:text-4xl font-light text-gray-900 mb-4 sm:mb-6 tracking-tight px-4">
              Prête pour votre création ?
            </h2>
            <p className="text-base sm:text-lg text-gray-600 mb-8 sm:mb-10 max-w-xl mx-auto font-light leading-relaxed px-4">
              Transformez vos mains en œuvre d'art avec nos créations sur mesure
            </p>
            <Link
              to="/connexion"
              className="inline-block bg-orange-600 text-white px-8 sm:px-12 py-3 sm:py-4 font-light tracking-wider text-sm hover:bg-orange-700 transition-all duration-300 border border-orange-600 hover:shadow-lg"
            >
              RÉSERVER MAINTENANT
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
};

export default GalleryPage;