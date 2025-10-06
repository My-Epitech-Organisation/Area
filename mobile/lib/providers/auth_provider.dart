import 'package:flutter/material.dart';
import '../services/services.dart';

/// Provider gérant l'état d'authentification
class AuthProvider extends ChangeNotifier {
  final AuthService _authService = AuthService();

  // État
  bool _isAuthenticated = false;
  String? _error;
  String? _userEmail;
  bool _isLoading = false;

  // Getters
  bool get isAuthenticated => _isAuthenticated;
  String? get error => _error;
  String? get userEmail => _userEmail;
  bool get isLoading => _isLoading;

  // ============================================
  // VÉRIFICATION DU STATUT AUTH AU DÉMARRAGE
  // ============================================

  Future<void> checkAuthStatus() async {
    _isAuthenticated = await _authService.isAuthenticated();
    notifyListeners();
  }

  // ============================================
  // CONNEXION EMAIL/PASSWORD
  // ============================================

  Future<bool> login(String email, String password) async {
    try {
      _setLoading(true);
      _clearError();

      await _authService.loginWithEmail(
        email: email,
        password: password,
      );

      _isAuthenticated = true;
      _userEmail = email;
      _setLoading(false);
      return true;
    } on AuthException catch (e) {
      _setError(e.message);
      _setLoading(false);
      return false;
    } catch (e) {
      _setError('Login failed: ${e.toString()}');
      _setLoading(false);
      return false;
    }
  }

  // ============================================
  // INSCRIPTION
  // ============================================

  Future<bool> register({
    required String username,
    required String email,
    required String password,
    required String confirmPassword,
  }) async {
    try {
      _setLoading(true);
      _clearError();

      // Step 1: Register the user
      await _authService.registerWithEmail(
        username: username,
        email: email,
        password: password,
        confirmPassword: confirmPassword,
      );
      
      // Step 2: Automatically login to get tokens
      await _authService.loginWithEmail(
        email: email,
        password: password,
      );

      _isAuthenticated = true;
      _userEmail = email;
      _setLoading(false);
      return true;
    } on AuthException catch (e) {
      _setError(e.message);
      _setLoading(false);
      return false;
    } catch (e) {
      _setError('Registration failed: ${e.toString()}');
      _setLoading(false);
      return false;
    }
  }

  // ============================================
  // CONNEXION GOOGLE
  // ============================================

  Future<bool> loginWithGoogle() async {
    try {
      _setLoading(true);
      _clearError();

      final data = await _authService.loginWithGoogle();

      if (data != null) {
        _isAuthenticated = true;
        _userEmail = data['email'];
        _setLoading(false);
        return true;
      }

      _setError('Google sign-in failed');
      _setLoading(false);
      return false;
    } on AuthException catch (e) {
      _setError(e.message);
      _setLoading(false);
      return false;
    } catch (e) {
      _setError('Google sign-in error: ${e.toString()}');
      _setLoading(false);
      return false;
    }
  }

  // ============================================
  // DÉCONNEXION
  // ============================================

  Future<void> logout() async {
    await _authService.logout();
    _isAuthenticated = false;
    _userEmail = null;
    _error = null;
    notifyListeners();
  }

  // ============================================
  // HELPERS PRIVÉS
  // ============================================

  void _setLoading(bool value) {
    _isLoading = value;
    notifyListeners();
  }

  void _setError(String message) {
    _error = message;
    notifyListeners();
  }

  void _clearError() {
    _error = null;
    notifyListeners();
  }

  void clearError() {
    _clearError();
  }
}
