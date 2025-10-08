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

  /// Get provider icon URL from web (PNG images)
  static String getIconUrl(String provider) {
    switch (provider.toLowerCase()) {
      case 'github':
        return 'https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Flogos-world.net%2Fwp-content%2Fuploads%2F2020%2F11%2FGitHub-Symbol.png&f=1&nofb=1&ipt=1e8fe0d0c31dac1d47abf59a23130ec2b31975a34721d1ea9284db059ba4a957';
      case 'google':
      case 'gmail':
        return 'https://upload.wikimedia.org/wikipedia/commons/thumb/2/2f/Google_2015_logo.svg/256px-Google_2015_logo.svg.png';
      case 'slack':
        return 'https://cdn-icons-png.flaticon.com/512/2111/2111615.png';
      case 'teams':
        return 'https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Flogos-world.net%2Fwp-content%2Fuploads%2F2021%2F04%2FMicrosoft-Teams-Logo.png&f=1&nofb=1&ipt=46d2e084ffa5f5ba094e7dc387d3425cf676b978d9900488914b4a3bed93bf55';
      case 'timer':
        return 'https://cdn-icons-png.flaticon.com/512/109/109613.png';
      case 'email':
        return 'https://cdn-icons-png.flaticon.com/512/542/542638.png';
      case 'webhook':
        return 'https://cdn-icons-png.flaticon.com/512/149/149852.png';
      default:
        return 'https://cdn-icons-png.flaticon.com/512/1828/1828970.png';
    }
  }

  /// Get provider icon asset path (fallback)
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
