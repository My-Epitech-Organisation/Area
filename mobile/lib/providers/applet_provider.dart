import 'package:flutter/material.dart';
import 'package:collection/collection.dart';
import '../models/applet.dart';
import '../models/execution.dart';
import '../services/services.dart';

class AppletProvider extends ChangeNotifier {
  final AppletService _appletService = AppletService();

  List<Applet> _applets = [];
  bool _isLoading = false;
  String? _error;

  List<Applet> get applets => _applets;
  bool get isLoading => _isLoading;
  String? get error => _error;

  List<Applet> get activeApplets => _applets.where((a) => a.isActive).toList();
  List<Applet> get inactiveApplets =>
      _applets.where((a) => !a.isActive).toList();

  int get totalCount => _applets.length;
  int get activeCount => _applets.where((a) => a.isActive).length;

  Future<void> loadApplets({bool forceRefresh = false}) async {
    try {
      _isLoading = true;
      _error = null;
      notifyListeners();

      _applets = await _appletService.fetchApplets(forceRefresh: forceRefresh);

      _enrichApplets();

      _isLoading = false;
      notifyListeners();
    } catch (e) {
      _isLoading = false;
      _error = e.toString();
      notifyListeners();
    }
  }

  void _enrichApplets() {
    debugPrint('[APPLETS] 📊 Loaded: ${_applets.length} applets');
    for (final applet in _applets) {
      if (applet.action.name.contains('Unknown') ||
          applet.action.service.name.contains('Unknown')) {
        debugPrint(
          '[APPLETS]     ⚠️  Unknown action/service - needs enrichment',
        );
      }
    }
  }

  Future<bool> createApplet({
    required String description,
    required int actionId,
    required int reactionId,
    required Map<String, dynamic> actionConfig,
    required Map<String, dynamic> reactionConfig,
  }) async {
    try {
      _isLoading = true;
      _error = null;
      notifyListeners();

      final newApplet = await _appletService.createApplet(
        name: description,
        actionId: actionId,
        reactionId: reactionId,
        actionConfig: actionConfig,
        reactionConfig: reactionConfig,
      );

      _applets.insert(0, newApplet);
      _isLoading = false;
      notifyListeners();
      return true;
    } catch (e) {
      _isLoading = false;
      _error = e.toString();
      notifyListeners();
      return false;
    }
  }

  Future<bool> updateApplet(
    int id, {
    String? name,
    String? status,
    Map<String, dynamic>? actionConfig,
    Map<String, dynamic>? reactionConfig,
  }) async {
    try {
      _isLoading = true;
      _error = null;
      notifyListeners();

      final updatedApplet = await _appletService.updateApplet(
        id,
        name: name,
        status: status,
        actionConfig: actionConfig,
        reactionConfig: reactionConfig,
      );

      final index = _applets.indexWhere((a) => a.id == id);
      if (index != -1) {
        _applets[index] = updatedApplet;
      }

      _isLoading = false;
      notifyListeners();
      return true;
    } catch (e) {
      _isLoading = false;
      _error = e.toString();
      notifyListeners();
      return false;
    }
  }

  Future<bool> deleteApplet(int id) async {
    try {
      _isLoading = true;
      _error = null;
      notifyListeners();

      await _appletService.deleteApplet(id);
      _applets.removeWhere((a) => a.id == id);

      _isLoading = false;
      notifyListeners();
      return true;
    } catch (e) {
      _isLoading = false;
      _error = e.toString();
      notifyListeners();
      return false;
    }
  }

  Future<bool> toggleApplet(int id) async {
    try {
      // Check current status and toggle appropriately
      final applet = _applets.firstWhereOrNull((a) => a.id == id);

      if (applet == null) {
        _error = 'Applet not found';
        notifyListeners();
        return false;
      }

      if (applet.isActive) {
        // Pause if active
        return await pauseApplet(id);
      } else {
        // Resume if paused
        return await resumeApplet(id);
      }
    } catch (e) {
      _error = e.toString();
      notifyListeners();
      return false;
    }
  }

  Future<bool> duplicateApplet(int id, String newName) async {
    try {
      _isLoading = true;
      _error = null;
      notifyListeners();

      final duplicatedApplet = await _appletService.duplicateApplet(
        id,
        newName,
      );

      _applets.insert(0, duplicatedApplet);
      _isLoading = false;
      notifyListeners();
      return true;
    } catch (e) {
      _isLoading = false;
      _error = e.toString();
      notifyListeners();
      return false;
    }
  }

  Future<bool> pauseApplet(int id) async {
    try {
      final updatedApplet = await _appletService.pauseApplet(id);

      final index = _applets.indexWhere((a) => a.id == id);
      if (index != -1) {
        _applets[index] = updatedApplet;
        notifyListeners();
      }

      return true;
    } catch (e) {
      _error = e.toString();
      notifyListeners();
      return false;
    }
  }

  Future<bool> resumeApplet(int id) async {
    try {
      final updatedApplet = await _appletService.resumeApplet(id);

      final index = _applets.indexWhere((a) => a.id == id);
      if (index != -1) {
        _applets[index] = updatedApplet;
        notifyListeners();
      }

      return true;
    } catch (e) {
      _error = e.toString();
      notifyListeners();
      return false;
    }
  }

  Future<List<Execution>> getAppletExecutions(
    int areaId, {
    int limit = 50,
  }) async {
    try {
      return await _appletService.getAppletExecutions(areaId, limit: limit);
    } catch (e) {
      _error = e.toString();
      notifyListeners();
      return [];
    }
  }

  void clear() {
    _applets.clear();
    _error = null;
    _appletService.clearCache();
    notifyListeners();
  }

  void clearError() {
    _error = null;
    notifyListeners();
  }
}
