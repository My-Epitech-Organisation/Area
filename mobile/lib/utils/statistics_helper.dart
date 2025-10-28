import '../models/applet.dart';

class StatisticsHelper {
  static Map<String, int> calculateStats(
    List<Applet>? applets,
    Map<String, dynamic>? executionsStats,
  ) {
    applets ??= [];
    executionsStats ??= {};

    return {
      'totalApplets': applets.length,
      'activeApplets': applets.where((a) => a.isActive).length,
      'totalExecutions': executionsStats['total'] ?? 0,
      'successfulExecutions': executionsStats['success'] ?? 0,
      'failedExecutions': executionsStats['failed'] ?? 0,
      'servicesCount': applets.isNotEmpty
          ? applets.map((a) => a.action.service.name).toSet().length
          : 0,
    };
  }

  static int getSuccessRatePercentage(int successful, int total) {
    if (total == 0) return 0;
    return ((successful / total) * 100).round();
  }

  static String getHealthStatus(int successful, int failed) {
    if (failed == 0) return 'healthy';
    if (successful > failed) return 'warning';
    return 'critical';
  }
}
