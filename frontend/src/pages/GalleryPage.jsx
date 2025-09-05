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
      url: "https://images.unsplash.com/photo-1629332791128-58f00882964d?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2Nzd8MHwxfHNlYXJjaHwxfHxoZW5uYSUyMGFydHxlbnwwfHx8fDE3NTcwNzE1NTd8MA&ixlib=rb-4.1.0&q=85",
      title: "Henné Traditionnel Marocain",
      category: "Traditionnel",
      description: "Motifs traditionnels inspirés de l'art ancestral marocain",
      likes: 42
    },
    {
      id: 2,
      url: "https://images.unsplash.com/photo-1629332791370-77208e6cbb67?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2Nzd8MHwxfHNlYXJjaHwzfHxoZW5uYSUyMGFydHxlbnwwfHx8fDE3NTcwNzE1NTd8MA&ixlib=rb-4.1.0&q=85",
      title: "Henné de Mariée",
      category: "Mariée",
      description: "Design élaboré pour le jour J avec détails exceptionnels",
      likes: 89
    },
    {
      id: 3,
      url: "https://images.unsplash.com/photo-1583878544826-8f8c418033ed?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDQ2MzR8MHwxfHNlYXJjaHwyfHxtZWhuZGklMjBkZXNpZ25zfGVufDB8fHx8MTc1NzA3MTU2M3ww&ixlib=rb-4.1.0&q=85",
      title: "Henné Bridal Complet",
      category: "Mariée",
      description: "Création complète mains et avant-bras pour mariée",
      likes: 76
    },
    {
      id: 4,
      url: "https://images.unsplash.com/photo-1674884060571-96a46a9a7a72?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDQ2MzR8MHwxfHNlYXJjaHwxfHxtZWhuZGklMjBkZXNpZ25zfGVufDB8fHx8MTc1NzA3MTU2M3ww&ixlib=rb-4.1.0&q=85",
      title: "Design Contemporain",
      category: "Moderne",
      description: "Motif moderne et épuré pour un style contemporain",
      likes: 34
    },
    {
      id: 5,
      url: "https://images.unsplash.com/photo-1556614697-e4e00b2233f6?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2Nzd8MHwxfHNlYXJjaHw0fHxoZW5uYSUyMGFydHxlbnwwfHx8fDE3NTcwNzE1NTd8MA&ixlib=rb-4.1.0&q=85",
      title: "Henné Simple Élégant",
      category: "Simple",
      description: "Design simple et raffiné pour toute occasion",
      likes: 28
    },
    {
      id: 6,
      url: "https://images.unsplash.com/photo-1623217509141-6f735087b50c?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2Nzd8MHwxfHNlYXJjaHwyfHxoZW5uYSUyMGFydHxlbnwwfHx8fDE3NTcwNzE1NTd8MA&ixlib=rb-4.1.0&q=85",
      title: "Art Henné Détaillé",
      category: "Traditionnel",
      description: "Création artistique avec détails fins et précis",
      likes: 55
    },
    {
      id: 7,
      url: "https://images.unsplash.com/photo-1530082625928-db66d39c5a21?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDQ2MzR8MHwxfHNlYXJjaHw0fHxtZWhuZGklMjBkZXNpZ25zfGVufDB8fHx8MTc1NzA3MTU2M3ww&ixlib=rb-4.1.0&q=85",
      title: "Henné Main Complète",
      category: "Traditionnel",
      description: "Couverture complète avec motifs traditionnels",
      likes: 67
    },
    {
      id: 8,
      url: "https://images.pexels.com/photos/33774874/pexels-photo-33774874.jpeg",
      title: "Création Artistique",
      category: "Moderne",
      description: "Approche artistique contemporaine du henné",
      likes: 43
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

          {/* Gallery Grid */}
          <div className="grid md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {filteredImages.map((image) => (
              <Card key={image.id} className="group overflow-hidden bg-white shadow-lg hover:shadow-2xl transition-all duration-300 transform hover:-translate-y-2">
                <div className="relative">
                  <img
                    src={image.url}
                    alt={image.title}
                    className="w-full h-64 object-cover transition-transform duration-300 group-hover:scale-110"
                  />
                  
                  {/* Overlay */}
                  <div className="absolute inset-0 bg-black/0 group-hover:bg-black/40 transition-all duration-300 flex items-center justify-center">
                    <div className="opacity-0 group-hover:opacity-100 transition-opacity duration-300 flex gap-3">
                      <Dialog>
                        <DialogTrigger asChild>
                          <button className="bg-white/90 text-gray-800 p-3 rounded-full hover:bg-white transition-colors">
                            <Eye className="w-5 h-5" />
                          </button>
                        </DialogTrigger>
                        <DialogContent className="max-w-4xl">
                          <div className="grid md:grid-cols-2 gap-6">
                            <img
                              src={image.url}
                              alt={image.title}
                              className="w-full h-auto rounded-lg"
                            />
                            <div className="space-y-4">
                              <div>
                                <h3 className="text-2xl font-bold text-gray-900 mb-2">
                                  {image.title}
                                </h3>
                                <Badge variant="outline" className="text-orange-600 border-orange-600 mb-4">
                                  {image.category}
                                </Badge>
                              </div>
                              <p className="text-gray-700 leading-relaxed">
                                {image.description}
                              </p>
                              <div className="flex items-center gap-2 text-gray-500">
                                <Heart className="w-4 h-4" />
                                <span>{image.likes} j'aime</span>
                              </div>
                            </div>
                          </div>
                        </DialogContent>
                      </Dialog>
                      
                      <button className="bg-white/90 text-red-600 p-3 rounded-full hover:bg-white hover:text-red-700 transition-colors">
                        <Heart className="w-5 h-5" />
                      </button>
                    </div>
                  </div>

                  {/* Category Badge */}
                  <div className="absolute top-4 left-4">
                    <Badge className="bg-orange-600 text-white">
                      {image.category}
                    </Badge>
                  </div>
                </div>

                <CardContent className="p-6">
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">
                    {image.title}
                  </h3>
                  <p className="text-gray-600 text-sm mb-4 leading-relaxed">
                    {image.description}
                  </p>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2 text-gray-500 text-sm">
                      <Heart className="w-4 h-4" />
                      <span>{image.likes}</span>
                    </div>
                    <button className="text-orange-600 hover:text-orange-700 text-sm font-medium transition-colors">
                      Voir plus
                    </button>
                  </div>
                </CardContent>
              </Card>
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