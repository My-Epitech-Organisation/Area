import 'package:flutter/material.dart';
import '../models/execution.dart';

/// Shows detailed information about an execution in a bottom sheet
void showExecutionDetailsBottomSheet(BuildContext context, Execution execution) {
  showModalBottomSheet(
    context: context,
    builder: (BuildContext context) {
      return ExecutionDetailsBottomSheet(execution: execution);
    },
    shape: const RoundedRectangleBorder(
      borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
    ),
    isScrollControlled: true,
  );
}

class ExecutionDetailsBottomSheet extends StatelessWidget {
  final Execution execution;

  const ExecutionDetailsBottomSheet({
    super.key,
    required this.execution,
  });

  @override
  Widget build(BuildContext context) {
    return DraggableScrollableSheet(
      expand: false,
      initialChildSize: 0.7,
      maxChildSize: 0.95,
      minChildSize: 0.5,
      builder: (context, scrollController) {
        return SingleChildScrollView(
          controller: scrollController,
          child: Container(
            padding: const EdgeInsets.all(24),
            decoration: const BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              mainAxisSize: MainAxisSize.min,
              children: [
                // Handle bar
                Center(
                  child: Container(
                    width: 40,
                    height: 4,
                    margin: const EdgeInsets.only(bottom: 16),
                    decoration: BoxDecoration(
                      color: Colors.grey.shade300,
                      borderRadius: BorderRadius.circular(2),
                    ),
                  ),
                ),

                // Header with status
                Row(
                  children: [
                    Icon(
                      execution.getStatusIcon(),
                      color: execution.getStatusColor(),
                      size: 32,
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            'Execution ${execution.id}',
                            style: const TextStyle(
                              fontSize: 20,
                              fontWeight: FontWeight.bold,
                              color: Colors.black87,
                            ),
                          ),
                          Text(
                            execution.status.toUpperCase(),
                            style: TextStyle(
                              fontSize: 14,
                              color: execution.getStatusColor(),
                              fontWeight: FontWeight.w600,
                            ),
                          ),
                        ],
                      ),
                    ),
                    IconButton(
                      onPressed: () => Navigator.pop(context),
                      icon: const Icon(Icons.close),
                    ),
                  ],
                ),
                const SizedBox(height: 24),

                // Details grid
                _buildDetailRow('Status', execution.status),
                const SizedBox(height: 12),
                _buildDetailRow(
                  'Created',
                  _formatDateTime(execution.createdAt),
                ),
                const SizedBox(height: 12),
                if (execution.startedAt != null)
                  _buildDetailRow(
                    'Started',
                    _formatDateTime(execution.startedAt!),
                  ),
                if (execution.startedAt != null) const SizedBox(height: 12),
                if (execution.completedAt != null)
                  _buildDetailRow(
                    'Completed',
                    _formatDateTime(execution.completedAt!),
                  ),
                if (execution.completedAt != null) const SizedBox(height: 12),
                if (execution.durationSeconds != null)
                  _buildDetailRow(
                    'Duration',
                    '${execution.durationSeconds!.toStringAsFixed(2)}s',
                  ),
                if (execution.durationSeconds != null) const SizedBox(height: 12),
                _buildDetailRow('Retry Count', execution.retryCount.toString()),
                const SizedBox(height: 24),

                // Error section (if any)
                if (execution.errorMessage != null) ...[
                  const Divider(),
                  const SizedBox(height: 12),
                  const Text(
                    'Error Details',
                    style: TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.bold,
                      color: Colors.red,
                    ),
                  ),
                  const SizedBox(height: 8),
                  Container(
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: Colors.red.shade50,
                      borderRadius: BorderRadius.circular(8),
                      border: Border.all(color: Colors.red.shade200),
                    ),
                    child: Text(
                      execution.errorMessage!,
                      style: TextStyle(
                        fontSize: 13,
                        color: Colors.red.shade700,
                        height: 1.5,
                      ),
                    ),
                  ),
                  const SizedBox(height: 24),
                ],

                // Trigger data section
                if (execution.triggerData.isNotEmpty) ...[
                  const Divider(),
                  const SizedBox(height: 12),
                  const Text(
                    'Trigger Data',
                    style: TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.bold,
                      color: Colors.black87,
                    ),
                  ),
                  const SizedBox(height: 8),
                  _buildDataSection(execution.triggerData),
                  const SizedBox(height: 24),
                ],

                // Result data section
                if (execution.resultData.isNotEmpty) ...[
                  const Divider(),
                  const SizedBox(height: 12),
                  const Text(
                    'Result Data',
                    style: TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.bold,
                      color: Colors.black87,
                    ),
                  ),
                  const SizedBox(height: 8),
                  _buildDataSection(execution.resultData),
                  const SizedBox(height: 24),
                ],
              ],
            ),
          ),
        );
      },
    );
  }

  Widget _buildDetailRow(String label, String value) {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        SizedBox(
          width: 100,
          child: Text(
            label,
            style: TextStyle(
              fontSize: 13,
              color: Colors.grey.shade600,
              fontWeight: FontWeight.w500,
            ),
          ),
        ),
        Expanded(
          child: Text(
            value,
            style: const TextStyle(
              fontSize: 13,
              color: Colors.black87,
              fontWeight: FontWeight.w600,
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildDataSection(Map<String, dynamic> data) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Colors.grey.shade50,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: Colors.grey.shade200),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: data.entries
            .map(
              (entry) => Padding(
                padding: const EdgeInsets.symmetric(vertical: 4),
                child: Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Expanded(
                      flex: 1,
                      child: Text(
                        '${entry.key}:',
                        style: TextStyle(
                          fontSize: 12,
                          color: Colors.grey.shade600,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                    ),
                    Expanded(
                      flex: 2,
                      child: Text(
                        entry.value.toString(),
                        style: const TextStyle(
                          fontSize: 12,
                          color: Colors.black87,
                        ),
                        maxLines: 3,
                        overflow: TextOverflow.ellipsis,
                      ),
                    ),
                  ],
                ),
              ),
            )
            .toList(),
      ),
    );
  }

  String _formatDateTime(DateTime dateTime) {
    final now = DateTime.now();
    final difference = now.difference(dateTime);

    if (difference.inMinutes < 1) return 'Just now';
    if (difference.inMinutes < 60) {
      return '${difference.inMinutes}m ago';
    }
    if (difference.inHours < 24) {
      return '${difference.inHours}h ago';
    }
    if (difference.inDays < 7) {
      return '${difference.inDays}d ago';
    }

    return '${dateTime.day}/${dateTime.month}/${dateTime.year} ${dateTime.hour.toString().padLeft(2, '0')}:${dateTime.minute.toString().padLeft(2, '0')}';
  }
}
