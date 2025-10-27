/// Service Provider Configuration
///
/// Centralized configuration for all OAuth service providers (Google, GitHub, etc.)
class ServiceProviderConfig {
  static const List<String> oauthServices = [
    'github',
    'gmail',
    'google',
    'slack',
    'twitch',
  ];

  static bool requiresOAuth(String serviceName) {
    // Map gmail to google for OAuth purposes
    final mappedName = mapServiceName(serviceName);
    return oauthServices.contains(mappedName.toLowerCase());
  }

  /// Map service names for consistency (gmail -> google)
  /// This is used to normalize service names across the application
  static String mapServiceName(String serviceName) {
    switch (serviceName.toLowerCase()) {
      case 'gmail':
        return 'google';
      default:
        return serviceName;
    }
  }

  /// Get user-friendly provider name
  static String getDisplayName(String provider) {
    switch (provider.toLowerCase()) {
      case 'google':
      case 'gmail':
        return 'Google';
      case 'github':
        return 'GitHub';
      case 'slack':
        return 'Slack';
      case 'twitch':
        return 'Twitch';
      default:
        return provider;
    }
  }

  /// Get provider icon URL from web (PNG images)
  static String getIconUrl(String provider) {
    final mappedProvider = mapServiceName(provider);
    switch (mappedProvider.toLowerCase()) {
      case 'github':
        return 'https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Flogos-world.net%2Fwp-content%2Fuploads%2F2020%2F11%2FGitHub-Symbol.png&f=1&nofb=1&ipt=1e8fe0d0c31dac1d47abf59a23130ec2b31975a34721d1ea9284db059ba4a957';
      case 'google':
        return 'https://upload.wikimedia.org/wikipedia/commons/thumb/2/2f/Google_2015_logo.svg/256px-Google_2015_logo.svg.png';
      case 'slack':
        return 'https://cdn-icons-png.flaticon.com/512/2111/2111615.png';
      case 'twitch':
        return 'https://cdn-icons-png.flaticon.com/512/5968/5968819.png';
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
}
