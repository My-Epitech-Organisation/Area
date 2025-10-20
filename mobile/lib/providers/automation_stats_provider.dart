import 'package:flutter/material.dart';
import '../services/automation_stats_service.dart';

class AutomationStatsProvider extends ChangeNotifier {
  final AutomationStatsService _statsService = AutomationStatsService();

  Map<String, dynamic>? _areasStats;
  Map<String, dynamic>? _executionsStats;

  bool _isLoadingAreas = false;
  bool _isLoadingExecutions = false;
  String? _error;

  Map<String, dynamic>? get areasStats => _areasStats;
  Map<String, dynamic>? get executionsStats => _executionsStats;
  bool get isLoadingAreas => _isLoadingAreas;
  bool get isLoadingExecutions => _isLoadingExecutions;
  bool get isLoading => _isLoadingAreas || _isLoadingExecutions;
  String? get error => _error;

  Future<void> loadAreasStats({bool forceRefresh = false}) async {
    try {
      _isLoadingAreas = true;
      _error = null;
      notifyListeners();

      _areasStats = await _statsService.getAreasStats(
        forceRefresh: forceRefresh,
      );

      _isLoadingAreas = false;
      notifyListeners();
    } catch (e) {
      _isLoadingAreas = false;
      _error = e.toString();
      notifyListeners();
    }
  }

  Future<void> loadExecutionsStats({bool forceRefresh = false}) async {
    try {
      _isLoadingExecutions = true;
      _error = null;
      notifyListeners();

      _executionsStats = await _statsService.getExecutionsStats(
        forceRefresh: forceRefresh,
      );

      _isLoadingExecutions = false;
      notifyListeners();
    } catch (e) {
      _isLoadingExecutions = false;
      _error = e.toString();
      notifyListeners();
    }
  }

  Future<void> loadAllStats({bool forceRefresh = false}) async {
    await Future.wait([
      loadAreasStats(forceRefresh: forceRefresh),
      loadExecutionsStats(forceRefresh: forceRefresh),
    ]);
  }
}
