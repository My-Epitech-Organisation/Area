/// Service Provider Configuration
///
/// Centralized configuration for all OAuth service providers (Google, GitHub, etc.)
/// This eliminates duplication across oauth_service.dart and service_token.dart
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
        return 'Connectez Gmail, Google Calendar, Drive et plus';
      case 'github':
        return 'Connectez vos repositories, issues et notifications';
      default:
        return 'Connectez ce service à votre compte';
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
