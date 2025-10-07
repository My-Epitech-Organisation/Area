import 'package:flutter/material.dart';
import '../services/services.dart';

class UserProvider extends ChangeNotifier {
  final UserService _userService = UserService();

  Map<String, dynamic>? _profile;
  Map<String, dynamic>? _statistics;
  
  bool _isLoadingProfile = false;
  bool _isLoadingStats = false;
  String? _error;

  Map<String, dynamic>? get profile => _profile;
  Map<String, dynamic>? get statistics => _statistics;
  bool get isLoadingProfile => _isLoadingProfile;
  bool get isLoadingStats => _isLoadingStats;
  String? get error => _error;

  Future<void> loadProfile({bool forceRefresh = false}) async {
    try {
      _isLoadingProfile = true;
      _error = null;
      notifyListeners();

      _profile = await _userService.getUserProfile(forceRefresh: forceRefresh);

      _isLoadingProfile = false;
      notifyListeners();
    } catch (e) {
      _isLoadingProfile = false;
      _error = e.toString();
      notifyListeners();
    }
  }

  Future<void> loadStatistics({bool forceRefresh = false}) async {
    try {
      _isLoadingStats = true;
      _error = null;
      notifyListeners();

      _statistics = await _userService.getUserStatistics(forceRefresh: forceRefresh);

      _isLoadingStats = false;
      notifyListeners();
    } catch (e) {
      _isLoadingStats = false;
      _error = e.toString();
      notifyListeners();
    }
  }

  void clear() {
    _profile = null;
    _statistics = null;
    _error = null;
    _userService.clearCache();
    notifyListeners();
  }

  void clearError() {
    _error = null;
    notifyListeners();
  }
}
