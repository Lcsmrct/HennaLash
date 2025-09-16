import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { Navigate, Link } from 'react-router-dom';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Card, CardContent, CardFooter } from '../components/ui/card';
import { AlertCircle, Loader2, CheckCircle, ArrowLeft, Eye, EyeOff, Mail, Lock, User, Phone, Sparkles, Heart } from 'lucide-react';
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
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);

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
      <div className="min-h-screen relative overflow-hidden">
        <Navigation />
        
        {/* Background */}
        <div className="absolute inset-0">
          <div 
            className="absolute inset-0 bg-cover bg-center bg-no-repeat"
            style={{
              backgroundImage: `url('https://images.unsplash.com/photo-1623217509141-6f735087b50c?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2Njl8MHwxfHNlYXJjaHwyfHxoZW5uYSUyMGhhbmRzfGVufDB8fHx8MTc1ODA1NjQyMHww&ixlib=rb-4.1.0&q=85')`,
            }}
          />
          <div className="absolute inset-0 bg-gradient-to-br from-green-900/80 via-emerald-900/70 to-teal-800/80"></div>
        </div>

        <div className="relative z-10 min-h-screen flex items-center justify-center px-4 pt-16">
          <div className="w-full max-w-md">
            <div className="bg-white/95 backdrop-blur-lg rounded-3xl shadow-2xl border border-white/20 overflow-hidden text-center">
              {/* Success Header */}
              <div className="bg-gradient-to-r from-green-500 to-emerald-500 px-8 py-6">
                <div className="flex justify-center mb-3">
                  <div className="w-16 h-16 bg-white/20 rounded-full flex items-center justify-center animate-pulse">
                    <CheckCircle className="w-8 h-8 text-white" />
                  </div>
                </div>
                <h1 className="text-2xl font-bold text-white mb-1">Bienvenue !</h1>
                <p className="text-white/90 text-sm">Votre compte a été créé avec succès</p>
              </div>
              
              {/* Success Content */}
              <div className="px-8 py-8">
                <div className="space-y-4 mb-8">
                  <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center mx-auto">
                    <Heart className="w-6 h-6 text-green-600" />
                  </div>
                  <p className="text-gray-600">
                    Félicitations ! Vous faites maintenant partie de notre communauté.
                    Vous pouvez dès maintenant vous connecter et réserver vos rendez-vous.
                  </p>
                </div>
                
                <Link to="/connexion" className="w-full block">
                  <Button className="w-full h-12 bg-gradient-to-r from-green-500 to-emerald-500 hover:from-green-600 hover:to-emerald-600 text-white font-semibold rounded-xl transition-all duration-300 transform hover:scale-[1.02] shadow-lg hover:shadow-xl">
                    <Sparkles className="mr-2 h-5 w-5" />
                    Se connecter maintenant
                  </Button>
                </Link>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen relative overflow-hidden">
      <Navigation />
      
      {/* Background */}
      <div className="absolute inset-0">
        <div 
          className="absolute inset-0 bg-cover bg-center bg-no-repeat"
          style={{
            backgroundImage: `url('https://images.unsplash.com/photo-1623217509141-6f735087b50c?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2Njl8MHwxfHNlYXJjaHwyfHxoZW5uYSUyMGhhbmRzfGVufDB8fHx8MTc1ODA1NjQyMHww&ixlib=rb-4.1.0&q=85')`,
          }}
        />
        <div className="absolute inset-0 bg-gradient-to-br from-purple-900/80 via-indigo-900/70 to-purple-800/80"></div>
        
        {/* Decorative Elements */}
        <div className="absolute inset-0 opacity-10">
          <div className="absolute top-32 right-20 w-40 h-40 border border-white/20 rounded-full"></div>
          <div className="absolute bottom-32 left-20 w-28 h-28 border border-white/20 rounded-full"></div>
          <div className="absolute top-1/3 left-1/3 w-20 h-20 border border-white/20 rounded-full"></div>
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

          {/* Registration Card */}
          <Card className="bg-white/95 backdrop-blur-lg rounded-3xl shadow-2xl border border-white/20 overflow-hidden">
            {/* Header */}
            <div className="bg-gradient-to-r from-purple-500 to-indigo-500 px-8 py-6 text-center">
              <div className="flex justify-center mb-3">
                <div className="w-12 h-12 bg-white/20 rounded-full flex items-center justify-center">
                  <User className="w-6 h-6 text-white" />
                </div>
              </div>
              <h1 className="text-2xl font-bold text-white mb-1">Rejoignez-nous !</h1>
              <p className="text-white/90 text-sm">Créez votre compte pour réserver en ligne</p>
            </div>

            <CardContent className="px-8 py-8">
              <form onSubmit={handleSubmit} className="space-y-5">
                {error && (
                  <Alert variant="destructive" className="border-red-200 bg-red-50/50 backdrop-blur-sm">
                    <AlertCircle className="h-4 w-4" />
                    <AlertDescription className="text-red-800 text-sm font-medium">{error}</AlertDescription>
                  </Alert>
                )}
                
                {/* Name Fields */}
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="first_name" className="text-gray-700 font-semibold text-sm flex items-center gap-2">
                      <User className="w-4 h-4 text-purple-500" />
                      Prénom
                    </Label>
                    <div className="relative">
                      <Input
                        id="first_name"
                        name="first_name"
                        value={formData.first_name}
                        onChange={handleChange}
                        placeholder="Prénom"
                        required
                        disabled={loading}
                        className="h-11 pl-11 pr-4 border-2 border-gray-200 focus:border-purple-400 focus:ring-purple-400/20 rounded-xl text-sm transition-all duration-200 bg-white/80 backdrop-blur-sm"
                      />
                      <User className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
                    </div>
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="last_name" className="text-gray-700 font-semibold text-sm flex items-center gap-2">
                      <User className="w-4 h-4 text-purple-500" />
                      Nom
                    </Label>
                    <div className="relative">
                      <Input
                        id="last_name"
                        name="last_name"
                        value={formData.last_name}
                        onChange={handleChange}
                        placeholder="Nom"
                        required
                        disabled={loading}
                        className="h-11 pl-11 pr-4 border-2 border-gray-200 focus:border-purple-400 focus:ring-purple-400/20 rounded-xl text-sm transition-all duration-200 bg-white/80 backdrop-blur-sm"
                      />
                      <User className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
                    </div>
                  </div>
                </div>
                
                {/* Email Field */}
                <div className="space-y-2">
                  <Label htmlFor="email" className="text-gray-700 font-semibold text-sm flex items-center gap-2">
                    <Mail className="w-4 h-4 text-purple-500" />
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
                      className="h-11 pl-11 pr-4 border-2 border-gray-200 focus:border-purple-400 focus:ring-purple-400/20 rounded-xl text-sm transition-all duration-200 bg-white/80 backdrop-blur-sm"
                    />
                    <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
                  </div>
                </div>
                
                {/* Phone Field */}
                <div className="space-y-2">
                  <Label htmlFor="phone" className="text-gray-700 font-semibold text-sm flex items-center gap-2">
                    <Phone className="w-4 h-4 text-purple-500" />
                    Téléphone <span className="text-gray-400 text-xs">(optionnel)</span>
                  </Label>
                  <div className="relative">
                    <Input
                      id="phone"
                      name="phone"
                      type="tel"
                      value={formData.phone}
                      onChange={handleChange}
                      placeholder="+33 1 23 45 67 89"
                      disabled={loading}
                      className="h-11 pl-11 pr-4 border-2 border-gray-200 focus:border-purple-400 focus:ring-purple-400/20 rounded-xl text-sm transition-all duration-200 bg-white/80 backdrop-blur-sm"
                    />
                    <Phone className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
                  </div>
                </div>
                
                {/* Password Fields */}
                <div className="grid grid-cols-1 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="password" className="text-gray-700 font-semibold text-sm flex items-center gap-2">
                      <Lock className="w-4 h-4 text-purple-500" />
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
                        className="h-11 pl-11 pr-11 border-2 border-gray-200 focus:border-purple-400 focus:ring-purple-400/20 rounded-xl text-sm transition-all duration-200 bg-white/80 backdrop-blur-sm"
                      />
                      <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
                      <button
                        type="button"
                        onClick={() => setShowPassword(!showPassword)}
                        className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600 transition-colors"
                      >
                        {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                      </button>
                    </div>
                  </div>
                  
                  <div className="space-y-2">
                    <Label htmlFor="confirmPassword" className="text-gray-700 font-semibold text-sm flex items-center gap-2">
                      <Lock className="w-4 h-4 text-purple-500" />
                      Confirmer le mot de passe
                    </Label>
                    <div className="relative">
                      <Input
                        id="confirmPassword"
                        name="confirmPassword"
                        type={showConfirmPassword ? "text" : "password"}
                        value={formData.confirmPassword}
                        onChange={handleChange}
                        placeholder="••••••••"
                        required
                        disabled={loading}
                        className="h-11 pl-11 pr-11 border-2 border-gray-200 focus:border-purple-400 focus:ring-purple-400/20 rounded-xl text-sm transition-all duration-200 bg-white/80 backdrop-blur-sm"
                      />
                      <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
                      <button
                        type="button"
                        onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                        className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600 transition-colors"
                      >
                        {showConfirmPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                      </button>
                    </div>
                  </div>
                </div>
                
                <Button 
                  type="submit" 
                  className="w-full h-12 bg-gradient-to-r from-purple-500 to-indigo-500 hover:from-purple-600 hover:to-indigo-600 text-white font-semibold rounded-xl transition-all duration-300 transform hover:scale-[1.02] shadow-lg hover:shadow-xl text-base" 
                  disabled={loading}
                >
                  {loading ? (
                    <>
                      <Loader2 className="mr-3 h-5 w-5 animate-spin" />
                      Création du compte...
                    </>
                  ) : (
                    <>
                      <Sparkles className="mr-2 h-5 w-5" />
                      Créer mon compte
                    </>
                  )}
                </Button>
              </form>
            </CardContent>
            
            <CardFooter className="flex flex-col space-y-3 px-8 pb-8 border-t border-gray-100">
              <p className="text-sm text-gray-600 text-center">
                Déjà un compte ?{' '}
                <Link to="/connexion" className="text-purple-600 hover:text-purple-700 font-semibold hover:underline transition-colors">
                  Se connecter
                </Link>
              </p>
              <p className="text-xs text-gray-500 text-center">
                En créant un compte, vous acceptez nos conditions d'utilisation
              </p>
            </CardFooter>
          </Card>

          {/* Additional Info */}
          <div className="mt-6 text-center">
            <p className="text-white/80 text-sm max-w-md mx-auto">
              ✨ Rejoignez notre communauté et découvrez l'art ancestral du henné
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default RegisterPage;