import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'home_page.dart';
import 'pages/create_applet_page.dart';
import 'pages/my_applets_page.dart';
import 'pages/user_page.dart';
import 'providers/navigation_provider.dart';

class SwipeNavigationPage extends StatefulWidget {
  const SwipeNavigationPage({super.key});

  @override
  State<SwipeNavigationPage> createState() => _SwipeNavigationPageState();
}

class _SwipeNavigationPageState extends State<SwipeNavigationPage> {
  late NavigationProvider _navigationProvider;

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

  @override
  void initState() {
    super.initState();
    _navigationProvider = NavigationProvider();
  }

  @override
  void dispose() {
    _navigationProvider.dispose();
    super.dispose();
  }

  void _onPageChanged(int index) {
    _navigationProvider.updateCurrentPage(index);
  }

  void _navigateToPage(int index) {
    _navigationProvider.navigateToPage(index);
  }

  @override
  Widget build(BuildContext context) {
    return ChangeNotifierProvider.value(
      value: _navigationProvider,
      child: Consumer<NavigationProvider>(
        builder: (context, navigationProvider, child) {
          return Scaffold(
            body: Semantics(
              label: 'Main navigation area',
              hint:
                  'Swipe left or right to navigate between pages, or use bottom navigation buttons',
              child: PageView(
                controller: navigationProvider.pageController,
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
                selectedIndex: navigationProvider.currentPage,
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
        },
      ),
    );
  }
}
