import 'package:flutter/material.dart';
import '../services/services.dart';
import '../models/service.dart';

class ServiceCatalogProvider extends ChangeNotifier {
  final ServiceCatalogService _catalogService = ServiceCatalogService();

  List<Service> _services = [];
  final Map<String, List<ServiceAction>> _actionsCache = {};
  final Map<String, List<ServiceReaction>> _reactionsCache = {};
  final Map<String, int> _actionIdsCache = {}; // name -> id
  final Map<String, int> _reactionIdsCache = {}; // name -> id

  bool _isLoadingServices = false;
  String? _error;

  List<Service> get services => _services;
  bool get isLoadingServices => _isLoadingServices;
  String? get error => _error;

  List<ServiceAction>? getActionsForService(String serviceName) {
    return _actionsCache[serviceName];
  }

  List<ServiceReaction>? getReactionsForService(String serviceName) {
    return _reactionsCache[serviceName];
  }

  int? getActionId(String actionName) {
    return _actionIdsCache[actionName];
  }

  int? getReactionId(String reactionName) {
    return _reactionIdsCache[reactionName];
  }

  ServiceAction? getAction(String actionName) {
    for (final actions in _actionsCache.values) {
      for (final action in actions) {
        if (action.name == actionName) {
          return action;
        }
      }
    }
    return null;
  }

  ServiceReaction? getReaction(String reactionName) {
    for (final reactions in _reactionsCache.values) {
      for (final reaction in reactions) {
        if (reaction.name == reactionName) {
          return reaction;
        }
      }
    }
    return null;
  }

  Future<void> loadServices({bool forceRefresh = false}) async {
    try {
      _isLoadingServices = true;
      _error = null;
      notifyListeners();

      _services = await _catalogService.getAvailableServices(
        forceRefresh: forceRefresh,
      );

      for (final service in _services) {
        _actionsCache[service.name] = service.actions;
        _reactionsCache[service.name] = service.reactions;

        for (final action in service.actions) {
          _actionIdsCache[action.name] = action.id;
        }
        for (final reaction in service.reactions) {
          _reactionIdsCache[reaction.name] = reaction.id;
        }
      }

      _isLoadingServices = false;
      notifyListeners();
    } catch (e) {
      _isLoadingServices = false;
      _error = e.toString();
      notifyListeners();
    }
  }

  void clear() {
    _services.clear();
    _actionsCache.clear();
    _reactionsCache.clear();
    _actionIdsCache.clear();
    _reactionIdsCache.clear();
    _error = null;
    _catalogService.clearCache();
    notifyListeners();
  }

  void clearError() {
    _error = null;
    notifyListeners();
  }
}
