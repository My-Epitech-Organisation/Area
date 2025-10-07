import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/user_provider.dart';
import '../providers/applet_provider.dart';
import '../providers/provider_manager.dart';
import 'service_connections_page.dart';

class UserPage extends StatelessWidget {
  const UserPage({super.key});

  @override
  Widget build(BuildContext context) {
    return const Scaffold(
      body: SafeArea(
        child: SingleChildScrollView(
          padding: EdgeInsets.all(16.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              UserProfileSection(),
              SizedBox(height: 24),
              StatisticsSection(),
              SizedBox(height: 24),
              SettingsSection(),
              SizedBox(height: 24),
              LogoutSection(),
            ],
          ),
        ),
      ),
    );
  }
}

class UserProfileSection extends StatelessWidget {
  const UserProfileSection({super.key});

  @override
  Widget build(BuildContext context) {
    return Consumer<UserProvider>(
      builder: (context, userProvider, child) {
        final userProfile = userProvider.profile;
        
        // Si on est en train de charger et qu'on n'a pas encore de profil
        if (userProvider.isLoadingProfile && userProfile == null) {
          return Container(
            padding: const EdgeInsets.all(20),
            decoration: _boxDecoration,
            child: const Center(
              child: CircularProgressIndicator(),
            ),
          );
        }
        
        // Si il y a une erreur
        if (userProvider.error != null && userProfile == null) {
          return Container(
            padding: const EdgeInsets.all(20),
            decoration: _boxDecoration,
            child: Column(
              children: [
                const Icon(Icons.error_outline, color: Colors.red, size: 40),
                const SizedBox(height: 8),
                Text(
                  'Error loading profile',
                  style: TextStyle(color: Colors.red[700]),
                ),
                const SizedBox(height: 4),
                Text(
                  userProvider.error!,
                  style: TextStyle(color: Colors.grey[600], fontSize: 12),
                  textAlign: TextAlign.center,
                ),
                const SizedBox(height: 8),
                ElevatedButton(
                  onPressed: () => userProvider.loadProfile(forceRefresh: true),
                  child: const Text('Retry'),
                ),
              ],
            ),
          );
        }

        return Container(
          padding: const EdgeInsets.all(20),
          decoration: _boxDecoration,
          child: Row(
            children: [
              const CircleAvatar(
                radius: 40,
                backgroundColor: Colors.blue,
                child: Icon(
                  Icons.person,
                  size: 40,
                  color: Colors.white,
                ),
              ),
              const SizedBox(width: 16),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      userProfile?['username'] ?? 'Unknown',
                      style: const TextStyle(
                        fontSize: 24,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      userProfile?['email'] ?? 'No email',
                      style: TextStyle(
                        fontSize: 16,
                        color: Colors.grey[600],
                      ),
                    ),
                    const SizedBox(height: 8),
                    UserVerificationBadge(
                      isVerified: userProfile?['email_verified'] == true,
                    ),
                  ],
                ),
              ),
            ],
          ),
        );
      },
    );
  }
}

class UserVerificationBadge extends StatelessWidget {
  const UserVerificationBadge({
    super.key,
    required this.isVerified,
  });

  final bool isVerified;

  @override
  Widget build(BuildContext context) {
    final color = isVerified ? Colors.green : Colors.orange;

    return Container(
      padding: const EdgeInsets.symmetric(
        horizontal: 12,
        vertical: 4,
      ),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.1),
        borderRadius: BorderRadius.circular(20),
      ),
      child: Text(
        isVerified ? 'Verified User' : 'Unverified User',
        style: TextStyle(
          color: color,
          fontWeight: FontWeight.w500,
        ),
      ),
    );
  }
}

class StatisticsSection extends StatelessWidget {
  const StatisticsSection({super.key});

