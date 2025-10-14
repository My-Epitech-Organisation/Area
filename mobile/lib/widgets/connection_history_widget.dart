import 'package:flutter/material.dart';
import '../models/connection_history.dart';
import '../services/oauth_service.dart';

/// Widget to display connection history in a beautiful timeline
class ConnectionHistoryWidget extends StatefulWidget {
  const ConnectionHistoryWidget({super.key});

  @override
  State<ConnectionHistoryWidget> createState() =>
      _ConnectionHistoryWidgetState();
}

class _ConnectionHistoryWidgetState extends State<ConnectionHistoryWidget> {
  final OAuthService _oauthService = OAuthService();
  ConnectionHistoryList? _history;
  bool _isLoading = false;
  bool _isExpanded = false;

  @override
  void initState() {
    super.initState();
    _loadHistory();
  }

  Future<void> _loadHistory() async {
    setState(() => _isLoading = true);
    try {
      final history = await _oauthService.getConnectionHistory(limit: 10);
      if (mounted) {
        setState(() => _history = history);
      }
    } catch (e) {
      // Show error instead of silently failing
      if (mounted) {
        setState(
          () => _history = ConnectionHistoryList(entries: [], totalEntries: 0),
        );
        // You can add a snackbar here if needed
        debugPrint('ConnectionHistoryWidget: Failed to load history: $e');
      }
    } finally {
      if (mounted) {
        setState(() => _isLoading = false);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_isLoading) {
      return const Card(
        child: Padding(
          padding: EdgeInsets.all(16),
          child: Center(child: CircularProgressIndicator()),
        ),
      );
    }

    if (_history == null || _history!.entries.isEmpty) {
      return Card(
        elevation: 2,
        margin: const EdgeInsets.symmetric(vertical: 8),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            children: [
              Row(
                children: [
                  const Icon(Icons.history, color: Colors.grey),
                  const SizedBox(width: 12),
                  const Expanded(
                    child: Text(
                      'Connection History',
                      style: TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.bold,
                        color: Colors.grey,
                      ),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 8),
              const Text(
                'No connection history available.\n'
                'Successful connections will appear here.',
                style: TextStyle(fontSize: 12, color: Colors.grey),
                textAlign: TextAlign.center,
              ),
            ],
          ),
        ),
      );
    }

    return Card(
      elevation: 2,
      margin: const EdgeInsets.symmetric(vertical: 8),
      child: Column(
        children: [
          // Header
          InkWell(
            onTap: () => setState(() => _isExpanded = !_isExpanded),
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Row(
                children: [
                  const Icon(Icons.history, color: Colors.blue),
                  const SizedBox(width: 12),
                  const Expanded(
                    child: Text(
                      'Connection History',
                      style: TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),
                  Text(
                    '${_history!.entries.length} events',
                    style: TextStyle(fontSize: 12, color: Colors.grey[600]),
                  ),
                  const SizedBox(width: 8),
                  Icon(
                    _isExpanded ? Icons.expand_less : Icons.expand_more,
                    color: Colors.grey,
                  ),
                ],
              ),
            ),
          ),

          // Timeline
          if (_isExpanded)
            Container(
              constraints: const BoxConstraints(maxHeight: 300),
              child: ListView.builder(
                shrinkWrap: true,
                physics: const ClampingScrollPhysics(),
                itemCount: _history!.entries.length,
                itemBuilder: (context, index) {
                  final entry = _history!.entries[index];
                  final isLast = index == _history!.entries.length - 1;

                  return _buildTimelineEntry(entry, isLast);
                },
              ),
            ),

          // Footer hint
          if (_isExpanded && _history!.totalEntries > _history!.entries.length)
            Padding(
              padding: const EdgeInsets.all(12),
              child: Text(
                'And ${_history!.totalEntries - _history!.entries.length} more events...',
                style: TextStyle(
                  fontSize: 12,
                  color: Colors.grey[500],
                  fontStyle: FontStyle.italic,
                ),
                textAlign: TextAlign.center,
              ),
            ),
        ],
      ),
    );
  }

  Widget _buildTimelineEntry(ConnectionHistoryEntry entry, bool isLast) {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // Timeline line and dot
        SizedBox(
          width: 60,
          child: Column(
            children: [
              Container(
                width: 12,
                height: 12,
                decoration: BoxDecoration(
                  color: entry.eventColor,
                  shape: BoxShape.circle,
                  border: Border.all(color: Colors.white, width: 2),
                  boxShadow: [
                    BoxShadow(
                      color: entry.eventColor.withValues(alpha: 0.3),
                      blurRadius: 4,
                      spreadRadius: 1,
                    ),
                  ],
                ),
                child: Icon(entry.eventIcon, size: 8, color: Colors.white),
              ),
              if (!isLast)
                Container(
                  width: 2,
                  height: 40,
                  color: Colors.grey[300],
                  margin: const EdgeInsets.symmetric(vertical: 4),
                ),
            ],
          ),
        ),

        // Content
        Expanded(
          child: Container(
            margin: const EdgeInsets.only(bottom: 16, right: 16),
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: entry.isError
                  ? Colors.red.withValues(alpha: 0.05)
                  : Colors.grey.withValues(alpha: 0.05),
              borderRadius: BorderRadius.circular(8),
              border: Border.all(
                color: entry.isError
                    ? Colors.red.withValues(alpha: 0.2)
                    : Colors.grey.withValues(alpha: 0.2),
                width: 1,
              ),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Service name and timestamp
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text(
                      entry.displayServiceName,
                      style: const TextStyle(
                        fontWeight: FontWeight.bold,
                        fontSize: 14,
                      ),
                    ),
                    Text(
                      entry.formattedTimestamp,
                      style: TextStyle(fontSize: 12, color: Colors.grey[600]),
                    ),
                  ],
                ),

                const SizedBox(height: 4),

                // Event type
                Container(
                  padding: const EdgeInsets.symmetric(
                    horizontal: 8,
                    vertical: 2,
                  ),
                  decoration: BoxDecoration(
                    color: entry.eventColor.withValues(alpha: 0.1),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Text(
                    entry.eventDisplayText,
                    style: TextStyle(
                      fontSize: 12,
                      color: entry.eventColor,
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                ),

                // Message if available
                if (entry.message != null && entry.message!.isNotEmpty) ...[
                  const SizedBox(height: 8),
                  Text(
                    entry.message!,
                    style: TextStyle(
                      fontSize: 13,
                      color: Colors.grey[700],
                      height: 1.3,
                    ),
                  ),
                ],
              ],
            ),
          ),
        ),
      ],
    );
  }
}
