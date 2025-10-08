/// Service Provider Configuration
///
/// Centralized configuration for all OAuth service providers (Google, GitHub, etc.)
class ServiceProviderConfig {
  static const List<String> oauthServices = [
    'github',
    'gmail',
    'google',
    'slack',
    'teams',
  ];

  static bool requiresOAuth(String serviceName) {
    return oauthServices.contains(serviceName.toLowerCase());
  }

  /// Get user-friendly provider name
  static String getDisplayName(String provider) {
    switch (provider.toLowerCase()) {
      case 'google':
        return 'Google';
      case 'github':
        return 'GitHub';
      case 'gmail':
        return 'Gmail';
      case 'slack':
        return 'Slack';
      case 'teams':
        return 'Microsoft Teams';
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
      case 'gmail':
        return 'Access your Gmail inbox and send emails';
      case 'slack':
        return 'Send messages to Slack channels and users';
      case 'teams':
        return 'Send messages to Microsoft Teams channels';
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
      case 'gmail':
        return 'assets/gmail_logo.png';
      case 'slack':
        return 'assets/slack_logo.png';
      case 'teams':
        return 'assets/teams_logo.png';
      default:
        return 'assets/default_service.png';
    }
  }
}
