import 'package:flutter/material.dart';
import '../services/services.dart';

class ServiceCatalogProvider extends ChangeNotifier {
  final ServiceCatalogService _catalogService = ServiceCatalogService();

  List<Map<String, dynamic>> _services = [];
  final Map<int, List<Map<String, dynamic>>> _actionsCache = {};
  final Map<int, List<Map<String, dynamic>>> _reactionsCache = {};

  bool _isLoadingServices = false;
  bool _isLoadingActions = false;
  bool _isLoadingReactions = false;
  String? _error;

  List<Map<String, dynamic>> get services => _services;
  bool get isLoadingServices => _isLoadingServices;
  bool get isLoadingActions => _isLoadingActions;
  bool get isLoadingReactions => _isLoadingReactions;
  String? get error => _error;

  List<Map<String, dynamic>>? getActionsForService(int serviceId) {
    return _actionsCache[serviceId];
  }

  List<Map<String, dynamic>>? getReactionsForService(int serviceId) {
    return _reactionsCache[serviceId];
  }

  Future<void> loadServices({bool forceRefresh = false}) async {
    try {
      _isLoadingServices = true;
      _error = null;
      notifyListeners();

      _services = await _catalogService.getAvailableServices(
        forceRefresh: forceRefresh,
      );

      _isLoadingServices = false;
      notifyListeners();
    } catch (e) {
      _isLoadingServices = false;
      _error = e.toString();
      notifyListeners();
    }
  }

  Future<void> loadActionsForService(
    int serviceId, {
    bool forceRefresh = false,
  }) async {
    try {
      _isLoadingActions = true;
      _error = null;
      notifyListeners();

      final actions = await _catalogService.getServiceActions(
        serviceId,
        forceRefresh: forceRefresh,
      );
      _actionsCache[serviceId] = actions;

      _isLoadingActions = false;
      notifyListeners();
    } catch (e) {
      _isLoadingActions = false;
      _error = e.toString();
      notifyListeners();
    }
  }

  Future<void> loadReactionsForService(
    int serviceId, {
    bool forceRefresh = false,
  }) async {
    try {
      _isLoadingReactions = true;
      _error = null;
      notifyListeners();

      final reactions = await _catalogService.getServiceReactions(
        serviceId,
        forceRefresh: forceRefresh,
      );
      _reactionsCache[serviceId] = reactions;

      _isLoadingReactions = false;
      notifyListeners();
    } catch (e) {
      _isLoadingReactions = false;
      _error = e.toString();
      notifyListeners();
    }
  }

  void clear() {
    _services.clear();
    _actionsCache.clear();
    _reactionsCache.clear();
    _error = null;
    _catalogService.clearCache();
    notifyListeners();
  }

  void clearError() {
    _error = null;
    notifyListeners();
  }
}
