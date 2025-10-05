import 'package:flutter/material.dart';
import '../models/applet.dart';
import '../services/api_service.dart';

class AppState extends ChangeNotifier {
  final ApiService _apiService = ApiService();

  // Auth state
  bool _isAuthenticated = false;
  bool get isAuthenticated => _isAuthenticated;

  Map<String, dynamic>? _userProfile;
  Map<String, dynamic>? get userProfile => _userProfile;

  // Applets state
  List<Applet> _applets = [];
  List<Applet> get applets => _applets;

  bool _isLoadingApplets = false;
  bool get isLoadingApplets => _isLoadingApplets;

  String? _appletsError;
  String? get appletsError => _appletsError;

  // Statistics state
  Map<String, dynamic>? _statistics;
  Map<String, dynamic>? get statistics => _statistics;

  bool _isLoadingStats = false;
  bool get isLoadingStats => _isLoadingStats;

  // Services state
  List<Map<String, dynamic>> _availableServices = [];
  List<Map<String, dynamic>> get availableServices => _availableServices;

  bool _isLoadingServices = false;
  bool get isLoadingServices => _isLoadingServices;

  // Generic loading states
  bool _isLoading = false;
  bool get isLoading => _isLoading;

  String? _error;
  String? get error => _error;

  // Initialize app state
  Future<void> initialize() async {
    final token = await _apiService.authToken;
    if (token != null) {
      _isAuthenticated = true;
      await loadUserProfile();
      await loadApplets();
      await loadStatistics();
      await loadAvailableServices();
    }
    notifyListeners();
  }

  // Authentication methods
  Future<bool> login(String email, String password) async {
    try {
      _setLoading(true);
      await _apiService.login(email, password);
      _isAuthenticated = true;
      await loadUserProfile();
      await loadApplets();
      await loadStatistics();
      _setLoading(false);
      return true;
    } catch (e) {
      final errorMessage = 'Login failed: ${e.toString()}';
      _setError(errorMessage);
      // ignore: avoid_print
      print('[AppState] Login error: $errorMessage');
      return false;
    }
  }

  Future<bool> register(String email, String password, String name) async {
    try {
      _setLoading(true);
      await _apiService.register(email, password, name);
      await _apiService.login(email, password);
      _isAuthenticated = true;
      await loadUserProfile();
      await loadApplets();
      await loadStatistics();
      _setLoading(false);
      return true;
    } catch (e) {
      final errorMessage = 'Registration failed: ${e.toString()}';
      _setError(errorMessage);
      // ignore: avoid_print
      print('[AppState] Registration error: $errorMessage');
      return false;
    }
  }

  Future<void> logout() async {
    await _apiService.clearAuthToken();
    _isAuthenticated = false;
    _userProfile = null;
    _applets.clear();
    _statistics = null;
    _availableServices.clear();
    notifyListeners();
  }

  // Data loading methods
  Future<void> loadUserProfile() async {
    try {
      _userProfile = await _apiService.getUserProfile();
      notifyListeners();
    } catch (e) {
      _setError('Failed to load profile: ${e.toString()}');
    }
  }

  Future<void> loadApplets({bool forceRefresh = false}) async {
    try {
      _isLoadingApplets = true;
      _appletsError = null;
      notifyListeners();

      _applets = await _apiService.fetchApplets(forceRefresh: forceRefresh);

      _isLoadingApplets = false;
      notifyListeners();
    } catch (e) {
      _isLoadingApplets = false;
      _appletsError = e.toString();
      notifyListeners();
    }
  }

  Future<void> loadStatistics() async {
    try {
      _isLoadingStats = true;
      notifyListeners();

      _statistics = await _apiService.getStatistics();

      _isLoadingStats = false;
      notifyListeners();
    } catch (e) {
      _isLoadingStats = false;
      _setError('Failed to load statistics: ${e.toString()}');
    }
  }

