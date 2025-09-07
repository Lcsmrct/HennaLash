import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { Navigate, Link } from 'react-router-dom';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Card, CardContent, CardFooter } from '../components/ui/card';
import { AlertCircle, Loader2, CheckCircle, ArrowLeft } from 'lucide-react';
import { Alert, AlertDescription } from '../components/ui/alert';
import Navigation from '../components/Navigation';

const RegisterPage = () => {
  const { register, isAuthenticated, user } = useAuth();
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    confirmPassword: '',
    first_name: '',
    last_name: '',
    phone: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);

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

    // Validate passwords match
    if (formData.password !== formData.confirmPassword) {
      setError('Les mots de passe ne correspondent pas');
      setLoading(false);
      return;
    }

    // Validate password strength
    if (formData.password.length < 6) {
      setError('Le mot de passe doit contenir au moins 6 caractères');
      setLoading(false);
      return;
    }

    const userData = {
      email: formData.email,
      password: formData.password,
      first_name: formData.first_name,
      last_name: formData.last_name,
      phone: formData.phone || null
    };

    const result = await register(userData);
    
    if (result.success) {
      setSuccess(true);
    } else {
      setError(result.error);
    }
    
    setLoading(false);
  };

  if (success) {
    return (
      <div className="min-h-screen bg-gradient-to-b from-orange-50 to-white">
        <Navigation />
        
        <section className="relative min-h-screen flex items-center justify-center overflow-hidden pt-16">
          <div 
            className="absolute inset-0 bg-cover bg-center bg-no-repeat"
            style={{
              backgroundImage: `url('https://images.unsplash.com/photo-1629332791128-58f00882964d?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2NzR8MHwxfHNlYXJjaHwxfHxoZW5uYSUyMGhhbmRzfGVufDB8fHx8MTc1NzI0ODk0MHww&ixlib=rb-4.1.0&q=85')`,
            }}
          >
            <div className="absolute inset-0 bg-black/60"></div>
          </div>

          <div className="relative z-10 w-full max-w-md mx-auto px-6">
            <div className="bg-white/95 backdrop-blur-sm rounded-2xl shadow-2xl p-6 sm:p-8 text-center">
              <div className="flex justify-center mb-4 sm:mb-6">
                <CheckCircle className="h-12 w-12 sm:h-16 sm:w-16 text-green-500" />
              </div>
              <h1 className="text-2xl sm:text-3xl font-bold text-gray-900 mb-3 sm:mb-4">Inscription réussie !</h1>
              <p className="text-sm sm:text-base text-gray-600 mb-6 sm:mb-8">
                Votre compte a été créé avec succès. Vous pouvez maintenant vous connecter.
              </p>
              <Link to="/connexion" className="w-full block">
                <Button className="w-full h-10 sm:h-12 bg-orange-600 hover:bg-orange-700 text-white font-semibold rounded-lg transition-all duration-300 transform hover:scale-105 shadow-lg text-sm sm:text-base">
                  Se connecter maintenant
                </Button>
              </Link>
            </div>
          </div>
        </section>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-orange-50 to-white">
      <Navigation />
      
      <section className="relative min-h-screen flex items-center justify-center overflow-hidden pt-16">
        {/* Background Image with Overlay - Image henné appropriée */}
        <div 
          className="absolute inset-0 bg-cover bg-center bg-no-repeat"
          style={{
            backgroundImage: `url('https://images.unsplash.com/photo-1629332791128-58f00882964d?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2NzR8MHwxfHNlYXJjaHwxfHxoZW5uYSUyMGhhbmRzfGVufDB8fHx8MTc1NzI0ODk0MHww&ixlib=rb-4.1.0&q=85')`,
          }}
        >
          <div className="absolute inset-0 bg-black/60"></div>
        </div>

        <div className="relative z-10 w-full max-w-md mx-auto px-6">
          <div className="mb-6 sm:mb-8">
            <Link 
              to="/" 
              className="inline-flex items-center gap-2 text-white/80 hover:text-white transition-colors group"
            >
              <ArrowLeft className="w-4 h-4 group-hover:-translate-x-1 transition-transform" />
              Retour à l'accueil
            </Link>
          </div>

          <Card className="bg-white/95 backdrop-blur-sm rounded-2xl shadow-2xl">
            <CardContent className="p-6 sm:p-8">
              <div className="text-center mb-6 sm:mb-8">
                <h1 className="text-2xl sm:text-3xl font-bold text-gray-900 mb-2">Inscription</h1>
                <p className="text-sm sm:text-base text-gray-600">
                  Créez votre compte pour réserver en ligne
                </p>
              </div>

              <form onSubmit={handleSubmit} className="space-y-4 sm:space-y-6">
            {error && (
              <Alert variant="destructive">
                <AlertCircle className="h-4 w-4" />
                <AlertDescription className="text-sm">{error}</AlertDescription>
              </Alert>
            )}
            
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 sm:gap-4">
              <div className="space-y-2">
                <Label htmlFor="first_name" className="text-sm font-medium">Prénom</Label>
                <Input
                  id="first_name"
                  name="first_name"
                  value={formData.first_name}
                  onChange={handleChange}
                  placeholder="Prénom"
                  required
                  disabled={loading}
                  className="h-10 text-sm"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="last_name" className="text-sm font-medium">Nom</Label>
                <Input
                  id="last_name"
                  name="last_name"
                  value={formData.last_name}
                  onChange={handleChange}
                  placeholder="Nom"
                  required
                  disabled={loading}
                  className="h-10 text-sm"
                />
              </div>
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="email" className="text-sm font-medium">Email</Label>
              <Input
                id="email"
                name="email"
                type="email"
                value={formData.email}
                onChange={handleChange}
                placeholder="votre@email.com"
                required
                disabled={loading}
                className="h-10 text-sm"
              />
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="phone" className="text-sm font-medium">Téléphone (optionnel)</Label>
              <Input
                id="phone"
                name="phone"
                type="tel"
                value={formData.phone}
                onChange={handleChange}
                placeholder="+33 1 23 45 67 89"
                disabled={loading}
                className="h-10 text-sm"
              />
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="password" className="text-sm font-medium">Mot de passe</Label>
              <Input
                id="password"
                name="password"
                type="password"
                value={formData.password}
                onChange={handleChange}
                placeholder="••••••••"
                required
                disabled={loading}
                className="h-10 text-sm"
              />
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="confirmPassword" className="text-sm font-medium">Confirmer le mot de passe</Label>
              <Input
                id="confirmPassword"
                name="confirmPassword"
                type="password"
                value={formData.confirmPassword}
                onChange={handleChange}
                placeholder="••••••••"
                required
                disabled={loading}
                className="h-10 text-sm"
              />
            </div>
            
            <Button type="submit" className="w-full h-10 sm:h-12 text-sm sm:text-base" disabled={loading}>
              {loading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Inscription...
                </>
              ) : (
                "S'inscrire"
              )}
            </Button>
              </form>
            </CardContent>
        <CardFooter className="flex flex-col space-y-2 px-6 sm:px-8 pb-6 sm:pb-8">
          <p className="text-xs sm:text-sm text-muted-foreground text-center">
            Déjà un compte ?{' '}
            <Link to="/connexion" className="text-primary hover:underline">
              Se connecter
            </Link>
          </p>
          <p className="text-xs text-muted-foreground text-center">
            <Link to="/" className="hover:underline">
              Retour à l'accueil
            </Link>
          </p>
        </CardFooter>
          </Card>
        </div>
      </section>
    </div>
  );
};

export default RegisterPage;