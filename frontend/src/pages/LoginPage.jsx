import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { Navigate, Link } from 'react-router-dom';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { AlertCircle, Loader2, ArrowLeft } from 'lucide-react';
import { Alert, AlertDescription } from '../components/ui/alert';
import Navigation from '../components/Navigation';

const LoginPage = () => {
  const { login, isAuthenticated, user } = useAuth();
  const [formData, setFormData] = useState({
    email: '',
    password: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // Redirect if already authenticated
  if (isAuthenticated) {
    return <Navigate to={user?.role === 'admin' ? '/admin' : '/mon-espace'} replace />;
  }

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    const result = await login(formData.email, formData.password);
    
    if (!result.success) {
      setError(result.error);
    }
    
    setLoading(false);
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-orange-50 to-white">
      <Navigation />
      
      {/* Hero Section with Background */}
      <section className="relative min-h-screen flex items-center justify-center overflow-hidden pt-16">
        {/* Background Image with Overlay */}
        <div 
          className="absolute inset-0 bg-cover bg-center bg-no-repeat"
          style={{
            backgroundImage: `url('https://images.unsplash.com/photo-1560472354-b33ff0c44a43?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1000&q=80')`,
          }}
        >
          {/* Dark overlay */}
          <div className="absolute inset-0 bg-black/60"></div>
        </div>

        {/* Content */}
        <div className="relative z-10 w-full max-w-md mx-auto px-6">
          {/* Back Link */}
          <div className="mb-8">
            <Link 
              to="/" 
              className="inline-flex items-center gap-2 text-white/80 hover:text-white transition-colors group"
            >
              <ArrowLeft className="w-4 h-4 group-hover:-translate-x-1 transition-transform" />
              Retour à l'accueil
            </Link>
          </div>

          {/* Login Form */}
          <div className="bg-white/95 backdrop-blur-sm rounded-2xl shadow-2xl p-8">
            <div className="text-center mb-8">
              <h1 className="text-3xl font-bold text-gray-900 mb-2">Connexion</h1>
              <p className="text-gray-600">
                Connectez-vous à votre espace personnel
              </p>
            </div>

            <form onSubmit={handleSubmit} className="space-y-6">
              {error && (
                <Alert variant="destructive" className="border-red-200 bg-red-50">
                  <AlertCircle className="h-4 w-4" />
                  <AlertDescription className="text-red-800">{error}</AlertDescription>
                </Alert>
              )}
              
              <div className="space-y-2">
                <Label htmlFor="email" className="text-gray-700 font-medium">
                  Adresse email
                </Label>
                <Input
                  id="email"
                  name="email"
                  type="email"
                  value={formData.email}
                  onChange={handleChange}
                  placeholder="votre@email.com"
                  required
                  disabled={loading}
                  className="h-12 border-gray-300 focus:border-orange-500 focus:ring-orange-500 rounded-lg"
                />
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="password" className="text-gray-700 font-medium">
                  Mot de passe
                </Label>
                <Input
                  id="password"
                  name="password"
                  type="password"
                  value={formData.password}
                  onChange={handleChange}
                  placeholder="••••••••"
                  required
                  disabled={loading}
                  className="h-12 border-gray-300 focus:border-orange-500 focus:ring-orange-500 rounded-lg"
                />
              </div>
              
              <Button 
                type="submit" 
                disabled={loading}
                className="w-full h-12 bg-orange-600 hover:bg-orange-700 text-white font-semibold rounded-lg transition-all duration-300 transform hover:scale-105 shadow-lg disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none"
              >
                {loading ? (
                  <>
                    <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                    Connexion en cours...
                  </>
                ) : (
                  'Se connecter'
                )}
              </Button>
            </form>

            {/* Links */}
            <div className="mt-8 space-y-4 text-center">
              <p className="text-gray-600">
                Pas encore de compte ?{' '}
                <Link 
                  to="/inscription" 
                  className="text-orange-600 hover:text-orange-700 font-semibold hover:underline transition-colors"
                >
                  Créer un compte
                </Link>
              </p>
              
              <div className="pt-4 border-t border-gray-200">
                <p className="text-sm text-gray-500">
                  Besoin d'aide ? Contactez-nous au{' '}
                  <span className="text-orange-600 font-medium">01 23 45 67 89</span>
                </p>
              </div>
            </div>
          </div>

          {/* Additional Info */}
          <div className="mt-8 text-center">
            <p className="text-white/80 text-sm">
              Votre espace sécurisé pour gérer vos rendez-vous et découvrir nos services
            </p>
          </div>
        </div>
      </section>
    </div>
  );
};

export default LoginPage;