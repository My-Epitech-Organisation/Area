import 'package:flutter/material.dart';

class Execution {
  final int id;
  final int areaId;
  final String status; // "pending", "running", "success", "failed", "skipped"
  final DateTime createdAt;
  final DateTime? startedAt;
  final DateTime? completedAt;
  final Map<String, dynamic> triggerData;
  final Map<String, dynamic> resultData;
  final String? errorMessage;
  final int retryCount;
  final double? durationSeconds;

  Execution({
    required this.id,
    required this.areaId,
    required this.status,
    required this.createdAt,
    this.startedAt,
    this.completedAt,
    required this.triggerData,
    required this.resultData,
    this.errorMessage,
    required this.retryCount,
    this.durationSeconds,
  });

  factory Execution.fromJson(Map<String, dynamic> json) {
    try {
      return Execution(
        id: json['id'],
        areaId: json['area'],
        status: json['status'] ?? 'pending',
        createdAt: DateTime.parse(
          json['created_at'] ?? DateTime.now().toIso8601String(),
        ),
        startedAt: json['started_at'] != null
            ? DateTime.parse(json['started_at'])
            : null,
        completedAt: json['completed_at'] != null
            ? DateTime.parse(json['completed_at'])
            : null,
        triggerData: json['trigger_data'] ?? {},
        resultData: json['result_data'] ?? {},
        errorMessage: json['error_message'],
        retryCount: json['retry_count'] ?? 0,
        durationSeconds: json['duration_seconds'] != null
            ? (json['duration_seconds'] as num).toDouble()
            : null,
      );
    } catch (e, stackTrace) {
      debugPrint('❌ ERROR in Execution.fromJson: $e');
      debugPrint('📊 JSON data: $json');
      debugPrint('📚 Stack trace: $stackTrace');
      rethrow;
    }
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'area': areaId,
      'status': status,
      'created_at': createdAt.toIso8601String(),
      'started_at': startedAt?.toIso8601String(),
      'completed_at': completedAt?.toIso8601String(),
      'trigger_data': triggerData,
      'result_data': resultData,
      'error_message': errorMessage,
      'retry_count': retryCount,
      'duration_seconds': durationSeconds,
    };
  }

  // Get status color
  Color getStatusColor() {
    switch (status) {
      case 'success':
        return Colors.green;
      case 'failed':
        return Colors.red;
      case 'running':
        return Colors.blue;
      case 'pending':
        return Colors.orange;
      case 'skipped':
        return Colors.grey;
      default:
        return Colors.grey;
    }
  }

  // Get status icon
  IconData getStatusIcon() {
    switch (status) {
      case 'success':
        return Icons.check_circle;
      case 'failed':
        return Icons.error;
      case 'running':
        return Icons.hourglass_top;
      case 'pending':
        return Icons.pending;
      case 'skipped':
        return Icons.skip_next;
      default:
        return Icons.help;
    }
  }
}
