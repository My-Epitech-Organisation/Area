/// Maps service names to their OAuth provider token
///
/// Problem: about.json lists "gmail" and "google_calendar" as separate services,
/// but OAuth only creates a "google" token.
///
/// This mapper handles the translation so automation execution finds the right token.
class ServiceTokenMapper {
  static const Map<String, String> _tokenMap = {
    'gmail': 'google',
    'google_calendar': 'google',
    'youtube': 'google',
  };

  /// Get the actual token service name to query in the database
  ///
  /// Example:
  /// - resolveTokenService('gmail') → 'google'
  /// - resolveTokenService('google') → 'google'
  /// - resolveTokenService('github') → 'github'
  static String resolveTokenService(String serviceName) {
    return _tokenMap[serviceName] ?? serviceName;
  }

  /// Check if a service uses a mapped token
  static bool isMappedService(String serviceName) {
    return _tokenMap.containsKey(serviceName);
  }

  /// Get all services that map to a specific token
  static List<String> getServicesForToken(String tokenName) {
    return _tokenMap.entries
        .where((e) => e.value == tokenName)
        .map((e) => e.key)
        .toList();
  }
}
