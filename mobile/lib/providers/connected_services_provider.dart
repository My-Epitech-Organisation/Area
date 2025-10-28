import 'package:flutter/material.dart';
import '../services/oauth_service.dart';
import '../models/service_token.dart';
import '../utils/service_token_mapper.dart';

/// Provider for managing connected OAuth services
class ConnectedServicesProvider extends ChangeNotifier {
  final OAuthService _oauthService = OAuthService();

  List<ServiceToken> _connectedServices = [];
  List<String> _availableProviders = [];
  bool _isLoading = false;
  String? _error;

  List<ServiceToken> get connectedServices => _connectedServices;
  List<String> get availableProviders => _availableProviders;
  bool get isLoading => _isLoading;
  String? get error => _error;

  /// Check if a specific service is connected
  /// Maps service names (e.g., gmail -> google) to find the actual token
  bool isServiceConnected(String serviceName) {
    final tokenName = ServiceTokenMapper.resolveTokenService(serviceName);
    return _connectedServices.any(
      (s) => s.serviceName.toLowerCase() == tokenName.toLowerCase(),
    );
  }

  /// Get connected service names
  List<String> get connectedServiceNames {
    return _connectedServices.map((s) => s.serviceName.toLowerCase()).toList();
  }

  /// Load connected services from API
  Future<void> loadConnectedServices({bool forceRefresh = false}) async {
    try {
      _isLoading = true;
      _error = null;
      notifyListeners();

      final serviceList = await _oauthService.getConnectedServices();

      _connectedServices = serviceList.connectedServices;
      _availableProviders = serviceList.availableProviders;
      _isLoading = false;
      notifyListeners();
    } catch (e) {
      _isLoading = false;
      _error = e.toString();
      notifyListeners();
    }
  }

  /// Disconnect a service
  Future<bool> disconnectService(String provider) async {
    try {
      await _oauthService.disconnectService(provider);
      await loadConnectedServices(forceRefresh: true);
      return true;
    } catch (e) {
      _error = e.toString();
      notifyListeners();
      return false;
    }
  }

  void clearError() {
    _error = null;
    notifyListeners();
  }
}
