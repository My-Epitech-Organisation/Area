import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'models/applet.dart';
import 'providers/applet_provider.dart';
import 'providers/user_provider.dart';
import 'providers/navigation_provider.dart';
import 'providers/automation_stats_provider.dart';
import 'providers/service_catalog_provider.dart';

class MyHomePage extends StatefulWidget {
  const MyHomePage({super.key});

  @override
  State<MyHomePage> createState() => _MyHomePageState();
}

class _MyHomePageState extends State<MyHomePage> {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _loadStats();
    });
  }

  Future<void> _loadStats() async {
    final statsProvider = context.read<AutomationStatsProvider>();
    final userProvider = context.read<UserProvider>();
    final appletProvider = context.read<AppletProvider>();
    final serviceProvider = context.read<ServiceCatalogProvider>();

    // Load all data in parallel for better performance
    final futures = <Future>[];

    // Always load stats (they might be dynamic)
    futures.add(statsProvider.loadAllStats());

    // Load user data only if not already loaded or loading
    if (userProvider.profile == null && !userProvider.isLoadingProfile) {
      futures.add(userProvider.loadProfile());
    }

    if (appletProvider.applets.isEmpty && !appletProvider.isLoading) {
      futures.add(appletProvider.loadApplets());
    }

    if (serviceProvider.services.isEmpty && !serviceProvider.isLoadingServices) {
      futures.add(serviceProvider.loadServices());
    }

    await Future.wait(futures);
  }

  @override
  Widget build(BuildContext context) {
    return Consumer3<UserProvider, AppletProvider, AutomationStatsProvider>(
      builder: (context, userProvider, appletProvider, statsProvider, child) {
        final userProfile = userProvider.profile;
        final applets = appletProvider.applets;
        final areasStats = statsProvider.areasStats;
        final executionsStats = statsProvider.executionsStats;

        return Scaffold(
          body: SafeArea(
            child: SingleChildScrollView(
              padding: const EdgeInsets.all(20.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  _buildHeader(userProfile),

                  const SizedBox(height: 32),

                  _buildMetricsCards(applets, areasStats, executionsStats),

                  const SizedBox(height: 32),

                  _buildQuickActions(context),

                  const SizedBox(height: 32),

                  _buildRecentApplets(applets),
                ],
              ),
            ),
          ),
        );
      },
    );
  }

  Widget _buildHeader(Map<String, dynamic>? userProfile) {
    final userName = userProfile?['username'] ?? 'User';

    return Row(
      children: [
        Container(
          padding: const EdgeInsets.all(12),
          decoration: BoxDecoration(
            gradient: LinearGradient(
              colors: [Colors.blue.shade400, Colors.blue.shade600],
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
            ),
            borderRadius: BorderRadius.circular(16),
          ),
          child: const Icon(Icons.waving_hand, color: Colors.white, size: 24),
        ),
        const SizedBox(width: 16),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                'Hello, $userName! 👋',
                style: const TextStyle(
                  fontSize: 24,
                  fontWeight: FontWeight.bold,
                  color: Colors.black87,
                ),
              ),
              const SizedBox(height: 4),
              Text(
                'Ready to automate your day?',
                style: TextStyle(fontSize: 16, color: Colors.grey.shade600),
              ),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildMetricsCards(
    List<Applet>? applets,
    Map<String, dynamic>? areasStats,
    Map<String, dynamic>? executionsStats,
  ) {
    final totalApplets = applets?.length ?? 0;
    final activeApplets = applets?.where((applet) => applet.isActive).length ?? 0;

    // Areas stats
    final totalAreas = areasStats?['total'] ?? 0;
    final activeAreas = areasStats?['active'] ?? 0;

    // Executions stats
    final totalExecutions = executionsStats?['total'] ?? 0;
    final successfulExecutions = executionsStats?['success'] ?? 0;
    final failedExecutions = executionsStats?['failed'] ?? 0;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'Your Statistics',
          style: TextStyle(
            fontSize: 20,
            fontWeight: FontWeight.bold,
            color: Colors.black87,
          ),
        ),
        const SizedBox(height: 16),
        GridView.count(
          crossAxisCount: 2,
          shrinkWrap: true,
          physics: const NeverScrollableScrollPhysics(),
          mainAxisSpacing: 16,
          crossAxisSpacing: 16,
          children: [
            _buildMetricCard(
              title: 'Total Applets',
              value: totalApplets.toString(),
              icon: Icons.apps,
              color: Colors.blue,
              subtitle: 'Created',
            ),
            _buildMetricCard(
              title: 'Active Applets',
              value: activeApplets.toString(),
              icon: Icons.check_circle,
              color: Colors.green,
              subtitle: 'Running',
            ),
            _buildMetricCard(
              title: 'Total Areas',
              value: totalAreas.toString(),
              icon: Icons.link,
              color: Colors.purple,
              subtitle: 'Automations',
            ),
            _buildMetricCard(
              title: 'Active Areas',
              value: activeAreas.toString(),
              icon: Icons.play_circle,
              color: Colors.orange,
              subtitle: 'Running',
            ),
            _buildMetricCard(
              title: 'Executions',
              value: totalExecutions.toString(),
              icon: Icons.play_arrow,
              color: Colors.teal,
              subtitle: 'Total runs',
            ),
            _buildMetricCard(
              title: 'Success Rate',
              value: totalExecutions > 0
                  ? '${((successfulExecutions / totalExecutions) * 100).round()}%'
                  : '0%',
              icon: Icons.trending_up,
              color: successfulExecutions > failedExecutions
                  ? Colors.green
                  : Colors.red,
              subtitle:
                  '$successfulExecutions/${totalExecutions - successfulExecutions}',
            ),
          ],
        ),
      ],
    );
  }

  Widget _buildMetricCard({
    required String title,
    required String value,
    required IconData icon,
    required Color color,
    required String subtitle,
  }) {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.05),
            blurRadius: 10,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            padding: const EdgeInsets.all(8),
            decoration: BoxDecoration(
              color: color.withValues(alpha: 0.1),
              borderRadius: BorderRadius.circular(12),
            ),
            child: Icon(icon, color: color, size: 24),
          ),
          const SizedBox(height: 12),
          Text(
            value,
            style: const TextStyle(
              fontSize: 28,
              fontWeight: FontWeight.bold,
              color: Colors.black87,
            ),
          ),
          const SizedBox(height: 4),
          Text(
            title,
            style: TextStyle(
              fontSize: 14,
              color: Colors.grey.shade600,
              fontWeight: FontWeight.w500,
            ),
          ),
          Text(
            subtitle,
            style: TextStyle(fontSize: 12, color: Colors.grey.shade500),
          ),
        ],
      ),
    );
  }

  Widget _buildQuickActions(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'Quick Actions',
          style: TextStyle(
            fontSize: 20,
            fontWeight: FontWeight.bold,
            color: Colors.black87,
          ),
        ),
        const SizedBox(height: 16),
        Row(
          children: [
            Expanded(
              child: _buildNavigationCard(
                context,
                icon: Icons.add,
                title: 'Create Automation',
                subtitle: 'Build new workflows',
                color: Colors.blue,
                onTap: () {
                  final navigationProvider = Provider.of<NavigationProvider>(
                    context,
                    listen: false,
                  );
                  navigationProvider.navigateToPage(
                    1,
                  ); // Index 1 = Create Automation
                },
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: _buildNavigationCard(
                context,
                icon: Icons.apps,
                title: 'Services',
                subtitle: 'Explore services',
                color: Colors.green,
                onTap: () {
                  WidgetsBinding.instance.addPostFrameCallback((_) {
                    Navigator.pushNamed(context, '/services');
                  });
                },
              ),
            ),
          ],
        ),
        const SizedBox(height: 12),
        Row(
          children: [
            Expanded(
              child: _buildNavigationCard(
                context,
                icon: Icons.list,
                title: 'My Automations',
                subtitle: 'View all workflows',
                color: Colors.purple,
                onTap: () {
                  final navigationProvider = Provider.of<NavigationProvider>(
                    context,
                    listen: false,
                  );
                  navigationProvider.navigateToPage(
                    2,
                  ); // Index 2 = My Automations
                },
              ),
            ),
            const SizedBox(width: 12),
            const Expanded(child: SizedBox()),
          ],
        ),
      ],
    );
  }

  Widget _buildNavigationCard(
    BuildContext context, {
    required IconData icon,
    required String title,
    required String subtitle,
    required Color color,
    required VoidCallback onTap,
  }) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(16),
      child: Container(
        padding: const EdgeInsets.all(20),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(16),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withValues(alpha: 0.05),
              blurRadius: 10,
              offset: const Offset(0, 4),
            ),
          ],
          border: Border.all(color: color.withValues(alpha: 0.1), width: 1),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Container(
              padding: const EdgeInsets.all(10),
              decoration: BoxDecoration(
                color: color.withValues(alpha: 0.1),
                borderRadius: BorderRadius.circular(12),
              ),
              child: Icon(icon, color: color, size: 24),
            ),
            const SizedBox(height: 12),
            Text(
              title,
              style: const TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.w600,
                color: Colors.black87,
              ),
            ),
            const SizedBox(height: 4),
            Text(
              subtitle,
              style: TextStyle(fontSize: 14, color: Colors.grey.shade600),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildRecentApplets(List<dynamic>? applets) {
    if (applets == null || applets.isEmpty) {
      return SizedBox(
        height: MediaQuery.of(context).size.height * 0.4,
        child: Center(
          child: Container(
            padding: const EdgeInsets.all(32),
            margin: const EdgeInsets.symmetric(horizontal: 24),
            decoration: BoxDecoration(
              color: Colors.grey.shade50,
              borderRadius: BorderRadius.circular(16),
            ),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              mainAxisAlignment: MainAxisAlignment.center,
              crossAxisAlignment: CrossAxisAlignment.center,
              children: [
                Icon(
                  Icons.lightbulb_outline,
                  size: 48,
                  color: Colors.grey.shade400,
                ),
                const SizedBox(height: 16),
                Text(
                  'No automations yet',
                  style: TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.w600,
                    color: Colors.grey.shade600,
                  ),
                ),
                const SizedBox(height: 8),
                Text(
                  'Create your first automation to get started',
                  style: TextStyle(fontSize: 14, color: Colors.grey.shade500),
                  textAlign: TextAlign.center,
                ),
              ],
            ),
          ),
        ),
      );
    }

    final recentApplets = applets.take(3).toList();

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            const Text(
              'Recent Automations',
              style: TextStyle(
                fontSize: 20,
                fontWeight: FontWeight.bold,
                color: Colors.black87,
              ),
            ),
            TextButton(
              onPressed: () {
                final navigationProvider = Provider.of<NavigationProvider>(
                  context,
                  listen: false,
                );
                navigationProvider.navigateToPage(
                  2,
                ); // Index 2 = My Automations
              },
              child: const Text('View All'),
            ),
          ],
        ),
        const SizedBox(height: 16),
        ...recentApplets.map((applet) => _buildAppletCard(applet)),
      ],
    );
  }

  Widget _buildAppletCard(Applet applet) {
    final isEnabled = applet.isActive;

    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.05),
            blurRadius: 8,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.all(8),
            decoration: BoxDecoration(
              color: isEnabled ? Colors.green.shade50 : Colors.grey.shade50,
              borderRadius: BorderRadius.circular(8),
            ),
            child: Icon(
              isEnabled ? Icons.check_circle : Icons.pause_circle,
              color: isEnabled ? Colors.green : Colors.grey,
              size: 20,
            ),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  applet.name,
                  style: const TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.w600,
                    color: Colors.black87,
                  ),
                ),
                const SizedBox(height: 2),
                Text(
                  applet.description,
                  style: TextStyle(fontSize: 14, color: Colors.grey.shade600),
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                ),
              ],
            ),
          ),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
            decoration: BoxDecoration(
              color: isEnabled ? Colors.green.shade50 : Colors.grey.shade50,
              borderRadius: BorderRadius.circular(12),
            ),
            child: Text(
              isEnabled ? 'Active' : 'Inactive',
              style: TextStyle(
                fontSize: 12,
                fontWeight: FontWeight.w500,
                color: isEnabled ? Colors.green.shade700 : Colors.grey.shade600,
              ),
            ),
          ),
        ],
      ),
    );
  }
}
