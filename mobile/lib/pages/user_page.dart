import 'package:flutter/material.dart';

class UserPage extends StatelessWidget {
  const UserPage({super.key});

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Header avec avatar et info utilisateur
            Semantics(
              label: 'User profile header',
              hint: 'Displays user avatar, name, email, and account status',
              child: Container(
                padding: const EdgeInsets.all(20),
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(12),
                  boxShadow: [
                    BoxShadow(
                      color: Colors.grey.withValues(alpha: 0.1),
                      spreadRadius: 1,
                      blurRadius: 5,
                      offset: const Offset(0, 2),
                    ),
                  ],
                ),
                child: Row(
                  children: [
                    Semantics(
                      label: 'User avatar',
                      hint: 'Profile picture placeholder',
                      child: CircleAvatar(
                        radius: 40,
                        backgroundColor: Theme.of(context).primaryColor,
                        child: const Icon(
                          Icons.person,
                          size: 40,
                          color: Colors.white,
                        ),
                      ),
                    ),
                    const SizedBox(width: 16),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Semantics(
                            label: 'User name: John Doe',
                            hint: 'Full name of the user account',
                            child: const Text(
                              'John Doe',
                              style: TextStyle(
                                fontSize: 24,
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                          ),
                          const SizedBox(height: 4),
                          Semantics(
                            label: 'User email: john.doe@example.com',
                            hint: 'Email address associated with the account',
                            child: Text(
                              'john.doe@example.com',
                              style: TextStyle(
                                fontSize: 16,
                                color: Colors.grey[600],
                              ),
                            ),
                          ),
                          const SizedBox(height: 8),
                          Semantics(
                            label: 'Account status: Premium User',
                            hint: 'Current subscription tier of the user',
                            child: Container(
                              padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
                              decoration: BoxDecoration(
                                color: Colors.green.withValues(alpha: 0.1),
                                borderRadius: BorderRadius.circular(20),
                              ),
                              child: const Text(
                                'Premium User',
                                style: TextStyle(
                                  color: Colors.green,
                                  fontWeight: FontWeight.w500,
                                ),
                              ),
                            ),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
            ),

            const SizedBox(height: 24),

            // Statistics Section
            Semantics(
              label: 'Statistics section',
              hint: 'User activity and performance metrics',
              header: true,
              child: const Text(
                'Statistics',
                style: TextStyle(
                  fontSize: 20,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ),
            const SizedBox(height: 16),
            Row(
              children: [
                Expanded(
                  child: Semantics(
                    label: 'Active Applets: 12',
                    hint: 'Number of currently active automation applets',
                    child: _buildStatCard(
                      'Active Applets',
                      '12',
                      Icons.play_arrow,
                      Colors.blue,
                    ),
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Semantics(
                    label: 'Total Triggers: 48',
                    hint: 'Total number of triggers executed across all applets',
                    child: _buildStatCard(
                      'Total Triggers',
                      '48',
                      Icons.flash_on,
                      Colors.orange,
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),
            Row(
              children: [
                Expanded(
                  child: Semantics(
                    label: 'This Month: 156',
                    hint: 'Number of executions in the current month',
                    child: _buildStatCard(
                      'This Month',
                      '156',
                      Icons.calendar_today,
                      Colors.green,
                    ),
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Semantics(
                    label: 'Success Rate: 98%',
                    hint: 'Percentage of successful applet executions',
                    child: _buildStatCard(
                      'Success Rate',
                      '98%',
                      Icons.check_circle,
                      Colors.purple,
                    ),
                  ),
                ),
              ],
            ),

            const SizedBox(height: 24),

            // Settings Section
            Semantics(
              label: 'Settings section',
              hint: 'Account and application configuration options',
              header: true,
              child: const Text(
                'Settings',
                style: TextStyle(
                  fontSize: 20,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ),
            const SizedBox(height: 16),
            Semantics(
              label: 'Account Settings button',
              hint: 'Tap to manage your account information',
              button: true,
              child: _buildSettingItem(
                context,
                'Account Settings',
                'Manage your account information',
                Icons.account_circle,
                () {},
              ),
            ),
            Semantics(
              label: 'Notifications button',
              hint: 'Tap to configure notification preferences',
              button: true,
              child: _buildSettingItem(
                context,
                'Notifications',
                'Configure notification preferences',
                Icons.notifications,
                () {},
              ),
            ),
            Semantics(
              label: 'Privacy & Security button',
              hint: 'Tap to manage privacy and security settings',
              button: true,
              child: _buildSettingItem(
                context,
                'Privacy & Security',
                'Manage privacy and security settings',
                Icons.security,
                () {},
              ),
            ),
            Semantics(
              label: 'Connected Apps button',
              hint: 'Tap to manage connected applications',
              button: true,
              child: _buildSettingItem(
                context,
                'Connected Apps',
                'Manage connected applications',
                Icons.apps,
                () {},
              ),
            ),
            Semantics(
              label: 'Billing & Plans button',
              hint: 'Tap to manage your subscription',
              button: true,
              child: _buildSettingItem(
                context,
                'Billing & Plans',
                'Manage your subscription',
                Icons.credit_card,
                () {},
              ),
            ),

            const SizedBox(height: 24),

            // Support Section
            Semantics(
              label: 'Support section',
              hint: 'Help and support resources',
              header: true,
              child: const Text(
                'Support',
                style: TextStyle(
                  fontSize: 20,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ),
            const SizedBox(height: 16),
            Semantics(
              label: 'Help Center button',
              hint: 'Tap to find answers and tutorials',
              button: true,
              child: _buildSettingItem(
                context,
                'Help Center',
                'Find answers and tutorials',
                Icons.help,
                () {},
              ),
            ),
            Semantics(
              label: 'Contact Support button',
              hint: 'Tap to get help from our team',
              button: true,
              child: _buildSettingItem(
                context,
                'Contact Support',
                'Get help from our team',
                Icons.support_agent,
                () {},
              ),
            ),

            const SizedBox(height: 32),

            // Sign Out Button
            Semantics(
              label: 'Sign Out button',
              hint: 'Tap to sign out of your account',
              button: true,
              child: SizedBox(
                width: double.infinity,
                height: 56, // Minimum 48dp + padding
                child: ElevatedButton.icon(
                  onPressed: () {},
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
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildStatCard(String title, String value, IconData icon, Color color) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        boxShadow: [
          BoxShadow(
            color: Colors.grey.withValues(alpha: 0.1),
            spreadRadius: 1,
            blurRadius: 5,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Column(
        children: [
          Icon(icon, color: color, size: 32),
          const SizedBox(height: 8),
          Text(
            value,
            style: const TextStyle(
              fontSize: 24,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 4),
          Text(
            title,
            style: TextStyle(
              fontSize: 12,
              color: Colors.grey[600],
            ),
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }

  Widget _buildSettingItem(BuildContext context, String title, String subtitle, IconData icon, VoidCallback onTap) {
    return Container(
      margin: const EdgeInsets.only(bottom: 8),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        boxShadow: [
          BoxShadow(
            color: Colors.grey.withValues(alpha: 0.1),
            spreadRadius: 1,
            blurRadius: 5,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: SizedBox(
        height: 72, // Minimum 48dp + padding for touch target
        child: ListTile(
          leading: Icon(icon, color: Theme.of(context).primaryColor),
          title: Text(title),
          subtitle: Text(subtitle),
          trailing: const Icon(Icons.chevron_right),
          onTap: onTap,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
          ),
        ),
      ),
    );
  }
}