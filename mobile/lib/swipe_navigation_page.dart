import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'home_page.dart';
import 'pages/create_applet_page.dart';
import 'pages/my_applets_page.dart';
import 'pages/user_page.dart';
import 'providers/app_state.dart';

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
    'Create Applet',
    'My Applets',
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
      duration: const Duration(milliseconds: 300),
      curve: Curves.easeInOut,
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
        final appState = Provider.of<AppState>(context, listen: false);
        await appState.logout();

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
        backgroundColor: Theme.of(context).colorScheme.inversePrimary,
        actions: [
          Semantics(
            label: 'Page indicators',
            hint:
                'Shows current page position. ${_currentPage + 1} of ${_pages.length} pages',
            child: Row(
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
                      width: 12,
                      height: 12,
                      decoration: BoxDecoration(
                        shape: BoxShape.circle,
                        color: _currentPage == index
                            ? Colors.white
                            : Colors.white.withValues(alpha: 0.5),
                      ),
                    ),
                  ),
                ),
              ),
            ),
          ),
          const SizedBox(width: 8),
          PopupMenuButton<String>(
            onSelected: (value) async {
              if (value == 'logout') {
                await _showLogoutConfirmation(context);
              }
            },
            itemBuilder: (context) => [
              const PopupMenuItem(
                value: 'logout',
                child: Row(
                  children: [
                    Icon(Icons.logout, color: Colors.red),
                    SizedBox(width: 8),
                    Text('Sign Out'),
                  ],
                ),
              ),
            ],
            child: const Padding(
              padding: EdgeInsets.all(8.0),
              child: Icon(Icons.more_vert),
            ),
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
          children: _pages,
        ),
      ),
      bottomNavigationBar: Semantics(
        label: 'Bottom navigation menu',
        hint:
            'Use these buttons to navigate between different sections of the app',
        child: BottomNavigationBar(
          currentIndex: _currentPage,
          onTap: _navigateToPage,
          type: BottomNavigationBarType.fixed,
          items: List.generate(
            _pages.length,
            (index) => BottomNavigationBarItem(
              icon: Icon(_pageIcons[index]),
              label: _pageTitles[index],
            ),
          ),
        ),
      ),
    );
  }
}