  @override
  Widget build(BuildContext context) {
    return Consumer2<AppletProvider, UserProvider>(
      builder: (context, appletProvider, userProvider, child) {
        final userProfile = userProvider.profile;
        final activeCount = appletProvider.applets.where((a) => a.isActive).length;
        final totalCount = appletProvider.applets.length;
        final serviceCount = appletProvider.applets
            .map((a) => a.action.service.name)
            .toSet()
            .length;

        return Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Statistics',
              style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 16),
            Row(
              children: [
                Expanded(
                  child: _buildStatCard(
                    'Active Applets',
                    '$activeCount',
                    Icons.play_arrow,
                    Colors.blue,
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: _buildStatCard(
                    'Total Applets',
                    '$totalCount',
                    Icons.flash_on,
                    Colors.orange,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),
            Row(
              children: [
                Expanded(
                  child: _buildStatCard(
                    'Services Used',
                    '$serviceCount',
                    Icons.calendar_today,
                    Colors.green,
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: UserStatusCard(
                    isVerified: userProfile?['email_verified'] == true,
                  ),
                ),
              ],
            ),
          ],
        );
      },
    );
  }

  Widget _buildStatCard(
    String title,
    String value,
    IconData icon,
    Color color,
  ) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: _boxDecoration,
      child: Column(
        children: [
          Icon(icon, size: 32, color: color),
          const SizedBox(height: 8),
          Text(
            value,
            style: TextStyle(
              fontSize: 24,
              fontWeight: FontWeight.bold,
              color: color,
            ),
          ),
          const SizedBox(height: 4),
          Text(
            title,
            style: TextStyle(fontSize: 12, color: Colors.grey[600]),
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }
}

class UserStatusCard extends StatelessWidget {
  const UserStatusCard({
    super.key,
    required this.isVerified,
  });

  final bool isVerified;

  @override
  Widget build(BuildContext context) {
    final color = isVerified ? Colors.green : Colors.orange;

    return Container(
      padding: const EdgeInsets.all(16),
      decoration: _boxDecoration,
      child: Column(
        children: [
          Icon(Icons.check_circle, size: 32, color: color),
          const SizedBox(height: 8),
          Text(
            isVerified ? 'Verified' : 'Unverified',
            style: TextStyle(
              fontSize: 24,
              fontWeight: FontWeight.bold,
              color: color,
            ),
          ),
          const SizedBox(height: 4),
          Text(
            'Status',
            style: TextStyle(fontSize: 12, color: Colors.grey[600]),
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }
}

class SettingsSection extends StatelessWidget {
  const SettingsSection({super.key});

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'Settings',
          style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
        ),
        const SizedBox(height: 16),
        Container(
          decoration: _boxDecoration,
          child: Column(
            children: [
              SettingItem(
                title: 'Connected Services',
                subtitle: 'Manage OAuth2 service connections',
                icon: Icons.link,
                onTap: () {
                  Navigator.push(
                    context,
                    MaterialPageRoute(
                      builder: (context) => const ServiceConnectionsPage(),
                    ),
                  );
                },
              ),
              const Divider(height: 1),
              const SettingItem(
                title: 'Notifications',
                subtitle: 'Manage your notification preferences',
                icon: Icons.notifications,
              ),
              const Divider(height: 1),
              const SettingItem(
                title: 'Privacy',
                subtitle: 'Control your privacy settings',
                icon: Icons.privacy_tip,
              ),
              const Divider(height: 1),
              const SettingItem(
                title: 'Help & Support',
                subtitle: 'Get help and contact support',
                icon: Icons.help,
              ),
              const Divider(height: 1),
              const SettingItem(
                title: 'About',
                subtitle: 'App version and information',
                icon: Icons.info,
              ),
            ],
          ),
        ),
      ],
    );
  }
}

class SettingItem extends StatelessWidget {
  const SettingItem({
    super.key,
    required this.title,
    required this.subtitle,
    required this.icon,
    this.onTap,
  });

  final String title;
  final String subtitle;
  final IconData icon;
  final VoidCallback? onTap;

  @override
  Widget build(BuildContext context) {
    return ListTile(
      leading: Icon(icon, color: Colors.grey[600]),
      title: Text(title),
      subtitle: Text(subtitle),
      trailing: const Icon(Icons.chevron_right),
      onTap: onTap ?? () {
        // TODO: Implement navigation to settings
      },
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
    );
  }
}

class LogoutSection extends StatelessWidget {
  const LogoutSection({super.key});

  Future<void> _handleLogout(BuildContext context) async {
    final confirmed = await _showLogoutConfirmation(context);
    if (!confirmed || !context.mounted) return;

    await _performLogout(context);
  }

  Future<bool> _showLogoutConfirmation(BuildContext context) async {
    return await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Confirm Sign Out'),
        content: const Text(
          'Are you sure you want to sign out of your account?',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(false),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () => Navigator.of(context).pop(true),
            style: ElevatedButton.styleFrom(
              backgroundColor: Colors.red,
              foregroundColor: Colors.white,
            ),
            child: const Text('Sign Out'),
          ),
        ],
      ),
    ) ?? false;
  }

  Future<void> _performLogout(BuildContext context) async {
    // Show loading indicator
    _showLoadingDialog(context);

    try {
      // Use ProviderManager to handle logout and cleanup
      await ProviderManager.onLogout(context);

      if (context.mounted) {
        // Close loading dialog
        Navigator.of(context).pop();
        // Navigate to login
        Navigator.of(context).pushNamedAndRemoveUntil('/login', (route) => false);
      }
    } catch (e) {
      if (context.mounted) {
        // Close loading dialog
        Navigator.of(context).pop();
        // Show error message
        _showErrorSnackBar(context, e.toString());
      }
    }
  }

  void _showLoadingDialog(BuildContext context) {
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (context) => const AlertDialog(
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            CircularProgressIndicator(),
            SizedBox(height: 16),
            Text('Signing out...'),
          ],
        ),
      ),
    );
  }

  void _showErrorSnackBar(BuildContext context, String error) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text('Error signing out: $error'),
        backgroundColor: Colors.red,
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: double.infinity,
      height: 56,
      child: ElevatedButton.icon(
        onPressed: () => _handleLogout(context),
        icon: const Icon(Icons.logout),
        label: const Text('Sign Out'),
        style: ElevatedButton.styleFrom(
          backgroundColor: Colors.red,
          foregroundColor: Colors.white,
          padding: const EdgeInsets.symmetric(vertical: 16),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
          ),
        ),
      ),
    );
  }
}

// Common box decoration
const _boxDecoration = BoxDecoration(
  color: Colors.white,
  borderRadius: BorderRadius.all(Radius.circular(12)),
  boxShadow: [
    BoxShadow(
      color: Color.fromRGBO(158, 158, 158, 0.1),
      spreadRadius: 1,
      blurRadius: 5,
      offset: Offset(0, 2),
    ),
  ],
);
