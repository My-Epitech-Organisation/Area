/// Utility class for date/time formatting functions
class DateTimeUtils {
  /// Format a datetime to a relative time string (e.g., "5m ago", "2h ago")
  /// Falls back to full date format for dates older than 7 days
  ///
  /// Examples:
  /// - DateTime.now() → "Just now"
  /// - 5 minutes ago → "5m ago"
  /// - 2 hours ago → "2h ago"
  /// - 3 days ago → "3d ago"
  /// - 10 days ago → "10/10/2025 14:30"
  static String formatDateTime(DateTime dateTime) {
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
