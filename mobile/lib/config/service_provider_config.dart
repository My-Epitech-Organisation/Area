import '../utils/service_token_mapper.dart';

/// Service Provider Configuration
///
/// Lightweight configuration for service-related utilities.
/// Most service metadata (logos, OAuth info) comes from about.json
class ServiceProviderConfig {
  /// Map service names for consistency (gmail/google_calendar -> google)
  /// This is used to normalize service names across the application
  static String mapServiceName(String serviceName) {
    return ServiceTokenMapper.resolveTokenService(serviceName);
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
      case 'spotify':
        return 'Spotify';
      case 'twitch':
        return 'Twitch';
      default:
        return provider;
    }
  }
}
