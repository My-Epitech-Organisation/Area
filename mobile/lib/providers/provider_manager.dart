import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'providers.dart';

class ProviderManager {
  static Future<void> initializeApp(BuildContext context) async {
    final authProvider = context.read<AuthProvider>();
    await authProvider.checkAuthStatus();

    if (authProvider.isAuthenticated && context.mounted) {
      await _loadUserData(context);
    }
  }

  static Future<void> _loadUserData(BuildContext context) async {
    if (!context.mounted) return;
    
    await Future.wait([
      context.read<UserProvider>().loadProfile(),
      context.read<AppletProvider>().loadApplets(),
      context.read<ServiceCatalogProvider>().loadServices(),
    ]);
  }

  static Future<void> onLogin(BuildContext context) async {
    if (!context.mounted) return;
    await _loadUserData(context);
  }

  static Future<void> onLogout(BuildContext context) async {
    final authProvider = context.read<AuthProvider>();
    await authProvider.logout();

    if (!context.mounted) return;
    
    context.read<UserProvider>().clear();
    context.read<AppletProvider>().clear();
    context.read<ServiceCatalogProvider>().clear();
  }

  static Future<void> refreshAll(BuildContext context) async {
    if (!context.mounted) return;
    
    await Future.wait([
      context.read<UserProvider>().loadProfile(forceRefresh: true),
      context.read<AppletProvider>().loadApplets(forceRefresh: true),
      context.read<ServiceCatalogProvider>().loadServices(forceRefresh: true),
    ]);
  }
}
