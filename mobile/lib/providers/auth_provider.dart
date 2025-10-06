import 'package:flutter/material.dart';
import '../services/auth_service.dart';

class AuthProvider extends ChangeNotifier {
  final AuthService _authService = AuthService();

  bool _isAuthenticated = false;
  String? _error;
  String? _userEmail;

  bool get isAuthenticated => _isAuthenticated;
  String? get error => _error;
  String? get userEmail => _userEmail;

  // Check if user is already authenticated on app start
  Future<void> checkAuthStatus() async {
    final token = await _authService.getAuthToken();
    _isAuthenticated = token != null;
    notifyListeners();
  }

  Future<bool> login(String email, String password) async {
    try {
      _error = null;
      final data = await _authService.loginWithEmail(email, password);

      if (data != null && data['access'] != null) {
        await _authService.setAuthToken(data['access']);
        if (data['refresh'] != null) {
          await _authService.setRefreshToken(data['refresh']);
        }
        _isAuthenticated = true;
        _userEmail = email;
        notifyListeners();
        return true;
      }

      _error = 'Invalid credentials';
      notifyListeners();
      return false;
    } catch (e) {
      _error = 'Login failed: ${e.toString()}';
      notifyListeners();
      return false;
    }
  }

  Future<bool> loginWithGoogle() async {
    try {
      _error = null;
      final data = await _authService.loginWithGoogle();

      if (data != null && data['access'] != null) {
        await _authService.setAuthToken(data['access']);
        if (data['refresh'] != null) {
          await _authService.setRefreshToken(data['refresh']);
        }
        _isAuthenticated = true;
        _userEmail = data['email'];
        notifyListeners();
        return true;
      }

      _error = 'Google sign-in failed';
      notifyListeners();
      return false;
    } catch (e) {
      _error = 'Google sign-in error: ${e.toString()}';
      notifyListeners();
      return false;
    }
  }

  Future<void> logout() async {
    await _authService.clearAuthToken();
    _isAuthenticated = false;
    _userEmail = null;
    _error = null;
    notifyListeners();
  }

  void clearError() {
    _error = null;
    notifyListeners();
  }
}
