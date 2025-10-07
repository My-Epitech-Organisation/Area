/// Service Provider Configuration
///
/// Centralized configuration for all OAuth service providers (Google, GitHub, etc.)
class ServiceProviderConfig {
  /// Get user-friendly provider name
  static String getDisplayName(String provider) {
    switch (provider.toLowerCase()) {
      case 'google':
        return 'Google';
      case 'github':
        return 'GitHub';
      default:
        return provider;
    }
  }

  /// Get provider description
  static String getDescription(String provider) {
    switch (provider.toLowerCase()) {
      case 'google':
        return 'Connect Gmail, Google Calendar, Drive and more';
      case 'github':
        return 'Connect your repositories, issues and notifications';
      default:
        return 'Connect this service to your account';
    }
  }

  /// Get provider icon asset path
  static String getIconPath(String provider) {
    switch (provider.toLowerCase()) {
      case 'google':
        return 'assets/google_logo.png';
      case 'github':
        return 'assets/github_logo.png';
      default:
        return 'assets/default_service.png';
    }
  }
}
