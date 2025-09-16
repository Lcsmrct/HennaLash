import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { AlertCircle, Loader2, ArrowLeft, Mail, Key } from 'lucide-react';
import { Alert, AlertDescription } from '../components/ui/alert';
import Navigation from '../components/Navigation';
import { apiService } from '../services/apiService';
import { toast } from '../hooks/use-toast';

const PasswordResetPage = () => {
  const navigate = useNavigate();
  const [step, setStep] = useState('request'); // 'request' or 'confirm'
  const [email, setEmail] = useState('');
  const [code, setCode] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleRequestReset = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      await apiService.requestPasswordReset(email);
      toast({
        title: "Code envoyé",
        description: "Si votre email existe, vous recevrez un code de réinitialisation sous peu."
      });
      setStep('confirm');
    } catch (error) {
      console.error('Password reset request error:', error);
      setError(error.response?.data?.detail || 'Erreur lors de l\'envoi du code');
    } finally {
      setLoading(false);
    }
  };

  const handleConfirmReset = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    // Validation
    if (newPassword !== confirmPassword) {
      setError('Les mots de passe ne correspondent pas');
      setLoading(false);
      return;
    }

    if (newPassword.length < 6) {
      setError('Le mot de passe doit contenir au moins 6 caractères');
      setLoading(false);
      return;
    }

    try {
      await apiService.confirmPasswordReset(email, code, newPassword);
      toast({
        title: "Succès",
        description: "Votre mot de passe a été réinitialisé avec succès !"
      });
      navigate('/connexion');
    } catch (error) {
      console.error('Password reset confirm error:', error);
      setError(error.response?.data?.detail || 'Code invalide ou expiré');
    } finally {
      setLoading(false);
    }
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
            backgroundImage: `url('https://images.unsplash.com/photo-1629332791128-58f00882964d?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2NzR8MHwxfHNlYXJjaHwxfHxoZW5uYSUyMGhhbmRzfGVufDB8fHx8MTc1NzI0ODk0MHww&ixlib=rb-4.1.0&q=85')`,
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
              to="/connexion" 
              className="inline-flex items-center gap-2 text-white/80 hover:text-white transition-colors group"
            >
              <ArrowLeft className="w-4 h-4 group-hover:-translate-x-1 transition-transform" />
              Retour à la connexion
            </Link>
          </div>

          {/* Reset Form */}
          <div className="bg-white/95 backdrop-blur-sm rounded-2xl shadow-2xl p-6 sm:p-8">
            <div className="text-center mb-6 sm:mb-8">
              <div className="flex justify-center mb-4">
                {step === 'request' ? (
                  <Mail className="w-12 h-12 text-orange-600" />
                ) : (
                  <Key className="w-12 h-12 text-orange-600" />
                )}
              </div>
              <h1 className="text-2xl sm:text-3xl font-bold text-gray-900 mb-2">
                {step === 'request' ? 'Mot de passe oublié' : 'Nouveau mot de passe'}
              </h1>
              <p className="text-sm sm:text-base text-gray-600">
                {step === 'request' 
                  ? 'Entrez votre email pour recevoir un code de réinitialisation'
                  : 'Entrez le code reçu par email et votre nouveau mot de passe'
                }
              </p>
            </div>

            {step === 'request' ? (
              <form onSubmit={handleRequestReset} className="space-y-4 sm:space-y-6">
                {error && (
                  <Alert variant="destructive" className="border-red-200 bg-red-50">
                    <AlertCircle className="h-4 w-4" />
                    <AlertDescription className="text-red-800 text-sm">{error}</AlertDescription>
                  </Alert>
                )}
                
                <div className="space-y-2">
                  <Label htmlFor="email" className="text-gray-700 font-medium text-sm sm:text-base">
                    Adresse email
                  </Label>
                  <Input
                    id="email"
                    name="email"
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="votre@email.com"
                    required
                    disabled={loading}
                    className="h-10 sm:h-12 border-gray-300 focus:border-orange-500 focus:ring-orange-500 rounded-lg text-sm sm:text-base"
                  />
                </div>
                
                <Button 
                  type="submit" 
                  disabled={loading}
                  className="w-full h-10 sm:h-12 bg-orange-600 hover:bg-orange-700 text-white font-semibold rounded-lg transition-all duration-300 transform hover:scale-105 shadow-lg disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none text-sm sm:text-base"
                >
                  {loading ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 sm:h-5 sm:w-5 animate-spin" />
                      Envoi en cours...
                    </>
                  ) : (
                    'Envoyer le code'
                  )}
                </Button>
              </form>
            ) : (
              <form onSubmit={handleConfirmReset} className="space-y-4 sm:space-y-6">
                {error && (
                  <Alert variant="destructive" className="border-red-200 bg-red-50">
                    <AlertCircle className="h-4 w-4" />
                    <AlertDescription className="text-red-800 text-sm">{error}</AlertDescription>
                  </Alert>
                )}
                
                <div className="space-y-2">
                  <Label htmlFor="code" className="text-gray-700 font-medium text-sm sm:text-base">
                    Code de réinitialisation
                  </Label>
                  <Input
                    id="code"
                    name="code"
                    type="text"
                    value={code}
                    onChange={(e) => setCode(e.target.value)}
                    placeholder="123456"
                    required
                    disabled={loading}
                    maxLength={6}
                    className="h-10 sm:h-12 border-gray-300 focus:border-orange-500 focus:ring-orange-500 rounded-lg text-sm sm:text-base text-center font-mono text-lg"
                  />
                  <p className="text-xs text-gray-500 text-center">
                    Code reçu par email (valable 15 minutes)
                  </p>
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="newPassword" className="text-gray-700 font-medium text-sm sm:text-base">
                    Nouveau mot de passe
                  </Label>
                  <Input
                    id="newPassword"
                    name="newPassword"
                    type="password"
                    value={newPassword}
                    onChange={(e) => setNewPassword(e.target.value)}
                    placeholder="••••••••"
                    required
                    disabled={loading}
                    minLength={6}
                    className="h-10 sm:h-12 border-gray-300 focus:border-orange-500 focus:ring-orange-500 rounded-lg text-sm sm:text-base"
                  />
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="confirmPassword" className="text-gray-700 font-medium text-sm sm:text-base">
                    Confirmer le mot de passe
                  </Label>
                  <Input
                    id="confirmPassword"
                    name="confirmPassword"
                    type="password"
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    placeholder="••••••••"
                    required
                    disabled={loading}
                    minLength={6}
                    className="h-10 sm:h-12 border-gray-300 focus:border-orange-500 focus:ring-orange-500 rounded-lg text-sm sm:text-base"
                  />
                </div>
                
                <Button 
                  type="submit" 
                  disabled={loading}
                  className="w-full h-10 sm:h-12 bg-orange-600 hover:bg-orange-700 text-white font-semibold rounded-lg transition-all duration-300 transform hover:scale-105 shadow-lg disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none text-sm sm:text-base"
                >
                  {loading ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 sm:h-5 sm:w-5 animate-spin" />
                      Réinitialisation...
                    </>
                  ) : (
                    'Réinitialiser le mot de passe'
                  )}
                </Button>

                <div className="text-center">
                  <button
                    type="button"
                    onClick={() => setStep('request')}
                    disabled={loading}
                    className="text-sm text-orange-600 hover:text-orange-700 underline disabled:opacity-50"
                  >
                    Renvoyer un nouveau code
                  </button>
                </div>
              </form>
            )}

            {/* Links */}
            <div className="mt-6 sm:mt-8 text-center">
              <p className="text-sm sm:text-base text-gray-600">
                Vous vous souvenez de votre mot de passe ?{' '}
                <Link 
                  to="/connexion" 
                  className="text-orange-600 hover:text-orange-700 font-semibold hover:underline transition-colors"
                >
                  Se connecter
                </Link>
              </p>
              
              <div className="pt-3 sm:pt-4 border-t border-gray-200 mt-4">
                <p className="text-xs sm:text-sm text-gray-500">
                  Besoin d'aide ? Contactez-nous au{' '}
                  <span className="text-orange-600 font-medium">01 23 45 67 89</span>
                </p>
              </div>
            </div>
          </div>

          {/* Additional Info */}
          <div className="mt-6 sm:mt-8 text-center">
            <p className="text-white/80 text-xs sm:text-sm">
              Le code de réinitialisation expire dans 15 minutes pour votre sécurité
            </p>
          </div>
        </div>
      </section>
    </div>
  );
};

export default PasswordResetPage;