  Future<void> loadAvailableServices() async {
    try {
      _isLoadingServices = true;
      notifyListeners();

      _availableServices = await _apiService.getAvailableServices();

      _isLoadingServices = false;
      notifyListeners();
    } catch (e) {
      _isLoadingServices = false;
      _setError('Failed to load services: ${e.toString()}');
    }
  }

  // Applet CRUD operations
  Future<bool> createApplet({
    required String name,
    required String description,
    required int actionId,
    required int reactionId,
    required Map<String, dynamic> actionConfig,
    required Map<String, dynamic> reactionConfig,
  }) async {
    try {
      _setLoading(true);
      final newApplet = await _apiService.createApplet(
        name: name,
        description: description,
        actionId: actionId,
        reactionId: reactionId,
        actionConfig: actionConfig,
        reactionConfig: reactionConfig,
      );

      // Optimistic update
      _applets.insert(0, newApplet);
      notifyListeners();

      // Refresh from server to ensure consistency
      await loadApplets(forceRefresh: true);
      _setLoading(false);
      return true;
    } catch (e) {
      _setError('Failed to create applet: ${e.toString()}');
      return false;
    }
  }

  Future<bool> updateApplet(int id, {
    String? name,
    String? description,
    String? status,
    Map<String, dynamic>? actionConfig,
    Map<String, dynamic>? reactionConfig,
  }) async {
    try {
      _setLoading(true);
      final updatedApplet = await _apiService.updateApplet(id,
        name: name,
        description: description,
        status: status,
        actionConfig: actionConfig,
        reactionConfig: reactionConfig,
      );

      // Update local state
      final index = _applets.indexWhere((a) => a.id == id);
      if (index != -1) {
        _applets[index] = updatedApplet;
      }
      notifyListeners();

      _setLoading(false);
      return true;
    } catch (e) {
      _setError('Failed to update applet: ${e.toString()}');
      return false;
    }
  }

  Future<bool> deleteApplet(int id) async {
    try {
      _setLoading(true);

      // Optimistic update
      _applets.removeWhere((a) => a.id == id);
      notifyListeners();

      await _apiService.deleteApplet(id);
      _setLoading(false);
      return true;
    } catch (e) {
      // Revert optimistic update on error
      await loadApplets(forceRefresh: true);
      _setError('Failed to delete applet: ${e.toString()}');
      return false;
    }
  }

  Future<bool> toggleApplet(int id) async {
    try {
      final updatedApplet = await _apiService.toggleApplet(id);

      // Update local state
      final index = _applets.indexWhere((a) => a.id == id);
      if (index != -1) {
        _applets[index] = updatedApplet;
        notifyListeners();
      }

      return true;
    } catch (e) {
      _setError('Failed to toggle applet: ${e.toString()}');
      return false;
    }
  }

  // Utility methods
  void _setLoading(bool loading) {
    _isLoading = loading;
    if (loading) _error = null;
    notifyListeners();
  }

  void _setError(String error) {
    _error = error;
    _isLoading = false;
    notifyListeners();
  }

  void clearError() {
    _error = null;
    notifyListeners();
  }

  // Computed properties
  int get activeAppletsCount => _applets.where((a) => a.isActive).length;
  int get totalAppletsCount => _applets.length;

  List<Applet> get activeApplets => _applets.where((a) => a.isActive).toList();
  List<Applet> get inactiveApplets => _applets.where((a) => !a.isActive).toList();

  Map<String, int> get appletsByTriggerService {
    final map = <String, int>{};
    for (final applet in _applets) {
      final serviceName = applet.action.service.name;
      map[serviceName] = (map[serviceName] ?? 0) + 1;
    }
    return map;
  }

  Map<String, int> get appletsByActionService {
    final map = <String, int>{};
    for (final applet in _applets) {
      final serviceName = applet.reaction.service.name;
      map[serviceName] = (map[serviceName] ?? 0) + 1;
    }
    return map;
  }
}