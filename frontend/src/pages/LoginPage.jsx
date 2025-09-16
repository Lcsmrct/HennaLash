import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { Navigate, Link } from 'react-router-dom';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { AlertCircle, Loader2, ArrowLeft, Eye, EyeOff, Mail, Lock, Sparkles } from 'lucide-react';
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
  const [showPassword, setShowPassword] = useState(false);

  // Redirect if already authenticated - with safety check
  if (isAuthenticated && user) {
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

    try {
      const result = await login(formData.email, formData.password);
      
      if (result.success) {
        // Redirection manuelle après login réussi pour éviter les race conditions
        const targetPath = result.user?.role === 'admin' ? '/admin' : '/mon-espace';
        window.location.href = targetPath;
      } else {
        setError(result.error);
      }
    } catch (error) {
      console.error('Login error:', error);
      setError('Erreur inattendue lors de la connexion');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen relative overflow-hidden">
      <Navigation />
      
      {/* Background with Pattern */}
      <div className="absolute inset-0">
        {/* Background Image */}
        <div 
          className="absolute inset-0 bg-cover bg-center bg-no-repeat"
          style={{
            backgroundImage: `url('https://images.unsplash.com/photo-1629332791128-58f00882964d?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2Njl8MHwxfHNlYXJjaHwxfHxoZW5uYSUyMGhhbmRzfGVufDB8fHx8MTc1ODA1NjQyMHww&ixlib=rb-4.1.0&q=85')`,
          }}
        />
        
        {/* Gradient Overlay */}
        <div className="absolute inset-0 bg-gradient-to-br from-orange-900/80 via-amber-900/70 to-orange-800/80"></div>
        
        {/* Decorative Elements */}
        <div className="absolute inset-0 opacity-10">
          <div className="absolute top-20 left-10 w-32 h-32 border border-white/20 rounded-full"></div>
          <div className="absolute bottom-20 right-10 w-24 h-24 border border-white/20 rounded-full"></div>
          <div className="absolute top-1/2 left-1/4 w-16 h-16 border border-white/20 rounded-full"></div>
        </div>
      </div>

      {/* Content */}
      <div className="relative z-10 min-h-screen flex items-center justify-center px-4 pt-16">
        <div className="w-full max-w-lg">
          {/* Back Link */}
          <div className="mb-8">
            <Link 
              to="/" 
              className="inline-flex items-center gap-2 text-white/90 hover:text-white transition-all duration-200 group"
            >
              <ArrowLeft className="w-4 h-4 group-hover:-translate-x-1 transition-transform duration-200" />
              <span className="text-sm font-medium">Retour à l'accueil</span>
            </Link>
          </div>

          {/* Login Card */}
          <div className="bg-white/95 backdrop-blur-lg rounded-3xl shadow-2xl border border-white/20 overflow-hidden">
            {/* Header */}
            <div className="bg-gradient-to-r from-orange-500 to-amber-500 px-8 py-6 text-center">
              <div className="flex justify-center mb-3">
                <div className="w-12 h-12 bg-white/20 rounded-full flex items-center justify-center">
                  <Sparkles className="w-6 h-6 text-white" />
                </div>
              </div>
              <h1 className="text-2xl font-bold text-white mb-1">Bon retour !</h1>
              <p className="text-white/90 text-sm">Connectez-vous à votre espace personnel</p>
            </div>

            {/* Form */}
            <div className="px-8 py-8">
              <form onSubmit={handleSubmit} className="space-y-6">
                {error && (
                  <Alert variant="destructive" className="border-red-200 bg-red-50/50 backdrop-blur-sm">
                    <AlertCircle className="h-4 w-4" />
                    <AlertDescription className="text-red-800 text-sm font-medium">{error}</AlertDescription>
                  </Alert>
                )}
                
                {/* Email Field */}
                <div className="space-y-2">
                  <Label htmlFor="email" className="text-gray-700 font-semibold text-sm flex items-center gap-2">
                    <Mail className="w-4 h-4 text-orange-500" />
                    Adresse email
                  </Label>
                  <div className="relative">
                    <Input
                      id="email"
                      name="email"
                      type="email"
                      value={formData.email}
                      onChange={handleChange}
                      placeholder="votre@email.com"
                      required
                      disabled={loading}
                      className="h-12 pl-12 pr-4 border-2 border-gray-200 focus:border-orange-400 focus:ring-orange-400/20 rounded-xl text-base transition-all duration-200 bg-white/80 backdrop-blur-sm"
                    />
                    <Mail className="absolute left-4 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                  </div>
                </div>
                
                {/* Password Field */}
                <div className="space-y-2">
                  <Label htmlFor="password" className="text-gray-700 font-semibold text-sm flex items-center gap-2">
                    <Lock className="w-4 h-4 text-orange-500" />
                    Mot de passe
                  </Label>
                  <div className="relative">
                    <Input
                      id="password"
                      name="password"
                      type={showPassword ? "text" : "password"}
                      value={formData.password}
                      onChange={handleChange}
                      placeholder="••••••••"
                      required
                      disabled={loading}
                      className="h-12 pl-12 pr-12 border-2 border-gray-200 focus:border-orange-400 focus:ring-orange-400/20 rounded-xl text-base transition-all duration-200 bg-white/80 backdrop-blur-sm"
                    />
                    <Lock className="absolute left-4 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                    <button
                      type="button"
                      onClick={() => setShowPassword(!showPassword)}
                      className="absolute right-4 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600 transition-colors"
                    >
                      {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                    </button>
                  </div>
                </div>
                
                {/* Submit Button */}
                <Button 
                  type="submit" 
                  disabled={loading}
                  className="w-full h-12 bg-gradient-to-r from-orange-500 to-amber-500 hover:from-orange-600 hover:to-amber-600 text-white font-semibold rounded-xl transition-all duration-300 transform hover:scale-[1.02] shadow-lg hover:shadow-xl disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none text-base"
                >
                  {loading ? (
                    <>
                      <Loader2 className="mr-3 h-5 w-5 animate-spin" />
                      Connexion en cours...
                    </>
                  ) : (
                    <>
                      <Sparkles className="mr-2 h-5 w-5" />
                      Se connecter
                    </>
                  )}
                </Button>
              </form>

              {/* Links */}
              <div className="mt-6 space-y-4 text-center">
                <div className="space-y-3">
                  <p className="text-gray-600 text-sm">
                    Pas encore de compte ?{' '}
                    <Link 
                      to="/inscription" 
                      className="text-orange-600 hover:text-orange-700 font-semibold hover:underline transition-colors"
                    >
                      Créer un compte
                    </Link>
                  </p>
                  
                  <p className="text-gray-600 text-sm">
                    Mot de passe oublié ?{' '}
                    <Link 
                      to="/mot-de-passe-oublie" 
                      className="text-orange-600 hover:text-orange-700 font-semibold hover:underline transition-colors"
                    >
                      Réinitialiser
                    </Link>
                  </p>
                </div>
                
                <div className="pt-4 border-t border-gray-200">
                  <p className="text-gray-500 text-xs">
                    Besoin d'aide ? Contactez-nous au{' '}
                    <span className="text-orange-600 font-semibold">01 23 45 67 89</span>
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Additional Info */}
          <div className="mt-6 text-center">
            <p className="text-white/80 text-sm max-w-md mx-auto">
              ✨ Votre espace sécurisé pour gérer vos rendez-vous et découvrir l'art du henné
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;