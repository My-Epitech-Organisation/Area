import 'package:flutter/material.dart';
import 'home_page.dart';
import 'pages/create_applet_page.dart';
import 'pages/my_applets_page.dart';
import 'providers/provider_manager.dart';
import 'pages/user_page.dart';

class SwipeNavigationPage extends StatefulWidget {
  const SwipeNavigationPage({super.key});

  @override
  State<SwipeNavigationPage> createState() => _SwipeNavigationPageState();
}

class _SwipeNavigationPageState extends State<SwipeNavigationPage> {
  final PageController _pageController = PageController();
  int _currentPage = 0;

  final List<Widget> _pages = [
    const MyHomePage(),
    const CreateAppletPage(),
    const MyAppletsPage(),
    const UserPage(),
  ];

  final List<String> _pageTitles = [
    'Dashboard',
    'Create Automation',
    'My Automations',
    'Profile',
  ];

  final List<IconData> _pageIcons = [
    Icons.home,
    Icons.add,
    Icons.list,
    Icons.person,
  ];

  void _onPageChanged(int index) {
    setState(() {
      _currentPage = index;
    });
  }

  void _navigateToPage(int index) {
    _pageController.animateToPage(
      index,
      duration: const Duration(milliseconds: 250),
      curve: Curves.easeInOutCubic,
    );
  }

  Future<void> _showLogoutConfirmation(BuildContext context) async {
    final confirmed = await showDialog<bool>(
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
    );

    if (confirmed == true && context.mounted) {
      // Show loading indicator
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

      try {
        // Use ProviderManager to handle logout and cleanup
        await ProviderManager.onLogout(context);

        if (context.mounted) {
          // Close loading dialog
          Navigator.of(context).pop();
          Navigator.of(
            context,
          ).pushNamedAndRemoveUntil('/login', (route) => false);
        }
      } catch (e) {
        if (context.mounted) {
          // Close loading dialog
          Navigator.of(context).pop();
          // Show error message
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text('Error signing out: $e'),
              backgroundColor: Colors.red,
            ),
          );
        }
      }
    }
  }

  @override
  void dispose() {
    _pageController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(_pageTitles[_currentPage]),
        backgroundColor: Colors.transparent,
        elevation: 0,
        foregroundColor: Colors.black87,
        surfaceTintColor: Colors.transparent,
        actions: [
          Semantics(
            label: 'Page indicators',
            hint:
                'Shows current page position. ${_currentPage + 1} of ${_pages.length} pages',
            child: SizedBox(
              width: 60, // Constrain width to prevent overflow
              child: Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: List.generate(
                  _pages.length,
                  (index) => Semantics(
                    label: 'Page ${index + 1} indicator',
                    hint: _currentPage == index
                        ? 'Current page'
                        : 'Tap to go to ${_pageTitles[index]} page',
                    button: true,
                    child: GestureDetector(
                      onTap: () => _navigateToPage(index),
                      child: Container(
                        margin: const EdgeInsets.symmetric(horizontal: 2),
                        width: 8, // Reduced size to fit better
                        height: 8, // Reduced size to fit better
                        decoration: BoxDecoration(
                          shape: BoxShape.circle,
                          color: _currentPage == index
                              ? Theme.of(context).colorScheme.primary
                              : Colors.grey.withAlpha(77), // Use withAlpha instead of withOpacity
                        ),
                      ),
                    ),
                  ),
                ),
              ),
            ),
          ),
          PopupMenuButton<String>(
            onSelected: (value) async {
              if (value == 'logout') {
                await _showLogoutConfirmation(context);
              }
            },
            icon: const Icon(Icons.more_vert, color: Colors.grey),
            itemBuilder: (context) => [
              const PopupMenuItem(
                value: 'logout',
                child: Row(
                  children: [
                    Icon(Icons.logout, color: Colors.red, size: 20),
                    SizedBox(width: 8),
                    Text('Sign Out', style: TextStyle(color: Colors.red)),
                  ],
                ),
              ),
            ],
          ),
        ],
      ),
      body: Semantics(
        label: 'Main navigation area',
        hint:
            'Swipe left or right to navigate between pages, or use bottom navigation buttons',
        child: PageView(
          controller: _pageController,
          onPageChanged: _onPageChanged,
          physics: const BouncingScrollPhysics(),
          children: _pages,
        ),
      ),
      bottomNavigationBar: Semantics(
        label: 'Bottom navigation menu',
        hint:
            'Use these buttons to navigate between different sections of the app',
        child: NavigationBar(
          selectedIndex: _currentPage,
          onDestinationSelected: _navigateToPage,
          destinations: List.generate(
            _pages.length,
            (index) => NavigationDestination(
              icon: Icon(_pageIcons[index]),
              label: _pageTitles[index],
            ),
          ),
        ),
      ),
    );
  }
}
