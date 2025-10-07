import 'package:flutter/material.dart';
import '../models/applet.dart';
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
  List<Applet> get inactiveApplets => _applets.where((a) => !a.isActive).toList();
  
  int get totalCount => _applets.length;
  int get activeCount => _applets.where((a) => a.isActive).length;

  Future<void> loadApplets({bool forceRefresh = false}) async {
    try {
      _isLoading = true;
      _error = null;
      notifyListeners();

      _applets = await _appletService.fetchApplets(forceRefresh: forceRefresh);

      _isLoading = false;
      notifyListeners();
    } catch (e) {
      _isLoading = false;
      _error = e.toString();
      notifyListeners();
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
        description: description,
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
    String? description,
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
        description: description,
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
      final updatedApplet = await _appletService.toggleApplet(id);

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
