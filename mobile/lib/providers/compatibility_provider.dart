import 'package:flutter/foundation.dart';
import 'dart:convert';
import '../services/http_client_service.dart';
import '../config/api_config.dart';

/// Provider for managing action-reaction compatibility rules
/// Loads rules dynamically from the backend on first use and caches them
class CompatibilityProvider extends ChangeNotifier {
  Map<String, List<String>> _rules = {};
  bool _isLoaded = false;
  bool _isLoading = false;
  String? _error;

  final HttpClientService _httpClient = HttpClientService();

  /// Get all compatibility rules
  Map<String, List<String>> get rules => _rules;

  /// Check if rules are loaded
  bool get isLoaded => _isLoaded;

  /// Check if rules are currently loading
  bool get isLoading => _isLoading;

  /// Get any error message
  String? get error => _error;

  /// Initialize and load rules from backend (can be called multiple times safely)
  Future<void> loadRules() async {
    if (_isLoaded) {
      return;
    }

    if (_isLoading) {
      return;
    }

    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      final response = await _httpClient.get(
        '${ApiConfig.baseUrl}/api/compatibility-rules/',
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body) as Map<String, dynamic>;

        _rules = {};
        data.forEach((key, value) {
          if (value is List) {
            _rules[key] = List<String>.from(value);
          }
        });

        _isLoaded = true;
      } else {
        throw Exception(
          'Failed to load compatibility rules: ${response.statusCode}',
        );
      }
    } catch (e) {
      _error = 'Failed to load compatibility rules: $e';
      debugPrint('[CompatibilityProvider] Error: $_error');
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  /// Get compatible reactions for an action
  List<String> getCompatibleReactions(
    String actionName,
    List<String> allReactions,
  ) {
    if (!_isLoaded) {
      return allReactions;
    }

    final compatible = _rules[actionName] ?? [];

    // If "*" is in the rules, return all reactions
    if (compatible.contains("*")) {
      return allReactions;
    }

    // Otherwise filter to only compatible ones
    return allReactions
        .where((reaction) => compatible.contains(reaction))
        .toList();
  }

  /// Check if a reaction is compatible with an action
  bool isCompatible(String actionName, String reactionName) {
    if (!_isLoaded) {
      return true;
    }

    final compatible = _rules[actionName] ?? [];
    if (compatible.contains("*")) return true;
    return compatible.contains(reactionName);
  }

  /// Refresh rules from backend
  Future<void> refreshRules() async {
    _isLoaded = false;
    _rules = {};
    _error = null;
    await loadRules();
  }
}
